# -*- coding: utf-8 -*-

from django.template.loader import get_template
from django.template import Context, RequestContext
from django.http import HttpResponse, HttpResponseRedirect, FileResponse
from django.contrib import auth
from django.db.models import Q
from django import forms
from django.contrib.auth.models import User, Group
from django.contrib.sessions.models import Session
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.core.mail import send_mail
from django.core import mail
from django.views.decorators.csrf import csrf_exempt

import smtplib
from email import encoders
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.utils import COMMASPACE, formatdate

from fishuser.models import Option
from fishuser.models import UserProfile
from fishuser.models import ResetPasswordUser
from fishuser.models import LoginHistory
from fishuser.models import WrongLogin
from fishuser.models import DocumentOfProjectModels
from fishuser.models import Plan
from fishuser.models import PlanBudget
from fishuser.models import Project
from fishuser.models import Project_Port
from fishuser.models import DefaultProject
from fishuser.models import FRCMUserGroup
from fishuser.models import Factory
from fishuser.models import Reserve
from fishuser.models import FundRecord
from fishuser.models import Fund
from fishuser.models import BudgetProject
from fishuser.models import Appropriate
from fishuser.models import Progress
from fishuser.models import ScheduledProgress
from fishuser.models import ProjectPhoto
from fishuser.models import FRCMTempFile
from fishuser.models import CencelLoginEmail
from fishuser.models import EmailList
from fishuser.models import _ca
from fishuser.models import CountyChaseTime
from fishuser.models import CountyChaseProjectOneByOne
from fishuser.models import CountyChaseProjectOneToMany
from fishuser.models import SystemInformation, SystemInformationFile
from supervise.models import Edit
from common.models import Log
from general.models import Place, Unit, UNITS, LOAD_UNITS
from general.models import FishCityMenuManager
from common.lib import find_sub_level
from common.lib import find_sub
from common.lib import nocache_response
from common.lib import md5password
from common.lib import readDATA
from common.lib import verifyOK
from common.lib import makePageList

from settings import NUMPERPAGE
from settings import DEBUG
from settings import CAN_VIEW_BUG_PAGE_IPS
import os
import random
import json
import base64
import time
if not hasattr(json, "write"):
    #for python2.6
    json.write = json.dumps
    json.read = json.loads

import re
import datetime
from datetime import timedelta
from common.models import Log
from django.forms import ModelForm
from math import ceil

from guardian.shortcuts import assign
from guardian.shortcuts import remove_perm
from guardian.shortcuts import get_perms

from django.conf import settings
CAN_VIEW_BUG_PAGE_IPS = settings.CAN_VIEW_BUG_PAGE_IPS
NUMPERPAGE = settings.NUMPERPAGE
ROOT = settings.ROOT

# from Crypto.PublicKey import RSA

# from aes_crypto import AESCrypto

TODAY = lambda: datetime.date.today()
NOW = lambda: datetime.datetime.now()
TAIWAN = Place.objects.get(name=u'臺灣地區')
years = [y-1911 for y in xrange(2008, TODAY().year+5)]
years.reverse()
this_year = TODAY().year - 1911

#轉移開始------------------------------------------------------------------

def _make_choose():
    options = Option.objects.all()
    chooses = {}
    for i in options:
        if chooses.has_key(i.swarm):
            chooses[i.swarm].append(i)
        else:
            chooses[i.swarm] = [i]
    return chooses


def needNotLogin(myFunc):
    def innerFunc(*args, **kw):
        R = args[0]
        if R.user.is_authenticated():
            if 'http' in R.GET.get('next', '/fishuser/user_profile/'):
                next = '/fishuser/user_profile/'
            else:
                next = R.GET.get('next', '/fishuser/user_profile/')
            return HttpResponseRedirect(next)
        return myFunc(*args, **kw)
    return innerFunc


def denyFunction(*args, **kw):
    """ 拒絕使用者使用的函式
    """
    #return HttpResponse('deny')
    return HttpResponseRedirect('/')


def checkAuthority(viewFunction):
    def modifyFunction(*args, **kw):
        R = args[0]
        right_type_value = kw.get('right_type_value', '')
        project_id = kw.get('project_id', 0)

        try: project = Project.objects.get(id=project_id)
        except Project.DoesNotExist: project = ''
        except: project = ''
        if '觀看管考系統資料' == right_type_value and R.user.username[1] == '_':
            return denyFunction(*args, **kw)

        if _ca(user=R.user, project=project,
            right_type_value=right_type_value) or R.user.is_staff:
            kw['project'] = project
            return viewFunction(*args, **kw)
        else:
            return denyFunction(*args, **kw)
    return login_required(modifyFunction)


#@needNotLogin
def download_backup(R):
    d = timedelta(days = 0)
    try:
	client_ip = R.META['HTTP_X_FORWARDED_FOR']
    except:
        client_ip = R.META['REMOTE_ADDR']
    date = (datetime.datetime.now() - d).strftime('%Y%m%d')
    year = (datetime.datetime.now() - d).strftime('%Y')
    file_name = 'cim.'+date+'.tar.bz2'
    sql = '/backup/cim.db/'+year+'/'+file_name 
    if client_ip in CAN_VIEW_BUG_PAGE_IPS:
        f = open(sql,'rb')
        response = FileResponse(f)
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename="{}"'.format(file_name)
        return response
    else:
        return HttpResponseRedirect('/')

def download_backup_d1(R):
    d = timedelta(days = 1)
    try:
    	client_ip = R.META['HTTP_X_FORWARDED_FOR']
    except:
	client_ip = R.META['REMOTE_ADDR']
    date = (datetime.datetime.now() - d).strftime('%Y%m%d')
    year = (datetime.datetime.now() - d).strftime('%Y')
    file_name = 'cim.'+date+'.tar.bz2'
    sql = '/backup/cim.db/'+year+'/'+file_name
  
    if client_ip in CAN_VIEW_BUG_PAGE_IPS:
        f = open(sql,'rb')
        response = FileResponse(f)
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename="{}"'.format(file_name)
        return response
    else:
        return HttpResponseRedirect('/')
    
def download_backup_d2(R):
    d = timedelta(days = 2)
    try:
        client_ip = R.META['HTTP_X_FORWARDED_FOR']
    except:
        client_ip = R.META['REMOTE_ADDR']
    date = (datetime.datetime.now() - d).strftime('%Y%m%d')
    year = (datetime.datetime.now() - d).strftime('%Y')
    file_name = 'cim.'+date+'.tar.bz2'
    sql =  '/backup/cim.db/'+year+'/'+file_name
    if client_ip in CAN_VIEW_BUG_PAGE_IPS:
        f = open(sql,'rb')
        response = FileResponse(f)
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename="{}"'.format(file_name)
        return response
    else:
        return HttpResponseRedirect('/')

def download_backup_image(R):
    client_ip = R.META['HTTP_X_FORWARDED_FOR']
    d = timedelta(days = 1)
    sunday = datetime.datetime.today()
    while sunday.weekday() != 6:
        sunday = sunday - d
    date = sunday.strftime('%Y%m%d')
    file_name = 'image_backup.zip'
    sql =  '/backup.raid/'+file_name
    if client_ip in CAN_VIEW_BUG_PAGE_IPS:
        f = open(sql,'rb')
        response = FileResponse(f)
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename="{}"'.format(file_name)
        return response
    else:
        return HttpResponseRedirect('/')
        
def download_backup_pccmating(R):
    client_ip = R.META['REMOTE_ADDR']
    file_name = 'pccmating_project_backup.sql'
    image_file = '/var/www/fes/apps/fishuser/upload/'+file_name
    #if client_ip in CAN_VIEW_BUG_PAGE_IPS:
    f = open(image_file,'rb')
    response = FileResponse(f)
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="{}"'.format(file_name)
    return response
    #else:
        #return HttpResponseRedirect('/')

@login_required
def index(R):
    t = get_template(os.path.join('fishuser', 'zh-tw', 'base.html'))
    html = t.render(RequestContext(R,{
        'toppage_name': u'工程管考系統',
        'subpage_name': u'計畫列表',
        }))
    return HttpResponse(html)
    

#登入
@needNotLogin
def login(R, session=None, wronglogin=False):
    try: session = Session.objects.all()[0]
    except IndexError: session = None

    user = R.user

    if 'login' == R.POST.get('submit', None):
        username = R.POST.get('username', '').lower()
        password = R.POST.get('password', '').lower()
        verifycode_id = R.POST.get('verifycode_id', 0)
        verify = R.POST.get('verify', 0)
        if not verifyOK(verifycode_id, verify): 
            return HttpResponse(json.dumps({'status': False, 'message': u'圖片數字不正確'}))

        user = auth.authenticate(username=username, password=password)

        if not user:
            try:
                wronglogin = WrongLogin.objects.get(session=session)
            except:
                wronglogin = False
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
            if R.META.has_key('http_x_forwarded_for'): ip = R.META['http_x_forwarded_for']
            elif R.META.has_key('HTTP_X_FORWARDED_FOR'): ip = R.META['HTTP_X_FORWARDED_FOR']
            else: ip = R.META['REMOTE_ADDR']

            lh = LoginHistory(user=user, ip=ip, datetime=NOW())
            lh.save()

            if up.need_resetpassword:
                return HttpResponse(json.dumps({'status': True, 'next': '/fishuser/reset_password/', 'user_id': up.user.id, 'message': u'第一次登入或是索取密碼信後，請修改密碼'}))
            else:
                return HttpResponse(json.dumps({'status': True, 'user_id': up.user.id}))

    ens = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    for i in xrange(len(ens)):
        ens[i] += '_account'
    account_users = User.objects.filter(username__in=ens)


    t = get_template(os.path.join('fishuser', 'zh-tw', 'login.html'))
    html = t.render(RequestContext(R,{
            'account_users': account_users,
            'next': R.GET.get('next', '/fishuser/user_profile/'),
        }))
    return HttpResponse(html)


#註冊帳號
def register_user(R):
    try:
        user = User.objects.get(username = R.POST.get('username', None))
        return HttpResponse(json.dumps({'status': False, 'message': '註冊失敗，此『%s』帳號已被申請使用。' % user.username}))
    except:
        new_user = User(
            username = R.POST.get('username', None),
            last_name = R.POST.get('last_name', None),
            first_name = R.POST.get('first_name', None),
            email = R.POST.get('email', 'None'),
            is_active = True,
        )
        password = R.POST.get('password', None)
        new_user.set_password(password)
        new_user.save()
        up = UserProfile(
            user = new_user,
            title = R.POST.get('title', ''),
            phone = R.POST.get('phone', ''),
            fax = R.POST.get('fax', ''),
            group = Group.objects.get(name='註冊'),
            is_satisfaction = 0,#更新
            system_memo = '',
        )
        new_user.groups.add(Group.objects.get(name='註冊'))
        up.save()

        return HttpResponse(json.dumps({'status': True}))


