# -*- coding:utf8 -*-
from django.utils.translation import ugettext as _
from django.db import models as M
from django.db.models import Q
from django.db.models import Sum
from django.db.models import Max
from django.db.models import Min
from django.db.models.signals import post_init, post_save, post_delete

from django.contrib.auth.models import User, Group
from project.models import Project, FRCMUserGroup

from dailyreport.models import Holiday
from dailyreport.models import Option
from dailyreport.models import LABOR_TYPE
from dailyreport.models import EQUIP_TYPE
from dailyreport.models import EngProfile
from dailyreport.models import Version
from dailyreport.models import Item
from dailyreport.models import ScheduleItem
from dailyreport.models import LaborEquip
from dailyreport.models import SpecialDate
from dailyreport.models import Report
from dailyreport.models import ReportItem
from dailyreport.models import ReportLaborEquip

import datetime, decimal
from guardian.shortcuts import assign, get_perms, remove_perm

from random import random
import datetime
import time
import re
import os.path
from xml.dom import minidom
from xml.dom import Node
from types import IntType, LongType
from django.conf import settings

def TODAY(): return datetime.date.today()

def NOW(): return datetime.datetime.now()



#匯入PCCES用的

class ParsePCCES:
    def ParseSpecialDate(self):
        for i in self.specialdatelist.replace(' ', '').split(';')[:-1]:
            j = i.split(',')
            try:
                start = datetime.date(*time.strptime(j[0], '%Y-%m-%d')[:3])
                end = datetime.date(*time.strptime(j[1], '%Y-%m-%d')[:3])
                type = Option.objects.get(swarm='specialdate', value=j[2])
            except:
                continue
            try:
                sd = SpecialDate.objects.get(project=self.project, start=start, end=end, type=type)
            except:
                sd = SpecialDate(project=self.project, start=start, end=end, type=type)

            sd.reason = j[3]
            sd.save()

    def _make_parent(self):
        try:
            item = Item.objects.get(version=self.version, uplevel__isnull=True)
        except Item.MultipleObjectsReturned:
            return item[0]
        except Item.DoesNotExist:
            item = Item(unit_num=1, unit_price=0, unit_name='式', name='根目錄',kind=self.dirkind,
                uplevel=None, priority=0, version=self.version, es=0, ef=0)
            item.save()
        return item

    def _clear_item(self):
        Item.objects.filter(version=self.version).delete()

    def clearParent(self):
        root = Item.objects.get(version=self.version, uplevel__isnull=True)
        for i in root.uplevel_subitem.all():
            i.uplevel = None
            i.save()
        root.delete()

    def __init__(self, context, project, version):
        self.item_kind = Option.objects.get(swarm='item_kind', value='工項')
        self.dirkind = Option.objects.get(swarm='item_kind', value='目錄')
        self.serialname = 0
        self.priority = 0
        self.project = project
        self.version = version
        #self._clear_item()
        try:
            self.parent = Item.objects.get(version=self.version, uplevel__isnull=True)
        except Item.DoesNotExist:
            self.parent = self._make_parent()
        self.detaillist = ''
        try:
            doc = minidom.parseString(context)
            self.detaillist = doc.getElementsByTagName('DetailList')[0]
            self.status = True
        except:
            self.status = False

        try:
            self.specialdatelist = self.GetText(
            doc.getElementsByTagName('SpecialDateList')[0]).replace('\n', '')
        except:
            self.specialdatelist = ''


    def Parse(self):
        try:
            if self.status and self.detaillist != '':
                self.ScanPayItem(self.detaillist, parent=self.parent)
        except:
            return False
        if self.specialdatelist: self.ParseSpecialDate()

        return True

    def GetText(self, node):
        for child in node.childNodes:
            if Node.TEXT_NODE == child.nodeType:
                return child.wholeText

    def MakeRows(self, h):
        self.priority += 1
        name = h['name']
        has_item = Item.objects.filter(name=name, uplevel=h['parent'])
        while has_item:
            name = '複製-' + name
            has_item = Item.objects.filter(name=name, uplevel=h['parent'])

        item = Item(unit_num=h['unit_num'], unit_price=h['unit_price'],
            unit_name=h['unit_name'], name=name,kind=self.dirkind,
            uplevel=h['parent'], version=self.version)

        try:
            item.priority = Item.objects.filter(uplevel=h['parent']).order_by('-priority')[0].priority + 1
        except:
            item.priority = 0

        item.save()
        return item

    def ScanPayItem(self, node, parent=''):
        h = {'parent': parent}
        isSum = False
        isDir = False
        if Node.ELEMENT_NODE == node.nodeType:
            for child in node.childNodes:
                if Node.ELEMENT_NODE == child.nodeType and 'PayItem' != child.tagName:
                    if 'Quantity' == child.tagName:
                        h['unit_num'] = self.GetText(child)
                    elif 'es' == child.tagName:
                        h['es'] = float(self.GetText(child))
                    elif 'ef' == child.tagName:
                        h['ef'] = float(self.GetText(child))
                    elif 'Price' == child.tagName:
                        h['unit_price'] = self.GetText(child)
                    elif 'Unit' == child.tagName and 'zh-TW' == child.getAttribute('language'):
                        h['unit_name'] = self.GetText(child).replace('&lt;', '<').replace('&gt;', '>')
                    elif 'Description' == child.tagName and 'zh-TW' == child.getAttribute('language'):
                        description = self.GetText(child)
                        if re.search(u"總[價計]", description) and self.parent == parent:
                            isSum = True
                        else:
                            h['name'] = description.replace('&lt;', '<').replace(
                                '&gt;', '>').replace('\r', '').replace('\n', '')

        if h.has_key('name') and (u'小計' == h['name'] or u'合計' == h['name']):
            return False
            
        if isSum == False and h.has_key('name'): parent = self.MakeRows(h)

        if node.hasChildNodes:
            for child in node.childNodes:
                if Node.ELEMENT_NODE == child.nodeType and 'PayItem' == child.tagName:
                    isDir = True
                    self.ScanPayItem(child, parent=parent)
            if isDir == False and parent != self.parent:
                self.SetItem(parent, h)


    def SetItem(self, item, h):
        item.kind = self.item_kind
        if h.get('es', 0) == 0: h['es'] = 1
        if h.get('ef', 0) == 0: h['ef'] = 1
        item.es = h['es']
        item.ef = h['ef']
        item.save()


def _testparsePCCES():
    project = Project.objects.all()[0]
    file = open('pcces.xml')
    version = project.dailyreport_version.latest()
    pp = ParsePCCES(file.read(), project, version)
    pp.Parse()
    #pp.ClearParent() #清除最上層的目錄