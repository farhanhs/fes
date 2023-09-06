# -*- coding: utf8 -*-
import os, re, json, math, settings

from datetime import datetime
from hashlib import md5
from time import sleep
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import Context, RequestContext
from django.template.loader import get_template
from django.views.decorators.csrf import csrf_exempt
from common.lib import nocache_response, readDATA, makeFileByWordExcel
from common.templatetags.utiltags import thumb
from fishuser.models import Project, FRCMUserGroup
from fishuser.models import _ca
from engphoto.models import NORMALPHOTOTYPE, DEFECTPHOTOTYPE, TRASHPHOTOTYPE, AUTODUPLICATETYPE, NONDUPLICATETYPE, LESSTHANPHOTOSIZELIMITTYPE, NONLESSTHANPHOTOSIZELIMITTYPE
from engphoto.models import Template, CheckPoint, Verify, Photo


TODAY = datetime.today()
NOW = datetime.now()


if not hasattr(json, 'write'):
    #for python2.6
    json.write = json.dumps
    json.read = json.loads


def denyFunction(*args, **kw):
    """ 拒絕使用者使用的函式
    """
    return HttpResponseRedirect('/u/vp/')


def authority_check(myfunc):
    def inner_func(*args, **kw):
        R = args[0]
        func_name = myfunc.__name__
        if func_name == 'getPic':
            if not R.user.is_authenticated() and R.GET.has_key('c') and R.GET['c']:
                project_id = re.sub('([^/]+/)+([0-9]+)_[0-9]+[\._][^/]+', r'\2', kw['filename'])
                if R.GET['c'].lower() != _duplicate_md5string(settings.DUPLICATE_PASSWD, kw['filename'], project_id):
                    return HttpResponseRedirect('/u/vp/')

            return myfunc(*args, **kw)

        if kw.has_key('photo_id') and kw['photo_id']:
            try: photo = Photo.objects.get(id=kw['photo_id'])
            except Photo.DoesNotExist: return HttpResponseRedirect('/u/vp/')
            project = photo.project
            del kw['photo_id']
            kw['photo'] = photo
        elif kw.has_key('checkpoint_id') and kw['checkpoint_id']:
            try: checkpoint = CheckPoint.objects.get(id=kw['checkpoint_id'])
            except CheckPoint.DoesNotExist: return HttpResponseRedirect('/u/vp/')
            project = checkpoint.project
            del kw['checkpoint_id']
            kw['checkpoint'] = checkpoint
        elif kw.has_key('checkpoint_ct_id') and kw['checkpoint_ct_id']:
            row_id = int(kw['checkpoint_ct_id'].split('_')[-1].replace('r', ''))
            checkpoint = CheckPoint.objects.get(id=row_id)
            project = checkpoint.project
            del kw['checkpoint_ct_id']
            kw['checkpoint'] = checkpoint
        elif kw.has_key('project_id') and kw['project_id']:
            try: project = Project.objects.get(id=kw['project_id'])
            except Project.DoesNotExist: return HttpResponseRedirect('/u/vp/')
            del kw['project_id']
        elif R.session.get('project_id', False):
            try: project = Project.objects.get(id=R.session['project_id'])
            except Project.DoesNotExist: return HttpResponseRedirect('/u/vp/')

        right_type_value = kw.get('right_type_value', '')
        kw['project'] = project
        if R.user.user_profile.group.name == '上層管理者' or R.user.user_profile.group.name == '管考填寫員' or R.user.user_profile.group.name == '署內主辦工程師' or R.user.is_staff:
            pass
        else:
            try:
                FRCMUserGroup.objects.get(user=R.user, project=project)
            except:
                return HttpResponseRedirect('/u/')
        if _ca(user=R.user, project=project,
            right_type_value=right_type_value) or R.user.is_staff:
            return nocache_response(myfunc(*args, **kw))
        else:
            return denyFunction(*args, **kw)

    if myfunc.__name__ == 'getPic':
        return inner_func
    else:
        return login_required(inner_func)


