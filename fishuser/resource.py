#-*- coding: utf8 -*-
import logging, datetime, re, json, traceback, sys, decimal

from django.http import HttpResponse
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
from fishuser.models import Option, UserProfile, CencelLoginEmail, LoginHistory, UnitManager
from fishuser.models import WrongLogin, Plan, PlanReserve, PlanBudget, Project, ProjectBidMoney, Draft_Project, Project_Port
from fishuser.models import DefaultProject, FRCMUserGroup, Factory, RelayInfo, Fund, Budget
from fishuser.models import FundRecord, Appropriate, Reserve, Progress, ProjectPhoto, FRCMTempFile
from fishuser.models import ScheduledProgress, BudgetProject, CountyChaseTime, CountyChaseTimeNewUpdate
from fishuser.models import CountyChaseProjectOneByOne, CountyChaseProjectOneToMany, CountyChaseProjectOneToManyPayout
from fishuser.models import Allocation, Project_Secret_Memo, DocumentFile, EmailList
from fishuser.models import ManageMoney, ProjectManageMoney, ManageMoneyRemain
from fishuser.models import ProjectBidMoneyVersion, ProjectBidMoneyVersionDetail
from fishuser.models import SystemInformation, SystemInformationFile
from harbor.models import FishingPort
from harbor.models import Aquaculture
from harbor.resource import FishingPortResource, AquacultureResource
from dailyreport.models import Version
from dailyreport.models import EngProfile
from pccmating.models import Project as PCC_Project
# from hoabor.resource import FishingPortResource, AquacultureResource
from pccmating.sync import getProjectInfo
from pccmating.models import ProjectProgress as PCC_ProjectProgress
from django.conf import settings
CAN_VIEW_BUG_PAGE_IPS = settings.CAN_VIEW_BUG_PAGE_IPS
NUMPERPAGE = settings.NUMPERPAGE
ROOT = settings.ROOT


TODAY = lambda: datetime.date.today()
NOW = lambda: datetime.datetime.now()

API_LIMIT_PER_PAGE = settings.API_LIMIT_PER_PAGE

__enable__ = [
                'UserResource',
                'GroupResource',
                'PlaceResource',
                'UnitResource',
                'UnitManagerResource',
                'UserProfileResource',
                'OptionResource',
                'PlanResource',
                'PlanReserveResource',
                'PlanBudgetResource',
                'ProjectResource',
                'ProjectBidMoneyResource',
                'Draft_ProjectResource',
                'DefaultProjectResource',
                'FRCMUserGroupResource',
                'FundResource',
                'BudgetResource',
                'AppropriateResource',
                'EmailListResource',
                'AllocationResource',
                'CountyChaseTimeResource',
                'CountyChaseTimeNewUpdateResource',
                'CountyChaseProjectOneByOneResource',
                'CountyChaseProjectOneToManyResource',
                'CountyChaseProjectOneToManyPayoutResource',
                'ProjectPhotoResource',
                'ManageMoneyResource',
                'ProjectManageMoneyResource',
                'ManageMoneyRemainResource',
                'ProjectBidMoneyVersionResource',
                'ProjectBidMoneyVersionDetailResource',
                'SystemInformationResource',
                'SystemInformationFileResource',
                ]

class RESTForbidden(Exception):
    pass



class SillyAuthentication(Authentication):
    def is_authenticated(self, request, **kwargs):
        if settings.DEBUG: logging.info('SillyAuthentication: %s' % request.user.is_authenticated())
        return request.user.is_authenticated()



class UserResource(ModelResource):
    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'
        ordering = ["username"]
        excludes = ['password', 'is_superuser', 'is_staff']
        allowed_methods = ['get', 'put']
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        filtering = {
            "username": ("exact", ),
        }
        paginator_class = Paginator

    def obj_update(self, bundle, request=None, **kwargs):
        obj_user = User.objects.get(pk=kwargs['pk'])
        user = bundle.request.user
        if obj_user != user and not user.is_staff and not user.has_perm('fishuser.top_menu_account'):
            raise ImmediateHttpResponse(response=http.HttpBadRequest(_(u'You have no permission。')))
        super(UserResource, self).obj_update(bundle, **kwargs)
        return bundle

    def obj_delete(self, bundle, **kwargs):
        obj_user = User.objects.get(pk=kwargs['pk'])
        user = bundle.request.user
        if obj_user != user and not user.is_staff and not user.has_perm('fishuser.top_menu_account'):
            raise ImmediateHttpResponse(response=http.HttpBadRequest(_(u'You have no permission。')))
        super(UserResource, self).obj_delete(bundle, **kwargs)

    def obj_get_list(self, bundle, **kwargs):
        user = bundle.request.user
        if not user.is_staff and not user.has_perm('fishuser.top_menu_account'):
            raise ImmediateHttpResponse(response=http.HttpBadRequest(_(u'You have no permission。')))

    def dehydrate_username(self, bundle):
        user = bundle.request.user
        obj_user = bundle.obj
        
        if obj_user != user and not user.is_staff and not user.has_perm('fishuser.top_menu_account'):
            return {}

        if bundle.obj:
            bundle.data['groups'] = [[g.id, g.name] for g in bundle.obj.groups.all()]
            bundle.data['groups_name'] = '<br>'.join([g.name for g in bundle.obj.groups.all()])
            bundle.data['listname_is_active'] = '開啟' if bundle.obj.is_active else '關閉'
            bundle.data['login_times'] = bundle.obj.loginhistory_set.all().count()
            row = UserProfile.objects.get_or_create(user=bundle.obj)
            row = UserProfile.objects.get(user=bundle.obj)
            bundle.data['projectup_id'] = row.id
            bundle.data['title'] = row.title if row.title else ''
            bundle.data['unit_id'] = row.unit.id if row.unit else ''
            bundle.data['listname_unit'] = row.unit.name if row.unit else ''
            bundle.data['fax'] = row.fax if row.fax else ''
            bundle.data['phone'] = row.phone if row.phone else ''

        return bundle.data['username']


    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/search/$" % (self._meta.resource_name), self.wrap_view('get_user_search'), name="api_get_user_search"),
        ]


    def get_user_search(self, request, **kwargs):
        info = {}
        for key in request.GET.iterkeys():
            info[key] = request.GET.get(key)

        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
        self.throttle_check(request)
        # Do the query.
        user = User.objects.get(id=info['user_id'])

        if u'縣市帳號管理員' in [g.name for g in user.groups.all()]:
            unit = user.user_profile.unit
            can_use_group_ids = [1,3,10]
            result = User.objects.filter(id__gte=0, username__startswith=user.username[:2]).order_by('username', 'last_name', 'first_name')
        else:
            can_use_group_ids = [1,3,4,5,6,7,8,9,10,26,27,28,30,31]
            result = User.objects.filter(id__gte=0).order_by('username', 'last_name', 'first_name')

        if user.is_staff:
            can_use_group_ids = [g.id for g in Group.objects.all()]
        groups = Group.objects.filter(id__in=can_use_group_ids).order_by('name')
        #群組
        if info.get('group', '') and info.get('group', '') != '' and info.get('group', '') != 'undefined':
            result = result.filter(groups__id=info.get('group', ''))
        else:
            ids = []
            for g in groups:
                ids.extend([u.id for u in result.filter(groups=g)])
            ids.extend([u.id for u in result.filter(groups=None)])
            result = result.filter(id__in=ids)
        #帳號
        if info.get('username', '') and info.get('username', '') != '' and info.get('username', '') != 'undefined':
            ids = []
            for key in re.split('[ ,]+', info.get('username', '')):
                ids.extend([i.id for i in result.filter(username__icontains=key)])
            result = result.filter(id__in=ids)
        #姓
        if info.get('last_name', '') and info.get('last_name', '') != '' and info.get('last_name', '') != 'undefined':
            ids = []
            for key in re.split('[ ,]+', info.get('last_name', '')):
                ids.extend([i.id for i in result.filter(last_name__icontains=key)])
            result = result.filter(id__in=ids)
        #名
        if info.get('first_name', '') and info.get('first_name', '') != '' and info.get('first_name', '') != 'undefined':
            ids = []
            for key in re.split('[ ,]+', info.get('first_name', '')):
                ids.extend([i.id for i in result.filter(first_name__icontains=key)])
            result = result.filter(id__in=ids)
        #執行機關
        if info.get('unit', '') and info.get('unit', '') != '' and info.get('unit', '') != 'undefined':
            unit = Unit.objects.get(id=info.get('unit', ''))
            if unit.uplevel.fullname == u'農業部漁業署':
                ups = UserProfile.objects.filter(unit=unit)
            else:
                ups = UserProfile.objects.filter(unit__place=unit.place)
            ids = [u.user.id for u in ups]
            result = result.filter(id__in=ids).order_by('user_profile__unit')


        paginator = Paginator(request.GET, result, resource_uri='/fishuser/api/v2/user/search/')

        objects = []
        for r in paginator.page()['objects']:
            bundle = self.build_bundle(obj=r, request=request)
            bundle = self.full_dehydrate(bundle)
            objects.append(bundle)

        object_list = {
            'meta': paginator.page()['meta'],
            'objects': objects,
        }

        self.log_throttled_access(request)

        return self.create_response(request, object_list)



class GroupResource(ModelResource):
    class Meta:
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        queryset = Group.objects.all()
        resource_name = 'group'
        ordering = ["id"]
        allowed_methods = ['get']



class PlaceResource(ModelResource):
    parent = fields.ForeignKey('self', 'parent', null=True)



    class Meta:
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        queryset = Place.objects.all()
        resource_name = 'place'
        ordering = ["zipcode"]
        allowed_methods = ['get', 'post', 'put']
        filtering = {
            "id": ("exact", ),
            "uplevel": ("exact",),
        }



