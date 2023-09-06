# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
import os, datetime, decimal, random
import sys
sys.path.append('../../../fishuser')
from fishuser.models import UserProfile
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
    help = "寄信給尚未填寫滿意度調查表的人"

    def handle(self, *args, **kw):
        email_list = []
        userprofile = UserProfile.objects.filter(is_satisfaction=False).all()
        for u in userprofile:
            user = User.objects.get(id = u.user_id)
            email_list.append(user.email)
        print email_list

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
            msg['Subject']=u'漁業署FES工程管理-《滿意度調查表》'

            #你要寫的內容
            info = u''
            info += u'<br>您好，這封信由系統自動寄出，請勿回信<br><br>'
            info += u'感謝您一直以來的支持與愛護，請您撥冗幾分鐘的時間，協助填寫滿意度調查表。<br><br>'
            info += u'您寶貴的意見將是我們持續改善的動力，謝謝！<br><br>'
            info += u'請按下連結進行填寫:<br><br>'
            info += u'<ul>'
            info += u'<a href="https://fes.toff.best/fishuser/satisfaction_page/" target="_blank">漁業工程管理系統-滿意度調查表</a>'
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
