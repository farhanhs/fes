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
from project.models import Option2, RecordProjectProfile, ReportField, ExportCustomReport, ExportCustomReportField
from fishuser.resource import UserResource, PlaceResource
from django.conf import settings
CAN_VIEW_BUG_PAGE_IPS = settings.CAN_VIEW_BUG_PAGE_IPS
NUMPERPAGE = settings.NUMPERPAGE
ROOT = settings.ROOT

TODAY = lambda: datetime.date.today()
NOW = lambda: datetime.datetime.now()

API_LIMIT_PER_PAGE = settings.API_LIMIT_PER_PAGE

__enable__ = [  
                'Option2Resource',
                'ExportCustomReportResource',
                'ReportFieldResource',
                ]

class RESTForbidden(Exception):
    pass



class SillyAuthentication(Authentication):
    def is_authenticated(self, request, **kwargs):
        if settings.DEBUG: logging.info('SillyAuthentication: %s' % request.user.is_authenticated())
        return request.user.is_authenticated()



class Option2Resource(ModelResource):
    class Meta:
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        queryset = Option2.objects.all()
        resource_name = 'option2'
        ordering = ["swarm"]
        allowed_methods = ['get', 'post', 'put']


class ReportFieldResource(ModelResource):
    tag = fields.ForeignKey(Option2Resource, 'tag', null=True) 
    class Meta:
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        queryset = ReportField.objects.all()
        resource_name = 'reportfield'
        ordering = ["tag"]
        allowed_methods = ['get', 'post', 'put']


class ExportCustomReportResource(ModelResource):
    owner = fields.ForeignKey(UserResource, 'owner')

    class Meta:
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        queryset = ExportCustomReport.objects.all()
        always_return_data = True
        resource_name = 'exportcustomreport'
        ordering = ["owner", 'name']
        allowed_methods = ['get', 'post', 'put', 'delete']
        filtering = {
            "id": ("exact"),
            "owner": ("exact"),
            "name": ("exact"),
        }

    def obj_update(self, bundle, request=None, **kwargs):
        r = ExportCustomReport.objects.get(pk=kwargs['pk'])
        if bundle.data.get('fields_add', ''):
            f = ReportField.objects.get(id=bundle.data.get('fields_add', ''))
            if ExportCustomReportField.objects.filter(export_custom_report=r):
                priority = ExportCustomReportField.objects.filter(export_custom_report=r).order_by('-priority')[0].priority + 1
            else:
                priority = 1
            row = ExportCustomReportField(
                export_custom_report = r,
                report_field = f,
                priority = priority
                )
            row.save()
        elif bundle.data.get('fields_remove', ''):
            f = ReportField.objects.get(id=bundle.data.get('fields_remove', ''))
            ExportCustomReportField.objects.filter(export_custom_report=r, report_field=f).delete()

        super(ExportCustomReportResource, self).obj_update(bundle, **kwargs)
        bundle = self.build_bundle(obj=r, request=request)
        bundle = self.full_dehydrate(bundle)
        return bundle