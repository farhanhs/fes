# -*- coding:utf-8 -*-
from django.utils.translation import ugettext as _
from django.db import models as M
from django.db.models import Q
from django.db.models import F
from django.db.models import Sum
from django.db.models import Max
from django.db.models import Min
from django.db.utils import DatabaseError
from django.db.models.signals import post_init, post_save, post_delete

from django.contrib.auth.models import User, Group
from project.models import Project, FRCMUserGroup

from dailyreport.lib import readDateRange
from dailyreport.lib import WorkingDate
from dailyreport.lib import updateFirstWordByUpper

import datetime, decimal
from guardian.shortcuts import assign, get_perms, remove_perm

from random import random
import datetime
import time
import re
import os.path, math, calendar
from xml.dom import minidom
from xml.dom import Node
from types import IntType, LongType
from django.conf import settings

def TODAY(): return datetime.date.today()

def NOW(): return datetime.datetime.now()

#設定群組名稱
MAJOR_ENGINEER_NAME = u'負責主辦工程師'
MAJOR2_ENGINEER_NAME = u'自辦主辦工程師'
MINOR_ENGINEER_NAME = u'協同主辦工程師'
INSPECTOR_NAME = u'監造廠商'
CONTRACTOR_NAME = u'營造廠商'

try: MAJOR_ENGINEER = Group.objects.get(name=MAJOR_ENGINEER_NAME)
except DatabaseError: MAJOR_ENGINEER = False
except Group.DoesNotExist: MAJOR_ENGINEER = False

try: MAJOR2_ENGINEER = Group.objects.get(name=MAJOR2_ENGINEER_NAME)
except DatabaseError: MAJOR2_ENGINEER = False
except Group.DoesNotExist: MAJOR2_ENGINEER = False

try: MINOR_ENGINEER = Group.objects.get(name=MINOR_ENGINEER_NAME)
except DatabaseError: MINOR_ENGINEER = False
except Group.DoesNotExist: MINOR_ENGINEER = False

try: INSPECTOR = Group.objects.get(name=INSPECTOR_NAME)
except DatabaseError: INSPECTOR = False
except Group.DoesNotExist: INSPECTOR = False

try: CONTRACTOR = Group.objects.get(name=CONTRACTOR_NAME)
except DatabaseError: CONTRACTOR = False
except Group.DoesNotExist: CONTRACTOR = False

DR_PERMISSIONS = {
    MAJOR_ENGINEER_NAME: [
        'edit_engprofile', 'view_engprofile',
        'view_contractor_report',
        'edit_inspector_report', 'view_inspector_report',
        'edit_special_date', 'view_special_date',
        'edit_schedule_item', 'view_schedule_item',
        'edit_item', 'view_item',
    ],
    MAJOR2_ENGINEER_NAME: [
        'edit_engprofile', 'view_engprofile',
        'view_contractor_report',
        'edit_inspector_report', 'view_inspector_report',
        'edit_special_date', 'view_special_date',
        'edit_schedule_item', 'view_schedule_item',
        'edit_item', 'view_item',
    ],
    MINOR_ENGINEER_NAME: [
        'edit_engprofile', 'view_engprofile',
        'view_contractor_report',
        'edit_inspector_report', 'view_inspector_report',
        'edit_special_date', 'view_special_date',
        'edit_schedule_item', 'view_schedule_item',
        'edit_item', 'view_item',
    ],
    INSPECTOR_NAME: [
        'edit_engprofile', 'view_engprofile',
        'view_contractor_report',
        'edit_inspector_report', 'view_inspector_report',
        'edit_special_date', 'view_special_date',
        'edit_schedule_item', 'view_schedule_item',
        'edit_item', 'view_item',
    ],
    CONTRACTOR_NAME: [
        'edit_engprofile', 'view_engprofile',
        'edit_contractor_report', 'view_contractor_report',
        'view_inspector_report',
        'view_special_date',
        'edit_schedule_item', 'view_schedule_item',
        'edit_item', 'view_item',
    ],
}

ALL_PERMISSIONS = [(p, p) for p in set(DR_PERMISSIONS[MAJOR_ENGINEER_NAME]+
                                    DR_PERMISSIONS[MINOR_ENGINEER_NAME]+
                                    DR_PERMISSIONS[INSPECTOR_NAME]+
                                    DR_PERMISSIONS[CONTRACTOR_NAME])]


def update_permission_with_rcmup(sender, instance=False, **kwgs):
    rup = instance
    if rup.is_active:
        user = rup.user
        try:
            engprofile = rup.project.dailyreport_engprofile.get()
        except EngProfile.DoesNotExist:
            engprofile = EngProfile()
            engprofile.setDefaultEngProfile(project=rup.project)
            engprofile.create_root_item()

        group = rup.group
        now_perms = get_perms(user, engprofile)
        for perm in DR_PERMISSIONS[group.name]:
            assign(perm, user, engprofile)
            if perm in now_perms: now_perms.remove(perm)
        for perm in now_perms:
            remove_perm(perm, user, engprofile)
    else:
        user = rup.user
        try:
            engprofile = rup.project.dailyreport_engprofile.get()
        except EngProfile.DoesNotExist:
            pass
        else:
            for perm in get_perms(user, engprofile):
                remove_perm(perm, user, engprofile)

post_save.connect(update_permission_with_rcmup, sender=FRCMUserGroup)


def delete_permission_with_rcmup(sender, instance=False, **kwgs):
    rup = instance
    if rup:
        user = rup.user
        try:
            engprofile = rup.project.dailyreport_engprofile.get()
        except EngProfile.DoesNotExist:
            pass
        else:
            for perm in get_perms(user, engprofile):
                remove_perm(perm, user, engprofile)

post_delete.connect(delete_permission_with_rcmup, sender=FRCMUserGroup)



class Option(M.Model):
    swarm= M.CharField(verbose_name='群', max_length=32)
    value = M.CharField(verbose_name='選項', max_length=64)

    def __unicode__(self):
        return '%s-%s' % (self.swarm, self.value)

    class Meta:
        verbose_name = u'選項'
        verbose_name_plural = u'選項'
        unique_together = (("swarm", "value"),)


try:
    DIR_ROUND = Option.objects.get(swarm='round_type', value=u'目錄四捨五入')
    ALL_ROUND = Option.objects.get(swarm='round_type', value=u'總價四捨五入')
    ITEM_ROUND = Option.objects.get(swarm='round_type', value=u'項目四捨五入')
except:
    DIR_ROUND = False
    ALL_ROUND = False
    ITEM_ROUND = False

try: DIRKIND = Option.objects.get(swarm='item_kind', value=u'目錄')
except: DIRKIND = False

try: ITEMKIND = Option.objects.get(swarm='item_kind', value=u'工項')
except: ITEMKIND = False

try: NONITEMKIND = Option.objects.get(swarm='item_kind', value=u'非工項')
except: NONITEMKIND = False

try: LABOR_TYPE = Option.objects.get(swarm='labor_or_equip', value=u'人員')
except: LABOR_TYPE = False

try: EQUIP_TYPE = Option.objects.get(swarm='labor_or_equip', value=u'機具')
except: EQUIP_TYPE = False



class Holiday(M.Model):
    name = M.CharField(verbose_name=u'名稱', max_length=256)
    date = M.DateField(verbose_name=u'日期')


    def __unicode__(self):
        return self.name

    class Meta:
        pass