@authority_check
def getOwnProject(R, project, **kw):
    try:
        projects = []
        for p in FRCMUserGroup.objects.filter(user=R.user).exclude(project__id=project.id).order_by('-id'):
            projects.append({'id': p.project.id, 'bid_no': p.project.bid_no, 'name': p.project.name})
        return HttpResponse(json.write({'status': True, 'nowproject':
        {'id': project.id, 'bid_no': project.bid_no, 'name': project.name}, 'projects': projects}))
    except Project.DoesNotExist:
        return HttpResponse(json.write({'status': False, 'message': 'Project.DoesNotExist'}))

    return HttpResponse(json.write({'status': False, 'message': 'unknown problem'}))


@authority_check
def bigPicture(R, project, photo, type, **kw):
    timeList = [str(p.id) for p in project.photo_set.filter(
    phototype=NORMALPHOTOTYPE, verify__isnull=False).order_by('-uploadtime')]

    defectList = [str(p.id) for p in project.photo_set.filter(
    phototype=DEFECTPHOTOTYPE, verify__isnull=False).order_by('-uploadtime')]

    trashList = [str(p.id) for p in project.photo_set.filter(
    phototype=TRASHPHOTOTYPE, verify__isnull=False).order_by('-uploadtime')]

    Dir = CheckPoint.objects.get(project=project, template__isnull=True,
    name='目錄', uplevel__isnull=True)
    checkpointList = []

    orderList = {}
    checkpoints = []
    for subCP in Dir.sublevel.all().order_by('priority', 'id'):
        for checkpoint in subCP.sublevel.all().order_by('priority', 'id'):
            for i, p in enumerate(checkpoint.photo_set.filter(phototype=NORMALPHOTOTYPE,
            verify__isnull=False).order_by('priority', 'id')):
                checkpointList.append(str(p.id))
                if i == 0:
                    checkpoint.first = p.id
                    if checkpoint == photo.checkpoint: checkpoint.isselected = 'selected'
                    checkpoints.append(checkpoint)

            for i, p in enumerate(checkpoint.photo_set.filter(phototype=NORMALPHOTOTYPE)
                .order_by('priority', 'id')):
                orderList[int(p.id)] = i+1

    t = get_template(os.path.join('engphoto', 'bigpicture.html'))
    html = t.render(RequestContext(R, {'photo_id': photo.id, 'type': type, 'project': project,
    'timeList': ','.join(timeList), 'orderList': str(orderList),
    'defectList': ','.join(defectList), 'trashList': ','.join(trashList),
    'checkpointList': ','.join(checkpointList), 'checkpoints': checkpoints}))
    return HttpResponse(html)


@authority_check
def getAllPhotoList(R, project, photo, **kw):
    Dir = CheckPoint.objects.get(project=project, template__isnull=True,
    name='目錄', uplevel__isnull=True)

    CPs = []
    for i, subCP in enumerate(Dir.sublevel.all().order_by('priority', 'id')):
        checkpoints = []
        for j, cp in enumerate(subCP.sublevel.all().order_by('priority', 'id')):
            checkpoints.append({'name': cp.rName(),
            'photo_ids': [p.id for p in cp.photo_set.filter(
            phototype=NORMALPHOTOTYPE).order_by('priority', 'id')]})
        CPs.append({'dir': {'name': subCP.rName()},
        'sublevel': checkpoints})

    normalphoto_ids = [p.id for p in
    Photo.objects.filter(project=project, phototype=NORMALPHOTOTYPE)]
    photos = _makePhotoLink(project, normalphoto_ids)

    return HttpResponse(json.write({'CPs': CPs,'status': True,'photos': photos }))


@authority_check
def makeEnough(R, project, photo, **kw):
    #TODO log 使用者「放寬檔案大小限制」紀錄
    photo.enoughtype = NONLESSTHANPHOTOSIZELIMITTYPE
    photo.save()
    return getPhotoById(R, project_id=project.id, photos_id=str(photo.id), right_type_value='檢視相片')


@authority_check
def makeNonDuplicate(R, project, photo, **kw):
    #TODO log 使用者「設定非重複相片」紀錄
    photo.duplicatetype = NONDUPLICATETYPE
    photo.save()
    return getPhotoById(R, project_id=project.id, photos_id=str(photo.id), right_type_value='檢視相片')


