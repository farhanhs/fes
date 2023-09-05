# -*- coding: utf-8 -*-
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
from django.core.servers.basehttp import FileWrapper
from django.utils.http import urlquote

from common.models import Log
from general.models import Place, Unit, UNITS, LOAD_UNITS
from common.lib import find_sub_level, find_sub, nocache_response, md5password, readDATA, verifyOK, makePageList, makeFileByWordExcel
from fishuser.models import Option
from fishuser.models import UserProfile
from fishuser.models import LoginHistory
from fishuser.models import WrongLogin
from fishuser.models import DocumentOfProjectModels
from fishuser.models import Plan
from fishuser.models import PlanBudget
from fishuser.models import Budget
from fishuser.models import Draft_Project
from fishuser.models import Project
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

from project.models import Option2
from project.models import RecordProjectProfile
from project.models import ExportCustomReport
from project.models import ReportField
from project.models import ExportCustomReportField

from supervise.models import Option
from supervise.models import Guide
from supervise.models import SuperviseCase
from supervise.models import ErrorLevel
from supervise.models import ErrorContent
from supervise.models import Error
from supervise.models import ErrorImprovePhoto
from supervise.models import Edit
from supervise.models import ErrorPhotoFile
from supervise.models import PCC_Project
from supervise.models import PCC_sync_record
from supervise.models import CaseFile, ErrorImproveFile

from pccmating.models import Project as PCCProject
from pccmating.sync import getProjectInfo

from harbor.models import FishingPort
from harbor.models import Aquaculture

from settings import ROOT
from settings import CAN_VIEW_BUG_PAGE_IPS
from settings import NUMPERPAGE

#from PIL.Image import split
import decimal
import calendar, math
import os, random, json, re, datetime

from guardian.shortcuts import assign
from guardian.shortcuts import remove_perm
from guardian.shortcuts import get_perms

from pccmating.sync import *
from pccmating.models import Cofiguration
from pccmating.models import Project as PCCProject

from urllib import urlencode
from urllib2 import Request, urlopen
import xlsxwriter
from cStringIO import StringIO

from django.conf import settings
ROOT = settings.ROOT

TODAY = lambda: datetime.date.today()
NOW = lambda: datetime.datetime.now()
TAIWAN = Place.objects.get(name=u'臺灣地區')
places = [TAIWAN] + list(Place.objects.filter(uplevel=TAIWAN).order_by('id'))
north_place_name = [u'臺北市', u'新北市', u'基隆市', u'桃園市', u'宜蘭縣', u'花蓮縣', u'新竹市', u'新竹縣', u'苗栗縣', u'臺中市', u'金門縣', u'連江縣',]
south_place_name = [u'彰化縣', u'雲林縣', u'嘉義市', u'嘉義縣', u'臺南市', u'高雄市', u'屏東縣', u'臺東縣', u'澎湖縣', u'南投縣', ]
years = [y-1911 for y in xrange(2008, TODAY().year+5)]
years.reverse()
this_year = TODAY().year - 1911
units = LOAD_UNITS()[:]


#轉移開始------------------------------------------------------------------

def _make_choose():
    options = Option.objects.all()
    chooses = {}
    for i in options:
        if chooses.has_key(i.swarm):
            chooses[i.swarm].append(i)
        else:
            chooses[i.swarm] = [i]
    return chooses


#搜尋頁面
@login_required
def search(R):
    if not R.user.has_perm('fishuser.top_menu_supervise_system'):
        # 沒有 "第一層選單_督導系統"
        return HttpResponseRedirect('/')


    t = get_template(os.path.join('supervise', 'zh-tw', 'search.html'))
    html = t.render(RequestContext(R,{
            'user': R.user,
            'units': units,
            'places': places,
            'toppage_name': u'督導系統',
            'subpage_name': u'搜尋',
        }))
    return HttpResponse(html)


#搜尋頁面
@login_required
def search_unit(R):
    if not R.user.has_perm('fishuser.top_menu_supervise_system'):
        # 沒有 "第一層選單_督導系統"
        return HttpResponseRedirect('/')

    condition = R.GET

    data = []
    if condition.get('start_date', '') and condition.get('end_date', ''):
        results = SuperviseCase.objects.filter(date__gte=condition['start_date'], date__lte=condition['end_date']).order_by('-date')
        results_score = results.exclude(score__lte=1)
        analysis = {
            'total': {
                'num': results.count(),
                'results': results,
                'avarage': round(float(str(sum([i.score for i in results_score]))) / results_score.count(), 2) if results_score else 0,
                'A': 0,
                'B': 0,
                'C': 0,
                'D': 0,
                'E': 0,
                'F': 0,
            }
        }
        for r in results:
            if r.score >= 90:
                analysis['total']['A'] += 1
            elif r.score >= 80:
                analysis['total']['B'] += 1
            elif r.score >= 70:
                analysis['total']['C'] += 1
            elif r.score >= 60:
                analysis['total']['D'] += 1
            elif r.score > 1:
                analysis['total']['E'] += 1
            else:
                analysis['total']['F'] += 1

        if condition['unit_type'] == 'subordinate_agencies_unit':
            new_units = []
            for u in units:
                u.unit_results = results.filter(subordinate_agencies_unit=u)
                if u.unit_results:
                    new_units.append(u)
                    print u.name, u.unit_results.count()
        elif condition['unit_type'] == 'project_organizer_agencies':
            names = list(set([c.project_organizer_agencies for c in results if c.project_organizer_agencies]))
            names.sort()
            new_units = []
            for name in names:
                u = Unit(name=name)
                u.unit_results = results.filter(project_organizer_agencies=name)
                new_units.append(u)
        elif condition['unit_type'] == 'project_manage_unit':
            names = list(set([c.project_manage_unit for c in results if c.project_manage_unit]))
            names.sort()
            new_units = []
            for name in names:
                u = Unit(name=name)
                u.unit_results = results.filter(project_manage_unit=name)
                new_units.append(u)
        elif condition['unit_type'] == 'designer':
            names = list(set([c.designer for c in results if c.designer]))
            names.sort()
            new_units = []
            for name in names:
                u = Unit(name=name)
                u.unit_results = results.filter(designer=name)
                new_units.append(u)
        elif condition['unit_type'] == 'inspector':
            names = list(set([c.inspector for c in results if c.inspector]))
            names.sort()
            new_units = []
            for name in names:
                u = Unit(name=name)
                u.unit_results = results.filter(inspector=name)
                new_units.append(u)
        elif condition['unit_type'] == 'construct':
            names = list(set([c.construct for c in results if c.construct]))
            names.sort()
            new_units = []
            for name in names:
                u = Unit(name=name)
                u.unit_results = results.filter(construct=name)
                new_units.append(u)

        for u in new_units:
            unit_results_score = u.unit_results.exclude(score__lte=1)
            tmp = {
                'name': u.name,
                'results': u.unit_results,
                'num': u.unit_results.count(),
                'avarage': round(float(str(sum([i.score for i in unit_results_score]))) / unit_results_score.count(), 2) if unit_results_score else 0,
                'A': 0,
                'B': 0,
                'C': 0,
                'D': 0,
                'E': 0,
                'F': 0,
            }
            for r in u.unit_results:
                if r.score >= 90:
                    tmp['A'] += 1
                elif r.score >= 80:
                    tmp['B'] += 1
                elif r.score >= 70:
                    tmp['C'] += 1
                elif r.score >= 60:
                    tmp['D'] += 1
                elif r.score > 1:
                    tmp['E'] += 1
                else:
                    tmp['F'] += 1
            data.append(tmp)


        def sort_by_num(a, b):
            if a['num'] < b['num']: return 1
            elif a['num'] == b['num']:
                if a['avarage'] < b['avarage']: return 1
                else: return -1
            else: return -1

        data.sort(sort_by_num)

        t = get_template(os.path.join('supervise', 'zh-tw', 'search_unit.html'))
        html = t.render(RequestContext(R,{
                'user': R.user,
                'units': new_units,
                'data': data,
                'analysis': analysis,
                'unit_type': condition['unit_type'],
                'start_date': condition['start_date'],
                'end_date': condition['end_date'],
                'toppage_name': u'督導系統',
                'subpage_name': u'搜尋廠商',
            }))
        return HttpResponse(html)

    today = TODAY()
    start_date = datetime.date(day=1, month=1, year=today.year)
    end_date = datetime.date(day=31, month=12, year=today.year)

    t = get_template(os.path.join('supervise', 'zh-tw', 'search_unit.html'))
    html = t.render(RequestContext(R,{
            'user': R.user,
            'start_date': str(start_date),
            'end_date': str(end_date),
            'unit_type': "inspector",
            'toppage_name': u'督導系統',
            'subpage_name': u'搜尋廠商',
        }))
    return HttpResponse(html)


#統計圖表
@login_required
def statistics_chart(R, **kw):
    if not R.user.has_perm('fishuser.top_menu_supervise_system'):
        # 沒有 "第一層選單_督導系統"
        return HttpResponseRedirect('/')

    date_from = '%s-01-01' % (NOW().year)
    d = calendar.monthrange(NOW().year, 12)
    date_to = '%s-%s-%s' % (NOW().year, 12, d[1])

    places = [Place(name=u"北部辦公室"), Place(name=u"南部辦公室")]
    for north in north_place_name:
        p = Place.objects.get(name=north)
        p.north = True
        places.append(p)
    for south in south_place_name:
        p = Place.objects.get(name=south)
        p.north = False
        places.append(p)

    t = get_template(os.path.join('supervise', 'zh-tw', 'statistics_chart.html'))
    html = t.render(RequestContext(R,{
            'user': R.user,
            'date_from': date_from,
            'date_to': date_to,
            'this_year': this_year,
            'toppage_name': u'督導系統',
            'subpage_name': u'統計圖表',
        }))
    return HttpResponse(html)

#統計圖表
@login_required
def statistics_chart_a(R, **kw):
    if not R.user.has_perm('fishuser.top_menu_supervise_system'):
        # 沒有 "第一層選單_督導系統"
        return HttpResponseRedirect('/')
    date_from = '%s-01-01' % (NOW().year)
    d = calendar.monthrange(NOW().year, 12)
    date_to = '%s-%s-%s' % (NOW().year, 12, d[1])


    t = get_template(os.path.join('supervise', 'zh-tw', 'statistics_chart_a.html'))
    html = t.render(RequestContext(R,{
            'date_from': date_from,
            'date_to': date_to,
            'toppage_name': u'督導系統',
            'subpage_name': u'完工之工程案的總體效益表',
        }))
    return HttpResponse(html)
#統計圖表
@login_required
def get_chart_data(R, **kw):

    date_from = R.POST.get('date_from', TODAY())
    date_to = R.POST.get('date_to', TODAY())
    chart_name = R.POST.get('chart_name', 'pie-1')
    sub_type = R.POST.get('sub_type', '1')
    
    def sort_by_num(a, b):
        if a.num < b.num: return 1
        else: return -1

    if chart_name == 'pie-1':
        #圓餅圖-缺失分類次數統計
        cases = SuperviseCase.objects.filter(date__gte=date_from, date__lte=date_to)
        data = {
                'datasets': [
                                {
                                    'data': [],
                                    'backgroundColor': []
                                }
                            ],
                'labels': []
            }
        errors = Error.objects.filter(case__in=cases)
        if not errors:
            return HttpResponse(json.dumps({'status': False, 'msg': u'此期間無數據'}))

        if sub_type == '1':
            ecs_01 = errors.filter(ec__no__startswith='4.01') #工程主辦機關
            ecs_02 = errors.filter(ec__no__startswith='4.02') #監造單位
            ecs_03 = errors.filter(ec__no__startswith='4.03') #承攬廠商
            titles = [
                u'　工程主辦機關　', 
                u'　監造單位　', 
                u'　承攬廠商　', 
            ]

            for n_ecs, ecs in enumerate([ecs_01, ecs_02, ecs_03]):
                data['datasets'][0]['data'].append(ecs.count())
                data['labels'].append(titles[n_ecs])

        elif sub_type == '2':
            ecs_04 = errors.filter(ec__no__startswith='5.0') #強度Ι－混凝土、鋼筋(構)、模板、土方、結構體、裝修、雜項等：（W1）
            ecs_05 = errors.filter(ec__no__startswith='5.10') #強度II－材料設備檢驗與管制（W2）
            ecs_06 = errors.filter(Q(ec__no__startswith='5.14')|Q(ec__no__startswith='5.17')).distinct() #安全（W3）
            ecs_07 = errors.filter(ec__no__startswith='6.') #施工進度
            ecs_08 = errors.filter(ec__no__startswith='7.') #規劃設計

            titles = [
                u'　混凝土、鋼筋(構)...等　', 
                u'　材料設備檢驗與管制　', 
                u'　安全　',
                u'　施工進度　',
                u'　規劃設計　',
            ]

            for n_ecs, ecs in enumerate([ecs_04, ecs_05, ecs_06, ecs_07, ecs_08]):
                data['datasets'][0]['data'].append(ecs.count())
                data['labels'].append(titles[n_ecs])

        data['sub_type'] = sub_type
        return HttpResponse(json.dumps({'status': True, 'data': data, 'title': [u'工程督導-分類缺失次數統計', u'(%s ~ %s)' % (date_from, date_to)]}))

    elif chart_name == 'histogram-1':
        #柱狀圖-缺失分類次數統計
        cases = SuperviseCase.objects.filter(date__gte=date_from, date__lte=date_to)
        data = {
                'labels': [],
                'datasets': [
                    {
                        'label': u'品質管理制度',
                        'backgroundColor': '#3FB2FF',
                        'borderWidth': 1,
                        'stack': 'Stack 0',
                        'data': []
                    },
                    {
                        'label': u'施工品質',
                        'backgroundColor': '#FFB979',
                        'borderWidth': 1,
                        'stack': 'Stack 0',
                        'data': []
                    },
                    {
                        'label': u'施工進度',
                        'backgroundColor': '#A3CC66',
                        'borderWidth': 1,
                        'stack': 'Stack 0',
                        'data': []
                    },
                    {
                        'label': u'規劃設計',
                        'backgroundColor': '#EFB6FF',
                        'borderWidth': 1,
                        'stack': 'Stack 0',
                        'data': []
                    }
                ]
            }

        errors = Error.objects.filter(case__in=cases)
        if not errors:
            return HttpResponse(json.dumps({'status': False, 'msg': u'此期間無數據'}))

        if sub_type == '1':
            ecs_01 = errors.filter(ec__no__startswith='4.01') #工程主辦機關
            ecs_02 = errors.filter(ec__no__startswith='4.02') #監造單位
            ecs_03 = errors.filter(ec__no__startswith='4.03') #承攬廠商

            titles = [
                u'工程主辦機關', 
                u'監造單位', 
                u'承攬廠商', 
            ]

            data['labels'] = titles
            data['datasets'][0]['data'] = [ecs_01.count(), ecs_02.count(), ecs_03.count()]
            data['datasets'].pop(3)
            data['datasets'].pop(2)
            data['datasets'].pop(1)
            left_max_num = max([ecs_01.count(), ecs_02.count(), ecs_03.count()])
            while left_max_num % 10 != 0:
                left_max_num += 1

        elif sub_type == '2':
            ecs_04 = errors.filter(ec__no__startswith='5.0') #強度Ι－混凝土、鋼筋(構)、模板、土方、結構體、裝修、雜項等：（W1）
            ecs_05 = errors.filter(ec__no__startswith='5.10') #強度II－材料設備檢驗與管制（W2）
            ecs_06 = errors.filter(Q(ec__no__startswith='5.14')|Q(ec__no__startswith='5.17')).distinct() #安全（W3）
            ecs_07 = errors.filter(ec__no__startswith='6.') #施工進度
            ecs_08 = errors.filter(ec__no__startswith='7.') #規劃設計

            titles = [
                u'混凝土、鋼筋(構)...等', 
                u'材料設備檢驗與管制', 
                u'安全',
                u'施工進度',
                u'規劃設計',
            ]

            data['labels'] = titles
            data['datasets'][1]['data'] = [ecs_04.count(), ecs_05.count(), ecs_06.count(), "", ""]
            data['datasets'][2]['data'] = ["", "", "", ecs_07.count(), ""]
            data['datasets'][3]['data'] = ["", "", "", "", ecs_08.count()]
            data['datasets'].pop(0)
            left_max_num = max([ecs_04.count(), ecs_05.count(), ecs_06.count()])
            while left_max_num % 10 != 0:
                left_max_num += 1

        return HttpResponse(json.dumps({'status': True, 'data': data, 'left_max_num': left_max_num, 'title': [u'工程督導-分類缺失次數統計', u'(%s ~ %s)' % (date_from, date_to)]}))

    elif chart_name in ['histogram-2', 'histogram-3', 'histogram-4']:
        #柱狀圖-主辦機關/監造單位/承攬廠商 缺失次數統計 
        cases = SuperviseCase.objects.filter(date__gte=date_from, date__lte=date_to)

        data = []
        errors = Error.objects.filter(case__in=cases)
        if not errors:
            return HttpResponse(json.dumps({'status': False, 'msg': u'此期間無數據'}))

        errors_no = set([i.ec.no for i in errors])
        if chart_name == 'histogram-2':
            ecs = ErrorContent.objects.filter(no__startswith='4.01', no__in=errors_no).order_by('no') #工程主辦機關
            title = u'工程督導-主辦機關缺失件數排名統計'
        elif chart_name == 'histogram-3':
            ecs = ErrorContent.objects.filter(no__startswith='4.02', no__in=errors_no).order_by('no') #監造單位
            title = u'工程督導-監造單位缺失件數排名統計'
        elif chart_name == 'histogram-4':
            ecs = ErrorContent.objects.filter(no__startswith='4.03', no__in=errors_no).order_by('no') #承攬廠商
            title = u'工程督導-承攬廠商缺失件數排名統計'

        for ec in ecs:
            ec.case_ids = set([i.case.id for i in errors.filter(ec__no=ec.no)])
            ec.num = len(ec.case_ids)

        ecs = list(ecs)
        ecs.sort(sort_by_num)
        data = {
                'labels': [],
                'datasets': [
                    {
                        'label': u'缺失件數',
                        'backgroundColor': '#5B79FF',
                        'borderWidth': 1,
                        'data': []
                    }
                ]
            }
        
        for ec in ecs:
            if ec.num:
                data['labels'].append(ec.no)
                data['datasets'][0]['data'].append(ec.num)

        total_num = sum(data['datasets'][0]['data'])
        left_max_num = max(data['datasets'][0]['data'])
        while left_max_num % 5 != 0:
            left_max_num += 1
        right_max_num = math.ceil(left_max_num*100. / total_num)

        return HttpResponse(json.dumps({'status': True, 'data': data, 'left_max_num': left_max_num, 'right_max_num': right_max_num, 'title': [title, u'(%s ~ %s)' % (date_from, date_to)]}))


    elif chart_name == 'histogram-5':
        #柱狀圖-施工缺失(品質、進度、規劃設計)次數統計
        cases = SuperviseCase.objects.filter(date__gte=date_from, date__lte=date_to)
        title = u'工程督導-施工缺失(品質、進度、規劃設計)次數排名統計'

        tmp = []
        errors = Error.objects.filter(case__in=cases)
        if not errors:
            return HttpResponse(json.dumps({'status': False, 'msg': u'此期間無數據'}))

        error_contents = [
            ["5.01", u"混凝土施工"],
            ["5.02", u"鋼筋施工"],
            ["5.03", u"模板施工"],
            ["5.04", u"鋼構施工"],
            ["5.05", u"環境生態保育"],
            ["5.06", u"土方工程施工"],
            ["5.07", u"工程施工"],
            ["5.08", u"裝修雜項工程施工"],
            ["5.09", u"工地管理(不含進度管理)"],
            ["5.10", u"檢驗審查紀錄"],
            ["5.14", u"工地職業安全衛生"],
            ["5.15", u"工區交通維持及安全管制措施"],
            ["5.16", u"汛期工地防災減災措施"],
            ["5.17", u"功能及節能減碳"],
            ["6.01", u"施工進度管理"],
            ["7.01", u"規劃設計有安全性不良情事"],
            ["7.02", u"規劃設計有施工性不良情事"],
            ["7.03", u"規劃設計有維護性不良情事"],
            ["7.04", u"公眾使用空間之規劃設計未針對性別差異於安全性、友善性或便利性作適當考量"]
        ]
        for ec in error_contents:
            code = ec[0]
            errs = errors.filter(ec__no__startswith=code)
            if errs:
                tmp.append([errs.count(), ec])

        tmp.sort()
        tmp.reverse()

        data = {
                'labels': [],
                'datasets': [
                    {
                        'label': u'缺失次數',
                        'backgroundColor': '#5B79FF',
                        'borderWidth': 1,
                        'data': []
                    }
                ]
            }
        
        for t in tmp:
            data['labels'].append(u'%s %s' % (t[1][0], t[1][1]))
            data['datasets'][0]['data'].append(t[0])

        total_num = sum(data['datasets'][0]['data'])
        left_max_num = max(data['datasets'][0]['data'])
        while left_max_num % 5 != 0:
            left_max_num += 1
        right_max_num = math.ceil(left_max_num*100. / total_num)

        return HttpResponse(json.dumps({'status': True, 'data': data, 'left_max_num': left_max_num, 'right_max_num': right_max_num, 'title': [title, u'(%s ~ %s)' % (date_from, date_to)]}))



