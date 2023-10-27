#-*- coding: utf8 -*-
import logging, datetime, re, json, traceback, sys

from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.conf import settings
from django.db.models import Q, Count
# from django.conf.urls import defaults as urls
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

from general.models import Place, Unit
from pccmating.models import Project as PCC_Project
from pccmating.models import ProjectProgress as PCC_ProjectProgress

# from hoabor.resource import FishingPortResource, AquacultureResource

TODAY = lambda: datetime.date.today()
NOW = lambda: datetime.datetime.now()

API_LIMIT_PER_PAGE = settings.API_LIMIT_PER_PAGE

__enable__ = [
                'PCC_ProjectResource',
                'PCC_ProjectProgressResource'
                ]

class RESTForbidden(Exception):
    pass



class SillyAuthentication(Authentication):
    def is_authenticated(self, request, **kwargs):
        if settings.DEBUG: logging.info('SillyAuthentication: %s' % request.user.is_authenticated())
        return request.user.is_authenticated()



class PCC_ProjectResource(ModelResource):

    class Meta:
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        queryset = PCC_Project.objects.all()
        always_return_data = True
        resource_name = 'pcc_project'
        allowed_methods = ['get', 'post', 'put', 'delete']
        filtering = {
            "uid": ("exact"),
        }



class PCC_ProjectProgressResource(ModelResource):
    project = fields.ForeignKey(PCC_ProjectResource, 'project')

    class Meta:
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        queryset = PCC_ProjectProgress.objects.all()
        always_return_data = True
        ordering = ["year", "month"]
        resource_name = 'pcc_projectprogress'
        allowed_methods = ['get', 'post', 'put', 'delete']
        filtering = {
            "project": ("exact"),
        }