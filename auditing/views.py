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

response = HttpResponse()
response['Pragma'] = 'No-cache'
response['Cache-control'] = 'No-cache'

from auditing.models import Option, AuditingCase, Error, PCC_Project
from auditing.models import ErrorContent
from fishuser.models import Project
from general.models import Place, Unit, UNITS, LOAD_UNITS
from pccmating.sync import *

import decimal
import calendar
import os, random, json, re, datetime, math

from guardian.shortcuts import assign, remove_perm, get_perms

from django.conf import settings
ROOT = settings.ROOT


TODAY = lambda: datetime.date.today()
NOW = lambda: datetime.datetime.now()

TAIWAN = Place.objects.get(name=u'臺灣地區')
places = [TAIWAN] + list(Place.objects.filter(uplevel=TAIWAN).order_by('id'))
north_place_name = [u'臺北市', u'新北市', u'基隆市', u'桃園市', u'宜蘭縣', u'花蓮縣', u'新竹市', u'新竹縣', u'苗栗縣', u'臺中市', u'金門縣', u'連江縣',]
south_place_name = [u'彰化縣', u'雲林縣', u'嘉義市', u'嘉義縣', u'臺南市', u'高雄市', u'屏東縣', u'臺東縣', u'澎湖縣', u'南投縣', ]

units = LOAD_UNITS()[:]

YEARS = lambda: [y-1911 for y in xrange(TODAY().year+4, 2007, -1)]
THIS_YEAR = lambda: TODAY().year - 1911


def _make_choose():
    """製造選單列表"""
    options = Option.objects.all()
    chooses = {}
    for i in options:
        if chooses.has_key(i.swarm):
            chooses[i.swarm].append(i)
        else:
            chooses[i.swarm] = [i]
    return chooses


def ch_sort(value):
    """轉換成中文序號"""
    list_0 = [u'', u'一', u'二', u'三', u'四', u'五', u'六', u'七', u'八', u'九']
    list_1 = [u'零', u'十', u'二十', u'三十', u'四十', u'五十', u'六十', u'七十', u'八十', u'九十']
    list_2 = [u'', u'一百', u'二百', u'三百', u'四百', u'五百', u'六百', u'七百', u'八百', u'九百']
    try:
        value = int(value)
    except: return u''
    if value <= 9: return list_0[value]
    elif value <= 99: return list_1[value/10] + list_0[value%10]
    elif value <= 999:
        if value in range(100, 999, 100):
            return list_2[value/100]
        elif (value/10)%10 == 1:
            return list_2[value/100] + u'一十' + list_0[value%10]
        return list_2[value/100] + list_1[(value/10)%10] + list_0[value%10]


#搜尋頁面
@login_required
def search_page(R):
    """搜尋頁面"""
    if not R.user.has_perm('fishuser.top_menu_auditing_system'):
        return HttpResponseRedirect('/')

    new_units = set([i.unit for i in AuditingCase.objects.all()])

    t = get_template(os.path.join('auditing', 'zh-tw', 'search.html'))
    html = t.render(RequestContext(R,{
            'user': R.user,
            'places': places,
            'units': new_units,
            'toppage_name': u'查核系統',
            'subpage_name': u'搜尋',
        }))
    return HttpResponse(html)


