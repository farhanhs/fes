# -*- coding: utf-8 -*-
import requests

from django import forms
from django.db.models import Q, Count
# from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.contrib.contenttypes.models import ContentType
from django.contrib.sessions.models import Session
from django.core.cache import cache
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.forms import ModelForm
from django.http import HttpResponse, HttpResponseRedirect
from django.template.loader import get_template
from django.template import Context, RequestContext

from fishuser.models import Option
from fishuser.models import UserProfile
from fishuser.models import LoginHistory
from fishuser.models import WrongLogin
from fishuser.models import DocumentOfProjectModels
from fishuser.models import Plan
from fishuser.models import PlanBudget
from fishuser.models import Project
from fishuser.models import Project_Port
from fishuser.models import Draft_Project
from fishuser.models import DefaultProject
from fishuser.models import FRCMUserGroup
from fishuser.models import Factory
from fishuser.models import Reserve
from fishuser.models import FundRecord
from fishuser.models import Fund
from fishuser.models import BudgetProject
from fishuser.models import Appropriate
from fishuser.models import Allocation
from fishuser.models import Progress
from fishuser.models import ScheduledProgress
from fishuser.models import ProjectPhoto
from fishuser.models import FRCMTempFile
from fishuser.models import _getProjectStatusInList
from fishuser.models import _ca
from fishuser.models import Budget
from fishuser.models import CountyChaseTime
from fishuser.models import CountyChaseProjectOneByOne
from fishuser.models import CountyChaseProjectOneToMany
from fishuser.models import CountyChaseProjectOneToManyPayout
from fishuser.views import login_required, checkAuthority
from pccmating.models import Project as PCCProject
from pccmating.models import ProjectProgress as PCCProgress

from project.models import Option2
from project.models import RecordProjectProfile
from project.models import ExportCustomReport
from project.models import ReportField
from project.models import ExportCustomReportField

from harbor.models import FishingPort
from harbor.models import Aquaculture

from dailyreport.models import Version
from dailyreport.models import EngProfile

from pccmating.models import Project as PCC_Project

from supervise.models import SuperviseCase
from supervise.models import Error

from general.models import Place, Unit, FishCityMenuManager, UNITS, LOAD_UNITS

from common.models import Log
from common.lib import find_sub_level, find_sub, nocache_response, md5password, readDATA, verifyOK, makePageList, makeFileByWordExcel

from frcm.models import CityFiles, ProjectFile, WarningCheck, WarningProject, NoImportProject, WarningMailList
from frcm.models import Option as FRCM_Option

import smtplib
from email import encoders
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.utils import COMMASPACE, formatdate

from django.conf import settings
NUMPERPAGE = settings.NUMPERPAGE
ROOT = settings.ROOT
import os, random, json, decimal, re, datetime, calendar, math

if not hasattr(json, "write"):
    #for python2.6
    json.write = json.dumps
    json.read = json.loads
 
from math import ceil

from guardian.shortcuts import assign
from guardian.shortcuts import remove_perm
from guardian.shortcuts import get_perms


TODAY = lambda: datetime.date.today()
NOW = lambda: datetime.datetime.now()
TAIWAN = Place.objects.get(name=u'臺灣地區')
places = [TAIWAN] + list(Place.objects.filter(uplevel=TAIWAN).order_by('id'))
years = [y-1911 for y in xrange(2008, TODAY().year+4)]
years.reverse()
this_year = TODAY().year - 1911
units = LOAD_UNITS()[:]

#轉移開始------------------------------------------------------------------

def _make_choose():
    options = Option.objects.all().order_by('id')
    chooses = {}
    for i in options:
        if chooses.has_key(i.swarm):
            chooses[i.swarm].append(i)
        else:
            chooses[i.swarm] = [i]
    return chooses


def _make_choose_frcm():
    options = FRCM_Option.objects.all().order_by('id')
    chooses = {}
    for i in options:
        if chooses.has_key(i.swarm):
            chooses[i.swarm].append(i)
        else:
            chooses[i.swarm] = [i]
    return chooses


#我的工程
@login_required
def my_project(R):
    
    user = R.user
    if not user.has_perm('fishuser.sub_menu_remote_control_system_my'):
        return HttpResponseRedirect('/')

    projects = [p.project for p in FRCMUserGroup.objects.filter(project__deleter=None, user=user)]
    countychasetime = CountyChaseTime.objects.all().order_by('-id')[0]
    have_print_button_self = False
    have_print_button_all = False
    working_projects = []
    finish_projects = []
    for p in projects:
        p.plan__name__list = u''.join([u'●%s' % i.plan.name for i in Budget.objects.filter(fund__project=p, plan__isnull=False)])
        p.usergroup = FRCMUserGroup.objects.get(user=user, project=p).group.name
        p.open = FRCMUserGroup.objects.get(user=user, project=p).is_active
        p.message = u'帳號關閉中'

        try:
            p.chase_data = countychasetime.countychaseprojectonetomany_set.get(project=p)
        except: pass

        try:
            ono = p.countychaseprojectonebyone_set.get()
            if p.purchase_type.value == u'一般勞務' and ono.act_ser_acceptance_closed <= TODAY():
                finish_projects.append(p)
            elif p.purchase_type.value in [u'工程', u'工程勞務'] and ono.act_eng_do_closed <= TODAY():
                finish_projects.append(p)
            else:
                working_projects.append(p)
        except:
            working_projects.append(p)

    t = get_template(os.path.join('frcm', 'zh-tw', 'my_project.html'))
    html = t.render(RequestContext(R,{
            'user': R.user,
            'projects': working_projects,
            'finish_projects': finish_projects,
            'toppage_name': u'遠端管理系統',
            'subpage_name': u'我的工程',
        }))
    return HttpResponse(html)

    
#工程案基本資料
@login_required
def project_profile(R, **kw):
    row = Project.objects.get(id=kw['project_id'])
    if not R.user.has_perm('fishuser.view_all_project_in_remote_control_system'):
        #沒有 "在(遠端工程系統)中_觀看_所有_工程案資訊"
        if not 'view_single_project_in_remote_control_system' in get_perms(R.user, row):
            #沒有 觀看此project 的 "在(遠端工程系統)中_觀看_單一_工程案資訊" 權限
            return HttpResponseRedirect('/')
        elif 'view_single_project_in_remote_control_system' in get_perms(R.user, row):
            #有 觀看此project 的 "在(遠端工程系統)中_觀看_單一_工程案資訊" 權限
            if not R.user.frcmusergroup_set.get(project=row).is_active:
                #被關閉權限的
                return HttpResponseRedirect('/')

    else:
        #有 "在(遠端工程系統)中_觀看_所有_工程案資訊"
        if not R.user.has_perm('fishuser.view_all_project_in_management_system'):
            #縣市政府人員
            new_units = []
            u_name = R.user.user_profile.unit.name[:3]
            for u in units:
                if u_name in u.name:
                    new_units.append(u)
            if row.unit not in new_units and not R.user.is_staff and not 'view_single_project_in_remote_control_system' in get_perms(R.user, row):
                #不是自己單位的工程
                return HttpResponseRedirect('/')

    if R.user.has_perm('fishuser.edit_all_project_in_management_system'):
        #管考人員
        edit = True #編輯資料權限
    elif 'edit_single_project_in_remote_control_system' in get_perms(R.user, row):
        edit = True
    else:
        edit = False

    if FRCMUserGroup.objects.filter(project=row, user=R.user) or R.user.is_staff:
        edit_supervise = True
    else:
        edit_supervise = False

    user = R.user
    project = row
    try:
        project.your_identity = FRCMUserGroup.objects.get(user=R.user, project=project)
    except:
        project.your_identity = u'瀏覽者'
        
    if not project.inspector_code: project.create_i_code()
    if not project.contractor_code: project.create_c_code()

    project.engineers = [u for u in FRCMUserGroup.objects.filter(project=project).exclude(group__name=u'監造廠商').exclude(group__name=u'營造廠商').order_by('id')]
    project.inspectors = [u for u in FRCMUserGroup.objects.filter(group__name=u'監造廠商', project=project)]
    project.contractors = [u for u in FRCMUserGroup.objects.filter(group__name=u'營造廠商', project=project)]
    project.engs = [u for u in FRCMUserGroup.objects.filter(project=project, group__name__in=[u'負責主辦工程師', u'協同主辦工程師', u'自辦主辦工程師'])]
    project.identity = user.user_profile.rIdentity(project.id)
    fund = Fund.objects.get(project=project)
    budgets = fund.budget_set.all().order_by('priority')
    duration_type = Option.objects.filter(swarm=u'duration_type').order_by('id')
    inspector_type = Option.objects.filter(swarm=u'inspector_type').order_by('id')

    chase_one_by_one = project.countychaseprojectonebyone_set.get()
    countychasetime = CountyChaseTime.objects.all().order_by('-id').first()
    try:
        chase_data = CountyChaseProjectOneToMany.objects.get(countychasetime=countychasetime, project=project)
    except:
        chase_data = False
        
    allocations = Allocation.objects.filter(project=project).order_by('date')

    try:
        engprofile = project.dailyreport_engprofile.get()
        if not engprofile.start_date:
            engprofile = None

        engprofile.months = []
        working_dates = engprofile.readWorkingDate()
        for n, d in enumerate(working_dates[:-1]):
            if d > TODAY(): break
            if d.month != working_dates[n+1].month:
                engprofile.months.append(d)
        if engprofile.months and engprofile.months[-1].month != working_dates[-1].month:
            engprofile.months.append(working_dates[-1])
        elif not engprofile.months and working_dates:
            engprofile.months.append(working_dates[-1])
    except:
        engprofile = None

    t = get_template(os.path.join('frcm', 'zh-tw', 'project_profile.html'))
    html = t.render(RequestContext(R,{
            'user': R.user,
            'project': project,
            'engprofile': engprofile,
            'edit': edit,
            'edit_supervise': edit_supervise,
            'places': places,
            'option' : _make_choose(),
            'fund': fund,
            'budgets': budgets,
            'allocations': allocations,
            'chase_data': chase_data,
            'chase_one_by_one': chase_one_by_one,
            'toppage_name': u'遠端管理系統',
        }))
    return HttpResponse(html)


#工程案 縣市進度追蹤
@login_required
def project_chase(R, **kw):
    row = Project.objects.get(id=kw['project_id'])
    if not R.user.has_perm('fishuser.view_all_project_in_remote_control_system'):
        #沒有 "在(遠端工程系統)中_觀看_所有_工程案資訊"
        if not 'view_single_project_in_remote_control_system' in get_perms(R.user, row):
            #沒有 觀看此project 的 "在(遠端工程系統)中_觀看_單一_工程案資訊" 權限
            return HttpResponseRedirect('/')
        elif 'view_single_project_in_remote_control_system' in get_perms(R.user, row):
            #有 觀看此project 的 "在(遠端工程系統)中_觀看_單一_工程案資訊" 權限
            if not R.user.frcmusergroup_set.get(project=row).is_active:
                #被關閉權限的
                return HttpResponseRedirect('/')

    else:
        #有 "在(遠端工程系統)中_觀看_所有_工程案資訊"
        if not R.user.has_perm('fishuser.view_all_project_in_management_system'):
            #縣市政府人員
            new_units = []
            u_name = R.user.user_profile.unit.name[:3]
            for u in units:
                if u_name in u.name:
                    new_units.append(u)
            if row.unit not in new_units and not R.user.is_staff and not 'view_single_project_in_remote_control_system' in get_perms(R.user, row):
                #不是自己單位的工程
                return HttpResponseRedirect('/')

    if R.user.has_perm('fishuser.edit_all_project_in_management_system'):
        #管考人員
        edit = True #編輯資料權限
    elif 'edit_single_project_in_remote_control_system' in get_perms(R.user, row):
        edit = True
    else:
        edit = False

    user = R.user
    project = row
    fund = Fund.objects.get(project=project)
    budgets = fund.budget_set.all().order_by('priority')
    
    chase_one_by_one = project.countychaseprojectonebyone_set.get()
    countychasetime = CountyChaseTime.objects.all().order_by('-id').first()
    chase_data = CountyChaseProjectOneToMany.objects.get(countychasetime=countychasetime, project=project)
    chase_data.pastDay = (datetime.date.today() - countychasetime.chase_date).days
    chase_data.dead_line = countychasetime.chase_date.replace(day=calendar.monthrange(countychasetime.chase_date.year, countychasetime.chase_date.month)[1])
    chase_data.dead_line += datetime.timedelta(days=6)
    try:
        last_chase_data = CountyChaseProjectOneToMany.objects.filter(project=project, complete=True).exclude(countychasetime=countychasetime).order_by('-countychasetime__id').first()
    except: last_chase_data = False

    for b in budgets:
        try:
            b.capital_ratify_use = CountyChaseProjectOneToManyPayout.objects.get(chase=chase_data, budget=b).self_payout
        except:
            b.capital_ratify_use = 0

    t = get_template(os.path.join('frcm', 'zh-tw', 'project_chase.html'))
    html = t.render(RequestContext(R,{
            'user': R.user,
            'project': project,
            'edit': edit,
            'option' : _make_choose(),
            'fund': fund,
            'budgets': budgets,
            'chase_data': chase_data,
            'last_chase_data': last_chase_data,
            'chase_one_by_one': chase_one_by_one,
            'toppage_name': u'遠端管理系統',
        }))
    return HttpResponse(html)