#登出
def logout(R):
    user = UserProfile.objects.get(user_id = R.user.id)
    user.is_satisfaction = R.POST.get('is_satisfaction', False)
    if user.is_satisfaction:
        user.project_score = R.POST.get('project_score', '')
        user.app_score = R.POST.get('app_score', '')
        user.all_score = R.POST.get('all_score', '')
        user.system_memo = R.POST.get('system_memo', '')
        user.save()
    auth.logout(R)
    response = HttpResponseRedirect('/')
    return response

#滿意度調查表
def satisfaction(R):
    user = UserProfile.objects.get(user_id = R.user.id)
    user.is_satisfaction = R.POST.get('is_satisfaction', False)
    user.project_score = R.POST.get('project_score', '')
    user.app_score = R.POST.get('app_score', '')
    user.all_score = R.POST.get('all_score', '')
    user.system_memo = R.POST.get('system_memo', '')
    user.save()
    return HttpResponse(status=200)

#滿意度頁面
@login_required
def satisfaction_page(R):
    t = get_template(os.path.join('fishuser', 'zh-tw', 'satisfaction_page.html'))
    html = t.render(RequestContext(R,{
            'user': R.user,
            'toppage_name': u'遠端管理系統',
        }))
    return HttpResponse(html)

#個人基本資料頁面
@login_required
def user_profile(R):
    logins = R.user.loginhistory_set.all().order_by('-datetime')
    warning_msg = ''
    if R.GET.get('need_check_ip'):
        try:
            if logins[0].ip != logins[1].ip and logins[0].datetime.date() == NOW().date():
                warning_msg = u'您上次使用的IP為%s(%s)，與本次登入不一致，請確認是否為本人登入。' % (logins[1].ip, logins[1].datetime)
        except:pass

    system_infos = SystemInformation.objects.filter(start_date__lte=TODAY()).order_by('-start_date')[:10]
    try:
        system_login = SystemInformation.objects.filter(on_login_page=True).order_by('-start_date')[0].title
    except:
        system_login = False

    t = get_template(os.path.join('fishuser', 'zh-tw', 'user_profile.html'))
    html = t.render(RequestContext(R,{
            'user': R.user,
            'system_infos': system_infos,
            'system_login': system_login,
            'logins': logins[:15] if logins.count() >= 15 else logins,
            'warning_msg': warning_msg,
            'toppage_name': u'遠端管理系統',
        }))
    return HttpResponse(html)


#個人自行修改密碼
@login_required
def reset_password(R):
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
            up = user.user_profile
            up.need_resetpassword = False
            up.save()
            return HttpResponse(json.dumps({'status': True}))

    t = get_template(os.path.join('fishuser', 'zh-tw', 'reset_password.html'))
    html = t.render(RequestContext(R,{
            'user': R.user,
            'toppage_name': u'遠端管理系統',
        }))
    return HttpResponse(html)


#管理員自行修改密碼
@login_required
def account_reset_password(R):
    if not R.user.is_staff and not R.user.has_perm('fishuser.top_menu_account'):
        return HttpResponseRedirect('/')
        
    user = User.objects.get(id=R.POST.get('user_id', None))
    password = R.POST.get('password', None)
    if len(password) < 32:
        #TODO 須制作 log 處理，因為發生這種狀態，表示系統可能遭受不明現象的攻擊
        return HttpResponse(json.dumps({'status': False, 'message': '密碼格式非常有問題'}))
    elif md5password(user.username) == password:
        return HttpResponse(json.dumps({'status': False, 'message': '密碼不可以跟帳號一樣'}))
    else:
        user.set_password(password)
        user.save()
        up = user.user_profile
        up.need_resetpassword = False
        up.save()
        return HttpResponse(json.dumps({'status': True}))


#寄送重新設定密碼信
def send_reset_password_email(R):
    try:
        user = User.objects.get(username=R.POST.get('username', None))
    except:
        return HttpResponse(json.dumps({'status': False, 'msg': u'查無此帳號!!!'}))

    codes = [0,1,2,3,4,5,6,7,8,9, 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']

    try: 
        reset = ResetPasswordUser.objects.get(user=user, time__gte=NOW()-datetime.timedelta(3))
        code = reset.code
    except:
        ResetPasswordUser.objects.filter(user=user).delete()
        code = ''
        for i in xrange(128):
            code += str(codes[random.randint(0, len(codes)-1)])
        reset = ResetPasswordUser(
            user = user,
            code = code,
            time = NOW(),
            )
        reset.save()

    smtpserver = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
    # smtpserver.ehlo()
    # smtpserver.starttls()
    smtpserver.ehlo()
    #登入系統
    smtpserver.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)

    #寄件人資訊
    fromaddr = settings.EMAIL_HOST_USER

    #收件人列表，格式為list即可
    toaddrs = [user.email]
    # toaddrs = [u'johnisacoolboy@gmail.com']

    msg = MIMEMultipart()
    msg['From']=fromaddr
    msg['To']=COMMASPACE.join(toaddrs)
    msg['Date']=formatdate(localtime=True)
    msg['Subject']=u'漁業署FES工程管理-重新設定密碼'

    #你要寫的內容
    info = u''
    info += u'<br>您好，這是「漁業工程管理系統FES」發出的密碼重新設定確認信，請勿回信<br>'
    info += u'<br>請點擊以下連結重新設定密碼<br>'
    info += u'<br>https://fes.fa.gov.tw/fishuser/email_reset_password/%s/<br>' % code
    info += u'<br>此連結可使用72小時，重新設定密碼後此連結將自動失效，請勿洩漏連結資訊給其他人<br>'

    def containsnonasciicharacters(str):
        return not all(ord(c) < 128 for c in str)

    if containsnonasciicharacters(info):
        htmltext = MIMEText(info.encode('utf-8', 'replace'), 'html','utf-8')
    else:
        htmltext = MIMEText(info, 'html')

    msg.attach(htmltext)

    smtpserver.sendmail(fromaddr, toaddrs, msg.as_string())

    #記得要登出
    smtpserver.quit()
    return HttpResponse(json.dumps({'status': True, 'msg': u'密碼設定信件已寄到您帳號所屬的Email!!!'}))


#Email重新設定密碼頁面
@csrf_exempt
def email_reset_password(R, **kw):
    try:
        reset = ResetPasswordUser.objects.get(code=kw['code'], time__gte=NOW()-datetime.timedelta(3))
    except:
        if R.POST.get('submit', '') == 'email_reset_password':
            try:
                reset = ResetPasswordUser.objects.get(code=R.POST.get('code', ''))
                user = reset.user
                user.set_password(R.POST.get('password', None))
                user.save()
                up = user.user_profile
                up.need_resetpassword = False
                up.save()
                reset.delete()
                return HttpResponse(json.dumps({'status': True}))
            except:
                return HttpResponseRedirect('/')
        else:
            return HttpResponseRedirect('/')

    t = get_template(os.path.join('fishuser', 'zh-tw', 'email_reset_password.html'))
    html = t.render(RequestContext(R,{
            'reset': reset,
        }))
    return HttpResponse(html)


#帳號搜尋
@login_required
def account_search(R):
    if not R.user.has_perm('fishuser.top_menu_account'):
        return HttpResponseRedirect('/')

    new_units = LOAD_UNITS()[:]

    if 9 in [g.id for g in R.user.groups.all()]:
        can_use_group_ids = [1,3,4,5,6,7,8,9,10,26,27,28,30,31]
    elif 10 in [g.id for g in R.user.groups.all()]:
        can_use_group_ids = [1,3,10]
        unit = R.user.user_profile.unit
        tmp = []
        for i in new_units:
            if i.place == unit.place:
                tmp.append(i)
        new_units = tmp
    elif R.user.is_staff:
        can_use_group_ids = [g.id for g in Group.objects.all()]
    elif R.user.is_superuser:
        can_use_group_ids = [g.id for g in Group.objects.all()]

    groups = Group.objects.filter(id__in=can_use_group_ids).order_by('-name')

    t = get_template(os.path.join('fishuser', 'zh-tw', 'account_search.html'))
    html = t.render(RequestContext(R,{
            'user': R.user,
            'units': new_units,
            'groups': groups,
            'toppage_name': u'帳號管理',
            'subpage_name': u'帳號搜尋',
        }))
    return HttpResponse(html)


#用來轉換帳戶用的
@login_required
def updateStuffToUser(R):
    username = R.POST.get('username', None)

    if not R.user.is_staff:
        return HttpResponse(json.write({'status': False, 'message': '你沒有權限轉換成 %s 。' % username}))
    try:
        if User.objects.get(username=username).is_staff:
            return HttpResponse(json.write({'status': False, 'message': '你不可以轉換成其他的系統管理員( %s )' % username}))
    except:
        pass

    original_user = R.user

    try:
        user = auth.authenticate(username=username, password=u"^!@#$%^&*('給admin轉帳號用')")
        if user:
            auth.login(R, user)
            return HttpResponse(json.write({'status': True}))
        else:
            return HttpResponse(json.write({'status': False, 'message': '%s 不存在。' % username}))

    except:
        return HttpResponse(json.write({'status': False, 'message': '轉 %s 有問題' % user.username}))


#新增移除群組使用
@login_required
def add_or_remove_user_group(R):
    if not R.user.has_perm('fishuser.top_menu_account'):
        return HttpResponseRedirect('/')

    user = User.objects.get(id=R.POST.get('user_id', 0))
    group = Group.objects.get(id=R.POST.get('group_id', 0))

    if R.POST.get('active', 'remove') == 'remove':
        user.groups.remove(group)
    else:
        user.groups.add(group)

    return HttpResponse(json.dumps({'status': True, 'group_id': group.id, 'group_name': group.name}))


