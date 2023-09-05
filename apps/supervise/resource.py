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
from supervise.models import Option, Guide, SuperviseCase, ErrorLevel, ErrorContent, CaseFile, ErrorImproveFile
from supervise.models import Error, ErrorImprovePhoto, ErrorPhotoFile, PCC_Project, PCC_sync_record
from fishuser.resource import UnitResource, PlaceResource, ProjectResource
from pccmating.models import Cofiguration
from pccmating.models import Project as PCCProject

from django.conf import settings
ROOT = settings.ROOT

TODAY = lambda: datetime.date.today()
NOW = lambda: datetime.datetime.now()

API_LIMIT_PER_PAGE = settings.API_LIMIT_PER_PAGE

__enable__ = [
                'OptionResource',
                'GuideResource',
                'SuperviseCaseResource',
                'ErrorLevelResource',
                'ErrorContentResource',
                'ErrorResource',
                'ErrorImprovePhotoResource',
                'ErrorImproveFileResource',
                'ErrorPhotoFileResource',
                'CaseFileResource',
                'PCC_ProjectResource',
                'PCCProjectResource',
                'CofigurationResource'
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



class GuideResource(ModelResource):
    class Meta:
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        queryset = Guide.objects.all()
        always_return_data = True
        resource_name = 'guide'
        ordering = ["id"]
        allowed_methods = ['get', 'post', 'put', 'delete']
        filtering = {
            'name': ALL_WITH_RELATIONS
        }



class SuperviseCaseResource(ModelResource):
    unit = fields.ForeignKey(UnitResource, 'unit', null=True)
    subordinate_agencies_unit = fields.ForeignKey(UnitResource, 'subordinate_agencies_unit', null=True)
    place = fields.ForeignKey(PlaceResource, 'place', null=True)
    location = fields.ForeignKey(PlaceResource, 'location', null=True)
    outguide = fields.ToManyField(GuideResource, 'outguide', full=True, null=True)
    inguide = fields.ToManyField(GuideResource, 'inguide', full=True, null=True)
    captain = fields.ToManyField(GuideResource, 'captain', full=True, null=True)
    worker = fields.ToManyField(GuideResource, 'worker', full=True, null=True)
    fes_project = fields.ForeignKey(ProjectResource, 'fes_project', null=True)

    class Meta:
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        queryset = SuperviseCase.objects.all()
        always_return_data = True
        resource_name = 'supervisecase'
        ordering = ["id"]
        allowed_methods = ['get', 'post', 'put', 'delete']
        paginator_class = Paginator


    def dehydrate_id(self, bundle):
        if bundle.obj:
            bundle.data['listname_place'] = bundle.obj.place.name if bundle.obj.place else ''
            bundle.data['listname_location'] = bundle.obj.location.name if bundle.obj.location else ''
            bundle.data['listname_subordinate_agencies_unit'] = bundle.obj.subordinate_agencies_unit.name if bundle.obj.subordinate_agencies_unit else ''
            bundle.data['outguide_list'] = ' '.join([i.name for i in bundle.obj.outguide.all()])
            bundle.data['inguide_list'] = ' '.join([i.name for i in bundle.obj.inguide.all()])

        return bundle.data['id']

    def obj_update(self, bundle, **kwargs):
        if bundle.request.META.has_key('x_forwarded_for'): ip = bundle.request.META['x_forwarded_for']
        elif bundle.request.META.has_key('X_FORWARDED_FOR'): ip = bundle.request.META['X_FORWARDED_FOR']
        else: ip = bundle.request.META['REMOTE_ADDR']
        case = SuperviseCase.objects.get(pk=kwargs['pk'])
        # outguide = M.ManyToManyField(Guide, related_name='outguide_set', verbose_name='外聘委員')
        # inguide = M.ManyToManyField(Guide, related_name='inguide_set', verbose_name='內聘委員')
        # captain = M.ManyToManyField(Guide, related_name='captain_set', verbose_name='領隊')
        # worker = M.ManyToManyField(Guide, related_name='worker_set', verbose_name='工作人員')
        if bundle.data.get('add_inguide', ''):
            guide = Guide.objects.filter(name=bundle.data.get('add_inguide', ''))
            if guide:
                guide=guide[0]
            else:
                guide = Guide(name=bundle.data.get('add_inguide', ''))
                guide.save()
            case.inguide.add(guide)
        if bundle.data.get('remove_inguide', ''):
            guide = Guide.objects.get(id=bundle.data.get('remove_inguide', ''))
            case.inguide.remove(guide)
        if bundle.data.get('add_outguide', ''):
            guide = Guide.objects.filter(name=bundle.data.get('add_outguide', ''))
            if guide:
                guide=guide[0]
            else:
                guide = Guide(name=bundle.data.get('add_outguide', ''))
                guide.save()
            case.outguide.add(guide)
        if bundle.data.get('remove_outguide', ''):
            guide = Guide.objects.get(id=bundle.data.get('remove_outguide', ''))
            case.outguide.remove(guide)
        if bundle.data.get('add_captain', ''):
            guide = Guide.objects.filter(name=bundle.data.get('add_captain', ''))
            if guide:
                guide=guide[0]
            else:
                guide = Guide(name=bundle.data.get('add_captain', ''))
                guide.save()
            case.captain.add(guide)
        if bundle.data.get('remove_captain', ''):
            guide = Guide.objects.get(id=bundle.data.get('remove_captain', ''))
            case.captain.remove(guide)
        if bundle.data.get('add_worker', ''):
            guide = Guide.objects.filter(name=bundle.data.get('add_worker', ''))
            if guide:
                guide=guide[0]
            else:
                guide = Guide(name=bundle.data.get('add_worker', ''))
                guide.save()
            case.worker.add(guide)
        if bundle.data.get('remove_worker', ''):
            guide = Guide.objects.get(id=bundle.data.get('remove_worker', ''))
            case.worker.remove(guide)
        
        # for key in bundle.data:
        #     key = key.replace('add_', '').replace('remove_', '')
        #     try:
        #         old_value = getattr(case, key)
        #         record = PCC_sync_record(
        #             user = bundle.request.user,
        #             case = case,
        #             ip = ip,
        #             field_name = key,
        #             old_value = old_value,
        #             new_value = bundle.data[key]
        #             )
        #         record.save()
        #     except: pass
            

        list_url = reverse('api_dispatch_list',
                            kwargs={'resource_name': 'guide', 'api_name': 'v2'})
        bundle.data['inguide'] = ['%s%s/'%(list_url, t.id) for t in case.inguide.all()]
        bundle.data['outguide'] = ['%s%s/'%(list_url, t.id) for t in case.outguide.all()]
        bundle.data['captain'] = ['%s%s/'%(list_url, t.id) for t in case.captain.all()]
        bundle.data['worker'] = ['%s%s/'%(list_url, t.id) for t in case.worker.all()]
        return super(SuperviseCaseResource, self).obj_update(bundle, **kwargs)

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/search/$" % (self._meta.resource_name), self.wrap_view('get_search'), name="api_get_search"),
        ]

    def get_search(self, request, **kwargs):
        info = {}
        for key in request.GET.iterkeys():
            info[key] = request.GET.get(key)

        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
        self.throttle_check(request)

        # Do the query.
        result = SuperviseCase.objects.all().order_by('-date', 'plan', 'project', 'place')

        #ids
        if info.get('ids', '') and info.get('ids', '') != '' and info.get('ids', '') != 'undefined':
            ids = info.get('ids', '').split(',')
            result = result.filter(id__in=ids[:-1])

        #計畫名稱
        if info.get('plan', '') and info.get('plan', '') != '' and info.get('plan', '') != 'undefined':
            ids = []
            for key in re.split('[ ,]+', info.get('plan', '')):
                if key:
                    ids.extend([i.id for i in result.filter(plan__icontains=key)])
            result = result.filter(id__in=ids)

        #工程名稱
        if info.get('project', '') and info.get('project', '') != '' and info.get('project', '') != 'undefined':
            ids = []
            for key in re.split('[ ,]+', info.get('project', '')):
                if key:
                    ids.extend([i.id for i in result.filter(project__icontains=key)])
            result = result.filter(id__in=ids)

        #主管機關
        if info.get('subordinate_agencies_unit', '') and info.get('subordinate_agencies_unit', '') != '' and info.get('subordinate_agencies_unit', '') != 'undefined':
            unit = Unit.objects.get(id=info.get('subordinate_agencies_unit', ''))
            result = result.filter(subordinate_agencies_unit=unit)

        #主辦機關
        if info.get('project_organizer_agencies', '') and info.get('project_organizer_agencies', '') != '' and info.get('project_organizer_agencies', '') != 'undefined':
            ids = []
            for key in re.split('[ ,]+', info.get('project_organizer_agencies', '')):
                if key:
                    ids.extend([i.id for i in result.filter(project_organizer_agencies__icontains=key)])
            result = result.filter(id__in=ids)

        #專案管理單位
        if info.get('project_manage_unit', '') and info.get('project_manage_unit', '') != '' and info.get('project_manage_unit', '') != 'undefined':
            ids = []
            for key in re.split('[ ,]+', info.get('project_manage_unit', '')):
                if key:
                    ids.extend([i.id for i in result.filter(project_manage_unit__icontains=key)])
            result = result.filter(id__in=ids)

        #設計單位
        if info.get('designer', '') and info.get('designer', '') != '' and info.get('designer', '') != 'undefined':
            ids = []
            for key in re.split('[ ,]+', info.get('designer', '')):
                if key:
                    ids.extend([i.id for i in result.filter(designer__icontains=key)])
            result = result.filter(id__in=ids)

        #監造單位
        if info.get('inspector', '') and info.get('inspector', '') != '' and info.get('inspector', '') != 'undefined':
            ids = []
            for key in re.split('[ ,]+', info.get('inspector', '')):
                if key:
                    ids.extend([i.id for i in result.filter(inspector__icontains=key)])
            result = result.filter(id__in=ids)

        #承包廠商
        if info.get('construct', '') and info.get('construct', '') != '' and info.get('construct', '') != 'undefined':
            ids = []
            for key in re.split('[ ,]+', info.get('construct', '')):
                if key:
                    ids.extend([i.id for i in result.filter(construct__icontains=key)])
            result = result.filter(id__in=ids)

        #外部委員
        if info.get('outguide', '') and info.get('outguide', '') != '' and info.get('outguide', '') != 'undefined':
            names = []
            for key in re.split('[ ,+]+', info.get('outguide')):
                for s in Guide.objects.filter(name__contains=key):
                    names.append(s.name)
            result = result.filter(outguide__name__in=names)

        #內部委員
        if info.get('inguide', '') and info.get('inguide', '') != '' and info.get('inguide', '') != 'undefined':
            names = []
            for key in re.split('[ ,+]+', info.get('inguide')):
                for s in Guide.objects.filter(name__contains=key):
                    names.append(s.name)
            result = result.filter(inguide__name__in=names)

        #督導日期
        if info.get('date_from', '') and info.get('date_from', '') != '' and info.get('date_from', '') != 'undefined':
            if not info.get('date_to', ''): info['date_to'] = info['date_from']
            result = result.filter(date__gte=info.get('date_from', ''), date__lte=info.get('date_to', ''))

        #開工日期
        if info.get('start_date_from', '') and info.get('start_date_from', '') != '' and info.get('start_date_from', '') != 'undefined':
            if not info.get('start_date_to', ''): info['start_date_to'] = info['start_date_from']
            result = result.filter(start_date__gte=info.get('start_date_from', ''), start_date__lte=info.get('start_date_to', ''))

        #預計完工日期
        if info.get('expected_completion_date_from', '') and info.get('expected_completion_date_from', '') != '' and info.get('expected_completion_date_from', '') != 'undefined':
            if not info.get('expected_completion_date_to', ''): info['expected_completion_date_to'] = info['expected_completion_date_from']
            result = result.filter(expected_completion_date__gte=info.get('expected_completion_date_from', ''), expected_completion_date__lte=info.get('expected_completion_date_to', ''))

        #縣市
        if info.get('place', '') and info.get('place', '') != '' and info.get('place', '') != 'undefined':
            place = Place.objects.get(id=info.get('place', ''))
            result = result.filter(place=place)

        #督導分數
        if info.get('score_from', '') and info.get('score_from', '') != '' and info.get('score_from', '') != 'undefined':
            if not info.get('score_to', ''): info['score_to'] = info['score_from']
            result = result.filter(score__gte=info.get('score_from', ''), score__lte=info.get('score_to', ''))

        #發包預算
        if info.get('budget_price_from', '') and info.get('budget_price_from', '') != '' and info.get('budget_price_from', '') != 'undefined':
            budget_price_from = str(float(info.get('budget_price_from', '')))
            budget_price_to = str(float(info.get('budget_price_to', '')))
            result = result.filter(budget_price__gte=budget_price_from, budget_price__lte=budget_price_to)

        #契約金額
        if info.get('contract_price_from', '') and info.get('contract_price_from', '') != '' and info.get('contract_price_from', '') != 'undefined':
            contract_price_from = str(float(info.get('contract_price_from', '')))
            contract_price_to = str(float(info.get('contract_price_to', '')))
            print contract_price_from, contract_price_to
            result = result.filter(contract_price__gte=contract_price_from, contract_price__lte=contract_price_to)

        #預定進度
        if info.get('scheduled_progress_from', '') and info.get('scheduled_progress_from', '') != '' and info.get('scheduled_progress_from', '') != 'undefined':
            result = result.filter(scheduled_progress__gte=info.get('scheduled_progress_from', ''), scheduled_progress__lte=info.get('scheduled_progress_to', ''))

        #實際進度
        if info.get('actual_progress_from', '') and info.get('actual_progress_from', '') != '' and info.get('actual_progress_from', '') != 'undefined':
            result = result.filter(actual_progress__gte=info.get('actual_progress_from', ''), actual_progress__lte=info.get('actual_progress_to', ''))

        #同意結案
        if info.get('finish_no', '') and info.get('finish_no', '') != '' and info.get('finish_no', '') != 'undefined':
            if info.get('finish_no', 'true') == 'true':
                result = result.exclude(finish_no="")
            else:
                result = result.filter(finish_no="")
            
        #缺失
        if info.get('error', '') and info.get('error', '') != '' and info.get('error', '') != 'undefined':
            key = R.POST.get('error')
            ids = []
            for k in re.split('[ ,]+', key):
                ids.extend([i.case.id for i in Error.objects.filter(ec__no__icontains=k)])
                ids.extend([i.case.id for i in Error.objects.filter(context__icontains=k)])
            result = result.filter(id__in=ids)

        all_ids = [i.id for i in result]

        paginator = Paginator(request.GET, result, resource_uri='/supervise/api/v2/supervisecase/search/')

        objects = []
        for r in paginator.page()['objects']:
            bundle = self.build_bundle(obj=r, request=request)
            bundle = self.full_dehydrate(bundle)
            objects.append(bundle)

        object_list = {
            'meta': paginator.page()['meta'],
            'objects': objects,
            'all_ids': all_ids,
        }
        
        self.log_throttled_access(request)

        return self.create_response(request, object_list)



