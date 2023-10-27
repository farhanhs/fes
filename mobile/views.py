# -*- coding: utf-8 -*-
import os, random, json, re, datetime
from os.path import join
from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.sessions.models import Session
from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.template.loader import get_template
from django.template import Context, RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from common.lib import verifyOK
from general.models import Place, Unit, FishCityMenuManager, UNITS, LOAD_UNITS
from common.lib import md5password
from fishuser.models import *
from dailyreport.models import EngProfile, Report
from supervise.models import SuperviseCase, Error
from gallery.models import Node as GalleryNode
from gallery.models import Photo as GalleryPhoto
from engphoto.models import Photo as EngPhoto
from engphoto.models import CheckPoint as EngNode
from weblive.models import Place as MonitorPlace
from weblive.models import Monitor

TODAY = lambda: datetime.date.today()
NOW = lambda: datetime.datetime.now()
TAIWAN = Place.objects.get(name=u'臺灣地區')
places = [TAIWAN] + list(Place.objects.filter(uplevel=TAIWAN).order_by('id'))
years = [y-1911 for y in xrange(2008, TODAY().year+4)]
years.reverse()
this_year = TODAY().year - 1911
units = LOAD_UNITS()[:]

# LOGIN_URL = reverse('m_login')
# reverse('m_index') = reverse('m_index')


def _make_choose():
    options = Option.objects.all().order_by('id')
    chooses = {}
    for i in options:
        if chooses.has_key(i.swarm):
            chooses[i.swarm].append(i)
        else:
            chooses[i.swarm] = [i]
    return chooses


def _need_unlogin(myFunc):
    def innerFunc(*args, **kw):
        R = args[0]
        if R.user.is_authenticated():
            if 'http' in R.GET.get('next', reverse('m_index')):
                next = reverse('m_index')
            else:
                next = R.GET.get('next', reverse('m_index'))
            return HttpResponseRedirect(next)
        return myFunc(*args, **kw)
    return innerFunc


@_need_unlogin
def login(R):
    try: session = Session.objects.all()[0]
    except IndexError: session = None

    user = R.user
    data = R.POST# or json.loads(R.body)
    next = R.GET.get('next', reverse('m_index'))

    if 'login' == data.get('submit', None):
        username = data.get('username', '').lower()
        password = data.get('password', '').lower()
        verifycode_id = data.get('verifycode_id', 0)
        verify = data.get('verify', 0)

        if not verifyOK(verifycode_id, verify): 
            return HttpResponse(json.dumps({'status': False, 'message': u'圖片數字不正確'}))

        user = auth.authenticate(username=username, password=password)

        if not user:
            try: wronglogin = WrongLogin.objects.get(session=session)
            except: wronglogin = False
            if wronglogin: wronglogin.times += 1
            else: wronglogin = WrongLogin(session=session, start_time=NOW())
            wronglogin.save()
            return HttpResponse(json.dumps({'status': False, 'message': u'無此帳號 或是 密碼錯誤。'}))
        elif not user.is_active:
            return HttpResponse(json.dumps({'status': False, 'message': u'此帳號已被停用'}))
        else:
            try: up = user.user_profile
            except UserProfile.DoesNotExist: up = UserProfile(user=user)
            auth.login(R, user)
            up.login += 1
            up.save()
            user.last_login = NOW()
            user.save()
            if R.META.has_key('x_forwarded_for'): ip = R.META['x_forwarded_for']
            elif R.META.has_key('X_FORWARDED_FOR'): ip = R.META['X_FORWARDED_FOR']
            else: ip = R.META['REMOTE_ADDR']

            lh = LoginHistory(user=user, ip=ip, datetime=NOW())
            lh.save()

            return HttpResponse(json.dumps({'status': True, 'next': next}))

    template = get_template(os.path.join('mobile', 'login.html'))
    html = template.render(RequestContext(R,{}))
    return HttpResponse(html)


@login_required(login_url='/mobile/login/')
def logout(R):
    auth.logout(R)
    return HttpResponseRedirect(reverse('m_login'))


@login_required(login_url='/mobile/login/')
def index(R):
    t = get_template(os.path.join('mobile', 'index.html'))
    html = t.render(RequestContext(R,{
        'user': R.user,
        'user_profile': R.user.user_profile,
        'system_infos': SystemInformation.objects.filter(start_date__lte=TODAY()).order_by('-start_date')[:5]
        }))
    return HttpResponse(html)


