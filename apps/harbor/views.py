# -*- coding:utf8 -*-
from sha import sha
from django.template.loader import get_template
from django.template import Context, RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import auth
from django.db.models import Q
from django.db import models as M
from django import forms
from django.contrib.auth.models import User, Group
from django.contrib.sessions.models import Session
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.core.mail import send_mail
from django.forms import ModelForm

from django import forms
from django.shortcuts import render_to_response

from common.models import Log

from fishuser.views import checkAuthority
from fishuser.models import UserProfile
from fishuser.models import CountyChaseTime
from fishuser.models import CountyChaseProjectOneByOne
from fishuser.models import CountyChaseProjectOneToMany


from harbor.models import Option
from harbor.models import Observatory
from harbor.models import FishingPort
from harbor.models import PortFisheryOutput
from harbor.models import FishingPortBoat
from harbor.models import MainProject
from harbor.models import Project
from harbor.models import Waves
from harbor.models import Tide
from harbor.models import FishingPortPhoto
from harbor.models import AverageRainfall
from harbor.models import AverageTemperature
from harbor.models import AveragePressure
from harbor.models import City
from harbor.models import FisheryOutput
from harbor.models import FishType
from harbor.models import FisheryType
from harbor.models import AquaculturePublic
from harbor.models import AquaculturePublicWork
from harbor.models import PortInstallationRecord
from harbor.models import TempFile
from harbor.models import DataShare
from harbor.models import Reef
from harbor.models import ReefLocation
from harbor.models import ReefPut
from harbor.models import ReefPutNum
from harbor.models import ReefProject
from harbor.models import ReefData

from dailyreport.models import EngProfile
from dailyreport.models import Version
from dailyreport.models import Report

from monitor.models import Account

from general.models import Place, Unit, UNITS, LOAD_UNITS
from common.lib import find_sub_level, find_sub, nocache_response, md5password, readDATA, verifyOK, makePageList
from common.templatetags.utiltags import thumb

from fishuser.models import _ca
from fishuser.models import Project as FA_project
import decimal
import numpy as np

from itertools import izip_longest
import random
import json
import shutil
import smtplib
import os, datetime, StringIO
import time
from time import strftime
import re, sys
from urllib import urlopen

if not hasattr(json, "write"):
    #for python2.6
    json.write = json.dumps
    json.read = json.loads

from django.conf import settings
CAN_VIEW_BUG_PAGE_IPS = settings.CAN_VIEW_BUG_PAGE_IPS
NUMPERPAGE = settings.NUMPERPAGE
ROOT = settings.ROOT

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


@login_required
def index(R):
    if not R.user.has_perm('fishuser.top_menu_harbor_system'):
        # 沒有 "第一層選單_漁港資訊系統"
        return HttpResponseRedirect('/')
    year = R.POST.get('year', '')
    fishingport_list = FishingPort.objects.all()
    today = datetime.date.today() - datetime.timedelta(days=7)
    for p in places:
        p.first_port = fishingport_list.filter(place=p, type__value=u"第一類漁港")
        p.second_port = fishingport_list.filter(place=p, type__value=u"第二類漁港")
        p.delete_port = fishingport_list.filter(place=p, type__value=u"廢除、合併或其他")
        p.fourth_port = fishingport_list.filter(place=p, type__value=u"第四類漁港")
        p.reef = Reef.objects.filter(place=p)
        p.projects = FA_project.objects.filter(year=this_year,deleter=None,place=p.id).order_by('id')
        #未結案之工程
        p.is_nofinishs = CountyChaseProjectOneByOne.objects.filter(project__in=p.projects).exclude(act_eng_do_closed__isnull=False, project__purchase_type__value__in=[u"工程", u"工程勞務"]).exclude(act_ser_acceptance_closed__isnull=False, project__purchase_type__value=u"一般勞務")
        #p.nofinish_ids = [i.project.id for i in p.is_nofinishs]
        p.nofinishs_completion_date = [i.sch_eng_do_completion if i.sch_eng_do_completion else '' for i in p.is_nofinishs]
        p.nofinishs_start_date = [i.sch_eng_do_start if i.sch_eng_do_start else '' for i in p.is_nofinishs]
        p.nofinish_names = [i.project.name for i in p.is_nofinishs]
        p.nofinish_ids = [i.project.id for i in p.is_nofinishs]

        p.nofinish_progress_act_contractor = []
        p.nofinish_progress_act_inspector = []
        p.nofinish_progress_design = []
        p.engprofile_status = []
        p.nofinish_total_money = []

        for i in p.is_nofinishs:
            try:
                p.engprofile = EngProfile.objects.filter(project_id=i.project_id).last()
                p.nofinish_progress_act_contractor.append(int(p.engprofile.act_contractor_percent))
                p.nofinish_progress_act_inspector.append(int(p.engprofile.act_inspector_percent)) 
                p.nofinish_progress_design.append(int(p.engprofile.design_percent))
            except:
                p.nofinish_progress_act_contractor.append('0')
                p.nofinish_progress_act_inspector.append('0')
                p.nofinish_progress_design.append('0')

            try:
                p.is_nofinishs_version = Version.objects.filter(project_id=i.project_id).last()
                p.nofinish_total_money.append(p.is_nofinishs_version.engs_price)

                try:
                    p.is_nofinishs_contractor = Report.objects.filter(project_id=i.project_id,contractor_check=True).order_by('date').last()
                    p.is_nofinishs_inspector = Report.objects.filter(project_id=i.project_id,inspector_check=True).order_by('date').last()
                    if p.is_nofinishs_version.engs_price == 0:
                        p.engprofile_status.append('未開始填寫報表')
                        
                    elif i.sch_eng_do_completion:
                        if i.sch_eng_do_completion == p.is_nofinishs_contractor.date and i.sch_eng_do_completion == p.is_nofinishs_inspector.date:
                            p.engprofile_status.append('施工和監造報日表已填寫完畢')
                        elif i.sch_eng_do_completion == p.is_nofinishs_contractor.date:
                            p.engprofile_status.append('施工日報表已填寫完畢(未落實填寫監造日報表)')
                        elif i.sch_eng_do_completion == p.is_nofinishs_inspector.date:
                            p.engprofile_status.append('監造日報表已填寫完畢(未落實填寫施工日報表)')
                        elif today < p.is_nofinishs_contractor.date and today < p.is_nofinishs_inspector.date:
                            p.engprofile_status.append('施工和監造日報表已落實填寫')
                        elif today < p.is_nofinishs_contractor.date:
                            p.engprofile_status.append('施工日報表已落實填寫(未落實填寫監造日報表)')
                        elif today < p.is_nofinishs_inspector.date:
                            p.engprofile_status.append('監造日報表已落實填寫(未落實填寫施工日報表)')
                        else:
                            p.engprofile_status.append('未落實填寫施工和監造日報表')

                    elif today < p.is_nofinishs_contractor.date and today < p.is_nofinishs_inspector.date:
                        p.engprofile_status.append('施工和監造日報表已落實填寫')
                    elif today < p.is_nofinishs_contractor.date:
                        p.engprofile_status.append('施工日報表已落實填寫(未落實填寫監造日報表)')
                    elif today < p.is_nofinishs_inspector.date:
                        p.engprofile_status.append('監造日報表已落實填寫(未落實填寫施工日報表)')
                    else:
                        p.engprofile_status.append('未落實填寫施工和監造日報表')
                except :
                    p.engprofile_status.append('未開始填寫施工和監造日報表')

            except:
                p.engprofile_status.append('未開始填寫報表')
                p.nofinish_total_money.append('0.000')

        p.nofinish_total = izip_longest(p.nofinish_names, p.nofinish_progress_design,
                                        p.nofinish_progress_act_inspector, p.nofinish_progress_act_contractor,
                                        p.nofinishs_start_date, p.nofinishs_completion_date,
                                        p.nofinish_total_money, p.engprofile_status, p.nofinish_ids, fillvalue='0')

        #已結案之工程
        p.is_finishs = CountyChaseProjectOneByOne.objects.filter(project__in=p.projects).exclude(act_eng_do_closed__isnull=True, project__purchase_type__value__in=[u"工程", u"工程勞務"]).exclude(act_ser_acceptance_closed__isnull=True, project__purchase_type__value=u"一般勞務")
        p.finishs_completion_date = [i.sch_eng_do_completion if i.sch_eng_do_completion else '' for i in p.is_finishs]
        p.finishs_start_date = [i.sch_eng_do_start if i.sch_eng_do_start else '' for i in p.is_finishs]
        p.finish_names = [i.project.name for i in p.is_finishs]
        p.finish_ids = [i.project.id for i in p.is_finishs]

        p.finish_progress_act_contractor = []
        p.finish_progress_act_inspector = []
        p.finish_progress_design = []
        p.finish_engprofile_status = []
        p.finish_total_money = []

        for i in p.is_finishs:
            try:
                p.engprofile = EngProfile.objects.filter(project_id=i.project_id).last()
                p.finish_progress_act_contractor.append(int(p.engprofile.act_contractor_percent))
                p.finish_progress_act_inspector.append(int(p.engprofile.act_inspector_percent))
                p.finish_progress_design.append(int(p.engprofile.design_percent))
            except:
                p.finish_progress_act_contractor.append('0')
                p.finish_progress_act_inspector.append('0')
                p.finish_progress_design.append('0')

            try:
                p.is_finishs_version = Version.objects.filter(project_id=i.project_id).last()
                p.finish_total_money.append(p.is_finishs_version.engs_price)

                try:
                    p.is_finishs_contractor = Report.objects.filter(project_id=i.project_id,
                                                                      contractor_check=True).order_by('date').last()
                    p.is_finishs_inspector = Report.objects.filter(project_id=i.project_id,
                                                                     inspector_check=True).order_by('date').last()
                    if p.is_finishs_version.engs_price == 0:
                        p.finish_engprofile_status.append('未開始填寫報表')

                    elif i.sch_eng_do_completion:
                        if i.sch_eng_do_completion == p.is_finishs_contractor.date and i.sch_eng_do_completion == p.is_finishs_inspector.date:
                            p.finish_engprofile_status.append('施工和監造報日表已填寫完畢')
                        elif i.sch_eng_do_completion == p.is_finishs_contractor.date:
                            p.finish_engprofile_status.append('施工日報表已填寫完畢(未落實填寫監造日報表)')
                        elif i.sch_eng_do_completion == p.is_finishs_inspector.date:
                            p.finish_engprofile_status.append('監造日報表已填寫完畢(未落實填寫施工日報表)')
                        elif today < p.is_finishs_contractor.date and today < p.is_finishs_inspector.date:
                            p.finish_engprofile_status.append('施工和監造日報表已落實填寫')
                        elif today < p.is_finishs_contractor.date:
                            p.finish_engprofile_status.append('施工日報表已落實填寫(未落實填寫監造日報表)')
                        elif today < p.is_finishs_inspector.date:
                            p.finish_engprofile_status.append('監造日報表已落實填寫(未落實填寫施工日報表)')
                        else:
                            p.finish_engprofile_status.append('未落實填寫施工和監造日報表')

                    elif today < p.is_finishs_contractor.date and today < p.is_finishs_inspector.date:
                        p.finish_engprofile_status.append('施工和監造日報表已落實填寫')
                    elif today < p.is_finishs_contractor.date:
                        p.finish_engprofile_status.append('施工日報表已落實填寫(未落實填寫監造日報表)')
                    elif today < p.is_finishs_inspector.date:
                        p.finish_engprofile_status.append('監造日報表已落實填寫(未落實填寫施工日報表)')
                    else:
                        p.finish_engprofile_status.append('未落實填寫施工和監造日報表')
                except:
                    p.finish_engprofile_status.append('未開始填寫施工和監造日報表')

            except:
                p.finish_engprofile_status.append('未開始填寫報表')
                p.finish_total_money.append('0.000')

        p.finish_total = izip_longest(p.finish_names, p.finish_progress_design, p.finish_progress_act_inspector,
                                        p.finish_progress_act_contractor, p.finishs_start_date,
                                        p.finishs_completion_date, p.finish_total_money, p.finish_engprofile_status,p.finish_ids,
                                        fillvalue='0')

    projects = FA_project.objects.filter(year=this_year,deleter=None).exclude(place=1).exclude(place=2)
    is_finishs = CountyChaseProjectOneByOne.objects.filter(project__in=projects).exclude(act_eng_do_closed__isnull=True, project__purchase_type__value__in=[u"工程", u"工程勞務"]).exclude(act_ser_acceptance_closed__isnull=True, project__purchase_type__value=u"一般勞務")
    
    is_finish_ids = [i.project.id for i in is_finishs]
    project_finish = len(is_finish_ids)
    project_total = len(list(projects))
    project_nofinish = project_total - project_finish
    
    t = get_template(os.path.join('harbor', 'zh-tw', 'index.html'))
    html = t.render(RequestContext(R,{
        'project_total': project_total,
        'project_finish':project_finish,
        'project_nofinish':project_nofinish,
        'user': R.user,
        'years': years,
        'places': places,
        'toppage_name': u'漁港資訊系統',
        'subpage_name': u'資訊主頁',
        }))
    return HttpResponse(html)