#統計表格
@login_required
def statistics(R, **kw):
    if not R.user.has_perm('fishuser.top_menu_supervise_system'):
        # 沒有 "第一層選單_督導系統"
        return HttpResponseRedirect('/')

    table_id = kw.get('table_id', '1')
    date_from = kw.get('date_from', 'this_year')
    date_to = kw.get('date_to', 'this_year')
    if date_from == 'this_year':
        date_from = '%s-%s-%s' % (NOW().year, '01', '01')
    if date_to == 'this_year':
        d = calendar.monthrange(NOW().year, 12)
        date_to = '%s-%s-%s' % (NOW().year, 12, d[1])

    places = [Place(name=u"北部辦公室"), Place(name=u"南部辦公室")]
    for north in north_place_name:
        p = Place.objects.get(name=north)
        p.north = True
        places.append(p)
    for south in south_place_name:
        p = Place.objects.get(name=south)
        p.north = False
        places.append(p)

    data, subpage_name = eval("make_statistics_%s(date_from='%s', date_to='%s', places=places)" % (table_id, date_from, date_to))

    t = get_template(os.path.join('supervise', 'zh-tw', 'statisticstable_%s.html' % table_id))
    html = t.render(RequestContext(R,{
            'user': R.user,
            'data': data,
            'date_from': date_from,
            'date_to': date_to,
            'this_year': this_year,
            'toppage_name': u'督導系統',
            'subpage_name': subpage_name,
        }))
    return HttpResponse(html)



#統計表格 - 單位-分數-件數
def make_statistics_1(date_from='', date_to='', places=[]):
    subpage_name = u'單位-分數-件數'
    types = [u'85(含)分以上', u'80(含)~85分', u'75(含)~80分', u'70(含)~75分', u'70(不含)分以下', u'不評分']

    cases = SuperviseCase.objects.filter(date__gte=date_from, date__lte=date_to)

    class data: pass
    data.num = cases.count()
    data.places = places
    data.over_85, data.range_80_85, data.range_75_80, data.range_70_75, data.under_70, data.no_score, data.sum = [], [], [], [], [], [], []
    data.A, data.B, data.C, data.D, data.E = [], [], [], [], []
    for n, p in enumerate(places):
        if n == 0:
            temp_cases = cases.filter(project_organizer_agencies__contains=u'漁業署', place__name__in=north_place_name)
        elif n == 1:
            temp_cases = cases.filter(project_organizer_agencies__contains=u'漁業署', place__name__in=south_place_name)
        else:
            temp_cases = cases.filter(place=p).exclude(project_organizer_agencies__contains='漁業署')
        
        data.over_85.append(temp_cases.filter(score__gte=85))
        data.range_80_85.append(temp_cases.filter(score__gte=80, score__lt=85))
        data.range_75_80.append(temp_cases.filter(score__gte=75, score__lt=80))
        data.range_70_75.append(temp_cases.filter(score__gte=70, score__lt=75))
        data.under_70.append(temp_cases.filter(score__gte=1, score__lt=70))
        data.no_score.append(temp_cases.filter(score=0))
        data.A.append(temp_cases.filter(score__gte=90))
        data.B.append(temp_cases.filter(score__gte=80, score__lt=90))
        data.C.append(temp_cases.filter(score__gte=70, score__lt=80))
        data.D.append(temp_cases.filter(score__gte=60, score__lt=70))
        data.E.append(temp_cases.filter(score__gte=1, score__lt=60))

        data.sum.append(temp_cases)

    data.over_85.append(cases.filter(score__gte=85))
    data.range_80_85.append(cases.filter(score__gte=80, score__lt=85))
    data.range_75_80.append(cases.filter(score__gte=75, score__lt=80))
    data.range_70_75.append(cases.filter(score__gte=70, score__lt=75))
    data.under_70.append(cases.filter(score__gte=1, score__lt=70))
    data.no_score.append(cases.filter(score=0))
    data.A.append(cases.filter(score__gte=90))
    data.B.append(cases.filter(score__gte=80, score__lt=90))
    data.C.append(cases.filter(score__gte=70, score__lt=80))
    data.D.append(cases.filter(score__gte=60, score__lt=70))
    data.E.append(cases.filter(score__gte=1, score__lt=60))

    data.sum.append(cases)

    return data, subpage_name


#統計表格 -  單位-扣點 
def make_statistics_2(date_from='', date_to='', places=[]):
    subpage_name = u'單位-扣點'
    types = [u'主辦扣點', u'專案管理扣點', u'監造扣點', u'營造扣點']
    
    cases = SuperviseCase.objects.filter(date__gte=date_from, date__lte=date_to)

    class data: pass
    data.num = cases.count()
    data.places = places
    data.organizer_deduction, data.project_manage_deduction, data.inspector_deduction, data.construct_deduction = [], [], [], []

    for n, p in enumerate(places):
        if n == 0:
            temp_cases = cases.filter(project_organizer_agencies__contains=u'漁業署', place__name__in=north_place_name)
        elif n == 1:
            temp_cases = cases.filter(project_organizer_agencies__contains=u'漁業署', place__name__in=south_place_name)
        else:
            temp_cases = cases.filter(place=p).exclude(project_organizer_agencies__contains='漁業署')
        data.organizer_deduction.append([sum([i.organizer_deduction for i in temp_cases.filter(organizer_deduction__gt=0)]), temp_cases.filter(organizer_deduction__gt=0)])
        data.project_manage_deduction.append([sum([i.project_manage_deduction for i in temp_cases.filter(project_manage_deduction__gt=0)]), temp_cases.filter(project_manage_deduction__gt=0)])
        data.inspector_deduction.append([sum([i.inspector_deduction for i in temp_cases.filter(inspector_deduction__gt=0)]), temp_cases.filter(inspector_deduction__gt=0)])
        data.construct_deduction.append([sum([i.construct_deduction for i in temp_cases.filter(construct_deduction__gt=0)]), temp_cases.filter(construct_deduction__gt=0)])

    data.organizer_deduction.append([sum([i.organizer_deduction for i in cases.filter(organizer_deduction__gt=0)]), cases.filter(organizer_deduction__gt=0)])
    data.project_manage_deduction.append([sum([i.project_manage_deduction for i in cases.filter(project_manage_deduction__gt=0)]), cases.filter(project_manage_deduction__gt=0)])
    data.inspector_deduction.append([sum([i.inspector_deduction for i in cases.filter(inspector_deduction__gt=0)]), cases.filter(inspector_deduction__gt=0)])
    data.construct_deduction.append([sum([i.construct_deduction for i in cases.filter(construct_deduction__gt=0)]), cases.filter(construct_deduction__gt=0)])

    return data, subpage_name


#統計表格 -  單位-缺失排名
def make_statistics_3(date_from='', date_to='', places=[]):
    subpage_name = u'單位-缺失排名'
    
    cases = SuperviseCase.objects.filter(date__gte=date_from, date__lte=date_to)
        
    def sort_by_times(a, b):
        if a.times < b.times: return 1
        else: return -1

    class data: pass
    data.num = cases.count()
    data.places = places
    data.range10 = range(1, 11)
    for n, p in enumerate(data.places):
        if n == 0:
            temp_cases = cases.filter(project_organizer_agencies__contains=u'漁業署', place__name__in=north_place_name)
        elif n == 1:
            temp_cases = cases.filter(project_organizer_agencies__contains=u'漁業署', place__name__in=south_place_name)
        else:
            temp_cases = cases.filter(place=p).exclude(project_organizer_agencies__contains='漁業署')
        p.errors = []
        all_errors = Error.objects.filter(case__in=temp_cases)
        all_ecs_id = [e.ec.id for e in all_errors]
        ecs = ErrorContent.objects.filter(id__in=all_ecs_id)
        
        for ec in ecs:
            if ec not in p.errors:
                ec.cases = temp_cases.filter(id__in=[i.case.id for i in all_errors.filter(ec=ec)])
                ec.times = all_errors.filter(ec=ec).count()
                p.errors.append(ec)
        p.errors.sort(sort_by_times)
        if len(p.errors) >= 10:
            p.errors = p.errors[:10]

    return data, subpage_name


#統計表格 - 單位-金額-件數
def make_statistics_4(date_from='', date_to='', places=[]):
    subpage_name = u'單位-金額-件數'
    types = [u'超過1億元', u'1億~5000萬', u'5000萬~2500萬', u'2500萬~1000萬', u'1000萬~500萬', u'500萬~250萬', u'250萬~100萬', u'100萬 以下']
    
    cases = SuperviseCase.objects.filter(date__gte=date_from, date__lte=date_to)

    class data: pass
    data.num = cases.count()
    data.places = places
    data.over_1e, data.range_1e_5000, data.range_5000_2500, data.range_2500_1000 = [], [], [], []
    data.range_1000_500, data.range_500_250, data.range_250_100, data.under_100, data.sum = [], [], [], [], []

    for n, p in enumerate(places):
        if n == 0:
            temp_cases = cases.filter(project_organizer_agencies__contains=u'漁業署', place__name__in=north_place_name)
        elif n == 1:
            temp_cases = cases.filter(project_organizer_agencies__contains=u'漁業署', place__name__in=south_place_name)
        else:
            temp_cases = cases.filter(place=p).exclude(project_organizer_agencies__contains='漁業署')

        data.over_1e.append(temp_cases.filter(budget_price__gt='100000'))
        data.range_1e_5000.append(temp_cases.filter(budget_price__lt='100000', budget_price__gte='50000'))
        data.range_5000_2500.append(temp_cases.filter(budget_price__lt='49999', budget_price__gte='25000'))
        data.range_2500_1000.append(temp_cases.filter(budget_price__lt='24999', budget_price__gte='10000'))
        data.range_1000_500.append(temp_cases.filter(budget_price__lt='10000', budget_price__gte='5000'))
        data.range_500_250.append(temp_cases.filter(budget_price__lt='5000', budget_price__gte='2500'))
        data.range_250_100.append(temp_cases.filter(budget_price__lt='2500', budget_price__gte='1000'))
        data.under_100.append(temp_cases.filter(budget_price__lte='1000'))
        data.sum.append(temp_cases)

    data.over_1e.append(cases.filter(budget_price__gt='100000'))
    data.range_1e_5000.append(cases.filter(budget_price__lt='100000', budget_price__gte='50000'))
    data.range_5000_2500.append(cases.filter(budget_price__lt='49999', budget_price__gte='25000'))
    data.range_2500_1000.append(cases.filter(budget_price__lt='24999', budget_price__gte='10000'))
    data.range_1000_500.append(cases.filter(budget_price__lt='10000', budget_price__gte='5000'))
    data.range_500_250.append(cases.filter(budget_price__lt='5000', budget_price__gte='2500'))
    data.range_250_100.append(cases.filter(budget_price__lt='2500', budget_price__gte='1000'))
    data.under_100.append(cases.filter(budget_price__lte='1000'))
    data.sum.append(cases)

    return data, subpage_name



#統計表格 - 單位-月份-件數
def make_statistics_5(date_from='', date_to='', places=[]):
    subpage_name = u'單位-月份-件數'
    
    cases = SuperviseCase.objects.filter(date__gte=date_from, date__lte=date_to)

    class data: pass
    data.num = cases.count()
    data.places = places
    data.months = [[] for m in xrange(12)]
    data.sum = []
    for n, p in enumerate(places):
        if n == 0:
            temp_cases = cases.filter(project_organizer_agencies__contains=u'漁業署', place__name__in=north_place_name)
        elif n == 1:
            temp_cases = cases.filter(project_organizer_agencies__contains=u'漁業署', place__name__in=south_place_name)
        else:
            temp_cases = cases.filter(place=p).exclude(project_organizer_agencies__contains='漁業署')

        for m in range(1, 13):
            data.months[m-1].append(temp_cases.filter(date__month=m))
        data.sum.append(temp_cases)

    for m in range(1, 13):
        data.months[m-1].append(cases.filter(date__month=m))
    data.sum.append(cases)

    return data, subpage_name


#統計表格 - 分類缺失次數排名
def make_statistics_6(date_from='', date_to='', places=[]):
    subpage_name = u'分類缺失次數排名'
    cases = SuperviseCase.objects.filter(date__gte=date_from, date__lte=date_to)

    def sort_by_num(a, b):
        if a.num.count() < b.num.count(): return 1
        else: return -1

    data = []
    errors = Error.objects.filter(case__in=cases)
    errors_no = set([i.ec.no for i in errors])
    ecs_01 = ErrorContent.objects.filter(no__startswith='4.01', no__in=errors_no).order_by('no') #工程主辦機關
    ecs_02 = ErrorContent.objects.filter(no__startswith='4.02', no__in=errors_no).order_by('no') #監造單位
    ecs_03 = ErrorContent.objects.filter(no__startswith='4.03', no__in=errors_no).order_by('no') #承攬廠商
    ecs_04 = ErrorContent.objects.filter(no__startswith='5.0', no__in=errors_no).order_by('no') #強度Ι－混凝土、鋼筋(構)、模板、土方、結構體、裝修、雜項等：（W1）
    ecs_05 = ErrorContent.objects.filter(no__startswith='5.10', no__in=errors_no).order_by('no') #強度II－材料設備檢驗與管制（W2）
    ecs_06 = ErrorContent.objects.filter(Q(no__startswith='5.14')|Q(no__startswith='5.17')).filter(no__in=errors_no).distinct().order_by('no') #安全（W3）
    ecs_07 = ErrorContent.objects.filter(no__startswith='6.', no__in=errors_no).order_by('no') #施工進度
    ecs_08 = ErrorContent.objects.filter(no__startswith='7.', no__in=errors_no).order_by('no') #規劃設計
    # ecs_09 = ErrorContent.objects.filter(no__startswith='5.17').order_by('no') #(六)功能指標
    titles = [
        u'品質管理制度-工程主辦機關', 
        u'品質管理制度-監造單位', 
        u'品質管理制度-承攬廠商', 
        u'施工品質-強度Ι－混凝土、鋼筋(構)、模板、土方、結構體、裝修、雜項等', 
        u'施工品質-強度II－材料設備檢驗與管制', 
        u'施工品質-安全',
        u'施工進度',
        u'規劃設計',
    ]
    for n_ecs, ecs in enumerate([ecs_01, ecs_02, ecs_03, ecs_04, ecs_05, ecs_06, ecs_07, ecs_08]):
        n = 0
        for ec in ecs:
            ec.num = errors.filter(ec__no=ec.no)
            n += ec.num.count()
        for ec in ecs: ec.percent = round(ec.num.count()*100. / n, 2) if ec.num.count() else 0
        ecs = list(ecs)
        ecs.sort(sort_by_num)
        temp_ecs = []
        for ec in ecs:
            if ec.percent:
                temp_ecs.append(ec)
            else:
                break
        data.append({'title': titles[n_ecs], 'n': n, 'data': temp_ecs})

    ecs_040506 = list(ecs_04) + list(ecs_05) + list(ecs_06)
    ecs_040506.sort(sort_by_num)
    temp_ecs_040506 = []
    n_040506 = data[-1]['n'] + data[-2]['n'] + data[-3]['n']
    for ec in ecs_040506:
        ec.percent = round(ec.num.count()*100. / n_040506, 2) if ec.num.count() else 0
        if ec.percent:
            temp_ecs_040506.append(ec)
        else:
            break

    #加入施工不分類
    data.append({
        'title': u"施工品質缺失(I、II、安全)",
         'n': n_040506, 
         'data': temp_ecs_040506}
    )

    return data, subpage_name


#統計表格 - 不分類缺失次數排名
def make_statistics_7(date_from='', date_to='', places=[]):
    subpage_name = u'不分類缺失次數排名'
    cases = SuperviseCase.objects.filter(date__gte=date_from, date__lte=date_to)

    def sort_by_num(a, b):
        if a.num.count() < b.num.count(): return 1
        else: return -1

    data = []
    errors = Error.objects.filter(case__in=cases)
    errors_no = set([i.ec.no for i in errors])
    ecs = ErrorContent.objects.filter(no__in=errors_no).order_by('no')
    titles = [u'不分類缺失一覽表']
    n = 0
    for ec in ecs:
        ec.num = errors.filter(ec__no=ec.no)
        ec.n = errors.filter(ec__no=ec.no, level__name='')
        ec.l = errors.filter(ec__no=ec.no, level__name='L')
        ec.m = errors.filter(ec__no=ec.no, level__name='M')
        ec.s = errors.filter(ec__no=ec.no, level__name='S')
        n += ec.num.count()
    for ec in ecs: ec.percent = round(ec.num.count()*100. / n, 2) if ec.num.count() else 0
    ecs = list(ecs)
    ecs.sort(sort_by_num)
    temp_ecs = []
    for ec in ecs:
        if ec.percent:
            temp_ecs.append(ec)
        else:
            break
    data.append({'title': titles[0], 'n': n, 'data': temp_ecs})
    return data, subpage_name


#統計表格 - 不分類缺失件數排名
def make_statistics_8(date_from='', date_to='', places=[]):
    subpage_name = u'不分類缺失件數排名'
    cases = SuperviseCase.objects.filter(date__gte=date_from, date__lte=date_to)

    def sort_by_num(a, b):
        if a.num_n < b.num_n: return 1
        else: return -1

    data = []
    errors = Error.objects.filter(case__in=cases)
    errors_no = set([i.ec.no for i in errors])
    ecs = ErrorContent.objects.filter(no__in=errors_no).order_by('no')
    titles = [u'不分類缺失一覽表']
    n = cases.count()
    for ec in ecs:
        ec.num = []
        tmp_case_ids = []
        for i in errors.filter(ec__no=ec.no):
            if i.case.id not in tmp_case_ids:
                tmp_case_ids.append(i.case.id)
                ec.num.append(i)
        ec.num_n = len(ec.num)
        ec.n = []
        tmp_case_ids = []
        for i in errors.filter(ec__no=ec.no, level__name=''):
            if i.case.id not in tmp_case_ids:
                tmp_case_ids.append(i.case.id)
                ec.n.append(i)
        ec.n_n = len(ec.n)
        ec.l = []
        tmp_case_ids = []
        for i in errors.filter(ec__no=ec.no, level__name='L'):
            if i.case.id not in tmp_case_ids:
                tmp_case_ids.append(i.case.id)
                ec.l.append(i)
        ec.l_n = len(ec.l)
        ec.m = []
        tmp_case_ids = []
        for i in errors.filter(ec__no=ec.no, level__name='M'):
            if i.case.id not in tmp_case_ids:
                tmp_case_ids.append(i.case.id)
                ec.m.append(i)
        ec.m_n = len(ec.m)
        ec.s = []
        tmp_case_ids = []
        for i in errors.filter(ec__no=ec.no, level__name='S'):
            if i.case.id not in tmp_case_ids:
                tmp_case_ids.append(i.case.id)
                ec.s.append(i)
        ec.s_n = len(ec.s)
    for ec in ecs: ec.percent = round(ec.num_n*100. / n, 2) if ec.num_n else 0
    ecs = list(ecs)
    ecs.sort(sort_by_num)
    temp_ecs = []
    for ec in ecs:
        if ec.percent:
            temp_ecs.append(ec)
        else:
            break
    data.append({'title': titles[0], 'n': n, 'data': temp_ecs})
    return data, subpage_name


