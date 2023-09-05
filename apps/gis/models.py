#-*- coding:utf8 -*-
from django.db import models as M
from django.db.models import Q
from django.contrib.sessions.models import Session
import datetime
import os
from PIL import Image
from types import IntType
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from settings import WRONGLOGINTIMELIMIT
from settings import WRONGLOGINDURATION
from harbor.models import FishingPort


_UPLOAD_TO = os.path.join('apps', 'gis', 'media', 'gis', 'photo', '%Y%m%d')
class PortPhotos(M.Model):
    fishingport = M.ForeignKey(FishingPort, verbose_name='漁港', null=True)
    lat = M.DecimalField(verbose_name=u'緯度', null=True , max_digits=16 , decimal_places=9)
    lng = M.DecimalField(verbose_name=u'經度', null=True , max_digits=16 , decimal_places=9)
    name = M.CharField(verbose_name=u'標題', max_length=254, null=True)
    memo = M.CharField(verbose_name=u'備註', max_length=4096, null=True)
    file = M.ImageField(upload_to=_UPLOAD_TO, null=True)
    uploader = M.ForeignKey(User, verbose_name=u'上傳者')
    uploadtime = M.DateTimeField(verbose_name=u'上傳時間', null=True)
    shoot_time = M.DateTimeField(verbose_name=u'拍照時間', null=True)
    priority = M.IntegerField(verbose_name=u'優先權', null=True)
    disable = M.BooleanField(verbose_name=u'刪除紀錄', default=0)

    def rUrl(self):
        return self.file.name.split('apps/gis')[-1]

    def rThumbUrl(self):
        file = self.file.name.split('/')[-1]
        src = self.file.name.split('apps/gis')[-1].replace(file, str(self.id) + '_w320h240.jpg')
        return src