class ErrorLevelResource(ModelResource):
    class Meta:
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        queryset = ErrorLevel.objects.all()
        always_return_data = True
        resource_name = 'errorlevel'
        ordering = ["id"]
        allowed_methods = ['get', 'post', 'put', 'delete']



class ErrorContentResource(ModelResource):
    class Meta:
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        queryset = ErrorContent.objects.all()
        always_return_data = True
        resource_name = 'errorcontent'
        ordering = ["id"]
        allowed_methods = ['get', 'post', 'put', 'delete']



class ErrorResource(ModelResource):
    case = fields.ForeignKey(SuperviseCaseResource, 'case', null=True)
    ec = fields.ForeignKey(ErrorContentResource, 'ec', null=True)
    level = fields.ForeignKey(ErrorLevelResource, 'level', null=True)
    guide = fields.ForeignKey(GuideResource, 'guide', null=True)

    class Meta:
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        queryset = Error.objects.all()
        always_return_data = True
        resource_name = 'error'
        ordering = ["id"]
        allowed_methods = ['get', 'post', 'put', 'delete']


    def dehydrate_id(self, bundle):
        if bundle.obj:
            bundle.data['case_id'] = bundle.obj.case.id
            bundle.data['case_name'] = bundle.obj.case.project
            bundle.data['case_outguide_list'] = ' '.join([i.name for i in bundle.obj.case.outguide.all()])
            bundle.data['case_inguide_list'] = ' '.join([i.name for i in bundle.obj.case.inguide.all()])
            if bundle.obj.level.name == 'L':
                bundle.data['listname_level'] = u'輕微'
            elif bundle.obj.level.name == 'M':
                bundle.data['listname_level'] = u'中等'
            elif bundle.obj.level.name == 'S':
                bundle.data['listname_level'] = u'嚴重'

        return bundle.data['id']


    def obj_update(self, bundle, **kwargs):
        if bundle.request.META.has_key('x_forwarded_for'): ip = bundle.request.META['x_forwarded_for']
        elif bundle.request.META.has_key('X_FORWARDED_FOR'): ip = bundle.request.META['X_FORWARDED_FOR']
        else: ip = bundle.request.META['REMOTE_ADDR']
        error = Error.objects.get(pk=kwargs['pk'])

        # for key in bundle.data:
        #     if key in ['ec', 'level']:
        #         new_value = bundle.data[key].split('/')[5]
        #     else:
        #         new_value = bundle.data[key]
        #     try:
        #         old_value = getattr(error, key)
        #         if key in ['ec', 'level']:
        #             old_value = old_value.id
        #         record = PCC_sync_record(
        #             user = bundle.request.user,
        #             case = error.case,
        #             ip = ip,
        #             field_name = 'error_%s' % key,
        #             old_value = old_value,
        #             new_value = new_value
        #             )
        #         record.save()
        #     except: pass
            
        return super(ErrorResource, self).obj_update(bundle, **kwargs)

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/search/$" % (self._meta.resource_name), self.wrap_view('get_search'), name="api_get_search"),
        ]


    def get_search(self, request, **kwargs):
        info = {}
        for key in request.GET.iterkeys():
            info[key] = request.GET.get(key)

        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
        self.throttle_check(request)

        # Do the query.
        result = Error.objects.all().order_by('case', 'ec__no')

        #ids
        if info.get('ids', '') and info.get('ids', '') != '' and info.get('ids', '') != 'undefined':
            ids = info.get('ids', '').split(',')
            result = result.filter(id__in=ids[:-1])

        objects = []

        for r in result:
            bundle = self.build_bundle(obj=r, request=request)
            bundle = self.full_dehydrate(bundle)
            objects.append(bundle)

        object_list = {
            'objects': objects,
        }

        self.log_throttled_access(request)
        return self.create_response(request, object_list)