@login_required(login_url='/mobile/login/')
def my_project(R):
    user = R.user
    if not user.has_perm('fishuser.sub_menu_remote_control_system_my'):
        return HttpResponseRedirect(reverse('m_index'))

    projects = [p.project for p in FRCMUserGroup.objects.filter(project__deleter=None, user=user).order_by('-project__id')]
    countychasetime = CountyChaseTime.objects.all().order_by('-id')[0]
    have_print_button_self = False
    have_print_button_all = False
    working_projects = []
    finish_projects = []

    for p in projects:
        p.usergroup = FRCMUserGroup.objects.get(user=user, project=p).group.name
        p.open = FRCMUserGroup.objects.get(user=user, project=p).is_active
        p.message = '帳號關閉中'

        try:
            ono = p.countychaseprojectonebyone_set.get()
            if p.purchase_type.value == u'一般勞務' and ono.act_ser_acceptance_closed:
                finish_projects.append(p)
            elif p.purchase_type.value in [u'工程', u'工程勞務'] and ono.act_eng_do_closed:
                finish_projects.append(p)
            else:
                working_projects.append(p)
        except:
            working_projects.append(p)

    t = get_template(os.path.join('mobile', 'my_project.html'))
    html = t.render(RequestContext(R,{
        'user': user,
        'user_profile': R.user.user_profile,
        'projects': working_projects,
        'finish_projects': finish_projects,
        }))
    return HttpResponse(html)




@login_required(login_url='/mobile/login/')
def search_project(R):
    if not R.user.has_perm('fishuser.sub_menu_remote_control_system_search'):
        # 沒有 "第二層選單_遠端管理系統_搜尋工程"
        return HttpResponseRedirect(reverse('m_index'))

    if not R.user.has_perm('fishuser.view_all_project_in_remote_control_system'):
        # 沒有 "在(遠端工程系統)中_觀看_所有_工程案資訊"
        new_units = [R.user.user_profile.unit]
    else:
        new_units = units

    top_plan = Plan.objects.get(uplevel=None)
    plans = [top_plan] + top_plan.rSubPlanInList()
    for i in plans:
        i.name = i.rLevelNumber() * '　' + '● ' + i.name

    fishing_ports = FishingPort.objects.all().order_by('place', 'name')
    aquacultures = Aquaculture.objects.all().order_by('place', 'name')

    t = get_template(os.path.join('mobile', 'search_project.html'))
    html = t.render(RequestContext(R,{
        'user': R.user,
        'user_profile': R.user.user_profile,
        'years': years,
        'this_year': this_year,
        'plans': plans,
        'fishing_ports': fishing_ports,
        'aquacultures': aquacultures,
        'option': _make_choose(),
        'places': places,
        'units': new_units,
        }))
    return HttpResponse(html)


@login_required(login_url='/mobile/login/')
def search_supervise(R):
    if not R.user.has_perm('fishuser.top_menu_supervise_system'):
        # 沒有 "第一層選單_督導系統"
        return HttpResponseRedirect(reverse('m_index'))

    t = get_template(os.path.join('mobile', 'search_supervise.html'))
    html = t.render(RequestContext(R,{
        'user': R.user,
        'units': units,
        'places': places,
        'user_profile': R.user.user_profile,
        }))
    return HttpResponse(html)


