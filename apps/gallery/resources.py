#-*- coding: utf8 -*-
from os.path import join, dirname
from datetime import datetime, time
from json import dumps, loads
from urlparse import parse_qs
from calendar import monthrange
from math import ceil
from PIL import Image
from django.conf import settings
from django.conf.urls import url
from django.core.urlresolvers import reverse
from django.core.exceptions import MultipleObjectsReturned
from django.core.servers.basehttp import FileWrapper
from django.template import RequestContext
from django.template.loader import get_template
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext as _
from django.db.models import Q
from django.contrib.auth.models import User, Group
from tastypie import fields
from tastypie.http import HttpResponse, HttpBadRequest, HttpUnauthorized, HttpForbidden
from tastypie.authentication import SessionAuthentication, ApiKeyAuthentication, MultiAuthentication
from tastypie.authorization import Authorization
from tastypie.serializers import Serializer
from tastypie.resources import ModelResource, ALL, ALL_WITH_RELATIONS
from tastypie.exceptions import ImmediateHttpResponse
from tastypie.utils import trailing_slash
from tastypie.cache import SimpleCache
from guardian.core import ObjectPermissionChecker
from guardian.shortcuts import get_perms, get_objects_for_user
try: from guardian.shortcuts import assign_perm, get_objects_for_user
except: from guardian.shortcuts import assign as assign_perm

from docxgen import opendocx, getdocument, getdocbody, replaceText, replaceImage, appendDoc, outputdocx, make_examine_doc, make_construction_photo_doc, make_maintain_six_photo_doc, make_maintain_nine_photo_doc, make_maintain_twelve_photo_doc
from gallery.models import NODE_PRIORITY_GAP, Option, Case, Node, Photo, Size, Comment, Log, Label, Template, Sample
from fishuser.models import FRCMUserGroup

try: from settings import IMAGE_RESPONSE
except ImportError: IMAGE_RESPONSE = "default"

try: from settings import SPECIAL_APIKEY
except ImportError: SPECIAL_APIKEY = []

try: from settings import PHOTODOC
except ImportError: PHOTODOC = []

try: from settings import IMPROVE_SHEET_NAME
except ImportError: IMPROVE_SHEET_NAME = u"缺失改善表"

IMPROVE_TAG = {1: Label.objects.get(value="improve_before"), 2: Label.objects.get(value="improve_implement"), 3: Label.objects.get(value="improve_after")}


__enable__ = ["CaseResource", "NodeResource", "PhotoResource", "ImageResource", "SizeResource", "CommentResource", "LabelResource", "TemplateResource", "SampleResource"]


def build_content_type(format, encoding="utf-8"):
    """
    回傳資料時允許自訂義 content type 中的 charset，預設為 utf-8。
    """
    if "charset" in format:
        return format

    return "%s; charset=%s" % (format, encoding)



class IISIApiKeyAuthentication(ApiKeyAuthentication):
    """
    以特殊 API Key 作為驗證 token，以支援工程資訊圖台跨平台驗證。
    """
    def is_authenticated(self, request, **kwargs):
        """
        讀取 API Key 是否有效，若有效則以使用者名稱運算該次連線權限。
        自訂義的 API 將不會自動執行驗證！請自行執行 self.is_authenticated(request) 驗證使用者！
        """
        username = request.META.get("HTTP_USERNAME") or request.POST.get("username") or request.GET.get("username")
        api_key = request.META.get("HTTP_APIKEY") or request.POST.get("apikey") or request.GET.get("apikey")

        if not username or not api_key:
            if request.user: return request.user.is_authenticated()
            else: return self._unauthorized()

        if api_key in SPECIAL_APIKEY:
            try: user = User.objects.get(username=username)
            except (User.DoesNotExist, User.MultipleObjectsReturned): return self._unauthorized()
            request.user = user
            return True
        return False



class CustomApiKeyAuthentication(ApiKeyAuthentication):
    """
    手機 APP 的登入驗證。由於 APP 端沒有 Cookie 可以記錄登入狀態，故改以 API Key 作為驗證 token。
    請於需要支援 APP 的 API Resource Meta 中的 authentication 加入此驗證方式。
    """
    def is_authenticated(self, request, **kwargs):
        """
        此自訂義驗證會先利用使用者名稱（username）查詢使用者（User），若查無使用者即回傳驗證不通過，若有則將其設為 request.user。
        最後再利用 API Key（apikey）驗證使用者的登入狀態。

        自訂義的 API 將不會自動執行驗證！請自行執行 self.is_authenticated(request) 驗證使用者！
        """
        username = request.META.get("HTTP_USERNAME") or request.POST.get("username")
        api_key = request.META.get("HTTP_APIKEY") or request.POST.get("apikey")
        if not username or not api_key:
            if request.user: return request.user.is_authenticated()
            else: return self._unauthorized()
        try: user = User.objects.get(username=username)
        except (User.DoesNotExist, User.MultipleObjectsReturned): return self._unauthorized()
        request.user = user
        return self.get_key(user, api_key)



class CustomSerializer(Serializer):
    """
    複寫原本的 serializer，使其支援解析更多種類的 content types 資料格式。

    手機 APP 的一般 request 使用 application/x-www-form-urlencoded 的 content types，上傳照片時則為 multipart/form-data。
    """
    formats = ["json", "jsonp", "xml", "yaml", "html", "plist", "urlencode", "form"]
    content_types = {
        "json": "application/json",
        "jsonp": "text/javascript",
        "xml": "application/xml",
        "yaml": "text/yaml",
        "html": "text/html",
        "plist": "application/x-plist",
        "urlencode": "application/x-www-form-urlencoded",
        "form": "multipart/form-data",
        }


    def from_urlencode(self, data, options=None):
        """ handles basic formencoded url posts """
        qs = dict((k, v if len(v)>1 else v[0] ) for k, v in parse_qs(data).iteritems())
        return qs

    def from_form(self, content):
        try:
            dict = cgi.parse_multipart(StringIO(content), self.form_boundary)
        except Exception, e: raise e
        for key, value in dict.iteritems():
            dict[key] = value[0] if len(value) > 0 else None
        return dict



class PrivateCache(SimpleCache):

    def cache_control(self):
        control = super(PrivateCache, self).cache_control()
        control.update({"s-maxage": 31556926})
        control.update({"max-age": 31556926})
        control.update({"private": True})

        return control