class Version(M.Model):
    # 版本
    project = M.ForeignKey(Project, related_name='dailyreport_version')
    start_date = M.DateField(verbose_name=u'版本起始日期', null=True)
    engs_price = M.DecimalField(verbose_name=u'該版本契約總價', max_digits=16, decimal_places=4)
    schedule_price = M.DecimalField(verbose_name=u'該版本進度總價', max_digits=16, decimal_places=4)
    pre_act_percent = M.DecimalField(verbose_name=u'前版本與「本版本 start_date 」的實際進度', default=decimal.Decimal('0'), max_digits=5, decimal_places=2)
    pre_design_percent = M.DecimalField(verbose_name=u'前版本在「本版本 start_date 」的預定進度', default=decimal.Decimal('0'), max_digits=5, decimal_places=2)
    update_time = M.DateTimeField(verbose_name=u'最後更新時間', auto_now=True, null=True)
    pre_i_money = M.DecimalField(verbose_name=u'前版本s對於此版本工項的監造累積金額', default=decimal.Decimal('0'), max_digits=16, decimal_places=3)
    pre_c_money = M.DecimalField(verbose_name=u'前版本s對於此版本工項的施工累積金額', default=decimal.Decimal('0'), max_digits=16, decimal_places=3)
    

    class Meta:
        get_latest_by = 'start_date'
        #unique_together = (("project", "start_date"),)


    def __unicode__(self):
        return '%s(%s)' % (self.project.name, self.start_date)


    def read_pre_version(self):
        #回傳上一個版本
        try:
            return Version.objects.filter(project=self.project, start_date__lt=self.start_date).order_by('-start_date')[0]
        except:
            return False

    def read_next_version(self):
        #回傳下一個版本
        try:
            return Version.objects.filter(project=self.project, start_date__gt=self.start_date).order_by('start_date')[0]
        except:
            return False

    def read_report_days(self):
        #回傳這個版本共填報了幾天
        reports = Report.objects.filter(project=self.project, date__gte=self.start_date)
        if self.read_next_version():
            reports = reports.filter(date__lt=self.read_next_version().start_date)

        return reports.count()

    def read_engs_price(self):
        #回傳該版本契約總價
        root_item = Item.objects.get(version=self, uplevel=None)
        return root_item.read_dir_price_by_roundkind()

    def read_schedule_price(self):
        #回傳該版本預定進度總價
        root_item = ScheduleItem.objects.get(version=self, uplevel=None)
        return root_item.read_dir_price()

    def new_version_copy_pre_item(self, *args, **kw):
        #新增變更設計複製前一個版本的資訊

        pre_version = self.project.dailyreport_version.filter(start_date__lt=self.start_date).latest()
        if not pre_version:
            return False

        #複製Item
        pre_root_item = Item.objects.get(version=pre_version, uplevel=None)
        next_round = [pre_root_item]
        def create_next_item(next_round):
            tmp_next_round = []
            for item in next_round:
                if item.uplevel:
                    uplevel = Item.objects.get(version=self, pre_item=item.uplevel)
                else:
                    uplevel = None
                new_item = Item(version=self, name=item.name, unit_name=item.unit_name, unit_num=item.unit_num,
                    unit_price=item.unit_price, pre_item=item,
                    kind=item.kind, uplevel=uplevel, priority=item.priority, memo=item.memo)
                new_item.save()
                for i in item.read_sub_item_in_list():
                    tmp_next_round.append(i)
            if tmp_next_round: create_next_item(tmp_next_round)
        create_next_item(next_round)
        
        #複製ScheduleItem
        pre_root_schedule_item = ScheduleItem.objects.get(version=pre_version, uplevel=None)
        next_round = [pre_root_schedule_item]
        def create_next_schedule_item(next_round):
            tmp_next_round = []
            for item in next_round:
                if item.uplevel:
                    uplevel = ScheduleItem.objects.get(version=self, pre_item=item.uplevel)
                else:
                    uplevel = None
                new_item = ScheduleItem(version=self, name=item.name, unit_name=item.unit_name, unit_num=item.unit_num,
                    unit_price=item.unit_price, pre_item=item, es=item.es, ef=item.ef,
                    kind=item.kind, uplevel=uplevel, priority=item.priority)
                new_item.save()
                for i in item.read_sub_item_in_list():
                    tmp_next_round.append(i)
            if tmp_next_round: create_next_schedule_item(tmp_next_round)
        create_next_schedule_item(next_round)

        #切換變更設計日期之後的item紀錄
        for ri in ReportItem.objects.filter(report__project=self.project, report__date__gte=self.start_date):
            ri.item = Item.objects.get(pre_item=ri.item)
            ri.save()

        return True



class Item(M.Model):
    # 日報表工項
    version = M.ForeignKey(Version)
    name = M.CharField(verbose_name=u'項目名稱', null=True, max_length=255)
    unit_name = M.CharField(verbose_name=u'單位', default='---', max_length=16)
    unit_num = M.DecimalField(verbose_name=u'設計數量', default=decimal.Decimal('1'), max_digits=16 , decimal_places=3)
    unit_price = M.DecimalField(verbose_name=u'單價', default=decimal.Decimal('0'), max_digits=16 , decimal_places=4)
    kind = M.ForeignKey(Option, verbose_name=u'工項種類', related_name='kind_item', default=11)
    uplevel = M.ForeignKey('self', null=True, related_name='item_uplevel')
    pre_item = M.ForeignKey('self', null=True, related_name='item_pre_item', verbose_name=u'前一個版本是誰')
    priority = M.IntegerField(verbose_name=u'優先權值')
    memo = M.TextField(verbose_name=u'備註', null=True, default='')

    class Meta:
        verbose_name = u'工程項目'
        verbose_name_plural = u'工程項目'
        permissions = (
            ('edit_item', 'Edit Item'),
            ('view_item', 'View Item'),
        )


    def __unicode__(self):
        return self.name


    def sum_price(self):
        #回傳 數量*單價
        if self.version.project.dailyreport_engprofile.get().round_type == ITEM_ROUND:
            return round(self.unit_num * self.unit_price)
        else:
            return self.unit_num * self.unit_price

    def read_brother_items(self):
        #回傳每個版本的相同工項
        items = [self]
        target = self
        while target.pre_item:
            items.append(target.pre_item)
            target = target.pre_item
        target = self
        while Item.objects.filter(pre_item=target):
            items.append(Item.objects.get(pre_item=target))
            target = Item.objects.get(pre_item=target)
        return items

    def read_sub_item_in_list(self):
        #回傳自己工項本身的子工項，針對DIRKIND使用
        return Item.objects.filter(uplevel=self).order_by('priority').prefetch_related('version', 'kind', 'uplevel', 'pre_item')

    def read_deep_sub_item_in_list(self):
        #回傳自己工項本身的子工項(包括工項的子工項)，針對DIRKIND使用
        items = [self]
        def readScheduleItemInlist(items, check_item):
            for i in check_item.read_sub_item_in_list():
                items.append(i)
                items = readScheduleItemInlist(items, i)
            return items

        items = readScheduleItemInlist(items, self)

        return items

    def read_level_num(self):
        #回傳是第幾階層的工項
        num = 0
        row = self
        while row.uplevel:
            num += 1
            row = row.uplevel
        return num

    def read_level_symbol(self):
        #回傳自己的項次，例如1.2.5
        symbol = str(self.priority + 1)
        row = self
        while row.uplevel:
            symbol = str(row.uplevel.priority + 1) + '.' + symbol
            row = row.uplevel

        return symbol[2:]

    def read_last_item(self):
        # 回傳下層裡面最後一個排序工項
        if Item.objects.filter(uplevel=self).order_by('-priority'):
            return Item.objects.filter(uplevel=self).order_by('-priority')[0]
        else:
            return Item(priority=-1, kind=Option())


    def read_dir_price_by_roundkind(self):
        #計算這個項目下的總計金額，針對DIRKIND所使用
        if self.kind != DIRKIND:
            return self.unit_price * self.unit_num

        dir_items = [self]
        def readDirItemInlist(items, check_item):
            for i in check_item.read_sub_item_in_list():
                if i.kind == DIRKIND:
                    items.append(i)
                    items = readDirItemInlist(items, i)
            return items

        items = readDirItemInlist(dir_items, self)
        items.reverse()
        if self.version.project.dailyreport_engprofile.get().round_type == ITEM_ROUND:
            #如果是項目四捨五入，則每一個項目四捨五入後再加
            for i in items:
                i.unit_price = sum([round(j.unit_price*j.unit_num) for j in Item.objects.filter(uplevel=i)])
                if i.kind == DIRKIND: i.unit_num = 1 #作保險，不知道為啥會出現數量為0，明明預設是1
                i.save()
            return float(items[-1].unit_price)
        elif self.version.project.dailyreport_engprofile.get().round_type == DIR_ROUND:
            #如果是目錄四捨五入，則加完後再四捨五入
            for i in items:
                i.unit_price = round(sum([j.unit_price*j.unit_num for j in Item.objects.filter(uplevel=i)]))
                if i.kind == DIRKIND: i.unit_num = 1 #作保險，不知道為啥會出現數量為0，明明預設是1
                i.save()
            return float(int(items[-1].unit_price))
        elif self.version.project.dailyreport_engprofile.get().round_type == ALL_ROUND:
            #如果是總價四捨五入，則加完後，判斷是不是root_item再四捨五入
            for i in items:
                i.unit_price = sum([j.unit_price*j.unit_num for j in Item.objects.filter(uplevel=i)])
                if i.kind == DIRKIND: i.unit_num = 1 #作保險，不知道為啥會出現數量為0，明明預設是1
                i.save()
            if not items[-1].uplevel:
                items[-1].unit_price = round(sum([j.unit_price*j.unit_num for j in Item.objects.filter(uplevel=items[-1])]))
                items[-1].save()
                return int(items[-1].unit_price)
            return float(items[-1].unit_price)

    def read_dir_price_by_realprice(self):
        #計算這個項目下的實際總計金額，針對DIRKIND所使用
        if self.kind != DIRKIND:
            return float(str(self.unit_price)) * float(str(self.unit_num))

        price = 0
        items = self.read_deep_sub_item_in_list()

        if self.version.project.dailyreport_engprofile.get().round_type == ITEM_ROUND:
            #如果是項目四捨五入，則每一個項目四捨五入後再加
            for i in items:
                if i.kind != DIRKIND:
                    price += round(i.unit_price*i.unit_num)
            return price
        elif self.version.project.dailyreport_engprofile.get().round_type == DIR_ROUND:
            #如果是目錄四捨五入，則加完後再四捨五入
            for i in items:
                if i.kind != DIRKIND:
                    price += i.unit_price*i.unit_num
            return round(price)
        elif self.version.project.dailyreport_engprofile.get().round_type == ALL_ROUND:
            #如果是總價四捨五入，則加完後，判斷是不是root_item再四捨五入
            for i in items:
                if i.kind != DIRKIND:
                    price += i.unit_price*i.unit_num
            return price


    def read_top_dir_in_list(self):
        # 回傳本身工項往上追到ROOT_DIR的路徑(倒著追)，例如 .5.2.1
        ids = ''
        row = self
        while row.uplevel:
            ids += '.' + str(row.uplevel.id)
            row = row.uplevel

        return ids