class ErrorImprovePhotoResource(ModelResource):
    case = fields.ForeignKey(SuperviseCaseResource, 'case', null=True)
    error = fields.ForeignKey(ErrorResource, 'error', null=True)
    improve_type = fields.ForeignKey(OptionResource, 'improve_type', null=True)

    class Meta:
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        queryset = ErrorImprovePhoto.objects.all()
        always_return_data = True
        resource_name = 'errorimprovephoto'
        ordering = ["id"]
        allowed_methods = ['get', 'post', 'put', 'delete']

    def dehydrate_id(self, bundle):
        if bundle.obj:
            bundle.data['before_src'] = bundle.obj.rBeforeUrl()
            bundle.data['middle_src'] = bundle.obj.rMiddleUrl()
            bundle.data['after_src'] = bundle.obj.rAfterUrl()
            bundle.data['before_thumb_src'] = bundle.obj.rBeforeThumbUrl()
            bundle.data['middle_thumb_src'] = bundle.obj.rMiddleThumbUrl()
            bundle.data['after_thumb_src'] = bundle.obj.rAfterThumbUrl()
            bundle.data['table_title'] = ''
            if bundle.obj.error:
                bundle.data['table_title'] = bundle.obj.error.ec.no + ' - ' + bundle.obj.error.context
            else:
                bundle.data['table_title'] = bundle.obj.improve_type.value

        return bundle.data['id']

    def obj_update(self, bundle, request=None, **kwargs):
        f = ErrorImprovePhoto.objects.get(pk=kwargs['pk'])
        
        if 'empty' in bundle.data.get('action', ''):
            field_name = bundle.data.get('action', '').split('_')[1]
            try:
                file_name = eval('f.%s.name' % field_name)
                file_name = file_name.replace(".jpg", "_t_w51h38.jpg").replace(".jpeg", "_t_w51h38.jpeg").replace(".png", "_t_w51h38.png").replace(".tif", "_t_w51h38.tif").replace(".bmp", "_t_w51h38.bmp")
                os.remove(os.path.join(ROOT, file_name))
            except: pass
            try:
                eval('os.remove(os.path.join(ROOT, f.%s.name))' % field_name)
            except: pass
            setattr(f, field_name, None)
            f.save()

        # super(ErrorImprovePhotoResource, self).obj_update(bundle, **kwargs)
        # bundle = self.build_bundle(obj=ErrorImprovePhoto, request=request)

        # bundle = self.full_dehydrate(bundle)

        return super(ErrorImprovePhotoResource, self).obj_update(bundle, **kwargs)


    def obj_delete(self, bundle, **kwargs):
        f = ErrorImprovePhoto.objects.get(pk=kwargs['pk'])
        request = bundle.request
        try:
            file_name = f.before.name
            file_name = file_name.replace(".jpg", "_t_w51h38.jpg").replace(".jpeg", "_t_w51h38.jpeg").replace(".png", "_t_w51h38.png").replace(".tif", "_t_w51h38.tif").replace(".bmp", "_t_w51h38.bmp")
            os.remove(os.path.join(ROOT, file_name))
        except: pass
        try:
            file_name = f.middle.name
            file_name = file_name.replace(".jpg", "_t_w51h38.jpg").replace(".jpeg", "_t_w51h38.jpeg").replace(".png", "_t_w51h38.png").replace(".tif", "_t_w51h38.tif").replace(".bmp", "_t_w51h38.bmp")
            os.remove(os.path.join(ROOT, file_name))
        except: pass
        try:
            file_name = f.after.name
            file_name = file_name.replace(".jpg", "_t_w51h38.jpg").replace(".jpeg", "_t_w51h38.jpeg").replace(".png", "_t_w51h38.png").replace(".tif", "_t_w51h38.tif").replace(".bmp", "_t_w51h38.bmp")
            os.remove(os.path.join(ROOT, file_name))
        except: pass
        try:
            os.remove(os.path.join(ROOT, f.before.name))
        except: pass
        try:
            os.remove(os.path.join(ROOT, f.middle.name))
        except: pass
        try:
            os.remove(os.path.join(ROOT, f.after.name))
        except: pass

        super(ErrorImprovePhotoResource, self).obj_delete(bundle, **kwargs)