#統計表格 - 分類缺失件數排名
def make_statistics_9(date_from='', date_to='', places=[]):
    subpage_name = u'分類缺失件數排名'
    cases = SuperviseCase.objects.filter(date__gte=date_from, date__lte=date_to)
    n = cases.count()

    def sort_by_num(a, b):
        if a.num < b.num: return 1
        else: return -1


    data = []
    errors = Error.objects.filter(case__in=cases)
    errors_no = set([i.ec.no for i in errors])
    ecs_01 = ErrorContent.objects.filter(no__startswith='4.01', no__in=errors_no).order_by('no') #工程主辦機關
    ecs_02 = ErrorContent.objects.filter(no__startswith='4.02', no__in=errors_no).order_by('no') #監造單位
    ecs_03 = ErrorContent.objects.filter(no__startswith='4.03', no__in=errors_no).order_by('no') #承攬廠商
    ecs_04 = ErrorContent.objects.filter(no__startswith='5.0', no__in=errors_no).order_by('no') #強度Ι－混凝土、鋼筋(構)、模板、土方、結構體、裝修、雜項等：（W1）
    ecs_05 = ErrorContent.objects.filter(no__startswith='5.10', no__in=errors_no).order_by('no') #強度II－材料設備檢驗與管制（W2）
    ecs_06 = ErrorContent.objects.filter(Q(no__startswith='5.14')|Q(no__startswith='5.17')).distinct().order_by('no') #安全（W3）
    ecs_07 = ErrorContent.objects.filter(no__startswith='6.', no__in=errors_no).order_by('no') #施工進度
    ecs_08 = ErrorContent.objects.filter(no__startswith='7.', no__in=errors_no).order_by('no') #規劃設計
    # ecs_09 = ErrorContent.objects.filter(no__startswith='5.17').order_by('no') #(六)功能指標
    titles = [
        u'品質管理制度-工程主辦機關', 
        u'品質管理制度-監造單位', 
        u'品質管理制度-承攬廠商', 
        u'施工品質-強度Ι－混凝土、鋼筋(構)、模板、土方、結構體、裝修、雜項等', 
        u'施工品質-強度II－材料設備檢驗與管制', 
        u'施工品質-安全',
        u'施工進度',
        u'規劃設計',
    ]
    for n_ecs, ecs in enumerate([ecs_01, ecs_02, ecs_03, ecs_04, ecs_05, ecs_06, ecs_07, ecs_08]):
        for ec in ecs:
            ec.case_ids = []
            for i in errors.filter(ec__no=ec.no):
                if i.case.id not in ec.case_ids:
                    ec.case_ids.append(i.case.id)
            ec.num = len(ec.case_ids)
            ec.percent = round(ec.num*100. / n, 2) if n else 0

        ecs = list(ecs)
        ecs.sort(sort_by_num)
        temp_ecs = []
        for ec in ecs:
            if ec.percent:
                temp_ecs.append(ec)
            else:
                break

        data.append({'title': titles[n_ecs], 'n': n, 'data': temp_ecs})

    ecs_040506 = list(ecs_04) + list(ecs_05) + list(ecs_06)
    ecs_040506.sort(sort_by_num)
    temp_ecs_040506 = []
    n_040506 = data[-1]['n'] + data[-2]['n'] + data[-3]['n']
    for ec in ecs_040506:
        if ec.percent:
            temp_ecs_040506.append(ec)
        else:
            break

    #加入施工不分類
    data.append({
        'title': u"施工品質缺失(I、II、安全)",
         'n': n, 
         'data': temp_ecs_040506}
    )

    return data, subpage_name


#從工程會同步或搜尋標案
@login_required
def search_supervise_form_pcc(R):
    if not R.user.has_perm('fishuser.sub_menu_supervise_system_create'):
        # 沒有 "第二層選單_督導系統_新增"
        return HttpResponseRedirect('/')

    pcc_projects = PCCProject.objects.filter(on_pcc_now=True)
    places = Place.objects.filter(uplevel=TAIWAN).order_by('id')
    t = get_template(os.path.join('supervise', 'zh-tw', 'search_supervise_form_pcc.html'))
    html = t.render(RequestContext(R,{
            'user': R.user,
            'years': years,
            'places': places,
            'pcc_project_num': pcc_projects.count(),
            'this_year': this_year,
            'toppage_name': u'督導系統',
            'subpage_name': u'搜尋工程會標案',
        }))
    return HttpResponse(html)



#從工程會同步所有的標案
@login_required
def sync_fishery_project_from_pcc(R):
    if not R.user.has_perm('fishuser.sub_menu_supervise_system_create'):
        # 沒有 "第二層選單_督導系統_新增"
        return HttpResponseRedirect('/')

    try:
        url = '%s%s' % (settings.PCCMATING_SERVER_HOST, 'fes_pccmating/get_all_fishery_project/')
        data = {}
        data['date'] = R.POST.get('date')
        data['uid'] = R.POST.get('uid')
        data['api_key'] = settings.PCCMATING_SERVER_APIKEY
        data = urlencode(data)
        req = Request(url, data)
        projects_list = json.loads(urlopen(req).read())
    except:
        return HttpResponse(json.dumps({'status': False, 'num': u'同步失敗'}))

    # projects_list = getAllFisheryProject()
    ids = []
    for p in projects_list:
        try:
            row = PCC_Project.objects.get(uid=p[u'編號'])
        except:
            row = PCC_Project(uid=p[u'編號'])
        row.implementation_department = p[u'執行機關']
        row.name = p[u'標案名稱']
        row.s_public_date = p[u'預定公告日期']
        row.r_decide_tenders_date = p[u'實際決標日期']
        row.contract_budget = p[u'發包預算']
        row.decide_tenders_price = p[u'決標金額']
        row.year = p[u'進度年']
        row.month = p[u'進度月']
        row.percentage_of_predict_progress = p[u'預定進度'] if p[u'預定進度'] else 0
        row.percentage_of_real_progress = p[u'實際進度'] if p[u'實際進度'] else 0
        row.percentage_of_dulta = round(float(row.percentage_of_real_progress) - float(row.percentage_of_predict_progress), 2)
        row.save()
        ids.append(row.id)
    PCC_Project.objects.all().exclude(id__in=ids).delete()

    return HttpResponse(json.dumps({'status': True, 'num': len(ids)}))


#觀看督導案詳細資料
@login_required
def project_profile(R, **kw):
    if not R.user.has_perm('fishuser.top_menu_supervise_system'):
        # 沒有 "第一層選單_督導系統"
        return HttpResponseRedirect('/')

    edit = False
    if R.user.has_perm('fishuser.sub_menu_supervise_system_create'):
        # 有 "第二層選單_督導系統_新增"
        edit = True

    project = SuperviseCase.objects.get(id=kw['project_id'])
    errors = Error.objects.filter(case=project).order_by('ec__no')
    errors_nos = list(set([e.ec.no for e in errors]))
    errors_nos.sort()
    errors_merge = {}
    for e in errors:
        if e.ec.no not in errors_merge:
            errors_merge[e.ec.no] = [e]
        else:
            errors_merge[e.ec.no].append(e)

    project.errors = []
    for e_no in errors_nos:
        if len(errors_merge[e_no]) == 1:
            project.errors.append(errors_merge[e_no][0])
        else:
            e = errors_merge[e_no][0]
            context = ''
            for i in range(len(errors_merge[e_no])):
                context += u'(%s)%s' % (i+1, errors_merge[e_no][i].context.replace('\r\n', '').replace('\n', '').replace('\r', ''))
            e.context = context
            project.errors.append(e)
    
    project.guides = []
    for g in project.outguide.all():
        project.guides.append({'obj': g, 'type': u'外部委員', 'errors': errors.filter(guide=g).order_by('ec__no')})

    for g in project.inguide.all():
        project.guides.append({'obj': g, 'type': u'內部委員', 'errors': errors.filter(guide=g).order_by('ec__no')})

    project.guides.append({'obj': None, 'type': u'未分類', 'errors': errors.filter(guide=None).order_by('ec__no')})

    for g in project.guides:
        for error in g['errors']:
            error.context = error.context.replace('\n', '').replace('\r', '')

    project.photos = ErrorPhotoFile.objects.filter(supervisecase=project).order_by('upload_date', 'id')
    for i in project.photos:
        if i.rExt().lower() in ['jpg', 'jpeg', 'tif', 'tiff', 'png', 'bmp']:
            i.is_photo = True

    project.captain_string = u'、'.join([g.name.replace('\n', '') for g in project.captain.all()])
    project.worker_string = u'、'.join([g.name.replace('\n', '') for g in project.worker.all()])
    project.files = project.casefile_set.all().order_by('id')

    t = get_template(os.path.join('supervise', 'zh-tw', 'project_profile.html'))
    html = t.render(RequestContext(R,{
            'user': R.user,
            'p': project,
            'edit': edit,
            'years': years,
            'units': units,
            'this_year': this_year,
            'toppage_name': u'督導系統',
        }))
    return HttpResponse(html)


#觀看督導案詳細資料
@login_required
def project_profile_record(R, **kw):
    if not R.user.has_perm('fishuser.top_menu_supervise_system'):
        # 沒有 "第一層選單_督導系統"
        return HttpResponseRedirect('/')

    project = SuperviseCase.objects.get(id=kw['project_id'])
    records = project.pcc_sync_record_case.all().order_by('-update_time')

    t = get_template(os.path.join('supervise', 'zh-tw', 'project_profile_record.html'))
    html = t.render(RequestContext(R,{
            'user': R.user,
            'p': project,
            'records': records,
        }))
    return HttpResponse(html)


#缺失改善紀錄表
@login_required
def error_imporve(R, **kw):
    case = SuperviseCase.objects.get(id=kw['project_id'])
    row = case.fes_project
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

    elif R.user.has_perm('fishuser.view_all_project_in_remote_control_system'):
        #有 "在(遠端工程系統)中_觀看_所有_工程案資訊"
        if not R.user.has_perm('fishuser.view_all_project_in_management_system'):
            #縣市政府人員
            if row.unit != R.user.user_profile.unit and not R.user.is_staff and not 'view_single_project_in_remote_control_system' in get_perms(R.user, row):
                #不是自己單位的工程
                return HttpResponseRedirect('/')

    edit = False
    if R.user.has_perm('fishuser.sub_menu_supervise_system_create'):
        # "第二層選單_督導系統_新增"
        edit = True

    if case.fes_project:
        if FRCMUserGroup.objects.filter(project=case.fes_project, user=R.user):
            edit = True


    case.errors = case.error_set.all().order_by('ec__no')
    case.photos = ErrorPhotoFile.objects.filter(supervisecase=case).order_by('upload_date', 'id')
    for i in case.photos:
        if i.rExt().lower() in ['jpg', 'jpeg', 'tif', 'tiff', 'png', 'bmp']:
            i.is_photo = True

    case.captain_string = u'、'.join([g.name.replace('\n', '') for g in case.captain.all()])
    case.worker_string = u'、'.join([g.name.replace('\n', '') for g in case.worker.all()])


    t = get_template(os.path.join('supervise', 'zh-tw', 'error_improve.html'))
    html = t.render(RequestContext(R,{
            'user': R.user,
            'p': case,
            'edit': edit,
            'years': years,
            'units': units,
            'this_year': this_year,
            'toppage_name': u'遠端管理系統',
        }))
    return HttpResponse(html)

#新增督導案
@login_required
def create_from_pcc(R):
    if not R.user.has_perm('fishuser.sub_menu_supervise_system_create'):
        # 沒有 "第二層選單_督導系統_新增"
        return HttpResponseRedirect('/')

    t = get_template(os.path.join('supervise', 'zh-tw', 'create_from_pcc.html'))
    html = t.render(RequestContext(R,{
            'user': R.user,
            'this_year': this_year,
            'toppage_name': u'督導系統',
            'subpage_name': u'從工程會新增',
        }))
    return HttpResponse(html)


#缺失改善紀錄表
@login_required
def statistics_only_chart(R, **kw):
    date_from = R.GET.get('date_from', TODAY())
    date_to = R.GET.get('date_to', TODAY())
    chart_name = R.GET.get('chart_name', 'pie-1')
    sub_type = R.GET.get('sub_type', '1')

    t = get_template(os.path.join('supervise', 'zh-tw', 'statistics_only_chart.html'))
    html = t.render(RequestContext(R,{
            'user': R.user,
            'date_from': date_from,
            'date_to': date_to,
            'chart_name': chart_name,
            'sub_type': sub_type,
        }))
    return HttpResponse(html)


#從工程會同步督導資料
@login_required
def get_supervise_info_from_pcc(R):
    #基本資料部分
    try:
        url = '%s%s' % (settings.PCCMATING_SERVER_HOST, 'fes_pccmating/sync_supervise_info/')
        data = {}
        data['date'] = R.POST.get('date')
        data['uid'] = R.POST.get('uid')
        data['api_key'] = settings.PCCMATING_SERVER_APIKEY
        data = urlencode(data)
        req = Request(url, data)
        doc = json.loads(urlopen(req).read())
        if doc.has_key('connect_error') and doc['connect_error']:
            return HttpResponse(json.dumps({'status': False, 'msg': u'查無資料，請確定標案編號及督導日期是否正確!!' + doc['connect_msg']}))
    except:
        return HttpResponse(json.dumps({'status': False, 'msg': u'查無資料，請確定標案編號及督導日期是否正確!!'}))


    try:
        case = SuperviseCase.objects.get(date=R.POST.get('date'), uid=R.POST.get('uid'))
    except:
        case = SuperviseCase(date=R.POST.get('date'), uid=R.POST.get('uid'))

    for key in doc:
        if key in ['outguide', 'inguide', 'captain', 'worker', 'place', 'location', 'subordinate_agencies_unit']:
            continue
        else:
            setattr(case, key, doc[key])

    if not case.plan: case.plan = u'尚未輸入'

    case.cdate = TODAY()

    try:
        case.subordinate_agencies_unit = Unit.objects.get(name=doc['subordinate_agencies_unit'])
    except:
        new_unit = Unit(
                        name = doc['subordinate_agencies_unit'],
                        fullname = doc['subordinate_agencies_unit'],
                        no = 'tem%@&!',
                        place = Place.objects.get(name='臺灣地區')
                        )
        new_unit.save()
        new_unit.no = str(100000000 + new_unit.id)[1:]
        new_unit.save()
        case.subordinate_agencies_unit = new_unit
    try:
        case.place = Place.objects.get(name=doc['place'], uplevel=TAIWAN)
    except:
        case.place = None
    try:
        case.location = Place.objects.get(name=doc['location'], uplevel=case.place)
    except:
        case.location = None
    case.save()

    for key in ['outguide', 'inguide', 'captain', 'worker']:
        for g in doc[key]:
            if g:
                if Guide.objects.filter(name=g):
                    guide = Guide.objects.filter(name=g)[0]
                else:
                    guide = Guide(name=g)
                    guide.save()
                eval('case.%s.add(guide)' % key)
    case.save()

    for g in Guide.objects.filter(Q(name__icontains='') | Q(name__icontains=' ') | Q(name__icontains='　')):
        if not g.name.replace(' ', '').replace('　', ''):
            g.delete()

    #缺失部分
    try:
        url = '%s%s' % (settings.PCCMATING_SERVER_HOST, 'fes_pccmating/sync_supervise_error/')
        data = {}
        data['date'] = R.POST.get('date')
        data['uid'] = R.POST.get('uid')
        data['api_key'] = settings.PCCMATING_SERVER_APIKEY
        data = urlencode(data)
        req = Request(url, data)
        doc = json.loads(urlopen(req).read())
    except:
        return HttpResponse(json.dumps({'status': False, 'msg': u'基本資料已同步，同步缺失時發生問題，資料尚未完整，請稍候再試一次!!'}))

    error_ecs_id = []
    for row in doc:
        try:
            ec = ErrorContent.objects.get(no=row[0])
        except:
            continue

        if u'輕微' in row[2]:
            el = ErrorLevel.objects.get(name=u"L")
        elif u'中等' in row[2]:
            el = ErrorLevel.objects.get(name=u"M")
        elif u'嚴重' in row[2]:
            el = ErrorLevel.objects.get(name=u"S")
        else:
            el = ErrorLevel.objects.get(name=u"")

        try:
            error = Error.objects.get(case=case, ec=ec)
        except:
            error = Error(
                case = case,
                ec = ec
                )
        error.context = row[1].replace('\n', '').replace('\r', '')
        error.level = el
        error.save()
        error_ecs_id.append(ec.id)
    case.error_set.all().exclude(ec__id__in=error_ecs_id).delete()

    if R.META.has_key('x_forwarded_for'): ip = R.META['x_forwarded_for']
    elif R.META.has_key('X_FORWARDED_FOR'): ip = R.META['X_FORWARDED_FOR']
    else: ip = R.META['REMOTE_ADDR']
    # record = PCC_sync_record(
    #     user = R.user,
    #     case = case,
    #     ip = ip,
    #     field_name = u'執行同步'
    #     )
    # record.save()

    return HttpResponse(json.dumps({'status': True, 'case_id': case.id}))


#上傳檔案的處理
@login_required
def new_file_upload(R):

    data = R.POST
    row_id = data['row_id']
    table_name = data['table_name']

    f = R.FILES.get('file', None)
    full_name = f.name.split(".")
    ext = full_name[-1].lower()
    full_name.remove(full_name[-1])
    name = "".join(full_name)
    if table_name == 'ErrorPhotoFile':
        case = SuperviseCase.objects.get(id=row_id)
        row = ErrorPhotoFile(
            name = name,
            supervisecase = case,
            ext = ext,
            upload_date = TODAY()
        )
        row.save()
        getattr(row, 'file').save('%s.%s'%(row.id, ext), f)
        row.save()
        url = row.rUrl()
        thumb_url = row.rThumbUrl()

    elif table_name == 'ErrorImproveFile':
        error = Error.objects.get(id=row_id)
        row = ErrorImproveFile(
            name = name,
            error = error,
            ext = ext,
            upload_date = TODAY()
        )
        row.save()
        getattr(row, 'file').save('%s.%s'%(row.id, ext), f)
        row.save()
        url = ''
        thumb_url = ''
    elif table_name == 'ErrorImprovePhoto':
        field_name = data['field_name']
        row = ErrorImprovePhoto.objects.get(id=row_id)
        try:
            eval('os.remove(os.path.join(ROOT, row.%s.name))' % field_name)
        except: pass
        try:
            file_name = eval('row.%s.name' % field_name)
            file_name = file_name.replace(".jpg", "_t_w51h38.jpg").replace(".jpeg", "_t_w51h38.jpeg").replace(".png", "_t_w51h38.png").replace(".tif", "_t_w51h38.tif").replace(".bmp", "_t_w51h38.bmp")
            os.remove(os.path.join(ROOT, file_name))
        except: pass
        getattr(row, field_name).save('%s-%s.%s'%(row.id, random.random(), ext), f)
        row.save()
        if field_name=='before':
            url = row.rBeforeUrl()
            thumb_url = row.rBeforeThumbUrl()
        elif field_name=='middle':
            url = row.rMiddleUrl()
            thumb_url = row.rMiddleThumbUrl()
        elif field_name=='after':
            url = row.rAfterUrl()
            thumb_url = row.rAfterThumbUrl()

    elif table_name == 'CaseFile':
        case = SuperviseCase.objects.get(id=row_id)
        row = CaseFile(
            name = name,
            supervisecase = case,
            ext = ext,
            upload_date = TODAY()
        )
        row.save()
        getattr(row, 'file').save('%s.%s'%(row.id, ext), f)
        row.save()
        url = row.rUrl()
        thumb_url = row.rThumbUrl()

    return HttpResponse(json.dumps({'status': True, 'id': row.id, 'ext': ext, 'name': name, 'url': url, 'thumb_url': thumb_url}))