class CaseResource(ModelResource):

    class Meta:
        authentication = MultiAuthentication(SessionAuthentication(), CustomApiKeyAuthentication(), IISIApiKeyAuthentication())
        authorization = Authorization()
        allowed_methods = ["get", "post", "put"]
        always_return_data = True
        resource_name = "case"
        # serializer = CustomSerializer()
        queryset = Case.objects.all()
        filtering = {
            "parent": ("exact"),
        }


    def create_response(self, request, data, response_class=HttpResponse, **response_kwargs):
        """
        複寫原本的 create_response，讓自訂義資料可以依照 request 本身的字集處理。
        """
        desired_format = self.determine_format(request)
        serialized = self.serialize(request, data, desired_format)
        return response_class(content=serialized, content_type=build_content_type(desired_format), **response_kwargs)


    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/tree%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view("tree"), name="api_tree"),
            url(r"^(?P<resource_name>%s)/tree/(?P<case_id>[0-9]+)%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view("structure"), name="api_structure"),
            url(r"^(?P<resource_name>%s)/public/list/(?P<year>[0-9]+)%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view("public_list"), name="api_public_list"),
        ]


    def obj_get_list(self, bundle, **kwargs):
        """
        複寫原本的 get_list，使用者只能讀取與自己有關的 Case。
        """
        request = bundle.request
        relation = Relational.objects.filter(user=request.user)
        result = super(CaseResource, self).obj_get_list(bundle, request=request)
        return result.filter(case_image_relation__in=relation)


    def tree(self, request, **kwargs):
        """
        讀取 Case 時一並回傳其節點（:class:`image_management.models.Node`）的樹狀結構。
        使用者只能讀取與自己有關的 Case。
        """
        self.method_check(request, allowed=["get"])
        self.is_authenticated(request)

        relation = Relational.objects.filter(user=request.user)
        result = self._meta.queryset.filter(case_image_relation__in=relation)

        data = []
        for case in result:
            root = case.rRootNode()
            data.append({"id": case.parent.id, "name": case.parent.name, "node": root.rTree()})
        return self.create_response(request, data)


    def structure(self, request, **kwargs):
        """
        讀取該 Case （:class:`image_management.models.Node`）查驗點的樹狀結構。
        使用者只能讀取與自己有關的 Case。
        """
        self.method_check(request, allowed=["get"])
        self.is_authenticated(request)

        try: case = self._meta.queryset.get(id=kwargs["case_id"])
        except Case.DoesNotExist: raise ImmediateHttpResponse(HttpBadRequest(_("invalid case id.")))

        checker = ObjectPermissionChecker(request.user)
        if checker.has_perm("view_case", case):
            root = case.rRootNode()
            return self.create_response(request, [root.rTree()])
        else: raise ImmediateHttpResponse(HttpForbidden(_("Has not permission to view case.")))


    def public_list(self, request, **kwargs):
        """
        依年度讀取公開工程列表。
        """
        self.method_check(request, allowed=["get"])

        if kwargs.has_key("year"): year = kwargs["year"]
        else: raise ImmediateHttpResponse(HttpBadRequest(_("Need year in url.")))

        try: year = int(year)
        except: raise ImmediateHttpResponse(HttpBadRequest(_("Invalid year format.")))

        data = request.GET
        limit = data.get('limit', 25)
        offset = data.get('offset', 0)
        try:
            limit = int(limit)
        except:
            limit = 25

        try:
            offset = int(offset)
        except:
            offset = 0

        public_cases = self._meta.queryset.filter(parent__year=year, parent__is_public=True, parent__deleter__isnull=True).order_by('parent__name')
        total = public_cases.count()

        meta = {'limit': limit, 'offset': offset, 'total_count': total}
        objects = []

        for obj in public_cases[offset*limit:(offset+1)*limit]:
            objects.append({'name': obj.parent.name, 'url': reverse("public_photo", kwargs={"project_id": obj.parent.id})})

        return self.create_response(request, {'meta': meta, 'objects': objects})



class LabelResource(ModelResource):
    
    class Meta:
        authentication = MultiAuthentication(SessionAuthentication(), CustomApiKeyAuthentication(), IISIApiKeyAuthentication())
        authorization = Authorization()
        allowed_methods = ["get"]
        always_return_data = True
        resource_name = "label"
        # serializer = CustomSerializer()
        queryset = Label.objects.all()
        excludes = []
        ordering = ["create_time"]
        filtering = {
            "id": ("exact"),
        }



class TemplateResource(ModelResource):
    label = fields.ToManyField(LabelResource, "label")
    
    class Meta:
        authentication = MultiAuthentication(SessionAuthentication(), CustomApiKeyAuthentication(), IISIApiKeyAuthentication())
        authorization = Authorization()
        allowed_methods = ["get", "post", "put", "delete"]
        always_return_data = True
        resource_name = "template"
        # serializer = CustomSerializer()
        queryset = Template.objects.all()
        excludes = []
        ordering = ["create_time"]
        filtering = {
            "id": ("exact"),
            "label": ALL_WITH_RELATIONS,
        }


    def create_response(self, request, data, response_class=HttpResponse, **response_kwargs):
        """
        複寫原本的 create_response，讓自訂義資料可以依照 request 本身的字集處理。
        """
        desired_format = self.determine_format(request)
        serialized = self.serialize(request, data, desired_format)
        return response_class(content=serialized, content_type=build_content_type(desired_format), **response_kwargs)


    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/(?P<case_id>[0-9]+)/export%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view("export"), name="api_export"),
        ]


    def obj_get_list(self, bundle, **kwargs):
        """
        複寫原本的 get_list，可依照樣版建立者分類。
        """
        request = bundle.request
        data = request.GET
        user = request.user
        result = super(TemplateResource, self).obj_get_list(bundle, request=request)

        if data.has_key("owner"):
            owner = data["owner"]
            set = Q()
            if owner == "my": set = Q(creator=user)
            elif owner == "unit" and data.has_key("case"):
                try: set = Q(creator__projectup_user__unit=Case.objects.get(id=data["case"]).parent.frcmusergroup_set.filter(group__id=5)[0].user.user_profile.unit)
                except IndexError: set = Q(creator__projectup_user__unit=user.user_profile.unit)
            elif owner == "public": set = Q(public=True)
            else: raise ImmediateHttpResponse(HttpBadRequest(_("Illegal parameter.")))
            result = result.filter(set)

        return result.order_by('name', 'id')



    def obj_create(self, bundle, **kwargs):
        """
        建立樣版。
        """
        request = bundle.request
        data = bundle.data

        if not data.has_key("name"): raise ImmediateHttpResponse(HttpBadRequest(_("Need template name.")))
        if get_objects_for_user(request.user, 'gallery.create_node'):
            if not data.has_key("sample"):
                bundle.data["sample"] = []
            if not data.has_key("label"):
                bundle.data["label"] = []
            return super(TemplateResource, self).obj_create(bundle, request=request, creator=request.user)
        else: raise ImmediateHttpResponse(HttpForbidden(_("Has not permission to create template.")))


    def obj_update(self, bundle, **kwargs):
        """
        更新樣版。
        """
        try: bundle.obj = self.obj_get(bundle=bundle, **kwargs)
        except Template.DoesNotExist: raise ImmediateHttpResponse(HttpBadRequest(_("Can't find match data.")))

        request = bundle.request
        data = bundle.data
        if get_objects_for_user(request.user, 'gallery.create_node'):
            if not data.has_key("sample"):
                bundle.data["sample"] = bundle.obj.sample.all()

            if not data.has_key("label"):
                bundle.data["label"] = bundle.obj.label.all()
            return super(TemplateResource, self).obj_update(bundle, **kwargs)
        else: raise ImmediateHttpResponse(HttpForbidden(_("Has not permission to update size.")))


    def export(self, request, **kwargs):
        """
        將結點結構匯出至樣版（:class:`gallery.models.Template`）。
        """
        self.is_authenticated(request)
        self.method_check(request, allowed=["post"])

        data = request.POST
        if not data: data = loads(request.body)

        try: case = Case.objects.get(id=kwargs["case_id"])
        except: raise ImmediateHttpResponse(HttpBadRequest(_("No match case.")))

        if data.has_key("name"): name = data["name"]
        else: raise ImmediateHttpResponse(HttpBadRequest(_("Need template name.")))

        if data.has_key("nodes"): nodes = data['nodes']
        else: raise ImmediateHttpResponse(HttpBadRequest(_("Need nodes id.")))

        if data.has_key("excluded"): excluded = data['excluded']
        else: raise ImmediateHttpResponse(HttpBadRequest(_("Need excluded id.")))

        nodes = [int(i) for i in nodes]
        excluded = [int(i) for i in excluded]

        user = request.user
        checker = ObjectPermissionChecker(user)
        if checker.has_perm("create_node", case):
            new_template = Template(name=name, creator=user)
            new_template.save()
            new_template.importNodes(nodes=nodes, excluded=excluded)

            return self.create_response(request, {"id": new_template.id, "name": new_template.name, "public": new_template.public})
        else: raise ImmediateHttpResponse(HttpForbidden(_("Has not permission to create node.")))