class ErrorImproveFileResource(ModelResource):
    error = fields.ForeignKey(ErrorResource, 'error', null=True)


    class Meta:
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        queryset = ErrorImproveFile.objects.all()
        always_return_data = True
        resource_name = 'errorimprovefile'
        ordering = ["id"]
        allowed_methods = ['get', 'post', 'put', 'delete']

    def obj_delete(self, bundle, **kwargs):
        f = ErrorImproveFile.objects.get(pk=kwargs['pk'])
        request = bundle.request
        try:
            os.remove(f.file.path)
        except: pass
        super(ErrorImproveFileResource, self).obj_delete(bundle, **kwargs)



class ErrorPhotoFileResource(ModelResource):
    supervisecase = fields.ForeignKey(SuperviseCaseResource, 'supervisecase', null=True)


    class Meta:
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        queryset = ErrorPhotoFile.objects.all()
        always_return_data = True
        resource_name = 'errorphotofile'
        ordering = ["id"]
        allowed_methods = ['get', 'post', 'put', 'delete']

    def obj_delete(self, bundle, **kwargs):
        f = ErrorPhotoFile.objects.get(pk=kwargs['pk'])
        request = bundle.request
        try:
            os.remove(f.file.path)
        except: pass
        super(ErrorPhotoFileResource, self).obj_delete(bundle, **kwargs)



