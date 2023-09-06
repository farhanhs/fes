# -*- coding: utf8 -*-
from django.utils.translation import ugettext as _
from django.db import models as M
from project.models import Project
from general.models import Place, Unit
from django.contrib.auth.models import User
from common.templatetags.utiltags import thumb
from common.lib import calsize
import os
from PIL import Image
import decimal, random
from django.conf import settings
ROOT = settings.ROOT

# Create your models here.
class Option(M.Model):
    swarm= M.CharField(verbose_name=u'群', max_length=128)
    value = M.CharField(verbose_name=u'選項', max_length=128)

    def __unicode__(self):
        return self.value


    class Meta:
        verbose_name = u'選項'
        verbose_name_plural = u'選項'
        unique_together = (("swarm", "value"),)



class Guide(M.Model):
    name = M.CharField(verbose_name=u'姓名', max_length=24)
    is_default = M.BooleanField(verbose_name=u'是否為常用', default=False)
    def __unicode__(self):
        return self.name


    class Meta:
        verbose_name = u'督導人員'
        verbose_name_plural = u'督導人員'


class SuperviseCase(M.Model):
    uid = M.CharField(verbose_name=u'標案編號', max_length=255, null=True)
    date = M.DateField(verbose_name=u'督導日期')
    plan = M.CharField(verbose_name=u'列管計畫名稱', max_length=512)
    finish_no = M.CharField(verbose_name=u'同意結案文號', max_length=512, default=u"")
    project = M.CharField(verbose_name=u'標案名稱', max_length=512)
    subordinate_agencies_unit = M.ForeignKey(Unit, verbose_name=u'標案所屬工程主管機關', null=True)
    project_organizer_agencies = M.CharField(verbose_name=u'標案主辦機關', max_length=512)
    project_manage_unit = M.CharField(verbose_name=u'專案管理單位', max_length=128)
    place = M.ForeignKey(Place, related_name='place_set', verbose_name=u'縣市')
    location = M.ForeignKey(Place, related_name='location_set',verbose_name=u'地點', null=True)
    designer = M.CharField(verbose_name=u'設計單位', max_length=128)
    inspector = M.CharField(verbose_name=u'監造單位', max_length=128)
    construct = M.CharField(verbose_name=u'承包商', max_length=512)
    budget_price = M.DecimalField(verbose_name=u'預算金額(千元)', max_digits=16 , decimal_places=3, null=True)
    contract_price = M.DecimalField(verbose_name=u'契約金額(千元)', max_digits=16 , decimal_places=3, null=True)
    contract_price_change = M.DecimalField(verbose_name=u'契約金額(千元)變更後', max_digits=16 , decimal_places=3, null=True)
    info = M.TextField(verbose_name=u'工程概要')
    progress_date = M.DateField(verbose_name=u'進度紀錄日期', null=True)
    scheduled_progress = M.DecimalField(verbose_name=u'工程預計累計進度' , max_digits=16 , decimal_places=4, null=True)
    actual_progress = M.DecimalField(verbose_name=u'工程實際累計進度' , max_digits=16 , decimal_places=4, null=True)
    scheduled_money = M.DecimalField(verbose_name=u'工程預定累計金額(千元)', max_digits=16 , decimal_places=3, null=True)
    actual_money = M.DecimalField(verbose_name=u'工程實際累計金額(千元)', max_digits=16 , decimal_places=3, null=True)
    progress_info = M.TextField(verbose_name=u'目前施工概況', null=True)
    outguide = M.ManyToManyField(Guide, related_name='outguide_set', verbose_name='外聘委員')
    inguide = M.ManyToManyField(Guide, related_name='inguide_set', verbose_name='內聘委員')
    captain = M.ManyToManyField(Guide, related_name='captain_set', verbose_name='領隊')
    worker = M.ManyToManyField(Guide, related_name='worker_set', verbose_name='工作人員')
    start_date = M.DateField(verbose_name=u'開工日期', null=True)
    expected_completion_date = M.DateField(verbose_name=u'預計完工日期', null=True)
    expected_completion_date_change = M.DateField(verbose_name=u'預計完工日期變更後', null=True)
    score = M.DecimalField(verbose_name=u'督導分數', max_digits=5, decimal_places=2)
    merit = M.TextField(verbose_name=u'優點')
    advise = M.TextField(verbose_name=u'建議事項(規劃設計問題)')
    advise_improve_result = M.TextField(verbose_name=u'改善對策及結果', null=True)
    advise_date = M.DateField(verbose_name=u'改善日期', null=True)
    advise_memo = M.TextField(verbose_name=u'備註', null=True)
    other_advise = M.TextField(verbose_name=u'建議事項(其他建議)')
    other_improve_result = M.TextField(verbose_name=u'改善對策及結果', null=True)
    other_date = M.DateField(verbose_name=u'改善日期', null=True)
    other_memo = M.TextField(verbose_name=u'備註', null=True)
    cdate = M.DateField(verbose_name=u'匯入日期')
    inspector_deduction = M.IntegerField(verbose_name=u'監造扣點', default=0)
    inspector_deduction_memo = M.TextField(verbose_name=u'監造扣點說明', null=True)
    construct_deduction = M.IntegerField(verbose_name=u'營造扣點', default=0)
    construct_deduction_memo = M.TextField(verbose_name=u'營造扣點說明', null=True)
    organizer_deduction = M.IntegerField(verbose_name=u'主辦扣點', default=0)
    organizer_deduction_memo = M.TextField(verbose_name=u'主辦扣點說明', null=True)
    project_manage_deduction = M.IntegerField(verbose_name=u'專案管理扣點', default=0)
    project_manage_deduction_memo = M.TextField(verbose_name=u'專案管理扣點說明', null=True)
    total_deduction = M.IntegerField(verbose_name=u'總扣點', default=0)
    is_test = M.BooleanField(verbose_name=u'是否鑽心', default=False)
    test = M.TextField(verbose_name=u'檢驗拆驗')
    test_result = M.TextField(verbose_name=u'鑽心結果', null=True)
    test_date = M.DateField(verbose_name=u'改善日期', null=True)
    test_memo = M.TextField(verbose_name=u'備註', null=True)
    fes_project = M.ForeignKey(Project, verbose_name=u'對應FES系統工程案', null=True)
    is_improve = M.BooleanField(default=False)

    def __unicode__(self):
        return '%s(%s)' % (self.project, self.date)


    def get_errorimprovephoto_advise(self):
        return self.errorimprovephoto_set.filter(improve_type__value=u'規劃設計問題及建議')


    def get_errorimprovephoto_otheradvise(self):
        return self.errorimprovephoto_set.filter(improve_type__value=u'其他建議')



