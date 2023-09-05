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
        chase = CountyChaseTime.objects.all().order_by('-id').first()
        records = chase.countychaseprojectonetomany_set.all().exclude(project__pcc_no__isnull=True).exclude(project__pcc_no="")
        for r in records:
            try:
                r.project.sync_pcc_info()
                print 'OK', r.project.pcc_no
            except:
                print 'F', r.project.pcc_no
            time.sleep(15)