class ScheduleItem(M.Model):
    # 預計進度工項
    version = M.ForeignKey(Version)
    name = M.CharField(verbose_name=u'項目名稱', null=True, max_length=256)
    unit_name = M.CharField(verbose_name=u'單位', default='---', max_length=16)
    unit_num = M.DecimalField(verbose_name=u'設計數量', default=decimal.Decimal('1') , max_digits=16 , decimal_places=3)
    unit_price = M.DecimalField(verbose_name=u'價格', default=decimal.Decimal('0'), max_digits=16 , decimal_places=4)
    es = M.IntegerField(verbose_name=u'開始日期', default=1)
    ef = M.IntegerField(verbose_name=u'結束日期', default=1)
    kind = M.ForeignKey(Option, verbose_name=u'工項種類', related_name='kind_scheduleitem', default=11)
    uplevel = M.ForeignKey('self', null=True, related_name='scheduleitem_uplevel')
    pre_item = M.ForeignKey('self', null=True, related_name='scheduleitem_pre_item', verbose_name=u'前一個版本是誰')
    priority = M.IntegerField(verbose_name=u'優先權值')


    class Meta:
        verbose_name = u'工程項目'
        verbose_name_plural = u'工程項目'
        permissions = (
            ('edit_schedule_item', 'Edit ScheduleItem'),
            ('view_schedule_item', 'View ScheduleItem'),
        )


    def __unicode__(self):
        return self.name


    def read_sub_item_in_list(self):
        #回傳自己工項本身的子工項，針對DIRKIND使用
        return ScheduleItem.objects.filter(uplevel=self).order_by('priority').prefetch_related('version', 'kind', 'uplevel', 'pre_item')

    def read_deep_sub_item_in_list(self):
        #回傳自己工項本身的子工項(包括工項的子工項)，針對DIRKIND使用
        items = [self]
        def readScheduleItemInlist(items, check_item):
            for i in check_item.read_sub_item_in_list():
                items.append(i)
                items = readScheduleItemInlist(items, i)
            return items

        items = readScheduleItemInlist(items, self)

        return items

    def read_level_num(self):
        #回傳是第幾階層的工項
        num = 0
        row = self
        while row.uplevel:
            num += 1
            row = row.uplevel
        return num

    def read_level_symbol(self):
        #回傳自己的項次，例如1.2.5
        symbol = str(self.priority + 1)
        row = self
        while row.uplevel:
            symbol = str(row.uplevel.priority + 1) + '.' + symbol
            row = row.uplevel

        return symbol[2:]

    def read_last_item(self):
        # 回傳下層裡面最後一個排序工項
        if ScheduleItem.objects.filter(uplevel=self).order_by('-priority'):
            return ScheduleItem.objects.filter(uplevel=self).order_by('-priority')[0]
        else:
            return ScheduleItem(priority=-1, kind=Option())

    def read_top_dir_in_list(self):
        # 回傳本身工項往上追到ROOT_DIR的路徑(倒著追)，例如 .5.2.1
        ids = ''
        row = self
        while row.uplevel:
            ids += '.' + str(row.uplevel.id)
            row = row.uplevel

        return ids

    def read_es(self):
        #計算這個項目下的最早開始時間，針對DIRKIND所使用
        if self.kind != DIRKIND:
            return self.es
        dir_items = [self]
        def readDirItemInlist(items, check_item):
            for i in check_item.read_sub_item_in_list():
                if i.kind == DIRKIND:
                    items.append(i)
                    items = readDirItemInlist(items, i)
            return items

        items = readDirItemInlist(dir_items, self)
        items.reverse()
        for i in items:
            if ScheduleItem.objects.filter(uplevel=i):
                i.es = min([j.es for j in ScheduleItem.objects.filter(uplevel=i)])
            else:
                i.es = 1
            i.save()
        return self.es

    def read_ef(self):
        #計算這個項目下的最早開始時間，針對DIRKIND所使用
        if self.kind != DIRKIND:
            return self.es
        dir_items = [self]
        def readDirItemInlist(items, check_item):
            for i in check_item.read_sub_item_in_list():
                if i.kind == DIRKIND:
                    items.append(i)
                    items = readDirItemInlist(items, i)
            return items

        items = readDirItemInlist(dir_items, self)
        items.reverse()
        for i in items:
            if ScheduleItem.objects.filter(uplevel=i):
                i.ef = max([j.ef for j in ScheduleItem.objects.filter(uplevel=i)])
            else:
                i.ef = 1
            i.save()
        return self.ef

    def read_dir_price(self):
        #計算這個項目下的總計金額，針對DIRKIND所使用
        if self.kind != DIRKIND:
            return self.unit_price

        dir_items = [self]
        def readDirItemInlist(items, check_item):
            for i in check_item.read_sub_item_in_list():
                if i.kind == DIRKIND:
                    items.append(i)
                    items = readDirItemInlist(items, i)
            return items

        items = readDirItemInlist(dir_items, self)
        items.reverse()

        for i in items:
            i.unit_price = round(sum([j.unit_price for j in ScheduleItem.objects.filter(uplevel=i)]))
            i.save()
        return int(items[-1].unit_price)



