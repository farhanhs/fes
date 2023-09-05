# -*- coding: utf-8 -*-
if __name__ == '__main__':
    import sys
    import os
    sys.path.append('../../../fes')
    sys.path.append('../../../fes/apps')
    sys.path.append('../../../fes/modules')
    sys.path.append('../../../cim')
    sys.path.append('../../../cim/apps')
    sys.path.append('../../../cim/modules')

    import settings
    from django.core.management import setup_environ
    setup_environ(settings)


from types import StringType, IntType
from django.template.loader import get_template
from django.template import Context, RequestContext
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.contrib.auth.models import User, Group
from django.db.models import Q
from common.lib import readDATA
from general.models import Place, Unit
from fishuser.models import _ca
from harbor.models import FishingPort
from monitor.models import Option, Monitor, Account, Preset
try: from settings import NVR_DATA
except ImportError: NVR_DATA = {'host': '', 'user': '', 'passwd': '', 'database': ''}
try: from settings import PROXY
except ImportError: PROXY = False
else:
    if type(PROXY[0]) != StringType or type(PROXY[1]) != IntType:
        PROXY = False

import os, re, datetime
import json
import httplib, urllib
import decimal
import random
from random import randint
import MySQLdb
from hashlib import md5
from time import time



class GeneralControl(object):
    class TimeoutError(Exception): pass
    class LoginError(Exception): pass
    class OperationError(Exception): pass



class PELCODControl(GeneralControl):
    def __init__(self, IP, user, passwd):
        self.IP = str(IP)
        self.user = str(user)
        self.passwd = str(passwd)
        self.status = self._login()


    def _getConnect(self, request):
        if PROXY == False:
            proxies = {}
        elif PROXY[0] == '' and PROXY[1] == '':
            proxies = {}
        else:
            proxies = {'http': 'http://%s:%s/'%(PROXY[0], PROXY[1])}
        url = 'http://%s:%s@%s%s' % (self.user, self.passwd, self.IP, request)
        R = urllib.urlopen(url, proxies=proxies)
        status = self.status = R.getcode()
        if status in [408, 504]:
            raise self.TimeoutError
        elif 200 != int(status):
            raise self.OperationError
        return status


    def _login(self):
        return 200


    def add_user(self, user, passwd, option):
        if option == Option.objects.get(swarm='account_type', value='Administrator'):
            #INFO 因為 PELCO-D 的機制是只能修改原 ADMIN ，不能新增另一個帳戶
            option = 'ADMIN'
            return 200
        elif option == Option.objects.get(swarm='account_type', value='Operator'):
            option = 'USER-PTZ'
        else:
            option = 'USER'
        act = '/SetUser.cgi?User=%s&Pass=%s&Authority=%s'%(user, passwd, option)
        return self._getConnect(act)


    set_password = add_user


    def ptz(self, command, speed):
        speed = re.sub('[^0-9]', '', speed)
        login = self.user+":"+self.passwd
        if 'Stop' == command: act = "/SetPTZ.cgi?Dir=Stop"
        elif 'Up' == command: act = "/SetPTZ.cgi?Dir=UpStart&PTZSpeed=%s"%speed
        elif 'Down' == command: act = "/SetPTZ.cgi?Dir=DownStart&PTZSpeed=%s"%speed
        elif 'Left' == command: act = "/SetPTZ.cgi?Dir=LeftStart&PTZSpeed=%s"%speed
        elif 'Right' == command: act = "/SetPTZ.cgi?Dir=RightStart&PTZSpeed=%s"%speed
        elif 'UL' == command: act = "/SetPTZ.cgi?Dir=UpLeftStart&PTZSpeed=%s"%speed
        elif 'UR' == command: act = "/SetPTZ.cgi?Dir=UpRightStart&PTZSpeed=%s"%speed
        elif 'DL' == command: act = "/SetPTZ.cgi?Dir=DownLeftStart&PTZSpeed=%s"%speed
        elif 'DR' == command: act = "/SetPTZ.cgi?Dir=DownRightStart&PTZSpeed=%s"%speed
        elif 'ZoomIn' == command: act = "/SetPTZ.cgi?Dir=ZoomInStart&PTZSpeed=%s"%speed
        elif 'ZoomOut' == command: act = "/SetPTZ.cgi?Dir=ZoomOutStart&PTZSpeed=%s"%speed
        return self._getConnect(act)


    def run_preset(self, preset):
        act = "/SetPTZ.cgi?Dir=Point%s"%preset
        return self._getConnect(act)


    def create_preset(self, no):
        act = "/SetPTZ.cgi?Dir=Preset%(no)s&PointName=%(no)s:Point%(no)s"%{'no': no}
        return self._getConnect(act)


    def update_preset(self, no):
        act = "/SetPTZ.cgi?Dir=Preset%(no)s&PointName=%(no)s:Point%(no)s"%{'no': no}
        return self._getConnect(act)


    def delete_preset(self, no):
        act = "/SetPTZ.cgi?RemoveName=%s"%no
        return self._getConnect(act)


    def update_quality(self, type):
        if type == 'low':
            number = 32
        elif type == 'high':
            number = 320
        else:
            number = 256
        act = "/SetMultimedia.cgi?Compression_Type=0&Bitrate=%s"%number
        return self._getConnect(act)



