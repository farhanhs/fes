# -*- coding: utf-8 -*-
import sys

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Group, Permission
from django.conf import settings


from auditing.models import Option, AuditingCase, Error, PCC_Project
from supervise.models import ErrorContent
from fishuser.models import Project
from general.models import Place, Unit
from pccmating.sync import *

import decimal
import calendar
import os, random, json, re, datetime, math
from time import time

TAIWAN = Place.objects.get(name=u'臺灣地區')
places = Place.objects.filter(uplevel=TAIWAN).order_by('id')
locations = Place.objects.filter(uplevel__in=places)


class Command(BaseCommand):
    help = 'Sync Pcc Auditing data'


    def handle(self, *args, **kw):
        t0 = time()
        # 同步所有的工程案列表
        projects_list = getAllOldProject()
        ids = []
        for n, p in enumerate(projects_list):
            try:
                row = PCC_Project.objects.get(pcc_no=p[u'編號'])
            except:
                row = PCC_Project(pcc_no=p[u'編號'])
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
            row.percentage_of_dulta = round(float(row.percentage_of_predict_progress) - float(row.percentage_of_real_progress), 2)
            row.save()
            ids.append(row.id)
        PCC_Project.objects.all().exclude(id__in=ids).delete()
        print time() - t0

        #取得所有查核紀錄並同步到資料庫
        for n, p in enumerate(PCC_Project.objects.all()):
            print n, ',', p.pcc_no, ':', 
            try:
                auditing_date = syncPccAuditingDate(pcc_no=p.pcc_no)
                for record in auditing_date:
                    [date, auditing_group] = record
                    print date,
                    result = syncPccAuditingInformation(date=date, pcc_no=p.pcc_no)
                    try:
                        row = AuditingCase.objects.get(pcc_no=p.pcc_no, date=date)
                    except:
                        row = AuditingCase(pcc_no=p.pcc_no, date=date)

                    row.plan = result['plan']
                    row.auditing_group = auditing_group
                    row.project_name = result['project_name']
                    try:
                        manage_unit = Unit.objects.filter(name=result['manage_unit'])[0]
                    except:
                        manage_unit = Unit(
                                        name = result['manage_unit'],
                                        fullname = result['manage_unit'],
                                        no = 'tem%@&!',
                                        place = Place.objects.get(name='臺灣地區')
                                        )
                        manage_unit.save()
                        manage_unit.no = str(100000000 + manage_unit.id)[1:]
                        manage_unit.save()
                    row.manage_unit = manage_unit
                    try:
                        unit = Unit.objects.filter(name=result['manage_unit'])[0]
                    except:
                        unit = Unit(
                                name = result['unit'],
                                fullname = result['unit'],
                                no = 'tem%@&!',
                                place = Place.objects.get(name='臺灣地區')
                                )
                        unit.save()
                        unit.no = str(100000000 + unit.id)[1:]
                        unit.save()
                    row.unit = unit
                    try:
                        row.place = places.get(name=result['place'])
                    except:
                        row.place = None
                    try:
                        row.location = Place.objects.filter(name=result['location'])[0]
                    except:
                        row.location = None
                    row.project_manage_unit = result['project_manage_unit']
                    row.designer = result['designer']
                    row.inspector = result['inspector']
                    row.construct = result['construct']
                    row.budget_price = int(result['budget_price']) * 1000
                    row.contract_price = int(result['contract_price']) * 1000
                    row.contract_price_change = int(result['contract_price_change']) * 1000 if result['contract_price_change'] else 0
                    row.info = result['info']
                    row.progress = result['progress']
                    row.supervisors_outside = result['supervisors_outside']
                    row.supervisors_inside = result['supervisors_inside']
                    row.captain = result['captain']
                    row.workers = result['workers']
                    row.start_date = result['start_date']
                    row.expected_completion_date = result['expected_completion_date']
                    row.expected_completion_date_change = result['expected_completion_date_change']
                    row.score = str(result['score'])
                    row.merit = result['merit']
                    row.advise = result['advise']
                    row.quality_indicators = result['quality_indicators']
                    row.other_advise = result['other_advise']
                    row.deduction_i_point = result['deduction_i_point']
                    row.deduction_c_point = result['deduction_c_point']
                    row.test = result['test']
                    row.save()

                    Error.objects.filter(case=row).delete()
                    errors = result['errors'].split('<br>')
                    for e in errors:
                        if re.search(u'<font size=-1>', e):
                            seek = re.search(u'<font size=-1>', e).start()
                            context = e[:seek].replace(' ', '').replace('\n', '')
                            context = '.'.join(context.split('.')[1:])
                            e = e[seek+14:]
                            seek = re.search(u'<', e).start()
                            no = e[:seek].replace('(', '').replace(')', '')
                            try:
                                errorcontent = ErrorContent.objects.get(no=no)
                            except:
                                errorcontent = None
                            error = Error(
                                case=row,
                                errorcontent=errorcontent,
                                context=context
                                )
                            error.save()
            except: pass
            print 'done'
        print time() - t0