@login_required
def port_profile(R, **kw):
    if not R.user.has_perm('fishuser.top_menu_harbor_system'):
        # 沒有 "第一層選單_漁港資訊系統"
        return HttpResponseRedirect('/')

    if R.user.has_perm('fishuser.sub_menu_harbor_system_edit'):
        # "第二層選單_漁港資訊系統_編輯資訊"
        edit = True
    else:
        edit = False

    port = FishingPort.objects.get(id=kw['port_id'])
    if R.user.username[1] == '_':
        account = User.objects.get(username=R.user.username[:2] + 'account')
        if account.user_profile.unit.name[:3] == port.place.name:
            have_page_image = True
        else:
            have_page_image = False
    else:
        have_page_image = True
    option = _make_choose()
    photos = FishingPortPhoto.objects.filter(fishingport=port)
    for type in option['photo_type']:
        type.photo = photos.filter(type=type)

    boats = port.fishingportboat_set.all()
    port.boat_type = []
    boat_type = Option.objects.filter(swarm="boat_type").order_by('id')
    for t in boat_type:
        if boats.filter(boat_type=t):
            port.boat_type.append(t)
    port.boats = []
    for y in xrange(70, 200):
        if boats.filter(year=y):
            temp = [FishingPortBoat(num=y)]
            for t in port.boat_type:
                if boats.filter(year=y, boat_type=t):
                    temp.append(boats.filter(year=y, boat_type=t)[0])
                else:
                    temp.append('')
            port.boats.append(temp)

    port.fes_project = FA_project.objects.filter(fishing_port=port).order_by('-year')
    port.mainprojects = port.mainproject_set.all().order_by('-year', '-id')
    port.projects = port.project_set.all().order_by('-year', '-id')
    port.files = port.tempfile_set.all().order_by('upload_user', '-upload_date')
    for f in port.files:
        if R.user.is_staff or R.user == f.upload_user: f.edit = True
        else: f.edit = False

    t = get_template(os.path.join('harbor', 'zh-tw', 'port_profile.html'))
    html = t.render(RequestContext(R,{
        'user': R.user,
        'edit': edit,
        'port': port,
        'photos': photos,
        'have_page_image': have_page_image,
        'option': option,
        'toppage_name': u'漁港資訊系統',
        'subpage_name': u'資訊主頁',
        }))
    return HttpResponse(html)


@login_required
def place_profile(R, **kw):
    if not R.user.has_perm('fishuser.top_menu_harbor_system'):
        # 沒有 "第一層選單_漁港資訊系統"
        return HttpResponseRedirect('/')

    if R.user.has_perm('fishuser.sub_menu_harbor_system_edit'):
        # "第二層選單_漁港資訊系統_編輯資訊"
        edit = True
    else:
        edit = False

    place = Place.objects.get(id=kw['place_id'])
    place.aquaculturepublicworks = place.aquaculturepublicwork_set.all().order_by('-year')
    place.aquaculturepublics = place.aquaculturepublic_set.all().order_by('-year')

    t = get_template(os.path.join('harbor', 'zh-tw', 'place_profile.html'))
    html = t.render(RequestContext(R,{
        'user': R.user,
        'edit': edit,
        'place': place,
        'city': place.city_set.get(),
        'option': _make_choose(),
        'toppage_name': u'漁港資訊系統',
        'subpage_name': u'資訊主頁',
        }))
    return HttpResponse(html)


@login_required
def reef_profile(R, **kw):
    #魚礁區基本資料
    if not R.user.has_perm('fishuser.top_menu_harbor_system'):
        # 沒有 "第一層選單_漁港資訊系統"
        return HttpResponseRedirect('/')

    if R.user.has_perm('fishuser.sub_menu_harbor_system_edit') or R.user.is_staff:
        # "第二層選單_漁港資訊系統_編輯資訊"
        edit = True
    else:
        edit = False

    reef = Reef.objects.get(id=kw['reef_id'])
    reef.reefputs = ReefPut.objects.filter(reef=reef)
    reef.projects = ReefProject.objects.filter(reef=reef)
    reef.datas = ReefData.objects.filter(reef=reef)
    reef.files = ReefData.objects.filter(reef=reef)

    t = get_template(os.path.join('harbor', 'zh-tw', 'reef_profile.html'))
    html = t.render(RequestContext(R,{
        'user': R.user,
        'edit': edit,
        'reef': reef,
        'option': _make_choose(),
        'toppage_name': u'漁港資訊系統',
        'subpage_name': u'資訊主頁',
        }))
    return HttpResponse(html)


#下載檔案專用
@login_required
def download_file(R, **kw):
    if not R.user.has_perm('fishuser.top_menu_harbor_system'):
        # 沒有 "第一層選單_漁港資訊系統"
        return HttpResponseRedirect('/')

    table_name = kw['table_name'] 
    file_id = kw['file_id']

    if table_name == 'TempFile':
        row = TempFile.objects.get(id=kw["file_id"])
    elif table_name == 'FishingPortPhoto':
        row = FishingPortPhoto.objects.get(id=kw["file_id"])
    elif table_name == 'DataShare':
        row = DataShare.objects.get(id=kw["file_id"])
    elif table_name == 'ReefData':
        row = ReefData.objects.get(id=kw["file_id"])

    f = open(os.path.join(ROOT, row.file.name), 'rb')
    content = f.read()
    response = HttpResponse(content_type='application/' + row.rExt())
    response['Content-Type'] = ('application/' + row.rExt())
    file_name = row.name.replace(" ", "") + '.' + row.rExt()
    response['Content-Disposition'] = ('attachment; filename='+ file_name).encode('cp950', 'replace')
    response.write(content)
    return response


#上傳檔案的處理
@login_required
def new_file_upload(R):
    data = R.POST
    table_name = data['table_name']

    f = R.FILES.get('file', None)
    full_name = f.name.split(".")
    ext = full_name[-1]
    full_name.remove(full_name[-1])
    name = "".join(full_name)

    if table_name == 'TempFile':
        port = FishingPort.objects.get(id=data['row_id'])
        new = TempFile(
            name = name,
            fishingport = port,
            upload_user = R.user,
            upload_date = TODAY()
        )
        new.save()
        getattr(new, 'file').save('%s.%s'%(new.id, ext), f)
        new.save()
    elif table_name == 'FishingPortPhoto':
        fishingport = FishingPort.objects.get(id=data['fishingport'].split('/')[-2])
        type = Option.objects.get(id=data['type'].split('/')[-2])
        name = data['name'] if data['name'] else name
        new = FishingPortPhoto(
            name = name,
            type = type,
            extname = ext,
            fishingport = fishingport
        )
        new.save()
        getattr(new, 'file').save('%s.%s'%(new.id, ext), f)
        new.save()
    elif table_name == 'DataShare':
        new = DataShare(
            name = name,
            upload_user = R.user,
            upload_date = TODAY()
        )
        new.save()
        getattr(new, 'file').save('%s.%s'%(new.id, ext), f)
        new.save()
    elif table_name == 'ReefData':
        reef = Reef.objects.get(id=data['row_id'])
        new = ReefData(
            name = name,
            reef = reef,
            upload_date = TODAY()
        )
        new.save()
        getattr(new, 'file').save('%s.%s'%(new.id, ext), f)
        new.save()

    return HttpResponse(json.dumps({'status': True, 'id': new.id, 'name': new.name, 'rExt': ext, 'upload_date': str(TODAY())}))


#港區監控系統
@login_required
def webcam(R):
    if not R.user.has_perm('fishuser.top_menu_harbor_system'):
        # 沒有 "第一層選單_漁港資訊系統"
        return HttpResponseRedirect('/')

    if R.user.username[1] != '_' or R.user.is_staff:
        allow_list = '0'
    else:
        account = User.objects.get(username=R.user.username[:2]+'account')
        unit_name = account.user_profile.unit.name[:3]
        allow_list = str(Place.objects.get(name=unit_name).id)

    now = NOW().strftime('%Y-%m-%d %H:%M:%S')
    verify_key = sha('%s: %s'%(now, allow_list)).hexdigest()
    
    t = get_template(os.path.join('harbor', 'zh-tw', 'webcam.html'))
    html = t.render(RequestContext(R,{
        'user': R.user,
        'allow_list': allow_list,
        'now': now,
        'verify_key': verify_key,
        'option': _make_choose(),
        'toppage_name': u'漁港資訊系統',
        'subpage_name': u'港區監控系統',
        }))
    return HttpResponse(html)


#港區錄影系統
@login_required
def webcam_record(R):
    if not R.user.has_perm('fishuser.top_menu_harbor_system'):
        # 沒有 "第一層選單_漁港資訊系統"
        return HttpResponseRedirect('/')

    if R.user.username[1] != '_' or R.user.is_staff:
        allow_list = '0'
    else:
        account = User.objects.get(username=R.user.username[:2]+'account')
        unit_name = account.user_profile.unit.name[:3]
        allow_list = str(Place.objects.get(name=unit_name).id)
    now = NOW().strftime('%Y-%m-%d %H:%M:%S')
    verify_key = sha('%s: %s'%(now, allow_list)).hexdigest()
    
    t = get_template(os.path.join('harbor', 'zh-tw', 'webcam_record.html'))
    html = t.render(RequestContext(R,{
        'user': R.user,
        'allow_list': allow_list,
        'now': now,
        'verify_key': verify_key,
        'option': _make_choose(),
        'toppage_name': u'漁港資訊系統',
        'subpage_name': u'港區錄影系統',
        }))
    return HttpResponse(html)