class CaseFileResource(ModelResource):
    supervisecase = fields.ForeignKey(SuperviseCaseResource, 'supervisecase', null=True)


    class Meta:
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        queryset = CaseFile.objects.all()
        always_return_data = True
        resource_name = 'casefile'
        ordering = ["id"]
        allowed_methods = ['get', 'post', 'put', 'delete']

    def obj_delete(self, bundle, **kwargs):
        f = CaseFile.objects.get(pk=kwargs['pk'])
        request = bundle.request
        try:
            os.remove(f.file.path)
        except: pass
        super(CaseFileResource, self).obj_delete(bundle, **kwargs)



class PCC_ProjectResource(ModelResource):

    class Meta:
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        queryset = PCC_Project.objects.all()
        always_return_data = True
        resource_name = 'pcc_project'
        ordering = ["id"]
        allowed_methods = ['get', 'post', 'put', 'delete']


    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/search/$" % (self._meta.resource_name), self.wrap_view('get_search'), name="api_get_search"),
        ]

    def get_search(self, request, **kwargs):
        info = {}
        for key in request.GET.iterkeys():
            info[key] = request.GET.get(key)

        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
        self.throttle_check(request)
        # Do the query.
        result = PCC_Project.objects.all().order_by('implementation_department', 'name', 'r_decide_tenders_date')

        #ids
        if info.get('ids', '') and info.get('ids', '') != '' and info.get('ids', '') != 'undefined':
            ids = info.get('ids', '').split(',')
            result = result.filter(id__in=ids[:-1])

        #標案名稱
        if info.get('name', '') and info.get('name', '') != '' and info.get('name', '') != 'undefined':
            ids = []
            for key in re.split('[ ,]+', info.get('name', '')):
                if key:
                    ids.extend([i.id for i in result.filter(name__icontains=key)])
            result = result.filter(id__in=ids)
        
        #執行機關
        if info.get('implementation_department', '') and info.get('implementation_department', '') != '' and info.get('implementation_department', '') != 'undefined':
            ids = []
            for key in re.split('[ ,]+', info.get('implementation_department', '')):
                if key:
                    ids.extend([i.id for i in result.filter(implementation_department__icontains=key)])
            result = result.filter(id__in=ids)

        #標案編號
        if info.get('uid', '') and info.get('uid', '') != '' and info.get('uid', '') != 'undefined':
            ids = []
            for key in re.split('[ ,]+', info.get('uid', '')):
                if key:
                    ids.extend([i.id for i in result.filter(uid__icontains=key)])
            result = result.filter(id__in=ids)
        
        #發包預算
        if info.get('contract_budget_from', '') and info.get('contract_budget_from', '') != '' and info.get('contract_budget_from', '') != 'undefined':
            contract_budget_from = str(float(info.get('contract_budget_from', '')) * 1000)
            contract_budget_to = str(float(info.get('contract_budget_to', '')) * 1000)
            result = result.filter(contract_budget__gte=contract_budget_from, contract_budget__lte=contract_budget_to)

        #決標金額
        if info.get('decide_tenders_price_from', '') and info.get('decide_tenders_price_from', '') != '' and info.get('decide_tenders_price_from', '') != 'undefined':
            decide_tenders_price_from = str(float(info.get('decide_tenders_price_from', '')) * 1000)
            decide_tenders_price_to = str(float(info.get('decide_tenders_price_to', '')) * 1000)
            result = result.filter(decide_tenders_price__gte=decide_tenders_price_from, decide_tenders_price__lte=decide_tenders_price_to)
        
        #預定進度
        if info.get('percentage_of_predict_progress_from', '') and info.get('percentage_of_predict_progress_from', '') != '' and info.get('percentage_of_predict_progress_from', '') != 'undefined':
            result = result.filter(percentage_of_predict_progress__gte=info.get('percentage_of_predict_progress_from', ''), percentage_of_predict_progress__lte=info.get('percentage_of_predict_progress_to', ''))
        
        #實際進度
        if info.get('percentage_of_real_progress_from', '') and info.get('percentage_of_real_progress_from', '') != '' and info.get('percentage_of_real_progress_from', '') != 'undefined':
            result = result.filter(percentage_of_real_progress__gte=info.get('percentage_of_real_progress_from', ''), percentage_of_real_progress__lte=info.get('percentage_of_real_progress_to', ''))
        
        #差異
        if info.get('percentage_of_dulta_from', '') and info.get('percentage_of_dulta_from', '') != '' and info.get('percentage_of_dulta_from', '') != 'undefined':
            result = result.filter(percentage_of_dulta__gte=info.get('percentage_of_dulta_from', ''), percentage_of_dulta__lte=info.get('percentage_of_dulta_to', ''))

        objects = []

        for r in result:
            bundle = self.build_bundle(obj=r, request=request)
            bundle = self.full_dehydrate(bundle)
            objects.append(bundle)

        object_list = {
            'objects': objects,
        }

        self.log_throttled_access(request)
        return self.create_response(request, object_list)