class UnitResource(ModelResource):
    place = fields.ForeignKey(PlaceResource, 'place', null=True)
    uplevel = fields.ForeignKey('self', 'uplevel', null=True)

    class Meta:
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        queryset = Unit.objects.all()
        resource_name = 'unit'
        ordering = ["name"]
        allowed_methods = ['get', 'post', 'put']
        filtering = {
            "id": ("exact", ),
            "uplevel": ("exact", "isnull"),
        }

    def obj_create(self, bundle, request=None, **kwargs):
        user = bundle.request.user
        if not user.has_perm('fishuser.sub_menu_management_system_create'):
            raise ImmediateHttpResponse(response=http.HttpBadRequest(_(u'You have no permission。')))

        bundle.obj = Unit()
        for key, value in kwargs.items():
            setattr(bundle.obj, key, value)
        bundle = self.full_hydrate(bundle)
        self.save_related(bundle)

        bundle.obj.save()

        # m2m_bundle = self.hydrate_m2m(bundle)
        # self.save_m2m(m2m_bundle)
        # unit = bundle.obj
        
        # unit.save()

        return bundle

    def dehydrate_no(self, bundle):
        if bundle.obj:
            bundle.data['listname_place'] = bundle.obj.place.name if bundle.obj.place else ''

        return bundle.data['no']

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/search/$" % (self._meta.resource_name), self.wrap_view('get_unit_search'), name="api_get_unit_search"),
        ]
        
    def get_unit_search(self, request, **kwargs):
        info = {}
        for key in request.GET.iterkeys():
            info[key] = request.GET.get(key)
        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
        self.throttle_check(request)
    
        # unit = Unit.objects.get(id=info['unit_id'])
        result=Unit.objects.all()
        #機關名稱
        if info.get('name', '') and info.get('name', '') != '' and info.get('name', '') != 'undefined':
            ids = []
            for key in re.split('[ ,]+', info.get('name', '')):
                ids.extend([i.id for i in result.filter(name__icontains=key)])
            result = result.filter(id__in=ids)
        #電話
        if info.get('phone', '') and info.get('phone', '') != '' and info.get('phone', '') != 'undefined':
            ids = []
            for key in re.split('[ ,]+', info.get('phone', '')):
                ids.extend([i.id for i in result.filter(phone__icontains=key)])
            result = result.filter(id__in=ids)
        #負責人
        if info.get('chairman', '') and info.get('chairman', '') != '' and info.get('chairman', '') != 'undefined':
            ids = []
            for key in re.split('[ ,]+', info.get('chairman', '')):
                ids.extend([i.id for i in result.filter(chairman__icontains=key)])
            result = result.filter(id__in=ids)
        #地址
        if info.get('address', '') and info.get('address', '') != '' and info.get('address', '') != 'undefined':
            ids = []
            for key in re.split('[ ,]+', info.get('address', '')):
                ids.extend([i.id for i in result.filter(address__icontains=key)])
            result = result.filter(id__in=ids)
        #對搜尋結果做排序(依id排序)
        result = sorted(result, key=lambda result: result.id)

        paginator = Paginator(request.GET, result, resource_uri='/fishuser/api/v2/unit/search/')
        objects = []
        for r in paginator.page()['objects']:
            bundle = self.build_bundle(obj=r, request=request)
            bundle = self.full_dehydrate(bundle)
            objects.append(bundle)

        object_list = {
            'meta': paginator.page()['meta'],
            'objects': objects,
        }
        self.log_throttled_access(request)

        return self.create_response(request, object_list)



class UnitManagerResource(ModelResource):
    unit = fields.ForeignKey(UnitResource, 'unit', full=True)

    class Meta:
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        queryset = UnitManager.objects.all()
        resource_name = 'unitmanager'
        ordering = ["name"]
        always_return_data = True
        allowed_methods = ['get', 'post', 'put', 'delete']
        filtering = {
            "id": ("exact", ),
            "unit": ("exact", ),
        }



class UserProfileResource(ModelResource):
    user = fields.ForeignKey(UserResource, 'user')
    unit = fields.ForeignKey(UnitResource, 'unit', null=True)

    class Meta:
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        queryset = UserProfile.objects.all()
        resource_name = 'userprofile'
        ordering = ["user"]
        allowed_methods = ['get', 'post', 'put']
        filtering = {
            "user": ("exact", ),
        }


    def dehydrate_id(self, bundle):
        if bundle.obj:
            bundle.data['listname_unit'] = bundle.obj.unit.name if bundle.obj.unit else ''

        return bundle.data['id']



class OptionResource(ModelResource):
    class Meta:
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        queryset = Option.objects.all()
        resource_name = 'option'
        ordering = ["swarm"]
        allowed_methods = ['get', 'post', 'put']



class CencelLoginEmailResource(ModelResource):
    user = fields.ForeignKey(UserResource, 'user')
    class Meta:
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        queryset = CencelLoginEmail.objects.all()
        resource_name = 'cencelloginemail'
        ordering = ["id"]
        allowed_methods = ['get', 'post', 'put', 'delete']



class LoginHistoryResource(ModelResource):
    user = fields.ForeignKey(UserResource, 'user')
    class Meta:
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        queryset = LoginHistory.objects.all()
        resource_name = 'loginhistory'
        ordering = ["id"]
        allowed_methods = ['get', 'post', 'put', 'delete']



class PlanResource(ModelResource):
    budget_type = fields.ForeignKey(OptionResource, 'budget_type')
    plan_class = fields.ForeignKey(OptionResource, 'plan_class', null=True)
    uplevel = fields.ForeignKey('self', 'uplevel', null=True)

    class Meta:
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        queryset = Plan.objects.all()
        always_return_data = True
        resource_name = 'plan'
        ordering = ["name", "sort", 'id']
        allowed_methods = ['get', 'post', 'put', 'delete']
        filtering = {
            "id": ("exact"),
            "uplevel": ("exact", "isnull"),
        }

    def obj_update(self, bundle, request=None, **kwargs):
        plan = Plan.objects.get(pk=kwargs['pk'])
        user = bundle.request.user
        super(PlanResource, self).obj_update(bundle, **kwargs)

        if bundle.data.get('submit', '') == 'update_sort':
            target = Plan.objects.get(id=bundle.data.get('row_id', ''))
            for p in Plan.objects.filter(uplevel=plan.uplevel, sort__gt=plan.sort):
                p.sort = str(float(str(p.sort)) - 1)
                p.save()
            if bundle.data.get('site', '') == 'front':
                sort = target.sort
                for p in Plan.objects.filter(uplevel=target.uplevel, sort__gte=target.sort):
                    p.sort = str(float(str(p.sort)) + 1)
                    p.save()
                plan.uplevel = target.uplevel
                plan.sort = sort
                plan.save()
            elif bundle.data.get('site', '') == 'sub':
                for p in Plan.objects.filter(uplevel=target):
                    p.sort = str(float(str(p.sort)) + 1)
                    p.save()
                plan.uplevel = target
                plan.sort = '1'
                plan.save()
        bundle = self.build_bundle(obj=plan, request=request)
        bundle = self.full_dehydrate(bundle)
        return bundle

    def obj_delete(self, bundle, **kwargs):
        p = Plan.objects.get(pk=kwargs['pk'])
        if p.rSubPlanInList():
            raise ImmediateHttpResponse(response=http.HttpBadRequest(_(u'無法刪除，此計畫尚有 %s 個子計畫。' % len(p.rSubPlanInList()))))

        if Project.objects.filter(plan=p).exclude(deleter=None):
            raise ImmediateHttpResponse(response=http.HttpBadRequest(_(u'無法刪除，此計畫尚有 %s 個工程案。' % (Project.objects.filter(plan=p).exclude(deleter=None).count()))))
        
        super(PlanResource, self).obj_delete(bundle, **kwargs)



class PlanReserveResource(ModelResource):
    plan = fields.ForeignKey(PlanResource, 'plan')

    class Meta:
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        always_return_data = True
        queryset = PlanReserve.objects.all()
        resource_name = 'planreserve'
        allowed_methods = ['get', 'post', 'put', 'delete']



class PlanBudgetResource(ModelResource):
    plan = fields.ForeignKey(PlanResource, 'plan')

    class Meta:
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        always_return_data = True
        queryset = PlanBudget.objects.all()
        resource_name = 'planbudget'
        allowed_methods = ['get', 'post', 'put', 'delete']


    def obj_create(self, bundle, request=None, **kwargs):
        user = bundle.request.user
        if not user.has_perm('fishuser.sub_menu_management_system_create'):
            raise ImmediateHttpResponse(response=http.HttpBadRequest(_(u'You have no permission。')))

        if PlanBudget.objects.filter(plan__id=bundle.data['plan'].split('/')[-2], year=bundle.data['year']):
            raise ImmediateHttpResponse(response=http.HttpBadRequest(_(u'無法新增，已有 %s 年度 預算。' % bundle.data['year'])))

        bundle.obj = PlanBudget()
        for key, value in kwargs.items():
            setattr(bundle.obj, key, value)
        bundle = self.full_hydrate(bundle)
        self.save_related(bundle)
        bundle.obj.save()
        target = bundle.obj
        while target.plan.uplevel:
            if not PlanBudget.objects.filter(plan=target.plan.uplevel, year=target.year):
                row = PlanBudget(
                        plan = target.plan.uplevel,
                        year = target.year,
                    )
                row.save()
            else:
                row = PlanBudget.objects.get(plan=target.plan.uplevel, year=target.year)
            target = row

        return bundle

    def obj_delete(self, bundle, **kwargs):
        pb = PlanBudget.objects.get(pk=kwargs['pk'])
        if PlanBudget.objects.filter(plan__in=pb.plan.rSubPlanInList(), year=pb.year):
            raise ImmediateHttpResponse(response=http.HttpBadRequest(_(u'無法刪除，子計畫尚有 %s 年度 預算。' % pb.year)))

        super(PlanBudgetResource, self).obj_delete(bundle, **kwargs)



