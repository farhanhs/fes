#-*- coding: utf8 -*-
import logging, datetime, re, json, traceback, sys

from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.conf import settings
from django.db.models import Q, Count
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.contrib.sites.models import Site
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

from fishuser.models import Project
from general.models import Place, Unit
from supervise.models import ErrorContent
from auditing.models import Option, AuditingCase, Error
from fishuser.resource import UnitResource, PlaceResource, ProjectResource
from supervise.resource import ErrorContentResource

from django.conf import settings
ROOT = settings.ROOT

TODAY = lambda: datetime.date.today()
NOW = lambda: datetime.datetime.now()

API_LIMIT_PER_PAGE = settings.API_LIMIT_PER_PAGE

__enable__ = [
                'OptionResource',
                'AuditingCaseResource',
                'ErrorResource',
                ]

class RESTForbidden(Exception):
    pass



class SillyAuthentication(Authentication):
    def is_authenticated(self, request, **kwargs):
        if settings.DEBUG: logging.info('SillyAuthentication: %s' % request.user.is_authenticated())
        return request.user.is_authenticated()



class OptionResource(ModelResource):
    class Meta:
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        queryset = Option.objects.all()
        always_return_data = True
        resource_name = 'option'
        ordering = ["swarm"]
        allowed_methods = ['get', 'post', 'put']



class AuditingCaseResource(ModelResource):
    project = fields.ForeignKey(ProjectResource, 'project', null=True)
    manage_unit = fields.ForeignKey(UnitResource, 'manage_unit', null=True)
    unit = fields.ForeignKey(UnitResource, 'unit', null=True)
    place = fields.ForeignKey(PlaceResource, 'place', null=True)
    location = fields.ForeignKey(PlaceResource, 'location', null=True)

    class Meta:
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        queryset = AuditingCase.objects.all()
        always_return_data = True
        resource_name = 'auditingcase'
        ordering = ["id"]
        allowed_methods = ['get', 'post', 'put', 'delete']
        paginator_class = Paginator



class ErrorResource(ModelResource):
    case = fields.ForeignKey(AuditingCaseResource, 'case')
    errorcontent = fields.ForeignKey(ErrorContentResource, 'errorcontent', null=True)

    class Meta:
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        queryset = Error.objects.all()
        always_return_data = True
        resource_name = 'error'
        ordering = ["id"]
        allowed_methods = ['get', 'post', 'put', 'delete']
        filtering = {
            "case": ("exact", ),
            "errorcontent": ("exact", ),
        }