class SampleResource(ModelResource):
    parent = fields.ForeignKey("self", "parent", null=True)

    class Meta:
        authentication = MultiAuthentication(SessionAuthentication(), CustomApiKeyAuthentication(), IISIApiKeyAuthentication())
        authorization = Authorization()
        allowed_methods = ["get", "post", "put", "delete"]
        always_return_data = True
        resource_name = "sample"
        # serializer = CustomSerializer()
        queryset = Sample.objects.all()
        excludes = []
        ordering = ["id", "parent", "name", "priority"]
        filtering = {
            "id": ("exact"),
            "parent": ALL_WITH_RELATIONS,
        }


    def create_response(self, request, data, response_class=HttpResponse, **response_kwargs):
        """
        複寫原本的 create_response，讓自訂義資料可以依照 request 本身的字集處理。
        """
        desired_format = self.determine_format(request)
        serialized = self.serialize(request, data, desired_format)
        return response_class(content=serialized, content_type=build_content_type(desired_format), **response_kwargs)


    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/(?P<template_id>[0-9]+)/roots%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view("template_roots"), name="api_template_node"),
            url(r"^(?P<resource_name>%s)/(?P<parent_id>[0-9]+)/samples%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view("template_samples"), name="api_template_node"),
        ]


    def template_roots(self, request, **kwargs):
        """
        獲取樣版 ROOT 資料夾，產生對應JSTREE之資料格式。
        """
        self.is_authenticated(request)
        self.method_check(request, allowed=["get"])

        if kwargs.has_key("template_id"): template_id = kwargs["template_id"]
        else: raise ImmediateHttpResponse(HttpBadRequest(_("Need template_id in url.")))

        try: template = Template.objects.get(id=template_id)
        except Node.DoesNotExist: raise ImmediateHttpResponse(HttpBadRequest(_("Can find match template.")))

        user = request.user
        checker = ObjectPermissionChecker(user)
        if get_objects_for_user(request.user, 'gallery.create_node'):
            data = []
            for root in template.sample.filter(parent=None).order_by("priority"):
                root_data = {
                    "parent": "#",
                    "text": root.name,
                    "state":{
                        "opened": False,
                        "selected": False
                    },
                    "li_attr": {
                        "sample_id": root.id
                    },
                    "data": {
                        "sample_id": root.id
                    }
                }

                if len(root.child_samples.all()):
                    root_data["children"] = True
                else:
                    root_data["children"] = False
                data.append(root_data)
            return HttpResponse(dumps(data), content_type="application/json")
        else: raise ImmediateHttpResponse(HttpForbidden(_("Has not permission to read.")))


    def template_samples(self, request, **kwargs):
        """
        獲取樣版 ROOT 資料夾底下的樣點，產生對應JSTREE之資料格式。
        """
        data = request.GET
        self.method_check(request, allowed=["get"])

        if kwargs.has_key("parent_id"): parent_id = kwargs["parent_id"]
        else: raise ImmediateHttpResponse(HttpBadRequest(_("Need parent_id in url.")))

        try: parent = Sample.objects.get(id=parent_id)
        except Node.DoesNotExist: raise ImmediateHttpResponse(HttpBadRequest(_("Can find match template.")))


        user = request.user
        checker = ObjectPermissionChecker(user)
        if get_objects_for_user(request.user, 'gallery.create_node'):
            samples = Sample.objects.filter(parent=parent).order_by("priority")
            data = []

            for sample in samples:
                sample_data = {
                    "parent": kwargs["parent_id"],
                    "text": sample.name,
                    "state":{
                        "opened": False,
                        "selected": False
                    },
                    "li_attr": {
                        "sample_id": sample.id
                    },
                    "data": {
                        "sample_id": sample.id
                    }
                }

                if len(sample.child_samples.all()):
                    sample_data["children"] = True
                else:
                    sample_data["children"] = False
                data.append(sample_data)
               
            return HttpResponse(dumps(data), content_type="application/json")
        else: raise ImmediateHttpResponse(HttpForbidden(_("Has not permission to read.")))


    def obj_create(self, bundle, **kwargs):
        """
        建立樣版查驗點。
        """
        request = bundle.request
        data = bundle.data

        if data.has_key("template_id"): template_id = data["template_id"]
        else: raise ImmediateHttpResponse(HttpBadRequest(_("Need template_id in data.")))
        if data.has_key("parent_id"): parent_id = data["parent_id"]
        else: raise ImmediateHttpResponse(HttpBadRequest(_("Need parent_id in data.")))

        try: 
            template = Template.objects.get(id=template_id)
        except Template.DoesNotExist: raise ImmediateHttpResponse(HttpBadRequest(_("Can't find match template.")))
        if parent_id:
            try:
                parent = self._meta.queryset.get(id=parent_id)
            except Sample.DoesNotExist: raise ImmediateHttpResponse(HttpBadRequest(_("Can't find match sample.")))

        if get_objects_for_user(request.user, 'gallery.create_node'):
            if parent_id:
                brother = self._meta.queryset.filter(parent=parent).order_by("-priority")
                priority = NODE_PRIORITY_GAP
                if brother: priority = brother[0].priority + NODE_PRIORITY_GAP
                bundle = super(SampleResource, self).obj_create(bundle, request=request, parent=parent, creator=request.user, priority=priority)

            else:
                bundle = super(SampleResource, self).obj_create(bundle, request=request, creator=request.user)
                template.sample.add(bundle.obj)
            
            return bundle
        else: raise ImmediateHttpResponse(HttpForbidden(_("Has not permission to create template.")))


    def obj_update(self, bundle, **kwargs):
        """
        修改樣版資料夾（:class:`image_management.models.Sample`）。

        若有 parent_id 會將其轉為物件，並檢查：
            * :meth:`image_management.models.Sample.isChildOf` 檢查目標節點是否是自己的子節點，無法移動至自己的子節點。
        """
        try: bundle.obj = self.obj_get(bundle=bundle, **kwargs)
        except Sample.DoesNotExist: raise ImmediateHttpResponse(HttpBadRequest(_("Can't find match data.")))

        request = bundle.request
        data = bundle.data
        if get_objects_for_user(request.user, 'gallery.create_node'):
            parent = False
            if data.has_key("parent_id"):
                try: parent = Sample.objects.get(id=data["parent_id"])
                except Sample.DoesNotExist: raise ImmediateHttpResponse(HttpBadRequest(_("Can't find match sample.")))
                del data["parent_id"]
            if data.has_key("before_id"):
                try: before = Sample.objects.get(id=data["before_id"])
                except Sample.DoesNotExist: raise ImmediateHttpResponse(HttpBadRequest(_("Can't find match sample.")))
                bundle.obj.moveToAfter(before)
                del data["before_id"]
            if data.has_key("after_id"):
                try: after = Sample.objects.get(id=data["after_id"])
                except Sample.DoesNotExist: raise ImmediateHttpResponse(HttpBadRequest(_("Can't find match sample.")))
                bundle.obj.moveToBefore(after)
                del data["after_id"]
            for key in data:
                if key in ["priority"]:
                    try: data[key] = abs(int(data[key]))
                    except: raise ImmediateHttpResponse(HttpForbidden(_("%s need to be a positive integer." % key)))

            bundle.obj._history_user = request.user
            super(SampleResource, self).obj_update(bundle, **kwargs)
            if parent:
                # if bundle.obj.isRoot(): raise ImmediateHttpResponse(HttpBadRequest(_("Can't move root node.")))
                # if not bundle.obj.isSameCase(bundle.obj): raise ImmediateHttpResponse(HttpBadRequest(_("Can't move node to different case.")))
                if parent.isChildOf(bundle.obj): raise ImmediateHttpResponse(HttpBadRequest(_("Can't move to self's child sample.")))
                setattr(bundle.obj, "parent", parent)
                bundle.obj.save()
                bundle.obj.uPriorityRange()
                
            return bundle
        else: raise ImmediateHttpResponse(HttpForbidden(_("Has not permission to update node.")))


    def obj_delete(self, bundle, **kwargs):
        """
        刪除樣版資料夾（:class:`image_management.models.Sample`）。
        """
        try: bundle.obj = self.obj_get(bundle=bundle, **kwargs)
        except Sample.DoesNotExist: raise ImmediateHttpResponse(HttpBadRequest(_("Can't find match data.")))

        request = bundle.request
        if get_objects_for_user(request.user, 'gallery.create_node'):
            bundle.obj._history_user = request.user
            return super(SampleResource, self).obj_delete(bundle, **kwargs)
        else: raise ImmediateHttpResponse(HttpForbidden(_("Has not permission to delete sample.")))



