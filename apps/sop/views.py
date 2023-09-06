# -*- coding: utf-8 -*-
import os, random, json, re, datetime, decimal, calendar, shutil, zipfile
from copy import copy
from django.template.loader import get_template
from django.template import Context, RequestContext
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.contrib import auth
from django.contrib.auth.models import User, Group, Permission
from django.contrib.sessions.models import Session
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.conf import settings
from sop.models import Sop, Item, File

from guardian.shortcuts import assign
from guardian.shortcuts import remove_perm
from guardian.shortcuts import get_perms

INTERNAL_IPS = settings.INTERNAL_IPS
MEDIA_ROOT = settings.MEDIA_ROOT
ROOT = settings.ROOT

def index(R):
    sops = Sop.objects.filter(is_use=True).order_by("priority", "id")
    res = []
    for i in sops:
        sop_info ={}
        sop_info['sop']=i
        forms = []
        sop_info['vsd_file'] = 0
        sop_info['stb_file'] = 0
        for j in i.item_sop.all():
            if j.type == 0:
                sop_info['png_file'] = j.file_item.get(is_use=True)
            elif j.type == 1:
                sop_info['stb_file'] = j.file_item.get(is_use=True)
            else:
                forms.append(str(j.id))
        sop_info['forms'] = ",".join(forms)
        res.append(sop_info)
    t = get_template(os.path.join('sop', 'zh-tw', 'web', 'index.html'))
    html = t.render(RequestContext(R,{
        'res':res,
        'res_count':len(res),
        }))
    # content = makeFileByWordExcel(template_name=template_name, result=result)
    # response = HttpResponse(content_type='application/xls')
    # response['Content-Type'] = ('application/xls')
    # response['Content-Disposition'] = ('attachment; filename=%s.xls' % (str(this_countychasetime.chase_date) + '-縣市進度追蹤表')).encode('cp950', 'replace')
    # response.write(content)
    # return respons
    return HttpResponse(html)


@login_required
def admin_index(R):
    if not R.user.has_perm('sop.edit_sop'):
        return HttpResponseRedirect('/')

    sops = Sop.objects.all().order_by("priority", "id")
    # .order_by("id")
    res = []
    for i in sops:
        sop_info ={}
        sop_info['sop']=i
        forms = []
        sop_info['vsd'] = 0
        sop_info['stb'] = 0
        for j in i.item_sop.all():
            if j.type == 0:
                sop_info['png']=j.id
            elif j.type == 1:
                sop_info['stb']=j.id
            elif j.type == 3:
                sop_info['vsd']=j.id
            else:
                forms.append(str(j.id))
        sop_info['forms'] = ",".join(forms)
        res.append(sop_info)

    t = get_template(os.path.join('sop', 'zh-tw', 'admin', 'index.html'))
    html = t.render(RequestContext(R,{
        'res':res
        }))
    return HttpResponse(html)


@login_required
def create(R):
    if not R.user.has_perm('sop.edit_sop'):
        return HttpResponseRedirect('/')

    t = get_template(os.path.join('sop', 'zh-tw', 'admin', 'new.html'))
    sops = Sop.objects.all()
    html = t.render(RequestContext(R,{
        'sops':sops
        }))
    return HttpResponse(html)


@login_required
def createSop(R):
    if not R.user.has_perm('sop.edit_sop'):
        return HttpResponseRedirect('/')

    data = R.POST
    sop = Sop.objects.create(title=data['title'], priority=max([i.priority for i in Sop.objects.all()] + [0]) + 1)
    res = {'id':sop.id,'title':sop.title}
    return HttpResponse(json.dumps(res))


@login_required
def createItem(R):
    if not R.user.has_perm('sop.edit_sop'):
        return HttpResponseRedirect('/')

    data = R.POST
    sop = Sop.objects.get(id=data['sop_id'])
    file_type = int(data["file_type"]);
    if file_type == 0:
        item_name = "作業流程圖"
    elif  file_type == 1:
        item_name = "標準作業書"
    elif file_type == 3:
        item_name = "作業流程圖-vsd"
    else:
        item_name = data["item_name"]
    item = Item(
        name= item_name,
        type = file_type,
        sop = sop,
        )
    item.save()
    f = R.FILES.get('file', None)
    full_name = f.name.split(".")
    ext = full_name[-1]
    full_name.remove(full_name[-1])
    name = "".join(full_name)
    item_file = File(
        name= name,
        ext = ext,
        item= item,
        upload_time=datetime.datetime.now(),
        )
    item_file.save()
    getattr(item_file, 'file').save('%s.%s'%(item_file.version, item_file.ext), f)
    item_file.save()

    return HttpResponse('OK')


@login_required
def loadSelectForm(R):
    if not R.user.has_perm('sop.edit_sop'):
        return HttpResponseRedirect('/')

    data =R.POST
    sop = Sop.objects.get(id=data['id'])
    d = []
    for i in sop.item_sop.filter(type=2):
        temp = [i.id,i.name]
        d.append(temp)
    return HttpResponse(json.dumps(d))