@login_required
def file_upload_project(R, **kw):
    row = Project.objects.get(id=kw['project_id'])
    page = kw['page']
    if not R.user.has_perm('fishuser.view_all_project_in_remote_control_system'):
        #沒有 "在(遠端工程系統)中_觀看_所有_工程案資訊"
        if not 'view_single_project_in_remote_control_system' in get_perms(R.user, row):
            #沒有 觀看此project 的 "在(遠端工程系統)中_觀看_單一_工程案資訊" 權限
            return HttpResponseRedirect('/')
        elif 'view_single_project_in_remote_control_system' in get_perms(R.user, row):
            #有 觀看此project 的 "在(遠端工程系統)中_觀看_單一_工程案資訊" 權限
            if not R.user.frcmusergroup_set.get(project=row).is_active:
                #被關閉權限的
                return HttpResponseRedirect('/')

    else:
        #有 "在(遠端工程系統)中_觀看_所有_工程案資訊"
        if not R.user.has_perm('fishuser.view_all_project_in_management_system'):
            #縣市政府人員
            new_units = []
            u_name = R.user.user_profile.unit.name[:3]
            for u in units:
                if u_name in u.name:
                    new_units.append(u)
            if row.unit not in new_units and not R.user.is_staff and not 'view_single_project_in_remote_control_system' in get_perms(R.user, row):
                #不是自己單位的工程
                return HttpResponseRedirect('/')

    if R.user.has_perm('fishuser.edit_all_project_in_management_system'):
        #管考人員
        edit = True #編輯資料權限
    elif FRCMUserGroup.objects.filter(user=R.user, is_active=True):
        edit = True
    else:
        edit = False

    user = R.user
    if page == "base":
        tags = FRCM_Option.objects.filter(swarm="project_file_tag").order_by('id')
        for t in tags:
            t.num = ProjectFile.objects.filter(project=row, tag=t).count()
        menu_tab = u"工程基本資料"
        files = ProjectFile.objects.filter(project=row, file_type__swarm="file_type_tag", file_type__value=u"工程基本資料").order_by('name', 'upload_time')

    elif page == "inspector":
        tags = FRCM_Option.objects.filter(swarm="inspector_file_tag").order_by('id')
        for t in tags:
            t.num = ProjectFile.objects.filter(project=row, tag=t).count()
        menu_tab = u"監造資料"
        files = ProjectFile.objects.filter(project=row, file_type__swarm="file_type_tag", file_type__value=u"監造資料").order_by('name', 'upload_time')
    
    t = get_template(os.path.join('frcm', 'zh-tw', 'fileupload_base.html'))
    html = t.render(RequestContext(R,{
        'user': R.user,
        'row': row,
        'files': files,
        'tags': tags,
        'edit': edit,
        'toppage_name': u'遠端管理系統',
        'menu_tab': menu_tab
        }))
    return HttpResponse(html)


#列印功程會資料頁面
@login_required
def print_pcc_information(R, **kw):
    row = PCCProject.objects.get(uid=kw['uid'])
    t = get_template(os.path.join('frcm', 'zh-tw', 'print_pcc_information.html'))
    html = t.render(RequestContext(R,{
            'user': R.user,
            'row': row,
            'toppage_name': u'遠端管理系統',
        }))
    return HttpResponse(html)



#廠商認領工程案
@login_required
def claim_project(R):
    if not R.user.has_perm('fishuser.sub_menu_remote_control_system_claim'):
        return HttpResponseRedirect('/')

    i_group = Group.objects.get(name=u'監造廠商')
    c_group = Group.objects.get(name=u'營造廠商')

    t = get_template(os.path.join('frcm', 'zh-tw', 'claim_project.html'))
    html = t.render(RequestContext(R,{
            'user': R.user,
            'today': TODAY(),
            'option': _make_choose(),
            'toppage_name': u'遠端管理系統',
            'subpage_name': u'認領工程',
            'i_group': i_group,
            'c_group': c_group,
        }))
    return HttpResponse(html)


#搜尋工程案
@login_required
def search_project(R):
    if not R.user.has_perm('fishuser.sub_menu_remote_control_system_search'):
        # 沒有 "第二層選單_遠端管理系統_搜尋工程"
        return HttpResponseRedirect('/')

    if R.user.has_perm('fishuser.view_all_project_in_management_system'):
        new_units = units
    else:
        # 沒有 "在(遠端工程系統)中_觀看_所有_工程案資訊"
        new_units = []
        u_name = R.user.user_profile.unit.name[:3]
        for u in units:
            if u_name in u.name:
                new_units.append(u)

    top_plan = Plan.objects.get(uplevel=None)
    # plans = [top_plan] + top_plan.rSubPlanInList()
    pp=[top_plan]
    sub_plans1 = Plan.objects.filter(uplevel=top_plan.id)
    sub_plans1 = sorted(sub_plans1, key=lambda sub_plans1: -sub_plans1.year)
    for p1 in sub_plans1:  
        pp.append(p1) 

    for i in pp:
        i.name = i.rLevelNumber() * u'　' + u'● ' + i.name

    fishing_ports = FishingPort.objects.all().order_by('place', 'name')
    aquacultures = Aquaculture.objects.all().order_by('place', 'name')
    reports = ExportCustomReport.objects.filter(owner=R.user)
    field_tags = Option2.objects.all().order_by('id')
    for t in field_tags:
        t.fields = t.reportfield_set.all().order_by('id')

    t = get_template(os.path.join('frcm', 'zh-tw', 'search_project.html'))
    html = t.render(RequestContext(R,{
        'user': R.user,
        'years': years,
        'this_year': this_year,
        'plans': pp,
        'reports': reports,
        'field_tags': field_tags,
        'fishing_ports': fishing_ports,
        'aquacultures': aquacultures,
        'option': _make_choose(),
        'places': places,
        'units': new_units,
        'toppage_name': u'遠端管理系統',
        'subpage_name': u'搜尋遠端工程',
        }))
    return HttpResponse(html)


#搜尋工程案
@login_required
def chase_projects(R):
    if not R.user.has_perm('fishuser.sub_menu_remote_control_system_search'):
        # 沒有 "第二層選單_遠端管理系統_搜尋工程"
        return HttpResponseRedirect('/')

    if R.user.has_perm('fishuser.view_all_project_in_management_system'):
        new_units = units
    else:
        # 沒有 "在(遠端工程系統)中_觀看_所有_工程案資訊"
        new_units = []
        u_name = R.user.user_profile.unit.name[:3]
        for u in units:
            if u_name in u.name:
                new_units.append(u)

    user_unit = R.user.user_profile.unit
    if not R.GET.get('unit_id', ''):
        unit = new_units[0]
    else:
        unit = Unit.objects.get(id=R.GET.get('unit_id', ''))
        if unit not in new_units:
            return HttpResponseRedirect('/')

    chase = CountyChaseTime.objects.all().order_by('-id').first()
    chase_datas = CountyChaseProjectOneToMany.objects.filter(project__unit=unit, countychasetime=chase).order_by('project__year', 'project__name')
    
    for c in chase_datas:
        project = c.project
        obo = CountyChaseProjectOneByOne.objects.get(project=project)
        if project.purchase_type.value in [u'工程', u'工程勞務'] and obo.act_eng_do_closed:
            c.is_close = True
        elif project.purchase_type.value in [u'一般勞務'] and obo.act_ser_acceptance_closed:
            c.is_close = True
        else:
            c.is_close = False
        try: 
            c.importer = project.frcmusergroup_set.get(group__name__in=[u'負責主辦工程師', u'自辦主辦工程師']).user.user_profile.rName()
        except: 
            c.importer = ''

    t = get_template(os.path.join('frcm', 'zh-tw', 'chase_projects.html'))
    html = t.render(RequestContext(R,{
        'user': R.user,
        'chase': chase,
        'unit': unit,
        'chase_datas': chase_datas,
        'option': _make_choose(),
        'units': new_units,
        'toppage_name': u'遠端管理系統',
        'subpage_name': u'縣市進度追蹤工程',
        }))
    return HttpResponse(html)


#工程師匯入工程案
@login_required
def import_project(R):
    if not R.user.has_perm('fishuser.sub_menu_remote_control_system_import'):
        # 沒有 "第二層選單_遠端管理系統_匯入工程"
        return HttpResponseRedirect('/')

    if not R.user.has_perm('fishuser.view_all_project_in_remote_control_system'):
        # 沒有 "在(遠端工程系統)中_觀看_所有_工程案資訊"
        new_units = []
        if not R.user.user_profile.unit:
            return HttpResponseRedirect('/')
        u_name = R.user.user_profile.unit.name[:3]
        for u in units:
            if u_name in u.name:
                new_units.append(u)
    else:
        new_units = units

    top_plan = Plan.objects.get(uplevel=None)
    #plans = [top_plan] + top_plan.rSubPlanInList()
    pp=[top_plan]
    sub_plans1 = Plan.objects.filter(uplevel=top_plan.id)
    sub_plans1 = sorted(sub_plans1, key=lambda sub_plans1: -sub_plans1.year)
    for p1 in sub_plans1:  
        pp.append(p1) 

    for i in pp:
        i.name = i.rLevelNumber() * '　' + '● ' + i.name

    fishing_ports = FishingPort.objects.all().order_by('place', 'name')
    aquacultures = Aquaculture.objects.all().order_by('place', 'name')
    responsible = Group.objects.get(name=u'負責主辦工程師')
    collaborative = Group.objects.get(name=u'協同主辦工程師')

    t = get_template(os.path.join('frcm', 'zh-tw', 'import_project.html'))
    html = t.render(RequestContext(R,{
        'user': R.user,
        'years': years,
        'today': TODAY(),
        'this_year': this_year,
        'plans': pp,
        'responsible': responsible,
        'collaborative': collaborative,
        'fishing_ports': fishing_ports,
        'aquacultures': aquacultures,
        'option': _make_choose(),
        'places': places,
        'units': new_units,
        'toppage_name': u'遠端管理系統',
        'subpage_name': u'匯入工程',
        }))
    return HttpResponse(html)


#工程提案區
@login_required
def draft_project(R):
    if not R.user.has_perm('fishuser.sub_menu_remote_control_system_proposal'):
        # 沒有 "第二層選單_遠端管理系統_工程提案區"
        return HttpResponseRedirect('/')

    if not R.user.has_perm('fishuser.view_all_project_in_remote_control_system'):
        # 沒有 "在(遠端工程系統)中_觀看_所有_工程案資訊"
        new_units = []
        u_name = R.user.user_profile.unit.name[:3]
        for u in units:
            if u_name in u.name:
                new_units.append(u)
        draft_projects = Draft_Project.objects.filter(unit__in=new_units, type__value=u"縣市提案草稿").order_by('place', 'sort')
    else:
        new_units = units
        draft_projects = Draft_Project.objects.filter(type__value=u"縣市提案草稿").order_by('place', 'sort')

    for p in draft_projects:
        p.place_dp_num = Draft_Project.objects.filter(type__value=u"縣市提案草稿", place=p.place).count()

    fishing_ports = FishingPort.objects.all().order_by('place', 'name')
    aquacultures = Aquaculture.objects.all().order_by('place', 'name')

    t = get_template(os.path.join('frcm', 'zh-tw', 'draft_project.html'))
    html = t.render(RequestContext(R,{
        'user': R.user,
        'years': years,
        'fishing_ports': fishing_ports,
        'aquacultures': aquacultures,
        'today': TODAY(),
        'this_year': this_year,
        'draft_projects': draft_projects,
        'option': _make_choose(),
        'places': places,
        'units': new_units,
        'toppage_name': u'遠端管理系統',
        'subpage_name': u'工程提案區',
        }))
    return HttpResponse(html)


#編輯工程提案資料
@login_required
def draft_project_profile(R, **kw):
    if not R.user.has_perm('fishuser.sub_menu_remote_control_system_proposal'):
        # 沒有 "第二層選單_遠端管理系統_工程提案區"
        return HttpResponseRedirect('/')

    draft_project = Draft_Project.objects.get(id=kw['draft_project_id'])
    if not R.user.has_perm('fishuser.view_all_project_in_remote_control_system'):
        # 沒有 "在(遠端工程系統)中_觀看_所有_工程案資訊"
        new_units = []
        u_name = R.user.user_profile.unit.name[:3]
        for u in units:
            if u_name in u.name:
                new_units.append(u)
        if draft_project.unit not in new_units:
            return HttpResponseRedirect('/frcm/draft_project/')
    else:
        new_units = units

    fishing_ports = FishingPort.objects.all().order_by('place', 'name')
    aquacultures = Aquaculture.objects.all().order_by('place', 'name')

    t = get_template(os.path.join('frcm', 'zh-tw', 'draft_project_profile.html'))
    html = t.render(RequestContext(R,{
        'user': R.user,
        'years': years,
        'fishing_ports': fishing_ports,
        'aquacultures': aquacultures,
        'today': TODAY(),
        'this_year': this_year,
        'p': draft_project,
        'option': _make_choose(),
        'places': places,
        'units': new_units,
        'toppage_name': u'遠端管理系統',
        'subpage_name': u'工程提案區',
        }))
    return HttpResponse(html)


