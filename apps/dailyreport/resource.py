#-*- coding: utf8 -*-
import logging, datetime, re, json, traceback, sys

from django.db import IntegrityError
from django.db.models.signals import post_save
from django.core.exceptions import ValidationError
from django.conf import settings
# from django.conf.urls import defaults as urls
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.contrib.auth.models import Group

from django.http import HttpResponseForbidden, HttpResponseServerError, HttpResponse
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_exempt
from django.utils.cache import patch_cache_control
from django.utils.translation import ugettext as _
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

from guardian.shortcuts import assign, get_objects_for_user, get_perms
import os, random, json, re, datetime, decimal

from fishuser.models import Project, FRCMUserGroup

from dailyreport.models import Holiday, Option, Version, Item, EngProfile
from dailyreport.models import ScheduleItem, LaborEquip, SpecialDate, Extension
from dailyreport.models import Report, ReportHoliday, ReportItem, ReportLaborEquip, SiteMaterial

from django.conf import settings
API_LIMIT_PER_PAGE = settings.API_LIMIT_PER_PAGE

def TODAY(): return datetime.date.today()

def NOW(): return datetime.datetime.now()

__enable__ = [
                'ProjectResource',
                'OptionResource',
                'HolidayResource',
                'VersionResource',
                'ItemResource',
                'ScheduleItemResource',
                'EngProfileResource',
                'ExtensionResource',
                'LaborEquipResource',
                'SpecialDateResource',
                'ReportResource',
                'ReportItemResource',
                'ReportLaborEquipResource',
                'SiteMaterialResource',
                ]

class RESTForbidden(Exception):
    pass



class SillyAuthentication(Authentication):
    def is_authenticated(self, request, **kwargs):
        if settings.DEBUG: logging.info('SillyAuthentication: %s' % request.user.is_authenticated())
        return request.user.is_authenticated()


class ProjectResource(ModelResource):
    class Meta:
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        queryset = Project.objects.all()
        resource_name = 'project'
        ordering = ["id"]
        allowed_methods = ['get', 'post', 'put']



class OptionResource(ModelResource):
    class Meta:
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        queryset = Option.objects.all()
        resource_name = 'option'
        ordering = ["swarm"]
        allowed_methods = ['get', 'post', 'put']



class HolidayResource(ModelResource):

    class Meta:
        queryset = Holiday.objects.all()
        resource_name = 'holiday'
        allowed_methods = ['get', 'post', 'put', 'delete']
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        filtering = {
        }



class VersionResource(ModelResource):
    project = fields.ForeignKey(ProjectResource, 'project')

    class Meta:
        queryset = Version.objects.all()
        resource_name = 'version'
        always_return_data = True
        allowed_methods = ['get', 'post', 'put', 'delete']
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        filtering = {
        }


    def obj_create(self, bundle, **kwargs):
        project = Project.objects.get(id=bundle.data['project_id'])
        start_date = bundle.data['start_date']
        engprofile = EngProfile.objects.get(project=project)
        pre_version = engprofile.readLatestVersion()
        user = bundle.request.user
        if not 'edit_item' in get_perms(user, engprofile) and not user.has_perm(u'dailyreport.edit_item'):
            raise RESTForbidden(_('You have no permission'))

        pre_items = Item.objects.filter(version=pre_version, kind__value=u'工項')
        pre_i_money = decimal.Decimal('0')
        pre_c_money = decimal.Decimal('0')
        for i in pre_items:
            report_items = ReportItem.objects.filter(item__in=i.read_brother_items(), report__date__lt=start_date)
            pre_i_money += sum([j.i_num for j in report_items.exclude(i_num='0')]) * i.unit_price
            pre_c_money += sum([j.c_num for j in report_items.exclude(c_num='0')]) * i.unit_price

        bdl = super(VersionResource, self
                    ).obj_create(bundle, request=bundle.request,
                                    project=project,
                                    start_date=start_date,
                                    engs_price=pre_version.engs_price,
                                    schedule_price=0,
                                    update_time=NOW(),
                                    pre_i_money=pre_i_money,
                                    pre_c_money=pre_c_money,
                                    )

        bundle.obj.new_version_copy_pre_item()

        return bdl

    def obj_delete(self, bundle, **kwargs):
        version = Version.objects.get(pk=kwargs['pk'])
        user = bundle.request.user
        engprofile = EngProfile.objects.get(project=version.project)
        if not 'edit_item' in get_perms(user, engprofile) and not user.has_perm(u'dailyreport.edit_item'):
            raise RESTForbidden(_('You have no permission'))

        if version.read_next_version():
            raise RESTForbidden(_('This is not Last Version'))

        if not version.read_pre_version():
            raise RESTForbidden(_('This is OnlyOne Version'))

        #切換變更設計日期之後的item紀錄
        for ri in ReportItem.objects.filter(report__project=version.project, report__date__gte=version.start_date):
            if ri.item.pre_item:
                ri.item = ri.item.pre_item
                ri.save()

        super(VersionResource, self).obj_delete(bundle, **kwargs)