class ErrorLevel(M.Model):
    name = M.CharField(verbose_name=u'缺失程度', unique=True, max_length=4)

    def __unicode__(self):
        return self.name


    class Meta:
        verbose_name = u'缺失程度'
        verbose_name_plural = u'缺失程度'


class ErrorContent(M.Model):
    no = M.CharField(verbose_name=u'缺失編號', max_length=64)
    introduction = M.TextField(verbose_name=u'缺失說明')

    def __unicode__(self):
        return self.no


class Error(M.Model):
    case = M.ForeignKey(SuperviseCase)
    ec = M.ForeignKey(ErrorContent)
    context = M.CharField(verbose_name=u'缺失內容', max_length=1024)
    level = M.ForeignKey(ErrorLevel, default=2)
    improve_result = M.TextField(verbose_name=u'改善對策及結果', null=True)
    date = M.DateField(verbose_name=u'改善日期', null=True)
    memo = M.TextField(verbose_name=u'備註', null=True)
    guide = M.ForeignKey(Guide, related_name='error_guide', verbose_name='委員', null=True)

    def __unicode__(self):
        return self.ec.no


    class Meta:
        verbose_name = u'缺失項目'
        verbose_name_plural = u'缺失項目'


def _ERROR_FILE_UPLOAD_TO(instance, filename):
    ext = filename.split('.')[-1].lower()
    if instance.error:
        return os.path.join('apps', 'supervise', 'media', 'supervise', 'photo_file', str(instance.error.case.id), str(instance.error.ec.no), str(instance.id)+'-'+str(random.random()) +'.'+ext)
    else:
        if instance.improve_type.value == u'規劃設計問題及建議':
            folder_name = 'advise'
        elif instance.improve_type.value == u'其他建議':
            folder_name = 'other_advise'
        return os.path.join('apps', 'supervise', 'media', 'supervise', 'photo_file', str(instance.case.id), folder_name, str(instance.id)+'-'+str(random.random())+'.'+ext)