class BE3204Control(GeneralControl):
    def __init__(self, IP, user, passwd):
        self.IP = str(IP)
        self.user = str(user)
        self.passwd = str(passwd)
        self._login()


    def _getConnect(self, request):
        if PROXY == False:
            conn = httplib.HTTPConnection(self.IP, timeout=30)
            conn.request("GET", request)
        elif PROXY[0] == '' and PROXY[1] == '':
            conn = httplib.HTTPConnection(self.IP, timeout=30)
            conn.request("GET", request)
        else:
            conn = httplib.HTTPConnection(PROXY[0], PROXY[1], timeout=30)
            conn.request("GET", "http://"+self.IP+request)
        R = conn.getresponse()
        status = self.status = int(R.status)
        if status in [408, 504]:
            raise self.TimeoutError
        elif 200 != int(self.status):
            raise self.OperationError
        return status


    def _login(self):
        act = "/vb.htm?login="+self.user+":"+self.passwd
        return self._getConnect(act)


    def _toHex(self, num):
        num = int(num)
        hex = ''
        while num != 0:
            unit = num%16
            if unit == 10:
                unit = 'A'
            elif unit == 11:
                unit = 'B'
            elif unit == 12:
                unit = 'C'
            elif unit == 13:
                unit = 'D'
            elif unit == 14:
                unit = 'E'
            elif unit == 15:
                unit = 'F'
            else:
                unit = str(unit)
            hex = unit + hex
            num = num/16
        if len(hex)==1:
            hex = '0' + hex
        if len(hex)==0:
            hex = '00'
        return hex


    def add_user(self, user, passwd, option):
        if option == Option.objects.get(swarm='account_type', value='Administrator'):
            option = '0'
        elif option == Option.objects.get(swarm='account_type', value='Operator'):
            option = '1'
        else:
            option = '2'
        act = "/vb.htm?adduser="+user+":"+passwd+":"+option
        return self._getConnect(act)


    set_password = add_user


    def ptz(self, command, speed):
        login = self.user+":"+self.passwd
        if 'Stop' == command: act = "/vb.htm?login="+login+"&dv840output=A000000000"
        elif 'Up' == command: act = "/vb.htm?login="+login+"&dv840output=A0000800"+speed
        elif 'Down' == command: act = "/vb.htm?login="+login+"s&dv840output=A0001000"+speed
        elif 'Left' == command: act = "/vb.htm?login="+login+"&dv840output=A00004"+speed+'00'
        elif 'Right' == command: act = "/vb.htm?login="+login+"&dv840output=A00002"+speed+'00'
        elif 'UL' == command: act = "/vb.htm?login="+login+"&dv840output=A0000C0C"+speed
        elif 'UR' == command: act = "/vb.htm?login="+login+"&dv840output=A0000A0C"+speed
        elif 'DL' == command: act = "/vb.htm?login="+login+"s&dv840output=A000140C"+speed
        elif 'DR' == command: act = "/vb.htm?login="+login+"s&dv840output=A000120C"+speed
        elif 'ZoomIn' == command: act = "/vb.htm?login="+login+"&dv840output=A000200000"
        elif 'ZoomOut' == command: act = "/vb.htm?login="+login+"&dv840output=A000400000"
        return self._getConnect(act)


    def run_preset(self, preset):
        login = self.user+":"+self.passwd
        preset_no = self._toHex(preset)
        act = "/vb.htm?login="+login+"&dv840output=A0000700"+preset_no
        return self._getConnect(act)


    def create_preset(self, no):
        login = self.user+":"+self.passwd
        set_no = self._toHex(no)
        act = "/vb.htm?login="+login+"&dv840output=A0000300"+set_no
        return self._getConnect(act)


    def update_preset(self, no):
        login = self.user+":"+self.passwd
        set_no = self._toHex(no)
        act = "/vb.htm?login="+login+"&dv840output=A0000300"+set_no
        return self._getConnect(act)


    def delete_preset(self, no):
        login = self.user+":"+self.passwd
        set_no = self._toHex(no)
        act = "/vb.htm?login="+login+"&dv840output=A0000500"+set_no
        return self._getConnect(act)


    def update_quality(self, type):
        login = self.user+":"+self.passwd
        if type == 'low':
            number = '0'
        elif type == 'high':
            number = '4'
        else:
            number = '2'
        act = "/vb.htm?login="+login+"&quality="+number;
        return self._getConnect(act)



