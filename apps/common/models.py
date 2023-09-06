# -*- coding:utf8 -*-
from django.utils.translation import ugettext as _
from django.db import models as M
from django.db.models import Count
from django.db.models.fields.related import ForeignKey
from django.db.models.fields import DecimalField
from django.db.models.fields import DateField
from django.db.models.fields import DateTimeField
from django.db.models.signals import post_save
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from types import ListType
from types import IntType
from types import LongType
from types import FloatType
from types import BooleanType
from types import StringType
from types import UnicodeType
from types import DictionaryType

from random import randint
from random import choice
import cPickle
import decimal
import datetime
import re
import json
if not hasattr(json, "write"):
    #for python2.6
    json.write = json.dumps
    json.read = json.loads


class JsonModel(object):
    def rJSON(self):
        dict = {}
        for f in self._meta.fields:
            dict[f.name] = ''
            try: value = getattr(self, f.name)
            except: value = None
            if not value: continue

            dict[f.name] = value

            if isinstance(f, ForeignKey):
                dict['%s_id'%f.name] = value.id
                if dict.has_key(f.name): del dict[f.name]
            elif isinstance(f, DecimalField):
                dict[f.name] = str(value)
            elif isinstance(f, DateField):
                dict[f.name] = value.strftime('%Y-%m-%d')
            elif isinstance(f, DateTimeField):
                dict[f.name] = value.strftime('%Y-%m-%d %H:%M:%S')

        return dict


class HolidayTypeManager(M.Manager):
    def get_query_set(self):
        return super(HolidayTypeManager,
            self).get_query_set().filter(swarm=u'holiday', value=u'假日')


class ForceWorkTypeManager(M.Manager):
    def get_query_set(self):
        return super(ForceWorkTypeManager,
            self).get_query_set().filter(swarm=u'holiday', value=u'強制開工')


class DifferentTypeError(Exception):
    """ 儲存在 StoreModel 的資料，對同一個 ExpandoModel object 來說，
    若 key 值相同，則 value 的型別必須相同。但對'''不同'''的 ExpandoModel object
    則不須相同。

    >>> p = ProjectExpandoModel.object.get(id=1)
    >>> print p.yyy
    'sss'
    >>> p.yyy = 30
    >>> p.save()
    raise DifferentTypeError
    >>> p2 = ProjectExpandoModel.object.get(id=2)
    >>> p2.yyy = 30
    >>> p.save()
    >>> print p2.yyy
    30
    """
    pass


class ForeignKeyType:
    """ 將 ForeignKey 的值轉成本物件，再存在 StoreModel 中。
    """
    def __init__(self, object):
        self.model, self.pk = object.__class__, object.pk

    def getObject(self):
        return self.model.objects.get(pk=self.pk)


class StoreModel(M.Model):
    """ 儲存任意類型的資料。本 Model 不會產生真正的資料表。使用上，
    一定是要用繼承的方式去創建另一個「會生成資料表的 Model」，
    然後拿那個 Model 專屬給有浮動欄位的 Model(也就是繼承 ExpandoModel 的子 Model)
    用。以下有兩個範例： PStoreModel, ProjectExpandoModel 以及
    HStoreModel, HarborExpandoModel 。

    save() 乃將 value 的原值，轉成 cPickle 格式。但在存檔前，先檢查 self.value
    是不是 Pickle 格式，如果是，則不會再次轉換成 String ; 如果否，則作 Pickle 轉換。

    >>> sm = StoreModel(name='test', value=30)
    >>> sm.save()
    >>> print sm.value
    'I30\n.'
    >>> sm.save() #未重後賦值，就作 save() ，'''不'''會將 value 改成 StringType
    >>> print sm.value
    'I30\n.'
    >>> sm.value = datetime.date(2010, 1, 1)
    >>> sm.save()
    >>> print sm.value
    "cdatetime\ndate\np1\n(S'\\x07\\xda\\x01\\x01'\ntRp2\n."
    """
    name = M.CharField(verbose_name=u'欄位名稱', max_length=255)
    value = M.CharField(verbose_name=u'值', null=True, max_length=512)


    class Meta:
        abstract = True


    @classmethod
    def rAllKeys(self):
        keys = []
        result = self.objects.values('name').annotate(Count('name'))
        dev_null = [keys.append(n['name']) for n in result if n['name'] not in keys]
        return keys

    def convertValue(self):
        value = cPickle.loads(str(self.value))
        if isinstance(value, ForeignKeyType): value = value.getObject()
        return value

    def save(self):
        """ 檢查 self.value 是不是 Pickle 格式，如果不是，才轉 Pickle
        """
        try:
            cPickle.loads(str(self.value))
        except cPickle.UnpicklingError:
            self.value = cPickle.dumps(self.value)
        super(StoreModel, self).save()


