# -*- coding: utf8 -*-
import os
from PIL import Image
from django.utils.translation import ugettext as _
from django.db import models as M
from django.db.models import Q
from django.core.files import File
from fishuser.models import *
from fishuser.models import _ca
from PIL.ExifTags import TAGS
from hashlib import md5
from datetime import datetime, date
from common.lib import calsize
from common.models import SelfBaseObject
from settings import ROOT, MEDIA_ROOT, PHOTO_SIZE_LIMIT, TMPPATH
from random import random



class Option(M.Model):
    swarm= M.CharField(verbose_name='群', max_length=32)
    value = M.CharField(verbose_name='選項', max_length=64)

    def __unicode__(self):
        return self.value


    class Meta:
        verbose_name = '選項'
        verbose_name_plural = '選項'
        unique_together = (("swarm", "value"),)

try:
    NORMALPHOTOTYPE = Option.objects.get(swarm='phototype', value='正常')
    DEFECTPHOTOTYPE = Option.objects.get(swarm='phototype', value='待改善相簿')
    TRASHPHOTOTYPE = Option.objects.get(swarm='phototype', value='資源回收筒')
    AUTODUPLICATETYPE = Option.objects.get(swarm='duplicatetype', value='系統判斷重複')
    NONDUPLICATETYPE = Option.objects.get(swarm='duplicatetype', value='監工認定非重複相片')
    LESSTHANPHOTOSIZELIMITTYPE = Option.objects.get(swarm='enoughtype', value='未達要求大小的相片')
    NONLESSTHANPHOTOSIZELIMITTYPE = Option.objects.get(swarm='enoughtype', value='人工放寬未達要求大小的相片')
except:
    NORMALPHOTOTYPE = None
    DEFECTPHOTOTYPE = None
    TRASHPHOTOTYPE = None
    AUTODUPLICATETYPE = None
    NONDUPLICATETYPE = None
    LESSTHANPHOTOSIZELIMITTYPE = None
    NONLESSTHANPHOTOSIZELIMITTYPE = None



class Template(M.Model):
    """ 放置樣板資料時，必遵守一項規定，即查驗點群組的 id 需小於其項下之查驗點 id 。
    """
    name = M.CharField(verbose_name='查驗點名稱', db_index=True, max_length=64)
    floor = M.IntegerField(verbose_name='最低套數/張數')
    help = M.CharField(verbose_name='說明', max_length=512)
    require = M.BooleanField(verbose_name='必要')
    uplevel = M.ForeignKey('self', related_name='sublevel', null=True)

    def __unicode__(self):
        return '%s/%s' % (self.uplevel, self.name)

    def isRequire(self):
        return self.require

    def rName(self):
        return self.name

    def getHelp(self):
        return self.help

    def getFloor(self):
        return self.floor



class CheckPoint(M.Model, SelfBaseObject):
    project = M.ForeignKey(Project, verbose_name='工程案')
    template = M.ForeignKey(Template, verbose_name='所引自的鐵版', null=True)
    name = M.CharField(verbose_name='查驗點名稱', db_index=True, max_length=128, null=True)
    need = M.IntegerField(verbose_name='需求張數')
    help = M.CharField(verbose_name='說明', max_length=256, null=True)
    uplevel = M.ForeignKey('self', related_name='sublevel', null=True)
    priority = M.IntegerField(verbose_name='優先值')

    def __unicode__(self):
        if self.uplevel and self.uplevel.rName() != '目錄':
            return '%s/%s' % (self.uplevel, self.rName())
        else:
            return '%s' % self.rName()

    def isRequire(self):
        if self.template: return self.template.require
        else: return False

    def rName(self):
        if self.name: return self.name
        elif self.template and self.template.name: return self.template.name
        else: return ''

    def getHelp(self):
        if self.help: return self.help
        elif self.template and self.template.help: return self.template.help
        else: return '無說明'

    def getFloor(self):
        return self.need

    def getAllPhotoNum(self):
        try:
            if self.uplevel: self.uplevel.rName()
        except CheckPoint.DoesNotExist: return 0
        return self.photo_set.filter(phototype=NORMALPHOTOTYPE).count()

    def getUploadPhotoNum(self):
        try:
            if self.uplevel: self.uplevel.rName()
        except CheckPoint.DoesNotExist: return 0
        return self.photo_set.filter(phototype=NORMALPHOTOTYPE, verify__isnull=False).exclude(
        enoughtype=LESSTHANPHOTOSIZELIMITTYPE).exclude(duplicatetype=AUTODUPLICATETYPE).count()