class CameraControl(object):
    def __init__(self, machine_no, IP, user, passwd):
        if machine_no == 'BE3204':
            self.camera = BE3204Control(IP, user, passwd)
        elif machine_no == 'PELCO-D':
            self.camera = PELCODControl(IP, user, passwd)



def _syncNVR():
    nvr_db = MySQLdb.connect(host=NVR_DATA['host'], user=NVR_DATA['user'], passwd=NVR_DATA['passwd'], db=NVR_DATA['database'])
    nvr_cursor = nvr_db.cursor()
    nvr_cursor.execute("SELECT * FROM db_table")
    result = nvr_cursor.fetchall()



def rIndex(R):
    cam = Monitor.objects.get(id=19)
    Viewer = Option.objects.get(swarm='account_type', value='Viewer')
    VAccount = Account.objects.get(monitor=cam, type=Viewer)
    IE = True
    preset = Preset.objects.filter(monitor=cam)
    t = get_template(os.path.join('monitor', 'index.html'))
    html = t.render(Context({'cam': cam, 'connect': True, 'preset': preset, 'VAccount': VAccount, 'edit': True, 'IE': IE}))
    return HttpResponse(html)


def makePresetSelection(presets, selected):
    content = ''
    content += '<select id="preset">'
    if selected == "":
        content += '<option value="" selected>請選擇預設場景　</option>'
    else:
        content += '<option value="">請選擇預設場景　</option>'
    for preset in presets:
        if preset.id == selected:
            content += '<option value="' + preset.no + '" selected>' + preset.name + '</option>'
        else:
            content += '<option value="' + preset.no + '">' + preset.name + '</option>'
    content += '</select>'
    return content


def _simple_verify(key, time_str):
    try:
        request_time = datetime.datetime.strptime(time_str, '%Y%m%d%H%M%S')
    except ValueError:
        return False
    utc_now = datetime.datetime.utcnow()
    if not (utc_now - datetime.timedelta(minutes=5) < request_time
        < utc_now + datetime.timedelta(minutes=5)):
        return False
    verify = md5(key+time_str+'22855647').hexdigest()
    return verify


