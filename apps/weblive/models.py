# -*- coding:utf8 -*-
import datetime, urllib
from django.conf import settings
from django.db import models as M


def NOW(): return datetime.datetime.now()


class Place(M.Model):
    """
        CREATE VIEW fesweblive.weblive_place (id, fes_id, name, zipcode, parent_id, update_time)
            as
            select id, id, name, zipcode, uplevel_id, update_time
                from fes.general_place;
    """
    fes_id = M.IntegerField(verbose_name=u'fes row id')
    name = M.CharField(verbose_name=u'區域名稱', null=False, max_length=128)
    zipcode = M.CharField(verbose_name=u'郵遞區號', max_length=20)
    parent = M.ForeignKey('self', null=True, related_name='child_set')
    update_time = M.DateTimeField(verbose_name='update_time of FES row', null=True)



class FishingPort(M.Model):
    """
        CREATE VIEW fesweblive.weblive_fishingport
            (id, fes_id, name, code, xcoord, ycoord, place_id, update_time)
            as
            select id, id, name, code, xcoord, ycoord, place_id, update_time
                from fes.harbor_fishingport;
    """
    #漁港資料
    fes_id = M.IntegerField(verbose_name=u'fes row id')
    name = M.CharField(verbose_name='漁港名稱', null=False, max_length=256)
    code = M.CharField(verbose_name='漁港代碼', null=False, max_length=256)
    xcoord = M.DecimalField(verbose_name='X座標', null=True , max_digits=20 , decimal_places=12)
    ycoord = M.DecimalField(verbose_name='y座標', null=True , max_digits=20 , decimal_places=12)
    place = M.ForeignKey(Place, verbose_name='縣市')
    update_time = M.DateTimeField(verbose_name='update_time of FES row', null=True)



class Control(object):
    class TimeoutError(Exception): pass
    class LoginError(Exception): pass
    class OperationError(Exception): pass



    def read_url(self, url):
        self.url = url
        if hasattr(settings, 'FES_PROXY'):
            proxies = {'http': settings.FES_PROXY}
            R = urllib.urlopen(url, proxies=proxies)
        else:
            R = urllib.urlopen(url)
        #url = 'http://%s:%s@%s%s' % (self.user, self.passwd, self.IP, request)
        status = self.status = R.getcode()
        if status in [408, 504]:
            raise self.TimeoutError
        elif 200 != int(status):
            raise self.OperationError
        return status



class BE3204Control(Control):
    def __init__(self, ip, login):
        self.ip = ip
        self.login = login


    def get_view_url(self):
        url = "http://%s@%s/ipcam/mjpeg.cgi" % (self.login, self.ip)
        return url


    def run_preset(self, preset_no):
        preset_no = '%02d' % int(preset_no)
        url = "http://" + self.ip + "/vb.htm?login=" + self.login + "&dv840output=A0000700" + preset_no
        return self.read_url(url)



class PELCODControl(Control):
    def __init__(self, ip, login):
        self.ip = ip
        self.login = login



    def get_view_url(self):
        url = "http://%s@%s/GetData.cgi?CH=1" % (self.login, self.ip)
        return url


    def run_preset(self, preset_no):
        cmd = "Dir=Point"+preset_no;
        url = 'http://'+self.login+'@'+self.ip+"/SetPTZ.cgi?"+cmd;
        return self.read_url(url)



