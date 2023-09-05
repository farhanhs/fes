# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
from django.template import Template
from django.template import Context
from django.template import RequestContext
from django.template.loader import get_template
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django import forms
from django.db.models import Q
from django.db.models import F
from django.forms import ModelForm
from django.contrib.auth.models import User, Group
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.decorators import login_required
from guardian.shortcuts import assign, get_perms

from dailyreport.models import Holiday
from dailyreport.models import Option
from dailyreport.models import LABOR_TYPE
from dailyreport.models import EQUIP_TYPE
from dailyreport.models import EngProfile
from dailyreport.models import Extension
from dailyreport.models import Version
from dailyreport.models import Item
from dailyreport.models import ScheduleItem
from dailyreport.models import LaborEquip
from dailyreport.models import SpecialDate
from dailyreport.models import Report
from dailyreport.models import ReportHoliday
from dailyreport.models import ReportItem
from dailyreport.models import ReportLaborEquip
from dailyreport.models import SiteMaterial

from dailyreport.parse_pcces import ParsePCCES
from dailyreport.lib import ProgressChart, make_contractor_excel_file, make_inspector_excel_file
from dailyreport.lib import make_contractor_excel_file2, make_inspector_excel_file2, make_working_date_excel_file

from fishuser.models import Project, FRCMUserGroup

response = HttpResponse()
response['Pragma'] = 'No-cache'
response['Cache-control'] = 'No-cache'

import os
import random
import datetime
import time
import decimal
import csv
import xlsxwriter
import urllib2
from cStringIO import StringIO
from hashlib import md5
from math import ceil
from urllib import urlencode
from urllib2 import Request
from urllib2 import urlopen
from urllib2 import HTTPError
from base64 import b64decode
import json
if not hasattr(json, "write"):
    #for python2.6
    json.write = json.dumps
    json.read = json.loads

from django.conf import settings
#判斷是否有開放試驗記錄的功能
try:
    HAVE_RCM_TEST_RECORD_SYSTEM = settings.HAVE_RCM_TEST_RECORD_SYSTEM
except:
    HAVE_RCM_TEST_RECORD_SYSTEM = False
#判斷是否只能看自己所屬單位的工程案
try:
    ONLY_CAN_SEE_THE_SAME_UNIT = settings.ONLY_CAN_SEE_THE_SAME_UNIT
except:
    ONLY_CAN_SEE_THE_SAME_UNIT = False

#設定群組名稱
MAJOR_ENGINEER_NAME = u'負責主辦工程師'
MAJOR2_ENGINEER_NAME = u'自辦主辦工程師'
MINOR_ENGINEER_NAME = u'協同主辦工程師'
INSPECTOR_NAME = u'監造廠商'
CONTRACTOR_NAME = u'營造廠商'

DIRKIND = Option.objects.get(swarm='item_kind', value='目錄')
ITEMKIND = Option.objects.get(swarm='item_kind', value='工項')
NONITEMKIND = Option.objects.get(swarm='item_kind', value='非工項')
ALL_ROUND = Option.objects.get(swarm='round_type', value='總價四捨五入')
DIR_ROUND = Option.objects.get(swarm='round_type', value='目錄四捨五入')
ITEM_ROUND = Option.objects.get(swarm='round_type', value='項目四捨五入')


def TODAY(): return datetime.date.today()
def NOW(): return datetime.datetime.now()

def _make_choose():
    options = Option.objects.all()
    chooses = {}
    for i in options:
        if chooses.has_key(i.swarm):
            chooses[i.swarm].append(i)
        else:
            chooses[i.swarm] = [i]
    return chooses

def start_page(R, **kw):
    # 決定進入page是哪一頁
    project = Project.objects.get(id=kw['project_id'])
    if not R.user.has_perm('fishuser.view_all_project_in_remote_control_system'):
        #沒有 "在(遠端工程系統)中_觀看_所有_工程案資訊"
        if not 'view_single_project_in_remote_control_system' in get_perms(R.user, project):
            #沒有 觀看此project 的 "在(遠端工程系統)中_觀看_單一_工程案資訊" 權限
            if project.unit != R.user.user_profile.unit:
                return HttpResponseRedirect('/')
        elif 'view_single_project_in_remote_control_system' in get_perms(R.user, project):
            #有 觀看此project 的 "在(遠端工程系統)中_觀看_單一_工程案資訊" 權限
            if not R.user.frcmusergroup_set.get(project=project).is_active:
                #被關閉權限的
                return HttpResponseRedirect('/')
    else:
        if R.user.username[1] == '_' and not R.user.is_staff:
            if project.unit != R.user.user_profile.unit:
                return HttpResponseRedirect('/')

    try:
        engprofile = EngProfile.objects.get(project=project)
    except EngProfile.DoesNotExist:
        engprofile = EngProfile()
        engprofile.setDefaultEngProfile(project=project)
        engprofile.create_root_item()
    
    try:
        group_name = FRCMUserGroup.objects.get(project=project, user=R.user).group.name
        if group_name == CONTRACTOR_NAME:
            type = 'contractor'
        elif group_name in [INSPECTOR_NAME, MAJOR_ENGINEER_NAME, MAJOR_ENGINEER_NAME2, MINOR_ENGINEER_NAME]:
            type = 'inspector'
    except:
        group_name = ''
        type = 'inspector'

    varsion = engprofile.readLatestVersion()
    if not varsion:
        engprofile.start_date = None
        engprofile.save()
        engprofile.create_root_item()

    if not engprofile.start_date:
        return HttpResponseRedirect('/dailyreport/engprofile/%s/%s/' % (project.id, type))
    #elif engprofile.start_date and not varsion:
    #    return HttpResponseRedirect('/dailyreport/engprofile/%s/%s/' % (project.id, type))
    elif varsion.item_set.all().count() == 1:
        return HttpResponseRedirect('/dailyreport/item/%s/%s/' % (type, varsion.id))
    else:
        if TODAY() < engprofile.start_date or not group_name:
            return HttpResponseRedirect('/dailyreport/report/%s/%s/' % (project.id, type))
        elif group_name:
            return HttpResponseRedirect('/dailyreport/report/%s/%s/#%s' % (project.id, type, TODAY()))
        
        
@login_required
def read_eng_profile(R, **kw):
    # 基本資料  編輯頁面
    project = Project.objects.get(id=kw['project_id'])
    report_type = kw['report_type']
    
    if not R.user.has_perm('fishuser.view_all_project_in_remote_control_system'):
        #沒有 "在(遠端工程系統)中_觀看_所有_工程案資訊"
        if not 'view_single_project_in_remote_control_system' in get_perms(R.user, project):
            #沒有 觀看此project 的 "在(遠端工程系統)中_觀看_單一_工程案資訊" 權限
            if project.unit != R.user.user_profile.unit:
                return HttpResponseRedirect('/')
        elif 'view_single_project_in_remote_control_system' in get_perms(R.user, project):
            #有 觀看此project 的 "在(遠端工程系統)中_觀看_單一_工程案資訊" 權限
            if not R.user.frcmusergroup_set.get(project=project).is_active:
                #被關閉權限的
                return HttpResponseRedirect('/')
    else:
        if R.user.username[1] == '_' and not R.user.is_staff:
            if project.unit != R.user.user_profile.unit:
                return HttpResponseRedirect('/')

    try:
        engprofile = EngProfile.objects.get(project=project)
    except EngProfile.DoesNotExist:
        engprofile = EngProfile()
        engprofile.setDefaultEngProfile(project=project)
        engprofile.create_root_item()

    if 'edit_engprofile' in get_perms(R.user, engprofile) or R.user.has_perm('dailyreport.edit_engprofile'):
        if R.user.is_staff:
            engprofile.is_inspector = True
            edit = True
        else:
            if FRCMUserGroup.objects.get(project=project, user=R.user).group.name == CONTRACTOR_NAME:
                engprofile.is_inspector = False
            else:
                engprofile.is_inspector = True
            edit = True
    else:
        edit = False

    extensions = Extension.objects.filter(project=project).order_by('date')

    t = get_template(os.path.join('dailyreport', 'zh-tw', 'eng_profile.html'))
    html = t.render(RequestContext(R,{
        'engprofile': engprofile,
        'edit': edit,
        'choose': _make_choose(),
        'report_type': report_type,
        'extensions': extensions,
        'toppage_name': u'基本資料',
        }))
    return HttpResponse(html)


@login_required
def read_and_edit_item(R, **kw):
    # 日報表契約項目  編輯頁面
    version = Version.objects.get(id=kw['version_id'])
    project = version.project
    engprofile = EngProfile.objects.get(project=project)
    engprofile.create_root_item()
    report_type = kw['report_type']

    if not R.user.has_perm('fishuser.view_all_project_in_remote_control_system'):
        #沒有 "在(遠端工程系統)中_觀看_所有_工程案資訊"
        if not 'view_single_project_in_remote_control_system' in get_perms(R.user, project):
            #沒有 觀看此project 的 "在(遠端工程系統)中_觀看_單一_工程案資訊" 權限
            if project.unit != R.user.user_profile.unit:
                return HttpResponseRedirect('/')
        elif 'view_single_project_in_remote_control_system' in get_perms(R.user, project):
            #有 觀看此project 的 "在(遠端工程系統)中_觀看_單一_工程案資訊" 權限
            if not R.user.frcmusergroup_set.get(project=project).is_active:
                #被關閉權限的
                return HttpResponseRedirect('/')
    else:
        if R.user.username[1] == '_' and not R.user.is_staff:
            if project.unit != R.user.user_profile.unit:
                return HttpResponseRedirect('/')

    if R.user.has_perm('dailyreport.edit_item'):
        edit = True
    elif 'edit_item' in get_perms(R.user, engprofile):
        if R.user.frcmusergroup_set.get(project=project).group.name == CONTRACTOR_NAME and engprofile.contractor_lock:
            edit = False
        else:
            edit = True
    else:
        edit = False

    root_item = version.item_set.get(uplevel=None)
    root_item.name = version.project.name
    root_item.save()
    engprofile = project.dailyreport_engprofile.get()

    items = root_item.read_deep_sub_item_in_list()

    need_confirm = 0
    for item in items:
        if u'小計' in item.name or u'合計' in item.name or u'總計' in item.name:
            need_confirm += 1

    t = get_template(os.path.join('dailyreport', 'zh-tw', 'item.html'))
    html = t.render(RequestContext(R,{
        'engprofile': engprofile,
        'edit': edit,
        'choose': _make_choose(),
        'report_type': report_type,
        'version': version,
        'root_item': root_item,
        'items': items,
        'need_confirm': need_confirm,
        'toppage_name': u'日報表契約項目',
        }))
    return HttpResponse(html)


@login_required
def read_and_edit_schedule_item(R, **kw):
    # 進度規劃項目  編輯頁面
    version = Version.objects.get(id=kw['version_id'])
    project = version.project
    engprofile = EngProfile.objects.get(project=project)
    engprofile.create_root_item()
    report_type = kw['report_type']

    if not R.user.has_perm('fishuser.view_all_project_in_remote_control_system'):
        #沒有 "在(遠端工程系統)中_觀看_所有_工程案資訊"
        if not 'view_single_project_in_remote_control_system' in get_perms(R.user, project):
            #沒有 觀看此project 的 "在(遠端工程系統)中_觀看_單一_工程案資訊" 權限
            if project.unit != R.user.user_profile.unit:
                return HttpResponseRedirect('/')
        elif 'view_single_project_in_remote_control_system' in get_perms(R.user, project):
            #有 觀看此project 的 "在(遠端工程系統)中_觀看_單一_工程案資訊" 權限
            if not R.user.frcmusergroup_set.get(project=project).is_active:
                #被關閉權限的
                return HttpResponseRedirect('/')
    else:
        if R.user.username[1] == '_' and not R.user.is_staff:
            if project.unit != R.user.user_profile.unit:
                return HttpResponseRedirect('/')

    if R.user.has_perm('dailyreport.edit_item'):
        edit = True
    elif 'edit_item' in get_perms(R.user, engprofile):
        if R.user.frcmusergroup_set.get(project=project).group.name == CONTRACTOR_NAME and engprofile.contractor_lock:
            edit = False
        else:
            edit = True
    else:
        edit = False

    root_item = version.scheduleitem_set.get(uplevel=None)
    root_item.name = version.project.name
    root_item.save()
    engprofile = project.dailyreport_engprofile.get()

    items = root_item.read_deep_sub_item_in_list()

    t = get_template(os.path.join('dailyreport', 'zh-tw', 'schedule_item.html'))
    html = t.render(RequestContext(R,{
        'engprofile': engprofile,
        'edit': edit,
        'choose': _make_choose(),
        'report_type': report_type,
        'version': version,
        'root_item': root_item,
        'items': items,
        'toppage_name': u'進度規劃項目',
        }))
    return HttpResponse(html)


@login_required
def read_and_edit_report(R, **kw):
    # 基本資料  編輯頁面
    project = Project.objects.get(id=kw['project_id'])
    report_type = kw['report_type']
    engprofile = EngProfile.objects.get(project=project)
    user_perms = get_perms(R.user, engprofile)

    if not R.user.has_perm('fishuser.view_all_project_in_remote_control_system'):
        #沒有 "在(遠端工程系統)中_觀看_所有_工程案資訊"
        if not 'view_single_project_in_remote_control_system' in get_perms(R.user, project):
            #沒有 觀看此project 的 "在(遠端工程系統)中_觀看_單一_工程案資訊" 權限
            if project.unit != R.user.user_profile.unit:
                return HttpResponseRedirect('/')
        elif 'view_single_project_in_remote_control_system' in get_perms(R.user, project):
            #有 觀看此project 的 "在(遠端工程系統)中_觀看_單一_工程案資訊" 權限
            if not R.user.frcmusergroup_set.get(project=project).is_active:
                #被關閉權限的
                return HttpResponseRedirect('/')
    else:
        if R.user.username[1] == '_' and not R.user.is_staff:
            if project.unit != R.user.user_profile.unit:
                return HttpResponseRedirect('/')


    if R.user.has_perm('dailyreport.edit_item'):
        edit = True
    elif 'edit_item' in get_perms(R.user, engprofile):
        if 'edit_inspector_report' in user_perms and report_type=='inspector':
            edit = True
        elif 'edit_contractor_report' in user_perms and report_type=='contractor':
            edit = True
        elif R.user.frcmusergroup_set.get(project=project).group.name == CONTRACTOR_NAME and report_type=='inspector':
            if not engprofile.contractor_read_inspectorReport:
                report_type = 'contractor'
                edit = True
            else:
                edit = False
        else:
            edit = False
    else:
        edit = False

    special_dates = SpecialDate.objects.filter(project=project)

    if report_type == 'inspector' and Report.objects.filter(project=project, inspector_check=True):
        last_day = Report.objects.filter(project=project, inspector_check=True).order_by('-date')[0].date
    elif report_type == 'contractor' and Report.objects.filter(project=project, contractor_check=True):
        last_day = Report.objects.filter(project=project, contractor_check=True).order_by('-date')[0].date
    else:
        last_day = engprofile.start_date

    if engprofile.scheduled_completion_day:
        engprofile.end_date = engprofile.scheduled_completion_day
    else:
        engprofile.end_date = engprofile.readWorkingDate(is_scheduled=True)[-1]
        
    t = get_template(os.path.join('dailyreport', 'zh-tw', 'report.html'))
    html = t.render(RequestContext(R,{
        'engprofile': engprofile,
        'edit': edit,
        'last_day': last_day,
        'user_perms': user_perms,
        'choose': _make_choose(),
        'report_type': report_type,
        'special_dates': special_dates,
        'toppage_name': u'日報表',
        }))
    return HttpResponse(html)


@login_required
def read_progress(R, **kw):
    #進度管理頁面
    project = Project.objects.get(id=kw['project_id'])
    report_type = kw['report_type']
    engprofile = EngProfile.objects.get(project=project)
    user_perms = get_perms(R.user, engprofile)

    if not R.user.has_perm('fishuser.view_all_project_in_remote_control_system'):
        #沒有 "在(遠端工程系統)中_觀看_所有_工程案資訊"
        if not 'view_single_project_in_remote_control_system' in get_perms(R.user, project):
            #沒有 觀看此project 的 "在(遠端工程系統)中_觀看_單一_工程案資訊" 權限
            if project.unit != R.user.user_profile.unit:
                return HttpResponseRedirect('/')
        elif 'view_single_project_in_remote_control_system' in get_perms(R.user, project):
            #有 觀看此project 的 "在(遠端工程系統)中_觀看_單一_工程案資訊" 權限
            if not R.user.frcmusergroup_set.get(project=project).is_active:
                #被關閉權限的
                return HttpResponseRedirect('/')
    else:
        if R.user.username[1] == '_' and not R.user.is_staff:
            if project.unit != R.user.user_profile.unit:
                return HttpResponseRedirect('/')

    random_str = str(random.random())

    t = get_template(os.path.join('dailyreport', 'zh-tw', 'progress.html'))
    html = t.render(RequestContext(R,{
        'engprofile': engprofile,
        'user_perms': user_perms,
        'choose': _make_choose(),
        'random_str': random_str,
        'report_type': report_type,
        'toppage_name': u'整合資訊',
        'subpage_name': u'進度管理',
        }))
    return HttpResponse(html)


@login_required
def range_report_output(R, **kw):
    project = Project.objects.get(id=kw['project_id'])
    report_type = kw['report_type']
    engprofile = EngProfile.objects.get(project=project)
    user_perms = get_perms(R.user, engprofile)

    if not R.user.has_perm('fishuser.view_all_project_in_remote_control_system'):
        #沒有 "在(遠端工程系統)中_觀看_所有_工程案資訊"
        if not 'view_single_project_in_remote_control_system' in get_perms(R.user, project):
            #沒有 觀看此project 的 "在(遠端工程系統)中_觀看_單一_工程案資訊" 權限
            if project.unit != R.user.user_profile.unit:
                return HttpResponseRedirect('/')
        elif 'view_single_project_in_remote_control_system' in get_perms(R.user, project):
            #有 觀看此project 的 "在(遠端工程系統)中_觀看_單一_工程案資訊" 權限
            if not R.user.frcmusergroup_set.get(project=project).is_active:
                #被關閉權限的
                return HttpResponseRedirect('/')
    else:
        if R.user.username[1] == '_' and not R.user.is_staff:
            if project.unit != R.user.user_profile.unit:
                return HttpResponseRedirect('/')

    if report_type == 'inspector': 
        if 'edit_contractor_report' in user_perms and not engprofile.contractor_read_inspectorReport and not R.user.is_staff:
            report_type = 'contractor'


    t = get_template(os.path.join('dailyreport', 'zh-tw', 'range_report_output.html'))
    html = t.render(RequestContext(R,{
        'engprofile': engprofile,
        'user_perms': user_perms,
        'choose': _make_choose(),
        'report_type': report_type,
        'toppage_name': u'列印區間報表',
        }))
    return HttpResponse(html)