@login_required(login_url='/mobile/login/')
def project_info(R, **kw):
    try: project = Project.objects.get(id=kw['project_id'])
    except project.DoesNotExist: return HttpResponseRedirect(reverse('m_index'))
    if not R.user.has_perm('fishuser.view_all_project_in_remote_control_system'):
        #沒有 "在(遠端工程系統)中_觀看_所有_工程案資訊"
        if not 'view_single_project_in_remote_control_system' in get_perms(R.user, project):
            #沒有 觀看此project 的 "在(遠端工程系統)中_觀看_單一_工程案資訊" 權限
            return HttpResponseRedirect(reverse('m_index'))
        elif 'view_single_project_in_remote_control_system' in get_perms(R.user, project):
            #有 觀看此project 的 "在(遠端工程系統)中_觀看_單一_工程案資訊" 權限
            if not R.user.frcmusergroup_set.get(project=project).is_active:
                #被關閉權限的
                return HttpResponseRedirect(reverse('m_index'))

    elif R.user.has_perm('fishuser.view_all_project_in_remote_control_system'):
        #有 "在(遠端工程系統)中_觀看_所有_工程案資訊"
        if not R.user.has_perm('fishuser.view_all_project_in_management_system'):
            #縣市政府人員
            if project.unit != R.user.user_profile.unit and not R.user.is_staff and not 'view_single_project_in_remote_control_system' in get_perms(R.user, project):
                #不是自己單位的工程
                return HttpResponseRedirect(reverse('m_index'))

    user = R.user
    try:
        project.your_identity = FRCMUserGroup.objects.get(user=R.user, project=project)
    except:
        project.your_identity = u'瀏覽者'
        
    if not project.inspector_code: project.create_i_code()
    if not project.contractor_code: project.create_c_code()

    project.engineers = [u for u in FRCMUserGroup.objects.filter(project=project).exclude(group__name=u'監造廠商').exclude(group__name=u'營造廠商').order_by('id')]
    project.ins_and_con = [u for u in FRCMUserGroup.objects.filter(group__name__in=[u'監造廠商', u'營造廠商'], project=project).order_by('-group')]
    project.engs = [u for u in FRCMUserGroup.objects.filter(project=project, group__name__in=[u'負責主辦工程師', u'協同主辦工程師', u'自辦主辦工程師'])]
    project.identity = user.user_profile.rIdentity(project.id)
    
    if project.identity not in [u'負責主辦工程師', u'協同主辦工程師', u'自辦主辦工程師', u'監造廠商'] and not R.user.has_perm('fishuser.view_all_project_in_remote_control_system'):
        project.inspector_code = u'無觀看權限'
    if project.identity not in [u'負責主辦工程師', u'協同主辦工程師', u'自辦主辦工程師', u'營造廠商'] and not R.user.has_perm('fishuser.view_all_project_in_remote_control_system'):
        project.contractor_code = u'無觀看權限'

    fund = Fund.objects.get(project=project)
    budget = list(Budget.objects.filter(fund=fund).order_by('year'))[0]
    if budget.capital_ratify_revision and budget.capital_ratify_revision != 0:
        project.budget_money = (budget.capital_ratify_revision or 0)
    else:
        project.budget_money = (budget.capital_ratify_budget or 0)

    chase_one_by_one = project.countychaseprojectonebyone_set.get()
        
    allocations = Allocation.objects.filter(project=project).order_by('date')

    t = get_template(os.path.join('mobile', 'project_info.html'))
    html = t.render(RequestContext(R,{
            'user': R.user,
            'project': project,
            'option' : _make_choose(),
            'fund': fund,
            'budget': fund.budget_set.all().order_by('year')[0],
            'allocations': allocations,
            'chase_one_by_one': chase_one_by_one,
        }))
    return HttpResponse(html)


@login_required(login_url='/mobile/login/')
def supervise_info(R, **kw):
    if not R.user.has_perm('fishuser.top_menu_supervise_system'):
        # 沒有 "第一層選單_督導系統"
        return HttpResponseRedirect(reverse('m_index'))

    project = SuperviseCase.objects.get(id=kw['project_id'])
    project.errors = Error.objects.filter(case=project).order_by('ec__no')
    for error in project.errors:
        error.context = error.context.replace('\n', '').replace('\r', '')

    project.captain_string = u'、'.join([g.name.replace('\n', '') for g in project.captain.all()])
    project.worker_string = u'、'.join([g.name.replace('\n', '') for g in project.worker.all()])
    project.outguide_string = u'、'.join([g.name.replace('\n', '') for g in project.outguide.all()])
    project.inguide_string = u'、'.join([g.name.replace('\n', '') for g in project.inguide.all()])
    if project.score >= 90:
        project.score = u'%s %s' % (project.score, u'(優等)')
    elif project.score >= 80:
        project.score = u'%s %s' % (project.score, u'(甲等)')
    elif project.score >= 70:
        project.score = u'%s %s' % (project.score, u'(乙等)')
    elif project.score >= 60:
        project.score = u'%s %s' % (project.score, u'(丙等)')
    elif project.score >= 1:
        project.score = u'%s %s' % (project.score, u'(丁等)')
    else:
        project.score = u'不評分'

    t = get_template(os.path.join('mobile', 'supervise_info.html'))
    html = t.render(RequestContext(R,{
            'user': R.user,
            'project': project,
        }))
    return HttpResponse(html)


