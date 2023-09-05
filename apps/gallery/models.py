#!-*- coding:utf8 -*-
from os.path import join, basename
from hashlib import sha1
from datetime import datetime, time
from importlib import import_module
from urlparse import urlparse
from PIL import Image, ImageFile
from PIL.ExifTags import TAGS
from django.conf import settings
from django.contrib.auth.models import User, Group
from django.contrib.contenttypes.models import ContentType
from django.db import models as M
from django.db.utils import DatabaseError
from django.db.models.signals import post_save, post_delete
from django.core.exceptions import MultipleObjectsReturned
from django.utils.translation import ugettext as _

from guardian.shortcuts import get_perms, remove_perm
try: from guardian.shortcuts import assign_perm
except: from guardian.shortcuts import assign as assign_perm
from sorl.thumbnail import get_thumbnail
from sorl.thumbnail import delete as delete_thumbnail

from project.models import Project
from fishuser.models import FRCMUserGroup
from gallery.permissions import IM_PERMISSIONS

try: from settings import MEDIA_ROOT
except ImportError: raise Exception("Need set MEDIA_ROOT in settings.")

try: from settings import PHOTO_PATH
except ImportError: raise Exception("Need set PHOTO_PATH in settings.")

try: from settings import DEFAULT_NODE
except ImportError: DEFAULT_NODE = [{"name": u"檢核點", "priority": 1000}, {"name": u"督導查核", "priority": 2000}, {"name": u"環境保護措施", "priority": 3000}, {"name": u"勞工安全衛生", "priority": 4000}]

OBJECT = Project

ImageFile.LOAD_TRUNCATED_IMAGES = True

NODE_PRIORITY_GAP = 10000000
PHOTO_PRIORITY_GAP = 1000
ALL_PERMISSIONS = []
for group in IM_PERMISSIONS:
    ALL_PERMISSIONS += [(p, p) for p in IM_PERMISSIONS[group]]


def convert_to_degrees(value):
    """
    將 GPS 座標從度分秒系統（DMS）轉換至經緯度座標系統（Latitude/Longitude）。

    :param value: 度分秒系統（DMS）度數
    :width value: list
    :rtype: Float
    """
    degree = float(value[0][0]) / float(value[0][1])
    minute = float(value[1][0]) / float(value[1][1])
    second = float(value[2][0]) / float(value[2][1])
    return degree + (minute/60.0) + (second/3600.0)


def photo_path(instance, filename):
    """
    建立相片儲存路徑。
    
    :rtype: String
    """
    now = datetime.now()
    return join(PHOTO_PATH, str(instance.node.case.parent.id), str(instance.node.id), "%s%s%s" % (now.year, now.month, now.day), filename)



class Option(M.Model):
    """
    選項物件。
    """
    swarm = M.CharField(verbose_name=_('Swarm'), max_length=64)
    value = M.CharField(verbose_name=_('Value'), max_length=512)


    def __unicode__(self):
        return self.value



class Case(M.Model):
    """
    紀錄父層物件並作為模組中介。
    """
    parent = M.OneToOneField(OBJECT, related_name="photo_case", verbose_name="父層物件")

    class Meta:
        permissions = (
            ('view_case', u'觀看案件'),
            ('create_node', u'建立節點'),
            ('update_node', u'編輯節點'),
            ('remove_node', u'刪除節點'),
            ('upload_photo', u'上傳照片'),
            ('update_photo', u'編輯照片'),
            ('verify_public', u'核可公開'),
        )


    def __unicode__(self):
        return self.parent.name


    def save(self, *args, **kwargs):
        """
        儲存後檢查其下是否有節點，若無則利用 :func:`gallery.models.cRootNode` 建立根節點。
        
        :rtype: True
        """
        super(Case, self).save(*args, **kwargs)
        if not self.nodes.all(): self.cRootNode()
        return True


    def cRootNode(self):
        """
        建立根節點。

        :rtype: :class:`gallery.models.Node`
        """
        try: root = Node.objects.get(case=self, name=u"主資料夾", parent=None, default=True, improve=False)
        except Node.DoesNotExist:
            root = Node(case=self, name=u"主資料夾", priority=0, default=True)
            root.save()
        self.cDefaultNode()
        return root


    def cDefaultNode(self):
        """
        建立預設節點。

        :rtype: Boolean
        """
        root = self.rRootNode()
        for node in DEFAULT_NODE:
            try: root.child_nodes.get(name=node["name"], default=True)
            except Node.DoesNotExist:
                default = Node(case=self, parent=root, name=node["name"], priority=node["priority"], default=True)
                default.save()

        return True


    def rRootNode(self):
        """
        讀取根節點。

        :rtype: :class:`gallery.models.Node`
        """
        try: return Node.objects.get(case=self, parent=None, default=True, improve=False)
        except Node.DoesNotExist: return self.cRootNode()


    def rRoots(self):
        """
        讀取根節點，包含督導缺失改善。

        :rtype: QuerySet
        """
        return Node.objects.filter(case=self, parent=None)


    def rImageCount(self):
        """
        計算本案件共有多少張照片。

        :rtype: Integer
        """
        return sum([i.total_count for i in self.rRoots()])



