# -*- coding:utf8 -*-
from django.db import models as M
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.contrib.sessions.models import Session

from fishuser.models import Option
from fishuser.models import UserProfile
from fishuser.models import LoginHistory
from fishuser.models import WrongLogin
from fishuser.models import DocumentOfProjectModels
from fishuser.models import Plan
from fishuser.models import PlanBudget
from fishuser.models import Project
from fishuser.models import Project_Port
from fishuser.models import DefaultProject
from fishuser.models import FRCMUserGroup
from fishuser.models import Factory
from fishuser.models import Reserve
from fishuser.models import FundRecord
from fishuser.models import Fund
from fishuser.models import BudgetProject
from fishuser.models import Appropriate
from fishuser.models import Progress
from fishuser.models import ScheduledProgress
from fishuser.models import ProjectPhoto
from fishuser.models import FRCMTempFile
from fishuser.models import _getProjectStatusInList
from fishuser.models import _ca
from harbor.models import FishingPort

import datetime
import os
from PIL import Image
import decimal

""" 匯出工程案的自定報表的流程，以使用者角度來說明：

    使用者在「搜尋管考工程」頁面，進行搜尋後，將「欲觀看之工程案」紀錄至「特定紀錄中」，
    勾選後，再選擇以「特定報表」作匯出。

"""


class Option2(M.Model):
    """ 因為 project.option 的名字已經被 fishuser.option 給搶走了，
        所以只好用 Option2 來命名
    """
    swarm= M.CharField(verbose_name=u'群', max_length=128)
    value = M.CharField(verbose_name=u'選項', max_length=128)

    def __unicode__(self):
        return self.value


    class Meta:
        verbose_name = u'選項'
        verbose_name_plural = u'選項'
        unique_together = (("swarm", "value"),)


class RecordProjectProfile(M.Model):
    name = M.CharField(verbose_name=u'名稱', max_length=64)
    owner = M.ForeignKey(User, verbose_name=u'使用者')
    projects = M.ManyToManyField(Project, verbose_name=u'紀錄工程案')
    create_time = M.DateTimeField(verbose_name=u'創建時間', auto_now_add=True)


class ReportField(M.Model):
    tag = M.ForeignKey(Option2)
    name = M.CharField(verbose_name=u'名稱', max_length=128)
    value_method = M.CharField(verbose_name=u'取值方式', max_length=256)

    def rValue(self, object):
        self.object = object
        return eval(self.value_method)


    class Meta:
        unique_together = (('tag', 'name'), )


class ExportCustomReport(M.Model):
    name = M.CharField(verbose_name=u'名稱', max_length=64)
    owner = M.ForeignKey(User, verbose_name=u'使用者')
    fields = M.ManyToManyField(ReportField, verbose_name=u'自定欄位', through='ExportCustomReportField') 
    create_time = M.DateTimeField(verbose_name=u'創建時間', auto_now_add=True)


class ExportCustomReportField(M.Model):
    export_custom_report = M.ForeignKey(ExportCustomReport)
    report_field = M.ForeignKey(ReportField)
    priority = M.IntegerField(verbose_name=u'優先權')