@login_required
def updateUpload(R):
    if not R.user.has_perm('sop.edit_sop'):
        return HttpResponseRedirect('/')

    data = R.POST
    sop = Sop.objects.get(id=data['sop_id'])
    try:
        item = sop.item_sop.get(id= int(data['item_id']))
        status = 'update'
        try:
            old_file = item.file_item.get(is_use=True)
            old_file.is_use = False
            old_file.save()
        except:
            pass
    except:
        if int(data['file_type']) == 0:
            item_name = "作業流程圖"
        elif int(data['file_type'])== 1:
            item_name = "標準作業書"
        else:
            item_name = data["name"]
        item = Item(
            name= item_name,
            type = int(data['file_type']),
            sop = sop,
            )
        item.save()
        status = 'new'
    f = R.FILES['file']
    full_name = f.name.split(".")
    ext = full_name[-1]
    full_name.remove(full_name[-1])
    name = "".join(full_name)
    item_file = File(
        name= name,
        ext = ext,
        item= item,
        upload_time=datetime.datetime.now(),
        )
    item_file.save()
    item_file.file = f
    item_file.save()

    res = {'status':status,'item_name':item.name,'file_count':len(item.file_item.all()),'item_id':item.id}
    return HttpResponse(json.dumps(res))


@login_required
def changeItemName(R):
    if not R.user.has_perm('sop.edit_sop'):
        return HttpResponseRedirect('/')

    data = R.POST
    item = Item.objects.get(id=int(data['item_id']))
    item.name = data['name']
    item.save()
    res ={}
    return HttpResponse(json.dumps(res))





def view_file(R, file_id):
    row_obj = File.objects.get(id=file_id)
    path = row_obj.get_actual_path()
    if not path: return HttpResponseNotFound()

    row_file = open(path, 'rb')
    raw = row_file.read()
    row_file.close()

    response = HttpResponse(raw, content_type="image/%s" % row_obj.ext)
    response['Cache-Control'] = 'private, max-age=31556926'
    return response


def download_file(R, **kw):
    row = File.objects.get(id=kw["file_id"])
    path = row.get_actual_path()
    if not path: return HttpResponseNotFound()

    f = open(path, 'rb')
    content = f.read()
    response = HttpResponse(content_type='application/' + row.ext)
    response['Content-Type'] = ('application/' + row.ext)
    file_name = row.item.name.replace(" ", "") + '.' + row.ext
    response['Content-Disposition'] = ('attachment; filename='+ file_name).encode('cp950', 'replace')
    response.write(content)
    return response


def download_zip_file(R, **kw):
    sop = Sop.objects.get(id=kw["sop_id"])
    # TYPE_CHOICE = (
    #     (0, '標準流程圖'),
    #     (1, '標準作業書'),
    #     (2, '表單'),
    # )

    #清空整理資料夾
    try:
        shutil.rmtree(os.path.join(ROOT, 'apps', 'sop', 'media', 'sop', 'file', str(sop.id), 'tempZipFile'))
    except: pass

    #嘗試做出整理資料夾
    try: os.makedirs(os.path.join(ROOT, 'apps', 'sop', 'media', 'sop', 'file', str(sop.id), 'tempZipFile'))
    except: pass
    #嘗試做出整理資料夾
    try: os.makedirs(os.path.join(ROOT, 'apps', 'sop', 'media', 'sop', 'file', str(sop.id), 'tempZipFile', 'files'))
    except: pass

    #整理檔案
    rows = File.objects.filter(item__sop=sop, is_use=True)
    for f in rows:
        source = f.get_actual_path()
        if source:
            out = os.path.join(ROOT, 'apps', 'sop', 'media', 'sop', 'file', str(sop.id), 'tempZipFile', 'files', f.item.name + '.' + f.ext)
            my_copy = shutil.copyfile(source, out)

    zip = zipfile.ZipFile(os.path.join(ROOT, 'apps', 'sop', 'media', 'sop', 'file', str(sop.id), 'tempZipFile', str(sop.id) + '.zip'), 'w', zipfile.ZIP_DEFLATED)
    startdir = os.path.join(ROOT, 'apps', 'sop', 'media', 'sop', 'file', str(sop.id), 'tempZipFile', 'files')
    startdir_walk = os.walk(startdir)
    for dirpath, dirnames, filenames in startdir_walk:
        for filename in filenames:
            path = os.path.join(dirpath, filename)
            zip.write(path, os.path.basename(path))
    zip.close()

    f = open(os.path.join(ROOT, 'apps', 'sop', 'media', 'sop', 'file', str(sop.id), 'tempZipFile', str(sop.id) + '.zip'), 'rb')
    content = f.read()
    response = HttpResponse(content_type='application/zip')
    response['Content-Type'] = ('application/zip')
    file_name = sop.title + '.zip'
    response['Content-Disposition'] = ('attachment; filename='+ file_name).encode('cp950', 'replace')
    response.write(content)

    return response