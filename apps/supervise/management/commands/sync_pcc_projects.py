# -*- coding: utf-8 -*-
import sys, os, random, json, re, datetime, math, smtplib, decimal, xlsxwriter, calendar
from os import makedirs
from os.path import join, exists, basename
from io import StringIO

from django.db.models import Q, Sum
from optparse import make_option
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Group, Permission
from django.conf import settings

from fishuser.models import CountyChaseTime
from supervise.models import *
from pccmating.models import Project as PCCProject
from pccmating.sync import getAllWorkingProjectInfo, getNoProgressProjectInfo
from pccmating.sync import getProjectInfo
import time

def TODAY(): return datetime.date.today()

def NOW(): return datetime.datetime.now()
  
class Command(BaseCommand):
    help = u'export 同步工程會在建工程'

    def handle(self, *args, **kw):
        #取得所有在建工程資訊
        content = getAllWorkingProjectInfo()
        #取出table
        table_start_seed = re.search(u"<TABLE", content).start()
        table_end_seed = re.search(u"</TABLE>", content).end()
        content = content[table_start_seed:table_end_seed]

        #取出欄位名稱
        first_tr_start_seed = re.search(u"<TR>", content).start()
        first_tr_end_seed = re.search(u"</TR>", content).end()
        first_tr = content[first_tr_start_seed:first_tr_end_seed]
        first_tr = first_tr.split(u'<TD')
        field_names = []
        for td in first_tr:
            td = td.replace('<TR>', '')
            if u'</TD>' in td:
                start_td_seed = re.search(u">", td).end()
                end_td_seed = re.search(u"</TD>", td).start()
                field_names.append(td[start_td_seed:end_td_seed].replace(u'<font size=-1>', '').replace(u'<font color=gray>', '').replace(u'<br>', '').replace(u'</font>', '').replace(u'(督導)', '').replace(u' ', ''))
        field_names.pop(0)

        #分解每一列tr
        data_trs = []
        content = content[first_tr_end_seed:]
        while u'<TR>' in content:
            tr_start_seed = re.search(u"<TR>", content).start()
            tr_end_seed = re.search(u"</TR>", content).end()
            data_trs.append(content[tr_start_seed: tr_end_seed])
            content = content[tr_end_seed:]

        #解析tr，整理內容資料
        data = []
        for tr in data_trs:
            tr = re.split('<TD' , tr)
            tmp = []
            for n_td, td in enumerate(tr[2:]):
                td_content_start_seed = re.search(u">", td).end()
                td_content_end_seed = re.search(u"</TD>", td).start()
                td = td[td_content_start_seed:td_content_end_seed]
                td = td.replace('<font size=-1>', '').replace('<font color=gray>', '').replace('<font color=red>', '')
                td = td.replace('</font>', '')
                td = td.replace(' ', '').replace('\n', '').replace('&nbsp', '')
                tmp.append(td)
                front_td = tr[2:][n_td-1]
                if 'COLSPAN=' in front_td:
                    colspan_num_seed = re.search(u"COLSPAN=", front_td).end()
                    colspan_num = front_td[colspan_num_seed]
                    if int(colspan_num) != 1:
                        for i in range(int(colspan_num)-1):
                            tmp.append(None)

            data.append(tmp)

        field_mapping = {}
        for field in PCCProject()._meta.fields:
            field_mapping[field.verbose_name] = field.name

        chase = CountyChaseTime.objects.all().order_by('-id').first()
        records = chase.countychaseprojectonetomany_set.filter(complete=False)
        #匯入到pccmating Project
        on_pcc_ids = []
        for d in data:
            try: 
                pcc_project, created = PCCProject.objects.get_or_create(uid=d[field_names.index(u'編號')])
                if created:
                    try:
                        extr = getProjectInfo(pcc_project.uid)
                        time.sleep(15)
                    except: pass

                pcc_project.on_pcc_now = True
                on_pcc_ids.append(pcc_project.uid)
                for k, v in enumerate(d):
                    # 欄位中文名稱 field_names[k]
                    # 欄位英文名稱 field_mapping[field_names[k]]
                    if v and field_names[k] in field_mapping:
                        field_type = PCCProject()._meta.get_field(field_mapping[field_names[k]]).get_internal_type()
                        if 'DateField' in field_type:
                            try:
                                v = datetime.datetime(int(v[:3]) + 1911, int(v[3:5]), int(v[5:]))
                            except:
                                v = None
                        if 'FloatField' in field_type or 'IntegerField' in field_type:
                            try:
                                v = float(v.replace(',', '').replace('/', '').replace('%', ''))
                            except:
                                v = 0

                        setattr(pcc_project, field_mapping[field_names[k]], v)
                try:
                    pcc_project.percentage_of_dulta = pcc_project.percentage_of_real_progress - pcc_project.percentage_of_predict_progress
                except: pass
                pcc_project.lastsync = NOW()
                pcc_project.save()

                #自動更新進度追蹤
                for r in records.filter(project__pcc_no=pcc_project.uid):
                    print r.project.id, '---------'
                    r.memo = pcc_project.r_executive_summary
                    r.behind_memo = u'%s\n%s\n%s' % (pcc_project.delay_factor or u'', pcc_project.delay_reason or u'', pcc_project.delay_solution or u'') 
                    r.schedul_progress_percent = pcc_project.percentage_of_predict_progress
                    r.actual_progress_percent = pcc_project.percentage_of_real_progress
                    r.save()
            except: pass


        #移除目前不再PCC上的工程標註
        for p in PCCProject.objects.filter(on_pcc_now=True).exclude(uid__in=on_pcc_ids):
            p.on_pcc_now = False
            p.save()









        #取得所有 進度未填清單-含剛決標或未開工案件
        content = getNoProgressProjectInfo()
        #取出table
        table_start_seed = re.search(u"<TABLE", content).start()
        table_end_seed = re.search(u"</TABLE>", content).end()
        content = content[table_start_seed:table_end_seed]

        #取出欄位名稱
        first_tr_start_seed = re.search(u"<TR>", content).start()
        first_tr_end_seed = re.search(u"</TR>", content).end()
        first_tr = content[first_tr_start_seed:first_tr_end_seed]
        first_tr = first_tr.split(u'<TH')
        field_names = []
        for td in first_tr:
            td = td.replace('<TR>', '')
            if '</TH>' in td:
                start_td_seed = re.search(u">", td).end()
                end_td_seed = re.search(u"</TH>", td).start()
                field_names.append(td[start_td_seed:end_td_seed].replace(u'<font size=-1>', '').replace(u'<font color=gray>', '').replace(u'<br>', '').replace(u'</font>', '').replace(u'(督導)', '').replace(u' ', '').replace(u'(千元)', ''))
        field_names.pop(0)

        #分解每一列tr
        data_trs = []
        content = content[first_tr_end_seed:]
        while u'<TR>' in content:
            tr_start_seed = re.search(u"<TR>", content).start()
            tr_end_seed = re.search(u"</TR>", content).end()
            data_trs.append(content[tr_start_seed: tr_end_seed])
            content = content[tr_end_seed:]

        #解析tr，整理內容資料
        data = []
        for tr in data_trs:
            tr = re.split('<TD' , tr)
            tmp = []
            for n_td, td in enumerate(tr[2:]):
                td_content_start_seed = re.search(u">", td).end()
                td_content_end_seed = re.search(u"</TD>", td).start()
                td = td[td_content_start_seed:td_content_end_seed]
                td = td.replace('<font size=-1>', '').replace('<font color=gray>', '').replace('<font color=red>', '')
                td = td.replace('<font color=maroon>', '').replace('<font color=olive>', '').replace('<font color=olive>', '')
                td = td.replace('</font>', '')
                td = td.replace(' ', '').replace('\n', '').replace('&nbsp', '')
                tmp.append(td)
                front_td = tr[2:][n_td-1]
                if 'COLSPAN=' in front_td:
                    colspan_num_seed = re.search(u"COLSPAN=", front_td).end()
                    colspan_num = front_td[colspan_num_seed]
                    if int(colspan_num) != 1:
                        for i in range(int(colspan_num)-1):
                            tmp.append(None)

            data.append(tmp)

        field_mapping = {}
        for field in PCCProject()._meta.fields:
            field_mapping[field.verbose_name] = field.name

    
        #匯入到pccmating Project
        on_pcc_ids = []
        for d in data:
            try: 
                pcc_project, created = PCCProject.objects.get_or_create(uid=d[field_names.index(u'編號')])
                if created:
                    try:
                        extr = getProjectInfo(pcc_project.uid)
                        time.sleep(15)
                    except: pass

                pcc_project.on_pcc_now = True
                on_pcc_ids.append(pcc_project.uid)
                for k, v in enumerate(d):
                    # 欄位中文名稱 field_names[k]
                    # 欄位英文名稱 field_mapping[field_names[k]]
                    # print field_names[k], k, v
                    if v and field_names[k] in field_mapping:
                        field_type = PCCProject()._meta.get_field(field_mapping[field_names[k]]).get_internal_type()
                        if u'進度月份' == field_names[k]:
                            setattr(pcc_project, 's_executive_summary', v)
                            setattr(pcc_project, 'r_executive_summary', v)

                        if 'DateField' in field_type:
                            try:
                                v = datetime.datetime(int(v[:3]) + 1911, int(v[3:5]), int(v[5:]))
                            except:
                                v = None
                        if 'FloatField' in field_type or 'IntegerField' in field_type:
                            try:
                                v = float(v.replace(',', '').replace('/', '').replace('%', ''))
                            except:
                                v = 0
                                
                        if u'決標金額' == field_names[k] and v:
                            v *= 1000

                        setattr(pcc_project, field_mapping[field_names[k]], v)

                try:
                    pcc_project.percentage_of_dulta = pcc_project.percentage_of_real_progress - pcc_project.percentage_of_predict_progress
                except: pass
                pcc_project.lastsync = NOW()
                pcc_project.save()

            except: pass