#資料交換區
@login_required
def datashare(R):
    if not R.user.has_perm('fishuser.top_menu_harbor_system'):
        # 沒有 "第一層選單_漁港資訊系統"
        return HttpResponseRedirect('/')

    files = DataShare.objects.all()
    for f in files:
        if R.user.is_staff or R.user == f.upload_user: f.edit = True
        else: f.edit = False
    
    t = get_template(os.path.join('harbor', 'zh-tw', 'datashare.html'))
    html = t.render(RequestContext(R,{
        'user': R.user,
        'files': files,
        'option': _make_choose(),
        'toppage_name': u'漁港資訊系統',
        'subpage_name': u'資料交換區',
        }))
    return HttpResponse(html)



#漁港設施記錄
@login_required
def portinstallationrecord(R):
    if not R.user.has_perm('fishuser.top_menu_harbor_system'):
        # 沒有 "第一層選單_漁港資訊系統"
        return HttpResponseRedirect('/')

    if R.user.has_perm('fishuser.sub_menu_harbor_system_edit_portinstallationrecord'):
        # "第二層選單_漁港資訊系統_填報漁港設施記錄"
        edit = True
    else:
        edit = False

    new_units = []
    for u in units:
        if u'漁會' in u.name:
            new_units.append(u)

    t = get_template(os.path.join('harbor', 'zh-tw', 'portinstallationrecord.html'))
    html = t.render(RequestContext(R,{
        'user': R.user,
        'place': places[1:],
        'edit': edit,
        'units': new_units,
        'range24': range(24),
        'option': _make_choose(),
        'toppage_name': u'漁港資訊系統',
        'subpage_name': u'漁港設施記錄',
        }))
    return HttpResponse(html)



#編輯資訊
@login_required
def edit_information(R):
    if not R.user.has_perm('fishuser.sub_menu_harbor_system_edit'):
        # 沒有 "第二層選單_漁港資訊系統_編輯資訊"
        return HttpResponseRedirect('/')

    accounts = Account.objects.all().order_by('monitor__place', 'monitor__port', 'monitor__name', 'type')
    observatorys = Observatory.objects.all().order_by('name')
    t = get_template(os.path.join('harbor', 'zh-tw', 'edit_information.html'))
    html = t.render(RequestContext(R,{
        'user': R.user,
        'places': places[1:],
        'accounts': accounts,
        'observatorys': observatorys,
        'option': _make_choose(),
        'toppage_name': u'漁港資訊系統',
        'subpage_name': u'編輯資訊',
        }))
    return HttpResponse(html)


#替換風花圖
@login_required
def observatory_file_upload(R):
    data = R.POST
    row_id = data['row_id']
    f = R.FILES.get('file', None)
    full_name = f.name.split(".")
    ext = full_name[-1]
    full_name.remove(full_name[-1])
    name = "".join(full_name)
    row = Observatory.objects.get(id=row_id)
    try:
        os.remove(os.path.join(ROOT, row.file.name))
    except: pass
    row.extname = ext
    getattr(row, 'file').save('%s-%s.%s'%(row.id, NOW(), ext), f)
    row.save()

    return HttpResponse(json.dumps({'status': True, 'id': row.id, 'url': row.rUrl()}))




#新增攝影機
@login_required
def webcam_create(R):
    if not R.user.has_perm('fishuser.sub_menu_harbor_system_edit'):
        # 沒有 "第二層選單_漁港資訊系統_編輯資訊"
        return HttpResponseRedirect('/')

    t = get_template(os.path.join('harbor', 'zh-tw', 'edit_page_webcam_create.html'))
    html = t.render(RequestContext(R,{
        'user': R.user,
        'places': places[1:],
        'option': _make_choose(),
        }))
    return HttpResponse(html)


















# 以下舊分頁------------------------------------------------------------------
# from harbor.views_201012_by_cerberus import fish_pool_list as fish_pool_list_201012_by_cerberus
# from harbor.views_201012_by_cerberus import fish_pool_create as fish_pool_create_201012_by_cerberus
# from harbor.views_201012_by_cerberus import fish_pool_edit as fish_pool_edit_201012_by_cerberus
# from harbor.views_201012_by_cerberus import fish_pool_update as fish_pool_update_201012_by_cerberus
# from harbor.views_201012_by_cerberus import fish_pool_delete as fish_pool_delete_201012_by_cerberus
# from harbor.views_20101230_by_cerberus import accounting_20101230_by_cerberus

# def _cMemu():
#     fishingport_list = FishingPort.objects.all()
#     city_list = City.objects.all()
#     observatory_list = Observatory.objects.all()
#     for i in city_list:
#         i.fishingport = []
#         for j in fishingport_list:
#             if i.place == j.place:
#                 i.fishingport.append(j)

#     class memu(): (city, obva) = (city_list, observatory_list)
#     return memu()


# def _cWriter(R):
#     user = R.user
#     if user.user_profile.group.name == '漁港資訊填寫員':
#         writer = 'PI'
#     elif user.user_profile.group.name == '漁船填寫員':
#         writer = 'BI'
#     elif user.is_staff:
#         writer = 'PI'
#     return writer


# @checkAuthority
# def rLiveWebcamLink(R, **kw):
#     user = R.user
#     if user.username[1] != '_' or user.is_staff:
#         allow_list = '0'
#     else:
#         account = User.objects.get(username=user.username[:2]+'account')
#         unit_name = UserProfile.objects.get(user=account).unit.name[:3]
#         allow_list = str(Place.objects.get(name=unit_name).id)
#     now = _NOW().strftime('%Y-%m-%d %H:%M:%S')
#     verify_key = sha('%s: %s'%(now, allow_list)).hexdigest()

#     t = get_template(os.path.join('harbor', 'live_webcam_link.html'))
#     html = t.render(RequestContext(R,{'allow_list': allow_list,
#                                         'now': now,
#                                         'verify_key': verify_key}))
#     return HttpResponse(html)

# @checkAuthority
# def rReplayLink(R, **kw):
#     user = R.user
#     if user.username[1] != '_' or user.is_staff:
#         allow_list = '0'
#     else:
#         account = User.objects.get(username=user.username[:2]+'account')
#         unit_name = UserProfile.objects.get(user=account).unit.name[:3]
#         allow_list = str(Place.objects.get(name=unit_name).id)
#     now = _NOW().strftime('%Y-%m-%d %H:%M:%S')
#     verify_key = sha('%s: %s'%(now, allow_list)).hexdigest()

#     t = get_template(os.path.join('harbor', 'replay_link.html'))
#     html = t.render(RequestContext(R,{'allow_list': allow_list,
#                                         'now': now,
#                                         'verify_key': verify_key}))
#     return HttpResponse(html)

# @checkAuthority
# def rDataShare(R, **kw):
#     user, DATA = R.user, readDATA(R)

#     files = DataShare.objects.all().order_by('upload_user', '-upload_date')

#     if R.POST.get('submit', ''):
#         row = DataShare(
#                     name = R.POST.get('name',''),
#                     memo = R.POST.get('memo',''),
#                     upload_user = user,
#                     upload_date = TODAY(),
#                     )
#         row.save()
#         file = R.FILES.get('file', None)
#         try:
#             ext = file.name.split('.')[-1]
#         except:
#             ext = 'zip'

#         getattr(row, 'file').save('%s.%s'%(row.id, ext), file)
#         row.save()

#     t = get_template(os.path.join('harbor', 'vdata_share.html'))
#     html = t.render(RequestContext(R,{'files': files
#     }))
#     return HttpResponse(html)


# @checkAuthority
# def rIndex(R, **kw):
#     fishingport_list = FishingPort.objects.all()
#     city_list = City.objects.all()
#     observatory_list = Observatory.objects.all()
#     for i in city_list:
#         i.fishingport = []
#         for j in fishingport_list:
#             if i.place == j.place:
#                 i.fishingport.append(j)
#     t = get_template(os.path.join('harbor', 'editmemu.html'))
#     html = t.render(RequestContext(R,{'writer':_cWriter(R), 'city_list':city_list,
#                                         'observatory_list':observatory_list}))
#     return HttpResponse(html)

# @checkAuthority
# def UploadPortFile(R, **kw):
#     port = FishingPort.objects.get(id=kw['port_id'])
#     page = 'PortFiles'
#     user, DATA = R.user, readDATA(R)
#     if user.user_profile.group.name in ['主辦工程師', '上層管理者', '管考填寫員'] or user.is_staff:
#         can_upload = True
#     else:
#         can_upload = False

#     files = TempFile.objects.filter(fishingport=port).order_by('upload_user', '-upload_date')

#     if R.POST.get('submit', ''):
#         row = TempFile(
#                     name = R.POST.get('name',''),
#                     memo = R.POST.get('memo',''),
#                     fishingport = port,
#                     upload_user = user,
#                     upload_date = TODAY(),
#                     )
#         row.save()
#         file = R.FILES.get('file', None)
#         try:
#             ext = file.name.split('.')[-1]
#         except:
#             ext = 'zip'
# #        if ext in ['jpg', 'jpeg', 'tiff', 'tif', 'png', 'gif']:
# #            thumb(row.file.name, "width=1024,height=768")

#         getattr(row, 'file').save('%s.%s'%(row.id, ext), file)
#         row.save()

#     t = get_template(os.path.join('harbor', 'vportfile.html'))
#     html = t.render(RequestContext(R,{'port': port, 'page': page, 'files': files,
#                                       'can_upload': can_upload
#     }))
#     return HttpResponse(html)


# @checkAuthority
# def port(R, **kw):
#     port = FishingPort.objects.get(id = kw['port_id'])
#     page = 'PortInfo'
#     if R.POST.get('submit', ''):
#         for k, v in R.POST.items():
#             list = k.split('_')
#             if list[0] == 'fishingport':
#                 field_name = list[1]
#                 if v == '':
#                     v = None
#                 setattr(port, field_name , v)
#                 port.save()

#             elif list[0] == 'fishingportphoto':
#                 field_name = list[1]
#                 field_id = list[2]
#                 row = FishingPortPhoto.objects.get(id= field_id)
#                 setattr(row, field_name , v)
#                 row.save()

#             elif list[0] == 'porttype':
#                 field_name = list[1]
#                 setattr(port, field_name , Option.objects.get(id=v))
#                 port.save()

#         if R.FILES.get('newphoto_file',''):
#             row = FishingPortPhoto(
#                                 name = R.POST.get('newphoto_name',''),
#                                 type = Option.objects.get(id = R.POST.get('newphoto_type',21)),
#                                 memo = R.POST.get('newphoto_memo',''),
#                                 fishingport = port,
#                                 )
#             row.save()
#             file = R.FILES.get('newphoto_file', None)
#             try: ext = file.name.split('.')[-1]
#             except: ext = 'jpg'
#             getattr(row, 'file').save('%s.%s'%(row.id, ext), file)
#             row.extname = ext
#             row.save()
#             thumb(row.file.name, "width=1024,height=768")