class ExpandoModel(M.Model):
    """ 本類別主要是供其他類別繼承的，並不直接使用。也不會產生真正的資料表。
    本類別可讓繼承類別擁有浮動的資料表欄位。但浮動欄位的名稱必須是 '_f_' 開頭，
    或是有中文字。

    本類別的浮動(onfly)欄位功能乃是使用與 StoreModel 作 ManyToMany Relation 而來的。
    而且欄位一定要叫 extra_fields

    使用方式如下：
    >>> em = XXXExpandoModel.object.get(id=1) # XXXExpandoModel 必須作一欄位設定
                                               # extra_fields = M.ManyToMany(XXXStoreModel)
    >>> setattr(em, '_f_xxx', 'yyy')
    >>> em.save() #這樣就會在 XXXStoreModel 中多一筆紀錄(name=u'xxx', value=u"S'yyy'\np1\n.")
    >>> print getattr(em, '_f_xxx')
    'yyy'
    >>> setattr(em, '_f_foreigh_key', Option.objects.get(id=1))
    >>> em.save()
    >>> em1 = XXXExpandoModel.object.get(id=1)
    >>> Option.objects.get(id=1) == getattr(em1, '_f_foreigh_key')
    True

    整個類別的運作機制是在 setattr(em, '_f_xxx', 'yyy') 時，將 '_f_xxx' 登記到
    READY_TO_SAVE_KEY_NAMES 的 list 上，
    待 em.save() 執行時，將 READY_TO_SAVE_KEY_NAMES 中有存在的 key 值抓出來，
    然後創造相對應的 XXXStoreModel(某個繼承 StoreModel 的子類別)。

    另外，本類別一被實例化，則會把它的相對應 XXXStoreModel object 紀錄抓出來並放到
    EXTRA_FIELDS 中。
    >>> em = ExpandoModel.object.get(id=1)
    >>> print em.EXTRA_FIELDS
    {u'_f_xxx': 'yyy'}
    """
    READY_TO_SAVE_KEY_NAMES = []
    EXTRA_FIELDS = {}

    class Meta:
        abstract = True


    def __init__(self, *args, **kw):
        self.READY_TO_SAVE_KEY_NAMES = []
        self.EXTRA_FIELDS = {}

        super(ExpandoModel, self).__init__(*args, **kw)

        if hasattr(self, 'id') and self.id:
            for ef in self.extra_fields.all():
                self.EXTRA_FIELDS[str(ef.name)] = ef.convertValue()

    def __setattr__(self, key, value):
        if (
            (re.match('^_f_', key) or not re.match('[a-zA-Z_0-9]+', key))
            and key not in self.READY_TO_SAVE_KEY_NAMES):
            self.READY_TO_SAVE_KEY_NAMES.append(key)
        super(ExpandoModel, self).__setattr__(key, value)

    def __getattr__(self, key):
        key = str(key)
        if key in self.EXTRA_FIELDS.keys():
            return self.EXTRA_FIELDS[key]
        else:
            return super(ExpandoModel, self).__getattr__(key)

    def uKeyByNewTypeValue(self, key, value):
        ef = self.extra_fields.get(name=key)
        ef.value = value
        ef.save()
        self.EXTRA_FIELDS[str(key)] = value

    def dKey(self, key):
        try:
            ef = self.extra_fields.get(name=key)
        except self.extra_fields.model.DoesNotExist:
            pass
        else:
            ef.delete()
            delattr(self, key)
            del self.EXTRA_FIELDS[str(key)]

    def save(self):
        if self.READY_TO_SAVE_KEY_NAMES and (not hasattr(self, 'id') or not self.id):
            super(ExpandoModel, self).save()

        while self.READY_TO_SAVE_KEY_NAMES:
            key = self.READY_TO_SAVE_KEY_NAMES.pop(0)
            new_value = getattr(self, key)
            if hasattr(new_value, '__metaclass__') and new_value.__metaclass__ == M.Model.__metaclass__:
                new_value = ForeignKeyType(new_value)

            try:
                ef = self.extra_fields.get(name=key)
            except self.extra_fields.model.DoesNotExist:
                sm = self.extra_fields.model(name=key, value=new_value)
                sm.save()
                self.extra_fields.add(sm)
            else:
                if type(ef.convertValue()) != type(new_value):
                    raise DifferentTypeError('%s != %s'%(ef.value, new_value))
                ef.value = new_value
                ef.save()
            self.EXTRA_FIELDS[str(key)] = getattr(self, key)

        super(ExpandoModel, self).save()