def record_action(R, action, monitor_id):
    user = R.user
    if not user.is_staff: return HttpResponse(u'無權限')

    if action not in ['start', 'stop']:
        return HttpResponse('No Action')

    try:
        a = int(monitor_id)
    except ValueError:
        return HttpResponse('No id')

    try:
        cam = Monitor.objects.get(id=monitor_id)
    except Monitor.DoesNotExist:
        return HttpResponse(u'找不到攝影機')

    key = str(randint(1000, 100000))
    request_time_str = datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S')
    verify = _simple_verify(key, request_time_str)

    return HttpResponseRedirect('http://webnvr.nchu-cm.com/control_camera/%s/%s/?key=%s&request_time_str=%s&verify=%s&name=%s'%
                (action, monitor_id, key, request_time_str, verify, cam.name.replace(u'(暫停錄影)', ''))
                )


def change_camera_name(R, action, monitor_id):
    user = R.user
    if not user.is_staff: return HttpResponse(u'無權限')

    if action not in ['start', 'stop']:
        return HttpResponse('No Action')

    try:
        a = int(monitor_id)
    except ValueError:
        return HttpResponse('No id')

    try:
        cam = Monitor.objects.get(id=monitor_id)
    except Monitor.DoesNotExist:
        return HttpResponse(u'找不到攝影機')
    else:
        if u'停止使用' not in cam.name:
            if action == 'start':
                if u'暫停錄影' in cam.name:
                    cam.name = cam.name.replace(u'(暫停錄影)', '')
                    cam.save()
            elif action == 'stop':
                if u'暫停錄影' not in cam.name:
                    cam.name += u'(暫停錄影)'
                    cam.save()

    return HttpResponseRedirect('/harbor/cam/show_password/#camera_%s'%cam.id)


# ////================================ following are AJAX function area ================================//// #

def matchAJAX(R, **kw):
    DATA = R.POST
    user = R.user
    submit = DATA.get('submit', None)
    result = json.dumps({'status': False, 'msg': "無此方法"})
    
    if 'getFishingPort' == submit:
        result = json.dumps(getFishingPort(DATA))
    elif 'addCam' == submit:
        result = json.dumps(addCam(DATA))
    elif 'makeCamMapBlock' == submit:
        result = json.dumps(makeCamMapBlock(DATA))
    elif 'makeCamImgBlock' == submit:
        result = makeCamImgBlock(DATA, user)
    elif 'getLogin' == submit:
        result = json.dumps(getLogin(DATA))
    elif 'runCamCmd' == submit:
        result = json.dumps(runCamCmd(DATA))
    elif 'runPreset' == submit:
        result = json.dumps(runPreset(DATA))
    elif 'cCamPreset' == submit:
        result = json.dumps(cCamPreset(DATA))
    elif 'uCamPreset' == submit:
        result = json.dumps(uCamPreset(DATA))
    elif 'dCamPreset' == submit:
        result = json.dumps(dCamPreset(DATA))
    elif 'makeCamEditBlock' == submit:
        result = makeCamEditBlock(DATA)
    elif 'uCamInfo' == submit:
        result = json.dumps(uCamInfo(DATA))
    elif 'dCam' == submit:
        result = json.dumps(dCam(DATA))
    elif 'gis_dump' == submit:
        result = json.dumps(gis_dump(DATA))
    elif 'show_password' == submit:
        result = json.dumps(show_password(R, DATA))

    
    return HttpResponse(result)


def show_password(R, DATA):
    user = R.user
    if not user.is_staff: return {'status': False, 'msg': '無權限'}

    cameras = []
    for m in Monitor.objects.filter(active=True).order_by('id'):
        for a in m.account_set.all().order_by('type'):
            h = {
                'id': m.id,
                'name': m.name,
                'machine_no': m.machine_no,
                'location': m.location,
                'ip': m.ip,
                'account': 'admin' if m.machine_no == 'PELCO-D' and a.account == 'fesadmin' else a.account,
                'passwd': 'a2285564' if m.machine_no == 'PELCO-D' and a.account == 'fesadmin' else a.passwd,
            }
            cameras.append(h)
    return {'status': True, 'cameras': cameras}