class ProjectResource(ModelResource):
    plan = fields.ForeignKey(PlanResource, 'plan', null=True)
    project_type = fields.ForeignKey(OptionResource, 'project_type')
    project_sub_type = fields.ForeignKey(OptionResource, 'project_sub_type', null=True)
    undertake_type = fields.ForeignKey(OptionResource, 'undertake_type')
    budget_type = fields.ForeignKey(OptionResource, 'budget_type')
    budget_sub_type = fields.ForeignKey(OptionResource, 'budget_sub_type')
    purchase_type = fields.ForeignKey(OptionResource, 'purchase_type')
    place = fields.ForeignKey(PlaceResource, 'place')
    fishing_port = fields.ToManyField(FishingPortResource, 'fishing_port', full=True, null=True)
    aquaculture = fields.ToManyField(AquacultureResource, 'aquaculture', full=True, null=True)
    unit = fields.ForeignKey(UnitResource, 'unit')
    status = fields.ForeignKey(OptionResource, 'status', null=True)
    deleter = fields.ForeignKey(UserResource, 'deleter', null=True)
    bid_type = fields.ForeignKey(OptionResource, 'bid_type', null=True)
    contract_type = fields.ForeignKey(OptionResource, 'contract_type', null=True)
    contractor = fields.ForeignKey(UnitResource, 'contractor', null=True)
    inspector = fields.ForeignKey(UnitResource, 'inspector', null=True)
    frcm_inspector_type = fields.ForeignKey(OptionResource, 'frcm_inspector_type', null=True)
    frcm_duration_type = fields.ForeignKey(OptionResource, 'frcm_duration_type', null=True)
    progress_type = fields.ForeignKey(OptionResource, 'progress_type', null=True)
    ex_project = fields.ForeignKey('self', 'ex_project', null=True)

    class Meta:
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        queryset = Project.objects.all()
        always_return_data = True
        resource_name = 'project'
        ordering = ["name"]
        allowed_methods = ['get', 'post', 'put', 'delete']
        paginator_class = Paginator


    def obj_delete(self, bundle, **kwargs):
        p = Project.objects.get(pk=kwargs['pk'])
        p.dailyreport_engprofile.filter().delete()
        p.frcmusergroup_set.filter().delete()

        super(ProjectResource, self).obj_delete(bundle, **kwargs)


    def dehydrate_name(self, bundle):
        if bundle.obj:
            bundle.data['listname_plan'] = bundle.obj.plan.name if bundle.obj.plan else ''
            bundle.data['listname_place'] = bundle.obj.place.name if bundle.obj.place else ''
            bundle.data['listname_unit'] = bundle.obj.unit.name if bundle.obj.unit else ''
            bundle.data['listname_deleter'] = bundle.obj.deleter.user_profile.rName() if bundle.obj.deleter else ''
            bundle.data['listname_contractor'] = bundle.obj.contractor.name if bundle.obj.contractor else ''
            bundle.data['listname_inspector'] = bundle.obj.inspector.name if bundle.obj.inspector else ''
            bundle.data['listname_project_type'] = bundle.obj.project_type.value if bundle.obj.project_type else ''
            bundle.data['listname_project_sub_type'] = bundle.obj.project_sub_type.value if bundle.obj.project_sub_type else ''
            bundle.data['listname_undertake_type'] = bundle.obj.undertake_type.value if bundle.obj.undertake_type else ''
            bundle.data['listname_budget_type'] = bundle.obj.budget_type.value if bundle.obj.budget_type else ''
            bundle.data['listname_budget_sub_type'] = bundle.obj.budget_sub_type.value if bundle.obj.budget_sub_type else ''
            bundle.data['listname_purchase_type'] = bundle.obj.purchase_type.value if bundle.obj.purchase_type else ''
            bundle.data['listname_status'] = bundle.obj.status.value if bundle.obj.status else ''
            bundle.data['listname_bid_type'] = bundle.obj.bid_type.value if bundle.obj.bid_type else ''
            bundle.data['listname_contract_type'] = bundle.obj.contract_type.value if bundle.obj.contract_type else ''
            bundle.data['listname_frcm_inspector_type'] = bundle.obj.frcm_inspector_type.value if bundle.obj.frcm_inspector_type else ''
            bundle.data['listname_frcm_duration_type'] = bundle.obj.frcm_duration_type.value if bundle.obj.frcm_duration_type else ''
            bundle.data['listname_progress_type'] = bundle.obj.progress_type.value if bundle.obj.progress_type else ''
            # bundle.data['plan__name'] = bundle.obj.plan.name if bundle.obj.plan else ''
            bundle.data['plan__name__list'] = u''.join([u'●%s' % i.plan.name for i in Budget.objects.filter(fund__project=bundle.obj, plan__isnull=False)])
            bundle.data['place__name'] = bundle.obj.place.name if bundle.obj.place else ''
            bundle.data['unit__name'] = bundle.obj.unit.name if bundle.obj.unit else ''
            bundle.data['deleter__name'] = bundle.obj.deleter.user_profile.rName() if bundle.obj.deleter else ''
            bundle.data['contractor__name'] = bundle.obj.contractor.name if bundle.obj.contractor else ''
            bundle.data['inspector__name'] = bundle.obj.inspector.name if bundle.obj.inspector else ''
            bundle.data['project_type__value'] = bundle.obj.project_type.value if bundle.obj.project_type else ''
            bundle.data['project_sub_type__value'] = bundle.obj.project_sub_type.value if bundle.obj.project_sub_type else ''
            bundle.data['undertake_type__value'] = bundle.obj.undertake_type.value if bundle.obj.undertake_type else ''
            bundle.data['budget_type__value'] = bundle.obj.budget_type.value if bundle.obj.budget_type else ''
            bundle.data['budget_sub_type__value'] = bundle.obj.budget_sub_type.value if bundle.obj.budget_sub_type else ''
            bundle.data['purchase_type__value'] = bundle.obj.purchase_type.value if bundle.obj.purchase_type else ''
            bundle.data['status__value'] = bundle.obj.status.value if bundle.obj.status else ''
            bundle.data['bid_type__value'] = bundle.obj.bid_type.value if bundle.obj.bid_type else ''
            bundle.data['contract_type__value'] = bundle.obj.contract_type.value if bundle.obj.contract_type else ''
            bundle.data['frcm_inspector_type__value'] = bundle.obj.frcm_inspector_type.value if bundle.obj.frcm_inspector_type else ''
            bundle.data['frcm_duration_type__value'] = bundle.obj.frcm_duration_type.value if bundle.obj.frcm_duration_type else ''
            bundle.data['progress_type__value'] = bundle.obj.progress_type.value if bundle.obj.progress_type else ''
            # [bundle.data['manage'], bundle.data['settlement_manage']] = bundle.obj.set_manage_money()

            try: 
                bundle.data['importer'] = bundle.obj.frcmusergroup_set.get(group__name__in=[u'負責主辦工程師', u'自辦主辦工程師']).user.user_profile.rName()
                if bundle.obj.frcmusergroup_set.get(group__name__in=[u'負責主辦工程師', u'自辦主辦工程師']).user == bundle.request.user:
                    bundle.data['is_self'] = True
            except: 
                bundle.data['importer'] = ''
            bundle.data["images_count"] = bundle.obj.rGalleryPics() if bundle.obj.use_gallery else bundle.obj.rFRCMAlreadyUploadPics()
            # bundle.data["act_inspector_percent"] = bundle.obj.get_act_inspector_percent()
            # bundle.data["act_contractor_percent"] = bundle.obj.get_act_contractor_percent()
            #取得工程進度
            bundle.data["pcc_s_percent"] = 0
            bundle.data["pcc_a_percent"] = 0

            progress = PCC_ProjectProgress.objects.filter(project__uid=bundle.obj.pcc_no).order_by('-year', '-month')
            engprofile = bundle.obj.dailyreport_engprofile.filter()
            if progress:
                #第一步 找看看工程會同步資料有沒有
                progress = progress.first()
                bundle.data["pcc_s_percent"] = round(progress.percentage_of_predict_progress*100, 2) 
                bundle.data["pcc_a_percent"] = round(progress.percentage_of_real_progress*100, 2)
            elif engprofile:
                #第二步 找日報表有沒有
                engprofile = engprofile.first()
                if engprofile.design_percent or engprofile.act_inspector_percent:
                    bundle.data["pcc_s_percent"] = round(float(str(engprofile.design_percent)), 2)
                    bundle.data["pcc_a_percent"] = round(float(str(engprofile.act_inspector_percent)), 2)
            #第三步 找看看進度追蹤
            if not bundle.data["pcc_s_percent"] and not bundle.data["pcc_a_percent"]:
                chases = CountyChaseProjectOneToMany.objects.filter(complete=True, project=bundle.obj).order_by('-id')
                if chases:
                    chase = chases.first()
                    bundle.data["pcc_s_percent"] = round(float(str(chase.schedul_progress_percent)), 2)
                    bundle.data["pcc_a_percent"] = round(float(str(chase.actual_progress_percent)), 2)

            #工程契約金額
            version = Version.objects.filter(project__id = bundle.obj.id).first()
            try:
                if bundle.obj.pcc_no:
                    pcc_project = PCC_Project.objects.get(uid = bundle.obj.pcc_no)
                    if not pcc_project.decide_tenders_price2 or pcc_project.decide_tenders_price2 == 0:
                        bundle.data["engs_price"] = str(int(pcc_project.decide_tenders_price)) + '元'
                    else:
                        bundle.data["engs_price"] = str(int(pcc_project.decide_tenders_price2)) + '元'
                elif version and version.engs_price:
                    bundle.data["engs_price"] = str(int(version.engs_price)) + '元'
                elif bundle.obj.construction_bid:
                    bundle.data["engs_price"] = str(int(bundle.obj.construction_bid)) + '元'
                elif bundle.obj.total_money:
                    bundle.data["engs_price"] = str(int(bundle.obj.total_money)) + '元'
                        
                else:
                    bundle.data["engs_price"] =  '0元'
            except:
                if version and version.engs_price:
                    bundle.data["engs_price"] = str(int(version.engs_price)) + '元'
                elif bundle.obj.construction_bid:
                    bundle.data["engs_price"] = str(int(bundle.obj.construction_bid)) + '元'
                elif bundle.obj.total_money:
                    bundle.data["engs_price"] = str(int(bundle.obj.total_money)) + '元'
                        
                else:
                    bundle.data["engs_price"] =  '0元'
            #實際累計完成金額
            bundle.data["act_money"] = str(int(bundle.data["pcc_a_percent"] * int(bundle.data["engs_price"].replace('元','')))/100) + '元'
            #     bundle.data["default_project"] = 'checked' if DefaultProject.objects.filter(user=bundle.request.user, project=bundle.obj) else '

            chase_time = CountyChaseTime.objects.all().order_by('-id')[0]
            if CountyChaseProjectOneToMany.objects.filter(countychasetime=chase_time, project=bundle.obj):
                bundle.data["chase_project"] = True
                bundle.data["chase_otm_id"] = CountyChaseProjectOneToMany.objects.filter(countychasetime=chase_time, project=bundle.obj)[0].id
            obo = CountyChaseProjectOneByOne.objects.get(project=bundle.obj)
            if bundle.obj.purchase_type.value in [u'工程', u'工程勞務'] and obo.act_eng_do_closed:
                bundle.data["is_close"] = True
            elif bundle.obj.purchase_type.value in [u'一般勞務'] and obo.act_ser_acceptance_closed:
                bundle.data["is_close"] = True
            else:
                bundle.data["is_close"] = False
            fishing_ports = '\n'.join([f.name for f in bundle.obj.fishing_port.all()])
            aquacultures = '\n'.join([a.name for a in bundle.obj.aquaculture.all()])

            bundle.data["fishing_port_and_aquaculture_list"] = fishing_ports + '\n' + aquacultures if aquacultures else fishing_ports

        return bundle.data['name']

    def obj_create(self, bundle, request=None, **kwargs):
        user = bundle.request.user
        if not user.has_perm('fishuser.sub_menu_management_system_create'):
            raise ImmediateHttpResponse(response=http.HttpBadRequest(_(u'You have no permission。')))

        bundle.obj = Project()
        for key, value in kwargs.items():
            setattr(bundle.obj, key, value)
        bundle = self.full_hydrate(bundle)
        self.save_related(bundle)

        bundle.obj.save()

        m2m_bundle = self.hydrate_m2m(bundle)
        self.save_m2m(m2m_bundle)
        project = bundle.obj
        if project.undertake_type.value != u'補助':
            project.allot_rate = 100
        else:
            project.allot_rate = bundle.data.get('allot_rate', 100)
        project.subsidy_limit = bundle.data.get('capital_ratify_budget', 0)

        project.save()

        fund = Fund(
                project = project
            )
        fund.save()
        budget =  Budget(
                fund = fund,
                plan = Plan.objects.get(id=bundle.data['plan'].split('/')[5]),
                year = project.year,
                capital_ratify_budget = bundle.data.get('capital_ratify_budget', 0),
                capital_ratify_local_budget = bundle.data.get('capital_ratify_local_budget', 0)
            )
        budget.save()
        chase_obo = CountyChaseProjectOneByOne(
                project = project,
                sch_ser_approved_plan = bundle.data.get('sch_approved_plan_date', None),
                act_ser_approved_plan = bundle.data.get('act_approved_plan_date', None) or None,
                sch_eng_plan_approved_plan = bundle.data.get('sch_approved_plan_date', None),
                act_eng_plan_approved_plan = bundle.data.get('act_approved_plan_date', None) or None,
            )
        chase_obo.save()
        return bundle


    def obj_update(self, bundle, request=None, **kwargs):
        project = Project.objects.get(pk=kwargs['pk'])
        user = bundle.request.user
        if not 'edit_single_project_in_remote_control_system' in get_perms(user, project) and not user.has_perm(u'fishuser.edit_all_project_in_management_system'):
            raise ImmediateHttpResponse(response=http.HttpBadRequest(_(u'You have no permission。')))
        if bundle.data.get('pcc_no', ''):
            # try:
            #     p = Project.objects.get(pcc_no=bundle.data.get('pcc_no', ''))
            #     raise ImmediateHttpResponse(response=http.HttpBadRequest(_(u'此工程會編號已存在，輸入編號與此工程重複 => id=%s - %s年度 - %s' % (p.id, p.year, p.name))))
            # except Project.DoesNotExist:
            ori_pcc_no = project.pcc_no
            try:
                # extr = getProjectInfo(bundle.data.get('pcc_no', ''))
                project.pcc_no = bundle.data.get('pcc_no', '')
                project.save()
                project.sync_pcc_info()
            except:
                project.pcc_no = ori_pcc_no
                project.save()
                raise ImmediateHttpResponse(response=http.HttpBadRequest(_(u'無法使用此編號取得工程資訊。編號有誤、或是權限不足(工程會補助機關未正確填報)。')))

        if bundle.data.get('ex_project', ''):
            ex_project = int(bundle.data.get('ex_project', '').split('/')[5])
            if ex_project == project.id:
                raise ImmediateHttpResponse(response=http.HttpBadRequest(_(u'設定錯誤，不可索引自己。')))
            elif Project.objects.filter(ex_project__id=ex_project).exclude(id=project.id):
                raise ImmediateHttpResponse(response=http.HttpBadRequest(_(u'設定錯誤，此工程已被索引過')))

            #連動里程碑資訊
            ex_project = Project.objects.get(id=ex_project)
            try:
                ex_c = CountyChaseProjectOneByOne.objects.get(project=ex_project)
                p_c = CountyChaseProjectOneByOne.objects.get(project=project)
                for field_name in p_c.__dict__:
                    if not getattr(p_c, field_name) and getattr(ex_c, field_name):
                        setattr(p_c, field_name, getattr(ex_c, field_name))
                    p_c.save()
            except: pass

        if bundle.data.get('fishing_port_add', ''):
            port = FishingPort.objects.get(id=bundle.data.get('fishing_port_add', ''))
            project.fishing_port.add(port)
        elif bundle.data.get('fishing_port_remove', ''):
            port = FishingPort.objects.get(id=bundle.data.get('fishing_port_remove', ''))
            project.fishing_port.remove(port)
        elif bundle.data.get('aquaculture_add', ''):
            aqua = Aquaculture.objects.get(id=bundle.data.get('aquaculture_add', ''))
            project.aquaculture.remove(aqua)
        elif bundle.data.get('aquaculture_remove', ''):
            aqua = Aquaculture.objects.get(id=bundle.data.get('aquaculture_remove', ''))
            project.aquaculture.remove(aqua)
        
        list_url = '/harbor/api/v2/fishingport/'
        bundle.data['fishing_port'] = ['%s%s/'%(list_url, t.id) for t in project.fishing_port.all()]
        list_url = '/harbor/api/v2/aquaculture/'
        bundle.data['aquaculture'] = ['%s%s/'%(list_url, t.id) for t in project.aquaculture.all()]

        if project.undertake_type.value == '自辦' and ('construction_bid' in bundle.data \
            or 'safety_fee' in bundle.data or 'business_tax' in bundle.data):
            need_update_manage = True
        else:
            need_update_manage = False

        if project.undertake_type.value == '自辦' and ('settlement_construction_bid' in bundle.data \
            or 'settlement_safety_fee' in bundle.data or 'settlement_business_tax' in bundle.data):
            need_update_settlement_manage = True
        else:
            need_update_settlement_manage = False

        bundle = super(ProjectResource, self).obj_update(bundle, **kwargs)

        if need_update_manage:
            project.set_manage_money(obj=bundle.obj)
        if need_update_settlement_manage:
            project.set_settlement_manage_money(obj=bundle.obj)
            
        if not project.inspector_code:
            project.create_i_code()
        if not project.contractor_code:
            project.create_c_code()

        bundle = self.build_bundle(obj=project, request=request)
        bundle = self.full_dehydrate(bundle)
        return bundle

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/search/$" % (self._meta.resource_name), self.wrap_view('get_search'), name="api_get_search"),
            url(r"^(?P<resource_name>%s)/code_search/$" % (self._meta.resource_name), self.wrap_view('code_search'), name="api_code_search"),
        ]

    def code_search(self, request, **kwargs):
        info = {}
        for key in request.GET.iterkeys():
            info[key] = request.GET.get(key)
        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
        self.throttle_check(request)

        code = info.get('code', '').upper()
        # Do the query.
        result = list(Project.objects.filter(inspector_code=code, deleter=None)) + list(Project.objects.filter(contractor_code=code, deleter=None))

        objects = []

        for r in result:
            if r.frcmusergroup_set.filter(user__id=info.get('user_id', '')):
                continue
            bundle = self.build_bundle(obj=r, request=request)
            bundle = self.full_dehydrate(bundle)
            objects.append(bundle)

        object_list = {
            'objects': objects,
        }

        self.log_throttled_access(request)
        return self.create_response(request, object_list)

    def get_search(self, request, **kwargs):
        info = {}
        for key in request.GET.iterkeys():
            info[key] = request.GET.get(key)

        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
        self.throttle_check(request)
        project = Project.objects.filter(deleter_id=None).order_by('-id')
        # Do the query.
        result = Project.objects.filter(deleter=None).order_by('-pcc_no', '-year', 'unit', 'name', 'id').prefetch_related(
                'project_type', 'project_sub_type', 
                'undertake_type', 'budget_type', 'budget_sub_type', 'purchase_type', 'place',
                'fishing_port', 'aquaculture', 'unit', 'status', 'deleter',
                'bid_type', 'contract_type', 'contractor', 'inspector', 'frcm_inspector_type',
                'frcm_duration_type', 'progress_type'
                )

        #ids
        if info.get('ids', '') and info.get('ids', '') != '' and info.get('ids', '') != 'undefined':
            ids = info.get('ids', '').split(',')
            result = result.filter(id__in=ids[:-1])
        #年度
        if info.get('year', '') and info.get('year', '') != '' and info.get('year', '') != 'undefined':
            result = result.filter(year=info.get('year', ''))
            project = Project.objects.filter(year__in=info.get('year', '').split(','), deleter_id=None).order_by('-id')
        #年度s
        if info.get('years', '') and info.get('years', '') != '' and info.get('years', '') not in ['undefined', 'null']:
            result = result.filter(year__in=info.get('years', '').split(','))
            project = Project.objects.filter(year__in=info.get('years', '').split(','), deleter_id=None).order_by('-id')
        #經費來源計劃
        if info.get('plan', '') and info.get('plan', '') != '' and info.get('plan', '') != 'undefined':
            if info.get('sub_plan', '') == 'false':
                plans = [Plan.objects.get(id=info.get('plan', ''))]
            else:
                plans = [Plan.objects.get(id=info.get('plan', ''))]
                for p in plans[0].rSubPlanInList():
                    plans.append(p)
            budgets = Budget.objects.filter(plan__in=plans)
            result = result.filter(id__in=set([i.fund.project.id for i in budgets]))
        #計畫編號
        if info.get('work_no', '') and info.get('work_no', '') != '' and info.get('work_no', '') != 'undefined':
            ids = []
            for key in re.split('[ ,]+', info.get('work_no', '')):
                if key:
                    ids.extend([i.id for i in result.filter(work_no__icontains=key)])
            result = result.filter(id__in=ids)
        #工程名稱
        if info.get('name', '') and info.get('name', '') != '' and info.get('name', '') != 'undefined':
            ids = []
            for key in re.split('[ ,]+', info.get('name', '')):
                if key:
                    ids.extend([i.id for i in result.filter(name__icontains=key)])
            result = result.filter(id__in=ids)
        #廠商名稱-----------------------------------------------------------------------------------------------
        if info.get('bid_final', '') and info.get('bid_final', '') != '' and info.get('bid_final', '') != 'undefined':
            ids = []
            data_project={}
            for p in project:
                contractors = [u.user.id for u in FRCMUserGroup.objects.filter(group__name=u'營造廠商', project_id=p)]
                unit_id = UserProfile.objects.get(user_id = contractors[0]).unit_id if contractors != [] else None
                try:
                    unit = EngProfile.objects.get(project=p).contractor_name
                except:
                    unit = None
                if not unit:
                    unit = Unit.objects.get(id = unit_id).fullname if unit_id else None
                if not unit:
                    unit = p.bid_final
                if unit:
                    try:
                        if data_project[unit[0] + unit[1]]:
                            for i in data_project.keys():
                                if unit[0] + unit[1] in i:
                                    data_project[unit[0] + unit[1]].append(int(p.id))
                    except:
                        data_project.setdefault(unit[0] + unit[1], [int(p.id)])
            for key in re.split('[ ,]+', info.get('bid_final', '')):
                if key:
                    try:
                        ids = data_project[key]
                    except:
                        ids.extend([i.id for i in result.filter(bid_final__icontains=key)])
            result = result.filter(id__in=ids)
        #標案編號
        if info.get('pcc_no', '') and info.get('pcc_no', '') != '' and info.get('pcc_no', '') != 'undefined':
            ids = []
            for key in re.split('[ ,]+', info.get('pcc_no', '')):
                ids.extend([i.id for i in result.filter(pcc_no__icontains=key)])
            result = result.filter(id__in=ids)
        #縣市
        if info.get('place', '') and info.get('place', '') != '' and info.get('place', '') != 'undefined':
            place_id = info.get('place', '').split('/')[-2]
            result = result.filter(place__id=place_id)
        #執行機關
        if info.get('unit', '') and info.get('unit', '') != '' and info.get('unit', '') != 'undefined':
            result = result.filter(unit__id=info.get('unit', ''))
        #工程屬性別
        if info.get('project_type', '') and info.get('project_type', '') != '' and info.get('project_type', '') != 'undefined':
            result = result.filter(project_type__id=info.get('project_type', ''))
        #承辦方式
        if info.get('undertake_type', '') and info.get('undertake_type', '') != '' and info.get('undertake_type', '') != 'undefined':
            result = result.filter(undertake_type__id=info.get('undertake_type', ''))
        #採購類別
        if info.get('purchase_type', '') and info.get('purchase_type', '') != '' and info.get('purchase_type', '') != 'undefined':
            result = result.filter(purchase_type__id=info.get('purchase_type', ''))
        #經費種類
        if info.get('budget_sub_type', '') and info.get('budget_sub_type', '') != '' and info.get('budget_sub_type', '') != 'undefined':
            result = result.filter(budget_sub_type__id=info.get('budget_sub_type', ''))
        #漁港
        if info.get('fishing_port', '') and info.get('fishing_port', '') != '' and info.get('fishing_port', '') != 'undefined':
            result = result.filter(fishing_port__id=info.get('fishing_port', ''))
        #養殖區
        if info.get('aquaculture', '') and info.get('aquaculture', '') != '' and info.get('aquaculture', '') != 'undefined':
            result = result.filter(aquaculture__id=info.get('aquaculture', ''))
        #發文(核定)日期
        if info.get('vouch_date_ub', None) and info.get('vouch_date_ub', None) != '':
            vouch_date_ub = info.get('vouch_date_ub', None).replace('/', '-').replace('.', '-')
            vouch_date_lb = info.get('vouch_date_lb', None).replace('/', '-').replace('.', '-')
            ids = []
            chase_projects = CountyChaseProjectOneByOne.objects.all()
            ids.extend([i.project.id for i in chase_projects.filter(act_ser_approved_plan__gte=vouch_date_ub, act_ser_approved_plan__lte=vouch_date_lb)])
            ids.extend([i.project.id for i in chase_projects.filter(act_eng_plan_approved_plan__gte=vouch_date_ub, act_eng_plan_approved_plan__lte=vouch_date_lb)])
            result = result.filter(id__in=ids)
        #是否已被匯入FRCM
        if info.get('is_import', '') and info.get('is_import', '') != '' and info.get('is_import', '') != 'undefined':
            frcm_result = FRCMUserGroup.objects.filter(project__deleter=None, group__name__in=['負責主辦工程師', '自辦主辦工程師'])
            ids = [p.project.id for p in frcm_result]
            if info.get('is_import', '') == 'true':
                result = result.filter(id__in=ids)
            else:
                result = result.exclude(id__in=ids)
        #負責工程師
        if info.get('eng_name', '') and info.get('eng_name', '') != '' and info.get('eng_name', '') != 'undefined':
            name_str = unicode(info.get('eng_name', None))
            frcm_result = FRCMUserGroup.objects.filter(project__deleter=None, group__name__in=['負責主辦工程師', '自辦主辦工程師'])
            if len(name_str) == 3:
                last_name = name_str[0]
                first_name = name_str[1:3]
                frcm_result = frcm_result.filter((Q(user__last_name__startswith=last_name)&Q(user__first_name__contains=first_name))|Q(user__first_name__contains=name_str))
            elif len(name_str) == 2:
                last_name = name_str[0]
                first_name = name_str[1]
                frcm_result = frcm_result.filter((Q(user__last_name__startswith=last_name)&Q(user__first_name__contains=first_name))|Q(user__last_name=name_str)|Q(user__first_name=name_str))
            elif len(name_str) == 1:
                frcm_result = frcm_result.filter(Q(user__last_name__contains=name_str)|Q(user__first_name__contains=name_str))
            else:
                last_name = name_str[0]
                first_name = name_str[-2:]
                frcm_result = FRCMUserGroup.objects.filter(user__last_name__contains=last_name, user__first_name__contains=first_name)
            ids = [i.project.id for i in frcm_result]
            result = result.filter(id__in=ids)
        #是否結案
        if info.get('is_finish', '') and info.get('is_finish', '') != '' and info.get('is_finish', '') != 'undefined':
            is_finishs = CountyChaseProjectOneByOne.objects.filter(project__in=result).exclude(act_eng_do_closed__isnull=True, project__purchase_type__value__in=[u"工程", u"工程勞務"]).exclude(act_ser_acceptance_closed__isnull=True, project__purchase_type__value=u"一般勞務")
            is_finish_ids = [i.project.id for i in is_finishs]
            if info.get('is_finish', '') == 'true':
                result = result.filter(id__in=is_finish_ids)
            else:
                result = result.exclude(id__in=is_finish_ids)

        result_ids = [str(i.id) for i in result]

        paginator = Paginator(request.GET, result, resource_uri='/fishuser/api/v2/project/search/')

        objects = []
        for r in paginator.page()['objects']:
            bundle = self.build_bundle(obj=r, request=request)
            bundle = self.full_dehydrate(bundle)
            objects.append(bundle)

        object_list = {
            'meta': paginator.page()['meta'],
            'objects': objects,
            'result_ids': ','.join(result_ids)
        }

        self.log_throttled_access(request)

        return self.create_response(request, object_list)