#跑 ./manage.py test common 時，必須打開註解
#class ForCompareExpandoModel(M.Model):
#    note1 = M.IntegerField()
#    note2 = M.IntegerField()
#    note3 = M.IntegerField()
#    note4 = M.IntegerField()
#    note5 = M.IntegerField()
#    note6 = M.IntegerField()
#    note7 = M.IntegerField()
#    note8 = M.IntegerField()
#    note9 = M.IntegerField()
#    note10 = M.IntegerField()
#    note11 = M.IntegerField()
#    note12 = M.IntegerField()
#    note13 = M.IntegerField()
#    note14 = M.IntegerField()
#    note15 = M.IntegerField()
#    note16 = M.IntegerField()
#    note17 = M.IntegerField()
#    note18 = M.IntegerField()
#    note19 = M.IntegerField()
#    note20 = M.IntegerField()
#    note21 = M.IntegerField()
#    note22 = M.IntegerField()
#    note23 = M.IntegerField()
#    note24 = M.IntegerField()
#    note25 = M.IntegerField()
#    note26 = M.IntegerField()
#    note27 = M.IntegerField()
#    note28 = M.IntegerField()
#    note29 = M.IntegerField()
#    note30 = M.IntegerField()
#    note31 = M.IntegerField()
#    note32 = M.IntegerField()
#    note33 = M.IntegerField()
#    note34 = M.IntegerField()
#    note35 = M.IntegerField()
#    note36 = M.IntegerField()
#    note37 = M.IntegerField()
#    note38 = M.IntegerField()
#    note39 = M.IntegerField()
#    note40 = M.IntegerField()
#    note41 = M.IntegerField()
#    note42 = M.IntegerField()
#    note43 = M.IntegerField()
#    note44 = M.IntegerField()
#    note45 = M.IntegerField()
#    note46 = M.IntegerField()
#    note47 = M.IntegerField()
#    note48 = M.IntegerField()
#    note49 = M.IntegerField()
#    note50 = M.IntegerField()
#    note51 = M.IntegerField()
#    note52 = M.IntegerField()
#    note53 = M.IntegerField()
#    note54 = M.IntegerField()
#    note55 = M.IntegerField()
#    note56 = M.IntegerField()
#    note57 = M.IntegerField()
#    note58 = M.IntegerField()
#    note59 = M.IntegerField()
#    note60 = M.IntegerField()
#    note61 = M.IntegerField()
#    note62 = M.IntegerField()
#    note63 = M.IntegerField()
#    note64 = M.IntegerField()
#    note65 = M.IntegerField()
#    note66 = M.IntegerField()
#    note67 = M.IntegerField()
#    note68 = M.IntegerField()
#    note69 = M.IntegerField()
#    note70 = M.IntegerField()
#    note71 = M.IntegerField()
#    note72 = M.IntegerField()
#    note73 = M.IntegerField()
#    note74 = M.IntegerField()
#    note75 = M.IntegerField()
#    note76 = M.IntegerField()
#    note77 = M.IntegerField()
#    note78 = M.IntegerField()
#    note79 = M.IntegerField()
#    note80 = M.IntegerField()
#    note81 = M.IntegerField()
#    note82 = M.IntegerField()
#    note83 = M.IntegerField()
#    note84 = M.IntegerField()
#    note85 = M.IntegerField()
#    note86 = M.IntegerField()
#    note87 = M.IntegerField()
#    note88 = M.IntegerField()
#    note89 = M.IntegerField()
#    note90 = M.IntegerField()
#    note91 = M.IntegerField()
#    note92 = M.IntegerField()
#    note93 = M.IntegerField()
#    note94 = M.IntegerField()
#    note95 = M.IntegerField()
#    note96 = M.IntegerField()
#    note97 = M.IntegerField()
#    note98 = M.IntegerField()
#    note99 = M.IntegerField()
#    note100 = M.IntegerField()
#    note101 = M.IntegerField()
#    note102 = M.IntegerField()
#    note103 = M.IntegerField()
#    note104 = M.IntegerField()
#    note105 = M.IntegerField()
#    note106 = M.IntegerField()
#    note107 = M.IntegerField()
#    note108 = M.IntegerField()
#    note109 = M.IntegerField()
#    note110 = M.IntegerField()
#    note111 = M.IntegerField()
#    note112 = M.IntegerField()
#    note113 = M.IntegerField()
#    note114 = M.IntegerField()
#    note115 = M.IntegerField()
#    note116 = M.IntegerField()
#    note117 = M.IntegerField()
#    note118 = M.IntegerField()
#    note119 = M.IntegerField()
#    note120 = M.IntegerField()
#    note121 = M.IntegerField()
#    note122 = M.IntegerField()
#    note123 = M.IntegerField()
#    note124 = M.IntegerField()
#    note125 = M.IntegerField()
#    note126 = M.IntegerField()
#    note127 = M.IntegerField()
#    note128 = M.IntegerField()
#    note129 = M.IntegerField()
#    note130 = M.IntegerField()
#    note131 = M.IntegerField()
#    note132 = M.IntegerField()
#    note133 = M.IntegerField()
#    note134 = M.IntegerField()
#    note135 = M.IntegerField()
#    note136 = M.IntegerField()
#    note137 = M.IntegerField()
#    note138 = M.IntegerField()
#    note139 = M.IntegerField()
#    note140 = M.IntegerField()
#    note141 = M.IntegerField()
#    note142 = M.IntegerField()
#    note143 = M.IntegerField()
#    note144 = M.IntegerField()
#    note145 = M.IntegerField()
#    note146 = M.IntegerField()
#    note147 = M.IntegerField()
#    note148 = M.IntegerField()
#    note149 = M.IntegerField()
#    note150 = M.IntegerField()
#    note151 = M.IntegerField()
#    note152 = M.IntegerField()
#    note153 = M.IntegerField()
#    note154 = M.IntegerField()
#    note155 = M.IntegerField()
#    note156 = M.IntegerField()
#    note157 = M.IntegerField()
#    note158 = M.IntegerField()
#    note159 = M.IntegerField()
#    note160 = M.IntegerField()
#    note161 = M.IntegerField()
#    note162 = M.IntegerField()
#    note163 = M.IntegerField()
#    note164 = M.IntegerField()
#    note165 = M.IntegerField()
#    note166 = M.IntegerField()
#    note167 = M.IntegerField()
#    note168 = M.IntegerField()
#    note169 = M.IntegerField()
#    note170 = M.IntegerField()
#    note171 = M.IntegerField()
#    note172 = M.IntegerField()
#    note173 = M.IntegerField()
#    note174 = M.IntegerField()
#    note175 = M.IntegerField()
#    note176 = M.IntegerField()
#    note177 = M.IntegerField()
#    note178 = M.IntegerField()
#    note179 = M.IntegerField()
#    note180 = M.IntegerField()
#    note181 = M.IntegerField()
#    note182 = M.IntegerField()
#    note183 = M.IntegerField()
#    note184 = M.IntegerField()
#    note185 = M.IntegerField()
#    note186 = M.IntegerField()
#    note187 = M.IntegerField()
#    note188 = M.IntegerField()
#    note189 = M.IntegerField()
#    note190 = M.IntegerField()
#    note191 = M.IntegerField()
#    note192 = M.IntegerField()
#    note193 = M.IntegerField()
#    note194 = M.IntegerField()
#    note195 = M.IntegerField()
#    note196 = M.IntegerField()
#    note197 = M.IntegerField()
#    note198 = M.IntegerField()
#    note199 = M.IntegerField()
#    note200 = M.IntegerField()