class ItemResource(ModelResource):
    version = fields.ForeignKey(VersionResource, 'version')
    kind = fields.ForeignKey(OptionResource, 'kind')
    uplevel = fields.ForeignKey('self', 'uplevel', null=True)
    pre_item = fields.ForeignKey('self', 'pre_item', null=True)

    class Meta:
        queryset = Item.objects.all()
        resource_name = 'item'
        allowed_methods = ['get', 'post', 'put', 'delete']
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        filtering = {
        }

    def dehydrate_name(self, bundle):
        if bundle.obj:
            items = [bundle.obj]
            def readItemInlist(items, check_item):
                for i in check_item.read_sub_item_in_list():
                    items.append(i)
                    items = readItemInlist(items, i)
                return items
            items = readItemInlist(items, bundle.obj)
            delete_ids = ".".join([str(i.id) for i in items])
            bundle.data['delete_ids'] = delete_ids
        return bundle.data['name']

    def obj_delete(self, bundle, **kwargs):
        item = Item.objects.get(pk=kwargs['pk'])
        version = item.version
        user = bundle.request.user
        engprofile = EngProfile.objects.get(project=item.version.project)
        if not 'edit_item' in get_perms(user, engprofile) and not user.has_perm(u'dailyreport.edit_item'):
            raise RESTForbidden(_('You have no permission'))

        for i in Item.objects.filter(uplevel=item.uplevel, priority__gt=item.priority):
            i.priority -= 1
            i.save()

        for ri in ReportItem.objects.filter(item=item).exclude(i_num='0', c_num='0').prefetch_related('report', 'item'):
            ri.report.update_sum_money()
        super(ItemResource, self).obj_delete(bundle, **kwargs)
        version.update_time = NOW()
        version.save()

        for v in Version.objects.filter(project=version.project):
            pre_version = v.read_pre_version()
            if not pre_version: continue
            pre_items = Item.objects.filter(version=v, kind__value=u'工項')
            pre_i_money = decimal.Decimal('0')
            pre_c_money = decimal.Decimal('0')
            for i in pre_items:
                report_items = ReportItem.objects.filter(item__in=i.read_brother_items(), report__date__lt=v.start_date)
                # if i.is_onetype or i.use_money: i.unit_price = i.unit_num
                pre_i_money += sum([j.i_num for j in report_items.exclude(i_num='0')]) * i.unit_price
                pre_c_money += sum([j.c_num for j in report_items.exclude(c_num='0')]) * i.unit_price
            v.pre_i_money = pre_i_money
            v.pre_c_money = pre_c_money
            v.save()
            
    def obj_update(self, bundle, request=None, **kwargs):
        item = Item.objects.get(pk=kwargs['pk'])
        user = bundle.request.user
        engprofile = EngProfile.objects.get(project=item.version.project)
        if not 'edit_item' in get_perms(user, engprofile) and not user.has_perm(u'dailyreport.edit_item'):
            raise RESTForbidden(_('You have no permission'))

        super(ItemResource, self).obj_update(bundle, **kwargs)
        
        if bundle.data.get('unit_price', ''):
            #調整version 的 pre_money
            version = item.version
            items = Item.objects.filter(version=version, kind__value=u'工項')
            pre_i_money = decimal.Decimal('0')
            pre_c_money = decimal.Decimal('0')
            for i in items:
                report_items = ReportItem.objects.filter(item__in=i.read_brother_items(), report__date__lt=version.start_date)
                pre_i_money += sum([j.i_num for j in report_items.exclude(i_num='0')]) * i.unit_price
                pre_c_money += sum([j.c_num for j in report_items.exclude(c_num='0')]) * i.unit_price
            version.pre_i_money = pre_i_money
            version.pre_c_money = pre_c_money
            version.save()
            for ri in ReportItem.objects.filter(item=item).exclude(i_num='0', c_num='0'):
                ri.report.update_sum_money()
        
        version = item.version
        version.update_time = NOW()
        version.save()
        return bundle.obj