#檔案管理
@login_required
def file_upload(R, **kw):
    if not R.user.has_perm('fishuser.sub_menu_remote_control_system_file'):
        # 沒有 "第二層選單_遠端管理系統_工程提案區"
        return HttpResponseRedirect('/')

    user_place = R.user.user_profile.unit.place
    if R.user.username[1] == '_':
        new_places = [user_place]
    else:
        new_places = places

    for p in new_places:
        p.files = CityFiles.objects.filter(place=p).order_by('-upload_date')
        for f in p.files:
            if f.upload_user == R.user or R.user.has_perm('fishuser.view_all_project_in_remote_control_system'):
                f.edit = True

    t = get_template(os.path.join('frcm', 'zh-tw', 'file_upload.html'))
    html = t.render(RequestContext(R,{
        'user': R.user,
        'years': years,
        'places': new_places,
        'toppage_name': u'遠端管理系統',
        'subpage_name': u'檔案管理',
        }))
    return HttpResponse(html)


#下載檔案專用
@login_required
def download_file(R, **kw):
    table_name = kw['table_name'] 
    file_id = kw['file_id']

    if table_name == 'CityFiles':
        row = CityFiles.objects.get(id=kw["file_id"])
        ext = row.rExt()
    elif table_name == 'ProjectFile':
        row = ProjectFile.objects.get(id=kw["file_id"])
        ext = row.ext

    f = open(row.file.path, 'rb')
    content = f.read()
    response = HttpResponse(content_type='application/' + ext)
    response['Content-Type'] = ('application/' + ext)
    file_name = row.name.replace(" ", "") + '.' + ext
    response['Content-Disposition'] = ('attachment; filename='+ file_name).encode('utf-8', 'replace')
    response.write(content)
    return response


#上傳檔案的處理
@login_required
def new_file_upload(R):
    data = R.POST

    place_id = data.get('place_id', '')
    table_name = data['table_name']

    f = R.FILES.get('file', None)
    full_name = f.name.split(".")
    ext = full_name[-1]
    full_name.remove(full_name[-1])
    name = "".join(full_name)
    html = ''

    if table_name == 'CityFiles':
        place = Place.objects.get(id=place_id)
        new = CityFiles(
            name = name,
            place = place,
            upload_user = R.user,
            upload_date = TODAY()
        )
        new.save()
        getattr(new, 'file').save('%s.%s'%(new.id, ext), f)
        new.save()

    elif table_name == 'ProjectFile':
        tags = []
        file_type = data.get('file_type', '')
        row_id = data.get('row_id', '')

        if file_type == u'工程基本資料':
            tags = FRCM_Option.objects.filter(swarm="project_file_tag").order_by('id')
        elif file_type == u'監造資料':
            tags = FRCM_Option.objects.filter(swarm="inspector_file_tag").order_by('id')

        project = Project.objects.get(id=row_id)
        new = ProjectFile(
            name = name,
            ext = ext,
            project = project,
            user = R.user,
            file_type = FRCM_Option.objects.get(swarm="file_type_tag", value=file_type),
            upload_time = NOW(),
            memo = '',
        )
        new.save()
        getattr(new, 'file').save('%s.%s'%(new.id, new.ext), f)
        new.save()
        new.can_delete = True

        t = get_template(os.path.join('frcm', 'zh-tw', 'tr_for_projectfile.html'))
        html = t.render(RequestContext(R,{
            'user': R.user,
            'row': project,
            'f': new,
            'edit': True,
            'tags': tags,
            'file_type': file_type
            }))

    return HttpResponse(json.dumps({'status': True, 'html': html, 'id': new.id, 'name': new.name, 'rExt': ext, 'place_id': place_id, 'upload_date': str(TODAY())}))


#依照設定導向工程相片系統
@login_required
def go_photo(R, project_id):
    project = Project.objects.get(id=project_id)
    if project.use_gallery: url = reverse('gallery.views.index', kwargs={'project_id': project.id})
    else: url = reverse('engphoto_index', kwargs={'project_id': project.id})
    return HttpResponseRedirect(url)


@login_required
def chase_use_pcc_progress(R):
    data = R.POST or json.loads(R.body)

    project = Project.objects.get(id=data['project_id'])
    if not project.pcc_no:
        return HttpResponse(json.dumps({
            'status': False, 
            'msg': '您尚未填寫工程會標案編號。', 
            }))
    try:
        project.sync_pcc_info()
    except: pass
    chase_otm = project.countychaseprojectonetomany_set.get(id=data['chase_otm_id'])

    pcc_progress = PCCProgress.objects.filter(project__uid=project.pcc_no).order_by('-year', '-month')

    if not pcc_progress:
        return HttpResponse(json.dumps({
            'status': False, 
            'msg': '查無工程會進度資訊', 
            }))
    else:
        progress = pcc_progress.first()
        chase_otm.schedul_progress_percent = progress.percentage_of_predict_progress * 100.
        chase_otm.actual_progress_percent = progress.percentage_of_real_progress * 100.
        chase_otm.save()

        return HttpResponse(json.dumps({
            'status': True, 
            'schedul_progress_percent': chase_otm.schedul_progress_percent, 
            'actual_progress_percent': chase_otm.actual_progress_percent,
            }))


@login_required
def my_unit(R):
    data = R.GET
    up = UserProfile.objects.get(user=R.user)
    unit = up.unit
    set_unit = False
    if R.user.is_staff:
        if data.get('username', ''):
            up = UserProfile.objects.get(user__username=data['username'])
            unit = up.unit
            set_unit = True
        if data.get('no', ''):
            try:
                unit = Unit.objects.get(no=data['no'])
            except:
                unit = None
    if not unit:
        if Unit.objects.filter(no=data['no']):
            unit = Unit.objects.get(no=data['no'])
        else:
            unit = Unit(no=data['no'], place=Place.objects.get(id=1))
            unit.save()

        set_unit = True
    if set_unit:
        up.unit = unit
        up.save()
    t = get_template(os.path.join('frcm', 'zh-tw', 'my_unit.html'))
    html = t.render(RequestContext(R,{
        'user': R.user,
        'unit': unit,
        'toppage_name': u'遠端管理系統',
        'subpage_name': u'編輯廠商資訊',
        }))
    return HttpResponse(html)


@login_required
def warning_info(R):
    """ 
    * 說明:預警系統 預警內容頁面 
    """
    if not R.user.has_perm('fishuser.sub_menu_warning_system_warninginfo'):
        return HttpResponseRedirect('/')

    if not R.user.has_perm('fishuser.view_all_project_in_management_system'):
        # 沒有 "在(管考系統)中_觀看_所有_工程案資訊"
        new_units = []
        u_name = R.user.user_profile.unit.name[:3]
        for u in units:
            if u_name in u.name:
                new_units.append(u)
    else:
        new_units = units

    warningcheck = WarningCheck.objects.all().order_by('-start_check_time')[0]

    #無人認領工程案
    no_import_projects = NoImportProject.objects.filter(warningcheck=warningcheck, project__unit__in=new_units).prefetch_related('project').order_by('-project__unit', 'project__year')
    warning_projects = warningcheck.warningproject_warningcheck.filter(project__unit__in=new_units).prefetch_related('project').order_by('-project__unit', 'project__year')
    min_year = 500
    max_year = 1
    for i in list(no_import_projects) + list(warning_projects):
        if i.project.year > max_year: max_year = i.project.year
        if i.project.year < min_year: min_year = i.project.year

    t = get_template(os.path.join('frcm', 'zh-tw', 'warning_warninginfo.html'))
    html = t.render(RequestContext(R,{
        'user': R.user,
        'years': range(max_year, min_year-1, -1),
        'units': new_units,
        'option': _make_choose(),
        'warningcheck': warningcheck,
        'warning_projects': warning_projects,
        'no_import_projects': no_import_projects,
        'toppage_name': u'遠端管理系統',
        'subpage_name': u'預警內容',
        }))
    return HttpResponse(html)


@login_required
def get_rcmup_users(R):
    """ 取得工程所屬工程師及廠商列表 """
    project = Project.objects.get(id=R.POST.get('row_id', ''))
    rcmup_users = FRCMUserGroup.objects.filter(project=project).order_by('group').prefetch_related('user', 'group')
    html = ''
    for i in rcmup_users:
        u = i.user
        up = u.user_profile
        html += '<tr class="tr_rcmup_user"><td>%s<br>%s</td><td>%s</td><td>%s</td><td>%s<br>%s</td></tr>' % (u.username, up.unit.name if up.unit else u'', up.rName(), i.group.name.split('_')[-1], up.phone or '', u.email)

    return HttpResponse(json.dumps({'project_name': '%s年度-%s' % (project.year, project.name), 'html': html}))