#下載缺失改善表DOC
@login_required
def download_error_improve(R, **kw):
    from supervise.docxlib import *
    case = SuperviseCase.objects.get(id=kw['project_id'])
    row = case.fes_project
    
    if not R.user.has_perm('fishuser.view_all_project_in_remote_control_system'):
        #沒有 "在(遠端工程系統)中_觀看_所有_工程案資訊"s
        if not 'view_single_project_in_remote_control_system' in get_perms(R.user, row):
            #沒有 觀看此project 的 "在(遠端工程系統)中_觀看_單一_工程案資訊" 權限
            return HttpResponseRedirect('/')
        elif 'view_single_project_in_remote_control_system' in get_perms(R.user, row):
            #有 觀看此project 的 "在(遠端工程系統)中_觀看_單一_工程案資訊" 權限
            if not R.user.frcmusergroup_set.get(project=row).is_active:
                #被關閉權限的
                return HttpResponseRedirect('/')

    elif R.user.has_perm('fishuser.view_all_project_in_remote_control_system'):
        #有 "在(遠端工程系統)中_觀看_所有_工程案資訊"
        if not R.user.has_perm('fishuser.view_all_project_in_management_system'):
            #縣市政府人員
            if row.unit != R.user.user_profile.unit and not R.user.is_staff and not 'view_single_project_in_remote_control_system' in get_perms(R.user, row):
                #不是自己單位的工程
                return HttpResponseRedirect('/')

    book = rDocx(os.path.join(ROOT, 'apps', 'supervise', 'static', 'supervise', 'v2', 'doc_templates', 'supervise_first_page.docx'))
    book_document = rDocument(book)
    book_body = rDocBody(book_document)

    image1 = None
    text_dict, image_dict = {}, {}
    text_dict[u"project_name"] = case.project
    text_dict[u"date"] = u'%s年%s月%s日' % (case.date.year - 1911, case.date.month, case.date.day)
    text_dict[u"project_organizer_agencies"] = case.project_organizer_agencies
    text_dict[u"inspector"] = case.inspector
    text_dict[u"construct"] = case.construct

    book_document = replaceText(book_document, text_dict)
    book = replaceImage(book, image_dict)

    case.errors = case.error_set.all().order_by('ec__no')
    
    #total_page = int(case.errors.count() / 3)  

    #   if case.errors.count() % 3 == 0:
    #        text_dict[u"total_page"] = str(total_page + 2)
    #   else:
    #        text_dict[u"total_page"] = str(total_page + 3)
    #        total_page += 1
    # 2021/8/25    
 
    if int(case.errors.count()) % 3 == 0:
        total_page = int(case.errors.count() / 3)  +1

        if case.errors.count() % 3 == 0:
            text_dict[u"total_page"] = str(total_page + 1)
        else:
            text_dict[u"total_page"] = str(total_page + 2)
            total_page += 1

    elif int(case.errors.count()) % 3 != 0:
        total_page = int(case.errors.count() / 3) 

        if case.errors.count() % 3 == 0:
            text_dict[u"total_page"] = str(total_page + 2)
        else:
            text_dict[u"total_page"] = str(total_page + 3)
            total_page += 1

    if case.errors.count() <= 3:
        new_book = rDocx(os.path.join(ROOT,'apps','supervise','static','supervise','v2','doc_templates','supervise_error_improve.docx'))
        new_book_document = rDocument(new_book)
        new_book_body = rDocBody(new_book_document)
        total_page = case.errors.count() / 3 + 1
        n = 0
        page = 1
        text_dict[u"page"] = str(n + 1)


        if case.errors.count() == 0:
            text_dict[u"error_1"] = u''
            text_dict[u"improve_1"] = u''
            text_dict[u"date_1"] = u''
            text_dict[u"memo_1"] = u''
            text_dict[u"error_2"] = u''
            text_dict[u"improve_2"] = u''
            text_dict[u"date_2"] = u''
            text_dict[u"memo_2"] = u''
            text_dict[u"error_3"] = u''
            text_dict[u"improve_3"] = u''
            text_dict[u"date_3"] = u''
            text_dict[u"memo_3"] = u''
        
        elif case.errors.count() == 1:
            text_dict[u"error_2"] = u''
            text_dict[u"improve_2"] = u''
            text_dict[u"date_2"] = u''
            text_dict[u"memo_2"] = u''
            text_dict[u"error_3"] = u''
            text_dict[u"improve_3"] = u''
            text_dict[u"date_3"] = u''
            text_dict[u"memo_3"] = u''
            text_dict[u"error_1"] = u'%s.%s(%s)-%s' % (n+1, case.errors[n].ec.no, case.errors[n].level.name, case.errors[n].context)
            text_dict[u"improve_1"] = case.errors[n].improve_result if case.errors[n].improve_result else u''
            text_dict[u"date_1"]  = str(case.errors[n].date) if case.errors[n].date else u''
            text_dict[u"memo_1"]  = case.errors[n].memo if case.errors[n].memo else u''


        elif case.errors.count() == 2:
            text_dict[u"error_3"] = u''
            text_dict[u"improve_3"] = u''
            text_dict[u"date_3"] = u''
            text_dict[u"memo_3"] = u''
            text_dict[u"error_1"] = u'%s.%s(%s)-%s' % (n+1, case.errors[n].ec.no, case.errors[n].level.name, case.errors[n].context)
            text_dict[u"improve_1"] = case.errors[n].improve_result if case.errors[n].improve_result else u''
            text_dict[u"date_1"]  = str(case.errors[n].date) if case.errors[n].date else u''
            text_dict[u"memo_1"]  = case.errors[n].memo if case.errors[n].memo else u''
            text_dict[u"error_2"] = u'%s.%s(%s)-%s' % (n+2, case.errors[n+1].ec.no, case.errors[n+1].level.name, case.errors[n+1].context)
            text_dict[u"improve_2"] = case.errors[n+1].improve_result if case.errors[n+1].improve_result else u''
            text_dict[u"date_2"]  = str(case.errors[n+1].date) if case.errors[n+1].date else u''
            text_dict[u"memo_2"]  = case.errors[n+1].memo if case.errors[n+1].memo else u''


        elif case.errors.count() == 3:
            text_dict[u"error_1"] = u'%s.%s(%s)-%s' % (n+1, case.errors[n].ec.no, case.errors[n].level.name, case.errors[n].context)
            text_dict[u"improve_1"] = case.errors[n].improve_result if case.errors[n].improve_result else u''
            text_dict[u"date_1"]  = str(case.errors[n].date) if case.errors[n].date else u''
            text_dict[u"memo_1"]  = case.errors[n].memo if case.errors[n].memo else u''
            text_dict[u"error_2"] = u'%s.%s(%s)-%s' % (n+2, case.errors[n+1].ec.no, case.errors[n+1].level.name, case.errors[n+1].context)
            text_dict[u"improve_2"] = case.errors[n+1].improve_result if case.errors[n+1].improve_result else u''
            text_dict[u"date_2"]  = str(case.errors[n+1].date) if case.errors[n+1].date else u''
            text_dict[u"memo_2"]  = case.errors[n+1].memo if case.errors[n+1].memo else u''
            text_dict[u"error_3"] = u'%s.%s(%s)-%s' % (n+3, case.errors[n+2].ec.no, case.errors[n+2].level.name, case.errors[n+2].context)
            text_dict[u"improve_3"] = case.errors[n+2].improve_result if case.errors[n+2].improve_result else u''
            text_dict[u"date_3"]  = str(case.errors[n+2].date) if case.errors[n+2].date else u''
            text_dict[u"memo_3"]  = case.errors[n+2].memo if case.errors[n+2].memo else u''
        
        new_book_document = replaceText(new_book_document, text_dict)
        
        book_body.append(cPagebreak())
        book_body.append(new_book_body)
    else:
    	for n in xrange(total_page-1):
            new_book = rDocx(os.path.join(ROOT, 'apps', 'supervise', 'static', 'supervise', 'v2', 'doc_templates','supervise_error_improve.docx'))
            new_book_document = rDocument(new_book)
            new_book_body = rDocBody(new_book_document)
            text_dict[u"page"] = str(n + 1)
            
            text_dict[u"error_1"] = u'%s.%s(%s)-%s' % (3*n+1, case.errors[3*n].ec.no, case.errors[3*n].level.name, case.errors[3*n].context)
            text_dict[u"improve_1"] = case.errors[3*n].improve_result if case.errors[3*n].improve_result else u''
            text_dict[u"date_1"]  = str(case.errors[3*n].date) if case.errors[3*n].date else u''
            text_dict[u"memo_1"]  = case.errors[3*n].memo if case.errors[3*n].memo else u''
            text_dict[u"error_2"] = u'%s.%s(%s)-%s' % (3*n+2, case.errors[3*n+1].ec.no, case.errors[3*n+1].level.name, case.errors[3*n+1].context)
            text_dict[u"improve_2"] = case.errors[3*n+1].improve_result if case.errors[3*n+1].improve_result else u''
            text_dict[u"date_2"]  = str(case.errors[3*n+1].date) if case.errors[3*n+1].date else u''
            text_dict[u"memo_2"]  = case.errors[3*n+1].memo if case.errors[3*n+1].memo else u''
            text_dict[u"error_3"] = u'%s.%s(%s)-%s' % (3*n+3, case.errors[3*n+2].ec.no, case.errors[3*n+2].level.name, case.errors[3*n+2].context)
            text_dict[u"improve_3"] = case.errors[3*n+2].improve_result if case.errors[3*n+2].improve_result else u''
            text_dict[u"date_3"]  = str(case.errors[3*n+2].date) if case.errors[3*n+2].date else u''
            text_dict[u"memo_3"]  = case.errors[3*n+2].memo if case.errors[3*n+2].memo else u''

            new_book_document = replaceText(new_book_document, text_dict)
        
            book_body.append(cPagebreak())
            book_body.append(new_book_body)

        page = n+1

    if case.errors.count() > 3 and case.errors.count() % 3 != 0:
        text_dict[u"error_1"] = text_dict[u"improve_1"] = text_dict[u"date_1"] = text_dict[u"memo_1"] = u''
        text_dict[u"error_2"] = text_dict[u"improve_2"] = text_dict[u"date_2"] = text_dict[u"memo_2"] = u''
        text_dict[u"error_3"] = text_dict[u"improve_3"] = text_dict[u"date_3"] = text_dict[u"memo_3"] = u''
        new_book = rDocx(os.path.join(ROOT, 'apps', 'supervise', 'static', 'supervise', 'v2', 'doc_templates', 'supervise_error_improve.docx'))
        new_book_document = rDocument(new_book)
        new_book_body = rDocBody(new_book_document)
        text_dict[u"page"] = str(page+1)
        page += 1
        for n in xrange((total_page-1)*3, case.errors.count()):
            text_dict[u"error_%s" % (n-(total_page-1)*3+1)] = u'%s.%s(%s)-%s' % (n+1, case.errors[n].ec.no, case.errors[n].level.name, case.errors[n].context)
            text_dict[u"improve_%s" % (n-(total_page-1)*3+1)] = case.errors[n].improve_result if case.errors[n].improve_result else u''
            text_dict[u"date_%s" % (n-(total_page-1)*3+1)]  = str(case.errors[n].date) if case.errors[n].date else u''
            text_dict[u"memo_%s" % (n-(total_page-1)*3+1)]  = case.errors[n].memo if case.errors[n].memo else u''

        new_book_document = replaceText(new_book_document, text_dict)
        
        book_body.append(cPagebreak())
        book_body.append(new_book_body)

    new_book = rDocx(os.path.join(ROOT, 'apps', 'supervise', 'static', 'supervise', 'v2', 'doc_templates', 'supervise_error_improve.docx'))
    new_book_document = rDocument(new_book)
    new_book_body = rDocBody(new_book_document)
    text_dict[u"page"] = str(page + 1)
    page += 1
    text_dict[u"error_1"] = u'規劃設計問題及建議-%s' % (case.advise)
    text_dict[u"improve_1"] = case.advise_improve_result if case.advise_improve_result else u''
    text_dict[u"date_1"]  = str(case.advise_date) if case.advise_date else u''
    text_dict[u"memo_1"]  = case.advise_memo if case.advise_memo else u''

    text_dict[u"error_2"] = u'其他建議-%s' % (case.other_advise)
    text_dict[u"improve_2"] = case.other_improve_result if case.other_improve_result else u''
    text_dict[u"date_2"]  = str(case.other_date) if case.other_date else u''
    text_dict[u"memo_2"]  = case.other_memo if case.other_memo else u''

    if case.is_test:
        text_dict[u"error_3"] = u'檢驗拆驗-%s' % (case.test)
        text_dict[u"improve_3"] = case.test_result if case.test_result else u''
        text_dict[u"date_3"]  = str(case.test_date) if case.test_date else u''
        text_dict[u"memo_3"]  = case.test_memo if case.test_memo else u''
    else:
        text_dict[u"error_3"] = u''
        text_dict[u"improve_3"] = u''
        text_dict[u"date_3"]  = u''
        text_dict[u"memo_3"]  = u''

    new_book_document = replaceText(new_book_document, text_dict)
    book_body.append(cPagebreak())
    book_body.append(new_book_body)

    new_book = rDocx(os.path.join(ROOT, 'apps', 'supervise', 'static', 'supervise', 'v2', 'doc_templates', 'supervise_error_signature.docx'))
    new_book_document = rDocument(new_book)
    new_book_body = rDocBody(new_book_document)
    text_dict[u"page"] = str(page + 1)
    new_book_document = replaceText(new_book_document, text_dict)
    book_body.append(cPagebreak())
    book_body.append(new_book_body)

    case.error_improve_photos = ErrorImprovePhoto.objects.filter(Q(error__in=case.errors) | Q(case=case))
    for ep in case.error_improve_photos:
        new_book = rDocx(os.path.join(ROOT, 'apps', 'supervise', 'static', 'supervise', 'v2', 'doc_templates', 'supervise_error_photo.docx'))
        new_book_document = rDocument(new_book)
        image1, image2, image3 = None, None, None
        text_dict, image_dict = {u'project_name': case.project}, {}
        text_dict[u'memo_1'] = ep.before_memo if ep.before_memo else u''
        text_dict[u'memo_2'] = ep.middle_memo if ep.middle_memo else u''
        text_dict[u'memo_3'] = ep.after_memo if ep.after_memo else u''
        if ep.before: image_dict["image1.png"] = ep.before.path
        if ep.middle: image_dict["image2.png"] = ep.middle.path
        if ep.after: image_dict["image3.png"] = ep.after.path

        new_book_document = replaceText(new_book_document, text_dict)
        new_book = replaceImage(new_book, image_dict)
        book_body.append(cPagebreak())
        book = appendDoc(book, new_book)

    if case.is_test:
        new_book = rDocx(os.path.join(ROOT, 'apps', 'supervise', 'static', 'supervise', 'v2', 'doc_templates', 'supervise_is_test.docx'))
        new_book_document = rDocument(new_book)
        book_body.append(cPagebreak())
        book = appendDoc(book, new_book)

    book = outputDocx(book)
    filename = u'%s-(%s)漁業署工程督導改善對策及結果表' % (case.date, case.project)
    file_size = book.tell()
    book.seek(0)

    response = HttpResponse(book, content_type='application/docx')
    response['Content-Disposition'] = (u'attachment; filename=%s.docx'% filename).encode('cp950', 'replace')
    response['Content-Length'] = file_size
    return response


#下載檔案專用
@login_required
def download_file(R, **kw):
    table_name = kw['table_name'] 
    file_id = kw['file_id']
    if table_name == 'ErrorPhotoFile':
        row = ErrorPhotoFile.objects.get(id=kw["file_id"])
    elif table_name == 'CaseFile':
        row = CaseFile.objects.get(id=kw["file_id"])
    elif table_name == 'ErrorImproveFile':
        row = ErrorImproveFile.objects.get(id=kw["file_id"])
        
    f = open(row.file.path, 'rb')

    content = f.read()
    response = HttpResponse(content_type='application/' + row.rExt())
    response['Content-Type'] = ('application/' + row.rExt())
    file_name = row.name.replace(" ", "") + '.' + row.rExt()
    if R.GET.get('open', ''):
        response['Content-Disposition'] = ('inline; filename='+ file_name).encode('utf-8', 'replace')
    else:
        response['Content-Disposition'] = ('attachment; filename='+ file_name).encode('utf-8', 'replace')

    response.write(content)

    return response


#自主新增督導案的頁面
@login_required
def CreatSuperviseCase(R):
    if not R.user.has_perm('fishuser.sub_menu_supervise_system_create'):
        # 沒有 "第二層選單_督導系統_新增"
        return HttpResponseRedirect('/')

    info = {
        'date': R.GET.get('date', ''),
        'uid': R.GET.get('uid', ''),
    }
    try:
        pcc_p = PCCProject.objects.get(uid=info['uid'])
    except:
        try:
            extr = getProjectInfo(info['uid'])
            pcc_p = PCCProject.objects.get(uid=info['uid'])
        except:
            pcc_p = None

    if pcc_p:
        info['project'] = pcc_p.name
        for u in units:
            if u.name == pcc_p.head_department:
                pcc_p.subordinate_agencies_unit = u.id
                break

        try:
            pcc_p.place = Place.objects.get(name=pcc_p.engineering_county[:3]).id
        except: pass
        try:
            pcc_p.location = Place.objects.get(name=pcc_p.engineering_county[3:]).id
        except: pass
        pcc_p.contract_budget = pcc_p.contract_budget/1000 if pcc_p.contract_budget else ''
        pcc_p.decide_tenders_price = pcc_p.decide_tenders_price/1000 if pcc_p.decide_tenders_price else ''
        pcc_p.decide_tenders_price2 = pcc_p.decide_tenders_price2/1000 if pcc_p.decide_tenders_price2 else ''
        

    subordinate_agencies_units = [[i.id, i.fullname] for i in Unit.fish_city_menu.all()]
    F_A = Unit.objects.get(name='漁業署')
    subordinate_agencies_units.insert(0, [F_A.id, F_A.fullname])
    COA = Unit.objects.get(name='農業委員會')
    subordinate_agencies_units.insert(0, [COA.id, COA.fullname])
    places = Place.objects.filter(uplevel=TAIWAN).order_by('id')

    if info.get('place', ''):
        locations = Place.objects.filter(uplevel__id=info.get('place', ''))
    else:
        locations = []

    for i in places:
        i.locations = '<option value=""> 請選擇 </option>'
        for lo in Place.objects.filter(uplevel=i):
            i.locations += '<option value="%s">%s</option>' % (lo.id, lo.name)
                

    t = get_template(os.path.join('supervise', 'zh-tw', 'create_by_self', 'create.html'))
    html = t.render(RequestContext(R,{
            'user': R.user,
            'info': pcc_p,
            'date': R.GET.get('date', ''),
            'years': years,
            'this_year': this_year,
            'units': units,
            'subordinate_agencies_units': subordinate_agencies_units,
            'places': places,
            'locations': locations,
            'subpage_name': u'從工程會新增',
            'toppage_name': u'督導系統',
        }))
    return HttpResponse(html)