def _duplicate_md5string(*args):
    return md5(''.join(args)).hexdigest()[19:29].lower()


def _makePhotoLink(project, photo_ids):
    photos = {}
    for p in photo_ids:
        if p:
            if project:
                try: photo = Photo.objects.get(id=p, project=project)
                except Photo.DoesNotExist: continue
            else:
                try: photo = Photo.objects.get(id=p)
                except Photo.DoesNotExist: continue
            if photo.file:
                thumbsrc = thumb(photo.file.name, "width=400,height=300")
                photos[p] = {
                    'id': photo.id,
                    'checkpoint_id': photo.checkpoint.id,
                    'phototype': photo.phototype.value,
                    'project_name': photo.project.name,
                    'name': photo.rName(),
                    'position': photo.position,
                    'titlename': photo.__str__(),
                    'link': '/engphoto/getpic/' + photo.file.url,
                    'inspector_check': photo.inspector_check and '是' or '否',
                    'note_con': photo.note_con,
                    'note_ins': photo.note_ins,
                    'note_eng': photo.note_eng,
                    'note_exp': photo.note_exp,
                    'photodate': photo.getPhotodate('%Y/%m/%d'),
                    'size': photo.calSize(),
                    'updatetime': photo.getUpdatetime('%Y/%m/%d %H:%M:%S'),
                    'uploadtime': photo.getUploadtime('%Y/%m/%d %H:%M:%S'),
                    'thumbsrc': thumbsrc
                }
                if not project:
                    photos[p]['thumbsrc'] += '?c=%s' % _duplicate_md5string(settings.DUPLICATE_PASSWD,
                    photos[p]['thumbsrc'], str(photo.project.id))
            else:
                photos[p] = {
                    'id': photo.id,
                    'checkpoint_id': photo.checkpoint.id,
                    'name': photo.rName(),
                    'position': photo.position,
                    'titlename': photo.__str__(),
                    'inspector_check': photo.inspector_check and '是' or '否',
                    'note_con': photo.note_con,
                    'note_ins': photo.note_ins,
                    'note_eng': photo.note_eng,
                    'note_exp': photo.note_exp,
                    'updatetime': photo.getUpdatetime('%Y/%m/%d %H:%M:%S')
                }
    return photos


@authority_check
def moveTo(R, project, target_id, source_id, **kw):
    target_photo = Photo.objects.get(id=target_id)
    source_photo = Photo.objects.get(id=source_id)

    target_photo.renameFromNormal(source_photo, Photo(), Photo())

    type = TRASHPHOTOTYPE

    edit = _edit(R, target_photo.project)

    edit['button'] = False
    t = get_template(os.path.join('engphoto', 'photos.html'))
    html = t.render(RequestContext(R, {'edit': edit, 'photos': [target_photo]}))
    return HttpResponse(html)


@authority_check
def getPhotoById(R, project, photos_id, **kw):
    photo_ids = photos_id.split('/')
    try:
        photos = _makePhotoLink(project, photo_ids)
        return HttpResponse(json.write({'status': True, 'project_bid_no': project.bid_no, 'photos': photos}))
    except:
        return HttpResponse(json.write({'status': False}))


@authority_check
def getPic(R, filename, **kw):
    try: ext = re.search('\.(\w+)$', filename).groups()[0]
    except: return HttpResponse('無圖片')

    pic = open(os.path.join(settings.ROOT, filename), 'rb')
    content = pic.read()
    pic.close()

    response = HttpResponse(content)
    response['Content-Type'] = 'image/%s'%ext
    return response


