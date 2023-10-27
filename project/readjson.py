# -*- coding: utf-8 -*-

#這東西還有用嗎???????????????????????????????????
#這東西還有用嗎???????????????????????????????????
#這東西還有用嗎???????????????????????????????????
#這東西還有用嗎???????????????????????????????????

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

from common.models import Log
from general.models import Place, Unit
from common.lib import find_sub_level, find_sub, nocache_response, md5password, readDATA, verifyOK, makePageList, makeFileByWordExcel
from fishuser.models import Option
from fishuser.models import UserProfile
from fishuser.models import LoginHistory
from fishuser.models import WrongLogin
from fishuser.models import DocumentOfProjectModels
from fishuser.models import Plan
from fishuser.models import PlanBudget
from fishuser.models import Project
from fishuser.models import Budget
from fishuser.models import Project_Port
from fishuser.models import DefaultProject
from fishuser.models import FRCMUserGroup
from fishuser.models import Factory
from fishuser.models import Reserve
from fishuser.models import FundRecord
from fishuser.models import Fund
from fishuser.models import Appropriate
from fishuser.models import Progress
from fishuser.models import RelayInfo
from fishuser.models import ScheduledProgress
from fishuser.models import ProjectPhoto
from fishuser.models import FRCMTempFile
from fishuser.models import _getProjectStatusInList
from fishuser.models import _ca
from project.models import Option2
from project.models import RecordProjectProfile
from project.models import ExportCustomReport
from project.models import ReportField
from project.models import ExportCustomReportField
from pccmating.sync import syncPccInformation
from pccmating.sync import getProjectInfo
from pccmating.models import Project as PCCProject
from pccmating.models import ProjectProgress as PCCProgress
from pccmating.sexual_assault_against_pcc.famhandler import FishMoney

from settings import NUMPERPAGE
import os, random, json, re, datetime
from common.models import Log
from django.forms import ModelForm
from fishuser.views import checkAuthority
import random
from harbor.models import FishingPort
from harbor.models import Aquaculture
from settings import ROOT
from dailyreport.models import EngProfile
#from PIL.Image import split
import decimal
import calendar
from copy import copy

def TODAY(): return datetime.datetime.today()

def NOW(): return datetime.datetime.now()

TAIWAN = Place.objects.get(name=u'臺灣地區')


