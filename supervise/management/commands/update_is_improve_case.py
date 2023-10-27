# -*- coding: utf-8 -*-
import sys, datetime

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Group, Permission
from django.conf import settings

from supervise.models import *

TODAY = lambda: datetime.date.today()

class Command(BaseCommand):
    help = '設定已經改善完畢的'


    def handle(self, *args, **kw):
        for c in SuperviseCase.objects.all():
            c.is_improve = False
            c.save()
            if (TODAY() - c.date).days >= 90:
                c.is_improve = True
                c.save()
            else:
                if not Error.objects.filter(case=c, date__isnull=True):
                    c.is_improve = True
                    c.save()
                    print 'complete %s' % (c.id)
                else:
                    print c.id