class BaseModel(M.Model):
    """
    包含檔案物件基本資訊的 Abstract Model。
    """
    creator = M.ForeignKey(User, related_name="%(app_label)s_%(class)s_ownership", null=True)
    create_time = M.DateTimeField(verbose_name="建立時間", default=datetime.now)
    update_time = M.DateTimeField(verbose_name="更新時間", default=datetime.now)


    class Meta:
        abstract = True



class Label(BaseModel):
    """
    標籤。
    """
    value = M.CharField(verbose_name="標籤值", max_length=255)
    name = M.CharField(verbose_name="標籤名稱", max_length=255)


    def __unicode__(self):
        return self.name



class Sample(BaseModel):
    """
    樣版節點。
    """
    parent = M.ForeignKey('self', related_name="child_samples", null=True)
    name = M.CharField(verbose_name="節點名稱", max_length=255)
    priority = M.PositiveIntegerField(verbose_name="排序", default=NODE_PRIORITY_GAP)


    def __unicode__(self):
        return self.name
    

    def save(self, *args, **kwargs):
        """
        沒有 name 時以賦予預設名稱。
        
        :rtype: True
        """
        if not self.name: self.name = _("新樣版查驗點")
        super(Sample, self).save(*args, **kwargs)
        return True


    def copyStructure(self, parent):
        """
        複製某樣版節點的結構到指定節點內。
        
        :param parent: 節點物件（:class:`gallery.models.Node`）
        :width parent: :class:`gallery.models.Node`
        :rtype: :class:`gallery.models.Node`
        """
        node = Node(name=self.name, parent=parent, priority=self.priority)
        node.save()

        children = self.child_samples.all().order_by("priority")
        if children:
            for child in children:
                child.copyStructure(parent=node)
        return node


    def rTree(self):
        """
        回傳該節點向下的樹狀結構並以 dict 形式回傳。
        
        :rtype: dict
        """
        children = self.child_samples.all().order_by('priority')
        if children: return {'id': self.id, 'name': self.name, 'children': [sample.rTree() for sample in children]}
        else: return {'id': self.id, 'name': self.name, 'children': []}


    def rTreeObject(self):
        """
        回傳該節點向下的樹狀結構並以物件形式回傳。
        
        :rtype: dict
        """
        children = self.child_samples.all().order_by('priority')
        if children: self.children = [samples.rTreeObject() for samples in children]
        else: self.children = []
        return self


    def isChildOf(self, sample):
        """
        檢查結點是否在其父節點中。
        
        :param node: 節點 ID 或物件（:class:`gallery.models.Node`）
        :width node: string, unicode, integer or :class:`gallery.models.Node`
        :rtype: True
        """
        if isinstance(sample, str) or isinstance(sample, unicode) or isinstance(sample, int):
            try: sample = Sample.objects.get(id=sample)
            except Sample.DoesNotExist: raise Exception(_("Can't find match sample."))
        elif isinstance(sample, Sample): sample = sample
        else: raise Exception("The param sample need to be a integer, string, unicode or Sample object")
        while self.parent:
            if sample == self.parent: return True
            self = self.parent
        return False


    def rBrothers(self):
        """
        回傳與該節點同階層的節點。若為 root 節點則回傳空 list。
        
        :rtype: QuerySet
        """
        if self.parent: return self.parent.child_samples.all()
        return []


    def rPrevious(self):
        """
        回傳該節點於樹狀結構中排序的前一個節點。若無則回傳 self。
        
        :rtype: :class:`gallery.models.Sample`
        """
        brothers = self.rBrothers()
        if brothers:
            brothers = list(brothers.order_by("priority", "create_time"))
            index = brothers.index(self)
            if index > 0: return brothers[index-1]
        return self


    def rNext(self):
        """
        回傳該節點於樹狀結構中排序的後一個節點。若無則回傳 self。
        
        :rtype: :class:`gallery.models.Node`
        """
        brothers = self.rBrothers()
        if brothers:
            brothers = list(brothers.order_by("-priority", "-create_time"))
            index = brothers.index(self)
            if index > 0: return brothers[index-1]
        return self


    def uPriorityGap(self):
        """
        於移動節點時檢查是否需要更新排序值（priority），若排序值與前一個節點相同，則更新排序值並回傳更新後的排序值；若不需要更新則回傳 False。
        
        :rtype: Integer
        """
        previous = self.rPrevious()
        if previous != self:
            self.priority = previous.priority + NODE_PRIORITY_GAP
            self.save()
            return self.priority
        return False


    def uPriorityRange(self):
        """
        於建立節點時檢查是否需要更新排序值（priority），若排序值與前一個節點相同，則更新排序值並回傳更新後的排序值；若不需要更新則回傳 False。
        
        :rtype: Integer
        """
        brothers = self.rBrothers()
        if brothers:
            brothers = list(brothers.order_by("-priority", "-create_time"))
            brothers.remove(self)
            if brothers: self.priority = brothers[0].priority + NODE_PRIORITY_GAP
            else: self.priority = NODE_PRIORITY_GAP
            self.save()
            return self.priority
        return False


    def moveToBefore(self, anchor):
        """
        將此節點移動到另一個節點（anchor）之前，會檢查父結點（parent）與排序值（priority）。
        
        :param anchor: 節點（:class:`gallery.models.Sample`）
        :width anchor: :class:`gallery.models.Sample`
        :rtype: Integer
        """
        if anchor.parent:
            self.parent = anchor.parent
            previous = anchor.rPrevious()

            if previous == anchor: self.priority = anchor.priority / 2
            else: self.priority = (previous.priority + anchor.priority)/2
            self.save()

            if self.priority == previous.priority:
                brothers = list(self.rBrothers().order_by("priority", "create_time"))
                for update in brothers[brothers.index(self):]: update.uPriorityGap()
            return self.priority
        return False


    def moveToAfter(self, anchor):
        """
        將此節點移動到另一個節點（anchor）之後，會檢查父結點（parent）與排序值（priority）。
        
        :param anchor: 節點（:class:`gallery.models.Sample`）
        :width anchor: :class:`gallery.models.Sample`
        :rtype: Integer
        """
        if anchor.parent:
            self.parent = anchor.parent
            next = anchor.rNext()
            if next == anchor: self.priority = anchor.priority + NODE_PRIORITY_GAP
            else: self.priority = (anchor.priority + next.priority)/2
            self.save()

            if self.priority == anchor.priority:
                brothers = list(self.rBrothers().order_by("priority", "create_time"))
                for update in brothers[brothers.index(self):]: update.uPriorityGap()
            return self.priority
        return False



