# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
import os, datetime, decimal, random
import sys
sys.path.append('../../../fishuser')
from fishuser.models import Project
from fishuser.models import CountyChaseProjectOneToMany
from pccmating.models import Project as PCC_Project
from dailyreport.models import Version
from pccmating.models import ProjectProgress as PCC_ProjectProgress

from django.contrib.auth.models import User

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
    help = "進度與經費有落差(大於10%)之預警"

    def handle(self, *args, **kw):
        project = Project.objects.filter(deleter=None)
        warning_project_id = []
        warning_project = []
        for p in project:
            #工程契約金額
            version = Version.objects.filter(project__id = p.id).first()
            if p.pcc_no:
                try:
                    pcc_project = PCC_Project.objects.get(uid = p.pcc_no)
                    if not pcc_project.decide_tenders_price2 or pcc_project.decide_tenders_price2 == 0:
                        engs_price = int(pcc_project.decide_tenders_price)
                    else:
                        engs_price = int(pcc_project.decide_tenders_price2)
                except:
                    engs_price =  0
            elif version and version.engs_price:
                engs_price = int(version.engs_price)
            elif p.construction_bid:
                engs_price = int(p.construction_bid)
            elif p.total_money:
                engs_price = int(p.total_money)
                    
            else:
                engs_price =  0
            #print engs_price

        #取得工程實際進度
            pcc_a_percent = 0
            if p.pcc_no:
                try:
                    progress = PCC_Project.objects.get(uid = p.pcc_no)
                except:
                    pass
            else:
                progress = False
            if not progress or not progress.percentage_of_real_progress:
                progress = False
            engprofile = p.dailyreport_engprofile.filter()
            if progress:
                #第一步 找看看工程會同步資料有沒有
                pcc_a_percent = progress.percentage_of_real_progress
            elif engprofile:
                #第二步 找日報表有沒有
                engprofile = engprofile.first()
                if engprofile.design_percent or engprofile.act_inspector_percent:
                    pcc_a_percent = round(float(str(engprofile.act_inspector_percent)), 2)
            #第三步 找看看進度追蹤
            if not pcc_a_percent:
                chases = CountyChaseProjectOneToMany.objects.filter(complete=True, project=p).order_by('-id')
                if chases:
                    chase = chases.first()
                    pcc_a_percent = round(float(str(chase.actual_progress_percent)), 2)
            #計算進度與經費差異
            act_money = int(pcc_a_percent / 100 * engs_price)
            #print act_money
            if p.pcc_no:
                warning_price = engs_price / 10
                try:
                    pcc_project = PCC_Project.objects.get(uid = p.pcc_no)
                    pcc_act_money = pcc_project.total_act_price
                    if act_money != int(pcc_act_money):
                        #print act_money, int(pcc_act_money) ,p.pcc_no
                        if abs(act_money - int(pcc_act_money)) > warning_price:
                            warning_project.append(p.name)
                            warning_project_id.append(str(p.id))
                except:
                    pass
        #print warning_project[0]
        #print warning_project_id
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
            #toaddrs = [i]
            #toaddrs = [u'a38269412@gmail.com']
            #toaddrs = [u'kuti8733@gmail.com',u'siyu1217@ms1.fa.gov.tw']
        
            msg = MIMEMultipart()
            msg['From']=fromaddr
            msg['To']=COMMASPACE.join(toaddrs)
            msg['Date']=formatdate(localtime=True)
            msg['Subject']=u'漁業署FES工程管理-《進度與經費落差之工程案》'

            #你要寫的內容
            info = u''
            info += u'<br>您好，這封信由系統自動寄出，請勿回信<br><br>'
            info += u'進度與經費落差超過10%的工程案如下:<br><br>'
            for i, project in enumerate(warning_project):
                info += u'<ul>'
                info += u'<li><a href="https://fes.fa.gov.tw/frcm/project_profile/%s/" target="_blank">%s</a></li><br>' % (warning_project_id[i], project)
                info += u'</ul>'
            
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
        except:
            pass