#跑 ./manage.py test common 時，必須打開註解
#class PStoreModel(StoreModel):
#    pass


#跑 ./manage.py test common 時，必須打開註解
#class ProjectExpandoModel(ExpandoModel):
#    """
#    >>> try:
#    >>>     o = ProjectExpandoModel.objects.get(id=1)
#    >>> except ProjectExpandoModel.DoesNotExist:
#    >>>     o = ProjectExpandoModel(no='no%s'%random.random(), name=u'隨便的名稱')
#    >>> # ProjectExpandoModel 只有 no, name 是手動設定的。
#    >>> key, value = 'attr%s'%random.randint(0, 10000), random.random()
#    >>> setattr(o, key, value)
#    >>> o.integer = 1333
#    >>> o.float = 499.99
#    >>> o.datetime = datetime(2010, 9, 10, 12, 32, 45)
#    >>> # 若要設定的屬性，其名稱是多位元組(就是中文)，要用 setattr 而不能用 o.測試 = 'whatever~~'
#    >>> setattr(o, u'測試', 'whatever~~')
#    >>> o.save() # 這樣就會在 StoreModel 中，生成 5 筆紀錄。
#    >>>
#    """
#    no = M.CharField(verbose_name=u'序號', unique=True, max_length=255)
#    name = M.CharField(verbose_name=u'名稱', max_length=255)
#    extra_fields = M.ManyToManyField(PStoreModel, verbose_name=u'額外欄位')


