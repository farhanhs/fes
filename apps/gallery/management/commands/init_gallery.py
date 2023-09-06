# -*- coding: utf-8 -*-
from os.path import join
from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand
from django.core.management import call_command

from project.models import Project
from fishuser.models import FRCMUserGroup
from gallery.permissions import IM_PERMISSIONS



class Command(BaseCommand):
    help = "Load data and set permissions."

    def handle(self, *args, **kw):
        # 載入預設資料
        call_command('loaddata', join('apps', 'gallery', 'fixtures', 'initial_data.json'))
        call_command('loaddata', join('apps', 'gallery', 'fixtures', 'image_group.json'))
        call_command('loaddata', join('apps', 'gallery', 'fixtures', 'image_size.json'))
        call_command('loaddata', join('apps', 'gallery', 'fixtures', 'default_template.json'))


        # 產生相片系統對應物件 Case
        print 'Generate gallery Case objects...'
        for project in Project.objects.all():
            project.save()


        # 對個別的 "工程-使用者" 關連身分設定權限
        print 'Setup project related user permissions...'
        for relation in FRCMUserGroup.objects.all():
            relation.save()


        # 對系統群組設定全域權限
        # {"model": "auth.group", "pk": 1, "fields": {"name": "上層管理者"}},
        # {"model": "auth.group", "pk": 3, "fields": {"name": "主辦工程師"}},
        # {"model": "auth.group", "pk": 26, "fields": {"name": "署內主辦工程師"}},
        # {"model": "auth.group", "pk": 27, "fields": {"name": "署內上層管理者"}},
        print 'Setup group permissions...'
        permissions = []
        for name in IM_PERMISSIONS:
            for perm in IM_PERMISSIONS[name]:
                if perm.startswith('view_') and perm not in permissions: permissions.append(perm)

        groups = Group.objects.filter(id__in=[1, 3, 26, 27])
        for i in permissions:
            for g in groups:
                permission = Permission.objects.get(codename=i, content_type__model='case', content_type__app_label='gallery')
                g.permissions.add(permission)
                print ('Group("%s") ADD Permission("%s")'%(g.name, permission.codename))




