#-*- coding: utf8 -*-
import logging, datetime, re, json, traceback, sys

from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.conf import settings
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
from tastypie.http import HttpBadRequest
from tastypie.exceptions import BadRequest, ApiFieldError
from tastypie.paginator import Paginator
from tastypie.authentication import Authentication, SessionAuthentication, ApiKeyAuthentication, MultiAuthentication
from tastypie.authorization import Authorization, DjangoAuthorization
from tastypie.resources import ModelResource
from tastypie.constants import ALL, ALL_WITH_RELATIONS

from guardian.shortcuts import assign, get_objects_for_user

import os, random

API_LIMIT_PER_PAGE = settings.API_LIMIT_PER_PAGE
from sop.models import File, Item, Sop
from tastypie.serializers import Serializer

__enable__ = [
               'FileResource',
               'ItemResource',
               'SopResource',
               'AuthSopResource',
               'AuthFileResource',
               'AuthItemResource',
            ]


class SopResource(ModelResource):

    class Meta:
        queryset = Sop.objects.all()
        resource_name = 'sop'
        allowed_methods = ['get']
        authorization= Authorization()


    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/(?P<pk>\w[\w/-]*)/(?P<type>\w[\w/-]*)/$" % (self._meta.resource_name), self.wrap_view('get_item'), name="api_get_vsd"),
        ]


    def get_item(self, request, **kwargs):
        item = Sop.objects.get(id=int(kwargs['pk'])).item_sop.filter(type=int(kwargs['type'])).order_by('id')
        objects = []
        item_res = ItemResource()
        for i in item:
            bundle = item_res.build_bundle(obj=i, request=request)
            bundle = item_res.full_dehydrate(bundle)
            objects.append(bundle)
        
        object_list = {'objects': objects,}
        self.log_throttled_access(request)
        return self.create_response(request,object_list)



class FileResource(ModelResource):

    class Meta:
        queryset = File.objects.all()
        resource_name = 'file'
        allowed_methods = ['get']
        authorization= Authorization()
        ordering = ["id"]
        filtering = {
            'is_use' : ALL,
        }


    def dehydrate(self, bundle):
        if bundle.obj: bundle.data['upload_time_format'] = datetime.datetime.strftime(bundle.obj.upload_time, '%Y-%m-%d %H:%M:%S')
        return bundle




class ItemResource(ModelResource):
    files= fields.ToManyField('sop.resource.FileResource', 'file_item', full=True, null=True)
    sop = fields.ForeignKey(SopResource, 'sop')

    class Meta:
        queryset = Item.objects.all()
        resource_name = 'item'
        allowed_methods = ['get']
        ordering = ["id"]
        authorization= Authorization()
        filtering = {
            'sop' :ALL_WITH_RELATIONS,
            'type':ALL,
            'files':ALL_WITH_RELATIONS,
        }

    def dehydrate(self, bundle):
        bundle.data['use_file'] = bundle.obj.file_item.get(is_use = True).id
        if bundle.obj.type == 0: bundle.data['filters'] = "vsd"
        elif bundle.obj.type == 1: bundle.data['filters'] = "doc,docx"
        else: bundle.data['filters'] = "doc,docx,xls,xlsx,pdf,jpg,jpeg,png,ppt,pptx,gif"
        return bundle



class AuthSopResource(ModelResource):

    class Meta:
        queryset = Sop.objects.all()
        resource_name = 'auth_sop'
        allowed_methods = ['get', 'post', 'put', 'delete']
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication())
        authorization= Authorization()


    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/(?P<pk>\w[\w/-]*)/(?P<type>\w[\w/-]*)/$" % (self._meta.resource_name), self.wrap_view('get_item'), name="api_get_vsd"),
        ]


    def get_item(self, request, **kwargs):
        item = Sop.objects.get(id=int(kwargs['pk'])).item_sop.filter(type=int(kwargs['type'])).order_by('id')
        objects = []
        item_res = ItemResource()
        for i in item:
            bundle = item_res.build_bundle(obj=i, request=request)
            bundle = item_res.full_dehydrate(bundle)
            objects.append(bundle)
        
        object_list = {'objects': objects,}
        self.log_throttled_access(request)
        return self.create_response(request,object_list)



class AuthFileResource(ModelResource):

    class Meta:
        queryset = File.objects.all()
        resource_name = 'auth_file'
        allowed_methods = ['get', 'post', 'put', 'delete']
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication())
        authorization= Authorization()
        ordering = ["id"]
        filtering = {
            'is_use' : ALL,
        }


    def dehydrate(self, bundle):
        if bundle.obj: bundle.data['upload_time_format'] = datetime.datetime.strftime(bundle.obj.upload_time, '%Y-%m-%d %H:%M:%S')
        return bundle



class AuthItemResource(ModelResource):
    files= fields.ToManyField('sop.resource.FileResource', 'file_item', full=True, null=True)
    sop = fields.ForeignKey(SopResource, 'sop')

    class Meta:
        queryset = Item.objects.all()
        resource_name = 'auth_item'
        allowed_methods = ['get', 'post', 'put',  'delete']
        ordering = ["id"]
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication())
        authorization= Authorization()
        filtering = {
            'sop' :ALL_WITH_RELATIONS,
            'type':ALL,
            'files':ALL_WITH_RELATIONS,
        }

    def dehydrate(self, bundle):
        bundle.data['use_file'] = bundle.obj.file_item.get(is_use = True).id
        if bundle.obj.type == 0: bundle.data['filters'] = "vsd"
        elif bundle.obj.type == 1: bundle.data['filters'] = "doc,docx"
        else: bundle.data['filters'] = "doc,docx,xls,xlsx,pdf,jpg,jpeg,png,ppt,pptx,gif"
        return bundle