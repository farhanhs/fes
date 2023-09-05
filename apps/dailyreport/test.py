
# -*- coding: utf8 -*-
import datetime
from django.test import TestCase
from django.utils import timezone
from django.db import models as M
from dailyreport.models import EngProfile

class test_schedule_porgress(TestCase):
    def setUpTestData(cls):
         pass
    def setUp(self):
        pass
    def profile_log(self,EngProfile):
        
        way = EngProfile.objects.Project_id
        start = EngProfile.objects.start_date
        dur = EngProfile.objects.druation
        dead = EngProfile.objects.deadline
        print("起始日期=",start,'/n')
        print("工程天數",dur)
        print("計算方式",way)
        print("比例分配",dead)
        self.assertEqual(dur, int(dead-start))
    