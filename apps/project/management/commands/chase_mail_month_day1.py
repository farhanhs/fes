# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
import os, datetime, decimal, random
import sys
sys.path.append('../../../fishuser')
#from fishuser.models import *
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
        chase = CountyChaseTime.objects.all().order_by('-id').first()
        records = chase.countychaseprojectonetomany_set.filter(complete=False)

        projects_map = {}
        for r in records:
            if r.project.purchase_type.value in [u"工程", u"工程勞務"]:
                if CountyChaseProjectOneByOne.objects.filter(project__deleter__isnull=True, project=r.project, act_eng_do_closed__isnull=False):
                    continue
            elif r.project.purchase_type.value in [u"一般勞務"]:
                if CountyChaseProjectOneByOne.objects.filter(project__deleter__isnull=True, project=r.project, act_ser_acceptance_closed__isnull=False):
                    continue
            projects_map[r.project.id] = r

        engs = FRCMUserGroup.objects.filter(project__id__in=[id for id in projects_map], group__name__in=[u'負責主辦工程師', u'自辦主辦工程師'])

        email_list = {}
        for e in engs:
            if email_list.has_key(e.user.email):
                email_list[e.user.email].append(projects_map[e.project.id])
            else:
                email_list[e.user.email] = [projects_map[e.project.id]]

        for i in email_list:
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
                toaddrs = [i]
                # toaddrs = [u'johnisacoolboy@gmail.com']

                msg = MIMEMultipart()
                msg['From']=fromaddr
                msg['To']=COMMASPACE.join(toaddrs)
                msg['Date']=formatdate(localtime=True)
                msg['Subject']=u'漁業署FES工程管理-《縣市進度追蹤填報預警系統》Day 1'

                #你要寫的內容
                info = u''
                info += u'<br>您好，這封信由系統自動寄出，請勿回信<br><br>'
                info += u'您所相關的工程於本期縣市進度追蹤中，尚未填寫完畢，請盡速至系統填寫進度資訊。<br>'
                info += u'尚未填報的工程資訊列表如下：<br>'
                info += u'<ul>'
                for r in email_list[i]:
                    info += u'<li><a href="https://fes.fa.gov.tw/frcm/project_profile/%s/" target="_blank">%s年度-%s</a></li>' % (r.project.id, r.project.year, r.project.name)
                info += u'</ul>'


                info += u'<br><h3>若您的工程已結案，請聯絡 02-23835796 林明緯，於系統設定工程結案。</h3><br>'

                info += u'<br>下次預警偵測時間為每月第三天，並同時通知 署內負責人<br>'
                info += u'<br><br>依據本署工程督導小組設置及作業要點第11點規定：當年度同一直轄市、縣(市)每月5日前未在本署遠端工程管理系統填報（更新）所執行相關工程累計至前１個月最新進度或填報不實資料者，每次記點１次，當年度累計逾3次者，次年度經費補助比例依「行政院農業部主管計畫補助基準」減少2％。<br><br>請各機關依時限確實填報。'


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