class ErrorImprovePhoto(M.Model):
    #缺失改善照片
    case = M.ForeignKey(SuperviseCase, null=True)
    error = M.ForeignKey(Error, null=True)
    improve_type = M.ForeignKey(Option, verbose_name=u'改善對向swarm="error_improve_type"', null=True) # 17=規劃設計問題及建議 18=其他建議
    before = M.ImageField(upload_to=_ERROR_FILE_UPLOAD_TO, null=True)
    before_memo = M.TextField(verbose_name=u'改善前說明', null=True)
    middle = M.ImageField(upload_to=_ERROR_FILE_UPLOAD_TO, null=True)
    middle_memo = M.TextField(verbose_name=u'改善中說明', null=True)
    after = M.ImageField(upload_to=_ERROR_FILE_UPLOAD_TO, null=True)
    after_memo = M.TextField(verbose_name=u'改善後說明', null=True)

    def rBeforeUrl(self):
        if not self.before: return '/media/supervise/v2/image/empty.png'
        return self.before.name.split('apps/supervise')[-1]

    def rMiddleUrl(self):
        if not self.middle: return '/media/supervise/v2/image/empty.png'
        return self.middle.name.split('apps/supervise')[-1]

    def rAfterUrl(self):
        if not self.after: return '/media/supervise/v2/image/empty.png'
        return self.after.name.split('apps/supervise')[-1]

    def rBeforeThumbUrl(self):
        if not self.before: return '/media/supervise/v2/image/empty.png'
        thumbsrc = thumb(self.before.name, "width=51,height=38")
        if thumbsrc == '/media/images/error.png':
            return self.before.name.split('apps/supervise')[-1]
        else:
            return thumbsrc.split('apps/supervise')[-1]

    def rMiddleThumbUrl(self):
        if not self.middle: return '/media/supervise/v2/image/empty.png'
        thumbsrc = thumb(self.middle.name, "width=51,height=38")
        if thumbsrc == '/media/images/error.png':
            return self.middle.name.split('apps/supervise')[-1]
        else:
            return thumbsrc.split('apps/supervise')[-1]

    def rAfterThumbUrl(self):
        if not self.after: return '/media/supervise/v2/image/empty.png'
        thumbsrc = thumb(self.after.name, "width=51,height=38")
        if thumbsrc == '/media/images/error.png':
            return self.after.name.split('apps/supervise')[-1]
        else:
            return thumbsrc.split('apps/supervise')[-1]



#決定可以編輯督導系統的人
class Edit(M.Model):
    user = M.OneToOneField(User, verbose_name=u'帳號', related_name=u'supervise_user_profile')



def _FILE_UPLOAD_TO(instance, filename):
    return os.path.join('apps', 'supervise', 'media', 'supervise', 'photo_file', str(instance.supervisecase.id), str(instance.id)+'.'+instance.ext)

class ErrorPhotoFile(M.Model):
    #督導缺失相片上傳區
    supervisecase = M.ForeignKey(SuperviseCase, verbose_name=u'督導案')
    upload_date = M.DateField(verbose_name=u'上傳日期')
    ext = M.CharField(verbose_name=u'副檔名', max_length=10, null=True)
    name = M.CharField(verbose_name=u'檔案名', max_length=256, null=True, default='')
    file = M.ImageField(upload_to=_FILE_UPLOAD_TO, null=True)
    memo = M.CharField(verbose_name=u'備註說明', null=True, max_length=2048)

    def rUrl(self):
        return self.file.name.split('apps/supervise/')[-1]

    def rThumbUrl(self):
        thumbsrc = thumb(self.file.name, "width=512,height=384")
        if thumbsrc == 'media/images/error.png':
            return self.file.name.split('apps/supervise/')[-1]
        else:
            return thumbsrc.split('apps/supervise/')[-1]

    def rExt(self):
        return self.file.name.split('.')[-1].lower()

    def calSize(self):
        if self.file:
            return calsize(self.file.size)
        else:
            return calsize(0)