#新增帳號
@login_required
def account_create(R):
    if not R.user.has_perm('fishuser.top_menu_account'):
        return HttpResponseRedirect('/')

    city_title = ''

    new_units = LOAD_UNITS()[:]

    if 9 in [g.id for g in R.user.groups.all()]:
        can_use_group_ids = [1,3,4,5,6,7,8,9,10,26,27,28,30]
    elif 10 in [g.id for g in R.user.groups.all()]:
        can_use_group_ids = [1,3,10]
        unit = R.user.user_profile.unit
        tmp = []
        for i in new_units:
            if i.place == unit.place:
                tmp.append(i)
        new_units = tmp
        city_title = R.user.username[:2]
    elif R.user.is_staff:
        can_use_group_ids = [g.id for g in Group.objects.all()]

    groups = Group.objects.filter(id__in=can_use_group_ids).order_by('-name')
    if 'creatUser' == R.POST.get('submit', ''):
        if R.POST.get('username','')[1] == '_':
            return HttpResponse(json.write({'status': False, 'message': '帳號第二個字元不可為"_"'}))
        try:
            u = User.objects.get(username=(city_title+R.POST.get('username','')))
            return HttpResponse(json.write({'status': False, 'message': '新增失敗，此帳號以被『%s』同仁使用' % u.user_profile.rName()}))
        except:
            u = User(
                    username = (city_title+R.POST.get('username','').lower()),
                    last_name = R.POST.get('last_name', None),
                    first_name = R.POST.get('first_name', None),
                    email = R.POST.get('email', 'None'),
                    last_login = NOW(), 
                    date_joined = NOW(),
                    is_staff = False,
                    )
            if 'True' == R.POST.get('is_active', None):
                u.is_active = True
            else:
                u.is_active = False
            password = R.POST.get('password', None)
            u.set_password(password)
            u.save()
            u.groups.add(Group.objects.get(id=R.POST.get('group', '')))

            up = UserProfile(user=u, is_satisfaction = 0, system_memo = '',)
            up.title = R.POST.get('title', '')
            up.phone = R.POST.get('phone', '')
            up.fax = R.POST.get('fax', '')
            up.group = Group.objects.get(id=R.POST.get('group', ''))
            up.unit = Unit.objects.get(id=R.POST.get('unit', ''))
            up.save()
            return HttpResponse(json.write({'status': True, 'username': u.username}))

    t = get_template(os.path.join('fishuser', 'zh-tw', 'account_create.html'))
    html = t.render(RequestContext(R,{
            'user': R.user,
            'units': new_units,
            'groups': groups,
            'city_title': city_title,
            'toppage_name': u'帳號管理',
            'subpage_name': u'創新帳號',
        }))
    return HttpResponse(html)


#叮催系統帳號管理  -  各縣市政府連絡窗口名單列表
@login_required
def email_list(R):
    if not R.user.has_perm('fishuser.top_menu_account'):
        return HttpResponseRedirect('/')

    users = EmailList.objects.all().order_by('place', 'name')
    places = [TAIWAN] + list(Place.objects.filter(uplevel=TAIWAN).order_by('id'))
    t = get_template(os.path.join('fishuser', 'zh-tw', 'account_email_list.html'))
    html = t.render(RequestContext(R,{
            'user': R.user,
            'users': users,
            'places': places,
            'toppage_name': u'帳號管理',
            'subpage_name': u'叮催系統帳號管理',
        }))

    return HttpResponse(html)


#叮催系統帳號管理  -  叮催資訊
def email_list_info(R):
    if R.META['REMOTE_ADDR'] not in CAN_VIEW_BUG_PAGE_IPS:
        return HttpResponseRedirect('/')

    place_id = R.GET.get('place_id', '1')
    try:
        place = Place.objects.get(id=place_id)
    except:
        place = None
    mail_lists = EmailList.objects.filter(place=place)
    countychasetime = CountyChaseTime.objects.all().order_by('-id')[0]
    countychasetime.time = CountyChaseTime.objects.all().count()
    countychasetime.pastDay = (datetime.date.today() - countychasetime.chase_date).days
    checks = []
    not_checks = []
    not_in_frcm = []
    no_contractors = []
    no_inspectors = []
    if not mail_lists:
        t = get_template(os.path.join('fishuser', 'email_info.html'))
        html = t.render(Context({}))
    else:
        projects = CountyChaseProjectOneToMany.objects.filter(countychasetime=countychasetime).order_by('project__place', 'project__year')
        frcm_ids = []

        for i in projects:
            if FRCMUserGroup.objects.filter(project__id=i.project.id).count() != 0:
                frcm_ids.append(i.project.id)
        if place != TAIWAN:
            projects = projects.filter(project__place=place).exclude(project__undertake_type__value='自辦')
        else:
            projects = projects.filter(project__undertake_type__value='自辦').order_by('project__place')

        no_contractors = []
        no_inspectors = []
        for i in projects.filter(project__id__in=frcm_ids):
            if not FRCMUserGroup.objects.filter(project=i.project, group__name=u'營造廠商'):
                i.project.frcmuser = FRCMUserGroup.objects.get(project=i.project, group__name__in=['負責主辦工程師', '自辦主辦工程師']).user
                no_contractors.append(i)
            if not FRCMUserGroup.objects.filter(project=i.project, group__name=u'監造廠商', project__frcm_inspector_type__value=u'委外監造'):
                i.project.frcmuser = FRCMUserGroup.objects.get(project=i.project, group__name__in=['負責主辦工程師', '自辦主辦工程師']).user
                no_inspectors.append(i)

        checks = []
        not_checks = []
        not_in_frcm = []

        temp = projects.filter(check=True)
        for i in temp:
            if i.schedul_progress_percent > i.actual_progress_percent:
                i.project.frcmuser = FRCMUserGroup.objects.get(project=i.project, group__name__in=['負責主辦工程師', '自辦主辦工程師']).user
                checks.append(i)
        not_checks = projects.filter(check=False, project__id__in=frcm_ids)
        for i in not_checks:
            i.project.frcmuser = FRCMUserGroup.objects.get(project=i.project, group__name__in=['負責主辦工程師', '自辦主辦工程師']).user
        not_in_frcm = projects.filter(complete=False).exclude(project__id__in=frcm_ids)
        for i in not_in_frcm:
            i.project.frcmuser = ''

    #先遮掉寄件人的信箱資訊
    for i in mail_lists:
        i.last_name = i.name[0]

    t = get_template(os.path.join('fishuser', 'email_info.html'))
    html_body = t.render(Context({
        'mail_lists': mail_lists,
        'place': place,
        'countychasetime': countychasetime,
        'not_checks': not_checks,
        'not_in_frcm': not_in_frcm,
        'checks': checks,
        'no_contractors': no_contractors,
        'no_inspectors': no_inspectors,
    }))

    type = R.GET.get('type', '')
    if type in ['json', 'xml']:
        ac = AESCrypto()
        d = {
            'password': base64.b64encode(_public_encypt(ac.secret, R.GET.get('public_key', ''))[0]),
            'emails': [ac.EncodeAES(str(u'%s <%s>' % (e.name, e.email))) for e in mail_lists],
            'title': ac.EncodeAES(str(u'(%s)漁業工程管理系統(FES)即時預警通知資訊' % place.name)),
            'body': ac.EncodeAES(str(html_body)),
        }
        if type == 'json':
            html = json.dumps(d)
        else:
            raise Exception(u'尚未實作')
    else:
        html = u'''<html>
    <head profile="http://gmpg.org/xfn/11">
        <meta http-equiv="content-type" content="text/html; charset=utf-8" />
        <title>漁業工程管理系統-盯催信</title>
    </head>
    <body id="id_body">%s</body></html>
        ''' % html_body
        html = re.sub(u'([0-9][0-9]+|負責人：[^\)<]+)', '*', html)
    return HttpResponse(html)


#查核系統頁面- 使用崁入的方式
@login_required
def auditing_statistics(R):
    if not R.user.has_perm('fishuser.top_menu_auditing_system'):
        return HttpResponseRedirect('/')

    t = get_template(os.path.join('fishuser', 'zh-tw', 'auditing_statistics.html'))
    html = t.render(RequestContext(R,{
            'toppage_name': u'查核系統',
        }))

    return HttpResponse(html)


#使用查核系統
@login_required
@checkAuthority
def Show_Auditing_Statistics(R, project, right_type_value=u'使用查核系統'):

    t = get_template(os.path.join('fishuser', 'zh-tw', 'auditing_statistics.html'))
    html = t.render(RequestContext(R,{
            'user': R.user,
            'toppage_name': u'查核系統',
        }))
    return HttpResponse(html)



#測試寄信
def email_to_john(R):
    smtpserver = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
    # smtpserver.ehlo()
    # smtpserver.starttls()
    smtpserver.ehlo()
    #登入系統
    smtpserver.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)

    #寄件人資訊
    fromaddr = settings.EMAIL_HOST_USER

    #收件人列表，格式為list即可
    toaddrs = [u'johnisacoolboy@gmail.com']

    msg = MIMEMultipart()
    msg['From']=fromaddr
    msg['To']=COMMASPACE.join(toaddrs)
    msg['Date']=formatdate(localtime=True)
    msg['Subject']=u'漁業署FES工程管理-測試寄信'

    #你要寫的內容
    info = u'<br>測試內容<br>'

    def containsnonasciicharacters(str):
        return not all(ord(c) < 128 for c in str)

    if containsnonasciicharacters(info):
        htmltext = MIMEText(info.encode('utf-8', 'replace'), 'html','utf-8')
    else:
        htmltext = MIMEText(info, 'html')

    msg.attach(htmltext)

    smtpserver.sendmail(fromaddr, toaddrs, msg.as_string())

    #記得要登出
    smtpserver.quit()

    print 'Good finish'
    return HttpResponseRedirect('/')