#     class photo_list(): pass
#     photos = []
#     for i in Option.objects.filter(swarm = 'photo_type').order_by('-id'):
#         temp = photo_list()
#         temp.name = i.value
#         temp.list = [j for j in FishingPortPhoto.objects.filter(fishingport=port, type__value=i.value)]
#         photos.append(temp)

#     photo_type = Option.objects.filter(swarm = 'photo_type').order_by('-id')

#     t = get_template(os.path.join('harbor', 'port.html'))
#     html = t.render(RequestContext(R,{
#                                     'writer':_cWriter(R),
#                                     'port' : port,
#                                     'classification' : port,
#                                     'photos' : photos,
#                                     'photo_type' : photo_type,
#                                     'city_list': _cMemu().city,
#                                     'observatory_list': _cMemu().obva,
#                                     'option' : _make_choose(),
#                                     'page' : page,
#                                     }))

#     return HttpResponse(html)

# @checkAuthority
# def observatory(R, **kw):
#     obs = Observatory.objects.get(id = kw['observatory_id'])
#     page = 'ObvaInfo'

#     if R.POST.get('submit', ''):
#         for k, v in R.POST.items():
#             list = k.split('__')
#             if list[0] == 'obs':
#                 field_name = list[1]
#                 setattr(obs, field_name , v)
#                 obs.save()

#         if R.FILES.get('obs__file',''):
#             file = R.FILES.get('obs__file', None)
#             try: ext = file.name.split('.')[-1]
#             except: ext = 'jpg'
#             getattr(obs, 'file').save('%s.%s'%(obs.id, ext), file)
#             obs.extname = ext
#             obs.save()

#         if R.POST.get('newmain__item',''):
#             row = MainProject(
#                               fishingport = port,
#                               year = R.POST.get('newmain__year',''),
#                               item = R.POST.get('newmain__item',''),
#                               num = R.POST.get('newboat__num',''),
#                               memo = R.POST.get('newmain__memo',''),
#                               )
#             row.save()
#     t = get_template(os.path.join('harbor', 'observatory.html'))
#     html = t.render(RequestContext(R,{
#                                     'writer':_cWriter(R),
#                                     'obs' : obs,
#                                     'classification' : obs,
#                                     'city_list': _cMemu().city,
#                                     'observatory_list': _cMemu().obva,
#                                     'page': page,
#                                     }))

#     return HttpResponse(html)

# @checkAuthority
# def city(R, **kw):
#     place = Place.objects.get(id = kw['place_id'])
#     # city = City.objects.get(place__id = place.id)
#     city = City.objects.filter(place__id = place.id).order_by('id')[0]
#     page = 'CityInfo'
#     if R.POST.get('submit', ''):
#         for k, v in R.POST.items():
#             list = k.split('__')
#             if list[0] == 'city':
#                 field_name = list[1]
#                 setattr(city, field_name , v)
#                 city.save()

#     t = get_template(os.path.join('harbor', 'city.html'))
#     html = t.render(RequestContext(R,{
#                                     'writer':_cWriter(R),
#                                     'city' : city,
#                                     'city_list': _cMemu().city,
#                                     'observatory_list': _cMemu().obva,
#                                     'classification': city.place,
#                                     'page': page,
#                                     }))

#     return HttpResponse(html)


# def _getModel(name):
#     if name == 'waves' :
#         return Waves
#     elif name == 'tide' :
#         return Tide
#     elif name == 'boat' :
#         return FishingPortBoat
#     elif name == 'mainproject' :
#         return MainProject
#     elif name == 'project' :
#         return Project
#     elif name == 'portfisheryoutput' :
#         return PortFisheryOutput
#     elif name == 'averagerainfall' :
#         return AverageRainfall
#     elif name == 'averagetemperature' :
#         return AverageTemperature
#     elif name == 'averagepressure' :
#         return AveragePressure
#     elif name == 'fisherytype' :
#         return FisheryType
#     elif name == 'fishtype' :
#         return FishType
#     elif name == 'fisheryoutput' :
#         return FisheryOutput
#     elif name == 'aquapubdnd' :
#         return AquaculturePublicWork
#     elif name == 'aquapubrec' :
#         return AquaculturePublic


# #def _checkDateType(row):
# #    for field in row._meta.fields :
# #        if field.__class__ == M.DateField :
# #            setattr(row, field.name, getattr(row,field.name).replace('/', '-'))
# #            #setattr(row, field.name, time.strptime(str(getattr(row,field.name)), '%Y-%m-%d'))
# #        else:
# #            pass

# @checkAuthority
# def edit(R, **kw):
#     model_name = _getModel(kw['edit_type'])
#     have_newdata = False
#     page = kw['edit_type']

#     if kw['edit_classification'] == 'port' :
#         classification = FishingPort.objects.get(id = kw['target_id'])
#         if 'year' in [i.name for i in model_name._meta.fields]:
#             data_list = model_name.objects.filter(fishingport = classification).order_by('year')
#         else :
#             data_list = model_name.objects.filter(fishingport = classification).order_by('id')
#         teaget = 'fishingport'
#     elif kw['edit_classification'] == 'city' :
#         classification = Place.objects.get(id = kw['target_id'])
#         data_list = model_name.objects.filter(place = classification).order_by('id')
#         teaget = 'place'
#     elif kw['edit_classification'] == 'observatory' :
#         classification = Observatory.objects.get(id = kw['target_id'])
#         data_list = model_name.objects.filter(observatory = classification).order_by('id')
#         teaget = 'observatory'

#     if R.POST.get('submit', ''):
#         for k, v in R.POST.items():
#             list = k.split('__')
#             if list[0] == kw['edit_type'] :
#                 field_name = list[1]
#                 field_id = list[2]
#                 row = model_name.objects.get(id= field_id)
#                 try :
#                     if v == '':
#                         v = None
#                     setattr(row, field_name , v)
#                     row.save()
#                 except:
#                     setattr(row, field_name , Option.objects.get(id = v))
#                     row.save()
#             elif list[0] == 'new' and v != '':
#                 have_newdata = True

#         if have_newdata:
#             mods = len(model_name._meta.fields)
#             input_dic = {}
#             input_dic[teaget] = classification
#             for column in xrange(1, mods):
#                 temp = model_name._meta.fields[column].name
#                 if R.POST.get('new__' + str(temp),'') == '':
#                     continue
#                 if model_name._meta.fields[column].__class__ == M.ForeignKey:
#                     input_dic[temp] = Option.objects.get(id = R.POST.get('new__' + str(temp),''))
#                 else:
#                     input_dic[temp] = R.POST.get('new__' + str(temp),'') or None


#             row = model_name(**input_dic)
# #            _checkDateType(row)
#             row.save()

#     t = get_template(os.path.join('harbor', kw['edit_type'] + '.html'))
#     html = t.render(RequestContext(R,{
#                                     'writer':_cWriter(R),
#                                     'classification' : classification,
#                                     'list' : data_list,
#                                     'option' : _make_choose(),
#                                     'city_list': _cMemu().city,
#                                     'observatory_list': _cMemu().obva,
#                                     'page': page,
#                                     }))

#     return HttpResponse(html)

# @checkAuthority
# def delRow(R, **kw):
#     if R.GET['model_name'] == 'fishingportphoto':
#         row = FishingPortPhoto.objects.get(id=kw['row_id'])
#     elif R.GET['model_name'] == 'waves':
#         row = Waves.objects.get(id=kw['row_id'])
#     elif R.GET['model_name'] == 'tide':
#         row = Tide.objects.get(id=kw['row_id'])
#     elif R.GET['model_name'] == 'boat':
#         row = FishingPortBoat.objects.get(id=kw['row_id'])
#     elif R.GET['model_name'] == 'mainproject':
#         row = MainProject.objects.get(id=kw['row_id'])
#     elif R.GET['model_name'] == 'project':
#         row = Project.objects.get(id=kw['row_id'])
#     elif R.GET['model_name'] == 'portfisheryoutput':
#         row = PortFisheryOutput.objects.get(id=kw['row_id'])
#     elif R.GET['model_name'] == 'fisherytype':
#         row = FisheryType.objects.get(id=kw['row_id'])
#     elif R.GET['model_name'] == 'fishtype':
#         row = FishType.objects.get(id=kw['row_id'])
#     elif R.GET['model_name'] == 'fisheryoutput':
#         row = FisheryOutput.objects.get(id=kw['row_id'])
#     elif R.GET['model_name'] == 'averagerainfall':
#         row = AverageRainfall.objects.get(id=kw['row_id'])
#     elif R.GET['model_name'] == 'averagepressure':
#         row = AveragePressure.objects.get(id=kw['row_id'])
#     elif R.GET['model_name'] == 'averagetemperature':
#         row = AverageTemperature.objects.get(id=kw['row_id'])
#     elif R.GET['model_name'] == 'aquapubrec':
#         row = AquaculturePublic.objects.get(id=kw['row_id'])
#     elif R.GET['model_name'] == 'aquapubdnd':
#         row = AquaculturePublicWork.objects.get(id=kw['row_id'])

#     row.delete()
#     return HttpResponse(json.write({'status': True, 'message': '刪除成功'}))

# @checkAuthority
# def addport(R, **kw):
#     if R.POST.get('new__port',''):
#         row = FishingPort(
#                         name = R.POST.get('new__port',''),
#                         place = Place.objects.get(id = R.POST.get('new__place','')),
#                         type = Option.objects.get(id = R.POST.get('new__type','')),
#                         observatory = Observatory.objects.get(id = R.POST.get('new__observatory','')),
#                         )
#         row.save()

#         if R.POST.get('new__code',''):
#             setattr(row, 'code' , R.POST.get('new__code',''))
#             row.save()
#         if R.POST.get('new__x_coord',''):
#             setattr(row, 'xcoord' , R.POST.get('new__x_coord',''))
#             row.save()
#         if R.POST.get('new__y_coord',''):
#             setattr(row, 'ycoord' , R.POST.get('new__y_coord',''))
#             row.save()


#     city_list = City.objects.all()
#     fishingport_list = FishingPort.objects.all()
#     observatory_list = Observatory.objects.all()
#     for i in city_list:
#         i.fishingport = []
#         for j in fishingport_list:
#             if i.place == j.place:
#                 i.fishingport.append(j)

#     t = get_template(os.path.join('harbor', 'addport.html'))
#     html = t.render(RequestContext(R,{
#                                     'writer':_cWriter(R),
#                                     'city_list' : city_list,
#                                     'observatory_list' : observatory_list,
#                                     'option' : _make_choose(),
#                                     }))

#     return HttpResponse(html)

# @checkAuthority
# def addobservatory(R, **kw):
#     if R.POST.get('new__observatory',''):
#         row = Observatory(
#                         name = R.POST.get('new__observatory',''),
#                         wind_memo = '',
#                         rainday_memo = '',
#                         file = None,
#                         )
#         row.save()