class Template(BaseModel):
    """
    節點的樣版設定。
    """
    name = M.CharField(verbose_name="樣版名稱", max_length=255)
    sample = M.ManyToManyField(Sample, verbose_name="樣版節點", related_name="node_template")
    label = M.ManyToManyField(Label, verbose_name="類別標籤", related_name="label_template")
    public = M.BooleanField(verbose_name="是否公開", default=False)


    def __unicode__(self):
        return self.name


    def pasteToNode(self, node):
        """
        將樣版（:class:`gallery.models.Template`）複製到某節點（:class:`gallery.models.Node`）底下。

        :param node: 節點（:class:`gallery.models.Node`）
        :width node: :class:`gallery.models.Node`
        :rtype: :class:`gallery.models.Template`
        """
        for temp in self.sample.all():
            sub = temp.copyStructure(parent=node)
        return self


    def importNodes(self, nodes, excluded):
        """
        依照節點（:class:`gallery.models.Node`）ID 建立樣版（:class:`gallery.models.Template`）。

        :param node: 要複製的節點 ID list
        :param excluded: 要忽略複製的節點 ID list
        :width node: Integer in List
        :width excluded: Integer in List
        :rtype: :class:`gallery.models.Template`
        """
        roots = Node.objects.filter(id__in=nodes).exclude(parent__id__in=nodes)
        for node in roots:
            node.copyToTemplate(nodes, excluded, self)
        return self