#寄信給所有FRCMUserGroup人員，告知相關工程資訊，目前設定為僅寄這兩年的資料
def email_to_frcmuser(R):
    if R.POST['code'] != u'32kmDWA1!@$DAS': return False
    import smtplib
    from dailyreport.models import Report

    projects = Project.objects.filter(deleter=None, year__in=[this_year, this_year-1])

    need_email_users = []
    for i in FRCMUserGroup.objects.filter(project__in=projects):
        if i.user.email not in need_email_users:
            need_email_users.append(i.user.email)

    for u_email in need_email_users:
        #你要寫的內容
        info = u''
        info += u'\n您好，這是「漁業工程管理系統FES」發出的每月填報進度彙整通知信，請勿回信'
        info += u'\n\n以下為您所相關的工程資訊：'

        projects = []
        for frcm_p in FRCMUserGroup.objects.filter(user__email=u_email):
            if frcm_p.project not in projects: projects.append(frcm_p.project)
        for pn, p in enumerate(projects):
            info += u'\n\n\n%s. 工程：%s年-%s' % (pn+1, p.year, p.name)
            info += u'\n網址路徑：https://fes.fa.gov.tw/frcm/project_profile/%s/' % (p.id)
            info += u'\n工程品質相片上傳張數：%s張' % p.get_images_count()
            try:
                engprofile = p.dailyreport_engprofile.get()
                if not engprofile.start_date:
                    info += u'\n尚未使用日報表系統'
                else:
                    info += u'\n日報表系統設定'
                    info += u'\n預定進度：%s' % engprofile.design_percent
                    wordingdates = engprofile.readWorkingDate()
                    if wordingdates[-1] > TODAY():
                        defined_finish_date = TODAY()
                    else:
                        defined_finish_date = wordingdates[-1]
                    need_filled = len(engprofile.readWorkingDate(defined_finish_date=defined_finish_date)) - 1
                    i_report = Report.objects.filter(project=p, date__lte=TODAY(), inspector_check=True).order_by('-date')
                    c_report = Report.objects.filter(project=p, date__lte=TODAY(), contractor_check=True).order_by('-date')
                    i_filled = i_report.count()
                    i_last_day = i_report[0].date if i_report else u'無'
                    c_filled = c_report.count()
                    c_last_day = c_report[0].date if c_report else u'無'
                    info += u'\n監造填寫實際進度：%s，最後填寫日期：%s，尚未填寫天數：%s天' % (engprofile.act_inspector_percent, i_last_day, need_filled - i_filled)
                    info += u'\n施工填寫實際進度：%s，最後填寫日期：%s，尚未填寫天數：%s天' % (engprofile.act_contractor_percent, c_last_day, need_filled - c_filled)
            except:
                info += u'\n尚未使用日報表系統'

        msg = mail.EmailMessage(u'漁業工程管理系統FES-每月填報進度彙整通知', info, u'FES填報進度彙整通知 <fes@ms1.fa.gov.tw>', [u_email])
        msg.content_subtype = "html"  # Main content is now text/html
        msg.send()

    print 'Good finish'
    return HttpResponseRedirect('/')


























#以下舊分頁-------------------------------------------------------------------------


# def rJSON(R, right_type_value=u'Ajax Request'):
#     submit = R.GET.get('submit', '')
#     if not submit: submit = R.POST.get('submit', '')

#     if 'rSelfUsername' == submit:
#         result = rSelfUsername(R)
#     elif 'deleteEmailListUser' == submit:
#         result = deleteEmailListUser(R)
#     elif 'addEmailListUser' == submit:
#         result = addEmailListUser(R)
#     elif 'checkBoxNeedEmail' == submit:
#         result = checkBoxNeedEmail(R)
#     elif 'BlurUpdateInfo' == submit:
#         result = BlurUpdateInfo(R)
#     else:
#         result = {'status': False, 'message': u'未指定方法'}

#     return HttpResponse(json.write(result))

# def BlurUpdateInfo(R):
#     row_id = R.POST.get('row_id')
#     field_name = R.POST.get('field_name')
#     table_name = R.POST.get('table_name')
#     value = R.POST.get('value')
#     return_value = value
#     return_value_ch = value
#     if table_name == 'EmailList':
#         row = EmailList.objects.get(id=row_id)

#     if field_name == 'place':
#         value = Place.objects.get(id=value)
#         return_value = value.id
#         return_value_ch = value.name

#     setattr(row, field_name, value)
#     row.save()
#     return {'status': True, 'return_value': return_value, 'return_value_ch': return_value_ch}


# def checkBoxNeedEmail(R):
#     row_id = R.POST.get('row_id')
#     row = EmailList.objects.get(id=row_id)
#     if row.need_email == True:
#         row.need_email = False
#     else:
#         row.need_email = True
#     row.save()
#     return {'status': True}

# def addEmailListUser(R):
#     row = EmailList(
#         name = '新增使用者'
#         )
#     row.save()
#     places = [TAIWAN] + list(Place.objects.filter(uplevel=TAIWAN).order_by('id'))
#     t = get_template(os.path.join('fishuser', 'email_account_tr.html'))
#     html = t.render(Context({'u': row, 'places': places}))
#     return {'status': True, 'html': html}

# def deleteEmailListUser(R):
#     row_id = R.POST.get('row_id')
#     row = EmailList.objects.get(id=row_id)
#     row.delete()
#     return {'status': True}

# @login_required
# def rSelfUsername(R):
#     return R.user.user_profile.rJsonInHtml()

# def tmp_redirect(myFunc):
#     def innerFunc(*args, **kw):
#         return HttpResponseRedirect('/u/')
#         return myFunc(*args, **kw)
#     return innerFunc


# def readAccountList(R):
#     ens = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
#     for i in xrange(len(ens)): ens[i] += '_account'
#     users = User.objects.filter(username__in=ens)

#     t = get_template(os.path.join('fishuser', 'read_account_list.html'))
#     html = t.render(Context({'users': users}))
#     return HttpResponse(html)


# def checkWrongLoginTime(myFunc):
#     def innerFunc(*args, **kw):
#         R = args[0]
#         try:
#             session = Session.objects.get(pk=R.COOKIES.get('sessionid', 'None'))
#             wronglogin = WrongLogin.objects.get(session=session)
#             if not wronglogin.rTypeStatus():
#                 kw['refuse'] = True
#                 return HttpResponse(json.write({'status': False,
#                 'message': '登入錯誤次已達%s次，請稍待%s分鐘後，再行登入'
#                 % (WRONGLOGINTIMELIMIT, WRONGLOGINDURATION)}))
#         except Session.DoesNotExist:
#             session = Session.objects.all()[0] # 隨便先給一個 session instance
#             wronglogin = False
#         except WrongLogin.DoesNotExist:
#             wronglogin = False

#         kw['session'] = session
#         kw['wronglogin'] = wronglogin

#         return myFunc(*args, **kw)
#     return innerFunc


# def checkNeedEditPassword(myFunc):
#     def innerFunc(*args, **kw):
#         R = args[0]
#         up = R.user.user_profile
#         if up.need_resetpassword: return HttpResponseRedirect('/u/eps/')
#         return myFunc(*args, **kw)
#     return login_required(innerFunc)

# def _checkUsernameFormat(username):
#     if re.match('^[0-9]{10}$', username):
#         return username
#     elif re.match('^[0-9]+-[0-9]+(#[0-9]+)?$', username):
#         return username
#     else:
#         return False

# def _checkEmailFormat(email):
#     if re.match('^[a-z0-9][-a-z0-9\.]*@([a-z0-9-]+\.)+[a-z]+$', email):
#         return email
#     else:
#         return False

# def _checkCompanyNoFormat(no):
#     #TODO 未驗證公司統編
#     return no

# def transfer(R):
#     t = get_template(os.path.join('fishuser', 'transfer.html'))
#     html = t.render(Context({}))
#     return HttpResponse(html)

# @login_required
# def getMenu(R):
#     #這是計算他有哪些選單可以按

#     user, DATA = R.user, readDATA(R)
#     url = DATA.get('url', '').split('/')
#     # /u/vp/ => ['','u','vp']
#     menu = '<div id="navigation"><ul>'
#     menu2 = ''
#     if  url[1] == u'u' and url[2] != u'account': menu += u'<li><a href="/u/" class="active">個人基本資料</a></li>'
#     else: menu += u'<li><a href="/u/">個人基本資料</a></li>'

#     #管考的選單
#     if _ca(user=user, project='', project_id=0, right_type_value=u'menu1_工程管考系統') and user.username[1] != u'_' or user.is_staff:
#         if  url[1] == u'project':
#             menu += u'<li><a href="/project/search/" class="active">工程管考系統</a></li>'
#             menu2 += u'</ul></div><div id="navigation2"><ul>'
#             if _ca(user=user, project='', project_id=0, right_type_value=u'menu2_搜尋管考工程'):
#                 if url[2] == u'search':menu2 += u'<li><a href="/project/search/" class="active">搜尋管考工程</a></li>'
#                 else:menu2 += u'<li><a href="/project/search/">搜尋管考工程</a></li>'
#             if _ca(user=user, project='', project_id=0, right_type_value=u'menu2_計畫列表'):
#                 if url[2] == u'replan':menu2 += u'<li><a href="/project/replan/1/" class="active">計畫列表</a></li>'
#                 else:menu2 += u'<li><a href="/project/replan/1/">計畫列表</a></li>'
# #            做不完，遮起來。尚待重整。
# #            if _ca(user=user, project='', project_id=0, right_type_value=u'menu2_預算統整表'):
# #                if url[2] == u'rebudget':menu2 += u'<li><a href="/project/rebudget/" class="active">預算統整表</a></li>'
# #                else:menu2 += u'<li><a href="/project/rebudget/">預算統整表</a></li>'
#             if _ca(user=user, project='', project_id=0, right_type_value=u'menu2_新增工程案'):
#                 if url[2] == u'draft_project':menu2 += u'<li><a href="/project/draft_project/fishery/" class="active">草稿匣</a></li>'
#                 else:menu2 += u'<li><a href="/project/draft_project/fishery/">草稿匣</a></li>'
#             if _ca(user=user, project='', project_id=0, right_type_value=u'menu2_新增工程案'):
#                 if url[2] == u'addproject':menu2 += u'<li><a href="/project/addproject/" class="active">新增工程案</a></li>'
#                 else:menu2 += u'<li><a href="/project/addproject/">新增工程案</a></li>'
#             if _ca(user=user, project='', project_id=0, right_type_value=u'menu2_縣市進度追蹤'):
#                 if url[2] == u'county_chase':menu2 += u'<li><a href="/project/county_chase/" class="active">縣市進度追蹤</a></li>'
#                 else:menu2 += u'<li><a href="/project/county_chase/">縣市進度追蹤</a></li>'
# #            暫時閹割，若真有需要再行重整
# #            if _ca(user=user, project='', project_id=0, right_type_value=u'menu2_各式統計報表'):
# #                if url[2] == u'makestatistics':menu2 += u'<li><a href="/project/makestatistics/select_year:'+str(TODAY().year-1911)+'/type_id:1/select_unit:0/select_undertake_type:0/select_fishingport:0/" class="active">各式統計報表</a></li>'
# #                else:menu2 += u'<li><a href="/project/makestatistics/select_year:'+str(TODAY().year-1911)+'/type_id:1/select_unit:0/select_undertake_type:0/select_fishingport:0/">各式統計報表</a></li>'
# #            if _ca(user=user, project='', project_id=0, right_type_value=u'menu2_匯出報表'):
# #                if url[2] == u'makedownloadfile': menu2 += u'<li title="匯出制式報表"><a href="/project/makedownloadfile/" class="active">匯出制式報表</a></li>'
# #                else: menu2 += u'<li title="匯出制式報表"><a href="/project/makedownloadfile/">匯出制式報表</a></li>'

