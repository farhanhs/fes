# -*- coding: utf8 -*-
from django.utils.translation import ugettext as _
from django.db import models as M

from fishuser.models import Project
from general.models import Place, Unit

from supervise.models import ErrorContent
from django.contrib.auth.models import User

import os, decimal, random
from PIL import Image
from django.conf import settings

ROOT = settings.ROOT


class Option(M.Model):
    """
       系統選單 選項列表
    """
    swarm= M.CharField(verbose_name=u'群', max_length=128)
    value = M.CharField(verbose_name=u'選項', max_length=128)

    def __unicode__(self):
        return self.value


    class Meta:
        verbose_name = u'選項'
        verbose_name_plural = u'選項'
        unique_together = (("swarm", "value"),)



class SyncLog(M.Model):
    """督導系統同步工程會標案管理系統紀錄"""
    syncdb_time = M.DateTimeField(verbose_name=u'同步時間', null=True)
    pcc_project_num = M.IntegerField(verbose_name=u'工程案數量', default=0)
    auditingcase_num = M.IntegerField(verbose_name=u'督導案數量', default=0)



class PCC_Project(M.Model):
    """標案管理系統工程紀錄"""
    pcc_no = M.CharField(verbose_name=u'標案編號', max_length=255, unique=True)
    implementation_department = M.CharField(verbose_name=u'執行機關', max_length=255, null=True)
    name = M.CharField(max_length=255, verbose_name=u'標案名稱', null=True)
    s_public_date = M.DateField(verbose_name=u'預定公告日期', null=True)
    r_decide_tenders_date = M.DateField(verbose_name=u'實際決標日期', null=True)
    contract_budget = M.FloatField(verbose_name=u'發包預算', null=True)
    decide_tenders_price = M.FloatField(verbose_name=u'決標金額', null=True)
    year = M.IntegerField(verbose_name=u'年度', null=True)
    month = M.IntegerField(verbose_name=u'月份', null=True)
    percentage_of_predict_progress = M.FloatField(verbose_name=u'預定進度', null=True)
    percentage_of_real_progress = M.FloatField(verbose_name=u'實際進度', null=True)
    percentage_of_dulta = M.FloatField(verbose_name=u'差異', null=True)



class AuditingCase(M.Model):
    """
       查核工程紀錄
    """
    date = M.DateField(verbose_name=u'查核日期')
    project = M.ForeignKey(Project, null=True)
    pcc_no = M.CharField(verbose_name=u'工程會標案編號', max_length=64)# 與標案管理系統比對之序號
    plan = M.CharField(verbose_name=u'列管計畫名稱', max_length=512)
    project_name = M.CharField(verbose_name=u'標案名稱', max_length=512)
    auditing_group = M.CharField(verbose_name=u'查核小組名稱', max_length=512, null=True)
    manage_unit = M.ForeignKey(Unit, related_name='auditingcase_manage_unit', verbose_name=u'標案所屬工程主管機關', null=True)
    unit = M.ForeignKey(Unit, related_name='auditingcase_unit', verbose_name=u'標案執行機關', null=True)
    place = M.ForeignKey(Place, related_name='auditingcase_place', verbose_name=u'縣市', null=True)
    location = M.ForeignKey(Place, related_name='auditingcase_location', verbose_name=u'行政區', null=True)
    project_manage_unit = M.CharField(verbose_name=u'專案管理單位', max_length=256, null=True)
    designer = M.CharField(verbose_name=u'設計單位', max_length=256, null=True)
    inspector = M.CharField(verbose_name=u'監造單位', max_length=256, null=True)
    construct = M.CharField(verbose_name=u'承包商', max_length=256, null=True)
    budget_price = M.IntegerField(verbose_name=u'發包預算金額', null=True, default=0)
    contract_price = M.IntegerField(verbose_name=u'契約金額', null=True, default=0)
    contract_price_change = M.IntegerField(verbose_name=u'變更設計後', null=True, default=0)
    info = M.TextField(verbose_name=u'工程概要')
    progress = M.TextField(verbose_name=u'工程進度、經費支用及目前施工概況', null=True)
    supervisors_outside = M.CharField(verbose_name=u'查核人員(外聘)', max_length=256, null=True)
    supervisors_inside = M.CharField(verbose_name=u'查核人員(內聘)', max_length=256, null=True)
    captain = M.CharField(verbose_name=u'領隊', max_length=256, null=True)
    workers = M.CharField(verbose_name=u'工作人員', max_length=256, null=True)
    start_date = M.DateField(verbose_name=u'開工日期', null=True)
    expected_completion_date = M.DateField(verbose_name=u'預計完工日期', null=True)
    expected_completion_date_change = M.DateField(verbose_name=u'預計完工日期變更後', null=True)
    score = M.DecimalField(verbose_name=u'查核分數', max_digits=5, decimal_places=2)
    merit = M.TextField(verbose_name=u'優點', null=True)
    advise = M.TextField(verbose_name=u'規劃設計問題及建議')
    quality_indicators = M.TextField(verbose_name=u'品質指標')
    other_advise = M.TextField(verbose_name=u'其他建議')
    memo = M.TextField(verbose_name=u'備註', null=True)
    deduction_i_point = M.IntegerField(verbose_name=u'監造扣點', default=0)
    deduction_c_point = M.IntegerField(verbose_name=u'施工扣點', default=0)
    test = M.TextField(verbose_name=u'檢驗拆驗')

    def __unicode__(self):
        return '%s(%s)' % (self.pcc_no, self.date)

    class Meta:
        unique_together = (("project", "date"),)


class Error(M.Model):
    """查核工程案缺失"""
    case = M.ForeignKey(AuditingCase)
    errorcontent = M.ForeignKey(ErrorContent, related_name='auditing_errorcontent', null=True)
    context = M.CharField(verbose_name=u'缺失內容', max_length=1024)

    def __unicode__(self):
        return self.errorcontent.no


    class Meta:
        verbose_name = u'缺失項目'
        verbose_name_plural = u'缺失項目'
        