@login_required
def online_print_range(R, **kw):
    #線上列印區間報表
    project = Project.objects.get(id=kw['project_id'])
    report_type = kw['report_type']
    info_type = kw['info_type']
    engprofile = EngProfile.objects.get(project=project)
    start_report_date = kw['start_report_date']
    start_report_date = datetime.datetime.strptime(start_report_date, "%Y-%m-%d").date()
    end_report_date = kw['end_report_date']
    end_report_date = datetime.datetime.strptime(end_report_date, "%Y-%m-%d").date()
    if start_report_date < engprofile.start_date: start_report_date = engprofile.start_date
    if end_report_date < engprofile.start_date: end_report_date = engprofile.start_date
    user_perms = get_perms(R.user, engprofile)
    
    weekday_name = [u'星期一', u'星期二', u'星期三', u'星期四', u'星期五', u'星期六', u'星期日']
    
    if not R.user.has_perm('fishuser.view_all_project_in_remote_control_system'):
        #沒有 "在(遠端工程系統)中_觀看_所有_工程案資訊"
        if not 'view_single_project_in_remote_control_system' in get_perms(R.user, project):
            #沒有 觀看此project 的 "在(遠端工程系統)中_觀看_單一_工程案資訊" 權限
            if project.unit != R.user.user_profile.unit:
                return HttpResponseRedirect('/')
        elif 'view_single_project_in_remote_control_system' in get_perms(R.user, project):
            #有 觀看此project 的 "在(遠端工程系統)中_觀看_單一_工程案資訊" 權限
            if not R.user.frcmusergroup_set.get(project=project).is_active:
                #被關閉權限的
                return HttpResponseRedirect('/')
    else:
        if R.user.username[1] == '_' and not R.user.is_staff:
            if project.unit != R.user.user_profile.unit:
                return HttpResponseRedirect('/')

    workingdates = engprofile.readWorkingDate()
    engprofile.working_days = len(workingdates)
    engprofile.extension = sum([i.day for i in engprofile.readExtensions()])
    report_date = start_report_date
    reports = []
    engprofile.contractor_name = engprofile.contractor_name if engprofile.contractor_name else ''
    
    start_version = Version.objects.filter(project=project, start_date__lte=start_report_date).order_by('start_date')
    if start_version:
        start_version = start_version[0]
    else:
        start_version = Version.objects.filter(project=project).order_by('start_date')[0]
    end_version = Version.objects.filter(project=project, start_date__lte=end_report_date).order_by('-start_date')
    if end_version:
        end_version = end_version[0]
    else:
        end_version = Version.objects.filter(project=project).order_by('-start_date')[0]
    
    versions = Version.objects.filter(project=project, start_date__gte=start_version.start_date, start_date__lte=end_version.start_date).order_by('start_date')
    version_items = {}
    for n, v in enumerate(versions):
        version_items[v.id] = {}
        version_items[v.id]['root_item'] = v.item_set.get(uplevel=None)
        version_items[v.id]['items'] = version_items[v.id]['root_item'].read_deep_sub_item_in_list()
        for i in version_items[v.id]['items']:
            if n == 0:
                if report_type == 'inspector':
                    version_items[v.id][i.id] = sum([k.i_num for k in ReportItem.objects.filter(report__date__lt=start_report_date, item__in=i.read_brother_items()).exclude(i_num='0')])
                else:
                    version_items[v.id][i.id] = sum([k.c_num for k in ReportItem.objects.filter(report__date__lt=start_report_date, item__in=i.read_brother_items()).exclude(c_num='0')])
                
            else:
                if report_type == 'inspector':
                    version_items[v.id][i.id] = sum([k.i_num for k in ReportItem.objects.filter(report__date__lt=v.start_date, item__in=i.read_brother_items()).exclude(i_num='0')])
                else:
                    version_items[v.id][i.id] = sum([k.c_num for k in ReportItem.objects.filter(report__date__lt=v.start_date, item__in=i.read_brother_items()).exclude(c_num='0')])

    reports = []
    while report_date <= end_report_date:
        if report_date not in workingdates and report_date <= workingdates[-1] and not ReportHoliday.objects.filter(project=project, date=report_date):
            report_date += datetime.timedelta(1)
            continue

        try:
            #看看當天有沒有填寫過
            report = Report.objects.get(project=project, date=report_date)
            report_items = report.reportitem_set.all().order_by('item__uplevel__priority', 'item__priority').prefetch_related('report', 'item')
        except:
            try:
                report = ReportHoliday.objects.get(project=project, date=report_date)
                report.i_sum_money=0
                report.c_sum_money=0
            except:
                report = Report(id=-1, date=report_date, i_sum_money=0, c_sum_money=0, project=project)
            report_items = []

        version = Version.objects.filter(project=project, start_date__lte=report_date).order_by('-start_date')[0]
        report.change_engs_price = version.engs_price if Version.objects.filter(project=project).count()-1 != 0 else ''
        report.change_version_times = Version.objects.filter(project=project, start_date__lte=report.date).count() - 1
        report.weekday = weekday_name[report_date.weekday()]
        root_item = version.item_set.get(uplevel=None)

        items = root_item.read_deep_sub_item_in_list()

        if info_type == 'all':
            tmp_items = []
            for item in items:
                if item.kind == DIRKIND:
                    tmp_items.append(item)
                    continue
                if report_items:
                    #表示當天有填寫紀錄
                    try:
                        report_item = report_items.get(item=item)
                    except:
                        report_item = ReportItem(report=report, item=item)
                        report_item.save()
                    if report_type == 'inspector':
                        item.num = report_item.i_num
                        version_items[version.id][item.id] += report_item.i_num
                        item.sum_num = version_items[version.id][item.id]
                        item.note = report_item.i_note
                    else:
                        item.num = report_item.c_num
                        version_items[version.id][item.id] += report_item.c_num
                        item.sum_num = version_items[version.id][item.id]
                        item.note = report_item.c_note
                else:
                    #當天沒有填寫紀錄
                    item.num = 0
                    item.sum_num = version_items[version.id][item.id]

                tmp_items.append(item)
            items = tmp_items
            items.pop(0)
        elif info_type == 'write':
            tmp_items = []
            if report_items:
                #表示當天有填寫紀錄
                for item in report_items:
                    if item.item.kind == DIRKIND: continue
                    if report_type == 'inspector':
                        if item.i_num or item.i_note:
                            item.item.num = item.i_num
                            version_items[version.id][item.item.id] += item.i_num
                            item.item.sum_num = version_items[version.id][item.item.id]
                            item.item.note = item.i_note
                            tmp_items.append(item.item)
                    else:
                        if item.c_num or item.c_note:
                            item.item.num = item.c_num
                            version_items[version.id][item.item.id] += item.c_num
                            item.item.sum_num = version_items[version.id][item.item.id]
                            item.item.note = item.c_note
                            tmp_items.append(item.item)
                items = tmp_items
            else:
                items = []
        elif info_type == 'blank':
            for item in items:
                item.num = ''
                item.note = ''
            items.pop(0)

        #計算本日完成、累計完成、預定累計完成
        pre_reports = Report.objects.filter(project=project, date__lte=report_date).order_by('-date')
        if not report_items and pre_reports: report_items = pre_reports[0].reportitem_set.all().prefetch_related('report', 'item')
        if report_type == 'inspector':
            if root_item.read_dir_price_by_roundkind() == 0:
                report.today_progress_rate = 0
                report.sum_progress_rate = 0
            else:
                report_money = sum([i.i_sum_money for i in Report.objects.filter(project=project, date__gte=version.start_date, date__lte=report_date)])
                report.today_progress_rate = round(float(str(report.i_sum_money)) / float(root_item.read_dir_price_by_roundkind()) * 100., 3)
                report.sum_progress_rate = round(float(str(report_money + version.pre_i_money)) / float(root_item.read_dir_price_by_roundkind()) * 100., 3)

        else:
            if root_item.read_dir_price_by_roundkind() == 0:
                report.today_progress_rate = 0
                report.sum_progress_rate = 0
            else:
                report_money = sum([i.c_sum_money for i in Report.objects.filter(project=project, date__gte=version.start_date, date__lte=report_date)])
                report.today_progress_rate = round(float(str(report.c_sum_money)) / float(root_item.read_dir_price_by_roundkind()) * 100., 3)
                report.sum_progress_rate = round(float(str(report_money + version.pre_c_money)) / float(root_item.read_dir_price_by_roundkind()) * 100., 3)

        schedule_progress_list = engprofile.read_schedule_progress()
        try:
            report.design_percent = schedule_progress_list[report_date]
        except:
            max_date = max([sp for sp in schedule_progress_list])
            if report_date >= max_date:
                report.design_percent = schedule_progress_list[max_date]
            else:
                dd = report_date - datetime.timedelta(1)
                while dd not in workingdates and dd >= engprofile.start_date:
                    dd -= datetime.timedelta(1)
                if dd < engprofile.start_date:
                    report.design_percent = 0
                else:
                    report.design_percent = schedule_progress_list[dd]

        max_day = max(workingdates)
        if engprofile.date_type.value == u'限期完工(日曆天每日施工)':
            report.all_duration = engprofile.deadline + datetime.timedelta(sum([i.day for i in Extension.objects.filter(project=project, date__lte=report_date)]))
            report.all_duration = (report.all_duration - engprofile.start_date).days
        else:
            report.all_duration = engprofile.duration + sum([i.day for i in Extension.objects.filter(project=project, date__lte=report_date)])
            
        if report.date >= max_day:
            report.used_duration = workingdates.index(max_day) + 1 + int((report.date - max_day).days)
        else:
            dd = report.date
            while dd not in workingdates and dd >= engprofile.start_date:
                dd -= datetime.timedelta(1)
            if dd < engprofile.start_date:
                report.used_duration = 0
            else:
                report.used_duration = workingdates.index(dd) + 1
        #已用天數減不計工期
        # report.used_duration -= sum([i.day for i in Extension.objects.filter(project=project, date__lte=report.date, type__value=u'不計工期')])

        # report.unused_duration = len(engprofile.readWorkingDate(is_scheduled=True)) - sum([i.day for i in Extension.objects.filter(project=project, date__gt=report.date)]) - report.used_duration
        report.unused_duration = report.all_duration - report.used_duration

        report.extensions = sum([i.day for i in Extension.objects.filter(project=project, date__lte=report.date)])
        # report.scheduled_completion_day = engprofile.readScheduledCompletionDay(date=report.date) 
        if engprofile.scheduled_completion_day:
            report.scheduled_completion_day = engprofile.scheduled_completion_day
        else:
            # report.scheduled_completion_day = workingdates[len(workingdates) - sum([i.day for i in Extension.objects.filter(project=project, date__gt=report.date)]) - 1]
            report.scheduled_completion_day = engprofile.readScheduledCompletionDay(date=report.date) 
 
        labors_and_equips = []
        site_materials = []
        if report_type == 'contractor':
            labors = LaborEquip.objects.filter(project=project, type__swarm='labor_or_equip', type__value=u'人員').order_by('sort')
            for labor in labors:
                try:
                    report_labor_equip = ReportLaborEquip.objects.get(report=report, type=labor)
                    labor.num = report_labor_equip.num
                except:
                    labor.num = 0
                labor.sum_num = sum([rle.num for rle in ReportLaborEquip.objects.filter(report__date__lte=report.date, type=labor)])
                if not labor.sum_num: labor.sum_num = 0

            equips = LaborEquip.objects.filter(project=project, type__swarm='labor_or_equip', type__value=u'機具').order_by('sort')
            for equip in equips:
                try:
                    report_labor_equip = ReportLaborEquip.objects.get(report=report, type=equip)
                    equip.num = report_labor_equip.num
                except:
                    equip.num = 0
                equip.sum_num = sum([rle.num for rle in ReportLaborEquip.objects.filter(report__date__lte=report.date, type=equip)])
                if not equip.sum_num: equip.sum_num = 0

            if info_type == 'all':
                labors_and_equips = []
                for i in xrange(max([labors.count(), equips.count()])):
                    if i >= labors.count():
                        labor = ''
                    else:
                        labor = labors[i]
                    if i >= equips.count():
                        equip = ''
                    else:
                        equip = equips[i]
                    labors_and_equips.append([labor, equip])
            elif info_type == 'write':
                labors_and_equips = []
                labors_tmp = []
                for l in labors:
                    if l.num: labors_tmp.append(l)
                equips_tmp = []
                for e in equips:
                    if e.num: equips_tmp.append(e)
                labors = labors_tmp
                equips = equips_tmp
                for i in xrange(max([len(labors), len(equips)])):
                    if i >= len(labors):
                        labor = ''
                    else:
                        labor = labors[i]
                    if i >= len(equips):
                        equip = ''
                    else:
                        equip = equips[i]
                    labors_and_equips.append([labor, equip])
            elif info_type == 'blank':
                labors_and_equips = []
                for i in xrange(max([labors.count(), equips.count()])):
                    if i >= labors.count():
                        labor = ''
                    else:
                        labors[i].num = ''
                        labors[i].sum_num = ''
                        labor = labors[i]
                    if i >= equips.count():
                        equip = ''
                    else:
                        equips[i].num = ''
                        equips[i].sum_num = ''
                        equip = equips[i]
                    labors_and_equips.append([labor, equip])
            try:
                site_materials = SiteMaterial.objects.filter(report=report)
            except:
                site_materials = []

        test_records = []
        if HAVE_RCM_TEST_RECORD_SYSTEM:
            test_records = TestRecord.objects.filter(testtype__project=project, record_date=report.date).order_by('testtype', 'record_date')

        report.test_records = test_records
        report.items = items
        report.labors_and_equips = labors_and_equips
        report.site_materials = site_materials
        if report.date >= datetime.datetime.strptime('2019-05-01', "%Y-%m-%d").date():
            report.over_20190501 = True
        else:
            report.over_20190501 = False

        reports.append(report)
        report_date += datetime.timedelta(1)

    t = get_template(os.path.join('dailyreport', 'zh-tw', 'online_print_' + report_type + '.html'))
    html = t.render(RequestContext(R,{
            'engprofile': engprofile,
            'reports': reports,
            'report_type': report_type,
        }))

    return HttpResponse(html)