# 以下舊分頁------------------------------------------------------------------
def readJson(R, **kw):
    DATA = readDATA(R)
    if 'importProject' == DATA.get('submit', None):
        if not _ca(user=R.user, project='', right_type_value= u'匯入工程案'):
            return HttpResponseRedirect('/u/transfer/')
        
        project = Project.objects.get(id=DATA.get('project_id',None))
        row = FRCMUserGroup(
                            user = User.objects.get(id=DATA.get('user_id',None)),
                            group = Group.objects.get(name=u'負責主辦工程師'),
                            project = project,
                            date = TODAY(),
                            )
        row.save()

        if '_' in R.user.username and '主辦工程師' in R.user.user_profile.group.name:
            project.local_charge = R.user.user_profile.rName()
            project.local_contacter = R.user.user_profile.rName()
            project.local_contacter_phone = R.user.user_profile.phone
            project.local_contacter_email = R.user.email
        elif '主辦工程師' in R.user.user_profile.group.name:
            project.self_charge = R.user.user_profile.rName()
            project.self_contacter = R.user.user_profile.rName()
            project.self_contacter_phone = R.user.user_profile.phone
            project.self_contacter_email = R.user.email

        project.frcm_inspector_type = Option.objects.get(swarm='inspector_type', value='委外監造')
        project.frcm_duration_type = Option.objects.get(swarm='duration_type', value='日曆天(不含六日)')
        again = True
        while again == True:
            contractor_code = ''
            for i in xrange(6):
                contractor_code += str(int(random.random()*10))
            try:
                k = Project.objects.get(contractor_code=contractor_code)
                again = True
            except:
                again = False
        again = True
        english = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
        while again == True:
            inspector_code = ''
            for i in xrange(6):
                inspector_code += english[int(random.random()*26)]
            try:
                k = Project.objects.get(inspector_code=inspector_code)
                again = True
            except:
                again = False
        project.contractor_code = contractor_code
        project.inspector_code = inspector_code
        project.save()
        p = {
            'id': project.id,
            'name': project.name,
            'start_date': str(project.start_date) or '',
            }
        duration_type_id = [i.id for i in Option.objects.filter(swarm=u'duration_type').order_by('id')]
        duration_type_value = [i.value for i in Option.objects.filter(swarm=u'duration_type').order_by('id')]
        inspector_type_id = [i.id for i in Option.objects.filter(swarm=u'inspector_type').order_by('id')]
        inspector_type_value = [i.value for i in Option.objects.filter(swarm=u'inspector_type').order_by('id')]

        return HttpResponse(json.write({'status': True, 'project': p,
                                        'duration_type_id': duration_type_id,
                                        'duration_type_value': duration_type_value,
                                        'inspector_type_id': inspector_type_id,
                                        'inspector_type_value': inspector_type_value,
                                        }))

    elif 'updateFRCMProject' == DATA.get('submit', None):
        row = Project.objects.get(id=DATA.get('project_id',''))
        if not _ca(user=R.user, project=row, right_type_value= u'編輯工程案基本資料'):
            return HttpResponseRedirect('/u/transfer/')

        field = DATA.get('field_name','')
        value = DATA.get('value','')
        message = ''
        if 'frcm_duration_type' == field:
            value = Option.objects.get(id=value)
            if value.value == '限期完工(日曆天每日施工)':
                message = '限期完工(日曆天每日施工)'
        elif 'frcm_duration' == field:
            try:
                value = int(value)
            except:
                return HttpResponse(json.write({'status': False, 'message': '此欄位須為數字'}))
        elif 'inspector_open' == field or 'contractor_open' == field:
            if value == 'open': value = True
            else: value = False
        elif 'frcm_inspector_type' == field:
            value = Option.objects.get(id=value)
            if value.value == '自辦監造(自動關閉監造帳號)':
                frcm = FRCMUserGroup.objects.get(group__name='負責主辦工程師', project=row)
                newgroup = Group.objects.get(name='自辦主辦工程師')
                setattr(frcm, 'group', newgroup)
                frcm.save()
                setattr(row, 'inspector_open', False)
                message = '自辦監造(自動關閉監造帳號)'
            elif value.value == '委外監造':
                frcm = FRCMUserGroup.objects.get(group__name='自辦主辦工程師', project=row)
                newgroup = Group.objects.get(name='負責主辦工程師')
                setattr(frcm, 'group', newgroup)
                frcm.save()

        setattr(row, field, value)
        row.save()
        return HttpResponse(json.write({'status': True, 'message': message}))

    elif 'getProject' == DATA.get('submit', None):
        if not _ca(user=R.user, project='', right_type_value= u'認領工程'):
            return HttpResponseRedirect('/u/transfer/')
        user = R.user
        code = DATA.get('code', None).upper()
        unit_no = DATA.get('unit_no', None).upper()
        for p in FRCMUserGroup.objects.filter(user=user):
            if p.project.contractor_code == code or p.project.inspector_code == code:
                return HttpResponse(json.write({'status': False, 'message': '此工程您已經認領過了，不可重複認領!!'}))
        try:
            unit = Unit.objects.get(no=unit_no)
        except:
            unit = Unit(
                        name = '尚未解析統編('+unit_no+')',
                        fullname = '尚未解析統編('+unit_no+')',
                        no = unit_no,
                        place = Place.objects.get(name='臺灣地區'),
                        uplevel = Unit.objects.get(name='民間機構'),
                        )
        try:
            project = Project.objects.get(contractor_code=code)
            group = Group.objects.get(name='營造廠商')
            unit.save()
            project.contractor = unit
        except:
            try:
                project = Project.objects.get(inspector_code=code)
                group = Group.objects.get(name='監造廠商')
                unit.save()
                project.inspector = unit
            except:
                return HttpResponse(json.write({'status': False, 'message': '無符合之工程案，請確認您的認領碼是否正確!!'}))
        row = FRCMUserGroup(
                            user = user,
                            group = group,
                            project = project,
                            date = TODAY(),
                            )
        project.save()
        row.save()
        return HttpResponse(json.write({'status': True, 'project_name': project.name, 'group': group.name}))

    elif 'regretToShareProject' == DATA.get('submit', None):
        project = Project.objects.get(id=DATA.get('project_id', None))
        user = R.user
        row = FRCMUserGroup.objects.get(user=user, project=project)
        row.delete()
        return HttpResponse(json.write({'status': True}))

    elif 'askToShareProject' == DATA.get('submit', None):
        if '主辦工程師' not in R.user.user_profile.group.name:
            return HttpResponse(json.write({'status': False, 'message': '並無申請權限!!'}))
        project = Project.objects.get(id=DATA.get('project_id', None))
        user = R.user
        try:
            FRCMUserGroup.objects.get(user=user, project=project)
            return HttpResponse(json.write({'status': False, 'message': '申請失敗，您已經擁有此件工程或已經申請過了!!'}))
        except: pass
        row = FRCMUserGroup(
                            user = user,
                            group = Group.objects.get(name='協同主辦工程師'),
                            project = project,
                            date = TODAY(),
                            is_active = False,
                            )
        row.save()
        return HttpResponse(json.write({'status': True}))

    elif 'answerAskShare' == DATA.get('submit', None):
        row = FRCMUserGroup.objects.get(id=DATA.get('row_id', None))
        if 'yes' == DATA.get('value', None):
            setattr(row, 'is_active', True)
            row.save()
            message = '處理完畢， %s 已成為協同主辦工程師'%row.user.user_profile.rName();
        elif 'no' == DATA.get('value', None):
            row.delete()
            message = '處理完畢， 您拒絕 %s 的申請'%row.user.user_profile.rName();

        return HttpResponse(json.write({'status': True, 'message': message}))

    elif 'sendBackProject' == DATA.get('submit', None):
        user = R.user
        project = Project.objects.get(id=DATA.get('project_id', None))
        row = FRCMUserGroup.objects.get(user=user, project=project)
        if row.group.name == '協同主辦工程師':
            row.delete()
        elif row.group.name == '營造廠商' and len(FRCMUserGroup.objects.filter(group__name='營造廠商', project=project)) > 1:
            row.delete()
        elif row.group.name == '監造廠商' and len(FRCMUserGroup.objects.filter(group__name='監造廠商', project=project)) > 1:
            row.delete()
        else:
            return HttpResponse(json.write({'status': False, 'message': '退還失敗，您目前的狀態無法執行此動作'}))
        return HttpResponse(json.write({'status': True}))

    elif 'transferEngineer' == DATA.get('submit', None):
        project = Project.objects.get(id=DATA.get('project_id', None))
        if 'get_list' == DATA.get('active', None):
            users = []
            for i in FRCMUserGroup.objects.filter(group__name='協同主辦工程師', project=project):
                u = {
                    'id': i.user.id,
                    'name': i.user.user_profile.rName(),
                    'title': i.user.user_profile.title,
                    }
                users.append(u)
            return HttpResponse(json.write({'status': True, 'users': users}))
        elif 'transfer' == DATA.get('active', None):
            own_row = FRCMUserGroup.objects.get(user=R.user, project=project)
            own_group = Group.objects.get(id=own_row.group.id)
            trans_row = FRCMUserGroup.objects.get(user__id=DATA.get('user_id', None), project=project)
            trans_group = Group.objects.get(id=trans_row.group.id)
            setattr(own_row, 'group', trans_group)
            own_row.save()
            setattr(trans_row, 'group', own_group)
            trans_row.save()
            return HttpResponse(json.write({'status': True}))

    elif 'editFile' == DATA.get('submit', None):
        row = FRCMTempFile.objects.get(id=DATA.get('field_id'))
        if R.user != row.upload_user:
            return HttpResponse(json.write({'status': False, 'message': '您無此權限!!'}))
        value = DATA.get('value', '')
        if DATA.get('field_name') in ['xcoord', 'ycoord']:
            try:
                value = decimal.Decimal(str(value))
            except:
                return HttpResponse(json.write({'status': False, 'message': '欄位格式錯誤，請檢查您的輸入資訊。'}))
        setattr(row, DATA.get('field_name'), value)
        row.save()
        value = DATA.get('value', '')
        return HttpResponse(json.write({'status': True, 'value': value}))

    elif 'deleteFile' == DATA.get('submit', None):
        row = FRCMTempFile.objects.get(id=DATA.get('row_id'))
        if R.user != row.upload_user:
            return HttpResponse(json.write({'status': False, 'message': '您無此權限!!'}))
        row.delete()
        return HttpResponse(json.write({'status': True}))

    elif 'editCityFile' == DATA.get('submit', None):
        row = CityFiles.objects.get(id=DATA.get('field_id'))

        value = DATA.get('value', '')
        if DATA.get('field_name') in ['lng', 'lat']:
            try:
                value = decimal.Decimal(str(value))
            except:
                return HttpResponse(json.write({'status': False, 'message': '欄位格式錯誤，請檢查您的輸入資訊。'}))
        setattr(row, DATA.get('field_name'), value)
        row.save()
        value = DATA.get('value', '')
        return HttpResponse(json.write({'status': True, 'value': value}))

    elif 'deleteCityFile' == DATA.get('submit', None):
        row = CityFiles.objects.get(id=DATA.get('row_id'))
        row.delete()
        return HttpResponse(json.write({'status': True}))

    elif 'setChaseComplete' == DATA.get('submit', None):
        row = CountyChaseProjectOneToMany.objects.get(id=DATA.get('chase_id'))
        if row.complete == False:
            if not row.schedul_progress_percent and row.schedul_progress_percent != 0: return HttpResponse(json.write({'status': False, 'msg': '尚未填寫"預計進度百分比(%)"'}))
            if not row.actual_progress_percent and row.actual_progress_percent != 0: return HttpResponse(json.write({'status': False, 'msg': '尚未填寫"實際進度百分比(%)"'}))
            if not row.memo: return HttpResponse(json.write({'status': False, 'msg': '尚未填寫"計畫執行情形說明"'}))
            row.complete = True
            complete = True
        else:
            row.complete = False
            complete = False
        row.save()
        return HttpResponse(json.write({'status': True, 'complete': complete}))

    elif 'updateChaseInfo' == DATA.get('submit', None):
        table_name = DATA.get('table_name', None)
        chase_id = DATA.get('chase_id', None)
        field_name = DATA.get('field_name', None)
        field_value = DATA.get('value', None)

        return_value = field_value
        countychasetime = list(CountyChaseTime.objects.all().order_by('id'))[-1]
        

        if table_name == 'CountyChaseProjectOneToMany':
            row = CountyChaseProjectOneToMany.objects.get(id=chase_id)
            row.update_time = TODAY()
            row.save()
            if row.complete:
                if not countychasetime.new_update: countychasetime.new_update = ''
                countychasetime.new_update += str(row.project.id)+'---'+ str(field_name) + '---' + str(field_value) + '@!*#'
        elif table_name == 'CountyChaseProjectOneByOne':
            row = CountyChaseProjectOneByOne.objects.get(id=chase_id)
            try:
                row2 = list(row.project.countychaseprojectonetomany_set.all().order_by('countychasetime'))[-1]
                row2.update_time = TODAY()
                row2.save()
            except: pass
            try:
                if CountyChaseProjectOneToMany.objects.get(countychasetime=countychasetime, project=row.project).complete:
                    if not countychasetime.new_update: countychasetime.new_update = ''
                    countychasetime.new_update += str(row.project.id)+'---'+ str(field_name) + '---' + str(field_value) + '@!*#'
            except: pass
        elif table_name == 'Unit':
            row = Unit.objects.get(id=chase_id)


        countychasetime.save()
        if table_name == 'CountyChaseProjectOneToMany' and field_name != 'memo':
            if field_value == '': field_value = 0
            field_value = decimal.Decimal(str(round(float(field_value), 3)))
            return_value = str(int(field_value))
        elif table_name == 'CountyChaseProjectOneByOne':
            if field_value == '': field_value = None

        setattr(row, field_name, field_value)
        row.save()
        
        return HttpResponse(json.write({'status': True, 'return_value': return_value}))

    elif 'updateChaseTotalMoney' == DATA.get('submit', None):
        chase_id = DATA.get('chase_id', None)
        field_value = DATA.get('value', None)
        chase = CountyChaseProjectOneByOne.objects.get(id=chase_id)
        if field_value == 'useTotalMoney':
            if chase.project.rSettlementTotalMoney() != 0: value = decimal.Decimal(str(round(float(chase.project.rSettlementTotalMoney()), 3)))
            else: value = decimal.Decimal(str(round(float(chase.project.rContractTotalMoney()), 3)))
        else:
            row = list(Budget.objects.filter(fund__project=chase.project).order_by('year'))[-1]
            value = row.rPlanMoney() or decimal.Decimal('0')

        return_value = str(int(value))
        setattr(chase, 'total_money', value)
        chase.save()
        return HttpResponse(json.write({'status': True, 'return_value': return_value}))

    elif 'setChaseProjectClose' == DATA.get('submit', None):
        row = CountyChaseProjectOneToMany.objects.get(id=DATA.get('chase_id')).getOneByOne()
        close = DATA.get('clase')
        if close == 'True':
            row.close = False
        else:
            row.close = True
        row.save()
        return HttpResponse(json.write({'status': True, 'close': row.close}))

    elif 'makeFRCMCountyChaseExcel' == DATA.get('submit', None):
        type = DATA.get('type', None)
        user = User.objects.get(id=DATA.get('user_id', None))
        countychasetime = list(CountyChaseTime.objects.all().order_by('id'))[-1]

        if type == 'my':
            projects = [i.project for i in FRCMUserGroup.objects.filter(user=user)]
        elif type == 'all':
            first_name = user.username.split('_')[0]
            account = User.objects.get(username=first_name+'_account')
            unit = account.user_profile.unit
            projects = [i for i in Project.objects.filter(unit=unit).exclude(undertake_type__value='自辦')]

        chase_projects = []
        false_projects = []
        for p in projects:
            try:
                row = CountyChaseProjectOneToMany.objects.get(countychasetime=countychasetime, project=p)
                chase_projects.append(p)
                if not row.complete: false_projects.append(p)
            except: pass
        
        if false_projects:
            t = get_template(os.path.join('frcm', 'make_dialog_false_print.html'))
            html = t.render(Context({
                'num': len(false_projects),
                'projects': false_projects,
            }))
            return HttpResponse(json.write({'status': False, 'html': html}))

#        from fishuser.views import _makeDownloadFile_CountyChase
        
        result = _makeDownloadFile_CountyChase(user=user, projects=chase_projects, countychasetime=countychasetime)
        template_name = 'county_chase.xls'
        content = makeFileByWordExcel(template_name=template_name, result=result)
        random_key = random.random()
        cache.set(random_key, content, 600)
        return HttpResponse(json.write({'status': True, 'url': '/frcm/get_file/'+str(random_key)+'/?file_name='+str(countychasetime.chase_date) + '-縣市進度追蹤表'}))


def getFile(R, key):
    content = cache.get(key)
    filename = R.GET.get('file_name')
    response = HttpResponse(content_type='application/xls')
    response['Content-Type'] = ('application/xls')
    response['Content-Disposition'] = ('attachment; filename=%s.xls' % (filename).encode('cp950'))
    response.write(content)
    return response