@csrf_exempt
@authority_check
def updatePhotoInfo(R, project, photo, **kw):
    DATA = readDATA(R)
    photo_id = DATA.get('photo_id', None) or str(photo.id)

    fieldname = DATA.get('fieldname', '')
    if not fieldname: fieldname = R.GET['fieldname']
    value = DATA.get('value', '')
    if not value: value = R.GET['value']

    message = {'status': False, 'photo_id': photo_id, 'fieldname': fieldname}

    photo = Photo.objects.get(id=photo_id)
    if fieldname == 'comment':
        righttype_for_who = R.user.user_profile.rIdentity(project_id=project.id)

        if righttype_for_who == '監造廠商':
            photo.note_ins = value
            photo.save()
            return HttpResponse(json.write({'status': True, 'type': 'id_note_ins'}))
        elif righttype_for_who == '營造廠商':
            photo.note_con = value
            photo.save()
            return HttpResponse(json.write({'status': True, 'type': 'id_note_con'}))
        elif righttype_for_who in ['負責主辦工程師', '協同主辦工程師', '自辦主辦工程師']:
            photo.note_eng = value
            photo.save()
            return HttpResponse(json.write({'status': True, 'type': 'id_note_eng'}))
        else:
            return HttpResponse(json.write({'status': False, 'type': righttype_for_who}))
    elif fieldname != 'file':
        if fieldname == 'photodate':
            try: value = datetime.strptime(value, '%Y/%m/%d')
            except:
                try: value = datetime.strptime(value, '%Y-%m-%d')
                except: value = None
        setattr(photo, fieldname, value)
        photo.save()
    else:
        #sleep(15) #為了要看更新時的資訊
        # 當相片原本是正常的，但被上傳一張重複相片時，樹狀結構的計算會出錯。
        if not photo.file:
            message['newphoto'] = True
            message['checkpoint_id'] = photo.checkpoint.id

        file = R.FILES.get('file_'+photo_id, None)
        if file:
            photo.save_file(file)
            if hasattr(photo, 'warning'):
                message['status'] = False
                message['message'] = '上傳至 %s 的施工相片，其%s' % (photo.checkpoint, photo.warning)
                return HttpResponse(json.write(message))

            photo.owner = R.user
            photo.save()
            message['owner_name'] = R.user.user_profile.rName()
            message['owner_username'] = R.user.username
            message['thumbsrc'] = thumb(photo.file.name, "width=400,height=300")
            try: message['photodate'] = photo.photodate.strftime('%Y/%m/%d')
            except: message['photodate'] = ''
            message['size'] = photo.calSize()
            message['duplicatetype'] = str(photo.duplicatetype)
            message['enoughtype'] = str(photo.enoughtype)
            message['uploadtime'] = photo.uploadtime.strftime('%Y-%m-%d %H:%M:%S')
    message['status'] = True
    return HttpResponse(json.write(message))


@authority_check
def deletePhoto(R, project, photo, **kw):
    DATA = readDATA(R)
    type = DATA.get('type', '')
    if type == '資源回收筒': type = TRASHPHOTOTYPE
    elif type == '待改善相簿': type = DEFECTPHOTOTYPE
    else: return HttpResponse(json.write({'status': False, 'message': u'無類別'}))

    newPhoto = photo.moveToStore(type, Photo())

    edit = _edit(R, newPhoto.project)

    edit['button'] = False
    t = get_template(os.path.join('engphoto', 'photos.html'))
    html = t.render(RequestContext(R, {'edit': edit, 'photos': [newPhoto]}))
    return HttpResponse(json.write({'status': True, 'html': html}))


def _edit(R, project):
    edit = {}
    upload_photo_role = _ca(user=R.user, project_id=project.id, right_type_value='上傳相片')
    if upload_photo_role:
        edit['position'] = 'canedit'
        edit['upfilebutton'] = 'canedit'
        edit['comment'] = R.user.user_profile.rIdentity(project_id=project.id)
        edit['photodate'] = 'canedit'

    if _ca(user=R.user, project_id=project.id, right_type_value='檢視相片'):
        edit['inspector_check'] = 'canedit'

    if _ca(user=R.user, project_id=project.id, right_type_value='移至待改善相簿'):
        edit['defectbutton'] = 'canedit'

    write_comment_role = _ca(user=R.user, project_id=project.id, right_type_value='填寫相片意見')
    if write_comment_role:
        edit['comment'] = R.user.user_profile.rIdentity(project_id=project.id)

    return edit


@authority_check
def getPhotoByNotEnough(R, project, photo, **kw):
    notenough = _makePhotoLink(project, [photo.id])
    edit_power = _edit(R, project)
    if edit_power.get('defectbutton', None):
        delete = True
    else:
        delete = False
    return HttpResponse(json.write({'delete': delete, 'notenough': notenough}))


