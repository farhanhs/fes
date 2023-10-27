# -*- coding:utf8 -*-
from django.db import models as M
from django.contrib.auth.models import User
from general.models import Place
from harbor.models import FishingPort



class Option(M.Model):
    swarm= M.CharField(verbose_name='群', max_length=32)
    value = M.CharField(verbose_name='選項', max_length=64)

    def __unicode__(self):
        return '%s-%s' % (self.swarm, self.value)

    class Meta:
        verbose_name = '選項'
        verbose_name_plural = '選項'
        unique_together = (("swarm", "value"),)


class Monitor(M.Model):
    machine_no = M.CharField(verbose_name=u'供應機型', choices=(('BE3204', 'BE3204'), ('PELCO-O', 'PELCO-O')), null=False, max_length=16)# 新增欄位， for 不同機型須有不同的直播方法
    place = M.ForeignKey(Place, verbose_name='縣市', null=True)
    port = M.ForeignKey(FishingPort, verbose_name='漁港', null=True)
    #nvr_id = M.IntegerField(verbose_name=u'NVR 系統編號', null=False)# 新增欄位，不限藍眼機器使用，如果將來我們會買其他人的 NVR 的話(這怎麼可能!!! 我們會自己作 NVR)
    name = M.CharField(verbose_name='名稱', null=True, max_length=512)
    #channel = M.CharField(verbose_name='廣播頻道', null=True, max_length=512)# 新增欄位，它似乎可視為機器的 UUID
    location = M.CharField(verbose_name='位置敘述', null=True, max_length=512)
    video_url = M.CharField(verbose_name='影片儲存位置', null=True, max_length=512)
    lat = M.DecimalField(verbose_name='緯度', null=True , max_digits=20 , decimal_places=12)
    lng = M.DecimalField(verbose_name='經度', null=True , max_digits=20 , decimal_places=12)
    ip = M.CharField(verbose_name='IP位置', null=True, max_length=256)
    active = M.BooleanField(verbose_name='啟用與否', default=True)
    taken = M.ForeignKey(User, verbose_name='操作人', null=True)
    #viewer_key = M.CharField(verbose_name='使用者金鑰', null=True, max_length=512)# 新增欄位，有些問題要問 adrian
    update_time = M.DateTimeField(auto_now=True)# 新增欄位


class Account(M.Model):
    # 一攝影機即為一伺服器，其帳號權限有三：Administrator、Operator、Viewer(Syntax Index ：0、1、2)
    monitor = M.ForeignKey(Monitor, verbose_name='攝影機')
    account = M.CharField(verbose_name='帳號', null=True, max_length=256)
    passwd = M.CharField(verbose_name='密碼', null=True, max_length=256)
    type = M.ForeignKey(Option, verbose_name='帳號類別', null=True)
    update_time = M.DateTimeField(auto_now=True)# 新增欄位


class Preset(M.Model):
    monitor = M.ForeignKey(Monitor, verbose_name='攝影機')
    name = M.CharField(verbose_name='設定名稱', null=True, max_length=256)
    no = M.CharField(verbose_name='設定對應碼', null=True, max_length=256)
    update_time = M.DateTimeField(auto_now=True)# 新增欄位 