#自主新增
@login_required
def create_by_self(R):
    if R.POST.get('place') and R.POST.get('place') != "":
        place = Place.objects.get(id=R.POST.get('place'))
    else: place = None
    if R.POST.get('location') and R.POST.get('location') != "" and R.POST.get('location') != "undefined":
        location = Place.objects.get(id=R.POST.get('location'))
    else: location = None

    row = SuperviseCase(
                        uid = R.POST.get('uid'),
                        plan = R.POST.get('plan'),
                        subordinate_agencies_unit = Unit.objects.get(id=R.POST.get('subordinate_agencies_unit')),
                        date = R.POST.get('date'),
                        project = R.POST.get('project'),
                        place = place,
                        location = location,
                        project_organizer_agencies = R.POST.get('project_organizer_agencies'),
                        project_manage_unit = R.POST.get('project_manage_unit'),
                        designer = R.POST.get('designer'),
                        inspector = R.POST.get('inspector'),
                        construct = R.POST.get('construct'),
                        budget_price = str(R.POST.get('budget_price')) if R.POST.get('budget_price') != "" else '0',
                        contract_price = str(R.POST.get('contract_price')) if R.POST.get('contract_price') != "" else '0',
                        contract_price_change = str(R.POST.get('contract_price_change')) if R.POST.get('contract_price_change') != "" else '0',
                        info = R.POST.get('info'),
                        progress_info= R.POST.get('progress_info'),
                        progress_date = R.POST.get('progress_date') if R.POST.get('progress_date') != "" else R.POST.get('date'),
                        scheduled_progress = str(R.POST.get('scheduled_progress')) if R.POST.get('scheduled_progress') != '' else '0',
                        actual_progress = str(R.POST.get('actual_progress')) if R.POST.get('actual_progress') != '' else '0',
                        scheduled_money = str(R.POST.get('scheduled_money')) if R.POST.get('scheduled_money') != "" else '0',
                        actual_money = str(R.POST.get('actual_money')) if R.POST.get('actual_money') != "" else '0',
                        start_date = R.POST.get('start_date') if R.POST.get('start_date') != "" else None,
                        expected_completion_date = R.POST.get('expected_completion_date') if R.POST.get('expected_completion_date') != "" else None,
                        score = str(R.POST.get('score')) if R.POST.get('score') != "" else '0',
                        merit = R.POST.get('merit'),
                        advise = R.POST.get('advise'),
                        other_advise = R.POST.get('other_advise'),
                        construct_deduction = R.POST.get('construct_deduction') if R.POST.get('construct_deduction') != "" else 0,
                        inspector_deduction = R.POST.get('inspector_deduction') if R.POST.get('inspector_deduction') != "" else 0,
                        organizer_deduction = R.POST.get('organizer_deduction') if R.POST.get('organizer_deduction') != "" else 0,
                        project_manage_deduction = R.POST.get('project_manage_deduction') if R.POST.get('project_manage_deduction') != "" else 0,
                        total_deduction = R.POST.get('total_deduction') if R.POST.get('total_deduction') != "" else 0,
                        construct_deduction_memo = R.POST.get('construct_deduction_memo'),
                        inspector_deduction_memo = R.POST.get('inspector_deduction_memo'),
                        organizer_deduction_memo = R.POST.get('organizer_deduction_memo'),
                        project_manage_deduction_memo = R.POST.get('project_manage_deduction_memo'),
                        is_test = R.POST.get('is_test'),
                        test = R.POST.get('test'),
                        cdate = TODAY(),
                        )

    row.save()
    # outguides = re.split(u"[，,、_ ，、]", R.POST.get('outguides'))
    # inguides = re.split(u"[，,、_ ，、]", R.POST.get('inguides'))
    captains = re.split(u"[，,、_ ，、]", R.POST.get('captains'))
    workers = re.split(u"[，,、_ ，、]", R.POST.get('workers'))

    # for i in outguides:
    #     i = i.replace(' ', '').replace('　', '')
    #     if not i: continue
    #     try: outguide = Guide.objects.get(name=i)
    #     except:
    #         outguide = Guide(name=i)
    #         outguide.save()
    #     row.outguide.add(outguide)
    # for i in inguides:
    #     i = i.replace(' ', '').replace('　', '')
    #     if not i: continue
    #     try: inguide = Guide.objects.get(name=i)
    #     except:
    #         inguide = Guide(name=i)
    #         inguide.save()
    #     row.inguide.add(inguide)
    for i in captains:
        i = i.replace(' ', '').replace('　', '')
        if not i: continue
        try: captain = Guide.objects.get(name=i)
        except:
            captain = Guide(name=i)
            captain.save()
        row.captain.add(captain)
    for i in workers:
        i = i.replace(' ', '').replace('　', '')
        if not i: continue
        try: worker = Guide.objects.get(name=i)
        except:
            worker = Guide(name=i)
            worker.save()
        row.worker.add(worker)

    return HttpResponse(json.dumps({'status': True, 'case_id': row.id}))


#觀看督導案詳細資料
@login_required
def edit_profile(R, **kw):
    if not R.user.has_perm('fishuser.sub_menu_supervise_system_create'):
        # 沒有 "第二層選單_督導系統_新增"
        return HttpResponseRedirect('/')

    case = SuperviseCase.objects.get(id=kw['project_id'])
    errors = Error.objects.filter(case=case).order_by('ec__no')

    case.guides = []
    for g in case.outguide.all():
        case.guides.append({'obj': g, 'type': u'外部委員', 'errors': errors.filter(guide=g).order_by('ec__no')})

    for g in case.inguide.all():
        case.guides.append({'obj': g, 'type': u'內部委員', 'errors': errors.filter(guide=g).order_by('ec__no')})

    case.guides.append({'obj': None, 'type': u'未分類', 'errors': errors.filter(guide=None).order_by('ec__no')})

    for g in case.guides:
        for error in g['errors']:
            error.context = error.context.replace('\n', '').replace('\r', '')

    subordinate_agencies_units = [[i.id, i.fullname] for i in Unit.fish_city_menu.all()]
    F_A = Unit.objects.get(name='漁業署')
    subordinate_agencies_units.insert(0, [F_A.id, F_A.fullname])
    COA = Unit.objects.get(name='農業委員會')
    subordinate_agencies_units.insert(0, [COA.id, COA.fullname])
    places = Place.objects.filter(uplevel=TAIWAN).order_by('id')
    for i in places:
        i.locations = '<option value=""> 請選擇 </option>'
        for lo in Place.objects.filter(uplevel=i):
            i.locations += '<option value="/fishuser/api/v2/place/%s/">%s</option>' % (lo.id, lo.name)

    error_levels = ErrorLevel.objects.all();
    default_guide = [g.name for g in Guide.objects.filter(is_default=True).order_by('name')]
    t = get_template(os.path.join('supervise', 'zh-tw', 'create_by_self', 'case_profile.html'))
    html = t.render(RequestContext(R,{
            'user': R.user,
            'p': case,
            'default_guide': default_guide,
            'subordinate_agencies_units': subordinate_agencies_units,
            'error_levels': error_levels,
            'years': years,
            'units': units,
            'places': places,
            'this_year': this_year,
            'toppage_name': u'督導系統',
        }))
    return HttpResponse(html)


#自主新增缺失
@login_required
def add_error_by_self(R):
    if not R.user.has_perm('fishuser.sub_menu_supervise_system_create'):
        # 沒有 "第二層選單_督導系統_新增"
        return HttpResponseRedirect('/')

    case = SuperviseCase.objects.get(id=R.POST.get('row_id', ''))
    error_content = ErrorContent.objects.filter(no=R.POST.get('error_no', ''))
    if not error_no:
        return HttpResponse(json.dumps({'status': False, 'msg': u'查無此缺失編號，請重新確認!!'}))

    if R.POST.get('guide_id', ''):
        guide = Guide.objects.get(id=R.POST.get('guide_id', ''))
    else:
        guide = None

    row = Error(
            case = case,
            ec = error_content[0],
            context = '',
            level = ErrorLevel.objects.get(id=2),
            guide = guide
        )
    row.save()

    error_levels = ErrorLevel.objects.all();
    t = get_template(os.path.join('supervise', 'zh-tw', 'create_by_self', 'tr_error.html'))
    html = t.render(RequestContext(R,{
            'user': R.user,
            'error_levels': error_levels,
            'error': row
        }))
    return HttpResponse(json.dumps({'status': True, 'html': html}))


#自主新增缺失
@login_required
def pcc_settings(R):
    if not R.user.is_staff:
        # 沒有 "第二層選單_督導系統_新增"
        return HttpResponseRedirect('/')

    configs = Cofiguration.objects.all()
    
    t = get_template(os.path.join('supervise', 'zh-tw', 'pcc_settings.html'))
    html = t.render(RequestContext(R,{
            'user': R.user,
            'configs': configs,
            'toppage_name': u'督導系統',
            'subpage_name': u'同步及搜尋工程會標案',
        }))
    return HttpResponse(html)


#缺失搜尋小工具
@login_required
def search_error(R):
    """缺失搜尋小工具"""
    keyword = R.POST.get('keyword')
    result = ErrorContent.objects.all().order_by('id')
    for key in re.split('[ ,]+', keyword):
        ids = []
        if key:
            ids.extend([i.id for i in result.filter(no__icontains=key)])
            ids.extend([i.id for i in result.filter(introduction__icontains=key)])
            result = result.filter(id__in=ids)
    html = ''
    for i in result:
        html += '<tr><td class="warning">%s</td><td>%s</td></tr>' % (i.no, i.introduction)
    return HttpResponse(json.dumps({'html': html}))


#廠商缺失排行
@login_required
def unit_error_sort(R):
    """廠商缺失排行"""
    data = R.GET
    condition = {
        'date__gte': data['start_date'],
        'date__lte': data['end_date'],
    }

    if data['unit_type'] == 'subordinate_agencies_unit':
        condition['subordinate_agencies_unit__name'] = data['name']
    else:
        condition[data['unit_type']] = data['name']

    cases = SuperviseCase.objects.filter(**condition)
    n1 = cases.count()

    def sort_by_num(a, b):
        if a.num < b.num: return 1
        else: return -1

    errors = Error.objects.filter(case__in=cases)
    n2 = errors.count()

    errors_no = set([i.ec.no for i in errors])
    ecs = ErrorContent.objects.filter(no__in=errors_no).order_by('no')
    
    for ec in ecs:
        ec_errors = errors.filter(ec__no=ec.no)
        ec.error_ids = [str(i.id) for i in ec_errors]
        ec.num = ec_errors.count()
        ec.case_num = len(set([i.case.id for i in ec_errors]))
        ec.n = errors.filter(ec__no=ec.no, level__name='').count()
        ec.l = errors.filter(ec__no=ec.no, level__name='L').count()
        ec.m = errors.filter(ec__no=ec.no, level__name='M').count()
        ec.s = errors.filter(ec__no=ec.no, level__name='S').count()

    for ec in ecs: 
        ec.percent_case = round(ec.case_num*100. / n1, 2)
        ec.percent_error = round(ec.num*100. / n2, 2)

    ecs = list(ecs)
    ecs.sort(sort_by_num)

    temp_ecs = []
    for ec in ecs:
        if ec.num:
            temp_ecs.append({
                'no': ec.no,
                'error_ids': ','.join(ec.error_ids),
                'introduction': ec.introduction,
                'case_num': ec.case_num,
                'num': ec.num,
                'n': ec.n,
                'l': ec.l,
                'm': ec.m,
                's': ec.s,
                'percent_case': ec.percent_case,
                'percent_error': ec.percent_error,
                })
        else:
            break

    return HttpResponse(json.dumps({
        'status': True,
        'ecs': temp_ecs
        }))


#匯出督導紀錄EXCEL
@login_required
def export_case_excel(R):
    """缺失搜尋小工具"""
    all_ids = R.POST.get('all_ids', '').split(',')
    cases = SuperviseCase.objects.filter(id__in=all_ids).order_by('date')

    output = StringIO()
    workbook = xlsxwriter.Workbook(output, 
                {'strings_to_numbers':  True,
                'strings_to_formulas': False,
                'strings_to_urls':     False})

    #設定每個cell的格式
    def myfmt(border=1, bg_color="", shrink="", align="center", valign="vcenter", text_wrap="", font_name=u"新細明體", font_size=12, num_format="", bold=False):
        fmt = workbook.add_format()
        if border: fmt.set_border(border) #邊框
        if bg_color: fmt.set_bg_color(bg_color) #背景顏色
        if shrink: fmt.set_shrink(shrink) #自動縮小符合欄寬
        if align: fmt.set_align(align) #左右對齊
        if valign: fmt.set_align(valign) #上下對齊
        if text_wrap: fmt.set_text_wrap(text_wrap) #自動換列
        if font_name: fmt.set_font_name(font_name) #字型
        if font_size: fmt.set_font_size(font_size) #字體大小
        if num_format: fmt.set_num_format(num_format) #格式化顯示
        if bold: fmt.set_bold(bold) #粗體

        return fmt

    # 新增一個sheet
    worksheet = workbook.add_worksheet(u"督導案件")
    worksheet.set_margins(left=0.3, right=0.3, top=0.3, bottom=0.3)
    worksheet.set_header(header='', margin=0.0)  
    row = 0 #第一列的編號為0

    column_width=[
       #   A   B   C   D   E   F   G   H   I   J   K   L   M   N   O   P
           6, 15, 70, 40,  8,  8, 13, 13, 13, 35, 30,  8, 20

    ]
    for i, e in enumerate(column_width):
        worksheet.set_column(i, i, e)

    first_d = '%s.%s.%s' % (cases.first().date.year-1911, str(cases.first().date.month).zfill(2), str(cases.first().date.day).zfill(2))
    last_d = '%s.%s.%s' % (cases.last().date.year-1911, str(cases.last().date.month).zfill(2), str(cases.last().date.day).zfill(2))
    
    worksheet.merge_range(row, 0, row, 12, u"%s~%s工程督導案件及等第" % (first_d, last_d), myfmt(font_size=20, align="center", bg_color="#E5E5FF"))
    row += 1
    worksheet.write(row, 0, u'序號', myfmt(shrink=True, bg_color="#E5E5FF"))
    worksheet.write(row, 1, u'督導日期', myfmt(shrink=True, bg_color="#E5E5FF"))
    worksheet.write(row, 2, u'督導案件', myfmt(shrink=True, bg_color="#E5E5FF"))
    worksheet.write(row, 3, u'工程主辦機關', myfmt(shrink=True, bg_color="#E5E5FF"))
    worksheet.write(row, 4, u'分數', myfmt(shrink=True, bg_color="#E5E5FF"))
    worksheet.write(row, 5, u'等第', myfmt(shrink=True, bg_color="#E5E5FF"))
    worksheet.write(row, 6, u'發包預算\n(千元)', myfmt(text_wrap=True, bg_color="#E5E5FF"))
    worksheet.write(row, 7, u'契約金額\n(千元)', myfmt(text_wrap=True, bg_color="#E5E5FF"))
    worksheet.write(row, 8, u'變更設計後\n(千元)', myfmt(text_wrap=True, bg_color="#E5E5FF"))
    worksheet.write(row, 9, u'督導委員', myfmt(shrink=True, bg_color="#E5E5FF"))
    worksheet.write(row, 10, u'檢驗拆驗', myfmt(shrink=True, bg_color="#E5E5FF"))
    worksheet.write(row, 11, u'總扣點', myfmt(shrink=True, bg_color="#E5E5FF"))
    worksheet.write(row, 12, u'同意結案文號', myfmt(shrink=True, bg_color="#E5E5FF"))
    row += 1

    for n, c in enumerate(cases):
        worksheet.write(row, 0, n+1, myfmt(shrink=True))
        worksheet.write(row, 1, c.date, myfmt(shrink=True, num_format='[$-zh-TW]e"年"m"月"d"日";@'))
        worksheet.write(row, 2, c.project, myfmt(text_wrap=True, align="left"))
        worksheet.write(row, 3, c.project_organizer_agencies, myfmt(text_wrap=True, align="left"))
        worksheet.write(row, 4, c.score, myfmt(shrink=True))
        if c.score >= 90:
            score_level = u'優'
        elif c.score >= 80:
            score_level = u'甲'
        elif c.score >= 70:
            score_level = u'乙'
        elif c.score >= 60:
            score_level = u'丙'
        elif c.score >= 1:
            score_level = u'丁'
        else:
            score_level = u'無'
        worksheet.write(row, 5, score_level, myfmt(shrink=True))
        worksheet.write(row, 6, c.budget_price if c.budget_price else '', myfmt(shrink=True, num_format='_-* #,##0_-;-* #,##0_-;_-* "-"??_-;_-@_-'))
        worksheet.write(row, 7, c.contract_price if c.contract_price else '', myfmt(shrink=True, num_format='_-* #,##0_-;-* #,##0_-;_-* "-"??_-;_-@_-'))
        worksheet.write(row, 8, c.contract_price_change if c.contract_price_change else '', myfmt(shrink=True, num_format='_-* #,##0_-;-* #,##0_-;_-* "-"??_-;_-@_-'))
        worksheet.write(row, 9, u'、'.join([g.name for g in c.outguide.all()] + [g.name for g in c.inguide.all()]), myfmt(shrink=True, align="left"))
        worksheet.write(row, 10, c.test, myfmt(text_wrap=True, align="left"))
        worksheet.write(row, 11, c.total_deduction, myfmt(align="right"))
        worksheet.write(row, 12, c.finish_no, myfmt(shrink=True, align="left"))
        row += 1

    worksheet.center_horizontally()#置中
    worksheet.fit_to_pages(1, 0) #列印符合欄寬
    worksheet.repeat_rows(0, 1) #重複表頭
    worksheet.set_landscape() #橫印
    worksheet.freeze_panes(2, 3) #凍結視窗
    worksheet.autofilter('A2:M2') # 加入篩選器

    workbook.close()
    output.seek(0)
    response = HttpResponse(output.read(), content_type="application/ms-excel")
    response['Content-Disposition'] = (u'attachment; filename=%s~%s-工程督導案件及等第.xlsx' % (first_d, last_d)).encode('cp950', 'replace')

    return response