@authority_check
def getPhotoByDuplicate(R, project, photo, **kw):
    suspend = _makePhotoLink(project, [photo.id])
    duplicate_ids = photo.setDuplicates()
    try:
        duplicate_ids.remove(photo.id)
    except:
        pass
    duplicates = _makePhotoLink(None, duplicate_ids)
    edit_power = _edit(R, project)
    if edit_power.get('defectbutton', None):
        delete = True
    else:
        delete = False
    return HttpResponse(json.write({'delete': delete, 'suspend': suspend, 'duplicates': duplicates}))


@authority_check
def getPhotoBySomething(R, project, type, page_id, **kw):
    page = int(page_id)
    edit = _edit(R, project)

    if type == 'bytimesort':
        phototype = NORMALPHOTOTYPE
        type = 'time'
    elif type == 'bydefect':
        phototype = DEFECTPHOTOTYPE
        edit['indefect'] = True
        type = 'defect'
    elif type == 'bytrash':
        phototype = TRASHPHOTOTYPE
        edit['intrash'] = True
        type = 'trash'
    else: return HttpResponse('')

    t = get_template(os.path.join('engphoto', 'photos.html'))
    html = t.render(RequestContext(R, {'type': type, 'edit': edit,
    'photos': list(project.photo_set.filter(phototype=phototype, verify__isnull=False).order_by('-updatetime'))[page*10:page*10+10]
    }))
    return HttpResponse(html)


@authority_check
def getPhotoNum(R, project, type, **kw):
    if type == 'bytimesort':
        phototype = NORMALPHOTOTYPE
    elif type == 'bydefect':
        phototype = DEFECTPHOTOTYPE
    elif type == 'bytrash':
        phototype = TRASHPHOTOTYPE
    else: return HttpResponse('')

    count = project.photo_set.filter(phototype=phototype, verify__isnull=False).count()
    if count == 0:
        page = 0
    else:
        page = int(math.ceil(count / 10.))

    return HttpResponse(json.write({'type': type, 'page': page}))


@authority_check
def getPhotoByCheckPoint(R, project, checkpoint, **kw):
    edit = _edit(R, project)
    _makePhoto(checkpoint)

    t = get_template(os.path.join('engphoto', 'photos.html'))
    html = t.render(RequestContext(R, {'type': 'checkpoint', 'edit': edit, 'photos':
    checkpoint.photo_set.filter(phototype=NORMALPHOTOTYPE).order_by('priority', 'id')}))
    return HttpResponse(html)


def _getAndsetCheckPoint(Dir):
    CPs = []
    for i, subCP in enumerate(Dir.sublevel.all().order_by('priority', 'id')):
        subCP.priority = i * 10
        subCP.save()
        checkpoints = []
        allPhotoNum = 0
        uploadPhotoNum = 0
        for j, cp in enumerate(subCP.sublevel.all().order_by('priority', 'id')):
            cp.priority = j * 10
            cp.save()
            checkpoints.append(cp)
            allPhotoNum += cp.getAllPhotoNum()
            uploadPhotoNum += cp.getUploadPhotoNum()

        subCP.allphotonum = allPhotoNum
        subCP.uploadphotonum = uploadPhotoNum

        CPs.append({'dir': subCP, 'sublevel': checkpoints})
    return CPs


@authority_check
def exportActualCheckPoint(R, **kw):
    if kw.has_key('project'):
        project = kw['project']
    if not project.checkpoint_set.count():
        _makeRequireCheckPoint(project)
    Dir = CheckPoint.objects.get(project=project, template__isnull=True,
    name='目錄', uplevel__isnull=True)

    checkpoints = []
    sum = 0
    for g in Dir.sublevel.all():
        subgroups = []
        subgroup_sum = 0
        for cp in g.sublevel.all():
            allphotonum = cp.getAllPhotoNum()
            subgroup_sum += allphotonum
            subgroups.append(['', cp.rName(), allphotonum])
        checkpoints.append([g.rName(), '', subgroup_sum])
        checkpoints.extend(subgroups)
        sum += subgroup_sum

    data = {'replace': {
        'project_bid_no': project.bid_no,
        'project_name': project.name,
        'time': NOW,
        'sum': sum,
    },
        'checkpoint_table': checkpoints
    }

    template_name = 'engphoto_checkpoint.xls'

    content = makeFileByWordExcel(template_name=template_name, result=data)
    response = HttpResponse(content_type='application/xls')
    response['Content-Type'] = ('application/xls')
    response['Content-Disposition'] = ('attachment; filename=%s_checkpoint.xls' % project.bid_no).encode('cp950')
    response.write(content)
    return response


