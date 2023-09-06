#!-*- coding:utf8 -*-
# cimcore.modules.pccmating.sync

import datetime, json
from django.conf import settings
try:
    from modules.pccmating import models
except ImportError:
    from pccmating import models
    
from sexual_assault_against_pcc import pcchandler
from urllib import urlencode
from urllib2 import Request, urlopen

def getHandler():
    username = models.Cofiguration.objects.get(key="username").value
    password = models.Cofiguration.objects.get(key="password").value
    
    
    host = models.Cofiguration.objects.get(key="host").value
    port = models.Cofiguration.objects.get(key="port").value
    
    proxy_ip, proxy_port, handler = None, None, None
    # try:
    #     proxy_ip = models.Cofiguration.objects.get(key="proxy_ip").value
    #     proxy_port = models.Cofiguration.objects.get(key="proxy_port").value
    # except Exception:
    #     pass
    if(proxy_ip and proxy_port):
        handler = pcchandler.SexualAssaultAgainstPCC(proxy_ip, int(proxy_port), url_prefix="http://%s:%s"%(host, port))
    else:
        try:
            handler = pcchandler.SexualAssaultAgainstPCC(host, int(port))
        except: return {'connect_error': True, 'connect_msg': u'SexualAssaultAgainstPCC 錯誤'}
    
    [login_info, x] = handler.login(username, password)
    try:
        if login_info.has_key('connect_error') and login_info['connect_error']:
            return login_info
    except: pass
    return handler

def syncPccInformation(project_id, handler = None):
    if(not handler): handler = getHandler()

    #改用遠端伺服器同步
    url = '%s%s' % (settings.PCCMATING_SERVER_HOST, 'fes_pccmating/get_project_info/')
    data = {}
    data['uid'] = project_id
    data['api_key'] = settings.PCCMATING_SERVER_APIKEY
    data = urlencode(data)
    req = Request(url, data)
    doc = json.loads(urlopen(req).read())

    # doc = handler.getProjectBasicInformation(project_id)

    # doc['basic_information'] = handler.getProjectFullInformation(doc[u'url_basic_information'])
    
    project = None
    try:
        project = models.Project.objects.get(uid=project_id)
    except:
        project = models.Project(uid=project_id)
    
    for f in models.Project._meta.fields:
        if(doc["basic_information"].has_key(f.name)): project.__setattr__(f.name, doc["basic_information"][f.name])
    
    project.lastsync = datetime.datetime.now()
    project.save()
    for index in range(len(doc["progress"])):
        try:
            syncPccProgress(project, doc["progress"][index]['doc'])
        except: pass
        
    return project
    
def syncPccProgress(project, doc):
    progress = None
    try:
        progress = project.progress.get(year=doc['year'], month=doc['month'])
    except models.ProjectProgress.DoesNotExist:
        progress = models.ProjectProgress(project=project)
    
    for f in models.ProjectProgress._meta.fields:
        if(doc.has_key(f.name)): progress.__setattr__(f.name, doc[f.name])
    
    progress.lastsync = datetime.datetime.now()
    progress.save()
    
    return progress

def getProjectInfo(project_id):
    #取得單一工程資訊
    project = syncPccInformation(project_id)
    return project


def getAllWorkingProjectInfo(handler = None):
    #取得所有在建工程資訊
    if(not handler): handler = getHandler()

    #改用遠端伺服器同步
    url = '%s%s' % (settings.PCCMATING_SERVER_HOST, 'fes_pccmating/get_all_working_project_info/')
    data = {}
    data['api_key'] = settings.PCCMATING_SERVER_APIKEY
    data = urlencode(data)
    req = Request(url, data)
    doc = json.loads(urlopen(req).read())
        
    return doc

def getAllWorkingProjectInfo_old(handler = None):
    #取得所有在建工程資訊
    if(not handler): handler = getHandler()

    #改用遠端伺服器同步
    url = '%s%s' % (settings.PCCMATING_SERVER_HOST, 'fes_pccmating/get_old_project_info/')
    data = {}
    data['api_key'] = settings.PCCMATING_SERVER_APIKEY
    data = urlencode(data)
    req = Request(url, data)
    doc = json.loads(urlopen(req).read())
        
    return doc

def getNoProgressProjectInfo(handler = None):
    #取得所有 進度未填清單-含剛決標或未開工案件
    if(not handler): handler = getHandler()

    #改用遠端伺服器同步
    url = '%s%s' % (settings.PCCMATING_SERVER_HOST, 'fes_pccmating/get_no_progress_project_info/')
    data = {}
    data['api_key'] = settings.PCCMATING_SERVER_APIKEY
    data = urlencode(data)
    req = Request(url, data)
    doc = json.loads(urlopen(req).read())
        
    return doc

def getAllFisheryProject(handler = None):
    if(not handler): handler = getHandler()
    projects_list = handler.getAllFisheryProjectInList()

    return projects_list

def syncPccSuperviseInformation(date, uid, handler = None):
    if(not handler): handler = getHandler()
    try:
        if handler.has_key('connect_error') and handler['connect_error']:
            return handler
    except: pass

    doc = handler.getProjectBasicInformation(uid)
    if doc.has_key('connect_error') and doc['connect_error']:
        return doc
    doc['supervise_basic_information'] = handler.getSuperviseBasicInformation(doc[u'url_supervise_information'], date)

    return doc['supervise_basic_information']

def syncPccSuperviseError(date, uid, handler = None):
    if(not handler): handler = getHandler()

    doc = handler.getProjectBasicInformation(uid)
    doc['supervise_error_information'] = handler.getSuperviseErrorInformation(doc[u'url_supervise_input'], date)

    return doc['supervise_error_information']
    










def getAllProject(handler = None):
    #取得所有標案系統工程基本資料
    if(not handler): handler = getHandler()
    projects_list = handler.getAllProject()
    return projects_list

def getAllOldProject(handler = None):
    #取得所有標案系統工程基本資料
    if(not handler): handler = getHandler()
    projects_list = handler.getAllOldProject()
    return projects_list

def syncPccAuditingInformation(date, pcc_no, handler = None):
    #取得查核紀錄的基本資料
    if(not handler): handler = getHandler()
    doc = handler.getProjectBasicInformation(pcc_no)
    doc['supervise_basic_information'] = handler.syncPccAuditingInformation(doc[u'url_supervise_information'], date)
    return doc['supervise_basic_information']


def syncPccAuditingDate(pcc_no, handler = None):
    #取得所有查核紀錄的日期
    if(not handler): handler = getHandler()
    doc = handler.getProjectBasicInformation(pcc_no)
    doc['auditing_dates'] = handler.syncPccAuditingDate(doc[u'url_supervise_information'])
    return doc['auditing_dates']