def _makeDownloadFile_CountyChase(user='', projects='', countychasetime='', new='True'):
    heads = [
            '項次', '最後更新日期', '年度', '縣市別', '漁港別養殖區別', '工程名稱', '辦理別1.自2.委3.補', '預定進度%',
            '實際進度%(N)', '計畫經費', '預算數核定數', '預算數修正核定數', '預算數本署負擔（保留）數(A)','預算數地方核定數', '預算數地方修正核定數',
            '預算數地方配合款(B)', '預算數歷年( C )', '本署負擔總經費(E)', '發包及其他費用合計(D)未發包以核定數代替', '漁業署撥款情形',
            '累計分配數（R）', '實支數本署(I)', '實支數縣府(J)', '應付未付數本署(L)', '應付未付數縣府(M)', '賸餘款本署(F)',
            '本署經費執行數（H）＝(I+L+F)', '執行率(P)＝（H）/（R+F）', '達成率(Q)＝（H）/（A）', '計畫執行情形說明(若有執行落後者，請詳細說明預定完成日期及因應措施',
            '預計至年底執行率', '執行單位', '執行單位聯絡窗口', '縣市政府聯絡方式(mail及電話)',
            '勞務_核定計畫', '勞務_簽辦招標', '勞務_公告招標', '勞務_公開評選會議(限制性招標)', '勞務_定約', '勞務_基本設計',
            '勞務_細部設計', '勞務_驗收結案', '勞務_簽辦招標', '設計規劃_核定計畫', '設計規劃_簽辦招標', '設計規劃_公告招標', '設計規劃_公開評選會議(限制性招標)',
            '設計規劃_定約', '設計規劃_基本設計', '設計規劃_細部設計', '設計規劃_驗收結案', '工程施做_簽辦招標', '工程施做_公告招標',
            '工程施做_定約', '工程施做_開工', '工程施做_完工', '工程施做_驗收', '工程施做_結案',
            ]

    data = {'replace': {}, 'table_eng': [], 'table_ser': []}
    for n, p in enumerate(projects):
        tmp = {}

        p.fund = p.fund_set.get()
        p.budget = list(p.fund.budget_set.all().order_by('year'))[-1]
        p.chase_obo = p.countychaseprojectonebyone_set.get()
        tmp['使用舊資料'] = ''
        tmp['從未填寫'] = ''
        if new == 'True':
            try: p.chase_otm = p.countychaseprojectonetomany_set.get(countychasetime=countychasetime, check=True)
            except:
                try:
                    p.chase_otm = list(p.countychaseprojectonetomany_set.filter(countychasetime__id__lt=countychasetime.id, check=True).order_by('countychasetime__id'))[-1]
                    tmp['使用舊資料'] = 'V'
                except:
                    p.chase_otm = p.countychaseprojectonetomany_set.get(countychasetime=countychasetime)
                    tmp['從未填寫'] = 'V'
        else:
            p.chase_otm = p.countychaseprojectonetomany_set.get(countychasetime=countychasetime)
        if p.chase_otm.update_time: tmp['最後更新日期'] = p.chase_otm.update_time
        else: tmp['最後更新日期'] = ''
        tmp['項次'] = n + 1
        tmp['年度'] = p.year
        tmp['縣市別'] = p.place.name
        port_str = ''
        for i in p.rSubLocation():
            port_str += i.name + ' '
        tmp['漁港別養殖區別'] = port_str
        tmp['工程名稱'] = p.name
        if p.undertake_type.value == '自辦': tmp['辦理別1.自2.委3.補'] = 1
        elif p.undertake_type.value == '委辦': tmp['辦理別1.自2.委3.補'] = 2
        elif p.undertake_type.value == '補助': tmp['辦理別1.自2.委3.補'] = 3
        tmp['預定進度%'] = float(str(p.chase_otm.schedul_progress_percent or 0)) / 100.
        tmp['實際進度%(N)'] = float(str(p.chase_otm.actual_progress_percent or 0)) / 100.
        tmp['預算數核定數'] = p.budget.capital_ratify_budget
        tmp['預算數修正核定數'] = p.budget.capital_ratify_revision
        tmp['預算數地方核定數'] = p.budget.capital_ratify_local_budget
        tmp['預算數地方修正核定數'] = p.budget.capital_ratify_local_revision
        tmp['計畫經費'] = p.budget.rPlanMoney()
        tmp['預算數本署負擔（保留）數(A)'] = p.fund.rSelfLoad()
        tmp['預算數地方配合款(B)'] = p.fund.rlocalMatchFund()
        tmp['預算數歷年( C )'] = float(str(p.budget.over_the_year or 0))
        tmp['本署負擔總經費(E)'] = tmp['預算數本署負擔（保留）數(A)'] + tmp['預算數歷年( C )']
        if p.rTotalMoneyInProject() != 0:#1.採用工程結算金額 #2.採用工程契約金額
            tmp['發包及其他費用合計(D)未發包以核定數代替'] = p.rTotalMoneyInProject()
        elif p.budget.capital_ratify_revision != 0:#3.採用修正核定數
            tmp['發包及其他費用合計(D)未發包以核定數代替'] = p.budget.capital_ratify_revision
        else:#4.採用核定數
            tmp['發包及其他費用合計(D)未發包以核定數代替'] = p.budget.capital_ratify_budget or 0
        tmp['漁業署撥款情形'] = p.rTotalAppropriate()
        tmp['累計分配數（R）'] = p.chase_otm.getFund().rAllocationToNow()
        tmp['實支數本署(I)'] = p.chase_otm.self_payout
        tmp['實支數縣府(J)'] = p.chase_otm.local_payout
        tmp['應付未付數本署(L)'] = p.chase_otm.self_unpay
        tmp['應付未付數縣府(M)'] = p.chase_otm.local_unpay
        tmp['賸餘款本署(F)'] = p.chase_otm.rSelf_Surplus()
#        tmp['賸餘款縣府(G)'] = p.chase_otm.rLocal_Surplus()
        tmp['本署經費執行數（H）＝(I+L+F)'] = p.chase_otm.getSelfExecutionMoney()
        tmp['執行率(P)＝（H）/（R+F）'] = p.chase_otm.getExecutionRate() / 100.
        tmp['達成率(Q)＝（H）/（A）'] = p.chase_otm.getReachedRate() / 100.
        tmp['計畫執行情形說明(若有執行落後者，請詳細說明預定完成日期及因應措施'] = p.chase_otm.memo
        if p.chase_otm.expected_to_end_percent: p.chase_otm.expected_to_end_percent = float(str(p.chase_otm.expected_to_end_percent))
        else: p.chase_otm.expected_to_end_percent = 0
        tmp['預計至年底執行率'] = p.chase_otm.expected_to_end_percent / 100.
        tmp['執行單位'] = p.unit.name
#        tmp['署內負責人'] = p.self_charge or ''
#        tmp['原始負責人'] = ''

        tmp['勞務_核定計畫'] = ('預計：' + str(p.chase_obo.sch_ser_approved_plan or '') + "           實際：" + str(p.chase_obo.act_ser_approved_plan or '')).encode('cp950')
        tmp['勞務_簽辦招標'] = ('預計：' + str(p.chase_obo.sch_ser_signed_tender  or '') + "           實際：" + str(p.chase_obo.act_ser_signed_tender or '')).encode('cp950')
        tmp['勞務_公告招標'] = ('預計：' + str(p.chase_obo.sch_ser_announcement_tender or '') + "           實際：" + str(p.chase_obo.act_ser_announcement_tender or '')).encode('cp950')
        tmp['勞務_公開評選會議(限制性招標)'] = ('預計：' + str(p.chase_obo.sch_ser_selection_meeting or '') + "           實際：" + str(p.chase_obo.act_ser_selection_meeting or '')).encode('cp950')
        tmp['勞務_定約'] = ('預計：' + str(p.chase_obo.sch_ser_promise or '') + "           實際：" + str(p.chase_obo.act_ser_promise or '')).encode('cp950')
        tmp['勞務_基本設計'] = ('預計：' + str(p.chase_obo.sch_ser_work_plan or '') + "           實際：" + str(p.chase_obo.act_ser_work_plan or '')).encode('cp950')
        tmp['勞務_細部設計'] = ('預計：' + str(p.chase_obo.sch_ser_interim_report or '') + "           實際：" + str(p.chase_obo.act_ser_interim_report or '')).encode('cp950')
        tmp['勞務_驗收結案'] = ('預計：' + str(p.chase_obo.sch_ser_final_report or '') + "           實際：" + str(p.chase_obo.act_ser_final_report or '')).encode('cp950')
        tmp['勞務_簽辦招標'] = ('預計：' + str(p.chase_obo.sch_ser_acceptance_closed or '') + "           實際：" + str(p.chase_obo.act_ser_acceptance_closed or '')).encode('cp950')

        tmp['設計規劃_核定計畫'] = ('預計：' + str(p.chase_obo.sch_eng_plan_approved_plan or '') + "           實際：" + str(p.chase_obo.act_eng_plan_approved_plan or '')).encode('cp950')
        tmp['設計規劃_簽辦招標'] = ('預計：' + str(p.chase_obo.sch_eng_plan_signed_tender or '') + "           實際：" + str(p.chase_obo.act_eng_plan_signed_tender or '')).encode('cp950')
        tmp['設計規劃_公告招標'] = ('預計：' + str(p.chase_obo.sch_eng_plan_announcement_tender or '') + "           實際：" + str(p.chase_obo.act_eng_plan_announcement_tender or '')).encode('cp950')
        tmp['設計規劃_公開評選會議(限制性招標)'] = ('預計：' + str(p.chase_obo.sch_eng_plan_selection_meeting or '') + "           實際：" + str(p.chase_obo.act_eng_plan_selection_meeting or '')).encode('cp950')
        tmp['設計規劃_定約'] = ('預計：' + str(p.chase_obo.sch_eng_plan_promise or '') + "           實際：" + str(p.chase_obo.act_eng_plan_promise or '')).encode('cp950')
        tmp['設計規劃_基本設計'] = ('預計：' + str(p.chase_obo.sch_eng_plan_basic_design or '') + "           實際：" + str(p.chase_obo.act_eng_plan_basic_design or '')).encode('cp950')
        tmp['設計規劃_細部設計'] = ('預計：' + str(p.chase_obo.sch_eng_plan_detail_design or '') + "           實際：" + str(p.chase_obo.act_eng_plan_detail_design or '')).encode('cp950')
        tmp['設計規劃_驗收結案'] = ('預計：' + str(p.chase_obo.sch_eng_plan_acceptance_closed or '') + "           實際：" + str(p.chase_obo.act_eng_plan_acceptance_closed or '')).encode('cp950')
        tmp['工程施做_簽辦招標'] = ('預計：' + str(p.chase_obo.sch_eng_do_signed_tender or '') + "           實際：" + str(p.chase_obo.act_eng_do_signed_tender or '')).encode('cp950')
        tmp['工程施做_公告招標'] = ('預計：' + str(p.chase_obo.sch_eng_do_announcement_tender or '') + "           實際：" + str(p.chase_obo.act_eng_do_announcement_tender or '')).encode('cp950')
        tmp['工程施做_定約'] = ('預計：' + str(p.chase_obo.sch_eng_do_promise or '') + "           實際：" + str(p.chase_obo.act_eng_do_promise or '')).encode('cp950')
        tmp['工程施做_開工'] = ('預計：' + str(p.chase_obo.sch_eng_do_start or '') + "           實際：" + str(p.chase_obo.act_eng_do_start or '')).encode('cp950')
        tmp['工程施做_完工'] = ('預計：' + str(p.chase_obo.sch_eng_do_completion or '') + "           實際：" + str(p.chase_obo.act_eng_do_completion or '')).encode('cp950')
        tmp['工程施做_驗收'] = ('預計：' + str(p.chase_obo.sch_eng_do_acceptance or '') + "           實際：" + str(p.chase_obo.act_eng_do_acceptance or '')).encode('cp950')
        tmp['工程施做_結案'] = ('預計：' + str(p.chase_obo.sch_eng_do_closed or '') + "           實際：" + str(p.chase_obo.act_eng_do_closed or '')).encode('cp950')

        try:
            p.frcm = p.frcmusergroup_set.get(group__name__in=[u'負責主辦工程師', u'自辦主辦工程師'])
            tmp[u'執行單位聯絡窗口'] = p.frcm.user.user_profile.rName()
            tmp[u'縣市政府聯絡方式(mail及電話)'] = str(p.frcm.user.user_profile.phone) + '    (' + p.frcm.user.email + ')'
        except:
            tmp[u'執行單位聯絡窗口'] = ''
            tmp[u'縣市政府聯絡方式(mail及電話)'] = ''

        if p.purchase_type.value in [u'工程', u'工程勞務']:
            data['table_eng'].append(tmp)
        else:
            data['table_ser'].append(tmp)
    return data

@checkAuthority
def readMyProject(R, project, right_type_value= u'menu1_遠端管理系統'):
    user = R.user
    if not user.user_profile.rIdentity() in ['主辦工程師', '署內主辦工程師', '註冊'] and not user.is_staff:
        return HttpResponseRedirect('/frcm/search/')
    projects = [p.project for p in FRCMUserGroup.objects.filter(project__deleter=None, user=user)]
    countychasetime = list(CountyChaseTime.objects.all().order_by('id'))[-1]
    have_print_button_self = False
    have_print_button_all = False
    for p in projects:
        p.usergroup = FRCMUserGroup.objects.get(user=user, project=p).group.name
        p.engs = []
        for u in FRCMUserGroup.objects.filter(project=p, group__name__in=['負責主辦工程師', '協同主辦工程師', '自辦主辦工程師']):
            u.group.name = u.group.name[0:2]
            p.engs.append(u)
        p.open = FRCMUserGroup.objects.get(user=user, project=p).is_active
        p.message = '帳號關閉中'
        if p.usergroup == '營造廠商':
            p.open = p.contractor_open
            if not p.open:
                p.message = '營造帳號關閉中'
        elif p.usergroup == '監造廠商':
            p.open = p.inspector_open
            if not p.open:
                p.message = '監造帳號關閉中'
        else:
            p.open = True
        if not p.frcmusergroup_set.get(user=user).is_active and p.frcmusergroup_set.get(user=user).group.name == '協同主辦工程師':
            p.message = '等待對方授權中'
            p.have_regret_button = True
        else:
            p.have_regret_button = False

        if '_' in user.username and not user.is_staff:
            have_print_button_all = True
        try:
            if not CountyChaseProjectOneByOne.objects.get(project=p).check:
                p.chase_data = CountyChaseProjectOneToMany.objects.get(countychasetime=countychasetime, project=p)
            if '主辦工程師' in user.user_profile.group.name or user.is_staff:
                have_print_button_self = True
        except: pass

        

    t = get_template(os.path.join('frcm', 'myproject.html'))
    html = t.render(Context({
        'user': R.user,
        'projects': projects,
        'have_print_button_self': have_print_button_self,
        'have_print_button_all': have_print_button_all,
    }))
    return HttpResponse(html)

