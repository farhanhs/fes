# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
import os, datetime, decimal, random
import sys
sys.path.append('../../../fishuser')
from fishuser.models import Project
from fishuser.models import CountyChaseProjectOneToMany
from fishuser.models import FRCMUserGroup
from fishuser.models import UserProfile

from pccmating.models import Project as PCC_Project
from pccmating.models import ProjectProgress as PCC_ProjectProgress

from dailyreport.models import Version
from dailyreport.models import EngProfile

from general.models import Unit

from django.contrib.auth.models import User
from django.conf import settings


def TODAY(): return datetime.date.today()

class Command(BaseCommand):
    help = "廠商得標金額計算"

    def handle(self, *args, **kw):
        tmp = []
        project = Project.objects.filter(year=108, deleter_id=None).order_by('-id')
        data = {}
        data_case = {}
        data_project = {}
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
            #以萬元做計算

            #營造廠商
            contractors = [u.user.id for u in FRCMUserGroup.objects.filter(group__name=u'營造廠商', project=p)]
            unit_id = UserProfile.objects.get(user_id = contractors[0]).unit_id if contractors != [] else None
            try:
                unit = EngProfile.objects.get(project=p).contractor_name
            except:
                unit = None
            if not unit:
                unit = Unit.objects.get(id = unit_id).fullname if unit_id else None
            if not unit:
                unit = p.bid_final
            if engs_price != 0 and unit:
                try:
                    if data[unit]:
                        for i in data.keys():
                            if unit[0] + unit[1] in i:
                                data[unit] += engs_price
                                data_case[unit] += 1
                                data_project[unit] = data_project[unit]+ ' ' + str(p.id)
                except KeyError:
                    data.setdefault(unit, engs_price)
                    data_case.setdefault(unit, 1)
                    data_project.setdefault(unit, str(p.id))
                
                    
        data = sorted(data.items(), key=lambda x:x[1])
        #data_case = sorted(data_case.items(), key=lambda x:x[1])
        for i in data[-10:]:
            print i[0],i[1],data_case[i[0]], data_project[i[0]]
            if ' ' in i[0]:
                i[0] = i[0].split(' ')
                print i[0]
        
