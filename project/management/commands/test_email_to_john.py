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
    help = u"測試寄信給我"

    def handle(self, *args, **kw):
        smtpserver = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
        # smtpserver.ehlo()
        # smtpserver.starttls()
        smtpserver.ehlo()
        #登入系統
        smtpserver.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)

        #寄件人資訊
        fromaddr = settings.EMAIL_HOST_USER

        #收件人列表，格式為list即可
        toaddrs = [u'johnisacoolboy@gmail.com']

        msg = MIMEMultipart()
        msg['From']=fromaddr
        msg['To']=COMMASPACE.join(toaddrs)
        msg['Date']=formatdate(localtime=True)
        msg['Subject']=u'漁業署測試寄信command'

        #你要寫的內容
        info = ''
        info += u'<br>您好，這封信由系統自動寄出，請勿回信<br>'

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