# 	    #TODO:WTF ACCOUTING 將被移除
#       #      if url[2] == u'accouting':menu2 += u'<li><a href="/harbor/accouting/?go=/media/accouting/index.html" class="active">會計系統資料</a></li>'
#       #      else:menu2 += u'<li><a href="/harbor/accouting/?go=/media/accouting/index.html">會計系統資料</a></li>'

# 	    menu2 += u'</ul></div>'
#         else:
#             menu += u'<li><a href="/project/search/">工程管考系統</a></li>'
#     #遠端的選單
#     if _ca(user=user, project='', project_id=0, right_type_value=u'menu1_遠端管理系統'):
#         if  url[1] == u'frcm':
#             menu += u'<li><a href="/frcm/" class="active">遠端管理系統</a></li>'
#             menu2 += u'</ul></div><div id="navigation2"><ul>'
#             if u'_' in user.username and not user.is_staff:
#                 if _ca(user=user, project='', project_id=0, right_type_value=u'menu2_縣市進度追蹤'):
#                     if url[2] == u'county_chase':menu2 += u'<li><a href="/frcm/county_chase/" class="active">縣市進度追蹤</a></li>'
#                     else:menu2 += u'<li><a href="/frcm/county_chase/">縣市進度追蹤</a></li>'
#             if _ca(user=user, project='', project_id=0, right_type_value=u'menu2_我的工程'):
#                 if url[2] == u'':menu2 += u'<li><a href="/frcm/" class="active">我的工程</a></li>'
#                 else:menu2 += u'<li><a href="/frcm/">我的工程</a></li>'
#             if _ca(user=user, project='', project_id=0, right_type_value=u'menu2_匯入工程'):
#                 if url[2] == u'import':menu2 += u'<li><a href="/frcm/import/" class="active">匯入工程</a></li>'
#                 else:menu2 += u'<li><a href="/frcm/import/">匯入工程</a></li>'
#             if _ca(user=user, project='', project_id=0, right_type_value=u'menu2_認領工程'):
#                 if url[2] == u'getproject':menu2 += u'<li><a href="/frcm/getproject/" class="active">認領工程</a></li>'
#                 else:menu2 += u'<li><a href="/frcm/getproject/">認領工程</a></li>'
#             if _ca(user=user, project='', project_id=0, right_type_value=u'menu2_搜尋遠端工程'):
#                 if url[2] == u'search':menu2 += u'<li><a href="/frcm/search/" class="active">搜尋遠端工程</a></li>'
#                 else:menu2 += u'<li><a href="/frcm/search/">搜尋遠端工程</a></li>'
# #            if user.user_profile.group.id == 3 and u'漁業署' in user.user_profile.unit.fullname:
# #                if url[2] == u'search':menu2 += u'<li><a href="/frcm/search/" class="active">搜尋遠端工程</a></li>'
# #                else:menu2 += u'<li><a href="/frcm/search/">搜尋遠端工程</a></li>'
# #            print str(user)[1], user.user_profile.unit.fullname, u'<{---'
#             if _ca(user=user, project='', project_id=0, right_type_value=u'menu2_檔案管理系統'):
#                 glist = [i.group.name for i in FRCMUserGroup.objects.filter(user=user)]
#                 if glist:
#                     if url[2] == u'filems':menu2 += u'<li><a href="/frcm/filems/" class="active">檔案管理</a></li>'
#                     else:menu2 += u'<li><a href="/frcm/filems/">檔案管理</a></li>'
#                 elif user.user_profile.group.name != u'註冊':
#                     if url[2] == u'filems':menu2 += u'<li><a href="/frcm/filems/" class="active">檔案管理</a></li>'
#                     else:menu2 += u'<li><a href="/frcm/filems/">檔案管理</a></li>'
#             if _ca(user=user, project='', project_id=0, right_type_value=u'menu2_匯出報表'):
#                 if url[2] == u'add_draft':menu2 += u'<li><a href="/frcm/add_draft/" class="active">工程提案區</a></li>'
#                 else:menu2 += u'<li><a href="/frcm/add_draft/">工程提案區</a></li>'

#             menu2 += u'</ul></div>'
#         else:
#             menu += u'<li><a href="/frcm/">遠端管理系統</a></li>'

#     #查核系統的選單
#     if _ca(user=user, project='', project_id=0, right_type_value=u'menu1_工程查核系統') and user.username[1] != u'_':
#         if url[1] == u'auditing_statistics':
#             menu += u'<li><a href="/auditing_statistics/" class="active">查核系統</a></li>'
#         else:
#             menu += u'<li><a href="/auditing_statistics/">查核系統</a></li>'

#     #督導系統的選單
#     if _ca(user=user, project='', project_id=0, right_type_value=u'menu1_工程督導系統') and user.username[1] != u'_':
#         if url[1] == u'supervise':
#             menu += u'<li><a href="/supervise/search/" class="active">督導系統</a></li>'
#             menu2 += u'</ul></div><div id="navigation2"><ul>'
#             if _ca(user=user, project='', project_id=0, right_type_value=u'menu2_督導查詢') and user.username[1] != u'_':
#                 if url[2] == u'search':menu2 += u'<li><a href="/supervise/search/" class="active">查詢</a></li>'
#                 else:menu2 += u'<li><a href="/supervise/search/">查詢</a></li>'
#             if _ca(user=user, project='', project_id=0, right_type_value=u'menu2_督導統計表單') and user.username[1] != u'_':
#                 if url[2] == u'statistics_table':menu2 += u'<li><a href="/supervise/statistics_table/all/01/" class="active">統計表單</a></li>'
#                 else:menu2 += u'<li><a href="/supervise/statistics_table/all/01/">統計表單</a></li>'
#             if user.is_staff or Edit.objects.filter(user = R.user):
#                 if url[2] == u'creat':menu2 += u'<li><a href="/supervise/creat/" class="active">新增</a></li>'
#                 else:menu2 += u'<li><a href="/supervise/creat/">新增</a></li>'
#         else:
#             menu += u'<li><a href="/supervise/search/">督導系統</a></li>'

#     #漁港系統的選單
#     if _ca(user=user, project='', project_id=0, right_type_value=u'menu1_漁港資訊系統'):
#         if  url[1] == u'harbor':
#             menu += u'<li><a href="/harbor/" class="active">漁港資訊系統</a></li>'
#             menu2 += u'</ul></div><div id="navigation2"><ul>'
#             if _ca(user=user, project='', project_id=0, right_type_value=u'menu2_資訊主頁'):
#                 if url[2] == u'view':menu2 += u'<li><a href="/harbor/" class="active">資訊主頁</a></li>'
#                 else:menu2 += u'<li><a href="/harbor/">資訊主頁</a></li>'
#             if _ca(user=user, project='', project_id=0, right_type_value=u'menu2_漁港搜尋'):
#                 if url[2] == u'search':menu2 += u'<li><a href="/gis/" class="active" target="_blank">漁港搜尋</a></li>'
#                 else:menu2 += u'<li><a href="/gis/" target="_blank">漁港搜尋</a></li>'
#             if _ca(user=user, project='', project_id=0, right_type_value=u'menu2_漁港設施記錄'):
#                 if url[2] == u'installation':menu2 += u'<li><a href="/harbor/installation/" class="active">漁港設施記錄</a></li>'
#                 else:menu2 += u'<li><a href="/harbor/installation/">漁港設施記錄</a></li>'
#             if _ca(user=user, project='', project_id=0, right_type_value=u'menu2_資訊編輯'):
#                 if url[2] == u'editinfo':menu2 += u'<li><a href="/harbor/editinfo/" class="active">資訊編輯</a></li>'
#                 else:menu2 += u'<li><a href="/harbor/editinfo/">資訊編輯</a></li>'

#             if url[2] == u'live_webcam':menu2 += u'<li><a href="/harbor/live_webcam/" class="active">港區監控系統</a></li>'
#             else:menu2 += u'<li><a href="/harbor/live_webcam/">港區監控系統</a></li>'

#             if url[2] == u'replay':menu2 += u'<li><a href="/harbor/replay/" class="active">港區錄影系統</a></li>'
#             else:menu2 += u'<li><a href="/harbor/replay/">港區錄影系統</a></li>'

#             if url[2] == u'data_share':menu2 += u'<li><a href="/harbor/data_share/" class="active">資料交換區</a></li>'
#             else:menu2 += u'<li><a href="/harbor/data_share/">資料交換區</a></li>'
#             menu2 += u'</ul></div>'
#         else:
#             menu += u'<li><a href="/harbor/">漁港資訊系統</a></li>'
#     #帳號管理的選單
#     if _ca(user=user, project='', project_id=0, right_type_value=u'menu1_帳號管理') or user.is_staff:
#         if  url[1] == u'u' and url[2] == u'account':
#             menu += u'<li><a href="/u/account/" class="active">帳號管理</a></li>'
#         else:
#             menu += u'<li><a href="/u/account/">帳號管理</a></li>'

#     menu += menu2


#     return HttpResponse(json.write({'status': True, 'menu': menu}))

# # @needNotLogin
# # @checkWrongLoginTime
# # def login(R, session=None, wronglogin=False):
# #     try: session = Session.objects.all()[0]
# #     except IndexError: session = None

# #     user, now, DATA = R.user, NOW(), readDATA(R)