class ProjectBidMoneyResource(ModelResource):
    project = fields.ForeignKey(ProjectResource, 'project')
    field_type = fields.ForeignKey(OptionResource, 'field_type')

    class Meta:
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        queryset = ProjectBidMoney.objects.all()
        always_return_data = True
        resource_name = 'projectbidmoney'
        ordering = ["field_type"]
        allowed_methods = ['get', 'post', 'put', 'delete']
        filtering = {
            "id": ("exact"),
            "project": ("exact"),
            "field_type": ("exact"),
        }
        


class Draft_ProjectResource(ModelResource):
    place = fields.ForeignKey(PlaceResource, 'place', null=True)
    fishing_port = fields.ToManyField(FishingPortResource, 'fishing_port', full=True, null=True)
    aquaculture = fields.ToManyField(AquacultureResource, 'aquaculture', full=True, null=True)
    project_type = fields.ForeignKey(OptionResource, 'project_type', null=True)
    project_sub_type = fields.ForeignKey(OptionResource, 'project_sub_type', null=True)
    project = fields.ForeignKey(ProjectResource, 'project', null=True)
    plan = fields.ForeignKey(PlanResource, 'plan', null=True)
    undertake_type = fields.ForeignKey(OptionResource, 'undertake_type', null=True)
    budget_sub_type = fields.ForeignKey(OptionResource, 'budget_sub_type', null=True)
    purchase_type = fields.ForeignKey(OptionResource, 'purchase_type', null=True)
    unit = fields.ForeignKey(UnitResource, 'unit', null=True)
    type = fields.ForeignKey(OptionResource, 'type', null=True)


    class Meta:
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        queryset = Draft_Project.objects.all()
        always_return_data = True
        resource_name = 'draft_project'
        ordering = ["name", 'unit', 'type']
        allowed_methods = ['get', 'post', 'put', 'delete']
        filtering = {
            "id": ("exact"),
            "place": ("exact"),
            "unit": ("exact"),
            "type": ("exact"),
        }

    def dehydrate_name(self, bundle):
        if bundle.obj:
            bundle.data['listname_plan'] = bundle.obj.plan.name if bundle.obj.plan else ''
            bundle.data['listname_place'] = bundle.obj.place.name if bundle.obj.place else ''
            bundle.data['listname_unit'] = bundle.obj.unit.name if bundle.obj.unit else ''
            bundle.data['listname_project'] = bundle.obj.project.name if bundle.obj.project else ''
            bundle.data['listname_project_type'] = bundle.obj.project_type.value if bundle.obj.project_type else ''
            bundle.data['listname_project_sub_type'] = bundle.obj.project_sub_type.value if bundle.obj.project_sub_type else ''
            bundle.data['listname_undertake_type'] = bundle.obj.undertake_type.value if bundle.obj.undertake_type else ''
            bundle.data['listname_budget_sub_type'] = bundle.obj.budget_sub_type.value if bundle.obj.budget_sub_type else ''
            bundle.data['listname_purchase_type'] = bundle.obj.purchase_type.value if bundle.obj.purchase_type else ''
            bundle.data['listname_type'] = bundle.obj.type.value if bundle.obj.type else ''

        return bundle.data['name']

    def obj_create(self, bundle, request=None, **kwargs):
        user = bundle.request.user
        bundle.obj = Draft_Project()
        for key, value in kwargs.items():
            setattr(bundle.obj, key, value)
        bundle = self.full_hydrate(bundle)
        self.save_related(bundle)
        bundle.obj.save()
        m2m_bundle = self.hydrate_m2m(bundle)
        self.save_m2m(m2m_bundle)
        project = bundle.obj
        project.sort = Draft_Project.objects.filter(type=project.type, place=project.place).count()
        project.save()

        return bundle

    def obj_delete(self, bundle, **kwargs):
        p = Draft_Project.objects.get(pk=kwargs['pk'])
        for i in Draft_Project.objects.filter(type=p.type, place=p.place, sort__gt=p.sort):
            i.sort -= 1
            i.save()

        super(Draft_ProjectResource, self).obj_delete(bundle, **kwargs)

    def obj_update(self, bundle, request=None, **kwargs):
        p = Draft_Project.objects.get(pk=kwargs['pk'])
        if bundle.data.get('fishing_port_add', ''):
            port = FishingPort.objects.get(id=bundle.data.get('fishing_port_add', ''))
            p.fishing_port.add(port)
        elif bundle.data.get('fishing_port_remove', ''):
            port = FishingPort.objects.get(id=bundle.data.get('fishing_port_remove', ''))
            p.fishing_port.remove(port)
        elif bundle.data.get('aquaculture_add', ''):
            aqua = Aquaculture.objects.get(id=bundle.data.get('aquaculture_add', ''))
            p.aquaculture.remove(aqua)
        elif bundle.data.get('aquaculture_remove', ''):
            aqua = Aquaculture.objects.get(id=bundle.data.get('aquaculture_remove', ''))
            p.aquaculture.remove(aqua)
        
        list_url = '/harbor/api/v2/fishingport/'
        bundle.data['fishing_port'] = ['%s%s/'%(list_url, t.id) for t in p.fishing_port.all()]
        list_url = '/harbor/api/v2/aquaculture/'
        bundle.data['aquaculture'] = ['%s%s/'%(list_url, t.id) for t in p.aquaculture.all()]

        if bundle.data.get('sort_down', ''):
            dps = Draft_Project.objects.filter(type=p.type, place=p.place, sort__gt=p.sort).order_by('sort')
            if dps:
                dps[0].sort -= 1
                dps[0].save()
                p.sort += 1
                p.save()
        elif bundle.data.get('sort_up', ''):
            dps = Draft_Project.objects.filter(type=p.type, place=p.place, sort__lt=p.sort).order_by('-sort')
            if dps:
                dps[0].sort += 1
                dps[0].save()
                p.sort -= 1
                p.save()

        if bundle.data.get('change_dproject_type', ''):
            type_fish = Option.objects.get(swarm="draft_type", value="漁業署草稿")
            type_place = Option.objects.get(swarm="draft_type", value="縣市提案草稿")
            dps = Draft_Project.objects.filter(type=p.type, place=p.place, sort__gt=p.sort).order_by('sort')
            for dp in dps:
                dp.sort -= 1
                dp.save()
            if p.type == type_fish:
                p.type = type_place
                p.sort = Draft_Project.objects.filter(type=type_place, place=p.place).count() + 1
            else:
                p.type = type_fish
                p.sort = Draft_Project.objects.filter(type=type_fish, place=p.place).count() + 1
            p.save()

        super(Draft_ProjectResource, self).obj_update(bundle, **kwargs)
        bundle = self.build_bundle(obj=p, request=request)
        bundle = self.full_dehydrate(bundle)
        return bundle