class Node(BaseModel):
    """
    儲存相片的節點，近似檔案結構中的資料夾。
    """
    case = M.ForeignKey(Case, related_name="nodes", null=True)
    parent = M.ForeignKey('self', related_name="child_nodes", null=True)
    name = M.CharField(verbose_name="節點名稱", max_length=255)
    note = M.TextField(verbose_name="節點備註", null=True)
    priority = M.PositiveIntegerField(verbose_name="排序", default=NODE_PRIORITY_GAP)
    needed_count = M.PositiveIntegerField(verbose_name="相片需求張數", default=3, null=True)
    images_count = M.PositiveIntegerField(verbose_name="上傳相片張數", default=0)
    total_count = M.PositiveIntegerField(verbose_name="總相片張數", default=0)
    default = M.BooleanField(verbose_name="是否為預設節點", default=False)
    improve = M.BooleanField(verbose_name="是否為缺失改善資料", default=False)


    def __unicode__(self):
        return self.name
    

    def save(self, *args, **kwargs):
        """
        儲存時透過 parent 自動賦予 case，並於沒有 name 時以賦予預設名稱。
        
        :rtype: True
        """
        try: origin_parent = Node.objects.get(id=self.id).parent
        except Node.DoesNotExist: origin_parent = False

        if self.parent: self.case = self.parent.case
        if not self.name: self.name = _("新查驗點")
        super(Node, self).save(*args, **kwargs)

        if origin_parent and origin_parent != self.parent:
            origin_parent.uImageCount()
            self.parent.uImageCount()
        return True


    def delete(self, *args, **kwargs):
        """
        刪除缺失改善資料夾時，檢查其他缺失改善資料夾，若無照片則一並刪除。
        
        :rtype: True
        """
        parent, improve = self.parent, self.improve
        super(Node, self).delete(*args, **kwargs)
        parent.uImageCount()
        if parent and improve:
            if not parent.total_count: parent.delete()
        return True


    def isRoot(self):
        """
        判斷此結點是否為預設的根結點。
        
        :rtype: Boolean
        """
        return (not self.parent) and (self.default)


    def isChildOf(self, node):
        """
        檢查此結點是否為另一節點（node）的子結點。
        
        :param node: 節點 ID 或物件（:class:`gallery.models.Node`）
        :width node: string, unicode, integer or :class:`gallery.models.Node`
        :rtype: True
        """
        if isinstance(node, str) or isinstance(node, unicode) or isinstance(node, int):
            try: node = Node.objects.get(id=node)
            except Node.DoesNotExist: raise Exception(_("Can't find match node."))
        elif isinstance(node, Node): node = node
        else: raise Exception("The param node need to be a integer, string, unicode or Node object")
        while self.parent:
            if node == self.parent: return True
            self = self.parent
        return False


    def isSameCase(self, node):
        """
        檢查此結點與另一節點（node）是否屬於同一個父節點。
        
        :param node: 節點 ID 或物件（:class:`gallery.models.Node`）
        :width node: string, unicode, integer or :class:`gallery.models.Node`
        :rtype: True
        """
        if isinstance(node, str) or isinstance(node, unicode) or isinstance(node, int):
            try: node = Node.objects.get(id=node)
            except Node.DoesNotExist: raise Exception(_("Can't find match node."))
        elif isinstance(node, Node): node = node
        else: raise Exception("The param node need to be a integer, string, unicode or Node object")
        return self.case == node.case


    def uImageCount(self, *args, **kwargs):
        """
        更新此結點所含的相片張數。
        
        :rtype: Integer
        """
        images = self.node_photos.all()
        self.images_count = len(images)

        total = self.images_count
        for child in self.child_nodes.all(): total += child.total_count
        self.total_count = total

        super(Node, self).save(*args, **kwargs)
        if self.parent: self.parent.uImageCount()
        return self.images_count


    def rProject(self):
        """
        讀取此結點所屬的工程案。
        
        :rtype: :class:`project.models.Project`
        """
        return self.case.parent


    def rTree(self):
        """
        回傳該節點向下的樹狀結構並以 dict 形式回傳。
        
        :rtype: dict
        """
        children = self.child_nodes.all().order_by('priority')
        if children: return {'id': self.id, 'name': self.name, 'images_count': self.images_count, 'children': [node.rTree() for node in children]}
        else: return {'id': self.id, 'name': self.name, 'images_count': self.images_count, 'children': []}


    def rTreeObject(self):
        """
        回傳該節點向下的樹狀結構並以物件形式回傳。
        
        :rtype: dict
        """
        children = self.child_nodes.all().order_by('priority')
        if children: self.children = [node.rTreeObject() for node in children]
        else: self.children = []
        return self


    def rPhoto(self):
        """
        回傳該節點內的所有照片物件（:class:`gallery.models.Photo`）。
        
        :rtype: QuerySet
        """
        return self.node_photos.all()


    def rBrothers(self):
        """
        回傳與該節點同階層的節點。若為 root 節點則回傳空 list。
        
        :rtype: QuerySet
        """
        if self.parent: return self.parent.child_nodes.all()
        return []


    def rPrevious(self):
        """
        回傳該節點於樹狀結構中排序的前一個節點。若無則回傳 self。
        
        :rtype: :class:`gallery.models.Node`
        """
        brothers = self.rBrothers()
        if brothers:
            brothers = list(brothers.order_by("priority", "create_time"))
            index = brothers.index(self)
            if index > 0: return brothers[index-1]
        return self


    def rNext(self):
        """
        回傳該節點於樹狀結構中排序的後一個節點。若無則回傳 self。
        
        :rtype: :class:`gallery.models.Node`
        """
        brothers = self.rBrothers()
        if brothers:
            brothers = list(brothers.order_by("-priority", "-create_time"))
            index = brothers.index(self)
            if index > 0: return brothers[index-1]
        return self


    def uPriorityGap(self):
        """
        於移動節點時檢查是否需要更新排序值（priority），若排序值與前一個節點相同，則更新排序值並回傳更新後的排序值；若不需要更新則回傳 False。
        
        :rtype: Integer
        """
        previous = self.rPrevious()
        if previous != self:
            self.priority = previous.priority + NODE_PRIORITY_GAP
            self.save()
            return self.priority
        return False


    def uPriorityRange(self):
        """
        於建立節點時檢查是否需要更新排序值（priority），若排序值與前一個節點相同，則更新排序值並回傳更新後的排序值；若不需要更新則回傳 False。
        
        :rtype: Integer
        """
        brothers = self.rBrothers()
        if brothers:
            brothers = list(brothers.order_by("-priority", "-create_time"))
            brothers.remove(self)
            if brothers: self.priority = brothers[0].priority + NODE_PRIORITY_GAP
            else: self.priority = NODE_PRIORITY_GAP
            self.save()
            return self.priority
        return False


    def moveToBefore(self, anchor):
        """
        將此節點移動到另一個節點（anchor）之前，會檢查父結點（parent）與排序值（priority）。
        
        :param anchor: 節點（:class:`gallery.models.Node`）
        :width anchor: :class:`gallery.models.Node`
        :rtype: Integer
        """
        if anchor.parent:
            self.parent = anchor.parent
            previous = anchor.rPrevious()

            if previous == anchor: self.priority = anchor.priority / 2
            else: self.priority = (previous.priority + anchor.priority)/2
            self.save()

            if self.priority == previous.priority:
                brothers = list(self.rBrothers().order_by("priority", "create_time"))
                for update in brothers[brothers.index(self):]: update.uPriorityGap()
            return self.priority
        return False


    def moveToAfter(self, anchor):
        """
        將此節點移動到另一個節點（anchor）之後，會檢查父結點（parent）與排序值（priority）。
        
        :param anchor: 節點（:class:`gallery.models.Node`）
        :width anchor: :class:`gallery.models.Node`
        :rtype: Integer
        """
        if anchor.parent:
            self.parent = anchor.parent
            next = anchor.rNext()
            if next == anchor: self.priority = anchor.priority + NODE_PRIORITY_GAP
            else: self.priority = (anchor.priority + next.priority)/2
            self.save()

            if self.priority == anchor.priority:
                brothers = list(self.rBrothers().order_by("priority", "create_time"))
                for update in brothers[brothers.index(self):]: update.uPriorityGap()
            return self.priority
        return False


    def rPath(self):
        """
        讀取此結點在樹狀結構中的完整路徑。
        
        :rtype: String
        """
        if self.parent and self.parent.parent: return "%s %s" % (self.parent.rPath(), self.name)
        return self.name


    def copyStructure(self, nodes=[], excluded=[], parent=None):
        """
        複製此節點的結構成為樣版節點。
        
        :rtype: :class:`gallery.models.Template`
        """
        temp = Sample(name=self.name)
        if parent:
            temp.parent = parent
            temp.priority = self.priority
        temp.save()
        children = self.child_nodes.all().order_by("priority")

        if children:
            for child in children:
                if child.id not in excluded:
                    child.copyStructure(nodes=nodes, excluded=excluded, parent=temp)
        return temp


    def copyToTemplate(self, nodes, excluded, template):
        """
        複製節點結構至某樣版（:class:`gallery.models.Template`）底下。

        :rtype: :class:`gallery.models.Template`
        """
        temp = self.copyStructure(nodes, excluded)
        template.sample.add(temp)
        return temp