class Monitor(M.Model):
    """
        CREATE VIEW fesweblive.weblive_monitor
            (id, fes_id, machine_no, place_id, port_id, name, location, video_url, lat, lng, ip, active, update_time)
            as
            select id, id,  machine_no, place_id, port_id, name, location, video_url, lat, lng, ip, active, update_time
                from fes.monitor_monitor;
    """
    fes_id = M.IntegerField(verbose_name=u'fes row id')
    machine_no = M.CharField(verbose_name=u'供應機型', choices=(('BE3204', 'BE3204'), ), null=False, max_length=16)# 新增欄位， for 不同機型須有不同的直播方法
    place = M.ForeignKey(Place, verbose_name='縣市', null=True)
    port = M.ForeignKey(FishingPort, verbose_name='漁港', null=True)
    #nvr_id = M.IntegerField(verbose_name=u'NVR 系統編號', null=True)# 新增欄位，不限藍眼機器使用，如果將來我們會買其他人的 NVR 的話(這怎麼可能!!! 我們會自己作 NVR)
    name = M.CharField(verbose_name='名稱', null=True, max_length=512)
    #channel = M.CharField(verbose_name='廣播頻道', null=True, max_length=512)# 新增欄位，它似乎可視為機器的 UUID
    location = M.CharField(verbose_name='位置敘述', null=True, max_length=512)
    video_url = M.CharField(verbose_name='影片儲存位置', null=True, max_length=512)
    lat = M.DecimalField(verbose_name='緯度', null=True , max_digits=20 , decimal_places=12)
    lng = M.DecimalField(verbose_name='經度', null=True , max_digits=20 , decimal_places=12)
    ip = M.CharField(verbose_name='IP位置', null=True, max_length=256)
    active = M.BooleanField(verbose_name='啟用與否', default=True)
    #viewer_key = M.CharField(verbose_name='使用者金鑰', null=True, max_length=512)# 新增欄位，有些問題要問 adrian
    update_time = M.DateTimeField(verbose_name='update_time of FES row', null=True)


    def get_view_url(self):
        try: account = self.account_set.get(type=3)
        except: return ''
        c = self.get_camera_control(account.account, account.passwd)
        return c.get_view_url()


    def get_camera_control(self, username, password):
        if self.machine_no == 'BE3204':
            self.camera_control = BE3204Control(self.ip, '%s:%s'%(username, password))
        elif self.machine_no == 'PELCO-D':
            self.camera_control = PELCODControl(self.ip, '%s:%s'%(username, password));
        return self.camera_control


    def count_alive(self):
        count = 0
        exist_uuid = []
        for al in self.alivelog_set.filter(create_time__gte=NOW()-datetime.timedelta(seconds=15)):
            if al.uuid not in exist_uuid:
                count += 1
                exist_uuid.append(al.uuid)
        return count


    def lastest_alive_log_time(self):
        log = self.alivelog_set.filter(create_time__gte=NOW()-datetime.timedelta(seconds=15)).order_by('-create_time')
        if log.count():
            return log[0].create_time
        else:
            return None



class SyncLog(M.Model):
    model_name = M.CharField(max_length=64)
    count = M.IntegerField(default=0)
    running_second = M.IntegerField(default=0)
    maximal_update_time = M.DateTimeField(verbose_name=u'update_time of FES row', null=True)
    create_time = M.DateTimeField(auto_now_add=True)
    done_time = M.DateTimeField(auto_now=True)



class Account(M.Model):
    """
        CREATE VIEW fesweblive.weblive_account
            (id, fes_id, monitor_id, account, passwd, type, update_time)
            as
            select id, id, monitor_id, account, passwd, type_id, update_time
                from fes.monitor_account;
    """
    # 一攝影機即為一伺服器，其帳號權限有三：Administrator、Operator、Viewer(Syntax Index ：1, 2, 3)
    fes_id = M.IntegerField(verbose_name=u'fes row id')
    monitor = M.ForeignKey(Monitor, verbose_name='攝影機')
    account = M.CharField(verbose_name='帳號', null=True, max_length=256)
    passwd = M.CharField(verbose_name='密碼', null=True, max_length=256)
    type = M.IntegerField(verbose_name='帳號類別', null=True)
    update_time = M.DateTimeField(verbose_name='update_time of FES row', null=True)


class Preset(M.Model):
    """
        CREATE VIEW fesweblive.weblive_preset
        (id, fes_id, monitor_id, name, no, update_time)
            as
            select id, id, monitor_id, name, no, update_time
                from fes.monitor_preset;
    """
    fes_id = M.IntegerField(verbose_name=u'fes row id')
    monitor = M.ForeignKey(Monitor, verbose_name='攝影機')
    name = M.CharField(verbose_name='設定名稱', null=True, max_length=256)
    no = M.CharField(verbose_name='設定對應碼', null=True, max_length=256)
    update_time = M.DateTimeField(verbose_name='update_time of FES row', null=True)


    def __str__(self):
        return '%s. %s' % (self.no, self.name)


    def __unicode__(self):
        return u'%s. %s' % (self.no, self.name)


class AliveLog(M.Model):
    monitor = M.ForeignKey(Monitor, verbose_name='攝影機')
    uuid = M.CharField(verbose_name=u'UUID', null=False, max_length=256)
    create_time = M.DateTimeField(auto_now_add=True)
