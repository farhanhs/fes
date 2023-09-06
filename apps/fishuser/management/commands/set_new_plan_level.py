# -*- coding: utf-8 -*-
import sys
print sys.path

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Group, Permission
from django.conf import settings


from fishuser.models import *



class Command(BaseCommand):
    help = 'set new plan level'

    def handle(self, *args, **kw):
        
        for b in Budget.objects.all():
            b.plan = b.fund.project.plan
            b.save()