class PCCProjectResource(ModelResource):

    class Meta:
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        queryset = PCCProject.objects.all()
        always_return_data = True
        resource_name = 'pccproject'
        ordering = ["id"]
        allowed_methods = ['get', 'put']
        filtering = {
            'chase': ALL_WITH_RELATIONS,
            'on_pcc_now': ALL_WITH_RELATIONS,
            'uid': ALL_WITH_RELATIONS,
            'host_department': ALL_WITH_RELATIONS,
            'implementation_department': ALL_WITH_RELATIONS,
            'name': ALL_WITH_RELATIONS,
            'contract_budget': ALL_WITH_RELATIONS,
            'decide_tenders_price': ALL_WITH_RELATIONS,
            'planning_unit': ALL_WITH_RELATIONS,
            'design_unit': ALL_WITH_RELATIONS,
            'inspector_name': ALL_WITH_RELATIONS,
            'project_manage_unit': ALL_WITH_RELATIONS,
            'constructor': ALL_WITH_RELATIONS,
            'engineering_county': ALL_WITH_RELATIONS,
            'project_memo': ALL_WITH_RELATIONS,
            'percentage_of_predict_progress': ALL_WITH_RELATIONS,
            'percentage_of_real_progress': ALL_WITH_RELATIONS,
            'percentage_of_dulta': ALL_WITH_RELATIONS,
            'head_department': ALL_WITH_RELATIONS,
            'r_start_date': ALL_WITH_RELATIONS,
            'r_decide_tenders_date': ALL_WITH_RELATIONS,
        }

class CofigurationResource(ModelResource):
    class Meta:
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        queryset = Cofiguration.objects.all()
        always_return_data = True
        resource_name = 'cofiguration'
        ordering = ["id"]
        allowed_methods = ['get', 'put', 'patch']