class Verify(M.Model):
    md5 = M.CharField(verbose_name='md5碼', max_length=34, db_index=True)



UPLOAD_TO = os.path.join('apps', 'engphoto', 'photo', 'file')
class Photo(M.Model, SelfBaseObject):
    project = M.ForeignKey(Project, verbose_name='工程案')
    checkpoint = M.ForeignKey(CheckPoint, verbose_name='查驗點')
    phototype = M.ForeignKey(Option, related_name='phototype_set', verbose_name='照片分類')
    position = M.CharField(verbose_name='椿號位置', max_length=128, null=True, default='')
    uploadname = M.CharField(verbose_name='上傳時檔案名', max_length=256, null=True, default='')
    file = M.ImageField(upload_to=UPLOAD_TO, null=True)
    extensiontype = M.ForeignKey(Option, related_name='extensiontype_set', verbose_name='附檔名', null=True)
    photodate = M.DateField(verbose_name='拍照時間', null=True)
    uploadtime = M.DateTimeField(verbose_name='上傳時間', null=True)
    updatetime = M.DateTimeField(verbose_name='欄位資訊最後更新時間', auto_now=True)
    inspector_check = M.NullBooleanField(verbose_name='監造人員是否檢視', null=True, default=0)
    note_con = M.TextField(verbose_name='營造廠商意見', null=True, default='')
    note_ins = M.TextField(verbose_name='監造廠商意見', null=True, default='')
    note_eng = M.TextField(verbose_name='主辦意見', null=True, default='')
    note_exp = M.TextField(verbose_name='專家意見', null=True, default='')
    verify = M.ForeignKey(Verify, verbose_name='相片驗證碼', null=True)
    #TODO 應該把 duplicatetype 及 enoughtype 兩個屬性合併成 errortype = M.ManyToManyField( Option, related_name='errortype_set' )
    duplicatetype = M.ForeignKey(Option, related_name="duplicatetype_set", null=True)
    enoughtype = M.ForeignKey(Option, related_name="enoughtype_set", null=True)
    owner = M.ForeignKey(User, related_name='photo_set', null=True)
    priority = M.IntegerField(verbose_name='順序', default=0)

    def getUploadtime(self, s):
        if self.uploadtime: return self.uploadtime.strftime(s)
        else: return ''

    def getUpdatetime(self, s):
        if self.updatetime: return self.updatetime.strftime(s)
        else: return ''

    def rName(self):
        return str(self.checkpoint) + '/' + self.position

    def setDuplicates(self):
        if not self.verify: return []
        if self.phototype == DEFECTPHOTOTYPE or self.phototype == TRASHPHOTOTYPE:
            return []

        type_id = NORMALPHOTOTYPE.id
        nonduplicatetype_id = NONDUPLICATETYPE.id
        try:
            from django.db import connection
            cursor = connection.cursor()
            table = '%s_%s' % (self._meta.app_label, self._meta.model_name)

            sql = """select id from %s where (verify_id = '%s'
            and (duplicatetype_id != %s or duplicatetype_id is null)
            and phototype_id = %s) or id = %s order by uploadtime""" % (
            table, self.verify.id, nonduplicatetype_id, type_id, self.id)

            cursor.execute(sql)

            list = []
            for row in cursor.fetchall(): list.append(row[0])
            if len(list) > 1:
                sql = """update %s set duplicatetype_id = Null where id = %s""" % (table, list[0])
                cursor.execute(sql)
                if list[0] == self.id: return []
                else: return list
            return []
        except:
            return False

    def getPhotodate(self, s):
        if self.photodate: return self.photodate.strftime(s)
        else: return ''

    def deleteNowFile(self):
        if not self.file: return

        try:
            self.verify = None
            self.uploadname = None
            self.photodate = None
            self.duplicatetype = None
            self.enoughtype = None
            self.file.delete()
        except OSError:
            pass
        except ValueError:
            pass

    def save_file(self, *args, **kw):
        if not self.id: self.save()

        file = args[0]
        file_ori_size = len(file.read())
        file.seek(0)
        self.deleteNowFile()
        self.uploadname = file.name

        im = Image.open(file)
        extensiontype = im.format.upper()
        try:
            self.extensiontype = Option.objects.get(swarm='extensiontype', value=extensiontype)
        except Option.DoesNotExist:
            self.warning = '檔案格式不可為 %s ' % extensiontype
            return

        if not self.photodate:
            photodate = None
            try:
                for tag, value in im._getexif().items():
                    if 'DateTime' == TAGS.get(tag, tag):
                        photodate = datetime.strptime(im._getexif()[tag],
                        '%Y:%m:%d %H:%M:%S')
                        break
            except:
                pass

            self.photodate = photodate

        if type(self.photodate) == datetime and self.photodate < datetime(1900, 1, 1):
            self.photodate = None
        elif type(self.photodate) == date and self.photodate < date(1900, 1, 1):
            self.photodate = None

        if extensiontype == 'TIF' or extensiontype == 'TIFF':
            tmpfile_name = str(random())
            tmpfile = File(open(os.path.join(TMPPATH, tmpfile_name) , 'wb'))
            im.save(tmpfile, 'JPEG')
            tmpfile.close()
            file = File(open(os.path.join(TMPPATH, tmpfile_name) , 'rb'))
            extensiontype = 'JPEG'
            self.extensiontype = Option.objects.get(swarm='extensiontype', value=extensiontype)

        file.seek(0)
        content = file.read()

        self.verify, created = Verify.objects.get_or_create(md5=md5(content).hexdigest())
        self.uploadtime = datetime.now()

        image_filename = '%s_%s.%s' % (self.project.id, self.id, self.extensiontype.value.lower())
        self.file.save(image_filename, file)

        md5dir = os.path.join(self.verify.md5[0:2], self.verify.md5[2:4])
        target_dir = os.path.join(ROOT, UPLOAD_TO, md5dir)
        target_filename = os.path.join(target_dir, image_filename)
        try:
            if not os.path.isdir(target_dir): os.makedirs(target_dir)
            os.rename(self.file.path, target_filename)
            self.file = os.path.join(UPLOAD_TO, md5dir, image_filename)
        except OSError:
            pass

        dup = self.setDuplicates()
        if self.duplicatetype == NONDUPLICATETYPE: pass
        elif len(dup) >= 2 : self.duplicatetype = AUTODUPLICATETYPE
        else: self.duplicatetype = None

        if file_ori_size < PHOTO_SIZE_LIMIT:
            self.enoughtype = LESSTHANPHOTOSIZELIMITTYPE

        self.save()

    def __unicode__(self):
        return '%s:%s / %s(%s) at %s' % (self.project, self.checkpoint, self.position, self.phototype, self.updatetime)

    def calSize(self):
        if self.file and os.path.exists(self.file.path):
            return calsize(self.file.size)
        else:
            return calsize(0)


    def moveToStore(self, phototype, emptyPhoto):
        if self.phototype == phototype: return False

        if self.phototype != NORMALPHOTOTYPE:
            self.phototype = phototype
            self.save()
            return self
        else:
            self.phototype = phototype
            self.save()

            emptyPhoto.project = self.project
            emptyPhoto.checkpoint = self.checkpoint
            emptyPhoto.phototype = NORMALPHOTOTYPE
            emptyPhoto.priority = self.priority
            emptyPhoto.save()
            return emptyPhoto

    def renameFromStore(self, storePhoto):
        for k in ['position', 'file', 'photodate', 'updatetime', 'inspector_check', 'note_con',
        'note_ins', 'note_eng', 'note_exp', 'verify']:
            setattr(self, k, getattr(storePhoto, k))
        self.phototype = NORMALPHOTOTYPE
        self.save()
        storePhoto.delete()

    def renameFromNormal(self, source_photo, empty_source_photo, empty_target_photo):
        empty_source_photo = source_photo.moveToStore(TRASHPHOTOTYPE, empty_source_photo)
        empty_target_photo = self.moveToStore(TRASHPHOTOTYPE, empty_target_photo)
        empty_target_photo.renameFromStore(source_photo)

    def get_next(self, number):
        """ 依查驗點優先值找出本張相片的下 number 張相片
        """
        pass
    def get_previous(self, number):
        """ 依查驗點優先值找出本張相片的前 number 張相片
        """
        pass