# #     if 'login' == DATA.get('submit', None):
# #         username = DATA.get('username', '').lower()
# #         password = DATA.get('password', '').lower()
# #         verifycode_id = DATA.get('verifycode_id', 0)
# #         verify = DATA.get('verify', 0)
# #         if not (DEBUG and verify=='skip'):
# #             if not verifyOK(verifycode_id, verify): return HttpResponse(json.write({'status': False, 'message': u'圖片數字不正確'}))
# #         user = auth.authenticate(username=username, password=password)
# #         if not user:
# #             try:
# #                 wronglogin = WrongLogin.objects.get(session=session)
# #             except:
# #                 wronglogin = False
# #             if wronglogin: wronglogin.times += 1
# #             else: wronglogin = WrongLogin(session=session, start_time=now)
# #             wronglogin.save()
# #             return HttpResponse(json.write({'status': False, 'message':
# #             '無此帳號 或是 密碼錯誤。已登入錯誤 %s 次' % wronglogin.times}))
# #         elif not user.is_active:
# #             return HttpResponse(json.write({'status': False, 'message': '此帳號已被停用'}))
# #         else:
# #             try: up = user.user_profile
# #             except UserProfile.DoesNotExist: up = UserProfile(user=user)
# #             auth.login(R, user)
# #             up.login += 1
# #             up.save()
# #             user.last_login = now
# #             user.save()

# #             lh = LoginHistory(user=user, ip=R.META['REMOTE_ADDR'], datetime=now)
# #             lh.save()

# #             if up.need_resetpassword:
# #                 return HttpResponse(json.write({'status': True, 'next': '/u/eps/', 'user_id': up.user.id,
# #                 'message': '第一次登入或是索取密碼信後，須修改密碼'}))
# #             else:
# #                 return HttpResponse(json.write({'status': True, 'user_id': up.user.id}))

# #     t = get_template(os.path.join('fishuser', 'login.html'))
# #     html = t.render(Context({'next': R.GET.get('next', '/fishuser/user_profile/')}))
# #     return HttpResponse(html)


# def SendLoginEmail(R):
#     now, DATA = NOW(), readDATA(R)
#     user = User.objects.get(id=DATA.get('user_id', ''))
#     try:
#         CencelLoginEmail.objects.get(user=user)
#     except:
#         content = '漁業署FES系統登入通知(http://fes.fa.gov.tw)：'
#         content += ('\n' + '登入帳號：' + user.username + '\n')
#         content += ('\n' + '登入時間：' + str(now) + '\n')
#         content += ('\n' + '登入電腦IP：' + str(R.META['REMOTE_ADDR']) + '\n')
#         content += ('\n' + '\n' + '此為登入安全性確認，由FES系統自動發出，請勿回信。')
#         content += ('\n' + '\n' + '(若要取消，請至FES系統，個人資訊頁面更改)。')

#         import smtplib
#         fromaddr = 'fes.gov@gmail.com'
#         toaddrs  = str(user.email)

#         # Add the From: and To: headers at the start!
#         msg = ("From: %s\r\nTo: %s\r\nSubject: %s\r\n" % (fromaddr, toaddrs, '漁業署FES系統登入安全性通知。'))
#         server = smtplib.SMTP('smtp.gmail.com',587) #port 465 or 587
#         server.ehlo()
#         server.starttls()
#         server.ehlo()
#         server.login('fes.gov@gmail.com','22855647')
# #            server.set_debuglevel(0)
#         server.sendmail(fromaddr, toaddrs, msg + content)
#         server.quit()

#     return HttpResponse('Ture')


# @login_required
# def readUserProfile(R):
#     t = get_template(os.path.join('fishuser', 'index.html'))
#     html = t.render(Context({'next': R.GET.get('next', '/fishuser/user_profile/')}))
#     return HttpResponse(html)

# @login_required
# @checkNeedEditPassword
# def viewProfile(R):
#     return HttpResponseRedirect(R.GET.get('next', '/fishuser/user_profile/'))
#     try:
#         up = R.user.user_profile
#     except:
#         up = UserProfile(user=R.user)
#         up.last_login = NOW()
#         up.group = Group.objects.get(name='主辦工程師')
#         up.login = 1
#         up.save()

#     try:
#         CencelLoginEmail.objects.get(user=up.user)
#         email = False
#     except:
#         email = True
#     t = get_template(os.path.join('fishuser', 'profile.html'))

#     html = t.render(RequestContext(R,{
#         'logins': R.user.loginhistory_set.all().order_by('-datetime')[0:10],
#         'email': email,
#         }))
#     return HttpResponse(html)

# @login_required
# def editProfile(R):
#     user, DATA = R.user, readDATA(R)
#     if 'editProfile' == DATA.get('submit', None):
#         last_name = DATA.get('last_name', None)
#         first_name = DATA.get('first_name', None)
#         email = _checkEmailFormat(DATA.get('email', 'None'))
#         title = DATA.get('title', '')
#         phone = DATA.get('phone', '')
#         fax = DATA.get('fax', '')

#         user.last_name = last_name
#         user.first_name = first_name
#         old_email = user.email
#         user.email = email
#         user.save()
#         up = UserProfile.objects.get(user=R.user)
#         up.title = title
#         old_phone = up.phone
#         up.phone = phone
#         up.fax = fax
#         up.save()

#         for i in Project.objects.filter(self_contacter_phone=old_phone):
#             i.self_contacter_phone = phone
#             i.save()
#         for i in Project.objects.filter(local_contacter_phone=old_phone):
#             i.local_contacter_phone = phone
#             i.save()
#         for i in Project.objects.filter(contractor_contacter_phone=old_phone):
#             i.contractor_contacter_phone = phone
#             i.save()
#         for i in Project.objects.filter(self_contacter_email=old_email):
#             i.self_contacter_email = email
#             i.save()
#         for i in Project.objects.filter(local_contacter_email=old_email):
#             i.local_contacter_email = email
#             i.save()
#         for i in Project.objects.filter(contractor_contacter_email=old_email):
#             i.contractor_contacter_email = email
#             i.save()

#         return HttpResponse(json.write({'status': True}))

#     t = get_template(os.path.join('fishuser', 'editprofile.html'))
#     html = t.render(RequestContext(R,{}))
#     return HttpResponse(html)

# @login_required
# def editPassword(R):
#     user, DATA = R.user, readDATA(R)
#     if 'editPassword' == DATA.get('submit', None):
#         password = DATA.get('password', None)
#         if not password:
#             return HttpResponse(json.write({'status': False, 'message': '未輸入新密碼'}))
#         else:
#             if len(password) < 32:
#                 #TODO 須制作 log 處理，因為發生這種狀態，表示系統可能遭受不明現象的攻擊
#                 return HttpResponse(json.write({'status': False, 'message': '密碼格式非常有問題'}))
#             elif md5password(user.username) == password:
#                 return HttpResponse(json.write({'status': False, 'message': '密碼不可以跟帳號一樣'}))
#             else:
#                 user.set_password(password)
#                 user.save()
#                 up = user.user_profile
#                 up.need_resetpassword = False
#                 up.save()
#                 return HttpResponse(json.write({'status': True}))

#     t = get_template(os.path.join('fishuser', 'editpassword.html'))
#     html = t.render(Context({}))
#     return HttpResponse(html)

# @login_required
# def getUserProfile(R):
#     if R.user.is_authenticated:
# #        if R.user.email.count('@') == 1: name = R.user.email
# #        else: name = R.user.user_profile.rName()
#         name = R.user.user_profile.rName() + '( ' + R.user.username + ' )'
#         if R.user.email.count('@') == 1: name += u'：' + R.user.email

#         userprofile = { 'name': name, 'username': R.user.username }
#     else:
#         userprofile = { 'name': '訪客', }
#     return nocache_response(HttpResponse(json.write(userprofile)))

# @login_required
# @checkAuthority
# def searchAccount(R, project, right_type_value=u'帳號管理'):
#     class searchForm(forms.Form):
#         username = forms.CharField(label='帳號', required=False)
#         name = forms.CharField(label='姓名', required=False)
#         email = forms.CharField(label='Email', required=False)
#         groups = [('','全部')] + [(group.id, group.name) for group in Group.objects.all()]
#         group = forms.ChoiceField(choices=groups, required=False, label='群組')
#         units = [('', '全部')]
#         for i in Unit.fish_city_menu.all():
#             units.append((i.id, i.name))
#             if i.uplevel and i.uplevel.name != '縣市政府':
#                 units.extend(
#                     [(j.id, '---'+j.name) for j in i.uplevel_subunit.all()]
#                 )
#         unit = forms.ChoiceField(choices=units, required=False, label='單位')

#     form = searchForm()

#     users_num = -1
#     users = []
#     querystring = ''
#     DATA = {}
#     for k, v in R.GET.items(): DATA[k] = v
#     for k, v in R.POST.items(): DATA[k] = v

#     if DATA.get('submit', None):
#         form = searchForm(DATA)
#         querystring = '&'.join(['%s=%s'%(k, v) for k, v in DATA.items() if k != 'page'])
#         users, users_num = _searchAccount(DATA, R.user)

#     t = get_template(os.path.join('fishuser', 'account.html'))
#     html = t.render(Context({
#         'user': R.user,
#         'form': form,
#         'users': users,
#         'page_list': makePageList(DATA.get('page', 1), users_num, NUMPERPAGE),
#         'querystring': querystring,
#         'users_num': users_num,
#     }))

#     return HttpResponse(html)


# def _searchAccount(DATA, user):
#     if user.user_profile.group.name == '縣市帳號管理員':
#         ids = []
#         for u in User.objects.all():
#             if u.username[0:2] == user.username[0:2]: ids.append(u.id)
#         result = UserProfile.objects.filter(user__id__in=ids)
#     else:
#         result = UserProfile.objects.all()

#     if DATA.get('username', None) != '':
#         result = result.filter(user__username__contains=DATA.get('username', None).lower())

#     if DATA.get('email', None) != '':
#         result = result.filter(user__email__contains=DATA.get('email', None).lower())

#     if DATA.get('name', None) != '':
#         name_str = unicode(DATA.get('name', None))
#         if len(name_str) == 3:
#             last_name = name_str[0]
#             first_name = name_str[1:3]
#             result = result.filter((Q(user__last_name__startswith=last_name)&Q(user__first_name__contains=first_name))|Q(user__first_name__contains=name_str))
#         elif len(name_str) == 2:
#             last_name = name_str[0]
#             first_name = name_str[1]
#             result = result.filter((Q(user__last_name__startswith=last_name)&Q(user__first_name__contains=first_name))|Q(user__last_name=name_str)|Q(user__first_name=name_str))
#         elif len(name_str) == 1:
#             result = result.filter(Q(user__last_name__contains=name_str)|Q(user__first_name__contains=name_str))
#         else:
#             last_name = name_str[0]
#             first_name = name_str[-2:]
#             result = result.filter(user__last_name__contains=last_name, user__first_name__contains=first_name)