#匯出督導紀錄EXCEL
@login_required
def export_pcc_project_excel(R):
    """缺失搜尋小工具"""
    all_ids = R.POST.get('all_ids', '').split(',')
    projects = PCCProject.objects.filter(uid__in=all_ids).order_by('uid')

    output = StringIO()
    workbook = xlsxwriter.Workbook(output, 
                {'strings_to_numbers':  True,
                'strings_to_formulas': False,
                'strings_to_urls':     False})

    #設定每個cell的格式
    def myfmt(border=1, bg_color="", shrink="", align="center", valign="vcenter", text_wrap="", font_name=u"新細明體", font_size=12, num_format="", bold=False):
        fmt = workbook.add_format()
        if border: fmt.set_border(border) #邊框
        if bg_color: fmt.set_bg_color(bg_color) #背景顏色
        if shrink: fmt.set_shrink(shrink) #自動縮小符合欄寬
        if align: fmt.set_align(align) #左右對齊
        if valign: fmt.set_align(valign) #上下對齊
        if text_wrap: fmt.set_text_wrap(text_wrap) #自動換列
        if font_name: fmt.set_font_name(font_name) #字型
        if font_size: fmt.set_font_size(font_size) #字體大小
        if num_format: fmt.set_num_format(num_format) #格式化顯示
        if bold: fmt.set_bold(bold) #粗體

        return fmt

    # 新增一個sheet
    worksheet = workbook.add_worksheet(u"工程會標案")
    worksheet.set_margins(left=0.3, right=0.3, top=0.3, bottom=0.3)
    worksheet.set_header(header='', margin=0.0)  
    row = 0 #第一列的編號為0

    column_width=[
       #   A   B   C   D   E   F   G   H   I   J   
           6, 30, 30, 30, 18, 70, 18, 18, 13, 13,
       #   K   L   M   N   O   P   Q   R   S   T
          18, 30, 30, 20, 15, 15, 15, 20, 20, 20,
       #   U   V   W   X   Y   Z  AA  AB  AC  AD
          20, 20, 15, 70, 18, 20, 15, 10, 10, 10,
       #  AE  AF  AG  AH  AI  AJ  AK
          10, 10, 20, 15, 25, 13, 13
    ]
    for i, e in enumerate(column_width):
        worksheet.set_column(i, i, e)

    head_color = "#E5E5FF"
    cut1 = 12
    cut2 = cut1 + 10
    cut3 = cut2 + 11
    cut4 = cut3 + 10
    worksheet.write(row, 0, u'序號', myfmt(shrink=True, bg_color=head_color))
    worksheet.write(row, 1, u'主管機關', myfmt(shrink=True, bg_color=head_color))
    worksheet.write(row, 2, u'主辦機關', myfmt(shrink=True, bg_color=head_color))
    worksheet.write(row, 3, u'執行機關', myfmt(shrink=True, bg_color=head_color))
    worksheet.write(row, 4, u'標案編號', myfmt(shrink=True, bg_color=head_color))
    worksheet.write(row, 5, u'標案名稱', myfmt(shrink=True, bg_color=head_color))
    worksheet.write(row, 6, u'完成設計日期', myfmt(shrink=True, bg_color=head_color))
    worksheet.write(row, 7, u'公告日期', myfmt(shrink=True, bg_color=head_color))
    worksheet.write(row, 8, u'公告次數', myfmt(shrink=True, bg_color=head_color))
    worksheet.write(row, 9, u'招標方式', myfmt(shrink=True, bg_color=head_color))
    worksheet.write(row, 10, u'決標日期', myfmt(shrink=True, bg_color=head_color))
    worksheet.write(row, 11, u'查核\n(工程會、農委會、縣市政府)', myfmt(text_wrap=True, bg_color=head_color))
    worksheet.write(row, 12, u'督導\n(漁業署)', myfmt(text_wrap=True, bg_color=head_color))

    worksheet.write(row, cut1+1, u'決標方式', myfmt(shrink=True, bg_color=head_color))
    worksheet.write(row, cut1+2, u'工程總預算\n(仟元)', myfmt(text_wrap=True, bg_color=head_color))
    worksheet.write(row, cut1+3, u'發包預算\n(仟元)', myfmt(text_wrap=True, bg_color=head_color))
    worksheet.write(row, cut1+4, u'契約金額\n(仟元)', myfmt(text_wrap=True, bg_color=head_color))
    worksheet.write(row, cut1+5, u'規劃單位', myfmt(shrink=True, bg_color=head_color))
    worksheet.write(row, cut1+6, u'設計單位', myfmt(shrink=True, bg_color=head_color))
    worksheet.write(row, cut1+7, u'專案管理單位', myfmt(shrink=True, bg_color=head_color))
    worksheet.write(row, cut1+8, u'監造單位', myfmt(shrink=True, bg_color=head_color))
    worksheet.write(row, cut1+9, u'施工廠商', myfmt(shrink=True, bg_color=head_color))
    worksheet.write(row, cut1+10, u'縣市鄉鎮', myfmt(shrink=True, bg_color=head_color))

    worksheet.write(row, cut2+1, u'工程概要', myfmt(shrink=True, bg_color=head_color))
    worksheet.write(row, cut2+2, u'開工日期', myfmt(shrink=True, bg_color=head_color))
    worksheet.write(row, cut2+3, u'預定完工日', myfmt(shrink=True, bg_color=head_color))
    worksheet.write(row, cut2+4, u'工期', myfmt(shrink=True, bg_color=head_color))
    worksheet.write(row, cut2+5, u'進度月份', myfmt(shrink=True, bg_color=head_color))
    worksheet.write(row, cut2+6, u'預定進度', myfmt(shrink=True, bg_color=head_color))
    worksheet.write(row, cut2+7, u'實際進度', myfmt(shrink=True, bg_color=head_color))
    worksheet.write(row, cut2+8, u'差異', myfmt(shrink=True, bg_color=head_color))
    worksheet.write(row, cut2+9, u'機關首長', myfmt(shrink=True, bg_color=head_color))
    worksheet.write(row, cut2+10, u'聯絡人', myfmt(shrink=True, bg_color=head_color))
    worksheet.write(row, cut2+11, u'聯絡電話', myfmt(shrink=True, bg_color=head_color))

    worksheet.write(row, cut3+1, u'聯絡Email', myfmt(shrink=True, bg_color=head_color))
    worksheet.write(row, cut3+2, u'內容填報日', myfmt(shrink=True, bg_color=head_color))
    worksheet.write(row, cut3+3, u'進度填報日', myfmt(shrink=True, bg_color=head_color))
    row += 1

    for n, p in enumerate(projects):
        worksheet.write(row, 0, n+1, myfmt(shrink=True))
        worksheet.write(row, 1, p.head_department or u'', myfmt(shrink=True, align="left"))
        worksheet.write(row, 2, p.host_department or u'', myfmt(shrink=True, align="left"))
        worksheet.write(row, 3, p.implementation_department or u'', myfmt(shrink=True, align="left"))
        worksheet.write_formula(row, 4, '="%s"' % (p.uid), myfmt(shrink=True, align="left"))
        worksheet.write(row, 5, p.name or u'', myfmt(text_wrap=True, align="left"))
        worksheet.write(row, 6, u'預定：%s\n實際：%s' % (p.s_design_complete_date or u'', p.r_design_complete_date or u''), myfmt(text_wrap=True, align="left"))
        worksheet.write(row, 7, u'預定：%s\n實際：%s' % (p.s_public_date or u'', p.r_public_date or u''), myfmt(text_wrap=True, align="left"))
        worksheet.write(row, 8, p.public_times or u'', myfmt(align="right"))
        worksheet.write(row, 9, p.r_tenders_method or u'', myfmt(shrink=True, align="left"))
        worksheet.write(row, 10, u'預定：%s\n實際：%s' % (p.s_decide_tenders_date or u'', p.r_decide_tenders_date or u''), myfmt(text_wrap=True, align="left"))
        supervise_record = u'\n'.join(['%s紀錄，%s分(%s)' % (i['date'], i['score'], i['level']) for i in p.mapping_supervise_record()])
        worksheet.write(row, 11, supervise_record, myfmt(text_wrap=True, align="left"))
        fes_supervise_record = u'\n'.join(['%s紀錄，%s分(%s)' % (i['date'], i['score'], i['level']) for i in p.get_fes_supervise_record()])
        worksheet.write(row, 12, fes_supervise_record, myfmt(text_wrap=True, align="left"))

        worksheet.write(row, cut1+1, p.decide_tenders_method or u'', myfmt(shrink=True, align="left"))
        worksheet.write(row, cut1+2, p.total_budget/1000 if p.total_budget else 0, myfmt(shrink=True, align="right", num_format='_-* #,##0_-;-* #,##0_-;_-* "-"??_-;_-@_-'))
        worksheet.write(row, cut1+3, p.contract_budget/1000 if p.contract_budget else 0, myfmt(shrink=True, align="right", num_format='_-* #,##0_-;-* #,##0_-;_-* "-"??_-;_-@_-'))
        if p.decide_tenders_price2:
            worksheet.write(row, cut1+4, p.decide_tenders_price2/1000 or 0, myfmt(shrink=True, align="right", num_format='_-* #,##0_-;-* #,##0_-;_-* "-"??_-;_-@_-'))
        else:
            worksheet.write(row, cut1+4, p.decide_tenders_price/1000 or 0, myfmt(shrink=True, align="right", num_format='_-* #,##0_-;-* #,##0_-;_-* "-"??_-;_-@_-'))
        worksheet.write(row, cut1+5, p.planning_unit or u'', myfmt(text_wrap=True, align="left"))
        worksheet.write(row, cut1+6, p.design_unit or u'', myfmt(text_wrap=True, align="left"))
        worksheet.write(row, cut1+7, p.project_manage_unit or u'', myfmt(text_wrap=True, align="left"))
        worksheet.write(row, cut1+8, p.inspector_name or u'', myfmt(text_wrap=True, align="left"))
        worksheet.write(row, cut1+9, p.constructor or u'', myfmt(text_wrap=True, align="left"))
        worksheet.write(row, cut1+10, p.engineering_county or u'', myfmt(shrink=True, align="left"))
        
        worksheet.write(row, cut2+1, p.project_memo or u'', myfmt(text_wrap=True, align="left"))
        worksheet.write(row, cut2+2, u'預定：%s\n實際：%s' % (p.s_start_date or u'', p.r_start_date or u''), myfmt(text_wrap=True, align="left"))
        worksheet.write(row, cut2+3, u'原合約：%s\n變更後：%s\n實　際：%s' % (p.s_end_date or u'', p.s_end_date2 or u'', p.r_end_date or u''), myfmt(text_wrap=True, align="left"))
        worksheet.write(row, cut2+4, u'%s%s天' % (p.frcm_duration_type or u'', p.frcm_duration), myfmt(shrink=True, align="left"))
        worksheet.write(row, cut2+5, p.month or u'', myfmt(shrink=True, align="left"))
        worksheet.write(row, cut2+6, p.percentage_of_predict_progress/100 if p.percentage_of_predict_progress else 0, myfmt(shrink=True, num_format="0.00%"))
        worksheet.write(row, cut2+7, p.percentage_of_real_progress/100 if p.percentage_of_real_progress else 0, myfmt(shrink=True, num_format="0.00%"))
        worksheet.write_formula(row, cut2+8, u'=AD%s-AC%s' % (row+1, row+1), myfmt(shrink=True, num_format="0.00%"))
        worksheet.write(row, cut2+9, p.head_of_agency or u'', myfmt(shrink=True, align="left"))
        worksheet.write(row, cut2+10, p.manager or u'', myfmt(text_wrap=True, align="left"))
        worksheet.write(row, cut2+11, p.telphone or u'', myfmt(shrink=True, align="left"))
        
        worksheet.write(row, cut3+1, p.manager_email or u'', myfmt(shrink=True, align="left"))
        worksheet.write(row, cut3+2, p.fill_date or u'', myfmt(shrink=True, align="left", num_format="yyyy-mm-dd"))
        worksheet.write(row, cut3+3, p.progress_date or u'', myfmt(shrink=True, align="left", num_format="yyyy-mm-dd"))
        row += 1

    worksheet.center_horizontally()#置中
    worksheet.fit_to_pages(1, 0) #列印符合欄寬
    worksheet.repeat_rows(0, 1) #重複表頭
    worksheet.set_landscape() #橫印
    worksheet.freeze_panes(1, 0) #凍結視窗
    worksheet.autofilter('A1:Z1') # 加入篩選器

    workbook.close()
    output.seek(0)
    response = HttpResponse(output.read(), content_type="application/ms-excel")
    response['Content-Disposition'] = (u'attachment; filename=%s-工程會督導選案表.xlsx' % (TODAY())).encode('cp950', 'replace')

    return response



#匯出督導紀錄EXCEL
@login_required
def export_pcc_project_excel2(R):
    """缺失搜尋小工具"""
    all_ids = R.POST.get('all_ids', '').split(',')
    projects = PCCProject.objects.filter(uid__in=all_ids).order_by('uid')

    output = StringIO()
    workbook = xlsxwriter.Workbook(output, 
                {'strings_to_numbers':  True,
                'strings_to_formulas': False,
                'strings_to_urls':     False})

    #設定每個cell的格式
    def myfmt(border=1, bg_color="", shrink="", align="center", valign="vcenter", text_wrap="", font_name=u"新細明體", font_size=12, num_format="", bold=False):
        fmt = workbook.add_format()
        if border: fmt.set_border(border) #邊框
        if bg_color: fmt.set_bg_color(bg_color) #背景顏色
        if shrink: fmt.set_shrink(shrink) #自動縮小符合欄寬
        if align: fmt.set_align(align) #左右對齊
        if valign: fmt.set_align(valign) #上下對齊
        if text_wrap: fmt.set_text_wrap(text_wrap) #自動換列
        if font_name: fmt.set_font_name(font_name) #字型
        if font_size: fmt.set_font_size(font_size) #字體大小
        if num_format: fmt.set_num_format(num_format) #格式化顯示
        if bold: fmt.set_bold(bold) #粗體

        return fmt

    # 新增一個sheet
    worksheet = workbook.add_worksheet(u"工程會標案")
    worksheet.set_margins(left=0.3, right=0.3, top=0.3, bottom=0.3)
    worksheet.set_header(header='', margin=0.0)  
    row = 0 #第一列的編號為0

    column_width=[
       #   A   B   C   D   E   F   G   H   I   J   
           6, 30, 30, 70, 18, 18, 18, 10, 10, 13,
       #   K   L   M   N   O   P   Q   R   S   T
          13, 13, 11, 10, 11, 10, 12, 12, 12, 15,
       #   U   V   W   X   Y   Z  AA  AB  AC  AD
          13, 13, 13, 13, 13, 13, 20, 20, 20, 20,
       #  AE  AF  AG  AH  AI  AJ  AK
          13, 13, 30, 13, 13
    ]
    for i, e in enumerate(column_width):
        worksheet.set_column(i, i, e)

    head_color = "#E5E5FF"
    cut1 = 3
    cut2 = cut1 + 8
    cut3 = cut2 + 8
    cut4 = cut3 + 6
    worksheet.write(row, 0, u'序號', myfmt(shrink=True, bg_color=head_color))
    worksheet.write(row, 1, u'主辦機關', myfmt(shrink=True, bg_color=head_color))
    worksheet.write(row, 2, u'執行機關', myfmt(shrink=True, bg_color=head_color))
    worksheet.write(row, 3, u'標案名稱', myfmt(shrink=True, bg_color=head_color))

    worksheet.write(row, cut1+1, u'本年度可用預算\n(仟元)', myfmt(text_wrap=True, bg_color=head_color))
    worksheet.write(row, cut1+2, u'決標金額\n(仟元)', myfmt(text_wrap=True, bg_color=head_color))
    worksheet.write(row, cut1+3, u'變更設計後\n契約金額\n(仟元)', myfmt(text_wrap=True, bg_color=head_color))
    worksheet.write(row, cut1+4, u'中央比', myfmt(shrink=True, bg_color=head_color))
    worksheet.write(row, cut1+5, u'地方比', myfmt(shrink=True, bg_color=head_color))
    worksheet.write(row, cut1+6, u'實際\n開工日期', myfmt(text_wrap=True, bg_color=head_color))
    worksheet.write(row, cut1+7, u'原合約\n預定完工日', myfmt(text_wrap=True, bg_color=head_color))
    worksheet.write(row, cut1+8, u'變更後\n預定完工日', myfmt(text_wrap=True, bg_color=head_color))

    worksheet.write(row, cut2+1, u'工期類別', myfmt(shrink=True, bg_color=head_color))
    worksheet.write(row, cut2+2, u'總天數', myfmt(shrink=True, bg_color=head_color))
    worksheet.write(row, cut2+3, u'進度月份', myfmt(shrink=True, bg_color=head_color))
    worksheet.write(row, cut2+4, u'累計天數', myfmt(shrink=True, bg_color=head_color))
    worksheet.write(row, cut2+5, u'預定進度%', myfmt(shrink=True, bg_color=head_color))
    worksheet.write(row, cut2+6, u'實際進度%', myfmt(shrink=True, bg_color=head_color))
    worksheet.write(row, cut2+7, u'差異%', myfmt(shrink=True, bg_color=head_color))
    worksheet.write(row, cut2+8, u'狀態', myfmt(shrink=True, bg_color=head_color))

    worksheet.write(row, cut3+1, u'總累計預定\n完成金額\n(仟元)', myfmt(text_wrap=True, bg_color=head_color))
    worksheet.write(row, cut3+2, u'年累計預定\n完成金額\n(仟元)', myfmt(text_wrap=True, bg_color=head_color))
    worksheet.write(row, cut3+3, u'總累計實際\n完成金額\n(仟元)', myfmt(text_wrap=True, bg_color=head_color))
    worksheet.write(row, cut3+4, u'年累計實際\n完成金額\n(仟元)', myfmt(text_wrap=True, bg_color=head_color))
    worksheet.write(row, cut3+5, u'已估驗計價\n金額\n(仟元)', myfmt(text_wrap=True, bg_color=head_color))
    worksheet.write(row, cut3+6, u'待支付\n金額\n(仟元)', myfmt(text_wrap=True, bg_color=head_color))

    worksheet.write(row, cut4+1, u'解約原因', myfmt(shrink=True, bg_color=head_color))
    worksheet.write(row, cut4+2, u'落後因素', myfmt(shrink=True, bg_color=head_color))
    worksheet.write(row, cut4+3, u'原因分析', myfmt(shrink=True, bg_color=head_color))
    worksheet.write(row, cut4+4, u'解決辦法', myfmt(shrink=True, bg_color=head_color))
    worksheet.write(row, cut4+5, u'改進期限', myfmt(shrink=True, bg_color=head_color))
    worksheet.write(row, cut4+6, u'實際\n完工日', myfmt(text_wrap=True, bg_color=head_color))
    worksheet.write(row, cut4+7, u'歸屬計畫', myfmt(shrink=True, bg_color=head_color))
    worksheet.write(row, cut4+8, u'內容\n填報日', myfmt(text_wrap=True, bg_color=head_color))
    worksheet.write(row, cut4+9, u'進度\n填報日', myfmt(text_wrap=True, bg_color=head_color))
    row += 1

    for n, p in enumerate(projects):
        worksheet.write(row, 0, n+1, myfmt(shrink=True))
        worksheet.write(row, 1, p.host_department or u'', myfmt(shrink=True, align="left"))
        worksheet.write(row, 2, p.implementation_department or u'', myfmt(shrink=True, align="left"))
        worksheet.write(row, 3, p.name or u'', myfmt(text_wrap=True, align="left"))

        worksheet.write(row, cut1+1, p.this_year_budget/1000 if p.this_year_budget else 0, myfmt(shrink=True, align="right", num_format='_-* #,##0_-;-* #,##0_-;_-* "-"??_-;_-@_-'))
        worksheet.write(row, cut1+2, p.decide_tenders_price/1000 if p.decide_tenders_price else 0, myfmt(shrink=True, align="right", num_format='_-* #,##0_-;-* #,##0_-;_-* "-"??_-;_-@_-'))
        worksheet.write(row, cut1+3, p.decide_tenders_price2/1000 if p.decide_tenders_price2 else 0, myfmt(shrink=True, align="right", num_format='_-* #,##0_-;-* #,##0_-;_-* "-"??_-;_-@_-'))
        worksheet.write(row, cut1+4, p.main_rate/100 if p.main_rate else 0, myfmt(shrink=True, num_format="0.00%"))
        worksheet.write(row, cut1+5, p.sub_rate/100 if p.sub_rate else 0, myfmt(shrink=True, num_format="0.00%"))
        worksheet.write(row, cut1+6, u'%s%s%s' % (p.r_start_date.year-1911, str(p.r_start_date.month).zfill(2), str(p.r_start_date.day).zfill(2)) if p.r_start_date else u"", myfmt(text_wrap=True, align="left"))
        worksheet.write(row, cut1+7, u'%s%s%s' % (p.s_end_date.year-1911, str(p.s_end_date.month).zfill(2), str(p.s_end_date.day).zfill(2)) if p.s_end_date else u"", myfmt(text_wrap=True, align="left"))
        worksheet.write(row, cut1+8, u'%s%s%s' % (p.s_end_date2.year-1911, str(p.s_end_date2.month).zfill(2), str(p.s_end_date2.day).zfill(2)) if p.s_end_date2 else u"", myfmt(text_wrap=True, align="left"))

        worksheet.write(row, cut2+1, p.frcm_duration_type or u'', myfmt(shrink=True, align="left"))
        worksheet.write(row, cut2+2, p.frcm_duration, myfmt(shrink=True, align="right"))
        worksheet.write(row, cut2+3, p.month or u'', myfmt(shrink=True, align="center"))
        worksheet.write(row, cut2+4, p.use_duration, myfmt(shrink=True, align="right"))
        worksheet.write(row, cut2+5, p.percentage_of_predict_progress/100 if p.percentage_of_predict_progress else 0, myfmt(shrink=True, num_format="0.00%"))
        worksheet.write(row, cut2+6, p.percentage_of_real_progress/100 if p.percentage_of_real_progress else 0, myfmt(shrink=True, num_format="0.00%"))
        worksheet.write_formula(row, cut2+7, u'=R%s-Q%s' % (row+1, row+1), myfmt(shrink=True, num_format="0.00%"))
        worksheet.write(row, cut2+8, p.status or u'', myfmt(shrink=True, align="left"))

        worksheet.write(row, cut3+1, p.total_sch_price/1000 if p.total_sch_price else 0, myfmt(shrink=True, align="right", num_format='_-* #,##0_-;-* #,##0_-;_-* "-"??_-;_-@_-'))
        worksheet.write(row, cut3+2, p.year_sch_price/1000 if p.year_sch_price else 0, myfmt(shrink=True, align="right", num_format='_-* #,##0_-;-* #,##0_-;_-* "-"??_-;_-@_-'))
        worksheet.write(row, cut3+3, p.total_act_price/1000 if p.total_act_price else 0, myfmt(shrink=True, align="right", num_format='_-* #,##0_-;-* #,##0_-;_-* "-"??_-;_-@_-'))
        worksheet.write(row, cut3+4, p.year_act_price/1000 if p.year_act_price else 0, myfmt(shrink=True, align="right", num_format='_-* #,##0_-;-* #,##0_-;_-* "-"??_-;_-@_-'))
        worksheet.write(row, cut3+5, p.invoice_price/1000 if p.invoice_price else 0, myfmt(shrink=True, align="right", num_format='_-* #,##0_-;-* #,##0_-;_-* "-"??_-;_-@_-'))
        worksheet.write(row, cut3+6, p.wait_pay_price/1000 if p.wait_pay_price else 0, myfmt(shrink=True, align="right", num_format='_-* #,##0_-;-* #,##0_-;_-* "-"??_-;_-@_-'))
        
        worksheet.write(row, cut4+1, p.cancel_reason or u'', myfmt(text_wrap=True, align="left"))
        worksheet.write(row, cut4+2, p.delay_factor or u'', myfmt(text_wrap=True, align="left"))
        worksheet.write(row, cut4+3, p.delay_reason or u'', myfmt(text_wrap=True, align="left"))
        worksheet.write(row, cut4+4, p.delay_solution or u'', myfmt(text_wrap=True, align="left"))
        worksheet.write(row, cut4+5, u'%s%s%s' % (p.improve_date.year-1911, str(p.improve_date.month).zfill(2), str(p.improve_date.day).zfill(2)) if p.improve_date else u"", myfmt(text_wrap=True, align="left"))
        worksheet.write(row, cut4+6, u'%s%s%s' % (p.r_end_date.year-1911, str(p.r_end_date.month).zfill(2), str(p.r_end_date.day).zfill(2)) if p.r_end_date else u"", myfmt(text_wrap=True, align="left"))
        worksheet.write(row, cut4+7, p.plan_name or u'', myfmt(text_wrap=True, align="left"))
        worksheet.write(row, cut4+8, u'%s%s%s' % (p.fill_date.year-1911, str(p.fill_date.month).zfill(2), str(p.fill_date.day).zfill(2)) if p.fill_date else u"", myfmt(text_wrap=True, align="left"))
        worksheet.write(row, cut4+9, u'%s%s%s' % (p.progress_date.year-1911, str(p.progress_date.month).zfill(2), str(p.progress_date.day).zfill(2)) if p.progress_date else u"", myfmt(text_wrap=True, align="left"))
        
        row += 1

    worksheet.center_horizontally()#置中
    worksheet.fit_to_pages(1, 0) #列印符合欄寬
    worksheet.repeat_rows(0, 1) #重複表頭
    worksheet.set_landscape() #橫印
    worksheet.freeze_panes(1, 0) #凍結視窗
    worksheet.autofilter('A1:Z1') # 加入篩選器

    workbook.close()
    output.seek(0)
    response = HttpResponse(output.read(), content_type="application/ms-excel")
    response['Content-Disposition'] = (u'attachment; filename=%s-工程會進度控管表.xlsx' % (TODAY())).encode('cp950', 'replace')

    return response













