#這是轉移 rcm4 至 rcm6 時，所用的 Model ，目前應該是不需要了。
##class ItemCat(M.Model):
##    name = M.CharField(max_length=50)
##    require = M.BooleanField()
##
##    def __unicode__(self):
##        return self.name
##
##class CheckPointCat(M.Model):
##    name = M.CharField(max_length=50)
##    photo_need = M.IntegerField()
##    help = M.TextField()
##    require = M.BooleanField()
##    item = M.ForeignKey(ItemCat)
##
##    def __unicode__(self):
##        return self.name
##
##class RCM4ToRCM6Log(M.Model):
##    type = M.CharField(max_length=24)
##    rcm4id = M.IntegerField()
##    checkpoint = M.ForeignKey(CheckPoint)
##
##
##class TmpItem(M.Model):
##    name = M.CharField(max_length=100)
##    itemcat = M.ForeignKey(ItemCat, null=True)
##    require = M.BooleanField() # 應該是用不到
##    project_id = M.IntegerField()
##    project_no = M.CharField(max_length=20)
##
##    def makeCheckpoint(self, priority):
##        project = self.getProject()
##        template = self.getTemplateByItem()
##        if template and not self.name:
##            name = None
##        else:
##            name = self.name
##        help = None
##        need = 1
##        try:
##            uplevel = CheckPoint.objects.get(project=project, name='目錄', uplevel__isnull=True)
##        except CheckPoint.DoesNotExist:
##            uplevel = CheckPoint(project=project, template=None, name='目錄', need=0, help=None,
##            uplevel=None, priority=0)
##            uplevel.save()
##        priority = priority * 10
##
##        try:
##            checkpoint = CheckPoint.objects.get(project=project, name=name, uplevel=uplevel)
##        except CheckPoint.DoesNotExist:
##            checkpoint = CheckPoint(project=project, template=template, name=name, help=help, need=need,
##            uplevel=uplevel, priority=priority)
##            checkpoint.save()
##            r4to6 = RCM4ToRCM6Log(type='item', rcm4id=self.id, checkpoint=checkpoint)
##            r4to6.save()
##        return checkpoint
##
##    def __unicode__(self):
##        return self.project_no + '::' + self.name
##
##    def getTemplateByItem(self):
##        if not self.itemcat: return None
##        try:
##            name = self.itemcat.name
##            return Template.objects.get(name=name, uplevel__isnull=True)
##        except Template.DoesNotExist:
##            print name
##            sys.exit()
##
##    def getProject(self):
##        try:
##            return Project.objects.get(no=self.project_no)
##        except Project.DoesNotExist:
##            try:
##                tpeic = TaojrProjectEngIdChangeLog.objects.get(old_engid=self.project_no)
##                return tpeic.getNewProject()
##            except TaojrProjectEngIdChangeLog.DoesNotExist:
##                return None
##
##class TmpCheckPoint(M.Model):
##    tmpitem = M.ForeignKey(TmpItem)
##    name = M.CharField(max_length=200)
##    photo_need = M.IntegerField()
##    checkpointcat = M.ForeignKey(CheckPointCat, null=True)
##    help = M.TextField()
##    require = M.BooleanField() # 應該是用不到
##
##    def __unicode__(self):
##        return str(self.tmpitem) + '::' + self.name
##
##    def getTemplateByCheckpoint(self, itemtemplate):
##        if  not itemtemplate or not self.checkpointcat: return None
##        try:
##            name = self.checkpointcat.name
##            return Template.objects.get(name=name, uplevel=itemtemplate)
##        except Template.DoesNotExist:
##            print name
##            sys.exit()
##
##    def makeCheckpoint(self, uplevel, priority):
##        project = self.tmpitem.getProject()
##        if uplevel.template:
##            template = self.getTemplateByCheckpoint(uplevel.template)
##        else:
##            template = None
##        if template and not self.name:
##            name = None
##        else:
##            name = self.name
##        if template and not self.help:
##            help = None
##        else:
##            help = self.help
##        need = self.photo_need
##        priority = priority * 10
##
##        try:
##            checkpoint = CheckPoint.objects.get(project=project, name=name, uplevel=uplevel)
##        except CheckPoint.DoesNotExist:
##            checkpoint = CheckPoint(project=project, template=template, name=name, help=help, need=need,
##            uplevel=uplevel, priority=priority)
##            checkpoint.save()
##            r4to6 = RCM4ToRCM6Log(type='checkpoint', rcm4id=self.id, checkpoint=checkpoint)
##            r4to6.save()
##        return checkpoint
##
##import re
##def _r(path):
##    path = str(path)
##    return re.sub('^/', '', path)
##
##from settings import ROOT, DEFAULTRCM4PHOTOPATH, MEDIA_ROOT
##class TmpPhoto(M.Model):
##    tmpcheckpoint = M.ForeignKey(TmpCheckPoint)
##    position = M.CharField(max_length=128)
##    path = M.TextField()
##    uploadname = M.CharField(max_length=100)
##    note_con = M.TextField()
##    note_ins = M.TextField()
##    note_eng = M.TextField()
##    note_exp = M.TextField()
##    updatetime = M.DateTimeField()
##    photodate = M.DateField()
##    inspector_check = M.BooleanField()
##    verify = M.CharField(max_length=64)
##    isdefective = M.BooleanField()
##
##    if not os.path.exists(DEFAULTRCM4PHOTOPATH): raise ValueError
##
##    def __unicode__(self):
##        return '%s/%s' % (self.tmpcheckpoint, self.position)
##
##
##    def makePhoto(self, rcm6photo):
##        fields = ['position', 'uploadname', 'note_con', 'note_ins', 'note_eng', 'note_exp',
##        'photodate', 'inspector_check']
##        for f in fields:
##            setattr(rcm6photo, f, getattr(self, f))
##
##        if type(self.updatetime) == datetime and self.updatetime >= datetime(1900,1,1):
##            rcm6photo.updatetime = self.updatetime
##            rcm6photo.uploadtime = self.updatetime
##
##        if self.isdefective: rcm6photo.phototype = DEFECTPHOTOTYPE
##
##        rcm6photo.save()
##
##        rcm4photo_filename = os.path.join(DEFAULTRCM4PHOTOPATH, _r(self.path), _r(self.uploadname))
##        if not os.path.isfile(rcm4photo_filename):
##            rcm4photo_filename = os.path.join(DEFAULTRCM4PHOTOPATH, _r(self.tmpcheckpoint.tmpitem.project_id),
##            _r(self.tmpcheckpoint.tmpitem.id), _r(self.tmpcheckpoint.id), _r(self.uploadname))
##
##            if not os.path.isfile(rcm4photo_filename):
##                rcm4photo_filename = os.path.join(DEFAULTRCM4PHOTOPATH,
##                _r(self.path), _r(self.uploadname)+'.thumb')
##
##                if not os.path.isfile(rcm4photo_filename):
##                    rcm4photo_filename = os.path.join(DEFAULTRCM4PHOTOPATH,
##                    _r(self.tmpcheckpoint.tmpitem.project_id), _r(self.tmpcheckpoint.tmpitem.id),
##                    _r(self.tmpcheckpoint.id), _r(self.uploadname)+'.thumb')
##
##                    if not os.path.isfile(rcm4photo_filename):
##                        rcm4photo_filename = os.path.join(ROOT,
##                        'apps/engphoto/static/engphoto/images/notexistinupgrade.jpg')
##                        print 'photo file is not exist, use default: ', rcm6photo.project, self.id
##
##                        if not os.path.isfile(rcm4photo_filename):
##                            print 'photo file is not exist: ', rcm6photo.project, self.id
##                            return rcm6photo
##
##        file = File(open(rcm4photo_filename))
##
##        rcm6photo.save_file(file)
##
##        rcm6photo.updatetime = self.updatetime
##        rcm6photo.uploadtime = self.updatetime
##        rcm6photo.save()
##
##        return rcm6photo