#     city_list = City.objects.all()
#     fishingport_list = FishingPort.objects.all()
#     observatory_list = Observatory.objects.all()
#     for i in city_list:
#         i.fishingport = []
#         for j in fishingport_list:
#             if i.place == j.place:
#                 i.fishingport.append(j)

#     t = get_template(os.path.join('harbor', 'addobservatory.html'))
#     html = t.render(RequestContext(R,{
#                                     'writer':_cWriter(R),
#                                     'city_list' : city_list,
#                                     'observatory_list' : observatory_list,
#                                     }))

#     return HttpResponse(html)


# @checkAuthority
# def addPortInstallation(R, **kw):
#     port = FishingPort.objects.get(id = kw['port_id'])
#     units = [[i.id, i.name] for i in Unit.objects.filter(uplevel__name='臺灣省漁會')]

#     if R.POST.get('submit', ''):
#         row = PortInstallationRecord(
#                 fishingport = port,
#                 date = R.POST.get('date',''),
#                 )
#         if R.POST.get('organization',None) != '':
#             row.organization = Unit.objects.get(id=R.POST.get('organization',None))
#         if R.POST.get('hour',None) != '' and R.POST.get('minute',None) != '':
#             row.time = R.POST.get('hour',None) + ':' + R.POST.get('minute',None)
#         if R.POST.get('arrival_port',None) != '':
#             row.arrival_port = R.POST.get('arrival_port',None)
#         if R.POST.get('leave_port',None) != '':
#             row.leave_port = R.POST.get('leave_port',None)
#         if R.POST.get('anchor',None) != '':
#             row.anchor = R.POST.get('anchor',None)
#         if R.POST.get('boat_supplies',None) != '':
#             row.boat_supplies = Option.objects.get(id=R.POST.get('boat_supplies',None))
#         if R.POST.get('boat_supplies_memo',None) != '':
#             row.boat_supplies_memo = R.POST.get('boat_supplies_memo',None)
#         if R.POST.get('port_environment',None) != '':
#             row.port_environment = Option.objects.get(id=R.POST.get('port_environment',None))
#         if R.POST.get('emergency',None) != '':
#             row.emergency = Option.objects.get(id=R.POST.get('emergency',None))
#         if R.POST.get('emergency_measures',None) != '':
#             row.emergency_measures = Option.objects.get(id=R.POST.get('emergency_measures',None))
#         if R.POST.get('memo',None) != '':
#             row.memo = R.POST.get('memo',None)
#         row.save()
#         url = '/harbor/portinstallation/record/' + kw['port_id'] + '/'
#         return HttpResponseRedirect(url)

#     tar_year = TODAY().year
#     tar_month = TODAY().month

#     t = get_template(os.path.join('harbor', 'installation.html'))
#     html = t.render(RequestContext(R,{
#                                     'writer':_cWriter(R),
#                                     'city_list': _cMemu().city,
#                                     'classification': port,
#                                     'units': units,
#                                     'option' : _make_choose(),
#                                     'page':'New', 'tar_year':tar_year, 'tar_month':tar_month,
#                                     }))

#     return HttpResponse(html)


# @checkAuthority
# def recordPortInstallation(R, **kw):
#     port = FishingPort.objects.get(id = kw['port_id'])
#     units = [[i.id, i.name] for i in Unit.objects.filter(uplevel__name='臺灣省漁會')]
#     years = [(y-1911, y-1911) for y in xrange(2006, TODAY().year+1)]
#     years.reverse()
#     month = [TODAY().month,[m for m in xrange(1,13)]]

#     records = PortInstallationRecord.objects.filter(fishingport=port).order_by('-date')

#     tar_year = TODAY().year
#     mark_year = tar_year - 1911
#     tar_month = TODAY().month
#     records = records.filter(date__year = tar_year)
#     records = records.filter(date__month = tar_month)

#     t = get_template(os.path.join('harbor', 'instrecord.html'))
#     html = t.render(RequestContext(R,{
#                                     'writer':_cWriter(R),
#                                     'city_list': _cMemu().city,
#                                     'units': units,
#                                     'classification': port,
#                                     'years': years,
#                                     'month': month,
#                                     'records': records,
#                                     'option' : _make_choose(),
#                                     'page':'Record',
#                                     'mark_year': mark_year,
#                                     'tar_year': tar_year,
#                                     'tar_month': tar_month,
#                                     }))

#     return HttpResponse(html)



# @checkAuthority
# def getInstallationRecord(R, **kw):
#     port = FishingPort.objects.get(id = kw['port_id'])
#     units = [[i.id, i.name] for i in Unit.objects.filter(uplevel__name='臺灣省漁會')]
#     years = [(y-1911, y-1911) for y in xrange(2006, TODAY().year+1)]
#     years.reverse()
#     month = [TODAY().month,[m for m in xrange(1,13)]]

#     records = PortInstallationRecord.objects.filter(fishingport=port).order_by('-date')

#     tar_year = int(kw['year'])
#     mark_year = tar_year - 1911
#     tar_month = int(kw['month'])
#     records = records.filter(date__year = tar_year)
#     records = records.filter(date__month = tar_month)

#     t = get_template(os.path.join('harbor', 'instrecord.html'))
#     html = t.render(RequestContext(R,{
#                                     'writer':_cWriter(R),
#                                     'city_list': _cMemu().city,
#                                     'classification': port,
#                                     'units': units,
#                                     'years': years,
#                                     'month': month,
#                                     'records': records,
#                                     'option' : _make_choose(),
#                                     'page':'Record',
#                                     'mark_year': mark_year,
#                                     'tar_year': tar_year,
#                                     'tar_month': tar_month,
#                                     }))

#     return HttpResponse(html)

# @checkAuthority
# def vIndex(R, **kw):
#     #TODO:資訊入口頁面
#     fishingport_list = FishingPort.objects.all()
#     city_list = City.objects.all()
#     for i in city_list:
#         i.fishingport = []
#         for j in fishingport_list:
#             if i.place == j.place:
#                 i.fishingport.append(j)
#     t = get_template(os.path.join('harbor', 'taiwan.html'))
#     html = t.render(RequestContext(R,{'city_list':city_list, 'page':'City'}))
#     return HttpResponse(html)

# @checkAuthority
# def vTypePort(R, **kw):
#     ports = FishingPort.objects.filter(type=kw['port_type']).order_by('id')
#     if kw['port_type'] == '1':
#         page = 'First'
#     elif kw['port_type'] == '2':
#         page = 'Second'
#     elif kw['port_type'] == '3':
#         page = 'Third'
#     elif kw['port_type'] == '4':
#         page = 'Fourth'

#     place_list = list(City.objects.all())
#     for city in place_list:
#         port_list = list(ports.filter(place=city.place))
#         city.port_list = []
#         if port_list:
#             temp = []
#             for i in xrange(4-len(port_list)%4):
#                 port_list.append('temp')
#             for i in xrange(len(port_list)/4):
#                 city.port_list.append(port_list[i*4:(i+1)*4])

#     t = get_template(os.path.join('harbor', 'typeport.html'))
#     html = t.render(RequestContext(R,{'place_list':place_list, 'page': page}))
#     return HttpResponse(html)

# @checkAuthority
# def rPortInfo(R, **kw):
#     port = FishingPort.objects.get(id=kw['port_id'])
#     photos = FishingPortPhoto.objects.filter(fishingport=kw['port_id'])
#     page = 'PortInfo'
#     try:
#         airphoto = list(photos.filter(type=31).order_by('-id'))[0]
#     except:
#         airphoto = photos.filter(type=31)
#     try:
#         location = list(photos.filter(type=21).order_by('-id'))[0]
#     except:
#         location = photos.filter(type=21)
#     try:
#         area = list(photos.filter(type=22).order_by('-id'))[0]
#     except:
#         area = photos.filter(type=22)

#     t = get_template(os.path.join('harbor', 'vportinfo.html'))
#     html = t.render(RequestContext(R,{'port':port, 'page': page,
#                                         'airphoto': airphoto,
#                                         'location': location,
#                                         'area': area,}))
#     return HttpResponse(html)

# @checkAuthority
# def rPortClimate(R, **kw):
#     port = FishingPort.objects.get(id=kw['port_id'])
#     wave = Waves.objects.filter(fishingport=port)
#     tide = Tide.objects.filter(fishingport=port)
#     try:obva = port.observatory
#     except:obva = False
#     if obva :
#         avgrain = port.observatory.averagerainfall_set.all()
#         avgtemp = port.observatory.averagetemperature_set.all()
#         avgpres = port.observatory.averagepressure_set.all()
#     else:
#         obva = False
#         avgrain = False
#         avgtemp = False
#         avgpres = False
#     page = 'PortClimate'

#     if wave:
#         wave_type = []
#         wave_list = []
#         for i in wave:
#             if i.type not in wave_type :
#                 wave_type.append(i.type)
#                 wave_list.append([i.type,2,[{'angle':i.angle, 'high':i.high, 'cycle':i.cycle}]])
#             elif i.type in wave_type :
#                 wave_list[wave_type.index(i.type)][2].append({'angle':i.angle, 'high':i.high, 'cycle':i.cycle})
#                 wave_list[wave_type.index(i.type)][1] += 1
#         waves_list = []
#         for wave in wave_list:
#             if wave_list.index(wave)%2 == 0:
#                 waves_list.append([wave])
#             else:
#                 waves_list[-1].append(wave)
#     else:
#         waves_list = ''
#     if avgpres:
#         avgpres_list = []
#         for i in avgpres:
#             avgpres_list.append(i)
#     else:
#         avgpres_list = ''
#     if avgtemp:
#         avgtemp_list = []
#         for i in avgtemp:
#             avgtemp_list.append(i)
#     else:
#         avgtemp_list = ''
#     if avgrain:
#         avgrain_list = []
#         for i in avgrain:
#             avgrain_list.append(i)
#     else:
#         avgrain_list = ''

#     t = get_template(os.path.join('harbor', 'vportclimate.html'))
#     html = t.render(RequestContext(R,{'port':port,'wave' : wave, 'tide' : tide,
#                                         'waves_list' : waves_list, 'avgrain':avgrain,'avgtemp':avgtemp,
#                                         'avgpres':avgpres, 'avgrain_list':avgrain_list,
#                                         'avgtemp_list':avgtemp_list, 'avgpres_list':avgpres_list,
#                                         'obva':obva,
#                                         'page': page,}))
#     return HttpResponse(html)

# @checkAuthority
# def rPortFishery(R, **kw):
#     port = FishingPort.objects.get(id=kw['port_id'])
#     fishery_list = PortFisheryOutput.objects.filter(fishingport=port).order_by('-year')
#     page = 'PortFishery'

#     t = get_template(os.path.join('harbor', 'vportfishery.html'))
#     html = t.render(RequestContext(R,{'port':port, 'fishery_list':fishery_list, 'page': page,}))
#     return HttpResponse(html)

# @checkAuthority
# def rPortBoat(R, **kw):
#     port = FishingPort.objects.get(id=kw['port_id'])
#     boat = FishingPortBoat.objects.filter(fishingport=port).order_by('boat_type')
#     page = 'PortBoat'