# 
def rJSON(R, right_type_value=u'Ajax Request'):
    submit = R.GET.get('submit', '')
    html = False
    if not submit: submit = R.POST.get('submit', '')
    if 'rFindLocation' == submit:
        result = rFindLocation(R)
    elif 'error_no' == submit:
        result = error_no(R)   
    elif 'add_New_Supervise_Case' == submit:
        result = add_New_Supervise_Case(R)
    elif 'search_Supervise_Case' == submit:
        result = search_Supervise_Case(R)
    elif 'update_supervise_info' == submit:
        result = update_supervise_info(R)
    elif 'deleteGuide' == submit:
        result = deleteGuide(R)    
    elif 'addGuide' == submit:
        result = addGuide(R)
    elif 'change_view_type_error' == submit:
        result = change_view_type_error(R)
    elif 'add_New_Error_For_Case' == submit:
        result = add_New_Error_For_Case(R)    
    elif 'deleteError' == submit:
        result = deleteError(R)   
    elif 'deleteCase' == submit:
        result = deleteCase(R)
    elif 'showFilterCases' == submit:
        result = showFilterCases(R)    
    elif 'deleteErrorPhoto' == submit:
        result = deleteErrorPhoto(R)    
    elif 'search_Error_Keyword' == submit:
        result = search_Error_Keyword(R)

    else:
        result = {'status': False, 'message': u'未指定方法'}

    if html: return HttpResponse(result)
    else: return HttpResponse(json.write(result))

def search_Error_Keyword(R):
    key = R.POST.get('key')
    ids = []
    for k in re.split('[ ,]+', key):
        ids.extend([i.id for i in ErrorContent.objects.filter(no__icontains=k)])
        ids.extend([i.id for i in ErrorContent.objects.filter(introduction__icontains=k)])
    errors = ErrorContent.objects.filter(id__in=ids)

    t = get_template(os.path.join('supervise', 'search_error_result.html'))
    html = t.render(RequestContext(R, {
            'errors': errors,
        }))

    return {'status': True, 'html': html}

def deleteErrorPhoto(R):
    row = ErrorPhotoFile.objects.get(id=R.POST.get('row_id'))
    row.file.delete()
    row.delete()
    return {'status': True}


def showFilterCases(R):
    ids = R.POST.get('ids').split(',')[:-1]
    search_condition = R.POST.get('search_condition')
    for i in xrange(len(ids)): ids[i] = int(ids[i])
    cases = SuperviseCase.objects.filter(id__in=ids)
    
    for case in cases:
        if len(case.inspector) > 10: case.inspector_s = case.inspector[:10] + '...(略)'
        else: case.inspector_s = case.inspector
        if len(case.construct) > 10: case.construct_s = case.construct[:10] + '...(略)'
        else: case.construct_s = case.construct
    
    if R.POST.get('deduction') == 'True':
        templates = 'case_list_deduction.html'
    else:
        templates = 'case_list.html'
    
    t = get_template(os.path.join('supervise', templates))
    html = t.render(RequestContext(R, {
            'cases': cases,
            'cases_num': len(cases),
            'search_condition': search_condition
        }))

    return {'status': True, 'html': html}

def deleteCase(R):
    row = SuperviseCase.objects.get(id=R.POST.get('case_id'))
    row.delete()
    return {'status': True}

def deleteError(R):
    row = Error.objects.get(id=R.POST.get('error_id'))
    row.delete()
    return {'status': True}
    
def add_New_Error_For_Case(R):
    row = SuperviseCase.objects.get(id=R.POST.get('case_id'))
    error_no = R.POST.get('error_no')
    error_level = R.POST.get('error_level')
    error_context = R.POST.get('error_context')
    try:
        ec = ErrorContent.objects.get(no=error_no)
    except:
        return {'status': False, 'msg': u'缺失編號錯誤'}
    try:
        level = ErrorLevel.objects.get(name=error_level)
    except:
        return {'status': False, 'msg': u'缺失程度錯誤'}
    error = Error(
                  case = row,
                  ec = ec,
                  context = error_context,
                  level = level
                  )
    error.save()
    
    t = get_template(os.path.join('supervise', 'error_tr.html'))
    html = t.render(RequestContext(R, {
            'error': error
        }))
    
    return {'status': True, 'html': html}


def change_view_type_error(R):
    row = Error.objects.get(id=R.POST.get('row_id'))
    if R.POST.get('field_name') == 'error_level':
        try:
            lv = ErrorLevel.objects.get(name=R.POST.get('value').upper())
        except:
            return {'status': False, 'msg': u'無此種等級分類'}
        row.level = lv
        row.save()
        
    elif R.POST.get('field_name') == 'context':
        row.context = R.POST.get('value')
        row.save()
    
    return {'status': True}
        
def addGuide(R):
    case = SuperviseCase.objects.get(id=R.POST.get('case_id'))
    guide = Guide.objects.filter(name=R.POST.get('name'))
    if len(guide) >= 1:
        guide = guide[0]
    else:
        guide = Guide(name=R.POST.get('name'))
        guide.save()

    if R.POST.get('field_name') == 'outguide':
        case.outguide.add(guide)
    elif R.POST.get('field_name') == 'inguide':
        case.inguide.add(guide)
    elif R.POST.get('field_name') == 'captain':
        case.captain.add(guide)
    elif R.POST.get('field_name') == 'worker':
        case.worker.add(guide)
    case.save()
    
    t = get_template(os.path.join('supervise', 'guide_tr.html'))
    html = t.render(RequestContext(R, {
            'case': case,
            'guide': guide,
            'field_name': R.POST.get('field_name')
        }))

    return {'status': True, 'html': html}


def deleteGuide(R):
    case = SuperviseCase.objects.get(id=R.POST.get('case_id'))
    guide = Guide.objects.get(id=R.POST.get('row_id'))
    if R.POST.get('field_name') == 'outguide':
        case.outguide.remove(guide)
    elif R.POST.get('field_name') == 'inguide':
        case.inguide.remove(guide)
    elif R.POST.get('field_name') == 'captain':
        case.captain.remove(guide)
    elif R.POST.get('field_name') == 'worker':
        case.worker.remove(guide)
    
    return {'status': True}

def update_supervise_info(R):
    if R.POST.get('table_name') == 'SuperviseCase':
        row = SuperviseCase.objects.get(id=R.POST.get('row_id'))
    html = ''
    field_name = R.POST.get('field_name')
    value = R.POST.get('value')
    return_value = value
    if field_name in ['budget_price', 'contract_price', 'scheduled_progress', 'actual_progress', 'scheduled_money', 'actual_money', 'score']:
        if value == '': value = '0'
        return_value = value
    elif field_name in ['subordinate_agencies_unit']:
        value = Unit.objects.get(id=value)
        return_value = value.fullname
    elif field_name == 'place':
        value = Place.objects.get(id=value)
        return_value = value.name
        locations = [[i.id, i.name] for i in Place.objects.filter(uplevel=value).order_by('id')]
        t = get_template(os.path.join('supervise', 'location_option.html'))
        html = t.render(RequestContext(R, {
                'locations': locations,
                'row': row
            }))
        setattr(row, "location", None)
    elif field_name == 'location':
        value = Place.objects.get(id=value)
        return_value = value.name
        
    setattr(row, field_name, value)
    row.save()
    
    return {'status': True, 'return_value': return_value, 'html': html}

def search_Supervise_Case(R):
    cases = SuperviseCase.objects.all()
    if R.POST.get('plan'):
        ids = []
        for plan in re.split('[ ,]+', R.POST.get('plan')):
            ids.extend([i.id for i in cases.filter(plan__icontains=plan)])
        cases = cases.filter(id__in=ids)
    
    if R.POST.get('project'):
        ids = []
        for project in re.split('[ ,]+', R.POST.get('project')):
            ids.extend([i.id for i in cases.filter(project__icontains=project)])
        cases = cases.filter(id__in=ids)
    
    if R.POST.get('project_organizer_agencies'):
        ids = []
        for project_organizer_agencies in re.split('[ ,]+', R.POST.get('project_organizer_agencies')):
            ids.extend([i.id for i in cases.filter(project_organizer_agencies__icontains=project_organizer_agencies)])
        cases = cases.filter(id__in=ids)
    
    if R.POST.get('project_manage_unit'):
        ids = []
        for project_manage_unit in re.split('[ ,]+', R.POST.get('project_manage_unit')):
            ids.extend([i.id for i in cases.filter(project_manage_unit__icontains=project_manage_unit)])
        cases = cases.filter(id__in=ids)
    
    if R.POST.get('designer'):
        ids = []
        for designer in re.split('[ ,]+', R.POST.get('designer')):
            ids.extend([i.id for i in cases.filter(designer__icontains=designer)])
        cases = cases.filter(id__in=ids)
    
    if R.POST.get('inspector'):
        ids = []
        for inspector in re.split('[ ,]+', R.POST.get('inspector')):
            ids.extend([i.id for i in cases.filter(inspector__icontains=inspector)])
        cases = cases.filter(id__in=ids)
        
    if R.POST.get('construct'):
        ids = []
        for construct in re.split('[ ,]+', R.POST.get('construct')):
            ids.extend([i.id for i in cases.filter(construct__icontains=construct)])
        cases = cases.filter(id__in=ids)
    
    if R.POST.get('outguides'):
        names = []
        for i in re.split('[ ,+]+', R.POST.get('outguides')):
            for s in Guide.objects.filter(name__contains=i):
                names.append(s.name)
        cases = cases.filter(outguide__name__in=names)
    
    if R.POST.get('inguides'):
        names = []
        for i in re.split('[ ,+]+', R.POST.get('inguides')):
            for s in Guide.objects.filter(name__contains=i):
                names.append(s.name)
        cases = cases.filter(inguide__name__in=names)
    
    if R.POST.get('subordinate_agencies_unit'):
        cases = cases.filter(subordinate_agencies_unit__id=R.POST.get('subordinate_agencies_unit'))
    
    if R.POST.get('location') and R.POST.get('location') != 'undefined':
        cases = cases.filter(location__id=R.POST.get('location'))
    elif R.POST.get('place'):
        cases = cases.filter(place__id=R.POST.get('place'))
    
    date_from = R.POST.get('date_from', None).replace('/', '-').replace('.', '-')
    date_to = R.POST.get('date_to', None).replace('/', '-').replace('.', '-')
    if date_from and not date_to:
        cases = cases.filter(date=date_from)
    elif not date_from and date_to:
        cases = cases.filter(date=date_to)
    elif date_from and date_to:
        cases = cases.filter(date__gte=date_from, date__lte=date_to)
        
    start_date_from = R.POST.get('start_date_from', None).replace('/', '-').replace('.', '-')
    start_date_to = R.POST.get('start_date_to', None).replace('/', '-').replace('.', '-')
    if start_date_from and not start_date_to:
        cases = cases.filter(date=start_date_from)
    elif not start_date_from and start_date_to:
        cases = cases.filter(date=start_date_to)
    elif start_date_from and start_date_to:
        cases = cases.filter(start_date__gte=start_date_from, start_date__lte=start_date_to)
    
    expected_completion_date_from = R.POST.get('expected_completion_date_from', None).replace('/', '-').replace('.', '-')
    expected_completion_date_to = R.POST.get('expected_completion_date_to', None).replace('/', '-').replace('.', '-')
    if expected_completion_date_from and not expected_completion_date_to:
        cases = cases.filter(date=expected_completion_date_from)
    elif not expected_completion_date_from and expected_completion_date_to:
        cases = cases.filter(date=expected_completion_date_to)
    elif expected_completion_date_from and expected_completion_date_to:
        cases = cases.filter(expected_completion_date__gte=expected_completion_date_from, expected_completion_date__lte=expected_completion_date_to) 
    
    if R.POST.get('budget_price_from', 0) and R.POST.get('budget_price_from', 0) != '':
        budget_price_from = decimal.Decimal(str(round(float(R.POST.get('budget_price_from', 0)), 3)))
    else: budget_price_from = decimal.Decimal('0')
    if R.POST.get('budget_price_to', 0) and R.POST.get('budget_price_to', 0) != '':
        budget_price_to = decimal.Decimal(str(round(float(R.POST.get('budget_price_to', 0)), 3)))
    else: budget_price_to = decimal.Decimal('0')
    if budget_price_from and not budget_price_to:
        cases = cases.filter(budget_price__gte=budget_price_from)
    elif not budget_price_from and budget_price_to:
        cases = cases.filter(budget_price__lte=budget_price_to)
    elif budget_price_from and budget_price_to:
        cases = cases.filter(budget_price__gte=budget_price_from, budget_price__lte=budget_price_to)
    
    if R.POST.get('contract_price_from', 0) and R.POST.get('contract_price_from', 0) != '':
        contract_price_from = decimal.Decimal(str(round(float(R.POST.get('contract_price_from', 0)), 3)))
    else: contract_price_from = decimal.Decimal('0')
    if R.POST.get('contract_price_to', 0) and R.POST.get('contract_price_to', 0) != '':
        contract_price_to = decimal.Decimal(str(round(float(R.POST.get('contract_price_to', 0)), 3)))
    else: contract_price_to = decimal.Decimal('0')
    if contract_price_from and not contract_price_to:
        cases = cases.filter(contract_price__gte=contract_price_from)
    elif not contract_price_from and contract_price_to:
        cases = cases.filter(contract_price__lte=contract_price_to)
    elif contract_price_from and contract_price_to:
        cases = cases.filter(contract_price__gte=contract_price_from, contract_price__lte=contract_price_to)
    
    if R.POST.get('scheduled_progress_from', 0) and R.POST.get('scheduled_progress_from', 0) != '':
        scheduled_progress_from = decimal.Decimal(str(round(float(R.POST.get('scheduled_progress_from', 0)), 3)))
    else: scheduled_progress_from = decimal.Decimal('0')
    if R.POST.get('scheduled_progress_to', 0) and R.POST.get('scheduled_progress_to', 0) != '':
        scheduled_progress_to = decimal.Decimal(str(round(float(R.POST.get('scheduled_progress_to', 0)), 3)))
    else: scheduled_progress_to = decimal.Decimal('0')
    if scheduled_progress_from and not scheduled_progress_to:
        cases = cases.filter(scheduled_progress__gte=scheduled_progress_from)
    elif not scheduled_progress_from and scheduled_progress_to:
        cases = cases.filter(scheduled_progress__lte=scheduled_progress_to)
    elif scheduled_progress_from and scheduled_progress_to:
        cases = cases.filter(scheduled_progress__gte=scheduled_progress_from, scheduled_progress__lte=scheduled_progress_to)
    
    if R.POST.get('actual_progress_from', 0) and R.POST.get('actual_progress_from', 0) != '':
        actual_progress_from = decimal.Decimal(str(round(float(R.POST.get('actual_progress_from', 0)), 3)))
    else: actual_progress_from = decimal.Decimal('0')
    if R.POST.get('actual_progress_to', 0) and R.POST.get('actual_progress_to', 0) != '':
        actual_progress_to = decimal.Decimal(str(round(float(R.POST.get('actual_progress_to', 0)), 3)))
    else: actual_progress_to = decimal.Decimal('0')
    if actual_progress_from and not actual_progress_to:
        cases = cases.filter(actual_progress__gte=actual_progress_from)
    elif not actual_progress_from and actual_progress_to:
        cases = cases.filter(actual_progress__lte=actual_progress_to)
    elif actual_progress_from and actual_progress_to:
        cases = cases.filter(actual_progress__gte=actual_progress_from, actual_progress__lte=actual_progress_to)
    
    if R.POST.get('score_from', 0) and R.POST.get('score_from', 0) != '':
        score_from = decimal.Decimal(str(round(float(R.POST.get('score_from', 0)), 3)))
    else: score_from = decimal.Decimal('0')
    if R.POST.get('score_to', 0) and R.POST.get('score_to', 0) != '':
        score_to = decimal.Decimal(str(round(float(R.POST.get('score_to', 0)), 3)))
    else: score_to = decimal.Decimal('0')
    if score_from and not score_to:
        cases = cases.filter(score__gte=score_from)
    elif not score_from and score_to:
        cases = cases.filter(score__lte=score_to)
    elif score_from and score_to:
        cases = cases = cases.filter(score__gte=score_from, score__lte=score_to)
    
    if R.POST.get('error', '') and R.POST.get('error', '') != '':
        key = R.POST.get('error')
        ids = []
        for k in re.split('[ ,]+', key):
            ids.extend([i.case.id for i in Error.objects.filter(ec__no__icontains=k)])
            ids.extend([i.case.id for i in Error.objects.filter(context__icontains=k)])
        cases = cases.filter(id__in=ids)
        
    for case in cases:
        if len(case.inspector) > 10: case.inspector_s = case.inspector[:10] + '...(略)'
        else: case.inspector_s = case.inspector
        if len(case.construct) > 10: case.construct_s = case.construct[:10] + '...(略)'
        else: case.construct_s = case.construct
    
    if R.user.is_staff or Edit.objects.filter(user = R.user):
        edit = True
    else: edit = False
    
    t = get_template(os.path.join('supervise', 'case_list.html'))
    html = t.render(RequestContext(R, {
            'edit': edit,
            'cases': cases,
            'cases_num': len(cases)
        }))

    return {'status': True, 'html': html}   

def error_no(R):
    value = R.POST.get('value')
    try:
        ErrorContent.objects.get(no=value)
        return {'status': True}
    except:
        return {'status': False}

def rFindLocation(R):
    place_id = R.POST.get('place_id')
    html = '<select class="input_text" name="location" id="location">'
    html += '<option value=""> 請選擇  </option>'
    for i in Place.objects.filter(uplevel__id=place_id).order_by('id'):
        html += '<option value="' + str(i.id) + '">' + str(i.name) + '</option>'
    html += '</select>'
    
    return {'status': True, 'html': html}


@checkAuthority
def index(R, project, right_type_value=u'觀看管考系統資料'):
    
    t = get_template(os.path.join('supervise', 'index.html'))
    html = t.render(RequestContext(R, {
        }))
    return HttpResponse(html)



@checkAuthority
def SearchSuperviseCase(R, project, right_type_value=u'觀看管考系統資料'):
    
    subordinate_agencies_units = [[i.id, i.fullname] for i in Unit.fish_city_menu.all()]
    F_A = Unit.objects.get(name='漁業署')
    subordinate_agencies_units.insert(0, [F_A.id, F_A.fullname])
    COA = Unit.objects.get(name='農業委員會')
    subordinate_agencies_units.insert(0, [COA.id, COA.fullname])
    places = [[i.id, i.name] for i in Place.objects.filter(uplevel=TAIWAN).order_by('id')]

    t = get_template(os.path.join('supervise', 'search.html'))
    html = t.render(RequestContext(R, {
            'subordinate_agencies_units': subordinate_agencies_units,
            'places': places,
        }))
    return HttpResponse(html)


