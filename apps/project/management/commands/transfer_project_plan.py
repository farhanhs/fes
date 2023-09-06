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
        for b in Budget.objects.all():
            b.plan = b.fund.project.plan
            b.save()