def getFishingPort(DATA):
    place = Place.objects.get(id=DATA.get('place', None))
    if DATA.get('state', None) == 'All':
        ports = FishingPort.objects.filter(place=place).order_by('id')
        sel_id = 'port'
    elif DATA.get('state', None) == 'Edit':
        cams = Monitor.objects.filter(place=place).order_by('id')
        sel_id = 'port_for_edit'
        ports = []
        for cam in cams:
            if cam.port not in ports:
                ports.append(cam.port)
    contents = ''
    contents += '<select id="' + sel_id + '" class="form-control">'
    if len(ports) > 0:
        for port in ports:
            contents += '<option value="' + str(port.id) + '" Lat="' + str(port.ycoord) + '" Lng="' + str(port.xcoord) + '">' + str(port.name) + '</option>'
    else:
        contents += '<option value="">此縣市尚無漁港</option>'
    contents += '</select>'
    return {'status': True, 'contents': contents}

def addCam(DATA):
    place = Place.objects.get(id=DATA.get('place', None))
    port = FishingPort.objects.get(id=DATA.get('port', None))
    name = DATA.get('name', None)
    machine_no = DATA.get('machine_no', None)
    lat = decimal.Decimal(str(DATA.get('lat', None)))
    lng = decimal.Decimal(str(DATA.get('lng', None)))
    location = DATA.get('location', None)
    if location=='':
        location = None
    IP = DATA.get('IP', None)
    video_url = DATA.get('video_url', '')
    account = DATA.get('account', None)
    passwd = DATA.get('passwd', None)
    monitors = Monitor.objects.filter(ip=IP)
    if monitors:
        return {'status': False, 'msg': '已有相同的 IP 位址存在，請再次確定。'}

    try:
        camera = CameraControl(machine_no.upper(), IP, account, passwd).camera
    except GeneralControl.LoginError:
        return {'status': False, 'msg': '無法登入攝影機，請檢查帳號密碼。'}
    except GeneralControl.TimeoutError:
        return {'status': False, 'msg': '無法連上攝影機，請檢查 IP。'}
    else:
        nweMonitor = Monitor(place=place, port=port, name=name,
                                machine_no=machine_no, lat=lat, lng=lng,
                                location=location, ip=IP, video_url=video_url)
        nweMonitor.save()
        AdminPasswd = '%08d' % int(100000000*random.random())
        OperPasswd = '%08d' % int(100000000*random.random())
        ViewPasswd = '%08d' % int(100000000*random.random())
        for (u, p, o) in (('fesadmin', AdminPasswd, Option.objects.get(swarm='account_type', value='Administrator')),
            ('fesoper', OperPasswd, Option.objects.get(swarm='account_type', value='Operator')),
            ('fesview', ViewPasswd, Option.objects.get(swarm='account_type', value='Viewer'))):
            try:
                camera.add_user(u, p, o)
            except GeneralControl.OperationError:
                return {'status': False, 'msg': '預設帳密權限不足，'
                        +'無法新增 fesadmin, fesoper, fesview 等帳號，'
                        +'請提供具管理者權限之帳號。'}
            else:
                nweAccount = Account(monitor=nweMonitor, account=u, passwd=p, type=o)
                nweAccount.save()
        return {'status': True, 'msg': '新增成功，並開設 fesadmin, fesoper, fesview 等帳號'}


def makeCamMapBlock(DATA):
    port = FishingPort.objects.get(id=DATA.get('area', None))
    lat= str(port.ycoord)
    lng= str(port.xcoord)
    monitors = Monitor.objects.filter(port=port)
    monitor_list = []
    for monitor in monitors:
        monitor_list.append({'id':str(monitor.id), 'lat':str(monitor.lat),
        'lng':str(monitor.lng), 'name':monitor.name, 'machine_no': monitor.machine_no,
        'location':monitor.location, 'ip':monitor.ip, 'video_url': monitor.video_url})
    if len(monitors) > 0: cam = True
    else: cam = False
    return {'status': True, 'cam': cam, 'lat': lat, 'lng': lng, 'monitor_list': monitor_list}