def readJson(R, **kw):
    if not _ca(user=R.user, project='', right_type_value=kw['right_type_value']) and not R.user.is_staff:
        return HttpResponseRedirect('/u/transfer/')

    DATA = readDATA(R)
    if 'updateProjectInfo' == DATA.get('submit', None):
        row = Project.objects.get(id=DATA.get('project_id', None))
        field_name = DATA.get('entry', None)
        return_name = ''
        return_extr = ''
        if field_name == 'plan':
            field_value = Plan.objects.get(id = DATA.get('new_info', None))
            return_name = field_value.name
            if field_value.no:
                return_extr = field_value.no
        elif field_name == 'bid_no':
            if DATA.get('new_info', None) != '':
		field_value = DATA.get('new_info', None)
		return_name = field_value
            elif DATA.get('new_info', None) == '':
                field_value = ''
                return_name = ''
        elif field_name == 'project_type' :
            field_value = Option.objects.get(id = DATA.get('new_info', None))
            return_name = field_value.value
            if u'漁港工程' in return_name:
		sub_options = Option.objects.filter(swarm='port_type').order_by('id')
            elif u'養殖區工程' in return_name:
                sub_options = Option.objects.filter(swarm='farm_type').order_by('id')
            return_extr = '<a class="show_project_sub_type">' + str(list(sub_options)[0].value) + '</a>'
            return_extr += '<select editing="project_sub_type" category="ProjectBase" class="edit_project_sub_type updateRedaction" value="' + str(list(sub_options)[0].id) + '" old_value="' + str(list(sub_options)[0].id) + '" style="display: none;">'
            for i in sub_options:
                return_extr += '<option value="' + str(i.id) + '" name="' + str(i.value) + '">' + str(i.value) + '</option>'
            return_extr += '</select>'
            setattr(row,  'project_sub_type',  list(sub_options)[0])
            row.fishing_port.all().delete()
            row.aquaculture.all().delete()
        elif field_name == 'project_sub_type':
            field_value = Option.objects.get(id = DATA.get('new_info', None))
            return_name = field_value.value
            if field_value.id in [197,  249]:
                return_extr = True
            else:
                return_extr = False
        elif field_name == 'purchase_type':
            field_value = Option.objects.get(id = DATA.get('new_info', None))
            return_name = field_value.value
            if field_value.id in [277,  278]:
                return_extr = True
            else:
                return_extr = False
        elif field_name == 'place':
            field_value = Place.objects.get(id = DATA.get('new_info', None))
            setattr(row, 'port' , None)
            setattr(row, 'x_coord' , None)
            setattr(row, 'y_coord' , None)
            return_name = field_value.name
            row.fishing_port.all().delete()
            row.aquaculture.all().delete()
        elif field_name.split('_')[0] == 'sub':
            if row.project_type.id == 227:
                try:
                    row.fishing_port.remove(row.fishing_port.get(id=DATA.get('old_info', None)))
                    new_location = FishingPort.objects.get(id=DATA.get('new_info', None))
                    row.fishing_port.add(new_location)
                except ValueError:
                    new_location = FishingPort.objects.get(id=DATA.get('new_info', None))
                    row.fishing_port.add(new_location)
            elif row.project_type.id == 228:
                try:
                    row.aquaculture.remove(row.aquaculture.get(id=DATA.get('old_info', None)))
                    new_location = Aquaculture.objects.get(id=DATA.get('new_info', None))
                    row.aquaculture.add(new_location)
                except ValueError:
                    new_location = Aquaculture.objects.get(id=DATA.get('new_info', None))
                    row.aquaculture.add(new_location)
            return_name = new_location.name
            return HttpResponse(json.write({'status': True, 'return_name': return_name}))
        elif field_name == 'unit':
            field_value = Unit.objects.get(id = DATA.get('new_info', None))
            return_name = field_value.name
        elif field_name == 'undertake_type' or field_name == 'budget_type' or field_name == 'budget_sub_type' or field_name == 'status' or field_name == 'bid_type' or field_name == 'contract_type' :
            field_value = Option.objects.get(id = DATA.get('new_info', None))
            return_name = field_value.value
        elif field_name == 'year':
            field_value = DATA.get('new_info', None)
            ys = int(DATA.get('new_info')) - int(DATA.get('old_info'))
            fund = Fund.objects.filter(project = DATA.get('project_id', None))
            for i in fund:
                i.year += ys
                i.save()
                for b in Budget.objects.filter(fund = i):
                    b.year += ys
                    b.save()
            reserve = Reserve.objects.filter(project = DATA.get('project_id', None))
            for r in reserve:
                r.year += ys
                r.save()

            return_name = field_value
        elif field_name in ['x_coord', 'y_coord', 'vouch_date', 'vouch_no', \
                            'self_charge', 'self_contacter', 'self_contacter_phone', 'self_contacter_email',\
                            'local_charge', 'local_contacter', 'local_contacter_phone', 'local_contacter_email',\
                            'contractor_charge', 'contractor_contacter', 'contractor_contacter_phone', 'contractor_contacter_email',\
                            'divert', 'invoke', 'available', 'location']:
            if DATA.get('new_info', None) == '':
                field_value = None
                return_name = ''
            else:
                field_value = DATA.get('new_info', None)
                return_name = field_value
        else:
            if 'date' in field_name and DATA.get('new_info', None) == '':
		field_value = None
		return_name = ''
	    else:
		field_value = DATA.get('new_info', None)
		return_name = field_value
        setattr(row, field_name , field_value)
        row.save()
        return HttpResponse(json.write({'status': True, 'return_name': return_name, 'return_extr': return_extr}))

    elif 'getFishingPort' == DATA.get('submit', None):
        ports = FishingPort.objects.filter(place=DATA.get('place', None)).order_by('id')
        try:
            num =  '_' + DATA.get('num', None)
        except:
            num = ''
        contents = ''
        contents += '<select id="port' + num + '" name="port' + num + '" class="getcoord">'
        contents += '<option value="" twdx="" twdy="">--非港區--</option>'
        for port in ports:
            contents += '<option value="' + str(port.id) + '" twdx="' + str(port.twd97().x) + '" twdy="' +str(port.twd97().y) +  '">' + str(port.name) + '</option>'
        contents += '</select>'

        return HttpResponse(json.write({'status': True, 'contents': contents}))

    elif 'changeFishingPort' == DATA.get('submit', None):
        ports = FishingPort.objects.filter(place=DATA.get('place', None)).order_by('id')
        contents = ''
        contents += '<a id="port" class="show_port">--非港區--</a>'
        contents += '<select id="port" class="edit_port update_edited updatecoord" value="" old_value="" style="display: none;">'
        contents += '<option value="" twdx="" twdy="" selected>--非港區--</option>'
        for port in ports:
            contents += '<option value="' + str(port.id) + '" twdx="' + str(port.twd97().x) + '" twdy="' +str(port.twd97().y) +  '">' + str(port.name) + '</option>'
        contents += '</select>'

        return HttpResponse(json.write({'status': True, 'contents': contents}))

    elif 'updateBudgetInfo' == DATA.get('submit', None):
        row = BudgetProject.objects.get(id=DATA.get('dn', None))
        return_name = ''
        field_name = DATA.get('entry', None)

        if DATA.get('new_info', None) == '':
            if 'memo' in field_name:
                field_value = ''
                return_name = ''
            else:
                field_value = 0
                return_name = '0'
        else:
            field_value = DATA.get('new_info', None)
            return_name = field_value

        setattr(row, field_name , field_value)
        row.save()

        return HttpResponse(json.write({'status': True, 'return_name': return_name,}))

    elif 'updateBidinfo' == DATA.get('submit', None):
        row = Project.objects.get(id=DATA.get('project_id', None))
        return_name = ''
        field_name = DATA.get('entry', None)
        spic_rz = False
        extr = ''
        if field_name == 'pcc_no':
            field_value = DATA.get('new_info', None)
            if DATA.get('new_info', None) == '':
                field_value = None
                return_name = ''
            else:
                return_name = field_value
                try: extr = getProjectInfo(field_value)
                except:
                    message = u'無法使用此編號取得工程資訊。編號有誤、或是權限不足(工程會補助機關未正確填報)。'
                    return HttpResponse(json.write({'status': False, 'return_name': return_name,  'message': message}))
        elif field_name == 'allot_rate' :
            if DATA.get('new_info', None) == '':
                field_value = decimal.Decimal(str(100.00))
                return_name = '100'
            else:
                field_value = decimal.Decimal(str(DATA.get('new_info', None)))
                return_name = str(field_value)
        elif field_name == 'bid_type' or field_name == 'contract_type' :
            if DATA.get('new_info', None) == '':
                field_value = None
                return_name = ''
            else:
                field_value = Option.objects.get(id = DATA.get('new_info', None))
                return_name = field_value.value
        elif field_name == 'design_bid' or field_name == 'inspect_bid' or field_name == 'construction_bid' or field_name == 'pollution' or field_name == 'manage' or field_name == 'other_defray':
            field_value = DATA.get('new_info', None)
            if DATA.get('new_info', None) == '':
                field_value = 0
                spic_rz = True
            if int(float(field_value)) == float(field_value):
                return_name = field_value
            else:
                return_name = str(round(float(field_value),3))
        else:
            field_value = DATA.get('new_info', None)
            if DATA.get('new_info', None) == '':
                field_value = None
                return_name = ''
            else:
                return_name = field_value
        setattr(row, field_name , field_value)
        row.save()
        FundRecords = Fund.objects.filter(project=row)
        if len(FundRecords) > 0:
            _updateFundRecord(project=row ,item=field_name)

        load, local = False, False
        if field_name == 'allot_rate' or field_name == 'design_bid' or field_name == 'inspect_bid' or field_name == 'construction_bid' or field_name == 'pollution' or field_name == 'manage' or field_name == 'other_defray':
            if row.rTotalMoney() == 0:
                load = True
            else:
                load = round(float(row.rTotalMoney())*float(str(row.allot_rate))*0.01, 3)
                local = round(float(row.rTotalMoney()) - load, 3)

        project = Project.objects.get(id=DATA.get('project_id', None))

        total = project.rTotalMoney()

        return HttpResponse(json.write({'status': True, 'return_name': return_name, 'spic_rz':spic_rz, 'load':load, 'local':local, 'extr': extr}))

    elif 'updateProgress' == DATA.get('submit', None):
        return_name = ''
        row = Progress.objects.get(id=DATA.get('row', None))
        order = Progress.objects.filter(project = DATA.get('project_id', None)).order_by('-date')
        for i in order:
            if DATA.get('new_info', None) == str(i.date):
                message = '日期已存在！'
                return HttpResponse(json.write({'status': False, 'return_name': return_name, 'message': message,}))
            else:
                setattr(row, 'record_date', datetime.date.today())
                row.save()


        field_name = DATA.get('entry', None).replace('_'+DATA.get('row', None))

        if 'date' in field_name and DATA.get('new_info', None) == '':
            field_value = None
            return_name = ''
        else:
            if DATA.get('new_info', None) == '':
                field_value = decimal.Decimal(str(0))
                return_name = ''
            else:
                field_value = DATA.get('new_info', None)
                if 'date' in field_name:
                    return_name = field_value

                elif 'progress' in field_name:
                    if int(float(field_value)) == float(field_value):
                        return_name = str(field_value) + '.00'
                    else:
                        return_name = str(round(float(field_value),3))
                else:
                    if int(float(field_value)) == float(field_value):
                        return_name = field_value
                    else:
                        return_name = str(round(float(field_value),3))
        setattr(row, field_name , field_value)
        row.save()
        FundRecords = Fund.objects.filter(project=row.project)
        if len(FundRecords) > 0:
            _updateFundRecord(project=row.project, item=DATA.get('name', None))

        insert = 'start'
        col = ''
        if 'schedul' in DATA.get('entry', None):
            col = 'Progress'
            if DATA.get('new_info', None) == '':
                insert = list(order)[-1].id
            else:
                for i in order:
                    try:
                        if i.schedul_date < ScheduledProgress.objects.get(id=row.id).schedul_date:
                            insert = i.id
                            break
                    except:
                        continue
        elif 'actual' in DATA.get('entry', None):
            col = 'Progress'
            if DATA.get('new_info', None) == '':
                insert = list(order)[-1].id
            else:
                for i in order:
                    try:
                        if i.date < Progress.objects.get(id=row.id).date:
                            insert = i.id
                            break
                    except:
                        continue
        elif 'allot_date' in DATA.get('name', None):
            col = 'Appropriate'
            if DATA.get('new_info', None) == '':
                insert = list(order)[-1].id
            else:
                for i in list(order):
                    try:
                        if i.allot_date < Appropriate.objects.get(id=row.id).allot_date:
                            insert = i.id
                            break
                    except:
                        continue

        return HttpResponse(json.write({'status': True, 'return_name': return_name, 'insert': insert, 'col': col,}))

    elif 'switchCountType' == DATA.get('submit', None):
        row = Project.objects.get(id=DATA.get('project', None))
        if DATA.get('count_type', None) == 'auto':
            field_value = 0
        elif DATA.get('count_type', None) == 'write':
            field_value = 1
        setattr(row, 'count_type' , field_value)
        row.save()

        return HttpResponse(json.write({'status': True,}))

    elif 'updateFundInfo' == DATA.get('submit', None):
        if DATA.get('rn', None)=='undefined':
            row = Reserve.objects.get(id=DATA.get('rd', None))
            field_name = DATA.get('entry', None)
            field_value = DATA.get('new_info', None)
            return_name = ''
            setattr(row, field_name, field_value)
            row.save()
            return_name = field_value
            return HttpResponse(json.write({'status': True, 'return_name': return_name, 'msg': '修改成功!'}))


        else:
            row = FundRecord.objects.get(id=DATA.get('rn', None))
            field_name = DATA.get('entry', None)
            return_name = '....'
            if DATA.get('new_info', None) == '':
                field_value = None
                if field_name == 'record_date':
                    return_name = '　---------　'
                else:
                    return_name = ''
            else:
                if field_name == 'record_date':
                    try:
                        FundRecord.objects.get(project=row.project, year=row.year, record_date=DATA.get('new_info', None))
                        return HttpResponse(json.write({'status': False, 'msg': '已有此日期之紀錄!'}))
                    except:
                        field_value = DATA.get('new_info', None)
                else:
                    field_value = DATA.get('new_info', None)
                return_name = field_value
            setattr(row, field_name , field_value)

            if field_name == 'record_date' and field_value != None:
                if field_value != None:
                    _updateFundRecord(project=row.project, item=field_name, record=row, date=datetime.datetime.strptime(field_value,"%Y-%m-%d").date())
                else:
                    _updateFundRecord(project=row.project, item=field_name, record=row, date='')
            else:
                _updateFundRecord(project=row.project, item=field_name, record=row)

            new_info = {}
            id_list = []
            key_list = ['local_payout', 'total_payout', 'sum_self_payout', 'sum_local_payout', 'total_sum_payout', 'payment', 'self_unpay', 'local_unpay', 'total_unpay', 'self_surplus', 'local_surplus', 'total_surplus', 'rate']
            new_records = FundRecord.objects.filter(project=row.project, year=row.year)
            for i in new_records:
                new_info[str(i.id)]={}
                new_info[str(i.id)]['local_payout'] = str(round(i.local_payout or 0, 3))
                new_info[str(i.id)]['total_payout'] = str(round(i.rPayout(), 3))
                new_info[str(i.id)]['sum_self_payout'] = str(round(i.sum_self_payout or 0, 3))
                new_info[str(i.id)]['sum_local_payout'] = str(round(i.sum_local_payout or 0, 3))
                new_info[str(i.id)]['total_sum_payout'] = str(round(i.rSumPayout(), 3))
                new_info[str(i.id)]['payment'] = str(round(i.payment or 0, 3))
                new_info[str(i.id)]['self_unpay'] = str(round(i.self_unpay or 0, 3))
                new_info[str(i.id)]['local_unpay'] = str(round(i.local_unpay or 0, 3))
                new_info[str(i.id)]['total_unpay'] = str(round(i.rUnpay(), 3))
                new_info[str(i.id)]['self_surplus'] = str(round(i.self_surplus or 0, 3))
                new_info[str(i.id)]['local_surplus'] = str(round(i.local_surplus or 0, 3))
                new_info[str(i.id)]['total_surplus'] = str(round(i.rSurplus(), 3))
                new_info[str(i.id)]['rate'] = str(round(i.rRate(), 2))
                id_list.append(str(i.id))
                for j in new_info[str(i.id)]:
                    if new_info[str(i.id)][j] == '0.0':
                        new_info[str(i.id)][j] = ''
                    if new_info[str(i.id)][j][-2:] == '.0':
                        new_info[str(i.id)][j] = new_info[str(i.id)][j][:-2]

            insert = 'start'
            order = FundRecord.objects.filter(project = row.project, year=row.year).order_by('-record_date')
            if FundRecord.objects.get(id=row.id).record_date == None:
                insert = list(order)[0].id
            else:
                for i in order:
                    try:
                        if i.record_date < FundRecord.objects.get(id=row.id).record_date:
                            insert = i.id
                            break
                    except:
                        continue

            return HttpResponse(json.write({'status': True, 'return_name': return_name, 'insert': insert, 'new_info':new_info, 'key_list':key_list, 'id_list':id_list,
                            }))


    elif 'updateFundRecode' == DATA.get('submit', None):
        row = FundRecord.objects.get(id=DATA.get('dn', None))
        return_name = ''
        field_name = DATA.get('name', None)
        if field_name == 'record_time':
            time = str(datetime.datetime.now())[10:]
            field_value = DATA.get('new_info', None) + time
            return_name = field_value
        elif field_name == 'status':
            field_value = Option.objects.get(id=DATA.get('new_info', None))
            return_name = field_value.value
        else:
            field_value = DATA.get('new_info', None)
            return_name = field_value
        setattr(row, field_name , field_value)
        row.save()
        title = str(row.record_time)[:10] + ' (' + row.status.value[:2] + ')'

        return HttpResponse(json.write({'status': True, 'return_name': return_name, 'title': title,}))

    elif 'deleteFundRecord' == DATA.get('submit', None):
        row = FundRecord.objects.get(id=DATA.get('dn', None))
        row.delete()

        return HttpResponse(json.write({'status': True,}))

    elif 'changeYearList' == DATA.get('submit', None):
        records = FundRecord.objects.filter(project = DATA.get('project', None), year = int(DATA.get('year', None))).order_by('-record_time')
        contents = ''
        list(records).sort()

        for i in records:
            contents += '<tr><td>'
            contents += '<a id="record_' + str(i.id) + '" href="/project/refundhistory/' + str(DATA.get('project', None)) + '/' + str(i.id) + '">' + str(i.record_time)[:10] + ' (' + i.status.value[:2] + ')' + '</a>'
            contents += '</tr></td>'

        return HttpResponse(json.write({'status': True, 'contents': contents}))

    elif 'makeFundRecord' == DATA.get('submit', None):
        record_time = datetime.datetime.now()
        try:
            adopt_progress = float(list(Progress.objects.filter(project=DATA.get('project', None)).order_by('-date'))[0].actual_progress_percent)
        except:
            adopt_progress = 0.0

        row = FundRecord(
                            project = Project.objects.get(id = DATA.get('project', None)),
                            year = int(DATA.get('year', None)),
                            record_time = record_time,
                            self_budget = DATA.get('self_budget', None),
                            local_budget = DATA.get('local_budget', None),
                            self_payout = DATA.get('self_payout', None),
                            local_payout = DATA.get('local_payout', None),
                            self_load = DATA.get('self_load', None),
                            self_past_budget = DATA.get('self_past_budget', None),
                            local_past_budget = DATA.get('local_past_budget', None),
                            payment = DATA.get('payment', None),
                            self_unpay = DATA.get('self_unpay', None),
                            local_unpay = DATA.get('local_unpay', None),
                            self_surplus = DATA.get('self_surplus', None),
                            local_surplus = DATA.get('local_surplus', None),
                            progress = str(adopt_progress),
                            status = Option.objects.get(id=180)
                            )
        row.save()

        contents = '<div class="flora" style="overflow: auto"><h2>'
        contents += '<style type="text/css">'
        contents += '.style0 { font-size: 16px; }'
        contents += '</style>'
        contents += '請選擇記錄狀態：'
        contents += '<select id="status" class="style0 fundrecord_set" dn="'+ str(row.id) +'">'
        for i in _make_choose()['fundrecord_status'] :
            contents += '<option value="' + str(i.id) + '">　' + i.value + '　</option>'
        contents += '</select>'
        contents += '<br>'
        contents += '狀態備註：<br>'
        contents += '<textarea cols="38" rows="10" id="status_memo" class="fundrecord_set" dn="'+ str(row.id) +'"></textarea>'
        contents += '</h2></div>'

        return HttpResponse(json.write({'status': True,'contents': contents}))

    elif 'updateFundRecordSet' == DATA.get('submit', None):
        row = FundRecord.objects.get(id=DATA.get('record', None))
        field_name = DATA.get('target', None)
        field_value = DATA.get('value', None)
        if field_name == 'status':
            setattr(row, field_name, Option.objects.get(id=field_value))
        elif  field_name == 'status_memo':
            setattr(row, field_name, field_value)
        row.save()

        return HttpResponse(json.write({'status': True}))

    elif 'getProjectSerial' == DATA.get('submit', None):
        plan = Plan.objects.get(id = DATA.get('plan_id', None))
        project_serial_code = ''
        if plan.project_serial == 'Null':
            project_serial_code = '001'
