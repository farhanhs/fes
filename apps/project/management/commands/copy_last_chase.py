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
    help = u"每月26日凌晨進行新的月份縣市進度追蹤"

    def handle(self, *args, **kw):
        chase = CountyChaseTime.objects.all().order_by('-id').first()

        for i in CountyChaseProjectOneToMany.objects.filter(countychasetime=chase):
            if i.complete: continue
            last_chases = CountyChaseProjectOneToMany.objects.filter(project=i.project, complete=True).exclude(countychasetime=chase).order_by('-id')
            if not last_chases: continue
            last_chase = last_chases[0]
            print i.memo
            print last_chase.memo
            i.memo = last_chase.memo
            i.schedul_progress_percent = last_chase.schedul_progress_percent
            i.actual_progress_percent = last_chase.actual_progress_percent
            i.expected_to_end_percent = last_chase.expected_to_end_percent
            i.self_payout = last_chase.self_payout
            i.self_unpay = last_chase.self_unpay
            i.save()