def makeCamImgBlock(DATA, user):
    cam = Monitor.objects.get(id=DATA.get('cam', None))
    Operator = Option.objects.get(swarm='account_type', value='Operator')
    OAccount = Account.objects.get(monitor=cam, type=Operator)
    Viewer = Option.objects.get(swarm='account_type', value='Viewer')
    VAccount = Account.objects.get(monitor=cam, type=Viewer)
    browser = DATA.get('browser', None)
    if browser == 'IE': IE = True
    else: IE = False

    try:
        camera = CameraControl(cam.machine_no, cam.ip, VAccount.account, VAccount.passwd).camera
    except:
        connect = False
    else:
        if 200 == camera.status: connect = True
        else: connect = False
    preset = Preset.objects.filter(monitor=cam).order_by('no')
    if user.is_staff or user.username in ['leondai294']:
        edit = True
    else:
        edit = False
    template = get_template(os.path.join('monitor', 'camimgblock.html'))
    html = template.render(RequestContext(DATA, {'cam': cam, 'connect': connect,
        'preset': preset, 'OAccount': OAccount, 'VAccount': VAccount,
        'edit': edit, 'IE': IE}))
    return html

def getLogin(DATA):
    cam = Monitor.objects.get(id=DATA.get('cam', None))
    Viewer = Option.objects.get(swarm='account_type', value='Viewer')
    VAccount = Account.objects.get(monitor=cam, type=Viewer)
    ip = cam.ip
    account = VAccount.account
    passwd = VAccount.passwd

    camera = CameraControl(cam.machine_no, ip, account, passwd).camera
    try:
        camera = CameraControl(cam.machine_no, ip, account, passwd).camera
    except:
        status = False
    else:
        if 200 == camera.status: status = True
        else: status = False

    return {'status': status, 'ip': ip, 'account': account, 'passwd': passwd}


def runCamCmd(DATA):
    cam = Monitor.objects.get(id=DATA.get('cam', None))
    Operator = Option.objects.get(swarm='account_type', value='Operator')
    OAccount = Account.objects.get(monitor=cam, type=Operator)
    camera = CameraControl(cam.machine_no, cam.ip, OAccount.account, OAccount.passwd).camera
    cmd = DATA.get('cmd', None)
    speed = DATA.get('speed', None)
    try: camera.ptz(cmd, speed)
    except: status = False
    else:
        if 200 == camera.status: status = True
        else: status = False
    return {'status': status}


def runPreset(DATA):
    cam = Monitor.objects.get(id=DATA.get('cam', None))
    Operator = Option.objects.get(swarm='account_type', value='Operator')
    OAccount = Account.objects.get(monitor=cam, type=Operator)
    camera = CameraControl(cam.machine_no, cam.ip, OAccount.account, OAccount.passwd).camera
    preset = DATA.get('preset', None)
    camera.run_preset(preset)
    if 200 == camera.status: status = True
    else: status = False
    return {'status': status}


def cCamPreset(DATA):
    cam = Monitor.objects.get(id=DATA.get('cam', None))
    Operator = Option.objects.get(swarm='account_type', value='Operator')
    OAccount = Account.objects.get(monitor=cam, type=Operator)
    presets = Preset.objects.filter(monitor=cam).order_by('no')
    if len(presets) > 0:
        for i in xrange(1,129):
            taken = False
            for preset in presets:
                if str(i) == preset.no:
                    taken = True
                    break
            if not taken:
                new_no = str(i)
                break
    else:
        new_no = str(1)

    camera = CameraControl(cam.machine_no, cam.ip, OAccount.account, OAccount.passwd).camera
    name = DATA.get('name', None)
    camera.create_preset(new_no)
    if camera.status == 200:
        nwePreset = Preset(monitor=cam, name=name, no=new_no)
        nwePreset.save()
        status = True
        presets = Preset.objects.filter(monitor=cam).order_by('id')
        content = makePresetSelection(presets, nwePreset.id)
    else:
        status = False
    return {'status': status, 'content': content}