@authority_check
def getActualCheckPoint(R, **kw):
    if kw.get('project', None):
        project = kw['project']
    else:
        checkpoint = kw['checkpoint']
        Dir = CheckPoint.objects.get(id=checkpoint.id)
        project = Dir.project

    if not project.checkpoint_set.count():
        _makeRequireCheckPoint(project)

    if kw.get('checkpoint', None):
        Dir = Dir
    else:
        Dir = CheckPoint.objects.get(project=project, template__isnull=True,
        name='目錄', uplevel__isnull=True)

    CPs = _getAndsetCheckPoint(Dir)
    uploadphotonum = 0
    allphotonum = 0
    for cps in CPs:
        uploadphotonum += cps['dir'].uploadphotonum
        allphotonum += cps['dir'].allphotonum

    if _ca(user=R.user, project=project, right_type_value='編輯查驗點'):
        editcheckpoint = True
    else:
        editcheckpoint = False

    t = get_template(os.path.join('engphoto', 'tree.html'))
    html = t.render(RequestContext(R, {'project': project, 'upDir': Dir.uplevel, 'editcheckpoint': editcheckpoint,
    'Dir': Dir, 'CPs': CPs, 'uploadphotonum': uploadphotonum, 'allphotonum': allphotonum}))
    return HttpResponse(html)


@authority_check
def sortCheckPoint(R, project, **kw):
    DATA = readDATA(R)
    priority = int(DATA.get('priority', 0)) * 10
    checkpoint = CheckPoint.objects.get(id=DATA.get('checkpoint_id', 0))
    target_dir = CheckPoint.objects.get(id=DATA.get('dir_id', 0))
    if checkpoint.uplevel != target_dir:
        return HttpResponse(json.write({'status': False, 'message': '禁止移動至其他查驗點群組下!'}))

    target_checkpoint = target_dir.sublevel.get(priority=priority)

    if checkpoint.priority < priority:
        checkpoint.priority = priority + 1
    elif checkpoint.priority > priority:
        checkpoint.priority = priority - 1
    checkpoint.save()

    for i, c in enumerate(target_dir.sublevel.all().order_by('priority', 'id')):
        c.priority = i * 10
        c.save()
    return HttpResponse(json.write({'status': True}))


@authority_check
def index(R, project, **kw):
    R.session['project_id'] = project.id

    showmenu = {}
    if _ca(user=R.user, project=project, right_type_value='移至待改善相簿'):
        showmenu['defect'] = True
    else:
        showmenu['defect'] = False

    if _ca(user=R.user, project=project, right_type_value='上傳相片'):
        showmenu['trash'] = True
    else:
        showmenu['trash'] = False

    t = get_template(os.path.join('engphoto', 'index.html'))
    html = t.render(RequestContext(R, {'showmenu': showmenu, 'project': project}))
    return HttpResponse(html)


def _makePhoto(checkpoint):
    existnum = checkpoint.photo_set.count()
    i = -1
    for i in xrange(checkpoint.need-existnum):
        p = Photo(project=checkpoint.project, checkpoint=checkpoint, phototype=NORMALPHOTOTYPE)
        p.save()
        p.priority = (p.id + existnum) * 10
    return (i+ 1)