class EngProfile(M.Model):
    # 工程基本資料
    project = M.ForeignKey(Project, related_name='dailyreport_engprofile')
    start_date = M.DateField(verbose_name=u'實際開工日期', null=True)
    date_type = M.ForeignKey(Option, verbose_name=u'工期計算方式', related_name='date_type_set', null=True)
    round_type = M.ForeignKey(Option, verbose_name=u'總價計算方式', related_name='round_type_set', default=211)
    duration = M.IntegerField(verbose_name=u'工期天數(不含展延)', null=True, default=0)
    deadline = M.DateField(verbose_name=u'限期完工日期(不含展延)', null=True)
    contractor_name = M.CharField(verbose_name='營造廠商名稱', max_length=128, null=True)
    inspector_name = M.CharField(verbose_name='監造廠商名稱', max_length=128, null=True)
    design_percent = M.DecimalField(verbose_name=u'預定進度百分比', default=decimal.Decimal('0'),max_digits=16 , decimal_places=3)
    scheduled_completion_day = M.DateField(verbose_name=u'預計完工日期', null=True)
    act_contractor_percent = M.DecimalField(verbose_name=u'營造實際進度百分比', default=decimal.Decimal('0'), max_digits=16 , decimal_places=3)
    act_inspector_percent = M.DecimalField(verbose_name=u'監造實際進度百分比', default=decimal.Decimal('0'), max_digits=16 , decimal_places=3)
    contractor_lock = M.NullBooleanField(verbose_name=u'鎖定營造廠商不給修改', null=True, default=False)
    contractor_read_inspectorReport = M.NullBooleanField(verbose_name=u'營造是否可以觀看監造報表', null=True, default=True)
    have_change_date = M.DateField(verbose_name=u'有修改日報表的日期，後面的需要更新', null=True)
    must_fix_item = M.ManyToManyField(Item, verbose_name=u'有變更的item', related_name=u'profile_must_fix_item')
    schedule_progress = M.DecimalField(verbose_name=u'預定進度', default=decimal.Decimal('0'), max_digits=16 , decimal_places=2)

    class Meta:
        verbose_name = u'工程案之日報表基本資訊'
        verbose_name_plural = u'工程案之日報表基本資訊'

        permissions = ALL_PERMISSIONS

    def read__design__c__i__percent(self):
        class percent: pass
        percent.c = 0
        percent.i = 0
        percent.design = 0

        if not self.start_date:
            return percent

        reports = Report.objects.filter(project=self.project).order_by('-date')
        if not reports: return percent

        workingdates = self.readWorkingDate()
        schedule_progress = self.read_schedule_progress()
        day = False

        workingdates.reverse()
        for d in workingdates:
            if TODAY() >= d:
                day = d
                break
        if not day:
            day = workingdates[-1]

        version = Version.objects.filter(project=self.project).order_by('-start_date')[0]

        root_item = version.item_set.get(uplevel=None)
        price = root_item.read_dir_price_by_roundkind()
        report_money_i = sum([i.i_sum_money for i in Report.objects.filter(project=self.project, date__gte=version.start_date)])
        report_money_c = sum([i.c_sum_money for i in Report.objects.filter(project=self.project, date__gte=version.start_date)])
                
        percent.design = schedule_progress[day]
        if price:
            percent.i = round(float(str(report_money_i + version.pre_i_money)) / price * 100., 3)
            percent.c = round(float(str(report_money_c + version.pre_c_money)) / price * 100., 3)
        else:
            percent.i = 0
            percent.c = 0

        self.act_contractor_percent = round(percent.c, 3)
        self.act_inspector_percent = round(percent.i, 3)
        self.design_percent = round(percent.design, 3)
        self.save()

        return percent

    def get_report(self, date):
        '''
        取得日報表填報
        給line bot使用
        '''
        try:
            return Report.objects.get(project=self.project, date=date)
        except:
            return Report(id=-1,project=self.project, date=date)

    def get_monthly_info(self, year, month):
        u'''
        取得工程標案月資訊，以當月最後一日 或 最後一天工作天為基準
            :param year: 年
            :param month: 月
            :param type: 監造或施工 (inspector, contractor)
            :year limit: int
            :month limit: int
            :type string
            :rtype: Dict
            Line-Bot使用
        '''
        date_range = [str(year), str(month).zfill(2)]
        engprofile = self
        project = engprofile.project
        workingdates_default = engprofile.readWorkingDate()
        if TODAY() < workingdates_default[-1]:
            defined_finish_date = TODAY()
        else:
            defined_finish_date = workingdates_default[-1]

        reports = Report.objects.filter(project=project).order_by('-date')

        if reports:
            if reports[0].date > defined_finish_date:
                defined_finish_date = reports[0].date
        workingdates = engprofile.readWorkingDate(defined_finish_date=defined_finish_date)

        if workingdates[-1].month == 12:
            workingdates.append(datetime.datetime.strptime('%s-01-01' % (workingdates[-1].year+1), '%Y-%m-%d').date())
        else:
            workingdates.append(datetime.datetime.strptime('%s-%s-01' % (workingdates[-1].year, workingdates[-1].month+1), '%Y-%m-%d').date())

        schedule_progress = engprofile.read_schedule_progress() #預定進度列表
        action_progress_i = engprofile.read_action_progress(report_type="inspector") #"監造"實際進度列表
        action_progress_c = engprofile.read_action_progress(report_type="contractor") #"施工"實際進度列表

        #整理每年的最後一天進度金額
        year_progress_s = {workingdates[0].year-1: 0} #每年的最後一天"預定"金額
        year_progress_a_i = {workingdates[0].year-1: 0} #每年的最後一天"監造"實際金額
        year_progress_a_c = {workingdates[0].year-1: 0} #每年的最後一天"施工"實際金額
        for n, d in enumerate(workingdates[:-1]):
            if workingdates[n].year != workingdates[n+1].year:
                version = Version.objects.filter(project=project, start_date__lte=d).order_by('-start_date')[0] # 今天使用的版本
                version.engs_price = version.read_engs_price()
                engs_price = float(str(version.engs_price)) if version.engs_price else 0 # 契約金額
                year_progress_s[workingdates[n].year] = round(schedule_progress[d] * engs_price / 100.)
                year_progress_a_i[workingdates[n].year] = round(action_progress_i[d] * engs_price /100.)
                year_progress_a_c[workingdates[n].year] = round(action_progress_c[d] * engs_price /100.)
        version = Version.objects.filter(project=project).order_by('-start_date')[0] # 最後使用的版本
        version.engs_price = version.read_engs_price()
        engs_price = float(str(version.engs_price)) if version.engs_price else 0 # 契約金額
        
        year_progress_s[workingdates[-2].year] = round(schedule_progress[workingdates[-2]] * engs_price / 100.)
        year_progress_a_i[workingdates[-2].year] = round(action_progress_i[workingdates[-2]] * engs_price /100.)
        year_progress_a_c[workingdates[-2].year] = round(action_progress_c[workingdates[-2]] * engs_price /100.)
        #整理每個工作天的進度資訊
        d = None  #要取哪一天
        for n, wd in enumerate(workingdates[:-1]):
            if workingdates[n].month != workingdates[n+1].month and int(workingdates[n].year) == int(year) and int(workingdates[n].month) == int(month):
                d = wd
                break

        if not d: d = workingdates[-2]

        version = Version.objects.filter(project=project, start_date__lte=d).order_by('-start_date')[0] # 今天使用的版本
        version.engs_price = version.read_engs_price()
        engs_price = float(str(version.engs_price)) if version.engs_price else 0 # 契約金額

        info = {
                'date': d, #今天的日期
                's': round(schedule_progress[d], 3), #預定累積進度
                's_money': round(schedule_progress[d] * engs_price / 100.), #預定累積金額 = 預定進度 * 預定金額 / 100
                'c': round(action_progress_c[d], 3), #實際"監造"累積進度
                'c_money': round(action_progress_c[d] * engs_price / 100.), #實際"監造"累積金額 = 監造實際進度 * 契約金額 / 100
                'i': round(action_progress_i[d], 3), #實際"施工"累積進度
                'i_money': round(action_progress_i[d] * engs_price / 100.)  #實際"施工"累積金額 = 施工實際進度 * 契約金額 / 100
                }

        #換算本年度累積金額
        info['this_year_s_money'] = info['s_money'] - year_progress_s[d.year-1]
        info['this_year_i_money'] = info['i_money'] - year_progress_a_i[d.year-1]
        info['this_year_c_money'] = info['c_money'] - year_progress_a_c[d.year-1]
        
        #換算本年度累積進度
        if (year_progress_s[d.year] - year_progress_s[d.year-1]):
            info['this_year_s'] = round(info['this_year_s_money'] * 100. / (year_progress_s[d.year] - year_progress_s[d.year-1]), 3)
            info['this_year_i'] = round(info['this_year_i_money'] * 100. / (year_progress_s[d.year] - year_progress_s[d.year-1]), 3)
            info['this_year_c'] = round(info['this_year_c_money'] * 100. / (year_progress_s[d.year] - year_progress_s[d.year-1]), 3)
        else:
            info['this_year_s'] = 0
            info['this_year_i'] = 0
            info['this_year_c'] = 0

        report = self.get_report(date=d)
        duration_info = report.get_duration_info()

        return {
                'date': d,
                'accumulated': duration_info['used_duration'],                 # 總累計已用工期(天)
                'schedule_progress': info['s'],     # 總累計預定進度
                'actual_progress_i': info['i'],         # 總累計實際進度
                'actual_progress_c': info['c'],         # 總累計實際進度
                'schedule_cost': info['s_money'],             # 總累計預定完成金額
                'actual_cost_i': info['i_money'],                 # 總累計實際完成金額
                'actual_cost_c': info['c_money'],                 # 總累計實際完成金額
                'year_schedule_progress': info['this_year_s'],     # 年累計預定進度
                'year_actual_progress_i': info['this_year_i'],         # 年累計實際進度
                'year_actual_progress_c': info['this_year_c'],         # 年累計實際進度
                'year_schedule_cost': info['this_year_s_money'],             # 年累計預定完成金額
                'year_actual_cost_i': info['this_year_i_money'],                 # 年累計實際完成金額
                'year_actual_cost_c': info['this_year_c_money'],                 # 年累計實際完成金額
        }

    def get_monthly_equipment_and_crew(self, year, month):
        u'''
            取得機具及人員資訊，回傳當月累計的數量
            :param year: 年
            :param month: 月
            :year limit: int
            :month limit: int
            :rtype: Dict
            Line-Bot使用
        '''
        date = datetime.date(year, month, 1)
        firstDayWeekDay, day = calendar.monthrange(year, month)
        start_date = date
        last_date = datetime.date(year, month, day)
        equipment = []
        crew = []
        for e in LaborEquip.objects.filter(project=self.project).order_by('id'):
            quantity = ReportLaborEquip.objects.filter(type=e, report__date__gte=start_date, report__date__lte=last_date).aggregate(Sum('num'))['num__sum'] or decimal.Decimal('0')
            if quantity:
                if e.type.id==201:
                    equipment.append({
                        'name': e.value, 
                        'quantity': quantity})
                else:
                    crew.append({
                        'name': e.value, 
                        'quantity': quantity})

        return {
            'equipment': equipment,
            'crew': crew
        }

    def readFirstVersion(self):
        #回傳第一個版本
        try: return self.project.dailyreport_version.all().order_by('start_date')[0]
        except IndexError: return None


    def readLatestVersion(self):
        #回傳最後一個版本
        try: return self.project.dailyreport_version.all().order_by('-start_date')[0]
        except IndexError: return None


    def read_version_in_list(self):
        #回傳全部版本
        try: return self.project.dailyreport_version.all().order_by('start_date')
        except IndexError: return None

    def read_change_version_times(self):
        try: return self.project.dailyreport_version.all().order_by('start_date').count() - 1
        except IndexError: return None

    def read_schedule_progress(self):
        #計算預定累積進度列表
        working_dates = self.readWorkingDate()
        versions = Version.objects.filter(project=self.project).order_by('-start_date')
        for v in versions:
            read_engs_price = v.read_engs_price()
            progress_list = [0 for i in working_dates]
            schedule_items = v.scheduleitem_set.all().exclude(kind=DIRKIND)
            for si in schedule_items:
                for d in xrange(si.es-1, si.ef):
                    progress_list[d] += float(str(si.unit_price))/(si.ef-si.es+1)
            for n, p in enumerate(progress_list):
                if n == 0: continue
                progress_list[n] += progress_list[n-1]
            for n, p in enumerate(progress_list):
                if read_engs_price == 0:
                    progress_list[n] = 0
                else:
                    progress_list[n] = round(p*100./read_engs_price, 3)

            v.progress_list = progress_list
        complex_progress_list = {}
        version = versions[0]
        for nd, wd in enumerate(working_dates):
            for v in versions:
                if wd >= v.start_date:
                    version = v
                    break
            complex_progress_list[wd] = version.progress_list[nd]
        return complex_progress_list

    def read_schedule_progress_for_s_curve(self):
        #計算預定累積進度列表 for 畫S曲線用
        working_dates = self.readWorkingDate()
        versions = Version.objects.filter(project=self.project).order_by('-start_date')
        v_progress_list = {}
        for v in versions:
            read_engs_price = float(v.read_engs_price())
            progress_list = [0 for i in working_dates]
            schedule_items = v.scheduleitem_set.all().exclude(kind=DIRKIND)
            for si in schedule_items:
                for d in xrange(si.es-1, si.ef):
                    progress_list[d] += float(str(si.unit_price))/(si.ef-si.es+1)
            for n, p in enumerate(progress_list):
                if n == 0: continue
                progress_list[n] += progress_list[n-1]
            for n, p in enumerate(progress_list):
                if read_engs_price == 0:
                    progress_list[n] = 0
                else:
                    progress_list[n] = round(p*100./read_engs_price, 3)
            v_progress_list[v.id] = progress_list

        complex_progress_list = {}
        change_progress = {}
        version = versions[0]
        pre_version = versions[0]
        for nd, wd in enumerate(working_dates):
            for v in versions:
                if wd >= v.start_date:
                    version = v
                    break
            if version.id != pre_version.id and nd != 0:
                change_progress[wd] = v_progress_list[pre_version.id][nd]
                pre_version = version
            elif version.id != pre_version.id and nd == 0:
                change_progress[working_dates[nd]-datetime.timedelta(1)] = 0
                pre_version = version
            complex_progress_list[wd] = v_progress_list[version.id][nd]
        return complex_progress_list, change_progress

    def read_action_progress(self, report_type="contractor"):
        #計算實際累積進度列表
        working_dates = self.readWorkingDate()
        
        versions = Version.objects.filter(project=self.project).order_by('start_date')
        version_engs_price = {}
        for v in versions:
            version_engs_price[v.start_date] = v.read_engs_price()

        progress_list = [0 for i in working_dates]
        reports = Report.objects.filter(project=self.project)

        for r in reports:
            if report_type == 'inspector':
                progress_list[working_dates.index(r.date)] = r.i_sum_money
            else:
                progress_list[working_dates.index(r.date)] = r.c_sum_money
        
        money = decimal.Decimal('0')
        pre_version = versions[0]
        complex_progress_list = {}
        for nd, wd in enumerate(working_dates):
            this_version = versions.filter(start_date__lte=wd).order_by('-start_date')[0]
            if this_version != pre_version:
                money = decimal.Decimal('0')
                pre_version = this_version

            money += progress_list[nd]
            if report_type == 'inspector':
                progress_list[nd] = money + this_version.pre_i_money
            else:
                progress_list[nd] = money + this_version.pre_c_money
            
            if version_engs_price[this_version.start_date]:
                complex_progress_list[wd] = round(float(str(progress_list[nd])) * 100/version_engs_price[this_version.start_date], 3)
            else:
                complex_progress_list[wd] = 0
        return complex_progress_list

    def update_report_item_sum_num_and_price(self, report_date='', report_type='both'):
        report_date = datetime.datetime.strptime(str(report_date), "%Y-%m-%d").date()

        have_progress_change = False
        #非常重要的動作，此時根據have_change_date進行填報記錄更新
        if report_date < self.have_change_date:
            #如果已經更新到7/15  則  讀取 7/15之前的日報表的都不需要更新
            pass
        else:
            #否則就更新到想要讀取的日期
            #拿到  需要更新日期~讀取日期  之間的所有日報表
            reports = Report.objects.filter(project=self.project, date__gte=self.have_change_date, date__lte=report_date).order_by('date')
            # if report_type == 'inspector':
            #     reports = reports.filter(inspector_check=True)
            # else:
            #     reports = reports.filter(contractor_check=True)
            #需要修正的items
            must_fix_items = self.must_fix_item.all()
            if must_fix_items:
                have_progress_change = True
            else:
                reports = []
            #把不同版本的相同工項都找出來
            tmp = []
            for mfi in must_fix_items:
                tmp += mfi.read_brother_items()
            must_fix_items = tmp

            for report in reports:
                #更新item 及 每日的填報金額
                #當天的所有工項
                report_items = report.reportitem_set.all()
                #找前一筆填寫紀錄
                pre_reports = Report.objects.filter(project=self.project, date__lt=report.date).order_by('-date')
                if pre_reports:
                    pre_report = pre_reports[0]
                    pre_report_items = pre_report.reportitem_set.all()
                else:
                    pre_report = []

                for report_item in report_items:
                    if report_item.item in must_fix_items:
                        if pre_report:
                            #如果有前一筆，就把他的累計數量加上今天填寫的變成自己的累計數量
                            try:
                                #如果前一筆有這個工項，就把他的累計數量加上今天填寫的變成自己的累計數量
                                pre_report_item = pre_report_items.get(item__in=report_item.item.read_brother_items())
                                report_item.i_sum_num = report_item.i_num + pre_report_item.i_sum_num
                                report_item.c_sum_num = report_item.c_num + pre_report_item.c_sum_num
                            except:
                                #如果前一筆沒有這個工項，則自己的數量就是累計數量
                                report_item.i_sum_num = report_item.i_num
                                report_item.c_sum_num = report_item.c_num
                        else:
                            #如果沒有前一筆填寫，則自己的數量就是累計數量
                            report_item.i_sum_num = report_item.i_num
                            report_item.c_sum_num = report_item.c_num
                        report_item.save()
                        
                #更新今日施做金額
                report.update_sum_money()
                report.save()
            #修正需要更新的日期為此次要求日期

            self.have_change_date = report_date

            for mfi in must_fix_items:
                #如果之後沒有此工項的填寫紀錄，就從需要修正工項列表中移除
                if not ReportItem.objects.filter(item__in=mfi.read_brother_items(), report__date__gt=report_date):
                    self.must_fix_item.remove(mfi)
            self.save()
        
        #順便更新基本資料的進度欄位
        if have_progress_change:
            self.read__design__c__i__percent()

        return True


    def setDefaultEngProfile(self, project=None):
        # 創立基本資料
        if not project: return False
        elif hasattr(self, 'project'): return self.project

        self.project = project
        self.contractor_lock = False
        self.contractor_read_inspectorReport = True
        self.design_percent = 0
        self.act_contractor_percent = 0
        self.act_inspector_percent = 0
        self.round_type = DIR_ROUND
        self.have_change_date = TODAY()
        self.save()

        #加入預設的人員機具列表
        for n, l in enumerate(Option.objects.filter(swarm="labor")):
            row = LaborEquip(project=project, type=LABOR_TYPE, value=l.value, sort=n+1)
            row.save()
        for n, e in enumerate(Option.objects.filter(swarm="equip")):
            row = LaborEquip(project=project, type=EQUIP_TYPE, value=e.value, sort=n+1)
            row.save()

        return True

    def create_root_item(self):
        #創立第一個Item and ScheduleItem
        if Item.objects.filter(version__project=self.project, uplevel=None):
            return True
        try:
            version = Version.objects.get(project=self.project)
        except:
            version = Version(
                project = self.project,
                start_date = TODAY(),
                engs_price = 0,
                schedule_price = 0,
                pre_act_percent = 0,
                pre_design_percent = 0,
                )
            version.save()

        item = Item(
            version = version,
            name = self.project.name,
            kind = DIRKIND,
            priority = 0
            )
        item.save()

        schedule_item = ScheduleItem(
            version = version,
            name = self.project.name,
            kind = DIRKIND,
            priority = 0
            )
        schedule_item.save()

        return item.id

    def readLatestWorkingDate(self):
        #預定完工日期
        if not hasattr(self, 'working_dates'): self.readWorkingDate(is_scheduled=True)
        if self.working_dates:
            return self.working_dates[-1]
        return ''

    def readExtensions(self):
        #所有工程展延紀錄
        extensions = self.project.dailyreport_extension.all().order_by('date')
        return extensions

    def readExtensionDay(self):
        #只回傳工程展延總天數
        return sum([i.day for i in self.readExtensions()])

    def readWorkingDate(self, defined_finish_date='', is_scheduled=False):
        #回傳所有可以填寫的日期列表
        """ defined_finish_date := 自行定義的結束日期。當有工程延誤的情況發生時，
            我們須計算預定完工日期後的工作日
        """
        if self.start_date: start_date = self.start_date
        else: return []
        if self.date_type: date_type = self.date_type.value
        else: return []
        if self.date_type.value == '限期完工(日曆天每日施工)':
            range = 0
            if self.deadline:
                finish_date = self.deadline + datetime.timedelta(sum([i.day for i in self.readExtensions()]))
            else: finish_date = None
        else:
            finish_date = None
            range = self.duration + sum([i.day for i in self.readExtensions()])

        if not is_scheduled:
            for v in self.project.dailyreport_version.all():
                si = v.scheduleitem_set.filter(kind=ITEMKIND).aggregate(Max('ef'))
                if si['ef__max'] and si['ef__max'] > range: range = si['ef__max']

        if not finish_date and range == 0: return []

        if not is_scheduled:
            report = self.project.dailyreport_report.all().aggregate(Max('date'))
            if report['date__max']:
                if not finish_date or finish_date < report['date__max']:
                    finish_date = report['date__max']

        if self.date_type.value == u'工作天':
            holidays = self.readHoliday(type_value=u'假日')
        else:
            holidays = []
        date_on = self.readSpecialDate(type_value='強制開工')
        date_off = self.readSpecialDate(type_value='停工') + self.readSpecialDate(type_value=u'休息日')

        if defined_finish_date: finish_date = defined_finish_date

        wd = WorkingDate(end_date=finish_date, start_date=start_date, holiday=holidays,
            date_type=date_type, date_off=date_off, date_on=date_on, range=range)
        self.working_dates = wd.readWorkingDate()
        
        #刪除不應該存在的日報表
        Report.objects.filter(project=self.project, date__lte=self.working_dates[-1]).exclude(date__in=self.working_dates).delete()
        
        return self.working_dates

    def readScheduledCompletionDay(self, date=u''):
        """
        計算預定完工日期
        #date以後的停工與展延都不能算
        """
        if self.start_date: start_date = self.start_date
        else: return ''
        if self.date_type: date_type = self.date_type.value
        else: return ''
        if self.date_type.value == '限期完工(日曆天每日施工)':
            return self.deadline
        else:
            finish_date = None
            range = self.duration + sum([i.day for i in Extension.objects.filter(project=self.project, date__lte=date)])
            range = math.ceil(range)

        if not finish_date and range == 0: return ''
        
        if self.date_type.value == u'工作天':
            holidays = self.readHoliday(type_value=u'假日')
        else:
            holidays = []

        day = []
        for d in self.project.dailyreport_specialdate.filter(type__value__in=[u'強制開工'], begin_date__lte=date):
            day.extend(readDateRange(d.start_date, d.end_date))
        date_on = []
        null = [date_on.append(d) for d in day if d not in date_on]
        date_on.sort()

        day = []
        for d in self.project.dailyreport_specialdate.filter(type__value__in=[u'停工', u'休息日', u'雨天停工'], begin_date__lte=date):
            day.extend(readDateRange(d.start_date, d.end_date))
        date_off = []
        null = [date_off.append(d) for d in day if d not in date_off]
        date_off.sort()

        wd = WorkingDate(end_date=finish_date, start_date=start_date, holiday=holidays,
            date_type=date_type, date_off=date_off, date_on=date_on, range=range)
        self.working_dates = wd.readWorkingDate()
        
        if self.working_dates: return self.working_dates[-1]
        else: return ''

    def readHoliday(self, type_value=u'假日'):
        #回傳開工日期以後的假日
        if not self.start_date: start_date = self.start_date
        else: start_date = datetime.date(2008, 1, 1)

        return [h.date for h in Holiday.objects.filter(date__gte=start_date)]

    def readSpecialDate(self, type_value='停工'):
        #回傳此工程案自定義停工或強制開工設定日期
        day = []
        for d in self.project.dailyreport_specialdate.filter(type__value=type_value):
            day.extend(readDateRange(d.start_date, d.end_date))
        unit_day = []
        null = [unit_day.append(d) for d in day if d not in unit_day]
        unit_day.sort()
        return unit_day


    def readColorDateOfInspectorReport(self):
        #回傳監造報表的顏色列表
        return self.readColorDateOfReport(report_type='inspector')

    def readColorDateOfContractorReport(self):
        #回傳施工日誌的顏色列表
        return self.readColorDateOfReport(report_type='contractor')


    def readColorDateOfReport(self, report_type=''):
        #根據施工或監造報表類型回傳顏色
        dates = {}
        if self.date_type.value != '限期完工(日曆天每日施工)':
            for d in self.readHoliday(type_value=u'假日'):
                dates[d.strftime('%Y-%m-%d')] = 'date_off'
        for d in self.readSpecialDate(type_value=u'停工'):
            dates[d.strftime('%Y-%m-%d')] = 'date_off'
        for d in self.readSpecialDate(type_value=u'休息日'):
            dates[d.strftime('%Y-%m-%d')] = 'date_off_rest'
        for d in self.readSpecialDate(type_value=u'強制開工'):
            dates[d.strftime('%Y-%m-%d')] = 'date_on'

        for r in getattr(self, 'read%sReport' % updateFirstWordByUpper(report_type))():
            date_str = r.date.strftime('%Y-%m-%d')
            date_type = dates.get(date_str, None)
            if date_type != 'date_off':
                dates[date_str] = 'reported'
            else:
                dates[date_str] = 'date_off_reported'

        for r in ReportHoliday.objects.filter(project=self.project):
            date_str = r.date.strftime('%Y-%m-%d')
            date_type = dates.get(date_str, '')
            if 'date_off' in date_type or not date_type:
                dates[date_str] = 'date_off_reported'
        return dates

    def readContractorReport(self):
        return self.readReport(report_type='contractor')

    def readInspectorReport(self):
        return self.readReport(report_type='inspector')

    def readAllReport(self):
        return self.readReport(report_type='all')

    def readReport(self, report_type=''):
        try:
            latest_report = self.project.dailyreport_report.latest()
            if not latest_report: return []
        except:
            return []

        working_dates = self.readWorkingDate()
        attribute = '%s_reports' % report_type
        if report_type == 'inspector':
            setattr(self, attribute,
                self.project.dailyreport_report.filter(inspector_check=True, date__in=working_dates).order_by('date'))
        elif report_type == 'contractor':
            setattr(self, attribute,
                self.project.dailyreport_report.filter(contractor_check=True, date__in=working_dates).order_by('date'))
        elif report_type == 'all':
            setattr(self, attribute,
                self.project.dailyreport_report.filter(date__in=working_dates).order_by('date'))
        return getattr(self, attribute)

    def readContractorReportGroupByMonth(self):
        #所有施工有填過的日報表
        return self.readReportGroupByMonth(type='contractor')

    def readInspectorReportGroupByMonth(self):
        #所有監工有填過的日報表
        return self.readReportGroupByMonth(type='inspector')

    def readAllReportGroupByMonth(self):
        #所有有填過的日報表
        return self.readReportGroupByMonth(type='all')

    def readNotCompleteReportGroupByMonth(self):
        #所有尚未填寫的日報表
        working_dates = self.readWorkingDate()
        date_by_month = {}
        for d in working_dates:
            if d > TODAY():
                break
            else:
                try:
                    report = Report.objects.get(date=d, project=self.project)
                except:
                    report = Report(inspector_check=False, contractor_check=False)
                key = d.strftime('%Y-%m')
                if date_by_month.has_key(key):
                    if not report.inspector_check:
                        date_by_month[key][0].append(d)
                    if not report.contractor_check:
                        date_by_month[key][1].append(d)
                else:
                    date_by_month[key] = [[], []]
                    if not report.inspector_check:
                        date_by_month[key][0].append(d)
                    if not report.contractor_check:
                        date_by_month[key][1].append(d)

        keys = date_by_month.keys()
        keys.sort()
        date_by_month_list = []
        for k in keys:
            if date_by_month[k][0] or date_by_month[k][1]:
                date_by_month_list.append({'key': k, 'value': date_by_month[k]})
        return date_by_month_list

    def readReportGroupByMonth(self, type=''):
        reports = getattr(self, 'read%sReport' % (updateFirstWordByUpper(type)))()
        reports_by_month = {}
        diff_date = [i.report.date for i in ReportItem.objects.filter(report__project=self.project, report__contractor_check=True, report__inspector_check=True).exclude(i_num=F('c_num'))]
        diff_date = set(diff_date)
        for i in reports:
            if i.date in diff_date: i.is_diff = True
            key = i.date.strftime('%Y-%m')
            reports_by_month.setdefault(key, []).append(i)
        keys = reports_by_month.keys()
        keys.sort()
        reports_by_month_list = []
        for k in keys:
            reports_by_month_list.append({'key': k, 'value': reports_by_month[k]})

        self.reports_by_month = reports_by_month_list
        return self.reports_by_month

    def reset_item_priority(self):
        '''
            重新順一次item序號
        '''
        for v in Version.objects.filter(project=self.project):
            items = v.item_set.filter(kind__value=u'目錄')
            for i in items:
                p = 0
                for j in Item.objects.filter(uplevel=i).order_by('priority'):
                    j.priority = p
                    p += 1
                    j.save()

            s_items = v.scheduleitem_set.filter(kind__value=u'目錄')
            for i in s_items:
                p = 0
                for j in ScheduleItem.objects.filter(uplevel=i).order_by('priority'):
                    j.priority = p
                    p += 1
                    j.save()

        return True