class DefaultProjectResource(ModelResource):
    user = fields.ForeignKey(UserResource, 'user')
    project = fields.ForeignKey(ProjectResource, 'project')

    class Meta:
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        always_return_data = True
        queryset = DefaultProject.objects.all()
        resource_name = 'defaultproject'
        ordering = ["project"]
        allowed_methods = ['get', 'post', 'put', 'delete']
        filtering = {
            "id": ("exact"),
            "user": ("exact"),
            "project": ("exact"),
        }



class FRCMUserGroupResource(ModelResource):
    user = fields.ForeignKey(UserResource, 'user')
    group = fields.ForeignKey(GroupResource, 'group')
    project = fields.ForeignKey(ProjectResource, 'project')

    class Meta:
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        always_return_data = True
        queryset = FRCMUserGroup.objects.all()
        resource_name = 'frcmusergroup'
        # excludes = ['user']
        ordering = ["project"]
        allowed_methods = ['get', 'post', 'put', 'delete']
        filtering = {
            "id": ("exact"),
            "user": ("exact"),
            "project": ("exact"),
        }

    def obj_create(self, bundle, request=None, **kwargs):
        if bundle.data.get('unit_no', ''):
            units = Unit.objects.filter(no=bundle.data['unit_no'])
            if units:
                unit = units.first()
            else:
                unit = Unit(no=bundle.data['unit_no'], place=Place.objects.get(id=1))
                unit.save()
            try:
                u = User.objects.get(id=bundle.data['user'].split('/')[5])
                up = u.user_profile
                if not up.unit:
                    up.unit = unit
                    up.save()
            except: pass

        bundle = super(FRCMUserGroupResource, self).obj_create(bundle, **kwargs)
        return bundle