@checkAuthority
def importProject(R, project, right_type_value= u'匯入工程案'):
    class searchForm(forms.Form):
        bid_no = forms.CharField(label='標案編號', required=False)
        name = forms.CharField(label='工作名稱', required=False)
        plans = [('', '全部')]
        for i in Plan.objects.filter(uplevel=None):
            plans.append((i.id, '---'*i.rLevelNumber() + i.name))
            for j in i.rSubPlanInList():
                plans.append((j.id, '---'*j.rLevelNumber() + j.name))
        plan = forms.ChoiceField(choices=plans, required=False, label='所屬計畫')
        search_type = [('cover', '　含下層計畫'), ('not', '不含下層計畫')]
        sub_type = forms.ChoiceField(choices=search_type, required=False, label='層級')
        years = [(y-1911, y-1911) for y in xrange(2006, TODAY().year+1)]
        years.insert(0, ('', '所有年度'))
        years.reverse()
        year = forms.ChoiceField(choices=years, required=False, label='年度')
        purchase_types = [('', '全部')] + [(type.id, type.value) for type in Option.objects.filter(swarm='purchase_type')]
        purchase_type = forms.ChoiceField(choices=purchase_types, required=False, label='採購類別：', help_text='(工程／勞務)')
        units = [('', '全部')]
        for i in Unit.fish_city_menu.all():
            units.append((i.id, i.name))
            if i.uplevel and i.uplevel.name != u'縣市政府':
                units.extend(
                    [(j.id, '---'+j.name) for j in i.uplevel_subunit.all()]
                )
        unit = forms.ChoiceField(choices=units, required=False, label='執行機關')
        impos = [('', '全部'), ('yes', ' (已被)匯入 '), ('no', ' (尚未)匯入 ')]
        impo = forms.ChoiceField(choices=impos, required=False, label='是否匯入')

    user, DATA = R.user, readDATA(R)

    form = searchForm()
    projects_num = -1
    projects = []
    querystring = ''
    INFO = {}
    for k, v in R.GET.items(): INFO[k] = v
    for k, v in R.POST.items(): INFO[k] = v
    INFO['user'] = user
    if INFO.get('submit', None):
        form = searchForm(INFO)
        querystring = '&'.join(['%s=%s'%(k, v) for k, v in INFO.items() if k != 'page'])
        projects, projects_num = _searchProject(INFO)

    for i in projects:
        try:
            i.importuser = FRCMUserGroup.objects.get(group__name='負責主辦工程師', project=i).user.user_profile.rName()
            try:
                FRCMUserGroup.objects.get(user=user, project=i)
                i.inlist = True
            except:
                i.inlist = False
        except:
            try:
                i.importuser = FRCMUserGroup.objects.get(group__name='自辦主辦工程師', project=i).user.user_profile.rName()
                try:
                    FRCMUserGroup.objects.get(user=user, project=i)
                    i.inlist = True
                except:
                    i.inlist = False
            except:
                pass

    t = get_template(os.path.join('frcm', 'import.html'))
    html = t.render(RequestContext(R,{
        'form':form,
        'projects': projects,
        'sortBy': INFO.get('sortBy', None) or 'year',
        'page_list': makePageList(INFO.get('page', 1), projects_num, NUMPERPAGE),
        'querystring': querystring,
        'projects_num': projects_num,
        }))
    return HttpResponse(html)

def _searchProject(INFO):
    if '_' in INFO['user'].username and not INFO['user'].is_staff:
        if '漁會' in INFO['user'].user_profile.unit.name:
            result = Project.objects.filter(deleter=None, unit=INFO['user'].user_profile.unit).order_by(INFO.get('sortBy', None))
        else:
            city_account = User.objects.get(username=INFO['user'].username.split('_')[0]+'_account')
            result = Project.objects.filter(deleter=None, unit__name__contains=city_account.user_profile.unit.name[0:3]).order_by(INFO.get('sortBy', None))
    else:
        result = Project.objects.filter(deleter=None).order_by(INFO.get('sortBy', None))

    if INFO.get('impo', None) != '' and INFO.get('impo', None) == 'yes':
        list = [i['project'] for i in FRCMUserGroup.objects.values('project').annotate(Count('project'))]
        result = result.filter(id__in=list)
    elif INFO.get('impo', None) != '' and INFO.get('impo', None) == 'no':
        list = [i['project'] for i in FRCMUserGroup.objects.values('project').annotate(Count('project'))]
        result = result.exclude(id__in=list)

    if INFO.get('bid_no', None) != '':
        ids = []
        for bid_no in re.split('[ ,]+', INFO.get('bid_no', None)):
            ids.extend([i.id for i in result.filter(bid_no__icontains=bid_no)])
        result = result.filter(id__in=ids)

    if INFO.get('name', None) != '':
        ids = []
        for name in re.split('[ ,]+', INFO.get('name', None)):
            ids.extend([i.id for i in result.filter(name__icontains=name)])
        result = result.filter(id__in=ids)

    if INFO.get('plan', None) != '':
        plan = Plan.objects.get(id=INFO.get('plan', None))
        if INFO.get('sub_type', None) == 'cover':
            plan_ids = [plan.id] + [i.id for i in Plan.objects.get(id=INFO.get('plan', None)).rSubPlanInList()]
            result = result.filter(plan__id__in=plan_ids)
        else:
            result = result.filter(plan = plan)
            
    if INFO.get('year', None) != '':
        result = result.filter(year=INFO.get('year', None))

    if INFO.get('purchase_type', None) != '':
        result = result.filter(purchase_type__id=INFO.get('purchase_type', None))

    if INFO.get('unit', None) != '':
        unit = Unit.objects.get(id=INFO.get('unit', None))
        result = result.filter(unit=unit)


    if not INFO.get('page', None): page = 1
    else: page = int(INFO['page'])

    projects = []
    result_num = result.count()
    for order, u in enumerate(result[(page-1)*NUMPERPAGE:page*NUMPERPAGE]):
        u.order = int((page-1)*NUMPERPAGE+order+1)
        projects.append(u)

    return projects, result_num

# def _make_choose():
#     options = Option.objects.all()
#     chooses = {}
#     for i in options:
#         if chooses.has_key(i.swarm):
#             chooses[i.swarm].append(i)
#         else:
#             chooses[i.swarm] = [i]
#     chooses['project_status'] = _getProjectStatusInList()
#     return chooses

@checkAuthority
def reProjectProfile(R, project, right_type_value= u'觀看工程案基本資料', **kw):
    user = R.user
    edit = False
    can_upload = False
    if user.user_profile.group.name == '上層管理者' or user.user_profile.group.name == '管考填寫員' or user.is_staff:
        group = user.user_profile.group.name
    elif user.user_profile.group.name == '署內主辦工程師':
        try:
            group = FRCMUserGroup.objects.get(user=user, project=project).group.name
            if group == '負責主辦工程師' or group == '協同主辦工程師' or group == '自辦主辦工程師':
                can_upload = True
                edit = True
        except:
            group = user.user_profile.group.name
    else:
        try:
            FRCMUserGroup.objects.get(user=user, project=project)
        except:
            return HttpResponseRedirect('/u/')
        if not FRCMUserGroup.objects.get(user=user, project=project).is_active:
            return HttpResponseRedirect('/u/')
        group = FRCMUserGroup.objects.get(user=user, project=project).group.name
        if group == '監造廠商' and project.inspector_open == False:
            return HttpResponseRedirect('/u/')
        elif group == '營造廠商' and project.contractor_open == False:
            return HttpResponseRedirect('/u/')
        if group == '負責主辦工程師' or group == '協同主辦工程師' or group == '自辦主辦工程師':
            can_upload = True
            edit = True
    if user.is_staff:
        edit = True
        can_upload = True

    files = FRCMTempFile.objects.filter(project=project).order_by('upload_user', '-upload_date')
    if R.POST.get('submit', ''):
        row = FRCMTempFile(
                    name = R.POST.get('name',''),
                    memo = R.POST.get('memo',''),
                    xcoord = decimal.Decimal(str(R.POST.get('xcoord',''))),
                    ycoord = decimal.Decimal(str(R.POST.get('ycoord',''))),
                    project = project,
                    upload_user = user,
                    upload_date = TODAY(),
                    )
        row.save()
        file = R.FILES.get('file', None)
        try:
            ext = file.name.split('.')[-1]
        except:
            ext = 'zip'
#        if ext in ['jpg', 'jpeg', 'tiff', 'tif', 'png', 'gif']:
#            thumb(row.file.name, "width=1024,height=768")

        getattr(row, 'file').save('%s.%s'%(row.id, ext), file)
        row.save()

    inspectors = [u.user for u in FRCMUserGroup.objects.filter(group__name='監造廠商', project=project)]
    contractors = [u.user for u in FRCMUserGroup.objects.filter(group__name='營造廠商', project=project)]
    engs = [(str(u.group.name[0:2])+":"+str(u.user.user_profile.rName())) for u in FRCMUserGroup.objects.filter(project=project, group__name__in=['負責主辦工程師', '協同主辦工程師', '自辦主辦工程師'])]
    project.identity = user.user_profile.rIdentity(project.id)
    fund = Fund.objects.get(project=project)
    budget = list(Budget.objects.filter(fund=fund).order_by('year'))[0]
    if budget.capital_ratify_revision and budget.capital_ratify_revision != 0:
        project.budget_money = (budget.capital_ratify_revision or 0)
    else:
        project.budget_money = (budget.capital_ratify_budget or 0)
    duration_type = Option.objects.filter(swarm=u'duration_type').order_by('id')
    inspector_type = Option.objects.filter(swarm=u'inspector_type').order_by('id')
    ask_share = FRCMUserGroup.objects.filter(project=project, is_active=False)
    if len(inspectors) > 1 and group == '監造廠商': send_back_button = True
    elif len(contractors) > 1 and group == '營造廠商': send_back_button = True
    elif group == '協同主辦工程師': send_back_button = True
    else: send_back_button = False
    if group in ['負責主辦工程師', '自辦主辦工程師'] and FRCMUserGroup.objects.filter(group__name='協同主辦工程師', is_active=True, project=project):
        transfer_button = True
    else:
        transfer_button = False

    place = [TAIWAN] + list(Place.objects.filter(uplevel=TAIWAN).order_by('id'))
    contract_total = project.rContractTotalMoney()
    settlement_total = project.rSettlementTotalMoney()

    chase_one_by_one = project.countychaseprojectonebyone_set.get()

    countychasetime = list(CountyChaseTime.objects.all().order_by('id'))[-1]
    try:
        chase_data = CountyChaseProjectOneToMany.objects.get(countychasetime=countychasetime, project=project)
        chase_data.pastDay = (datetime.date.today() - countychasetime.chase_date).days
        try:
            last_chase_data = list(CountyChaseProjectOneToMany.objects.filter(project=project).exclude(countychasetime=countychasetime).order_by('countychasetime'))[-1]
        except: last_chase_data = False
    except:
        chase_data = False
        last_chase_data = False

    allocation = Allocation.objects.filter(project=project).order_by('date')

    if _ca(user=user, project='', project_id=0, right_type_value=u'使用縣市追蹤系統') or edit:
        chase_edit = True
    else:
        chase_edit = False

    t = get_template(os.path.join('frcm', 'profile.html'))
    html = t.render(RequestContext(R,{
        'chase_edit': chase_edit,
        'project': project,
        'edit': edit,
        'can_upload': can_upload,
        'files': files,
        'group': group,
        'engs': engs,
        'place_list': place,
        'contract_total': contract_total,
        'settlement_total': settlement_total,
        'send_back_button': send_back_button,
        'transfer_button': transfer_button,
        'ask_share': ask_share,
        'inspectors': inspectors,
        'contractors': contractors,
        'duration_type': duration_type,
        'inspector_type': inspector_type,
        'all_users': project.frcmusergroup_set.all(),
        'option' : _make_choose(),
        'fund': fund,
        'budget': fund.budget_set.all().order_by('year')[0],
        'allocation': allocation,
        'chase_data': chase_data,
        'last_chase_data': last_chase_data,
        'chase_one_by_one': chase_one_by_one,
        }))
    return HttpResponse(html)