def uCamPreset(DATA):
    cam = Monitor.objects.get(id=DATA.get('cam', None))
    Operator = Option.objects.get(swarm='account_type', value='Operator')
    OAccount = Account.objects.get(monitor=cam, type=Operator)
    camera = CameraControl(cam.machine_no, cam.ip, OAccount.account, OAccount.passwd).camera

    preset = Preset.objects.get(monitor=cam, no=DATA.get('preset', None))
    camera.update_preset(preset.no)
    name = DATA.get('name', None)
    if camera.status == 200:
        setattr(preset, 'name', name)
        preset.save()
        status = True
        presets = Preset.objects.filter(monitor=cam).order_by('id')
        content = makePresetSelection(presets, preset.id)
    else:
        status = False
    return {'status': status, 'content': content}


def dCamPreset(DATA):
    cam = Monitor.objects.get(id=DATA.get('cam', None))
    Operator = Option.objects.get(swarm='account_type', value='Operator')
    OAccount = Account.objects.get(monitor=cam, type=Operator)
    camera = CameraControl(cam.machine_no, cam.ip, OAccount.account, OAccount.passwd).camera
    preset = Preset.objects.get(monitor=cam, no=DATA.get('preset', None))
    camera.delete_preset(preset.no)
    if camera.status == 200:
        preset.delete()
        status = True
        presets = Preset.objects.filter(monitor=cam).order_by('id')
        content = makePresetSelection(presets, '')
    else:
        status = False
    return {'status': status, 'content': content}

def makeCamEditBlock(DATA):
    cams = Monitor.objects.all()
    place_list = []
    for cam in cams:
        if cam.place not in place_list:
            place_list.append(cam.place)
    template = get_template(os.path.join('monitor', 'cameditblock.html'))
    html = template.render(RequestContext(DATA, {'place_list': place_list,}))
    return html

def uCamInfo(DATA):
    cam = Monitor.objects.get(id=DATA.get('cam', None))
    name = DATA.get('name', None)
    machine_no = DATA.get('machine_no', None)
    location = DATA.get('location', None)
    ip = DATA.get('ip', None)
    video_url = DATA.get('video_url', None)
    lat = DATA.get('lat', None)
    lng = DATA.get('lng', None)
    setattr(cam, 'name', name)
    setattr(cam, 'machine_no', machine_no)
    setattr(cam, 'location', location)
    setattr(cam, 'ip', ip)
    setattr(cam, 'video_url', video_url)
    setattr(cam, 'lat', lat)
    setattr(cam, 'lng', lng)
    cam.save()
    return {'status': True}

def dCam(DATA):
    cam = Monitor.objects.get(id=DATA.get('cam', None))
    cam.delete()
    return {'status': True}

def gis_dump(DATA):
    cams = Monitor.objects.all()
    cam_list = []
    for cam in cams:
        cam_list.append({'lat': str(cam.lat), 'lng': str(cam.lng), 'name': cam.name, 'title': cam.name, 'url': '/harbor/portcam/'+str(cam.port.id) })
    return {'status': True, 'camera': cam_list}


def uQuality(R):
    try:
        cam = Monitor.objects.get(id=R.GET.get('id', 0))
    except Monitor.DoesNotExist:
        try:
            cam = Monitor.objects.get(ip=R.GET.get('ip', 0))
        except Monitor.DoesNotExist:
            return HttpResponseForbidden('')
    Admin_type = Option.objects.get(swarm='account_type', value='Administrator')
    AAccount = Account.objects.get(monitor=cam, type=Admin_type)
    account = AAccount.account
    passwd = AAccount.passwd
    if cam.machine_no == 'PELCO-D':
        account, passwd = 'admin', 'a2285564'
    camera = CameraControl(cam.machine_no, cam.ip, account, passwd).camera
    camera.update_quality(R.GET.get('type', 'middle'))
    return HttpResponse('')