#     if boat :
#         boat_type = []
#         for i in boat:
#             if i.boat_type.value not in boat_type:
#                 boat_type.append(i.boat_type.value)
#         years = []
#         for y in boat:
#             if y.year not in years:
#                 years.append(y.year)
#         years.sort()
#         years.reverse()
#         boat_list = []
#         for y in years:
#             temp = []
#             temp.append(y)
#             for i in xrange(len(boat_type)):
#                 temp.append(0)
#             boat_list.append(temp[:])
#         for b in boat:
#             for y in boat_list:
#                 if b.year == y[0]:
#                     y[boat_type.index(b.boat_type.value)+1] = b.num
#     else:
#         boat_type = ''
#         boat_list = ''


#     t = get_template(os.path.join('harbor', 'vportboat.html'))
#     html = t.render(RequestContext(R,{'port':port, 'boat':boat,
#                                         'boat_type':boat_type, 'boat_list':boat_list, 'page': page,}))
#     return HttpResponse(html)

# @checkAuthority
# def rPortDevelopment(R, **kw):
#     port = FishingPort.objects.get(id=kw['port_id'])
#     mainproject = MainProject.objects.filter(fishingport=port)
#     project = Project.objects.filter(fishingport=port).order_by('-year')
#     page = 'PortDevelopment'

#     if mainproject:
#         mainproject_type = []
#         mainproject_list = []
#         for i in mainproject:
#             if i.year not in mainproject_type :
#                 mainproject_type.append(i.year)
#                 mainproject_list.append([i.year,2,[i]])
#             elif i.year in mainproject_type :
#                 mainproject_list[mainproject_type.index(i.year)][2].append(i)
#                 mainproject_list[mainproject_type.index(i.year)][1] += 1
#         mainproject_list.reverse()
#     else:
#         mainproject_list = ''

#     if project:
#         project_type = []
#         project_list = []
#         for i in project:
#             if i.year not in project_type :
#                 project_type.append(i.year)
#                 project_list.append([i.year,2,[i]])
#             elif i.year in project_type :
#                 project_list[project_type.index(i.year)][2].append(i)
#                 project_list[project_type.index(i.year)][1] += 1
#     else:
#         project_list = ''

#     fa_projects = [p.project for p in FA_project_port.objects.filter(port=port).order_by('-project__year')]

#     t = get_template(os.path.join('harbor', 'vportdevelopment.html'))
#     html = t.render(RequestContext(R,{'port':port, 'project':project, 'project_list':project_list,
#                                       'mainproject':mainproject, 'mainproject_list':mainproject_list,
#                                       'page': page, 'fa_projects': fa_projects}))
#     return HttpResponse(html)

# @checkAuthority
# def rPortPhotos(R, **kw):
#     port = FishingPort.objects.get(id=kw['port_id'])
#     photos = FishingPortPhoto.objects.filter(fishingport=port).order_by('type')
#     page = 'PortPhotos'

#     type_list = []
#     for photo in photos:
#         if photo.type not in type_list:
#             type_list.append(photo.type)

#     if type_list:
#         phototype = type_list[0]
#     else:
#         phototype = False

#     photo_list = photos.filter(type=phototype)
#     if photo_list:
#         preinstall = photo_list[0]
#         photo_num = len(photo_list)
#         total = len(list(photos))
#     else:
#         preinstall = False
#         photo_num = False
#         total = False

#     t = get_template(os.path.join('harbor', 'vportphotos.html'))
#     html = t.render(RequestContext(R,{'port':port, 'type_list':type_list, 'photo_list': photo_list,
#                                         'phototype': phototype, 'preinstall': preinstall, 'photo_num': photo_num,
#                                         'total': total, 'page': page,}))
#     return HttpResponse(html)

# @checkAuthority
# def rPortTypePhotos(R, **kw):
#     port = FishingPort.objects.get(id=kw['port_id'])
#     phototype = Option.objects.get(id=kw['type'])
#     photos = FishingPortPhoto.objects.filter(fishingport=port).order_by('type')
#     targetphotos = photos.filter(type=phototype)
#     page = 'PortPhotos'

#     type_list = []
#     for photo in photos:
#         if photo.type not in type_list:
#             type_list.append(photo.type)

#     standard = list(targetphotos)[0]

#     photo_num = len(targetphotos)
#     total = len(list(photos))

#     t = get_template(os.path.join('harbor', 'vporttypephotos.html'))
#     html = t.render(RequestContext(R,{'port':port, 'phototype': phototype, 'targetphotos': targetphotos,
#                                         'type_list':type_list, 'standard': standard, 'photo_num': photo_num,
#                                         'total': total, 'page': page,}))
#     return HttpResponse(html)


# @checkAuthority
# def makeMiddlePhoto(R, **kw):
#     photos = FishingPortPhoto.objects.all()[0:10]
#     for i in photos:
#         thumb(i.file.name, "width=1024,height=768")

#     return HttpResponseRedirect('/harbor/')


# @checkAuthority
# def rCityInfo(R, **kw):
#     place = Place.objects.get(id = kw['place_id'])
#     city = City.objects.get(place__id = place.id)
#     page = 'CityInfo'
#     airphoto = False
#     for port in city.rPortinList():
#         try:
#             airphoto = list(port.fishingportphoto_set.filter(type__swarm='photo_type', type__value='空照圖'))[-1]
#             break
#         except: continue

#     t = get_template(os.path.join('harbor', 'vcityinfo.html'))
#     html = t.render(RequestContext(R,{'city':city, 'place':place, 'page': page, 'airphoto': airphoto}))
#     return HttpResponse(html)

# @checkAuthority
# def rCityFisheryType(R, **kw):
#     place = Place.objects.get(id = kw['place_id'])
#     city = City.objects.get(place__id = place.id)
#     page = 'FisheryType'
#     fishery_list = FisheryType.objects.filter(place=place)

#     t = get_template(os.path.join('harbor', 'vcityfishery.html'))
#     html = t.render(RequestContext(R,{'city':city, 'place':place, 'page': page, 'fishery_list': fishery_list,}))
#     return HttpResponse(html)

# @checkAuthority
# def rCityFishType(R, **kw):
#     place = Place.objects.get(id = kw['place_id'])
#     city = City.objects.get(place__id = place.id)
#     page = 'FishType'
#     fish_list = FishType.objects.filter(place=place)

#     t = get_template(os.path.join('harbor', 'vcityfish.html'))
#     html = t.render(RequestContext(R,{'city':city, 'place':place, 'page': page, 'fish_list': fish_list,}))
#     return HttpResponse(html)

# @checkAuthority
# def rCityFisheryOutput(R, **kw):
#     place = Place.objects.get(id = kw['place_id'])
#     city = City.objects.get(place__id = place.id)
#     page = 'FisheryOutput'
#     fisheryop_list = FisheryOutput.objects.filter(place=place).order_by('-year')

#     t = get_template(os.path.join('harbor', 'vcityfishop.html'))
#     html = t.render(RequestContext(R,{'city':city, 'place':place, 'page': page, 'fisheryop_list': fisheryop_list,}))
#     return HttpResponse(html)

# @checkAuthority
# def rCityAquaculturePublicWorks(R, **kw):
#     place = Place.objects.get(id = kw['place_id'])
#     city = City.objects.get(place__id = place.id)
#     page = 'AquaculturePublicWorks'
#     all_works = AquaculturePublicWork.objects.filter(place=place)
#     all_Pub = AquaculturePublic.objects.filter(place=place).order_by('-year')

# #    works = []
# #    works_list = []
# #    for work in all_works:
# #        if work.project_name not in works:
# #            works.append(work.project_name)
# #            works_list.append([2,work,[]])
# #        else:
# #            works_list[works.index(work.project_name)][2].append(work)
# #            works_list[works.index(work.project_name)][0] += 2
#     years = []
#     work_list = []
#     for work in all_works:
#         if work.year not in years:
#             years.append(work.year)
#             work_list.append([work.year, 2, [work]])
#         else:
#             work_list[years.index(work.year)][2].append(work)
#             work_list[years.index(work.year)][1] += 1

#     years = []
#     pub_list = []
#     for pub in all_Pub:
#         if pub.year not in years:
#             years.append(pub.year)
#             pub_list.append([pub.year, 2, [pub]])
#         else:
#             pub_list[years.index(pub.year)][2].append(pub)
#             pub_list[years.index(pub.year)][1] += 1

#     t = get_template(os.path.join('harbor', 'vcityaquapub.html'))
#     html = t.render(RequestContext(R,{'city':city, 'place':place, 'page': page,
#                                         'work_list': work_list,
#                                         'pub_list': pub_list,}))
#     return HttpResponse(html)

# @checkAuthority
# def rCityPorts(R, **kw):
#     place = Place.objects.get(id = kw['place_id'])
#     city = City.objects.get(place__id = place.id)
#     page = 'CityPorts'
#     ports = FishingPort.objects.filter(place=place)
#     port_list = [['第一類漁港',[[]]],['第二類漁港',[[]]],['第三類漁港',[[]]],['第四類漁港',[[]]]]
# #    port_list = [[i.value,[[]]] for i in ports]
#     type_list = []
#     for port in ports:
#         if port.type.id not in type_list:
#             type_list.append(port.type.id)
#         if len(port_list[(int(port.type.id) -1)][1][-1]) < 4 :
#             port_list[(int(port.type.id) -1)][1][-1].append(port)
#         elif len(port_list[(int(port.type.id) -1)][1][-1]) == 4 :
#             port_list[(int(port.type.id) -1)][1].append([port])
#     ports_list = []
#     for type in type_list:
#         ports_list.append(port_list[type - 1])

#     t = get_template(os.path.join('harbor', 'vcityports.html'))
#     html = t.render(RequestContext(R,{'city':city, 'place':place, 'page': page, 'port_list': ports_list,}))
#     return HttpResponse(html)

# @checkAuthority
# def vInstallation(R, **kw):
#     city_list = City.objects.all().order_by('id')
#     prot_list = FishingPort.objects.filter(place = list(city_list)[0].place)
#     select_city = ''
#     select_port = ''
#     select_year = ''
#     from_month = TODAY().month
#     to_month = TODAY().month
#     record_list = ''
#     search = False
#     years = [(y-1911, y-1911) for y in xrange(2006, TODAY().year+1)]
#     years.reverse()
#     month = [TODAY().month,[m for m in xrange(1,13)]]
#     end_month = [m for m in xrange(TODAY().month,13)]
#     DATA = readDATA(R)
#     if DATA.get('submit', ''):
#         prot_list = FishingPort.objects.filter(place__id = int(DATA.get('place', '')))
#         port = FishingPort.objects.get(id=DATA.get('port', ''))
#         select_city = int(DATA.get('place', ''))
#         select_port = int(DATA.get('port', ''))
#         select_year = int(DATA.get('year', ''))
#         from_month = int(DATA.get('month_from', ''))
#         to_month = int(DATA.get('month_to', ''))
#         search = True
#         records = PortInstallationRecord.objects.filter(fishingport = port)
#         records = records.filter(date__year = int(DATA.get('year', ''))+1911)
#         record_list = []
#         for m in xrange(int(DATA.get('month_from', '')),int(DATA.get('month_to', ''))+1):
#             if records.filter(date__month= m):
#                 record_list.append([m,list(records.filter(date__month= m))])