@checkAuthority
def getProject(R, project, right_type_value= u'認領工程'):

    t = get_template(os.path.join('frcm', 'getproject.html'))
    html = t.render(RequestContext(R,{
        }))
    return HttpResponse(html)

@checkAuthority
def searchFRCMProject(R, project, right_type_value= u'menu2_搜尋遠端工程'):
    class searchFRCMForm(forms.Form):
        eng_name = forms.CharField(label='負責工程師', required=False)
        bid_no = forms.CharField(label='標案編號', required=False)
        name = forms.CharField(label='工作名稱', required=False)
        plans = [('', '全部')]
        for i in Plan.objects.filter(uplevel=None):
            plans.append((i.id, '---'*i.rLevelNumber() + i.name))
            for j in i.rSubPlanInList():
                plans.append((j.id, '---'*j.rLevelNumber() + j.name))
        plan = forms.ChoiceField(choices=plans, required=False, label='所屬計畫')
        search_type = [('cover', '　含下層計畫'), ('not', '不含下層計畫')]
        sub_type = forms.ChoiceField(choices=search_type, required=False, label='層級')
        years = [(y-1911, y-1911) for y in xrange(2006, TODAY().year+1)]
        years.insert(0, ('', '所有年度'))
        years.reverse()
        year = forms.ChoiceField(choices=years, required=False, label='年度')
        purchase_types = [('', '全部')] + [(type.id, type.value) for type in Option.objects.filter(swarm='purchase_type')]
        purchase_type = forms.ChoiceField(choices=purchase_types, required=False, label='採購類別：', help_text='(工程／勞務)')
        units = [('', '全部')]
        for i in Unit.fish_city_menu.all():
            units.append((i.id, i.name))
            if i.uplevel and i.uplevel.name != u'縣市政府':
                units.extend(
                    [(j.id, '---'+j.name) for j in i.uplevel_subunit.all()]
                )
        unit = forms.ChoiceField(choices=units, required=False, label='執行機關')


    user, DATA = R.user, readDATA(R)

    form = searchFRCMForm()
    projects_num = -1
    projects = []
    querystring = ''
    INFO = {}
    for k, v in R.GET.items(): INFO[k] = v
    for k, v in R.POST.items(): INFO[k] = v
    INFO['user'] = user
    if INFO.get('submit', None):
        form = searchFRCMForm(INFO)
        querystring = '&'.join(['%s=%s'%(k, v) for k, v in INFO.items() if k != 'page'])
        projects, projects_num = _searchFRCMProject(INFO)

    projects = [p.project for p in projects]
    for i in projects:
        try:
            i.importuser = FRCMUserGroup.objects.get(group__name='負責主辦工程師', project=i).user.user_profile.rName()
            try:
                FRCMUserGroup.objects.get(user=user, project=i)
                i.inlist = True
            except:
                i.inlist = False
        except:
            try:
                i.importuser = FRCMUserGroup.objects.get(group__name='自辦主辦工程師', project=i).user.user_profile.rName()
                try:
                    FRCMUserGroup.objects.get(user=user, project=i)
                    i.inlist = True
                except:
                    i.inlist = False
            except:
                pass
        i.engs = [(str(u.group.name[0:2])+":"+str(u.user.user_profile.rName())) for u in FRCMUserGroup.objects.filter(project=i, group__name__in=['負責主辦工程師', '協同主辦工程師', '自辦主辦工程師'])]

    t = get_template(os.path.join('frcm', 'searchfrcm.html'))
    html = t.render(RequestContext(R,{
        'form':form,
        'projects': projects,
        'sortBy': INFO.get('sortBy', None) or 'year',
        'page_list': makePageList(INFO.get('page', 1), projects_num, NUMPERPAGE),
        'querystring': querystring,
        'projects_num': projects_num,
        }))
    return HttpResponse(html)

def _searchFRCMProject(INFO):
    if '_' in INFO['user'].username and not INFO['user'].is_staff:
        city_account = User.objects.get(username=INFO['user'].username.split('_')[0]+'_account')
        result = FRCMUserGroup.objects.filter(project__deleter=None, group__name__in=['負責主辦工程師', '自辦主辦工程師'], project__unit__name__contains=city_account.user_profile.unit.name[0:3]).order_by('project__'+INFO.get('sortBy', None))
    else:
        result = FRCMUserGroup.objects.filter(project__deleter=None, group__name__in=['負責主辦工程師', '自辦主辦工程師']).order_by('project__'+INFO.get('sortBy', None))

    if INFO.get('eng_name', None) != '':
        name_str = unicode(INFO.get('eng_name', None))
        if len(name_str) == 3:
            last_name = name_str[0]
            first_name = name_str[1:3]
            result = result.filter((Q(user__last_name__startswith=last_name)&Q(user__first_name__contains=first_name))|Q(user__first_name__contains=name_str))
        elif len(name_str) == 2:
            last_name = name_str[0]
            first_name = name_str[1]
            result = result.filter((Q(user__last_name__startswith=last_name)&Q(user__first_name__contains=first_name))|Q(user__last_name=name_str)|Q(user__first_name=name_str))
        elif len(name_str) == 1:
            result = result.filter(Q(user__last_name__contains=name_str)|Q(user__first_name__contains=name_str))
        else:
            last_name = name_str[0]
            first_name = name_str[-2:]
            result = result.filter(user__last_name__contains=last_name, user__first_name__contains=first_name)

    if INFO.get('bid_no', None) != '':
        ids = []
        for bid_no in re.split('[ ,]+', INFO.get('bid_no', None)):
            ids.extend([i.id for i in result.filter(project__bid_no__icontains=bid_no)])
        result = result.filter(id__in=ids)

    if INFO.get('name', None) != '':
        ids = []
        for name in re.split('[ ,]+', INFO.get('name', None)):
            ids.extend([i.id for i in result.filter(project__name__icontains=name)])
        result = result.filter(id__in=ids)

    if INFO.get('plan', None) != '':
        plan = Plan.objects.get(id=INFO.get('plan', None))
        if INFO.get('sub_type', None) == 'cover':
            plan_ids = [plan.id] + [i.id for i in Plan.objects.get(id=INFO.get('plan', None)).rSubPlanInList()]
            result = result.filter(project__plan__id__in=plan_ids)
        else:
            result = result.filter(project__plan = plan)

    if INFO.get('year', None) != '':
        result_ids = [s.project.id for s in result]
        project_ids = [p.id for p in Project.objects.filter(id__in=result_ids, year=INFO.get('year', None))]
        result = result.filter(project__id__in=project_ids)

    if INFO.get('purchase_type', None) != '':
        result = result.filter(project__purchase_type__id=INFO.get('purchase_type', None))

    if INFO.get('unit', None) != '':
        unit = Unit.objects.get(id=INFO.get('unit', None))
        result = result.filter(project__unit=unit)


    if not INFO.get('page', None): page = 1
    else: page = int(INFO['page'])

    projects = []
    result_num = result.count()
    for order, u in enumerate(result[(page-1)*NUMPERPAGE:page*NUMPERPAGE]):
        u.order = int((page-1)*NUMPERPAGE+order+1)
        projects.append(u)

    return projects, result_num


@checkAuthority
def mFiles(R, **kw):
    user, DATA = R.user, R.POST
    place_list = [TAIWAN] + list(Place.objects.filter(uplevel=TAIWAN).order_by('id'))

    if user.user_profile.group.name in ['主辦工程師', '上層管理者', '管考填寫員']:
        right = True
    else:
        right = False

    if user.username[1] == '_':
        right = False

    if user.is_staff:
        right = True

    if R.POST.get('submit', ''):
        file = R.FILES.get('file', None)
        place = Place.objects.get(id=DATA.get('place',''))
        location = DATA.get('location','')
        filename = DATA.get('name','')
        memo = DATA.get('memo','')
        try:
            lng = decimal.Decimal(str(DATA.get('lng','')))
            lat = decimal.Decimal(str(DATA.get('lat','')))

        except:
            lng = None
            lat = None
        if filename == '':
            filename = str(file.name)

        row = CityFiles(
                    name = filename,
                    memo = memo,
                    place = place,
                    location = location,
                    upload_user = user,
                    upload_date = TODAY(),
                    file = file,
                    lat = lat,
                    lng = lng,
                    )
        row.save()

        try:
            ext = file.name.split('.')[-1]
        except:
            ext = 'zip'
        if ext in ['jpg', 'jpeg', 'tiff', 'tif', 'png', 'gif']:
            thumb(row.file.name, "width=1024,height=768")

        getattr(row, 'file').save('%s.%s'%(row.id, ext), file)
        row.save()

    lately_files = CityFiles.objects.all().order_by('upload_user', '-upload_date', '-id')[0:20]
    all_files = CityFiles.objects.all().order_by('place__id')
    city_list = []
    cities = []
    for f in all_files:
        if f.place.id not in cities:
            cities.append(f.place.id)
            city_list.append([f.place.id, f.place.name, 1])
        else:
            city_list[cities.index(f.place.id)][2] += 1

    t = get_template(os.path.join('frcm', 'filesmp.html'))
    html = t.render(RequestContext(R,{'place_list': place_list, 'lately_files': lately_files, 'right': right, 'city_list': city_list, 'page': 'upload'}))
    return HttpResponse(html)


@checkAuthority
def mCityFiles(R, **kw):
    user, DATA = R.user, R.POST
    place = Place.objects.get(id=kw['place_id'])
    page = place.id

    if user.user_profile.group.name in ['主辦工程師', '上層管理者', '管考填寫員']:
        right = True
    else:
        right = False

    if user.username[1] == '_':
        right = False

    if user.is_staff:
        right = True

    lately_files = CityFiles.objects.filter(place=place).order_by('upload_user', '-upload_date', '-id')
    all_files = CityFiles.objects.all().order_by('place__id')
    city_list = []
    cities = []
    for f in all_files:
        if f.place.id not in cities:
            cities.append(f.place.id)
            city_list.append([f.place.id, f.place.name, 1])
        else:
            city_list[cities.index(f.place.id)][2] += 1


    if R.POST.get('submit', ''):
        file = R.FILES.get('file', None)
        place = place
        location = DATA.get('location','')
        filename = DATA.get('name','')
        memo = DATA.get('memo','')
        try:
            lng = decimal.Decimal(str(DATA.get('lng','')))
            lat = decimal.Decimal(str(DATA.get('lat','')))

        except:
            lng = None
            lat = None
        if filename == '':
            filename = str(file.name)

        row = CityFiles(
                    name = filename,
                    memo = memo,
                    place = place,
                    location = location,
                    upload_user = user,
                    upload_date = TODAY(),
                    file = file,
                    lat = lat,
                    lng = lng,
                    )
        row.save()

        try:
            ext = file.name.split('.')[-1]
        except:
            ext = 'zip'
        if ext in ['jpg', 'jpeg', 'tiff', 'tif', 'png', 'gif']:
            thumb(row.file.name, "width=1024,height=768")

        getattr(row, 'file').save('%s.%s'%(row.id, ext), file)
        row.save()

    t = get_template(os.path.join('frcm', 'cityfilesmp.html'))
    html = t.render(RequestContext(R,{'lately_files': lately_files, 'right': right, 'city_list': city_list, 'place': place}))
    return HttpResponse(html)


@checkAuthority
def ReadAndEditCountyChase(R, project, right_type_value=u'使用縣市追蹤系統', **kw):
    from project.views import sort_By_South
    user, DATA = R.user, readDATA(R)

    city_account = User.objects.get(username=user.username.split('_')[0]+'_account')
    projects = Project.objects.filter(deleter=None, unit__name__contains=city_account.user_profile.unit.name[0:3]).order_by('name')

    countychasetime = list(CountyChaseTime.objects.all().order_by('id'))[-1]
    countychasetime.time = CountyChaseTime.objects.all().count()
    countychasetime.pastDay = (datetime.date.today() - countychasetime.chase_date).days
    countychasetime.num = CountyChaseProjectOneToMany.objects.filter(countychasetime=countychasetime).count()

    places = [Place.objects.get(name=city_account.user_profile.unit.name[0:3])]

    places = sort_By_South(places, countychasetime)

    place = places[-1]

    t = get_template(os.path.join('frcm', 'readandeditcountychase.html'))
    html = t.render(RequestContext(R,{
        'place': place,
        'countychasetime': countychasetime,
        }))
    return HttpResponse(html)