#執行搜尋動作
@login_required
def search_case(R):
    """根據輸入資訊搜尋查核工程"""
    if not R.user.has_perm('fishuser.top_menu_auditing_system'):
        return HttpResponseRedirect('/')

    info = R.POST
    result = AuditingCase.objects.all().order_by('-date', 'project_name').prefetch_related('project')
    #工程名稱
    if info.get('project_name', '') and info.get('project_name', '') != '' and info.get('project_name', '') != 'undefined':
        ids = []
        for key in re.split('[ ,]+', info.get('project_name', '')):
            if not key.replace(' ', ''): continue
            ids.extend([i.id for i in result.filter(project_name__icontains=key)])
        result = result.filter(id__in=ids)

    #查核日期
    if info.get('date_from', '') and info.get('date_from', '') != '' and info.get('date_from', '') != 'undefined':
        result = result.filter(date__gte=info.get('date_from', ''), date__lte=info.get('date_to', ''))
    
    #查核分數
    if info.get('score_from', '') and info.get('score_from', '') != '' and info.get('score_from', '') != 'undefined':
        score_from = str(float(info.get('score_from', '')))
        score_to = str(float(info.get('score_to', '')))
        result = result.filter(score__gte=score_from, score__lte=score_to)

    #主辦機關
    if info.get('project_unit', '') and info.get('project_unit', '') != '' and info.get('project_unit', '') != 'undefined':
        unit = Unit.objects.get(id=info.get('project_unit', ''))
        result = result.filter(unit=unit)

    #專案管理單位
    if info.get('project_manage_unit', '') and info.get('project_manage_unit', '') != '' and info.get('project_manage_unit', '') != 'undefined':
        ids = []
        for key in re.split('[ ,]+', info.get('project_manage_unit', '')):
            if not key.replace(' ', ''): continue
            ids.extend([i.id for i in result.filter(project_manage_unit__icontains=key)])
        result = result.filter(id__in=ids)

    #設計單位
    if info.get('designer', '') and info.get('designer', '') != '' and info.get('designer', '') != 'undefined':
        ids = []
        for key in re.split('[ ,]+', info.get('designer', '')):
            if not key.replace(' ', ''): continue
            ids.extend([i.id for i in result.filter(designer__icontains=key)])
        result = result.filter(id__in=ids)

    #監造單位
    if info.get('inspector', '') and info.get('inspector', '') != '' and info.get('inspector', '') != 'undefined':
        ids = []
        for key in re.split('[ ,]+', info.get('inspector', '')):
            if not key.replace(' ', ''): continue
            ids.extend([i.id for i in result.filter(inspector__icontains=key)])
        result = result.filter(id__in=ids)

    #承包廠商
    if info.get('construct', '') and info.get('construct', '') != '' and info.get('construct', '') != 'undefined':
        ids = []
        for key in re.split('[ ,]+', info.get('construct', '')):
            if not key.replace(' ', ''): continue
            ids.extend([i.id for i in result.filter(construct__icontains=key)])
        result = result.filter(id__in=ids)

    #行政區
    if info.get('place', '') and info.get('place', '') != '' and info.get('place', '') != 'undefined':
        place = Place.objects.get(id=info.get('place', ''))
        result = result.filter(place=place)

    #發包預算
    if info.get('budget_price_from', '') and info.get('budget_price_from', '') != '' and info.get('budget_price_from', '') != 'undefined':
        budget_price_from = str(float(info.get('budget_price_from', '')) * 1000)
        budget_price_to = str(float(info.get('budget_price_to', '')) * 1000)
        result = result.filter(budget_price__gte=budget_price_from, budget_price__lte=budget_price_to)

    #契約金額
    if info.get('contract_price_from', '') and info.get('contract_price_from', '') != '' and info.get('contract_price_from', '') != 'undefined':
        contract_price_from = str(float(info.get('contract_price_from', '')) * 1000)
        contract_price_to = str(float(info.get('contract_price_to', '')) * 1000)
        result = result.filter(contract_price__gte=contract_price_from, contract_price__lte=contract_price_to)

    #外部委員
    if info.get('supervisors', '') and info.get('supervisors', '') != '' and info.get('supervisors', '') != 'undefined':
        ids = []
        for key in re.split('[ ,]+', info.get('supervisors', '')):
            if not key.replace(' ', ''): continue
            ids.extend([i.id for i in result.filter(supervisors_outside__icontains=key)])
            ids.extend([i.id for i in result.filter(supervisors_inside__icontains=key)])
        result = result.filter(id__in=ids)


    #缺失
    if info.get('error', '') and info.get('error', '') != '' and info.get('error', '') != 'undefined':
        key = R.POST.get('error')
        ids = []
        for k in re.split('[ ,]+', key):
            if not k.replace(' ', ''): continue
            ids.extend([i.case.id for i in Error.objects.filter(errorcontent__no__icontains=k)])
            ids.extend([i.case.id for i in Error.objects.filter(context__icontains=k)])
        result = result.filter(id__in=ids)
    data = {}
    data['offsetid'] = int(info.get('offsetid', 0))
    if data['offsetid']: data['previous'] = True
    data['limit'] = int(info.get('limit', 25))
    data['total_count'] = result.count()
    if data['total_count'] > (data['offsetid'] + data['limit']):
        data['next'] = True
        result = result[data['offsetid']: data['offsetid'] + data['limit']]
    else:
        data['next'] = False
        result = result[data['offsetid']:]

    data['result'] = []
    for n, i in enumerate(result):
        row = {
            'sort': n + data['offsetid'] + 1,
            'id': i.id,
            'date': str(i.date),
            'auditing_group': i.auditing_group or '',
            'project_name': i.project_name,
            'project_unit_name': i.unit.name,
            'location_name': i.place.name if i.place else '',
            'score': str(i.score).replace('.00', ''),
        }
        data['result'].append(row)
    return HttpResponse(json.dumps(data))


#觀看查核案詳細資料
@login_required
def view_profile(R, **kw):
    """編輯查核案詳細資料"""
    case = AuditingCase.objects.get(id=kw['case_id'])
    if not R.user.has_perm('fishuser.top_menu_auditing_system'):
        return HttpResponseRedirect('/')

    case.errors = Error.objects.filter(case=case).order_by('id')
    for error in case.errors:
        error.context = error.context.replace('\n', '').replace('\r', '')
        error.save()

    t = get_template(os.path.join('auditing', 'zh-tw', 'view_profile.html'))
    html = t.render(RequestContext(R,{
            'user': R.user,
            'case': case,
            'years': YEARS(),
            'units': units,
            'places': places,
            'this_year': THIS_YEAR(),
            'options': _make_choose(),
            'toppage_name': u'查核系統',
        }))
    return HttpResponse(html)