def stop_watch_monitor():
    i = 0
    T = 0
    for m in Monitor.objects.all().order_by('id'):
        if m.ip in ['220.130.187.55', '210.59.162.247', '211.72.223.22']: continue
        if m.machine_no == 'PELCO-D':
            speed = '0'
        else:
            speed = '0C'
        i += 1
        ip = m.ip
        a = m.account_set.get(type__value='Administrator')
        account = a.account if m.machine_no != 'PELCO-D' else 'admin'
        password = a.passwd if m.machine_no != 'PELCO-D' else 'a2285564'
        camera = CameraControl(m.machine_no, ip, account, password).camera
        t0 = time()
        camera.ptz('Left', speed)
        camera.ptz('Stop', speed)
        t = time() - t0
        print i, m.id, m.name, m.machine_no, ip, t
        T += t
    print u'平均時間: %s' % (T / i)

    u"""
未開啟錄影前，在中興大學電腦上：
    1 碧砂漁港魚貨直銷中心 BE3204 211.72.223.133 0.814496994019
    2 頭城區漁會 BE3204 61.220.216.214 0.180932998657
    3 臺中梧棲漁港 BE3204 211.72.239.7 0.207957983017
    4 烏石漁港魚貨直銷中心 BE3204 61.221.43.1 0.18022608757
    5 新竹區漁會-no2 PELCO-D 211.20.114.106 0.365556001663
    6 屏東縣東港區漁會 PELCO-D 203.69.17.148 0.540233135223
    7 屏東縣漁業通訊電台 PELCO-D 203.69.17.4 0.469913005829
    8 高雄漁業署本部-no2 PELCO-D 210.61.241.69 0.36278295517
    9 前鎮漁港魚貨直銷中心 PELCO-D 211.75.254.206 0.37303519249
    10 臺中梧棲漁港管理所 PELCO-D 210.61.91.235 0.438500881195
    11 蘇澳區漁會 PELCO-D 60.250.219.52 0.408967018127
    12 拍賣魚市場 PELCO-D 60.250.219.19 0.359298944473
    13 活魚儲運中心 PELCO-D 60.249.220.76 0.417838096619
    14 中油加油站 PELCO-D 220.130.231.145 0.458837032318
    15 臺東區漁會 PELCO-D 61.219.157.16 0.523647069931
    16 海洋巡防總局第十五海巡隊 PELCO-D 61.219.156.163 0.469175815582
    17 金城里活動中心 PELCO-D 211.23.244.109 0.469434976578
    18 新竹區漁會-no1 PELCO-D 211.20.114.105 0.378146886826
    平均時間: 0.412165615294


未開啟錄影前，在漁業署電腦上：
    1 碧砂漁港魚貨直銷中心 BE3204 211.72.223.133 0.764128923416
    2 頭城區漁會 BE3204 61.220.216.214 0.17414188385
    3 臺中梧棲漁港 BE3204 211.72.239.7 0.177263021469
    4 烏石漁港魚貨直銷中心 BE3204 61.221.43.1 0.130656003952
    5 新竹區漁會-no2 PELCO-D 211.20.114.106 0.347023963928
    6 屏東縣東港區漁會 PELCO-D 203.69.17.148 0.685631036758
    7 屏東縣漁業通訊電台 PELCO-D 203.69.17.4 0.460276126862
    8 高雄漁業署本部-no2 PELCO-D 210.61.241.69 0.30995798111
    9 前鎮漁港魚貨直銷中心 PELCO-D 211.75.254.206 0.306966781616
    10 臺中梧棲漁港管理所 PELCO-D 210.61.91.235 0.445891857147
    11 蘇澳區漁會 PELCO-D 60.250.219.52 0.375577926636
    12 拍賣魚市場 PELCO-D 60.250.219.19 0.339953899384
    13 活魚儲運中心 PELCO-D 60.249.220.76 0.41280412674
    14 中油加油站 PELCO-D 220.130.231.145 0.608150005341
    15 臺東區漁會 PELCO-D 61.219.157.16 3.46904706955
    16 海洋巡防總局第十五海巡隊 PELCO-D 61.219.156.163 0.417391061783
    17 金城里活動中心 PELCO-D 211.23.244.109 0.412853002548
    18 新竹區漁會-no1 PELCO-D 211.20.114.105 0.297457933426
    平均時間: 0.563065144751
    """




if __name__ == '__main__':
    stop_watch_monitor()