class Photo(BaseModel):
    """
    相片資料。
    """
    node = M.ForeignKey(Node, related_name="node_photos")
    photo = M.ImageField(upload_to=photo_path)
    origin = M.CharField(verbose_name="原始檔名", max_length=255)
    sha_code = M.CharField(verbose_name="特徵碼", max_length=40)
    note = M.TextField(verbose_name="備註", null=True)
    time = M.DateTimeField(verbose_name="拍照時間", null=True)
    lat = M.DecimalField(verbose_name="緯度", max_digits=16 , decimal_places=9, null=True)
    lng = M.DecimalField(verbose_name="經度", max_digits=16 , decimal_places=9, null=True)
    priority = M.PositiveIntegerField(verbose_name="排序", default=PHOTO_PRIORITY_GAP)
    label = M.ManyToManyField(Label, verbose_name="類別標籤", related_name="label_photo")
    is_public = M.BooleanField(verbose_name="是否核可公開", default=False)


    class Meta:
        permissions = (
            ('remove_photo', u'刪除照片'),
        )


    def __unicode__(self):
        return self.origin


    def save(self, *args, **kwargs):
        """
        儲存時保留原始檔名至 origin 欄位。
        若是新增照片，則以 :meth:`gallery.models.Node.uImageCount` 更新其節點（:class:`gallery.models.Node`）的相片張數。
        若是更新資訊，則檢查其節點是否異動，若有則同時更新前後兩節點的相片張數。
        
        :rtype: True
        """
        is_create = (self.pk is None)
        try: origin_node = Photo.objects.get(id=self.id).node
        except Photo.DoesNotExist: origin_node = False
        current_node = self.node
        if not self.origin: self.origin = self.photo.name
        if not self.sha_code: self.sha_code = sha1(self.photo.read()).hexdigest()
        if not self.time: self.time = self.create_time

        super(Photo, self).save(*args, **kwargs)

        if is_create:
            self.uTimeLatLng()
            self.initThumbnail()
        if self.sha_code:
            photos = self.__class__.objects.filter(sha_code=self.sha_code).order_by('create_time')
            if photos and photos[0] != self:
                try: self.label.add(Label.objects.get(value='repeat_photo'))
                except Label.DoesNotExist: pass
        # if self.sha_code and DUPLICATE_TAG:
        #     try: PHOTO_CONTENT_TYPE.photo_tags.get(obj_id=self.id, type=DUPLICATE_TAG)
        #     except Tag.DoesNotExist:
        #         photos = self.__class__.objects.filter(sha_code=self.sha_code).order_by('create_time')
        #         if photos and photos[0] != self:
        #             tag = Tag(content_type=PHOTO_CONTENT_TYPE, obj_id=self.id, type=DUPLICATE_TAG)
        #             tag .save()
        #     else: pass
        if not origin_node: current_node.uImageCount()
        elif origin_node != current_node:
            origin_node.uImageCount()
            current_node.uImageCount()
        return True


    def delete(self, *args, **kwargs):
        """
        刪除照片時，一並刪除檔案，同時更新其節點（:class:`gallery.models.Node`）的相片張數。
        
        :rtype: True
        """
        storage, path, current_node = self.photo.storage, self.photo.path, self.node
        super(Photo, self).delete(*args, **kwargs)

        storage.delete(path)
        current_node.uImageCount()
        if current_node.improve and not current_node.rPhoto(): current_node.delete()
        return True


    def rProject(self):
        """
        讀取此照片所屬的工程案。
        
        :rtype: :class:`project.models.Project`
        """
        return self.node.case.parent


    def rExt(self):
        """
        讀取照片檔案副檔名。
        
        :rtype: String
        """
        return self.photo.path.split(".")[-1].lower()


    def rSize(self):
        """
        讀取照片檔案大小。
        
        :rtype: Long
        """
        return self.photo.size


    def rFileName(self):
        """
        讀取照片檔案名稱。
        
        :rtype: String
        """
        return basename(self.photo.path)


    def rExif(self):
        """
        讀取照片檔案中的 EXIF 資訊並將其轉為 dictionary 格式回傳。
        
        :rtype: dict
        """
        img = Image.open(self.photo.path)
        exif_data = img._getexif()
        exif = {}
        if exif_data:
            for key, value in exif_data.items():
                exif[TAGS.get(key, key)] = value
        return exif


    def rPath(self):
        """
        讀取檔案路徑。
        
        :rtype: String
        """
        return self.photo.path


    def uTimeLatLng(self):
        """
        將 EXIF 資訊中的 DateTime 紀錄為拍照時間、GPSInfo 紀錄為經緯度。
        由於 EXIF 資訊的地理資訊為度分秒格式（DMS），須利用 :func:`gallery.lib.convert_to_degrees` 轉換為經緯度。
        
        :rtype: True
        """
        exif = self.rExif()
        if exif:
            if exif.has_key("DateTime") and exif["DateTime"]:
                try: self.time = datetime.strptime(exif["DateTime"], '%Y:%m:%d %H:%M:%S')
                except: pass
            if exif.has_key("GPSInfo") and exif["GPSInfo"] and len(exif["GPSInfo"])==4:
                try:
                    lat = convert_to_degrees(exif["GPSInfo"][2])
                    lng = convert_to_degrees(exif["GPSInfo"][4])
                    if exif["GPSInfo"][1] != "N": lat = 0 - lat
                    if exif["GPSInfo"][3] != "E": lng = 0 - lng
                    self.lat, self.lng = lat, lng
                except: pass
            self.save()
        return True


    # def cAllSizeThumbnail(self):
    #     """
    #     製作所有尺寸的縮圖。
        
    #     :rtype: True
    #     """
    #     for size in Size.objects.all():
    #         self.rThumbnail(size=size)
    #     return True


    def initThumbnail(self):
        """
        製作全部的縮圖。
        
        :rtype: True
        """
        for size in Size.objects.all():
            self.rThumbnail(size)
        return True


    def cThumbnail(self, size=None):
        """
        製作指定尺寸的縮圖。
        
        :param size: 縮圖尺寸
        :size limit: string, integer or :class:`gallery.models.Size`
        :rtype: Thumbnail(:class:`gallery.models.Thumbnail`)
        """
        def makeBySize(size):
            size.quality = int(size.quality)
            if size.name == "compress": img = get_thumbnail(self.photo, "%sx%s" % (self.photo.width, self.photo.height), quality=size.quality)
            elif size.width < 0 or size.height < 0:
                img_w, img_h = float(self.photo.width), float(self.photo.height)
                boundary_w, boundary_h = abs(size.height), abs(size.width)

                img_ratio = img_h / img_w
                boundary_ratio = boundary_h / boundary_w
                if img_ratio < boundary_ratio: scale = boundary_w / img_w
                else: scale = boundary_h / img_h

                img = get_thumbnail(self.photo, "%sx%s" % (int(scale * img_w), int(scale * img_h)), quality=size.quality)
            else: img = get_thumbnail(self.photo, "%sx%s" % (size.width, size.height), crop="center", quality=size.quality)
            return img

        def resaveImg(path):
            im = Image.open(path)
            im.save(path, format='JPEG')


        if size:
            if isinstance(size, str) or isinstance(size, unicode):
                try: size = Size.objects.get(name=size)
                except Node.DoesNotExist: raise Exception(_("Can't find match size."))
            elif isinstance(size, int):
                try: size = Size.objects.get(id=size)
                except Node.DoesNotExist: raise Exception(_("Can't find match size."))
            elif isinstance(size, Size): size = size
            else: raise Exception("The param size need to be a string, unicode, integer or Size object")

            try: img = makeBySize(size)
            except:
                resaveImg(self.photo.path)
                img = makeBySize(size)

            new_thumbnail = Thumbnail(original=self, url=img.url, size=size)
            new_thumbnail.save()
            return new_thumbnail
        else: return False


    def rThumbnail(self, size=None):
        """
        讀取縮圖。若無指定尺寸，則利用 :meth:`cThumbnail` 製作。
        
        :param size: 縮圖尺寸
        :size limit: string, integer or :class:`gallery.models.Size`
        :rtype: Thumbnail(:class:`gallery.models.Thumbnail`)
        """
        if size:
            if isinstance(size, str) or isinstance(size, unicode):
                try: size = Size.objects.get(name=size)
                except Node.DoesNotExist: raise Exception(_("Can't find match size."))
            elif isinstance(size, int):
                try: size = Size.objects.get(id=size)
                except Node.DoesNotExist: raise Exception(_("Can't find match size."))
            elif isinstance(size, Size): size = size
            else: raise Exception("The param size need to be a string, unicode, integer or Size object")

            thumbnails = self.thumbnails.filter(size=size).order_by('-create_time')
            if not thumbnails:
                return self.cThumbnail(size=size)
            else:
                return thumbnails[0]
        else: return False


    def rBrothers(self):
        """
        回傳該照片同節點之照片。
        
        :rtype: QuerySet
        """
        if self.node: return self.node.rPhoto()
        return []


    def rPrevious(self):
        """
        回傳該照片前一個張照片。若無則回傳 self。
        
        :rtype: :class:`gallery.models.Photo`
        """
        brothers = self.rBrothers()
        if brothers:
            brothers = list(brothers.order_by("priority", "create_time"))
            index = brothers.index(self)
            if index > 0: return brothers[index-1]
        return self


    def rNext(self):
        """
        回傳該照片前一個張照片。若無則回傳 self。
        
        :rtype: :class:`gallery.models.Photo`
        """
        brothers = self.rBrothers()
        if brothers:
            brothers = list(brothers.order_by("-priority", "-create_time"))
            index = brothers.index(self)
            if index > 0: return brothers[index-1]
        return self


    def uPriorityGap(self):
        """
        於移動照片時檢查是否需要更新排序值（priority），若排序值與前一個節點相同，則更新排序值並回傳更新後的排序值；若不需要更新則回傳 False。
        
        :rtype: Integer
        """
        previous = self.rPrevious()
        if previous != self:
            self.priority = previous.priority + NODE_PRIORITY_GAP
            self.save()
            return self.priority
        return False


    def uPriorityRange(self):
        """
        於建立照片時檢查是否需要更新排序值（priority），若排序值與前一個節點相同，則更新排序值並回傳更新後的排序值；若不需要更新則回傳 False。
        
        :rtype: Integer
        """
        brothers = self.rBrothers()
        if brothers:
            brothers = list(brothers.order_by("-priority", "-create_time"))
            brothers.remove(self)
            if brothers: self.priority = brothers[0].priority + NODE_PRIORITY_GAP
            else: self.priority = NODE_PRIORITY_GAP
            self.save()
            return self.priority
        return False


    def moveToBefore(self, anchor):
        """
        將此照片移動到另一個照片（anchor）之前，會檢查父結點（parent）與排序值（priority）。
        
        :param anchor: 節點（:class:`gallery.models.Photo`）
        :width anchor: :class:`gallery.models.Photo`
        :rtype: Integer
        """
        if anchor.node:
            self.node = anchor.node
            previous = anchor.rPrevious()

            if previous == anchor: self.priority = anchor.priority / 2
            else: self.priority = (previous.priority + anchor.priority)/2
            self.save()

            if self.priority == previous.priority:
                brothers = list(self.rBrothers().order_by("priority", "create_time"))
                for update in brothers[brothers.index(self):]: update.uPriorityGap()
            return self.priority
        return False


    def moveToAfter(self, anchor):
        """
        將此照片移動到另一個照片（anchor）之後，會檢查父結點（parent）與排序值（priority）。
        
        :param anchor: 節點（:class:`gallery.models.Photo`）
        :width anchor: :class:`gallery.models.Photo`
        :rtype: Integer
        """
        if anchor.node:
            self.node = anchor.node
            next = anchor.rNext()
            if next == anchor: self.priority = anchor.priority + NODE_PRIORITY_GAP
            else: self.priority = (anchor.priority + next.priority)/2
            self.save()

            if self.priority == anchor.priority:
                brothers = list(self.rBrothers().order_by("priority", "create_time"))
                for update in brothers[brothers.index(self):]: update.uPriorityGap()
            return self.priority
        return False


    def uRotation(self, degree):
        """
        將照片旋轉 degree 度。同時也會更新縮圖角度。
        
        :param degree: 旋轉角度
        :width degree: Integer
        :rtype: True
        """
        img = Image.open(self.photo.path)
        img = img.rotate(degree*-1, expand=True)
        img.save(self.photo.path)
        self.update_time = datetime.now()
        self.save()
        for size in Size.objects.all():
            self.rThumbnail(size).uRotation(degree)
        return True


    def rCompress(self):
        """
        讀取照片壓縮檔的路徑。
        
        :rtype: String
        """
        return self.rThumbnail(size="compress").rPath()


    def rDTVersion(self):
        """
        讀取照片更新時間並以版本格式回傳。
        
        :rtype: String
        """
        return self.update_time.__format__("%f%S%H%M%d%m%Y")


    def rThumbUrl(self):
        return "/gallery/api/v1/image/view/%s/?v=%s&size=medium" % (self.id, self.rDTVersion())


    def rCompressUrl(self):
        return "/gallery/api/v1/image/view/%s/?v=%s&size=compress" % (self.id, self.rDTVersion())