#     if DATA.get('group', None) != '':
#         group = Group.objects.get(id=DATA.get('group', None))
#         result = result.filter(group=group)

#     if DATA.get('unit', None) != '':
#         result = result.filter(unit=DATA.get('unit', None))

#     if not DATA.get('page', None): page = 1
#     else: page = int(DATA['page'])

#     users = []
#     result_num = result.count()
#     for order, u in enumerate(result[(page-1)*NUMPERPAGE:page*NUMPERPAGE]):
#         u.order = int((page-1)*NUMPERPAGE+order+1)
#         users.append(u)

#     return users, result_num


# @login_required
# @checkAuthority
# def EmailAccountList(R, project, right_type_value=u'帳號管理'):
#     users = EmailList.objects.all().order_by('place', 'name')
#     places = [TAIWAN] + list(Place.objects.filter(uplevel=TAIWAN).order_by('id'))
#     t = get_template(os.path.join('fishuser', 'email_account_list.html'))
#     html = t.render(Context({
#         'users': users,
#         'places': places,
#     }))

#     return HttpResponse(html)


# def makeEmailInfo(R):
#     if R.META['REMOTE_ADDR'] not in CAN_VIEW_BUG_PAGE_IPS:
#         return HttpResponseRedirect('/')

#     place_id = R.GET.get('place_id', '1')
#     try:
#         place = Place.objects.get(id=place_id)
#     except:
#         place = None
#     mail_lists = EmailList.objects.filter(place=place)
#     countychasetime = CountyChaseTime.objects.all().order_by('-id')[0]
#     countychasetime.time = CountyChaseTime.objects.all().count()
#     countychasetime.pastDay = (datetime.date.today() - countychasetime.chase_date).days
#     checks = []
#     not_checks = []
#     not_in_frcm = []
#     no_contractors = []
#     no_inspectors = []
#     if not mail_lists:
#         t = get_template(os.path.join('fishuser', 'email_info.html'))
#         html = t.render(Context({}))
#     else:
#         projects = CountyChaseProjectOneToMany.objects.filter(countychasetime=countychasetime).order_by('project__place', 'project__year')
#         frcm_ids = []

#         for i in projects:
#             if FRCMUserGroup.objects.filter(project__id=i.project.id).count() != 0:
#                 frcm_ids.append(i.project.id)
#         if place != TAIWAN:
#             projects = projects.filter(project__place=place).exclude(project__undertake_type__value='自辦')
#         else:
#             projects = projects.filter(project__undertake_type__value='自辦').order_by('project__place')

#         no_contractors = []
#         no_inspectors = []
#         for i in projects.filter(project__id__in=frcm_ids):
#             if not FRCMUserGroup.objects.filter(project=i.project, group__name=u'營造廠商'):
#                 print [x.group.id for x in FRCMUserGroup.objects.filter(project=i.project)]
#                 i.project.frcmuser = FRCMUserGroup.objects.get(project=i.project, group__name__in=['負責主辦工程師', '自辦主辦工程師']).user
#                 no_contractors.append(i)
#             if not FRCMUserGroup.objects.filter(project=i.project, group__name=u'監造廠商', project__frcm_inspector_type__value=u'委外監造'):
#                 i.project.frcmuser = FRCMUserGroup.objects.get(project=i.project, group__name__in=['負責主辦工程師', '自辦主辦工程師']).user
#                 no_inspectors.append(i)

#         checks = []
#         not_checks = []
#         not_in_frcm = []

#         temp = projects.filter(check=True)
#         for i in temp:
#             if i.schedul_progress_percent > i.actual_progress_percent:
#                 i.project.frcmuser = FRCMUserGroup.objects.get(project=i.project, group__name__in=['負責主辦工程師', '自辦主辦工程師']).user
#                 checks.append(i)
#         not_checks = projects.filter(check=False, project__id__in=frcm_ids)
#         for i in not_checks:
#             i.project.frcmuser = FRCMUserGroup.objects.get(project=i.project, group__name__in=['負責主辦工程師', '自辦主辦工程師']).user
#         not_in_frcm = projects.filter(complete=False).exclude(project__id__in=frcm_ids)
#         for i in not_in_frcm:
#             i.project.frcmuser = ''

#     #先遮掉寄件人的信箱資訊
#     for i in mail_lists:
#         i.last_name = i.name[0]

#     t = get_template(os.path.join('fishuser', 'email_info.html'))
#     html_body = t.render(Context({
#         'mail_lists': mail_lists,
#         'place': place,
#         'countychasetime': countychasetime,
#         'not_checks': not_checks,
#         'not_in_frcm': not_in_frcm,
#         'checks': checks,
#         'no_contractors': no_contractors,
#         'no_inspectors': no_inspectors,
#     }))

#     type = R.GET.get('type', '')
#     if type in ['json', 'xml']:
#         ac = AESCrypto()
#         d = {
#             'password': base64.b64encode(_public_encypt(ac.secret, R.GET.get('public_key', ''))[0]),
#             'emails': [ac.EncodeAES(str(u'%s <%s>' % (e.name, e.email))) for e in mail_lists],
#             'title': ac.EncodeAES(str(u'(%s)漁業署工程管理系統(FES)即時預警通知資訊' % place.name)),
#             'body': ac.EncodeAES(str(html_body)),
#         }
#         if type == 'json':
#             html = json.dumps(d)
#         else:
#             raise Exception(u'尚未實作')
#     else:
#         html = u'''<html>
#     <head profile="http://gmpg.org/xfn/11">
#         <meta http-equiv="content-type" content="text/html; charset=utf-8" />
#         <title>漁業署工程管理系統-盯催信</title>
#     </head>
#     <body id="id_body">%s</body></html>
#         ''' % html_body
#         html = re.sub(u'([0-9][0-9]+|負責人：[^\)<]+)', '*', html)
#     return HttpResponse(html)


# def _public_encypt(s, public_key=''):
#     if not public_key:
#         public_key = DEFAULT_PUBLIC_KEY
#     elif not re.search('-BEGIN +PUBLIC +KEY-', public_key):
#         public_key = base64.b64decode(public_key)

#     key = RSA.importKey(public_key)
#     return key.encrypt(base64.b64encode(s), random.randint(-10240000, 10240000))


# DEFAULT_PUBLIC_KEY = '''-----BEGIN PUBLIC KEY-----
# MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC9OTQ5xMJ25qzxnI04g6ZIZkqi
# hnjNi1La/2zyWOapw+qD4qS89Kywa7M09d1KmUPi56+IiezZLHQ1Fl/1QvPif/da
# a89DZUXWbFScG9nNNZTbiKZzZm/Ji3EPep9Xtb+9f8mseiIWa4Esy6qLvkNCTRAQ
# w6UXFrrOZFI6Ba7kGQIDAQAB
# -----END PUBLIC KEY-----'''


# DEFAULT_PRIVATE_KEY = '''-----BEGIN RSA PRIVATE KEY-----
# MIICXAIBAAKBgQC9OTQ5xMJ25qzxnI04g6ZIZkqihnjNi1La/2zyWOapw+qD4qS8
# 9Kywa7M09d1KmUPi56+IiezZLHQ1Fl/1QvPif/daa89DZUXWbFScG9nNNZTbiKZz
# Zm/Ji3EPep9Xtb+9f8mseiIWa4Esy6qLvkNCTRAQw6UXFrrOZFI6Ba7kGQIDAQAB
# AoGAEPCND1rg+dn+w4Z7UgLfIP4fUlttdyEw4rAZJbz1sV77oKDqlIvm5chOe8BC
# 9kmwPSD2oueOD4ceRB5jqsY6pPXDzSAJpmiSQ78eNcir/Ga1mhmjOkzTDFkr1XKf
# kXerZtNurPl5P3hB/nPZqiXgV2TI4G5YOagKoAYegCnEYYECQQDM6kIC19J/UfuG
# Y88rsw6ky2Zik8dgRB+99tdV47KOyJgMbtNqDx79YnykRQsVNyHssy5zckmiFbHr
# AttZWjaRAkEA7GWAnWFzrmCTq8dPGmYkKJbOlnWi5wAyR6T0GStYCm8/rotOsXdT
# sZnsPprHld7o9LTMAbdRkUGqsBdgDsnpCQJAethhVIUAS5XhfVKuq1sAB2ls6uH/
# H8YXZXHq7DHCJPk6thFmqul/wZXedThzCXfw3Y8Z5Nn6LLJm5CXlTC7aEQJAYuYM
# KsuMdBWfcixOIcM9uWVuRHAumOnyHxsZrDX//U2RnNpXL9O2RgUZWw+yFDdPyqCh
# AM7K5zRLzqPY4hcC0QJBAKSd7PICK1yAj7YnjQwOPMu6rDv4Q26KjeSFmY5k0cYt
# fZSZ1x5JQ9/ziYJYl3RI1hSFKybLZ0naKCUfy2HUqp8=
# -----END RSA PRIVATE KEY-----
# '''


# @login_required
# @checkAuthority
# def creatUser(R, project, right_type_value='開創帳號'):
#     user, DATA = R.user, readDATA(R)

#     if user.user_profile.group.name == '縣市帳號管理員':
#         city_title = user.username[0:2]
#     else:
#         city_title = ''

#     if 'creatUser' == DATA.get('submit', None):
#         if DATA.get('username','')[1] == '_':
#             return HttpResponse(json.write({'status': False, 'message': '帳號第二個字元不可為"_"'}))
#         try:
#             u = User.objects.get(username=(city_title+DATA.get('username','')))
#             return HttpResponse(json.write({'status': False, 'message': '新增失敗，此帳號以被『%s』同仁使用' % u.user_profile.rName()}))
#         except:
#             u = User(
#                     username = (city_title+DATA.get('username','').lower()),
#                     last_name = DATA.get('last_name', None),
#                     first_name = DATA.get('first_name', None),
#                     email = DATA.get('email', 'None'),
#                     date_joined = NOW(),
#                     is_staff = False,
#                     )
#             if 'True' == DATA.get('is_active', None):
#                 u.is_active = True
#             else:
#                 u.is_active = False

#             password = DATA.get('password', None)
#             u.set_password(password)
#             u.save()
#             up = UserProfile(user=u)
#             up.title = DATA.get('title', '')
#             up.phone = DATA.get('phone', '')
#             up.fax = DATA.get('fax', '')
#             up.group = Group.objects.get(id=DATA.get('group', ''))
#             up.unit = Unit.objects.get(id=DATA.get('unit', ''))
#             up.save()

