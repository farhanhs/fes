# -*- coding: utf-8 -*-
from time import time
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Group, Permission
from django.core.files.base import ContentFile
try: from guardian.shortcuts import assign_perm
except: from guardian.shortcuts import assign as assign_perm
from guardian.shortcuts import get_users_with_perms
from rcm.models import Project, RcmUP
from gallery.models import Case, Node, Photo
from gallery.models import ALL_PERMISSIONS



class Command(BaseCommand):
    help = "ONLY RUN IN OLD SYSTEM AND RUN IT ONCE! Move old 'check point photo' model's data to new 'gallery' model."

    def handle(self, *args, **kw):
        for project in Project.objects.all().order_by("id"):
            project.save() # 利用 Project 的 post save signal 來建立 Case。
            case = project.photo_case # 取得剛建立的 Case

            roots = project.checkpoint_set.filter(parent__isnull=True)
            for root in roots: self.rCPTree(case, root) # 拷貝查驗點資料至新節點


        # 賦予群組權限。
        groups = Group.objects.filter(id__in=[1,2,3,4,5,6,7])#專家_、管理者_、工程師_
        for i in ALL_PERMISSIONS:
            for g in groups:
                if i[0].startswith('view_'):
                    permission = Permission.objects.get(content_type__model='case', codename=i[0], content_type__app_label='gallery')
                    g.permissions.add(permission)

        # 利用 RcmUP 的 post save signal 來賦予 User 對 Case 的權限
        rcm_relations = RcmUP.objects.all()
        for r in rcm_relations: r.save()


    def rCPTree(self, case, cp, parent_node=False):
        """
        利用遞回拷貝 CheckPoint 至 Node
        """
        if not parent_node:
            clone_node = case.nodes.get(parent__isnull=True)
            clone_node.note = cp.note
            clone_node.priority = cp.priority
            clone_node.needed_count = cp.needed_count
            clone_node.images_count = cp.images_count
        else:
            clone_node = Node(case=case, parent=parent_node, name=cp.name, note=cp.note, priority=cp.priority, needed_count=cp.needed_count, images_count=cp.images_count)
        clone_node.save()

        for picture in cp.photo_set.all(): # 拷貝查驗點下的照片至新節點下
            clone_photo = Photo(node=clone_node, origin="%s.%s"%(picture.name, picture.ext), sha_code=picture.sha_code, note=picture.note, time=picture.photo_time)
            clone_photo.photo.save("%s.%s"%(str(int(time()*1000)), picture.ext), ContentFile(picture.read()))

            # 拷貝照片的權限
            for user in get_users_with_perms(picture):
                clone_photo.creator = user
                clone_photo.save()
                assign_perm("remove_photo", user, clone_photo)

        for child in cp.checkpoint_set.all(): # 拷貝查驗點下的子節點至新節點下
            self.rCPTree(case, child, clone_node)

    """
    後續動作：
        * 將 uploaded-files 移至新專案底下。
        * 於 sql 修正 Photo 於 Database 中的路徑：
            > UPDATE gallery_photo SET photo = REPLACE(photo, '舊路徑', '新路徑') WHERE photo LIKE '%舊路徑%';

    """