class Extension(M.Model):
    # 工程展延紀錄
    project = M.ForeignKey(Project, related_name='dailyreport_extension', verbose_name=u'工程案')
    date = M.DateField(verbose_name=u'申請日期')
    day = M.IntegerField(verbose_name=u'展延天數', null=True, default=0)
    no = M.CharField(verbose_name=u'文號', max_length=1024, null=True)
    memo = M.TextField(verbose_name=u'備註', null=True, default='')


    def save(self, *args, **kw):

        super(Extension, self).save(*args, **kw)
        engprofile = EngProfile.objects.get(project=self.project)
        engprofile.extension = sum([i.day for i in Extension.objects.filter(project=self.project)])
        engprofile.save()



class SpecialDate(M.Model):
    # 特別日子 包含 停工 休息日 強制開工
    project = M.ForeignKey(Project, related_name='dailyreport_specialdate', verbose_name=u'工程案')
    start_date = M.DateField(verbose_name=u'起始日期')
    end_date = M.DateField(verbose_name=u'結束日期')
    begin_date = M.DateField(verbose_name=u'生效日期')
    no = M.CharField(verbose_name=u'文號', max_length=1024, null=True)
    type = M.ForeignKey(Option, default=221)
    reason = M.TextField(verbose_name=u'原因', null=True, default='')

    def __unicode__(self):
        return '%s:%s %s~%s %s' % (self.project, self.type.value, self.start_date, self.end_date, self.reason)

    class Meta:
        verbose_name = u'特別日子'
        verbose_name_plural = u'特別日子'
        permissions = (
            ('edit_special_date', 'Edit SpecialDate'),
            ('view_special_date', 'View SpecialDate'),
        )

    def get_days(self):
        return (self.end_date - self.start_date).days