#             return HttpResponse(json.write({'status': True, 'username': u.username}))



#     groups = []
#     for i in Group.objects.all():
#         if i.name == '上層管理者': groups.append(i)
#         elif i.name == '主辦工程師': groups.append(i)
#     if user.user_profile.group.name == '本署帳號管理員' or user.is_staff:
#         for i in Group.objects.all():
#             if i.name == '本署帳號管理員':groups.append(i)
#             elif i.name == '管考填寫員': groups.append(i)
#             elif i.name == '漁船填寫員': groups.append(i)
#             elif i.name == '漁港資訊填寫員': groups.append(i)

#     units = []
#     for i in Unit.fish_city_menu.all():
#         units.append([i.id, i.name])
#         if i.uplevel and i.uplevel.name != '縣市政府':
#             units.extend(
#                 [[j.id, '---'+j.name] for j in i.uplevel_subunit.all()]
#             )
#     t = get_template(os.path.join('fishuser', 'creatuser.html'))
#     html = t.render(Context({
#         'user': R.user,
#         'groups': groups,
#         'city_title': city_title,
#         'units': units,
#     }))

#     return HttpResponse(html)

# @login_required
# @checkAuthority
# def editUser(R, user_id, project, right_type_value=u'帳號管理'):
#     user, DATA = R.user, readDATA(R)
#     edituser = User.objects.get(id=user_id)

#     if 'editUser' == DATA.get('submit', None):
#         edituser.last_name = DATA.get('last_name', None)
#         edituser.first_name = DATA.get('first_name', None)
#         edituser.email = DATA.get('email', 'None')
#         if 'True' == DATA.get('is_active', None):
#             edituser.is_active = True
#         else:
#             edituser.is_active = False
#         if DATA.get('password', None) != '':
#             password = DATA.get('password', None)
#             edituser.set_password(password)
#         edituser.save()

#         up = UserProfile.objects.get(user=edituser)
#         up.title = DATA.get('title', '')
#         up.phone = DATA.get('phone', '')
#         up.fax = DATA.get('fax', '')
#         up.group = Group.objects.get(id=DATA.get('group', ''))
#         if DATA.get('unit', '') != '':
#             up.unit = Unit.objects.get(id=DATA.get('unit', ''))
#         else:
#             up.unit = None
#         up.save()

#         return HttpResponse(json.write({'status': True}))



#     groups = []
#     if edituser.user_profile.group.name == '縣市帳號管理員':
#         groups.append(Group.objects.get(name='縣市帳號管理員'))
#     else:
#         for i in Group.objects.all():
#             if i.name == '上層管理者': groups.append(i)
#             elif i.name == '主辦工程師': groups.append(i)
#             elif i.name == '註冊': groups.append(i)
#         if user.user_profile.group.name == '本署帳號管理員' or user.is_staff:
#             for i in Group.objects.all():
#                 if i.name == '本署帳號管理員':groups.append(i)
#                 elif i.name == '署內主辦工程師': groups.append(i)
#                 elif i.name == '管考填寫員': groups.append(i)
#                 elif i.name == '漁船填寫員': groups.append(i)
#                 elif i.name == '漁港資訊填寫員': groups.append(i)

#     units = []
#     for i in Unit.fish_city_menu.all():
#         units.append([i.id, i.name])
#         if i.uplevel and i.uplevel.name != '縣市政府':
#             units.extend(
#                 [[j.id, '---'+j.name] for j in i.uplevel_subunit.all()]
#             )

#     t = get_template(os.path.join('fishuser', 'edituser.html'))
#     html = t.render(Context({
#         'user': R.user,
#         'edituser': edituser,
#         'groups': groups,
#         'units': units,
#     }))

#     return HttpResponse(html)

# @needNotLogin
# def registerUser(R):
#     DATA = readDATA(R)
#     if 'registerUser' == DATA.get('submit', None):
#         try:
#             user = User.objects.get(username = DATA.get('username', None))
#             return HttpResponse(json.write({'status': False, 'message': '新增失敗，此『%s』帳號已被申請使用' % user.username}))
#         except:
#             newuser = User(
#                 username = DATA.get('username', None),
#                 last_name = DATA.get('last_name', None),
#                 first_name = DATA.get('first_name', None),
#                 email = DATA.get('email', 'None'),
#                 is_active = True,
#             )
#             password = DATA.get('password', None)
#             newuser.set_password(password)
#             newuser.save()
#             up = UserProfile(
#                 user=newuser,
#                 title = DATA.get('title', ''),
#                 phone = DATA.get('phone', ''),
#                 fax = DATA.get('fax', ''),
#                 group = Group.objects.get(name='註冊'),
#             )
#             up.save()

#             return HttpResponse(json.write({'status': True}))

#     t = get_template(os.path.join('fishuser', 'registeruser.html'))
#     html = t.render(Context({}))
#     return HttpResponse(html)



@login_required
@checkAuthority
def Show_History_Engineering(R, project, right_type_value=u'使用歷史工程案系統'):

    t = get_template(os.path.join('fishuser', 'show_history_engineering.html'))
    html = t.render(Context({}))
    return HttpResponse(html)


@login_required
def makeTaiwanWord(R):
    #資料庫常常恢復成台，強制改回去臺
    places = Place.objects.filter(name__contains='台')
    for i in places:
        i.name = i.name.replace('台', '臺')
        i.save()
    return HttpResponse(json.write({'status': True, 'places': [i.id for i in places]}))


from django.contrib.auth.backends import ModelBackend
class ExchangeBackend(ModelBackend):
    """
        這是為了要能讓 admin 群組在不知道使用者密碼時，直接可以轉帳號用的擴充認證 model
    """
    def authenticate(self, username=None, password=None):
        try: user = User.objects.get(username=username)
        except User.DoesNotExist: return None

        if password == "^!@#$%^&*('給admin轉帳號用')":
            return user
        else:
            if user.check_password(password): return user
            else: return None

    def get_user(self, user_id):
        try: return User.objects.get(pk=user_id)
        except User.DoesNotExist: return None



#讀取全部系統公告
@login_required
def system_information_get_all(R):
    """ 
    讀取全部系統公告頁面 
    """
    page = int(R.GET.get('page', 1))
    is_login_page = R.POST.get('is_login_page', False)

    infos = SystemInformation.objects.filter(start_date__lte=TODAY()).order_by('-start_date')
    n = sort = infos.count()
    for info in infos:
        info.sort = sort
        sort -= 1
    page_list = range(1, int(ceil(infos.count()/25.)+1))
    infos = infos[(page-1)*25:page*25]
    t = get_template(os.path.join('fishuser', 'system', 'system_information_get_all.html'))
    html = t.render(RequestContext(R,{
        'user': R.user,
        'page': page,
        'page_list': page_list,
        'infos': infos,
        'n': n
    }))
    return HttpResponse(html)


#編輯系統公告
@login_required
def system_information_edit(R):
    """ 
    編輯系統公告頁面 
    """
    if not R.user.is_staff:
        return HttpResponseRedirect('/')

    infos = SystemInformation.objects.all().order_by('-start_date')

    t = get_template(os.path.join('fishuser', 'system', 'system_information_edit.html'))
    html = t.render(RequestContext(R,{
        'user': R.user,
        'infos': infos,
    }))
    return HttpResponse(html)


#新增系統公告
@login_required
def system_information_create(R):
    """ 
    建立新系統公告頁面 
    """
    if not R.user.is_staff:
        return HttpResponseRedirect('/')

    for i in SystemInformationFile.objects.filter(systeminformation=None):
        try:
            os.remove(os.path.join(settings.BASE_DIR, 'uploaded-files', i.file.name))
        except: pass
        i.delete()

    t = get_template(os.path.join('fishuser', 'system', 'system_information_create.html'))
    html = t.render(RequestContext(R,{
        'user': R.user,
    }))
    return HttpResponse(html)


#讀取檔案
@login_required
def get_image(R, **kw):
    ''' 
    讀取圖片檔案 
    '''
    row_id = kw['row_id']
    image = SystemInformationFile.objects.get(id=row_id)
    f = open(image.file.path, 'rb')
    content = f.read()
    return HttpResponse(content, content_type='image/png')


#新增公告
@login_required
def set_information(R):
    """ 
    新增系統公告
    """
    start_date = R.POST.get('start_date', '')
    on_login_page = True if R.POST.get('on_login_page', '') == 'true' else False
    title = R.POST.get('title', '')
    memo = R.POST.get('memo', '')

    user = R.user
    systeminformation = SystemInformation(
            start_date=start_date,
            user=user,
            on_login_page=on_login_page,
            title=title,
            memo=memo
        )
    systeminformation.save()

    for i in SystemInformationFile.objects.filter(systeminformation=None):
        i.systeminformation = systeminformation
        i.save()

    return HttpResponse(json.dumps({'status': True}))


#下載檔案專用
@login_required
def download_file(R, **kw):
    ''' 
    下載檔案
    '''
    table_name = kw['table_name']
    file_id = kw['file_id']

    if table_name == 'systeminformationfile':
        row = SystemInformationFile.objects.get(id=file_id)

    f = open(row.file.path, 'rb')
    content = f.read()
    response = HttpResponse(content_type='application/' + row.rExt())
    response['Content-Type'] = ('application/' + row.rExt())
    file_name = row.name.replace(" ", "") + '.' + row.rExt()
    response['Content-Disposition'] = ('attachment; filename='+ file_name).encode('cp950')
    response.write(content)
    return response


#上傳檔案的處理
@login_required
def new_file_upload(R):
    ''' 
    * 說明:上傳檔案的處理
    * 輸入:http request
    > method:POST
    * 輸出:json
    > data:'status', 'id', 'name', 'ext'
    * 主關聯資料:SystemInformationFile
     
    '''
    data = R.POST

    table_name = data.get('table_name', '')
    row_id = data.get('row_id', '')

    f = R.FILES.get('file', None)
    full_name = f.name.split(".")
    ext = full_name[-1]
    full_name.remove(full_name[-1])
    name = "".join(full_name)

    if table_name == 'SystemInformationFile':
        new = SystemInformationFile(
            name = name,
        )
        if row_id:
            new.systeminformation = SystemInformation.objects.get(id=row_id)
        new.save()
        getattr(new, 'file').save('%s.%s'%(new.id, ext), f)
        new.save()
    return HttpResponse(json.dumps({'status': True, 'id': new.id, 'name': new.name, 'ext': ext}))