#        else:
#            project_serial = plan.project_serial
#            project_serial_code = '%03d' % (plan.project_serial + 1)
        return HttpResponse(json.write({'project_serial_code': project_serial_code}))

    elif 'updatePlanInfo' == DATA.get('submit', None):
        row = Plan.objects.get(id=DATA.get('plan_id', None))
        if DATA.get('plan_name', None) != '':
            setattr(row, 'name' , DATA.get('plan_name', None))
        if DATA.get('plan_host', None) != '':
            setattr(row, 'host' , DATA.get('plan_host', None))
            plan_host = DATA.get('plan_host', None)
        else:
            setattr(row, 'host' , None)
            plan_host = '----'
        if DATA.get('plan_no', None) != '':
            setattr(row, 'no' , DATA.get('plan_no', None))
            plan_no = DATA.get('plan_no', None)
        else:
            setattr(row, 'no' , None)
            plan_no = '----'
        if DATA.get('plan_budget', None) != '':
            setattr(row, 'budget' , DATA.get('plan_budget', None))
            plan_budget = DATA.get('plan_budget', None)
        else:
            setattr(row, 'budgeto' , None)
            plan_budget = '----'
        if DATA.get('plan_note', None) != '':
            setattr(row, 'note' , DATA.get('plan_note', None))
            plan_note = DATA.get('plan_note', None)
        else:
            setattr(row, 'note' , None)
            plan_note = '----'
        row.save()
        return HttpResponse(json.write({'status': True, 'plan_name':row.name, 'plan_host':plan_host, 'plan_no':plan_no, 'plan_budget':plan_budget, 'plan_note':plan_note}))

    elif 'setDefaultProject' == DATA.get('submit', None):
        project = Project.objects.get(id=DATA.get('project_id', None))
        try:
            default = DefaultProject.objects.get(user=R.user, project=project)
            default.delete()
        except:
            default = DefaultProject(
                                    user = R.user,
                                    project = project,
                                    )
            default.save()
        return HttpResponse(json.write({'status': True}))

    elif 'deleteProjectPhoto' == DATA.get('submit', None):
        row = ProjectPhoto.objects.get(id=DATA.get('photo_id', None))
        row.delete()
        project = Project.objects.filter(id=DATA.get('project_id', None))
        count = len(ProjectPhoto.objects.filter(project=project))
        return HttpResponse(json.write({'status': True, 'count': count}))

    elif 'updatePhotoInfo_Edit' == DATA.get('submit', None):
        row = ProjectPhoto.objects.get(id=DATA.get('photo_id', None))
        setattr(row, DATA.get('field_name', ''), DATA.get('value', ''))
        row.save()
        return HttpResponse(json.write({'status': True}))

    elif 'ShowandHidePlan' == DATA.get('submit', None):
        lv = DATA.get('lv', 'all')
        if lv == 'all': lv = 99999
        else: lv = int(lv)
        show_plans = []
        hide_plans = []
        for i in Plan.objects.all().order_by('id'):
            if i.rLevelNumber() <= lv:
                show_plans.append(str(i.id))
            else:
                hide_plans.append(str(i.id))
        return HttpResponse(json.write({'status': True, 'show_plans': show_plans, 'hide_plans': hide_plans ,}))

    elif 'ShowSubPlan' == DATA.get('submit',None):
        plan_id = int(DATA.get('id'))
        show_subplans=[]
        for i in Plan.objects.all().order_by("id"):
            if i.uplevel_id == plan_id:
                show_subplans.append(str(i.id))
        return HttpResponse(json.write({'show_subplans': show_subplans}))

    elif 'HideSubPlan' == DATA.get('submit',None):
        plan_id = int(DATA.get('id'))
        subplans = Plan.objects.get(id = plan_id).rSubPlanInList()
        hide_subplans=[]
        for i in subplans:
            hide_subplans.append(str(i.id))
        return HttpResponse(json.write({'hide_subplans': hide_subplans}))


    elif 'setPlanToWorkExcel' == DATA.get('submit', None):
        plan = Plan.objects.get(id=DATA.get('plan_id',''))
        plans = [str(plan.id)]
        for p in plan.rSubPlanInList():
            plans.append(str(p.id))
        return HttpResponse(json.write({'status': True, 'plans': plans}))

    elif 'quickupdate' == DATA.get('submit', None):
        return_name = ''
        message = ''
        row = Project.objects.get(id=DATA.get('project_id', None))
        if DATA.get('field', None) == 'status':
            value = Option.objects.get(id=DATA.get('new_info', None))
            setattr(row, DATA.get('field', None), value)
            return_name = value.value
        else:
            if DATA.get('new_info', None) == '':
                value = None
            else:
                value = DATA.get('new_info', None)
            setattr(row, DATA.get('field', None), value)
            return_name = DATA.get('new_info', None)
        try:
            row.save()
            status = True
        except:
            message = '格式錯誤！'
            status = False
        return HttpResponse(json.write({'status': status, 'return_name': return_name, 'message': message}))

    elif 'checkUndertakeType' == DATA.get('submit', None):
        undertake_type = Option.objects.get(id=DATA.get('undertake_type', None))
        if undertake_type.value == '自辦':
            status = False #means hide info
        else:
            status = True #means show info
        return HttpResponse(json.write({'status': status}))

    elif 'getPlanListInTable' == DATA.get('submit', None):
        plan = Plan.objects.get(id=DATA.get('plan_id', None))
        table = '<table class="plan_radio_table" border="1" style="border-collapse: collapse">'
        table += '<tr align="center" bgcolor="#CCFF99"><td>選擇<br>位置</td><td>計畫名稱</td></tr>'
        top_plan = Plan.objects.get(id=1)
        for i in [top_plan] + top_plan.rSubPlanInList():
            if i not in  [top_plan, plan] + plan.rSubPlanInList():
                table += '<tr bgcolor="#FFFFFF"><td align="center"><input id="plan_radio" name="plan_radio" type="radio" value="' + str(i.id) + '"></td>'
                table += '<td>' + '　　' * i.rLevelNumber() + i.name + '</td></tr>'
            else:
                table += '<tr bgcolor="#AAAAAA"><td align="center"></td>'
                table += '<td>' + '　　' * i.rLevelNumber() + i.name + '</td></tr>'
        table += '</table>'
        return HttpResponse(json.write({'table': table}))

    elif 'updatePlanSort' == DATA.get('submit', None):
        relation = DATA.get('relation_radio', None) # ['theSameLevel' or 'isSubLevel']
        select_plan = Plan.objects.get(id=DATA.get('plan_radio', None))
        if relation == 'theSameLevel':
            target_plan = select_plan.uplevel
        elif relation == 'isSubLevel':
            target_plan = select_plan
        wantSortPlan = Plan.objects.get(id=DATA.get('wantSortPlan', None))
        move_list = [wantSortPlan] + wantSortPlan.rSubPlanInList()
        gt_plans = Plan.objects.filter(sort__gt=target_plan.sort).order_by('sort')
        try:
            up_sort_num = float(select_plan.rSubPlanInList()[-1].sort)
        except:
            up_sort_num = float(select_plan.sort)
        try:
            down_sort_num = float(Plan.objects.filter(sort__gt=decimal.Decimal(str(up_sort_num))).order_by('sort')[0].sort)
        except:
            down_sort_num = 10000
        wantSortPlan.uplevel = target_plan
        wantSortPlan.save()
        if not gt_plans:
            sort_num = target_plan.sort
            for i in move_list:
                i.sort = sort_num + 1
                i.save()
                sort_num += 1
        else:
            for i in move_list:
                up_sort_num = (up_sort_num + down_sort_num) / 2.
                i.sort = decimal.Decimal(str(up_sort_num))
                i.save()
        return HttpResponse(json.write({'status': True}))

    elif 'addPlanBudget' == DATA.get('submit', None):
        plan = Plan.objects.get(id=DATA.get('plan', None))
        try:
            busgets = PlanBudget.objects.filter(plan = plan).order_by('year')
            new_year = list(busgets)[-1].year + 1
            if new_year > TODAY().year - 1910:
                new_year = None
        except:
            new_year = TODAY().year - 1911
        row = PlanBudget(plan = plan, year = new_year)
        try:
            all_budget = PlanBudget.objects.filter(plan=plan).order_by('-year')
            insert = list(all_budget)[0].id
            for i in list(all_budget):
                if i.year == None:
                    insert = i.id
        except:
            insert = 'start'

        row.save()

        id = str(row.id)
        years = [y-1911 for y in xrange(2006, TODAY().year+2)]
        years.reverse()
        if new_year == None:
            new_year = ''

        content = ''
        content += '<tr align="right" id="' + str(plan.id) + '_' + id + '">'
        content += '<td id="year_' + id + '" class="editable" align="center">'
        content += '<a id="year_' + id + '" class="show_year_' + id + '">' + str(new_year) + '</a>'
        content += '<select id="year_' + id + '" class="edit_year_' + id + ' update_planbudget" planbudget="' + id + '" field="year" value="' + str(new_year) + '" old_value="' + str(new_year) + '" style="display: none;">'
        content += '<option value=""></option>'
        for y in years:
            content += '<option value="' + str(y) + '"'
            if y == new_year:
                content += ' selected '
            content += '>' + str(y) + '</option>'
        content += '</select></td>'
        content += '<td><span id="total_' + id + '">0</span></td>'
        content += '<td id="capital_self_' + id + '" class="editable">'
        content += '<a id="capital_self_' + id + '" class="show_capital_self_' + id + '"></a>'
        content += '<input id="capital_self_' + id + '" class="edit_capital_self_' + id + ' update_planbudget float" planbudget="' + id + '" field="capital_self" size="7" type="text" value="" old_value="" style="text-align: right;display: none;"></td>'
        content += '<td id="capital_trust_' + id + '" class="editable">'
        content += '<a id="capital_trust_' + id + '" class="show_capital_trust_' + id + '"></a>'
        content += '<input id="capital_trust_' + id + '" class="edit_capital_trust_' + id + ' update_planbudget float" planbudget="' + id + '" field="capital_trust" size="7" type="text" value="" old_value="" style="text-align: right;display: none;"></td>'
        content += '<td id="capital_grant_' + id + '" class="editable">'
        content += '<a id="capital_grant_' + id + '" class="show_capital_grant_' + id + '"></a>'
        content += '<input id="capital_grant_' + id + '" class="edit_capital_grant_' + id + ' update_planbudget float" planbudget="' + id + '" field="capital_grant" size="7" type="text" value="" old_value="" style="text-align: right;display: none;"></td>'
        content += '<td><span id="capital_total_' + id + '">0</td>'
        content += '<td id="regular_self_' + id + '" class="editable">'
        content += '<a id="regular_self_' + id + '" class="show_regular_self_' + id + '"></a>'
        content += '<input id="regular_self_' + id + '" class="edit_regular_self_' + id + ' update_planbudget float" planbudget="' + id + '" field="regular_self" size="7" type="text" value="" old_value="" style="text-align: right;display: none;"></td>'
        content += '<td id="regular_trust_' + id + '" class="editable">'
        content += '<a id="regular_trust_' + id + '" class="show_regular_trust_' + id + '"></a>'
        content += '<input id="regular_trust_' + id + '" class="edit_regular_trust_' + id + ' update_planbudget float" planbudget="' + id + '" field="regular_trust" size="7" type="text" value="" old_value="" style="text-align: right;display: none;"></td>'
        content += '<td id="regular_grant_' + id + '" class="editable">'
        content += '<a id="regular_grant_' + id + '" class="show_regular_grant_' + id + '"></a>'
        content += '<input id="regular_grant_' + id + '" class="edit_regular_grant_' + id + ' update_planbudget float" planbudget="' + id + '" field="regular_grant" size="7" type="text" value="" old_value="" style="text-align: right;display: none;"></td>'
        content += '<td><span id="regular_total_' + id + '">0</td>'
        content += '<td id="memo_' + id + '" class="editable" align="left">'
        content += '<a id="memo_' + id + '" class="show_memo_' + id + '"></a>'
        content += '<textarea id="memo_' + id + '" cols="17" rows="1" class="edit_memo_' + id + ' update_planbudget" planbudget="' + id + '" field="memo" type="text" value="" old_value="" style="display: none;"></textarea></td>'
        content += '<td align="center"><img src="/media/images/delete.png" title="刪除紀錄" dn="' + id + '" class="deletePlanBudget"></td></tr>'

        return HttpResponse(json.write({'status': True, 'insert':insert, 'plan_id':plan.id, 'content':content}))

    elif 'updatePlanBudget' == DATA.get('submit', None):
        row = PlanBudget.objects.get(id=DATA.get('planbudget', None))
        plan = row.plan.id
        return_name = ''
        field_name = DATA.get('field', None)
        if DATA.get('new_info', None) == '':
            field_value = None
            return_name = ''
        else:
            if field_name == 'year':
                planbudgets = PlanBudget.objects.filter(plan=row.plan)
                pb_years = []
                for p in planbudgets:
                    pb_years.append(str(p.year))
                if DATA.get('new_info', None) in pb_years:
                    return HttpResponse(json.write({'status': False, 'message': '已有此年度資料!'}))
            field_value = DATA.get('new_info', None)
            return_name = field_value

        setattr(row, field_name , field_value)
        row.save()

        insert = 'start'
        order = PlanBudget.objects.filter(plan = row.plan).order_by('-year')
        if PlanBudget.objects.get(id=row.id).year == None:
            insert = list(order)[0].id
        else:
            for i in order:
                try:
                    if i.year < PlanBudget.objects.get(id=row.id).year:
                        insert = i.id
                        break
                except:
                    continue

        total = row.rTotal()
        ctotal = row.rCapitalTotal()
        rtotal = row.rRegularTotal()
        return HttpResponse(json.write({'status': True, 'return_name': return_name, 'total': total, 'ctotal': ctotal, 'rtotal':rtotal, 'insert':insert, 'plan':plan}))


    elif 'deletePlanBudget' == DATA.get('submit', None):

        row = PlanBudget.objects.get(id = DATA.get('pb', None))
        plan = str(row.plan.id)
        row.delete()

        return HttpResponse(json.write({'status': True, 'plan': plan}))


    elif 'addProjectFund' == DATA.get('submit', None):
        project = Project.objects.get(id=DATA.get('project', None))
        year = int(DATA.get('year', None))
        new_date = datetime.date.today()

        records = FundRecord.objects.filter(project = project, year = year).order_by('record_date')
        record_dates = [r.record_date  for r in records]
        if new_date in record_dates:
            new_date = None

        row = FundRecord(project = project, year = year, record_date = new_date)
        try:
            all_records = FundRecord.objects.filter(project = project, year = year).order_by('-record_date')
            insert = list(all_records)[0].id
            for i in list(all_records):
                if i.record_date == None:
                    insert = i.id
        except:
            insert = 'start'
        row.save()
        _updateFundRecord(project=row.project,record=row, item='new_record')

        id = str(row.id)
        if row.record_date:
            show_date = str(row.record_date)
            date_value = str(row.record_date)
            pay = str(row.payment)
        else:
            show_date = '　---------　'
            date_value = ''
            pay = ''

        content = ''
        content += '<tr align="right" id="record_' + id + '" class="hightlightFundrecord">'
        content += '<td align="center" id="record_date_' + id + '" class="editable">'
        content += '<a id="record_date_' + id + '" class="show_record_date_' + id + '">' + show_date + '</a>'
        content += '<input id="record_date_' + id + '" class="edit_record_date_' + id + ' update_edited chooseDate" field="record_date" size="9" rn="' + id + '" type="text" value="' + date_value + '" old_value="' + date_value + '" style="display: none;"></td>'
        content += '<td align="right" id="self_payout_' + id + '" class="editable">'
        content += '<a id="self_payout_' + id + '" class="show_self_payout_' + id + '"></a>'
        content += '<input id="self_payout_' + id + '"  class="edit_self_payout_' + id + ' update_edited float" field="self_payout" size="6" rn="' + id + '" type="text" value="" old_value="" style="display: none; text-align:right;"></td>'
        content += '<td><span id="s_local_payout_' + id + '"></span></td>'
        content += '<td><span id="s_total_payout_' + id + '"></span></td>'
        content += '<td><span id="s_sum_self_payout_' + id + '"></span></td>'
        content += '<td><span id="s_sum_local_payout_' + id + '"></span></td>'
        content += '<td><span id="s_total_sum_payout_' + id + '"></span></td>'
        content += '<td><span id="s_payment_' + id + '">' + pay + '</span></td>'
        content += '<td><span id="s_self_unpay_' + id + '"></span></td>'
        content += '<td><span id="s_local_unpay_' + id + '"></span></td>'
        content += '<td><span id="s_total_unpay_' + id + '"></span></td>'
        content += '<td><span id="s_self_surplus_' + id + '"></span></td>'
        content += '<td><span id="s_local_surplus_' + id + '"></span></td>'
        content += '<td><span id="s_total_surplus_' + id + '"></span></td>'
        content += '<td align="center"><span id="s_rate_' + id + '"></span></td>'
        content += '<td id="status_memo_' + id + '" class="editable" align="left"><a id="status_memo_' + id + '" class="show_status_memo_' + id + '"></a>'
        content += '<textarea id="status_memo_' + id + '" cols="17" rows="1" class="edit_status_memo_' + id + ' update_edited" field="status_memo"  rn="' + id + '" field="status_memo" type="text" value="" old_value="" style="display: none;"></textarea></td>'
        content += '<td align="center"><img id="delete_' + id + '" src="/media/images/delete.png" title="刪除紀錄" rn="' + id + '" date="' + date_value + '" class="deleteProjectFund"></td></tr>'

        return HttpResponse(json.write({'status': True, 'insert':insert, 'content':content}))


    elif 'deleteProjectFund' == DATA.get('submit', None):
        row = FundRecord.objects.get(id = DATA.get('rn', None))
        project = row.project
        year = row.year
        row.delete()
        _updateFundRecord(project=project, item='delete')

        new_info = {}
        id_list = []
        key_list = ['local_payout', 'total_payout', 'sum_self_payout', 'sum_local_payout', 'total_sum_payout', 'payment', 'self_unpay', 'local_unpay', 'total_unpay', 'self_surplus', 'local_surplus', 'total_surplus', 'rate']
        new_records = FundRecord.objects.filter(project=project, year=year)
        for i in new_records:
            new_info[str(i.id)]={}
            new_info[str(i.id)]['local_payout'] = str(round(i.local_payout or 0, 3))
            new_info[str(i.id)]['total_payout'] = str(round(i.rPayout(), 3))
            new_info[str(i.id)]['sum_self_payout'] = str(round(i.sum_self_payout or 0, 3))
            new_info[str(i.id)]['sum_local_payout'] = str(round(i.sum_local_payout or 0, 3))
            new_info[str(i.id)]['total_sum_payout'] = str(round(i.rSumPayout(), 3))
            new_info[str(i.id)]['payment'] = str(round(i.payment or 0, 3))
            new_info[str(i.id)]['self_unpay'] = str(round(i.self_unpay or 0, 3))
            new_info[str(i.id)]['local_unpay'] = str(round(i.local_unpay or 0, 3))
            new_info[str(i.id)]['total_unpay'] = str(round(i.rUnpay(), 3))
            new_info[str(i.id)]['self_surplus'] = str(round(i.self_surplus or 0, 3))
            new_info[str(i.id)]['local_surplus'] = str(round(i.local_surplus or 0, 3))
            new_info[str(i.id)]['total_surplus'] = str(round(i.rSurplus(), 3))
            new_info[str(i.id)]['rate'] = str(round(i.rRate(), 2))
            id_list.append(str(i.id))
            for j in new_info[str(i.id)]:
                if new_info[str(i.id)][j] == '0.0':
                    new_info[str(i.id)][j] = ''
                if new_info[str(i.id)][j][-2:] == '.0':
                    new_info[str(i.id)][j] = new_info[str(i.id)][j][:-2]


        return HttpResponse(json.write({'status': True, 'key_list':key_list, 'id_list':id_list, 'new_info':new_info,}))


    elif 'jsGetChart' == DATA.get('submit', None):
        status = False
        title = DATA.get('mark', None)
        tag_list = DATA.get('tag_list', None).split('+')
        num_list = DATA.get('num_list', None).split('+')
        data = []
        name = []
        for n, i in enumerate(num_list):
            if i != '':
                data.append(int(i))
                name.append(tag_list[n])
                if int(i) != 0:
                    status = True


        chart_cache_name = R.session.session_key + '_data_' + DATA.get('tar', None) + '_' + DATA.get('tp', None) + '_' + DATA.get('tf', None)
        cache.set(chart_cache_name, {'title': title, 'names': name, 'values': data}, 3600) #會快取 3600 秒


        return HttpResponse(json.write({'status': status, 'chart_cache_name': chart_cache_name, 'name':name, 'data':data}))

    elif 'selectYearByChage' == DATA.get('submit', None):
        year = DATA.get('year', TODAY().year)
        html = ''
        if year == TODAY().year: last_month = TODAY().month
        else: last_month = 12
        html += '<option value="' + str(last_month) + '" selected>　' + str(last_month) + '　</option>'
        for i in xrange(last_month-1):
            html += '<option value="' + str(last_month - i - 1) + '" >　' + str(last_month - i - 1) + '　</option>'
        return HttpResponse(json.write({'html': html}))

    elif 'deleteProject' == DATA.get('submit', None):
        project_id = DATA.get('project_id', 0)
        project = Project.objects.get(id=project_id)
        if not _ca(user=R.user, project=project, project_id=0, right_type_value=u'刪除管考工程案'):
            return HttpResponse(json.write({'status': False, 'message': '您並未有刪除工程案的權限!!'}))
        project.deleter = R.user
        project.save()
        return HttpResponse(json.write({'status': True}))

    elif 'recoverProject' == DATA.get('submit', None):
        project_id = DATA.get('project_id', 0)
        project = Project.objects.get(id=project_id)
        if not _ca(user=R.user, project=project, project_id=0, right_type_value=u'刪除管考工程案'):
            return HttpResponse(json.write({'status': False, 'message': '您並未有刪除工程案的權限!!'}))
        project.deleter = None
        project.save()
        return HttpResponse(json.write({'status': True}))

    elif 'addMoreFishingPort' == DATA.get('submit', None):
        if 'True' == DATA.get('inedit', None):
            fp = Project_Port(project = Project.objects.get(id=DATA.get('project_id', None)))
            fp.save()
            html = '<tr id="tr_fishingport_'+str(fp.id)+'"><td id="port_'+str(fp.id)+'" class="redaction">'
            html += '<a class="show_port_'+str(fp.id)+'">--非港區--</a>'
            html += '<select editing="port_'+str(fp.id)+'" category="ProjectBase"  class="edit_port_'+str(fp.id)+' updateRedaction" value="" old_value="" style="display: none;">'
            html += '<option value="" twdx="" twdy="">--非港區--</option>'
            for p in FishingPort.objects.all().order_by('place__id', 'name'):
                html += '<option value="'+str(p.id)+'">'+p.place.name+'_'+p.name+'</option>'
            html += '</select><img inedit="True" row_id="'+str(fp.id)+'" class="deleteFishingPort" src="/media/images/delete.png" title="刪除漁港資訊"></td></tr>'
            return HttpResponse(json.write({'status': True, 'html': html, 'port_id': fp.id}))
        else:
            num = DATA.get('num', None)
            places = [TAIWAN] + list(Place.objects.filter(uplevel=TAIWAN).order_by('id'))
            html = '<br id="br_'+str(num)+'"><select id="place_'+str(num)+'">'
            for i in places:
                html += '<option value="' + str(i.id) + '">' + i.name + '</option>'
            html += '</select>'
            html += '<span id="FishingPort_' + str(num) + '"><select id="port_' + str(num) + '"><option value="">--非港區--</option></select>'
            html += '</span><img id="delete_Port_' + str(num) + '" row_id="' + str(num) + '" class="deleteFishingPort" src="/media/images/delete.png" title="刪除漁港資訊">'
            return HttpResponse(json.write({'status': True, 'html': html}))

    elif 'deleteFishingPort' == DATA.get('submit', None):
        row_id = DATA.get('row_id', None)
        row = Project_Port.objects.get(id=row_id)
        row.delete()
        return HttpResponse(json.write({'status': True}))