class ScheduleItemResource(ModelResource):
    version = fields.ForeignKey(VersionResource, 'version')
    kind = fields.ForeignKey(OptionResource, 'kind')
    uplevel = fields.ForeignKey('self', 'uplevel', null=True)
    pre_item = fields.ForeignKey('self', 'pre_item', null=True)

    class Meta:
        queryset = ScheduleItem.objects.all()
        resource_name = 'scheduleitem'
        allowed_methods = ['get', 'post', 'put', 'delete']
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        filtering = {
        }

    def dehydrate_name(self, bundle):
        if bundle.obj:
            items = [bundle.obj]
            def readItemInlist(items, check_item):
                for i in check_item.read_sub_item_in_list():
                    items.append(i)
                    items = readItemInlist(items, i)
                return items
            items = readItemInlist(items, bundle.obj)
            delete_ids = ".".join([str(i.id) for i in items])
            bundle.data['delete_ids'] = delete_ids

        return bundle.data['name']

    def obj_update(self, bundle, request=None, **kwargs):
        item = ScheduleItem.objects.get(pk=kwargs['pk'])
        user = bundle.request.user
        engprofile = EngProfile.objects.get(project=item.version.project)
        if not 'edit_item' in get_perms(user, engprofile) and not user.has_perm(u'dailyreport.edit_item'):
            raise RESTForbidden(_('You have no permission'))

        if bundle.data.get('es', ''):
            if item.ef < int(bundle.data['es']):
                item.ef = int(bundle.data['es'])
                item.save()
        if bundle.data.get('ef', ''):
            if item.es > int(bundle.data['ef']):
                item.es = int(bundle.data['ef'])
                item.save()

        super(ScheduleItemResource, self).obj_update(bundle, **kwargs)
        return bundle.obj