def _makeRequireCheckPoint(project):
    hash = {}
    sum = 0
    try:
        checkpointDir = project.checkpoint_set.get(template__isnull=True, name='目錄',
        uplevel__isnull=True)
    except CheckPoint.DoesNotExist:
        checkpointDir = CheckPoint(project=project, need=0, name='目錄', priority=0)
        checkpointDir.save()

    for i, t in enumerate(Template.objects.filter(require=True).order_by('id')):
        try:
            t.checkpoint_set.get(project=project)
        except:
            cp = CheckPoint(project=project, template=t, need=t.floor, priority=i)
            cp.save()
            hash[t.id] = cp
            if not t.uplevel:
                cp.uplevel = checkpointDir
            else:
                cp.uplevel = hash[t.uplevel.id]
            cp.save()
            if not t.sublevel.count(): sum += _makePhoto(cp)

    return sum


@authority_check
def addCheckPoint(R, project, kind, **kw):
    DATA = readDATA(R)
    ids = {}
    for k, v in DATA.items():
        try:
            id = int(k)
            try: need = int(v)
            except: need = 0
            ids[id] = need
        except: pass
    checkpointDir = CheckPoint.objects.get(project=project, template__isnull=True,
    name='目錄', uplevel__isnull=True)

    if kind == 'project':
        try: (k, v) = ids.items()[0]
        except IndexError: return HttpResponse(json.write({'status': False, 'message': '未選取查驗點! '}))
        anotherProjectCheckPoint = CheckPoint.objects.get(id=k)
        another_checkpointDir = CheckPoint.objects.get(project=anotherProjectCheckPoint.project,
        template__isnull=True, name='目錄', uplevel__isnull=True)

        Template_packages = CheckPoint.objects.filter(id__in=ids.keys(), uplevel=another_checkpointDir)
        Template_checkpoints = CheckPoint.objects.filter(id__in=ids.keys(), uplevel__in=Template_packages)

    elif kind == 'template':
        Template_packages = Template.objects.filter(id__in=ids.keys(), uplevel__isnull=True)
        Template_checkpoints = Template.objects.filter(id__in=ids.keys(), uplevel__isnull=False)

    packages_times = {}
    for tps in Template_packages:
        if ids[tps.id] > 0: packages_times[tps.id] = ids[tps.id]

    subcheckpoint_num = checkpointDir.sublevel.count()
    checkpoints_sum = subcheckpoint_num
    photos_sum = 0
    while packages_times:
        Template_packages_hash = {}
        for Template_checkpoint in Template_checkpoints:
            if Template_packages.filter(id=Template_checkpoint.uplevel.id):
                if Template_packages_hash.has_key(Template_checkpoint.uplevel.id):
                    uplevel = Template_packages_hash[Template_checkpoint.uplevel.id]
                else:
                    if kind == 'project':
                        template = Template_checkpoint.uplevel.template
                        if template:
                            name = help = None
                        else:
                            name = Template_checkpoint.uplevel.rName()
                            help = Template_checkpoint.uplevel.getHelp()
                    elif kind == 'template':
                        template = Template_checkpoint.uplevel
                        name = help = None
                    uplevel = CheckPoint(project=project, template=template,
                    need=0, uplevel=checkpointDir, name=name, help=help,
                    priority=(Template_checkpoint.uplevel.id+checkpoints_sum)*10)
                    uplevel.save()
                    Template_packages_hash[Template_checkpoint.uplevel.id] = uplevel

                if ids[Template_checkpoint.id] < Template_checkpoint.getFloor():
                    need = Template_checkpoint.getFloor()
                else:
                    need = ids[Template_checkpoint.id]
                if kind == 'project':
                    template = Template_checkpoint.template
                    if template:
                        name = help = None
                    else:
                        name = Template_checkpoint.rName()
                        help = Template_checkpoint.getHelp()
                elif kind == 'template':
                    template = Template_checkpoint
                    name = help = None
                checkpoint = CheckPoint(project=project, template=template, need=need,
                name=name, help=help, uplevel=uplevel,
                priority=(Template_checkpoint.id+checkpoints_sum)*10)
                checkpoint.save()
                checkpoints_sum += 1
                photos_sum += _makePhoto(checkpoint)
        for tph in Template_packages_hash.keys():
            packages_times[tph] -= 1
            if packages_times[tph] <= 0:
                Template_checkpoints = Template_checkpoints.exclude(uplevel__id=tph)
                del packages_times[tph]

    return HttpResponse(json.write({'status': True,
    'message': '已新增 %s 個查驗點及 %s 張相片上傳欄位。'
    %(checkpoints_sum - subcheckpoint_num, photos_sum)}))


