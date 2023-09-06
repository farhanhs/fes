# -*- coding:utf8 -*-
import datetime, os, decimal, random, time

from os.path import join, isabs
from PIL import Image
from django.db import models as M
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.contrib.sessions.models import Session
from django.conf import settings
import shutil


class Sop(M.Model):
    title = M.CharField(verbose_name=u'標題', max_length=128)
    is_use = M.BooleanField(default=False)
    release_date = M.DateField(default=datetime.datetime.now)
    memo = M.TextField(verbose_name=u'備註')
    priority = M.IntegerField()

    class Meta:
        permissions = (
            ('edit_sop', u'管理編輯SOP'),
            )

    def __unicode__(self):
        return self.title


    def save(self, *args, **kw):
        if not self.priority:
            current_sops = Sop.objects.order_by('-priority')
            self.priority = current_sops[0].priority + 1 if current_sops else 1
        super(Sop, self).save(*args, **kw)


    def delete(self):
        try:
            shutil.rmtree(os.path.join(settings.ROOT, 'apps', 'sop', 'media', 'sop', 'file', str(self.id)))
        except: pass

        super(Sop, self).delete()


class Item(M.Model):
    TYPE_CHOICE = (
        (0, '標準流程圖'),
        (1, '標準作業書'),
        (2, '表單'),
        (3, '標準流程圖-vsd'),
    )
    name = M.CharField(verbose_name=u'表單',max_length=128)
    sop = M.ForeignKey(Sop,verbose_name=u'標準作業程序', related_name="item_sop" , null=True)
    type = M.IntegerField(choices=TYPE_CHOICE)

    def __unicode__(self):
        return self.name


    def filters(self):
        if self.type == 0:
            return 'png'
        elif self.type == 1:
            return 'doc,docx'
        elif self.type == 2:
            return 'doc,docx,xls,xlsx,pdf,jpg,jpeg,png'
        elif self.type == 3:
            return 'vsd'
        else:
            return False


    def fullname(self):
        return self.sop.title+'-'+self.name


def _DOCUMENT_UPLOAD_TO(instance, filename):
    if instance.item.type == 2:
        return os.path.join('apps', 'sop', 'media', 'sop', 'file', str(instance.item.sop.id) ,'form', str(instance.version)+'.'+instance.ext)
    else:
        return os.path.join('apps', 'sop', 'media', 'sop', 'file', str(instance.item.sop.id) , str(instance.version)+'.'+instance.ext)



class File(M.Model):
    version = M.CharField(max_length=8)
    name = M.CharField(max_length=50)
    item = M.ForeignKey(Item, verbose_name=u'文件', related_name="file_item", null=True)
    ext = M.CharField(max_length=20)
    file = M.FileField(upload_to=_DOCUMENT_UPLOAD_TO, null=True)
    is_use = M.BooleanField(default=True)
    upload_time = M.DateTimeField()
    memo = M.TextField(verbose_name=u'備註')

    def __unicode__(self):
        return self.name + self.ext

    def save(self, *args, **kw):
        if not self.version: self.create_version_code()
        super(File, self).save(*args, **kw)

    def get_url(self):
        return self.file.name.replace('apps/sop', "")

    def get_actual_path(self):
        if os.path.isfile(os.path.join(settings.ROOT, self.file.url)):
            return os.path.join(settings.ROOT, self.file.url)
        elif os.path.isfile(os.path.join(settings.MEDIA_ROOT, self.file.url)):
            return os.path.join(settings.MEDIA_ROOT, self.file.url)
        else: return False

    def create_version_code(self):
        version_box = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','1','2','3','4','5','6','7','8','9','0']
        again = True
        while again == True:
            version = ''
            for i in xrange(6):
                version += version_box[int(random.random()*36)]
            try:
                k = Project.objects.get(i_code=i_code)
                again = True
            except:
                again = False
        self.version = version