class EngProfileResource(ModelResource):
    project = fields.ForeignKey(ProjectResource, 'project')
    date_type = fields.ForeignKey(OptionResource, 'date_type', null=True)
    round_type = fields.ForeignKey(OptionResource, 'round_type')
    must_fix_item = fields.ToManyField(ItemResource, 'must_fix_item', null=True)

    class Meta:
        queryset = EngProfile.objects.all()
        resource_name = 'engprofile'
        allowed_methods = ['get', 'post', 'put']
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        filtering = {
            "project": ("exact", ),
        }

    def prepend_urls(self):
        return [
            url(r'^(?P<resource_name>%s)/(?P<project_id>[0-9]+)/reset_item_priority/$' % (self._meta.resource_name), self.wrap_view('reset_item_priority'), name='api_reset_item_priority'),
            url(r'^(?P<resource_name>%s)/(?P<project_id>[0-9]+)/get_monthly_info/$' % (self._meta.resource_name), self.wrap_view('get_monthly_info'), name='api_get_monthly_info'),
            url(r'^(?P<resource_name>%s)/(?P<project_id>[0-9]+)/get_monthly_equipment_and_crew/$' % (self._meta.resource_name), self.wrap_view('get_monthly_equipment_and_crew'), name='api_get_monthly_equipment_and_crew'),
        ]

    def reset_item_priority(self, request, **kwargs):
        try: eng = self._meta.queryset.get(project__id=kwargs['project_id'])
        except EngProfile.DoesNotExist: raise ImmediateHttpResponse(HttpBadRequest('EngProfile does not exist'))

        eng.reset_item_priority()

        return HttpResponse(json.dumps({'status': True}))

    def get_monthly_info(self, request, **kwargs):
        try: eng = self._meta.queryset.get(project__id=kwargs['project_id'])
        except EngProfile.DoesNotExist: raise ImmediateHttpResponse(HttpBadRequest('EngProfile does not exist'))

        info = eng.get_monthly_info(int(request.GET['year']), int(request.GET['month']))
        info['date'] = str(info['date'])
        return HttpResponse(json.dumps(info))

    def get_monthly_equipment_and_crew(self, request, **kwargs):
        try: eng = self._meta.queryset.get(project__id=kwargs['project_id'])
        except EngProfile.DoesNotExist: raise ImmediateHttpResponse(HttpBadRequest('EngProfile does not exist'))
        info = eng.get_monthly_equipment_and_crew(int(request.GET['year']), int(request.GET['month']))
        for i in info['equipment']:
            i['quantity'] = float(str(i['quantity']))
        for i in info['crew']:
            i['quantity'] = float(str(i['quantity']))
            
        return HttpResponse(json.dumps(info))



class ExtensionResource(ModelResource):
    project = fields.ForeignKey(ProjectResource, 'project')

    class Meta:
        queryset = Extension.objects.all()
        always_return_data = True
        resource_name = 'extension'
        allowed_methods = ['get', 'post', 'put', 'delete']
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        filtering = {
            "id": ("exact", ),
        }

    def obj_delete(self, bundle, **kwargs):
        extension = Extension.objects.get(pk=kwargs['pk'])
        project = extension.project
        engprofile = EngProfile.objects.get(project=project)
        user = bundle.request.user
        if not 'edit_engprofile' in get_perms(user, engprofile) and not user.has_perm(u'dailyreport.edit_engprofile'):
            raise RESTForbidden(_('You have no permission'))

        super(ExtensionResource, self).obj_delete(bundle, **kwargs)

        engprofile.extension = sum([i.day for i in Extension.objects.filter(project=project)])
        engprofile.save()

        