@authority_check
def changeNeed(R, project, checkpoint, **kw):
    DATA = readDATA(R)
    try:
        value = int(DATA.get('value', 0))
    except ValueError:
        return HttpResponse(json.write({'status': False, 'message': '請設定整數', 'value': checkpoint.need}))

    low = checkpoint.photo_set.filter(phototype=NORMALPHOTOTYPE, verify__isnull=False).count()
    empty_file = checkpoint.photo_set.filter(phototype=NORMALPHOTOTYPE, verify__isnull=True).order_by('-updatetime')
    if 0 < value < low:
        return HttpResponse(json.write({'status': False, 'message': '已上傳%s張相片，張數不可低於該值'%low,
        'value': checkpoint.need}))
    elif value <= 0:
        return HttpResponse(json.write({'status': False, 'message': '張數需超過 0 張',
        'value': checkpoint.need}))
    else:
        orineed = checkpoint.need
        checkpoint.need = value
        checkpoint.save()

        if value > orineed:
            _makePhoto(checkpoint)
        elif value < orineed:
            for p in empty_file[:orineed-value]: p.delete()

        return HttpResponse(json.write({'status': True}))


@authority_check
def addSingleCheckPoint(R, project, checkpoint, **kw):
    if checkpoint.uplevel.name == '目錄':
        kind = '查驗點群組'
    else:
        kind = '查驗點'

    DATA = readDATA(R)
    if DATA.get('type', None) == 'child_checkpoint':
        uplevel = checkpoint
        kind = '查驗點'
        child_checkpoints = checkpoint.sublevel.all().order_by('priority')
        if child_checkpoints:
            priority = child_checkpoints[0].priority - 1
        else:
            priority = 0
    else:
        uplevel = checkpoint.uplevel
        priority = checkpoint.priority

    new_checkpoint = CheckPoint(project=checkpoint.project,
    name='**%s**'%kind, help='無說明', need=0,
    uplevel=uplevel, priority=priority)

    try:
        new_checkpoint.save()
        return HttpResponse(json.write({'status': True, 'id': new_checkpoint.id}))
    except:
        return HttpResponse(json.write({'status': False}))


@authority_check
def getSingleCheckPoint(R, project, checkpoint, **kw):
    if checkpoint.template:
        require = checkpoint.template.require
    else:
        require = False
    checkpoint.need = checkpoint.getAllPhotoNum()
    checkpoint.save()
    res = {
        'content_type_id': checkpoint.getContentTypeId(),
        'name': checkpoint.rName(),
        'help': checkpoint.getHelp(),
        'need': checkpoint.need,
        'require': require
    }
    return HttpResponse(json.write(res))


@authority_check
def getCheckPoint(R, project, kind, **kw):
    if kind == 'template':
        CPs = Template.objects.filter(require=False, uplevel__isnull=True)
    elif kind == 'project':
        try:
            dir = CheckPoint.objects.get(project__id=project.id, name='目錄', uplevel__isnull=True)
        except:
            return HttpResponse(json.write({'id': project.id, 'status': False}))
        CPs = dir.sublevel.exclude(template__require=True) #原為 .filter(template__require=False)，但可能有些查驗點的 template=null ，所以反而會找不到，所以改成「排除 template = True 」的查驗點(通常為「施工前中後」)。

    checkpoints = []
    for checkpoint in CPs:
        key = {
            'id': checkpoint.id,
            'name': checkpoint.rName(),
            'floor': checkpoint.getFloor(),
            'help': checkpoint.getHelp(),
        }
        values = [key]
        for sublevel in checkpoint.sublevel.all():
            values.append({
                'id': sublevel.id,
                'name': sublevel.rName(),
                'floor': sublevel.getFloor(),
                'help': sublevel.getHelp(),
            })
        checkpoints.append(values)
    if len(checkpoints) > 0:
        return HttpResponse(json.write({'id': project.id, 'status': True, 'CheckPoints': checkpoints}))
    else:
        return HttpResponse(json.write({'id': project.id, 'status': False}))