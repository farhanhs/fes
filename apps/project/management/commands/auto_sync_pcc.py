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
import time

def TODAY(): return datetime.date.today()

class Command(BaseCommand):
    help = u"每日凌晨進行同步工程會資料"

    def handle(self, *args, **kw):
        t0 = time.time()
        records = Project.objects.all().exclude(pcc_no__isnull=True).exclude(pcc_no="")
        total = records.count()
        print 'this is records length',len(records)
        #print 'this is records',records
        for n, r in enumerate(records):
            time.sleep(10)
            try:
                r.sync_pcc_info()
                print 'OK', r.pcc_no, round(((n+1)*100./total), 2), '%'
            except:
                print 'F', r.pcc_no, round(((n+1)*100./total), 2), '%'
        