class LaborEquipResource(ModelResource):
    project = fields.ForeignKey(ProjectResource, 'project')
    type = fields.ForeignKey(OptionResource, 'type')
    uplevel = fields.ForeignKey('self', 'uplevel', null=True)

    class Meta:
        queryset = LaborEquip.objects.all()
        resource_name = 'laborequip'
        always_return_data = True
        allowed_methods = ['get', 'post', 'put', 'delete']
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        filtering = {
            "id": ("exact", ),
        }

    def dehydrate_id(self, bundle):
        if bundle.obj:
            if not bundle.obj.is_first():
                up = LaborEquip.objects.get(project=bundle.obj.project, type=bundle.obj.type, sort=bundle.obj.sort-1)
            else: up = None
            if not bundle.obj.is_last():
                down = LaborEquip.objects.get(project=bundle.obj.project, type=bundle.obj.type, sort=bundle.obj.sort+1)
            else: down = None
            bundle.data['up_id'] = up.id if up else None
            bundle.data['up_is_first'] = up.is_first() if up else None
            bundle.data['up_is_last'] = up.is_last() if up else None
            bundle.data['down_id'] = down.id if down else None
            bundle.data['down_is_first'] = down.is_first() if down else None
            bundle.data['down_is_last'] = down.is_last() if down else None
            bundle.data['is_first'] = bundle.obj.is_first()
            bundle.data['is_last'] = bundle.obj.is_last()

        return bundle.data['id']

    def obj_update(self, bundle, request=None, **kwargs):
        laborequip = LaborEquip.objects.get(pk=kwargs['pk'])
        
        if bundle.data.get('sort_duration', '') == 'up':
            up_row = LaborEquip.objects.get(project=laborequip.project, type=laborequip.type, sort=laborequip.sort-1)
            up_row.sort, laborequip.sort = laborequip.sort, up_row.sort
            up_row.save()
            laborequip.save()
        elif bundle.data.get('sort_duration', '') == 'down':
            down_row = LaborEquip.objects.get(project=laborequip.project, type=laborequip.type, sort=laborequip.sort+1)
            down_row.sort, laborequip.sort = laborequip.sort, down_row.sort
            down_row.save()
            laborequip.save()
        
        return super(LaborEquipResource, self).obj_update(bundle, **kwargs)

    def obj_delete(self, bundle, **kwargs):
        laborequip = LaborEquip.objects.get(pk=kwargs['pk'])
        for i in LaborEquip.objects.filter(project=laborequip.project, type=laborequip.type, sort__gt=laborequip.sort):
            i.sort -= 1
            i.save()

        super(LaborEquipResource, self).obj_delete(bundle, **kwargs)



class SpecialDateResource(ModelResource):
    project = fields.ForeignKey(ProjectResource, 'project')
    type = fields.ForeignKey(OptionResource, 'type')

    class Meta:
        queryset = SpecialDate.objects.all()
        resource_name = 'specialdate'
        allowed_methods = ['get', 'post', 'put', 'delete']
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        filtering = {
            "id": ("exact", ),
        }


    def dehydrate_id(self, bundle):
        if bundle.obj:
            bundle.data['type_list_name'] = bundle.obj.type.value
        return bundle.data['id']


    def obj_delete(self, bundle, **kwargs):
        specialdate = SpecialDate.objects.get(pk=kwargs['pk'])
        start_date = specialdate.start_date
        end_date = specialdate.end_date
        project = specialdate.project
        engprofile = EngProfile.objects.get(project=project)
        user = bundle.request.user
        if not 'edit_special_date' in get_perms(user, engprofile) and not user.has_perm(u'dailyreport.edit_special_date'):
            raise RESTForbidden(_('You have no permission'))

        super(SpecialDateResource, self).obj_delete(bundle, **kwargs)

        #休息日不能存在日報表填報紀錄
        for hreport in ReportHoliday.objects.filter(project=project, date__gte=start_date, date__lte=end_date):
            report = Report(
                project = hreport.project,
                date = hreport.date,
                morning_weather = hreport.morning_weather,
                afternoon_weather = hreport.afternoon_weather,
                contractor_check=True,
                inspector_check=True,
                i_sum_money='0',
                c_sum_money='0',
                describe_subcontractor=hreport.describe_subcontractor,
                sampling=hreport.sampling,
                notify=hreport.notify,
                note=hreport.note,
                c_describe_subcontractor=hreport.c_describe_subcontractor,
                c_sampling=hreport.c_sampling,
                c_notify=hreport.c_notify,
                c_note=hreport.c_note,
                i_project_status = hreport.i_project_status,
                pre_education = hreport.pre_education,
                has_insurance = hreport.has_insurance,
                safety_equipment = hreport.safety_equipment,
                pre_check = hreport.pre_check,
                i_pre_check =hreport.i_pre_check,
            )
            report.save()
            hreport.delete()

        workingdates = engprofile.readWorkingDate()
        for report in Report.objects.filter(project=project, date__gte=start_date, date__lte=end_date):
            if report.date not in workingdates:
                report.delete()
            engprofile.save()

        