class Size(BaseModel):
    """
    縮圖尺寸
    """
    name = M.CharField(verbose_name="尺寸名稱", max_length=32, unique=True)
    width = M.IntegerField(verbose_name="寬度")
    height = M.IntegerField(verbose_name="高度")
    quality = M.PositiveIntegerField(verbose_name="壓縮品質", default=80)

    class Meta:
        unique_together = ('width', 'height')
        permissions = (
            ('manage_size', u'管理縮圖尺寸'),
        )


    def __unicode__(self):
        return self.name


    def rSize(self):
        """
        已 thumbnail sorl 格式回傳尺寸寬高。
        
        :rtype: String
        """
        return "%sx%s" % (self.width, self.height)



class Thumbnail(BaseModel):
    """
    紀錄縮圖資訊。
    """
    original = M.ForeignKey(Photo, related_name="thumbnails")
    size = M.ForeignKey(Size, related_name="same_size")
    url = M.CharField(verbose_name="縮圖路徑", max_length=256)
    

    def __unicode__(self):
        return u"%s: %s" % (self.original, self.size)


    def rPath(self):
        """
        讀取縮圖路徑。
        
        :rtype: string
        """
        return join(MEDIA_ROOT, join(*self.url.split("/")))


    def uRotation(self, degree):
        """
        將縮圖旋轉 degree 度。
        
        :param degree: 旋轉角度
        :width degree: Integer
        :rtype: True
        """
        img = Image.open(self.rPath())
        img = img.rotate(degree*-1, expand=True)
        img.save(self.rPath())
        return True