@login_required(login_url='/mobile/login/')
def dailyreport(R, **kw):
    try: project = Project.objects.get(id=kw['project_id'])
    except Project.DoesNotExist: return HttpResponseRedirect(reverse('m_index'))

    if not R.user.has_perm('fishuser.view_all_project_in_remote_control_system'):
        #沒有 "在(遠端工程系統)中_觀看_所有_工程案資訊"
        if not 'view_single_project_in_remote_control_system' in get_perms(R.user, project):
            #沒有 觀看此project 的 "在(遠端工程系統)中_觀看_單一_工程案資訊" 權限
            if project.unit != R.user.user_profile.unit:
                return HttpResponseRedirect(reverse('m_index'))
        elif 'view_single_project_in_remote_control_system' in get_perms(R.user, project):
            #有 觀看此project 的 "在(遠端工程系統)中_觀看_單一_工程案資訊" 權限
            if not R.user.frcmusergroup_set.get(project=project).is_active:
                #被關閉權限的
                return HttpResponseRedirect(reverse('m_index'))
    else:
        if R.user.username[1] == '_' and not R.user.is_staff:
            if project.unit != R.user.user_profile.unit:
                return HttpResponseRedirect(reverse('m_index'))

    engprofile = project.dailyreport_engprofile.get_or_create()
    engprofile = project.dailyreport_engprofile.get()
    engprofile.extensions = project.dailyreport_extension.all().order_by('date')
    engprofile.specialdates = project.dailyreport_specialdate.all().order_by('begin_date')

    working_dates = engprofile.readWorkingDate()

    if working_dates:
        should_done_date = working_dates[-1]
    else:
        should_done_date = TODAY()

    reports = Report.objects.filter(project=project).order_by('-date')
    if reports:
        if reports[0].date > should_done_date:
            should_done_date = reports[0].date

    if should_done_date > TODAY():
        should_done_date = TODAY()

    if working_dates:
        schedule_progress = engprofile.read_schedule_progress()
        i_action_progress = engprofile.read_action_progress(report_type='inspector')
        c_action_progress = engprofile.read_action_progress(report_type='contractor')
    else:
        schedule_progress = []
        i_action_progress = []
        c_action_progress = []

    month_list = []
    progress = []
    if working_dates:
        start_date = working_dates[0]
        while start_date != should_done_date + datetime.timedelta(1):
            if start_date not in working_dates and start_date <= working_dates[-1]:
                start_date += datetime.timedelta(1)
                continue

            if u'%s-%s' % (start_date.year, start_date.month) not in month_list:
                month_list.append(u'%s-%s' % (start_date.year, start_date.month))

            progress.append({
                    u'date': start_date,
                    u'd': 0,
                    u'i': 0,
                    u'c': 0
                })

            if schedule_progress.has_key(start_date):
                progress[-1]['d'] = schedule_progress[start_date]
            if i_action_progress.has_key(start_date):
                progress[-1]['i'] = i_action_progress[start_date]
            if c_action_progress.has_key(start_date):
                progress[-1]['c'] = c_action_progress[start_date]
            start_date += datetime.timedelta(1)

    month_list.reverse()
    progress.reverse()
    engprofile.progress = progress

    random_str = str(random.random())

    t = get_template(os.path.join('mobile', 'dailyreport.html'))
    html = t.render(RequestContext(R,{
            'user': R.user,
            'project': project,
            'engprofile': engprofile,
            'month_list': month_list,
            'month_list_string': ','.join(month_list),
            'random_str': random_str,
            'TODAY': TODAY(),
        }))
    return HttpResponse(html)