class ReportResource(ModelResource):
    project = fields.ForeignKey(ProjectResource, 'project')
    morning_weather = fields.ForeignKey(OptionResource, 'morning_weather')
    afternoon_weather = fields.ForeignKey(OptionResource, 'afternoon_weather')

    class Meta:
        queryset = Report.objects.all()
        resource_name = 'report'
        always_return_data = True
        allowed_methods = ['get', 'post', 'put', 'delete']
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        filtering = {
            "id": ("exact", ),
            "project": ("exact", ),
            "date": ALL_WITH_RELATIONS,
        }

    def obj_update(self, bundle, request=None, **kwargs):
        report = Report.objects.get(pk=kwargs['pk'])
        user = bundle.request.user
        engprofile = EngProfile.objects.get(project=report.project)
        if bundle.data.get('inspector_check', '') == False:
            if not 'edit_inspector_report' in get_perms(user, engprofile) and not user.has_perm(u'dailyreport.edit_inspector_report'):
                raise RESTForbidden(_('You have no permission'))
        elif bundle.data.get('contractor_check', '') == False:
            if not 'edit_contractor_report' in get_perms(user, engprofile) and not user.has_perm(u'dailyreport.edit_contractor_report'):
                raise RESTForbidden(_('You have no permission'))

        bundle = super(ReportResource, self).obj_update(bundle, **kwargs)
        user = bundle.request.user
        report = Report.objects.get(pk=kwargs['pk'])
        engprofile = EngProfile.objects.get(project=report.project)

        if not report.contractor_check and not report.inspector_check:
            report.delete()
        elif bundle.data.get('contractor_check', '') == False:
            report_items = report.reportitem_set.all()
            for report_item in report_items: #刪除數量
                if report_item.c_num:
                    report_item.c_num = 0
                    report_item.save()
            report.c_describe_subcontractor = '' #刪除填寫內容
            report.c_sampling = ''
            report.c_notify = ''
            report.c_note = ''
            report.c_sum_money = 0
            report.save()
            ReportLaborEquip.objects.filter(report=report).delete() #刪除人員機具
        elif bundle.data.get('inspector_check', '') == False:
            report_items = report.reportitem_set.all()
            for report_item in report_items: #刪除數量
                if report_item.i_num:
                    report_item.i_num = 0
                    report_item.save()
            report.describe_subcontractor = '' #刪除填寫內容
            report.sampling = ''
            report.notify = ''
            report.note = ''
            report.i_sum_money = 0
            report.save()
            
        engprofile.save()
        return bundle



class ReportItemResource(ModelResource):
    report = fields.ForeignKey(ReportResource, 'report')
    item = fields.ForeignKey(ItemResource, 'item')

    class Meta:
        queryset = ReportItem.objects.all()
        resource_name = 'reportitem'
        allowed_methods = ['get', 'post', 'put', 'delete']
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        filtering = {
        }



class ReportLaborEquipResource(ModelResource):
    report = fields.ForeignKey(ReportResource, 'report')
    type = fields.ForeignKey(LaborEquipResource, 'type')

    class Meta:
        queryset = ReportLaborEquip.objects.all()
        resource_name = 'reportlaborequip'
        allowed_methods = ['get', 'post', 'put', 'delete']
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        filtering = {
        }



class SiteMaterialResource(ModelResource):
    report = fields.ForeignKey(ReportResource, 'report')

    class Meta:
        queryset = SiteMaterial.objects.all()
        resource_name = 'sitematerial'
        allowed_methods = ['get', 'post', 'put', 'delete']
        authentication = MultiAuthentication(ApiKeyAuthentication(), SessionAuthentication(), SillyAuthentication())
        authorization = Authorization()
        filtering = {
        }