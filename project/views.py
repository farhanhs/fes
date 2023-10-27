# -*- coding: utf-8 -*-
# Create your views here.
if __name__ == '__main__':
    import sys, os
    sys.path.append(os.path.join(os.path.dirname(__file__), '../../../cim'))
    import settings
    from django.core.management import setup_environ
    setup_environ(settings)

from django.core.cache import cache
from django.core.mail import send_mail
from django.template.loader import get_template
from django.template import Context, RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import auth
from django.db.models import Q
from django.db.utils import DatabaseError
from django import forms
from django.contrib.auth.models import User, Group
from django.contrib.sessions.models import Session
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.forms import ModelForm
from django.views.decorators.csrf import csrf_exempt

from django.core.serializers.json import DjangoJSONEncoder

from common.models import Log
from general.models import Place, Unit
from common.lib import find_sub_level, find_sub, nocache_response, md5password, readDATA, verifyOK, makePageList, makeFileByWordExcel
from fishuser.models import Option
from fishuser.models import UserProfile
from fishuser.models import LoginHistory
from fishuser.models import WrongLogin
from fishuser.models import DocumentOfProjectModels
from fishuser.models import Plan, PlanReserve
from fishuser.models import PlanBudget
from fishuser.models import Budget
from fishuser.models import Draft_Project
from fishuser.models import Project
from fishuser.models import ProjectBidMoney
from fishuser.models import Project_Port
from fishuser.models import DefaultProject
from fishuser.models import FRCMUserGroup
from fishuser.models import Factory
from fishuser.models import Reserve
from fishuser.models import FundRecord
from fishuser.models import Fund
from fishuser.models import Appropriate
from fishuser.models import Allocation
from fishuser.models import Progress
from fishuser.models import RelayInfo
from fishuser.models import ScheduledProgress
from fishuser.models import ProjectPhoto
from fishuser.models import FRCMTempFile
from fishuser.models import _getProjectStatusInList
from fishuser.models import _ca
from fishuser.models import CountyChaseTime
from fishuser.models import CountyChaseProjectOneByOne
from fishuser.models import CountyChaseProjectOneToMany
from fishuser.models import Project_Secret_Memo
from fishuser.models import DocumentFile
from fishuser.models import CencelLoginEmail
from fishuser.views import checkAuthority
from fishuser.models import ManageMoney, ProjectManageMoney, ManageMoneyRemain
from fishuser.models import ProjectBidMoneyVersion, ProjectBidMoneyVersionDetail

from project.models import Option2
from project.models import RecordProjectProfile
from project.models import ExportCustomReport
from project.models import ReportField
from project.models import ExportCustomReportField
from project.lib import make_chase_excel_file, make_custom_report_excel_file, make_project_manage_money_excel, make_control_form_excel_file, make_port_engineering_excel_file

from harbor.models import FishingPort
from harbor.models import Aquaculture

from dailyreport.models import EngProfile

from gallery.models import Photo
from engphoto.models import Photo as Old_Photo

from pccmating.sync import syncPccInformation
from pccmating.sync import getProjectInfo
from pccmating.models import Project as PCCProject
from pccmating.models import ProjectProgress as PCCProgress
from pccmating.sexual_assault_against_pcc.famhandler import FishMoney


from django.conf import settings
CAN_VIEW_BUG_PAGE_IPS = settings.CAN_VIEW_BUG_PAGE_IPS
NUMPERPAGE = settings.NUMPERPAGE
ROOT = settings.ROOT

import os, random, json, re, datetime
import xlsxwriter
from cStringIO import StringIO

import sys
reload(sys)
sys.setdefaultencoding("utf8")

if not hasattr(json, "write"):
    #for python2.6
    json.write = json.dumps
    json.read = json.loads

#from PIL.Image import split
import decimal
import calendar
import base64
from copy import copy
from readjson import readJson

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
units = []
for i in Unit.fish_city_menu.all():
    units.append(i)
    if i.uplevel and i.uplevel.name != u'縣市政府':
        units.extend(
            [j for j in i.uplevel_subunit.all()])
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


#我的追蹤工程
@login_required
def default_project(R):
    default_projects = []
    for dp in DefaultProject.objects.filter(user=R.user).order_by('project__place', '-id'):
        if dp.project not in default_projects:
            try:
                dp.project.importer = dp.project.frcmusergroup_set.get(group__name__in=[u'負責主辦工程師', u'自辦主辦工程師']).user.user_profile.rName()
            except:
                dp.project.importer = ''
            default_projects.append(dp.project)


    t = get_template(os.path.join('project', 'zh-tw', 'default_project.html'))
    html = t.render(RequestContext(R,{
        'user': R.user,
        'years': years,
        'default_projects': default_projects,
        'this_year': this_year,
        'option': _make_choose(),
        'toppage_name': u'工程管考系統',
        'subpage_name': u'追蹤工程',
        }))
    return HttpResponse(html)


#計畫列表
@login_required
def plan_list(R):
    if not R.user.has_perm('fishuser.sub_menu_management_system_plan'):
        # 沒有 "第二層選單_工程管考系統_計畫列表"
        return HttpResponseRedirect('/')

    if R.user.has_perm('fishuser.edit_all_project_in_management_system'):
        edit = True
    else:
        edit = False


    top_plan = Plan.objects.get(uplevel=None)
    plans = [top_plan] + top_plan.rSubPlanInList()
    pp=[top_plan]
    sub_plans1 = Plan.objects.filter(uplevel=top_plan.id)
    sub_plans1 = sorted(sub_plans1, key=lambda sub_plans1: -sub_plans1.year)
    for p1 in sub_plans1:  
        pp.append(p1) 
        sub_plans2 = Plan.objects.filter(uplevel=p1.id)
        sub_plans2 = sorted(sub_plans2, key=lambda sub_plans2: -sub_plans2.year)
        for p2 in sub_plans2:
            pp.append(p2)
            sub_plans3 = Plan.objects.filter(uplevel=p2.id)
            sub_plans3 = sorted(sub_plans3, key=lambda sub_plans3: -sub_plans3.year)
            for p3 in sub_plans3:
                pp.append(p3)
                sub_plans4 = Plan.objects.filter(uplevel=p3.id)
                sub_plans4 = sorted(sub_plans4, key=lambda sub_plans4: -sub_plans4.year)
                pp = pp + sub_plans4
     
    class_names = ['danger', 'info', 'success', 'warning']
    for i in pp:
        i.front_tag = i.rLevelNumber()
        i.back_tag = 12 - i.rLevelNumber()
        i.class_name = class_names[i.rLevelNumber()] if i.rLevelNumber() < len(class_names) else class_names[-1]
    
    year_month = []
    engineering_year = os.listdir('/var/www/fes/apps/project/exceltemp')    
    for year in engineering_year:
        month_files = os.listdir('/var/www/fes/apps/project/exceltemp/%s'%year)
        for month_file in month_files:
            month = month_file.replace('month_', '').replace('.xlsx', '')
            year_month.append(year + '_' + month)
            
    #plans = sorted(plans, key=lambda plans: -plans.year)
    t = get_template(os.path.join('project', 'zh-tw', 'plan_list.html'))
    html = t.render(RequestContext(R,{
        'user': R.user,
        'years': years,
        'edit': edit,
        'plans': pp,
        'this_year': this_year,
        'option': _make_choose(),
        'engineering_year': engineering_year,
        'year_month': json.dumps(year_month), 
        'toppage_name': u'工程管考系統',
        'subpage_name': u'計畫列表',
        }))
    return HttpResponse(html)

def plan_query(R, **kw):
    plan_id = kw['plan_id']
    year = kw['year']
    top_plan = Plan.objects.get(uplevel=None)
    top_plans_id = [top_plan.id]
    
    if(plan_id=='0' and year=='0'):
        plans_id = []
        plans = Plan.objects.all()
        for p in plans:
            if(p.id in top_plans_id or p.uplevel_id in top_plans_id):
                continue
            plans_id.append(p.id)
        d = {}
        d['ids'] = plans_id
        return HttpResponse(json.write(d))

    if(plan_id=='0'):
        plans_id = []
        plans = Plan.objects.filter(year=year)
        for p in plans:
            if(p.id in top_plans_id or p.uplevel_id in top_plans_id):
                continue
            plans_id.append(p.id)
        d = {}
        d['ids'] = plans_id
        return HttpResponse(json.write(d))
    
    if(year=='0'):
        plans_id = []
        sub_plans1 = Plan.objects.filter(uplevel=plan_id)
        for p1 in sub_plans1:
            plans_id.append(p1.id)
            sub_plans2 = Plan.objects.filter(uplevel=p1.id)
            for p2 in sub_plans2:
                plans_id.append(p2.id)
                sub_plans3 = Plan.objects.filter(uplevel=p2.id)
                for p3 in sub_plans3:
                    plans_id.append(p3.id)
                    sub_plans4 = Plan.objects.filter(uplevel=p3.id)
                    for p4 in sub_plans4:
                        plans_id.append(p4.id)
        for id in plans_id:
            check = Plan.objects.get(id=id)
            if check.uplevel_id in top_plans_id:
                plans_id.remove(id)
        d={}
        d['ids'] = plans_id
        return HttpResponse(json.write(d))

    plans_id = []
    sub_plans1 = Plan.objects.filter(uplevel=plan_id)
    for p1 in sub_plans1:
        if(str(p1.year)==year): 
            plans_id.append(p1.id)
        sub_plans2 = Plan.objects.filter(uplevel=p1.id)
        for p2 in sub_plans2:
            if(str(p2.year)==year):
                plans_id.append(p2.id)
            sub_plans3 = Plan.objects.filter(uplevel=p2.id)
            for p3 in sub_plans3:
                if(str(p3.year)==year):
                    plans_id.append(p3.id)
                sub_plans4 = Plan.objects.filter(uplevel=p3.id)
                for p4 in sub_plans4:
                    if(str(p4.year)==year):
                        plans_id.append(p4.id)
    
    for id in plans_id:
        check = Plan.objects.get(id=id)
        if check.uplevel_id in top_plans_id:
            plans_id.remove(id)

    d={}
    d['ids'] = plans_id

    return HttpResponse(json.write(d))



@login_required
def plan_type_edit(R):
    if not R.user.has_perm('fishuser.sub_menu_management_system_plan'):
        # 沒有 "第二層選單_工程管考系統_計畫列表"
        return HttpResponseRedirect('/')

    if R.user.has_perm('fishuser.edit_all_project_in_management_system'):
        edit = True
    else:
        edit = False

    types=Option.objects.filter(swarm='plan_class').all()
    top_plan = Plan.objects.get(uplevel=None)
    plans = [top_plan] + top_plan.rSubPlanInList()
    class_names = ['danger', 'info', 'success', 'warning']
    for i in plans:
        i.front_tag = i.rLevelNumber()
        i.back_tag = 12 - i.rLevelNumber()
        i.class_name = class_names[i.rLevelNumber()] if i.rLevelNumber() < len(class_names) else class_names[-1]

    t = get_template(os.path.join('project', 'zh-tw', 'plan_type_edit.html'))
    html = t.render(RequestContext(R,{
        'types': types,
        'user': R.user,
        'years': years,
        'edit': edit,
        'plans': plans,
        'this_year': this_year,
        'option': _make_choose(),
        'toppage_name': u'工程管考系統',
        'subpage_name': u'計畫列表',
        }))
    return HttpResponse(html)

#新增計畫類別
def create_plan_type(R, **kw):
    value = kw['value']
    try:
        test = Option.objects.create(swarm='plan_class', value=value)
        test.save()
        return HttpResponse(json.write({'status': 'success'}))
    except:
        return HttpResponse(json.write({'status': '類別已存在'}))

#刪除計畫類別
def delete_plan_type(R, **kw):
    id = kw['id']
    test = Option.objects.get(value=id)
    plans = Plan.objects.filter(plan_class=test.id)
    l=len(plans)
    plan_name = []
    for i in range(l):
        plan_name.append(plans[i].name)
    if l==0:
        test.delete()
        return HttpResponse(json.write({'status': 'success'}))
    else:
        print(123)
        return HttpResponse(json.write({'status': '有使用中的計畫', 'plans': plan_name})) 
    print(345)
# 計畫列表-取得計畫資訊
@login_required
def get_plan_info(R):
    if not R.user.has_perm('fishuser.sub_menu_management_system_plan'):
        # 沒有 "第二層選單_工程管考系統_計畫列表"
        return HttpResponseRedirect('/')

    if R.user.has_perm('fishuser.edit_all_project_in_management_system'):
        edit = True
    else:
        edit = False

    projects = Project.objects.all()
    plan = Plan.objects.get(id=R.POST.get('row_id', ''))
    budgets = PlanBudget.objects.filter(plan=plan).order_by('year')
    reserves = PlanReserve.objects.filter(plan=plan).order_by('year')
    for b in budgets:
        b.sum_budget = b.read_sum_budget()


    t = get_template(os.path.join('project', 'zh-tw', 'plan_list_info.html'))
    html = t.render(RequestContext(R,{
        'user': R.user,
        'years': years,
        'edit': edit,
        'p': plan,
        'projects': projects,
        'budgets': budgets,
        'reserves': reserves,
        'this_year': this_year,
        'option': _make_choose()
        }))
    return HttpResponse(json.dumps({'html': html}))


# 計畫列表-新增計畫
@login_required
def create_plan(R):
    if not R.user.has_perm('fishuser.sub_menu_management_system_create'):
        # 沒有 "第二層選單_工程管考系統_新增工程"
        return HttpResponseRedirect('/')

    uplevel = Plan.objects.get(id=R.POST.get('row_id', ''))
    if uplevel.rSubPlanInList():
        sort = str(float(str(uplevel.rSubPlanInList()[-1].sort)) + 1)
        insert_after = uplevel.rSubPlanInList()[-1].id
    else:
        sort = '1'
        insert_after = uplevel.id
    plan = Plan(
            name = R.POST.get('name', ''),
            uplevel = uplevel,
            sort = sort,
        )
    plan.save()
    class_names = ['danger', 'info', 'success', 'warning']
    plan.front_tag = plan.rLevelNumber()
    plan.back_tag = 12 - plan.rLevelNumber()
    plan.class_name = class_names[plan.rLevelNumber()] if plan.rLevelNumber() < len(class_names) else class_names[-1]

    t = get_template(os.path.join('project', 'zh-tw', 'plan_list_create.html'))
    html = t.render(RequestContext(R,{
        'user': R.user,
        'years': years,
        'edit': True,
        'p': plan,
        'this_year': this_year,
        'option': _make_choose()
        }))
    return HttpResponse(json.dumps({'html': html, 'row_id': plan.id, 'insert_after': insert_after}))


#計畫列表-製造排序選擇表格
@login_required
def make_sort_table(R):
    if not R.user.has_perm('fishuser.sub_menu_management_system_create'):
        # 沒有 "第二層選單_工程管考系統_新增工程"
        return HttpResponseRedirect('/')

    plan = Plan.objects.get(id=R.POST.get('row_id', ''))
    top_plan = Plan.objects.get(uplevel=None)
    sub_plans = [plan] + plan.rSubPlanInList()
    plans = [top_plan] + top_plan.rSubPlanInList()
    class_names = ['danger', 'info', 'success', 'warning']
    for i in plans:
        i.front_tag = i.rLevelNumber()
        i.back_tag = 12 - i.rLevelNumber()
        i.class_name = class_names[i.rLevelNumber()] if i.rLevelNumber() < len(class_names) else class_names[-1]
        if i in sub_plans:
            i.no_bitton = True


    t = get_template(os.path.join('project', 'zh-tw', 'plan_list_sort_tr.html'))
    html = t.render(RequestContext(R,{
        'user': R.user,
        'years': years,
        'edit': True,
        'plan': plan,
        'plans': plans,
        }))
    return HttpResponse(json.dumps({'html': html}))


#搜尋工程案
@login_required
def search_project(R):
    if not R.user.has_perm('fishuser.sub_menu_management_system_search'):
        # 沒有 "第二層選單_遠端管理系統_搜尋工程"
        return HttpResponseRedirect('/')

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
    reports = ExportCustomReport.objects.filter(owner=R.user)
    field_tags = Option2.objects.all().order_by('id')
    for t in field_tags:
        t.fields = t.reportfield_set.all().order_by('id')


    default_project_ids = u','.join([str(i.project.id) for i in DefaultProject.objects.filter(user=R.user)])

    t = get_template(os.path.join('project', 'zh-tw', 'search_project.html'))
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
        'units': units,
        'default_project_ids': default_project_ids,
        'toppage_name': u'工程管考系統',
        'subpage_name': u'搜尋管考工程',
        }))
    return HttpResponse(html)

#工程回收桶
@login_required
def recycled_project(R):
    if not R.user.has_perm('fishuser.sub_menu_management_system_create'):
        # 沒有 "第二層選單_工程管考系統_新增工程案"
        return HttpResponseRedirect('/')

    projects = Project.objects.all().exclude(deleter=None).order_by('-year', 'unit', '-id')

    t = get_template(os.path.join('project', 'zh-tw', 'recycled_project.html'))
    html = t.render(RequestContext(R,{
        'user': R.user,
        'years': years,
        'this_year': this_year,
        'option': _make_choose(),
        'projects': projects,
        'toppage_name': u'工程管考系統',
        'subpage_name': u'搜尋管考工程',
        }))
    return HttpResponse(html)

@login_required
def project_deleter_use(R):
    project_id = R.POST.get('id', '')
    project = Project.objects.get(id=project_id)
    if not project.inspector_code: project.create_i_code()
    if not project.contractor_code: project.create_c_code()
    return HttpResponse(status=200)

#工程案基本資料
@login_required
def project_profile(R, **kw):
    row = Project.objects.get(id=kw['project_id'])
    if not R.user.has_perm('fishuser.view_all_project_in_management_system'):
        return HttpResponseRedirect('/')

    if R.user.has_perm('fishuser.edit_all_project_in_management_system'):
        #管考人員
        edit = True #編輯資料權限
    else:
        edit = False

    user = R.user

    top_plan = Plan.objects.get(uplevel=None)
    plans = [top_plan] + top_plan.rSubPlanInList()
    for i in plans:
        i.name = i.rLevelNumber() * '　' + '● ' + i.name

    project = row
    project.connects = [project]
    ex = project.ex_project
    while ex:
        project.connects.insert(0, ex)
        ex = ex.ex_project
    next = Project.objects.filter(ex_project=project)
    while next:
        project.connects.append(next[0])
        next = Project.objects.filter(ex_project=next[0])
    project.engineers = [u for u in FRCMUserGroup.objects.filter(project=project).exclude(group__name=u'監造廠商').exclude(group__name=u'營造廠商').order_by('id')]
    project.inspectors = [u for u in FRCMUserGroup.objects.filter(group__name=u'監造廠商', project=project)]
    project.contractors = [u for u in FRCMUserGroup.objects.filter(group__name=u'營造廠商', project=project)]
    project.engs = [u for u in FRCMUserGroup.objects.filter(project=project, group__name__in=[u'負責主辦工程師', u'協同主辦工程師', u'自辦主辦工程師'])]
    project.identity = user.user_profile.rIdentity(project.id)
    fund = Fund.objects.get(project=project)
    # budget = list(Budget.objects.filter(fund=fund).order_by('year'))[0]
    # if budget.capital_ratify_revision and budget.capital_ratify_revision != 0:
    #     project.budget_money = (budget.capital_ratify_revision or 0)
    # else:
    #     project.budget_money = (budget.capital_ratify_budget or 0)
    duration_type = Option.objects.filter(swarm=u'duration_type').order_by('id')
    inspector_type = Option.objects.filter(swarm=u'inspector_type').order_by('id')

    chase_one_by_one = project.countychaseprojectonebyone_set.get()
    countychasetime = CountyChaseTime.objects.all().order_by('-id')[0]
    try:
        chase_data = CountyChaseProjectOneToMany.objects.get(countychasetime=countychasetime, project=project)
        chase_data.pastDay = (datetime.date.today() - countychasetime.chase_date).days
        try:
            last_chase_data = list(CountyChaseProjectOneToMany.objects.filter(project=project).exclude(countychasetime=countychasetime).order_by('countychasetime'))[-1]
        except: last_chase_data = False
    except:
        chase_data = False
        last_chase_data = False

    allocations = Allocation.objects.filter(project=project).order_by('date')

    fishing_ports = FishingPort.objects.all().order_by('place', 'name')
    aquacultures = Aquaculture.objects.all().order_by('place', 'name')
    def sort_by_date(A, B):
        if A.date > B.date: return 1
        else: return -1
    progresss = []
    progresss_y_m = []
    # for p in Progress.objects.filter(project=project):
    #     p.date = datetime.datetime.strptime('%s-%s-%s' % (p.date.year, p.date.month, p.date.day), '%Y-%m-%d')
    #     p.memo = p.status.value if p.status else ''
    #     p.schedul_percent = p.schedul_progress_percent
    #     p.actual_percent = p.actual_progress_percent
    #     progresss_y_m.append(str(p.date.year)+str(p.date.month))
    #     p.i_dailyreport_percent = project.dailyreport_report.filter(date__lte=p.date).order_by('-date')[0].read_progress(report_type='inspector') if project.dailyreport_report.filter(date__lte=p.date) else u'無值'
    #     p.c_dailyreport_percent = project.dailyreport_report.filter(date__lte=p.date).order_by('-date')[0].read_progress(report_type='contractor') if project.dailyreport_report.filter(date__lte=p.date) else u'無值'
    #     progresss.append(p)
    for p in PCCProgress.objects.filter(project__uid=project.pcc_no):
        try:
            if str(p.year + 1911) + str(p.month) in progresss_y_m:
                continue
        except:
            pass
        p.date = datetime.datetime.strptime('%s-%s-28' % (p.year + 1911, p.month), '%Y-%m-%d')
        p.memo = (p.status or '') + '\n' + (p.r_memo or '')
        p.schedul_percent = p.percentage_of_predict_progress * 100
        p.actual_percent = p.percentage_of_real_progress * 100
    
        p.i_dailyreport_percent = project.dailyreport_report.filter(date__lte=p.date).order_by('-date')[0].read_progress(report_type='inspector') if project.dailyreport_report.filter(date__lte=p.date) else u'無值'
        p.c_dailyreport_percent = project.dailyreport_report.filter(date__lte=p.date).order_by('-date')[0].read_progress(report_type='contractor') if project.dailyreport_report.filter(date__lte=p.date) else u'無值'
        progresss.append(p)
    progresss.sort(sort_by_date)
    
    appropriates = Appropriate.objects.filter(project=project).order_by('allot_date', 'type')

    fundrecords = []
    fundrecords_y_m = []
    for p in FundRecord.objects.filter(project=project):
        p.date = datetime.datetime.strptime('%s-%s-%s' % (p.date.year, p.date.month, p.date.day), '%Y-%m-%d')
        progresss_y_m.append(str(p.date.year)+str(p.date.month))
        p.real_pay = p.total_pay
        fundrecords.append(p)
    for p in PCCProgress.objects.filter(project__uid=project.pcc_no):
        if str(p.year + 1911) + str(p.month) in progresss_y_m:
            continue
        p.date = datetime.datetime.strptime('%s-%s-28' % (p.year + 1911, p.month), '%Y-%m-%d')
        p.real_pay = p.totale_money_paid
        fundrecords.append(p)
    fundrecords.sort(sort_by_date)

    photos = ProjectPhoto.objects.filter(project=project).order_by('uploadtime')
    project.photo_count = project.photo_set.filter(verify__isnull=False).count()

    use_manage = sum([i.money for i in ProjectManageMoney.objects.filter(project=project)])
    limit_money = project.manage if project.manage else 0 - use_manage if use_manage else 0

    t = get_template(os.path.join('project', 'zh-tw', 'project_profile.html'))
    html = t.render(RequestContext(R,{
            'user': R.user,
            'years': years,
            'plans': plans,
            'project': project,
            'edit': edit,
            'places': places,
            'option' : _make_choose(),
            'fishing_ports': fishing_ports,
            'aquacultures': aquacultures,
            'progresss': progresss,
            'appropriates': appropriates,
            'fundrecords': fundrecords,
            'units': units,
            'photos': photos,
            'fund': fund,
            'budgets': fund.budget_set.exclude(new=0).order_by('priority'),
            'allocations': allocations,
            'chase_data': chase_data,
            'last_chase_data': last_chase_data,
            'chase_one_by_one': chase_one_by_one,
            'limit_money': limit_money,
            'toppage_name': u'工程管考系統',
        }))
    return HttpResponse(html)

#上傳檔案的處理
@login_required
def new_file_upload(R):
    data = R.POST

    table_name = data['table_name']

    f = R.FILES.get('file', None)
    full_name = f.name.split(".")
    ext = full_name[-1].lower()
    full_name.remove(full_name[-1])
    name = "".join(full_name)

    if table_name == 'ProjectPhoto':
        # if ext not in [i.value.lower() for i in Option.objects.filter(swarm="extensiontype")]:
        #     return HttpResponse(json.dumps({'status': False, 'msg': u'上傳失敗，檔案格式不支援，系統僅支援"jpg/jpeg/png/tif/tiff"等圖片類型檔案'}))
        project = Project.objects.get(id=data['project_id'])
        new = ProjectPhoto(
            project = project,
            name = name,
            memo = '',
            extension = None,
            uploadtime = NOW()
        )
        new.save()
        getattr(new, 'file').save('%s.%s'%(new.id, ext), f)
        new.save()

    return HttpResponse(json.dumps({'status': True, 'id': new.id, 'name': new.name, 'memo': new.memo, 'rExt': ext, 'rUrl': new.rUrl()}))


#新增工程案
@login_required
def create_project(R):
    if not R.user.has_perm('fishuser.sub_menu_management_system_create'):
        # 沒有 "第二層選單_工程管考系統_新增工程案"
        return HttpResponseRedirect('/')

    top_plan = Plan.objects.get(uplevel=None)
    plans = [top_plan] + top_plan.rSubPlanInList()
    for i in plans:
        i.name = i.rLevelNumber() * '　' + '● ' + i.name

    fishing_ports = FishingPort.objects.all().order_by('place', 'name')
    aquacultures = Aquaculture.objects.all().order_by('place', 'name')

    t = get_template(os.path.join('project', 'zh-tw', 'create_project.html'))
    html = t.render(RequestContext(R,{
        'user': R.user,
        'years': years,
        'this_year': this_year,
        'plans': plans,
        'fishing_ports': fishing_ports,
        'aquacultures': aquacultures,
        'option': _make_choose(),
        'places': places,
        'units': units,
        'toppage_name': u'工程管考系統',
        'subpage_name': u'新增工程案',
        }))
    return HttpResponse(html)


#工程提案區 - 漁業署草稿
@login_required
def draft_project(R):
    if not R.user.has_perm('fishuser.sub_menu_management_system_draft'):
        # 沒有 "第二層選單_工程管考系統_草稿匣"
        return HttpResponseRedirect('/')

    new_units = units
    draft_projects = Draft_Project.objects.filter(type__value=u"漁業署草稿").order_by('place', 'sort')

    for p in draft_projects:
        p.place_dp_num = Draft_Project.objects.filter(type__value=u"漁業署草稿", place=p.place).count()

    fishing_ports = FishingPort.objects.all().order_by('place', 'name')
    aquacultures = Aquaculture.objects.all().order_by('place', 'name')

    top_plan = Plan.objects.get(uplevel=None)
    plans = [top_plan] + top_plan.rSubPlanInList()
    for i in plans:
        i.name = i.rLevelNumber() * '　' + '● ' + i.name

    t = get_template(os.path.join('project', 'zh-tw', 'draft_project.html'))
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
        'plans': plans,
        'toppage_name': u'工程管考系統',
        'subpage_name': u'草稿匣',
        }))
    return HttpResponse(html)


#工程提案區 - 縣市提案草稿
@login_required
def draft_project_place(R):
    if not R.user.has_perm('fishuser.sub_menu_management_system_draft'):
        # 沒有 "第二層選單_工程管考系統_草稿匣"
        return HttpResponseRedirect('/')

    new_units = units
    draft_projects = Draft_Project.objects.filter(type__value=u"縣市提案草稿").order_by('place', 'sort')

    for p in draft_projects:
        p.place_dp_num = Draft_Project.objects.filter(type__value=u"縣市提案草稿", place=p.place).count()

    fishing_ports = FishingPort.objects.all().order_by('place', 'name')
    aquacultures = Aquaculture.objects.all().order_by('place', 'name')

    t = get_template(os.path.join('project', 'zh-tw', 'draft_project_place.html'))
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
        'toppage_name': u'工程管考系統',
        'subpage_name': u'草稿匣',
        }))
    return HttpResponse(html)


#編輯工程提案資料
@login_required
def draft_project_profile(R, **kw):
    if not R.user.has_perm('fishuser.sub_menu_management_system_draft'):
        # 沒有 "第二層選單_工程管考系統_草稿匣"
        return HttpResponseRedirect('/')

    draft_project = Draft_Project.objects.get(id=kw['draft_project_id'])
    new_units = units

    fishing_ports = FishingPort.objects.all().order_by('place', 'name')
    aquacultures = Aquaculture.objects.all().order_by('place', 'name')

    t = get_template(os.path.join('project', 'zh-tw', 'draft_project_profile.html'))
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
        'toppage_name': u'工程管考系統',
        'subpage_name': u'草稿匣',
        }))
    return HttpResponse(html)


#新增工程案 從 草稿匣
@login_required
def create_project_from_draft(R):
    if not R.user.has_perm('fishuser.sub_menu_management_system_create'):
        # 沒有 "第二層選單_工程管考系統_新增工程案"
        return HttpResponseRedirect('/')

    p = Draft_Project.objects.get(id=R.POST.get('project_id', ''))
    plan = Plan.objects.get(id=R.POST.get('plan_id', ''))
    project = Project(
            year = p.year,
            plan = plan,
            place = p.place,
            project_type = p.project_type,
            project_sub_type = p.project_sub_type,
            name = p.name,
            unit = p.unit,
            project_memo = '',
            undertake_type = p.undertake_type,
            budget_sub_type = p.budget_sub_type,
            purchase_type = p.purchase_type,
            allot_rate = '100'
        )
    if p.info: project.project_memo += '主要工程內容：\n' + p.info
    if p.other_memo: project.project_memo += '\n\n其他補充說明：\n' + p.other_memo
    if p.memo: project.project_memo += '\n\n備註：\n' + p.memo

    project.save()
    fund = Fund(
            project = project
        )
    fund.save()
    budget =  Budget(
            fund = fund,
            year = project.year,
            capital_ratify_budget = p.self_money,
            capital_ratify_local_budget = p.local_money,
        )
    budget.save()
    chase_obo = CountyChaseProjectOneByOne(
            project = project,
        )
    chase_obo.save()
    for i in Draft_Project.objects.filter(type=p.type, place=p.place, sort__gt=p.sort):
        i.sort -= 1
        i.save()
    p.delete()
    return HttpResponse(json.dumps({'project_id': project.id}))


#縣市進度追蹤系統
@login_required
def chase(R):
    if not R.user.has_perm('fishuser.sub_menu_management_system_city'):
        # 沒有 "第二層選單_工程管考系統_縣市進度追蹤"
        return HttpResponseRedirect('/')

    places = Place.objects.filter(uplevel=TAIWAN).order_by('id')
    top_plan = Plan.objects.get(uplevel=None)
    plans = [top_plan] + top_plan.rSubPlanInList()
    for i in plans:
        i.name = i.rLevelNumber() * '　' + '● ' + i.name

    #刪除被移除的工程案
    CountyChaseProjectOneToMany.objects.all().exclude(project__deleter=None).delete()

    chase_time = CountyChaseTime.objects.all().order_by('-id')[0]
    chase_time.times = CountyChaseTime.objects.all().count()
    chase_time.past_day = (datetime.date.today() - chase_time.chase_date).days
    chase_time.num = CountyChaseProjectOneToMany.objects.filter(countychasetime=chase_time).count()
    # chase_time.need_check_complete = chase_time.countychaseprojectonetomany_set.filter(complete=True).count()
    # chase_time.need_check_close = CountyChaseProjectOneByOne.objects.filter(close=True).count()
    project__undertake_type__value='自辦'
    north_place_name = [
        u'臺灣地區', u'臺北市', u'新北市', u'基隆市', u'桃園市', u'宜蘭縣', u'花蓮縣', u'新竹市', u'新竹縣', u'苗栗縣', u'臺中市', u'金門縣', u'連江縣',
        ]
    south_place_name = [
        u'彰化縣', u'雲林縣', u'嘉義市', u'嘉義縣', u'臺南市', u'高雄市', u'屏東縣', u'臺東縣', u'澎湖縣', u'南投縣', 
        ]
    north_places = [Place.objects.get(name=i) for i in north_place_name]
    for i in north_places: i.is_north = True
    south_places = [Place.objects.get(name=i) for i in south_place_name]
    for i in south_places: i.is_north = False
    new_places = north_places + south_places

    projects = CountyChaseProjectOneToMany.objects.filter(countychasetime=chase_time)

    rcm_projects_id = [i.project_id for i in FRCMUserGroup.objects.filter(project__in=[j.project for j in projects])]

    for p in new_places:
        p.check = projects.filter(project__place=p, complete=True).exclude(project__undertake_type__value=u'自辦')
        not_checks = projects.filter(project__place=p, complete=False).exclude(project__undertake_type__value=u'自辦')
        p.import_not_check = not_checks.filter(project__id__in=rcm_projects_id)
        p.not_import_not_check = not_checks.exclude(project__id__in=rcm_projects_id)

    place_north = Place(name=u'北部辦公室')
    place_north.check = projects.filter(complete=True, project__undertake_type__value=u'自辦', project__place__name__in=north_place_name)
    not_checks = projects.filter(complete=False, project__undertake_type__value=u'自辦', project__place__name__in=north_place_name)
    place_north.import_not_check = not_checks.filter(project__id__in=rcm_projects_id)
    place_north.not_import_not_check = not_checks.exclude(project__id__in=rcm_projects_id)
    new_places.insert(0, place_north)
    place_south = Place(name=u'南部辦公室')
    place_south.check = projects.filter(complete=True, project__undertake_type__value=u'自辦', project__place__name__in=south_place_name)
    not_checks = projects.filter(complete=False, project__undertake_type__value=u'自辦', project__place__name__in=south_place_name)
    place_south.import_not_check = not_checks.filter(project__id__in=rcm_projects_id)
    place_south.not_import_not_check = not_checks.exclude(project__id__in=rcm_projects_id)
    new_places.insert(1, place_south)

    fishing_ports = FishingPort.objects.all().order_by('place', 'name')
    aquacultures = Aquaculture.objects.all().order_by('place', 'name')

    t = get_template(os.path.join('project', 'zh-tw', 'chase.html'))
    html = t.render(RequestContext(R,{
        'user': R.user,
        'years': years,
        'chase_time':chase_time,
        'fishing_ports': fishing_ports,
        'aquacultures': aquacultures,
        'today': TODAY(),
        'this_year': this_year,
        'option': _make_choose(),
        'places': new_places,
        'units': units,
        'chase_page': 'chase',
        'toppage_name': u'工程管考系統',
        'subpage_name': u'縣市進度追蹤',
        }))
    return HttpResponse(html)


#製造進度追蹤table
@login_required
def chase_table(R):
    if not R.user.has_perm('fishuser.sub_menu_management_system_city'):
        # 沒有 "第二層選單_工程管考系統_縣市進度追蹤"
        return HttpResponseRedirect('/')

    chase_time = CountyChaseTime.objects.get(id=R.POST.get('chase_id', ''))
    chase_time.times = CountyChaseTime.objects.filter(chase_date__lte=chase_time.chase_date).count()
    if chase_time.read_next_chase():
        chase_time.past_day = (chase_time.read_next_chase().chase_date - chase_time.chase_date).days
    else:
        chase_time.past_day = (datetime.date.today() - chase_time.chase_date).days
    chase_time.num = CountyChaseProjectOneToMany.objects.filter(countychasetime=chase_time).count()
    # chase_time.need_check_complete = chase_time.countychaseprojectonetomany_set.filter(check=False, complete=True).count()
    # chase_time.need_check_close = CountyChaseProjectOneByOne.objects.filter(check=False).count()
    project__undertake_type__value='自辦'
    north_place_name = [
        u'臺灣地區', u'臺北市', u'新北市', u'基隆市', u'桃園市', u'宜蘭縣', u'花蓮縣', u'新竹市', u'新竹縣', u'苗栗縣', u'臺中市', u'金門縣', u'連江縣',
        ]
    south_place_name = [
        u'彰化縣', u'雲林縣', u'嘉義市', u'嘉義縣', u'臺南市', u'高雄市', u'屏東縣', u'臺東縣', u'澎湖縣', u'南投縣', 
        ]
    north_places = [Place.objects.get(name=i) for i in north_place_name]
    for i in north_places: i.is_north = True
    south_places = [Place.objects.get(name=i) for i in south_place_name]
    for i in south_places: i.is_north = False
    new_places = north_places + south_places

    projects = CountyChaseProjectOneToMany.objects.filter(countychasetime=chase_time)

    rcm_projects_id = [i.project_id for i in FRCMUserGroup.objects.filter(project__in=[j.project for j in projects])]
    for p in new_places:
        p.check = projects.filter(project__place=p, complete=True).exclude(project__undertake_type__value=u'自辦')
        not_checks = projects.filter(project__place=p, complete=False).exclude(project__undertake_type__value=u'自辦')
        p.import_not_check = not_checks.filter(project__id__in=rcm_projects_id)
        p.not_import_not_check = not_checks.exclude(project__id__in=rcm_projects_id)

    place_north = Place(name=u'北部辦公室')
    place_north.check = projects.filter(complete=True, project__undertake_type__value=u'自辦', project__place__name__in=north_place_name)
    not_checks = projects.filter(complete=False, project__undertake_type__value=u'自辦', project__place__name__in=north_place_name)
    place_north.import_not_check = not_checks.filter(project__id__in=rcm_projects_id)
    place_north.not_import_not_check = not_checks.exclude(project__id__in=rcm_projects_id)
    new_places.insert(0, place_north)
    place_south = Place(name=u'南部辦公室')
    place_south.check = projects.filter(complete=True, project__undertake_type__value=u'自辦', project__place__name__in=south_place_name)
    not_checks = projects.filter(complete=False, project__undertake_type__value=u'自辦', project__place__name__in=south_place_name)
    place_south.import_not_check = not_checks.filter(project__id__in=rcm_projects_id)
    place_south.not_import_not_check = not_checks.exclude(project__id__in=rcm_projects_id)
    new_places.insert(1, place_south)

    t = get_template(os.path.join('project', 'zh-tw', 'chase_table.html'))
    html = t.render(RequestContext(R,{
        'user': R.user,
        'years': years,
        'chase_time':chase_time,
        'today': TODAY(),
        'this_year': this_year,
        'option': _make_choose(),
        'places': new_places,
        'units': units,
        }))
    return HttpResponse(json.dumps({'html': html}))
        

#縣市進度追蹤系統-選擇追蹤工程
@login_required
def chase_select_project(R):
    if not R.user.has_perm('fishuser.sub_menu_management_system_city'):
        # 沒有 "第二層選單_工程管考系統_縣市進度追蹤"
        return HttpResponseRedirect('/')

    top_plan = Plan.objects.get(uplevel=None)
    plans = [top_plan] + top_plan.rSubPlanInList()
    for i in plans:
        i.name = i.rLevelNumber() * '　' + '● ' + i.name

    fishing_ports = FishingPort.objects.all().order_by('place', 'name')
    aquacultures = Aquaculture.objects.all().order_by('place', 'name')
    chase_time = CountyChaseTime.objects.all().order_by('-id')[0]
    chase_time.need_check_complete = chase_time.countychaseprojectonetomany_set.filter(complete=True).count()

    t = get_template(os.path.join('project', 'zh-tw', 'chase_select_project.html'))
    html = t.render(RequestContext(R,{
        'user': R.user,
        'years': years,
        'chase_time': chase_time,
        'this_year': this_year,
        'plans': plans,
        'fishing_ports': fishing_ports,
        'aquacultures': aquacultures,
        'option': _make_choose(),
        'places': places,
        'units': units,
        'chase_page': 'chase_select_project',
        'toppage_name': u'工程管考系統',
        'subpage_name': u'縣市進度追蹤',
        }))
    return HttpResponse(html)

#漁港管控表
@login_required
def control_form(R):
    # if not R.user.has_perm('fishuser.sub_menu_management_control_form'):
    #     # 沒有 "第二層選單_工程管考系統_漁港管控表"
    #     return HttpResponseRedirect('/')
    top_plans = []

    top_plan = Plan.objects.get(uplevel=None)
    top_plans += [top_plan]
    top_plans_1 = Plan.objects.filter(uplevel=top_plan.id).order_by('-year')
    top_plans += top_plans_1

    t = get_template(os.path.join('project', 'zh-tw', 'control_form.html'))
    html = t.render(RequestContext(R,{
        'user': R.user,
        'years': years,
        'top_plans': top_plans,
        'toppage_name': u'工程管考系統',
        'subpage_name': u'漁港管控表',
        }))
    return HttpResponse(html)

#取得漁港管控表資料
@login_required
def get_control_form_info(R):
    year = R.POST.get('year', this_year)
    budget_type = R.POST.get('budget_type', '')
    top_plan_id = R.POST.get('top_plan_id', '')
    
    
    if top_plan_id == '':
        projects = Project.objects.filter(year = year, deleter=None).order_by('work_no')
    else:
        sub_plans = [top_plan_id]
        sub_plans1 = Plan.objects.filter(uplevel=top_plan_id)
        for p1 in sub_plans1:
            sub_plans.append(p1.id)
            sub_plans2 = Plan.objects.filter(uplevel=p1.id)
            for p2 in sub_plans2:
                sub_plans.append(p2.id)
                sub_plans3 = Plan.objects.filter(uplevel=p2.id)
                for p3 in sub_plans3:
                    sub_plans.append(p3.id)
                    sub_plans4 = Plan.objects.filter(uplevel=p3.id)
                    for p4 in sub_plans4:
                        sub_plans.append(p4.id)
                        sub_plans5 = Plan.objects.filter(uplevel=p4.id)
                        for p5 in sub_plans5:
                            sub_plans.append(p5.id)
        projects = []
        for plan in sub_plans:
            proj = Project.objects.filter(year = year, budget_sub_type__value = budget_type, plan = plan, deleter=None)
            projects += proj
        projects = sorted(projects, key=lambda projects: projects.work_no)

    data = []
    undertake_type = {156: '補助', 157: '自辦', 158: '委辦'}
    for p in projects:

        fund = Fund.objects.get(project=p)
        budget = Budget.objects.filter(fund=fund).order_by('-priority')[0]
        data.append({
            'id': p.id,
            'undertake_type': undertake_type[p.undertake_type_id],
            'budget_id': budget.id,
            'name': p.name,
            'work_no': p.work_no,
            'capital_ratify_revision': float(budget.capital_ratify_revision) if budget.capital_ratify_revision else '',
            'capital_ratify_local_revision': float(budget.capital_ratify_local_revision) if budget.capital_ratify_local_revision else '',
            'allowance': float(p.allowance) if p.allowance else '',
            'allowance_revise': float(p.allowance_revise) if p.allowance_revise else '',
            'matching_fund_1': float(p.matching_fund_1) if p.matching_fund_1 else '',
            'matching_fund_2': float(p.matching_fund_2) if p.matching_fund_2 else '',
            'fund_1': float(p.fund_1) if p.fund_1 else '',
            'fund_2': float(p.fund_2) if p.fund_2 else '',
            'commission': float(p.commission) if p.commission else '',
            'commission_revise': float(p.commission_revise) if p.commission_revise else '',
            'selfpay': float(p.selfpay) if p.selfpay else '',
            'selfpay_revise': float(p.selfpay_revise) if p.selfpay_revise else '',
            'control_form_memo': p.control_form_memo if p.control_form_memo else ''
        })

    return HttpResponse(json.dumps(
        {'data': data}
    ))

#取得計畫編號資料
@login_required
def get_work_no_info(R):
    year = R.POST.get('year', this_year)
    budget_type = R.POST.get('budget_type', '')
    projects = Project.objects.filter(year = year,budget_sub_type__value = budget_type, deleter=None).order_by('work_no')
    
    data = []
    for p in projects:
        try:
            data.append(p.work_no.rsplit('-', 1)[0])
        except AttributeError:
            data.append('尚未填寫工程編號')

    work_list = [i for n, i in enumerate(data) if i not in data[:n]]

    return HttpResponse(json.dumps(
        {'data': work_list}
    ))

#漁港管控表-線上列印
@login_required
def control_form_online_print(R, **kw):
    year = kw['year']
    budget_type = kw['budget_type']
    top_plan_id = kw['top_plan_id']
    if(top_plan_id == 'ALL'):
        top_plan_name = 'ALL'
    else:
        top_plan_name = Plan.objects.get(id=top_plan_id)

    if top_plan_id == 'ALL':
        projects = Project.objects.filter(year = year, budget_sub_type__value = budget_type, deleter=None).order_by('work_no')
    else:
        sub_plans = [top_plan_id]
        sub_plans1 = Plan.objects.filter(uplevel=top_plan_id)
        for p1 in sub_plans1:
            sub_plans.append(p1.id)
            sub_plans2 = Plan.objects.filter(uplevel=p1.id)
            for p2 in sub_plans2:
                sub_plans.append(p2.id)
                sub_plans3 = Plan.objects.filter(uplevel=p2.id)
                for p3 in sub_plans3:
                    sub_plans.append(p3.id)
                    sub_plans4 = Plan.objects.filter(uplevel=p3.id)
                    for p4 in sub_plans4:
                        sub_plans.append(p4.id)
                        sub_plans5 = Plan.objects.filter(uplevel=p4.id)
                        for p5 in sub_plans5:
                            sub_plans.append(p5.id)
        projects = []
        for plan in sub_plans:
            proj = Project.objects.filter(year = year, budget_sub_type__value = budget_type, plan = plan, deleter=None)
            projects += proj
        projects = sorted(projects, key=lambda projects: projects.work_no)

    for p in projects:
        fund = Fund.objects.get(project=p)
        budget = Budget.objects.filter(fund=fund).order_by('-priority')[0]
        p.capital_ratify_revision = budget.capital_ratify_revision / 1000 if budget.capital_ratify_revision else ''
        p.capital_ratify_local_revision = budget.capital_ratify_local_revision / 1000 if budget.capital_ratify_local_revision else ''

    t = get_template(os.path.join('project', 'zh-tw', 'control_form_online_print.html'))
    html = t.render(RequestContext(R,{
        'year': year,
        'budget_type': kw['budget_type'],
        'top_plan_name': top_plan_name,
        'projects': projects,
        }))
    return HttpResponse(html)

#漁港管控表-匯出excel
@login_required
def control_form_make_excel(R, **kw):
    year = kw['year']
    budget_type = kw['budget_type']
    top_plan_id = kw['top_plan_id']
    if(top_plan_id == 'ALL'):
        top_plan_name = 'ALL'
    else:
        top_plan_name = Plan.objects.get(id=top_plan_id)

    selfpay_projects = []
    commission_projects = []
    allowance_projects = []
    if top_plan_id == 'ALL':
        selfpay_projects = Project.objects.filter(year = year,budget_sub_type__value = budget_type, deleter=None, undertake_type__value = '自辦').order_by('work_no')
        commission_projects = Project.objects.filter(year = year,budget_sub_type__value = budget_type, deleter=None, undertake_type__value = '委辦').order_by('work_no')
        allowance_projects = Project.objects.filter(year = year,budget_sub_type__value = budget_type, deleter=None, undertake_type__value = '補助').order_by('work_no')
    else:
        sub_plans = [top_plan_id]
        sub_plans1 = Plan.objects.filter(uplevel=top_plan_id)
        for p1 in sub_plans1:
            sub_plans.append(p1.id)
            sub_plans2 = Plan.objects.filter(uplevel=p1.id)
            for p2 in sub_plans2:
                sub_plans.append(p2.id)
                sub_plans3 = Plan.objects.filter(uplevel=p2.id)
                for p3 in sub_plans3:
                    sub_plans.append(p3.id)
                    sub_plans4 = Plan.objects.filter(uplevel=p3.id)
                    for p4 in sub_plans4:
                        sub_plans.append(p4.id)
                        sub_plans5 = Plan.objects.filter(uplevel=p4.id)
                        for p5 in sub_plans5:
                            sub_plans.append(p5.id)
        for plan in sub_plans:
            selfpay_proj = Project.objects.filter(year = year, budget_sub_type__value = budget_type, plan = plan, deleter=None, undertake_type__value = '自辦')
            commission_proj = Project.objects.filter(year = year, budget_sub_type__value = budget_type, plan = plan, deleter=None, undertake_type__value = '委辦')
            allowance_proj = Project.objects.filter(year = year, budget_sub_type__value = budget_type, plan = plan, deleter=None, undertake_type__value = '補助')
            selfpay_projects += selfpay_proj
            commission_projects += commission_proj
            allowance_projects += allowance_proj

    
    for projects in [selfpay_projects, commission_projects, allowance_projects]:
        for p in projects:
            fund = Fund.objects.get(project=p)
            budget = Budget.objects.filter(fund=fund).order_by('-priority')[0]
            
            p.capital_ratify_revision = budget.capital_ratify_revision / 1000 if budget.capital_ratify_revision else ''
            p.capital_ratify_local_revision = budget.capital_ratify_local_revision / 1000 if budget.capital_ratify_local_revision else ''
    
    selfpay_projects = sorted(selfpay_projects, key=lambda selfpay_projects: selfpay_projects.work_no)
    commission_projects = sorted(commission_projects, key=lambda commission_projects: commission_projects.work_no)
    allowance_projects = sorted(allowance_projects, key=lambda allowance_projects: allowance_projects.work_no)
    projects = [selfpay_projects, commission_projects, allowance_projects]
            
    file_name = u'%s年度-%s-漁港管控表' % (year, kw['budget_type'])

    output = StringIO()
    workbook = xlsxwriter.Workbook(output, 
        {'strings_to_numbers':  True,
        'strings_to_formulas': False,
        'strings_to_urls':     False})
    #workbook = make_control_form_excel_file(workbook=workbook, projects=projects, budget_type=kw['budget_type'], year=year, work_no=work_no)
    workbook = make_control_form_excel_file(workbook=workbook, projects=projects, budget_type=budget_type, year=year, top_plan_name=top_plan_name)
    workbook.close()

    output.seek(0)
    response = HttpResponse(output.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response['Content-Disposition'] = ('attachment; filename=%s.xlsx' % (file_name)).encode('cp950')

    return response

#匯出漁港工程大表excel
@login_required
def port_engineering_make_excel(R, **kw):
    year = kw['year']
    month = TODAY().month
    exclude_id = [2346, 2583, 2899, 2511] #測試用工程案

    projects = Project.objects.filter(year=year, deleter=None).exclude(id__in=exclude_id)
    file_name = '%s年漁港大表-進度-%s月%s日' % (year, month, TODAY().day)

    for p in projects:
        port_name = ' '
        fund = Fund.objects.get(project=p)
        budget = Budget.objects.filter(fund=fund).first()
        chase_project = CountyChaseProjectOneByOne.objects.get(project_id=p.id)
        try:
            engprofile = EngProfile.objects.get(project=p)
        except:
            engprofile = None

        #計畫歸屬與分類
        # try:
        first_plan = Plan.objects.get(id=p.plan_id).uplevel_id
        # second_plan = Plan.objects.get(id=first_plan).uplevel_id
        if first_plan:
            p.plan_name = Plan.objects.get(id=first_plan).name
            plan_class_id = Plan.objects.get(id=first_plan).plan_class_id
            p.plan_class = Option.objects.get(id=plan_class_id).value if plan_class_id else ' '
            #print('first plan ')
            #print(first_plan)
            print('p_name')
            print(p.plan_name)
            #print('p_class_id')
            #print(plan_class_id)
            #print('p_class')
            #print(p.plan_class)
            
        else:
            p.plan_name = Plan.objects.get(id=p.plan_id).name
            plan_class_id = Plan.objects.get(id=p.plan_id).plan_class_id
            p.plan_class = Option.objects.get(id=plan_class_id).value if plan_class_id else ' '
            #print('plan_id')
            #print(p.plan_id)
            print('p_name')
            print(p.plan_name)
            #print('p_class_id')
            #print(plan_class_id)
            #print('p_class')
            #print(p.plan_class)
            
            
        # except:
        #     p.plan_name = ' '
        #     p.plan_class = ' '



        #補助比例
        #print('p.pcc_no')
        #print(p.pcc_no)
        if p.pcc_no:
            p.allowance_scale = str(PCCProject.objects.get(uid=p.pcc_no).main_rate) + '%'
        else:
            capital_ratify_revision = budget.capital_ratify_revision if budget.capital_ratify_revision else 0
            capital_ratify_local_revision = budget.capital_ratify_local_revision if budget.capital_ratify_local_revision else 0

            if capital_ratify_revision != 0 and capital_ratify_local_revision != 0:
                p.allowance_scale = str(round((capital_ratify_revision - capital_ratify_local_revision) / capital_ratify_revision * 100, 2)) + '%'
            else:
                p.allowance_scale = ''
            #print('capital_ratify_revision')
            #print(capital_ratify_revision)
            #print(capital_ratify_local_revision)

        
        #經費類別
        p.undertake = Option.objects.get(id=p.undertake_type_id).value
        
        #採購類別
        p.purchase = Option.objects.get(id=p.purchase_type_id).value

        #核定日期
        p.act_eng_plan_approved_plan = str(chase_project.act_eng_plan_approved_plan) if chase_project.act_eng_plan_approved_plan else str(chase_project.sch_eng_plan_approved_plan)

        #工程執行機關
        p.unit = Unit.objects.get(id=p.unit_id)

        #工程案漁港
        for port in p.fishing_port.all():
            port_name += port.name + '\n'
        p.port = port_name

        print('port')
        print(p.port)
        #辦理情形
        if chase_project.act_eng_do_closed:
            p.handling = '已結案'
        elif chase_project.act_eng_do_completion:
            p.handling = '已完工'
        elif chase_project.stat_illus_memo:
            p.handling = chase_project.stat_illus_memo
        else:
            p.handling = ' '

        #工程進度
        progress = PCCProgress.objects.filter(project__uid=p.pcc_no).order_by('-year', '-month')
        pcc_s_percent = 0
        pcc_a_percent = 0
        if progress:
            #第一步 找看看工程會同步資料有沒有
            progress = progress.first()
            pcc_s_percent = round(progress.percentage_of_predict_progress*100, 2)
            pcc_a_percent = round(progress.percentage_of_real_progress*100, 2)
        elif engprofile:
            #第二步 找日報表有沒有
            if engprofile.design_percent or pcc_s_percent:
                pcc_s_percent = round(float(str(engprofile.design_percent)), 2)
                pcc_a_percent = round(float(str(pcc_s_percent)), 2)
        #第三步 找看看進度追蹤
        if not pcc_s_percent and not pcc_a_percent:
            chases = CountyChaseProjectOneToMany.objects.filter(complete=True, project=p).order_by('-id')
            if chases:
                chase = chases.first()
                pcc_s_percent = round(float(str(chase.schedul_progress_percent)), 2)
                pcc_a_percent = round(float(str(chase.actual_progress_percent)), 2)
        
        p.pcc_s_percent = str(pcc_s_percent) + '%'
        p.pcc_a_percent = str(pcc_a_percent) + '%'
        p.difference_percent = str(pcc_a_percent - pcc_s_percent) + '%'

        #工期
        if p.frcm_duration_type_id:
            p.duration_type = Option.objects.get(id=p.frcm_duration_type_id).value
        else:
            p.duration_type = ''
        
        #屬標餘款
        if p.tender_excess_funds == 0:
            p.tender_excess_funds = False
        elif p.tender_excess_funds == 1:
            p.tender_excess_funds = True
        else:
            p.tender_excess_funds = 'null'

        #招標預算
        if p.pcc_no:
            p.bidding_budget = PCCProject.objects.get(uid=p.pcc_no).contract_budget / 1000
        elif p.tender_budget:
            p.bidding_budget = p.tender_budget
        else:
            p.bidding_budget = ' '

        #決標金額
        if p.pcc_no:
            p.decide_tenders_price = PCCProject.objects.get(uid=p.pcc_no).decide_tenders_price / 1000
        elif p.construction_bid != 0 and p.construction_bid:
            p.decide_tenders_price = p.construction_bid / 1000
        else:
            p.decide_tenders_price = ''

        #契約金額
        if p.pcc_no:
            if PCCProject.objects.get(uid=p.pcc_no).decide_tenders_price2:
                p.decide_tenders_price2 = PCCProject.objects.get(uid=p.pcc_no).decide_tenders_price2 / 1000
            else:
                p.decide_tenders_price2 = PCCProject.objects.get(uid=p.pcc_no).decide_tenders_price / 1000
        elif p.construction_bid != 0 and p.construction_bid:
            p.decide_tenders_price2 = p.construction_bid / 1000
        else:
            p.decide_tenders_price2 = ''

        #年度預算
        p.nine_budget = 0
        p.ten_budget = 0
        p.eleven_budget = 0
        p.twelve_budget = 0

        budget_list = Budget.objects.filter(fund=fund)
        for year_budget in budget_list:
            if year_budget.year <= 109 and year_budget.capital_ratify_budget:  #109年以前
                p.nine_budget += year_budget.capital_ratify_budget
            elif year_budget.year == 110 and year_budget.capital_ratify_budget: #110年
                p.ten_budget += year_budget.capital_ratify_budget
            elif year_budget.year == 111 and year_budget.capital_ratify_budget: #111年
                p.eleven_budget += year_budget.capital_ratify_budget
            elif year_budget.year >= 112 and year_budget.capital_ratify_budget: #112年之後
                p.twelve_budget += year_budget.capital_ratify_budget

        #結算金額
        p.balancing_price = 0
        if p.pcc_no:
            p.balancing_price = PCCProject.objects.get(uid=p.pcc_no).balancing_price if PCCProject.objects.get(uid=p.pcc_no).balancing_price else 0
        elif p.settlement_total_money:
            p.balancing_price = p.settlement_total_money
        elif p.settlement_construction_bid:
            p.balancing_price += p.settlement_construction_bid if p.settlement_construction_bid else 0
            p.balancing_price += p.settlement_planning_design_inspect if p.settlement_planning_design_inspect else 0
            p.balancing_price += p.settlement_manage if p.settlement_manage else 0
            p.balancing_price += p.settlement_pollution if p.settlement_pollution else 0
            try:
                p.balancing_price += ProjectBidMoney.objects.get(project_id=p.id).settlement_value if ProjectBidMoney.objects.get(project_id=p.id).settlement_value else 0
            except:
                pass
        
        #核定函勞務決標期限
        p.eng_plan_final_deadline = chase_project.act_eng_plan_final_deadline if chase_project.act_eng_plan_final_deadline else chase_project.sch_eng_plan_final_deadline

        #預計勞務決標日期
        p.sch_eng_plan_final = chase_project.sch_eng_plan_final

        #實際勞務決標日期
        p.act_eng_plan_final = chase_project.act_eng_plan_final

        #核定函工程決標期限
        p.eng_do_approved_plan = chase_project.act_eng_do_approved_plan if chase_project.act_eng_do_approved_plan else chase_project.sch_eng_do_approved_plan

        #預計工程決標日期
        p.sch_eng_do_final = chase_project.sch_eng_do_final

        #實際工程決標日期
        p.act_eng_do_final = chase_project.act_eng_do_final

        #預計工程簽約日期
        p.sch_eng_do_promise = chase_project.sch_eng_do_promise
        
        #實際工程簽約日期
        p.act_eng_do_promise = chase_project.act_eng_do_promise

        #預定開工日期
        p.sch_eng_do_start = chase_project.sch_eng_do_start

        #實際開工日期
        p.act_eng_do_start = chase_project.act_eng_do_start

        #預定完工日期
        p.sch_eng_do_completion = chase_project.sch_eng_do_completion

        #實際完工日期
        p.act_eng_do_completion = chase_project.act_eng_do_completion

        #勞務公告上網
        if chase_project.act_eng_plan_announcement_tender:
            p.eng_plan_announcement_tender = chase_project.act_eng_plan_announcement_tender 
        elif chase_project.sch_eng_plan_announcement_tender :
            p.eng_plan_announcement_tender = chase_project.sch_eng_plan_announcement_tender 
        else:
            p.eng_plan_announcement_tender = ' '

        #勞務履約中
        p.stat_wrk_per = chase_project.stat_wrk_per
        p.stat_wrk_per_date = chase_project.stat_wrk_per_date
        p.stat_wrk_per_memo = chase_project.stat_wrk_per_memo
        
        #工程標案招標文件準備中
        p.stat_file_prep = chase_project.stat_file_prep
        p.stat_file_prep_date = chase_project.stat_file_prep_date
        p.stat_file_prep_memo = chase_project.stat_file_prep_memo
        
        #工程標案招標文件公開預覽中
        p.stat_file_prvw = chase_project.stat_file_prvw
        p.stat_file_prvw_date = chase_project.stat_file_prvw_date
        p.stat_file_prvw_memo = chase_project.stat_file_prvw_memo
        
        #工程標案招標文件上網公告中
        p.stat_file_oln = chase_project.stat_file_oln
        p.stat_file_oln_date = chase_project.stat_file_oln_date
        p.stat_file_oln_memo = chase_project.stat_file_oln_memo
        
        #工程標案已決標，訂約中(含待開工)
        p.stat_res_ctr = chase_project.stat_res_ctr
        p.stat_res_ctr_date = chase_project.stat_res_ctr_date
        p.stat_res_ctr_memo = chase_project.stat_res_ctr_memo
        
        #施工中
        p.stat_cnst = chase_project.stat_cnst
        p.stat_cnst_date = chase_project.stat_cnst_date
        p.stat_cnst_memo = chase_project.stat_cnst_memo
        
        #停工中
        p.stat_stop = chase_project.stat_stop
        p.stat_stop_date = chase_project.stat_stop_date
        p.stat_stop_memo = chase_project.stat_stop_memo
        
        #履約爭議中
        p.stat_cnfl = chase_project.stat_cnfl
        p.stat_cnfl_date = chase_project.stat_cnfl_date
        p.stat_cnfl_memo = chase_project.stat_cnfl_memo
        
        #解約中
        p.stat_term_ing = chase_project.stat_term_ing
        p.stat_term_ing_date = chase_project.stat_term_ing_date
        p.stat_term_ing_memo = chase_project.stat_term_ing_memo
        
        #已申報竣工，竣工查驗中或準備驗收資料
        p.stat_cmplt = chase_project.stat_cmplt
        p.stat_cmplt_date = chase_project.stat_cmplt_date
        p.stat_cmplt_memo = chase_project.stat_cmplt_memo
        
        #驗收中(含初驗)
        p.stat_acpt = chase_project.stat_acpt
        p.stat_acpt_date = chase_project.stat_acpt_date
        p.stat_acpt_memo = chase_project.stat_acpt_memo
        
        #結算付款中
        p.stat_pay = chase_project.stat_pay
        p.stat_pay_date = chase_project.stat_pay_date
        p.stat_pay_memo = chase_project.stat_pay_memo
        
        #已結案
        if chase_project.act_eng_do_closed:
            p.eng_do_closed = True
            p.act_eng_do_closed = chase_project.act_eng_do_closed
        else:
            p.eng_do_closed = False
        
        #已解約(請加註日期)
        p.stat_term_ed = chase_project.stat_term_ed
        p.stat_term_ed_date = chase_project.stat_term_ed_date
        p.stat_term_ed_memo = chase_project.stat_term_ed_memo

        #其他(請加註日期)
        p.stat_oth = chase_project.stat_oth
        p.stat_oth_date = chase_project.stat_oth_date
        p.stat_oth_memo = chase_project.stat_oth_memo

        #停工或落後原因
        p.stat_stop_reason_memo = chase_project.stat_stop_reason_memo

        #解決對策
        p.stat_solution_memo = chase_project.stat_solution_memo

    output = StringIO()
    workbook = xlsxwriter.Workbook(output, 
        {'strings_to_numbers':  True,
        'strings_to_formulas': False,
        'strings_to_urls':     False})
    workbook = make_port_engineering_excel_file(workbook=workbook, projects=projects, month=month)
    workbook.close()
    output.seek(0)

    #response = HttpResponse(result, content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    
    response = HttpResponse(output.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response['Content-Disposition'] = ('attachment; filename=%s.xlsx' % (file_name)).encode('cp950')

    return response


#下載漁港工程大表excel
@login_required
def port_engineering_download_excel(R, **kw):
    year = kw['year']
    month = kw['month']
    file_name = '%s年漁港大表-進度-%s月' % (year, month)
    try:
        with open('/var/www/fes/apps/project/exceltemp/%s/month_%s.xlsx' %(year, month), 'rb') as ff:
            result = ff.read()
        
        response = HttpResponse(result, content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response['Content-Disposition'] = ('attachment; filename=%s.xlsx' % (file_name)).encode('cp950')
        
        return response
    
    except:
        response = HttpResponse('<script>alert("檔案不存在");window.close();</script>') 
        return response
    
#於工程案之金額資訊中，直接新增自辦工程管理費
@login_required
def add_manage_money(R):
    project_id = R.POST.get('project_id', '')
    date = R.POST.get('date', '')
    year = R.POST.get('year', '')
    name = R.POST.get('name', '')
    money = decimal.Decimal(R.POST.get('money', '0'), 3)
    manage_money = ManageMoney.objects.create(year=year, date=date, name=name, is_commission=False, is_remain=False)
    manage_money.save()
    project_manage_money = ProjectManageMoney.objects.create(managemoney_id=manage_money.id, project_id=project_id, money=money)
    project_manage_money.save()

    data = {'date':date, 'name':name, 'id':manage_money.id, 'money':R.POST.get('money', '0')}

    return HttpResponse(json.dumps(data))

#縣市進度追蹤系統-申請填寫完畢
# @login_required
# def chase_complete(R):
#     if not R.user.has_perm('fishuser.sub_menu_management_system_city'):
#         # 沒有 "第二層選單_工程管考系統_縣市進度追蹤"
#         return HttpResponseRedirect('/')

#     chase_time = CountyChaseTime.objects.all().order_by('-id')[0]
#     chase_time.need_check_complete = chase_time.countychaseprojectonetomany_set.filter(check=False, complete=True).count()
#     # chase_time.need_check_close = CountyChaseProjectOneByOne.objects.filter(check=False, close=True).count()
    
#     projects = chase_time.countychaseprojectonetomany_set.filter(check=False, complete=True)

#     t = get_template(os.path.join('project', 'zh-tw', 'chase_complete.html'))
#     html = t.render(RequestContext(R,{
#         'user': R.user,
#         'years': years,
#         'chase_time': chase_time,
#         'this_year': this_year,
#         'option': _make_choose(),
#         'places': places,
#         'units': units,
#         'projects': projects,
#         'chase_page': 'chase_complete',
#         'toppage_name': u'工程管考系統',
#         'subpage_name': u'縣市進度追蹤',
#         }))
#     return HttpResponse(html)


# #縣市進度追蹤系統-申請結案
# @login_required
# def chase_close(R):
#     if not R.user.has_perm('fishuser.sub_menu_management_system_city'):
#         # 沒有 "第二層選單_工程管考系統_縣市進度追蹤"
#         return HttpResponseRedirect('/')

#     chase_time = CountyChaseTime.objects.all().order_by('-id')[0]
#     chase_time.need_check_complete = chase_time.countychaseprojectonetomany_set.filter(check=False, complete=True).count()
#     chase_time.need_check_close = CountyChaseProjectOneByOne.objects.filter(check=False, close=True).count()
    
#     projects = CountyChaseProjectOneByOne.objects.filter(check=False, close=True)

#     t = get_template(os.path.join('project', 'zh-tw', 'chase_close.html'))
#     html = t.render(RequestContext(R,{
#         'user': R.user,
#         'years': years,
#         'chase_time': chase_time,
#         'this_year': this_year,
#         'option': _make_choose(),
#         'places': places,
#         'units': units,
#         'projects': projects,
#         'chase_page': 'chase_close',
#         'toppage_name': u'工程管考系統',
#         'subpage_name': u'縣市進度追蹤',
#         }))
#     return HttpResponse(html)


#縣市進度追蹤系統-申請結案
@login_required
def chase_print(R):
    if not R.user.has_perm('fishuser.sub_menu_management_system_city'):
        # 沒有 "第二層選單_工程管考系統_縣市進度追蹤"
        return HttpResponseRedirect('/')

    top_plan = Plan.objects.get(uplevel=None)
    plans = [top_plan] + top_plan.rSubPlanInList()
    for i in plans:
        i.name = i.rLevelNumber() * '　' + '● ' + i.name

    chase_time = CountyChaseTime.objects.all().order_by('-id').first()

    t = get_template(os.path.join('project', 'zh-tw', 'chase_print.html'))
    html = t.render(RequestContext(R,{
        'user': R.user,
        'years': years,
        'plans': plans,
        'this_year': this_year,
        'option': _make_choose(),
        'places': places,
        'units': units,
        'chase_time': chase_time,
        'chase_page': 'chase_print',
        'toppage_name': u'工程管考系統',
        'subpage_name': u'縣市進度追蹤',
        }))
    return HttpResponse(html)


@login_required
def get_chart_data(R):
    """ 取得統計圖表需要的資料 """
    type = R.POST.get('type', 'start_date')
    year = R.POST.get('year', this_year)
    chase = CountyChaseTime.objects.all().order_by('-id').first()
    records = chase.countychaseprojectonetomany_set.all()
    if year:
        records = records.filter(project__year=year)
    projects = Project.objects.filter(id__in=[i.project.id for i in records])
    engs = EngProfile.objects.filter(project__in=projects).exclude(start_date=None)

    if type == 'start_date':
        data = []
        for i in range(1, 13):
            num = engs.filter(start_date__month=i).count()
            data.append(num)
        data.append(len(projects) - sum(data))
        
    elif type == 'project_status':
        data = {'titles': [u'超前(> 5%)', u'穩定(-5% ~ 5%)', u'須注意(-5% ~ -10%)', u'落後(< -10%)]', u'未設定'], 'nums': []}

        a = 0
        b = 0
        c = 0
        d = 0
        for e in engs:
            delta_progress = e.act_inspector_percent - e.design_percent
            if delta_progress >= 5:
                a += 1
            elif delta_progress >= -5:
                b += 1
            elif delta_progress >= -10:
                c += 1
            else:
                d += 1
        data['nums'] = [a, b, c, d]
        data['nums'].append(len(projects) - sum(data['nums']))

    elif type == 'project_num':
        data = {'units': [], 'nums': []}
        for u in units[:-1]:
            data['units'].append(u.name)
            data['nums'].append(projects.filter(unit=u).count())
    
    elif type == 'project_photo':
        data = {u'0張': 0, u'0~100張': 0, u'101~200張': 0, u'201~300張': 0, u'301~400張': 0, u'401~500張': 0, u'500張以上': 0}
        title = [u'0張', u'0~100張', u'101~200張', u'201~300張', u'301~400張', u'401~500張', u'500張以上']
        photos = Photo.objects.filter(node__case__parent__in=projects)
        old_photos = Old_Photo.objects.filter(project__in=projects).exclude(file__isnull=True)
        print old_photos.count()
        for p in projects:
            if p.use_gallery:
                photos_num = photos.filter(node__case__parent=p).count()
            else:
                photos_num = old_photos.filter(project=p).count()
            if photos_num == 0: data[u'0張'] += 1
            elif photos_num <= 100: data[u'0~100張'] += 1
            elif photos_num <= 200: data[u'101~200張'] += 1
            elif photos_num <= 300: data[u'201~300張'] += 1
            elif photos_num <= 400: data[u'301~400張'] += 1
            elif photos_num <= 500: data[u'401~500張'] += 1
            else: data[u'500張以上'] += 1
        data = {'title': title, 'num': [data[i] for i in title]}

    return HttpResponse(json.dumps({'data': data}))


#縣市進度追蹤系統-申請結案
@login_required
def chase_connecter(R):
    if not R.user.has_perm('fishuser.sub_menu_management_system_city'):
        # 沒有 "第二層選單_工程管考系統_縣市進度追蹤"
        return HttpResponseRedirect('/')


    t = get_template(os.path.join('project', 'zh-tw', 'chase_connecter.html'))
    html = t.render(RequestContext(R,{
        'user': R.user,
        'years': years,
        'this_year': this_year,
        'option': _make_choose(),
        'places': places,
        'units': units,
        'chase_page': 'chase_connecter',
        'toppage_name': u'工程管考系統',
        'subpage_name': u'縣市進度追蹤',
        }))
    return HttpResponse(html)


#縣市進度追蹤系統-製造Excel
def chase_make_excel(R):
    search_result_ids = R.POST.get('ids', '').split(',') if R.POST.get('ids', '') else []
    
    output = StringIO()
    workbook = xlsxwriter.Workbook(output, 
        {'strings_to_numbers':  True,
        'strings_to_formulas': False,
        'strings_to_urls':     False})

    records = CountyChaseProjectOneToMany.objects.filter(id__in=search_result_ids).order_by('project__plan', 'project__name')
    if records:
        file_name = u'%s-縣市進度追蹤表' % records[0].countychasetime.chase_date
    else:
        file_name = u'%s-縣市進度追蹤表' % TODAY()

    workbook = make_chase_excel_file(workbook=workbook, records=records)

    workbook.close()
    output.seek(0)
    response = HttpResponse(output.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response['Content-Disposition'] = (u'attachment; filename=%s.xlsx' % (file_name)).encode('utf-8', 'replace')

    return response


#列印自定義報表
def print_custom_report(R, **kw):
    report_id = R.POST.get('custom_report', '')
    projects_id = R.POST['search_result_ids'].split(',')

    report = ExportCustomReport.objects.get(id=report_id)
    projects = Project.objects.filter(id__in=projects_id)
    file_name = R.user.user_profile.rName() + '-自定義報表-' + report.name
    output = StringIO()
    workbook = xlsxwriter.Workbook(output, 
        {'strings_to_numbers':  True,
        'strings_to_formulas': False,
        'strings_to_urls':     False})

    workbook = make_custom_report_excel_file(workbook=workbook, report=report, projects=projects)
    workbook.close()
    output.seek(0)
    response = HttpResponse(output.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response['Content-Disposition'] = ('attachment; filename=%s.xlsx' % (file_name)).encode('cp950')

    return response



@login_required
def set_manage_money(R):
    if not R.user.has_perm('fishuser.sub_menu_management_system_manage_money'):
        # 沒有 "第二層選單_工程管考系統_自辦工程管理費"
        return HttpResponseRedirect('/')

    year = R.POST.get('year', '')
    unit = R.POST.get('unit', '')

    projects = Project.objects.filter(deleter=None, undertake_type__value=u'自辦')

    managemoneys = ManageMoney.objects.filter(is_remain=False).filter(is_commission=False).order_by('-date')

    if year:
        managemoneys = managemoneys.filter(year=year)
        projects = projects.filter(year=year)
    if unit:
        projects = projects.filter(unit__id=unit)
        projectmanagemoney_ids = set([i.managemoney.id for i in ProjectManageMoney.objects.filter(project__in=projects,
                                                                                                  managemoney__in=managemoneys)])
        managemoneys = managemoneys.filter(id__in=projectmanagemoney_ids)

    project_id = []
    for i in managemoneys:
        if unit:
            project_manages = i.projectmanagemoney_set.filter(project__unit__id=unit)
        else:
            project_manages = i.projectmanagemoney_set.all()
        for p in project_manages:
            project_id.append(p.project.id)

    projects = projects.filter(id__in=project_id).order_by('-id')

    #各工程案的管理費計算
    for p in projects:
        p.manage = p.settlement_manage if p.settlement_manage else p.manage
        if not p.manage: p.manage = decimal.Decimal('0')
        p.use_manage = sum([i.money for i in ProjectManageMoney.objects.filter(project=p)])
        if p.use_manage >= p.manage:
            p.color = "danger"
        else:
            p.color = ''
        p.limit_money = p.manage - p.use_manage

    new_units = []
    for i in Unit.objects.filter(uplevel__name__in=[u'漁業署']).order_by('-uplevel', 'id'):
        new_units.append(i)
        new_units.extend([j for j in i.uplevel_subunit.all()])

    t = get_template(os.path.join('project', 'zh-tw', 'set_manage_money.html'))
    html = t.render(RequestContext(R,{
        'user': R.user,
        'years': years,
        'this_year': this_year,
        'option': _make_choose(),
        'units': new_units,
        'projects': projects,
        'toppage_name': u'工程管考系統',
        'subpage_name': u'自辦工程管理費',
        }))
    return HttpResponse(html)

@login_required
def manage_money(R):
    project_id = R.GET.get('id', '')
    project = Project.objects.get(id=project_id)

    project.manage = project.settlement_manage if project.settlement_manage else project.manage
    if not project.manage: project.manage = decimal.Decimal('0')
    project.use_manage = sum([i.money for i in ProjectManageMoney.objects.filter(project=project)])
    if project.use_manage >= project.manage:
        project.color = "danger"
    else:
        project.color = ''
    project.limit_money = project.manage - project.use_manage

    managemoneys = ManageMoney.objects.filter(is_remain=False).filter(is_commission=False).order_by('-date')
    projectmanagemoney_ids = set([i.managemoney.id for i in ProjectManageMoney.objects.filter(project=project)])
    managemoneys = managemoneys.filter(id__in=projectmanagemoney_ids)

    already_user_money = decimal.Decimal('0')
    for i in managemoneys:
        project_manages = i.projectmanagemoney_set.all()
        i.total_money = format(int(sum([p.money for p in project_manages])), ',')
        i.projects_manage_money_id = int(sum([p.id for p in project_manages]))

        already_user_money += sum([p.money for p in project_manages])

    t = get_template(os.path.join('project', 'zh-tw', 'manage_money.html'))
    html = t.render(RequestContext(R,{
        'user': R.user,
        'p': project,
        'managemoneys': managemoneys,
        }))
    return HttpResponse(html)

# @login_required
# def copy_money(R, **kw):
#     budget_id = kw['budget_id']
    
#     budget = Budget.objects.get(id=budget_id)
    
#     copy = Budget.objects.create(fund_id=budget.fund_id, year=budget.year, capital_ratify_budget=budget.capital_ratify_budget, capital_ratify_revision=budget.capital_ratify_revision, capital_ratify_local_budget=budget.capital_ratify_local_budget, capital_ratify_local_revision=budget.capital_ratify_local_revision, over_the_year=budget.over_the_year, proportion=budget.proportion, plan_id=budget.plan_id, priority=budget.priority, new=0, origin_budget=budget.id)
#     copy.save()

#     return HttpResponse(json.write({'status': 'success'}))



@login_required
def set_manage_money_remain(R):
    if not R.user.has_perm('fishuser.sub_menu_management_system_manage_money'):
        # 沒有 "第二層選單_工程管考系統_自辦工程管理費"
        return HttpResponseRedirect('/')

    t = get_template(os.path.join('project', 'zh-tw', 'set_manage_money_remain.html'))
    html = t.render(RequestContext(R,{
        'user': R.user,
        'years': years,
        'this_year': this_year,
        'option': _make_choose(),
        'toppage_name': u'工程管考系統',
        'subpage_name': u'自辦工程管理費',
        }))
    return HttpResponse(html)


@login_required
def get_manage_info(R):
    year = R.POST.get('year', '')
    unit = R.POST.get('unit', '')
    is_remain = R.POST.get('is_remain', 'false')
    is_commission = R.POST.get('is_commission', 'false')
    if is_remain == 'true':
        is_remain = True
    else:
        is_remain = False
    if is_commission == 'true':
        is_commission = True
    else:
        is_commission = False

    projects = Project.objects.filter(deleter=None, undertake_type__value=u'自辦')

    managemoneys = ManageMoney.objects.filter(is_remain=False).filter(is_commission=False).order_by('-date')
    managemoneys_remain = ManageMoney.objects.filter(is_commission=False).filter(is_remain=True).order_by('-date')



    if year:
        managemoneys = managemoneys.filter(year=year)
        managemoneys_remain = managemoneys_remain.filter(year=year)
        projects = projects.filter(year=year)
    if unit:
        projects = projects.filter(unit__id=unit)
        projectmanagemoney_ids = set([i.managemoney.id for i in ProjectManageMoney.objects.filter(project__in=projects,
                                                                                                  managemoney__in=managemoneys)])
        managemoneys = managemoneys.filter(id__in=projectmanagemoney_ids)

    limit_manage_money = decimal.Decimal('0')

    for p in projects:
        if p.settlement_manage:
            limit_manage_money += p.settlement_manage
        elif p.manage:
            limit_manage_money += p.manage

    data = []
    already_user_money = decimal.Decimal('0')
    for i in managemoneys:
        if unit:
            project_manages = i.projectmanagemoney_set.filter(project__unit__id=unit)
        else:
            project_manages = i.projectmanagemoney_set.all()
        data.append({
            'id': i.id,
            'year': i.year,
            'date': str(i.date),
            'name': i.name,
            'total_money': str(sum([p.money for p in project_manages])),
            'projects_manage_money': [
                {'id': p.id, 'project_id': p.project.id, 'project_name': p.project.name, 'money': str(p.money)} for p in
                project_manages],
        })
        already_user_money += sum([p.money for p in project_manages])

    #切分用
    project_id = []
    for i in managemoneys:
        if unit:
            project_manages = i.projectmanagemoney_set.filter(project__unit__id=unit)
        else:
            project_manages = i.projectmanagemoney_set.all()
        for p in project_manages:
            pid = p.project.id
            if pid not in project_id:
                project_id.append(pid)

    un_use_money = limit_manage_money - already_user_money
    remain_money = 0
    if is_remain:
        limit_manage_money = un_use_money
        data = []
        already_user_money = decimal.Decimal('0')
        for i in managemoneys_remain:
            project_manages = i.projectmanagemoney_set.all()
            data.append({
                'id': i.id,
                'year': i.year,
                'date': str(i.date),
                'name': i.name,
                'total_money': str(sum([p.money for p in project_manages])),
                'projects_manage_money': [
                    {'id': p.id, 'project_id': p.project.id, 'project_name': p.project.name, 'money': str(p.money)} for
                    p in project_manages],
            })
            already_user_money += sum([p.money for p in project_manages])

        un_use_money = limit_manage_money - already_user_money
        remain_money = str(ManageMoneyRemain.objects.get(year=year).money)
    return HttpResponse(json.dumps(
        {'limit_manage_money': str(limit_manage_money), 'already_user_money': str(already_user_money),
         'un_use_money': str(un_use_money), 'data': data, 'remain_money': remain_money, 'project_id': project_id}))


@login_required
def get_project_for_manage_money(R):
    year = R.POST.get('year', '')
    projects = Project.objects.filter(deleter=None, undertake_type__value=u'自辦', year=year)
    html = ''
    for p in projects:
        manage = p.settlement_manage if p.settlement_manage else p.manage
        if not manage: manage = decimal.Decimal('0')
        use_manage = sum([i.money for i in ProjectManageMoney.objects.filter(project=p)])
        if use_manage >= manage:
            color = "danger"
        else:
            color = ''
        limit_money = manage - use_manage
        html += '<tr class="%s"><td>%s<br>(%s)</td><td align="right">%s</td><td align="right">%s</td><td align="right">%s</td>' % (color, p.name, p.unit.name, format(int(float(str(manage))), ','), format(int(float(str(use_manage))), ','), format(int(float(str(limit_money))), ','))
        if use_manage >= manage:
            html += '<td></td>'
        else:
            html += '<td><button class="btn btn-success btn-sm add_projectmanagemoney" project_name="%s" limit_money="%s" project_id="%s"><span class="glyphicon glyphicon-plus"></span></button></td>' % (p.name, int(float(str(limit_money))), p.id)
        html += '</tr>'

    return HttpResponse(json.dumps({'html': html}))


@login_required
def project_for_manage_money(R):
    year = R.GET.get('year', '')
    projects = Project.objects.filter(deleter=None, undertake_type__value=u'自辦', year=year)

    for p in projects:
        p.manage = p.settlement_manage if p.settlement_manage else p.manage
        if not p.manage: p.manage = decimal.Decimal('0')
        p.use_manage = sum([i.money for i in ProjectManageMoney.objects.filter(project=p)])
        if p.use_manage >= p.manage:
            p.color = "danger"
        else:
            p.color = ''
        p.limit_money = p.manage - p.use_manage

    t = get_template(os.path.join('project', 'zh-tw', 'project_for_manage_money.html'))
    html = t.render(RequestContext(R,{
        'user': R.user,
        'year': year,
        'projects': projects,
        }))
    return HttpResponse(html)


@login_required
def project_for_manage_money_excel(R):
    year = R.GET.get('year', '')
    projects = Project.objects.filter(deleter=None, undertake_type__value=u'自辦', year=year)

    for p in projects:
        p.manage = p.settlement_manage if p.settlement_manage else p.manage
        if not p.manage: p.manage = decimal.Decimal('0')
        p.use_manage = sum([i.money for i in ProjectManageMoney.objects.filter(project=p)])
        if p.use_manage >= p.manage:
            p.color = "danger"
        else:
            p.color = ''
        p.limit_money = p.manage - p.use_manage

    file_name = u'%s年度-自辦工程費支用情形' % year
    output = StringIO()
    workbook = xlsxwriter.Workbook(output, 
        {'strings_to_numbers':  True,
        'strings_to_formulas': False,
        'strings_to_urls':     False})

    workbook = make_project_manage_money_excel(workbook=workbook, projects=projects)
    workbook.close()
    output.seek(0)
    response = HttpResponse(output.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response['Content-Disposition'] = ('attachment; filename=%s.xlsx' % (file_name)).encode('cp950')

    return response

@login_required
def set_manage_money_commission(R):
    if not R.user.has_perm('fishuser.sub_menu_management_system_manage_money_commission'):
        # 沒有 "第二層選單_工程管考系統_委辦工程管理費"
        return HttpResponseRedirect('/')

    new_units = []
    for i in Unit.objects.filter(uplevel__name__in=[u'漁業署']).order_by('-uplevel', 'id'):
        new_units.append(i)
        new_units.extend([j for j in i.uplevel_subunit.all()])

    t = get_template(os.path.join('project', 'zh-tw', 'set_manage_money_commission.html'))
    html = t.render(RequestContext(R,{
        'user': R.user,
        'years': years,
        'this_year': this_year,
        'option': _make_choose(),
        'units': new_units,
        'toppage_name': u'工程管考系統',
        'subpage_name': u'委辦工程管理費',
        }))
    return HttpResponse(html)



@login_required
def set_manage_money_commission_remain(R):
    if not R.user.has_perm('fishuser.sub_menu_management_system_manage_money_commission'):
        # 沒有 "第二層選單_工程管考系統_委辦工程管理費"
        return HttpResponseRedirect('/')

    t = get_template(os.path.join('project', 'zh-tw', 'set_manage_money_commission_remain.html'))
    html = t.render(RequestContext(R,{

        'user': R.user,
        'years': years,
        'this_year': this_year,
        'option': _make_choose(),
        'toppage_name': u'工程管考系統',
        'subpage_name': u'委辦工程管理費',
        }))
    return HttpResponse(html)



@login_required
def get_manage_commission_info(R):
    year = R.POST.get('year', '')
    unit = R.POST.get('unit', '')
    is_remain = R.POST.get('is_remain', 'false')
    is_commission = R.POST.get('is_commission', 'false')
    if is_remain == 'true':
        is_remain = True
    else:
        is_remain = False
    
    if is_commission == 'true':
        is_commission = True
    else:
        is_commission = False
    projects = Project.objects.filter(deleter=None, undertake_type__value=u'委辦')

    managemoneys = ManageMoney.objects.filter(is_remain=False).filter(is_commission=True).order_by('-date')
    managemoneys_remain = ManageMoney.objects.filter(is_commission=True).filter(is_remain=True).order_by('-date')

    if year:
        managemoneys = managemoneys.filter(year=year)
        managemoneys_remain = managemoneys_remain.filter(year=year)
        projects = projects.filter(year=year)
    if unit:
        projects = projects.filter(unit__id=unit)
        projectmanagemoney_ids = set([i.managemoney.id for i in ProjectManageMoney.objects.filter(project__in=projects,

                                                                                                  managemoney__in=managemoneys)])
        managemoneys = managemoneys.filter(id__in=projectmanagemoney_ids)
 

    limit_manage_money = decimal.Decimal('0')

    for p in projects:
        if p.cm_settlement_value:
            limit_manage_money += p.cm_settlement_value
        elif p.cm_value:
            limit_manage_money += p.cm_value
 
    data = []
    already_user_money = decimal.Decimal('0')
    
    for i in managemoneys:
        if unit:
            project_manages = i.projectmanagemoney_set.filter(project__unit__id=unit)
        else:
            project_manages = i.projectmanagemoney_set.all()
        data.append({
            'id': i.id,
            'year': i.year,
            'date': str(i.date),
            'name': i.name,
            'total_money': str(sum([p.money for p in project_manages])),
            'projects_manage_money': [
                {'id': p.id, 'project_id': p.project.id, 'project_name': p.project.name, 'money': str(p.money)} for p in
                project_manages],
        })
        already_user_money += sum([p.money for p in project_manages])


    un_use_money = limit_manage_money - already_user_money
    remain_money = 0
    if is_remain:
        limit_manage_money = un_use_money
        data = []
        already_user_money = decimal.Decimal('0')
        for i in managemoneys_remain:
            project_manages = i.projectmanagemoney_set.all()
            data.append({
                'id': i.id,
                'year': i.year,
                'date': str(i.date),
                'name': i.name,
                'total_money': str(sum([p.money for p in project_manages])),
                'projects_manage_money': [
                    {'id': p.id, 'project_id': p.project.id, 'project_name': p.project.name, 'money': str(p.money)} for
                    p in project_manages],
            })
            already_user_money += sum([p.money for p in project_manages])

        un_use_money = limit_manage_money - already_user_money
        remain_money = str(ManageMoneyRemain.objects.get(year=year).money)

    return HttpResponse(json.dumps(
        {'limit_manage_money': str(limit_manage_money), 'already_user_money': str(already_user_money),
         'un_use_money': str(un_use_money), 'data': data, 'remain_money': remain_money}))


@login_required
def get_project_for_manage_money_commission(R):
    year = R.POST.get('year', '')
    projects = Project.objects.filter(deleter=None, undertake_type__value=u'委辦', year=year)
    html = ''
    for p in projects:
        manage = p.cm_settlement_value if p.cm_settlement_value else p.cm_value
        if not manage: manage = decimal.Decimal('0')
        use_manage = sum([i.money for i in ProjectManageMoney.objects.filter(project=p)])
        if use_manage >= manage:
            color = "danger"
        else:
            color = ''
        limit_money = manage - use_manage
        html += '<tr class="%s"><td>%s<br>(%s)</td><td align="right">%s</td><td align="right">%s</td><td align="right">%s</td>' % (color, p.name, p.unit.name, format(int(float(str(manage))), ','), format(int(float(str(use_manage))), ','), format(int(float(str(limit_money))), ','))
        if use_manage >= manage:
            html += '<td></td>'
        else:
            html += '<td><button class="btn btn-success btn-sm add_projectmanagemoney" project_name="%s" limit_money="%s" project_id="%s"><span class="glyphicon glyphicon-plus"></span></button></td>' % (p.name, int(float(str(limit_money))), p.id)
        html += '</tr>'

    return HttpResponse(json.dumps({'html': html}))


@login_required
def project_for_manage_money_commission(R):
    year = R.GET.get('year', '')
    projects = Project.objects.filter(deleter=None, undertake_type__value=u'委辦', year=year)

    for p in projects:
        p.manage = p.cm_settlement_value if p.cm_settlement_value else p.cm_value
        if not p.manage: p.manage = decimal.Decimal('0')
        p.use_manage = sum([i.money for i in ProjectManageMoney.objects.filter(project=p)])
        if p.use_manage >= p.manage:
            p.color = "danger"
        else:
            p.color = ''
        p.limit_money = p.manage - p.use_manage

    t = get_template(os.path.join('project', 'zh-tw', 'project_for_manage_money_commission.html'))
    html = t.render(RequestContext(R,{
        'user': R.user,
        'year': year,
        'projects': projects,
        }))
    return HttpResponse(html)


@login_required
def project_for_manage_money_commission_excel(R):
    year = R.GET.get('year', '')
    projects = Project.objects.filter(deleter=None, undertake_type__value=u'委辦', year=year)

    for p in projects:
        p.manage = p.cm_settlement_value if p.cm_settlement_value else p.cm_value
        if not p.manage: p.manage = decimal.Decimal('0')
        p.use_manage = sum([i.money for i in ProjectManageMoney.objects.filter(project=p)])
        if p.use_manage >= p.manage:
            p.color = "danger"
        else:
            p.color = ''
        p.limit_money = p.manage - p.use_manage

    file_name = u'%s年度-委辦工程費支用情形' % year
    output = StringIO()
    workbook = xlsxwriter.Workbook(output, 
        {'strings_to_numbers':  True,
        'strings_to_formulas': False,
        'strings_to_urls':     False})

    workbook = make_project_manage_money_excel(workbook=workbook, projects=projects)
    workbook.close()
    output.seek(0)
    response = HttpResponse(output.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response['Content-Disposition'] = ('attachment; filename=%s.xlsx' % (file_name)).encode('cp950')

    return response

@login_required
def renew_bid_money_statistic_table(R):
    project = Project.objects.get(id=R.POST.get('project_id', ''))
    data = {}
    data['construction_bid_total'] = int(float(str(project.rconstruction_bid())))
    data['construction_bid_use'] = int(float(str(sum([i.num for i in Appropriate.objects.filter(project=project, type__value=u'工程款').exclude(num=None)]))))
    data['construction_bid_left'] = data['construction_bid_total'] - data['construction_bid_use']
    data['construction_bid_left_percent'] = '%s%%' % round(data['construction_bid_left']*100. / data['construction_bid_total'] if data['construction_bid_total'] else 0, 3)
    bidmoneys = ProjectBidMoney.objects.filter(project=project, field_type__value__in=[u'規劃費', u'設計金額', u'監造金額'])
    data['planning_design_inspect_total'] = 0
    if bidmoneys:
        for i in bidmoneys:
            if i.settlement_value: value = i.settlement_value
            elif i.value: value = i.value
            else: value = 0
            data['planning_design_inspect_total'] += int(float(str(value)))
    else:
        if project.settlement_planning_design_inspect:
            data['planning_design_inspect_total'] = int(float(str(project.settlement_planning_design_inspect)))
        elif project.planning_design_inspect:
            data['planning_design_inspect_total'] = int(float(str(project.planning_design_inspect)))
        else:
            data['planning_design_inspect_total'] = 0
    data['planning_design_inspect_use'] = int(float(str(sum([i.num for i in Appropriate.objects.filter(project=project, type__value=u'勞務類').exclude(num=None)]))))
    data['planning_design_inspect_left'] = data['planning_design_inspect_total'] - data['planning_design_inspect_use']
    data['planning_design_inspect_left_percent'] = '%s%%' % round(data['planning_design_inspect_left']*100. / data['planning_design_inspect_total'] if data['planning_design_inspect_total'] else 0, 3)
    data['manage_total'] = int(float(str(project.rmanage())))
    data['manage_use'] = int(float(str(sum([i.money for i in ProjectManageMoney.objects.filter(project=project).exclude(money=None)]))))
    data['manage_left'] = data['manage_total'] - data['manage_use']
    data['manage_percent'] = '%s%%' % round(data['manage_left']*100. / data['manage_total'] if data['manage_total'] else 0, 3)
    result = []
    for i in data:
        result.append([i, data[i]])

    return HttpResponse(json.dumps({'result': result}))


@login_required
def add_projectbidmoneyversion(R):
    project = Project.objects.get(id=R.POST.get('project_id', ''))
    if ProjectBidMoneyVersion.objects.filter(date=R.POST.get('date', '')):
        return HttpResponse(json.dumps({'msg': u'新增失敗!!! 已有此日期紀錄。'}))
    version = ProjectBidMoneyVersion(
            project = project,
            date = R.POST.get('date', ''),
            no = R.POST.get('no', ''),
            memo = R.POST.get('memo', '')
        )
    version.save()

    field_name = [['construction_bid', u'工程金額'], ['safety_fee', u'保險費'], ['business_tax', u'營業稅'], 
                  ['planning_design_inspect', u'規劃設計監造費'], ['manage', u'工程管理費'], ['pollution', u'空污費']]
    for i in field_name:
        row = ProjectBidMoneyVersionDetail(
                version = version,
                field_name = i[1],
                value = getattr(project, i[0]),
                settlement_value = getattr(project, 'settlement_%s' % i[0]),
                memo = getattr(project, '%s_memo' % i[0]),
            )
        row.save()
    for j in ProjectBidMoney.objects.filter(project=project):
        row = ProjectBidMoneyVersionDetail(
                version = version,
                field_name = j.field_type.value,
                value = j.value,
                settlement_value = j.settlement_value,
                memo = j.memo
            )
        row.save()

    return HttpResponse(json.dumps({'msg': u'新增成功。'}))


@login_required
def get_projectbidmoneyversion(R):
    project = Project.objects.get(id=R.POST.get('project_id', ''))
    
    if R.user.has_perm('fishuser.edit_all_project_in_management_system'):
        #管考人員
        edit = True #編輯資料權限
    else:
        edit = False

    field_name = [['construction_bid', u'工程金額'], ['safety_fee', u'保險費'], ['business_tax', u'營業稅'], 
                  ['planning_design_inspect', u'規劃設計監造費'], ['manage', u'工程管理費'], ['pollution', u'空污費']]

    this_version = ProjectBidMoneyVersion(
            project=project,
            date=TODAY(),
        )
    this_version.details = []
    for i in field_name:
        row = ProjectBidMoneyVersionDetail(
                version = this_version,
                field_name = i[1],
                value = getattr(project, i[0]),
                settlement_value = getattr(project, 'settlement_%s' % i[0]),
                memo = getattr(project, '%s_memo' % i[0]),
            )
        this_version.details.append(row)

    for j in ProjectBidMoney.objects.filter(project=project):
        row = ProjectBidMoneyVersionDetail(
                version = this_version,
                field_name = j.field_type.value,
                value = j.value,
                settlement_value = j.settlement_value,
                memo = j.memo
            )
        this_version.details.append(row)

    pre_versions = ProjectBidMoneyVersion.objects.filter(project=project).order_by('-date')
    for v in pre_versions:
        v.details = ProjectBidMoneyVersionDetail.objects.filter(version=v).order_by('id')

    versions = [this_version] + list(pre_versions)

    for n, v in enumerate(versions):
        if n == len(versions)-1:
            v.version_name = u"原始契約"
        else:
            v.version_name = u"%s變更" % versions[n+1].date
            if n == 0:
                v.version_name += u'(目前)'
            v.pre_version = versions[n+1]

    t = get_template(os.path.join('project', 'zh-tw', 'projectbidmoneyversion_for_dialog.html'))
    html = t.render(RequestContext(R,{
        'edit': edit,
        'user': R.user,
        'versions': versions,
        }))

    return HttpResponse(json.dumps({'html': html}))





# 以下舊分頁------------------------------------------------------------------
# def _syncPCCData(project=False, pcc_no=False):
#     if project:
#         pcc_no = Project.pcc_no
#     try: syncPccInformation(pcc_no)
#     except: return 'False!!SYNCFail!!'
#     if not project and pcc_no != '':
#         try: project = Project.objects.get(pcc_no=pcc_no)
#         except Project.DoesNotExist: return 'False!!ProjectNotExist!!'
#     try: pcc_record = PCCProject.objects.get(uid=pcc_no)
#     except PCCProject.DoesNotExist: return 'False!!PCCRecordNotExist!!'

#     obo = CountyChaseProjectOneByOne.objects.get(project=project)
#     obo.sch_eng_plan_acceptance_closed = pcc_record.s_design_complete_date
#     obo.act_eng_plan_acceptance_closed = pcc_record.r_design_complete_date
#     obo.sch_eng_plan_signed_tender = pcc_record.s_public_date
#     obo.sch_eng_do_signed_tender = pcc_record.s_public_date
#     obo.act_eng_plan_signed_tender = pcc_record.r_public_date
#     obo.act_eng_do_signed_tender = pcc_record.r_public_date
#     obo.sch_eng_plan_announcement_tender = pcc_record.s_decide_tenders_date
#     obo.sch_eng_do_announcement_tender = pcc_record.s_decide_tenders_date
#     obo.act_eng_plan_announcement_tender = pcc_record.r_decide_tenders_date
#     obo.act_eng_do_announcement_tender = pcc_record.r_decide_tenders_date
#     obo.sch_eng_do_start = pcc_record.s_start_date
#     obo.act_eng_do_start = pcc_record.r_start_date
#     obo.sch_eng_do_completion = pcc_record.s_end_date
#     obo.act_eng_do_completion = pcc_record.r_end_date
#     obo.act_eng_do_acceptance = pcc_record.r_checked_and_accepted_date
#     obo.sch_eng_do_closed = pcc_record.s_last_pay_date
#     obo.act_eng_do_closed = pcc_record.r_last_pay_date
#     if pcc_record.s_end_date2:
#         obo.eng_do_completion_memo = '變更前：' + str(pcc_record.s_end_date)
#         obo.sch_eng_do_completion = pcc_record.s_end_date2
#     obo.save()

#     pcc_progress = PCCProgress.objects.filter(project=pcc_record).order_by('year', 'month')
#     for p in pcc_progress:
#         pcc_sync_date = p.lastsync
#         pcc_record = p.project
#         year = p.year
#         month = p.month
#         total_s_progress = decimal.Decimal(str(p.percentage_of_predict_progress*100))
#         total_r_progress = decimal.Decimal(str(p.percentage_of_real_progress*100))
#         total_s_money = decimal.Decimal(str(p.money_of_predict_progress))
#         total_r_money = decimal.Decimal(str(p.money_of_real_progress))
#         total_pay = decimal.Decimal(str(p.totale_money_paid))
#         s_memo = p.s_memo
#         r_memo = p.r_memo
#         if p.status == '設計中': option_id = 162
#         elif p.status == '施工中': option_id = 165
#         elif p.status == '停工': option_id = 166
#         elif p.status == '完工待驗收': option_id = 167
#         elif p.status == '驗收完成': option_id = 168
#         elif p.status == '已結案': option_id = 213
#         elif p.status == '解約': option_id = 214
#         elif p.status == '解約重新發包': option_id = 235
#         elif p.status == '準備招標文件中': option_id = 236
#         elif p.status == '公告中': option_id = 237
#         elif p.status == '審標中': option_id = 238
#         elif p.status == '未開工': option_id = 239
#         elif p.status == '準備開工中': option_id = 240
#         elif p.status == '驗收': option_id = 241
#         else: option_id = False
#         if option_id: status = Option.objects.get(id=option_id)
#         else: status = None
#         try:
#             record = RelayInfo.objects.get(project__pcc_no=pcc_no, year=year, month=month)
#             setattr(record, 'pcc_sync_date', pcc_sync_date)
#             setattr(record, 'total_s_progress', total_s_progress)
#             setattr(record, 'total_r_progress', total_r_progress)
#             setattr(record, 'total_s_money', total_s_money)
#             setattr(record, 'total_r_money', total_r_money)
#             setattr(record, 'total_pay', total_pay)
#             setattr(record, 's_memo', s_memo)
#             setattr(record, 'r_memo', r_memo)
#             setattr(record, 'status', status)
#             record.save()
#         except RelayInfo.DoesNotExist:
#             newRecord = RelayInfo(
#                             project = project,
#                             pcc_record = pcc_record,
#                             pcc_sync_date = pcc_sync_date,
#                             year = year,
#                             month = month,
#                             date = datetime.datetime.strptime(str(year+1911)+'-'+str(month)+'-'+str(calendar.monthrange(year+1911, month)[1]), '%Y-%m-%d'),
#                             total_s_progress = total_s_progress,
#                             total_r_progress = total_r_progress,
#                             total_s_money = total_s_money,
#                             total_r_money = total_r_money,
#                             total_pay = total_pay,
#                             s_memo = s_memo,
#                             r_memo = r_memo,
#                             status = status,
#                             )
#             newRecord.save()


#         except: return 'False!!DataError!!'
#     return project

# def _syncProgress(relay_progress, user):
#     newProgress = Progress(
#         project = relay_progress.project,
#         date = relay_progress.date,
#         schedul_progress_percent = relay_progress.total_s_progress,
#         actual_progress_percent = relay_progress.total_r_progress,
#         status = relay_progress.status,
#         record_date = TODAY(),
#         source = relay_progress,
#         editer = user,
#     )
#     newProgress.save()
#     return newProgress

# def _syncFundRecord(relay_progress):
#     try:
#         row = FundRecord.objects.get(project=relay_progress.project, date=relay_progress.date)
#         row.total_s_money = relay_progress.total_s_money
#         row.total_pay = relay_progress.total_pay
#         row.record_date = TODAY()
#         row.reocrd_source = relay_progress
#         row.save()
#     except:
#         newFundRecord = FundRecord(
#             project = relay_progress.project,
#             year = relay_progress.date.year - 1911,
#             date = relay_progress.date,
#             total_s_money = relay_progress.total_s_money,
#             total_pay = relay_progress.total_pay,
#             record_date = TODAY(),
#             reocrd_source = relay_progress,
#         )
#         newFundRecord.save()
#     return newFundRecord


# def _updateFundRecord(project='',date='', record='', item=''):
#     # TODO: 重新整理...
#     total_budget = ['design_bid', 'inspect_bid', 'construction_bid', 'pollution', 'manage', 'other_defray', 'allot_rate']
#     record_date = ['record_date',]
#     record_add = ['new_record',]
#     record_money = ['self_payout',]
#     record_nums = ['actual_progress_percent', 'date', 'num', 'allot_date', 'self_payout', 'delete']
#     if item in total_budget:
#         fund_records = FundRecord.objects.filter(project=project)
#         years = []
#         for i in fund_records:
#             setattr(i, 'self_budget',i.cSelfBudget())
#             i.save()
#             setattr(i, 'local_budget',i.cLocalBudget())
#             i.save()
#             setattr(i, 'local_payout',i.cLocalPayout())
#             i.save()
#             setattr(i, 'sum_self_payout',i.cSumSelfPayout())
#             i.save()
#             setattr(i, 'sum_local_payout',i.cSumLocalPayout())
#             i.save()
#             setattr(i, 'self_load',i.cSelfLoad())
#             i.save()
#             setattr(i, 'payment',i.cPayment())
#             i.save()
#             setattr(i, 'self_past_budget',i.cSelfPastBudget())
#             i.save()
#             setattr(i, 'local_past_budget',i.cLocalPastBudget())
#             i.save()
#             setattr(i, 'progress',i.cProgress())
#             i.save()
#             setattr(i, 'self_surplus',i.cSelfSurplus())
#             i.save()
#             setattr(i, 'local_surplus',i.cLocalSurplus())
#             i.save()
#             setattr(i, 'self_unpay',i.cSelfUnpay())
#             i.save()
#             setattr(i, 'local_unpay',i.cLocalUnpay())
#             i.save()
#             if i.year not in years:
#                 years.append(i.year)
#         for y in years:
#             _updateFund(project=project, year=y)
#     if item in record_date:
#         setattr(record, 'self_budget',record.cSelfBudget())
#         setattr(record, 'local_budget',record.cLocalBudget())
#         setattr(record, 'local_payout',record.cLocalPayout())
#         setattr(record, 'sum_self_payout',record.cSumSelfPayoutByInfo(date=date))
#         setattr(record, 'sum_local_payout',record.cSumLocalPayoutByInfo(date=date))
#         setattr(record, 'self_load',record.cSelfLoad())
#         setattr(record, 'payment',record.cPaymentByInfo(date=date))
#         setattr(record, 'self_past_budget',record.cSelfPastBudget())
#         setattr(record, 'local_past_budget',record.cLocalPastBudget())
#         setattr(record, 'progress',record.cProgressByInfo(date=date))
#         setattr(record, 'self_surplus',record.cSelfSurplus())
#         setattr(record, 'local_surplus',record.cLocalSurplus())
#         setattr(record, 'self_unpay',record.cSelfUnpay())
#         setattr(record, 'local_unpay',record.cLocalUnpay())
#         record.save()
#         fund_records = list(FundRecord.objects.filter(project=record.project, year=record.year))
#         for i in fund_records:
#             setattr(i, 'sum_self_payout',i.cSumSelfPayout())
#             record.save()
#             setattr(i, 'sum_local_payout',i.cSumLocalPayout())
#             i.save()
#     if item in record_money:
#         setattr(record, 'self_budget',record.cSelfBudget())
#         record.save()
#         setattr(record, 'local_budget',record.cLocalBudget())
#         record.save()
#         setattr(record, 'local_payout',record.cLocalPayout())
#         record.save()
#         setattr(record, 'sum_self_payout',record.cSumSelfPayout())
#         record.save()
#         setattr(record, 'sum_local_payout',record.cSumLocalPayout())
#         record.save()
#         setattr(record, 'self_load',record.cSelfLoad())
#         record.save()
#         setattr(record, 'payment',record.cPayment())
#         record.save()
#         setattr(record, 'self_past_budget',record.cSelfPastBudget())
#         record.save()
#         setattr(record, 'local_past_budget',record.cLocalPastBudget())
#         record.save()
#         setattr(record, 'progress',record.cProgress())
#         record.save()
#         setattr(record, 'self_surplus',record.cSelfSurplus())
#         record.save()
#         setattr(record, 'local_surplus',record.cLocalSurplus())
#         record.save()
#         setattr(record, 'self_unpay',record.cSelfUnpay())
#         record.save()
#         setattr(record, 'local_unpay',record.cLocalUnpay())
#         record.save()
#         _updateFund(project=record.project, year=record.year)
#     if item in record_add:
#         setattr(record, 'self_budget',record.cSelfBudget())
#         setattr(record, 'local_budget',record.cLocalBudget())
#         setattr(record, 'local_payout',record.cLocalPayout())
#         setattr(record, 'sum_self_payout',record.cSumSelfPayout())
#         setattr(record, 'sum_local_payout',record.cSumLocalPayout())
#         setattr(record, 'self_load',record.cSelfLoad())
#         setattr(record, 'payment',record.cPayment())
#         setattr(record, 'self_past_budget',record.cSelfPastBudget())
#         setattr(record, 'local_past_budget',record.cLocalPastBudget())
#         setattr(record, 'progress',record.cProgress())
#         setattr(record, 'self_surplus',record.cSelfSurplus())
#         setattr(record, 'local_surplus',record.cLocalSurplus())
#         setattr(record, 'self_unpay',record.cSelfUnpay())
#         setattr(record, 'local_unpay',record.cLocalUnpay())
#         record.save()
#         _updateFund(project=record.project, year=record.year)
#     if item in record_nums:
#         fund_records = list(FundRecord.objects.filter(project=project))
#         years = []
#         for fund_record in fund_records:
#             setattr(fund_record, 'progress',fund_record.cProgress())
#             fund_record.save()
#             setattr(fund_record, 'self_budget',fund_record.cSelfBudget())
#             fund_record.save()
#             setattr(fund_record, 'local_budget',fund_record.cLocalBudget())
#             fund_record.save()
#             setattr(fund_record, 'local_payout',fund_record.cLocalPayout())
#             fund_record.save()
#             setattr(fund_record, 'sum_self_payout',fund_record.cSumSelfPayout())
#             fund_record.save()
#             setattr(fund_record, 'sum_local_payout',fund_record.cSumLocalPayout())
#             fund_record.save()
#             setattr(fund_record, 'self_load',fund_record.cSelfLoad())
#             fund_record.save()
#             setattr(fund_record, 'payment',fund_record.cPayment())
#             fund_record.save()
#             setattr(fund_record, 'self_past_budget',fund_record.cSelfPastBudget())
#             fund_record.save()
#             setattr(fund_record, 'local_past_budget',fund_record.cLocalPastBudget())
#             fund_record.save()
#             setattr(fund_record, 'self_surplus',fund_record.cSelfSurplus())
#             fund_record.save()
#             setattr(fund_record, 'local_surplus',fund_record.cLocalSurplus())
#             fund_record.save()
#             setattr(fund_record, 'self_unpay',fund_record.cSelfUnpay())
#             fund_record.save()
#             setattr(fund_record, 'local_unpay',fund_record.cLocalUnpay())
#             fund_record.save()
#             if fund_record.year not in years:
#                 years.append(fund_record.year)
#         for y in years:
#             _updateFund(project=project, year=y)


# def _updateFund(project='', year=''):
#     last_record = list(FundRecord.objects.filter(project=project, year=year).order_by('-record_date'))[0]
#     fund = Fund.objects.get(project=project, year=year)
#     setattr(fund, 'record_date',last_record.record_date)
#     setattr(fund, 'self_budget',last_record.self_budget)
#     setattr(fund, 'local_budget',last_record.local_budget)
#     setattr(fund, 'sum_self_payout',last_record.sum_self_payout)
#     setattr(fund, 'sum_local_payout',last_record.sum_local_payout)
#     setattr(fund, 'self_load',last_record.self_load)
#     setattr(fund, 'self_past_budget',last_record.self_past_budget)
#     setattr(fund, 'local_past_budget',last_record.local_past_budget)
#     setattr(fund, 'payment',last_record.payment)
#     setattr(fund, 'self_unpay',last_record.self_unpay)
#     setattr(fund, 'local_unpay',last_record.local_unpay)
#     setattr(fund, 'self_surplus',last_record.self_surplus)
#     setattr(fund, 'local_surplus',last_record.local_surplus)
#     setattr(fund, 'progress',last_record.progress)
#     fund.save()

# #resdJson 搬家了

# @checkAuthority
# def searchAdvancedProject(R, project, right_type_value=u'觀看管考系統資料'):
#     user, DATA = R.user, readDATA(R)

#     plans = []
#     for i in Plan.objects.filter(uplevel=None):
#         i.name = '---' * i.rLevelNumber() + i.name
#         plans.append(i)
#         for j in i.rSubPlanInList():
#             j.name = '---' * j.rLevelNumber() + j.name
#             plans.append(j)
#     years = [y-1911 for y in xrange(2006, TODAY().year+2)]
#     years.reverse()
#     units = []
#     for i in Unit.fish_city_menu.all():
#         units.append(i)
#         if i.uplevel and i.uplevel.name != '縣市政府':
#             temp = []
#             for j in i.uplevel_subunit.all():
#                 j.name = '---' + j.name
#                 temp.append(j)
#             units.extend(temp)
#     statuss = [i for i in _getProjectStatusInList()]
    
#     default_projects = [p.project for p in DefaultProject.objects.filter(user=user)]
#     for i in default_projects:
#         i.short_plan_name = i.plan.name[:5] + '...'

#     projects_num = -1
#     projects = []
#     querystring = ''
#     INFO = {}
#     for k, v in R.GET.items(): INFO[k] = v
#     for k, v in R.POST.items(): INFO[k] = v

#     for k in INFO:
#         if k in ['plan1', 'plan2', 'plan3', 'project_sub_type',
#                  'year_lb', 'year_ub', 'unit1', 'unit2', 'unit3',
#                  'status1', 'status2', 'status3', 'budget_type', 'budget_sub_type', 'undertake_type']:
#             try: INFO[k] = int(INFO[k])
#             except: pass

#     if INFO.get('submit', None):
#         querystring = '&'.join(['%s=%s'%(k, v) for k, v in INFO.items() if k != 'page'])
#         projects, projects_num = _searchAdvancedProject(INFO)

#     for i in default_projects: i.default = i.isdefault(user)
#     for i in projects:
#         i.default = i.isdefault(user)

#     budget_types = Option.objects.filter(swarm='budget_type')
#     budget_sub_types = Option.objects.filter(swarm='budget_sub_type')
#     undertake_types = Option.objects.filter(swarm='undertake_type')

#     for n, i in enumerate(projects):
#         i.short_plan_name = i.plan.name[:5] + '...'

#     if _ca(user=user, project='', project_id=0, right_type_value=u'刪除管考工程案'):
#         delete = True
#     else:
#         delete = False

#     t = get_template(os.path.join('project', 'advancedsearch.html'))
#     html = t.render(RequestContext(R, {
#         'default_projects':default_projects,
#         'projects': projects,
#         'units': units,
#         'years': years,
#         'plans': plans,
#         'statuss': statuss,
#         'budget_types': budget_types,
#         'budget_sub_types': budget_sub_types,
#         'undertake_types': undertake_types,
#         'INFO': INFO,
#         'sortBy': INFO.get('sortBy', None) or 'year',
#         'page_list': makePageList(INFO.get('page', 1), projects_num, NUMPERPAGE),
#         'querystring': querystring,
#         'projects_num': projects_num,
#         'option' : _make_choose(),
#         'delete': delete,
#         }))
#     return HttpResponse(html)

# def _searchAdvancedProject_FilterRule(result=[], INFO={}, field_name='', ids1=[], ids2=[], ids3=[], have1=False, have2=False, have3=False, temp=[]):
#     if have1:
#         if have2 and not have3:
#             if INFO.get(field_name + '_and1', None) == 'and':
#                 for i in ids1:
#                     if i in ids2: temp.append(i)
#             elif INFO.get(field_name + '_and1', None) == 'or':
#                 temp += ids1
#                 for i in ids2:
#                     if i not in temp: temp.append(i)
#         elif have3 and not have2:
#             if INFO.get(field_name + '_and2', None) == 'and':
#                 for i in ids1:
#                     if i in ids3: temp.append(i)
#             elif INFO.get(field_name + '_and2', None) == 'or':
#                 temp += ids1
#                 for i in ids3:
#                     if i not in temp: temp.append(i)
#         elif have2 and have3:
#             if INFO.get(field_name + '_and1', None) == 'and' and INFO.get(field_name + '_and2', None) == 'and':
#                 for i in ids1:
#                     if i in ids2 and i in ids3: temp.append(i)
#             elif INFO.get(field_name + '_and1', None) == 'or' and INFO.get(field_name + '_and2', None) == 'or':
#                 temp += ids1
#                 for i in ids2 + ids3:
#                     if i not in temp: temp.append(i)
#             elif INFO.get(field_name + '_and1', None) == 'and' and INFO.get(field_name + '_and2', None) == 'or':
#                 for i in ids1:
#                     if i in ids2: temp.append(i)
#                 for i in ids3:
#                     if i not in temp: temp.append(i)
#             elif INFO.get(field_name + '_and1', None) == 'or' and INFO.get(field_name + '_and2', None) == 'and':
#                 for i in ids2:
#                     if i in ids3: temp.append(i)
#                 for i in ids1:
#                     if i not in temp: temp.append(i)
#         else:
#             temp = ids1
#         result = result.filter(id__in=temp)
#     elif have2:
#         if have3 and INFO.get(field_name + '_and2', None) == 'and':
#             for i in ids2:
#                 if i in ids3: temp.append(i)
#         elif have3 and INFO.get(field_name + '_and2', None) == 'or':
#             temp += ids2
#             for i in ids3:
#                 if i not in temp: temp.append(i)
#         else:
#             temp = ids2
#         result = result.filter(id__in=temp)
#     elif have3 and not have1 and not have2:
#         temp = ids3
#         result = result.filter(id__in=temp)

#     return result

# def _searchAdvancedProject(INFO):
#     result = Project.objects.filter(deleter=None).order_by('name', 'budget_type', INFO.get('sortBy', None))

#     [ids1, ids2, ids3, have1, have2, have3, temp] = [[], [], [], False, False, False, []]
#     if INFO.get('bid_no1', None) and INFO.get('bid_no1', None) != '':
#         have1 = True
#         for bid_no in re.split('[ ,]+', INFO.get('bid_no1', None)):
#             ids1.extend([i.id for i in result.filter(bid_no__icontains=bid_no)])
#     if INFO.get('bid_no2', None) and INFO.get('bid_no2', None) != '':
#         have2 = True
#         for bid_no in re.split('[ ,]+', INFO.get('bid_no2', None)):
#             ids2.extend([i.id for i in result.filter(bid_no__icontains=bid_no)])
#     if INFO.get('bid_no3', None) and INFO.get('bid_no3', None) != '':
#         have3 = True
#         for bid_no in re.split('[ ,]+', INFO.get('bid_no3', None)):
#             ids3.extend([i.id for i in result.filter(bid_no__icontains=bid_no)])
#     result = _searchAdvancedProject_FilterRule(result=result, INFO=INFO, field_name='bid_no', ids1=ids1, ids2=ids2, ids3=ids3, have1=have1, have2=have2, have3=have3, temp=[])

#     [ids1, ids2, ids3, have1, have2, have3, temp] = [[], [], [], False, False, False, []]
#     if INFO.get('vouch_no1', None) and INFO.get('vouch_no1', None) != '':
#         have1 = True
#         for vouch_no in re.split('[ ,]+', INFO.get('vouch_no1', None)):
#             ids1.extend([i.id for i in result.filter(vouch_no__icontains=vouch_no)])
#     if INFO.get('vouch_no2', None) and INFO.get('vouch_no2', None) != '':
#         have2 = True
#         for vouch_no in re.split('[ ,]+', INFO.get('vouch_no2', None)):
#             ids2.extend([i.id for i in result.filter(vouch_no__icontains=vouch_no)])
#     if INFO.get('vouch_no3', None) and INFO.get('vouch_no3', None) != '':
#         have3 = True
#         for vouch_no in re.split('[ ,]+', INFO.get('vouch_no3', None)):
#             ids3.extend([i.id for i in result.filter(vouch_no__icontains=vouch_no)])
#     result = _searchAdvancedProject_FilterRule(result=result, INFO=INFO, field_name='vouch_no', ids1=ids1, ids2=ids2, ids3=ids3, have1=have1, have2=have2, have3=have3, temp=[])

#     [ids1, ids2, ids3, have1, have2, have3, temp] = [[], [], [], False, False, False, []]
#     if INFO.get('name1', None) and INFO.get('name1', None) != '':
#         have1 = True
#         for name in re.split('[ ,]+', INFO.get('name1', None)):
#             ids1.extend([i.id for i in result.filter(name__icontains=name)])
#     if INFO.get('name2', None) and INFO.get('name2', None) != '':
#         have2 = True
#         for name in re.split('[ ,]+', INFO.get('name2', None)):
#             ids2.extend([i.id for i in result.filter(name__icontains=name)])
#     if INFO.get('name3', None) and INFO.get('name3', None) != '':
#         have3 = True
#         for name in re.split('[ ,]+', INFO.get('name3', None)):
#             ids3.extend([i.id for i in result.filter(name__icontains=name)])
#     result = _searchAdvancedProject_FilterRule(result=result, INFO=INFO, field_name='name', ids1=ids1, ids2=ids2, ids3=ids3, have1=have1, have2=have2, have3=have3, temp=[])

#     [ids1, ids2, ids3, have1, have2, have3, temp] = [[], [], [], False, False, False, []]
#     if INFO.get('plan1', None) and INFO.get('plan1', None) != '':
#         have1 = True
#         plan = Plan.objects.get(id=INFO.get('plan1', None))
#         ids1.extend([i.id for i in result.filter(plan=plan)])
#         if INFO.get('project_sub_type', None) == 1:
#             for i in plan.rSubPlanInList():
#                 ids1.extend([j.id for j in result.filter(plan=i)])
#     if INFO.get('plan2', None) and INFO.get('plan2', None) != '':
#         have2 = True
#         plan = Plan.objects.get(id=INFO.get('plan2', None))
#         ids2.extend([i.id for i in result.filter(plan=plan)])
#         if INFO.get('project_sub_type', None) == 1:
#             for i in plan.rSubPlanInList():
#                 ids2.extend([j.id for j in result.filter(plan=i)])
#     if INFO.get('plan3', None) and INFO.get('plan3', None) != '':
#         have3 = True
#         plan = Plan.objects.get(id=INFO.get('plan3', None))
#         ids3.extend([i.id for i in result.filter(plan=plan)])
#         if INFO.get('project_sub_type', None) == 1:
#             for i in plan.rSubPlanInList():
#                 ids3.extend([j.id for j in result.filter(plan=i)])
#     result = _searchAdvancedProject_FilterRule(result=result, INFO=INFO, field_name='plan', ids1=ids1, ids2=ids2, ids3=ids3, have1=have1, have2=have2, have3=have3, temp=[])

#     [ids1, ids2, ids3, have1, have2, have3, temp] = [[], [], [], False, False, False, []]
#     if INFO.get('unit1', None) and INFO.get('unit1', None) != '':
#         have1 = True
#         unit = Unit.objects.get(id=INFO.get('unit1', None))
#         ids1.extend([i.id for i in result.filter(unit=unit)])
#     if INFO.get('unit2', None) and INFO.get('unit2', None) != '':
#         have2 = True
#         unit = Unit.objects.get(id=INFO.get('unit2', None))
#         ids2.extend([i.id for i in result.filter(unit=unit)])
#     if INFO.get('unit3', None) and INFO.get('unit3', None) != '':
#         have3 = True
#         unit = Unit.objects.get(id=INFO.get('unit3', None))
#         ids3.extend([i.id for i in result.filter(unit=unit)])
#     result = _searchAdvancedProject_FilterRule(result=result, INFO=INFO, field_name='unit', ids1=ids1, ids2=ids2, ids3=ids3, have1=have1, have2=have2, have3=have3, temp=[])

# #    [ids1, ids2, ids3, have1, have2, have3, temp] = [[], [], [], False, False, False, []]
# #    if INFO.get('status1', None) and INFO.get('status1', None) != '':
# #        have1 = True
# #        status = Option.objects.get(id=INFO.get('status1', None))
# #        ids1.extend([i.id for i in result.filter(status=status)])
# #    if INFO.get('status2', None) and INFO.get('status2', None) != '':
# #        have2 = True
# #        status = Option.objects.get(id=INFO.get('status2', None))
# #        ids2.extend([i.id for i in result.filter(status=status)])
# #    if INFO.get('status3', None) and INFO.get('status3', None) != '':
# #        have3 = True
# #        status = Option.objects.get(id=INFO.get('status3', None))
# #        ids3.extend([i.id for i in result.filter(status=status)])
# #    result = _searchAdvancedProject_FilterRule(result=result, INFO=INFO, field_name='status', ids1=ids1, ids2=ids2, ids3=ids3, have1=have1, have2=have2, have3=have3, temp=[])


#     if INFO.get('year_lb', None) and INFO.get('year_lb', None) != '':
#         if INFO.get('year_ub', None) and INFO.get('year_ub', None) != '':
#             result = result.filter(year__gte=INFO.get('year_lb', None), year__lte=INFO.get('year_ub', None))
#         else:
#             result = result.filter(year__gte=INFO.get('year_lb', None))
#     else:
#         if INFO.get('year_ub', None) and INFO.get('year_ub', None) != '':
#             result = result.filter(year__lte=INFO.get('year_ub', None))

#     [ids1, ids2, ids3, have1, have2, have3, temp] = [[], [], [], False, False, False, []]
#     if INFO.get('place', None) and INFO.get('place', None) != '':
#         have1 = True
#         place = Place.objects.get(id=INFO.get('place', None))
#         ids1.extend([i.id for i in result.filter(place=place)])
#     if INFO.get('place2', None) and INFO.get('place2', None) != '':
#         have2 = True
#         place = Place.objects.get(id=INFO.get('place2', None))
#         ids2.extend([i.id for i in result.filter(place=place)])
#     if INFO.get('place3', None) and INFO.get('place3', None) != '':
#         have3 = True
#         place = Place.objects.get(id=INFO.get('place3', None))
#         ids3.extend([i.id for i in result.filter(place=place)])
#     result = _searchAdvancedProject_FilterRule(result=result, INFO=INFO, field_name='place', ids1=ids1, ids2=ids2, ids3=ids3, have1=have1, have2=have2, have3=have3, temp=[])


#     [ids1, ids2, ids3, have1, have2, have3, temp] = [[], [], [], False, False, False, []]
#     if INFO.get('port', None) and INFO.get('port', None) != '':
#         have1 = True
#         ids1 = [p.id for p in Project_Port.objects.filter(port__id = INFO.get('port', None))]
#     if INFO.get('port2', None) and INFO.get('port2', None) != '':
#         have2 = True
#         ids2 = [p.id for p in Project_Port.objects.filter(port__id = INFO.get('port2', None))]
#     if INFO.get('port3', None) and INFO.get('port3', None) != '':
#         have3 = True
#         ids3 = [p.id for p in Project_Port.objects.filter(port__id = INFO.get('port3', None))]
#     result = _searchAdvancedProject_FilterRule(result=result, INFO=INFO, field_name='port', ids1=ids1, ids2=ids2, ids3=ids3, have1=have1, have2=have2, have3=have3, temp=[])

#     if INFO.get('budget_type', None) and INFO.get('budget_type', None) != '':
#         result = result.filter(plan__budget_type__id=INFO.get('budget_type', None))

#     if INFO.get('budget_sub_type', None) and INFO.get('budget_sub_type', None) != '':
#         result = result.filter(budget_sub_type__id=INFO.get('budget_sub_type', None))

#     if INFO.get('undertake_type', None) and INFO.get('undertake_type', None) != '':
#         result = result.filter(undertake_type__id=INFO.get('undertake_type', None))

#     if INFO.get('progress', None) and INFO.get('progress', None) != '':
#         try:
#             value = float(INFO.get('progress_value', None))
#             temp = []
#             if INFO.get('progress', None) == 'g':
#                 for p in result:
#                     if p.getProgressPercent() > value:
#                         temp.append(p)
#             elif INFO.get('progress', None) == 'e':
#                 for p in result:
#                     if p.getProgressPercent() == value:
#                         temp.append(p)
#             elif INFO.get('progress', None) == 's':
#                 for p in result:
#                     if p.getProgressPercent() <= value:
#                         temp.append(p)
#             elif INFO.get('progress', None) == 'b':
#                 for p in result:
#                     if (p.getProgressPercent(datetime.date.today(), 'schedul') - p.getProgressPercent()) >= value:
#                         temp.append(p)
#             result = temp[:]
#         except: pass




#     if not INFO.get('page', None): page = 1
#     else: page = int(INFO['page'])
#     projects = []
#     result_num = len(result)
#     if INFO.get('budgetpage', ''):
#         for order, u in enumerate(result):
#             u.order = int((page-1)*NUMPERPAGE+order+1)
#             projects.append(u)
#     else:
#         for order, u in enumerate(result[int((page-1)*NUMPERPAGE):int(page*NUMPERPAGE)]):
#             u.order = int((page-1)*NUMPERPAGE+order+1)
#             projects.append(u)

#     return projects, result_num

# @checkAuthority
# def exportCustomReport(R, project, export_custom_report_id=0, export_type='html', right_type_value=u'觀看管考系統資料'):
#     try: ecr = ExportCustomReport.objects.get(id=export_custom_report_id)
#     except ExportCustomReport.DoesNotExist:
#         return HttpResponse(u'無資料')
#     projects, projects_num, p_list = _searchProject(R.GET, use_page=False)
#     fields = ecr.exportcustomreportfield_set.all().order_by('priority')
#     datas = []
#     for p in projects:
#         data = [p.bid_no, p.name]
#         for ecrf in fields:
#             data.append(ecrf.report_field.rValue(p))
#         datas.append(data)

#     if 'html' == export_type:
#         t = get_template(os.path.join('project', 'export_custom_report.html'))
#         html = t.render(RequestContext(R, {'export_custom_report': ecr,
#             'fields': fields, 'datas': datas,
#             'querystring': '&'.join(['%s=%s'%(k, v) for k, v in R.GET.items() if k != 'page'])
#             }))
#         return HttpResponse(html)
#     elif 'csv' == export_type:
#         t = get_template(os.path.join('project', 'export_custom_report.csv'))
#         csv = t.render(RequestContext(R, {'export_custom_report': ecr,
#             'fields': fields, 'datas': datas,
#             'querystring': '&'.join(['%s=%s'%(k, v) for k, v in R.GET.items() if k != 'page'])
#             }))
#         response = HttpResponse(content_type='application/xls')
#         response['Content-Type'] = ('application/xls')
#         response['Content-Disposition'] = ('attachment; filename=%s.xls'%ecr.name).encode('cp950')
#         response.write(csv)
#         return response

# @checkAuthority
# def convertHTMLToFile(R, project, right_type_value=u'觀看管考系統資料'):

#     DATA = R.POST
#     body = DATA.get('body', '')
#     name = DATA.get('name', 'test.xls')
#     html = """<html>
#                 <head>
#                     <meta http-equiv="content-type" content="text/html; charset=utf-8" />
#                     <title></title>
#                 </head>
#                 <body>%s</body></html>""" % body

#     response = HttpResponse(content_type='application/xls')
#     response['Content-Type'] = ('application/xls')
#     response['Content-Disposition'] = ('attachment; filename=%s'%name).encode('cp950')
#     response.write(html)
#     return response


# @checkAuthority
# def readDefaultDetail(R, project, right_type_value=u'觀看管考系統資料'):
#     user, DATA = R.user, readDATA(R)
#     default_projects = [p.project for p in DefaultProject.objects.filter(user=user)]
#     for i in default_projects:
#         i.short_plan_name = i.plan.name[:5] + '...'
#         try:
#             i.chase = list(CountyChaseProjectOneToMany.objects.filter(project=i))[-1]
#         except: pass
        


#     t = get_template(os.path.join('project', 'read_default_detail.html'))
#     html = t.render(RequestContext(R, {
#         'default_projects': default_projects,
#         }))
#     return HttpResponse(html)


# @checkAuthority
# def searchProject(R, project, right_type_value=u'觀看管考系統資料'):
#     class searchForm(forms.Form):
#         bid_no = forms.CharField(label='標案編號：　', required=False)
#         name = forms.CharField(label='工作名稱：　', required=False)
#         vouch_no = forms.CharField(label='發文(核定)文號：　', required=False)
#         vouch_date_ub = forms.CharField(label='發文(核定)日期：┌', required=False)
#         vouch_date_lb = forms.CharField(label='└', required=False)
#         plans = [('', '全部')]
#         for i in Plan.objects.filter(uplevel=None):
#             plans.append((i.id, '---'*i.rLevelNumber() + i.name))
#             for j in i.rSubPlanInList():
#                 plans.append((j.id, '---'*j.rLevelNumber() + j.name))
#         plan = forms.ChoiceField(choices=plans, required=False, label='所屬計畫：　')
#         project_sub_type = [('0', '不含下層計畫'), ('1', '含下層計畫')]
#         project_sub_type = forms.ChoiceField(choices=project_sub_type, required=False, label='層級：　')
# #        budget_types = [('', '全部')] + [(type.id, type.value) for type in Option.objects.filter(swarm='budget_type')]
# #        budget_type = forms.ChoiceField(choices=budget_types, required=False, label='預算別：', help_text='(公務預算／特別預算)')
#         purchase_types = [('', '全部')] + [(type.id, type.value) for type in Option.objects.filter(swarm='purchase_type')]
#         purchase_type = forms.ChoiceField(choices=purchase_types, required=False, label='採購類別：　', help_text='(工程／勞務)')
#         budget_sub_types = [('', '全部')] + [(type.id, type.value) for type in Option.objects.filter(swarm='budget_sub_type')]
#         budget_sub_type = forms.ChoiceField(choices=budget_sub_types, required=False, label='經費種類：　', help_text='(資本門／經常門)')
#         undertake_types = [('', '全部')] + [(type.id, type.value) for type in Option.objects.filter(swarm='undertake_type')]
#         undertake_type = forms.ChoiceField(choices=undertake_types, required=False, label='承辦方式：　', help_text='(自辦／委辦／補助)')
#         years = [(y-1911, y-1911) for y in xrange(2006, TODAY().year+2)]
#         years.insert(0, ('', '所有年度'))
#         years.reverse()
#         year = forms.ChoiceField(choices=years, required=False, label='年度：　')
#         places = [('', '全部')] + [(i.id, i.name) for i in Place.objects.filter(uplevel=TAIWAN).order_by('id')]
#         place = forms.ChoiceField(choices=places, required=False, label='縣市別：　')
#         units = [('', '全部')]
#         for i in Unit.fish_city_menu.all():
#             units.append((i.id, i.name))
#             if i.uplevel and i.uplevel.name != '縣市政府':
#                 units.extend(
#                     [(j.id, '---'+j.name) for j in i.uplevel_subunit.all()]
#                 )
#         unit = forms.ChoiceField(choices=units, required=False, label='執行機關：　')
# #        statuss = [('', '全部')]
# #        statuss += [[i.id, i.value] for i in _getProjectStatusInList()]
# #        status = forms.ChoiceField(choices=statuss, required=False, label='工程狀態：')
#         progress_state = [('', '全部'), ('g', '大於'), ('e', '等於'), ('s', '小於'), ('b', '落後')]
#         progress = forms.ChoiceField(choices=progress_state, required=False, label='進度搜尋：　')
#         progress_value = forms.CharField(label='', required=False)

# #TODO 暫時不開放「紀錄」
# #        record_project_profile_choices = [('', '')]
# #        record_project_profile_choices.extend([(rpp.id, rpp.name)
# #            for rpp in R.user.recordprojectprofile_set.all().order_by('id')])
# #        record_project_profiles = forms.ChoiceField(choices=record_project_profile_choices,
# #            required=False, label='紀錄名稱：')


#     user, DATA = R.user, readDATA(R)

#     default_projects = [p.project for p in DefaultProject.objects.filter(user=user)]
#     for i in default_projects:
#         i.short_plan_name = i.plan.name[:5] + '...'

#     form = searchForm()
#     projects_num = -1
#     projects = []
#     querystring = ''
#     INFO = {}
#     for k, v in R.GET.items(): INFO[k] = v
#     for k, v in R.POST.items(): INFO[k] = v
#     p_list = []
#     if INFO.get('submit', None):
#         form = searchForm(INFO)
#         querystring = '&'.join(['%s=%s'%(k, v) for k, v in INFO.items() if k != 'page'])
#         projects, projects_num, p_list = _searchProject(INFO)

#     for i in default_projects: i.default = i.isdefault(user)
#     for i in projects:
#         i.default = i.isdefault(user)

#     for n, i in enumerate(projects):
#         i.short_plan_name = i.plan.name[:5] + '...'

#     if _ca(user=user, project='', project_id=0, right_type_value=u'刪除管考工程案'):
#         delete = True
#     else:
#         delete = False

#     plans = [['', '全部']]
#     for i in Plan.objects.filter(uplevel=None):
#         plans.append([i.id, '---'*i.rLevelNumber() + i.name])
#         for j in i.rSubPlanInList():
#             plans.append([j.id, '---'*j.rLevelNumber() + j.name])

#     t = get_template(os.path.join('project', 'search.html'))
#     html = t.render(RequestContext(R, {
#         'form': form,
#         'plans': plans,
#         'default_projects': default_projects,
#         'projects': projects,
#         'sortBy': INFO.get('sortBy', None) or 'year',
#         'page_list': makePageList(INFO.get('page', 1), projects_num, NUMPERPAGE),
#         'querystring': querystring,
#         'projects_num': projects_num,
#         'option' : _make_choose(),
#         'delete': delete,
#         'p_list': p_list,
#         }))
#     R.querystring = querystring
#     return HttpResponse(html)

# def _searchProject(INFO, user='', use_page=True):
#     if INFO.get('sortBy', None):
#         result = Project.objects.filter(deleter=None).order_by(INFO.get('sortBy', None))
#     else:
#         result = Project.objects.filter(deleter=None)

#     if INFO.get('bid_no', None) and INFO.get('bid_no', None) != '':
#         ids = []
#         for bid_no in re.split('[ ,]+', INFO.get('bid_no', None)):
#             ids.extend([i.id for i in result.filter(bid_no__icontains=bid_no)])
#         result = result.filter(id__in=ids)

#     if INFO.get('vouch_no', None) and INFO.get('vouch_no', None) != '':
#         ids = []
#         chase_projects = CountyChaseProjectOneByOne.objects.all()
#         for vouch_no in re.split('[ ,]+', INFO.get('vouch_no', None)):
#             ids.extend([i.project_id for i in chase_projects.filter(ser_approved_plan_memo__icontains=vouch_no)])
#         for vouch_no in re.split('[ ,]+', INFO.get('vouch_no', None)):
#             ids.extend([i.project_id for i in chase_projects.filter(eng_plan_approved_plan_memo__icontains=vouch_no)])
#         result = result.filter(id__in=ids)

#     if INFO.get('vouch_date_ub', None) and INFO.get('vouch_date_ub', None) != '':
#         vouch_date_ub = INFO.get('vouch_date_ub', None).replace('/', '-').replace('.', '-')
#         vouch_date_lb = INFO.get('vouch_date_lb', None).replace('/', '-').replace('.', '-')
#         ids = []
#         chase_projects = CountyChaseProjectOneByOne.objects.all()
#         ids.extend([i.project_id for i in chase_projects.filter(act_ser_approved_plan__gte=vouch_date_ub, act_ser_approved_plan__lte=vouch_date_lb)])
#         ids.extend([i.project_id for i in chase_projects.filter(act_eng_plan_approved_plan__gte=vouch_date_ub, act_eng_plan_approved_plan__lte=vouch_date_lb)])
#         result = result.filter(id__in=ids)

#     if INFO.get('name', None) and INFO.get('name', None) != '':
#         ids = []
#         for name in re.split('[ ,]+', INFO.get('name', None)):
#             ids.extend([i.id for i in result.filter(name__icontains=name)])
#         result = result.filter(id__in=ids)

#     if INFO.get('plan', None) and INFO.get('plan', None) != '':
#         plan = Plan.objects.get(id=INFO.get('plan', None))
#         if INFO.get('project_sub_type', None) == '1':
#             plan_ids = [plan.id] + [i.id for i in Plan.objects.get(id=INFO.get('plan', None)).rSubPlanInList()]
#             result = result.filter(plan__id__in=plan_ids)
#         else:
#             result = result.filter(plan = plan)

# #    if INFO.get('budget_type', None) and INFO.get('budget_type', None) != '':
# #        result = result.filter(plan__budget_type=Option.objects.get(id=INFO.get('budget_type', None)))
#     if INFO.get('purchase_type', None) and INFO.get('purchase_type', None) != '':
#         result = result.filter(purchase_type=Option.objects.get(id=INFO.get('purchase_type', None)))

#     if INFO.get('budget_sub_type', None) and INFO.get('budget_sub_type', None) != '':
#         result = result.filter(budget_sub_type=Option.objects.get(id=INFO.get('budget_sub_type', None)))

#     if INFO.get('undertake_type', None) and INFO.get('undertake_type', None) != '':
#         result = result.filter(undertake_type=Option.objects.get(id=INFO.get('undertake_type', None)))

#     if INFO.get('year', None) and INFO.get('year', None) != '':
#         result = result.filter(year=INFO.get('year', None))

#     if INFO.get('unit', None) and INFO.get('unit', None) != '':
#         unit = Unit.objects.get(id=INFO.get('unit', None))
#         result = result.filter(unit=unit)

#     if INFO.get('place', None) and INFO.get('place', None) != '':
#         place = Place.objects.get(id=INFO.get('place', None))
#         result = result.filter(place=place)
# #    if INFO.get('status', None) and INFO.get('status', None) != '':
# #        status = Option.objects.get(id=INFO.get('status', None))
# #        result = result.filter(status=status)

#     if INFO.get('progress', None) and INFO.get('progress', None) != '':
#         try:
#             value = float(INFO.get('progress_value', None))
#             value_state = True
#         except:
#             value_state = False
#         if value_state:
#             temp = []
#             for p in result:
#                 if p.rNowProgress():
#                     if INFO.get('progress', None) == 'g':
#                         if float(str(p.rNowProgress().actual_progress_percent or 0)) > value:
#                             temp.append(p)
#                     elif INFO.get('progress', None) == 'e':
#                         if float(str(p.rNowProgress().actual_progress_percent or 0)) == value:
#                             temp.append(p)
#                     elif INFO.get('progress', None) == 's':
#                         if float(str(p.rNowProgress().actual_progress_percent or 0)) < value:
#                             temp.append(p)
#                     elif INFO.get('progress', None) == 'b':
#                         if (float(str(p.rNowProgress().schedul_progress_percent or 0)) - float(str(p.rNowProgress().actual_progress_percent or 0))) >= value:
#                             temp.append(p)
#             result = temp[:]

#     if INFO.get('record_project_profiles', None):
#         record_project_profile_id = INFO.get('record_project_profiles')
#         try:
#             rpp = RecordProjectProfile.objects.get(id=record_project_profile_id)
#         except RecordProjectProfile.DoesNotExist:
#             pass
#         else:
#             result = result.filter(id__in=[p.id for p in rpp.projects.all()])

#     p_list = [int(i.id) for i in result]

#     result_num = len(result)
#     if not use_page:
#         projects = result[:]
#     else:
#         if not INFO.get('page', None): page = 1
#         else: page = int(INFO['page'])

#         projects = []
#         for order, u in enumerate(result[int((page-1)*NUMPERPAGE):int(page*NUMPERPAGE)]):
#             u.order = int((page-1)*NUMPERPAGE+order+1)
#             projects.append(u)

#     return projects, result_num, p_list

# @checkAuthority
# def makeStatistics(R, project, right_type_value=u'觀看管考系統資料', **kw):
#     user, DATA = R.user, readDATA(R)
#     years = ['所有'] + [str(y-1911) for y in xrange(2006, TODAY().year+2)]
#     years.reverse()
#     INFO = {}
#     for x in kw['dictionary_str'].split('/'):
#         k, v = x.split(':')
#         INFO[k] = v

#     if INFO['select_year'] == '0': select_year='所有'
#     else: select_year = INFO['select_year']

#     if select_year == '所有': projects = Project.objects.all()
#     else: projects = Project.objects.filter(year=select_year)

#     fishingports = []
#     if INFO['select_unit'] != '0':
#         unit = Unit.objects.get(id=INFO['select_unit'])
#         projects = projects.filter(unit=unit)
#         fishingports = [[i.id, i.name] for i in FishingPort.objects.filter(place__name__contains=unit.name[0:2])]

#     if INFO['select_undertake_type'] != '0': projects = projects.filter(undertake_type__id=INFO['select_undertake_type'])

#     if INFO['select_fishingport'] != '0':
#         fp_projects = [p.project for p in Project_Port.objects.filter(port__id = INFO['select_fishingport'])]
#         temp = []
#         for i in projects:
#             if i in fp_projects:
#                 temp.append(i)
#         projects = temp

#     if INFO['type_id'] == '1': type = u'各執行機關執行率'
#     elif INFO['type_id'] == '2': type = u'各執行機關所屬工程件數金額'
#     elif INFO['type_id'] == '3': type = u'各執行機關開工月份分佈表'
#     elif INFO['type_id'] == '4': type = u'各執行機關工程金額分佈表'

#     units = []
#     for i in Unit.fish_city_menu.all():
#         units.append([i.id, i.name])
#         if i.uplevel and i.uplevel.name != '縣市政府':
#             units.extend([[j.id, '-----'+j.name] for j in i.uplevel_subunit.all()])

#     plans = []
#     for p in Plan.objects.filter(uplevel=None):
#         p.front = 20 * p.rLevelNumber()
#         plans.append(p)
#         for sp in p.rSubPlanInList():
#             sp.front = 30 * sp.rLevelNumber()
#             plans.append(sp)

#     if u'各執行機關執行率' == type:

#         projects = list(projects)
#         for p in projects:
#             if select_year == '所有':
#                 p.budget = sum([(f.self_budget + f.local_budget) for f in Fund.objects.filter(project=p)])
#                 p.payout = sum([(f.sum_self_payout + f.sum_local_payout) for f in Fund.objects.filter(project=p)])
#             else:
#                 p.budget = sum([(f.self_budget + f.local_budget) for f in Fund.objects.filter(project=p, year=select_year)])
#                 p.payout = sum([(f.sum_self_payout + f.sum_local_payout) for f in Fund.objects.filter(project=p, year=select_year)])



#         for plan in plans:
#             plan.rate_num_list = [[0,0] for i in xrange(11)]
#             plan.num = 0
#             plan.budget = 0
#             plan.payout = 0
#             for i in projects:
#                 if i.plan == plan:
#                     plan.num += 1
#                     plan.budget += i.budget
#                     plan.payout += i.payout
#                     plan.rate_num_list[int(i.rTrueRate()/10.)][0] += 1
#                     plan.rate_num_list[int(i.rTrueRate()/10.)][1] += 1
#             plan.total_num = plan.num
#             plan.total_budget = plan.budget
#             plan.total_payout = plan.payout
#             for subplan in plan.rSubPlanInList():
#                 for i in projects:
#                     if i.plan == subplan:
#                         plan.total_num += 1
#                         plan.total_budget += i.budget
#                         plan.total_payout += i.payout
#                         plan.rate_num_list[int(i.rTrueRate()/10.)][1] += 1
#             if plan.budget == 0: plan.rate = '0.0'
#             else: plan.rate = round((plan.payout*100/plan.budget), 3)
#             if plan.total_budget == 0: plan.total_rate = '0.0'
#             else: plan.total_rate = round((plan.total_payout*100/plan.total_budget), 3)
#             plan.budget = plan.budget/1000
#             plan.total_budget = plan.total_budget/1000
#             plan.payout = plan.payout/1000
#             plan.total_payout = plan.total_payout/1000

#         names, values = [], []
#         for plan in plans:
#             names.append(unicode(plan.name))
#             values.append(plan.num)
#         chart_cache_name = '%s_table_01' % R.session.session_key
#         cache.set(chart_cache_name, {'title': u'計畫-數量圖', 'names': names, 'values': values}, 3600) #會快取 3600 秒

#         template = 'table_01.html'
#         request = {'plans' : plans, 'select_unit': int(INFO['select_unit']), 'chart_cache_name': chart_cache_name}

#     elif u'各執行機關所屬工程件數金額' == type:
#         statuss = [stat for stat in Option.objects.filter(swarm='project_status').order_by('id')]

#         for plan in plans:
#             plan.status_num_list = []
#             for n, stat in enumerate(statuss):
#                 plan.status_num_list.append([stat.id, len(projects.filter(plan=plan, status=stat)), len(projects.filter(plan=plan, status=stat))])
#             plan.num = len(projects.filter(plan=plan))
#             plan.money = sum([p.rTotalMoney() for p in projects.filter(plan=plan)])
#             plan.total_num = plan.num
#             plan.total_money = plan.money
#             for subplan in plan.rSubPlanInList():
#                 for n, stat in enumerate(statuss):
#                     plan.status_num_list[n][2] += len(projects.filter(plan=subplan, status=stat))
#                 plan.total_num += len(projects.filter(plan=subplan))
#                 plan.total_money += sum([p.rTotalMoney() for p in projects.filter(plan=subplan)])
#             plan.money = plan.money/1000
#             plan.total_money = plan.total_money/1000

#         names, values = [], []
#         for plan in plans:
#             names.append(unicode(plan.name))
#             values.append(plan.num)
#         chart_cache_name = '%s_table_02' % R.session.session_key
#         cache.set(chart_cache_name, {'title': u'計畫-數量圖', 'names': names, 'values': values}, 3600) #會快取 3600 秒

#         template = 'table_02.html'
#         request = {'plans' : plans, 'statuss': statuss, 'select_unit': int(INFO['select_unit']), 'chart_cache_name': chart_cache_name}

#     elif u'各執行機關開工月份分佈表' == type:
#         for plan in plans:
#             plan.start_month = [[0, 0] for i in xrange(13)]
#             little_projects = projects.filter(plan=plan)
#             plan.num = len(little_projects)
#             plan.start_month[0][0] = plan.start_month[0][1] = len(little_projects.filter(start_date=None))
#             for p in little_projects.exclude(start_date=None):
#                 plan.start_month[int(p.start_date.month)][0] += 1
#                 plan.start_month[int(p.start_date.month)][1] += 1
#             plan.total_num = plan.num
#             for subplan in plan.rSubPlanInList():
#                 little_projects = projects.filter(plan=subplan)
#                 plan.start_month[0][1] += len(little_projects.filter(start_date=None))
#                 plan.total_num += len(little_projects)
#                 for p in little_projects.exclude(start_date=None):
#                     plan.start_month[int(p.start_date.month)][1] += 1

#         names, values = [], []
#         for plan in plans:
#             names.append(unicode(plan.name))
#             values.append(plan.num)
#         chart_cache_name = '%s_table_03' % R.session.session_key
#         cache.set(chart_cache_name, {'title': u'計畫-數量圖', 'names': names, 'values': values}, 3600) #會快取 3600 秒

#         template = 'table_03.html'
#         request = {'plans' : plans, 'select_unit': int(INFO['select_unit']), 'chart_cache_name': chart_cache_name}

#     elif u'各執行機關工程金額分佈表' == type:
#         money_range = [0, 1000000, 2000000, 3000000, 4000000, 5000000, 7500000, 10000000, 20000000]
#         money_range_str = []
#         for n in xrange(len(money_range)-1):
#             money_range_str.append([str(money_range[n]/10000) + '萬',str(money_range[n+1]/10000-1) + '萬'])
#         money_range_str.append([str(money_range[-1]/10000) + '萬','以上'])

#         for plan in plans:
#             plan.money_range = []
#             for n in xrange(len(money_range)-1):
#                 plan.money_range.append([0,0,money_range[n],money_range[n+1]])
#             plan.money_range.append([0,0,money_range[-1],9999999999999999])
#             [[0, 0] for i in xrange(len(money_range))]
#             little_projects = projects.filter(plan=plan)
#             plan.num = len(little_projects)
#             for n in xrange(len(money_range)-1):
#                 plan.money_range[n][0] = plan.money_range[n][1] = \
#                 len(little_projects.extra(
#                                         where=['(design_bid+construction_bid+pollution+manage+other_defray)>=%s',
#                                         '(design_bid+construction_bid+pollution+manage+other_defray)<%s'],
#                                         params=[str(money_range[n]), str(money_range[n+1])])
#                                         )
#             plan.money_range[-1][0] = plan.money_range[-1][1] = \
#             len(little_projects.extra(
#                                     where=['(design_bid+construction_bid+pollution+manage+other_defray)>=%s'],
#                                     params=[str(money_range[-1])])
#                                     )
#             plan.total_num = plan.num
#             for subplan in plan.rSubPlanInList():
#                 little_projects = projects.filter(plan=subplan)
#                 plan.total_num += len(little_projects)
#                 for n in xrange(len(money_range)-1):
#                     plan.money_range[n][1] += \
#                     len(little_projects.extra(
#                                             where=['(design_bid+construction_bid+pollution+manage+other_defray)>=%s',
#                                             '(design_bid+construction_bid+pollution+manage+other_defray)<%s'],
#                                             params=[str(money_range[n]), str(money_range[n+1])])
#                                             )
#                 plan.money_range[-1][1] += \
#                 len(little_projects.extra(
#                                         where=['(design_bid+construction_bid+pollution+manage+other_defray)>=%s'],
#                                         params=[str(money_range[-1])])
#                                         )

#         names, values = [], []
#         for plan in plans:
#             names.append(unicode(plan.name))
#             values.append(plan.num)
#         chart_cache_name = '%s_table_04' % R.session.session_key
#         cache.set(chart_cache_name, {'title': u'計畫-數量圖', 'names': names, 'values': values}, 3600) #會快取 3600 秒

#         template = 'table_04.html'
#         request = {'plans' : plans, 'select_unit': int(INFO['select_unit']), 'money_range_str': money_range_str, 'chart_cache_name': chart_cache_name}

#     request['years'] = years
#     request['type'] = type
#     request['type_id'] = INFO['type_id']
#     request['select_year'] = select_year
#     request['units'] = units
#     request['undertake_types'] = [[i.id, i.value] for i in Option.objects.filter(swarm='undertake_type')]
#     request['select_undertake_type'] = int(INFO['select_undertake_type'])
#     request['fishingports'] = fishingports
#     request['select_fishingport'] = int(INFO['select_fishingport'])


#     t = get_template(os.path.join('project', template))
#     html = t.render(RequestContext(R, request))
#     return HttpResponse(html)

# @login_required
# @checkAuthority
# def makeStatisticsProjects(R, project, right_type_value=u'觀看管考系統資料'):
#     user, DATA = R.user, readDATA(R)
#     projects = Project.objects.all()

#     if DATA.get('unit_id','') and DATA.get('unit_id','') != '0':
#         unit = Unit.objects.get(id=DATA.get('unit_id',''))
#         projects = projects.filter(unit=unit)

#     if DATA.get('select_year','') and DATA.get('select_year','') != '所有':
#         projects = projects.filter(year=DATA.get('select_year',''))

#     if DATA.get('status_id',''):
#         status = Option.objects.get(id=DATA.get('status_id',''))
#         projects = projects.filter(status=status)

#     if DATA.get('from_money','') and DATA.get('to_money',''):
#         projects = projects.extra(
#                                 where=['(design_bid+construction_bid+pollution+manage+other_defray)>=%s',
#                                 '(design_bid+construction_bid+pollution+manage+other_defray)<%s'],
#                                 params=[DATA.get('from_money',''), DATA.get('to_money','')]
#                                 )

#     if DATA.get('start_month',''):
#         if DATA.get('start_month','') == '1':
#             projects = projects.filter(start_date=None)
#         else:
#             projects = projects.filter(start_date__month=int(DATA.get('start_month',''))-1)

#     if DATA.get('select_undertake_type','') and DATA.get('select_undertake_type','') != '0':
#         projects = projects.filter(undertake_type__id=DATA.get('select_undertake_type',''))

#     result = []
#     if DATA.get('plan_id',''):
#         plan = Plan.objects.get(id=DATA.get('plan_id',''))
#         result += projects.filter(plan=plan)
#         if DATA.get('include_sub','') == 'True':
#             for sp in plan.rSubPlanInList():
#                 result += projects.filter(plan=sp)
#     else:
#         result = projects

#     projects = result
#     result = []
#     if DATA.get('true_rate',''):
#         rate = int(DATA.get('true_rate','')) - 1
#         for p in projects:
#             if int(p.rTrueRate()/10.) == rate:
#                 result.append(p)
#     else:
#         result = projects

#     if DATA.get('select_fishingport','') and DATA.get('select_fishingport','') != '0':
#         fp_projects = [p.project for p in Project_Port.objects.filter(port__id = DATA.get('select_fishingport',''))]
#         temp = []
#         for i in projects:
#             if i in fp_projects:
#                 temp.append(i)
#         projects = temp

#     projects = []
#     for i in result:
#         p = {
#             'id': i.id,
#             'year': i.year,
#             'bid_no': i.bid_no,
#             'name': i.name,
#             'place': i.place.name,
#             'unit': i.unit.name,
#             'status': i.status.value,
#             'plan': i.plan.name,
#             }
#         projects.append(p)

#     return HttpResponse(json.write({'projects': projects }))


# @login_required
# @checkAuthority
# def ReadAndEditPlan(R, project, right_type_value=u'觀看管考系統資料', **kw):
#     user, DATA = R.user, readDATA(R)
#     if _ca(user=user, project='', project_id=0, right_type_value=u'填寫管考系統資料'):
#         edit = True
#     else:
#         edit = False

#     top_paln = Plan.objects.get(uplevel=None)
#     plans = [top_paln] + top_paln.rSubPlanInList()
#     for i in plans:
# #        i.front = [[] for q in xrange(i.rLevelNumber())]
#         i.front = (i.rLevelNumber()-1) * 20
#         i.width = 250 - i.front

#     years = [y-1911 for y in xrange(2006, TODAY().year+6)]
#     years.reverse()

#     target_plan = Plan.objects.get(id=kw['plan_id'])
#     target_plan.path = [target_plan]
#     while target_plan.path[-1].uplevel: target_plan.path.append(target_plan.path[-1].uplevel)
#     target_plan.path.pop(0)
#     target_plan.path.reverse()
    
#     if target_plan.auto_sum: target_plan.updatePlanBudgetInfo()
#     budgets = PlanBudget.objects.filter(plan=target_plan).order_by('year')
#     budget_projects = Budget.objects.filter(fund__project__plan=target_plan, fund__project__deleter=None).order_by('fund__project__place', 'fund__project__id')
#     for b in budgets:
#         if b.plan.auto_sum:
#             b.capital_self = b.rAuto_Sum('capital_self')
#             b.capital_trust = b.rAuto_Sum('capital_trust')
#             b.capital_grant = b.rAuto_Sum('capital_grant')
#             b.regular_self = b.rAuto_Sum('regular_self')
#             b.regular_trust = b.rAuto_Sum('regular_trust')
#             b.regular_grant = b.rAuto_Sum('regular_grant')
# #            b.public_self = b.rAuto_Sum('public_self')
# #            b.public_trust = b.rAuto_Sum('public_trust')
# #            b.public_grant = b.rAuto_Sum('public_grant')

#         b.real_capital_self = int(sum([money.capital_ratify_revision or money.capital_ratify_budget or 0 for money in budget_projects.filter(year=b.year, fund__project__budget_sub_type__value=r'資本門', fund__project__undertake_type__value=r'自辦')]))
#         b.real_capital_trust = int(sum([money.capital_ratify_revision or money.capital_ratify_budget or 0 for money in budget_projects.filter(year=b.year, fund__project__budget_sub_type__value=r'資本門', fund__project__undertake_type__value=r'委辦')]))
#         b.real_capital_grant = int(sum([money.capital_ratify_revision or money.capital_ratify_budget or 0 for money in budget_projects.filter(year=b.year, fund__project__budget_sub_type__value=r'資本門', fund__project__undertake_type__value=r'補助')]))
#         b.real_regular_self = int(sum([money.capital_ratify_revision or money.capital_ratify_budget or 0 for money in budget_projects.filter(year=b.year, fund__project__budget_sub_type__value=r'經常門', fund__project__undertake_type__value=r'自辦')]))
#         b.real_regular_trust = int(sum([money.capital_ratify_revision or money.capital_ratify_budget or 0 for money in budget_projects.filter(year=b.year, fund__project__budget_sub_type__value=r'經常門', fund__project__undertake_type__value=r'委辦')]))
#         b.real_regular_grant = int(sum([money.capital_ratify_revision or money.capital_ratify_budget or 0 for money in budget_projects.filter(year=b.year, fund__project__budget_sub_type__value=r'經常門', fund__project__undertake_type__value=r'補助')]))
# #        b.real_public_self = int(sum([money.capital_ratify_revision or 0 for money in budget_projects.filter(fund__project__budget_type__value=r'公務預算', fund__project__budget_sub_type__value=r'經常門', fund__project__undertake_type__value=r'自辦')]))
# #        b.real_public_trust = int(sum([money.capital_ratify_revision or 0 for money in budget_projects.filter(fund__project__budget_type__value=r'公務預算', fund__project__budget_sub_type__value=r'經常門', fund__project__undertake_type__value=r'委辦')]))
# #        b.real_public_grant = int(sum([money.capital_ratify_revision or 0 for money in budget_projects.filter(fund__project__budget_type__value=r'公務預算', fund__project__budget_sub_type__value=r'經常門', fund__project__undertake_type__value=r'補助')]))
#         b.minus_capital_self = float(str(b.capital_self or 0)) - b.real_capital_self
#         b.minus_capital_trust = float(str(b.capital_trust or 0)) - b.real_capital_trust
#         b.minus_capital_grant = float(str(b.capital_grant or 0)) - b.real_capital_grant
#         b.minus_regular_self = float(str(b.regular_self or 0)) - b.real_regular_self
#         b.minus_regular_trust = float(str(b.regular_trust or 0)) - b.real_regular_trust
#         b.minus_regular_grant = float(str(b.regular_grant or 0)) - b.real_regular_grant
# #        b.minus_public_self = float(str(b.public_self or 0)) - b.real_public_self
# #        b.minus_public_trust = float(str(b.public_trust or 0)) - b.real_public_trust
# #        b.minus_public_grant = float(str(b.public_grant or 0)) - b.real_public_grant

#     t = get_template(os.path.join('project', 'readandeditplan.html'))
#     html = t.render(RequestContext(R,{
#         'years': years,
#         'plans': plans,
#         'target_plan': target_plan,
#         'edit': edit,
#         'budgets': budgets,
#         'budget_projects': budget_projects,
#         'budget_types': Option.objects.filter(swarm='budget_type'),
#         'budget_sub_types': Option.objects.filter(swarm='budget_sub_type'),
#         'undertake_types': Option.objects.filter(swarm='undertake_type'),
#         }))
#     return HttpResponse(html)

# @checkAuthority
# def ReadAndEditPlanBudget(R, project, right_type_value=u'觀看管考系統資料', **kw):
#     user, DATA = R.user, readDATA(R)
#     if _ca(user=user, project='', project_id=0, right_type_value=u'填寫管考系統資料'):
#         edit = True
#     else:
#         edit = False

#     years = [y-1911 for y in xrange(2006, TODAY().year+2)]
#     years.reverse()
#     top_paln = Plan.objects.get(uplevel=None)
#     plans = [top_paln] + top_paln.rSubPlanInList()
#     for p in plans:
#         p.budgets = []
#     budgets = list(PlanBudget.objects.all().order_by('-year'))
#     budget_list = []
#     for i in budgets:
#         if i.year == None:
#             budget_list.append(i)
#         else:
#             budget_list.insert(0,i)
#     for b in budget_list:
#         for p in plans:
#             if b.plan == p:
#                 p.budgets.append(b)
#     for i in plans:
#         i.front = [[] for q in xrange(i.rLevelNumber())]
#     layer = kw['layer']
#     t = get_template(os.path.join('project', 'readandeditplanbudget.html'))
#     html = t.render(RequestContext(R,{
#         'plans':plans,
#         'edit':edit,
#         'years':years,
#         'layer':layer,
#         }))
#     return HttpResponse(html)

# @login_required
# @checkAuthority
# def ReadAndEditCountyChase(R, project, right_type_value=u'使用縣市追蹤系統', **kw):
#     user, DATA = R.user, readDATA(R)
#     if _ca(user=user, project='', project_id=0, right_type_value=u'使用縣市追蹤系統'):
#         edit = True
#     else:
#         edit = False

#     class searchForm(forms.Form):
#         bid_no = forms.CharField(label='標案編號：', required=False)
#         name = forms.CharField(label='工作名稱：', required=False)
#         close_checks = [('', '全部'), ('False', '尚未確認結案'), ('True', '已確認結案')]
#         close_check = forms.ChoiceField(choices=close_checks, required=False, label='是否結案：')
#         plans = [('', '全部')]
#         for i in Plan.objects.filter(uplevel=None):
#             plans.append((i.id, '---'*i.rLevelNumber() + i.name))
#             for j in i.rSubPlanInList():
#                 plans.append((j.id, '---'*j.rLevelNumber() + j.name))
#         plan = forms.ChoiceField(choices=plans, required=False, label='所屬計畫：')
#         project_sub_type = [('0', '不含下層計畫'), ('1', '含下層計畫')]
#         project_sub_type = forms.ChoiceField(choices=project_sub_type, required=False, label='層級：')
#         purchase_types = [('', '全部')] + [(type.id, type.value) for type in Option.objects.filter(swarm='purchase_type')]
#         purchase_type = forms.ChoiceField(choices=purchase_types, required=False, label='採購類別：', help_text='(工程／勞務)')
#         budget_sub_types = [('', '全部')] + [(type.id, type.value) for type in Option.objects.filter(swarm='budget_sub_type')]
#         budget_sub_type = forms.ChoiceField(choices=budget_sub_types, required=False, label='經費種類：', help_text='(資本門／經常門)')
#         undertake_types = [('', '全部')] + [(type.id, type.value) for type in Option.objects.filter(swarm='undertake_type')]
#         undertake_type = forms.ChoiceField(choices=undertake_types, required=False, label='承辦方式：', help_text='(自辦／委辦／補助)')
#         years = [(y-1911, y-1911) for y in xrange(2006, TODAY().year+2)]
#         years.insert(0, ('', '所有年度'))
#         years.reverse()
#         year = forms.ChoiceField(choices=years, required=False, label='年度：')
#         places = [('', '全部')] + [(i.id, i.name) for i in Place.objects.filter(uplevel=TAIWAN).order_by('id')]
#         place = forms.ChoiceField(choices=places, required=False, label='縣市別')
#         units = [('', '全部')]
#         for i in Unit.fish_city_menu.all():
#             units.append((i.id, i.name))
#             if i.uplevel and i.uplevel.name != '縣市政府':
#                 units.extend(
#                     [(j.id, '---'+j.name) for j in i.uplevel_subunit.all()]
#                 )
#         unit = forms.ChoiceField(choices=units, required=False, label='執行機關：')

#     places = Place.objects.filter(uplevel=TAIWAN).order_by('id')
#     plans = [['', '全部']]
#     for i in Plan.objects.filter(uplevel=None):
#         plans.append([i.id, '---'*i.rLevelNumber() + i.name])
#         for j in i.rSubPlanInList():
#             plans.append([j.id, '---'*j.rLevelNumber() + j.name])

#     for i in CountyChaseProjectOneToMany.objects.all().exclude(project__deleter=None):
#         i.delete()

#     form = searchForm()
#     projects_num = -1
#     projects = []
#     querystring = ''
#     INFO = {}
#     for k, v in R.GET.items(): INFO[k] = v
#     for k, v in R.POST.items(): INFO[k] = v
#     p_list = []
#     if INFO.get('submit', None):
#         form = searchForm(INFO)
#         querystring = '&'.join(['%s=%s'%(k, v) for k, v in INFO.items() if k != 'page'])
#         projects, projects_num, p_list = _searchChaseProject(INFO, use_page=False)
#         for p in projects:
#             if FRCMUserGroup.objects.filter(project=p).count() > 0: p.frcm = True
#             else: p.frcm = False

#     countychasetime = list(CountyChaseTime.objects.all().order_by('id'))[-1]
#     countychasetime.time = CountyChaseTime.objects.all().count()
#     countychasetime.pastDay = (datetime.date.today() - countychasetime.chase_date).days
#     countychasetime.num = CountyChaseProjectOneToMany.objects.filter(countychasetime=countychasetime).count()

#     for n, p in enumerate(projects):
#         p.isChaseOBO = CountyChaseProjectOneByOne.objects.get(project=p)
#         try:
#             p.isChase = CountyChaseProjectOneToMany.objects.get(countychasetime=countychasetime, project=p)
#         except: p.isChase = False
    
#     places = sort_By_South(places, countychasetime)

#     t = get_template(os.path.join('project', 'readandeditcountychase.html'))
#     html = t.render(RequestContext(R,{
#         'edit': edit,
#         'places': places,
#         'form': form,
#         'plans': plans,
#         'projects': projects,
#         'projects_num': projects_num,
#         'option' : _make_choose(),
#         'p_list': p_list,
#         'countychasetime': countychasetime,

#         }))
#     R.querystring = querystring
#     return HttpResponse(html)


# def _makeDownloadFile_CountyChase(user='', projects='', countychasetime='', new='True'):
#     heads = [
#             '項次', '最後更新日期', '年度', '縣市別', '漁港別養殖區別', '工程名稱', '辦理別1.自2.委3.補', '預定進度%',
#             '實際進度%(N)', '計畫經費', '預算數核定數', '預算數修正核定數', '預算數本署負擔（保留）數(A)','預算數地方核定數', '預算數地方修正核定數',
#             '預算數地方配合款(B)', '預算數歷年( C )', '本署負擔總經費(E)', '發包及其他費用合計(D)未發包以核定數代替', '漁業署撥款情形',
#             '累計分配數（R）', '實支數本署(I)', '實支數縣府(J)', '應付未付數本署(L)', '應付未付數縣府(M)', '賸餘款本署(F)',
#             '本署經費執行數（H）＝(I+L+F)', '執行率(P)＝（H）/（R+F）', '達成率(Q)＝（H）/（A）', '計畫執行情形說明(若有執行落後者，請詳細說明預定完成日期及因應措施',
#             '預計至年底執行率', '執行單位', '執行單位聯絡窗口', '縣市政府聯絡方式(mail及電話)',
#             '勞務_核定計畫', '勞務_簽辦招標', '勞務_公告招標', '勞務_公開評選會議(限制性招標)', '勞務_定約', '勞務_基本設計',
#             '勞務_細部設計', '勞務_驗收結案', '勞務_簽辦招標', '設計規劃_核定計畫', '設計規劃_簽辦招標', '設計規劃_公告招標', '設計規劃_公開評選會議(限制性招標)',
#             '設計規劃_定約', '設計規劃_基本設計', '設計規劃_細部設計', '設計規劃_驗收結案', '工程施做_簽辦招標', '工程施做_公告招標',
#             '工程施做_定約', '工程施做_開工', '工程施做_完工', '工程施做_驗收', '工程施做_結案',
#             ]

#     data = {'replace': {}, 'table_eng': [], 'table_ser': []}
#     for n, p in enumerate(projects):
#         tmp = {}

#         p.fund = p.fund_set.get()
#         p.budget = list(p.fund.budget_set.all().order_by('year'))[-1]
#         p.chase_obo = p.countychaseprojectonebyone_set.get()
#         p.chase_otm = p.countychaseprojectonetomany_set.get(countychasetime=countychasetime)
#         if p.chase_otm.update_time: tmp['最後更新日期'] = p.chase_otm.update_time
#         else: tmp['最後更新日期'] = ''
#         tmp['項次'] = n + 1
#         tmp['年度'] = p.year
#         tmp['縣市別'] = p.place.name
#         port_str = ''
#         for i in p.rSubLocation():
#             port_str += i.name + ' '
#         tmp['漁港別養殖區別'] = port_str
#         tmp['工程名稱'] = p.name
#         if p.undertake_type.value == '自辦': tmp['辦理別1.自2.委3.補'] = 1
#         elif p.undertake_type.value == '委辦': tmp['辦理別1.自2.委3.補'] = 2
#         elif p.undertake_type.value == '補助': tmp['辦理別1.自2.委3.補'] = 3
#         tmp['預定進度%'] = float(str(p.chase_otm.schedul_progress_percent or 0)) / 100.
#         tmp['實際進度%(N)'] = float(str(p.chase_otm.actual_progress_percent or 0)) / 100.
#         tmp['預算數核定數'] = p.budget.capital_ratify_budget
#         tmp['預算數修正核定數'] = p.budget.capital_ratify_revision
#         tmp['預算數地方核定數'] = p.budget.capital_ratify_local_budget
#         tmp['預算數地方修正核定數'] = p.budget.capital_ratify_local_revision
#         tmp['計畫經費'] = p.budget.rPlanMoney()
#         tmp['預算數本署負擔（保留）數(A)'] = p.fund.rSelfLoad()
#         tmp['預算數地方配合款(B)'] = p.fund.rlocalMatchFund()
#         tmp['預算數歷年( C )'] = float(str(p.budget.over_the_year or 0))
#         tmp['本署負擔總經費(E)'] = tmp['預算數本署負擔（保留）數(A)'] + tmp['預算數歷年( C )']
#         if p.rTotalMoneyInProject() != 0:#1.採用工程結算金額 #2.採用工程契約金額
#             tmp['發包及其他費用合計(D)未發包以核定數代替'] = p.rTotalMoneyInProject()
#         elif p.budget.capital_ratify_revision != 0:#3.採用修正核定數
#             tmp['發包及其他費用合計(D)未發包以核定數代替'] = p.budget.capital_ratify_revision
#         else:#4.採用核定數
#             tmp['發包及其他費用合計(D)未發包以核定數代替'] = p.budget.capital_ratify_budget or 0
#         tmp['漁業署撥款情形'] = p.rTotalAppropriate()
#         tmp['累計分配數（R）'] = p.chase_otm.getFund().rAllocationToNow()
#         tmp['實支數本署(I)'] = p.chase_otm.self_payout
#         tmp['實支數縣府(J)'] = p.chase_otm.local_payout
#         tmp['應付未付數本署(L)'] = p.chase_otm.self_unpay
#         tmp['應付未付數縣府(M)'] = p.chase_otm.local_unpay
#         tmp['賸餘款本署(F)'] = p.chase_otm.rSelf_Surplus()
# #        tmp['賸餘款縣府(G)'] = p.chase_otm.rLocal_Surplus()
#         tmp['本署經費執行數（H）＝(I+L+F)'] = p.chase_otm.getSelfExecutionMoney()
#         tmp['執行率(P)＝（H）/（R+F）'] = p.chase_otm.getExecutionRate() / 100.
#         tmp['達成率(Q)＝（H）/（A）'] = p.chase_otm.getReachedRate() / 100.
#         tmp['計畫執行情形說明(若有執行落後者，請詳細說明預定完成日期及因應措施'] = p.chase_otm.memo
#         if p.chase_otm.expected_to_end_percent: p.chase_otm.expected_to_end_percent = float(str(p.chase_otm.expected_to_end_percent))
#         else: p.chase_otm.expected_to_end_percent = 0
#         tmp['預計至年底執行率'] = p.chase_otm.expected_to_end_percent / 100.
#         tmp['執行單位'] = p.unit.name
# #        tmp['署內負責人'] = p.self_charge or ''
# #        tmp['原始負責人'] = ''
        
#         tmp['勞務_核定計畫'] = ('預計：' + str(p.chase_obo.sch_ser_approved_plan or '') + "           實際：" + str(p.chase_obo.act_ser_approved_plan or '')).encode('cp950')
#         tmp['勞務_簽辦招標'] = ('預計：' + str(p.chase_obo.sch_ser_signed_tender  or '') + "           實際：" + str(p.chase_obo.act_ser_signed_tender or '')).encode('cp950')
#         tmp['勞務_公告招標'] = ('預計：' + str(p.chase_obo.sch_ser_announcement_tender or '') + "           實際：" + str(p.chase_obo.act_ser_announcement_tender or '')).encode('cp950')
#         tmp['勞務_公開評選會議(限制性招標)'] = ('預計：' + str(p.chase_obo.sch_ser_selection_meeting or '') + "           實際：" + str(p.chase_obo.act_ser_selection_meeting or '')).encode('cp950')
#         tmp['勞務_定約'] = ('預計：' + str(p.chase_obo.sch_ser_promise or '') + "           實際：" + str(p.chase_obo.act_ser_promise or '')).encode('cp950')
#         tmp['勞務_基本設計'] = ('預計：' + str(p.chase_obo.sch_ser_work_plan or '') + "           實際：" + str(p.chase_obo.act_ser_work_plan or '')).encode('cp950')
#         tmp['勞務_細部設計'] = ('預計：' + str(p.chase_obo.sch_ser_interim_report or '') + "           實際：" + str(p.chase_obo.act_ser_interim_report or '')).encode('cp950')
#         tmp['勞務_驗收結案'] = ('預計：' + str(p.chase_obo.sch_ser_final_report or '') + "           實際：" + str(p.chase_obo.act_ser_final_report or '')).encode('cp950')
#         tmp['勞務_簽辦招標'] = ('預計：' + str(p.chase_obo.sch_ser_acceptance_closed or '') + "           實際：" + str(p.chase_obo.act_ser_acceptance_closed or '')).encode('cp950')

#         tmp['設計規劃_核定計畫'] = ('預計：' + str(p.chase_obo.sch_eng_plan_approved_plan or '') + "           實際：" + str(p.chase_obo.act_eng_plan_approved_plan or '')).encode('cp950')
#         tmp['設計規劃_簽辦招標'] = ('預計：' + str(p.chase_obo.sch_eng_plan_signed_tender or '') + "           實際：" + str(p.chase_obo.act_eng_plan_signed_tender or '')).encode('cp950')
#         tmp['設計規劃_公告招標'] = ('預計：' + str(p.chase_obo.sch_eng_plan_announcement_tender or '') + "           實際：" + str(p.chase_obo.act_eng_plan_announcement_tender or '')).encode('cp950')
#         tmp['設計規劃_公開評選會議(限制性招標)'] = ('預計：' + str(p.chase_obo.sch_eng_plan_selection_meeting or '') + "           實際：" + str(p.chase_obo.act_eng_plan_selection_meeting or '')).encode('cp950')
#         tmp['設計規劃_定約'] = ('預計：' + str(p.chase_obo.sch_eng_plan_promise or '') + "           實際：" + str(p.chase_obo.act_eng_plan_promise or '')).encode('cp950')
#         tmp['設計規劃_基本設計'] = ('預計：' + str(p.chase_obo.sch_eng_plan_basic_design or '') + "           實際：" + str(p.chase_obo.act_eng_plan_basic_design or '')).encode('cp950')
#         tmp['設計規劃_細部設計'] = ('預計：' + str(p.chase_obo.sch_eng_plan_detail_design or '') + "           實際：" + str(p.chase_obo.act_eng_plan_detail_design or '')).encode('cp950')
#         tmp['設計規劃_驗收結案'] = ('預計：' + str(p.chase_obo.sch_eng_plan_acceptance_closed or '') + "           實際：" + str(p.chase_obo.act_eng_plan_acceptance_closed or '')).encode('cp950')
#         tmp['工程施做_簽辦招標'] = ('預計：' + str(p.chase_obo.sch_eng_do_signed_tender or '') + "           實際：" + str(p.chase_obo.act_eng_do_signed_tender or '')).encode('cp950')
#         tmp['工程施做_公告招標'] = ('預計：' + str(p.chase_obo.sch_eng_do_announcement_tender or '') + "           實際：" + str(p.chase_obo.act_eng_do_announcement_tender or '')).encode('cp950')
#         tmp['工程施做_定約'] = ('預計：' + str(p.chase_obo.sch_eng_do_promise or '') + "           實際：" + str(p.chase_obo.act_eng_do_promise or '')).encode('cp950')
#         tmp['工程施做_開工'] = ('預計：' + str(p.chase_obo.sch_eng_do_start or '') + "           實際：" + str(p.chase_obo.act_eng_do_start or '')).encode('cp950')
#         tmp['工程施做_完工'] = ('預計：' + str(p.chase_obo.sch_eng_do_completion or '') + "           實際：" + str(p.chase_obo.act_eng_do_completion or '')).encode('cp950')
#         tmp['工程施做_驗收'] = ('預計：' + str(p.chase_obo.sch_eng_do_acceptance or '') + "           實際：" + str(p.chase_obo.act_eng_do_acceptance or '')).encode('cp950')
#         tmp['工程施做_結案'] = ('預計：' + str(p.chase_obo.sch_eng_do_closed or '') + "           實際：" + str(p.chase_obo.act_eng_do_closed or '')).encode('cp950')
        
#         try:
#             p.frcm = p.frcmusergroup_set.get(group__name__in=['負責主辦工程師', '自辦主辦工程師'])
#             tmp['執行單位聯絡窗口'] = p.frcm.user.user_profile.rName()
#             tmp['縣市政府聯絡方式(mail及電話)'] = str(p.frcm.user.user_profile.phone) + '    (' + p.frcm.user.email + ')'
#         except:
#             tmp['執行單位聯絡窗口'] = ''
#             tmp['縣市政府聯絡方式(mail及電話)'] = ''

#         if p.purchase_type.value == '工程':
#             data['table_eng'].append(tmp)
#         else:
#             data['table_ser'].append(tmp)
#     return data


# @login_required
# @checkAuthority
# def AllChaseInfo(R, project, right_type_value=u'使用縣市追蹤系統', **kw):
#     user, DATA = R.user, readDATA(R)
#     project = Project.objects.get(id=kw['project_id'])
#     if _ca(user=user, project='', project_id=0, right_type_value=u'使用縣市追蹤系統'):
#         edit = True
#     else:
#         edit = False

#     chases = CountyChaseProjectOneToMany.objects.filter(project=project).order_by('-countychasetime__id')
#     for i in chases:
#         i.chase_time = CountyChaseTime.objects.filter(chase_date__lte=i.countychasetime.chase_date).count()

#     t = get_template(os.path.join('project', 'all_chase_info.html'))
#     html = t.render(RequestContext(R,{
#         'edit': edit,
#         'project': project,
#         'chases': chases,
#         }))
#     return HttpResponse(html)


# @login_required
# @checkAuthority
# def ReadAndPrintCountyChase(R, project, right_type_value=u'使用縣市追蹤系統', **kw):
#     user, DATA = R.user, readDATA(R)
#     if _ca(user=user, project='', project_id=0, right_type_value=u'使用縣市追蹤系統'):
#         edit = True
#     else:
#         edit = False

#     class searchForm(forms.Form):
#         countychasetimes = []
#         for i in CountyChaseTime.objects.all().order_by('-id')[0:10]:
#             times = CountyChaseTime.objects.filter(id__lte=i.id).count()
#             num = CountyChaseProjectOneToMany.objects.filter(countychasetime__id=i.id).count()
#             countychasetimes.append((i.id, '第'+str(times)+'次( '+str(i.chase_date)+' )-[ '+str(num)+'件 ]'))
#         countychasetime = forms.ChoiceField(choices=countychasetimes, required=False, label='選擇追蹤版本：')
# #        news = [('True', '最新狀況'), ('False', '維持原版本')]
# #        new = forms.ChoiceField(choices=news, required=False, label='')
#         close_checks = [('', '全部'), ('False', '尚未確認結案'), ('True', '已確認結案')]
#         close_check = forms.ChoiceField(choices=close_checks, required=False, label='是否結案：')
#         complete_checks = [('', '全部'), ('False', '尚未確認填寫完畢'), ('True', '已確認填寫完畢')]
#         complete_check = forms.ChoiceField(choices=complete_checks, required=False, label='是否填寫完畢：')
#         plans = [('', '全部')]
#         for i in Plan.objects.filter(uplevel=None):
#             plans.append((i.id, '---'*i.rLevelNumber() + i.name))
#             for j in i.rSubPlanInList():
#                 plans.append((j.id, '---'*j.rLevelNumber() + j.name))
#         plan = forms.ChoiceField(choices=plans, required=False, label='所屬計畫：')
#         project_sub_type = [('0', '不含下層計畫'), ('1', '含下層計畫')]
#         project_sub_type = forms.ChoiceField(choices=project_sub_type, required=False, label='　　層級：')
#         purchase_types = [('', '全部')] + [(type.id, type.value) for type in Option.objects.filter(swarm='purchase_type')]
#         purchase_type = forms.ChoiceField(choices=purchase_types, required=False, label='採購類別：', help_text='(工程／勞務)')
#         budget_sub_types = [('', '全部')] + [(type.id, type.value) for type in Option.objects.filter(swarm='budget_sub_type')]
#         budget_sub_type = forms.ChoiceField(choices=budget_sub_types, required=False, label='經費種類：', help_text='(資本門／經常門)')
#         undertake_types = [('', '全部')] + [(type.id, type.value) for type in Option.objects.filter(swarm='undertake_type')]
#         undertake_type = forms.ChoiceField(choices=undertake_types, required=False, label='承辦方式：', help_text='(自辦／委辦／補助)')
#         years = [(y-1911, y-1911) for y in xrange(2006, TODAY().year+2)]
#         years.insert(0, ('', '所有年度'))
#         years.reverse()
#         year = forms.ChoiceField(choices=years, required=False, label='年度：')
#         places = [('', '全部')] + [(i.id, i.name) for i in Place.objects.filter(uplevel=TAIWAN).order_by('id')]
#         place = forms.ChoiceField(choices=places, required=False, label='縣市別')
#         units = [('', '全部')]
#         for i in Unit.fish_city_menu.all():
#             units.append((i.id, i.name))
#             if i.uplevel and i.uplevel.name != '縣市政府':
#                 units.extend(
#                     [(j.id, '---'+j.name) for j in i.uplevel_subunit.all()]
#                 )
#         unit = forms.ChoiceField(choices=units, required=False, label='執行機關：')

#     places = Place.objects.filter(uplevel=TAIWAN).order_by('id')
#     plans = [['', '全部']]
#     for i in Plan.objects.filter(uplevel=None):
#         plans.append([i.id, '---'*i.rLevelNumber() + i.name])
#         for j in i.rSubPlanInList():
#             plans.append([j.id, '---'*j.rLevelNumber() + j.name])

#     form = searchForm()
#     projects_num = -1
#     projects = []
#     querystring = ''
#     INFO = {}
#     for k, v in R.GET.items(): INFO[k] = v
#     for k, v in R.POST.items(): INFO[k] = v
#     p_list = []
    
#     countychasetime = list(CountyChaseTime.objects.all().order_by('id'))[-1]
#     countychasetime.time = CountyChaseTime.objects.all().count()
#     countychasetime.pastDay = (datetime.date.today() - countychasetime.chase_date).days
#     countychasetime.num = CountyChaseProjectOneToMany.objects.filter(countychasetime=countychasetime).count()

#     chase_projects = countychasetime.countychaseprojectonetomany_set.all()
#     close_num = 0
#     complete_num = 0
#     for p in chase_projects:
#         if p.getOneByOne().check == False and p.getOneByOne().close == True:
#             close_num += 1
#         if p.check == False and p.complete == True:
#             complete_num += 1
    
#     if INFO.get('submit', None):
#         form = searchForm(INFO)
#         querystring = '&'.join(['%s=%s'%(k, v) for k, v in INFO.items() if k != 'page'])
#         projects, projects_num, p_list = _searchChaseProject(INFO, use_page=False)
#         this_countychasetime = CountyChaseTime.objects.get(id=INFO.get('countychasetime', None))
#         for p in projects:
#             p.chase = CountyChaseProjectOneToMany.objects.get(countychasetime=this_countychasetime, project=p)
#             if FRCMUserGroup.objects.filter(project=p).count() > 0: p.frcm = True
#             else: p.frcm = False
#     elif INFO.get('makeExcel', None):
#         INFO['sortBy'] = 'place'
#         form = searchForm(INFO)
#         projects, projects_num, p_list = _searchChaseProject(INFO, use_page=False)
#         this_countychasetime = CountyChaseTime.objects.get(id=INFO.get('countychasetime', None))
# #        this_countychasetime_num = CountyChaseTime.objects.filter(id__lte=this_countychasetime.id).count()
#         result = _makeDownloadFile_CountyChase(user=user, projects=projects, countychasetime=this_countychasetime, new=INFO.get('new'))
#         template_name = 'county_chase.xls'
#         content = makeFileByWordExcel(template_name=template_name, result=result)
#         response = HttpResponse(content_type='application/xls')
#         response['Content-Type'] = ('application/xls')
#         response['Content-Disposition'] = ('attachment; filename=%s.xls' % (str(this_countychasetime.chase_date) + '-縣市進度追蹤表')).encode('cp950')
#         response.write(content)
#         return response

#     places = sort_By_South(places, countychasetime)

#     t = get_template(os.path.join('project', 'readandprintcountychase.html'))
#     html = t.render(RequestContext(R,{
#         'edit': edit,
#         'places': places,
#         'form': form,
#         'plans': plans,
#         'close_num': close_num,
#         'complete_num': complete_num,
#         'projects': projects,
#         'projects_num': projects_num,
#         'option' : _make_choose(),
#         'p_list': p_list,
#         'countychasetime': countychasetime,
#         }))
#     R.querystring = querystring
#     return HttpResponse(html)


# def _searchChaseProject(INFO, user='', use_page=True):
#     if INFO.get('sortBy', None):
#         result = Project.objects.filter(deleter=None).order_by(INFO.get('sortBy', None))
#     else:
#         result = Project.objects.filter(deleter=None)

#     if INFO.get('countychasetime', None):
#         countychasetime = CountyChaseTime.objects.get(id=INFO.get('countychasetime', None))
#         ids = []
#         ids.extend([i.project.id for i in CountyChaseProjectOneToMany.objects.filter(countychasetime=countychasetime)])
#         result = result.filter(id__in=ids)

#     if INFO.get('bid_no', None) and INFO.get('bid_no', None) != '':
#         ids = []
#         for bid_no in re.split('[ ,]+', INFO.get('bid_no', None)):
#             ids.extend([i.id for i in result.filter(bid_no__icontains=bid_no)])
#         result = result.filter(id__in=ids)

#     if INFO.get('name', None) and INFO.get('name', None) != '':
#         ids = []
#         for name in re.split('[ ,]+', INFO.get('name', None)):
#             ids.extend([i.id for i in result.filter(name__icontains=name)])
#         result = result.filter(id__in=ids)

#     if INFO.get('plan', None) and INFO.get('plan', None) != '':
#         plan = Plan.objects.get(id=INFO.get('plan', None))
#         if INFO.get('project_sub_type', None) == '1':
#             plan_ids = [plan.id] + [i.id for i in Plan.objects.get(id=INFO.get('plan', None)).rSubPlanInList()]
#             result = result.filter(plan__id__in=plan_ids)
#         else:
#             result = result.filter(plan = plan)

#     if INFO.get('purchase_type', None) and INFO.get('purchase_type', None) != '':
#         result = result.filter(purchase_type=Option.objects.get(id=INFO.get('purchase_type', None)))

#     if INFO.get('budget_sub_type', None) and INFO.get('budget_sub_type', None) != '':
#         result = result.filter(budget_sub_type=Option.objects.get(id=INFO.get('budget_sub_type', None)))

#     if INFO.get('undertake_type', None) and INFO.get('undertake_type', None) != '':
#         result = result.filter(undertake_type=Option.objects.get(id=INFO.get('undertake_type', None)))

#     if INFO.get('year', None) and INFO.get('year', None) != '':
#         result = result.filter(year=INFO.get('year', None))

#     if INFO.get('unit', None) and INFO.get('unit', None) != '':
#         unit = Unit.objects.get(id=INFO.get('unit', None))
#         result = result.filter(unit=unit)

#     if INFO.get('place', None) and INFO.get('place', None) != '':
#         place = Place.objects.get(id=INFO.get('place', None))
#         result = result.filter(place=place)

#     if INFO.get('close_check', None):
#         ids = []
#         if INFO.get('close_check', None) == 'True':
#             for i in result:
#                 try:
#                     if i.countychaseprojectonebyone_set.get().check: ids.append(i.id)
#                 except: pass
#         elif INFO.get('close_check', None) == 'False':
#             for i in result:
#                 try:
#                     if not i.countychaseprojectonebyone_set.get().check: ids.append(i.id)
#                 except: ids.append(i.id)
#         result = result.filter(id__in=ids)

#     if INFO.get('complete_check', None):
#         ids = []
#         if INFO.get('complete_check', None) == 'True':
#             for i in result:
#                 try:
#                     if i.countychaseprojectonetomany_set.get(countychasetime=countychasetime).check: ids.append(i.id)
#                 except: pass
#         elif INFO.get('complete_check', None) == 'False':
#             for i in result:
#                 try:
#                     if not i.countychaseprojectonetomany_set.get(countychasetime=countychasetime).check: ids.append(i.id)
#                 except: ids.append(i.id)
#         result = result.filter(id__in=ids)


#     p_list = [int(i.id) for i in result]

#     result_num = len(result)
#     if not use_page:
#         projects = result[:]
#     else:
#         if not INFO.get('page', None): page = 1
#         else: page = int(INFO['page'])

#         projects = []
#         for order, u in enumerate(result[int((page-1)*NUMPERPAGE):int(page*NUMPERPAGE)]):
#             u.order = int((page-1)*NUMPERPAGE+order+1)
#             projects.append(u)

#     return projects, result_num, p_list


# @login_required
# @checkAuthority
# def CountyChaseSetCloseCheck(R, project, right_type_value=u'使用縣市追蹤系統', **kw):
#     user, DATA = R.user, readDATA(R)

#     places = Place.objects.filter(uplevel=TAIWAN).order_by('id')
#     plans = [['', '全部']]
#     for i in Plan.objects.filter(uplevel=None):
#         plans.append([i.id, '---'*i.rLevelNumber() + i.name])
#         for j in i.rSubPlanInList():
#             plans.append([j.id, '---'*j.rLevelNumber() + j.name])


#     projects_num = -1
#     projects = []
#     querystring = ''
#     INFO = {}
#     for k, v in R.GET.items(): INFO[k] = v
#     for k, v in R.POST.items(): INFO[k] = v
#     p_list = []

#     countychasetime = list(CountyChaseTime.objects.all().order_by('id'))[-1]
#     countychasetime.time = CountyChaseTime.objects.all().count()
#     countychasetime.pastDay = (datetime.date.today() - countychasetime.chase_date).days
#     countychasetime.num = CountyChaseProjectOneToMany.objects.filter(countychasetime=countychasetime).count()

#     chase_projects = countychasetime.countychaseprojectonetomany_set.all().order_by('project__place')

#     projects = []
#     for i in chase_projects:
#         if i.getOneByOne().check == False and i.getOneByOne().close == True:
#             i.project.frcmuser = FRCMUserGroup.objects.get(project=i.project, group__name__in=['負責主辦工程師', '自辦主辦工程師']).user
#             i.project.chase = CountyChaseProjectOneToMany.objects.get(countychasetime=countychasetime, project=i.project)
#             projects.append(i.project)
            
#     places = sort_By_South(places, countychasetime)

#     t = get_template(os.path.join('project', 'countychasesetclosecheck.html'))
#     html = t.render(RequestContext(R,{
#         'places': places,
#         'plans': plans,
#         'projects': projects,
#         'option' : _make_choose(),
#         'countychasetime': countychasetime,
#         }))
#     R.querystring = querystring
#     return HttpResponse(html)


# @login_required
# @checkAuthority
# def CountyChaseSetCompleteCheck(R, project, right_type_value=u'使用縣市追蹤系統', **kw):
#     user, DATA = R.user, readDATA(R)

#     places = Place.objects.filter(uplevel=TAIWAN).order_by('id')
#     plans = [['', '全部']]
#     for i in Plan.objects.filter(uplevel=None):
#         plans.append([i.id, '---'*i.rLevelNumber() + i.name])
#         for j in i.rSubPlanInList():
#             plans.append([j.id, '---'*j.rLevelNumber() + j.name])


#     projects_num = -1
#     projects = []
#     querystring = ''
#     INFO = {}
#     for k, v in R.GET.items(): INFO[k] = v
#     for k, v in R.POST.items(): INFO[k] = v
#     p_list = []

#     countychasetime = list(CountyChaseTime.objects.all().order_by('id'))[-1]
#     countychasetime.time = CountyChaseTime.objects.all().count()
#     countychasetime.pastDay = (datetime.date.today() - countychasetime.chase_date).days
#     countychasetime.num = CountyChaseProjectOneToMany.objects.filter(countychasetime=countychasetime).count()

#     chase_projects = countychasetime.countychaseprojectonetomany_set.all().order_by('project__place')

#     projects = []
#     for i in chase_projects:
#         if i.check == False and i.complete == True:
#             i.project.frcmuser = FRCMUserGroup.objects.get(project=i.project, group__name__in=['負責主辦工程師', '自辦主辦工程師']).user
#             i.project.chase = CountyChaseProjectOneToMany.objects.get(countychasetime=countychasetime, project=i.project)
#             projects.append(i.project)
        
#     places = sort_By_South(places, countychasetime)

#     t = get_template(os.path.join('project', 'countychasesetcompletecheck.html'))
#     html = t.render(RequestContext(R,{
#         'places': places,
#         'plans': plans,
#         'projects': projects,
#         'option' : _make_choose(),
#         'countychasetime': countychasetime,
#         }))
#     R.querystring = querystring
#     return HttpResponse(html)

# def sort_By_South(places, countychasetime):
#     class fish_self(): pass
#     tmp = []
#     for place in places:
#         place.check = CountyChaseProjectOneToMany.objects.filter(countychasetime=countychasetime, project__place=place, check=True).exclude(project__undertake_type__value='自辦').count()
#         place.not_in_frcm = 0
#         for i in CountyChaseProjectOneToMany.objects.filter(countychasetime=countychasetime, project__place=place, check=False).exclude(project__undertake_type__value='自辦'):
#             if FRCMUserGroup.objects.filter(project=i.project).count() == 0:
#                 place.not_in_frcm += 1
#         place.not_check = CountyChaseProjectOneToMany.objects.filter(countychasetime=countychasetime, project__place=place, check=False).exclude(project__undertake_type__value='自辦').count() - place.not_in_frcm
#     north = []
#     south = []
#     no_idea = []
#     no_idea_places = ['南投縣']
#     south_places = ['彰化縣', '雲林縣', '嘉義市', '嘉義縣', '臺南市', '高雄市', '屏東縣', '臺南市', '澎湖縣', '臺東縣']
#     for place in places:
#         if place.name in south_places:
#             place.south = True
#             south.append(place)
#         elif place.name in no_idea_places:
#             no_idea.append(place)
#         elif place.name != '南海島':
#             place.south = False
#             north.append(place)

#     fish_north = fish_self()
#     fish_north.name = '北部辦公室'
#     fish_north.id = 'north'
#     fish_north.check = CountyChaseProjectOneToMany.objects.filter(countychasetime=countychasetime, check=True, project__undertake_type__value='自辦').exclude(project__place__name__in=south_places).count()
#     fish_north.not_in_frcm = 0
#     for i in CountyChaseProjectOneToMany.objects.filter(countychasetime=countychasetime, check=False, project__undertake_type__value='自辦').exclude(project__place__name__in=south_places):
#         if FRCMUserGroup.objects.filter(project=i.project).count() == 0:
#             fish_north.not_in_frcm += 1
#     fish_north.not_check = CountyChaseProjectOneToMany.objects.filter(countychasetime=countychasetime, check=False, project__undertake_type__value='自辦').exclude(project__place__name__in=south_places).count() - fish_north.not_in_frcm

#     fish_south = fish_self()
#     fish_south.name = '南部辦公室'
#     fish_south.id = 'south'
#     fish_south.check = CountyChaseProjectOneToMany.objects.filter(countychasetime=countychasetime, project__place__name__in=south_places, check=True, project__undertake_type__value='自辦').count()
#     fish_south.not_in_frcm = 0
#     for i in CountyChaseProjectOneToMany.objects.filter(countychasetime=countychasetime, project__place__name__in=south_places, check=False, project__undertake_type__value='自辦'):
#         if FRCMUserGroup.objects.filter(project=i.project).count() == 0:
#             fish_south.not_in_frcm += 1
#     fish_south.not_check = CountyChaseProjectOneToMany.objects.filter(countychasetime=countychasetime, project__place__name__in=south_places, check=False, project__undertake_type__value='自辦').count() - fish_south.not_in_frcm





#     places = [fish_north] + [fish_south] + north + south + no_idea
#     return places

# @login_required
# @checkAuthority
# def addProject(R, project, right_type_value=u'新增工程案', **kw):
#     place = [TAIWAN] + list(Place.objects.filter(uplevel=TAIWAN).order_by('id'))
#     units = []
#     for i in Unit.fish_city_menu.all():
#         units.append((i.id, i.name))
#         if i.uplevel and i.uplevel.name != '縣市政府':
#             units.extend(
#                 [(j.id, '---'+j.name) for j in i.uplevel_subunit.all()]
#             )
#     years = [y-1911 for y in xrange(2006, TODAY().year+2)]
#     years.reverse()
#     carry_info = {}
#     try:
#         for i in kw['dictionary_str'].split('+'):
#             k, v = i.split(':')
#             if k == 'plan_id':
#                 carry_info[k] = int(v)
#             else:
#                 carry_info[k] = v
#     except: pass
#     max_level = 0
#     all_plans = []
#     for i in Plan.objects.filter(uplevel=None):
#         all_plans.append({'id':i.id, 'name':i , 'level':i.rLevelNumber(), 'serial':i.project_serial, 'code':i.code, 'up_code':'000'})
#         for j in i.rSubPlanInList():
#             all_plans.append({'id':j.id, 'name':'---'*j.rLevelNumber() + j.name, 'level':j.rLevelNumber(), 'serial':j.project_serial, 'code':j.code, 'up_code':j.uplevel.code})
#             if j.rLevelNumber() > max_level:
#                 max_level = j.rLevelNumber()
    
#     project_type_sorts = Option.objects.filter(swarm='project_type_sort').order_by('value')
#     project_sub_types = Option.objects.filter(swarm='port_type').order_by('id')
#     budget_sub_types = Option.objects.filter(swarm='budget_sub_type').order_by('id')
#     farm_types = Option.objects.filter(swarm='farm_type').order_by('id')


#     t = get_template(os.path.join('project', 'addproject.html'))
#     html = t.render(RequestContext(R,{'plans' : all_plans, 'carry_info': carry_info, 'project_type_sorts' : project_type_sorts,
#                                     'project_sub_types' : project_sub_types, 'farm_types': farm_types, 'max_level' : max_level, 'years' : years,
#                                     'this_year': int(TODAY().year - 1911), 'units' : units, 'years' : years,
#                                     'place_list' : place, 'option' : _make_choose(), 'budget_sub_types': budget_sub_types,
#                                     }))
#     return HttpResponse(html)


# def addProjectFromDraft(R, **kw):
#     place = [TAIWAN] + list(Place.objects.filter(uplevel=TAIWAN).order_by('id'))
#     units = []
#     for i in Unit.fish_city_menu.all():
#         units.append((i.id, i.name))
#         if i.uplevel and i.uplevel.name != '縣市政府':
#             units.extend(
#                 [(j.id, '---'+j.name) for j in i.uplevel_subunit.all()]
#             )
#     years = [y-1911 for y in xrange(2006, TODAY().year+2)]
#     years.reverse()
#     carry_info = {}
#     try:
#         for i in kw['dictionary_str'].split('+'):
#             k, v = i.split(':')
#             if k == 'plan_id':
#                 carry_info[k] = int(v)
#             else:
#                 carry_info[k] = v
#     except: pass
#     max_level = 0
#     all_plans = []
#     for i in Plan.objects.filter(uplevel=None):
#         all_plans.append({'id':i.id, 'name':i , 'level':i.rLevelNumber(), 'serial':i.project_serial, 'code':i.code, 'up_code':'000'})
#         for j in i.rSubPlanInList():
#             all_plans.append({'id':j.id, 'name':'---'*j.rLevelNumber() + j.name, 'level':j.rLevelNumber(), 'serial':j.project_serial, 'code':j.code, 'up_code':j.uplevel.code})
#             if j.rLevelNumber() > max_level:
#                 max_level = j.rLevelNumber()

#     project_type_sorts = Option.objects.filter(swarm='project_type_sort').order_by('value')
#     project_sub_types = Option.objects.filter(swarm='port_type').order_by('id')
#     budget_sub_types = Option.objects.filter(swarm='budget_sub_type').order_by('id')
#     farm_types = Option.objects.filter(swarm='farm_type').order_by('id')

#     project = Draft_Project.objects.get(id=kw['project_id'])
# #    project = Draft_Project.objects.get(id=R.POST.get('project_id'))
# #    data = []
# #    data_dic = {}
# #    for field_name in project._meta.get_all_field_names():
# #        if field_name != 'fishing_port' and field_name != 'aquaculture':
# #            try:
# #                #為了連外鍵所用的欄位
# #                data.append([field_name, getattr(project, field_name).id])
# #                data_dic[field_name] = getattr(project, field_name).id
# #            except:
# #                try:
# #                    #數字欄位
# #                    data.append([field_name, float(str(getattr(project, field_name)))])
# #                    data_dic[field_name] = float(str(getattr(project, field_name)))
# #                except:
# #                    #正常欄位
# #                    data.append([field_name, getattr(project, field_name)])
# #                    data_dic[field_name] = getattr(project, field_name)
# #    exproject = []
# #    if project.project:
# #        exproject = [project.project.id, (str(project.project.year) + ':' + project.project.name)]
# #
#     port_list = []
#     port_html = ''
#     if project.project_type.value == '1 漁港工程':
#         for p in project.fishing_port.all():
#             port_list.append(p.id)
#             port_html += '<select id="FishingPort" class="sub_location setCoord"><option value="" twdx="" twdy="">請選擇</option>'
#             port_html += '<option selected="selected" value="'+str(p.id)+'" twdx="" twdy="">'+p.name+'</option></select><br>'

#     else:
#         for p in project.aquaculture.all():
#             port_list.append(p.id)
#             port_html += '<select id="FishingPort" class="sub_location setCoord"><option value="" twdx="" twdy="">請選擇</option>'
#             port_html += '<option selected="selected" value="'+str(p.id)+'" twdx="" twdy="">'+p.name+'</option></select><br>'
#     port_html += '<span id="insertSubLocation"></span>'

#     t = get_template(os.path.join('project', 'addproject_from_draft.html'))
#     html = t.render(RequestContext(R,{'plans' : all_plans, 'carry_info': carry_info, 'project_type_sorts' : project_type_sorts,
#                                     'project_sub_types' : project_sub_types, 'farm_types': farm_types, 'max_level' : max_level, 'years' : years,
#                                     'this_year': int(TODAY().year - 1911), 'units' : units, 'years' : years, 'port_html': port_html,
#                                     'place_list' : place, 'option' : _make_choose(), 'budget_sub_types': budget_sub_types, 'project': project
#                                     }))
#     return HttpResponse(html)


# @login_required
# @checkAuthority
# def reDraftProject(R, project, right_type_value=u'新增工程案', **kw):
#     if R.user.is_staff or R.user.user_profile.group.name == '管考填寫員':
#         power = True

#     place = [TAIWAN] + list(Place.objects.filter(uplevel=TAIWAN).order_by('id'))
#     units = []
#     for i in Unit.fish_city_menu.all():
#         units.append((i.id, i.name))
#         if i.uplevel and i.uplevel.name != '縣市政府':
#             units.extend(
#                          [(j.id, '---' + j.name) for j in i.uplevel_subunit.all()]
#                          )
#     years = [y-1911 for y in xrange(2006, TODAY().year + 2)]
#     years.reverse()
#     carry_info = {}
#     try:
#         for i in kw['dictionary_str'].split('+'):
#             k, v = i.split(':')
#             if k == 'plan_id':
#                 carry_info[k] = int(v)
#             else:
#                 carry_info[k] = v
#     except: pass
#     max_level = 0

#     all_plans = []
#     for i in Plan.objects.filter(uplevel=None):
#         all_plans.append({'id':i.id, 'name':i, 'level':i.rLevelNumber(), 'serial':i.project_serial, 'code':i.code, 'up_code':'000'})
#         for j in i.rSubPlanInList():
#             all_plans.append({'id':j.id, 'name':'---' * j.rLevelNumber() + j.name, 'level':j.rLevelNumber(), 'serial':j.project_serial, 'code':j.code, 'up_code':j.uplevel.code})
#             if j.rLevelNumber() > max_level:
#                 max_level = j.rLevelNumber()

#     page_title = '漁業署提案'
#     if kw['draft_type'] == 'fishery':
#         type = '漁業署草稿'
#         projects = Draft_Project.objects.filter(type__value='漁業署草稿').order_by('place', 'sort')
#     elif kw['draft_type'] == 'city':
#         type = '縣市提案草稿'
#         projects = Draft_Project.objects.filter(type__value='縣市提案草稿').order_by('place', 'sort')
    
#     for p in projects:
#         if p.project_type.value == '1 漁港工程':
#             p.port = p.fishing_port.all()
#         else:
#             p.port = p.aquaculture.all()
#     project_sub_types = Option.objects.filter(swarm='port_type').order_by('id')
#     project_type_sorts = Option.objects.filter(swarm='project_type_sort').order_by('value')
#     budget_sub_types = Option.objects.filter(swarm='budget_sub_type').order_by('id')
#     farm_types = Option.objects.filter(swarm='farm_type').order_by('id')

    

#     t = get_template(os.path.join('project', 'draft_projects.html'))
#     html = t.render(RequestContext(R, {
#                     'plans': all_plans, 'projects': projects, 'page_title': page_title, 'url': '/project/draft_project/',
#                     'project_sub_types': project_sub_types, 'farm_types': farm_types, 'max_level': max_level, 'years': years, 'power': power,
#                     'this_year': int(TODAY().year - 1911), 'units': units, 'years': years, 'project_type_sorts': project_type_sorts,
#                     'place_list': place, 'option': _make_choose(), 'budget_sub_types': budget_sub_types, 'type': type
#                     }))
#     return HttpResponse(html)


# #<{------ re function ------}>
# @login_required
# @checkAuthority
# def guideProjectURL(R, project, right_type_value=u'觀看管考系統資料', **kw):
#     user, DATA = R.user, readDATA(R)
    
#     url = '/project/basic/' + kw['project_id'] + '/'
#     return HttpResponseRedirect(url)




# @login_required
# @checkAuthority
# def eProjectBasic(R, project, right_type_value=u'觀看管考系統資料', **kw):
#     user, DATA = R.user, readDATA(R)
#     if _ca(user=user, project='', project_id=0, right_type_value=u'填寫管考系統資料'):
#         edit = True
#     else:
#         edit = False

#     target_project = Project.objects.get(id = kw['project_id'])

# # <{------ 工程基本資料 ------}>
#     place = [TAIWAN] + list(Place.objects.filter(uplevel=TAIWAN).order_by('id'))
#     ports = FishingPort.objects.filter(place=target_project.place)
#     units = []
#     for i in Unit.fish_city_menu.all():
#         units.append((i.id, i.name))
#         if i.uplevel and i.uplevel.name != '縣市政府':
#             units.extend(
#                 [(j.id, '---'+j.name) for j in i.uplevel_subunit.all()]
#             )
#     status = Project.objects.get(id = kw['project_id']).status
#     undertak = Project.objects.get(id = kw['project_id']).undertake_type
#     if undertak.id == 157:
#         notselfundertak = False
#     else:
#         notselfundertak = True
#     years = [y-1911 for y in xrange(2006, TODAY().year+2)]
#     years.reverse()
#     max_level = 0
#     all_plans = []
#     plans = []
#     for i in Plan.objects.filter(uplevel=None):
#         all_plans.append({'id':i.id, 'value':i, 'level':i.rLevelNumber()})
#         for j in i.rSubPlanInList():
#             all_plans.append({'id':j.id, 'value':'---'*j.rLevelNumber() + j.name, 'level':j.rLevelNumber()})
#             if j.rLevelNumber() > max_level:
#                 max_level = j.rLevelNumber()
#     project_type_sorts = Option.objects.filter(swarm='project_type_sort').order_by('value')
#     project_sub_types = Option.objects.filter(swarm='port_type').order_by('id')
#     project_purchase_types = Option.objects.filter(swarm='purchase_type').order_by('id')

#     farm_types = Option.objects.filter(swarm='farm_type').order_by('id')
#     other_ids = [197,  249]
#     if target_project.place.id == 1:
#         if target_project.project_type.id == 227: sub_location_list = FishingPort.objects.all()
#         elif target_project.project_type.id == 228: sub_location_list = Aquaculture.objects.all()
#     else:
#         if target_project.project_type.id == 227: sub_location_list = FishingPort.objects.filter(place=target_project.place)
#         elif target_project.project_type.id == 228: sub_location_list = Aquaculture.objects.filter(place=target_project.place)

#     chase_one_by_one = project.countychaseprojectonebyone_set.get()

#     document_files = DocumentFile.objects.filter(project=project).order_by('date')
    
# # <{------ 標案資料 ------}>
#     total_cost_contract = target_project.rContractTotalMoney()
#     total_cost_settlement = target_project.rSettlementTotalMoney()
#     #share = False
#     #if target_project.rTotalMoney() == 0 or target_project.allot_rate == None:
#     #    share = False
#     #else:
#     #    load = round(float(target_project.rTotalMoney())*float(target_project.allot_rate)*0.01, 3)
#     #    local = round(float(target_project.rTotalMoney()) - load, 3)
#     #    share = [load, local]
#     t = get_template(os.path.join('project', 'basicinfo.html'))
#     html = t.render(RequestContext(R,{
#                                     'page' : 'Basic',
#                                     'target_project' : target_project,
#                                     'edit':edit,
#                                     'plans' : all_plans,
#                                     'project_type_sorts': project_type_sorts, 
#                                     'project_sub_types' : project_sub_types,
#                                     'project_purchase_types': project_purchase_types,
#                                     'farm_types' : farm_types,
#                                     'other_ids': other_ids, 
#                                     'years' : years,
#                                     'units' : units,
#                                     'notselfundertak' : notselfundertak,
#                                     'years' : years,
#                                     'place_list' : place,
#                                     'option' : _make_choose(),
#                                     'total_cost_contract' : total_cost_contract,
#                                     'total_cost_settlement' : total_cost_settlement,
#                                     #'share':share,
#                                     'sub_location_list': sub_location_list,
#                                     'chase_one_by_one': chase_one_by_one,
#                                     'document_files': document_files,
#                                     }))
#     return HttpResponse(html)

# @login_required
# @checkAuthority
# def uploadDocumentFile(R, project, right_type_value=u'填寫管考系統資料', **kw):
#     DATA = readDATA(R)
#     no = R.GET.get('no')
#     date = R.GET.get('date')
#     memo = R.GET.get('memo')
#     file = R.FILES.get('newfile_file_'+str(project.id), None)
#     try:
#         extension = file.name.split('.')[-1].lower()
#     except:
#         extension = 'zip'
#     row = DocumentFile(
#                         no = no,
#                         date = date,
#                         memo = memo,
#                         ext = extension,
#                         upload_user = R.user,
#                         project = project,
#                         )
#     row.save()
    
#     if file:
#         getattr(row, 'file').save('%s.%s'%(row.id, extension), file)
#         row.save()

#     return HttpResponse(json.write({'status': True, 'id': row.id}))


# def makeNewFileTr(R):
#     id = R.POST.get('id', None)
#     row = DocumentFile.objects.get(id=id)

#     t = get_template(os.path.join('project', 'document_file.html'))
#     html = t.render(RequestContext(R,{
#         'document_files': [row],
#         'edit': True
#         }))
#     return {'status':True, 'html': html}

# @login_required
# @checkAuthority
# def toFundPage(R, project, right_type_value=u'觀看管考系統資料', **kw):
#     user, DATA = R.user, readDATA(R)
#     project = Project.objects.get(id=kw['project_id'])
#     reserved = Reserve.objects.filter(project=project)
#     if reserved.count() == 0: last_year = project.year
#     else: last_year = reserved.order_by('-year')[0].year
#     url = '/project/fund/' + kw['project_id'] + '/' + str(last_year)
#     return HttpResponseRedirect(url)


# @login_required
# @checkAuthority
# def eProjectFund(R, project, right_type_value=u'觀看管考系統資料', **kw):
#     user, DATA = R.user, readDATA(R)
#     if _ca(user=user, project='', project_id=0, right_type_value=u'填寫管考系統資料'):
#         edit = True
#     else:
#         edit = False
#     project = Project.objects.get(id = kw['project_id'])
#     fund = Fund.objects.get(project = project)
#     budgets = Budget.objects.filter(fund=fund)
#     for data in budgets:
#         try: reserve = Reserve.objects.get(year=data.year, project=data.fund.project)
#         except Reserve.DoesNotExist: reserve = False
#         data.reserve = reserve
#         data.ShouldPayThisYear = data.rShouldPayThisYear(year=data.year)
#         data.TotalAppropriatebyThisYear = data.rTotalAppropriatebyThisYear(year=data.year)
#         data.TotalProjectNotPayThisYear = data.rTotalProjectNotPayThisYear(year=data.year)
        
#     fund_record = FundRecord.objects.filter(project=project).order_by('date')
#     appropriate = Appropriate.objects.filter(project=project).order_by('allot_date')
#     allocation = Allocation.objects.filter(project=project).order_by('date')
#     t = get_template(os.path.join('project', 'fund.html'))
#     html = t.render(RequestContext(R,{
#                                 'page':'reFund',
#                                 'target_project': project,
#                                 'edit':edit,
#                                 'fund_record_list' : fund_record,
#                                 'fund' : fund,
#                                 'budgets': budgets,
#                                 'appropriate': appropriate,
#                                 'allocation': allocation,
#                                 }))
#     return HttpResponse(html)

# import time
# @login_required
# @checkAuthority
# def eProjectProgress(R, project, right_type_value=u'觀看管考系統資料', **kw):
#     user, DATA = R.user, readDATA(R)
#     td = TODAY().date()
#     if _ca(user=user, project='', project_id=0, right_type_value=u'填寫管考系統資料'):
#         edit = True
#     else:
#         edit = False
#     target_project = Project.objects.get(id = kw['project_id'])
#     progress = Progress.objects.filter(project=target_project).order_by('date')

#     t = get_template(os.path.join('project', 'progress.html'))
#     html = t.render(RequestContext(R,{
#                                 'target_project' : target_project,
#                                 'edit':edit,
#                                 'progress': progress,
#                                 'option' : _make_choose(),
#                                 }))
#     return HttpResponse(html)


# class ProjectForm(ModelForm):
#     class Meta:
#         model = Project
#         fields = []

#     plans = [('', '')]
#     for i in Plan.objects.filter(uplevel=None):
#         plans.append((i.id, i))
#         for j in i.rSubPlanInList():
#             plans.append((j.id, '---'*j.rLevelNumber() + j.name))

#     plan = forms.ChoiceField(label='上層計畫', choices=plans, required=True)

# @checkAuthority
# def ProjectMilestone(R, project, right_type_value=u'觀看管考系統資料', **kw):
#     user, DATA = R.user, readDATA(R)
#     if _ca(user=user, project='', project_id=0, right_type_value=u'填寫管考系統資料'):
#         edit = True
#     else:
#         edit = False

#     target_project = Project.objects.get(id = kw['project_id'])

#     t = get_template(os.path.join('project', 'milestone.html'))
#     html = t.render(RequestContext(R,{
#                                     'target_project' : target_project,
#                                     'edit':edit,
#                                     'page':'reMilestone',
#                                     }))
#     return HttpResponse(html)


# @checkAuthority
# def reserveProject(R, project, right_type_value=u'填寫管考系統資料', **kw):
#     project = Project.objects.get(id = kw['project_id'])
#     reserved = Reserve.objects.filter(project=project).order_by('year')
#     years = [str(project.year), ]
#     for i in reserved:
#         years.append(str(i.year))
#     t = get_template(os.path.join('project', 'reserve.html'))
#     html = t.render(RequestContext(R,{
#                                     'target_project' : project,
#                                     'years' : years,
#                                     'page':'reFund',
#                                     }))
#     return HttpResponse(html)


# def _searchBudgetProject(INFO):

#     result = Project.objects.filter(id__in=ids, deleter=None).order_by('budget_type', INFO.get('sortBy', None))

#     if INFO.get('plan', None) and INFO.get('plan', None) != '':
#         plan = Plan.objects.get(id=INFO.get('plan', None))
#         if INFO.get('sub_type', None) == 'cover':
#             plan_ids = [plan.id] + [i.id for i in Plan.objects.get(id=INFO.get('plan', None)).rSubPlanInList()]
#             result = result.filter(plan__id__in=plan_ids)
#         else:
#             result = result.filter(plan = plan)



#     if INFO.get('unit', None) and INFO.get('unit', None) != '':
#         unit = Unit.objects.get(id=INFO.get('unit', None))
#         result = result.filter(unit=unit)

#     if INFO.get('status', None) and INFO.get('status', None) != '':
#         status = Option.objects.get(id=INFO.get('status', None))
#         result = result.filter(status=status)

#     if INFO.get('budget_type', None) and INFO.get('budget_type', None) != '':
#         budget_type = Option.objects.get(id=INFO.get('budget_type', None))
#         result = result.filter(budget_type=budget_type)

#     if INFO.get('place', None) and INFO.get('place', None) != '':
#         result = result.filter(place=INFO.get('place', None))

#     if INFO.get('port', None) and INFO.get('port', None) != '':
#         fp_projects = [p.project for p in Project_Port.objects.filter(port__id = INFO.get('port', None))]
#         temp = []
#         for i in result:
#             if i in fp_projects:
#                 temp.append(i)
#         result = temp

#     projects = list(result)
#     result_num = len(result)

#     return projects, result_num

# from engphoto.models import Photo
# @checkAuthority
# def uploadPhoto(R, project, right_type_value=u'觀看管考系統資料', **kw):

#     user, DATA = R.user, readDATA(R)
#     if _ca(user=user, project='', project_id=0, right_type_value=u'填寫管考系統資料'):
#         edit = True
#     else:
#         edit = False

#     file = R.FILES.get('file', None)
#     if file:
#         if ProjectPhoto.objects.filter(project=project):
#             insert_place = list(ProjectPhoto.objects.filter(project=project))[-1].id
#         else:
#             insert_place = 'start'
#         row = ProjectPhoto(
#                             project = project,
#                             name = R.GET['name'],
#                             memo = R.GET['memo'],
#                             uploadtime = NOW(),
#                             )
#         try:
#             row.extension = Option.objects.get(swarm='extensiontype', value=(file.name.split('.')[-1]).upper())
#         except:
#             row.extension = Option.objects.get(swarm='extensiontype', value='JPG')
#         row.save()
#         getattr(row, 'file').save('%s.%s'%(row.id, row.extension.value), file)
#         row.save()

#         count = len(ProjectPhoto.objects.filter(project=project))
#         INFO = {
#                 'id': row.id,
#                 'url': row.rUrl(),
#                 'project_id': row.project.id,
#                 'name': row.name,
#                 'memo': row.memo,
#                 'uploadtime': str(row.uploadtime).split('.')[0],
#                 'extension': str(row.extension.value),
#                 }

#         return HttpResponse(json.write({'status': True, 'insert_place': insert_place,
#                                         'count': count, 'INFO': INFO}))

#     if user.user_profile.group.name == '上層管理者':
#         can_see_photo = True
#     else:
#         can_see_photo = False
#     try:
#         FRCMUserGroup.objects.get(user=user,project=project)
#         can_see_photo = True
#     except:
#         pass

#     if FRCMUserGroup.objects.filter(project=project): in_frcm = True
#     else: in_frcm = False
#     frcm_photo_num = len(Photo.objects.filter(project=project, phototype__value='正常').exclude(file=''))

#     photos = ProjectPhoto.objects.filter(project=project).order_by('id')
#     t = get_template(os.path.join('project', 'photo.html'))
#     html = t.render(RequestContext(R,{
#                                     'edit': edit,
#                                     'target_project': project,
#                                     'photos': photos,
#                                     'in_frcm': in_frcm,
#                                     'page':'rePhoto',
#                                     'can_see_photo': can_see_photo,
#                                     'frcm_photo_num': frcm_photo_num,
#                                     }))
#     return HttpResponse(html)


# @login_required
# @checkAuthority
# def recoverProject(R, project, right_type_value=u'刪除管考工程案'):
#     projects = Project.objects.all().exclude(deleter=None).order_by('-id')

#     t = get_template(os.path.join('project', 'recoverproject.html'))
#     html = t.render(RequestContext(R,{
#         'projects': projects,
#         }))
#     return HttpResponse(html)

# from settings import CHINESE_FONT_FILE
# from cStringIO import StringIO
# import matplotlib
# import pylab
# #matplotlib.use('Agg')
# import matplotlib.pyplot as plt
# CHINESE_FONT = matplotlib.font_manager.FontProperties(fname=CHINESE_FONT_FILE)
# import numpy

# def makeCharts(R, chart_cache_name='', right_type_value=''):
#     t = get_template(os.path.join('project', 'makecharts.html'))
#     html = t.render(RequestContext(R, {'chart_cache_name': chart_cache_name}))
#     return HttpResponse(html)

# def _convert_float(v):
#     try: float(v)
#     except: return None
#     else: return True

# def makeBar(R, chart_cache_name='', right_type_value=''):
#     chart_dictionary = cache.get(chart_cache_name)
#     title = chart_dictionary.get('title', '')
#     names = chart_dictionary.get('names', '')
#     values = chart_dictionary.get('values', '')
#     values_len = len(values)
#     new_values = []
#     for i, name in enumerate(names):
#         if i < values_len:
#             try: new_values.append(float(values[i]))
#             except: new_values.append(0)

#     fig = plt.figure(figsize=(9,7))
#     ax1 = fig.add_subplot(111)
#     plt.subplots_adjust(left=0.4, right=0.88)
#     pos = numpy.arange(len(names))+0.5    #Center bars on the Y-axis ticks
#     rects = ax1.barh(pos, new_values, align='center', height=0.5, color='m')

#     #ax1.axis([0,100,0,5])
#     pylab.yticks(pos, names, fontproperties=CHINESE_FONT)
#     ax1.set_title(title, fontproperties=CHINESE_FONT)

#     imdata=StringIO()
#     fig.savefig(imdata,format='png')

#     return HttpResponse(imdata.getvalue(), content_type='image/png')

# def makePie(R, chart_cache_name='', right_type_value=''):
#     chart_dictionary = cache.get(chart_cache_name)
#     if not chart_dictionary:
#         #資料已被洗掉，要重新執行 /project/makestatistics/select_year:98/type_id:1/select_unit:0/select_undertake_type:0/select_fishingport:0/ 網址
#         #最好的方法，是讓整理 plans 資訊的程式變成 calculatePlan 函式，當 chart_dictionary == None 時，
#         #再執行一次 calculatePlan 函式即可。
#         raise ValueError
#     title = chart_dictionary.get('title', '')
#     names = chart_dictionary.get('names', '')
#     values = chart_dictionary.get('values', '')
#     new_names = []
#     new_values = []
#     for i, value in enumerate(values):
#         if value > 0:
#             new_names.append(unicode(names[i]))
#             new_values.append(values[i])

#     if not new_values:
#         file = open(os.path.join(ROOT, 'apps', 'project', 'static', 'project', 'image', 'no_pic.png'), 'b')
#         return HttpResponse(file.read(), content_type='image/png')

#     explode = [0, ] * len(new_values)
#     explode[0] = 0.05

#     fig = plt.figure(figsize=(8, 8))
#     fig.subplotpars.update(left=0.3, right=0.8)

#     ax = fig.add_subplot(111)
#     p_set, t_set, a_set = ax.pie(new_values, explode=explode, labels=new_names, autopct='%1.1f%%', shadow=True)
#     for t in t_set: t.set_font_properties(CHINESE_FONT)
#     ax.set_title(title, fontproperties=CHINESE_FONT)

#     imdata=StringIO()
#     fig.savefig(imdata,format='png')

#     return HttpResponse(imdata.getvalue(), content_type='image/png')

# def makePlot(R, chart_cache_name, right_type_value):
#     chart_dictionary = cache.get(chart_cache_name)
#     title = chart_dictionary.get('title', '')
#     names = chart_dictionary.get('names', '')
#     values = chart_dictionary.get('values', '')
#     values_len = len(values)
#     new_values = []
#     for i, name in enumerate(names):
#         if i < values_len:
#             try: new_values.append(float(values[i]))
#             except: new_values.append(0)

#     pos = numpy.arange(len(new_values))

#     fig = plt.figure()
#     ax = fig.add_subplot(111)
#     pic = ax.plot(pos, new_values, "or-")
#     fig.subplots_adjust(bottom=0.7)

#     ax.set_title(title, fontproperties=CHINESE_FONT)
#     pylab.xticks(pos, names, rotation=270, fontproperties=CHINESE_FONT)

#     imdata=StringIO()
#     fig.savefig(imdata,format='png')

#     return HttpResponse(imdata.getvalue(), content_type='image/png')

# if __name__ == '__main__':
#     myfont = matplotlib.font_manager.FontProperties(fname='apps/project/bkai00mp.ttf')

#     title = u'秀中文標題'
#     names = [u'A中濁', 'B1', 'C2']
#     values = [10, 30, 40]
#     new_names = []
#     new_values = []
#     for i, value in enumerate(values):
#         if value > 0:
#             new_names.append(unicode(names[i]))
#             new_values.append(values[i])

#     explode = [0, ] * len(new_values)
#     explode[0] = 0.05

#     fig = plt.figure(figsize=(8, 8))

#     ax = fig.add_subplot(111)
#     p, t, a = ax.pie(new_values, explode=explode, labels=new_names, autopct='%1.1f%%', shadow=True)
#     t[0].set_font_properties(myfont)
#     ax.set_title(title, fontproperties=myfont)

#     fig.savefig('pie.png',format='png')


# @checkAuthority
# def makeProjectSerial(R, project, right_type_value=u'觀看管考系統資料'):
#     class searchForm(forms.Form):
#         bid_no = forms.CharField(label='標案編號：', required=False)
#         name = forms.CharField(label='工作名稱：', required=False)
#         vouch_no = forms.CharField(label='發文(核定)文號：', required=False)
#         plans = [('', '全部')]
#         for i in Plan.objects.filter(uplevel=None):
#             plans.append((i.id, '---'*i.rLevelNumber() + i.name))
#             for j in i.rSubPlanInList():
#                 plans.append((j.id, '---'*j.rLevelNumber() + j.name))
#         plan = forms.ChoiceField(choices=plans, required=False, label='所屬計畫：')
#         project_sub_types = [('1', '含下層計畫'), ('0', '不含下層計畫')]
#         project_sub_type = forms.ChoiceField(choices=project_sub_types, required=False, label='　　層級：')
#         years = [(y-1911, y-1911) for y in xrange(2006, TODAY.year+2)]
#         years.insert(0, ('', '所有年度'))
#         years.reverse()
#         year = forms.ChoiceField(choices=years, required=False, label='年度：')
#         units = [('', '全部')]
#         for i in Unit.fish_city_menu.all():
#             units.append((i.id, i.name))
#             if i.uplevel and i.uplevel.name != '縣市政府':
#                 units.extend(
#                     [(j.id, '---'+j.name) for j in i.uplevel_subunit.all()]
#                 )
#         unit = forms.ChoiceField(choices=units, required=False, label='執行機關：')
# #        statuss = [('', '全部')]
# #        statuss += [[i.id, i.value] for i in _getProjectStatusInList()]
# #        status = forms.ChoiceField(choices=statuss, required=False, label='工程狀態：')
#         progress_state = [('', '全部'), ('g', '大於'), ('e', '等於'), ('s', '小於'), ('b', '落後')]
#         progress = forms.ChoiceField(choices=progress_state, required=False, label='進度搜尋：')
#         progress_value = forms.CharField(label='', required=False)


#     user, DATA = R.user, readDATA(R)

#     default_projects = [p.project for p in DefaultProject.objects.filter(user=user)]

#     form = searchForm()
#     projects_num = -1
#     projects = []
#     querystring = ''
#     INFO = {}
#     for k, v in R.GET.items(): INFO[k] = v
#     for k, v in R.POST.items(): INFO[k] = v

#     if INFO.get('submit', None):
#         form = searchForm(INFO)
#         querystring = '&'.join(['%s=%s'%(k, v) for k, v in INFO.items() if k != 'page'])
#         projects, projects_num, p_list = _searchProject(INFO)

#         for i in projects: i.serial = str(i.plan.no) + '-' + str(i.id)

#     elif INFO.get('makeExcel', None):
#         form = searchForm(INFO)
#         querystring = '&'.join(['%s=%s'%(k, v) for k, v in INFO.items() if k != 'page'])
#         projects = _searchProjectForExport(INFO)

#         result = _makeDownloadFile_ProjectSerial(projects=projects)
#         template_name = 'project_serial.xls'
#         content = makeFileByWordExcel(template_name=template_name, result=result)
#         response = HttpResponse(content_type='application/xls')
#         response['Content-Type'] = ('application/xls')
#         response['Content-Disposition'] = ('attachment; filename=%s.xls' % ('編碼對照表')).encode('cp950')
#         response.write(content)
#         return response

#     t = get_template(os.path.join('project', 'makeserial.html'))
#     html = t.render(RequestContext(R,{
#         'form':form,
#         'default_projects':default_projects,
#         'projects': projects,
#         'sortBy': INFO.get('sortBy', None) or 'year',
#         'page_list': makePageList(INFO.get('page', 1), projects_num, NUMPERPAGE),
#         'querystring': querystring,
#         'projects_num': projects_num,
#         'option' : _make_choose(),
#         }))
#     return HttpResponse(html)

# @checkAuthority
# def editProjectListBudget(R, project, right_type_value=u'填寫管考系統資料', **kw):
#     year = kw['year']
#     plan_id = kw['plan_id']
#     sub_plan = kw['sub_plan']
#     budget_sub_type = kw['budget_sub_type']
#     undertake_type = kw['undertake_type']
    
#     plan = Plan.objects.get(id=plan_id)
#     if sub_plan == '0':
#         sub_plan = '否'
#         plans = [plan]
#     else:
#         sub_plan = '是'
#         plans = [plan] + [p for p in plan.rSubPlanInList()]

#     project_budgets = [b.fund.project for b in Budget.objects.filter(fund__project__plan__in=plans, year=year, fund__project__deleter=None)]
#     funds = Fund.objects.filter(project__in=project_budgets, project__plan__in=plans).order_by('project__place', 'project__name')

#     if budget_sub_type != '0':
#         funds = funds.filter(project__budget_sub_type__id=budget_sub_type)
#         budget_sub_type = Option.objects.get(id=budget_sub_type).value
#     else:
#         budget_sub_type = '全部'
#     if undertake_type != '0':
#         funds = funds.filter(project__undertake_type__id=undertake_type)
#         undertake_type = Option.objects.get(id=undertake_type).value
#     else:
#         undertake_type = '全部'

#     for f in funds:
#         f.budget = Budget.objects.get(fund=f, year=year)
#         f.budget.TotalAppropriatebyThisYear = f.budget.rTotalAppropriatebyLastYear(year=year)
#         f.budget.ShouldPayThisYear = f.budget.rShouldPayThisYear(year=year)
#         f.budget.TotalAppropriatebyThisYear = f.budget.rTotalAppropriatebyThisYear(year=year)
#         f.budget.TotalProjectNotPayThisYear = f.budget.rTotalProjectNotPayThisYear(year=year)

#     t = get_template(os.path.join('project', 'editprojectlistbudget.html'))
#     html = t.render(RequestContext(R,{
#         'funds': funds,
#         'num': len(funds),
#         'year': year,
#         'plan': plan,
#         'sub_plan': sub_plan,
#         'budget_sub_type': budget_sub_type,
#         'undertake_type': undertake_type,
#         }))
#     return HttpResponse(html)


# def _searchProjectForExport(INFO):
#     result = Project.objects.filter(deleter=None).order_by(INFO.get('sortBy', None))
#     if INFO.get('bid_no', None) and INFO.get('bid_no', None) != '':
#         ids = []
#         for bid_no in re.split('[ ,]+', INFO.get('bid_no', None)):
#             ids.extend([i.id for i in result.filter(bid_no__icontains=bid_no)])
#         result = result.filter(id__in=ids)

#     if INFO.get('vouch_no', None) and INFO.get('vouch_no', None) != '':
#         ids = []
#         for vouch_no in re.split('[ ,]+', INFO.get('vouch_no', None)):
#             ids.extend([i.id for i in result.filter(vouch_no__icontains=vouch_no)])
#         result = result.filter(id__in=ids)

#     if INFO.get('name', None) and INFO.get('name', None) != '':
#         ids = []
#         for name in re.split('[ ,]+', INFO.get('name', None)):
#             ids.extend([i.id for i in result.filter(name__icontains=name)])
#         result = result.filter(id__in=ids)

#     if INFO.get('plan', None) and INFO.get('plan', None) != '':
#         plan = Plan.objects.get(id=INFO.get('plan', None))
#         if INFO.get('project_sub_type', None) == '1':
#             plan_ids = [plan.id] + [i.id for i in Plan.objects.get(id=INFO.get('plan', None)).rSubPlanInList()]
#             result = result.filter(plan__id__in=plan_ids)
#         else:
#             result = result.filter(plan = plan)

#     if INFO.get('year', None) and INFO.get('year', None) != '':
#         result = result.filter(year=INFO.get('year', None))

#     if INFO.get('unit', None) and INFO.get('unit', None) != '':
#         unit = Unit.objects.get(id=INFO.get('unit', None))
#         result = result.filter(unit=unit)

# #    if INFO.get('status', None) and INFO.get('status', None) != '':
# #        status = Option.objects.get(id=INFO.get('status', None))
# #        result = result.filter(status=status)

#     if INFO.get('progress', None) and INFO.get('progress', None) != '':
#         try:
#             value = float(INFO.get('progress_value', None))
#             value_state = True
#         except:
#             value_state = False
#         if value_state:
#             temp = []
#             if INFO.get('progress', None) == 'g':
#                 for p in result:
#                     if p.getProgressPercent() > value:
#                         temp.append(p)
#             elif INFO.get('progress', None) == 'e':
#                 for p in result:
#                     if p.getProgressPercent() == value:
#                         temp.append(p)
#             elif INFO.get('progress', None) == 's':
#                 for p in result:
#                     if p.getProgressPercent() <= value:
#                         temp.append(p)
#             elif INFO.get('progress', None) == 'b':
#                 for p in result:
#                     if (p.getProgressPercent(datetime.date.today(), 'schedul') - p.getProgressPercent()) >= value:
#                         temp.append(p)
#             result = temp[:]
#     return result


# def rJSON(R, right_type_value=u'Ajax Request'):
#     submit = R.GET.get('submit', '')
#     html = False
#     if not submit: submit = R.POST.get('submit', '')
#     if 'rProjectsByUser' == submit:
#         result = rSelfProjects(R)
#     elif 'rProjectsInRecordProjectProfile' == submit:
#         result = rProjectsInRecordProjectProfile(R)
#     elif 'recordProjects' == submit:
#         result = recordProjects(R)
#     elif 'recordAllProjects' == submit:
#         result = recordAllProjects(R)
#     elif 'deleteExportCustomReport' == submit:
#         result = deleteExportCustomReport(R)
#     elif 'addOrRemoveFieldFromExportCustomReport' == submit:
#         result = addOrRemoveFieldFromExportCustomReport(R)
#     elif 'uExportCustomReportFieldPriority' == submit:
#         result = uExportCustomReportFieldPriority(R)
#     elif 'cExportCustomReport' == submit:
#         result = cExportCustomReport(R)
#     elif 'rReportFields' == submit:
#         result = rReportFields(R)
#     elif 'cRecordProjectProfile' == submit:
#         result = cRecordProjectProfile(R)
#     elif 'syncPCCData' == submit:
#         result = syncPCCData(R)
#     elif 'uProgress' == submit:
#         result = uProgress(R)
#     elif 'rPCCProgress' == submit:
#         result = rPCCProgress(R)
#     elif 'syncProgress' == submit:
#         result = syncProgress(R)
#     elif 'dProgress' == submit:
#         result = dProgress(R)
#     elif 'uFund' == submit:
#         result = uFund(R)
#     elif 'uBudget' == submit:
#         result = uBudget(R)
#     elif 'uFundRecord' == submit:
#         result = uFundRecord(R)
#     elif 'cAppropriate' == submit:
#         result = cAppropriate(R)
#     elif 'addAllocation' == submit:
#         result = addAllocation(R)
#     elif 'uAppropriate' == submit:
#         result = uAppropriate(R)
#     elif 'uAllocation' == submit:
#         result = uAllocation(R)
#     elif 'dAppropriate' == submit:
#         result = dAppropriate(R)
#     elif 'deleteProjectAllocation' == submit:
#         result = deleteProjectAllocation(R)
#     elif 'dProjectFundRecord' == submit:
#         result = dProjectFundRecord(R)
#     elif 'rPCCFundRecord' == submit:
#         result = rPCCFundRecord(R)
#     elif 'syncFundRecord' == submit:
#         result = syncFundRecord(R)
#     elif 'rFundingDetail' == submit:
#         result = rFundingDetail(R)
#     elif 'runReserveProject' == submit:
#         result = runReserveProject(R)
#     elif 'dReserve' == submit:
#         result = dReserve(R)
#     elif 'uBidinfo' == submit:
#         result = uBidinfo(R)
#     elif 'uReserveInfo' == submit:
#         result = uReserveInfo(R)
#     elif 'rPCCProject' == submit:
#         result = rPCCProject(R)
#     elif 'getSubLocation' == submit:
#         result = getSubLocation(R)
#     elif 'cProject' == submit:
#         result = cProject(R)
#     elif 'dSubLocation' == submit:
#         result = dSubLocation(R)
#     elif 'rAccoutingData' == submit:
#         result = rAccoutingData(R)
#     elif 'syncAccoutingData' == submit:
#         result = syncAccoutingData(R)
#     elif 'syncPCCProjectData' == submit:
#         result = syncPCCProjectData(R)
#     elif 'BatchEdit_Plan' == submit:
#         result = batchEdit_Plan(R)
#     elif 'deletePlan' == submit:
#         result = deletePlan(R)
#     elif 'getPlanListInTable' == submit:
#         result = getPlanListInTable(R)
#     elif 'updatePlanSort' == submit:
#         result = updatePlanSort(R)
#     elif 'updatePlanInfo' == submit:
#         result = updatePlanInfo(R)
#     elif 'addPlan' == submit:
#         result = addPlan(R)
#     elif 'addPlanBudget' == submit:
#         result = addPlanBudget(R)
#     elif 'deletePlanBudget' == submit:
#         result = deletePlanBudget(R)
#     elif 'updateAutoSum' == submit:
#         result = updateAutoSum(R)
#     elif 'get_editProjectListBudget_Option' == submit:
#         result = get_editProjectListBudget_Option(R)
#     elif 'updateBudgetInfo' == submit:
#         result = updateBudgetInfo(R)
#     elif 'setChaseProject' == submit:
#         result = setChaseProject(R)
#     elif 'addNewChase' == submit:
#         result = addNewChase(R)
#     elif 'ShowChaseProject' == submit:
#         result = ShowChaseProject(R)
#     elif 'deleteLastChase' == submit:
#         result = deleteLastChase(R)
#     elif 'updateChartNewUpdateInfo' == submit:
#         result = updateChartNewUpdateInfo(R)
#     elif 'setCheckForClose' == submit:
#         result = setCheckForClose(R)
#     elif 'setFalseForClose' == submit:
#         result = setFalseForClose(R)
#     elif 'setCheckForComplete' == submit:
#         result = setCheckForComplete(R)
#     elif 'setFalseForComplete' == submit:
#         result = setFalseForComplete(R)
#     elif 'updateChartNewUpdateInfoDialog' == submit:
#         result = updateChartNewUpdateInfoDialog(R)
#     elif 'updateChaseInfo' == submit:
#         result = updateChaseInfo(R)
#     elif 'updateMemoInfo' == submit:
#         result = updateMemoInfo(R)
#     elif 'makeNewFileTr' == submit:
#         result = makeNewFileTr(R)
#     elif 'deleteDocumentFile' == submit:
#         result = deleteDocumentFile(R)
#     elif 'updateFileInfo' == submit:
#         result = updateFileInfo(R)
#     elif 'CencelLoginEmail' == submit:
#         result = UpdateCencelLoginEmail(R)
#     elif 'add_Draft_Project' == submit:
#         result = add_Draft_Project(R)
#     elif 'Search_Project_Name_Button' == submit:
#         result = Search_Project_Name_Button(R)
#     elif 'delete_Draft_Project' == submit:
#         result = delete_Draft_Project(R)
#     elif 'edit_Draft_Project' == submit:
#         result = edit_Draft_Project(R)
#     elif 'update_type_Draft_Project' == submit:
#         result = update_type_Draft_Project(R)

#     else:
#         result = {'status': False, 'message': u'未指定方法'}

#     if html: return HttpResponse(result)
#     else: return HttpResponse(json.write(result))

# def update_type_Draft_Project(R):
#     project = Draft_Project.objects.get(id=R.POST.get('project_id'))
#     project.type = Option.objects.get(swarm='draft_type', value='漁業署草稿')
#     project.save()
#     return {'status': True}

# def edit_Draft_Project(R):
#     project = Draft_Project.objects.get(id=R.POST.get('project_id'))
#     data = []
#     for field_name in project._meta.get_all_field_names():
#         if field_name == 'sort':
#             data.append(['sort', project.get_sort_num()])
#         elif field_name != 'fishing_port' and field_name != 'aquaculture':
#             try:
#                 #為了連外鍵所用的欄位
#                 data.append([field_name, getattr(project, field_name).id])
#             except:
#                 try:
#                     #數字欄位
#                     data.append([field_name, float(str(getattr(project, field_name)))])
#                 except:
#                     #正常欄位
#                     data.append([field_name, getattr(project, field_name)])
#     data.append(['project_id', project.id])

#     exproject = []
#     if project.project:
#         exproject = [project.project.id, (str(project.project.year) + ':' + project.project.name)]

#     port_list = []
#     port_html = ''
#     if project.project_type.value == '1 漁港工程':
#         for p in project.fishing_port.all():
#             port_list.append(p.id)
#             port_html += '<select id="FishingPort" class="sub_location setCoord"><option value="" twdx="" twdy="">請選擇</option>'
#             port_html += '<option selected="selected" value="'+str(p.id)+'" twdx="" twdy="">'+p.name+'</option></select><br>'

#     else:
#         for p in project.aquaculture.all():
#             port_list.append(p.id)
#             port_html += '<select id="FishingPort" class="sub_location setCoord"><option value="" twdx="" twdy="">請選擇</option>'
#             port_html += '<option selected="selected" value="'+str(p.id)+'" twdx="" twdy="">'+p.name+'</option></select><br>'
#     port_html += '<span id="insertSubLocation"></span>'

#     html_sort = '<option value="last" name="{{ forloop.counter }}">(放置於最後位置)</option>'
#     for i in Draft_Project.objects.filter(place=project.place).order_by('sort'):
#         if i.get_sort_num() == project.get_sort_num():
#             html_sort += '<option value="' + str(i.get_sort_num()) + '" selected>' + str(i.get_sort_num()) + ' (取代 ' + str(i.name) + ' 順序)</option>'
#         else:
#             html_sort += '<option value="' + str(i.get_sort_num()) + '">' + str(i.get_sort_num()) + ' (取代 ' + str(i.name) + ' 順序)</option>'

#     return {'status': True, 'data': data, 'exproject': exproject, 'port_list': port_list, 'port_html': port_html, 'project_id': project.id, 'html_sort': html_sort}


# def delete_Draft_Project(R):
#     project = Draft_Project.objects.get(id=R.POST.get('project_id'))
#     if project.type.value == '縣市提案草稿':
#         project.delete()
#         msg = '刪除成功!'
#     elif project.type.value == '漁業署草稿':
#         project.type = Option.objects.get(swarm='draft_type', value='縣市提案草稿')
#         project.save()
#         msg = '已退回"縣市提案草稿"!'
#     return {'status': True, 'msg': msg}

# def Search_Project_Name_Button(R):
#     DATA = R.POST
#     projects = Project.objects.all().order_by('name')
#     ids = []
#     for name in re.split('[ ,]+', DATA.get('name', None)):
#         ids.extend([i.id for i in projects.filter(name__icontains=name)])
#     projects = projects.filter(id__in=ids)

#     html = ''
#     for i in projects:
#         html += '<option value="' + str(i.id) + '">'+ str(i.year) +'年：'+ i.name + '</option>'

#     return {'status': True, 'html': html}


# def add_Draft_Project(R):
#     DATA = R.POST
#     sort = DATA.get('sort', None)
#     if sort == 'last':
#         all_sort_num = [i.sort for i in Draft_Project.objects.filter(
#                 place=Place.objects.get(id=DATA.get('place_id', None))
#             )
#         ]
#         sort = max(all_sort_num) + 1
#     else:
#         draft_p_s = Draft_Project.objects.filter(place=Place.objects.get(id=DATA.get('place_id', None))).order_by('sort')[int(sort)-1:]
#         try:
#             sort = draft_p_s[int(sort)-1].sort
#         except:
#             sort = 1
#         for i in draft_p_s:
#             i.sort += 1
#             i.save()


#     if DATA.get('action', None) == 'update':
#         row = Draft_Project.objects.get(id=DATA.get('del_project_id', None))
#         row.delete()

#     NewProject = Draft_Project(
#         year = DATA.get('year', None),
#         name = DATA.get('name', None),
#         capital_ratify_budget = DATA.get('capital_ratify_budget', 0) or 0,
#         self_money = DATA.get('self_money', 0) or 0,
#         local_money = DATA.get('local_money', 0) or 0,
#         project_type = Option.objects.get(id=DATA.get('project_type', None)),
#         project_sub_type = Option.objects.get(id=DATA.get('project_sub_type', None)),
#         place = Place.objects.get(id=DATA.get('place_id', None)),
#         purchase_type = Option.objects.get(id=DATA.get('purchase_type_id', None)),
#         undertake_type = Option.objects.get(id=DATA.get('undertake_type_id', None)),
#         budget_sub_type = Option.objects.get(id=DATA.get('budget_sub_type_id', None)),
#         unit = Unit.objects.get(id=DATA.get('unit_id', None)),
#         info = DATA.get('info', None),
#         review_results = DATA.get('review_results', None),
#         design = DATA.get('design', None),
#         fish_boat = DATA.get('fish_boat', None),
#         real_fish_boat = DATA.get('real_fish_boat', None),
#         other_memo = DATA.get('other_memo', None),
#         fect = DATA.get('fect', None),
#         memo = DATA.get('memo', None),
#         type = Option.objects.get(swarm='draft_type', value=DATA.get('type', None)),
#         sort = sort,
#     )
#     try: NewProject.plan = Plan.objects.get(id=DATA.get('plan_id', None))
#     except: pass
#     try: NewProject.project = Project.objects.get(id=DATA.get('project_id', None))
#     except: pass
#     NewProject.save()
#     sub_location = ['', ] + DATA.get('sub_location', None).split(',')[:-1]
#     if DATA.get('project_type', None) == '227':
#         for i in range(1, len(sub_location)):
#             if sub_location[i] != '' and sub_location[i] != sub_location[i-1]:
#                 NewProject.fishing_port.add(FishingPort.objects.get(id=sub_location[i]))
#     elif DATA.get('project_type', None) == '228':
#         for i in range(1, len(sub_location)):
#             if sub_location[i] != '' and sub_location[i] != sub_location[i-1]:
#                 NewProject.aquaculture.add(Aquaculture.objects.get(id=sub_location[i]))
    
#     return {'status': True, 'new_draft_id': str(NewProject.id)}


# def UpdateCencelLoginEmail(R):
#     value = R.POST.get('value', None)
#     if '取消' == value:
#         row = CencelLoginEmail(user = R.user)
#         row.save()
#         return_value = '啟用'
#         msg = '您的通知已取消'
#     else:
#         row = CencelLoginEmail.objects.get(user = R.user)
#         row.delete()
#         return_value = '取消'
#         msg = '您的通知已啟用'

#     return {'status': True, 'msg': msg,'return_value': return_value}


# def updateFileInfo(R):
#     table_name = R.POST.get('table_name', None)
#     row_id = R.POST.get('row_id', None)
#     field_name = R.POST.get('field_name', None)
#     field_value = R.POST.get('value', None)
#     return_value = field_value
#     row = DocumentFile.objects.get(id=row_id)
#     if field_value == '': field_value = None
    
#     setattr(row, field_name, field_value)
#     row.save()

#     return {'status': True, 'return_value': return_value}

# def deleteDocumentFile(R):
#     row_id = R.POST.get('row_id', None)
#     row = DocumentFile.objects.get(id=row_id)
#     row.file.delete()
#     row.delete()
#     return {'status': True}

# def updateMemoInfo(R):
#     table_name = R.POST.get('table_name', None)
#     project_id = R.POST.get('project_id', None)
#     field_name = R.POST.get('field_name', None)
#     field_value = R.POST.get('value', None)
#     return_value = field_value
    
#     try:
#         row = Project_Secret_Memo.objects.get(project__id=project_id)
#     except:
#         row = Project_Secret_Memo(
#             project = Project.objects.get(id=project_id),
#         )
#         row.save()

#     setattr(row, 'date', TODAY())
#     setattr(row, field_name, field_value)
#     row.save()

#     return {'status': True, 'return_value': return_value}


# def updateChaseInfo(R):
#     table_name = R.POST.get('table_name', None)
#     chase_id = R.POST.get('chase_id', None)
#     field_name = R.POST.get('field_name', None)
#     field_value = R.POST.get('value', None)

#     return_value = field_value
#     countychasetime = list(CountyChaseTime.objects.all().order_by('id'))[-1]


#     if table_name == 'CountyChaseProjectOneToMany':
#         row = CountyChaseProjectOneToMany.objects.get(id=chase_id)
#         if row.complete:
#             if not countychasetime.new_update: countychasetime.new_update = ''
#             countychasetime.new_update += str(row.project.id)+'---'+ str(field_name) + '---' + str(field_value) + '@!*#'
#     elif table_name == 'CountyChaseProjectOneByOne':
#         try:
#             row = CountyChaseProjectOneByOne.objects.get(id=chase_id)
#             if CountyChaseProjectOneToMany.objects.get(countychasetime=countychasetime, project=row.project).complete:
#                 if not countychasetime.new_update: countychasetime.new_update = ''
#                 countychasetime.new_update += str(row.project.id)+'---'+ str(field_name) + '---' + str(field_value) + '@!*#'
#         except: pass
#     countychasetime.save()
#     if table_name == 'CountyChaseProjectOneToMany' and field_name != 'memo':
#         if field_value == '': field_value = 0
#         field_value = decimal.Decimal(str(round(float(field_value), 3)))
#         return_value = str(int(field_value))
#     elif table_name == 'CountyChaseProjectOneByOne':
#         if field_value == '': field_value = None

#     setattr(row, field_name, field_value)
#     row.save()

#     return {'status': True, 'return_value': return_value}


# def updateChartNewUpdateInfoDialog(R):
#     update = list(CountyChaseTime.objects.all().order_by('id'))[-1].new_update.split('@!*#')[:-1]
#     heads = {
#             'schedul_progress_percent': '預計進度百分比(%)',
#             'actual_progress_percent': '實際進度百分比(%)',
#             'self_payout': '本署實支數(元)',
#             'local_payout': '地方實支數(元)',
#             'self_unpay': '本署應付未付數(元)',
#             'local_unpay': '地方應付未付數(元)',
#             'self_surplus': '本署賸餘款(元)',
#             'local_surplus': '地方賸餘款(元)',
#             'memo': '計畫執行情形說明',
# #            'Scheduled_internet_services': '勞務上網，預計日期',
# #            'Scheduled_planning_and_Design': '規劃設計，預計日期',
# #            'Scheduled_chart_review': '書圖審查，預計日期',
# #            'Scheduled_internet_engineering': '工程上網，預計日期',
# #            'Scheduled_engineering_contract': '工程訂約，預計日期',
# #            'Scheduled_suspended': '工程勞務停工，預計日期',
# #            'Scheduled_performance': '工程勞務履約，預計日期',
# #            'Scheduled_complete': '工程勞務完成，預計日期',
# #            'Actual_internet_services': '勞務上網，實際日期',
# #            'Actual_planning_and_Design': '規劃設計，實際日期',
# #            'Actual_chart_review': '書圖審查，實際日期',
# #            'Actual_internet_engineering': '工程上網，實際日期',
# #            'Actual_engineering_contract': '工程訂約，實際日期',
# #            'Actual_suspended': '工程勞務停工，實際日期',
# #            'Actual_performance': '工程勞務履約，實際日期',
# #            'Actual_complete': '工程勞務完成，實際日期',
#             }

#     data = []
#     for i in update:
#         row = i.split('---')
#         project = Project.objects.get(id=row[0])
#         try: data.append([project, heads[row[1]], row[2]])
#         except: pass

#     t = get_template(os.path.join('project', 'make_dialog_new_update.html'))
#     html = t.render(RequestContext(R,{
#         'data': data,
#         }))
#     return {'html': html}

# def deleteExportCustomReport(R):
#     export_custom_report_id = R.POST.get('export_custom_report_id', None)
#     report = ExportCustomReport.objects.get(id=export_custom_report_id)
#     report.delete()
#     return {'status': True}

# def setCheckForClose(R):
#     chase = CountyChaseProjectOneToMany.objects.get(id=R.POST.get('chase_id', None)).getOneByOne()
#     if chase.check:
#         chase.check = False
#         msg = '點擊確定'
#     else:
#         chase.check = True
#         msg = '已確定'
#     chase.save()

#     return {'status': True, 'msg': msg}


# def setFalseForClose(R):
#     chase = CountyChaseProjectOneToMany.objects.get(id=R.POST.get('chase_id', None)).getOneByOne()
#     chase.close = False
#     chase.save()
#     return {'status': True}


# def setCheckForComplete(R):
#     chase = CountyChaseProjectOneToMany.objects.get(id=R.POST.get('chase_id', None))
#     if chase.check:
#         chase.check = False
#         msg = '點擊確定'
#     else:
#         chase.check = True
#         msg = '已確定'
#     chase.save()

#     return {'status': True, 'msg': msg}


# def setFalseForComplete(R):
#     chase = CountyChaseProjectOneToMany.objects.get(id=R.POST.get('chase_id', None))
#     chase.complete = False
#     chase.save()

#     return {'status': True}

# def updateChartNewUpdateInfo(R):
#     countychasetime = list(CountyChaseTime.objects.all().order_by('id'))[-1]
#     countychasetime.new_update = ''
#     countychasetime.save()
#     return {'status': True}


# def deleteLastChase(R):
#     countychasetime = list(CountyChaseTime.objects.all().order_by('id'))[-1]
#     countychasetime.delete()
#     return {'status': True}


# def ShowChaseProject(R):
#     place_id = R.POST.get('place_id', None)
#     type = R.POST.get('type', None)
#     countychasetime = list(CountyChaseTime.objects.all().order_by('id'))[-1]
#     projects = CountyChaseProjectOneToMany.objects.filter(countychasetime=countychasetime).order_by('project__place', 'project__year')
#     frcm_ids = []
#     for i in projects:
#         if FRCMUserGroup.objects.filter(project__id=i.project.id).count() != 0:
#             frcm_ids.append(i.project.id)

#     south_places = ['彰化縣', '雲林縣', '嘉義市', '嘉義縣', '臺南市', '高雄市', '屏東縣', '臺南市', '澎湖縣', '臺東縣']
#     if place_id == 'north':
#         projects = projects.filter(project__undertake_type__value='自辦').exclude(project__place__name__in=south_places)
#     elif place_id == 'south':
#         projects = projects.filter(project__undertake_type__value='自辦', project__place__name__in=south_places)
#     else:
#         projects = projects.filter(project__place__id=place_id).exclude(project__undertake_type__value='自辦')

#     if type == 'check':
#         projects = projects.filter(check=True)
#         for i in projects:
#             i.project.frcmuser = FRCMUserGroup.objects.get(project=i.project, group__name__in=['負責主辦工程師', '自辦主辦工程師']).user
#     elif type == 'not_check':
#         projects = projects.filter(check=False, project__id__in=frcm_ids)
#         for i in projects:
#             i.project.frcmuser = FRCMUserGroup.objects.get(project=i.project, group__name__in=['負責主辦工程師', '自辦主辦工程師']).user
#     elif type == 'not_in_frcm':
#         projects = projects.filter(complete=False).exclude(project__id__in=frcm_ids)
#         for i in projects:
#             i.project.frcmuser = ''
#     else:
#         for i in projects:
#             try:
#                 i.project.frcmuser = FRCMUserGroup.objects.get(project=i.project, group__name__in=['負責主辦工程師', '自辦主辦工程師']).user
#             except:
#                 i.project.frcmuser = ''

#     temp = []
#     users = []
#     for c_p in projects:
#         if c_p.project.frcmuser not in users:
#             users.append(c_p.project.frcmuser)

#     for u in users:
#         for c_p in projects:
#             if c_p.project.frcmuser == u:
#                 temp.append(c_p.project)

#     t = get_template(os.path.join('project', 'make_dialog_chaseproject.html'))
#     html = t.render(RequestContext(R,{
#         'projects': temp,
#         'project_num': projects.count(),
#         }))
#     return {'html': html}

# def addNewChase(R):
#     auto = R.POST.get('auto_import', None)
#     countychasetime = list(CountyChaseTime.objects.all().order_by('id'))[-1]
#     user = User.objects.get(id=R.POST.get('user_id', None))
#     row = CountyChaseTime(chase_date=TODAY(), new_update='', user=user)
#     row.save()
#     if auto == 'True':
#         for c in CountyChaseProjectOneToMany.objects.filter(countychasetime=countychasetime):
#             new_chase = CountyChaseProjectOneToMany(
#                 countychasetime = row,
#                 project = c.project,
#             )
#             new_chase.save()

#     return {'status': True}

# def setChaseProject(R):
#     countychasetime = list(CountyChaseTime.objects.all().order_by('id'))[-1]
#     project = Project.objects.get(id=R.POST.get('project_id', None))
    
#     try:
#         row = CountyChaseProjectOneToMany.objects.get(countychasetime=countychasetime, project=project)
#         row.delete()
#     except:
#         row = CountyChaseProjectOneToMany(
#                                 countychasetime = countychasetime,
#                                 project = project,
#                                 )
#         row.save()
#         row.getOneByOne()
#     return {'status': True}

# def updateBudgetInfo(R):
#     field_name = R.POST.get('field_name', None)
#     field_value = R.POST.get('value', None)
#     row_id = R.POST.get('row_id', None)
#     table_name = R.POST.get('table_name', None)
#     input_type = R.POST.get('input_type', None)
#     year = R.POST.get('year', None)

#     return_value = field_value
#     if table_name == 'Fund': row = Fund.objects.get(id=row_id)
#     elif table_name == 'Budget': row = Budget.objects.get(id=row_id)
    
#     if input_type == 'float':
#         if field_value == '': field_value = 0
#         field_value = decimal.Decimal(str(round(float(field_value), 3)))
#         return_value = str(int(field_value))

#     setattr(row, field_name, field_value)
#     row.save()
#     manage = 0
#     if table_name == 'Fund' and field_name == 'contract':
#         value = float(field_value)
#         if value < 5000000: manage += value * 0.03
#         elif value >= 5000000: manage += 5000000 * 0.03
#         if value > 5000000 and value < 25000000: manage += (value-5000000) * 0.015
#         elif value >= 25000000: manage += (25000000-5000000) * 0.015
#         if value > 25000000 and value < 100000000: manage += (value-25000000) * 0.01
#         elif value >= 100000000: manage += (100000000-25000000) * 0.01
#         if value > 100000000 and value < 500000000: manage += (value-100000000) * 0.007
#         elif value >= 500000000:
#             manage += (500000000-100000000) * 0.007
#             manage += (value - 500000000) * 0.005
#         manage = int(manage+0.5)
#         manage = decimal.Decimal(str(round(float(manage), 3)))
#         setattr(row, 'manage', manage)
#         row.save()
#         manage = str(int(manage))

#     if table_name == 'Fund':
#         rTotalProjectBudget = row.rTotalProjectBudget()
#         b = Budget.objects.get(fund=row, year=year)
#         rTotalAppropriatebyLastYear = b.rTotalAppropriatebyLastYear(year=year)
#         rShouldPayThisYear = b.rShouldPayThisYear(year=year)
#         rTotalAppropriatebyThisYear = b.rTotalAppropriatebyThisYear(year=year)
#         rTotalProjectNotPayThisYear = b.rTotalProjectNotPayThisYear(year=year)
#     elif table_name == 'Budget':
#         rTotalProjectBudget = row.fund.rTotalProjectBudget()
#         rTotalAppropriatebyLastYear = row.rTotalAppropriatebyLastYear(year=year)
#         rShouldPayThisYear = row.rShouldPayThisYear(year=year)
#         rTotalAppropriatebyThisYear = row.rTotalAppropriatebyThisYear(year=year)
#         rTotalProjectNotPayThisYear = row.rTotalProjectNotPayThisYear(year=year)


#     return {'status': True, 'return_value': return_value, 'rTotalProjectBudget': rTotalProjectBudget,
#             'rTotalAppropriatebyLastYear': rTotalAppropriatebyLastYear, 'rShouldPayThisYear': rShouldPayThisYear,
#             'rTotalAppropriatebyThisYear': rTotalAppropriatebyThisYear, 'rTotalProjectNotPayThisYear': rTotalProjectNotPayThisYear,
#             'manage': manage,
#             }
    


# def get_editProjectListBudget_Option(R):
#     year = [y-1911 for y in xrange(2006, TODAY().year+2)]
#     budget_types = [['0', '全部']] + [[i.id, i.value] for i in Option.objects.filter(swarm='budget_type')]
#     budget_sub_types = [['0', '全部']] + [[i.id, i.value] for i in Option.objects.filter(swarm='budget_sub_type')]
#     undertake_types = [['0', '全部']] + [[i.id, i.value] for i in Option.objects.filter(swarm='undertake_type')]
#     plan_id = R.POST.get('plan_id', None)
#     t = get_template(os.path.join('project', 'make_dialog_editprojectlistbudget.html'))
#     html = t.render(RequestContext(R,{
#         'years': year,
#         'plan_id': plan_id,
#         'budget_types': budget_types,
#         'budget_sub_types': budget_sub_types,
#         'undertake_types': undertake_types,
#         'today_year': TODAY().year-1911,
#         }))
#     return {'html': html}

# def updateAutoSum(R):
#     plan = Plan.objects.get(id=int(R.POST.get('plan_id', None)))
#     if plan.auto_sum: plan.auto_sum = False
#     else: plan.auto_sum = True
#     plan.save()
#     return {'status': True}


# def deletePlanBudget(R):
#     budget = PlanBudget.objects.get(id=int(R.POST.get('plan_id', None)))
#     budget.delete()
#     return {'status': True}


# def addPlanBudget(R):
#     plan = Plan.objects.get(id=int(R.POST.get('plan_id', None)))
#     try: year = PlanBudget.objects.filter(plan=plan).order_by('-year')[0].year + 1
#     except: year = TODAY().year - 1911
#     row = PlanBudget(
#         plan = plan,
#         year = year,
#     )
#     row.save()
#     return {'status': True}


# def addPlan(R):
#     lv = R.POST.get('lv', None)
#     name = R.POST.get('name', None)
#     now_plan = Plan.objects.get(id=int(R.POST.get('plan_id', None)))
#     up_plan = now_plan.uplevel

#     num = 0
#     for i in Plan.objects.all():
#         if i.rLevelNumber() == now_plan.rLevelNumber():
#             if int(i.code) >= num:
#                 num = int(i.code)
#     new_code = '%03d' % (num+1)
    
#     if lv == 'equal':
#         try: up_sort_num = float(up_plan.rSubPlanInList()[-1].sort)
#         except: up_sort_num = float(up_plan.sort)
#         new_plan_uplevel = up_plan
#     else:
#         try: up_sort_num = float(now_plan.rSubPlanInList()[-1].sort)
#         except: up_sort_num = float(now_plan.sort)
#         new_plan_uplevel = now_plan
#     try: down_sort_num = float(Plan.objects.filter(sort__gt=decimal.Decimal(str(up_sort_num))).order_by('sort')[0].sort)
#     except: down_sort_num = 10000

#     sort = (up_sort_num + down_sort_num) / 2.

#     row = Plan(
#                 name = name,
#                 note = '',
#                 code = new_code,
#                 budget_type = Option.objects.get(swarm="budget_type", value='公務預算'),
#                 sort = decimal.Decimal(str(sort)),
#                 uplevel = new_plan_uplevel,
#                 )
#     row.save()

#     return {'status': True, 'new_plan_id': row.id}

# def updatePlanInfo(R):
#     field_name = R.POST.get('field_name', None)
#     field_value = R.POST.get('value', None)
#     plan_id = R.POST.get('plan_id', None)
    
#     plan_field = ['name', 'code', 'note', 'project_serial', 'sort', 'uplevel', 'host', 'budget', 'no', 'budget_type']
#     planbudget_field = ['year', 'capital_self', 'capital_trust', 'capital_grant', 'regular_self', 'regular_trust', 'regular_grant', 'memo']
#     return_value_2 = ''
#     return_value = field_value
#     if field_name in plan_field: row = Plan.objects.get(id=plan_id)
#     elif field_name in planbudget_field: row = PlanBudget.objects.get(id=plan_id)
#     try:
#         if field_name == 'year' and PlanBudget.objects.get(plan=row.plan, year=field_value):
#             return {'status': False, 'msg': '資料更新失敗『年度資料重複』，請重新選擇年度。'}
#     except: pass
#     if field_name in ['budget', 'capital_self', 'capital_trust', 'capital_grant', 'regular_self', 'regular_trust', 'regular_grant']:
#         if field_value == '': field_value = 0
#         field_value = decimal.Decimal(str(round(float(field_value), 3)))
#         return_value = str(int(field_value))
#     if field_name in ['budget_type']:
#         field_value = Option.objects.get(id=field_value)
#         return_value = str(int(field_value.id))
#         return_value_2 = field_value.value

#     setattr(row, field_name, field_value)
#     row.save()

#     return {'status': True, 'return_value': return_value, 'return_value_2': return_value_2}


# def deletePlan(R):
#     row = Plan.objects.get(id=R.POST.get('plan_id', None))
#     for p in Project.objects.filter(plan=row):
#         p.plan = Plan.objects.get(id=1)
#         p.save()
#     up_plan_id = row.uplevel.id
#     row.delete()

#     return {'status': True, 'up_plan_id': up_plan_id,}


# def getPlanListInTable(R):
#     plan = Plan.objects.get(id=R.POST.get('plan_id', None))
#     table = '<table class="plan_radio_table" border="1" style="border-collapse: collapse">'
#     table += '<tr align="center" bgcolor="#CCFF99"><td>選擇<br>位置</td><td>計畫名稱</td></tr>'
#     top_plan = Plan.objects.get(id=1)
#     for i in [top_plan] + top_plan.rSubPlanInList():
#         if i not in  [top_plan, plan] + plan.rSubPlanInList():
#             table += '<tr bgcolor="#FFFFFF"><td align="center"><input id="plan_radio" name="plan_radio" type="radio" value="' + str(i.id) + '"></td>'
#             table += '<td>' + '　　' * i.rLevelNumber() + i.name + '</td></tr>'
#         else:
#             table += '<tr bgcolor="#AAAAAA"><td align="center"></td>'
#             table += '<td>' + '　　' * i.rLevelNumber() + i.name + '</td></tr>'
#     table += '</table>'
#     return {'table': table}


# def updatePlanSort(R):
#     relation = R.POST.get('relation_radio', None) # ['theSameLevel' or 'isSubLevel']
#     select_plan = Plan.objects.get(id=R.POST.get('plan_radio', None))
#     if relation == 'theSameLevel':
#         target_plan = select_plan.uplevel
#     elif relation == 'isSubLevel':
#         target_plan = select_plan
#     wantSortPlan = Plan.objects.get(id=R.POST.get('wantSortPlan', None))
#     move_list = [wantSortPlan] + wantSortPlan.rSubPlanInList()
#     gt_plans = Plan.objects.filter(sort__gt=target_plan.sort).order_by('sort')
#     try:
#         up_sort_num = float(select_plan.rSubPlanInList()[-1].sort)
#     except:
#         up_sort_num = float(select_plan.sort)
#     try:
#         down_sort_num = float(Plan.objects.filter(sort__gt=decimal.Decimal(str(up_sort_num))).order_by('sort')[0].sort)
#     except:
#         down_sort_num = 10000
#     wantSortPlan.uplevel = target_plan
#     wantSortPlan.save()
#     if not gt_plans:
#         sort_num = target_plan.sort
#         for i in move_list:
#             i.sort = sort_num + 1
#             i.save()
#             sort_num += 1
#     else:
#         for i in move_list:
#             up_sort_num = (up_sort_num + down_sort_num) / 2.
#             i.sort = decimal.Decimal(str(up_sort_num))
#             i.save()
#     return {'status': True}


# def batchEdit_Plan(R):
#     plan = Plan.objects.get(id=R.POST.get('plan_no', ''))
#     p_list = R.POST.get('p_list', '').replace('[','').replace(']','').split(',')
#     for p_no in p_list:
#         project = Project.objects.get(id=int(p_no))
#         project.plan =plan
#         project.save()
#     return {'status': True}


# def recordAllProjects(R):
#     record_project_profile_id = R.POST.get('record_project_profile_id', '')
#     checked = R.POST.get('checked', '')
#     if '' == record_project_profile_id or '' == checked:
#         result = {'status': False, 'message': u'未指定類型'}
#     try:
#         rpp = RecordProjectProfile.objects.get(id=record_project_profile_id)
#     except RecordProjectProfile.DoesNotExist:
#         result = {'status': False, 'message': u'找不到設定檔'}

#     querystring = R.POST.get('querystring', '')
#     hash = {}
#     if querystring:
#         for word in querystring.split('&'):
#             key, value = word.split('=')
#             hash[key] = value
#     projects, projects_num, p_list = _searchProject(hash, use_page=False)

#     project_ids = [p.id for p in projects]
#     if checked in 'true':
#         for p in Project.objects.filter(id__in=project_ids):
#             rpp.projects.add(p)
#     else:
#         for p in Project.objects.filter(id__in=project_ids):
#             rpp.projects.remove(p)

#     return {'status': True}

# def rProjectsInRecordProjectProfile(R):
#     record_project_profile_id = R.POST.get('record_project_profile_id', '')
#     try:
#         rpp = RecordProjectProfile.objects.get(id=record_project_profile_id)
#     except RecordProjectProfile.DoesNotExist:
#         result = {'status': False, 'message': u'找不到設定檔'}
#     R.session['now_record_project_profile_id'] = rpp.id
#     return {'status': True, 'project_ids': [p.id for p in rpp.projects.all()]}

# def recordProjects(R):
#     record_project_profile_id = R.POST.get('record_project_profile_id', '')
#     checked = R.POST.get('checked', '')
#     project_ids = R.POST.get('project_ids', '')
#     if '' == record_project_profile_id or '' == checked or '' == project_ids:
#         result = {'status': False, 'message': u'未指定類型及工程案'}

#     try:
#         rpp = RecordProjectProfile.objects.get(id=record_project_profile_id)
#     except RecordProjectProfile.DoesNotExist:
#         result = {'status': False, 'message': u'找不到設定檔'}

#     project_ids = project_ids.split(',')
#     if checked in 'true':
#         for p in Project.objects.filter(id__in=project_ids):
#             rpp.projects.add(p)
#     else:
#         for p in Project.objects.filter(id__in=project_ids):
#             rpp.projects.remove(p)

#     return {'status': True}

# def cExportCustomReport(R):
#     name = R.POST.get('name', '')
#     if not name:
#         return {'status': False, 'message': u'報表名稱必填'}

#     try:
#         R.user.exportcustomreport_set.get(name=name)
#     except ExportCustomReport.DoesNotExist:
#         ecr = ExportCustomReport(owner=R.user, name=name)
#         ecr.save()
#         return {'status': True, 'exportcustomreport_id': ecr.id}
#     else:
#         return {'status': False, 'message': u'報表名稱已存在'}

# def cRecordProjectProfile(R):
#     name = R.POST.get('name', '')
#     if not name:
#         return {'status': False, 'message': u'紀錄名稱必填'}

#     try:
#         R.user.recordprojectprofile_set.get(name=name)
#     except RecordProjectProfile.DoesNotExist:
#         rpp = RecordProjectProfile(owner=R.user, name=name)
#         rpp.save()
#         return {'status': True, 'recordprojectprofile_id': rpp.id}
#     else:
#         return {'status': False, 'message': u'紀錄名稱已存在'}

# def rSelfProjects(R):
#     projects = FRCMUserGroup.objects.filter(user=R.user)
#     return {'status': True,
#         'projects': [ {'id':str(p.project.id), 'name':p.project.name} for p in projects]}

# def rReportFields(R):
#     def _rECRF(rf, ecr):
#         try: ecrf = ExportCustomReportField.objects.get(report_field=rf, export_custom_report=ecr)
#         except ExportCustomReportField.DoesNotExist: ecrf = None
#         return ecrf

#     try:
#         ecr = ExportCustomReport.objects.get(id=R.POST.get('export_custom_report_id', 0))
#     except ExportCustomReport.DoesNotExist:
#         return {'stauts': False, 'message': u'報表不存在'}
#     except ValueError:
#         return {'stauts': False, 'message': u'報表不存在'}

#     tags, fields = [], {}
#     for o in Option2.objects.filter(swarm='report_field_tag').order_by('id'):
#         tags.append(o.value)

#         fields[o.value] = [{ 'id': rf.id, 'name': rf.name,
#             'export_custom_report_field_id': _rECRF(rf, ecr).id if _rECRF(rf, ecr) else 0,
#             'export_custom_report_field_checked': True if _rECRF(rf, ecr) else False,
#             'export_custom_report_field_priority': _rECRF(rf, ecr).priority if _rECRF(rf, ecr) else 0,
#             } for rf in o.reportfield_set.all().order_by('id')]

#     return {'status': True, 'tags': tags, 'fields': fields}

# def addOrRemoveFieldFromExportCustomReport(R):
#     export_custom_report_id = R.POST.get('export_custom_report_id', '')
#     add_or_remove = R.POST.get('add_or_remove', '')
#     report_field_id = R.POST.get('report_field_id', '')

#     # if not export_custom_report_id or '' == add_or_remove or not report_field_id:
#     #     return {'status': False, 'message': u'欄位皆必填'}

#     try:
#         ecr = ExportCustomReport.objects.get(id=export_custom_report_id)
#     except ExportCustomReport.DoesNotExist:
#         return {'stauts': False, 'message': u'報表不存在'}
#     except ValueError:
#         return {'stauts': False, 'message': u'報表不存在'}

#     try:
#         rf = ReportField.objects.get(id=report_field_id)
#     except ReportField.DoesNotExist:
#         return {'stauts': False, 'message': u'欄位不存在'}
#     except ValueError:
#         return {'stauts': False, 'message': u'欄位不存在'}

#     try:
#         ecrf = ExportCustomReportField.objects.get(report_field=rf, export_custom_report=ecr)
#     except ExportCustomReportField.DoesNotExist:
#         ecrf = None
#     if (add_or_remove == True or add_or_remove == 'true' or add_or_remove == 'checked') and not ecrf:
#         ecrf = ExportCustomReportField(report_field=rf, export_custom_report=ecr, priority=(rf.id-1)*16)
#         ecrf.save()
#     elif ecrf:
#         ecrf.delete()

#     return {'status': True, 'export_custom_report_field_id': ecrf.id if ecrf else 0,
#         'export_custom_report_field_priority': ecrf.priority if ecrf else 0,}

# def uExportCustomReportFieldPriority(R):
#     id = R.POST.get('id', '')
#     priority = R.POST.get('priority', '')
#     if not id or not priority:
#         return {'status': False, 'message': u'欄位皆必填'}
#     try:
#         ecrf = ExportCustomReportField.objects.get(id=id)
#     except ExportCustomReportField.DoesNotExist:
#         return {'status': False, 'message': u'找不到資料'}
#     else:
#         ecrf.priority = int(float(priority))
#         ecrf.save()

#         ecr = ecrf.export_custom_report
#         try:
#             prev = ExportCustomReportField.objects.filter(
#                 export_custom_report=ecr,
#                 priority__lte=ecrf.priority).exclude(id=ecrf.id).order_by('-priority')[0]
#         except IndexError:
#             prev = None
#         try:
#             next = ExportCustomReportField.objects.filter(
#                 export_custom_report=ecr,
#                 priority__gte=ecrf.priority).exclude(id=ecrf.id).order_by('priority')[0]
#         except IndexError:
#             next = None
#         if not prev or not next or (ecrf.priority - prev.priority) <= 1 or (next.priority - ecrf.priority) <=1:
#             prioritys = []
#             for i, ecrf in enumerate(ecr.exportcustomreportfield_set.all().order_by('priority', 'report_field__id')):
#                 ecrf.priority = i * 16
#                 ecrf.save()
#                 prioritys.append([ecrf.id, ecrf.priority])
#         else:
#             prioritys = False

#         return {'status': True, 'prioritys': prioritys}

# def syncPCCData(R):
#     pcc_no = R.POST.get('pcc_no', '')
#     if pcc_no != '':
#         _syncPCCData(pcc_no=pcc_no)
#         return {'status': True,}
#     else:
#         return {'status': False}

# def uProgress(R):
#     DATA = R.POST
#     return_name = ''
#     row = Progress.objects.get(id=DATA.get('row', None))
#     order = Progress.objects.filter(project = DATA.get('project_id', None)).order_by('-date')
#     for i in order:
#         if DATA.get('new_info', None) == str(i.date):
#             message = '日期已存在！'
#             return {'status': False, 'return_name': return_name, 'message': message}
#     field_name = DATA.get('entry', None).replace('_'+DATA.get('row', None), '')
#     field_value = DATA.get('new_info', None)
#     if field_name == 'date':
#         return_name = field_value
#     elif field_name == 'schedul_progress_percent' or field_name == 'actual_progress_percent':
#         if field_value == '': field_value = 0
#         field_value = decimal.Decimal(str(round(float(field_value), 2)))
#         return_name = str(round(float(field_value), 2))
#         if return_name.split('.')[1]=='0': return_name += '0'
#     elif field_name == 'status':
#         field_value = Option.objects.get(id=field_value)
#         return_name = field_value.value


#     setattr(row, field_name, field_value)
#     row.save()

#     return {'status': True, 'return_name': return_name}

# def rPCCProgress(R):
#     DATA = R.POST
#     project = Project.objects.get(id=DATA.get('project_id', None))
#     try:
#         pcc_record = PCCProject.objects.get(uid=project.pcc_no)
#         record = True
#     except PCCProject.DoesNotExist:
#         pcc_record = False
#         record = False
#     pcc_progress = RelayInfo.objects.filter(project=project).order_by('year', 'month')
#     t = get_template(os.path.join('project', 'pcc_progress.html'))
#     html = t.render(RequestContext(R, {
#         'pcc_record': pcc_record,
#         'pcc_progress': pcc_progress,
#         }))
#     return {'html': html, 'record': record}

# def syncProgress(R):
#     DATA = R.POST
#     relay_progress = RelayInfo.objects.get(id=DATA.get('relay_progress_id', None))
#     _syncProgress(relay_progress, R.user)
#     return {'status': True}

# def dProgress(R):
#     DATA = R.POST
#     progress = Progress.objects.get(id=DATA.get('progress_id', None))
#     progress.delete()
#     return {'status': True}

# def uFund(R):
#     DATA = R.POST
#     return_name = ''
#     fund = Fund.objects.get(project__id=DATA.get('project_id', None))
#     field_name = DATA.get('entry', None)
#     field_value = DATA.get('new_Info', None)
#     return_name = field_value
#     if field_value == '':
#         field_value = None
#         return_name = ''
#     try:
#         setattr(fund, field_name, field_value)
#         fund.save()
#     except:
#         return {'status': False, 'message': u'輸入格式錯誤，修改失敗!!'}
#     return {'status': True, 'return_name': return_name, 'new_total': fund.rTotalProjectBudget(), 'new_self': fund.rSelfLoad(), 'new_local': fund.rlocalMatchFund()}

# def uBudget(R):
#     DATA = R.POST
#     return_name = ''
#     year = DATA.get('entry', None).split('_')[0]
#     field_name = DATA.get('entry', None).replace(year+'_', '')
#     field_value = DATA.get('new_Info', None)
#     return_name = field_value
#     budget = Budget.objects.get(year=year, fund=Fund.objects.get(project__id=DATA.get('project_id', None)))
#     if field_value == '':
#         field_value = None
#         return_name = ''
#     setattr(budget, field_name, field_value)
#     budget.save()
#     if field_name == 'capital_ratify_revision' and field_value and field_value != '0':
#         setattr(budget.fund.project, 'subsidy_limit', field_value)
#         budget.fund.project.save()
#     elif field_name == 'capital_ratify_revision':
#         setattr(budget.fund.project, 'subsidy_limit', budget.capital_ratify_budget)
#         budget.fund.project.save()
#     elif field_name == 'capital_ratify_budget' and (budget.capital_ratify_revision == 0 or not budget.capital_ratify_revision):
#         setattr(budget.fund.project, 'subsidy_limit', field_value)
#         budget.fund.project.save()
#     return {'status': True, 'return_name': return_name}

# def uFundRecord(R):
#     DATA = R.POST
#     return_name = ''
#     record = FundRecord.objects.get(id=DATA.get('row', None))
#     field_name = DATA.get('entry', None).replace('_'+DATA.get('row', None), '')
#     field_value = DATA.get('new_Info', None)
#     return_name = field_value
#     if field_value == '':
#         field_value = None
#         return_name = ''
#     setattr(record, field_name, field_value)
#     record.save()
#     return {'status': True, 'return_name': return_name}

# def cAppropriate(R):
#     DATA = R.POST
#     NewAppropriate = Appropriate(
#                 project = Project.objects.get(id=DATA.get('project_id', None)),
#                 allot_date = TODAY(),
#                 record_date = TODAY(),
#     )
#     NewAppropriate.save()

#     t = get_template(os.path.join('project', 'appropriate_unit.html'))
#     html = t.render(RequestContext(R, {
#     'edit': True,
#     'a': Appropriate.objects.get(id=NewAppropriate.id),
#     }))
#     return {'status': True, 'html': html}

# def addAllocation(R):
#     DATA = R.POST
#     NewAllocation = Allocation(
#                 project = Project.objects.get(id=DATA.get('project_id', None)),
#                 date = TODAY(),
#     )
#     NewAllocation.save()
#     NewAllocation.date = NewAllocation.date.date
#     t = get_template(os.path.join('project', 'allocation_unit.html'))
#     html = t.render(RequestContext(R, {
#     'edit': True,
#     'a': NewAllocation,
#     }))
#     return {'status': True, 'html': html}

# def uAppropriate(R):
#     DATA = R.POST
#     return_name = ''
#     appropriate = Appropriate.objects.get(id=DATA.get('row', None))
#     field_name = DATA.get('entry', None).replace('_'+DATA.get('row', None), '')
#     field_value = DATA.get('new_Info', None)
#     return_name = field_value
#     if field_value == '':
#         field_value = None
#         return_name = ''
#     setattr(appropriate, field_name, field_value)
#     appropriate.save()
#     # TODO: 變更日期時重新排序
#     return {'status': True, 'return_name': return_name}

# def uAllocation(R):
#     DATA = R.POST
#     return_name = ''
#     allocation = Allocation.objects.get(id=DATA.get('row', None))
#     field_name = DATA.get('entry', None).replace('_'+DATA.get('row', None), '')
#     field_value = DATA.get('new_Info', None)
#     return_name = field_value
#     if field_value == '':
#         field_value = None
#         return_name = ''
#     setattr(allocation, field_name, field_value)
#     allocation.save()
#     return {'status': True, 'return_name': return_name}

# def dAppropriate(R):
#     DATA = R.POST
#     appropriate = Appropriate.objects.get(id=DATA.get('appropriate_id', None))
#     appropriate.delete()
#     return {'status': True}

# def deleteProjectAllocation(R):
#     DATA = R.POST
#     allocation = Allocation.objects.get(id=DATA.get('allocation_id', None))
#     allocation.delete()
#     return {'status': True}

# def dProjectFundRecord(R):
#     DATA = R.POST
#     fundrecord = FundRecord.objects.get(id=DATA.get('fundrecord_id', None))
#     fundrecord.delete()
#     return {'status': True}

# def rPCCFundRecord(R):
#     DATA = R.POST
#     project = Project.objects.get(id=DATA.get('project_id', None))
#     try:
#         pcc_record = PCCProject.objects.get(uid=project.pcc_no)
#         record = True
#     except PCCProject.DoesNotExist:
#         pcc_record = False
#         record = False
#     pcc_fund = RelayInfo.objects.filter(project=project).order_by('year', 'month')

#     t = get_template(os.path.join('project', 'pcc_fund.html'))
#     html = t.render(RequestContext(R, {
#         'pcc_record': pcc_record,
#         'pcc_fund': pcc_fund,
#         }))
#     return {'html': html, 'record': record}

# def syncFundRecord(R):
#     DATA = R.POST
#     relay_record = RelayInfo.objects.get(id=DATA.get('relay_fund_id', None))
#     _syncFundRecord(relay_record)
#     return {'status': True}

# def rFundingDetail(R):
#     DATA = R.POST
#     project = Project.objects.get(id=DATA.get('project_id', None))
#     t = get_template(os.path.join('project', 'funding_detail.html'))
#     html = t.render(RequestContext(R, {
#         'project': project,
#         }))
#     return {'html': html}

# def runReserveProject(R):
#     DATA = R.POST
#     project = Project.objects.get(id=DATA.get('project_id', None))
#     reserved = Reserve.objects.filter(project=project).order_by('year')
#     if reserved.count() == 0: new_year = int(project.year) + 1
#     else: new_year = int(list(reserved)[-1].year) + 1
#     amount = DATA.get('amount',None)
#     if DATA.get('apply_date',None) == '': apply_date = TODAY()
#     else: apply_date = DATA.get('apply_date',None)
#     if DATA.get('reserve_date',None) == '': reserve_date = None
#     else: reserve_date = DATA.get('reserve_date',None)
#     if DATA.get('allocation',None) == '': allocation = None
#     else: allocation = DATA.get('allocation',None)
#     if DATA.get('un_allocation',None) == '': un_allocation = None
#     else: un_allocation = DATA.get('un_allocation',None)
#     if DATA.get('reason',None) == '': reason = None
#     else: reason = DATA.get('reason',None)
#     if DATA.get('prove',None) == '': prove = None
#     else: prove = DATA.get('prove',None)
#     if DATA.get('memo',None) == '': memo = None
#     else: memo = DATA.get('memo',None)
#     NewReserve = Reserve(
#             project = project,
#             year = new_year,
#             amount = amount,
#             apply_date = apply_date,
#             reserve_date = reserve_date,
#             allocation = allocation,
#             un_allocation = un_allocation,
#             reason = reason,
#             prove = prove,
#             memo = memo,
#             )
#     NewReserve.save()
#     NewBudget = Budget(
#             year = new_year,
#             fund = Fund.objects.get(project=project),
#             )
#     NewBudget.save()
#     return {'status': True, 'new_year': new_year}

# def dReserve(R):
#     DATA = R.POST
#     reserve = Reserve.objects.get(id=DATA.get('reserve_id', None))
#     budget = Budget.objects.get(year=reserve.year, fund=reserve.project.fund_set.get())
#     reserve.delete()
#     budget.delete()
#     return {'status': True, 'year': reserve.year}

# def uBidinfo(R):
#     DATA = R.POST
#     return_name = ''
#     extr = ''
#     project = Project.objects.get(id=DATA.get('project_id', None))
#     field_name = DATA.get('entry', None)
#     if DATA.get('new_info', None) == '':
#         field_value = None
#     else:
#         field_value = DATA.get('new_info', None)
#         return_name = field_value
#     if field_name == 'pcc_no' and field_value:
#         try:
#             p = Project.objects.get(pcc_no=field_value)
#             return {'status': False, 'return_name': '', 'message': u'此工程會編號已存在', 'project_info': '輸入編號與此工程重複 id=' + str(p.id) + ' - ' + str(p.year)  + '年度 - ' + p.name}
#         except Project.DoesNotExist:
#             try: extr = getProjectInfo(field_value)
#             except:
#                 message = u'無法使用此編號取得工程資訊。編號有誤、或是權限不足(工程會補助機關未正確填報)。'
#                 return {'status': False, 'return_name': return_name,  'message': message}
#     elif field_name == 'allot_rate' :
#         if DATA.get('new_info', None) == '':
#             field_value = decimal.Decimal(str(100.00))
#             return_name = '100'
#         else:
#             field_value = decimal.Decimal(str(DATA.get('new_info', None)))
#             return_name = str(field_value)
#     elif field_name == 'bid_type' or field_name == 'contract_type' :
#         field_value = Option.objects.get(id = DATA.get('new_info', None))
#         return_name = field_value.value
#     else:
#         field_value = DATA.get('new_info', None)
#         if DATA.get('new_info', None) == '':
#             field_value = None
#             return_name = ''
#         else:
#             return_name = field_value
#     setattr(project, field_name , field_value)
#     project.save()
#     contract_fees = ['planning_fee', 'commissioned_research', 'design_bid', 'inspect_bid', 'construction_bid', 'pollution', 'manage', 'subsidy', 'other_defray', 'total_money']
#     contract_total = 'init'
#     if field_name in contract_fees:
#         contract_total = project.rContractTotalMoney()
#     settlement_fees = ['settlement_planning_fee', 'settlement_commissioned_research', 'settlement_design_bid', 'settlement_inspect_bid', 'settlement_construction_bid', 'settlement_pollution', 'settlement_manage', 'settlement_subsidy', 'settlement_other_defray', 'settlement_total_money']
#     settlement_total = 'init'
#     if field_name in settlement_fees:
#         settlement_total = project.rSettlementTotalMoney()
#     return {'status': True, 'return_name': return_name, 'extr': extr, 'contract_total': contract_total, 'settlement_total': settlement_total}

# def uReserveInfo(R):
#     DATA = R.POST
#     return_name = ''
#     year = DATA.get('entry', None).split('_')[0]
#     field_name = DATA.get('entry', None).replace(year+'_', '')
#     field_value = DATA.get('new_Info', None)
#     return_name = field_value
#     reserve = Reserve.objects.get(project__id=DATA.get('project_id', None), year=year)
#     if DATA.get('new_Info', None) == '':
#         field_value = None
#     else:
#         field_value = DATA.get('new_Info', None)
#         return_name = field_value
#     setattr(reserve, field_name , field_value)
#     reserve.save()
#     fees = ['amount', 'allocation', 'un_allocation']
#     if field_name in fees: num = True
#     else: num = False
#     return {'status': True, 'return_name': return_name, 'num': num}

# def rPCCProject(R):
#     DATA = R.POST
#     project = Project.objects.get(id=DATA.get('project_id', None))
#     try:
#         pcc_record = PCCProject.objects.get(uid=project.pcc_no)
#         record = True
#     except PCCProject.DoesNotExist:
#         pcc_record = False
#         record = False
#     t = get_template(os.path.join('project', 'pcc_project.html'))
#     html = t.render(RequestContext(R, {
#         'pcc_project': pcc_record,
#         }))
#     return {'status': True, 'html': html, 'record': record}

# def getSubLocation(R):
#     DATA = R.POST
#     type = DATA.get('type', None)
#     edit = DATA.get('edit', None)
#     project_id = DATA.get('project_id', None)
#     if edit == 'true': edit = 'new' + str(TODAY().microsecond)
#     elif edit == 'false': edit = False
#     if type == '227':
#         location = 'FishingPort'
#         if DATA.get('place', None) == '1': options = FishingPort.objects.all().order_by('id')
#         else: options = FishingPort.objects.filter(place__id=DATA.get('place', None)).order_by('id')
#     elif type == '228':
#         location = 'Aquaculture'
#         if DATA.get('place', None) == '1': options = Aquaculture.objects.all().order_by('id')
#         else: options = Aquaculture.objects.filter(place__id=DATA.get('place', None)).order_by('id')
#     t = get_template(os.path.join('project', 'sublocation_option.html'))
#     html = t.render(RequestContext(R, {
#         'edit': edit,
#         'location_type': location,
#         'sub_options': options,
#         }))

#     html_sort = '<option value="last" name="{{ forloop.counter }}">(放置於最後位置)</option>'
#     for i in Draft_Project.objects.filter(place__id=DATA.get('place', None)).order_by('sort'):
#         try:
#             if i.id == int(project_id):
#                 html_sort += '<option value="' + str(i.get_sort_num()) + '" selected>' + str(i.get_sort_num()) + ' (取代 ' + str(i.name) + ' 順序)</option>'
#             else:
#                 html_sort += '<option value="' + str(i.get_sort_num()) + '">' + str(i.get_sort_num()) + ' (取代 ' + str(i.name) + ' 順序)</option>'
#         except:
#             html_sort += '<option value="' + str(i.get_sort_num()) + '">' + str(i.get_sort_num()) + ' (取代 ' + str(i.name) + ' 順序)</option>'
#     return {'status': True, 'html': html, 'html_sort': html_sort}

# def cProject(R):
#     DATA = R.POST
#     NewProject = Project(
#         plan = Plan.objects.get(id=DATA.get('plan_id', None)),
#         year = int(DATA.get('year', None)),
#         project_type = Option.objects.get(id=DATA.get('project_type', None)),
#         project_sub_type = Option.objects.get(id=DATA.get('project_sub_type', None)),
#         name = DATA.get('name', None),
#         bid_no = DATA.get('bid_no', None),
#         place = Place.objects.get(id=DATA.get('place_id', None)),
#         location = DATA.get('location', None),
# #        budget_type = Option.objects.get(id=DATA.get('budget_type_id', None)),
#         purchase_type = Option.objects.get(id=DATA.get('purchase_type_id', None)),
#         budget_sub_type = Option.objects.get(id=DATA.get('budget_sub_type_id', None)),
#         undertake_type = Option.objects.get(id=DATA.get('undertake_type_id', None)),
#         unit = Unit.objects.get(id=DATA.get('unit_id', None)),
#         self_charge = DATA.get('self_charge', None),
#         self_contacter = DATA.get('self_contacter', None),
#         self_contacter_phone = DATA.get('self_contacter_phone', None),
#         self_contacter_email = DATA.get('self_contacter_email', None),
#         local_charge = DATA.get('local_charge', None),
#         local_contacter = DATA.get('local_contacter', None),
#         local_contacter_phone = DATA.get('local_contacter_phone', None),
#         local_contacter_email = DATA.get('local_contacter_email', None),
#         contractor_charge = DATA.get('contractor_charge', None),
#         contractor_contacter = DATA.get('contractor_contacter', None),
#         contractor_contacter_phone = DATA.get('contractor_contacter_phone', None),
#         contractor_contacter_email = DATA.get('contractor_contacter_email', None),
#         project_memo = DATA.get('project_memo', None),
# #        status = Option.objects.get(id=159),
#     )
#     #辦理別(F) = 補助，則為新增工程案時所輸入之資訊，可於管考系統編輯；
#     #若使用者未填寫，則預設本署負擔比例 = 核定數(J) / 計畫經費(I)。若辦理別(F)不為補助，則本署負擔比例必為100%。
#     if NewProject.undertake_type.value != '補助':
#         NewProject.allot_rate = 100
#     else:
#         allot_rate = DATA.get('allot_rate', 0)
#         if not allot_rate: allot_rate = 100
#         NewProject.allot_rate = allot_rate
#     #本署負擔上限金額 = 核定數(J)，本欄位不可編輯。
#     NewProject.subsidy_limit = DATA.get('capital_ratify_budget', None) or 0
#     NewProject.save()
#     if DATA.get('x_coord', None) != '': setattr(NewProject, 'x_coord', int(DATA.get('x_coord', None)))
#     if DATA.get('y_coord', None) != '': setattr(NewProject, 'y_coord', int(DATA.get('y_coord', None)))
#     NewProject.save()
#     sub_location = ['', ] + DATA.get('sub_location', None).split(',')[:-1]
#     if DATA.get('project_type', None) == '227':
#         for i in range(1, len(sub_location)):
#             if sub_location[i] != '' and sub_location[i] != sub_location[i-1]:
#                 NewProject.fishing_port.add(FishingPort.objects.get(id=sub_location[i]))
#     elif DATA.get('project_type', None) == '228':
#         for i in range(1, len(sub_location)):
#             if sub_location[i] != '' and sub_location[i] != sub_location[i-1]:
#                 NewProject.aquaculture.add(Aquaculture.objects.get(id=sub_location[i]))
#     NewFund = Fund(
#         project = NewProject,
#         year = NewProject.year,
#     )
#     NewFund.save()
#     NewBudget = Budget(
#         fund = NewFund,
#         year = NewProject.year,
#         capital_ratify_budget = DATA.get('capital_ratify_budget', None) or 0,
#         capital_ratify_local_budget = DATA.get('capital_ratify_local_budget', None) or 0,
#     )
#     NewBudget.save()
#     NewChaseOneByOne = CountyChaseProjectOneByOne(
#         project = NewProject,
#     )
#     NewChaseOneByOne.save()
#     try:
#         action = DATA.get('action', None).split('__')
#         draft_project = Draft_Project.objects.get(id=action[1])
#         draft_project.delete()
#     except: pass

#     return {'status': True, 'new_project_id': str(NewProject.id)}

# def syncChaseData(R):
#     projects = Project.objects.all()
#     for i in projects:
#         fund = Fund.objects.get(project=i)
#         if Budget.objects.filter(fund=fund).count() == 0:
#             NewBudget = Budget(
#                 fund = fund,
#                 year = i.year,
#                 capital_ratify_budget = 0,
#             )
#             NewBudget.save()
#     t = get_template(os.path.join('project', 'sync_result.html'))
#     html = t.render(RequestContext(R,{
#         'status': '同步成功',
#         }))
#     return HttpResponse(html)

# def dSubLocation(R):
#     DATA = R.POST
#     project = Project.objects.get(id=DATA.get('project_id', None))
#     try:
#         if project.project_type.id == 227: project.fishing_port.remove(project.fishing_port.get(id=DATA.get('location_id', None)))
#         elif project.project_type.id == 228: project.aquaculture.remove(project.aquaculture.get(id=DATA.get('location_id', None)))
#         return {'status': True,}
#     except:
#         return {'status': False, 'msg': '該紀錄已不存在！'}


# def rAccoutingData(R):
#     DATA = R.POST
#     project = Project.objects.get(id=DATA.get('project_id', None))
#     accout_no = project.no
#     fm = FishMoney("fes.fa.gov.tw")
#     fm.login()
#     try: response = fm.get_project(project_code=accout_no)#'099!0201113'
#     except fm.NotExistProjectAccountError, e:
#         return {'status': False, 'html': e.message}
#     except fm.NoProjectAccountDataError, e:
#         return {'status': False, 'html': e.message}
#     t = get_template(os.path.join('project', 'accouting_data.html'))
#     html = t.render(RequestContext(R, {
#         'project': project,
#         'data_obj': response,
#         }))
#     return {'status': True, 'html': html}


# def syncAccoutingData(R):
#     DATA = R.POST
#     project = Project.objects.get(id=DATA.get('project_id', None))
#     accout_no = project.no
#     fm = FishMoney("fes.fa.gov.tw")
#     fm.login()
#     try: response = fm.get_project(project_code=accout_no)#'099!0201113'
#     except Exception: return {'status': False, 'msg': '資料聯繫錯誤！'}
#     vouch_date = response[u'核定日期']
#     setattr(project, 'vouch_date', vouch_date)
#     project.save()
#     ratify_budget = decimal.Decimal(str(round(float(response[u'核定金額']), 3)))
#     fund = project.fund_set.get()
#     setattr(fund, 'capital_ratify_budget', ratify_budget)
#     fund.save()
#     accout_appropriates = response[u'撥付資料']
#     appropriates = project.appropriate_set.all()
#     for j in accout_appropriates:
#         same = False
#         for i in appropriates:
#             if i.allot_date.year==j[u'撥付日期'].year and i.allot_date.month==j[u'撥付日期'].month and i.allot_date.day==j[u'撥付日期'].day:
#                 same = True
#                 setattr(i, 'num', decimal.Decimal(str(round(float(j[u'合計']), 3))))
#                 i.save()
#         if not same:
#             NewAppropriate = Appropriate(
#                 project = project,
#                 num = decimal.Decimal(str(round(float(j[u'合計']), 3))),
#                 allot_date = j[u'撥付日期'],
#                 record_date = TODAY()
#             )
#             NewAppropriate.save()
#     return {'status': True}


# def syncPCCProjectData(R):
#     DATA = R.POST
#     project = Project.objects.get(id=DATA.get('project_id', None))
#     pcc_data = PCCProject.objects.get(uid=project.pcc_no)
#     if pcc_data.r_tenders_method:
#         print pcc_data.r_tenders_method, 'ININININ'
#         if u'限制性' in pcc_data.r_tenders_method: tenders_method = Option.objects.get(swarm='bid_type', value=u'限制性招標')
#         elif u'選擇性' in pcc_data.r_tenders_method: tenders_method = Option.objects.get(swarm='bid_type', value=u'選擇性招標')
#         elif u'公開' in pcc_data.r_tenders_method: tenders_method = Option.objects.get(swarm='bid_type', value=u'公開招標')
#         setattr(project, 'bid_type', tenders_method)
#     if pcc_data.s_start_date: setattr(project, 'sstart_date', pcc_data.s_start_date)
#     if pcc_data.r_start_date: setattr(project, 'start_date', pcc_data.r_start_date)
#     if pcc_data.s_end_date: setattr(project, 'term_date', pcc_data.s_end_date)
#     if pcc_data.r_end_date: setattr(project, 'rterm_date', pcc_data.r_end_date)
#     if pcc_data.r_checked_and_accepted_date: setattr(project, 'check_date', pcc_data.r_checked_and_accepted_date)
#     project.save()
#     return {'status': True}


# def syncTotalPCCFundRecord(R):
#     if R.META.get('REMOTE_ADDR', '') not in CAN_VIEW_BUG_PAGE_IPS:
#         return HttpResponse('你不能做這件事喔!!!')
#     pcc_no_projects = Project.objects.filter(deleter=None).exclude(pcc_no=None)
#     success_num = 0
#     faild_num = 0

#     for p in pcc_no_projects:
#         try:
#             _syncPCCData(pcc_no=p.pcc_no)
#             success_num += 1
#         except:
#             faild_num += 1

#     for r in  RelayInfo.objects.all():
#         try: _syncFundRecord(r)
#         except: msg = "I don't wanna fix it!!  Fuck You anyway..."

#     t = get_template(os.path.join('project', 'sync_result.html'))
#     html = t.render(RequestContext(R,{
#         'status': 'ＰＣＣ同步成功',
#         'success_num': success_num,
#         'faild_num': faild_num
#         }))
#     return HttpResponse(html)


# def syncTotalAccoutingData(R):
#     if R.META.get('REMOTE_ADDR', '') not in CAN_VIEW_BUG_PAGE_IPS:
#         return HttpResponse('你不能做這件事喔!!!')
    
#     fm = FishMoney("fes.fa.gov.tw")
#     fm.login()
#     accounting_no_projects = Project.objects.filter(deleter=None).exclude(no=None)
#     msg = 0
#     success_num = 0
#     notexist_faild_num = 0
#     nodata_faild_num = 0
#     faild_num = 0
#     faild_nos = []
#     for project in accounting_no_projects:
#         accout_no = project.no
#         try: response = fm.get_project(project_code=accout_no)#'099!0201113'
#         except fm.NotExistProjectAccountError, e:
#             notexist_faild_num += 1
#             continue
#         except fm.NoProjectAccountDataError, e:
#             nodata_faild_num += 1
#             continue
#         except Exception:
#             faild_nos.append(accout_no)
#             faild_num += 1
#             continue
#         vouch_date = response[u'核定日期'] or None
#         setattr(project, 'vouch_date', vouch_date)
#         project.save()
#         ratify_budget = decimal.Decimal(str(round(float(response[u'核定金額']), 3)))
#         fund = project.fund_set.get()
#         setattr(fund, 'capital_ratify_budget', ratify_budget)
#         fund.save()
#         accout_appropriates = response[u'撥付資料']
#         appropriates = project.appropriate_set.all()
#         for j in accout_appropriates:
#             same = False
#             for i in appropriates:
#                 if i.allot_date.year==j[u'撥付日期'].year and i.allot_date.month==j[u'撥付日期'].month and i.allot_date.day==j[u'撥付日期'].day:
#                     same = True
#                     setattr(i, 'num', decimal.Decimal(str(round(float(j[u'合計']), 3))))
#                     i.save()
#             if not same:
#                 NewAppropriate = Appropriate(
#                     project = project,
#                     num = decimal.Decimal(str(round(float(j[u'合計']), 3))),
#                     allot_date = j[u'撥付日期'],
#                     record_date = TODAY()
#                 )
#                 NewAppropriate.save()
#         success_num += 1

#     t = get_template(os.path.join('project', 'sync_result.html'))
#     html = t.render(RequestContext(R,{
#         'status': 'Accounting同步成功',
#         'success_num': success_num,
#         'notexist_faild_num': notexist_faild_num,
#         'nodata_faild_num': nodata_faild_num,
#         'faild_num': faild_num,
#         'faild_nos': faild_nos,
#         }))
#     return HttpResponse(html)


# #def sync100money(R):
# #    from project.import_100_data import data_100 as data
# #    good = 0
# #    bad = 0
# #    list = []
# #    list2 = []
# #    for i in data:
# #        try:
# #            row = Project.objects.get(year=100, name=i[0], deleter=None)
# #            row.subsidy_limit = i[2]
# #            row.save()
# #        except:
# #            list.append(i[0])
# #        try:
# #            row2 = Budget.objects.get(year=100, fund__project__name=i[0], fund__project__deleter=None)
# #            row2.capital_ratify_budget = i[1]
# #            row2.save()
# #            good += 1
# #        except:
# #            list2.append(i[0])
# #            bad += 1
# #
# #    return HttpResponse(json.write({'good': good, 'bad': bad, 'list': list2}))


# @checkAuthority
# def SecretGarden(R, project, right_type_value=u'觀看管考系統資料'):
#     class searchForm(forms.Form):
#         years = [(y-1911, y-1911) for y in xrange(2006, TODAY().year+2)]
#         years.insert(0, ('', '所有年度'))
#         years.reverse()
#         year = forms.ChoiceField(choices=years, required=False, label='年度：　')
#         bid_no = forms.CharField(label='標案編號：　', required=False)
#         name = forms.CharField(label='工作名稱：　', required=False)
#         vouch_date_ub = forms.CharField(label='發文(核定)日期：┌', required=False)
#         vouch_date_lb = forms.CharField(label='└', required=False)
#         plans = [('', '全部')]
#         for i in Plan.objects.filter(uplevel=None):
#             plans.append((i.id, '---'*i.rLevelNumber() + i.name))
#             for j in i.rSubPlanInList():
#                 plans.append((j.id, '---'*j.rLevelNumber() + j.name))
#         plan = forms.ChoiceField(choices=plans, required=False, label='所屬計畫：　')
#         purchase_types = [('', '全部')] + [(type.id, type.value) for type in Option.objects.filter(swarm='purchase_type')]
#         purchase_type = forms.ChoiceField(choices=purchase_types, required=False, label='採購類別：　', help_text='(工程／勞務)')
#         budget_sub_types = [('', '全部')] + [(type.id, type.value) for type in Option.objects.filter(swarm='budget_sub_type')]
#         budget_sub_type = forms.ChoiceField(choices=budget_sub_types, required=False, label='經費種類：　', help_text='(資本門／經常門)')
#         undertake_types = [('', '全部')] + [(type.id, type.value) for type in Option.objects.filter(swarm='undertake_type')]
#         undertake_type = forms.ChoiceField(choices=undertake_types, required=False, label='承辦方式：　', help_text='(自辦／委辦／補助)')
#         places = [('', '全部')] + [(i.id, i.name) for i in Place.objects.filter(uplevel=TAIWAN).order_by('id')]
#         place = forms.ChoiceField(choices=places, required=False, label='縣市別：　')
#         units = [('', '全部')]
#         for i in Unit.fish_city_menu.all():
#             units.append((i.id, i.name))
#             if i.uplevel and i.uplevel.name != '縣市政府':
#                 units.extend(
#                     [(j.id, '---'+j.name) for j in i.uplevel_subunit.all()]
#                 )
#         unit = forms.ChoiceField(choices=units, required=False, label='執行機關：　')
#         chases = [('', '全部'), ('unchase', '未追蹤'), ('chase_complete_check', '追蹤中(填完+確認)'), ('chase_complete_uncheck', '追蹤中(填完+未確認)'), ('chase_uncomplete', '追蹤中(未填完)')]
#         chase = forms.ChoiceField(choices=chases, required=False, label='追蹤狀態：　')
#         memo_1 = forms.CharField(label='備註1：　', required=False)
#         memo_2 = forms.CharField(label='備註2：　', required=False)
#         memo_3 = forms.CharField(label='備註3：　', required=False)

#     user, DATA = R.user, readDATA(R)

#     default_projects = [p.project for p in DefaultProject.objects.filter(user=user)]
#     for i in default_projects:
#         i.short_plan_name = i.plan.name[:5] + '...'

#     form = searchForm()
#     projects_num = -1
#     projects = []
#     querystring = ''
#     INFO = {}
#     for k, v in R.GET.items(): INFO[k] = v
#     for k, v in R.POST.items(): INFO[k] = v
#     p_list = []
#     if INFO.get('submit', None):
#         form = searchForm(INFO)
#         querystring = '&'.join(['%s=%s'%(k, v) for k, v in INFO.items() if k != 'page'])
#         projects, projects_num, p_list = _SecretGarden(INFO)

#     for p in projects:
#         if FRCMUserGroup.objects.filter(project=p).count() > 0: p.frcm = True
#         else: p.frcm = False
#         try:
#             memo = Project_Secret_Memo.objects.get(project=p)
#             p.memo_1 = memo.memo_1
#             p.memo_2 = memo.memo_2
#             p.memo_3 = memo.memo_3
#         except: pass
#         countychasetime = list(CountyChaseTime.objects.all().order_by('id'))[-1]
#         if CountyChaseProjectOneToMany.objects.filter(countychasetime=countychasetime, project=p) > 0: p.chase = True
#         else: p.chase = False


#     for n, i in enumerate(projects):
#         i.short_plan_name = i.plan.name[:5] + '...'

#     if _ca(user=user, project='', project_id=0, right_type_value=u'刪除管考工程案'):
#         delete = True
#     else:
#         delete = False

#     plans = [['', '全部']]
#     for i in Plan.objects.filter(uplevel=None):
#         plans.append([i.id, '---'*i.rLevelNumber() + i.name])
#         for j in i.rSubPlanInList():
#             plans.append([j.id, '---'*j.rLevelNumber() + j.name])

#     t = get_template(os.path.join('project', 'secret_garden.html'))
#     html = t.render(RequestContext(R, {
#         'form': form,
#         'plans': plans,
#         'projects': projects,
#         'sortBy': INFO.get('sortBy', None) or 'year',
#         'page_list': makePageList(INFO.get('page', 1), projects_num, NUMPERPAGE),
#         'querystring': querystring,
#         'projects_num': projects_num,
#         'option' : _make_choose(),
#         'delete': delete,
#         'p_list': p_list,
#         }))
#     R.querystring = querystring
#     return HttpResponse(html)

# def _SecretGarden(INFO, user='', use_page=True):
#     if INFO.get('sortBy', None):
#         result = Project.objects.filter(deleter=None).order_by(INFO.get('sortBy', None))
#     else:
#         result = Project.objects.filter(deleter=None)

#     if INFO.get('bid_no', None) and INFO.get('bid_no', None) != '':
#         ids = []
#         for bid_no in re.split('[ ,]+', INFO.get('bid_no', None)):
#             ids.extend([i.id for i in result.filter(bid_no__icontains=bid_no)])
#         result = result.filter(id__in=ids)

#     if INFO.get('vouch_date_ub', None) and INFO.get('vouch_date_ub', None) != '':
#         vouch_date_ub = INFO.get('vouch_date_ub', None).replace('/', '-').replace('.', '-')
#         vouch_date_lb = INFO.get('vouch_date_lb', None).replace('/', '-').replace('.', '-')
#         ids = []
#         ids.extend([i.id for i in result.filter(vouch_date__gte=vouch_date_ub, vouch_date__lte=vouch_date_lb)])
#         result = result.filter(id__in=ids)

#     if INFO.get('name', None) and INFO.get('name', None) != '':
#         ids = []
#         for name in re.split('[ ,]+', INFO.get('name', None)):
#             ids.extend([i.id for i in result.filter(name__icontains=name)])
#         result = result.filter(id__in=ids)

#     if INFO.get('plan', None) and INFO.get('plan', None) != '':
#         plan = Plan.objects.get(id=INFO.get('plan', None))
#         if INFO.get('project_sub_type', None) == '1':
#             plan_ids = [plan.id] + [i.id for i in Plan.objects.get(id=INFO.get('plan', None)).rSubPlanInList()]
#             result = result.filter(plan__id__in=plan_ids)
#         else:
#             result = result.filter(plan = plan)

#     if INFO.get('purchase_type', None) and INFO.get('purchase_type', None) != '':
#         result = result.filter(purchase_type=Option.objects.get(id=INFO.get('purchase_type', None)))

#     if INFO.get('budget_sub_type', None) and INFO.get('budget_sub_type', None) != '':
#         result = result.filter(budget_sub_type=Option.objects.get(id=INFO.get('budget_sub_type', None)))

#     if INFO.get('undertake_type', None) and INFO.get('undertake_type', None) != '':
#         result = result.filter(undertake_type=Option.objects.get(id=INFO.get('undertake_type', None)))

#     if INFO.get('year', None) and INFO.get('year', None) != '':
#         result = result.filter(year=INFO.get('year', None))

#     if INFO.get('unit', None) and INFO.get('unit', None) != '':
#         unit = Unit.objects.get(id=INFO.get('unit', None))
#         result = result.filter(unit=unit)

#     if INFO.get('place', None) and INFO.get('place', None) != '':
#         place = Place.objects.get(id=INFO.get('place', None))
#         result = result.filter(place=place)

#     if INFO.get('chase', None) and INFO.get('chase', None) != '':
#         countychasetime = list(CountyChaseTime.objects.all().order_by('id'))[-1]
#         if INFO.get('chase', None) == 'unchase':
#             ids = [c.project.id for c in CountyChaseProjectOneToMany.objects.filter(countychasetime=countychasetime)]
#             result = result.exclude(id__in=ids)
#         elif INFO.get('chase', None) == 'chase_complete_check':
#             ids = [c.project.id for c in CountyChaseProjectOneToMany.objects.filter(countychasetime=countychasetime, complete=True, check=True)]
#             result = result.filter(id__in=ids)
#         elif INFO.get('chase', None) == 'chase_complete_uncheck':
#             ids = [c.project.id for c in CountyChaseProjectOneToMany.objects.filter(countychasetime=countychasetime, complete=True, check=False)]
#             result = result.filter(id__in=ids)
#         elif INFO.get('chase', None) == 'chase_uncomplete':
#             ids = [c.project.id for c in CountyChaseProjectOneToMany.objects.filter(countychasetime=countychasetime, complete=False, check=False)]
#             result = result.filter(id__in=ids)

#     secret_memo = Project_Secret_Memo.objects.all()
#     if INFO.get('memo_1', None) and INFO.get('memo_1', None) != '':
#         ids = []
#         for name in re.split('[ ,]+', INFO.get('memo_1', None)):
#             ids.extend([i.project.id for i in secret_memo.filter(memo_1__icontains=name)])
#         result = result.filter(id__in=ids)

#     if INFO.get('memo_2', None) and INFO.get('memo_2', None) != '':
#         ids = []
#         for name in re.split('[ ,]+', INFO.get('memo_2', None)):
#             ids.extend([i.project.id for i in secret_memo.filter(memo_2__icontains=name)])
#         result = result.filter(id__in=ids)

#     if INFO.get('memo_3', None) and INFO.get('memo_3', None) != '':
#         ids = []
#         for name in re.split('[ ,]+', INFO.get('memo_3', None)):
#             ids.extend([i.project.id for i in secret_memo.filter(memo_3__icontains=name)])
#         result = result.filter(id__in=ids)

#     if INFO.get('record_project_profiles', None):
#         record_project_profile_id = INFO.get('record_project_profiles')
#         try:
#             rpp = RecordProjectProfile.objects.get(id=record_project_profile_id)
#         except RecordProjectProfile.DoesNotExist:
#             pass
#         else:
#             result = result.filter(id__in=[p.id for p in rpp.projects.all()])

#     p_list = [int(i.id) for i in result]

#     result_num = len(result)
#     if not use_page:
#         projects = result[:]
#     else:
#         if not INFO.get('page', None): page = 1
#         else: page = int(INFO['page'])

#         projects = []
#         for order, u in enumerate(result[int((page-1)*NUMPERPAGE):int(page*NUMPERPAGE)]):
#             u.order = int((page-1)*NUMPERPAGE+order+1)
#             projects.append(u)

#     return projects, result_num, p_list




import xml.etree.cElementTree as ET
from cStringIO import StringIO
from pysimplesoap.server import SoapDispatcher, SOAPHandler
from pysimplesoap.client import SoapClient, SoapFault


def data_connect_project_for_aerc(special_connect_code='', year='', project_name=''):
    '''
    key值對應表
        ['id','工程id'], 
        ['name', '工程名稱'], 
        ['year', '年度'],
        ['plan_id', '所屬計畫id'],
        ['plan_name', '所屬計畫名稱'],
        ['place', '縣市'],
        ['location', '位置'],
        ['budget_sub_type', '會計科目'],
        ['bid_type', '招標方式'],
        ['sch_eng_do_start', '預定開工日期'],
        ['sch_eng_do_completion', '預定完工日期'],
        ['act_eng_do_start', '實際開工日期'],
        ['act_eng_do_completion', '實際完工日期'],
        ['eng', '監工主辦(遠端負責主辦)'],
        ['bid_no', '契約編號'],
        ['read_total_money', '契約金額'],
        ['contractor', '營造廠商名稱'],
        ['contractor_charge', '營造廠商負責人'],
        ['contractor_contacter_phone', '營造廠商電話'],
        ['total_money', '工程費'],
        ['rTotalProjectBudget', '工程預算'],
        ['rSelfLoad', '本署負擔'],
        ['rlocalMatchFund', '地方配合款'],
        ['rplanning_fee', '規劃費'],
        ['rcommissioned_research', '委託研究'],
        ['rdesign_bid', '設計決標金額'],
        ['rinspect_bid', '監造決標金額'],
        ['rconstruction_bid', '工程決標金額'],
        ['rpollution', '空污費'],
        ['rmanage', '工程管理費'],
        ['rsubsidy', '外水電補助費'],
        ['rother_defray', '其他費用'],
        ['fishing_port_or_aquaculture', '漁港別養殖區別', ['name': '名稱']],
        ['approved_plan', '核定日期'],
        ['all_progress', '進度資訊', ['date': '進度日期', 'schedul_progress_percent': '預定進度', 'actual_progress_percent': '實際進度' ,'memo': '施工狀況']],
    '''

    if special_connect_code != 'AeRC_es!$48519IiM':
        return False

    projects = Project.objects.filter(name=project_name, year=year, deleter=None)

    result = []
    for p in projects:
        data = {}
        CountyChaseProjectOneByOne.objects.get_or_create(project=p)
        p.obo = CountyChaseProjectOneByOne.objects.get(project=p)
        try:
            p.eng = base64.encodestring(FRCMUserGroup.objects.get(project=project, group__name__in=[u'負責主辦工程師', u'自辦主辦工程師']).user.user_profile.rName())
        except:
            p.eng = ''
        p.progresss = Progress.objects.filter(project=p).order_by('date')
        
        fields = [  ['p.id', 'id','工程id'], 
                    ['p.name', 'name', '工程名稱'], 
                    ['p.year', 'year', '年度'],
                    ['p.plan.id', 'plan_id', '所屬計畫id'],
                    ['p.plan.name', 'plan_name', '所屬計畫名稱'],
                    ['p.place.name', 'place', '縣市'],
                    ['p.location', 'location', '位置'],
                    ['p.budget_sub_type.value if p.budget_sub_type else ""', 'budget_sub_type', '會計科目'],
                    ['p.bid_type.value if p.bid_type else ""', 'bid_type', '招標方式'],
                    ['p.obo.sch_eng_do_start', 'sch_eng_do_start', '預定開工日期'],
                    ['p.obo.sch_eng_do_completion', 'sch_eng_do_completion', '預定完工日期'],
                    ['p.obo.act_eng_do_start', 'act_eng_do_start', '實際開工日期'],
                    ['p.obo.act_eng_do_completion', 'act_eng_do_completion', '實際完工日期'],
                    ['p.eng', 'eng', '監工主辦(遠端負責主辦)'],
                    ['p.bid_no', 'bid_no', '契約編號'],
                    ['p.read_total_money()', 'read_total_money', '契約金額'],
                    ['p.contractor.name if p.contractor else ""', 'contractor', '營造廠商名稱'],
                    ['p.contractor_charge', 'contractor_charge', '營造廠商負責人'],
                    ['p.contractor_contacter_phone', 'contractor_contacter_phone', '營造廠商電話'],
                    ['p.read_total_money()', 'total_money', '工程費'],
                    ['p.fund_set.get().rTotalProjectBudget()', 'rTotalProjectBudget', '工程預算'],
                    ['p.fund_set.get().rSelfLoad()', 'rSelfLoad', '本署負擔'],
                    ['p.fund_set.get().rlocalMatchFund()', 'rlocalMatchFund', '地方配合款'],
                    ['p.rplanning_fee()', 'rplanning_fee', '規劃費'],
                    ['p.rcommissioned_research()', 'rcommissioned_research', '委託研究'],
                    ['p.rdesign_bid()', 'rdesign_bid', '設計決標金額'],
                    ['p.rinspect_bid()', 'rinspect_bid', '監造決標金額'],
                    ['p.rconstruction_bid()', 'rconstruction_bid', '工程決標金額'],
                    ['p.rpollution()', 'rpollution', '空污費'],
                    ['p.rmanage()', 'rmanage', '工程管理費'],
                    ['p.rsubsidy()', 'rsubsidy', '外水電補助費'],
                    ['p.rother_defray()', 'rother_defray', '其他費用'],
                    ]
        for f in fields:
            data[f[1]] = base64.encodestring(str(eval(f[0])))

        data['fishing_port_or_aquaculture'] = []
        for port in p.fishing_port.all():
            data['fishing_port_or_aquaculture'].append({'port_or_aquaculture': {'name': base64.encodestring(port.name)}})
        for port in p.aquaculture.all():
            data['fishing_port_or_aquaculture'].append({'port_or_aquaculture': {'name': base64.encodestring(port.name)}})
        
        if p.purchase_type.value == '工程':
            if p.obo.act_eng_plan_approved_plan:
                data['approved_plan'] = base64.encodestring(str(p.obo.act_eng_plan_approved_plan))
            else:
                data['approved_plan'] = base64.encodestring(str(p.obo.sch_eng_plan_approved_plan) if p.obo.sch_eng_plan_approved_plan else 'None')
        else:
            if p.obo.act_ser_approved_plan:
                data['approved_plan'] = base64.encodestring(str(p.obo.act_ser_approved_plan))
            else:
                data['approved_plan'] = base64.encodestring(str(p.obo.sch_ser_approved_plan) if p.obo.sch_ser_approved_plan else 'None')

        data['all_progress'] = []
        for pro in p.progresss:
            data['all_progress'].append(
                {'progress': 
                    {
                        'date': base64.encodestring(str(pro.date)), 
                        'schedul_progress_percent': base64.encodestring(str(pro.schedul_progress_percent)),
                        'actual_progress_percent': base64.encodestring(str(pro.actual_progress_percent)),
                        'memo': base64.encodestring(str(pro.s_memo if pro.s_memo else '') + str(pro.r_memo if pro.r_memo else ''))
                    }
                }
            )

        result.append({'project': data})

    return result

def data_connect_plan_for_aerc(special_connect_code=''):
    '''
    key值對應表
        ['id', '編號id'],
        ['name', '計畫名稱'],
        ['code', '計畫代號'],
        ['p.no', '計畫編號'],
        ['budget_type', '預算類別'],
        ['uplevel_id', '上層計畫id'],
        ['note', '計畫說明'],
    '''

    if special_connect_code != 'AeRC_es!$48519IiM':
        return False
        
    plans = []
    for i in Plan.objects.filter(uplevel=None):
        plans.append(i)
        for j in i.rSubPlanInList():
            plans.append(j)
    
    result = []
    for p in plans:
        data = {}
        fields = [  ['p.id', 'id', '編號id'],
                    ['p.name', 'name', '計畫名稱'],
                    ['p.code', 'code', '計畫代號'],
                    ['p.no', 'no', '計畫編號'],
                    ['p.budget_type.value', 'budget_type', '預算類別'],
                    ['p.uplevel.id if p.uplevel else ""', 'uplevel_id', '上層計畫id'],
                    ['p.note', 'note', '計畫說明'],
                    ]
        for f in fields:
            data[f[1]] = base64.encodestring(str(eval(f[0])))
        result.append({'plan': data})
    return result


dispatcher = SoapDispatcher(
    'my_dispatcher',
    location = "http://fes.fa.gov.tw/project/data_connect_for_aerc",
    action = 'http://fes.fa.gov.tw/project/data_connect_for_aerc',
    namespace = "http://example.com/sample.wsdl",
    prefix="ns0",
    trace = True,
    ns = True)

# register func
dispatcher.register_function('data_connect_project_for_aerc', data_connect_project_for_aerc,
    returns={'result': [{'project': {
        "id": str,
        "name": str,
        "year": str,
        "plan_id": str,
        "plan_name": str,
        "place": str,
        "location": str,
        "budget_sub_type": str,
        "bid_type": str,
        "sch_eng_do_start": str,
        "sch_eng_do_completion": str,
        "act_eng_do_start": str,
        "act_eng_do_completion": str,
        "eng": str,
        "bid_no": str,
        "read_total_money": str,
        "contractor": str,
        "contractor_charge": str,
        "contractor_contacter_phone": str,
        "total_money": str,
        "rTotalProjectBudget": str,
        "rSelfLoad": str,
        "rlocalMatchFund": str,
        "rplanning_fee": str,
        "rcommissioned_research": str,
        "rdesign_bid": str,
        "rinspect_bid": str,
        "rconstruction_bid": str,
        "rpollution": str,
        "rmanage": str,
        "rsubsidy": str,
        "rother_defray": str,
        "approved_plan": str,
        "fishing_port_or_aquaculture": [{'port_or_aquaculture': {'name': str}}],
        "all_progress": [{'progress': {'date': str, 'schedul_progress_percent': str,
                        'actual_progress_percent': str, 'memo': str}}]
    }}]}, 
    args={'special_connect_code': str, 'year': str, 'project_name': str})

dispatcher.register_function('data_connect_plan_for_aerc', data_connect_plan_for_aerc,
    returns={'result': [{'plan': {
        "id": str,
        "name": str,
        "code": str,
        "no": str,
        "budget_type": str,
        "uplevel_id": str,
        "note": str
    }}]}, 
    args={'special_connect_code': str})


@csrf_exempt
def dispatcher_handler(request):
    if request.method == "POST":
        response = HttpResponse(content_type="text/xml")
        response.write(dispatcher.dispatch(request.body))
    else:
        response = HttpResponse(content_type="text/xml")
        response.write(dispatcher.wsdl())
    response['Content-length'] = str(len(response.content))
    return response