class Comment(BaseModel):
    """
    對於相片的評論。
    """
    photo = M.ForeignKey(Photo, related_name="photo_comments")
    content = M.TextField(verbose_name="內容")

    class Meta:
        permissions = (
            ('update_comment', u'修改評論'),
            ('remove_comment', u'刪除評論'),
        )


    def rProject(self):
        """
        讀取此評論所屬的工程案。
        
        :rtype: :class:`project.models.Project`
        """
        return self.photo.node.case.parent



class Log(M.Model):
    user = M.ForeignKey(User, related_name="user_log_set")
    obj_id = M.IntegerField()
    content_type = M.ForeignKey(ContentType, related_name="contenttype_log")
    is_new = M.BooleanField(default=True)


    # def save(self, *args, **kw):
    #     try: event = Event.objects.get_or_create(project=self.content_type.get_object_for_this_type(id=self.obj_id).rProject(), event_date=datetime.now().date())
    #     except MultipleObjectsReturned:
    #         events = Event.objects.filter(project=self.content_type.get_object_for_this_type(id=self.obj_id).rProject(), event_date=datetime.now().date()).order_by("id")
    #         event = events[0]
    #         for i in events[1:]: i.delete()
    #     else:
    #         super(Log, self).save(*args, **kw)


# class Tag(M.Model):
#     content_type = M.ForeignKey(ContentType, related_name="photo_tags")
#     obj_id = M.IntegerField()
#     type = M.ForeignKey(Option)