def _ERRORFILE_UPLOAD_TO(instance, filename):
    return os.path.join('apps', 'supervise', 'media', 'supervise', 'error_file', str(instance.error.id), str(instance.id)+'.'+instance.ext)

class ErrorImproveFile(M.Model):
    #督導缺失檔案上傳區
    error = M.ForeignKey(Error, verbose_name=u'缺失')
    upload_date = M.DateField(verbose_name=u'上傳日期')
    ext = M.CharField(verbose_name=u'副檔名', max_length=10, null=True)
    name = M.CharField(verbose_name=u'檔案名', max_length=256, null=True, default='')
    file = M.FileField(upload_to=_ERRORFILE_UPLOAD_TO, null=True)

    def rUrl(self):
        return self.file.name.split('apps/supervise/')[-1]

    def rExt(self):
        return self.file.name.split('.')[-1].lower()

    def calSize(self):
        if self.file:
            return calsize(self.file.size)
        else:
            return calsize(0)



def _FILE_UPLOAD_TO(instance, filename):
    return os.path.join('apps', 'supervise', 'media', 'supervise', 'case_file', str(instance.supervisecase.id), str(instance.id)+'.'+instance.ext)

class CaseFile(M.Model):
    #督導缺失相片上傳區
    supervisecase = M.ForeignKey(SuperviseCase, verbose_name=u'督導案')
    upload_date = M.DateField(verbose_name=u'上傳日期')
    ext = M.CharField(verbose_name=u'副檔名', max_length=10, null=True)
    name = M.CharField(verbose_name=u'檔案名', max_length=256, null=True, default='')
    file = M.ImageField(upload_to=_FILE_UPLOAD_TO, null=True)
    memo = M.CharField(verbose_name=u'備註說明', null=True, max_length=2048)

    def rUrl(self):
        return self.file.name.split('apps/supervise/')[-1]

    def rThumbUrl(self):
        thumbsrc = thumb(self.file.name, "width=512,height=384")
        if thumbsrc == 'media/images/error.png':
            return self.file.name.split('apps/supervise/')[-1]
        else:
            return thumbsrc.split('apps/supervise/')[-1]

    def rExt(self):
        return self.file.name.split('.')[-1].lower()

    def calSize(self):
        if self.file:
            return calsize(self.file.size)
        else:
            return calsize(0)



class PCC_Project(M.Model):
    #從工程會擷取『經費來源屬"漁業署"之工程標』
    uid = M.CharField(verbose_name=u'標案編號', max_length=255, unique=True)
    implementation_department = M.CharField(max_length=255, verbose_name=u'執行機關',  null=True)
    name = M.CharField(max_length=255, verbose_name=u'標案名稱',  null=True)
    s_public_date = M.DateField(verbose_name=u'預定公告日期', null=True)
    r_decide_tenders_date = M.DateField(verbose_name=u'實際決標日期', null=True)
    contract_budget = M.FloatField(verbose_name=u'發包預算', null=True)
    decide_tenders_price = M.FloatField(verbose_name=u'決標金額', null=True)
    year = M.IntegerField(verbose_name=u'年度',  null=True)
    month = M.IntegerField(verbose_name=u'月份',  null=True)
    percentage_of_predict_progress = M.FloatField(verbose_name=u'預定進度', null=True)
    percentage_of_real_progress = M.FloatField(verbose_name=u'實際進度', null=True)
    percentage_of_dulta = M.FloatField(verbose_name=u'差異', null=True)



class PCC_sync_record(M.Model):
    #從工程會同步工程的紀錄
    user = M.ForeignKey(User, verbose_name=u'帳號', related_name=u'pcc_sync_record_user')
    case = M.ForeignKey(SuperviseCase, verbose_name=u'督導案', related_name=u'pcc_sync_record_case')
    ip = M.CharField(verbose_name=u'IP', max_length=15, null=True)
    field_name = M.CharField(verbose_name=u'修改欄位名稱', max_length=128)
    old_value = M.TextField(verbose_name=u'舊值', null=True)
    new_value = M.TextField(verbose_name=u'新值', null=True)
    update_time = M.DateTimeField(verbose_name=u'修改時間', auto_now=True)