@checkAuthority
def reDraftProject(R, project, right_type_value=u'menu2_匯出報表', **kw):
    if R.user.username[1] == '_':
        place = Place.objects.filter(name__icontains=R.user.user_profile.unit.name[:2])
    else:
        place = [TAIWAN] + list(Place.objects.filter(uplevel=TAIWAN).order_by('id'))
    units = []
    if R.user.is_staff or R.user.user_profile.group.name == '管考填寫員':
        power = True
        for i in Unit.fish_city_menu.all():
            units.append((i.id, i.name))
            if i.uplevel and i.uplevel.name != u'縣市政府':
                units.extend(
                    [(j.id, '---'+j.name) for j in i.uplevel_subunit.all()]
                )
    else:
        power = False
        units.append([R.user.user_profile.unit.id, R.user.user_profile.unit.name])
    years = [y-1911 for y in xrange(2006, TODAY().year+2)]
    years.reverse()
    carry_info = {}
    try:
        for i in kw['dictionary_str'].split('+'):
            k, v = i.split(':')
            if k == 'plan_id':
                carry_info[k] = int(v)
            else:
                carry_info[k] = v
    except: pass
    max_level = 0

    all_plans = []
    for i in Plan.objects.filter(uplevel=None):
        all_plans.append({'id':i.id, 'name':i , 'level':i.rLevelNumber(), 'serial':i.project_serial, 'code':i.code, 'up_code':'000'})
        for j in i.rSubPlanInList():
            all_plans.append({'id':j.id, 'name':'---'*j.rLevelNumber() + j.name, 'level':j.rLevelNumber(), 'serial':j.project_serial, 'code':j.code, 'up_code':j.uplevel.code})
            if j.rLevelNumber() > max_level:
                max_level = j.rLevelNumber()

    if R.user.username[1] == '_':
        projects = Draft_Project.objects.filter(type__value='縣市提案草稿', place__name__icontains=R.user.user_profile.unit.name[:2]).order_by('place', 'sort')
    else:
        projects = Draft_Project.objects.filter(type__value='縣市提案草稿').order_by('place', 'sort')

    for p in projects:
        if p.project_type.value == '1 漁港工程':
            p.port = p.fishing_port.all()
        else:
            p.port = p.aquaculture.all()
    project_sub_types = Option.objects.filter(swarm='port_type').order_by('id')
    project_type_sorts = Option.objects.filter(swarm='project_type_sort').order_by('value')
    budget_sub_types = Option.objects.filter(swarm='budget_sub_type').order_by('id')
    farm_types = Option.objects.filter(swarm='farm_type').order_by('id')
    html_sort = '<option value="">請先選擇縣市</option>'

    t = get_template(os.path.join('project', 'draft_projects.html'))
    html = t.render(RequestContext(R,{
        'plans' : all_plans, 'projects': projects, 'page_title': '縣市提案', 'url': '/frcm/add_draft/',
        'project_sub_types' : project_sub_types, 'farm_types': farm_types, 'max_level' : max_level, 'years' : years, 'power': power,
        'this_year': int(TODAY().year - 1911), 'units' : units, 'years' : years, 'project_type_sorts': project_type_sorts, 'html_sort': html_sort,
        'place_list' : place, 'option' : _make_choose(), 'budget_sub_types': budget_sub_types, 'type': '縣市提案草稿'
        }))
    return HttpResponse(html)


@checkAuthority
def unit_no(R, project, right_type_value=u'menu2_匯出報表', **kw):
    if not R.user.is_staff:
        return HttpResponseRedirect('/')

    units = Unit.objects.filter(name__icontains=u'尚未解析').order_by('id')

    t = get_template(os.path.join('frcm', 'unit_no.html'))
    html = t.render(RequestContext(R,{
        'units': units,
        }))
    return HttpResponse(html)


@checkAuthority
def unit_no(R, project, right_type_value=u'menu2_匯出報表', **kw):
    if not R.user.is_staff:
        return HttpResponseRedirect('/')

    units = Unit.objects.filter(name__icontains=u'尚未解析').order_by('id')

    t = get_template(os.path.join('frcm', 'unit_no.html'))
    html = t.render(RequestContext(R,{
        'units': units,
        }))
    return HttpResponse(html)

#結案通報(email)
@login_required
def send_email(R):
    date = R.POST.get('date', '')
    project_id = R.POST.get('id', '')
    project = Project.objects.get(id=project_id)

    try:
        smtpserver = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
        # smtpserver.ehlo()
        # smtpserver.starttls()
        smtpserver.ehlo()
        #登入系統
        smtpserver.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)

        #寄件人資訊
        fromaddr = settings.EMAIL_HOST_USER

        #收件人列表，格式為list即可
        #toaddrs = [i]
        toaddrs = [u'kuti8733@gmail.com',u'meixiu0502@ms1.fa.gov.tw']
      
        msg = MIMEMultipart()
        msg['From']=fromaddr
        msg['To']=COMMASPACE.join(toaddrs)
        msg['Date']=formatdate(localtime=True)
        msg['Subject']=u'漁業署FES工程管理-《結案通報》'

        #你要寫的內容
        info = u''
        info += u'<br>您好，這封信由系統自動寄出，請勿回信<br><br>'
        info += u'需結案的工程如下：<br>'
        info += u'<ul>'
        info += u'<li><a href="https://fes.fa.gov.tw/project/project_profile/%s/" target="_blank">%s年度-%s</a></li>' % (project.id, project.year, project.name)
        info += u'</ul>'
        info += u'需結案的日期為:%s<br>' % (date)
        info += u'通報者:%s<br>' % (R.user.last_name + R.user.first_name)
        info += u'通報者電話:%s<br>' % (R.user.user_profile.phone)
        info += u'通報者信箱:%s' % (R.user.email)

        def containsnonasciicharacters(str):
            return not all(ord(c) < 128 for c in str)

        if containsnonasciicharacters(info):
            htmltext = MIMEText(info.encode('utf-8', 'replace'), 'html','utf-8')
        else:
            htmltext = MIMEText(info, 'html')

        msg.attach(htmltext)

        smtpserver.sendmail(fromaddr, toaddrs, msg.as_string())

        #記得要登出
        smtpserver.quit()
    except:
        pass
    return HttpResponse(status=204)

#需新增工程案通報(email)
@login_required
def report_name(R):
    project = R.POST.get('project', '')
    date = R.POST.get('check_date', '')

    try:
        smtpserver = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
        # smtpserver.ehlo()
        # smtpserver.starttls()
        smtpserver.ehlo()
        #登入系統
        smtpserver.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)

        #寄件人資訊
        fromaddr = settings.EMAIL_HOST_USER

        #收件人列表，格式為list即可
        #toaddrs = [i]
        #toaddrs = [u'a38269412@gmail.com']
        toaddrs = [u'kuti8733@gmail.com',u'meixiu0502@ms1.fa.gov.tw']
       
        msg = MIMEMultipart()
        msg['From']=fromaddr
        msg['To']=COMMASPACE.join(toaddrs)
        msg['Date']=formatdate(localtime=True)
        msg['Subject']=u'漁業署FES工程管理-《需新增工程案通報》'

        #你要寫的內容
        info = u''
        info += u'<br>您好，這封信由系統自動寄出，請勿回信<br><br>'
        info += u'需新增工程案如下：<br>'
        info += u'<ul>'
        info += u'%s' % (project)
        info += u'</ul><br>'
        info += u'核定日期為：%s<br>' % (date)
        info += u'通報者:%s<br>' % (R.user.last_name + R.user.first_name)
        info += u'通報者電話:%s<br>' % (R.user.user_profile.phone)
        info += u'通報者信箱:%s' % (R.user.email)

        def containsnonasciicharacters(str):
            return not all(ord(c) < 128 for c in str)

        if containsnonasciicharacters(info):
            htmltext = MIMEText(info.encode('utf-8', 'replace'), 'html','utf-8')
        else:
            htmltext = MIMEText(info, 'html')

        msg.attach(htmltext)

        smtpserver.sendmail(fromaddr, toaddrs, msg.as_string())

        #記得要登出
        smtpserver.quit()
    except:
        pass
    return HttpResponse(status=204)

#得標金額 資料計算
@login_required
def statisticstable_money_data(R):
    #int(NOW().year - 1911)
    year = R.POST.get('year', '')
    #柱狀圖-廠商得標金額排行
    tmp = []
    case_list = []

    project = Project.objects.filter(year=year, deleter_id=None).order_by('-id')
    project_money = {}
    data_case = {}
    for p in project:
        #工程契約金額
        version = Version.objects.filter(project__id = p.id).first()
        if p.pcc_no:
            try:
                pcc_project = PCC_Project.objects.get(uid = p.pcc_no)
                if not pcc_project.decide_tenders_price2 or pcc_project.decide_tenders_price2 == 0:
                    engs_price = int(pcc_project.decide_tenders_price)
                else:
                    engs_price = int(pcc_project.decide_tenders_price2)
            except:
                engs_price =  0
        elif version and version.engs_price:
            engs_price = int(version.engs_price)
        elif p.construction_bid:
            engs_price = int(p.construction_bid)
        elif p.total_money:
            engs_price = int(p.total_money)
        else:
            engs_price =  0
        #以萬元做計算
        engs_price = int(engs_price / 10000)
        #營造廠商
        contractors = [u.user.id for u in FRCMUserGroup.objects.filter(group__name=u'營造廠商', project=p)]
        unit_id = UserProfile.objects.get(user_id = contractors[0]).unit_id if contractors != [] else None
        try:
            unit = EngProfile.objects.get(project=p).contractor_name
        except:
            unit = None
        if not unit:
            unit = Unit.objects.get(id = unit_id).fullname if unit_id else None
        if not unit:
            unit = p.bid_final
        if engs_price != 0 and unit:
            try:
                if project_money[unit]:
                    for i in project_money.keys():
                        if unit[0] + unit[1] in i:
                            project_money[unit] += engs_price
                            data_case[unit] += 1
            except:
                project_money.setdefault(unit, engs_price)
                data_case.setdefault(unit, 1)
                    
    project_money = sorted(project_money.items(), key=lambda x:x[1])
    #data_case = sorted(data_case.items(), key=lambda x:x[1])
    for i in project_money[-10:]:
        tmp.append([i[1], i[0]])
        case_list.append(data_case[i[0]])

    case_list.reverse()
    tmp.sort()
    tmp.reverse()

    data = {
            'labels': [],
            'datasets': [
                {
                    'label': u'累計金額(萬元)',
                    'backgroundColor': '#5B79FF',
                    'borderWidth': 1,
                    'data': []
                }
            ]
        }
    
    for t in tmp:
        data['labels'].append(u'%s' % t[1])
        data['datasets'][0]['data'].append(t[0])

    total_num = sum(data['datasets'][0]['data'])
    right_max_num = max(data['datasets'][0]['data'])
    while right_max_num % 5000 != 0:
        right_max_num += 1
    left_max_num = math.ceil(right_max_num*100. / total_num)
    
    
    return HttpResponse(json.dumps({'status': True, 'data': data, 'left_max_num': left_max_num, 'right_max_num': right_max_num, 'case_list': case_list}))

@login_required
def statisticstable_money(R):
    years = [y-1911 for y in xrange(2009, TODAY().year+1)]
    years.reverse()

    t = get_template(os.path.join('frcm', 'zh-tw', 'statisticstable_money.html'))
    html = t.render(RequestContext(R,{
            'user': R.user,
            'years': years,
            'subpage_name': u'廠商得標金額排行',
            'toppage_name': u'遠端管理系統',
        }))
    return HttpResponse(html)



def unit_search(R, **kw):
    id = kw['id']
    unit = Unit.objects.get(id=id)
    birthday = unit.birthday
    if(birthday!=None):
        birthday = unit.birthday.strftime('%Y-%m-%d')
    d = {
        'id': unit.id,
        'name': unit.name,
        'fullname': unit.fullname,
        'no': unit.no,
        'chairman': unit.chairman,
        'capital': unit.capital,
        'birthday': birthday,
        'operation': unit.operation,
        'address': unit.address,
        'phone': unit.phone,
        'fax': unit.fax,
        'website': unit.website,
        'email': unit.email,
        'uplevel':unit.uplevel_id,
    }

    return HttpResponse(json.write(d))

def unit_edit(R, **kw):
    id = kw['id']
    unit = Unit.objects.get(id=id)    
    is_exec = kw['isexec']
    if is_exec == 'true':
        unit.uplevel_id = 6
    else:
        unit.uplevel_id = 99
    unit.save()
    return HttpResponse(json.write([]))

def unit_create(R):
    data = json.loads(R.body)
    if data['capital']=='' and data['birthday']=='':
        unit = Unit.objects.create(place_id=1, no=str(data['no']), chairman=str(data['chairman']), name=str(data['name']), fullname=str(data['fullname']), address=str(data['address']), operation=str(data['operation']), phone=str(data['phone']), fax=str(data['fax']), website=str(data['website']), email=str(data['email']), uplevel_id=int(data['exec']))
    elif data['capital']=='':
        unit = Unit.objects.create(place_id=1, no=str(data['no']), chairman=str(data['chairman']), name=str(data['name']), fullname=str(data['fullname']), address=str(data['address']), birthday=str(data['birthday']), operation=str(data['operation']), phone=str(data['phone']), fax=str(data['fax']), website=str(data['website']), email=str(data['email']), uplevel_id=int(data['exec']))
    elif data['birthday']=='':
        unit = Unit.objects.create(place_id=1, no=str(data['no']), chairman=str(data['chairman']), name=str(data['name']), fullname=str(data['fullname']), address=str(data['address']), capital=int(data['capital']), operation=str(data['operation']), phone=str(data['phone']), fax=str(data['fax']), website=str(data['website']), email=str(data['email']), uplevel_id=int(data['exec']))
    else:
        unit = Unit.objects.create(place_id=1, no=str(data['no']), chairman=str(data['chairman']), name=str(data['name']), fullname=str(data['fullname']), address=str(data['address']), capital=int(data['capital']), birthday=str(data['birthday']), operation=str(data['operation']), phone=str(data['phone']), fax=str(data['fax']), website=str(data['website']), email=str(data['email']), uplevel_id=int(data['exec']))
    
    unit.save()
    return HttpResponse(json.write({'status': 'success'}))