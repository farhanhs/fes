#-*- coding: utf8 -*-
from os.path import join
from datetime import datetime, time
from django.conf import settings
from django.utils.translation import ugettext as _
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.template.loader import get_template
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from guardian.core import ObjectPermissionChecker
from guardian.shortcuts import get_perms
from tastypie.http import HttpBadRequest
from fishuser.models import Project
from gallery.models import DEFAULT_NODE, Case, Photo

try: from settings import COMPRESS
except ImportError: COMPRESS = False

try: from settings import PHOTODOC
except ImportError: PHOTODOC = []

try: from settings import NODETEMPLATE
except ImportError: NODETEMPLATE = False

try: from settings import DEFECT
except ImportError: DEFECT = False

try: from settings import COPYNODE
except ImportError: COPYNODE = False


@login_required
def from_rcm(R, project_id):
    """
    轉換路徑並檢查相片系統資料是否建立。
    """
    try: project = Project.objects.get(id=project_id)
    except Project.DoesNotExist: return HttpBadRequest(_("No Match Project."))

    try: case = project.photo_case
    except Case.DoesNotExist:
        project.save()
        case = project.photo_case

    url = reverse("gallery.views.index", kwargs={"project_id": project.id})
    return HttpResponseRedirect(url)


@login_required
def index(R, project_id):
    """
    執行相片系統頁面。
    會檢查是否有自定查驗點，否則顯示提示。
    會檢查是否有缺失改善相片資料，有則顯示改善照片分頁。
    """
    try: project = Project.objects.get(id=project_id)
    except Project.DoesNotExist: return HttpBadRequest(_("No Match Project."))

    try: case = project.photo_case
    except Case.DoesNotExist:
        project.save()
        case = project.photo_case

    if not R.user.has_perm('fishuser.view_all_project_in_remote_control_system'):
        # 若無 "在(遠端工程系統)中_觀看_所有_工程案資訊" 權限
        if u'view_case' not in get_perms(R.user, case):
            # 若無 "觀看相片系統" 權限
            return HttpResponseRedirect('/')
        else:
            if not R.user.frcmusergroup_set.get(project=project).is_active:
                # 被關閉權限的
                return HttpResponseRedirect('/')
    else:
        # 有 "在(遠端工程系統)中_觀看_所有_工程案資訊" 權限
        if not R.user.has_perm('fishuser.view_all_project_in_management_system'):
            # 無法觀看管考、縣市政府人員
            new_units = []
            u_name = R.user.user_profile.unit.name[:3]
            for u in units:
                if u_name in u.name:
                    new_units.append(u)
            if project.unit not in new_units and not R.user.is_staff and not 'view_case' in get_perms(R.user, project):
                #不是自己單位的工程
                return HttpResponseRedirect('/')


    # 檢查是否有設定查驗點，否則顯示提示。
    insert, show_guide  = "", 0
    checker = ObjectPermissionChecker(R.user)
    if checker.has_perm("create_node", case) and len(case.nodes.all()) <= (len(DEFAULT_NODE)+1):
        if not len(case.nodes.all()):
            case.cRootNode()
        
        if DEFAULT_NODE:
            try: show_guide = case.nodes.get(name=DEFAULT_NODE[0]["name"]).id
            except: show_guide = case.nodes.get(parent=None).id
        else:
            show_guide = case.nodes.get(parent=None).id


    # 檢查是否有缺失改善相片資料，有則顯示改善照片分頁。
    improve = case.nodes.filter(improve=True)


    permissions = get_perms(R.user, case)
    if R.user.has_perm("gallery.remove_comment"): permissions.append("remove_comment")

    template = get_template(join("gallery", "index.html"))
    html = template.render(RequestContext(R, {"project": project, "case": case, "permissions": permissions, "insert": insert, "GUIDE": int(show_guide), "COMPRESS": int(COMPRESS), "COPYNODE": int(COPYNODE), "PHOTODOC": PHOTODOC, "NODETEMPLATE": int(NODETEMPLATE), "IMPROVE": len(improve), "DEFECT": DEFECT}))
    return HttpResponse(html)


def examine(R):
    """
    輸出相片文件時的預覽頁面，會根據產生文件的參數模擬文件格式。
    """
    data = R.GET
    if data.has_key("project_id"): project_id = data["project_id"]
    else: return HttpBadRequest(_("Need a project id"))

    if data.has_key("date"):
        try: date = datetime.strptime(data["date"], "%Y-%m-%d").date()
        except ValueError: return HttpBadRequest(_("take_date format is incorrect, please set format %Y-%m-%d."))
    else: return HttpBadRequest(_("Need a date"))

    try: case = Case.objects.get(parent__id=project_id)
    except Case.DoesNotExist: return HttpResponse(_("No match case"))

    photos = Photo.objects.filter(node__case=case, time__range=(datetime.combine(date, time.min), datetime.combine(date, time.max))).order_by("node__priority", "priority")
    # 強制排序
    # nodes = [photo.node for photo in photos]
    # nodes = sorted(set(nodes), key=nodes.index)
    # order_photos = []
    # for node in nodes:
    #     order_photos += photos.filter(node=node).order_by("priority")

    template = get_template(join("gallery", "examine.html"))
    html = template.render(RequestContext(R, {"date": date, "photos": photos}))
    return HttpResponse(html)


def support(R):
    """
    檢查使用者瀏覽器是否支援 html5 功能，若否則顯示提示使用者升級瀏覽器。
    """
    template = get_template(join("gallery", "support.html"))
    html = template.render(RequestContext(R,{"display_name": settings.SYS_HOST_NAME}))
    return HttpResponse(html)