class FundResource(ModelResource):
    project = fields.ForeignKey(ProjectResource, 'project')

    class Meta:
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        always_return_data = True
        queryset = Fund.objects.all()
        resource_name = 'fund'
        ordering = ["project"]
        allowed_methods = ['get', 'post', 'put', 'delete']
        filtering = {
            "id": ("exact"),
            "project": ("exact"),
        }



class BudgetResource(ModelResource):
    fund = fields.ForeignKey(FundResource, 'fund')
    plan = fields.ForeignKey(PlanResource, 'plan')

    class Meta:
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        always_return_data = True
        queryset = Budget.objects.all()
        resource_name = 'budget'
        allowed_methods = ['get', 'post', 'put', 'delete']
        filtering = {
            "id": ("exact"),
            "fund": ("exact"),
        }

    def dehydrate(self, bundle):
        user = bundle.request.user
        if bundle.obj:
            bundle.data['plan__name'] = bundle.obj.plan.name if bundle.obj.plan else ''
        return bundle

    def obj_create(self, bundle, request=None, **kwargs):
        if not bundle.data.get('year', ''):
            plan = Plan.objects.get(id=bundle.data['plan'].split('/')[5])
            bundle.data['year'] = plan.year
            budgets = Budget.objects.filter(fund__id=bundle.data['fund'].split('/')[5]).order_by('-priority')
            if budgets:
                bundle.data['priority'] = budgets.first().priority + 10000
            else:
                bundle.data['priority'] = 10000
        
        bundle = super(BudgetResource, self).obj_create(bundle, **kwargs)
        return bundle

    def obj_update(self, bundle, request=None, **kwargs):
        budget = Budget.objects.get(pk=kwargs['pk'])
        # if bundle.data['priority']
        if bundle.data.get('direction', '') == 'up':
            pre_item = Budget.objects.filter(fund=budget.fund, priority__lt=budget.priority).order_by('-priority')
            if not pre_item: raise ImmediateHttpResponse(response=http.HttpBadRequest(_(u'已是第一個項目。')))
            pre_item = pre_item[0]
            bundle.data['priority'], pre_item.priority = pre_item.priority, budget.priority
            pre_item.save()
        elif bundle.data.get('direction', '') == 'down':
            next_item = Budget.objects.filter(fund=budget.fund, priority__gt=budget.priority).order_by('priority')
            if not next_item: raise ImmediateHttpResponse(response=http.HttpBadRequest(_(u'已是最後一個項目。')))
            next_item = next_item[0]
            bundle.data['priority'], next_item.priority = next_item.priority, budget.priority
            next_item.save()

        bundle = super(BudgetResource, self).obj_update(bundle, **kwargs)
        # project = budget.fund.project
        # if bundle.data.get('capital_ratify_revision', ''):
        #     project.subsidy_limit = bundle.data.get('capital_ratify_revision', '')
        #     project.save()
        # elif bundle.data.get('capital_ratify_budget', '') and not budget.capital_ratify_revision:
        #     project.subsidy_limit = bundle.data.get('capital_ratify_budget', '')
        #     project.save()
        # bundle = self.build_bundle(obj=budget, request=request)
        # bundle = self.full_dehydrate(bundle)
        return bundle



class AppropriateResource(ModelResource):
    project = fields.ForeignKey(ProjectResource, 'project')
    type = fields.ForeignKey(OptionResource, 'type', null=True)

    class Meta:
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        always_return_data = True
        queryset = Appropriate.objects.all()
        resource_name = 'appropriate'
        allowed_methods = ['get', 'post', 'put', 'delete']
        filtering = {
            "id": ("exact"),
            "project": ("project"),
            "type": ("project"),
        }



