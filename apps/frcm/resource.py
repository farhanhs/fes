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
from frcm.models import CityFiles, Option, ProjectFile
from fishuser.resource import UserResource, PlaceResource, ProjectResource
from fishuser.models import FRCMUserGroup
from django.conf import settings
CAN_VIEW_BUG_PAGE_IPS = settings.CAN_VIEW_BUG_PAGE_IPS
NUMPERPAGE = settings.NUMPERPAGE
ROOT = settings.ROOT

TODAY = lambda: datetime.date.today()
NOW = lambda: datetime.datetime.now()

API_LIMIT_PER_PAGE = settings.API_LIMIT_PER_PAGE

__enable__ = [
                'OptionResource',
                'CityFilesResource',
                'ProjectFileResource'
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
        resource_name = 'option'
        always_return_data = True
        ordering = ["swarm"]
        allowed_methods = ['get', 'post', 'put']

        

class CityFilesResource(ModelResource):
    upload_user = fields.ForeignKey(UserResource, 'upload_user')
    place = fields.ForeignKey(PlaceResource, 'place', null=True)

    class Meta:
        queryset = CityFiles.objects.all()
        resource_name = 'cityfiles'
        ordering = ["upload_date"]
        allowed_methods = ['get', 'post', 'put', 'delete']
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        filtering = {
            "name": ("exact", ),
        }


    def obj_delete(self, bundle, **kwargs):
        city_file = CityFiles.objects.get(pk=kwargs['pk'])
        request = bundle.request
        try:
            os.remove(os.path.join(ROOT, city_file.file.name))
        except: pass
        super(CityFilesResource, self).obj_delete(bundle, **kwargs)



class ProjectFileResource(ModelResource):
    user = fields.ForeignKey(UserResource, 'user')
    project = fields.ForeignKey(ProjectResource, 'project')
    file_type = fields.ForeignKey(OptionResource, 'file_type')
    tag = fields.ToManyField(OptionResource, 'tag', null=True)



    class Meta:
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        queryset = ProjectFile.objects.all()
        resource_name = 'projectfile'
        ordering = ["name"]
        always_return_data = True
        allowed_methods = ['get', 'post', 'patch', 'put', 'delete']
        filtering = {
            "id": ("exact"),
            "user": ("exact"),
            "file_type": ("exact"),
            "project": ("exact"),
        }


    def obj_delete(self, bundle, **kwargs):
        projectfile = ProjectFile.objects.get(pk=kwargs['pk'])
        request = bundle.request

        if request.user.has_perm('fishuser.edit_all_project_in_management_system'):
            #管理者_工程管理者
            can_delete = True
        elif FRCMUserGroup.objects.filter(user=request.user, is_active=True):
            can_delete = True
        else:
            can_delete = False

        if can_delete:
            os.remove(projectfile.file.path)
            super(ProjectFileResource, self).obj_delete(bundle, **kwargs)
        else:
            raise ImmediateHttpResponse(response=http.HttpBadRequest(_(u'You have no permission to delete file')))


    def obj_update(self, bundle, **kwargs):
        try: projectfile = self._meta.queryset.get(id=kwargs["pk"])
        except: projectfile = bundle.obj
        
        if bundle.data.get('tag_add', ''):
            tag = Option.objects.get(id=bundle.data.get('tag_add', ''))
            projectfile.tag.add(tag)
        elif bundle.data.get('tag_remove', ''):
            tag = Option.objects.get(id=bundle.data.get('tag_remove', ''))
            projectfile.tag.remove(tag)
        
        list_url = reverse('api_dispatch_list', kwargs={'resource_name': 'option', 'api_name': 'v2'})
        bundle.data['tag'] = ['%s%s/'%(list_url, t.id) for t in projectfile.tag.all()]

        bundle = super(ProjectFileResource, self).obj_update(bundle, **kwargs)

        return bundle