#         end_month = [m for m in xrange(int(DATA.get('month_from', '')),13)]
#     t = get_template(os.path.join('harbor', 'vinstrecord.html'))
#     html = t.render(RequestContext(R,{'city_list':city_list, 'select_city':select_city,
#                                         'prot_list':prot_list, 'port':select_port,
#                                         'years':years, 'select_year':select_year,
#                                         'month':month, 'end_month':end_month,
#                                         'from_month':from_month, 'to_month':to_month,
#                                         'record_list':record_list,
#                                         'search':search
#                                         }))
#     return HttpResponse(html)


# @checkAuthority
# def UploadCityFile(R, **kw):
#     user, DATA = R.user, R.POST
#     place = Place.objects.get(id = kw['place_id'])
#     city = City.objects.get(place__id = place.id)
#     page = 'CityFiles'
#     if user.user_profile.group.name in ['主辦工程師', '上層管理者', '管考填寫員']:
#         can_upload = True
#     else:
#         can_upload = False

#     if user.username[1] == '_':
#         can_upload = False

#     files = CityFiles.objects.filter(place=place).order_by('upload_user', '-upload_date', '-id')

#     if R.POST.get('submit', ''):
#         file = R.FILES.get('file', None)
#         location = DATA.get('location','')
#         filename = DATA.get('name','')
#         memo = DATA.get('memo','')
#         try:
#             lng = decimal.Decimal(str(DATA.get('lng','')))
#             lat = decimal.Decimal(str(DATA.get('lat','')))

#         except:
#             lng = None
#             lat = None
#         if filename == '':
#             filename = str(file.name)

#         row = CityFiles(
#                     name = filename,
#                     memo = memo,
#                     place = place,
#                     location = location,
#                     upload_user = user,
#                     upload_date = TODAY(),
#                     file = file,
#                     lat = lat,
#                     lng = lng,
#                     )
#         row.save()

#         try:
#             ext = file.name.split('.')[-1]
#         except:
#             ext = 'zip'
#         if ext in ['jpg', 'jpeg', 'tiff', 'tif', 'png', 'gif']:
#             thumb(row.file.name, "width=1024,height=768")

#         getattr(row, 'file').save('%s.%s'%(row.id, ext), file)
#         row.save()

#     t = get_template(os.path.join('harbor', 'vcityfile.html'))
#     html = t.render(RequestContext(R,{'city':city, 'place':place, 'page': page, 'files': files, 'can_upload': can_upload}))
#     return HttpResponse(html)


# @checkAuthority
# def readJson(R, **kw):
#     DATA = readDATA(R)
#     if 'rPlacePort' == DATA.get('submit', None):
#         ports = FishingPort.objects.filter(place=DATA.get('place', None))
#         type_list = [i for i in Option.objects.filter(swarm='fishingport_type').order_by('id')]
#         port_list = []
#         for i in type_list:
#             i.ports = list(ports.filter(type=i))
#             port_list.append([i.value] + i.ports)

#         portblock = '<h2>'
#         for type in port_list:
#             if len(type) > 1:
#                 portblock += u'<span>' + type[0] + u'</span><table>'
#                 for port in type[1:]:
#                     portblock += u'<tr><td align="left">　　<img width="20" heigth="20" src="/media/harbor/image/enter.gif"><a href="/harbor/portinfo/' + str(port.id) + '">' + port.name + '</a></td></tr>'
#                 portblock += u'</table>'
#         portblock += '</h2>'
#         return HttpResponse(json.write({'status': True, 'portblock': portblock}))

#     elif 'getPhoto' == DATA.get('submit', None):
#         photo = FishingPortPhoto.objects.get(id=DATA.get('id', None))

#         photoblock = '<tr><td><a href="/' + photo.rUrl() + '" target="_blank">'
#         photoblock += '<img width="600" src="/' + photo.rUrl() + '" title="' + photo.name
#         if photo.name and photo.memo:
#             photoblock += ':'
#         photoblock += photo.memo + '">'
#         photoblock += '</a></tr></td>'
#         if photo.memo :
#             photoblock += '<tr><td>'
#             photoblock += photo.memo
#             photoblock += '</tr></td>'
#         return HttpResponse(json.write({'status': True, 'photoblock': photoblock, }))

#     elif 'getInfoMemo' == DATA.get('submit', None):

#         contents = '<div class="flora" style="overflow: auto">'
#         if DATA.get('type', None) == 'avgtemp':
#             data = AverageTemperature.objects.get(id=DATA.get('id', None))
#             width = 450
#             height = 230
#             contents += '<h2>' + data.memo + '</h2>'
#         elif DATA.get('type', None) == 'avgrain':
#             data = AverageRainfall.objects.get(id=DATA.get('id', None))
#             width = 450
#             height = 230
#             contents += '<h2>' + data.rain_memo + '</h2>'
#         elif DATA.get('type', None) == 'avgrainday':
#             data = AverageRainfall.objects.get(id=DATA.get('id', None))
#             width = 450
#             height = 230
#             contents += '<h2>' + data.day_memo + '</h2>'
#         elif DATA.get('type', None) == 'avgpres':
#             data = AveragePressure.objects.get(id=DATA.get('id', None))
#             width = 450
#             height = 230
#             contents += '<h2>' + data.memo + '</h2>'
#         elif DATA.get('type', None) == 'project':
#             if DATA.get('is_infa', None) == '':
#                 data = Project.objects.get(id=DATA.get('id', None))
#                 width = 700
#                 height = 600
#                 contents += '<table><tr><td>'
#                 contents += '<h2><table align="left" style="border-collapse: collapse" border="1" cellpadding="2" cellspacing="2">'
#                 contents += '<tr><td width="150" bgcolor="#66CCFF">工程名稱</td><td colspan="3">' + data.name + '</td></tr>'
#                 contents += '<tr><td bgcolor="#66CCFF">年度</td><td width="160">' + str(data.year) + '</td><td width="150" bgcolor="#66CCFF">計畫名稱</td><td width="160">' + str(data.plan) + '</td></tr>'
#                 contents += '<tr><td bgcolor="#66CCFF">經費來源</td><td width="160">' + str(data.funds_source) + '</td><td width="150" bgcolor="#66CCFF">計畫經費</td><td width="160" align="right">' + str(data.plan_fund) + '</td></tr>'
#                 contents += '<tr><td bgcolor="#66CCFF">發包日期</td><td width="160">'+ str(data.contract_date) + '</td><td width="150" bgcolor="#66CCFF">經費</td><td width="160" align="right">' + str(data.funds) + '</td></tr>'
#                 contents += '<tr><td rowspan="2" bgcolor="#66CCFF">工作項目</td><td bgcolor="#66CCFF">預定</td><td colspan="2">' + str(data.schedule_item) + '</td></tr>'
#                 contents += '<tr><td bgcolor="#66CCFF">實際</td><td colspan="2">' + str(data.reality_item) + '</td></tr>'
#                 contents += '<tr><td rowspan="2" bgcolor="#66CCFF">完工日期</td><td bgcolor="#66CCFF">預定</td><td colspan="2">' + str(data.design_finish_date) + '</td></tr>'
#                 contents += '<tr><td bgcolor="#66CCFF">實際</td><td colspan="2">' + str(data.act_finish_date) + '</td></tr>'
#                 contents += '<tr><td bgcolor="#66CCFF">發包工作費</td><td width="160" align="right">' + str(data.contract_fund) + '</td><td width="150" bgcolor="#66CCFF">管理經費</td><td width="160" align="right">' + str(data.manage_fund) + '</td></tr>'
#                 contents += '<tr><td bgcolor="#66CCFF">供給材料經費</td><td width="160" align="right">' + str(data.supply_material_fund) + '</td><td width="150" bgcolor="#66CCFF">其它經費</td><td width="160" align="right">' + str(data.other_fund) + '</td></tr>'
#                 contents += '<tr><td bgcolor="#66CCFF">實列預算經費</td><td width="160" align="right">' + str(data.reality_budget_fund) + '</td><td width="150" bgcolor="#66CCFF">結算經費</td><td width="160" align="right">' + str(data.settlement_fund) + '</td></tr>'
#                 contents += '<tr><td bgcolor="#66CCFF">第一次追加日期</td><td width="160">' + str(data.first_change_design_date) + '</td><td width="150" bgcolor="#66CCFF">一次追加變更設計費</td><td width="160" align="right">' + str(data.first_change_design) + '</td></tr>'
#                 contents += '<tr><td bgcolor="#66CCFF">第二次追加日期</td><td width="160">' + str(data.second_change_design_date) + '</td><td width="150" bgcolor="#66CCFF">二次追加變更設計費</td><td width="160" align="right">' + str(data.second_change_design) + '</td></tr>'
#                 contents += '<tr><td bgcolor="#66CCFF" colspan="4">備註</td></tr>'
#                 contents += '<tr><td colspan="4">' + str(data.note) + '</td></tr></table></h2>'
#                 contents += '</td></tr></table>'
#             else:
#                 data = FA_project.objects.get(id=DATA.get('id', None))
#                 width = 700
#                 height = 600
#                 contents += '<table><tr><td>'
#                 contents += '<h2><table align="left" style="border-collapse: collapse" border="1" cellpadding="2" cellspacing="2">'
#                 contents += '<tr><td bgcolor="#66CCFF" width="120">標案編號</td><td width="250">'+ str(data.bid_no or '') +'</td><td bgcolor="#66CCFF" width="120">年度</td><td width="250">'+ str(data.year) +'</td></tr>'
#                 contents += '<tr><td bgcolor="#66CCFF">計畫編號</td><td>'+ str(data.work_no or '') +'</td><td bgcolor="#66CCFF">縣市</td><td>'+ str(data.place.name) +'</td></tr>'
#                 contents += '<tr><td bgcolor="#66CCFF">計畫名稱</td><td colspan="3">'+ str(data.plan.name) +'</td></tr>'
#                 contents += '<tr><td bgcolor="#66CCFF">工作名稱</td><td colspan="3">'+ str(data.name) +'</td></tr>'
#                 contents += '<tr><td bgcolor="#66CCFF">設計包決標金額</td><td align="right">'+ str(data.design_bid) +'</td><td bgcolor="#66CCFF">預計完工日期</td><td>'+ str(data.term_date) +'</td></tr>'
#                 contents += '<tr><td bgcolor="#66CCFF">工程包決標金額</td><td align="right">'+ str(data.construction_bid) +'</td><td bgcolor="#66CCFF">實際完工日期</td><td>'+ str(data.rterm_date) +'</td></tr>'
#                 contents += '<tr><td bgcolor="#66CCFF">空污費</td><td align="right">'+ str(data.pollution) +'</td><td bgcolor="#66CCFF">X座標</td><td align="right">'+ str(data.x_coord) +'</td></tr>'
#                 contents += '<tr><td bgcolor="#66CCFF">施工管理費</td><td align="right">'+ str(data.manage) +'</td><td bgcolor="#66CCFF">Y座標</td><td align="right">'+ str(data.y_coord) +'</td></tr>'
#                 contents += '<tr><td bgcolor="#66CCFF">其他費用</td><td align="right">'+ str(data.other_defray) +'</td><td bgcolor="#66CCFF">預算別</td><td>'+ str(data.plan.budget_type.value) +'</td></tr>'
#                 contents += '<tr><td colspan="4" bgcolor="#66CCFF">工程備註</td></tr>'
#                 contents += '<tr><td colspan="4">'+ str(data.project_memo) +'</td></tr>'
#                 contents += '</table></h2></td></tr></table>'