@checkAuthority
def ReadAndEditSuperviseCase(R, project, right_type_value=u'觀看管考系統資料', **kw):
    if R.user.is_staff or Edit.objects.filter(user = R.user):
        edit = True
    else: edit = False
    
    subordinate_agencies_units = [[i.id, i.fullname] for i in Unit.fish_city_menu.all()]
    F_A = Unit.objects.get(name='漁業署')
    subordinate_agencies_units.insert(0, [F_A.id, F_A.fullname])
    COA = Unit.objects.get(name='農業委員會')
    subordinate_agencies_units.insert(0, [COA.id, COA.fullname])
    case = SuperviseCase.objects.get(id=kw['case_id'])
    places = [[i.id, i.name] for i in Place.objects.filter(uplevel=TAIWAN).order_by('id')]
    locations = [[i.id, i.name] for i in Place.objects.filter(uplevel=case.place).order_by('id')]
    errors = Error.objects.filter(case=case).order_by('ec__no')
    if case.score >= 90: score_level = '優等'
    elif case.score >= 80: score_level = '甲等'
    elif case.score >= 70: score_level = '乙等'
    elif case.score >= 60: score_level = '丙等'
    elif case.score < 60: score_level = '丁等'
    
    photos = ErrorPhotoFile.objects.filter(supervisecase=kw['case_id'])
    
    t = get_template(os.path.join('supervise', 'case_profile.html'))
    html = t.render(RequestContext(R, {
            'edit': edit,
            'errors': errors,
            'p': case,
            'subordinate_agencies_units': subordinate_agencies_units,
            'places': places,
            'locations': locations,
            'score_level': score_level,
            'photos': photos
        }))
    return HttpResponse(html)

@checkAuthority
def uploadPhotoFile(R, project, right_type_value=u'觀看管考系統資料', **kw):
    DATA = readDATA(R)
    name = R.GET.get('name')
    memo = R.GET.get('memo')
    supervisecase = SuperviseCase.objects.get(id=kw['supervise_id'])
    file = R.FILES.get('newfile_file_'+str(supervisecase.id), None)

    try:
        extension = file.name.split('.')[-1].lower()
    except:
        extension = 'zip'
    
    row = ErrorPhotoFile(
                        name = name,
                        memo = memo,
                        ext = extension,
                        upload_date = TODAY(),
                        supervisecase = supervisecase,
                        )
    row.save()
    
    if file:
        getattr(row, 'file').save('%s.%s'%(row.id, extension), file)
        row.save()
    
    return HttpResponse(json.dumps({'status': True, 'id': row.id, 'name': row.name,
                                    'memo': row.memo, 'photo_rThumbUrl': row.rThumbUrl(),
                                    'photo_rUrl': row.rUrl()
                                    }))


@checkAuthority
def TestIndex(R, project, right_type_value=u'觀看管考系統資料', **kw):
    t = get_template(os.path.join('supervise', 'index02.html'))
    html = t.render(RequestContext(R, {
        }))
    return HttpResponse(html)

def make_deduction_list(tmp, t):
    list = [['', tmp[0]]]
    for i in tmp[1:]:
        if t == '主辦扣點':
            p = 0
            for j in i:
                p += j.organizer_deduction
            list.append([p, i])
        
        elif t == '專案管理扣點':
            p = 0
            for j in i:
                p += j.project_manage_deduction
            list.append([p, i])
        elif t == '監造扣點':
            p = 0
            for j in i:
                p += j.inspector_deduction
            list.append([p, i])
        elif t == '營造扣點':
            p = 0
            for j in i:
                p += j.construct_deduction
            list.append([p, i])
    return list
    
    
@checkAuthority
def StatisticsTable(R, project, right_type_value=u'觀看管考系統資料', **kw):
    if R.user.is_staff or Edit.objects.filter(user = R.user):
        edit = True
    else: edit = False

    south_places = ['彰化縣', '雲林縣', '嘉義市', '嘉義縣', '臺南市', '高雄市', '屏東縣', '臺南市', '澎湖縣', '臺東縣']
    all_place = Place.objects.filter(uplevel=TAIWAN).order_by('id')
    places = [Unit.objects.get(name='北部辦公室'), Unit.objects.get(name='南部辦公室')]
    places[0].bgcolor = 1
    places[1].bgcolor = 1
    cases = list(SuperviseCase.objects.all().order_by('date'))
    years = [y for y in xrange(cases[0].date.year, cases[-1].date.year+1)]
    years.reverse()
    
    south_place = []
    north_place = []
    for i in all_place:
        if i.name not in south_places:
            i.south = False
            i.bgcolor = 2
            north_place.append(i)
    for i in all_place:
        if i.name in south_places:
            i.south = True
            i.bgcolor = 1
            south_place.append(i)
    places += north_place + south_place
    if kw['year'] == 'all':
        cases = SuperviseCase.objects.all()
        year = '全部'
    else:
        cases = SuperviseCase.objects.filter(date__year=int(kw['year']))
        year = int(kw['year'])
    all_case_num = len(cases)
    
    if kw['table_id'] == '01': #「分數區間統計」
        title = '單位-分數-件數  統計表'
        table_id = 1
        data = []
        types = ['85(含)分以上', '80(含)~85分', '75(含)~80分', '70(含)~75分', '70(不含)分以下']
        
        for t in types:
            tmp = [t]

            if t == '85(含)分以上': up_level, low_level = '101', '85'
            elif t == '80(含)~85分': up_level, low_level = '85', '80'
            elif t == '75(含)~80分': up_level, low_level = '80', '75'
            elif t == '70(含)~75分': up_level, low_level = '75', '70'
            elif t == '70(不含)分以下': up_level, low_level = '70', '0'
            tmp.append(cases.filter(score__gte=low_level, score__lt=up_level, subordinate_agencies_unit__fullname__contains='漁業署', place__in=north_place))
            tmp.append(cases.filter(score__gte=low_level, score__lt=up_level, subordinate_agencies_unit__fullname__contains='漁業署', place__in=south_place))
            for i in (north_place + south_place):
                tmp.append(cases.filter(score__gte=low_level, score__lt=up_level, place=i).exclude(subordinate_agencies_unit__fullname__contains='漁業署'))
            
            tmp.append(cases.filter(score__gte=low_level, score__lt=up_level))
            for n, i in enumerate(tmp[1:]):
                if len(i) == 0: tmp[n+1] = ''
            data.append(tmp)
            
        tmp = ['小計']
        tmp.append(cases.filter(subordinate_agencies_unit__fullname__contains='漁業署', place__in=north_place))
        tmp.append(cases.filter(subordinate_agencies_unit__fullname__contains='漁業署', place__in=south_place))
        for i in (north_place + south_place):
            tmp.append(cases.filter(place=i).exclude(subordinate_agencies_unit__fullname__contains='漁業署'))
        tmp.append(cases)
        for n, i in enumerate(tmp[1:]):
            if len(i) == 0: tmp[n+1] = ''    
        data.append(tmp)
        places.append('小計')
        
    elif kw['table_id'] == '02': #「單位扣點統計」
        title = '單位-扣點  統計表'
        table_id = 2
        data = []
        types = ['主辦扣點', '專案管理扣點', '監造扣點', '營造扣點']
        for t in types:
            tmp = [t]

            if t == '主辦扣點': tmp_cases = cases.exclude(organizer_deduction=0)
            elif t == '專案管理扣點': tmp_cases = cases.exclude(project_manage_deduction=0)
            elif t == '監造扣點': tmp_cases = cases.exclude(inspector_deduction=0)
            elif t == '營造扣點': tmp_cases = cases.exclude(construct_deduction=0)
            tmp.append(tmp_cases.filter(subordinate_agencies_unit__fullname__contains='漁業署', place__in=north_place))
            tmp.append(tmp_cases.filter(subordinate_agencies_unit__fullname__contains='漁業署', place__in=south_place))
            for i in (north_place + south_place):
                tmp.append(tmp_cases.filter(place=i).exclude(subordinate_agencies_unit__fullname__contains='漁業署'))
            
            tmp.append(tmp_cases)
            for n, i in enumerate(tmp[1:]):
                if len(i) == 0: tmp[n+1] = ''
            tmp = make_deduction_list(tmp, t)
            
            data.append(tmp)
        places.append('小計')
        
    elif kw['table_id'] == '04': #「各單位缺失排名榜」
        def sort_by_num(a, b):
            if a.num < b.num: return 1
            else: return -1
        
        def make_error_list(ids, data, unit):
            error_num = []
            errors = Error.objects.filter(case__id__in=ids)
            for e in errors:
                if e.ec not in error_num:
                    e.ec.num = 1
                    e.ec.cases_id = str(e.case.id) + ','
                    error_num.append(e.ec)
                else:
                    error_num[error_num.index(e.ec)].num += 1
                    error_num[error_num.index(e.ec)].cases_id += str(e.case.id) + ','
            error_num.sort(sort_by_num)
            if not error_num:
                error_num = ['' for i in range(11)]
            data.append([unit] + error_num[:10])
            return data
        
        title = '單位-缺失排行 統計表'
        table_id = 4

        data = [[i+1 for i in range(10)]]
        data[0].insert(0, '')
        ids = [i.id for i in cases.filter(subordinate_agencies_unit__fullname__contains='漁業署', place__in=north_place)]
        data = make_error_list(ids, data, places[0])
        ids = [i.id for i in cases.filter(subordinate_agencies_unit__fullname__contains='漁業署', place__in=south_place)]
        data = make_error_list(ids, data, places[1])
        for p in (north_place + south_place):
            ids = [i.id for i in cases.filter(place=p).exclude(subordinate_agencies_unit__fullname__contains='漁業署')]
            data = make_error_list(ids, data, p)
        
    elif kw['table_id'] == '05': #「金額區間統計」
        title = '單位-金額-件數  統計表'
        table_id = 5
        data = []
        types = ['1億元 以上', '1億~5000萬', '5000萬~2500萬', '2500萬~1000萬', '1000萬~500萬', '500萬~250萬', '250萬~100萬', '100萬 以下']
        
        for t in types:
            tmp = [t]

            if t == '1億元 以上': up_level, low_level = '99999999', '100000'
            elif t == '1億~5000萬': up_level, low_level = '100000', '50000'
            elif t == '5000萬~2500萬': up_level, low_level = '50000', '25000'
            elif t == '2500萬~1000萬': up_level, low_level = '25000', '10000'
            elif t == '1000萬~500萬': up_level, low_level = '10000', '5000'
            elif t == '500萬~250萬': up_level, low_level = '5000', '2500'
            elif t == '250萬~100萬': up_level, low_level = '2500', '1000'
            elif t == '100萬 以下': up_level, low_level = '1000', '0'
            tmp.append(cases.filter(contract_price__gte=low_level, contract_price__lt=up_level, subordinate_agencies_unit__fullname__contains='漁業署', place__in=north_place))
            tmp.append(cases.filter(contract_price__gte=low_level, contract_price__lt=up_level, subordinate_agencies_unit__fullname__contains='漁業署', place__in=south_place))
            for i in (north_place + south_place):
                tmp.append(cases.filter(contract_price__gte=low_level, contract_price__lt=up_level, place=i).exclude(subordinate_agencies_unit__fullname__contains='漁業署'))
            
            tmp.append(cases.filter(contract_price__gte=low_level, contract_price__lt=up_level))
            for n, i in enumerate(tmp[1:]):
                if len(i) == 0: tmp[n+1] = ''
            data.append(tmp)
            
        tmp = ['小計']
        tmp.append(cases.filter(subordinate_agencies_unit__fullname__contains='漁業署', place__in=north_place))
        tmp.append(cases.filter(subordinate_agencies_unit__fullname__contains='漁業署', place__in=south_place))
        for i in (north_place + south_place):
            tmp.append(cases.filter(place=i).exclude(subordinate_agencies_unit__fullname__contains='漁業署'))
        tmp.append(cases)
        for n, i in enumerate(tmp[1:]):
            if len(i) == 0: tmp[n+1] = ''    
        data.append(tmp)
        places.append('小計')
    
    elif kw['table_id'] == '06': #「月份區間統計」
        title = '單位-月份-件數  統計表'
        table_id = 6
        data = []
        types = [m for m in xrange(1, 13)]
        for t in types:
            tmp = [str(t)+'月']

            tmp.append(cases.filter(date__month=t, subordinate_agencies_unit__fullname__contains='漁業署', place__in=north_place))
            tmp.append(cases.filter(date__month=t, subordinate_agencies_unit__fullname__contains='漁業署', place__in=south_place))
            for i in (north_place + south_place):
                tmp.append(cases.filter(date__month=t, place=i).exclude(subordinate_agencies_unit__fullname__contains='漁業署'))
            
            tmp.append(cases.filter(date__month=t))
            for n, i in enumerate(tmp[1:]):
                if len(i) == 0: tmp[n+1] = ''
            data.append(tmp)
            
        tmp = ['小計']
        tmp.append(cases.filter(subordinate_agencies_unit__fullname__contains='漁業署', place__in=north_place))
        tmp.append(cases.filter(subordinate_agencies_unit__fullname__contains='漁業署', place__in=south_place))
        for i in (north_place + south_place):
            tmp.append(cases.filter(place=i).exclude(subordinate_agencies_unit__fullname__contains='漁業署'))
        tmp.append(cases)
        for n, i in enumerate(tmp[1:]):
            if len(i) == 0: tmp[n+1] = ''    
        data.append(tmp)
        places.append('小計')
    elif kw['table_id'] == '07': #「分類缺失排名分布表」
        def sort_by_num(a, b):
            if a.num < b.num: return 1
            else: return -1
        
        title = u'分類缺失排名分布表'
        table_id = 7
        data = []
        ecs_01 = ErrorContent.objects.filter(no__startswith='4.01').order_by('no') #工程主辦機關
        ecs_02 = ErrorContent.objects.filter(no__startswith='4.02').order_by('no') #監造單位
        ecs_03 = ErrorContent.objects.filter(no__startswith='4.03').order_by('no') #承攬廠商
        ecs_04 = ErrorContent.objects.filter(no__startswith='5.0').order_by('no').exclude(Q(no__startswith='5.05')|Q(no__startswith='5.09')|Q(no__startswith='5.08.08')|Q(no__startswith='5.08.09')|Q(no__startswith='5.08.99')) #強度Ι－混凝土、鋼筋(構)、模板、土方、結構體、裝修、雜項等：（W1）
        ecs_05 = ErrorContent.objects.filter(no__startswith='5.10').order_by('no') #強度II－材料設備檢驗與管制（W2）
        ecs_06 = ErrorContent.objects.filter(no__startswith='5.14').order_by('no') #安全（W3）
        ecs_07 = ErrorContent.objects.filter(Q(no__startswith='5.05')|Q(no__startswith='5.09')).order_by('no') #(四)環境：
        ecs_08 = ErrorContent.objects.filter(Q(no__startswith='5.08.08')|Q(no__startswith='5.08.09')|Q(no__startswith='5.08.99')).order_by('no') #(五)美觀
        ecs_09 = ErrorContent.objects.filter(no__startswith='5.17').order_by('no') #(六)功能指標
        errors = Error.objects.filter(case__in=cases)
        titles = [u'工程主辦機關', u'監造單位', u'承攬廠商', u'強度Ι－混凝土、鋼筋(構)、模板、土方、結構體、裝修、雜項等', u'強度II－材料設備檢驗與管制', u'安全', u'環境', u'美觀', u'功能指標']
        for n_ecs, ecs in enumerate([ecs_01, ecs_02, ecs_03, ecs_04, ecs_05, ecs_06, ecs_07, ecs_08, ecs_09]):
            n = 0
            for ec in ecs:
                ec.num = errors.filter(ec__no=ec.no).count()
                n += ec.num
            for ec in ecs: ec.percent = round(ec.num*100. / n, 2)
            ecs = list(ecs)
            ecs.sort(sort_by_num)
            data.append({'title': titles[n_ecs], 'n': n, 'data': ecs[:15] if len(ecs) >= 15 else ecs})


    places.insert(0, '')
    
    
    t = get_template(os.path.join('supervise', 'statisticstable_'+kw['table_id']+'.html'))
    html = t.render(RequestContext(R, {
            'title': title,
            'table_id': table_id,
            'year': year,
            'years': years,
            'all_case_num': all_case_num,
            'places': places,
            'data': data,
        }))
    return HttpResponse(html)


#讀取檔案
@login_required
def get_image(R, **kw):
    ''' 
    讀取圖片檔案 
    '''
    table_name = kw['table_name']
    row_id = kw['row_id']

    try:
        if table_name == "ErrorImprovePhoto":
            image = ErrorImprovePhoto.objects.get(id=row_id)
            if kw['field_name'] == 'before':
                if kw['is_thumb'] == 'false':
                    f = open(image.before.path, 'rb')
                else:
                    f = open(image.before.path, 'rb')
            elif kw['field_name'] == 'middle':
                if kw['is_thumb'] == 'false':
                    f = open(image.middle.path, 'rb')
                else:
                    f = open(image.middle.path, 'rb')
            elif kw['field_name'] == 'after':
                if kw['is_thumb'] == 'false':
                    f = open(image.after.path, 'rb')
                else:
                    f = open(image.after.path, 'rb')
        elif table_name == "ErrorPhotoFile":
            image = ErrorPhotoFile.objects.get(id=row_id)
            if kw['is_thumb'] == 'false':
                f = open(image.file.path, 'rb')
            else:
                f = open(image.file.path, 'rb')
    except:
        f = open(os.path.join(settings.MODULES_PATH, 'supervise', 'static', 'supervise', 'v2', 'image', 'empty.png'), 'rb')

    content = f.read()
    return HttpResponse(content, content_type='image/png')




# @checkAuthority
# def makeDocSuperviseCase(R, project, right_type_value=u'觀看管考系統資料', **kw):
#     supervise_id = kw['supervise_id']
#     row = SuperviseCase.objects.get(id=supervise_id)

#     result = {'replace': {}}
#     field_name = ['date', 'plan', 'project', 'subordinate_agencies_unit', 'project_organizer_agencies', 'project_manage_unit',
#     'designer', 'inspector', 'construct', 'budget_price', 'contract_price', 'progress_date', 'scheduled_progress',
#     'actual_progress', 'scheduled_money', 'actual_money', 'start_date', 'expected_completion_date',
#     'inspector_deduction', 'construct_deduction', 'organizer_deduction', 'project_manage_deduction'
#     ]
#     for f in field_name:
#         try:
#             value = str(getattr(row, f))
#         except:
#             value = ''
#         result['replace'][f] = value

#     if row.score >= 90: score_level = '(優等)'
#     elif row.score >= 80: score_level = '(甲等)'
#     elif row.score >= 70: score_level = '(乙等))'
#     elif row.score >= 60: score_level = '(丙等)'
#     elif row.score < 60: score_level = '(丁等)'
#     result['replace']['score'] = str(row.score) + score_level

#     result['replace']['place'] = row.place.name if row.place.name else ''
#     result['replace']['location'] = row.location.name if row.location.name else ''

#     guide = ''
#     for g in row.outguide.all():
#         guide += '外部委員：' + g.name + '^p'
#     for g in row.inguide.all():
#         guide += '內部委員：' + g.name + '^p'
#     if guide: guide = guide[:-2]
#     result['replace']['guide'] = guide

#     captain = ''
#     for g in row.captain.all():
#         captain += g.name + '、'
#     if captain: captain = captain[:-1]
#     result['replace']['captain'] = captain

#     worker = ''
#     for g in row.worker.all():
#         worker += g.name + '、'
#     if worker: worker = worker[:-1]
#     result['replace']['worker'] = worker

#     errors = Error.objects.filter(case=row).order_by('id')

#     for e in xrange(len(errors)):
#         result['replace']['error'+str(e+1)] = str(e+1) + '. ' + '(' + str(errors[e].level.name) + ')' + ' [' + str(errors[e].ec.no) + ']' + str(errors[e].context) + '^p'

#     for e in xrange(len(errors), 200):
#         result['replace']['error'+str(e+1)] = ''


#     need_batch = ['info', 'merit', 'advise', 'other_advise', 'test']
#     for f in need_batch:
#         for i in xrange(1, 21):
#             value = getattr(row, f)
#             if not value: value = ''
#             value = unicode(value)

#             if len(value) > (i * 150):
#                 result['replace'][f + str(i)] = (value[(i-1) * 150:(i) * 150]).encode('utf8')
#             elif len(value) >= ((i-1) * 150) and len(value) <= (i * 150):
#                 result['replace'][f + str(i)] = (value[(i-1) * 150:]).encode('utf8')
#             else:
#                 result['replace'][f + str(i)] = ''

#     template_name = 'supervise_caseinfo.doc'
#     content = makeFileByWordExcel(template_name=template_name, result=result)
#     response = HttpResponse(content_type='application/doc')
#     response['Content-Type'] = ('application/doc')
#     response['Content-Disposition'] = ('attachment; filename=%s.doc' % (str(row.date) + '-' + str(row.place.name) + '-' + str(row.project) + '督導紀錄表')).encode('cp950')
#     response.write(content)
#     return response\
