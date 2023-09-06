# -*- coding: utf8 -*-
from django.utils.translation import ugettext as _
from django.db import models as M
from common.models import SelfBaseObject
import re


UNITS = []

def LOAD_UNITS():
    if not UNITS:
        for i in Unit.fish_city_menu.all():
            UNITS.append(i)
            if i.uplevel and i.uplevel.name != u'縣市政府':
                UNITS.extend([j for j in i.uplevel_subunit.all()])
    return UNITS



class Option(M.Model):
    swarm= M.CharField(verbose_name=u'群', max_length=32)
    value = M.CharField(verbose_name=u'選項', max_length=64)

    def __unicode__(self):
        return self.value


    class Meta:
        verbose_name = u'選項'
        verbose_name_plural = u'選項'
        unique_together = (("swarm", "value"),)


class Place(M.Model):
    name = M.CharField(verbose_name=_(u'區域名稱'), null=False, max_length=128)
    zipcode = M.CharField(verbose_name=_(u'郵遞區號'), max_length=20)
    uplevel = M.ForeignKey('self', null=True, related_name='uplevel_subregion')
    update_time = M.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.name

    def rChildSetInList(self):
        list = [self]
        child_set = self.uplevel_subregion.order_by('zipcode', 'id')
        if child_set:
            dev_nul = [list.extend(c.rChildSetInList()) for c in child_set]
        return list

    def rHash(self):
        return {'id': self.id, 'name': self.name, 'zipcode': self.zipcode,
            'uplevel': self. uplevel}

    def rHashInHtml(self):
        hash = self.rHash()
        hash['uplevel_id'] = hash['uplevel'].id if hash['uplevel'] else ''
        del hash['uplevel']
        return hash

    def getFullPlace(self, ceilplace=''):
        place = self
        places = []
        while place != None and place != place.uplevel and place != ceilplace:
            places.insert(0, place.name)
            place = place.uplevel
        if places: return places
        else: return False

    def findPlace(self, address):
        #address = re.sub(u'^臺', u'台', unicode(address))
        place = self.__class__.objects.get(name=u'臺灣地區')
        for add in address.split(' '):
            try:
                place = place.uplevel_subregion.get(name=add)
            except self.__class__.DoesNotExist:
                return place
        return place

    class Meta:
        ordering = (u'name',)
        verbose_name = _(u'區域名')
        verbose_name_plural = _(u'區域名')


class FishCityMenuManager(M.Manager):
    def get_queryset(self):
        list = []
        for i in super(FishCityMenuManager, self).get_queryset().filter(
            uplevel__name__in=[u'漁業署']).order_by('-uplevel', 'id'):
            list.append(i)
        for i in super(FishCityMenuManager, self).get_queryset().filter(
            uplevel__name__in=[u'縣市政府']).order_by('-uplevel', 'id'):
            list.append(i)
        for i in super(FishCityMenuManager, self).get_queryset().filter(
            uplevel__name__in=[u'臺灣省漁會']).order_by('-uplevel', 'id'):
            list.append(i)
        return list


class Unit(M.Model, SelfBaseObject):
    name = M.CharField(verbose_name='名稱', null=False, max_length=128)
    fullname = M.CharField(verbose_name='全名', null=False, max_length=256)
    no = M.CharField(verbose_name='統一編號', null=False, unique=True, max_length=8)
    chairman = M.CharField(verbose_name='負責人', null=True, max_length=64)
    capital = M.PositiveIntegerField(null=True)
    kind = M.ForeignKey(Option, verbose_name='組織種類', null=True)
    birthday = M.DateField(verbose_name='設立日期', null=True)
    operation = M.TextField(verbose_name='營業項目', null=True)
    html = M.TextField(verbose_name='輸入 html 碼', null=True)
    place = M.ForeignKey(Place)
    address = M.CharField(verbose_name='地址', null=True, max_length=256)
    phone = M.CharField(verbose_name='電話', null=True, max_length=20)
    fax = M.CharField(verbose_name='傳真', null=True, max_length=20)
    website = M.URLField(verbose_name='網址', null=True)
    email = M.EmailField(verbose_name='E-mail', null=True)
    uplevel = M.ForeignKey('self', null=True, related_name='uplevel_subunit')

    objects = M.Manager()
    fish_city_menu = FishCityMenuManager()

    def __unicode__(self):
        return self.name

    def rChildSetInList(self):
        list = [self]
        child_set = self.uplevel_subunit.order_by('id')
        if child_set:
            dev_nul = [list.extend(c.rChildSetInList()) for c in child_set]
        return list

    def rIsRightNo(self):
        if u'無法解析' in self.name or u'無法解析' in self.fullname: return False
        else: return True

    def rNonParseNo(self):
        return self.__class__.objects.filter(name__startswith=u'尚未解析統編')

    def cUnit(self):
        self.name = u'未知'
        self.fullname = u'未知'
        self.place = Place.objects.get(name=u'臺灣地區')
        self.save()
        return self.id

    def rFullUnit(self, ceilunit=''):
        unit = self
        units = []
        while unit != None and unit != unit.uplevel and unit != ceilunit:
            units.insert(0, unit.name)
            unit = unit.uplevel
        if units: return units
        else: return False


    class Admin:
        list_display   = ('name', 'no', 'fullname', 'address', 'phone', 'fax'
            , 'place', 'website', 'email', 'uplevel', )
        list_filter    = ('uplevel',)
        ordering       = ('fullname', 'name',)
        search_fields  = ('name', 'no', 'email', 'phone', 'fax', 'address',)

    class Meta:
        ordering = ('fullname', 'name')
        verbose_name = u'公司機關單位'
        verbose_name_plural = u'公司機關單位'