class EmailListResource(ModelResource):
    place = fields.ForeignKey(PlaceResource, 'place', null=True)

    class Meta:
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        queryset = EmailList.objects.all()
        always_return_data = True
        resource_name = 'emaillist'
        allowed_methods = ['get', 'post', 'put', 'delete']

    def dehydrate_id(self, bundle):
        if bundle.obj:
            bundle.data['listname_place'] = bundle.obj.place.name if bundle.obj.place else ''
            bundle.data['listname_need_email'] = '是' if  bundle.obj.need_email else '否'
        return bundle.data['id']



class AllocationResource(ModelResource):
    project = fields.ForeignKey(ProjectResource, 'project', null=True)

    class Meta:
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        queryset = Allocation.objects.all()
        always_return_data = True
        resource_name = 'allocation'
        allowed_methods = ['get', 'post', 'put', 'delete']



class CountyChaseTimeResource(ModelResource):
    user = fields.ForeignKey(UserResource, 'user', null=True)

    class Meta:
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        queryset = CountyChaseTime.objects.all()
        always_return_data = True
        resource_name = 'countychasetime'
        allowed_methods = ['get', 'post', 'put', 'delete']

    def obj_create(self, bundle, request=None, **kwargs):
        user = bundle.request.user
        if not user.has_perm('fishuser.sub_menu_management_system_city'):
            raise ImmediateHttpResponse(response=http.HttpBadRequest(_(u'You have no permission。')))
        bundle.obj = CountyChaseTime()
        bundle.obj.chase_date = TODAY()
        bundle.obj.user = user
        bundle = self.full_hydrate(bundle)
        self.save_related(bundle)
        bundle.obj.save()
        if bundle.data['have_project']:
            ex_chase = bundle.obj.read_ex_chase()
            for p in ex_chase.countychaseprojectonetomany_set.all():
                row = CountyChaseProjectOneToMany(
                    countychasetime = bundle.obj,
                    project = p.project
                    )
                row.save()
        return bundle



class CountyChaseTimeNewUpdateResource(ModelResource):
    countychasetime = fields.ForeignKey(CountyChaseTimeResource, 'countychasetime')
    project = fields.ForeignKey(ProjectResource, 'project')

    class Meta:
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        queryset = CountyChaseTimeNewUpdate.objects.all()
        always_return_data = True
        resource_name = 'countychasetimenewupdate'
        allowed_methods = ['get', 'post', 'put', 'delete']



class CountyChaseProjectOneByOneResource(ModelResource):
    project = fields.ForeignKey(ProjectResource, 'project')

    class Meta:
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        queryset = CountyChaseProjectOneByOne.objects.all()
        always_return_data = True
        resource_name = 'countychaseprojectonebyone'
        allowed_methods = ['get', 'post', 'put', 'delete']


    def obj_update(self, bundle, request=None, **kwargs):
        chase = CountyChaseProjectOneByOne.objects.get(pk=kwargs['pk'])
        if bundle.data.get('set_total_money', ''):
            if bundle.data.get('set_total_money', '') == 'use_plan_money':
                chase.total_money = str(list(chase.project.fund_set.get().budget_set.all().order_by('year'))[0].rPlanMoney())
            else:
                chase.total_money = str(chase.project.read_total_money())
            chase.save()

        bundle_data = bundle.data

        super(CountyChaseProjectOneByOneResource, self).obj_update(bundle, **kwargs)
        bundle = self.build_bundle(obj=chase, request=request)
        bundle = self.full_dehydrate(bundle)

        #若有延續工程則 里程碑資料連動
        connect_project = [chase.project]
        ex = chase.project.ex_project
        while ex:
            connect_project.insert(0, ex)
            ex = ex.ex_project
        next = Project.objects.filter(ex_project=chase.project)
        while next:
            connect_project.append(next[0])
            next = Project.objects.filter(ex_project=next[0])
        
        for i in CountyChaseProjectOneByOne.objects.filter(project__in=connect_project):
            for key in bundle_data:
                if key == 'pk': continue
                try:
                    setattr(i, key, bundle_data[key])
                except: pass
                i.save()
        return bundle



class CountyChaseProjectOneToManyResource(ModelResource):
    countychasetime = fields.ForeignKey(CountyChaseTimeResource, 'countychasetime')
    project = fields.ForeignKey(ProjectResource, 'project')

    class Meta:
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        queryset = CountyChaseProjectOneToMany.objects.all()
        always_return_data = True
        resource_name = 'countychaseprojectonetomany'
        ordering = ["id"]
        allowed_methods = ['get', 'post', 'put', 'delete']
        filtering = {
            "id": ("exact"),
            "countychasetime": ("exact"),
            "project": ("exact"),
        }

    def dehydrate(self, bundle):
        if bundle.obj:
            project = bundle.obj.project
            bundle.data['countychasetime__chase_date'] = bundle.obj.countychasetime.chase_date
            bundle.data['project__plan__name__list'] = u''.join([u'●%s' % i.plan.name for i in Budget.objects.filter(fund__project=project, plan__isnull=False)])
            bundle.data['project__id'] = project.id
            bundle.data['project__year'] = project.year
            bundle.data['project__name'] = project.name
            bundle.data['project__bid_no'] = project.bid_no
            bundle.data['project__place__name'] = project.place.name if project.place else ''
            fishing_ports = '\n'.join([f.name for f in project.fishing_port.all()])
            aquacultures = '\n'.join([a.name for a in project.aquaculture.all()])
            bundle.data["project__fishing_port_and_aquaculture_list"] = fishing_ports + '\n' + aquacultures if aquacultures else fishing_ports
            bundle.data['project__purchase_type__value'] = project.purchase_type.value if project.purchase_type else ''
            bundle.data['project__undertake_type__value'] = project.undertake_type.value if project.undertake_type else ''
            bundle.data['project__self_contacter'] = project.self_contacter
            try: 
                bundle.data['project__importer'] = project.frcmusergroup_set.get(group__name__in=[u'負責主辦工程師', u'自辦主辦工程師']).user.user_profile.rName()
            except: 
                bundle.data['project__importer'] = u'-'

        return bundle

    def obj_update(self, bundle, request=None, **kwargs):
        chase = CountyChaseProjectOneToMany.objects.get(pk=kwargs['pk'])
        
        chase_time = CountyChaseTime.objects.all().order_by('-chase_date').first()

        setattr(chase, 'update_time', TODAY())
        chase.save()

        super(CountyChaseProjectOneToManyResource, self).obj_update(bundle, **kwargs)
        bundle = self.build_bundle(obj=chase, request=request)
        bundle = self.full_dehydrate(bundle)
        return bundle

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
        result = CountyChaseProjectOneToMany.objects.filter(countychasetime__id=info.get('chase_time_id')).order_by('project__plan', 'project__name').prefetch_related(
                'project__plan', 'project__unit', 'project__place', 'project__budget_sub_type', 'project__purchase_type'
                )
        #ids
        if info.get('ids', '') and info.get('ids', '') != '' and info.get('ids', '') != 'undefined':
            ids = info.get('ids', '').split(',')
            result = result.filter(id__in=ids[:-1])
        #年度
        if info.get('year', '') and info.get('year', '') != '' and info.get('year', '') != 'undefined':
            result = result.filter(project__year=info.get('year', ''))
        #經費來源計劃
        if info.get('plan', '') and info.get('plan', '') != '' and info.get('plan', '') != 'undefined':
            if info.get('sub_plan', '') == 'false':
                plans = [Plan.objects.get(id=info.get('plan', ''))]
            else:
                plans = [Plan.objects.get(id=info.get('plan', ''))]
                for p in plans[0].rSubPlanInList():
                    plans.append(p)
            budgets = Budget.objects.filter(plan__in=plans)
            result = result.filter(project__id__in=set([i.fund.project.id for i in budgets]))
        #工程名稱
        if info.get('name', '') and info.get('name', '') != '' and info.get('name', '') != 'undefined':
            ids = []
            for key in re.split('[ ,]+', info.get('name', '')):
                if key:
                    ids.extend([i.id for i in result.filter(project__name__icontains=key)])
            result = result.filter(id__in=ids)
        #標案編號
        if info.get('bid_no', '') and info.get('bid_no', '') != '' and info.get('bid_no', '') != 'undefined':
            ids = []
            for key in re.split('[ ,]+', info.get('bid_no', '')):
                ids.extend([i.id for i in result.filter(project__bid_no__icontains=key)])
            result = result.filter(id__in=ids)
        #縣市
        if info.get('place', '') and info.get('place', '') != '' and info.get('place', '') != 'undefined':
            place_id = info.get('place', '').split('/')[-2]
            result = result.filter(project__place__id=place_id)
        #執行機關
        if info.get('unit', '') and info.get('unit', '') != '' and info.get('unit', '') != 'undefined':
            result = result.filter(project__unit__id=info.get('unit', ''))
        #採購類別
        if info.get('purchase_type', '') and info.get('purchase_type', '') != '' and info.get('purchase_type', '') != 'undefined':
            result = result.filter(project__purchase_type__id=info.get('purchase_type', ''))
        #經費種類
        if info.get('budget_sub_type', '') and info.get('budget_sub_type', '') != '' and info.get('budget_sub_type', '') != 'undefined':
            result = result.filter(project__budget_sub_type__id=info.get('budget_sub_type', ''))
        if info.get('condition', '') and info.get('condition', '') != '' and info.get('condition', '') != 'undefined':
            condition = info.get('condition', '')
            ids = []
            if info.get('progress_delay', 'false') == 'true': #進度落後
                rate = decimal.Decimal(info.get('progress_delay_rate', '15'));
                for r in result.filter(complete=True):
                    schedul_progress_percent = r.schedul_progress_percent if r.schedul_progress_percent else decimal.Decimal('0')
                    actual_progress_percent = r.actual_progress_percent if r.actual_progress_percent else decimal.Decimal('0')
                    if schedul_progress_percent - actual_progress_percent > rate:
                        ids.append(r.id)
                # result = result.filter(id__in=ids)
            if info.get('have_give_up', 'false') == 'true': #流標N次以上
                give_up_times = int(info.get('give_up_times', '1'))
                give_ups = CountyChaseProjectOneByOne.objects.filter(give_up_times__gte=give_up_times, project__in=[r.project for r in result])
                for r in result.filter(project__in=[g.project for g in give_ups]):
                    ids.append(r.id)
            # if info.get('milestone_delay', 'false') == 'true': #里程碑進度逾期
            #     projects_map = {}
            #     for i in result: projects_map[i.project.id] = i.id
            #     milestones = [i for i in CountyChaseProjectOneByOne.objects.filter(project__id__in=[j for j in projects_map])]
            #     for i in milestones:
            #         if i.project.purchase_type.value in [u'工程', u'工程勞務']:
            #             check_fields = ['eng_plan_agree_plan', 'eng_plan_approved_plan', 'eng_plan_announcement_tender',
            #                             'eng_plan_final', 'eng_plan_promise', 'eng_plan_detail_design',
            #                             'eng_plan_acceptance', 'eng_plan_acceptance_closed', 'eng_do_agree_plan',
            #                             'eng_do_approved_plan', 'eng_do_announcement_tender', 'eng_do_final',
            #                             'eng_do_promise', 'eng_do_start', 'eng_do_completion',
            #                             'eng_do_acceptance'
            #                             ]
            #         elif i.project.purchase_type.value == u'一般勞務':
            #             check_fields = ['ser_approved_plan', 'ser_signed_tender', 'ser_announcement_tender',
            #                             'ser_selection_meeting', 'ser_promise', 'ser_work_plan',
            #                             'ser_interim_report', 'ser_final_report'
            #                             ]
            #         for cf in check_fields:
            #             if not getattr(i, 'act_%s' % (cf)) and getattr(i, 'sch_%s' % (cf)) and getattr(i, 'sch_%s' % (cf)) < TODAY():
            #                 ids.append(projects_map[i.project.id])
            #                 break
            #     # result = result.filter(id__in=ids)
            if info.get('not_finish', 'false') == 'true': #已匯入，尚未填報完畢
                import_projects = FRCMUserGroup.objects.filter(project__in=[i.project for i in result], group__name__in=[u'負責主辦工程師', u'自辦主辦工程師'])
                ids += [r.id for r in result.filter(project__in=[i.project for i in import_projects], complete=False)]
            if info.get('no_owner', 'false') == 'true': #無人認領工程
                import_projects = FRCMUserGroup.objects.filter(project__in=[i.project for i in result], group__name__in=[u'負責主辦工程師', u'自辦主辦工程師'])
                ids += [r.id for r in result.exclude(project__in=[i.project for i in import_projects])]
            if info.get('progress_freeze', 'false') == 'true': #填報完畢，進度停滯
                last_chase = CountyChaseTime.objects.filter(id__lt=info.get('chase_time_id')).order_by('-id').first()
                projects_map = {}
                for i in last_chase.countychaseprojectonetomany_set.all():
                    projects_map[i.project.id] = i
                for r in result.filter(complete=True):
                    if projects_map.has_key(r.project.id) \
                    and projects_map[r.project.id].actual_progress_percent == r.actual_progress_percent:
                        ids.append(r.id)
                # result = result.filter(id__in=ids)
            if info.get('key_word', 'false') == 'true': #關鍵字搜尋
                for key in re.split('[ ,]+', info.get('key_word_info', '')):
                    if key:
                        ids.extend([i.id for i in result.filter(memo__icontains=key)])
                        ids.extend([i.id for i in result.filter(behind_memo__icontains=key)])
                
            # if info.get('repeat_report', 'false') == 'true': #填報完畢，數據與上期填報重複 或 進度停滯
            #     last_chase = CountyChaseTime.objects.filter(id__lt=info.get('chase_time_id')).order_by('-id').first()
            #     projects_map = {}
            #     for i in last_chase.countychaseprojectonetomany_set.all():
            #         projects_map[i.project.id] = i
            #     for r in result.filter(complete=True):
            #         if projects_map.has_key(r.project.id) \
            #         and projects_map[r.project.id].schedul_progress_percent == r.schedul_progress_percent \
            #         and projects_map[r.project.id].actual_progress_percent == r.actual_progress_percent \
            #         and projects_map[r.project.id].self_payout == r.self_payout \
            #         and projects_map[r.project.id].local_payout == r.local_payout \
            #         and projects_map[r.project.id].self_unpay == r.self_unpay \
            #         and projects_map[r.project.id].local_unpay == r.local_unpay:
            #             ids.append(r.id)
            #     # result = result.filter(id__in=ids)
            
            result = result.filter(id__in=ids)
        paginator = Paginator(request.GET, result, resource_uri='/fishuser/api/v2/countychaseprojectonetomany/search/')

        objects = []
        for r in paginator.page()['objects']:
            bundle = self.build_bundle(obj=r, request=request)
            bundle = self.full_dehydrate(bundle)
            objects.append(bundle)

        object_list = {
            'meta': paginator.page()['meta'],
            'objects': objects,
            'all_ids': ','.join([str(i.id) for i in result])
        }

        self.log_throttled_access(request)

        return self.create_response(request, object_list)