# class Event(M.Model):
#     project = M.ForeignKey(OBJECT)
#     event_date = M.DateField(verbose_name="發生日期")


#     def is_checkpoint_new(self):
#         e_history = Node.history.filter(case_id=self.project.photo_case.id, history_date__range=(datetime.combine(self.event_date, time.min), datetime.combine(self.event_date, time.max)),)
#         if len(e_history) > 0: return True
#         else: return False


#     def is_photo_new(self):
#         e_history = Photo.history.filter(node_id__in=[node.id for node in self.project.photo_case.nodes.all()], history_date__range=(datetime.combine(self.event_date, time.min), datetime.combine(self.event_date, time.max)),)
#         if len(e_history) > 0: return True
#         else: return False


#     def is_comment_new(self):
#         photo = []
#         for node in self.project.photo_case.nodes.all(): photo += [photo.id for photo in node.node_photos.all()]
#         e_history = Comment.history.filter(photo_id__in=photo, history_date__range=(datetime.combine(self.event_date, time.min), datetime.combine(self.event_date, time.max)),)
#         if len(e_history): return True
#         else: return False




##############################################################################################################
###  ========================================  Signal Functions  ========================================  ###
##############################################################################################################

def cCaseBySignal(sender, instance, **kwargs):
    """
    當父層物件儲存時，檢查是否有建立關聯（:class:`gallery.models.Case`）。
    若無則建立關聯物件（:class:`gallery.models.Case`）。
    
    :rtype: True
    """
    try: instance.photo_case
    except Case.DoesNotExist:
        new_case = Case(parent=instance)
        new_case.save()
    return True


def assignPermissionBySignal(sender, instance, **kwargs):
    """
    當儲存使用者對父層物件的群組關聯（:class:`fishuser.models.FRCMUserGroup`）時，一並賦予對應的物件權限。
    
    :rtype: True
    """
    try: case = instance.project.photo_case
    except Case.DoesNotExist: case = False

    if case:
        current_permissions = get_perms(instance.user, case)
        permissions = [value for value, name in case.__class__._meta.permissions]

        for permission in current_permissions:
            remove_perm(permission, instance.user, case)

        if instance.is_active:
            for permission in IM_PERMISSIONS[instance.group.name]:
                if permission in permissions: assign_perm(permission, instance.user, case)


def removePermission(sender, instance, **kwargs):
    """
    當使用者對父層物件的群組關聯（:class:`fishuser.models.FRCMUserGroup`）被刪除時，一並移除對應的物件權限。
    
    :rtype: True
    """
    try: case = instance.project.photo_case
    except Case.DoesNotExist: case = False

    if case:
        current_permissions = get_perms(instance.user, case)

        for permission in current_permissions:
            remove_perm(permission, instance.user, case)


def removeThumbnailFile(sender, instance, **kwargs):
    """
    刪除縮圖（:class:`gallery.models.Thumbnail`）時，一並刪除檔案。
    
    :rtype: True
    """
    delete_thumbnail(instance.url)
    return True


post_save.connect(cCaseBySignal, OBJECT)
post_save.connect(assignPermissionBySignal, FRCMUserGroup)
post_delete.connect(removePermission, FRCMUserGroup)
post_delete.connect(removeThumbnailFile, Thumbnail)


# try: PHOTO_CONTENT_TYPE = ContentType.objects.get_for_model(Photo)
# except DatabaseError: PHOTO_CONTENT_TYPE = False
# except ContentType.DoesNotExist: PHOTO_CONTENT_TYPE = False

# try: DUPLICATE_TAG = Option.objects.get(swarm='cpp-photo-tag', value='duplicate')
# except DatabaseError: DUPLICATE_TAG = False
# except Option.DoesNotExist: DUPLICATE_TAG = False