#         contents += '</div>'
#         return HttpResponse(json.write({'status': True, 'contents': contents, 'width': width, 'height': height,}))

#     elif 'getPort' == DATA.get('submit', None):
#         ports = FishingPort.objects.filter(place=DATA.get('place', None)).order_by('id')
#         contents = ''
#         contents += '<select id="Port" style="font-size: 20px;">'
#         for port in ports:
#             contents += '<option value="' + str(port.id) + '">　' + str(port.name) + '　</option>'
#         contents += '</select>'

#         return HttpResponse(json.write({'status': True, 'contents': contents}))

#     elif 'updateInfo' == DATA.get('submit', None):
#         row = PortInstallationRecord.objects.get(id=int(DATA.get('id', None)))
#         field_name = DATA.get('field', None)
#         return_name = ''
#         if field_name == 'boat_supplies' or field_name == 'port_environment' or field_name == 'emergency' or field_name == 'emergency_measures':
#             if DATA.get('new_inf', None) == '':
#                 field_value = None
#                 return_name = '----'
#             else:
#                 field_value = Option.objects.get(id = DATA.get('new_inf', None))
#                 return_name = field_value.value
#         elif field_name == 'organization':
#             if DATA.get('new_inf', None) == '':
#                 field_value = None
#                 return_name = '----'
#             else:
#                 field_value = Unit.objects.get(id = DATA.get('new_inf', None))
#                 return_name = field_value.name
#         else:
#             if DATA.get('new_inf', None) == '':
#                 field_value = None
#                 return_name = '----'
#             else:
#                 field_value = DATA.get('new_inf', None)
#                 return_name = field_value
#         setattr(row, field_name , field_value)
#         row.save()

#         return HttpResponse(json.write({'status': True, 'return_name': return_name}))

#     elif 'editPortFile' == DATA.get('submit', None):
#         row = TempFile.objects.get(id=DATA.get('field_id'))
#         if R.user != row.upload_user:
#             return HttpResponse(json.write({'status': False, 'message': '您無此權限!!'}))
#         setattr(row, DATA.get('field_name'), DATA.get('value', ''))
#         row.save()
#         value = DATA.get('value', '')
#         return HttpResponse(json.write({'status': True, 'value': value}))

#     elif 'deletePortFile' == DATA.get('submit', None):
#         row = TempFile.objects.get(id=DATA.get('row_id'))
#         if R.user != row.upload_user:
#             return HttpResponse(json.write({'status': False, 'message': '您無此權限!!'}))
#         row.delete()
#         return HttpResponse(json.write({'status': True}))

#     elif 'editShareFile' == DATA.get('submit', None):
#         row = DataShare.objects.get(id=DATA.get('field_id'))
#         if R.user != row.upload_user:
#             return HttpResponse(json.write({'status': False, 'message': '您無此權限!!'}))
#         setattr(row, DATA.get('field_name'), DATA.get('value', ''))
#         row.save()
#         value = DATA.get('value', '')
#         return HttpResponse(json.write({'status': True, 'value': value}))

#     elif 'deleteShareFile' == DATA.get('submit', None):
#         row = DataShare.objects.get(id=DATA.get('row_id'))
#         if R.user != row.upload_user:
#             return HttpResponse(json.write({'status': False, 'message': '您無此權限!!'}))
#         row.delete()
#         return HttpResponse(json.write({'status': True}))

# @checkAuthority
# def TransformToPort(R, **kw):
#     #給外部連結過來轉換網址用的
#     try:
#         port = FishingPort.objects.get(code=kw['port_code'])
#         return HttpResponseRedirect('/harbor/portinfo/'+str(port.id)+'/')
#     except:
#         return HttpResponseRedirect('/harbor/')


# @checkAuthority
# def rPortCam(R, **kw):
#     port = FishingPort.objects.get(id=kw['port_id'])
#     port_id = 9
#     page = 'PortCam'
#     t = get_template(os.path.join('harbor', 'vportcam.html'))
#     html = t.render(RequestContext(R,{'port':port, 'page': page, 'port_id': port_id}))
#     return HttpResponse(html)

# @checkAuthority
# def rCam(R, **kw):
#     port = FishingPort.objects.get(id=kw['port_id'])
#     cam = FishingPort.objects.get(id=kw['port_id'])
#     port_id = 9
#     page = 'PortCam'
#     t = get_template(os.path.join('harbor', 'vportcam.html'))
#     html = t.render(RequestContext(R,{'port':port, 'page': page, 'port_id': port_id}))
#     return HttpResponse(html)

# @checkAuthority
# def addcam(R, **kw):
#     TAIWAN = Place.objects.get(name=u'臺灣地區')
#     places = Place.objects.filter(uplevel=TAIWAN).order_by('id')
#     city_list = City.objects.all()
#     fishingport_list = FishingPort.objects.all()
#     observatory_list = Observatory.objects.all()
#     for i in city_list:
#         i.fishingport = []
#         for j in fishingport_list:
#             if i.place == j.place:
#                 i.fishingport.append(j)
#     t = get_template(os.path.join('harbor', 'addcam.html'))
#     html = t.render(RequestContext(R,{  'places': places,
#                                 'writer':_cWriter(R),
#                                 'city_list' : city_list,
#                                 'observatory_list' : observatory_list,
#                                 }))
#     return HttpResponse(html)


# @checkAuthority
# def show_password(R, **kw):
#     t = get_template(os.path.join('harbor', 'show_password.html'))
#     html = t.render(RequestContext(R,{
#                                 'writer': _cWriter(R),
#                                 }))
#     return HttpResponse(html)


# @checkAuthority
# def editcam(R, **kw):
#     TAIWAN = Place.objects.get(name=u'臺灣地區')
#     places = Place.objects.filter(uplevel=TAIWAN).order_by('id')
#     city_list = City.objects.all()
#     fishingport_list = FishingPort.objects.all()
#     observatory_list = Observatory.objects.all()
#     for i in city_list:
#         i.fishingport = []
#         for j in fishingport_list:
#             if i.place == j.place:
#                 i.fishingport.append(j)

#     t = get_template(os.path.join('harbor', 'cam.html'))
#     html = t.render(RequestContext(R,{  'places': places,
#                                 'writer':_cWriter(R),
#                                 'city_list' : city_list,
#                                 'observatory_list' : observatory_list,
#                                 }))
#     return HttpResponse(html)


# def UploadCityFileWithJSFormExample(R, **kw):
#     return HttpResponse(u"""<html>
# <head>
#     <meta http-equiv="content-type" content="text/html; charset=utf-8" />
#     <script type="text/javascript" src="/media/jquery.ui-1.5.1/jquery-1.2.6.js"></script>
# </head>
# <body>
#     <!-- 以下 這兩行可以放在任何頁面，但記得該頁面要先引用 jquery lib -->
#     <script type="text/javascript" src="/media/harbor/js/upload_city_file.js"></script>
#     <form id="whatever_name_is_OK" class="upload_city_file"></form>
#     <!-- 以上 這兩行可以放在任何頁面，但記得該頁面要先引用 jquery lib -->

#     <h1>同頁面，可放不同的 form ，只要 id 不同，就不會打架</h1>
#     <form id="form2" class="upload_city_file"></form>
# </body>
# </html>

# """)

# def UploadCityFileWithJS(R, **kw):
#     DATA = R.POST
#     file = R.FILES.get('file', None)
#     place = Place.objects.get(id=DATA.get('place_id',''))
#     location = R.POST.get('location','')
#     filename = R.POST.get('name','')
#     memo = R.POST.get('memo','')
#     redirect = R.POST.get('redirect','/')
#     try:
#         lng = decimal.Decimal(str(R.POST.get('lng','')))
#         lat = decimal.Decimal(str(R.POST.get('lat','')))

#     except:
#         lng = None
#         lat = None

#     if filename == '': filename = str(file.name)

#     cf = CityFiles(
#                 name = filename,
#                 memo = memo,
#                 place = place,
#                 location = location,
#                 upload_user = R.user,
#                 upload_date = _TODAY(),
#                 file = file,
#                 lat = lat,
#                 lng = lng,
#                 )
#     cf.save()

#     try: ext = file.name.split('.')[-1]
#     except: ext = 'zip'
#     if ext in ['jpg', 'jpeg', 'tiff', 'tif', 'png', 'gif']:
#         thumb(cf.file.name, "width=1024,height=768")

#     getattr(cf, 'file').save('%s.%s'%(cf.id, ext), file)
#     cf.save()

#     return HttpResponse(u"""<html>
# <head>
#     <meta http-equiv="content-type" content="text/html; charset=utf-8" />
#     <meta http-equiv="Refresh" content="5; url=%(redirect)s">
# </head>
# <body>
# %(filename)s 檔案上傳成功， 5 秒後將回到原頁面，如未返回，請點選<a href="%(redirect)s">本連結</a>。
# </body>
# </html>
# """ % {'redirect': redirect, 'filename': filename})

# # god damn aquaculture
# def list_aquaculture(R):
#     pass

# def view_aquaculture(R):
#     pass

# def create_aquaculture(R):
#     pass

# def update_aquaculture(R):
#     pass

# from settings import ROOT
# import csv
# @checkAuthority
# def ImportTempProject(R, **kw):
#     data = list(csv.reader(open(os.path.join(ROOT, 'apps', 'harbor', 'projects2.csv'),"rb")))
#     all = len(data)
#     good = 0
#     bad = 0
#     have = 0
#     bad_list = []
#     for n, p in enumerate(data[1:]):
#         if not Project.objects.filter(year=int(p[3]), name=p[6]):
#             try: p[13] = int(p[13])
#             except: p[13] = 0
#             try:
#                 fishingport = FishingPort.objects.filter(name__contains=p[2])
#                 if len(fishingport) >= 1:
#                     fishingport = fishingport[0]
#                 row = Project(
#                     name = str(p[6]),
#                     year = int(p[3]),
#                     plan = str(p[4]),
#                     contract_fund = int(p[13]),
#                     fishingport = fishingport
#                 )
#                 row.save()
#                 good += 1
#             except:
#                 bad += 1
#                 bad_list.append(n)
#                 pass

#         else:
#             pass
#             have += 1
#     t = get_template(os.path.join('harbor', 'import_temp_project.html'))
#     html = t.render(RequestContext(R,{
#     'all': all,
#     'good': good,
#     'bad': bad,
#     'bad_list': bad_list,
#     'have': have
#     }))
#     return HttpResponse(html)