class CountyChaseProjectOneToManyPayoutResource(ModelResource):
    chase = fields.ForeignKey(CountyChaseProjectOneToManyResource, 'chase')
    budget = fields.ForeignKey(BudgetResource, 'budget')

    class Meta:
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        queryset = CountyChaseProjectOneToManyPayout.objects.all()
        always_return_data = True
        resource_name = 'countychaseprojectonetomanypayout'
        ordering = ["id"]
        allowed_methods = ['get', 'post', 'put', 'delete', 'patch']
        filtering = {
            "id": ("exact"),
            "budget": ("exact"),
            "chase": ("exact"),
        }



class ProjectPhotoResource(ModelResource):
    project = fields.ForeignKey(ProjectResource, 'project')

    class Meta:
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        always_return_data = True
        queryset = ProjectPhoto.objects.all()
        resource_name = 'projectphoto'
        ordering = ["project"]
        allowed_methods = ['get', 'post', 'put', 'delete']
        filtering = {
            "id": ("exact"),
            "project": ("exact"),
        }

    def obj_delete(self, bundle, **kwargs):
        f = ProjectPhoto.objects.get(pk=kwargs['pk'])
        request = bundle.request
        try:
            os.remove(f.file.path)
        except: pass
        super(ProjectPhotoResource, self).obj_delete(bundle, **kwargs)



class ManageMoneyResource(ModelResource):
    
    class Meta:
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        always_return_data = True
        queryset = ManageMoney.objects.all()
        resource_name = 'managemoney'
        ordering = []
        allowed_methods = ['get', 'post', 'put', 'delete']
        filtering = {
            "id": ("exact"),
            "year": ("year"),
        }



class ProjectManageMoneyResource(ModelResource):
    managemoney = fields.ForeignKey(ManageMoneyResource, 'managemoney')
    project = fields.ForeignKey(ProjectResource, 'project')

    class Meta:
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        always_return_data = True
        queryset = ProjectManageMoney.objects.all()
        resource_name = 'projectmanagemoney'
        ordering = []
        allowed_methods = ['get', 'post', 'put', 'delete']
        filtering = {
            "id": ("exact"),
            "managemoney": ("managemoney"),
            "project": ("project"),
        }


     
class ManageMoneyRemainResource(ModelResource):

    class Meta:
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        always_return_data = True
        queryset = ManageMoneyRemain.objects.all()
        resource_name = 'managemoneyremain'
        ordering = []
        allowed_methods = ['get', 'post', 'put', 'delete']
        filtering = {
            "id": ("exact"),
            "year": ("year"),
        }   


class ProjectBidMoneyVersionResource(ModelResource):
    project = fields.ForeignKey(ProjectResource, 'project')

    class Meta:
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        always_return_data = True
        queryset = ProjectBidMoneyVersion.objects.all()
        resource_name = 'projectbidmoneyversion'
        ordering = []
        allowed_methods = ['get', 'post', 'put', 'delete']
        filtering = {
            "id": ("exact"),
        }   
        


class ProjectBidMoneyVersionDetailResource(ModelResource):
    version = fields.ForeignKey(ProjectBidMoneyVersionResource, 'version')

    class Meta:
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        always_return_data = True
        queryset = ProjectBidMoneyVersionDetail.objects.all()
        resource_name = 'projectbidmoneyversiondetail'
        ordering = []
        allowed_methods = ['get', 'post', 'put', 'delete']
        filtering = {
            "id": ("exact"),
        }   



class SystemInformationResource(ModelResource):
    user = fields.ForeignKey(UserResource, 'user')

    class Meta:
        queryset = SystemInformation.objects.all()
        resource_name = 'systeminformation'
        ordering = ["start_date"]
        allowed_methods = ['get', 'post', 'put', 'delete']
        always_return_data = True
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        filtering = {
            "id": ("exact", ),
            "user": ("exact", ),
        }

    def obj_delete(self, bundle, **kwargs):
        info = SystemInformation.objects.get(pk=kwargs['pk'])
        for file in info.systeminformationfile_set.all():
            try:
                os.remove(os.path.join(settings.BASE_DIR, 'media', file.file.name))
            except: pass
        super(SystemInformationResource, self).obj_delete(bundle, **kwargs)



class SystemInformationFileResource(ModelResource):
    systeminformation = fields.ForeignKey(SystemInformationResource, 'question')

    class Meta:
        queryset = SystemInformationFile.objects.all()
        resource_name = 'systeminformationfile'
        ordering = ["id"]
        allowed_methods = ['get', 'post', 'put', 'delete']
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        filtering = {
            "question": ("exact", ),
        }


    def obj_delete(self, bundle, **kwargs):
        file = SystemInformationFile.objects.get(pk=kwargs['pk'])
        try:
            os.remove(os.path.join(settings.BASE_DIR, 'media', file.file.name))
        except: pass
        super(SystemInformationFileResource, self).obj_delete(bundle, **kwargs)


    
