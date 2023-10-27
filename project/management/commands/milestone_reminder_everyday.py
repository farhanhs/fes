# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
import os, datetime, decimal, random
from fishuser.models import *
from django.conf import settings
import smtplib
from email import encoders
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.utils import COMMASPACE, formatdate


def TODAY(): return datetime.date.today()

class Command(BaseCommand):
    help = u"每月1日凌晨寄信通知尚未填寫    負責主辦"

    def handle(self, *args, **kw):

        def email_to_user(users=[], field=[], project=None, memo=None):
            try:
                smtpserver = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
                # smtpserver.ehlo()
                # smtpserver.starttls()
                smtpserver.ehlo()
                #登入系統
                smtpserver.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)

                #寄件人資訊
                fromaddr = settings.EMAIL_HOST_USER

                #收件人列表，格式為list即可
                toaddrs = [i.user.email for i in users]

                msg = MIMEMultipart()
                msg['From']=fromaddr
                msg['To']=COMMASPACE.join(toaddrs)
                msg['Date']=formatdate(localtime=True)
                msg['Subject']=u'漁業署FES工程管理-里程碑預定日期提醒通知'

                #你要寫的內容
                info = u''
                info += u'<br>您好，這封信由系統自動寄出，請勿回信<br><br>'
                info += u'您所相關的工程於里程碑中設定了預定日期資訊如下。<br>'
                info += u'<br><br>工程：<a href="http://fes.fa.gov.tw/frcm/project_profile/%s/" target="_blank">%s年度-%s</a>' % (project.id, project.year, project.name)
                info += u'<br><br>設定《%s》: %s  %s' % (field[1], reminder_date, memo or u'')
                info += u'<br><br>請記得準備辦理相關流程及資料。'


                def containsnonasciicharacters(str):
                    return not all(ord(c) < 128 for c in str)

                if containsnonasciicharacters(info):
                    htmltext = MIMEText(info.encode('utf-8', 'replace'), 'html','utf-8')
                else:
                    htmltext = MIMEText(info, 'html')

                msg.attach(htmltext)

                smtpserver.sendmail(fromaddr, toaddrs, msg.as_string())

                #記得要登出
                smtpserver.quit()
            except: pass


        milestone_fields = {
            'eng': [
                ["eng_plan_agree_plan", u"設計規劃階段-同意計畫"],
                ["eng_plan_approved_plan", u"設計規劃階段-核定計畫"],
                ["eng_plan_announcement_tender", u"設計規劃階段-勞務公告上網"],
                ["eng_plan_final", u"設計規劃階段-勞務決標"],
                ["eng_plan_promise", u"設計規劃階段-定約"],
                ["eng_plan_detail_design", u"設計規劃階段-提送預算書圖"],
                ["eng_plan_acceptance", u"設計規劃階段-勞務驗收"],
                ["eng_plan_acceptance_closed", u"設計規劃階段-勞務結案"],

                ["eng_do_agree_plan", u"工程施作階段-同意工程"],
                ["eng_do_approved_plan", u"工程施作階段-核定工程"],
                ["eng_do_announcement_tender", u"工程施作階段-工程公告上網"],
                ["eng_do_final", u"工程施作階段-工程決標"],
                ["eng_do_promise", u"工程施作階段-工程定約"],
                ["eng_do_start", u"工程施作階段-開工"],
                ["eng_do_completion", u"工程施作階段-完工"],
                ["eng_do_acceptance", u"工程施作階段-驗收"],
                ["eng_do_closed", u"工程施作階段-結案"]
            ],
            'ser': [
                ["ser_approved_plan", u"核定計畫"],
                ["ser_signed_tender", u"簽辦招標"],
                ["ser_announcement_tender", u"公告招標"],
                ["ser_selection_meeting", u"公開評選會議(限制性招標)"],
                ["ser_promise", u"定約"],
                ["ser_work_plan", u"工作計畫書"],
                ["ser_interim_report", u"期中報告"],
                ["ser_final_report", u"期末報告"],
                ["ser_do_acceptance", u"驗收"],
                ["ser_acceptance_closed", u"結案"]
            ]
        }

        reminder_date = TODAY() + datetime.timedelta(days=3)
        while reminder_date.isoweekday() in [6, 7]:
            reminder_date += datetime.timedelta(days=1)

        obo_engs = CountyChaseProjectOneByOne.objects.filter(project__deleter__isnull=True, project__purchase_type__value__in=[u"工程", u'工程勞務'], act_eng_do_closed__isnull=True)
        obo_sers = CountyChaseProjectOneByOne.objects.filter(project__deleter__isnull=True, project__purchase_type__value=u"一般勞務", act_ser_acceptance_closed__isnull=True)

        for obo in obo_engs:
            p = obo.project
            connect_users = FRCMUserGroup.objects.filter(project=p)
            if not connect_users: continue #沒有可以通知的人就跳過
            for field in milestone_fields['eng']:
                sch = getattr(obo, 'sch_%s' % (field[0]))
                act = getattr(obo, 'act_%s' % (field[0]))
                memo = getattr(obo, '%s_memo' % (field[0]))
                if not act and sch and sch == reminder_date:
                    toaddrs = [i.user.email for i in connect_users]
                    print toaddrs,p
                    #email_to_user(users=connect_users, field=field, project=p, memo=memo)

        for obo in obo_sers:
            p = obo.project
            connect_users = FRCMUserGroup.objects.filter(project=p)
            if not connect_users: continue #沒有可以通知的人就跳過
            for field in milestone_fields['ser']:
                sch = getattr(obo, 'sch_%s' % (field[0]))
                act = getattr(obo, 'act_%s' % (field[0]))
                memo = getattr(obo, '%s_memo' % (field[0]))
                if not act and sch and sch == reminder_date:
                    #email_to_user(users=connect_users, field=field, project=p, memo=memo)
                    pass


        