class Report(M.Model):
    # 每日日報表紀錄  監造 與施工紀錄 合併
    project = M.ForeignKey(Project, related_name='dailyreport_report', verbose_name=u'工程案')
    date = M.DateField(verbose_name=u'日期')
    contractor_check = M.BooleanField(verbose_name=u'營造廠商填寫', default=False)
    inspector_check = M.BooleanField(verbose_name=u'監造廠商填寫', default=False)
    lock_c = M.BooleanField(default=False, verbose_name=u'是否鎖定不給(雙方)修改')
    update_time = M.DateTimeField(verbose_name=u'最後更新時間', auto_now=True)
    morning_weather = M.ForeignKey(Option, verbose_name=u'上午天氣', related_name='morning_weather_report', default=20)
    afternoon_weather = M.ForeignKey(Option, verbose_name=u'下午天氣', related_name='afternoon_weather_report', default=20)
    has_professional_item = M.BooleanField(verbose_name=u'是否有須依「營造業專業工程特定施工項目應置之技術士種類、比率或人數標準表」規定', default=False)
    pre_education = M.BooleanField(verbose_name=u'實施勤前教育(含工地預防災變及危害告知)', default=False)
    has_insurance = M.IntegerField(verbose_name=u'確認新進勞工是否提報勞工保險(或其他商業保險)資料及安全衛生教育訓練紀錄', default=3) # 1有  2.無  3.無新進勞工
    safety_equipment = M.BooleanField(verbose_name=u'檢查勞工個人防護具', default=False)
    pre_check = M.BooleanField(verbose_name=u'施工廠商施工前檢查事項辦理情形', default=False)
    i_sum_money = M.DecimalField(verbose_name=u'監工單日施作金額', max_digits=16 , decimal_places=3, null=True)
    c_sum_money = M.DecimalField(verbose_name=u'施工單日施作金額', max_digits=16 , decimal_places=3, null=True)

    i_project_status = M.TextField(verbose_name=u'一、工程進行情況(含約定之重要施工項目及數量)：', null=True)
    note = M.TextField(verbose_name=u'二、監督依照設計圖說施工(含約定之檢驗停留點及施工抽查等情形)：', null=True)
    sampling = M.TextField(verbose_name=u'三、查核材料規格及品質(含約定之檢驗停留點、材料設備管制及檢（試）驗等抽驗情形)：', null=True)
    describe_subcontractor = M.TextField(verbose_name=u'四、督導工地職業安全衛生事項：', null=True)
    i_pre_check = M.TextField(verbose_name=u'(一)施工廠商施工前檢查事項辦理情形：', null=True)
    notify = M.TextField(verbose_name=u'五、其他約定監造事項(含重要事項紀錄、主辦機關指示及通知廠商辦理事項等)：', null=True)
    
    c_describe_subcontractor = M.TextField(verbose_name=u'五、工地職業安全衛生事項之督導、公共環境與安全之維護及其他工地行政事務：', null=True)
    c_sampling = M.TextField(verbose_name=u'六、施工取樣試驗紀錄：', null=True)
    c_notify = M.TextField(verbose_name=u'七、通知協力廠商辦理事項：', null=True)
    c_note = M.TextField(verbose_name=u'八、重要事項紀錄：', null=True)

    
    class Meta:
        get_latest_by = 'date'
        permissions = (
            ('edit_contractor_report', 'Edit Constractor Report'),
            ('edit_inspector_report', 'Edit Inspector Report'),
            ('view_contractor_report', 'View Constractor Report'),
            ('view_inspector_report', 'View Inspector Report'),
        )
        unique_together = (("project", "date"),)


    '''
    沒用到
    def __unicode__(self):
        return '%s(%s):%s' % (self.project, self.date)
    '''
    def get_duration_info(self):
        '''
            取得工期資訊
            Line-Bot使用
        '''
        project = self.project
        report_date = self.date
        engprofile = EngProfile.objects.get(project=project)
        workingdates = engprofile.readWorkingDate()
        max_day = max(workingdates)
        workingdates_scheduled = engprofile.readWorkingDate(is_scheduled=True)
        all_duration = len(workingdates_scheduled) - sum([i.day for i in Extension.objects.filter(project=project, date__gt=report_date)])

        if report_date >= max_day:
            used_duration = workingdates.index(max_day) + 1 + int((report_date - max_day).days)
        else:
            dd = report_date
            while dd not in workingdates and dd >= engprofile.start_date:
                dd -= datetime.timedelta(1)
            if dd < engprofile.start_date:
                used_duration = 0
            else:
                used_duration = workingdates.index(dd) + 1

        unused_duration = all_duration - used_duration
        
        used_duration -= sum([i.day for i in Extension.objects.filter(project=project, date__lte=report_date)])
        return {
            'unused_duration': unused_duration,
            'used_duration': used_duration,
        }

    def read_version(self):
        versions = Version.objects.filter(project=self.project, start_date__lte=self.date).order_by('-start_date')
        return versions[0]

    def update_sum_money(self):
        version = self.read_version()
        report_items = self.reportitem_set.all().exclude(i_num=0, c_num=0).prefetch_related('item')
        i_sum_money = 0
        c_sum_money = 0
        for i in report_items:
            i_sum_money += float(str(i.i_num)) * float(str(i.item.unit_price))
            c_sum_money += float(str(i.c_num)) * float(str(i.item.unit_price))

        self.i_sum_money = i_sum_money
        self.c_sum_money = c_sum_money

        self.save()

        

    def read_progress(self, report_type='inspector'):
        #今日累計完成進度
        version = Version.objects.filter(project=self.project, start_date__lte=self.date).order_by('-start_date')[0]
        root_item = version.item_set.get(uplevel=None)
        pre_reports = Report.objects.filter(project=self.project, date__lte=self.date)
        if report_type == 'inspector':
            if root_item.read_dir_price_by_roundkind() == 0:
                return 0
            else:
                return round(sum([float(str(r.i_sum_money)) for r in pre_reports]) / root_item.read_dir_price_by_roundkind() * 100., 3)
        else:
            if root_item.read_dir_price_by_roundkind() == 0:
                return 0
            else:
                return round(sum([float(str(r.c_sum_money)) for r in pre_reports]) / root_item.read_dir_price_by_roundkind() * 100., 3)