@login_required(login_url='/mobile/login/')
def gallery(request, project_id):
    try: project = Project.objects.get(id=project_id)
    except Project.DoesNotExist: return HttpResponseRedirect(reverse('m_index'))

    def _push_gallery_photo(gallery_photo, node):
        gallery_photo += list(GalleryPhoto.objects.filter(node=node).order_by('priority'))
        for child in node.child_nodes.all().order_by('priority'):
            _push_gallery_photo(gallery_photo, child)
        return gallery_photo

    def _push_eng_photo(enf_photo, node):
        enf_photo += list(EngPhoto.objects.filter(checkpoint=node, uploadtime__isnull=False, phototype__id=1).order_by('priority'))
        for child in node.sublevel.all().order_by('priority'):
            _push_eng_photo(enf_photo, child)
        return enf_photo

    data = request.GET
    img_per_page = 10
    page, order, options = 1, 'time', ['time', 'node']
    if data.has_key('page') and data['page']: page = int(data['page'])
    if data.has_key('order') and data['order']: order = data['order']
    if order not in options: order = options[0]

    gallery_photo, enf_photo = [], []
    if order == options[0]:
        if project.use_gallery:
            gallery_photo = GalleryPhoto.objects.filter(node__case__parent=project).order_by('create_time')
        else:
            enf_photo = EngPhoto.objects.filter(project=project, uploadtime__isnull=False, phototype__id=1).order_by('uploadtime')
    elif order == options[1]:
        if project.use_gallery:
            for node in GalleryNode.objects.filter(case__parent=project, parent__isnull=True).order_by('priority'):
                gallery_photo = _push_gallery_photo(gallery_photo, node)
        else:
            for node in EngNode.objects.filter(project=project, uplevel__isnull=True).order_by('priority'):
                enf_photo = _push_eng_photo(enf_photo, node)

    total = len(gallery_photo) + len(enf_photo)
    final = (total/img_per_page + (total%img_per_page > 0)) or 1
    page = page if page > 0 else 1
    page = page if page <= final else final
    lower = (page-1)*img_per_page + 1
    lower = lower if lower < total else total
    upper = (page-1)*img_per_page + img_per_page
    upper = upper if upper < total else total

    template = loader.get_template(join('mobile', 'gallery.html'))
    context = {
        'project': project,
        'page': page,
        'total': total,
        'final': final,
        'lower': lower,
        'upper': upper,
        'gallery_photo': gallery_photo[lower-1 if lower-1 > -1 else lower:upper],
        'enf_photo': enf_photo[lower-1 if lower-1 > -1 else lower:upper],
    }
    return HttpResponse(template.render(context, request))


@login_required(login_url='/mobile/login/')
def claim_project(R):

    i_group = Group.objects.get(name=u'監造廠商')
    c_group = Group.objects.get(name=u'營造廠商')

    t = get_template(os.path.join('mobile', 'claim_project.html'))
    html = t.render(RequestContext(R,{
            'user': R.user,
            'i_group': i_group,
            'c_group': c_group,
            'today': TODAY(),
        }))
    return HttpResponse(html)



@login_required(login_url='/mobile/login/')
def set_password(R):
    print R.POST
    if R.POST.get('submit', '') == 'reset_password':
        user = R.user
        password = R.POST.get('password', None)
        if len(password) < 32:
            #TODO 須制作 log 處理，因為發生這種狀態，表示系統可能遭受不明現象的攻擊
            return HttpResponse(json.dumps({'status': False, 'message': '密碼格式非常有問題'}))
        elif md5password(user.username) == password:
            return HttpResponse(json.dumps({'status': False, 'message': '密碼不可以跟帳號一樣'}))
        else:
            user.set_password(password)
            user.save()
            return HttpResponse(json.dumps({'status': True}))

    t = get_template(os.path.join('mobile', 'set_password.html'))
    html = t.render(RequestContext(R,{
            'user': R.user,
        }))
    return HttpResponse(html)


@login_required(login_url='/mobile/login/')
def monitor(request):
    if not request.user.has_perm(u'fishuser.top_menu_harbor_system'):
        return HttpResponseRedirect(reverse('mobile.views.index'))

    if request.user.username[1] != '_' or request.user.is_staff:
        cams = Monitor.objects.all().order_by('place', 'port')
    else:
        account = User.objects.get(username=request.user.username[:2]+'account')
        unit_name = account.user_profile.unit.name[:3]
        cams = Monitor.objects.filter(place=MonitorPlace.objects.get(name=unit_name)).order_by('place', 'port')

    monitor_group, ports = [], []
    for monitor in cams:
        if monitor.port not in ports:
            ports.append(monitor.port)
            monitor_group.append({'port': monitor.port, 'monitors': []})

        monitor_group[ports.index(monitor.port)]['monitors'].append(monitor)


    template = loader.get_template(join('mobile', 'monitor.html'))
    context = {
        'monitor_group': monitor_group,
        'ports': ports,
    }
    return HttpResponse(template.render(context, request))