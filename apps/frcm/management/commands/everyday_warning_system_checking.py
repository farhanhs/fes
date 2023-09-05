# -*- coding: utf-8 -*-
import sys, datetime, decimal, math

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from django.contrib.auth.models import Group, Permission
from django.conf import settings

from general.models import Place, Unit
from fishuser.models import Option, Project, FRCMUserGroup, CountyChaseProjectOneByOne, CountyChaseProjectOneToMany
from frcm.models import WarningCheck, WarningProject, NoImportProject, WarningMailList
from dailyreport.models import EngProfile, Report
from pccmating.models import ProjectProgress as PCC_ProjectProgress

def TODAY(): return datetime.date.today()

def NOW(): return datetime.datetime.now()


class Command(BaseCommand):
    help = u'禮拜日進行預警系統的計算'

    def handle(self, *args, **kw):
        # WarningCheck.objects.all().delete()
        check_date = TODAY() - datetime.timedelta(1)
        warningcheck = WarningCheck(
            check_date = check_date,
            start_check_time = NOW(),
            )
        warningcheck.save()

        p_ids = []
        for i in CountyChaseProjectOneByOne.objects.filter(project__deleter__isnull=True, project__year__gt=101, project__purchase_type__value__in=[u"工程", u"工程勞務"], act_eng_do_closed__isnull=True):
            if i.act_eng_do_approved_plan and i.act_eng_do_approved_plan < TODAY(): continue
            p_ids.append(i.project.id)

        for i in CountyChaseProjectOneByOne.objects.filter(project__deleter__isnull=True, project__year__gt=101, project__purchase_type__value=u"一般勞務", act_ser_acceptance_closed__isnull=True):
            if i.act_ser_approved_plan and i.act_ser_approved_plan < TODAY(): continue
            p_ids.append(i.project.id)

        projects = Project.objects.filter(id__in=p_ids)
        engprofile_project_ids = []
        n = 0
        for p in projects:
            delay_progress = False #進度落後>10%
            delay_progress_memo = ''
            dailyreport_no_report = False #日報表未填寫超過5日
            dailyreport_no_report_memo = ''
            over_progress = False #進度超過110%
            over_progress_memo = ''
            no_engphoto = False #進度超過10%，相片數量為0張者
            no_engphoto_memo = ''
            try:
                engprofile = EngProfile.objects.get(project=p)
            except:
                engprofile = None

            if not engprofile or not engprofile.start_date:
                n += 1
            else:
                engprofile_project_ids.append(p.id) #有填報日報表的工程

            progress = PCC_ProjectProgress.objects.filter(project__uid=p.pcc_no).order_by('-year', '-month')
            pcc_s_percent = 0
            pcc_a_percent = 0
            if progress:
                #第一步 找看看工程會同步資料有沒有
                progress = progress.first()
                pcc_s_percent = round(progress.percentage_of_predict_progress*100, 2)
                pcc_a_percent = round(progress.percentage_of_real_progress*100, 2)
            elif engprofile:
                #第二步 找日報表有沒有
                if engprofile.design_percent or pcc_s_percent:
                    pcc_s_percent = round(float(str(engprofile.design_percent)), 2)
                    pcc_a_percent = round(float(str(pcc_s_percent)), 2)
            #第三步 找看看進度追蹤
            if not pcc_s_percent and not pcc_a_percent:
                chases = CountyChaseProjectOneToMany.objects.filter(complete=True, project=p).order_by('-id')
                if chases:
                    chase = chases.first()
                    pcc_s_percent = round(float(str(chase.schedul_progress_percent)), 2)
                    pcc_a_percent = round(float(str(chase.actual_progress_percent)), 2)

            try:
                if (pcc_s_percent - pcc_a_percent) >= 10:
                    delay_progress = True
                    delay_progress_memo = u'進度落後%s%%，超過警戒值進行警示通知' % (pcc_s_percent - pcc_a_percent)
            except: pass
            try:
                working_dates = engprofile.readWorkingDate(is_scheduled=True)
                i_no_report = 0
                c_no_report = 0 
                for d in working_dates:
                    min_day = min([TODAY().date(), working_dates[-1]])
                    if d >= min_day:
                        break
                    else:
                        try:
                            report = Report.objects.get(date=d, project=p)
                            if not report.inspector_check: i_no_report += 1
                            if not report.contractor_check: c_no_report += 1
                        except:
                            i_no_report += 1
                            c_no_report += 1
                if (i_no_report > 7 or c_no_report > 7):
                    dailyreport_no_report = True
                    dailyreport_no_report_memo = '日報表上未填寫天數，監造：%s天，施工：%s天，填報速度落後進行警示通知' % (i_no_report, c_no_report)
            except: pass
            try:
                if pcc_s_percent >= 110:
                    over_progress = True
                    over_progress_memo = u'工程進度：%s%%，進度異常超過110%%進行警示通知' % (pcc_s_percent)
            except: pass
            try:
                images_count = p.rGalleryPics() if p.use_gallery else bundle.obj.rFRCMAlreadyUploadPics()
                if (pcc_s_percent >= 10) and images_count == 0:
                    no_engphoto = True
                    no_engphoto_memo = u'工程進度：%s%%，但尚未上傳任何施工品質相片進行警示通知' % (pcc_s_percent)
            except: pass

            if delay_progress or dailyreport_no_report or over_progress or no_engphoto:
                row = WarningProject(
                    warningcheck = warningcheck,
                    project = p,
                    delay_progress = delay_progress,
                    dailyreport_no_report = dailyreport_no_report,
                    over_progress = over_progress,
                    no_engphoto = no_engphoto,
                    delay_progress_memo = delay_progress_memo,
                    dailyreport_no_report_memo = dailyreport_no_report_memo,
                    over_progress_memo = over_progress_memo,
                    no_engphoto_memo = no_engphoto_memo,
                    )
                row.save()

        rcmups = FRCMUserGroup.objects.filter(group__id__in=[11,14])
        import_project_ids = set([i.project.id for i in rcmups])
        #無人認領工程案
        no_import_projects = projects.exclude(id__in=import_project_ids)
        no_import_project_ids = []
        for p in no_import_projects:
            row = NoImportProject(
                    warningcheck = warningcheck,
                    project = p
                )
            row.save()
            no_import_project_ids.append(p.id)

        warningcheck.end_check_time = NOW()
        warningcheck.save()

        print 'n=%s' % n
        print 'projects=%s' % projects.count()
        print 'have_dailyreport=%s' % (len(engprofile_project_ids))
        print 'warning_projects=%s' % (warningcheck.warningproject_warningcheck.all().count())
        print warningcheck.start_check_time
        print warningcheck.end_check_time
        print 'finish'