class ReportHoliday(M.Model):
    """不計工期、放假日 的 日報表紀錄"""
    project = M.ForeignKey(Project, related_name='dailyreport_reportholiday', verbose_name=u'工程案')
    date = M.DateField(verbose_name=u'日期')
    morning_weather = M.ForeignKey(Option, verbose_name=u'上午天氣', related_name='morning_weather_reportholiday', default=20)
    afternoon_weather = M.ForeignKey(Option, verbose_name=u'下午天氣', related_name='afternoon_weather_reportholiday', default=20)
    describe_subcontractor = M.TextField(verbose_name=u'工程進行情況補充說明：', null=True)
    sampling = M.TextField(verbose_name=u'查核材料規格及品質（含約定之檢驗停留點、材料設備管制及檢（試）驗等抽驗情形）', null=True)
    notify = M.TextField(verbose_name=u'其他約定監造事項（含督導工地勞工安全衛生事項、重要事項紀錄、主辦機關指示及通知廠商辦理事項：', null=True)
    note = M.TextField(verbose_name=u'監督依照設計圖說施工(含約定之檢驗停留點及施工抽查等情形)：', null=True)
    c_describe_subcontractor = M.TextField(verbose_name=u'劦盛工程顧問有限公司', null=True)
    c_sampling = M.TextField(verbose_name=u'施工取樣試驗紀錄：', null=True)
    c_notify = M.TextField(verbose_name=u'通知分包商辦理事項：', null=True)
    c_note = M.TextField(verbose_name=u'重要事項紀錄(含主辦機關及監造單位指示、工地遇緊急異常狀況及需解決施工技術問題之通報處理情形、施工要徑、進度落原因及因應對策等)：', null=True)
    
    i_project_status = M.TextField(verbose_name=u'一、工程進行情況(含約定之重要施工項目及數量)：', null=True)
    pre_education = M.BooleanField(verbose_name=u'實施勤前教育(含工地預防災變及危害告知)', default=False)
    has_insurance = M.IntegerField(verbose_name=u'確認新進勞工是否提報勞工保險(或其他商業保險)資料及安全衛生教育訓練紀錄', default=3) # 1有  2.無  3.無新進勞工
    safety_equipment = M.BooleanField(verbose_name=u'檢查勞工個人防護具', default=False)
    pre_check = M.BooleanField(verbose_name=u'施工廠商施工前檢查事項辦理情形', default=False)
    i_pre_check = M.TextField(verbose_name=u'(一)施工廠商施工前檢查事項辦理情形：', null=True)
    
    class Meta:
        unique_together = (("project", "date"),)



