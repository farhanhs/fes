# -*- coding: utf-8 -*-
import sys
print sys.path

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Group, Permission
from django.conf import settings


from dailyreport.models import ALL_PERMISSIONS as ALL_PERMISSIONS_DAILYREPORT
from gallery.models import ALL_PERMISSIONS as ALL_PERMISSIONS_GALLERY


class Command(BaseCommand):
    help = 'Create the permissions for project, dailyreport modules'


    def handle(self, *args, **kw):
        # {"model": "auth.group", "pk": 1, "fields": {"name": "上層管理者"}},
        # {"model": "auth.group", "pk": 27, "fields": {"name": "署內上層管理者"}},
        # {"model": "auth.group", "pk": 3, "fields": {"name": "主辦工程師"}},
        # {"model": "auth.group", "pk": 26, "fields": {"name": "署內主辦工程師"}},

        # {"model": "auth.group", "pk": 6, "fields": {"name": "管考填寫員"}},

        # {"model": "auth.group", "pk": 7, "fields": {"name": "漁船填寫員"}},
        # {"model": "auth.group", "pk": 8, "fields": {"name": "漁港資訊填寫員"}},

        # {"model": "auth.group", "pk": 9, "fields": {"name": "本署帳號管理員"}},
        # {"model": "auth.group", "pk": 10, "fields": {"name": "縣市帳號管理員"}},

        # {"model": "auth.group", "pk": 13, "fields": {"name": "註冊"}},
        # {"model": "auth.group", "pk": 28, "fields": {"name": "督導系統填寫員"}},

        # {"model": "auth.group", "pk": 30, "fields": {"name": "SOP管理者"}},
        # {"model": "auth.group", "pk": 31, "fields": {"name": "主計室"}},
        for g_id in xrange(1, 100):
            try:
                group = Group.objects.get(id=g_id)
                group.permissions.clear()
            except: pass

        perm_list = [
            # ['content_type__model', 'codename', 'name','content_type__app_label']
            ['option', u'top_menu_management_system', u'第一層選單_工程管考系統', 'fishuser', [27,26,6,31]],
            ['option', u'top_menu_remote_control_system', u'第一層選單_遠端管理系統', 'fishuser', [1,27,3,26,6,13,31]],
            ['option', u'top_menu_auditing_system', u'第一層選單_查核系統', 'fishuser', [27,26,6]],
            ['option', u'top_menu_supervise_system', u'第一層選單_督導系統', 'fishuser', [27,26,6]],
            ['option', u'top_menu_harbor_system', u'第一層選單_漁港資訊系統', 'fishuser', [1,27,3,26,6,7,8]],
            ['option', u'top_menu_account', u'第一層選單_帳號管理', 'fishuser', [9,10]],
            ['option', u'sub_menu_management_system_search', u'第二層選單_工程管考系統_搜尋管考工程', 'fishuser', [27,26,6,31]],
            ['option', u'sub_menu_management_system_plan', u'第二層選單_工程管考系統_計畫列表', 'fishuser', [27,26,6]],
            ['option', u'sub_menu_management_system_draft', u'第二層選單_工程管考系統_草稿匣', 'fishuser', [6]],
            ['option', u'sub_menu_management_system_create', u'第二層選單_工程管考系統_新增工程案', 'fishuser', [6]],
            ['option', u'sub_menu_management_system_city', u'第二層選單_工程管考系統_縣市進度追蹤', 'fishuser', [27,6]],
            ['option', u'sub_menu_management_system_manage_money', u'第二層選單_工程管考系統_自辦工程管理費', 'fishuser', [6,31]],
            ['option', u'sub_menu_management_system_manage_money_commission', u'第二層選單_工程管考系統_委辦工程管理費', 'fishuser', [6,31]],
            ['option', u'sub_menu_remote_control_system_my', u'第二層選單_遠端管理系統_我的工程', 'fishuser', [3,13,26]],
            ['option', u'sub_menu_remote_control_system_import', u'第二層選單_遠端管理系統_匯入工程', 'fishuser', [3,26]],
            ['option', u'sub_menu_remote_control_system_claim', u'第二層選單_遠端管理系統_認領工程', 'fishuser', [13]],
            ['option', u'sub_menu_remote_control_system_search', u'第二層選單_遠端管理系統_搜尋遠端工程', 'fishuser', [1,27,3,26,31]],
            ['option', u'sub_menu_remote_control_system_file', u'第二層選單_遠端管理系統_檔案管理', 'fishuser', [1,27,3,26]],
            ['option', u'sub_menu_remote_control_system_proposal', u'第二層選單_遠端管理系統_工程提案區', 'fishuser', [1,27,3,26]],
            ['option', u'sub_menu_remote_control_system_statisticstable_money', u'第二層選單_遠端管理系統_廠商得標金額排行', 'fishuser', [1,27,3,26]],
            ['option', u'sub_menu_supervise_system_create', u'第二層選單_督導系統_新增', 'fishuser', [6,28]],
            ['option', u'sub_menu_harbor_system_edit', u'第二層選單_漁港資訊系統_編輯資訊', 'fishuser', [8]],
            ['option', u'sub_menu_harbor_system_edit_portinstallationrecord', u'第二層選單_漁港資訊系統_填報漁港設施記錄', 'fishuser', [7, 8]],
            ['option', u'sub_menu_warning_system_warninginfo', u'第二層選單_工程預警內容', 'fishuser', [1,6,27]],
            
            ['option', u'sub_menu_management_control_form', u'第二層選單_工程管考系統_漁港管控表', 'fishuser', [1,3,26,27]],

            ['project', u'view_all_project_in_management_system', u'在(工程管理系統)中_觀看_所有_工程案資訊', 'fishuser', [6,26,27,31]],
            ['project', u'edit_all_project_in_management_system', u'在(工程管理系統)中_編輯_所有_工程案資訊', 'fishuser', [6]],
            ['project', u'view_all_project_in_remote_control_system', u'在(遠端工程系統)中_觀看_所有_工程案資訊', 'fishuser', [1,6,26,27,31]],

            
            ['sop', u'edit_sop', u'管理編輯SOP', 'sop', [30]],
        ]

        for n, perm in enumerate(perm_list):
            for g_id in perm[-1]:
                group = Group.objects.get(id=g_id)
                permission = Permission.objects.get(content_type__model=perm[0], codename=perm[1], name=perm[2], content_type__app_label=perm[3])
                group.permissions.add(permission)
                print ('Group("%s") ADD Permission("%s")'%(group.name, permission.codename))

        #日報表系統的權限設定
        groups = Group.objects.filter(id__in=[1, 27, 3, 26, 6, 9, 10])
        for i in ALL_PERMISSIONS_DAILYREPORT:
            for g in groups:
                if i[0].startswith('view_'):
                    permission = Permission.objects.get(content_type__model='engprofile', codename=i[0], name=i[1], content_type__app_label='dailyreport')
                    g.permissions.add(permission)
                    print ('Group("%s") ADD Permission("%s")'%(g.name, permission.codename))

        #相片系統的權限設定
        groups = Group.objects.filter(id__in=[1, 27, 3, 26, 6, 9, 10])
        for i in ALL_PERMISSIONS_GALLERY:
            for g in groups:
                if i[0].startswith('view_'):
                    permission = Permission.objects.get(content_type__model='case', codename=i[0], content_type__app_label='gallery')
                    g.permissions.add(permission)
                    print ('Group("%s") ADD Permission("%s")'%(g.name, permission.codename))