#只是示範用
#class HStoreModel(StoreModel):
#    pass


#只是示範用
#class HarborExpandoModel(ExpandoModel):
#    """ 請參考 ProjectExpandoModel
#    """
#    name = M.CharField(verbose_name=u'名稱', unique=True, max_length=255)
#    extra_fields = M.ManyToManyField(HStoreModel, verbose_name=u'額外欄位')


class Option(M.Model):
    swarm= M.CharField(verbose_name=u'群', max_length=32)
    value = M.CharField(verbose_name=u'選項', max_length=64)

    def __unicode__(self):
        return self.value

    class Meta:
        unique_together = (("swarm", "value"),)


class HolidayManager(M.Manager):
    def get_query_set(self):
        return super(HolidayManager, self).get_query_set().filter(
            type=Option.objects.get(swarm=u'holiday', value=u'假日')).order_by('date')


class ForceWorkManager(M.Manager):
    def get_query_set(self):
        return super(ForceWorkManager, self).get_query_set().filter(
            type=Option.objects.get(swarm=u'holiday', value=u'強制開工')).order_by('date')

class Holiday(M.Model):
    name = M.CharField(verbose_name=u'名稱', max_length=256)
    type = M.ForeignKey(Option, related_name=u'dailyreport_holiday_type')
    date = M.DateField(verbose_name=u'日期')
    holiday_set = HolidayManager()
    force_work_set = ForceWorkManager()
    objects = M.Manager()

    def __unicode__(self):
        return self.name

    class Meta:
        pass


class VerifyCode(M.Model):
    key = M.CharField(verbose_name=u'圖片上所顯現的碼', max_length=32)
    isdone = M.BooleanField(verbose_name=u'是否使用過', default=False)


#> > >
#try:
#    CREATETYPE = Option.objects.get(swarm=u'log_type', value=u'新增')
#    UPDATETYPE = Option.objects.get(swarm=u'log_type', value=u'修改')
#    DELETETYPE = Option.objects.get(swarm=u'log_type', value=u'刪除')
#    SELECTTYPE = Option.objects.get(swarm=u'log_type', value=u'顯示')
#except:
#    pass
## 莫明奇妙的現象，如果我使用上面四個變數，將會導致在跑 user_profile 函式時，
## 無法找到相對應的 model 物件 UserProfile 。其出現錯誤訊息如下：
## """ AttributeError at /dailyreport/contractor/13545/
## 'NoneType' object has no attribute '_default_manager'
## Request Method:GET
## Request URL:http://rcm5/dailyreport/contractor/13545/
## Exception Type:AttributeError
## Exception Value:'NoneType' object has no attribute '_default_manager'
## Exception Location:/usr/lib/python2.5/site-packages/django/contrib/auth/models.py in get_profile, line 249 """
#< < <


