#-*- coding: utf8 -*-
import logging, datetime, re, json, traceback, sys

from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.conf import settings
from django.db.models import Q, Count
# from django.conf.urls import defaults as urls
from django.core import mail
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.http import HttpResponseForbidden, HttpResponseServerError
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_exempt
from django.utils.cache import patch_cache_control
from django.views.debug import ExceptionReporter
from django.template.loader import get_template
from django.template import Context, RequestContext

from django.conf.urls import *

from tastypie import fields
from tastypie import http
from tastypie.http import HttpBadRequest
from tastypie.exceptions import BadRequest, ApiFieldError
from tastypie.exceptions import ImmediateHttpResponse
from tastypie.paginator import Paginator
from tastypie.authentication import Authentication, SessionAuthentication, ApiKeyAuthentication, MultiAuthentication
from tastypie.authorization import Authorization, DjangoAuthorization
from tastypie.resources import ModelResource
from tastypie.constants import ALL, ALL_WITH_RELATIONS

from guardian.shortcuts import assign, get_objects_for_user, get_perms

import os, random, json, re, datetime

from help.models import Question, QuestionFile
from fishuser.resource import UserResource
from django.conf import settings
CAN_VIEW_BUG_PAGE_IPS = settings.CAN_VIEW_BUG_PAGE_IPS
NUMPERPAGE = settings.NUMPERPAGE
ROOT = settings.ROOT

TODAY = lambda: datetime.date.today()
NOW = lambda: datetime.datetime.now()

API_LIMIT_PER_PAGE = settings.API_LIMIT_PER_PAGE

__enable__ = [
                'QuestionResource',
                'QuestionFileResource'
                ]

class RESTForbidden(Exception):
    pass



class SillyAuthentication(Authentication):
    def is_authenticated(self, request, **kwargs):
        if settings.DEBUG: logging.info('SillyAuthentication: %s' % request.user.is_authenticated())
        return request.user.is_authenticated()



class QuestionResource(ModelResource):
    user = fields.ForeignKey(UserResource, 'user')
    completer = fields.ForeignKey(UserResource, 'completer', null=True)

    class Meta:
        queryset = Question.objects.all()
        resource_name = 'question'
        ordering = ["ask_time"]
        allowed_methods = ['get', 'post', 'put', 'delete']
        always_return_data = True
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        filtering = {
            "user": ("exact", ),
        }



class QuestionFileResource(ModelResource):
    question = fields.ForeignKey(QuestionResource, 'question')

    class Meta:
        queryset = QuestionFile.objects.all()
        resource_name = 'questionfile'
        ordering = ["id"]
        allowed_methods = ['get', 'post', 'put', 'delete']
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        filtering = {
            "question": ("exact", ),
        }


    def obj_delete(self, bundle, **kwargs):
        file = QuestionFile.objects.get(pk=kwargs['pk'])
        request = bundle.request
        try:
            os.remove(os.path.join(ROOT, file.file.name))
        except: pass
        super(QuestionFileResource, self).obj_delete(bundle, **kwargs)
