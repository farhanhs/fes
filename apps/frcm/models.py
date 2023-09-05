#-*- coding:utf8 -*-
from django.db import models as M
from django.contrib.auth.models import User
from general.models import Place, Unit
import os
from PIL import Image
from common.lib import calsize
from common.templatetags.utiltags import thumb
import cmath
from fishuser.models import Project

_UPLOAD_TO = os.path.join('apps', 'frcm', 'media', 'frcm', 'cityfile', '%Y%m%d')


class Option(M.Model):
    swarm= M.CharField(verbose_name=u'群', max_length=128)
    value = M.CharField(verbose_name=u'選項', max_length=128)


    def __unicode__(self):
        return self.value

        

class CityFiles(M.Model):
    upload_user = M.ForeignKey(User, verbose_name='上傳者')
    place = M.ForeignKey(Place, verbose_name='縣市')
    location = M.CharField(verbose_name='地方', null=True, max_length=2048)
    upload_date = M.DateField(verbose_name='上傳日期')
    name = M.CharField(verbose_name='檔案名', max_length=256, null=True, default='')
    file = M.ImageField(upload_to=_UPLOAD_TO, null=True)
    memo = M.CharField(verbose_name='備註說明', null=True, max_length=2048)
    lat = M.DecimalField(verbose_name=u'緯度', null=True , max_digits=16 , decimal_places=9)
    lng = M.DecimalField(verbose_name=u'經度', null=True , max_digits=16 , decimal_places=9)

    def rUrl(self):
        return self.file.name.split('apps/frcm/')[-1]

    def rThumbUrl(self):
        thumbsrc = thumb(self.file.name, "width=1024,height=768")
        if thumbsrc == 'media/images/error.png':
            return self.file.name.split('apps/frcm/')[-1]
        else:
            return thumbsrc.split('apps/frcm/')[-1]

    def rExt(self):
        return self.file.name.split('.')[-1].lower()

    def calSize(self):
        if self.file:
            return calsize(self.file.size)
        else:
            return calsize(0)



def _PROJECTFILE_BASE(instance, filename):
    if instance.file_type.value == u'工程基本資料':
        return os.path.join('apps', 'frcm', 'project_file', str(instance.project.id), 'base', str(instance.id)+'.'+instance.ext)
    elif instance.file_type.value == u'監造資料':
        return os.path.join('apps', 'frcm', 'project_file', str(instance.project.id), 'inspector', str(instance.id)+'.'+instance.ext)

    

class ProjectFile(M.Model):
    # 工程案的上傳檔案
    name = M.CharField(max_length=256)
    project = M.ForeignKey(Project, verbose_name=u'所屬工程案', related_name="projectfile_project")
    user = M.ForeignKey(User, verbose_name=u'上傳者', related_name="projectfile_user")
    ext = M.CharField(max_length=20)
    file = M.FileField(upload_to=_PROJECTFILE_BASE, null=True)
    upload_time = M.DateTimeField()
    file_type = M.ForeignKey(Option, verbose_name=u'檔案分區', related_name='projectfile_file_type')
    tag = M.ManyToManyField(Option, verbose_name=u'工程案標籤', related_name='projectfile_tag')
    memo = M.TextField(verbose_name=u'備註', null=True)


    def __unicode__(self):
        return self.name + '.' + self.ext

    def get_url(self):
        url = self.file.name.split('modules/project')[-1]
        return url

    def calSize(self):
        if self.file:
            return calsize(self.file.size)
        else:
            return calsize(0)

    def web_review(self):
        ext = self.ext.lower()
        if ext in ['jpg', 'jpeg', 'bmp', 'png', 'tif', 'tiff', 'gif']:
            return 'image'
        elif ext == 'pdf':
            return 'pdf'
        else:
            return ''



class WarningCheck(M.Model):
    ''' 預警系統 預警紀錄 '''
    check_date = M.DateField(verbose_name=u'被檢查的日期') #因為是凌晨檢查，所以應該是檢查前一天的紀錄是否異常
    start_check_time = M.DateTimeField(verbose_name=u'開始檢查時間')
    end_check_time = M.DateTimeField(verbose_name=u'結束檢查時間', null=True)
    email = M.BooleanField(verbose_name=u'是否有Email通知', default=False)
    start_email_time = M.DateTimeField(verbose_name=u'開始Email時間', null=True)
    end_email_time = M.DateTimeField(verbose_name=u'結束Email時間', null=True)



class WarningProject(M.Model):
    ''' 需預警工程案及項目 '''
    warningcheck = M.ForeignKey(WarningCheck, verbose_name=u'哪一個紀錄', related_name="warningproject_warningcheck")
    project = M.ForeignKey(Project, verbose_name=u'工程案', related_name="warningproject_project")

    diff_progress = M.BooleanField(verbose_name=u'監造營造進度不一致>10%', default=False)
    diff_progress_memo = M.TextField(verbose_name=u'說明', null=True)
    diff_progress_explanation = M.TextField(verbose_name=u'廠商回覆改善說明', null=True)

    delay_progress = M.BooleanField(verbose_name=u'進度落後(監造)>10%', default=False)
    delay_progress_memo = M.TextField(verbose_name=u'說明', null=True)
    delay_progress_explanation = M.TextField(verbose_name=u'廠商回覆改善說明', null=True)

    dailyreport_no_report = M.BooleanField(verbose_name=u'日報表未填寫超過7日', default=False)
    dailyreport_no_report_memo = M.TextField(verbose_name=u'說明', null=True)
    dailyreport_no_report_explanation = M.TextField(verbose_name=u'廠商回覆改善說明', null=True)

    over_progress = M.BooleanField(verbose_name=u'進度超過110%', default=False)
    over_progress_memo = M.TextField(verbose_name=u'說明', null=True)
    over_progress_explanation = M.TextField(verbose_name=u'廠商回覆改善說明', null=True)

    no_engphoto = M.BooleanField(verbose_name=u'進度超過10%，相片數量為0張者', default=False)
    no_engphoto_memo = M.TextField(verbose_name=u'說明', null=True)
    no_engphoto_explanation = M.TextField(verbose_name=u'廠商回覆改善說明', null=True)

    schedule_progress_error = M.BooleanField(verbose_name=u'預定進度設定未完整', default=False)
    schedule_progress_error_memo = M.TextField(verbose_name=u'說明', null=True)
    schedule_progress_error_explanation = M.TextField(verbose_name=u'廠商回覆改善說明', null=True)

    class Meta:
        unique_together = (('warningcheck', 'project'), )



class NoImportProject(M.Model):
    '''尚無人匯入日報表工程'''
    warningcheck = M.ForeignKey(WarningCheck, verbose_name=u'哪一個紀錄', related_name="noimportproject_warningcheck")
    project = M.ForeignKey(Project, verbose_name=u'工程案', related_name="noimportproject_project")

    class Meta:
        unique_together = (('warningcheck', 'project'), )



class WarningMailList(M.Model):
    """
       預警系統 通知對象紀錄
    """
    user = M.ForeignKey(User, verbose_name=u'帳號', related_name=u'warningmaillist_user')

    def save(self, *args, **kw):
        assign('project.sub_menu_warning_system_warninginfo', self.user)

        super(WarningMailList, self).save(*args, **kw)


    def delete(self):
        remove_perm('project.sub_menu_warning_system_warninginfo', self.user)

        super(WarningMailList, self).delete()