class Log(M.Model):
    content_type = M.ForeignKey(ContentType, null=True)
    user = M.ForeignKey(User, null=True)
    log_type = M.ForeignKey(Option)
    create_time = M.DateTimeField(verbose_name=u'紀錄時間', auto_now_add=True)
    object_id = M.IntegerField(verbose_name=u'物件編號')
    object_repr = M.TextField(verbose_name=u'物件描述')
    action_repr = M.CharField(verbose_name=u'執行動作的描述', max_length=256)

    def makeHTTP500Log(self,  user=None, bug_page=None, url=''):
        if not bug_page or not url: return False

        self.content_type = ContentType.objects.get_for_model(BugPage)
        if user.__class__ == User: self.user = user
        self.log_type = Option.objects.get(swarm=u'log_type', value=u'HTTP500')
        self.object_id = bug_page.id
        self.object_repr = '%s:%s'%(bug_page.code, url)
        self.action_repr = 'HTTP500'
        self.save()
        return True

    def makeHTTP404Log(self,  user=None, referer='', url=''):
        if not referer or not url: return False

        if user.__class__ == User:
            self.user = user
            user_id = self.user.id
        else:
            user_id = 0
        self.log_type = Option.objects.get(swarm=u'log_type', value=u'HTTP404')
        self.object_id = int(
            '%s%02d%05d' % (
                datetime.datetime.now().strftime('%H'),
                randint(0, 99),
                user_id
            )
        )
        self.object_repr = '%s=>%s' % (referer, url)
        self.action_repr = 'HTTP404'
        self.save()
        return True

    def makeCreateLog(self, content_type=u'', user=u'', object_id=u'', action_repr=u'', **newvalue):
        if type(content_type) == IntType or type(content_type) == LongType:
            content_type = ContentType.objects.get(id=content_type)
        try:
            create_type = Option.objects.get(swarm=u'log_type', value=u'新增')
            if not content_type.selfmetamodel_set.get().log_type.filter(id=create_type.id):
                return False
        except:
            return False

        if newvalue: object_repr = json.write(newvalue)[1:-1]
        else: object_repr = ''

        self.content_type=content_type
        if user.__class__ == User: self.user = user
        self.log_type=create_type
        self.object_id=object_id
        self.object_repr=object_repr
        self.action_repr=action_repr
        self.save()

        return True

    def makeUpdateLog(self, content_type=u'', user=u'', object_id=u'', ori=u'', new=u'', action_repr=u''):
        if type(content_type) == IntType or type(content_type) == LongType:
            content_type = ContentType.objects.get(id=content_type)
        try:
            update_type = Option.objects.get(swarm=u'log_type', value=u'修改')
            if not content_type.selfmetamodel_set.get().log_type.filter(id=update_type.id):
                return False
        except:
            return False

        object_repr = '%s>%s' % (ori, new)

        self.content_type=content_type
        if user.__class__ == User: self.user = user
        self.log_type=update_type
        self.object_id=object_id
        self.object_repr=object_repr
        self.action_repr=action_repr
        self.save()

        return True

class SelfMetaModel(M.Model):
    content_type = M.ForeignKey(ContentType)
    arriveat_user = M.CharField(verbose_name=u'以逗號分隔的欄位名，紀錄如何找到 User', max_length=128)
    log_type = M.ManyToManyField(Option)