class NodeResource(ModelResource):
    case = fields.ForeignKey(CaseResource, "case", null=True)
    parent = fields.ForeignKey("self", "parent", null=True)

    class Meta:
        authentication = MultiAuthentication(SessionAuthentication(), CustomApiKeyAuthentication(), IISIApiKeyAuthentication())
        authorization = Authorization()
        allowed_methods = ["get", "post", "put", "delete"]
        always_return_data = True
        resource_name = "node"
        # serializer = CustomSerializer()
        queryset = Node.objects.all()
        excludes = []
        ordering = ["id", "parent", "name", "priority"]
        filtering = {
            "id": ("exact"),
            "case": ALL_WITH_RELATIONS,
            "parent": ALL_WITH_RELATIONS,
        }


    def create_response(self, request, data, response_class=HttpResponse, **response_kwargs):
        """
        複寫原本的 create_response，讓自訂義資料可以依照 request 本身的字集處理。
        """
        desired_format = self.determine_format(request)
        serialized = self.serialize(request, data, desired_format)
        return response_class(content=serialized, content_type=build_content_type(desired_format), **response_kwargs)

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/timeline%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view("time_line"), name="api_time_line"),
            url(r"^(?P<resource_name>%s)/root_node%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view("root_node"), name="api_root_node"),
            url(r"^(?P<resource_name>%s)/root_improve%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view("root_improve"), name="api_root_improve"),
            url(r"^(?P<resource_name>%s)/sub_node/(?P<node_id>[0-9]+)%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view("sub_node"), name="api_move"),
            url(r"^(?P<resource_name>%s)/image_docx%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view("image_docx"), name="api_image_docx"),
            url(r"^(?P<resource_name>%s)/(?P<node_id>[0-9]+)/insert%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view("insert"), name="api_insert"),
            url(r"^(?P<resource_name>%s)/(?P<improve_id>[0-9]+)/delete%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view("improve_delete"), name="api_improve_delete"),
        ]

    def time_line(self, request, **kwargs):
        """
        產生拍照時間的時間樹。
        """
        data = request.GET
        times = Photo.objects.filter(node__case=data["case"]).exclude(time=None).values("time").order_by("time")

        time_dict, count = {}, {}
        for take in times:
            year = take["time"].year
            month = "%02d" % take["time"].month
            day = "%02d" % take["time"].day

            if not time_dict.has_key(year):
                time_dict[year] = {}
                count["count-%s" % year] = 0
            if not time_dict[year].has_key(month):
                time_dict[year][month] = []
                count["count-%s-%s" % (year, month)] = 0
            if day not in time_dict[year][month]:
                time_dict[year][month].append(day)
                count["count-%s-%s-%s" % (year, month, day)] = 0

            count["count-%s" % year] += 1
            count["count-%s-%s" % (year, month)] += 1
            count["count-%s-%s-%s" % (year, month, day)] += 1

        time_tree = []
        year_order = [y for y in time_dict]
        year_order.sort()
        for year in year_order:
            year_child = []
            month_order = [m for m in time_dict[year]]
            month_order.sort()
            for month in month_order:
                month_child = []
                time_dict[year][month].sort()
                for day in time_dict[year][month]:
                    month_child.append({"id": "take_%s-%s-%s" % (year, month, day), "text": day, "icon": "glyphicon glyphicon-calendar", "data": {"count": count["count-%s-%s-%s" % (year, month, day)]}})

                year_child.append({"id": "take_%s-%s-" % (year, month), "text": month, "children": month_child, "icon": "glyphicon glyphicon-calendar", "data": {"count": count["count-%s-%s" % (year, month)]}})
            time_tree.append({"id": "take_%s--" % (year), "text": year, "children": year_child, "icon": "glyphicon glyphicon-calendar", "data": {"count": count["count-%s" % (year)]}})

        if len(time_tree):
            time_tree[-1]["state"] = {"opened": True, "selected": False}
            time_tree[-1]["children"][-1]["state"] = {"opened": True, "selected": False}
            time_tree[-1]["children"][-1]["children"][-1]["state"] = {"opened": True, "selected": True}

        return HttpResponse(dumps(time_tree), content_type="application/json")


    def root_node(self, request, **kwargs):
        """
            產生對應JSTREE之資料格式，ROOT資料夾
        """
        data = request.GET
        pile = Node.objects.filter(case__id=data["case"], parent__isnull=True, improve=False).order_by('id')
        if len(pile) > 1:
            for i in pile[1:]:
                if i.total_count < 1:
                    try: i.delete()
                    except: pass

        node = Node.objects.get(case__id=data["case"], parent__isnull=True, improve=False)
        json_data = {
            "id": node.id,
            "parent": "#",
            "text": node.name,
            "state": {
                "opened": False,
                "selected": False
            },
            "li_attr": {
                "node_id": node.id
            },
            "data": {
                "node_child_count": len(node.child_nodes.all()),
                "images_count": node.images_count or 0,
                "total_count": node.total_count or 0,
                "default": True,
            },
            "icon": "glyphicon glyphicon-folder-close"
        }

        if len(node.child_nodes.all()):
            json_data["children"] = True
        else:
            json_data["children"] = False
        return HttpResponse(dumps(json_data), content_type="application/json")


    def root_improve(self, request, **kwargs):
        """
            產生對應JSTREE之資料格式，ROOT資料夾
        """
        data = request.GET
        improves = Node.objects.filter(case__id=data["case"], parent__isnull=True, improve=True)
        data = []
        for index, node in enumerate(improves):
            json_data = {
                "id": node.id,
                "parent": "#",
                "text": node.name,
                "state": {
                    "opened": (index == len(improves)-1),
                    "selected": (index == len(improves)-1)
                },
                "li_attr": {
                    "node_id": node.id
                },
                "data": {
                    "node_child_count": len(node.child_nodes.all()),
                    "images_count": node.images_count or 0,
                    "total_count": node.total_count or 0,
                    "default": True,
                },
                "icon": "glyphicon glyphicon-folder-close"
            }

            if len(node.child_nodes.all()):
                json_data["children"] = True
            else:
                json_data["children"] = False

            data.append(json_data)
        return HttpResponse(dumps(data), content_type="application/json")


    def sub_node(self, request, **kwargs):
        """
            產生對應JSTREE之資料格式，SUB資料夾
        """
        nodes = Node.objects.filter(parent__id=kwargs["node_id"]).order_by("priority")
        json_data = []
        for node in nodes:
            node_data = {
                "id": node.id,
                "parent": kwargs["node_id"],
                "text": node.name,
                "state":{
                    "opened": False,
                    "selected": False
                },
                "li_attr": {
                    "node_id": node.id,
                    # "parent_id": node.parent.id,
                },
                "data": {
                    "node_child_count": len(node.child_nodes.all()),
                    "images_count": node.images_count or 0,
                    "total_count": node.total_count or 0,
                    "default": node.default,
                }
            }
            if node.default:
                node_data["icon"] = "glyphicon glyphicon-folder-close"

            if len(node.child_nodes.all()):
                node_data["children"] = True
            else:
                node_data["children"] = False
            json_data.append(node_data)
           
        return HttpResponse(dumps(json_data), content_type="application/json")


    def image_docx(self, request, **kwargs):
        """
        產生含工程相片的 docx 檔案。
        """
        total = 0
        image_list = []
        data = request.POST

        if data.has_key("filename"): filename = request.POST["filename"]
        else: filename = False

        if data.has_key("doc_type"): doc_type = request.POST["doc_type"]
        else: raise ImmediateHttpResponse(HttpBadRequest(_("Need doc_type in data.")))

        if data.has_key("node_id"): node_id = request.POST.getlist("node_id")
        else: raise ImmediateHttpResponse(HttpBadRequest(_("Need node_id in data.")))

        try: node_list = self._meta.queryset.filter(id__in=node_id).order_by("priority")
        except ValueError: raise ImmediateHttpResponse(HttpBadRequest(_("invalid node id.")))

        if not node_list: raise ImmediateHttpResponse(HttpBadRequest(_("Can not find match node.")))
        if not filename: filename = node_list[0].case.parent.name
        
        for node in node_list:
            image_list += list(node.node_photos.all().order_by("priority"))

        if not len(image_list): raise ImmediateHttpResponse(HttpBadRequest(_("No image include.")))

        if doc_type == "examine": head = make_examine_doc(image_list)
        elif doc_type == "construction_photo": head = make_construction_photo_doc(image_list)
        elif doc_type == "maintain_6": head = make_maintain_six_photo_doc(image_list)
        elif doc_type == "maintain_9": head = make_maintain_nine_photo_doc(image_list)
        elif doc_type == "maintain_12": head = make_maintain_twelve_photo_doc(image_list)
        else: raise ImmediateHttpResponse(HttpBadRequest(_("Wrong document type.")))

        for doc in PHOTODOC:
            if doc["doc"] == doc_type:
                name = doc["name"]
                break
            for sub in doc["sub"]:
                if sub["doc"] == doc_type:
                    name = doc["name"]
                    break

        file_size = head.tell()
        head.seek(0)
        response = HttpResponse(head, content_type="application/docx")
        response['Content-Disposition'] = (u"attachment; filename=%s%s.docx"% (filename, name)).encode("cp950", "replace")
        response['Content-Length'] = file_size
        return response


    def insert(self, request, **kwargs):
        """
        插入樣板。
        """
        self.is_authenticated(request)
        self.method_check(request, allowed=["put"])
        DATA = loads(request.body)

        try: node = Node.objects.get(id= kwargs["node_id"])
        except Node.DoesNotExist: raise ImmediateHttpResponse(HttpBadRequest(_("Invalid node id.")))

        templates = Template.objects.filter(id__in=DATA)
        checker = ObjectPermissionChecker(request.user)
        if checker.has_perm("create_node", node.case):
            for template in templates: template.pasteToNode(node)
            return self.create_response(request, [node.rTree()])
        else: raise ImmediateHttpResponse(HttpForbidden(_("Has not permission to create node.")))


    def dehydrate(self, bundle):
        if bundle.obj:
            list_url = reverse("api_dispatch_list", kwargs={"resource_name": "node", "api_name": "v1"})
            bundle.data["sub_node"] = ["%s%s/" % (list_url, sub.id) for sub in bundle.obj.child_nodes.all().order_by("priority", "create_time")]
            bundle.data["imgs_count"] = bundle.obj.node_photos.count()
            bundle.data["permissions"] = get_perms(bundle.request.user, bundle.obj.case)
            try:
                log = Log.objects.get(user=bundle.request.user, obj_id=bundle.obj.id, content_type=ContentType.objects.get(app_label="gallery", model="node"))
                if log.is_new == True:
                    bundle.data["is_new"] = True
                    bundle.data["log"] = log.id
                else:
                    bundle.data["is_new"] = False
                    bundle.data["log"] = log.id
            except:
                bundle.data["is_new"] = False

        return bundle


    def obj_create(self, bundle, **kwargs):
        """
        建立子節點。根節點（root node）會於父層物件連結（:class:`image_management.models.Case`）產生時一並建立。
        """
        request = bundle.request
        data = bundle.data
        checker = ObjectPermissionChecker(request.user)
        if data.has_key("parent_id"): parent_id = data["parent_id"]
        else: raise ImmediateHttpResponse(HttpBadRequest(_("Need parent_id in data.")))
        try: 
            parent = self._meta.queryset.get(id=parent_id)
            case = parent.case
        except Node.DoesNotExist: raise ImmediateHttpResponse(HttpBadRequest(_("Can't find match node.")))
        if checker.has_perm("create_node", parent.case):
            brother = self._meta.queryset.filter(parent=parent).order_by("-priority")

            if data.has_key("copy"):
                try: target = self._meta.queryset.get(id=data["copy"])
                except Node.DoesNotExist: raise ImmediateHttpResponse(HttpBadRequest(_("Can't find match node.")))
                children = [i.id for i in target.child_nodes.all().order_by("priority")]
                bundle.data["name"] = target.name
                bundle.data["copy"] = children

            if brother:
                setattr(bundle, "case", case)
                bundle = super(NodeResource, self).obj_create(bundle, request=request, parent=parent, creator=request.user, priority=brother[0].priority+NODE_PRIORITY_GAP)
            else:
                bundle = super(NodeResource, self).obj_create(bundle, request=request, parent=parent, creator=request.user)
            rcm_up = FRCMUserGroup.objects.filter(project=bundle.obj.case.parent)
            for relation in rcm_up:
                log = Log.objects.create(user=relation.user, obj_id=bundle.obj.id, content_type=ContentType.objects.get(app_label="gallery", model="node"))
                if log.user == bundle.request.user:
                    log.is_new = False
                    log.save()
            
            return bundle
        else: raise ImmediateHttpResponse(HttpForbidden(_("Has not permission to create node.")))


    def obj_update(self, bundle, **kwargs):
        """
        修改節點（:class:`image_management.models.Node`）。

        會檢查修改欄位，限制無法修改 case、檢查 priority, needed_count 及 images_count 的值，確保其為正整數。
        若有 parent_id 會將其轉為物件，並檢查：
            * :meth:`image_management.models.Node.isRoot` 檢查是否為根節點，無法移動根節點。
            * :meth:`image_management.models.Node.isSameCase` 檢查節點是否屬於同 Case，無法移動節點至不同 Case 的節點。
            * :meth:`image_management.models.Node.isChildOf` 檢查目標節點是否是自己的子節點，無法移動至自己的子節點。
        """
        try: bundle.obj = self.obj_get(bundle=bundle, **kwargs)
        except Node.DoesNotExist: raise ImmediateHttpResponse(HttpBadRequest(_("Can't find match data.")))

        request = bundle.request
        data = bundle.data
        checker = ObjectPermissionChecker(request.user)
        if checker.has_perm("update_node", bundle.obj.case):
            parent = False
            if data.has_key("case"): del data["case"]
            if data.has_key("parent_id"):
                try: parent = Node.objects.get(id=data["parent_id"])
                except Node.DoesNotExist: raise ImmediateHttpResponse(HttpBadRequest(_("Can't find match node.")))
                del data["parent_id"]
            if data.has_key("before_id"):
                try: before = Node.objects.get(id=data["before_id"])
                except Node.DoesNotExist: raise ImmediateHttpResponse(HttpBadRequest(_("Can't find match node.")))
                bundle.obj.moveToAfter(before)
                del data["before_id"]
            if data.has_key("after_id"):
                try: after = Node.objects.get(id=data["after_id"])
                except Node.DoesNotExist: raise ImmediateHttpResponse(HttpBadRequest(_("Can't find match node.")))
                bundle.obj.moveToBefore(after)
                del data["after_id"]
            for key in data:
                if key in ["priority", "needed_count", "images_count"]:
                    try: data[key] = abs(int(data[key]))
                    except: raise ImmediateHttpResponse(HttpForbidden(_("%s need to be a positive integer." % key)))

            bundle.obj._history_user = request.user
            super(NodeResource, self).obj_update(bundle, **kwargs)
            if parent:
                if bundle.obj.isRoot(): raise ImmediateHttpResponse(HttpBadRequest(_("Can't move root node.")))
                if not bundle.obj.isSameCase(bundle.obj): raise ImmediateHttpResponse(HttpBadRequest(_("Can't move node to different case.")))
                if parent.isChildOf(bundle.obj): raise ImmediateHttpResponse(HttpBadRequest(_("Can't move to self's child node.")))
                setattr(bundle.obj, "parent", parent)
                bundle.obj.save()
                bundle.obj.uPriorityRange()
                
            rcm_up = FRCMUserGroup.objects.filter(project=bundle.obj.case.parent)
            for relation in rcm_up:
                log, c = Log.objects.get_or_create(user=relation.user, obj_id=bundle.obj.id, content_type=ContentType.objects.get(app_label="gallery", model="node"))
                if relation.user == bundle.request.user:
                    log.is_new = False
                    log.save()
                else:
                    log.is_new = True
                    log.save()
            return bundle
        else: raise ImmediateHttpResponse(HttpForbidden(_("Has not permission to update node.")))

    def obj_delete(self, bundle, **kwargs):
        """
        刪除節點（:class:`image_management.models.Node`）。

        會檢查是否為根節點（無 parent），根節點無法被刪除。
        """
        try: bundle.obj = self.obj_get(bundle=bundle, **kwargs)
        except Node.DoesNotExist: raise ImmediateHttpResponse(HttpBadRequest(_("Can't find match data.")))

        request = bundle.request
        checker = ObjectPermissionChecker(request.user)
        if checker.has_perm("remove_node", bundle.obj.case):
            if bundle.obj.isRoot(): raise ImmediateHttpResponse(HttpBadRequest(_("Can't delete root node.")))
            bundle.obj._history_user = request.user
            return super(NodeResource, self).obj_delete(bundle, **kwargs)
        else: raise ImmediateHttpResponse(HttpForbidden(_("Has not permission to delete node.")))


    def improve_delete(self, request, **kwargs):
        """
        刪除缺失改善表資料夾。
        """
        self.is_authenticated(request)
        self.method_check(request, allowed=["delete"])

        try: improve_id = kwargs["improve_id"]
        except Node.DoesNotExist: raise ImmediateHttpResponse(HttpBadRequest(_("Need improve_id in url.")))

        try: inprove_node = Node.objects.get(note=improve_id, default=True, improve=True)
        except Node.DoesNotExist: return HttpResponse(dumps({"status": False}))

        checker = ObjectPermissionChecker(request.user)
        if checker.has_perm("remove_photo", photo):
            inprove_node.delete()
            return HttpResponse(dumps({"status": True}))
        else: raise ImmediateHttpResponse(HttpForbidden(_("Has not permission to delete.")))



class PhotoResource(ModelResource):
    node = fields.ForeignKey(NodeResource, "node")
    label = fields.ToManyField(LabelResource, "label")

    class Meta:
        authentication = MultiAuthentication(SessionAuthentication(), CustomApiKeyAuthentication(), IISIApiKeyAuthentication())
        authorization = Authorization()
        allowed_methods = ["get", "post", "put", "delete"]
        resource_name = "photo"
        # serializer = CustomSerializer()
        queryset = Photo.objects.all()
        excludes = ["photo", "sha_code"]
        ordering = ["id", "time", "create_time", "priority", "label"]
        filtering = {
            "id": ("exact"),
            "node": ALL_WITH_RELATIONS,
            "origin": ALL_WITH_RELATIONS,
            "time": ALL_WITH_RELATIONS,
            "is_public": ALL_WITH_RELATIONS,
        }
        always_return_data = True

    def dehydrate(self, bundle):
        bundle.data["node_name"] = bundle.obj.node.name
        bundle.data["tags"] = [tag.name for tag in bundle.obj.label.all()]
        bundle.data["thumb_url"] = "/gallery/api/v1/image/view/%s/?v=%s&size=medium" % (bundle.obj.id, bundle.obj.rDTVersion())
        bundle.data["sized_url"] = "/gallery/api/v1/image/view/%s/?v=%s&size=" % (bundle.obj.id, bundle.obj.rDTVersion())
        bundle.data["creator__name"] = bundle.obj.creator.last_name + bundle.obj.creator.first_name
        bundle.data["comment_count"] = bundle.obj.photo_comments.count()
        bundle.data["permissions"] = get_perms(bundle.request.user, bundle.obj.node.case) + get_perms(bundle.request.user, bundle.obj)

        try:
            log, c = Log.objects.get_or_create(user=bundle.request.user, content_type=ContentType.objects.get_for_model(Photo), obj_id=bundle.obj.id)
        except MultipleObjectsReturned:
            logs = Log.objects.filter(user=bundle.request.user, content_type=ContentType.objects.get_for_model(Photo), obj_id=bundle.obj.id).order_by("id")
            log = logs[0]
            for i in logs[1:]: i.delete()
        else:
            if bundle.obj.node.improve:
                label = bundle.obj.label.get()
                bundle.data["is_improve"] = label.name
            else:
                bundle.data["is_new"] = log.is_new
                bundle.data["is_improve"] = 0
            log.is_new = False
            log.save()

        return bundle
            

    def create_response(self, request, data, response_class=HttpResponse, **response_kwargs):
        """
        複寫原本的 create_response，讓自訂義資料可以依照 request 本身的字集處理。
        """
        desired_format = self.determine_format(request)
        serialized = self.serialize(request, data, desired_format)
        return response_class(content=serialized, content_type=build_content_type(desired_format), **response_kwargs)


    def build_filters(self, filters=None, ignore_bad_filters=False):
        """
        複寫原本的 filters，可以 node id 進行 filtering。
        """
        if filters is None: filters = {}
        orm_filters = super(PhotoResource, self).build_filters(filters)

        if "node" in filters: orm_filters["node"] = filters["node"]
        if "node_id" in filters: orm_filters["node"] = filters["node_id"]
        if "take_date" in filters:
            try: year, month, day = filters["take_date"].split("-")
            except: raise ImmediateHttpResponse(HttpForbidden(_("take_date value is incorrect, please set format %Y-%m-%d.")))

            if not month and not day:
                year = int(year)
                start = datetime.combine(datetime.strptime("%s-%s-%s" % (year, 1, 1), "%Y-%m-%d").date(), time.min)
                end = datetime.combine(datetime.strptime("%s-%s-%s" % (year, 12, monthrange(year, 12)[1]), "%Y-%m-%d").date(), time.max)
                orm_filters["time__range"] = (start, end)
            elif not day:
                year, month = int(year), int(month)
                start = datetime.combine(datetime.strptime("%s-%s-%s" % (year, month, 1), "%Y-%m-%d").date(), time.min)
                end = datetime.combine(datetime.strptime("%s-%s-%s" % (year, month, monthrange(year, month)[1]), "%Y-%m-%d").date(), time.max)
                orm_filters["time__range"] = (start, end)
            else:
                try: date = datetime.strptime(filters["take_date"], "%Y-%m-%d").date()
                except ValueError: raise ImmediateHttpResponse(HttpForbidden(_("take_date format is incorrect, please set format %Y-%m-%d.")))
                orm_filters["time__range"] = (datetime.combine(date, time.min), datetime.combine(date, time.max))
        if "upload_date" in filters:
            try: date = datetime.strptime(filters["upload_date"], "%Y-%m-%d").date()
            except ValueError: raise ImmediateHttpResponse(HttpForbidden(_("upload_date format is incorrect, please set format %Y-%m-%d.")))
            orm_filters["create_time__range"] = (datetime.combine(date, time.min), datetime.combine(date, time.max))
        return orm_filters


    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/upload/(?P<node_id>[0-9]+)%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view("upload"), name="api_upload"),
            url(r"^(?P<resource_name>%s)/upload_improve%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view("upload_improve"), name="api_upload_improve"),
            url(r"^(?P<resource_name>%s)/preview_docx%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view("preview_docx"), name="api_preview_docx"),
            url(r"^(?P<resource_name>%s)/image_docx%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view("image_docx"), name="api_image_docx"),
            url(r"^(?P<resource_name>%s)/(?P<case_id>[0-9]+)/public/list%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view("public_list"), name="api_public_list"),
        ]


    def obj_update(self, bundle, **kwargs):
        """
        修改相片（:class:`image_management.models.Photo`）。

        僅允許修改 node 及 note，若有 notd_id 會將其轉為 Node 物件。此處並無限制其修改 node 的範圍。
        """
        try: bundle.obj = self.obj_get(bundle=bundle, **kwargs)
        except Photo.DoesNotExist: raise ImmediateHttpResponse(HttpBadRequest(_("Can't find match data.")))

        request = bundle.request
        data = bundle.data
        checker = ObjectPermissionChecker(request.user)

        if checker.has_perm("update_photo", bundle.obj.node.case):
            if data.has_key("node_id"):
                try: node = Node.objects.get(id=data["node_id"])
                except Node.DoesNotExist: raise ImmediateHttpResponse(HttpBadRequest(_("Can't find match node.")))
                bundle.data["node"] = node
                if len(node.node_photos.all()) > 0:
                    bundle.data["priority"] = node.node_photos.order_by("-priority")[0].priority+NODE_PRIORITY_GAP
                else:
                    bundle.data["priority"] = NODE_PRIORITY_GAP
                del data["node_id"]
            if data.has_key("take_date"):
                try: date = datetime.strptime(data["take_date"], "%Y-%m-%d").date()
                except: ImmediateHttpResponse(HttpForbidden(_("The date format should be %Y-%m-%d.")))
                if bundle.obj.time: dtime = bundle.obj.time.time()
                else: dtime = time.min
                bundle.data["time"] = datetime.combine(date, dtime)
                del data["take_date"]
            if data.has_key("after_id"):
                try: after = Photo.objects.get(id=data["after_id"])
                except Photo.DoesNotExist: raise ImmediateHttpResponse(HttpBadRequest(_("Can't find match photo.")))
                bundle.obj.moveToBefore(after)
                del data["after_id"]
            if data.has_key("degree"):
                try: degree = int(data["degree"])
                except: raise ImmediateHttpResponse(HttpBadRequest(_("Rotation degree should be integer.")))
                bundle.obj.uRotation(degree)
                del data["degree"]

            if not data.has_key("label"):
                bundle.data["label"] = bundle.obj.label.all()

            return super(PhotoResource, self).obj_update(bundle, **kwargs)
        else: raise ImmediateHttpResponse(HttpForbidden(_("Has not permission to update node.")))


    def obj_delete(self, bundle, **kwargs):
        """
        刪除相片（:class:`image_management.models.Photo`）。
        """
        try: bundle.obj = self.obj_get(bundle=bundle, **kwargs)
        except Photo.DoesNotExist: raise ImmediateHttpResponse(HttpBadRequest(_("Can't find match data.")))

        request = bundle.request
        checker = ObjectPermissionChecker(request.user)
        if checker.has_perm("remove_photo", bundle.obj) or request.user.has_perm("gallery.remove_photo"):
            super(PhotoResource, self).obj_delete(bundle, **kwargs)
        else: raise ImmediateHttpResponse(HttpForbidden(_("Has not permission to delete photo.")))


    def upload(self, request, **kwargs):
        """
        接收上傳的照片。

        :param kwargs["node_id"]: 節點 ID
        :param request.FILES["file[]"]: 相片檔案
        """
        self.is_authenticated(request)
        self.method_check(request, allowed=["post"])

        if kwargs.has_key("node_id"): node_id = kwargs["node_id"]
        else: raise ImmediateHttpResponse(HttpBadRequest(_("Need node_id in url.")))

        if request.FILES.has_key("file"):
            files = request.FILES.getlist("file")
        else: raise ImmediateHttpResponse(HttpBadRequest(_("No file upload.")))

        try: node = Node.objects.get(id=node_id)
        except Node.DoesNotExist: raise ImmediateHttpResponse(HttpBadRequest(_("Can find match node.")))
        user = request.user
        checker = ObjectPermissionChecker(user)
        data = []

        if checker.has_perm("upload_photo", node.case):
            for photo in files:
                ext = photo.name.split('.')[-1].lower()
                if ext not in ['jpg', 'jpeg']: raise ImmediateHttpResponse(HttpBadRequest(_("File type not except, only allow jpg/jpeg files.")))

                new_photo = Photo(node=node, photo=photo, creator=request.user)
                if len(node.node_photos.all()) > 0:
                    new_photo.priority = node.node_photos.order_by("-priority")[0].priority+NODE_PRIORITY_GAP
                new_photo.save()

                assign_perm("remove_photo", request.user, new_photo)
                tags = [tag.name for tag in new_photo.label.all()]
                list_url = reverse("api_dispatch_list", kwargs={"resource_name": "photo", "api_name": "v1"})
                data.append({"__status__": True, "id": new_photo.id, "origin": new_photo.origin, "tags": tags, "is_new": True, "is_improve": 0,
                                "resource_uri": "%s%s/" % (list_url, new_photo.id),
                                "thumb_url": "/gallery/api/v1/image/view/%s/?v=%s&size=medium" % (new_photo.id, new_photo.rDTVersion()),
                                "sized_url": "/gallery/api/v1/image/view/%s/?v=%s&size=" % (new_photo.id, new_photo.rDTVersion()),
                                "creator__name": user.last_name + user.first_name,
                                "time": new_photo.time,
                                "permissions": get_perms(user, new_photo.node.case) + get_perms(user, new_photo)})
            return self.create_response(request, data)
        else: raise ImmediateHttpResponse(HttpForbidden(_("Has not permission to upload.")))


    def upload_improve(self, request, **kwargs):
        """
        接收缺失改善照片。

        :param request.POST["project_id"]: 工程 ID
        :param request.POST["supervise_date"]: 督導日期
        :param request.POST["improve_id"]: 改善表 ID
        :param request.POST["error_name"]: 缺失項目
                :param request.POST["sort_id"]: 改善前中號 {1: "改善前", 2: "改善中'", 3: "改善後"}
        :param request.FILES["file"]: 相片檔案
        """
        self.is_authenticated(request)
        self.method_check(request, allowed=["post"])

        data = request.POST

        if data.has_key("project_id"):
            try: case = Case.objects.get(parent__id=data["project_id"])
            except: raise ImmediateHttpResponse(HttpBadRequest(_("Can find match project or case not been create.")))
        else: raise ImmediateHttpResponse(HttpBadRequest(_("Need project_id in post data.")))

        if data.has_key("supervise_date"):
            supervise_name = u"%s 督導記錄" % data["supervise_date"].replace("-", "/")
            try: supervise_node = Node.objects.get(case=case, name=supervise_name, default=True, improve=True)
            except Node.DoesNotExist: 
                supervise_node = Node(case=case, name=supervise_name, default=True, improve=True)
                supervise_node.save()
        else: raise ImmediateHttpResponse(HttpBadRequest(_("Need supervise_date in post data.")))

        if data.has_key("improve_id"):
            improve_id = data["improve_id"]

            try: inprove_node = Node.objects.get(name=IMPROVE_SHEET_NAME, note=improve_id, default=True, improve=True)
            except Node.DoesNotExist:
                if data.has_key("error_name"): error_name = data["error_name"]
                else: raise ImmediateHttpResponse(HttpBadRequest(_("Need error_name in post data.")))

                try: defect_node = Node.objects.get(case=case, parent=supervise_node, name=error_name, default=True, improve=True)
                except Node.DoesNotExist:
                    defect_node = Node(case=case, parent=supervise_node, name=error_name, default=True, improve=True)
                    defect_node.save()

                inprove_node = Node(case=case, parent=defect_node, name=IMPROVE_SHEET_NAME, note=improve_id, default=True, improve=True)
                inprove_node.save()
        else: raise ImmediateHttpResponse(HttpBadRequest(_("Need improve_id in post data.")))

        if data.has_key("sort_id"):
            try: sort_id = int(data["sort_id"])
            except: raise ImmediateHttpResponse(HttpBadRequest(_("Parameter Type Error: sort_id need to be a integer.")))
            label = IMPROVE_TAG[sort_id]
        else: raise ImmediateHttpResponse(HttpBadRequest(_("Need sort_id in post data.")))

        if request.FILES.has_key("file"): files = request.FILES.getlist("file")
        else: raise ImmediateHttpResponse(HttpBadRequest(_("No file upload.")))
        
        photo = files[0]
        ext = photo.name.split('.')[-1].lower()
        if ext not in ['jpg', 'jpeg']: raise ImmediateHttpResponse(HttpBadRequest(_("File type not except, only allow jpg/jpeg files.")))

        user = request.user
        checker = ObjectPermissionChecker(user)

        if checker.has_perm("upload_photo", case):
            old_photos = label.label_photo.filter(node=inprove_node)
            for p in old_photos: p.delete()

            new_photo = Photo(node=inprove_node, photo=photo, creator=request.user)
            new_photo.save()
            new_photo.label.add(label)
            assign_perm("remove_photo", request.user, new_photo)
            return HttpResponse(dumps({"id": new_photo.id}))
        else: raise ImmediateHttpResponse(HttpForbidden(_("Has not permission to upload.")))


    def preview_docx(self, request, **kwargs):
        """
        產生含工程相片的 docx 檔案預覽。
        """
        data = request.GET

        if data.has_key("doc_type"): doc = data["doc_type"]
        else: raise ImmediateHttpResponse(HttpBadRequest(_("Need doc type in data.")))

        if data.has_key("photo_id"): photo_id = data["photo_id"].split(",")[:-1]
        else: raise ImmediateHttpResponse(HttpBadRequest(_("Need photo_id in data.")))
        
        try: photo_list = list(self._meta.queryset.filter(id__in=photo_id))
        except ValueError: raise ImmediateHttpResponse(HttpBadRequest(_("invalid photo id.")))

        photo_id = [int(i) for i in photo_id]
        photo_list.sort(key=lambda t: photo_id.index(t.pk))

        project_name = photo_list[0].node.case.parent.name
        try: contractor_name = photo_list[0].node.case.parent.frcmusergroup_set.filter(group__id=4).first().user.user_profile.unit.name or ""
        except: contractor_name = ""

        images = len(photo_list)

        if doc in ["examine", "construction_photo"]:
            page = (images/3) + (images%3 > 0)
            image_list = []
            for i in xrange(page): image_list.append(photo_list[i*3:((i+1)*3)])
        elif doc in ["maintain_6"]:
            page = (images/6) + (images%6 > 0)
            image_list = []
            for i in xrange(page):
                page_photo = photo_list[i*6:((i+1)*6)]
                page_pair = []
                for n in xrange(0, len(page_photo), 2):
                    p1 = page_photo[n]
                    p2 = False
                    if n+1 < len(page_photo): p2 = page_photo[n+1]
                    page_pair.append((p1, p2))
                image_list.append(page_pair)
        elif doc in ["maintain_9"]:
            page = (images/9) + (images%9 > 0)
            image_list = []
            for i in xrange(page):
                page_photo = photo_list[i*9:((i+1)*9)]
                page_pair = []
                for n in xrange(0, len(page_photo), 3):
                    p1 = page_photo[n]
                    p2, p3 = False, False
                    if n+1 < len(page_photo): p2 = page_photo[n+1]
                    if n+2 < len(page_photo): p3 = page_photo[n+2]
                    page_pair.append((p1, p2, p3))
                image_list.append(page_pair)
        elif doc in ["maintain_12"]:
            page = (images/12) + (images%12 > 0)
            image_list = []
            for i in xrange(page):
                page_photo = photo_list[i*12:((i+1)*12)]
                page_pair = []
                for n in xrange(0, len(page_photo), 3):
                    p1 = page_photo[n]
                    p2, p3 = False, False
                    if n+1 < len(page_photo): p2 = page_photo[n+1]
                    if n+2 < len(page_photo): p3 = page_photo[n+2]
                    page_pair.append((p1, p2, p3))
                image_list.append(page_pair)

        try: template = get_template(join("gallery", "%s_preview.html" % doc))
        except Template.DoesNotExist: raise ImmediateHttpResponse(HttpBadRequest(_("Wrong doc type.")))
        html = template.render(RequestContext(request, {"image_list": image_list, "project_name": project_name, "contractor_name": contractor_name, "doc": doc}))

        return self.create_response(request, {"html": html})


    def image_docx(self, request, **kwargs):
        """
        產生含工程相片的 docx 檔案。
        """
        data = request.POST
        if data.has_key("filename"): filename = request.POST["filename"]
        else: filename = False

        if data.has_key("doc_type"): doc_type = data["doc_type"]
        else: raise ImmediateHttpResponse(HttpBadRequest(_("Need doc type in data.")))

        if data.has_key("photo_id"): photo_id = request.POST.getlist("photo_id")
        else: raise ImmediateHttpResponse(HttpBadRequest(_("Need photo_id in data.")))

        try: image_list = list(self._meta.queryset.filter(id__in=photo_id))
        except ValueError: raise ImmediateHttpResponse(HttpBadRequest(_("invalid photo id.")))

        photo_id = [int(i) for i in photo_id]
        if not len(photo_id): raise ImmediateHttpResponse(HttpBadRequest(_("No image include.")))

        image_list.sort(key=lambda t: photo_id.index(t.pk))
        project_name = image_list[0].node.case.parent.name
        if not filename: filename = project_name


        if doc_type == "examine": head = make_examine_doc(image_list)
        elif doc_type == "construction_photo": head = make_construction_photo_doc(image_list)
        elif doc_type == "maintain_6": head = make_maintain_six_photo_doc(image_list)
        elif doc_type == "maintain_9": head = make_maintain_nine_photo_doc(image_list)
        elif doc_type == "maintain_12": head = make_maintain_twelve_photo_doc(image_list)
        else: raise ImmediateHttpResponse(HttpBadRequest(_("Wrong document type.")))

        for doc in PHOTODOC:
            if doc["doc"] == doc_type:
                name = doc["name"]
                break
            for sub in doc["sub"]:
                if sub["doc"] == doc_type:
                    name = doc["name"]
                    break


        file_size = head.tell()
        head.seek(0)
        response = HttpResponse(head, content_type="application/docx")
        response['Content-Disposition'] = (u"attachment; filename=%s%s.docx"% (filename, name)).encode("cp950", "replace")
        response['Content-Length'] = file_size
        return response


    def public_list(self, request, **kwargs):
        """
        讀取公開照片列表。
        """
        self.method_check(request, allowed=["get"])

        if kwargs.has_key("case_id"): case_id = kwargs["case_id"]
        else: raise ImmediateHttpResponse(HttpBadRequest(_("Need case_id in url.")))

        try: case = Case.objects.get(id=case_id)
        except Case.DoesNotExist: raise ImmediateHttpResponse(HttpBadRequest(_("Can't find match case.")))

        if not case.parent.is_public:
            raise ImmediateHttpResponse(HttpBadRequest(_("Project is not public.")))

        data = request.GET
        limit = data.get('limit', 25)
        offset = data.get('offset', 0)
        try:
            limit = int(limit)
        except:
            limit = 25

        try:
            offset = int(offset)
        except:
            offset = 0

        public_photos = self._meta.queryset.filter(node__case=case, is_public=True).order_by('time')
        total = public_photos.count()

        meta = {'limit': limit, 'offset': offset, 'total_count': total}
        objects = []

        for obj in public_photos[offset*limit:(offset+1)*limit]:
            objects.append({'url': '/gallery/api/v1/image/public/view/{id}/?v={version}'.format(id=obj.id, version=obj.rDTVersion())})

        return self.create_response(request, {'meta': meta, 'objects': objects})



class ImageResource(ModelResource):
    node = fields.ForeignKey(NodeResource, "node")

    class Meta:
        authentication = MultiAuthentication(SessionAuthentication(), CustomApiKeyAuthentication(), IISIApiKeyAuthentication())
        authorization = Authorization()
        allowed_methods = []
        resource_name = "image"
        always_return_data = True
        cache = PrivateCache()
        # serializer = CustomSerializer()
        queryset = Photo.objects.all()
        excludes = ["photo", "sha_code"]
        ordering = ["id"]
        filtering = {
            "id": ("exact"),
            "is_public": ALL_WITH_RELATIONS,
        }


    def dehydrate(self, bundle):
        bundle.data["node_name"] = bundle.obj.node.name
        bundle.data["tags"] = [tag.name for tag in bundle.obj.label.all()]
        bundle.data["thumb_url"] = "/gallery/api/v1/image/view/%s/?v=%s&size=medium" % (bundle.obj.id, bundle.obj.rDTVersion())
        bundle.data["sized_url"] = "/gallery/api/v1/image/view/%s/?v=%s&size=" % (bundle.obj.id, bundle.obj.rDTVersion())
        bundle.data["creator__name"] = bundle.obj.creator.last_name + bundle.obj.creator.first_name
        bundle.data["comment_count"] = bundle.obj.photo_comments.count()
        bundle.data["permissions"] = get_perms(bundle.request.user, bundle.obj.node.case) + get_perms(bundle.request.user, bundle.obj)

        try:
            log, c = Log.objects.get_or_create(user=bundle.request.user, content_type=ContentType.objects.get_for_model(Photo), obj_id=bundle.obj.id)
        except MultipleObjectsReturned:
            logs = Log.objects.filter(user=bundle.request.user, content_type=ContentType.objects.get_for_model(Photo), obj_id=bundle.obj.id).order_by("id")
            log = logs[0]
            for i in logs[1:]: i.delete()
        else:
            if bundle.obj.node.improve:
                label = bundle.obj.label.get()
                bundle.data["is_improve"] = label.name
            else:
                bundle.data["is_new"] = log.is_new
                bundle.data["is_improve"] = 0
            log.is_new = False
            log.save()
        return bundle
            

    def create_response(self, request, data, response_class=HttpResponse, **response_kwargs):
        """
        複寫原本的 create_response，讓自訂義資料可以依照 request 本身的字集處理。
        """
        desired_format = self.determine_format(request)
        serialized = self.serialize(request, data, desired_format)
        return response_class(content=serialized, content_type=build_content_type(desired_format), **response_kwargs)


    def build_filters(self, filters=None, ignore_bad_filters=False):
        """
        複寫原本的 filters，可以 node id 進行 filtering。
        """
        if filters is None: filters = {}
        orm_filters = super(PhotoResource, self).build_filters(filters)

        if "node" in filters: orm_filters["node"] = filters["node"]
        if "node_id" in filters: orm_filters["node"] = filters["node_id"]
        if "take_date" in filters:
            try: date = datetime.strptime(filters["take_date"], "%Y-%m-%d").date()
            except ValueError: raise ImmediateHttpResponse(HttpForbidden(_("take_date format is incorrect, please set format %Y-%m-%d.")))
            orm_filters["time__range"] = (datetime.combine(date, time.min), datetime.combine(date, time.max))
        if "upload_date" in filters:
            try: date = datetime.strptime(filters["upload_date"], "%Y-%m-%d").date()
            except ValueError: raise ImmediateHttpResponse(HttpForbidden(_("upload_date format is incorrect, please set format %Y-%m-%d.")))
            orm_filters["create_time__range"] = (datetime.combine(date, time.min), datetime.combine(date, time.max))
        return orm_filters


    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/view/(?P<photo_id>[0-9]+)%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view("view"), name="api_view"),
            url(r"^(?P<resource_name>%s)/public/view/(?P<photo_id>[0-9]+)%s$" % (self._meta.resource_name, trailing_slash()), self.wrap_view("public_view"), name="api_public_view"),
        ]


    def view(self, request, **kwargs):
        """
        讀取相片。若透過 GET 給予 width 及 height，則會回傳指定尺寸之縮圖，若無則回傳原始檔案。

        :param kwargs["photo_id"]: 相片 ID
        :param request.GET["size"]: 縮圖尺寸名稱
        """
        self.is_authenticated(request)
        self.method_check(request, allowed=["get"])

        if kwargs.has_key("photo_id"): photo_id = kwargs["photo_id"]
        else: raise ImmediateHttpResponse(HttpBadRequest(_("Need photo_id in url.")))

        try: photo = self._meta.queryset.get(id=photo_id)
        except Photo.DoesNotExist: raise ImmediateHttpResponse(HttpBadRequest(_("Can't find match photo.")))

        size = False
        if request.GET.has_key("size"):
            try: size = Size.objects.get(name=request.GET["size"])
            except Size.DoesNotExist: raise ImmediateHttpResponse(HttpBadRequest(_("Can't find match size.")))
        
        checker = ObjectPermissionChecker(request.user)

        if checker.has_perm("view_case", photo.node.case) or request.user.has_perm("gallery.view_case"):
            if size: photo = photo.rThumbnail(size=size)
            if IMAGE_RESPONSE == "default":
                file = open(photo.rPath(), "rb")
                raw = file.read()
                file.close()
                response = HttpResponse(raw, content_type="image/jpg")
            elif IMAGE_RESPONSE == "X-Sendfile":
                response = HttpResponse()
                response["X-Sendfile"] = photo.rPath()
                response["Content-Type"] = ""
                # del response["content-type"]
            return response
        else: raise ImmediateHttpResponse(HttpForbidden(_("Has not permission to view.")))


    def public_view(self, request, **kwargs):
        """
        讀取相片共公開瀏覽，需檢查 is_public。若透過 GET 給予 width 及 height，則會回傳指定尺寸之縮圖，若無則回傳原始檔案。

        :param kwargs["photo_id"]: 相片 ID
        :param request.GET["size"]: 縮圖尺寸名稱
        """
        self.method_check(request, allowed=["get"])

        if kwargs.has_key("photo_id"): photo_id = kwargs["photo_id"]
        else: raise ImmediateHttpResponse(HttpBadRequest(_("Need photo_id in url.")))

        try: photo = self._meta.queryset.get(id=photo_id)
        except Photo.DoesNotExist: raise ImmediateHttpResponse(HttpBadRequest(_("Can't find match photo.")))

        if not photo.node.case.parent:
            raise ImmediateHttpResponse(HttpBadRequest(_("Project is not public.")))

        if not photo.is_public:
            raise ImmediateHttpResponse(HttpBadRequest(_("Photo is not public.")))

        size = False
        if request.GET.has_key("size"):
            try: size = Size.objects.get(name=request.GET["size"])
            except Size.DoesNotExist: raise ImmediateHttpResponse(HttpBadRequest(_("Can't find match size.")))
        
        if size: photo = photo.rThumbnail(size=size)
        if IMAGE_RESPONSE == "default":
            file = open(photo.rPath(), "rb")
            raw = file.read()
            file.close()
            response = HttpResponse(raw, content_type="image/jpg")
        elif IMAGE_RESPONSE == "X-Sendfile":
            response = HttpResponse()
            response["X-Sendfile"] = photo.rPath()
            response["Content-Type"] = ""
            # del response["content-type"]
        return response



class SizeResource(ModelResource):

    class Meta:
        authentication = MultiAuthentication(SessionAuthentication(), CustomApiKeyAuthentication(), IISIApiKeyAuthentication())
        authorization = Authorization()
        allowed_methods = ["get", "post", "put", "delete"]
        always_return_data = True
        resource_name = "size"
        # serializer = CustomSerializer()
        queryset = Size.objects.all()
        filtering = {
            "id": ("exact"),
            "name": ("exact"),
            "width": ("exact"),
            "height": ("exact"),
        }


    def create_response(self, request, data, response_class=HttpResponse, **response_kwargs):
        """
        複寫原本的 create_response，讓自訂義資料可以依照 request 本身的字集處理。
        """
        desired_format = self.determine_format(request)
        serialized = self.serialize(request, data, desired_format)
        return response_class(content=serialized, content_type=build_content_type(desired_format), **response_kwargs)


    def obj_create(self, bundle, **kwargs):
        """
        建立縮圖尺寸（:class:`image_management.models.Size`）。

        會檢查 name 是否重複、width 及 height 是否有相同者。
        """
        request = bundle.request
        data = bundle.data
        
        if request.user.is_superuser or request.user.is_staff:
            try: name = data["name"]
            except KeyError: raise ImmediateHttpResponse(HttpBadRequest(_("Need name in data.")))

            try: width = data["width"]
            except KeyError: raise ImmediateHttpResponse(HttpBadRequest(_("Need width in data.")))

            try: height = data["height"]
            except KeyError: raise ImmediateHttpResponse(HttpBadRequest(_("Need height in data.")))

            # check = self._meta.queryset.filter(Q(Q(name=name)|Q(width=width, height=height)))
            if self._meta.queryset.filter(name=name): raise ImmediateHttpResponse(HttpBadRequest(_("Duplicate name.")))
            if self._meta.queryset.filter(width=width, height=height): raise ImmediateHttpResponse(HttpBadRequest(_("Duplicate width and height.")))
            return super(SizeResource, self).obj_create(bundle, request=request, creator=request.user)
        else: raise ImmediateHttpResponse(HttpForbidden(_("Has not permission to create size.")))


    def obj_update(self, bundle, **kwargs):
        """
        修改縮圖尺寸（:class:`image_management.models.Size`）。

        僅允許修改尺寸名稱，不允許修改其寬高，以避免製成的縮圖成果不一。
        """
        try: bundle.obj = self.obj_get(bundle=bundle, **kwargs)
        except Size.DoesNotExist: raise ImmediateHttpResponse(HttpBadRequest(_("Can't find match data.")))

        request = bundle.request
        data = bundle.data
        if request.user.is_superuser or request.user.is_staff:
            if data.has_key("width"): del data["width"]
            if data.has_key("height"): del data["height"]
            return super(SizeResource, self).obj_update(bundle, **kwargs)
        else: raise ImmediateHttpResponse(HttpForbidden(_("Has not permission to update size.")))


    def obj_delete(self, bundle, **kwargs):
        """
        刪除縮圖尺寸（:class:`image_management.models.Size`）。
        """
        try: bundle.obj = self.obj_get(bundle=bundle, **kwargs)
        except Node.DoesNotExist: raise ImmediateHttpResponse(HttpBadRequest(_("Can't find match data.")))

        request = bundle.request
        if request.user.is_superuser or request.user.is_staff:
            super(SizeResource, self).obj_delete(bundle, **kwargs)
        else: raise ImmediateHttpResponse(HttpForbidden(_("Has not permission to delete size.")))



class CommentResource(ModelResource):
    photo = fields.ForeignKey(PhotoResource, "photo")
    
    class Meta:
        authentication = MultiAuthentication(SessionAuthentication(), CustomApiKeyAuthentication(), IISIApiKeyAuthentication())
        authorization = Authorization()
        allowed_methods = ["get", "post", "delete"]
        always_return_data = True
        resource_name = "comment"
        # serializer = CustomSerializer()
        queryset = Comment.objects.all()
        excludes = []
        ordering = ["create_time"]
        filtering = {
            "id": ("exact"),
            "photo": ("exact", ),
        }


    def create_response(self, request, data, response_class=HttpResponse, **response_kwargs):
        """
        複寫原本的 create_response，讓自訂義資料可以依照 request 本身的字集處理。
        """
        desired_format = self.determine_format(request)
        serialized = self.serialize(request, data, desired_format)
        return response_class(content=serialized, content_type=build_content_type(desired_format), **response_kwargs)


    def dehydrate(self, bundle):
        if bundle.obj: bundle.data["creator__name"] = bundle.obj.creator.last_name + bundle.obj.creator.first_name
        return bundle


    def obj_create(self, bundle, **kwargs):
        """
        建立評論（:class:`gallery.models.Comment`）。
        """
        request = bundle.request
        data = bundle.data
        checker = ObjectPermissionChecker(request.user)

        if data.has_key("photo_id"): photo_id = data["photo_id"]
        else: raise ImmediateHttpResponse(HttpBadRequest(_("Need photo_id in data.")))

        try: photo = Photo.objects.get(id=photo_id)
        except Photo.DoesNotExist: raise ImmediateHttpResponse(HttpBadRequest(_("Can't find match photo.")))

        if checker.has_perm("update_photo", photo.node.case):
            bundle = super(CommentResource, self).obj_create(bundle, request=request, photo=photo, creator=request.user)
            rcm_up = FRCMUserGroup.objects.filter(project=bundle.obj.photo.node.case.parent)
            for relation in rcm_up:
                log, c = Log.objects.get_or_create(user=relation.user, obj_id=bundle.obj.photo.id, content_type=ContentType.objects.get(app_label="gallery", model="photo"))
                if c == False:
                    log.is_new = True
                    log.save()
                if log.user == bundle.request.user:
                    log.is_new = False
                    log.save()

            return bundle
        else: raise ImmediateHttpResponse(HttpForbidden(_("Has not permission to create node.")))


    def obj_delete(self, bundle, **kwargs):
        """
        刪除評論（:class:`gallery.models.Comment`）。
        """
        try: bundle.obj = self.obj_get(bundle=bundle, **kwargs)
        except Comment.DoesNotExist: raise ImmediateHttpResponse(HttpBadRequest(_("Can't find match data.")))

        request = bundle.request
        checker = ObjectPermissionChecker(request.user)
        try: comment = bundle.obj
        except Comment.DoesNotExist: raise ImmediateHttpResponse(HttpBadRequest(_("Can't find match comment.")))

        if checker.has_perm("remove_comment", comment) or request.user.has_perm("gallery.remove_comment"):
            bundle.obj._history_user = request.user
            return super(CommentResource, self).obj_delete(bundle, **kwargs)
        else: raise ImmediateHttpResponse(HttpForbidden(_("Has not permission to delete comment.")))