@login_required
def make_excel_range(R, **kw):
    #輸出Excel區間報表
    project = Project.objects.get(id=kw['project_id'])
    report_type = kw['report_type']
    info_type = kw['info_type']
    engprofile = EngProfile.objects.get(project=project)
    start_report_date = kw['start_report_date']
    start_report_date = datetime.datetime.strptime(start_report_date, "%Y-%m-%d").date()
    end_report_date = kw['end_report_date']
    end_report_date = datetime.datetime.strptime(end_report_date, "%Y-%m-%d").date()
    if start_report_date < engprofile.start_date: start_report_date = engprofile.start_date
    if end_report_date < engprofile.start_date: end_report_date = engprofile.start_date
    user_perms = get_perms(R.user, engprofile)
    
    weekday_name = [u'星期一', u'星期二', u'星期三', u'星期四', u'星期五', u'星期六', u'星期日']
    
    if not R.user.has_perm('fishuser.view_all_project_in_remote_control_system'):
        #沒有 "在(遠端工程系統)中_觀看_所有_工程案資訊"
        if not 'view_single_project_in_remote_control_system' in get_perms(R.user, project):
            #沒有 觀看此project 的 "在(遠端工程系統)中_觀看_單一_工程案資訊" 權限
            if project.unit != R.user.user_profile.unit:
                return HttpResponseRedirect('/')
        elif 'view_single_project_in_remote_control_system' in get_perms(R.user, project):
            #有 觀看此project 的 "在(遠端工程系統)中_觀看_單一_工程案資訊" 權限
            if not R.user.frcmusergroup_set.get(project=project).is_active:
                #被關閉權限的
                return HttpResponseRedirect('/')
    else:
        if R.user.username[1] == '_' and not R.user.is_staff:
            if project.unit != R.user.user_profile.unit:
                return HttpResponseRedirect('/')

    workingdates = engprofile.readWorkingDate()
    engprofile.working_days = len(workingdates)
    engprofile.extension = sum([i.day for i in engprofile.readExtensions()])
    report_date = start_report_date

    engprofile.contractor_name = engprofile.contractor_name if engprofile.contractor_name else ''

    start_version = Version.objects.filter(project=project, start_date__lte=start_report_date).order_by('-start_date')
    if start_version:
        start_version = start_version[0]
    else:
        start_version = Version.objects.filter(project=project).order_by('-start_date')[0]
    end_version = Version.objects.filter(project=project, start_date__lte=end_report_date).order_by('-start_date')
    if end_version:
        end_version = end_version[0]
    else:
        end_version = Version.objects.filter(project=project).order_by('-start_date')[0]

    versions = Version.objects.filter(project=project, start_date__gte=start_version.start_date, start_date__lte=end_version.start_date).order_by('start_date')
    version_items = {}
    for n, v in enumerate(versions):
        version_items[v.id] = {}
        version_items[v.id]['root_item'] = v.item_set.get(uplevel=None)
        version_items[v.id]['items'] = version_items[v.id]['root_item'].read_deep_sub_item_in_list()
        for i in version_items[v.id]['items']:
            if n == 0:
                if report_type == 'inspector':
                    version_items[v.id][i.id] = sum([k.i_num for k in ReportItem.objects.filter(report__date__lt=start_report_date, item__in=i.read_brother_items()).exclude(i_num='0')])
                else:
                    version_items[v.id][i.id] = sum([k.c_num for k in ReportItem.objects.filter(report__date__lt=start_report_date, item__in=i.read_brother_items()).exclude(c_num='0')])
                
            else:
                if report_type == 'inspector':
                    version_items[v.id][i.id] = sum([k.i_num for k in ReportItem.objects.filter(report__date__lt=v.start_date, item__in=i.read_brother_items()).exclude(i_num='0')])
                else:
                    version_items[v.id][i.id] = sum([k.c_num for k in ReportItem.objects.filter(report__date__lt=v.start_date, item__in=i.read_brother_items()).exclude(c_num='0')])

    data = {'reports': {}}
    while report_date <= end_report_date:
        if report_date not in workingdates and report_date <= workingdates[-1] and not ReportHoliday.objects.filter(project=project, date=report_date):
            report_date += datetime.timedelta(1)
            continue

        try:
            #看看當天有沒有填寫過
            report = Report.objects.get(project=project, date=report_date)
            report_items = report.reportitem_set.all().order_by('item__uplevel__priority', 'item__priority').prefetch_related('report', 'item')
        except:
            try:
                report = ReportHoliday.objects.get(project=project, date=report_date)
                report.i_sum_money=0
                report.c_sum_money=0
            except:
                report = Report(id=-1, date=report_date, i_sum_money=0, c_sum_money=0, project=project)
            report.has_professional_item = False
            report_items = []

        version = versions.filter(start_date__lte=report_date).order_by('-start_date')[0]
        root_item = version_items[version.id]['root_item']
        items = version_items[version.id]['items']
        report.weekday = weekday_name[report_date.weekday()]

        #計算本日完成、累計完成、預定累計完成
        pre_reports = Report.objects.filter(project=project, date__lte=report_date).order_by('-date')
        if not report_items and pre_reports: report_items = pre_reports[0].reportitem_set.all().prefetch_related('report', 'item')
        if report_type == 'inspector':
            if root_item.read_dir_price_by_roundkind() == 0:
                report.today_progress_rate = 0
                report.sum_progress_rate = 0
            else:
                report_money = sum([i.i_sum_money for i in Report.objects.filter(project=project, date__gte=version.start_date, date__lte=report_date)])
                report.today_progress_rate = round(float(str(report.i_sum_money)) / root_item.read_dir_price_by_roundkind() * 100., 3)
                report.sum_progress_rate = round(float(str(report_money + version.pre_i_money)) / root_item.read_dir_price_by_roundkind() * 100., 3)

        else:
            if root_item.read_dir_price_by_roundkind() == 0:
                report.today_progress_rate = 0
                report.sum_progress_rate = 0
            else:
                report_money = sum([i.c_sum_money for i in Report.objects.filter(project=project, date__gte=version.start_date, date__lte=report_date)])
                report.today_progress_rate = round(float(str(report.c_sum_money)) / root_item.read_dir_price_by_roundkind() * 100., 3)
                report.sum_progress_rate = round(float(str(report_money + version.pre_c_money)) / root_item.read_dir_price_by_roundkind() * 100., 3)

        schedule_progress_list = engprofile.read_schedule_progress()
        try:
            report.design_percent = schedule_progress_list[report_date]
        except:
            max_date = max([sp for sp in schedule_progress_list])
            if report_date >= max_date:
                report.design_percent = schedule_progress_list[max_date]
            else:
                dd = report_date - datetime.timedelta(1)
                while dd not in workingdates and dd >= engprofile.start_date:
                    dd -= datetime.timedelta(1)
                if dd < engprofile.start_date:
                    report.design_percent = 0
                else:
                    report.design_percent = schedule_progress_list[dd]

        max_day = max(workingdates)
        if engprofile.date_type.value == u'限期完工(日曆天每日施工)':
            all_duration = engprofile.deadline + datetime.timedelta(sum([i.day for i in Extension.objects.filter(project=project, date__lte=report_date)]))
            all_duration = (all_duration - engprofile.start_date).days
        else:
            all_duration = engprofile.duration + sum([i.day for i in Extension.objects.filter(project=project, date__lte=report_date)])
            
        if report.date >= max_day:
            report.used_duration = workingdates.index(max_day) + 1 + int((report.date - max_day).days)
        else:
            dd = report.date
            while dd not in workingdates and dd >= engprofile.start_date:
                dd -= datetime.timedelta(1)
            if dd < engprofile.start_date:
                report.used_duration = 0
            else:
                report.used_duration = workingdates.index(dd) + 1
        
        # report.unused_duration = len(engprofile.readWorkingDate(is_scheduled=True)) - sum([i.day for i in Extension.objects.filter(project=project, date__gt=report.date)]) - report.used_duration
        #已用天數減不計工期
        # report.used_duration -= sum([i.day for i in Extension.objects.filter(project=project, date__lte=report.date, type__value=u'不計工期')])

        report.extensions = sum([i.day for i in Extension.objects.filter(project=project, date__lte=report.date)])
        # report.scheduled_completion_day = engprofile.readScheduledCompletionDay(date=report.date) 
        if engprofile.scheduled_completion_day:
            report.scheduled_completion_day = engprofile.scheduled_completion_day
        else:
            # report.scheduled_completion_day = workingdates[len(workingdates) - sum([i.day for i in Extension.objects.filter(project=project, date__gt=report.date)]) - 1]
            report.scheduled_completion_day = engprofile.readScheduledCompletionDay(date=report.date) 

        report.unused_duration = all_duration - report.used_duration
        data['reports'][str(report_date)] = {}
        data['reports'][str(report_date)]['item_table'] = []
        data['reports'][str(report_date)]['manmachine_table'] = []
        data['reports'][str(report_date)]['site_material_table'] = []
        
        data['reports'][str(report_date)]['replace'] = {
                'reportdate': '%s-%s-%s(%s)' % (report_date.year-1911, report_date.month, report_date.day, report.weekday),
                'morning_weather': report.morning_weather.value if report.id != -1 and report.morning_weather else '',
                'afternoon_weather': report.afternoon_weather.value if report.id != -1 and report.afternoon_weather else '',
                'project_name': report.project.name,
                'duration': engprofile.duration,
                'all_duration': all_duration,
                'used_duration': report.used_duration,
                'unused_duration': report.unused_duration,
                'extension': engprofile.readExtensionDay(),
                'project_contractor_name': engprofile.contractor_name,
                'start_date': '%s-%s-%s' % (engprofile.start_date.year-1911, engprofile.start_date.month, engprofile.start_date.day),
                'end_date': '%s-%s-%s' % (report.scheduled_completion_day.year-1911, report.scheduled_completion_day.month, report.scheduled_completion_day.day),
                'design_percent': round(float(report.design_percent), 3),
                'act_percent': round(report.sum_progress_rate, 3),
                'change_version_times': Version.objects.filter(project=project, start_date__lte=report.date).count()-1,
                'init_version_price': Version.objects.filter(project=project).order_by('start_date')[0].engs_price,
                'change_version_price': version.engs_price if Version.objects.filter(project=project).count()-1 != 0 else '',
                'has_professional_item': u'有' if hasattr(report, 'has_professional_item') and report.has_professional_item else u'無',
                'pre_education': u'有' if hasattr(report, 'pre_education') and report.pre_education else u'無',
                'has_insurance': [u'有', u'無', u'無新進勞工'][report.has_insurance-1] if hasattr(report, 'has_insurance') else u'無',
                'safety_equipment': u'有' if hasattr(report, 'safety_equipment') and report.safety_equipment else u'無',
                'pre_check': u'有' if hasattr(report, 'pre_check') and report.pre_check else u'無',
                'date_type': engprofile.date_type.value,
            }

        if report.date >= datetime.datetime.strptime('2019-05-01', "%Y-%m-%d").date():
            data['reports'][str(report_date)]['replace']['over_20190501'] = True
        else:
            data['reports'][str(report_date)]['replace']['over_20190501'] = False

        if report_type == 'inspector':
            data['reports'][str(report_date)]['replace']['describe_subcontractor'] = report.describe_subcontractor if report.describe_subcontractor else ''
            data['reports'][str(report_date)]['replace']['sampling'] = report.sampling if report.sampling else ''
            data['reports'][str(report_date)]['replace']['notify'] = report.notify if report.notify else ''
            data['reports'][str(report_date)]['replace']['note'] = report.note if report.note else ''
            data['reports'][str(report_date)]['replace']['i_pre_check'] = report.i_pre_check if report.i_pre_check else ''
            data['reports'][str(report_date)]['replace']['i_project_status'] = report.i_project_status if report.i_project_status else ''
        else:
            data['reports'][str(report_date)]['replace']['describe_subcontractor'] = report.c_describe_subcontractor if report.c_describe_subcontractor else ''
            data['reports'][str(report_date)]['replace']['sampling'] = report.c_sampling if report.c_sampling else ''
            data['reports'][str(report_date)]['replace']['notify'] = report.c_notify if report.c_notify else ''
            data['reports'][str(report_date)]['replace']['note'] = report.c_note if report.c_note else ''
        

        item_table = data['reports'][str(report_date)]['item_table']
        manmachine_table = data['reports'][str(report_date)]['manmachine_table']
        site_material_table = data['reports'][str(report_date)]['site_material_table']
        replace = data['reports'][str(report_date)]['replace']

        if info_type == 'all':
            if report_date not in workingdates: report_items = []
            for item in items[1:]:
                if item.kind == DIRKIND:
                    item_table.append([item.name, u'---',
                        str(item.unit_num), '', '', '', 'dir'])
                    continue
                item.note = ''
                if report_items:
                    #表示當天有填寫紀錄
                    try:
                        report_item = report_items.get(item=item)
                    except:
                        report_item = ReportItem(report=report, item=item)
                        report_item.save()
                    if report_type == 'inspector':
                        item.num = report_item.i_num if report_item.i_num else ''
                        version_items[version.id][item.id] += report_item.i_num
                        item.sum_num = version_items[version.id][item.id]
                        item.note = report_item.i_note
                    else:
                        item.num = report_item.c_num if report_item.c_num else ''
                        version_items[version.id][item.id] += report_item.c_num
                        item.sum_num = version_items[version.id][item.id]
                        item.note = report_item.c_note

                else:
                    #當天沒有填寫紀錄
                    item.num = ''
                    item.sum_num = version_items[version.id][item.id]
                    item.note = ''
                
                item_table.append([item.name, item.unit_name,
                    str(item.unit_num), str(item.num), str(item.sum_num), item.note])

        elif info_type == 'write':
            if report_date not in workingdates: report_items = []
            if report_items:
                #表示當天有填寫紀錄
                for item in report_items:
                    if item.item.kind == DIRKIND: continue
                    if report_type == 'inspector':
                        if item.i_num or item.i_note:
                            item.item.num = item.i_num
                            version_items[version.id][item.item.id] += item.i_num
                            item.item.sum_num = version_items[version.id][item.item.id]
                            item.item.note = item.i_note
                            item_table.append([item.item.name, item.item.unit_name,
                                str(item.item.unit_num), str(item.item.num), str(item.item.sum_num), item.item.note])
                    else:
                        if item.c_num or item.c_note:
                            item.item.num = item.c_num
                            version_items[version.id][item.item.id] += item.c_num
                            item.item.sum_num = version_items[version.id][item.item.id]
                            item.item.note = item.c_note
                            item_table.append([item.item.name, item.item.unit_name,
                                str(item.item.unit_num), str(item.item.num), str(item.item.sum_num), item.item.note])

        elif info_type == 'blank':
            replace['has_professional_item'] = u'□有□無'
            for item in items[1:]:
                if item.kind == DIRKIND:
                    item_table.append([item.name, item.unit_name, str(item.unit_num), '', '', '', 'dir'])
                else:
                    item_table.append([item.name, item.unit_name, str(item.unit_num), '', '', ''])

        

        labors_and_equips = []
        site_materials = []
        if report_type == 'contractor':
            labors = LaborEquip.objects.filter(project=project, type__swarm='labor_or_equip', type__value=u'人員').order_by('sort')
            for labor in labors:
                try:
                    report_labor_equip = ReportLaborEquip.objects.get(report=report, type=labor)
                    labor.num = report_labor_equip.num
                except:
                    labor.num = ''
                labor.sum_num = sum([rle.num for rle in ReportLaborEquip.objects.filter(report__date__lte=report.date, type=labor)])
                if not labor.sum_num: labor.sum_num = 0

            equips = LaborEquip.objects.filter(project=project, type__swarm='labor_or_equip', type__value=u'機具').order_by('sort')
            for equip in equips:
                try:
                    report_labor_equip = ReportLaborEquip.objects.get(report=report, type=equip)
                    equip.num = report_labor_equip.num
                except:
                    equip.num = ''
                equip.sum_num = sum([rle.num for rle in ReportLaborEquip.objects.filter(report__date__lte=report.date, type=equip)])
                if not equip.sum_num: equip.sum_num = 0

            if info_type == 'all':
                labors_and_equips = []
                for i in xrange(max([labors.count(), equips.count()])):
                    if i >= labors.count():
                        labor = ''
                    else:
                        labor = labors[i]
                    if i >= equips.count():
                        equip = ''
                    else:
                        equip = equips[i]

                    if labor: lv, ln, lsn = str(labor.value), str(labor.num), str(labor.sum_num)
                    else:lv, ln, lsn = '', '', ''
                    if equip: ev, en, esn = str(equip.value), str(equip.num), str(equip.sum_num)
                    else:ev, en, esn = '', '', ''
                    manmachine_table.append([
                        lv, ln, lsn,
                        ev, en, esn])
            elif info_type == 'write':
                labors_and_equips = []
                labors_tmp = []
                for l in labors:
                    if l.num: labors_tmp.append(l)
                equips_tmp = []
                for e in equips:
                    if e.num: equips_tmp.append(e)
                labors = labors_tmp
                equips = equips_tmp
                for i in xrange(max([len(labors), len(equips)])):
                    if i >= len(labors):
                        labor = ''
                    else:
                        labor = labors[i]
                    if i >= len(equips):
                        equip = ''
                    else:
                        equip = equips[i]

                    if labor: lv, ln, lsn = str(labor.value), str(labor.num), str(labor.sum_num)
                    else:lv, ln, lsn = '', '', ''
                    if equip: ev, en, esn = str(equip.value), str(equip.num), str(equip.sum_num)
                    else:ev, en, esn = '', '', ''
                    manmachine_table.append([
                        lv, ln, lsn,
                        ev, en, esn])
            elif info_type == 'blank':
                labors_and_equips = []
                for i in xrange(max([labors.count(), equips.count()])):
                    if i >= labors.count():
                        labor = ''
                    else:
                        labors[i].num = ''
                        labors[i].sum_num = ''
                        labor = labors[i]
                    if i >= equips.count():
                        equip = ''
                    else:
                        equips[i].num = ''
                        equips[i].sum_num = ''
                        equip = equips[i]
                    if labor: lv, ln, lsn = str(labor.value), str(labor.num), str(labor.sum_num)
                    else:lv, ln, lsn = '', '', ''
                    if equip: ev, en, esn = str(equip.value), str(equip.num), str(equip.sum_num)
                    else:ev, en, esn = '', '', ''
                    manmachine_table.append([
                        lv, ln, lsn,
                        ev, en, esn])
            try:
                site_materials = SiteMaterial.objects.filter(report=report)
                for sm in site_materials:
                    site_material_table.append([sm.name, sm.unit_name,
                        str(sm.unit_num), str(sm.today_num), str(sm.today_sum_num), sm.note])
            except: pass
        report_date += datetime.timedelta(1)

    #開始製造EXCEL
    output = StringIO()
    workbook = xlsxwriter.Workbook(output, 
                {'strings_to_numbers':  True,
                'strings_to_formulas': False,
                'strings_to_urls':     False})

    if report_type == 'inspector':
        workbook = make_inspector_excel_file(workbook=workbook, data=data)
    elif report_type == 'contractor':
        workbook = make_contractor_excel_file(workbook=workbook, data=data)

    workbook.close()
    output.seek(0)
    response = HttpResponse(output.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    if start_report_date == end_report_date:
        response['Content-Disposition'] = ('attachment; filename=%s(%s)_%s_%s.xlsx' % (str(start_report_date), report_type[0], engprofile.project.name.replace(' ', ''), info_type)).encode('cp950', 'replace')
    else:
        response['Content-Disposition'] = ('attachment; filename=%s~%s(%s)_%s_%s.xlsx' % (str(start_report_date), str(end_report_date), report_type[0], engprofile.project.name.replace(' ', ''), info_type)).encode('cp950', 'replace')
    
    return response


@login_required
def online_print_range2(R, **kw):
    """
        線上列印區間報表
        2017/08/01 日前版本
    """
    project = Project.objects.get(id=kw['project_id'])
    report_type = kw['report_type']
    info_type = kw['info_type']
    engprofile = EngProfile.objects.get(project=project)
    start_report_date = kw['start_report_date']
    start_report_date = datetime.datetime.strptime(start_report_date, "%Y-%m-%d").date()
    end_report_date = kw['end_report_date']
    end_report_date = datetime.datetime.strptime(end_report_date, "%Y-%m-%d").date()
    if start_report_date < engprofile.start_date: start_report_date = engprofile.start_date
    if end_report_date < engprofile.start_date: end_report_date = engprofile.start_date
    user_perms = get_perms(R.user, engprofile)
    
    weekday_name = [u'星期一', u'星期二', u'星期三', u'星期四', u'星期五', u'星期六', u'星期日']
    
    if not R.user.has_perm('fishuser.view_all_project_in_remote_control_system'):
        #沒有 "在(遠端工程系統)中_觀看_所有_工程案資訊"
        if not 'view_single_project_in_remote_control_system' in get_perms(R.user, project):
            #沒有 觀看此project 的 "在(遠端工程系統)中_觀看_單一_工程案資訊" 權限
            if project.unit != R.user.user_profile.unit:
                return HttpResponseRedirect('/')
        elif 'view_single_project_in_remote_control_system' in get_perms(R.user, project):
            #有 觀看此project 的 "在(遠端工程系統)中_觀看_單一_工程案資訊" 權限
            if not R.user.frcmusergroup_set.get(project=project).is_active:
                #被關閉權限的
                return HttpResponseRedirect('/')
    else:
        if R.user.username[1] == '_' and not R.user.is_staff:
            if project.unit != R.user.user_profile.unit:
                return HttpResponseRedirect('/')

    workingdates = engprofile.readWorkingDate()
    engprofile.working_days = len(workingdates)
    engprofile.extension = sum([i.day for i in engprofile.readExtensions()])
    report_date = start_report_date
    reports = []
    engprofile.contractor_name = engprofile.contractor_name if engprofile.contractor_name else ''
    
    start_version = Version.objects.filter(project=project, start_date__lte=start_report_date).order_by('-start_date')
    if start_version:
        start_version = start_version[0]
    else:
        start_version = Version.objects.filter(project=project).order_by('-start_date')[0]
    end_version = Version.objects.filter(project=project, start_date__lte=end_report_date).order_by('-start_date')
    if end_version:
        end_version = end_version[0]
    else:
        end_version = Version.objects.filter(project=project).order_by('-start_date')[0]
    
    versions = Version.objects.filter(project=project, start_date__gte=start_version.start_date, start_date__lte=end_version.start_date).order_by('start_date')
    version_items = {}
    for n, v in enumerate(versions):
        version_items[v.id] = {}
        version_items[v.id]['root_item'] = v.item_set.get(uplevel=None)
        version_items[v.id]['items'] = version_items[v.id]['root_item'].read_deep_sub_item_in_list()
        for i in version_items[v.id]['items']:
            if n == 0:
                if report_type == 'inspector':
                    version_items[v.id][i.id] = sum([k.i_num for k in ReportItem.objects.filter(report__date__lt=start_report_date, item__in=i.read_brother_items()).exclude(i_num='0')])
                else:
                    version_items[v.id][i.id] = sum([k.c_num for k in ReportItem.objects.filter(report__date__lt=start_report_date, item__in=i.read_brother_items()).exclude(c_num='0')])
                
            else:
                if report_type == 'inspector':
                    version_items[v.id][i.id] = sum([k.i_num for k in ReportItem.objects.filter(report__date__lt=v.start_date, item__in=i.read_brother_items()).exclude(i_num='0')])
                else:
                    version_items[v.id][i.id] = sum([k.c_num for k in ReportItem.objects.filter(report__date__lt=v.start_date, item__in=i.read_brother_items()).exclude(c_num='0')])

    reports = []
    while report_date <= end_report_date:
        if report_date not in workingdates and report_date <= workingdates[-1] and not ReportHoliday.objects.filter(project=project, date=report_date):
            report_date += datetime.timedelta(1)
            continue

        try:
            #看看當天有沒有填寫過
            report = Report.objects.get(project=project, date=report_date)
            report_items = report.reportitem_set.all().order_by('item__uplevel__priority', 'item__priority').prefetch_related('report', 'item')
        except:
            try:
                report = ReportHoliday.objects.get(project=project, date=report_date)
                report.i_sum_money=0
                report.c_sum_money=0
            except:
                report = Report(id=-1, date=report_date, i_sum_money=0, c_sum_money=0, project=project)
            report_items = []

        version = Version.objects.filter(project=project, start_date__lte=report_date).order_by('-start_date')[0]
        report.change_engs_price = version.engs_price if Version.objects.filter(project=project).count()-1 != 0 else ''
        report.change_version_times = Version.objects.filter(project=project, start_date__lte=report.date).count() - 1
        report.weekday = weekday_name[report_date.weekday()]
        root_item = version.item_set.get(uplevel=None)

        items = root_item.read_deep_sub_item_in_list()

        if info_type == 'all':
            tmp_items = []
            for item in items:
                if item.kind == DIRKIND:
                    tmp_items.append(item)
                    continue
                if report_items:
                    #表示當天有填寫紀錄
                    try:
                        report_item = report_items.get(item=item)
                    except:
                        report_item = ReportItem(report=report, item=item)
                        report_item.save()
                    if report_type == 'inspector':
                        item.num = report_item.i_num
                        version_items[version.id][item.id] += report_item.i_num
                        item.sum_num = version_items[version.id][item.id]
                        item.note = report_item.i_note
                    else:
                        item.num = report_item.c_num
                        version_items[version.id][item.id] += report_item.c_num
                        item.sum_num = version_items[version.id][item.id]
                        item.note = report_item.c_note
                else:
                    #當天沒有填寫紀錄
                    item.num = 0
                    item.sum_num = version_items[version.id][item.id]

                tmp_items.append(item)
            items = tmp_items
            items.pop(0)
        elif info_type == 'write':
            tmp_items = []
            if report_items:
                #表示當天有填寫紀錄
                for item in report_items:
                    if item.item.kind == DIRKIND: continue
                    if report_type == 'inspector':
                        if item.i_num or item.i_note:
                            item.item.num = item.i_num
                            version_items[version.id][item.item.id] += item.i_num
                            item.item.sum_num = version_items[version.id][item.item.id]
                            item.item.note = item.i_note
                            tmp_items.append(item.item)
                    else:
                        if item.c_num or item.c_note:
                            item.item.num = item.c_num
                            version_items[version.id][item.item.id] += item.c_num
                            item.item.sum_num = version_items[version.id][item.item.id]
                            item.item.note = item.c_note
                            tmp_items.append(item.item)
                items = tmp_items
            else:
                items = []
        elif info_type == 'blank':
            for item in items:
                item.num = ''
                item.note = ''
            items.pop(0)

        #計算本日完成、累計完成、預定累計完成
        pre_reports = Report.objects.filter(project=project, date__lte=report_date).order_by('-date')
        if not report_items and pre_reports: report_items = pre_reports[0].reportitem_set.all().prefetch_related('report', 'item')
        if report_type == 'inspector':
            if root_item.read_dir_price_by_roundkind() == 0:
                report.today_progress_rate = 0
                report.sum_progress_rate = 0
            else:
                report_money = sum([i.i_sum_money for i in Report.objects.filter(project=project, date__gte=version.start_date, date__lte=report_date)])
                report.today_progress_rate = round(float(str(report.i_sum_money)) / root_item.read_dir_price_by_roundkind() * 100., 3)
                report.sum_progress_rate = round(float(str(report_money + version.pre_i_money)) / root_item.read_dir_price_by_roundkind() * 100., 3)

        else:
            if root_item.read_dir_price_by_roundkind() == 0:
                report.today_progress_rate = 0
                report.sum_progress_rate = 0
            else:
                report_money = sum([i.c_sum_money for i in Report.objects.filter(project=project, date__gte=version.start_date, date__lte=report_date)])
                report.today_progress_rate = round(float(str(report.c_sum_money)) / root_item.read_dir_price_by_roundkind() * 100., 3)
                report.sum_progress_rate = round(float(str(report_money + version.pre_c_money)) / root_item.read_dir_price_by_roundkind() * 100., 3)

        schedule_progress_list = engprofile.read_schedule_progress()
        try:
            report.design_percent = schedule_progress_list[report_date]
        except:
            max_date = max([sp for sp in schedule_progress_list])
            if report_date >= max_date:
                report.design_percent = schedule_progress_list[max_date]
            else:
                dd = report_date - datetime.timedelta(1)
                while dd not in workingdates and dd >= engprofile.start_date:
                    dd -= datetime.timedelta(1)
                if dd < engprofile.start_date:
                    report.design_percent = 0
                else:
                    report.design_percent = schedule_progress_list[dd]

        max_day = max(workingdates)
        if engprofile.date_type.value == u'限期完工(日曆天每日施工)':
            report.all_duration = engprofile.deadline + datetime.timedelta(sum([i.day for i in Extension.objects.filter(project=project, date__lte=report_date)]))
            report.all_duration = (report.all_duration - engprofile.start_date).days
        else:
            report.all_duration = engprofile.duration + sum([i.day for i in Extension.objects.filter(project=project, date__lte=report_date)])
            
        if report.date >= max_day:
            report.used_duration = workingdates.index(max_day) + 1 + int((report.date - max_day).days)
        else:
            dd = report.date
            while dd not in workingdates and dd >= engprofile.start_date:
                dd -= datetime.timedelta(1)
            if dd < engprofile.start_date:
                report.used_duration = 0
            else:
                report.used_duration = workingdates.index(dd) + 1
        #已用天數減不計工期
        # report.used_duration -= sum([i.day for i in Extension.objects.filter(project=project, date__lte=report.date, type__value=u'不計工期')])

        # report.unused_duration = len(engprofile.readWorkingDate(is_scheduled=True)) - sum([i.day for i in Extension.objects.filter(project=project, date__gt=report.date)]) - report.used_duration
        report.unused_duration = report.all_duration - report.used_duration

        report.extensions = sum([i.day for i in Extension.objects.filter(project=project, date__lte=report.date)])
        report.scheduled_completion_day = engprofile.readScheduledCompletionDay(date=report.date) 
 
        labors_and_equips = []
        site_materials = []
        if report_type == 'contractor':
            labors = LaborEquip.objects.filter(project=project, type__swarm='labor_or_equip', type__value=u'人員').order_by('sort')
            for labor in labors:
                try:
                    report_labor_equip = ReportLaborEquip.objects.get(report=report, type=labor)
                    labor.num = report_labor_equip.num
                except:
                    labor.num = 0
                labor.sum_num = sum([rle.num for rle in ReportLaborEquip.objects.filter(report__date__lte=report.date, type=labor)])
                if not labor.sum_num: labor.sum_num = 0

            equips = LaborEquip.objects.filter(project=project, type__swarm='labor_or_equip', type__value=u'機具').order_by('sort')
            for equip in equips:
                try:
                    report_labor_equip = ReportLaborEquip.objects.get(report=report, type=equip)
                    equip.num = report_labor_equip.num
                except:
                    equip.num = 0
                equip.sum_num = sum([rle.num for rle in ReportLaborEquip.objects.filter(report__date__lte=report.date, type=equip)])
                if not equip.sum_num: equip.sum_num = 0

            if info_type == 'all':
                labors_and_equips = []
                for i in xrange(max([labors.count(), equips.count()])):
                    if i >= labors.count():
                        labor = ''
                    else:
                        labor = labors[i]
                    if i >= equips.count():
                        equip = ''
                    else:
                        equip = equips[i]
                    labors_and_equips.append([labor, equip])
            elif info_type == 'write':
                labors_and_equips = []
                labors_tmp = []
                for l in labors:
                    if l.num: labors_tmp.append(l)
                equips_tmp = []
                for e in equips:
                    if e.num: equips_tmp.append(e)
                labors = labors_tmp
                equips = equips_tmp
                for i in xrange(max([len(labors), len(equips)])):
                    if i >= len(labors):
                        labor = ''
                    else:
                        labor = labors[i]
                    if i >= len(equips):
                        equip = ''
                    else:
                        equip = equips[i]
                    labors_and_equips.append([labor, equip])
            elif info_type == 'blank':
                labors_and_equips = []
                for i in xrange(max([labors.count(), equips.count()])):
                    if i >= labors.count():
                        labor = ''
                    else:
                        labors[i].num = ''
                        labors[i].sum_num = ''
                        labor = labors[i]
                    if i >= equips.count():
                        equip = ''
                    else:
                        equips[i].num = ''
                        equips[i].sum_num = ''
                        equip = equips[i]
                    labors_and_equips.append([labor, equip])
            try:
                site_materials = SiteMaterial.objects.filter(report=report)
            except:
                site_materials = []

        test_records = []
        if HAVE_RCM_TEST_RECORD_SYSTEM:
            test_records = TestRecord.objects.filter(testtype__project=project, record_date=report.date).order_by('testtype', 'record_date')

        report.test_records = test_records
        report.items = items
        report.labors_and_equips = labors_and_equips
        report.site_materials = site_materials
        reports.append(report)
        report_date += datetime.timedelta(1)

    t = get_template(os.path.join('dailyreport', 'zh-tw', 'online_print_' + report_type + '2.html'))
    html = t.render(RequestContext(R,{
            'engprofile': engprofile,
            'reports': reports,
            'report_type': report_type,
        }))

    return HttpResponse(html)


@login_required
def make_excel_range2(R, **kw):
    """
        輸出Excel區間報表
        2017/08/01 日前版本
    """
    project = Project.objects.get(id=kw['project_id'])
    report_type = kw['report_type']
    info_type = kw['info_type']
    engprofile = EngProfile.objects.get(project=project)
    start_report_date = kw['start_report_date']
    start_report_date = datetime.datetime.strptime(start_report_date, "%Y-%m-%d").date()
    end_report_date = kw['end_report_date']
    end_report_date = datetime.datetime.strptime(end_report_date, "%Y-%m-%d").date()
    if start_report_date < engprofile.start_date: start_report_date = engprofile.start_date
    if end_report_date < engprofile.start_date: end_report_date = engprofile.start_date
    user_perms = get_perms(R.user, engprofile)
    
    weekday_name = [u'星期一', u'星期二', u'星期三', u'星期四', u'星期五', u'星期六', u'星期日']
    
    if not R.user.has_perm('fishuser.view_all_project_in_remote_control_system'):
        #沒有 "在(遠端工程系統)中_觀看_所有_工程案資訊"
        if not 'view_single_project_in_remote_control_system' in get_perms(R.user, project):
            #沒有 觀看此project 的 "在(遠端工程系統)中_觀看_單一_工程案資訊" 權限
            if project.unit != R.user.user_profile.unit:
                return HttpResponseRedirect('/')
        elif 'view_single_project_in_remote_control_system' in get_perms(R.user, project):
            #有 觀看此project 的 "在(遠端工程系統)中_觀看_單一_工程案資訊" 權限
            if not R.user.frcmusergroup_set.get(project=project).is_active:
                #被關閉權限的
                return HttpResponseRedirect('/')
    else:
        if R.user.username[1] == '_' and not R.user.is_staff:
            if project.unit != R.user.user_profile.unit:
                return HttpResponseRedirect('/')

    workingdates = engprofile.readWorkingDate()
    engprofile.working_days = len(workingdates)
    engprofile.extension = sum([i.day for i in engprofile.readExtensions()])
    report_date = start_report_date

    engprofile.contractor_name = engprofile.contractor_name if engprofile.contractor_name else ''

    start_version = Version.objects.filter(project=project, start_date__lte=start_report_date).order_by('-start_date')
    if start_version:
        start_version = start_version[0]
    else:
        start_version = Version.objects.filter(project=project).order_by('-start_date')[0]
    end_version = Version.objects.filter(project=project, start_date__lte=end_report_date).order_by('-start_date')
    if end_version:
        end_version = end_version[0]
    else:
        end_version = Version.objects.filter(project=project).order_by('-start_date')[0]

    versions = Version.objects.filter(project=project, start_date__gte=start_version.start_date, start_date__lte=end_version.start_date).order_by('start_date')
    version_items = {}
    for n, v in enumerate(versions):
        version_items[v.id] = {}
        version_items[v.id]['root_item'] = v.item_set.get(uplevel=None)
        version_items[v.id]['items'] = version_items[v.id]['root_item'].read_deep_sub_item_in_list()
        for i in version_items[v.id]['items']:
            if n == 0:
                if report_type == 'inspector':
                    version_items[v.id][i.id] = sum([k.i_num for k in ReportItem.objects.filter(report__date__lt=start_report_date, item__in=i.read_brother_items()).exclude(i_num='0')])
                else:
                    version_items[v.id][i.id] = sum([k.c_num for k in ReportItem.objects.filter(report__date__lt=start_report_date, item__in=i.read_brother_items()).exclude(c_num='0')])
                
            else:
                if report_type == 'inspector':
                    version_items[v.id][i.id] = sum([k.i_num for k in ReportItem.objects.filter(report__date__lt=v.start_date, item__in=i.read_brother_items()).exclude(i_num='0')])
                else:
                    version_items[v.id][i.id] = sum([k.c_num for k in ReportItem.objects.filter(report__date__lt=v.start_date, item__in=i.read_brother_items()).exclude(c_num='0')])

    data = {'reports': {}}
    while report_date <= end_report_date:
        if report_date not in workingdates and report_date <= workingdates[-1] and not ReportHoliday.objects.filter(project=project, date=report_date):
            report_date += datetime.timedelta(1)
            continue

        try:
            #看看當天有沒有填寫過
            report = Report.objects.get(project=project, date=report_date)
            report_items = report.reportitem_set.all().order_by('item__uplevel__priority', 'item__priority').prefetch_related('report', 'item')
        except:
            try:
                report = ReportHoliday.objects.get(project=project, date=report_date)
                report.i_sum_money=0
                report.c_sum_money=0
            except:
                report = Report(id=-1, date=report_date, i_sum_money=0, c_sum_money=0, project=project)
            report.has_professional_item = False
            report_items = []

        version = versions.filter(start_date__lte=report_date).order_by('-start_date')[0]
        root_item = version_items[version.id]['root_item']
        items = version_items[version.id]['items']
        report.weekday = weekday_name[report_date.weekday()]

        #計算本日完成、累計完成、預定累計完成
        pre_reports = Report.objects.filter(project=project, date__lte=report_date).order_by('-date')
        if not report_items and pre_reports: report_items = pre_reports[0].reportitem_set.all().prefetch_related('report', 'item')
        if report_type == 'inspector':
            if root_item.read_dir_price_by_roundkind() == 0:
                report.today_progress_rate = 0
                report.sum_progress_rate = 0
            else:
                report_money = sum([i.i_sum_money for i in Report.objects.filter(project=project, date__gte=version.start_date, date__lte=report_date)])
                report.today_progress_rate = round(float(str(report.i_sum_money)) / root_item.read_dir_price_by_roundkind() * 100., 3)
                report.sum_progress_rate = round(float(str(report_money + version.pre_i_money)) / root_item.read_dir_price_by_roundkind() * 100., 3)

        else:
            if root_item.read_dir_price_by_roundkind() == 0:
                report.today_progress_rate = 0
                report.sum_progress_rate = 0
            else:
                report_money = sum([i.c_sum_money for i in Report.objects.filter(project=project, date__gte=version.start_date, date__lte=report_date)])
                report.today_progress_rate = round(float(str(report.c_sum_money)) / root_item.read_dir_price_by_roundkind() * 100., 3)
                report.sum_progress_rate = round(float(str(report_money + version.pre_c_money)) / root_item.read_dir_price_by_roundkind() * 100., 3)

        schedule_progress_list = engprofile.read_schedule_progress()
        try:
            report.design_percent = schedule_progress_list[report_date]
        except:
            max_date = max([sp for sp in schedule_progress_list])
            if report_date >= max_date:
                report.design_percent = schedule_progress_list[max_date]
            else:
                dd = report_date - datetime.timedelta(1)
                while dd not in workingdates and dd >= engprofile.start_date:
                    dd -= datetime.timedelta(1)
                if dd < engprofile.start_date:
                    report.design_percent = 0
                else:
                    report.design_percent = schedule_progress_list[dd]

        max_day = max(workingdates)
        if engprofile.date_type.value == u'限期完工(日曆天每日施工)':
            all_duration = engprofile.deadline + datetime.timedelta(sum([i.day for i in Extension.objects.filter(project=project, date__lte=report_date)]))
            all_duration = (all_duration - engprofile.start_date).days
        else:
            all_duration = engprofile.duration + sum([i.day for i in Extension.objects.filter(project=project, date__lte=report_date)])
            
        if report.date >= max_day:
            report.used_duration = workingdates.index(max_day) + 1 + int((report.date - max_day).days)
        else:
            dd = report.date
            while dd not in workingdates and dd >= engprofile.start_date:
                dd -= datetime.timedelta(1)
            if dd < engprofile.start_date:
                report.used_duration = 0
            else:
                report.used_duration = workingdates.index(dd) + 1
        
        # report.unused_duration = len(engprofile.readWorkingDate(is_scheduled=True)) - sum([i.day for i in Extension.objects.filter(project=project, date__gt=report.date)]) - report.used_duration
        #已用天數減不計工期
        # report.used_duration -= sum([i.day for i in Extension.objects.filter(project=project, date__lte=report.date, type__value=u'不計工期')])

        report.extensions = sum([i.day for i in Extension.objects.filter(project=project, date__lte=report.date)])
        report.scheduled_completion_day = engprofile.readScheduledCompletionDay(date=report.date) 
        
        report.unused_duration = all_duration - report.used_duration
        data['reports'][str(report_date)] = {}
        data['reports'][str(report_date)]['item_table'] = []
        data['reports'][str(report_date)]['manmachine_table'] = []
        data['reports'][str(report_date)]['site_material_table'] = []
        
        data['reports'][str(report_date)]['replace'] = {
                'reportdate': '%s-%s-%s(%s)' % (report_date.year-1911, report_date.month, report_date.day, report.weekday),
                'morning_weather': report.morning_weather.value if report.id != -1 and report.morning_weather else '',
                'afternoon_weather': report.afternoon_weather.value if report.id != -1 and report.afternoon_weather else '',
                'project_name': report.project.name,
                'duration': engprofile.duration,
                'all_duration': all_duration,
                'used_duration': report.used_duration,
                'unused_duration': report.unused_duration,
                'extension': engprofile.readExtensionDay(),
                'project_contractor_name': engprofile.contractor_name,
                'start_date': '%s-%s-%s' % (engprofile.start_date.year-1911, engprofile.start_date.month, engprofile.start_date.day),
                'end_date': '%s-%s-%s' % (report.scheduled_completion_day.year-1911, report.scheduled_completion_day.month, report.scheduled_completion_day.day),
                'design_percent': round(float(report.design_percent), 3),
                'act_percent': round(report.sum_progress_rate, 3),
                'change_version_times': Version.objects.filter(project=project, start_date__lte=report.date).count()-1,
                'init_version_price': Version.objects.filter(project=project).order_by('start_date')[0].engs_price,
                'change_version_price': version.engs_price if Version.objects.filter(project=project).count()-1 != 0 else '',
                'has_professional_item': u'有' if hasattr(report, 'has_professional_item') and report.has_professional_item else u'無',
                'pre_education': u'有' if hasattr(report, 'pre_education') and report.pre_education else u'無',
                'has_insurance': [u'有', u'無', u'無新進勞工'][report.has_insurance-1] if hasattr(report, 'has_insurance') else u'無',
                'safety_equipment': u'有' if hasattr(report, 'safety_equipment') and report.safety_equipment else u'無',
                'pre_check': u'有' if hasattr(report, 'pre_check') and report.pre_check else u'無',
                #'date_type': engprofile.date_type.value,
            }
        if report_type == 'inspector':
            data['reports'][str(report_date)]['replace']['describe_subcontractor'] = report.describe_subcontractor if report.describe_subcontractor else ''
            data['reports'][str(report_date)]['replace']['sampling'] = report.sampling if report.sampling else ''
            data['reports'][str(report_date)]['replace']['notify'] = report.notify if report.notify else ''
            data['reports'][str(report_date)]['replace']['note'] = report.note if report.note else ''
            data['reports'][str(report_date)]['replace']['i_pre_check'] = report.i_pre_check if hasattr(report, 'i_pre_check') and report.i_pre_check else ''
            data['reports'][str(report_date)]['replace']['i_project_status'] = report.i_project_status if hasattr(report, 'i_project_status') and report.i_project_status else ''
        else:
            data['reports'][str(report_date)]['replace']['describe_subcontractor'] = report.c_describe_subcontractor if report.c_describe_subcontractor else ''
            data['reports'][str(report_date)]['replace']['sampling'] = report.c_sampling if report.c_sampling else ''
            data['reports'][str(report_date)]['replace']['notify'] = report.c_notify if report.c_notify else ''
            data['reports'][str(report_date)]['replace']['note'] = report.c_note if report.c_note else ''
        

        item_table = data['reports'][str(report_date)]['item_table']
        manmachine_table = data['reports'][str(report_date)]['manmachine_table']
        site_material_table = data['reports'][str(report_date)]['site_material_table']
        replace = data['reports'][str(report_date)]['replace']

        if info_type == 'all':
            if report_date not in workingdates: report_items = []
            for item in items[1:]:
                if item.kind == DIRKIND:
                    item_table.append([item.name, u'---',
                        str(item.unit_num), '', '', '', 'dir'])
                    continue
                item.note = ''
                if report_items:
                    #表示當天有填寫紀錄
                    try:
                        report_item = report_items.get(item=item)
                    except:
                        report_item = ReportItem(report=report, item=item)
                        report_item.save()
                    if report_type == 'inspector':
                        item.num = report_item.i_num if report_item.i_num else ''
                        version_items[version.id][item.id] += report_item.i_num
                        item.sum_num = version_items[version.id][item.id]
                        item.note = report_item.i_note
                    else:
                        item.num = report_item.c_num if report_item.c_num else ''
                        version_items[version.id][item.id] += report_item.c_num
                        item.sum_num = version_items[version.id][item.id]
                        item.note = report_item.c_note

                else:
                    #當天沒有填寫紀錄
                    item.num = ''
                    item.sum_num = version_items[version.id][item.id]
                    item.note = ''
                
                item_table.append([item.name, item.unit_name,
                    str(item.unit_num), str(item.num), str(item.sum_num), item.note])

        elif info_type == 'write':
            if report_date not in workingdates: report_items = []
            if report_items:
                #表示當天有填寫紀錄
                for item in report_items:
                    if item.item.kind == DIRKIND: continue
                    if report_type == 'inspector':
                        if item.i_num or item.i_note:
                            item.item.num = item.i_num
                            version_items[version.id][item.item.id] += item.i_num
                            item.item.sum_num = version_items[version.id][item.item.id]
                            item.item.note = item.i_note
                            item_table.append([item.item.name, item.item.unit_name,
                                str(item.item.unit_num), str(item.item.num), str(item.item.sum_num), item.item.note])
                    else:
                        if item.c_num or item.c_note:
                            item.item.num = item.c_num
                            version_items[version.id][item.item.id] += item.c_num
                            item.item.sum_num = version_items[version.id][item.item.id]
                            item.item.note = item.c_note
                            item_table.append([item.item.name, item.item.unit_name,
                                str(item.item.unit_num), str(item.item.num), str(item.item.sum_num), item.item.note])

        elif info_type == 'blank':
            replace['has_professional_item'] = u'□有□無'
            for item in items[1:]:
                if item.kind == DIRKIND:
                    item_table.append([item.name, item.unit_name, str(item.unit_num), '', '', '', 'dir'])
                else:
                    item_table.append([item.name, item.unit_name, str(item.unit_num), '', '', ''])

        

        labors_and_equips = []
        site_materials = []
        if report_type == 'contractor':
            labors = LaborEquip.objects.filter(project=project, type__swarm='labor_or_equip', type__value=u'人員').order_by('sort')
            for labor in labors:
                try:
                    report_labor_equip = ReportLaborEquip.objects.get(report=report, type=labor)
                    labor.num = report_labor_equip.num
                except:
                    labor.num = ''
                labor.sum_num = sum([rle.num for rle in ReportLaborEquip.objects.filter(report__date__lte=report.date, type=labor)])
                if not labor.sum_num: labor.sum_num = 0

            equips = LaborEquip.objects.filter(project=project, type__swarm='labor_or_equip', type__value=u'機具').order_by('sort')
            for equip in equips:
                try:
                    report_labor_equip = ReportLaborEquip.objects.get(report=report, type=equip)
                    equip.num = report_labor_equip.num
                except:
                    equip.num = ''
                equip.sum_num = sum([rle.num for rle in ReportLaborEquip.objects.filter(report__date__lte=report.date, type=equip)])
                if not equip.sum_num: equip.sum_num = 0

            if info_type == 'all':
                labors_and_equips = []
                for i in xrange(max([labors.count(), equips.count()])):
                    if i >= labors.count():
                        labor = ''
                    else:
                        labor = labors[i]
                    if i >= equips.count():
                        equip = ''
                    else:
                        equip = equips[i]

                    if labor: lv, ln, lsn = str(labor.value), str(labor.num), str(labor.sum_num)
                    else:lv, ln, lsn = '', '', ''
                    if equip: ev, en, esn = str(equip.value), str(equip.num), str(equip.sum_num)
                    else:ev, en, esn = '', '', ''
                    manmachine_table.append([
                        lv, ln, lsn,
                        ev, en, esn])
            elif info_type == 'write':
                labors_and_equips = []
                labors_tmp = []
                for l in labors:
                    if l.num: labors_tmp.append(l)
                equips_tmp = []
                for e in equips:
                    if e.num: equips_tmp.append(e)
                labors = labors_tmp
                equips = equips_tmp
                for i in xrange(max([len(labors), len(equips)])):
                    if i >= len(labors):
                        labor = ''
                    else:
                        labor = labors[i]
                    if i >= len(equips):
                        equip = ''
                    else:
                        equip = equips[i]

                    if labor: lv, ln, lsn = str(labor.value), str(labor.num), str(labor.sum_num)
                    else:lv, ln, lsn = '', '', ''
                    if equip: ev, en, esn = str(equip.value), str(equip.num), str(equip.sum_num)
                    else:ev, en, esn = '', '', ''
                    manmachine_table.append([
                        lv, ln, lsn,
                        ev, en, esn])
            elif info_type == 'blank':
                labors_and_equips = []
                for i in xrange(max([labors.count(), equips.count()])):
                    if i >= labors.count():
                        labor = ''
                    else:
                        labors[i].num = ''
                        labors[i].sum_num = ''
                        labor = labors[i]
                    if i >= equips.count():
                        equip = ''
                    else:
                        equips[i].num = ''
                        equips[i].sum_num = ''
                        equip = equips[i]
                    if labor: lv, ln, lsn = str(labor.value), str(labor.num), str(labor.sum_num)
                    else:lv, ln, lsn = '', '', ''
                    if equip: ev, en, esn = str(equip.value), str(equip.num), str(equip.sum_num)
                    else:ev, en, esn = '', '', ''
                    manmachine_table.append([
                        lv, ln, lsn,
                        ev, en, esn])
            try:
                site_materials = SiteMaterial.objects.filter(report=report)
                for sm in site_materials:
                    site_material_table.append([sm.name, sm.unit_name,
                        str(sm.unit_num), str(sm.today_num), str(sm.today_sum_num), sm.note])
            except: pass
        report_date += datetime.timedelta(1)

    #開始製造EXCEL
    output = StringIO()
    workbook = xlsxwriter.Workbook(output, 
                {'strings_to_numbers':  True,
                'strings_to_formulas': False,
                'strings_to_urls':     False})

    if report_type == 'inspector':
        workbook = make_inspector_excel_file2(workbook=workbook, data=data)
    elif report_type == 'contractor':
        workbook = make_contractor_excel_file2(workbook=workbook, data=data)

    workbook.close()
    output.seek(0)
    response = HttpResponse(output.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    if start_report_date == end_report_date:
        response['Content-Disposition'] = ('attachment; filename=%s(%s)_%s_%s.xlsx' % (str(start_report_date), report_type[0], engprofile.project.name.replace(' ', ''), info_type)).encode('cp950', 'replace')
    else:
        response['Content-Disposition'] = ('attachment; filename=%s~%s(%s)_%s_%s.xlsx' % (str(start_report_date), str(end_report_date), report_type[0], engprofile.project.name.replace(' ', ''), info_type)).encode('cp950', 'replace')
    
    return response


@login_required
def calender(R, **kw):
    """工期彙整行事曆頁面"""
    project = Project.objects.get(id=kw['project_id'])
    report_type = kw['report_type']
    engprofile = EngProfile.objects.get(project=project)
    
    if not R.user.has_perm('fishuser.view_all_project_in_remote_control_system'):
        #沒有 "在(遠端工程系統)中_觀看_所有_工程案資訊"
        if not 'view_single_project_in_remote_control_system' in get_perms(R.user, project):
            #沒有 觀看此project 的 "在(遠端工程系統)中_觀看_單一_工程案資訊" 權限
            if project.unit != R.user.user_profile.unit:
                return HttpResponseRedirect('/')
        elif 'view_single_project_in_remote_control_system' in get_perms(R.user, project):
            #有 觀看此project 的 "在(遠端工程系統)中_觀看_單一_工程案資訊" 權限
            if not R.user.frcmusergroup_set.get(project=project).is_active:
                #被關閉權限的
                return HttpResponseRedirect('/')
    else:
        if R.user.username[1] == '_' and not R.user.is_staff:
            if project.unit != R.user.user_profile.unit:
                return HttpResponseRedirect('/')

    if 'edit_engprofile' in get_perms(R.user, engprofile) or R.user.has_perm('dailyreport.edit_engprofile'):
        if R.user.is_staff:
            edit = True
        else:
            if FRCMUserGroup.objects.get(project=project, user=R.user).group.name == CONTRACTOR_NAME:
                edit = False
            else:
                edit = True
    else:
        edit = False


    reports = Report.objects.filter(project=project).order_by('-date')
    if report_type == 'inspector' and reports.filter(inspector_check=True):
        last_day = reports.filter(inspector_check=True).order_by('-date')[0].date
    elif report_type == 'contractor' and reports.filter(contractor_check=True):
        last_day = reports.filter(contractor_check=True).order_by('-date')[0].date
    else:
        last_day = engprofile.start_date

    events = []
    colors = {
        u'停工': '#b0afff !important',
        u'強制開工': '#ffafd6 !important',
        u'休息日': '#afd6ff !important',
        u'雨天(不計工期)': '#b0afff !important',
        u'不計工期': '#b0afff !important',
        u'假日': '#afd6ff !important',
    }

    working_dates = engprofile.readWorkingDate()
    date = engprofile.start_date
    day = 0
    events.append(
        {
            'title': u'今天',
            'start': str(TODAY()),
            'textColor': 'black',
            'backgroundColor': '#FFD6BB !important'
        }
    )

    while date <= working_dates[-1]:
        if date in working_dates:
            day += 1

        events.append(
            {
                'title': u'累積工期：%s天' % (day),
                'start': str(date),
                'textColor': 'black',
                'backgroundColor': '#ccc !important'
            }
        )

        date += datetime.timedelta(days=1)

    events.append(
            {
                'title': u'開工日',
                'start': str(engprofile.start_date),
                'textColor': 'black',
                'backgroundColor': '#B6FF00 !important',
                'date_range': str(engprofile.start_date),
                'date_memo': u'工程開工日',
            }
        )

    for i in project.dailyreport_extension.all():
        events.append(
            {
                'title': u'設定「%s」 (%s天)' % (u"展延", i.day),
                'start': str(i.date),
                'textColor': 'black',
                'backgroundColor': '#E98015 !important',
                'date_range': str(i.date),
                'date_memo': u'%s天數：%s天<br>文號：%s<br>備註：%s' % (u"展延", i.day, i.no, i.memo.replace('\n', '')),
            }
        )

    for i in project.dailyreport_specialdate.all():
        events.append(
            {
                'title': u'%s' % (i.type.value),
                'start': str(i.start_date),
                'end': str(i.end_date + datetime.timedelta(days=1)),
                'textColor': 'black',
                'backgroundColor': colors[i.type.value],
                'date_range': str(i.start_date) if i.start_date == i.end_date else '%s ~ %s' % (i.start_date, i.end_date),
                'date_memo': u'文號：%s<br>原因：%s' % (i.no, i.reason.replace('\n', '')),
            }
        )
        events.append(
            {
                'start': str(i.start_date),
                'end': str(i.end_date + datetime.timedelta(days=1)),
                'rendering': 'background',
                'backgroundColor': colors[i.type.value]
            }
        )

    if engprofile.scheduled_completion_day:
        engprofile.end_date = end_date = engprofile.scheduled_completion_day
    else:
        engprofile.end_date = end_date = engprofile.readWorkingDate(is_scheduled=True)[-1]

    events.append(
            {
                'title': u'預定完工日',
                'start': str(end_date),
                'textColor': 'black',
                'backgroundColor': '#B6FF00 !important',
                'date_range': str(end_date),
                'date_memo': u'預定完工日',
            }
        )

    extensions = Extension.objects.filter(project=project).order_by('date')
    special_dates = SpecialDate.objects.filter(project=project)

    #讀取 政府行政機關辦公日曆表  國定假日
    # try:
    #     url = 'http://data.ntpc.gov.tw/api/v1/rest/datastore/382000000A-000077-002'
    #     opener = urllib2.build_opener()
    #     opener.addheaders = [('User-agent', 'Chrome')]
    #     response = opener.open(url)
    #     contents = json.loads(response.read())
    # except:
    f = open(os.path.join(settings.ROOT, 'apps', 'dailyreport', 'static', 'dailyreport', 'holidays.json'))
    contents = json.load(f)
    print('load success')
 
    holidays = []
    for row in contents['result']['records']:
        if row['holidayCategory'] != u"星期六、星期日":
            date = row['date'].split('/')
            row['date'] = datetime.date(int(date[0]),int(date[1]),int(date[2]))
            if row['date'] >= engprofile.start_date and row['date'] <= (engprofile.end_date + datetime.timedelta(days=60)):
                holidays.append(row)

    t = get_template(os.path.join('dailyreport', 'zh-tw', 'calender.html'))
    html = t.render(RequestContext(R,{
        'edit': edit,
        'engprofile': engprofile,
        'choose': _make_choose(),
        'events': events,
        'holidays': holidays,
        'last_day': last_day,
        'extensions': extensions,
        'special_dates': special_dates,
        'report_type': report_type,
        'toppage_name': u'工期彙整行事曆',
        }))
    return HttpResponse(html)


@login_required
def make_excel_working_date(R, **kw):
    """輸出Excel 工作天"""
    project = Project.objects.get(id=kw['project_id'])
    engprofile = EngProfile.objects.get(project=project)

    #開始製造EXCEL
    output = StringIO()
    workbook = xlsxwriter.Workbook(output, 
                {'strings_to_numbers':  True,
                'strings_to_formulas': False,
                'strings_to_urls':     False})

    workbook = make_working_date_excel_file(workbook=workbook, engprofile=engprofile)

    workbook.close()

    output.seek(0)
    response = HttpResponse(output.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response['Content-Disposition'] = ('attachment; filename=%s-%s-工期彙整.xlsx' % (str(TODAY()), engprofile.project.name.replace(' ', ''))).encode('cp950', 'replace')
    
    return response


@login_required
def calendar_information(R, **kw):
    # 行事歷程
    project = Project.objects.get(id=kw['project_id'])
    report_type = kw['report_type']
    engprofile = EngProfile.objects.get(project=project)
    user_perms = get_perms(R.user, engprofile)
    date_range = kw['date_range']

    if not R.user.has_perm('fishuser.view_all_project_in_remote_control_system'):
        #沒有 "在(遠端工程系統)中_觀看_所有_工程案資訊"
        if not 'view_single_project_in_remote_control_system' in get_perms(R.user, project):
            #沒有 觀看此project 的 "在(遠端工程系統)中_觀看_單一_工程案資訊" 權限
            if project.unit != R.user.user_profile.unit:
                return HttpResponseRedirect('/')
        elif 'view_single_project_in_remote_control_system' in get_perms(R.user, project):
            #有 觀看此project 的 "在(遠端工程系統)中_觀看_單一_工程案資訊" 權限
            if not R.user.frcmusergroup_set.get(project=project).is_active:
                #被關閉權限的
                return HttpResponseRedirect('/')
    else:
        if R.user.username[1] == '_' and not R.user.is_staff:
            if project.unit != R.user.user_profile.unit:
                return HttpResponseRedirect('/')


    if 'edit_engprofile' in get_perms(R.user, engprofile) or R.user.has_perm('dailyreport.edit_engprofile'):
        if R.user.is_staff:
            edit_inspector = True
            edit_contractor = True
        else:
            if FRCMUserGroup.objects.get(project=project, user=R.user).group.name == CONTRACTOR_NAME:
                edit_inspector = False
                edit_contractor = True
            elif FRCMUserGroup.objects.get(project=project, user=R.user).group.name == INSPECTOR_NAME:
                edit_inspector = True
                edit_contractor = False
    else:
        edit_inspector = False
        edit_contractor = False

    edit = edit_inspector or edit_contractor
    
    workingdates_default = engprofile.readWorkingDate()
    if TODAY() < workingdates_default[-1]:
        defined_finish_date = TODAY()
    else:
        defined_finish_date = workingdates_default[-1]

    reports = Report.objects.filter(project=project).order_by('-date')

    if reports:
        if reports[0].date > defined_finish_date:
            defined_finish_date = reports[0].date

    workingdates = engprofile.readWorkingDate(defined_finish_date=defined_finish_date)

    all_month = [[workingdates[0].year, [str(workingdates[0].month).zfill(2)]]]
    for d in workingdates:
        if d.year == all_month[-1][0]:
            if str(d.month).zfill(2) not in all_month[-1][1]:
                all_month[-1][1].append(str(d.month).zfill(2))
        else:
            all_month.append([d.year, [str(d.month).zfill(2)]])

    calendars = []
    week_string = [u'一', u'二', u'三', u'四', u'五', u'六', u'日']

    if date_range == 'first':
        if TODAY() > workingdates[-1]:
            date_range = [str(workingdates[-1].year), str(workingdates[-1].month).zfill(2)]
        else:
            date_range = [str(TODAY().year), str(TODAY().month).zfill(2)]
    elif date_range != 'all':
        date_range = date_range.split('-')

    for d in workingdates:
        if date_range != 'all':
            if str(d.year) != date_range[0] or str(d.month).zfill(2) != date_range[1]:
                continue

        try:
            r = reports.get(date=d)
        except:
            r = Report(date=d)

        if d > TODAY():
            r.edit_button = False
        else:
            r.edit_button = True

        r.isoweekday = week_string[r.date.isoweekday()-1]
        if r.isoweekday == u'六' or r.isoweekday == u'日':
            r.is_weekend = True

        calendars.append(r)

    templat_name = 'information_calendar.html'

    t = get_template(os.path.join('dailyreport', 'zh-tw', templat_name))
    html = t.render(RequestContext(R,{
        'engprofile': engprofile,
        'user_perms': user_perms,
        'choose': _make_choose(),
        'calendars': calendars,
        'all_month': all_month,
        'edit': edit,
        'date_range': date_range,
        'edit_inspector': edit_inspector,
        'edit_contractor': edit_contractor,
        'report_type': report_type,
        'toppage_name': u'整合資訊',
        'subpage_name': u'行事歷程',
        }))
    return HttpResponse(html)


@login_required
def read_progress_information(R, **kw):
    # 進度資訊列表
    project = Project.objects.get(id=kw['project_id'])
    report_type = kw['report_type']
    engprofile = EngProfile.objects.get(project=project)
    user_perms = get_perms(R.user, engprofile)
    date_range = kw['date_range']

    if not R.user.has_perm('fishuser.view_all_project_in_remote_control_system'):
        #沒有 "在(遠端工程系統)中_觀看_所有_工程案資訊"
        if not 'view_single_project_in_remote_control_system' in get_perms(R.user, project):
            #沒有 觀看此project 的 "在(遠端工程系統)中_觀看_單一_工程案資訊" 權限
            if project.unit != R.user.user_profile.unit:
                return HttpResponseRedirect('/')
        elif 'view_single_project_in_remote_control_system' in get_perms(R.user, project):
            #有 觀看此project 的 "在(遠端工程系統)中_觀看_單一_工程案資訊" 權限
            if not R.user.frcmusergroup_set.get(project=project).is_active:
                #被關閉權限的
                return HttpResponseRedirect('/')
    else:
        if R.user.username[1] == '_' and not R.user.is_staff:
            if project.unit != R.user.user_profile.unit:
                return HttpResponseRedirect('/')

    workingdates_default = engprofile.readWorkingDate()
    if TODAY() < workingdates_default[-1]:
        defined_finish_date = TODAY()
    else:
        defined_finish_date = workingdates_default[-1]

    reports = Report.objects.filter(project=project).order_by('-date')

    if reports:
        if reports[0].date > defined_finish_date:
            defined_finish_date = reports[0].date

    workingdates = engprofile.readWorkingDate(defined_finish_date=defined_finish_date)

    all_month = [[workingdates[0].year, [str(workingdates[0].month).zfill(2)]]]
    for d in workingdates:
        if d.year == all_month[-1][0]:
            if str(d.month).zfill(2) not in all_month[-1][1]:
                all_month[-1][1].append(str(d.month).zfill(2))
        else:
            all_month.append([d.year, [str(d.month).zfill(2)]])

    calendars = []
    week_string = [u'一', u'二', u'三', u'四', u'五', u'六', u'日']

    if date_range == 'first':
        if TODAY() > workingdates[-1]:
            date_range = [str(workingdates[-1].year), str(workingdates[-1].month).zfill(2)]
        else:
            date_range = [str(TODAY().year), str(TODAY().month).zfill(2)]
    elif date_range != 'all':
        date_range = date_range.split('-')

    progress_list = []
    if engprofile.start_date:
        #在workingdates 加一天(下一個月01日)
        if workingdates[-1].month == 12:
            workingdates.append(datetime.datetime.strptime('%s-01-01' % (workingdates[-1].year+1), '%Y-%m-%d'))
        else:
            workingdates.append(datetime.datetime.strptime('%s-%s-01' % (workingdates[-1].year, workingdates[-1].month+1), '%Y-%m-%d'))

        schedule_progress = engprofile.read_schedule_progress() #預定進度列表
        action_progress_i = engprofile.read_action_progress(report_type="inspector") #"監造"實際進度列表
        action_progress_c = engprofile.read_action_progress(report_type="contractor") #"施工"實際進度列表
        
        #整理每年的最後一天進度金額
        year_progress_s = {workingdates[0].year-1: 0} #每年的最後一天"預定"金額
        year_progress_a_i = {workingdates[0].year-1: 0} #每年的最後一天"監造"實際金額
        year_progress_a_c = {workingdates[0].year-1: 0} #每年的最後一天"施工"實際金額
        for n, d in enumerate(workingdates[:-1]):
            if workingdates[n].year != workingdates[n+1].year:
                version = Version.objects.filter(project=project, start_date__lte=d).order_by('-id')[0] # 今天使用的版本
                engs_price = float(str(version.engs_price)) if version.engs_price else 0 # 契約金額
                year_progress_s[workingdates[n].year] = int(schedule_progress[d] * engs_price / 100.)
                year_progress_a_i[workingdates[n].year] = int(action_progress_i[d] * engs_price /100.)
                year_progress_a_c[workingdates[n].year] = int(action_progress_c[d] * engs_price /100.)
        version = Version.objects.filter(project=project).order_by('-start_date')[0] # 最後使用的版本
        engs_price = float(str(version.engs_price)) if version.engs_price else 0 # 契約金額
        year_progress_s[workingdates[-2].year] = int(schedule_progress[workingdates[-2]] * engs_price / 100.)
        year_progress_a_i[workingdates[-2].year] = int(action_progress_i[workingdates[-2]] * engs_price /100.)
        year_progress_a_c[workingdates[-2].year] = int(action_progress_c[workingdates[-2]] * engs_price /100.)

        #整理每個工作天的進度資訊
        for n, d in enumerate(workingdates[:-1]):
            if workingdates[n].month != workingdates[n+1].month:
                if date_range != 'all' and '%s-%s' % (d.year, str(d.month).zfill(2)) != '%s-%s' % (date_range[0], date_range[1]):
                    continue
                version = Version.objects.filter(project=project, start_date__lte=d).order_by('start_date')[0] # 今天使用的版本
                engs_price = float(str(version.engs_price)) if version.engs_price else 0 # 契約金額
                info = {
                        'date': d, #今天的日期
                        's': schedule_progress[d], #預定累積進度
                        's_money': int(schedule_progress[d] * engs_price / 100.), #預定累積金額 = 預定進度 * 預定金額 / 100
                        'c': action_progress_c[d], #實際"監造"累積進度
                        'c_money': int(action_progress_c[d] * engs_price / 100.), #實際"監造"累積金額 = 監造實際進度 * 契約金額 / 100
                        'i': action_progress_i[d], #實際"施工"累積進度
                        'i_money': int(action_progress_i[d] * engs_price / 100.)  #實際"施工"累積金額 = 施工實際進度 * 契約金額 / 100
                        }

                #換算本年度累積金額
                info['this_year_s_money'] = info['s_money'] - year_progress_s[d.year-1]
                info['this_year_i_money'] = info['i_money'] - year_progress_a_i[d.year-1]
                info['this_year_c_money'] = info['c_money'] - year_progress_a_c[d.year-1]

                #換算本年度累積進度
                if (year_progress_s[d.year] - year_progress_s[d.year-1]):
                    info['this_year_s'] = info['this_year_s_money'] * 100. / (year_progress_s[d.year] - year_progress_s[d.year-1])
                    info['this_year_i'] = info['this_year_i_money'] * 100. / (year_progress_s[d.year] - year_progress_s[d.year-1])
                    info['this_year_c'] = info['this_year_c_money'] * 100. / (year_progress_s[d.year] - year_progress_s[d.year-1])
                else:
                    info['this_year_s'] = 0
                    info['this_year_i'] = 0
                    info['this_year_c'] = 0
                progress_list.append(info)

    this_month_progress = []
    diff_date = []
    if date_range != 'all':
        diff_date = [i.report.date for i in ReportItem.objects.filter(report__date__year=int(date_range[0]), report__date__month=int(date_range[1]), report__project=project).exclude(i_num=F('c_num'))]
        diff_date = set(diff_date)

        for n, d in enumerate(workingdates[:-1]):
            if '%s-%s' % (d.year, str(d.month).zfill(2)) == '%s-%s' % (date_range[0], date_range[1]):
                if n == 0:
                    ex_i, ex_c = 0, 0
                else:
                    ex_i, ex_c = action_progress_i[workingdates[n-1]], action_progress_c[workingdates[n-1]]
                this_i, this_c = action_progress_i[d], action_progress_c[d]
                delta_i, delta_c = this_i-ex_i, this_c-ex_c
                if d not in diff_date:
                    delta_i = delta_c
                this_month_progress.append([d, week_string[d.isoweekday()-1], schedule_progress[d], delta_i, this_i, delta_c, this_c])

        

    t = get_template(os.path.join('dailyreport', 'zh-tw', 'information_progress.html'))
    html = t.render(RequestContext(R,{
        'engprofile': engprofile,
        'user_perms': user_perms,
        'all_month': all_month,
        'date_range': date_range,
        'finish_date': workingdates[-2],
        'choose': _make_choose(),
        'progress_list': progress_list,
        'this_month_progress': this_month_progress,
        'diff_date': diff_date,
        'report_type': report_type,
        'toppage_name': u'整合資訊',
        'subpage_name': u'進度資訊列表',
        }))
    return HttpResponse(html)

@login_required
def read_progress_chart(R, **kw):
    # 製造進度圖表
    project = Project.objects.get(id=kw['project_id'])
    report_type = kw.get('report_type', 'contractor')
    engprofile = EngProfile.objects.get(project=project)
    user_perms = get_perms(R.user, engprofile)

    working_dates = engprofile.readWorkingDate()
    should_done_date = working_dates[-1]
    reports = Report.objects.filter(project=project).order_by('-date')
    if reports:
        if reports[0].date > should_done_date:
            should_done_date = reports[0].date

    schedule_progress, change_progress = engprofile.read_schedule_progress_for_s_curve()
    action_progress = engprofile.read_action_progress(report_type=report_type)
    

    start_date = working_dates[0]
    #
    s_money = []
    a_money = []
    date_count = 0
    multi_version_design_percents = []
    multi_version_act_percents = []
    while start_date != should_done_date + datetime.timedelta(1):
        #test
        version = Version.objects.filter(project=project, start_date__lte=working_dates[0]).order_by('-start_date')[0]
        engs_price = float(str(version.engs_price)) if version.engs_price else 0
        #

        if schedule_progress.has_key(start_date):
            if change_progress.has_key(start_date):
                multi_version_design_percents.append(
                    { u'日期': start_date, u'預定累計進度': change_progress[start_date] }
                )
            multi_version_design_percents.append(
                { u'日期': start_date, u'預定累計進度': schedule_progress[start_date] }
            )
        else:
            if not multi_version_design_percents:
                multi_version_design_percents.append(
                    { u'日期': start_date, u'預定累計進度': 0 }
                )

        if action_progress.has_key(start_date):
            try:
                row = reports.get(date=start_date)
                if report_type == 'inspector' and row.inspector_check:
                    has_reported = True
                elif report_type == 'contractor' and row.contractor_check:
                    has_reported = True
                else:
                    has_reported = False
            except:
                has_reported = False
            multi_version_act_percents.append(
                { 'has_reported': has_reported, u'日期': start_date, u'實際累計進度': action_progress[start_date] }
            )
        else:
            if not multi_version_act_percents:
                multi_version_act_percents.append(
                    { 'has_reported': False, u'日期': start_date, u'實際累計進度': 0 }
                )
        start_date += datetime.timedelta(1)
    
    versions = Version.objects.filter(project=project).order_by('start_date')
    if versions.count == 1:
        change_date = []
    else:
        change_date = [v.start_date for v in versions[1:]]

    if engprofile.scheduled_completion_day:
        end_date = engprofile.scheduled_completion_day
    else:
        end_date = engprofile.readWorkingDate(is_scheduled=True)[-1]

    pc = ProgressChart()
    pc.SetEndDate(end_date)
    pc.SetStartDate(engprofile.start_date)
    pc.SetDaytype(engprofile.date_type.value)
    pc.SetItem((multi_version_design_percents, multi_version_act_percents, working_dates, change_date, engs_price))
    pc.NewChart()
    pc.DrawDayAxis()
    pc.DrawPercentAxis()
    pc.DrawX()
    pc.DrawStartDate()
    pc.DrawEndDate()
    pc.DrawDaytype()

    if engprofile.date_type.value == '限期完工(日曆天每日施工)':
        pc.SetDeadline(engprofile.deadline)
        pc.DrawDeadline()
    else:
        schedule_items = engprofile.readLatestVersion().scheduleitem_set.filter(kind=ITEMKIND).order_by('-ef')
        if schedule_items:
            ef = schedule_items[0].ef
        else:
            ef = 1
        pc.SetDuration(engprofile.duration, ef)
        pc.DrawDuration()

    pc.DrawTitle()

    from cStringIO import StringIO
    buffer = StringIO()
    pc.SaveChart(buffer)
    png = buffer.getvalue()
    buffer.close()

    return HttpResponse(png, content_type='image/png')


@login_required
def update_engprofile(R):
    # 用來更新基本資料

    engprofile = EngProfile.objects.get(id=R.POST["engprofile_id"])


    if not 'edit_engprofile' in get_perms(R.user, engprofile) and not R.user.has_perm(u'dailyreport.edit_engprofile'):
        return HttpResponse(json.dumps({'status': False, 'msg': u'您沒有權限!!'}))

    engprofile.start_date = R.POST["start_date"]
    date_type = Option.objects.get(swarm="date_type", value=R.POST["date_type"])
    engprofile.date_type = date_type
    engprofile.duration = R.POST["duration"] if R.POST["duration"] else 0
    if int(engprofile.duration) > 2000:
        return HttpResponse(json.dumps({'status': False, 'msg': u'您輸入的工期天數有誤，請確認工期資訊!!'}))
    engprofile.deadline = R.POST["deadline"] if R.POST["deadline"] else None
    engprofile.scheduled_completion_day = R.POST["scheduled_completion_day"] if R.POST["scheduled_completion_day"] else None
    if R.POST.get("contractor_lock", ""):
        engprofile.contractor_lock = True if R.POST["contractor_lock"] == 'lock' else False
    if R.POST.get("contractor_read_inspectorReport", ""):
        engprofile.contractor_read_inspectorReport = False if R.POST["contractor_read_inspectorReport"] == 'lock' else True

    engprofile.inspector_name = R.POST["inspector_name"]
    engprofile.contractor_name = R.POST["contractor_name"]
    engprofile.schedule_progress = R.POST["schedule_progress"]
    engprofile.save()

    #休息日不能存在日報表填報紀錄
    workingdates = EngProfile.objects.get(id=engprofile.id).readWorkingDate()
    for report in Report.objects.filter(project=engprofile.project):
        if report.date not in workingdates:
            reportholiday = ReportHoliday(
                project = report.project,
                date = report.date,
                morning_weather = report.morning_weather,
                afternoon_weather = report.afternoon_weather,
                describe_subcontractor=report.describe_subcontractor,
                sampling=report.sampling,
                notify=report.notify,
                note=report.note,
                c_describe_subcontractor=report.c_describe_subcontractor,
                c_sampling=report.c_sampling,
                c_notify=report.c_notify,
                c_note=report.c_note,
            )
            reportholiday.save()
            report.delete()
        engprofile.save()

    version = engprofile.readFirstVersion()
    version = engprofile.readLatestVersion()
    version.start_date = engprofile.start_date
    version.save()

    return HttpResponse(json.dumps({'status': True}))


@login_required
def update_priority(R):
    # 調整item or schedule_item的序位
    table_name = R.POST['table_name']
    row_id = R.POST['row_id']
    direction = R.POST['direction']

    if table_name == 'item':
        row = Item.objects.get(id=row_id)
        before_item = Item.objects.filter(uplevel=row.uplevel, priority__lt=row.priority).order_by('-priority')
        uplevel_after_item = Item.objects.filter(uplevel=row.uplevel.uplevel, priority__gt=row.uplevel.priority).order_by('priority')
        after_item = Item.objects.filter(uplevel=row.uplevel, priority__gte=row.priority).order_by('priority')
        last_row = Item.objects.filter(uplevel=row.uplevel).order_by('-priority')[0]
    elif table_name == 'scheduleitem':
        row = ScheduleItem.objects.get(id=row_id)
        before_item = ScheduleItem.objects.filter(uplevel=row.uplevel, priority__lt=row.priority).order_by('-priority')
        uplevel_after_item = ScheduleItem.objects.filter(uplevel=row.uplevel.uplevel, priority__gt=row.uplevel.priority).order_by('priority')
        after_item = ScheduleItem.objects.filter(uplevel=row.uplevel, priority__gte=row.priority).order_by('priority')
        last_row = ScheduleItem.objects.filter(uplevel=row.uplevel).order_by('-priority')[0]

    if row.priority == 0 and direction == 'up':
        return HttpResponse(json.dumps({'status': False, 'msg': '已經為第1序位，無法再向上移動'}))
    elif last_row == row and direction == 'down':
        return HttpResponse(json.dumps({'status': False, 'msg': '已經為最後序位，無法再向下移動'}))
    elif not row.uplevel.uplevel and direction == 'outdent':
        return HttpResponse(json.dumps({'status': False, 'msg': '已經高階層，無法再向前凸排'}))
    elif direction == 'indent':
        if not before_item.filter(kind=DIRKIND):
            return HttpResponse(json.dumps({'status': False, 'msg': '同階層無資料夾工項，無法再向後縮排'}))

    if direction == 'up':
        if table_name == 'item':
            target_row = Item.objects.filter(uplevel=row.uplevel, priority__lt=row.priority).order_by('-priority')[0]
        elif table_name == 'scheduleitem':
            target_row = ScheduleItem.objects.filter(uplevel=row.uplevel, priority__lt=row.priority).order_by('-priority')[0]
        tmp = target_row.priority
        target_row.priority = row.priority
        target_row.save()
        row.priority = tmp
        row.save()
    elif direction == 'down':
        if table_name == 'item':
            target_row = Item.objects.filter(uplevel=row.uplevel, priority__gt=row.priority).order_by('priority')[0]
        elif table_name == 'scheduleitem':
            target_row = ScheduleItem.objects.filter(uplevel=row.uplevel, priority__gt=row.priority).order_by('priority')[0]
        tmp = target_row.priority
        target_row.priority = row.priority
        target_row.save()
        row.priority = tmp
        row.save()
        while target_row.kind == DIRKIND and target_row.read_last_item().priority != -1:
            if table_name == 'item':
                target_row = Item.objects.filter(uplevel=target_row).order_by('-priority')[0]
            elif table_name == 'scheduleitem':
                target_row = ScheduleItem.objects.filter(uplevel=target_row).order_by('-priority')[0]
    elif direction == 'outdent':
        target_row = row.uplevel
        row.priority = row.uplevel.priority + 1
        row.uplevel = row.uplevel.uplevel
        for i in uplevel_after_item:
            i.priority += 1
            i.save()
        for i in after_item:
            i.priority -= 1
            i.save()
        row.save()

        while target_row.kind == DIRKIND and target_row.read_last_item().priority != -1:
            if table_name == 'item':
                target_row = Item.objects.filter(uplevel=target_row).order_by('-priority')[0]
            elif table_name == 'scheduleitem':
                target_row = ScheduleItem.objects.filter(uplevel=target_row).order_by('-priority')[0]
    elif direction == 'indent':
        for i in before_item:
            if i.kind == DIRKIND:
                target_row = i
                break
        row.priority = target_row.read_last_item().priority + 1
        next_target = target_row.read_last_item()
        row.uplevel = target_row
        for i in after_item:
            i.priority -= 1
            i.save()
        row.save()

        while next_target.kind == DIRKIND and next_target.read_last_item().priority != -1:
            if table_name == 'item':
                next_target = Item.objects.filter(uplevel=next_target).order_by('-priority')[0]
            elif table_name == 'scheduleitem':
                next_target = ScheduleItem.objects.filter(uplevel=next_target).order_by('-priority')[0]
        target_row = next_target

    deep_sub_item = row.read_deep_sub_item_in_list()
    deep_sub_item.pop(0)

    return HttpResponse(json.dumps({'status': True, 'target_id': target_row.id, 'sub_item_ids': '_'.join([str(i.id) for i in deep_sub_item]) }))


@login_required
def create_item(R):
    # 新增item or schedule_item項目
    table_name = R.POST['table_name']
    row_id = R.POST['row_id']
    level = R.POST['level']

    if table_name == 'item':
        row = Item.objects.get(id=row_id)
        new_row = Item()
        t = get_template(os.path.join('dailyreport', 'zh-tw', 'tr_item.html'))
    elif table_name == 'scheduleitem':
        row = ScheduleItem.objects.get(id=row_id)
        new_row = ScheduleItem()
        t = get_template(os.path.join('dailyreport', 'zh-tw', 'tr_schedule_item.html'))

    engprofile = EngProfile.objects.get(project=row.version.project)
    new_row.unit_name = u'式'
    new_row.unit_num = '1'
    new_row.unit_price = '0'
    new_row.es = 1
    new_row.ef = 1
    new_row.version = row.version

    random_num = int(random.random() * 100000)

    if level == 'same_dir':
        target_row = row.uplevel
        new_row.uplevel = target_row
        new_row.name = u'請輸入『新資料夾』名稱，系統隨機碼：' + str(random_num)
        new_row.kind = DIRKIND
        new_row.priority = target_row.read_last_item().priority + 1

    elif level == 'sub_dir':
        target_row = row
        new_row.uplevel = target_row
        new_row.name = u'請輸入『新資料夾』名稱，系統隨機碼：' + str(random_num)
        new_row.kind = DIRKIND
        new_row.priority = target_row.read_last_item().priority + 1

    elif level == 'item':
        if row.kind == DIRKIND:
            target_row = row
        else:
            target_row = row.uplevel
        new_row.uplevel = target_row
        new_row.name = u'請輸入『新工項』名稱，系統隨機碼：' + str(random_num)
        new_row.kind = ITEMKIND
        new_row.unit_name = u'---'
        new_row.unit_num = '0'
        new_row.priority = target_row.read_last_item().priority + 1
        target_row = target_row.read_last_item() if target_row.read_last_item().priority != -1 else target_row
    new_row.save()

    #加入這個版本有填寫日報表天數的紀錄
    if level == 'item' and table_name == 'item':
        if row.version.read_next_version():
            end_day = row.version.read_next_version().start_date
        else:
            end_day = TODAY() + datetime.timedelta(1)
        reports = Report.objects.filter(project=row.version.project, date__gte=row.version.start_date, date__lt=end_day)
        for r in reports:
            report_item = ReportItem(
                report = r,
                item = new_row,
                i_num = 0,
                c_num = 0,
                i_sum_num = 0,
                c_sum_num = 0
                )
            report_item.save()

    #找到我要插入的位置
    if table_name == 'item':
        nr = new_row.priority
        while Item.objects.filter(uplevel=target_row, priority__lt=nr).order_by('-priority'):
            target_row = Item.objects.filter(uplevel=target_row, priority__lt=nr).order_by('-priority')[0]
            nr = 500

    elif table_name == 'scheduleitem':
        nr = new_row.priority
        while ScheduleItem.objects.filter(uplevel=target_row, priority__lt=nr).order_by('-priority'):
            target_row = ScheduleItem.objects.filter(uplevel=target_row, priority__lt=nr).order_by('-priority')[0]
            nr = 500

    html = t.render(RequestContext(R,{
            'engprofile': engprofile,
            'edit': True,
            'item': new_row,
        }))

    return HttpResponse(json.dumps({'status': True, 'target_id': target_row.id, 'html': html, 'new_row_id': new_row.id}))


@login_required
def create_extension(R):
    row = Extension(
        project=Project.objects.get(id=R.POST.get('project_id', '')),
        day=R.POST.get('day', ''),
        no=R.POST.get('no', ''),
        date=R.POST.get('date', ''),
        memo=R.POST.get('memo', ''),
        )
    row.save()

    return HttpResponse(json.dumps({'status': True}))


@login_required
def create_item_by_pcces(R):
    file = R.FILES.get('file', None)
    project_id = R.POST.get('project_id', None)
    project = Project.objects.get(id=project_id)
    if file:
        try:
            version = Version.objects.get(project=project)
        except:
            return HttpResponse(json.dumps({'status': False, 'msg': '只有初始版本才可以使用匯入PCCES方法'}))
        if Item.objects.filter(version=version).count() != 1:
            return HttpResponse(json.dumps({'status': False, 'msg': '必須只有初始項目才能匯入PCCES，請刪除自行新增的所有工項'}))

        pcces_file = ''.join([str(chunk) for chunk in file.chunks()])
        pp = ParsePCCES(pcces_file, project, version)
        if pp.Parse():
            return HttpResponse(json.dumps({'status': True}))

    return HttpResponse(json.dumps({'status': False}))

DIRKIND = Option.objects.get(swarm='item_kind', value='目錄')
ITEMKIND = Option.objects.get(swarm='item_kind', value='工項')
@login_required
def create_item_by_csv(R):
    file = R.FILES.get('file', None)
    project_id = R.POST.get('project_id', None)
    project = Project.objects.get(id=project_id)
    if file:
        try:
            version = Version.objects.get(project=project)
        except:
            return HttpResponse(json.dumps({'status': False, 'msg': '只有初始版本才可以使用匯入CSV方法'}))
        if Item.objects.filter(version=version).count() != 1:
            return HttpResponse(json.dumps({'status': False, 'msg': '必須只有初始項目才能匯入CSV，請刪除自行新增的所有工項'}))

        csv_file = ''.join([str(chunk) for chunk in file.chunks()])
        data = csv.reader(file)
        root_item = Item.objects.get(version=version, uplevel=None)
        up_level_item = root_item
        first_item_priority = 0
        second_item_priority = 0
        for row in list(data)[2:]:
            new_row = Item(
                version = version,
                unit_num = float(row[3].replace(',', '')) if row[3] else 0,
                unit_price = float(row[4].replace(',', '')) if row[4] else 0,
                )
            try: new_row.name = row[1].decode("cp950").encode("utf8")
            except: new_row.name = u'X-------(注意特殊編碼，無法解析，請自行輸入)-------X'
            try: new_row.unit_name = row[2].decode("cp950").encode("utf8")
            except: new_row.unit_name = u'-------注意特殊編碼-------'
            try: new_row.memo = row[5].decode("cp950").encode("utf8")
            except: new_row.memo = u'-------注意特殊編碼，無法解析，請自行輸入-------'
            if '*' in row[0]:
                new_row.kind = DIRKIND
                new_row.uplevel = root_item
                new_row.pre_item = None
                new_row.priority = first_item_priority
                new_row.save()
                up_level_item = new_row
                first_item_priority += 1
                second_item_priority = 0
            else:
                new_row.kind = ITEMKIND
                new_row.uplevel = up_level_item
                new_row.pre_item = None
                new_row.priority = second_item_priority
                new_row.save()
                second_item_priority += 1

        return HttpResponse(json.dumps({'status': True}))

    return HttpResponse(json.dumps({'status': False}))


@login_required
def update_report_page(R):
    engprofile = EngProfile.objects.get(project__id=R.POST["project_id"])
    project = engprofile.project
    report_type = R.POST["report_type"]
    report_date = R.POST["report_date"]
    report_date = datetime.datetime.strptime(report_date, "%Y-%m-%d").date()
    version = Version.objects.filter(project=project, start_date__lte=report_date).order_by('-start_date')[0]
    user_perms = get_perms(R.user, engprofile)

    if report_type == 'inspector':
        if not 'view_inspector_report' in user_perms and not R.user.has_perm(u'dailyreport.view_inspector_report'):
            return HttpResponse(json.dumps({'status': False, 'msg': u'您沒有權限!!'}))
        elif 'edit_contractor_report' in user_perms and not engprofile.contractor_read_inspectorReport and not R.user.is_staff:
            return HttpResponse(json.dumps({'status': False, 'msg': u'目前設定，施工廠商無法觀看監造報表!!'}))
    else:
        if not 'view_contractor_report' in user_perms and not R.user.has_perm(u'dailyreport.view_contractor_report'):
            return HttpResponse(json.dumps({'status': False, 'msg': u'您沒有權限!!'}))
    
    try:
        #看看當天有沒有填寫過
        report = Report.objects.get(project=project, date=report_date)
        report_items = report.reportitem_set.all().prefetch_related('report', 'item')
        report.has_report = True
    except:
        report = Report(id=-1, date=report_date, i_sum_money=0, c_sum_money=0)
        report_items = []
        report.has_report = False
    
    # workingdates = engprofile.readWorkingDate()
    # workingdates_for_today = engprofile.readWorkingDate(defined_finish_date=TODAY())
    # if report_date not in workingdates_for_today:
    #     return HttpResponse(json.dumps({'status': False, 'msg': u'今天因為『工期計算方式』或『停工/強制開工設定』，今日停工無法填寫(不計工期)！'}))

    # version = Version.objects.filter(project=project, start_date__lte=report_date).order_by('-start_date')[0]

    #是否可以編輯
    edit_test_record = True
    if report_type == 'inspector' and R.user.has_perm('dailyreport.edit_inspector_report'):
        edit = True
    elif report_type == 'contractor' and R.user.has_perm('dailyreport.edit_contractor_report'):
        edit = True
    elif report_type == 'inspector' and 'edit_inspector_report' in user_perms:
        if not R.user.frcmusergroup_set.get(project=project).is_active:
            edit = False
            edit_test_record = False
        else:
            edit = True
    elif report_type == 'contractor' and 'edit_contractor_report' in user_perms:
        if not R.user.frcmusergroup_set.get(project=project).is_active or report.lock_c:
            edit = False
            edit_test_record = False
        else:
            edit = True
    else:
        edit = False
        edit_test_record = False

    if report.lock_c:
        edit = False

    version = Version.objects.filter(project=project, start_date__lte=report_date).order_by('-start_date')[0]
    if not version.update_time:
        version.update_time = NOW()
        version.save()
    update_time = str(version.update_time)[:19].replace(' ', '-').replace(':', '-')
    report_template_version_id = '%s-%s-%s-%s-%s' % (project.id, version.id, report_type, 'edit' if edit else 'not_edit', update_time)
    url = '?template_version=%s&project_id=%s&version_id=%s&report_type=%s&edit=%s&update_time=%s' % (1.12, project.id, version.id, report_type, 'edit' if edit else 'not_edit', update_time)
    return HttpResponse(json.dumps({'status': True, 'edit': edit, 'url': url, 'report_template_version_id': report_template_version_id}))


@login_required
def get_report_template(R):
    engprofile = EngProfile.objects.get(project__id=R.GET["project_id"])
    project = engprofile.project
    report_type = R.GET["report_type"]
    user_perms = get_perms(R.user, engprofile)
    
    workingdates = engprofile.readWorkingDate()
    workingdates_for_today = engprofile.readWorkingDate(defined_finish_date=TODAY())

    #是否可以編輯
    edit = R.GET['edit'] == 'edit'
    version = Version.objects.get(id=R.GET['version_id'])
    if not version.update_time:
        version.update_time = NOW()
        version.save()
    update_time = str(version.update_time)[:19].replace(' ', '-').replace(':', '-')
    report_template_version_id = '%s-%s-%s-%s-%s' % (project.id, version.id, report_type, 'edit' if edit else 'not_edit', update_time)

    file_path = os.path.join(settings.ROOT, 'apps', 'dailyreport', 'temp_files', 'report_templates')
    if not os.path.exists(file_path): os.makedirs(file_path)

    file_path = os.path.join(file_path, str(project.id))
    if not os.path.exists(file_path): os.makedirs(file_path)

    file_list = os.listdir(file_path)
    for file_name in file_list:
        if '%s-%s-%s-%s' % (project.id, version.id, report_type, 'edit' if edit else 'not_edit') in file_name and file_name != report_template_version_id:
            os.remove(os.path.join(file_path, file_name))
    file_path = os.path.join(file_path, '%s.txt' % report_template_version_id)
    if os.path.exists(file_path):
        txt_file = open(file_path, 'r')
        raw = txt_file.read()
        txt_file.close()

        response = HttpResponse(raw, content_type="text/html")
        response['Cache-Control'] = 'private, max-age=31556926'
        return response

    root_item = version.item_set.get(uplevel=None)
    items = root_item.read_deep_sub_item_in_list()
    

    t = get_template(os.path.join('dailyreport', 'zh-tw', 'report_day.html'))
    html = t.render(RequestContext(R,{
            'edit': edit,
            'engprofile': engprofile,
            'version': version,
            'user_perms': user_perms,
            'choose': _make_choose(),
            'items': items,
            'report_type': report_type,
        }))

    txt_file = open(file_path, "w")
    txt_file.write(html)
    txt_file.close()
    txt_file = open(file_path, "r")
    raw = txt_file.read()
    txt_file.close()

    response = HttpResponse(raw, content_type="text/html")
    response['Cache-Control'] = 'private, max-age=31556926'
    return response


@login_required
def get_report_data(R):
    engprofile = EngProfile.objects.get(project__id=R.POST["project_id"])
    project = engprofile.project
    report_type = R.POST["report_type"]
    report_date = R.POST["report_date"]
    report_date = datetime.datetime.strptime(report_date, "%Y-%m-%d").date()
    user_perms = get_perms(R.user, engprofile)

    try:
        #看看當天有沒有填寫過
        report = Report.objects.get(project=project, date=report_date)
        report_items = report.reportitem_set.all().prefetch_related('report', 'item')
        report.has_report = True
        if report_type == 'inspector' and report.inspector_check:
            have_delete_button = True
        elif report_type == 'contractor' and report.contractor_check:
            have_delete_button = True
        else:
            have_delete_button = False
    except:
        try:
            report = ReportHoliday.objects.get(project=project, date=report_date)
            report.i_sum_money=0
            report.c_sum_money=0
        except:
            report = Report(id=-1, date=report_date, i_sum_money=0, c_sum_money=0)
        report_items = []
        report.lock_c = False
        report.has_report = False
        have_delete_button = False
    #是否可以編輯
    if R.user.has_perm('dailyreport.edit_inspector_report'): have_lock_button = True
    else: have_lock_button = False
    if report_type == 'inspector' and R.user.has_perm('dailyreport.edit_inspector_report'):
        edit = True
    elif report_type == 'contractor' and R.user.has_perm('dailyreport.edit_contractor_report'):
        edit = True
    elif report_type == 'inspector' and 'edit_inspector_report' in user_perms:
        if not R.user.frcmusergroup_set.get(project=project).is_active:
            edit = False
        else:
            edit = True
    elif report_type == 'contractor' and 'edit_contractor_report' in user_perms:
        if not R.user.frcmusergroup_set.get(project=project).is_active or report.lock_c:
            edit = False
        else:
            edit = True
    else:
        edit = False

    if report.lock_c:
        edit = False

    workingdates = engprofile.readWorkingDate()
    workingdates_for_today = engprofile.readWorkingDate(defined_finish_date=TODAY())
    version = Version.objects.filter(project=project, start_date__lte=report_date).order_by('-start_date')[0]

    item_data = []
    if report_date not in workingdates_for_today:
        is_special_day = True
        try:
            #看看休息日當天有沒有填寫過
            report = ReportHoliday.objects.get(project=project, date=report_date)
            report.has_report = True
        except:
            report = Report(id=-1, date=report_date)
            report.has_report = False

    else:
        is_special_day = False
        #item部分
        root_item = version.item_set.get(uplevel=None)
        items = root_item.read_deep_sub_item_in_list()
        item_data = []

        for item in items:
            if item.kind == DIRKIND: continue
            if report.has_report:
                #表示當天有填寫紀錄
                if report_items.filter(item=item):
                    report_item = report_items.get(item=item)
                else:
                    #如果沒有這個工項，則補作(不應該沒有，只是做保險)
                    report_item = ReportItem(
                        report = report,
                        item = item
                    )
                    report_item.save()
                if report_type == 'inspector':
                    item.num = report_item.i_num
                    item.another_num = report_item.c_num
                    item.note = report_item.i_note
                else:
                    item.num = report_item.c_num
                    item.another_num = report_item.i_num
                    item.note = report_item.c_note
            else:
                #當天沒有填寫紀錄
                item.num = 0
                item.another_num = 0
                item.note = ''
                
            item_data.append([item.id, float(str(item.num)) if item.num else '', float(str(item.another_num)) if item.another_num else '', 0, 0, item.note])

    #基本資料部分
    engprofile.extension = sum([i.day for i in engprofile.project.dailyreport_extension.filter(date__lte=report_date)])
    max_day = max(workingdates)
    if report.date > max_day:
        used_duration = workingdates.index(max_day) + 1 + int((report.date - max_day).days)
    else:
        dd = report_date
        while dd not in workingdates and dd >= engprofile.start_date:
            dd -= datetime.timedelta(1)
        if dd < engprofile.start_date:
            used_duration = 0
        else:
            used_duration = workingdates.index(dd) + 1

    if engprofile.date_type.value == '限期完工(日曆天每日施工)':
        duration = u'%s ( + 展延 %s 天)' % (engprofile.deadline, engprofile.extension)
        # unused_duration = (engprofile.deadline - engprofile.start_date).days + sum([i.day for i in project.dailyreport_extension.all()]) - used_duration
    else:
        duration = u'<span id="duration">%s</span> 天 ( + 展延 %s 天)' % (engprofile.duration, engprofile.extension)
        # unused_duration = engprofile.duration + sum([i.day for i in project.dailyreport_extension.all()]) - used_duration

    unused_duration = len(engprofile.readWorkingDate(is_scheduled=True)) - sum([i.day for i in Extension.objects.filter(project=project, date__gt=report.date)]) - used_duration
    special_dates_data = ''
    special_dates = SpecialDate.objects.filter(project=project, start_date__lte=report_date).order_by('start_date')
    for day in special_dates:
        day.days = (day.end_date - day.start_date).days + 1
        special_dates_data += '<li>%s - 期間：%s ~ %s(共%s天) - 原因：%s</li>' % (day.type.value, day.start_date, day.end_date, day.days, day.reason)
        
    if Extension.objects.filter(project=project, date__lte=report_date):
        extensions = Extension.objects.filter(project=project, date__lte=report_date).order_by('date')
        for n_d, day in enumerate(extensions):
            special_dates_data += '<li>%s 第%s次展延 - 天數：%s天 - 備註：%s</li>' % (day.date, n_d+1, day.day, day.memo)

    profile_data = {
        'is_special_day': is_special_day,
        'report_id': report.id,
        'morning_weather': [report.morning_weather.id, report.morning_weather.value] if report.has_report else [20, u'晴天'],
        'afternoon_weather': [report.afternoon_weather.id, report.afternoon_weather.value] if report.has_report else [20, u'晴天'],
        'duration': duration,
        'unused_duration': unused_duration,
        'used_duration': used_duration,
        'engs_price': float(str(version.engs_price)),
        'special_dates_data': special_dates_data,
        'has_professional_item': True if hasattr(report, 'has_professional_item') and report.has_professional_item else False,
        'pre_education': True if hasattr(report, 'pre_education') and report.pre_education else False,
        'safety_equipment': True if hasattr(report, 'safety_equipment') and report.safety_equipment else False,
        'pre_check': True if hasattr(report, 'pre_check') and report.pre_check else False,
        'has_insurance': report.has_insurance if hasattr(report, 'has_insurance') else False,
        'describe_subcontractor': report.describe_subcontractor if report_type=='inspector' else report.c_describe_subcontractor,
        'another_describe_subcontractor': report.c_describe_subcontractor if report_type=='inspector' else report.describe_subcontractor,
        'note': report.note if report_type=='inspector' else report.c_note,
        'another_note': report.c_note if report_type=='inspector' else report.note,
        'sampling': report.sampling if report_type=='inspector' else report.c_sampling,
        'another_sampling': report.c_sampling if report_type=='inspector' else report.sampling,
        'notify': report.notify if report_type=='inspector' else report.c_notify,
        'another_notify': report.c_notify if report_type=='inspector' else report.notify,
        'i_pre_check': report.i_pre_check if hasattr(report, 'i_pre_check') and report.i_pre_check else '',
        'i_project_status': report.i_project_status if hasattr(report, 'i_project_status') and report.i_project_status else '',
    }

    #人員部分
    labors = LaborEquip.objects.filter(project=project, type__swarm='labor_or_equip', type__value=u'人員').order_by('sort')
    labor_data = ''
    for labor in labors:
        try:
            report_labor_equip = ReportLaborEquip.objects.get(report=report, type=labor)
            labor.num = report_labor_equip.num
        except:
            labor.num = 0
        labor.sum_num = sum([rle.num for rle in ReportLaborEquip.objects.filter(report__date__lte=report.date, type=labor)])
        if not labor.sum_num: labor.sum_num = 0
        t = get_template(os.path.join('dailyreport', 'zh-tw', 'tr_report_labor.html'))
        html = t.render(RequestContext(R,{
                'edit': edit,
                'user_perms': user_perms,
                'labor': labor,
            }))
        labor_data += html

    #機具部分
    equips = LaborEquip.objects.filter(project=project, type__swarm='labor_or_equip', type__value=u'機具').order_by('sort')
    equip_data = ''
    for equip in equips:
        try:
            report_labor_equip = ReportLaborEquip.objects.get(report=report, type=equip)
            equip.num = report_labor_equip.num
        except:
            equip.num = 0
        equip.sum_num = sum([rle.num for rle in ReportLaborEquip.objects.filter(report__date__lte=report.date, type=equip)])
        if not equip.sum_num: equip.sum_num = 0
        t = get_template(os.path.join('dailyreport', 'zh-tw', 'tr_report_equip.html'))
        html = t.render(RequestContext(R,{
                'edit': edit,
                'user_perms': user_perms,
                'equip': equip,
            }))
        equip_data += html

    #工地材料部分
    sitematerial_data = ''
    try:
        for n, site_material in enumerate(SiteMaterial.objects.filter(report=report)):
            t = get_template(os.path.join('dailyreport', 'zh-tw', 'tr_site_material.html'))
            html = t.render(RequestContext(R,{
                    'n': n+1,
                    'edit': edit,
                    'site_material': site_material,
                }))
            sitematerial_data += html
    except: pass
    
    return HttpResponse(json.dumps({
        'profile_data': profile_data,
        'item_data': item_data,
        'labor_data': labor_data,
        'equip_data': equip_data,
        'sitematerial_data': sitematerial_data,
        'edit': edit,
        'lock_c': True if hasattr(report, 'lock_c') and report.lock_c else False,
        'have_lock_button': have_lock_button,
        'have_delete_button': have_delete_button,
        }))


@login_required
def get_item_sum(R):
    report_date = R.POST.get('report_date', '')
    report_type = R.POST.get('report_type', '')
    item_id = R.POST.get('item_id', '')
    item = Item.objects.get(id=item_id)
    if report_type == 'inspector':
        pre_sum = sum([i.i_num for i in ReportItem.objects.filter(item__in=item.read_brother_items(), report__date__lt=report_date).exclude(i_num='0')])
    else:
        pre_sum = sum([i.c_num for i in ReportItem.objects.filter(item__in=item.read_brother_items(), report__date__lt=report_date).exclude(c_num='0')])

    return HttpResponse(json.dumps({'pre_sum': str(round(pre_sum, 5))}))


@login_required
def get_all_item_sum(R):
    report_date = R.POST.get('report_date', '')
    report_type = R.POST.get('report_type', '')
    project_id = R.POST.get('project_id', '')
    version = Version.objects.filter(project__id=project_id, start_date__lte=report_date).order_by('-start_date')[0]
    items = version.item_set.all().exclude(kind=DIRKIND)

    report_items = ReportItem.objects.filter(report__date__lt=report_date)
    items_sum = []
    for item in items:
        if report_type == 'inspector':
            pre_sum = sum([i.i_num for i in report_items.filter(item__in=item.read_brother_items(), report__date__lt=report_date).exclude(i_num='0')])
        else:
            pre_sum = sum([i.c_num for i in report_items.filter(item__in=item.read_brother_items(), report__date__lt=report_date).exclude(c_num='0')])
        items_sum.append([item.id, str(round(pre_sum, 5))])

    return HttpResponse(json.dumps({'items_sum': items_sum}))

    
@login_required
def update_report_page_progress(R):
    engprofile = EngProfile.objects.get(project__id=R.POST["project_id"])
    project = engprofile.project
    report_type = R.POST["report_type"]
    report_date = R.POST["report_date"]
    report_date = datetime.datetime.strptime(report_date, "%Y-%m-%d").date()
    user_perms = get_perms(R.user, engprofile)

    try:
        #看看當天有沒有填寫過
        report = Report.objects.get(project=project, date=report_date)
        report_items = report.reportitem_set.all().prefetch_related('report', 'item')
        report.has_report = True
    except:
        report = Report(id=-1, date=report_date, i_sum_money=0, c_sum_money=0)
        report_items = []
        report.has_report = False
    
    workingdates = engprofile.readWorkingDate()
    workingdates_for_today = engprofile.readWorkingDate(defined_finish_date=TODAY())

    version = Version.objects.filter(project=project, start_date__lte=report_date).order_by('-start_date')[0]

    root_item = version.item_set.get(uplevel=None)
    root_item_dir_price = root_item.read_dir_price_by_roundkind()
    #engs_price為契約金額計算出現問題時使用
   
    engs_price = float(version.engs_price)
    if engs_price != 0 and engs_price != root_item.read_dir_price_by_roundkind():
        root_item_dir_price = engs_price
    else:
        root_item_dir_price = root_item.read_dir_price_by_roundkind()
   

    #計算本日完成、累計完成、預定累計完成
    pre_reports = Report.objects.filter(project=project, date__lte=report_date).order_by('-date')
    if not report_items and pre_reports: report_items = pre_reports[0].reportitem_set.all().prefetch_related('report', 'item')
    if report_type == 'inspector':
        if root_item_dir_price == 0:
            report.money = 0
            report.today_money = 0
            report.today_progress_rate = 0
            report.sum_money = 0
            report.sum_progress_rate = 0
        else:
            report.money = sum([i.i_sum_money for i in Report.objects.filter(project=project, date__gte=version.start_date, date__lte=report_date)])
            report.today_money = float(str(report.i_sum_money))
            report.today_progress_rate = round(float(str(report.i_sum_money)) / root_item_dir_price * 100., 3)
            report.sum_money = report.money + version.pre_i_money
            report.sum_progress_rate = round(float(str(report.money + version.pre_i_money)) / root_item_dir_price * 100., 3)
    else:
        if root_item_dir_price == 0:
            report.money = 0
            report.today_money = 0
            report.today_progress_rate = 0
            report.sum_money = 0
            report.sum_progress_rate = 0
        else:
            report.money = sum([i.c_sum_money for i in Report.objects.filter(project=project, date__gte=version.start_date, date__lte=report_date)])
            report.today_money = float(str(report.c_sum_money))
            report.today_progress_rate = round(float(str(report.c_sum_money)) / root_item_dir_price * 100., 3)
            report.sum_money = report.money + version.pre_c_money
            report.sum_progress_rate = round(float(str(report.money + version.pre_c_money)) / root_item_dir_price * 100., 3) 

    schedule_progress_list = engprofile.read_schedule_progress()
    try:
        report.design_percent = schedule_progress_list[report_date]
    except:
        max_date = max([sp for sp in schedule_progress_list])
        if report_date >= max_date:
            report.design_percent = schedule_progress_list[max_date]
        else:
            dd = report_date - datetime.timedelta(1)
            while dd not in workingdates and dd >= engprofile.start_date:
                dd -= datetime.timedelta(1)
            if dd < engprofile.start_date:
                report.design_percent = 0
            else:
                report.design_percent = schedule_progress_list[dd]

    report.design_money = report.design_percent * root_item_dir_price / 100.

    #更新基本資料頁面的進度
    engprofile.read__design__c__i__percent()

    return HttpResponse(json.dumps({
        'design_percent': report.design_percent, 
        'sum_progress_rate': report.sum_progress_rate, 
        'today_progress_rate': report.today_progress_rate,
        'design_money': int(report.design_money), 
        'sum_progress_money': int(report.sum_money), 
        'today_progress_money': int(report.today_money),
    }))


@login_required
def update_report_data(R):
    morning_weather = R.POST['morning_weather']
    afternoon_weather = R.POST['afternoon_weather']
    cut_row_code = R.POST['cut_row_code']
    cut_value_code = R.POST['cut_value_code']
    project_id = R.POST['project_id']
    report_type = R.POST['report_type']
    report_date = R.POST['report_date']
    report_date = datetime.datetime.strptime(report_date, "%Y-%m-%d").date()
    info = R.POST['info'].split(cut_row_code)
    labor_info = R.POST['labor_info'].split(cut_row_code)
    equip_info = R.POST['equip_info'].split(cut_row_code)
    describe_subcontractor = R.POST['describe_subcontractor']
    sampling = R.POST['sampling']
    notify = R.POST['notify']
    note = R.POST['note']
    i_pre_check = R.POST.get('i_pre_check', '')
    i_project_status = R.POST.get('i_project_status', '')
    has_professional_item = R.POST.get('has_professional_item', False)
    has_insurance = R.POST.get('has_insurance', 3)
    pre_education = R.POST.get('pre_education', 'False')
    safety_equipment = R.POST.get('safety_equipment', 'False')
    pre_check = R.POST.get('pre_check', 'False')
    is_special_day = R.POST.get('is_special_day', False)

    project = Project.objects.get(id=project_id)
    engprofile = EngProfile.objects.get(project=project)
    workingdates_for_today = engprofile.readWorkingDate(defined_finish_date=TODAY())
    if is_special_day:
        try:
            report = ReportHoliday.objects.get(project=project, date=report_date)
        except:
            report = ReportHoliday(
                project = project,
                date = report_date,
                )
        report.morning_weather = Option.objects.get(id=morning_weather)
        report.afternoon_weather = Option.objects.get(id=afternoon_weather)
        if report_type == 'inspector':
            report.describe_subcontractor = describe_subcontractor
            report.sampling = sampling
            report.notify = notify
            report.note = note
            report.pre_check = True if pre_check and pre_check == 'True' else False
            report.i_pre_check = i_pre_check
            report.i_project_status = i_project_status
        else:
            report.c_describe_subcontractor = describe_subcontractor
            report.c_sampling = sampling
            report.c_notify = notify
            report.c_note = note
            report.has_professional_item = True if has_professional_item == 'True' else False
            report.has_insurance = has_insurance
            report.pre_education = True if pre_education == 'True' else False
            report.safety_equipment = True if safety_equipment == 'True' else False

        report.save()
        return HttpResponse(json.dumps({'status': True, 'report_id': report.id}))
    # if report_date not in workingdates_for_today:
    #     return HttpResponse(json.dumps({'status': False, 'msg': u'本日為停工無法填寫!!!'}))

    try:
        report = Report.objects.get(project=project, date=report_date)
    except:
        report = Report(
            project = project,
            date = report_date,
            )
    report.morning_weather = Option.objects.get(id=morning_weather)
    report.afternoon_weather = Option.objects.get(id=afternoon_weather)
    if report_type == 'inspector':
        report.inspector_check = True
    elif report_type == 'contractor':
        report.contractor_check = True

    report.update_time = NOW()
    report.i_sum_money = 0
    report.c_sum_money = 0

    if report_type == 'inspector':
        report.describe_subcontractor = describe_subcontractor
        report.sampling = sampling
        report.notify = notify
        report.note = note
        report.pre_check = True if pre_check and pre_check == 'True' else False
        report.i_pre_check = i_pre_check
        report.i_project_status = i_project_status
    else:
        report.c_describe_subcontractor = describe_subcontractor
        report.c_sampling = sampling
        report.c_notify = notify
        report.c_note = note
        report.has_professional_item = True if has_professional_item == 'True' else False
        report.has_insurance = has_insurance
        report.pre_education = True if pre_education == 'True' else False
        report.safety_equipment = True if safety_equipment == 'True' else False

    report.save()

    for row in info:
        tmp = row.split(cut_value_code)
        try:
            id, num, note = tmp[0], tmp[1], tmp[2]
            item = Item.objects.get(id=id)
        except:
            continue
        try:
            num = float(str(num))
        except:
            num = 0
            
        if report.reportitem_set.filter(item=item):
            report_item = report.reportitem_set.get(item=item)
        else:
            report_item = report.reportitem_set.get_or_create(item=item)
            report_item = report.reportitem_set.get(item=item)

        if report_type == 'inspector':
            report_item.i_num = num
            report_item.i_note = note
            
        elif report_type == 'contractor':
            report_item.c_num = num
            report_item.c_note = note

        report_item.save()

    #調整version 的 pre_money
    version = Version.objects.filter(project=project, start_date__lte=report_date).order_by('-start_date')[0]
    after_versions = Version.objects.filter(project=project, start_date__gt=version.start_date)
    for av in after_versions:
        items = Item.objects.filter(version=av, kind__value=u'工項')
        pre_i_money = decimal.Decimal('0')
        pre_c_money = decimal.Decimal('0')
        for i in items:
            report_items = ReportItem.objects.filter(item__in=i.read_brother_items(), report__date__lt=av.start_date)
            pre_i_money += sum([j.i_num for j in report_items.exclude(i_num='0')]) * i.unit_price
            pre_c_money += sum([j.c_num for j in report_items.exclude(c_num='0')]) * i.unit_price
        av.pre_i_money = pre_i_money
        av.pre_c_money = pre_c_money
        av.save()

    for le in labor_info + equip_info:
        tmp = le.split(cut_value_code)
        try:
            id, num = tmp[0], tmp[1]
            laborequip = LaborEquip.objects.get(id=id)
        except:
            continue
        try:
            num = float(str(num))
        except:
            num = 0
        try:
            row = ReportLaborEquip.objects.get(report=report, type=laborequip)
            if num == 0:
                row.delete()
            else:
                row.num = num
                row.save()
        except:
            if num != 0:
                row = ReportLaborEquip(
                        report=report,
                        type=laborequip,
                        num = num
                    )
                row.save()

    engprofile.save()
    report.update_sum_money()

    return HttpResponse(json.dumps({'status': True, 'report_id': report.id}))


@login_required
def create_labor_or_equip(R):
    type = R.POST['type']
    name = R.POST['name']
    project_id = R.POST['project_id']
    project = Project.objects.get(id=project_id)
    engprofile = EngProfile.objects.get(project=project)
    user_perms = get_perms(R.user, engprofile)
    if type == 'labor':
        type = Option.objects.get(swarm="labor_or_equip", value=u"人員")
    else:
        type = Option.objects.get(swarm="labor_or_equip", value=u"機具")

    if LaborEquip.objects.filter(type=type, project=project, value=name):
        return HttpResponse(json.dumps({'status': False, 'msg': u'已有此種類名稱，不可重複新增'}))
        
    row = LaborEquip(
        project = project,
        type = type,
        value = name,
        sort = LaborEquip.objects.filter(project=project, type=type).count() + 1
        )
    row.save()
    row.sum_num = 0

    if not row.is_first():
        up_id = LaborEquip.objects.get(project=project, type=type, sort=row.sort-1).id
    else:
        up_id = None
        
    if R.POST['type'] == 'labor':
        t = get_template(os.path.join('dailyreport', 'zh-tw', 'tr_report_labor.html'))
        html = t.render(RequestContext(R,{
                'edit': True,
                'user_perms': user_perms,
                'labor': row
            }))
    else:
        t = get_template(os.path.join('dailyreport', 'zh-tw', 'tr_report_equip.html'))
        html = t.render(RequestContext(R,{
                'edit': True,
                'user_perms': user_perms,
                'equip': row
            }))
    return HttpResponse(json.dumps({'status': True, 'html': html, 'row_id': row.id, 'up_id': up_id}))


@login_required
def create_special_date(R):
    type = Option.objects.get(id=R.POST['type_id'])
    start_date = R.POST['start_date']
    end_date = R.POST['end_date']
    begin_date = R.POST['begin_date']
    no = R.POST['no']
    reason = R.POST['reason']
    project = Project.objects.get(id=R.POST['project_id'])
    row = SpecialDate(
            project = project,
            start_date = start_date,
            end_date = end_date,
            type = type,
            reason = reason,
            no = no,
            begin_date = begin_date
        )
    row.save()

    engprofile = EngProfile.objects.get(project=project)
    user_perms = get_perms(R.user, engprofile)
    #休息日不能存在日報表填報紀錄
    if type.value not in [u'強制開工']:
        for report in Report.objects.filter(project=project, date__gte=start_date, date__lte=end_date):
            reportholiday = ReportHoliday(
                project = report.project,
                date = report.date,
                morning_weather = report.morning_weather,
                afternoon_weather = report.afternoon_weather,
                describe_subcontractor=report.describe_subcontractor,
                sampling=report.sampling,
                notify=report.notify,
                note=report.note,
                c_describe_subcontractor=report.c_describe_subcontractor,
                c_sampling=report.c_sampling,
                c_notify=report.c_notify,
                c_note=report.c_note,
                i_project_status = report.i_project_status,
                pre_education = report.pre_education,
                has_insurance = report.has_insurance,
                safety_equipment = report.safety_equipment,
                pre_check = report.pre_check,
                i_pre_check =report.i_pre_check,
            )
            reportholiday.save()
            report.delete()
    t = get_template(os.path.join('dailyreport', 'zh-tw', 'tr_special_date.html'))
    html = t.render(RequestContext(R,{
            'user_perms': user_perms,
            'sd': row,
            'edit': True,
        }))
    return HttpResponse(json.dumps({'status': True, 'html': html}))


@login_required
def create_site_material(R):
    report = Report.objects.get(id=R.POST.get('report_id', ''))
    row = SiteMaterial(
        report = report
        )
    row.save()

    t = get_template(os.path.join('dailyreport', 'zh-tw', 'tr_site_material.html'))
    html = t.render(RequestContext(R,{
            'edit': True,
            'site_material': row
        }))
    return HttpResponse(json.dumps({'status': True, 'html': html}))


@login_required
def create_test_record(R):
    testtype = TestType.objects.get(id=R.POST.get('testtype', ''))
    engprofile = EngProfile.objects.get(project=testtype.project)
    row = TestRecord(
        testtype = testtype,
        record_name = R.POST.get('record_name', ''),
        type = R.POST.get('type', ''),
        record_date = R.POST.get('record_date', ''),
        qualified = True if R.POST.get('qualified', '') == 'True' else False,
        qualified_date = R.POST.get('qualified_date', '') if R.POST.get('qualified_date', '') else None,
        record_memo = R.POST.get('record_memo', ''),
        )
    row.save()

    t = get_template(os.path.join('dailyreport', 'zh-tw', 'tr_testrecord.html'))
    html = t.render(RequestContext(R,{
            'edit': True,
            'r': row,
            'engprofile': engprofile
        }))
    return HttpResponse(json.dumps({'status': True, 'row_id': row.id, 'html': html}))