#TODO 想使用 __metaclass__ 來創建 getXXX, setXXX 方法。
#def _addMethod(fldName, clsName, verb, methodMaker, dict):
#    """Make a get or set method and add it to dict."""
#    compiledName = _getCompiledName(fldName, clsName)
#    methodName = _getMethodName(fldName, verb)
#    dict[methodName] = methodMaker(compiledName)
#
#def _getCompiledName(fldName, clsName):
#    """Return mangled fldName if necessary, else no change."""
#    # If fldName starts with 2 underscores and does *not* end with 2 underscores...
#    if fldName[:2] == '__' and fldName[-2:] != '__':
#        return "_%s%s" % (clsName, fldName)
#    else:
#        return fldName

#def _getMethodName(fldName, verb):
#    """'_salary', 'get'  => 'getSalary'"""
#    s = fldName.lstrip('_') # Remove leading underscores
#    return verb + s.capitalize()

#def _makeGetter(compiledName):
#    """Return a method that gets compiledName's value."""
#    return lambda self: self.__dict__[compiledName]
#    #value =  str(lambda self: self.__dict__[compiledName])
#    #if value == 'None': value = ''
#    #return value

#def _makeSetter(compiledName):
#    """Return a method that sets compiledName's value."""
#    return lambda self, value: setattr(self, compiledName, value)

#class Accessors(type):
#    """Adds accessor methods to a class."""
#    def __new__(cls, clsName, bases, dict):
#        for fldName in dict.get('_READ', []) + dict.get('_READ_WRITE', []):
#            _addMethod(fldName, clsName, 'get', _makeGetter, dict)
#        for fldName in dict.get('_WRITE', []) + dict.get('_READ_WRITE', []):
#            _addMethod(fldName, clsName, 'set', _makeSetter, dict)
#        return type.__new__(cls, clsName, bases, dict)


class SelfBaseObject(object):
    def getContentTypeId(self):
        app_label = self._meta.app_label
        model = self._meta.model_name
        try:
            self.content_type_id = ContentType.objects.get(app_label=app_label, model=model).id
            return self.content_type_id
        except ContentType.DoesNotExist:
            return False

    def validateUser(self, u):
        list = self.getUsers()
        if u in list: return True
        elif len(list) > 0 and list[0] == 'novalidate': return True
        else: return False

    def getUsers(self):
        if not hasattr(self, 'content_type_id'): self.getContentTypeId()

        try:
            smm = SelfMetaModel.objects.get(content_type__id=self.content_type_id)
        except SelfMetaModel.DoesNotExist:
            return []

        if smm.arriveat_user.lower() == 'novalidate':
            return ['novalidate']
        else:
            obj = self
            for s in smm.arriveat_user.split(','):
                if s == 'userprofile_set.all()':
                    return [u.user for u in getattr(obj, 'userprofile_set').all()]
                else:
                    obj = getattr(obj, s)

            if type(obj) == ListType:
                if obj[0].__class__ == User:
                    return obj
            else:
                if obj.__class__ == User:
                    return [obj]

            return []


class CustomField(M.Model):
    content_type = M.ForeignKey(ContentType)
    object_id = M.IntegerField(verbose_name=u'在 content_type 中的 row id')
    field_name = M.CharField(verbose_name=u'欄位名稱', max_length=64)
    value = M.CharField(max_length=256)


class BugPage(M.Model, SelfBaseObject):
    code = M.CharField(verbose_name=u'錯誤碼代碼', max_length=4, null=True)
    create_time = M.DateTimeField(verbose_name=u'紀錄時間', auto_now_add=True)
    html = M.TextField(verbose_name=u'除錯頁面內容')
    is_solved = M.BooleanField(verbose_name=u'是否解決', default=False)

    def rTitle(self):
        s = re.findall('<title>(.*)</title>', self.html)
        if s:
            return s[0]
        else:
            return u'無 Title'

    def rDescribe(self):
        s = re.findall('<pre class="exception_value">(.*)</pre>', self.html)
        if s:
            return s[0]
        else:
            return u'無描述'

LETTER_SET = ('2', '3', '5', '6', '8', '9', 'A', 'J', 'K', 'L', 'N', 'Y', 'Z')
def rBugCode(sender=None, instance=None, **kw):
    if instance.code: return
    instance.code = ''.join([choice(LETTER_SET) for i in xrange(4)]).upper()
    instance.save()

post_save.connect(rBugCode, sender=BugPage)