class ReportItem(M.Model):
    # 每日填寫工項 數量
    report = M.ForeignKey(Report, verbose_name=u'報表')
    item = M.ForeignKey(Item, verbose_name=u'施作工項')
    i_num = M.DecimalField(verbose_name=u'監造填寫數量', null=True, default=decimal.Decimal('0.00'), max_digits=16 , decimal_places=5)
    i_sum_num = M.DecimalField(verbose_name=u'累計監造數量', null=True, default=decimal.Decimal('0.00'), max_digits=16 , decimal_places=5)
    i_note = M.TextField(verbose_name=u'監造備註', null=True)
    c_num = M.DecimalField(verbose_name=u'施工填寫數量', null=True, default=decimal.Decimal('0.00'), max_digits=16 , decimal_places=5)
    c_sum_num = M.DecimalField(verbose_name=u'施工累計數量', null=True, default=decimal.Decimal('0.00'), max_digits=16 , decimal_places=5)
    c_note = M.TextField(verbose_name=u'施工備註', null=True)

    class Meta:
        unique_together = (("report", "item"),)


    def pre_report_item(self, report_type=''):
        items = self.item.read_brother_items()
        if report_type=="inspector":
            pre_report_items = ReportItem.objects.filter(report__project=self.report.project, report__inspector_check=True, report__date__lt=self.report.date, item__in=items).order_by('-report__date')
        elif report_type=="contractor":
            pre_report_items = ReportItem.objects.filter(report__project=self.report.project, report__contractor_check=True, report__date__lt=self.report.date, item__in=items).order_by('-report__date')
        
        if pre_report_items:
            return pre_report_items[0]
        else:
            return False



class LaborEquip(M.Model):
    # 這件工程的人員/機具 列表
    project = M.ForeignKey(Project, null=True, related_name='dailyreport_laborquip', verbose_name=u'工程案')
    type = M.ForeignKey(Option, default=200)
    sort = M.IntegerField(verbose_name=u'排序', default=1)
    value = M.CharField(verbose_name=u'名稱', max_length=64)

    def is_first(self):
        if self.sort == 1: return True
        else: return False

    def is_last(self):
        if self.sort == LaborEquip.objects.filter(project=self.project, type=self.type).count(): return True
        else: return False

        

class ReportLaborEquip(M.Model):
    # 每日填寫之機具/人員 數量
    report = M.ForeignKey(Report, verbose_name=u'報表')
    type = M.ForeignKey(LaborEquip, verbose_name=u'人機項目')
    num = M.DecimalField(verbose_name=u'數量', null=True, max_digits=16 , decimal_places=3)



class SiteMaterial(M.Model):
    # 每日填寫之工地材料
    report = M.ForeignKey(Report, verbose_name=u'報表')
    name = M.CharField(verbose_name='材料名稱', null=True, max_length=256)
    unit_name = M.CharField(verbose_name='單位', max_length=16, null=True)
    unit_num = M.DecimalField(verbose_name='設計數量', default=0 , max_digits=16 , decimal_places=3, null=True)
    today_num = M.DecimalField(verbose_name='本日完成數量', default=0 , max_digits=16 , decimal_places=3, null=True)
    today_sum_num = M.DecimalField(verbose_name='累計完成數量', default=0 , max_digits=16 , decimal_places=3, null=True)
    note = M.CharField(verbose_name='備註', max_length=128, null=True)


    class Meta:
        verbose_name = '工地材料'
        verbose_name_plural = '工地材料'
