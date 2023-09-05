#-*- coding:utf8 -*-

from django.db import models as M
from django.contrib.auth.models import User
from general.models import Place, Unit
import os
from PIL import Image
from common.lib import calsize
from common.templatetags.utiltags import thumb
import cmath
from math import radians
from math import sin
from math import cos
from math import tan
from math import pow

'''
這是純粹儲存漁港、縣市等資訊的展示資料
包含可擴充的特性，目前的工作為將DBMaker的資料，轉換成為SQL的資料
最後再開始決定頁面如何展示這些資料
'''


class Option(M.Model):
    swarm= M.CharField(verbose_name='群', max_length=32)
    value = M.CharField(verbose_name='選項', max_length=64)

    def __unicode__(self):
        return '%s-%s' % (self.swarm, self.value)

    class Meta:
        verbose_name = '選項'
        verbose_name_plural = '選項'
        unique_together = (("swarm", "value"),)


_UPLOAD_TO = os.path.join('apps', 'harbor', 'media', 'harbor')
class Observatory(M.Model):
    #觀測站
    name = M.CharField(verbose_name='測站名稱', null=False, max_length=256)
    wind_memo = M.CharField(verbose_name='風花圖說明', null=True, max_length=1024)
    rainday_memo = M.CharField(verbose_name='月平均降雨日數說明', null=True, max_length=1024)
    file = M.ImageField(upload_to=os.path.join(_UPLOAD_TO, 'observatory'), null=True)
    extname = M.CharField(verbose_name='副檔名', max_length=256, null=True, default='')

    def rUrl(self):
        if self.file:
            return self.file.name.split('apps/harbor')[-1]
        else:
            return ''

class FishingPort(M.Model):
    #漁港資料
    name = M.CharField(verbose_name='漁港名稱', null=False, max_length=256)
    code = M.CharField(verbose_name='漁港代碼', null=False, max_length=256)
    xcoord = M.DecimalField(verbose_name='X座標', null=True , max_digits=20 , decimal_places=12)
    ycoord = M.DecimalField(verbose_name='y座標', null=True , max_digits=20 , decimal_places=12)
    place = M.ForeignKey(Place, verbose_name='縣市')
    type = M.ForeignKey(Option, verbose_name='第幾類漁港')
    observatory = M.ForeignKey(Observatory, verbose_name='觀測站', null=True)
    location = M.CharField(verbose_name='地理位置', null=True, max_length=4096)
    history = M.CharField(verbose_name='建港沿革', null=True, max_length=4096)
    range = M.CharField(verbose_name='漁港區域範圍', null=True, max_length=4096)
    update_time = M.DateTimeField(auto_now=True)

    def twd97(self):
        if self.xcoord == None or self.ycoord == None:
            class C(): (x, y) = ('','')
        else:
            lon = radians(float(self.xcoord))
            lat = radians(float(self.ycoord))
            a = 6378137.0
            b = 6356752.314245
            long0 = radians(121)
            k0 = 0.9999
            dx = 250000
            e = (1-b**2/a**2)**0.5
            e2 = e**2/(1-e**2)
            n = (a-b)/(a+b)
            nu = a/(1-(e**2)*(sin(lat)**2))**0.5
            p = lon-long0
            A = a*(1 - n + (5/4.0)*(n**2 - n**3) + (81/64.0)*(n**4  - n**5))
            B = (3*a*n/2.0)*(1 - n + (7/8.0)*(n**2 - n**3) + (55/64.0)*(n**4 - n**5))
            C = (15*a*(n**2)/16.0)*(1 - n + (3/4.0)*(n**2 - n**3))
            D = (35*a*(n**3)/48.0)*(1 - n + (11/16.0)*(n**2 - n**3))
            E = (315*a*(n**4)/51.0)*(1 - n)
            S = A*lat - B*sin(2*lat) + C*sin(4*lat) - D*sin(6*lat) + E*sin(8*lat)
            K1 = S*k0
            K2 = k0*nu*sin(2*lat)/4.0
            K3 = (k0*nu*sin(lat)*(cos(lat)**3)/24.0) * \
                (5 - tan(lat)**2 + 9*e2*(cos(lat)**2) + 4*(e2**2)*(cos(lat)**4))
            Y = K1 + K2*(p**2) + K3*(p**4)
            K4 = k0*nu*cos(lat)
            K5 = (k0*nu*(cos(lat)**3)/6.0) * \
                (1 - tan(lat)**2 + e2*(cos(lat)**2))
            X = K4*p + K5*(p**3) + dx

            class C(): (x, y) = (int(X),int(Y))
        return C()

    def twd97_2_googlemap(self):
        # ref from: http://blog.ez2learn.com/2009/08/15/lat-lon-to-twd97/
        # Cerberus: This code is for TWD97 cartesian transfer to a WGS84 base coordinates. This code can
        # get a similar answer, but it is not tested and verified.
        x = self.xcoord and self.xcoord or 0
        y = self.ycoord and self.ycoord or 0
        x = float(str(x))
        y = float(str(y))
        a = 6378137.0
        b = 6356752.314245
        lon0 = 121/180*3.1415
        k0 = 0.9999
        dx = 250000
        dy = 0
        e = (1-b**2/a**2)**0.5
        M = y/k0
        x = x - dx
        mu = M/(a*(1.0 - pow(e, 2)/4.0 - 3*pow(e, 4)/64.0 - 5*pow(e, 6)/256.0))
        e1 = (1.0 - pow((1.0 - pow(e, 2)), 0.5)) / (1.0 + pow((1.0 - pow(e, 2)), 0.5))
        J1 = (3*e1/2 - 27*pow(e1, 3)/32.0)
        J2 = (21*pow(e1, 2)/16 - 55*pow(e1, 4)/32.0)
        J3 = (151*pow(e1, 3)/96.0)
        J4 = (1097*pow(e1, 4)/512.0)
        fp = mu + J1*cmath.sin(2*mu) + J2*cmath.sin(4*mu) + J3*cmath.sin(6*mu) + J4*cmath.sin(8*mu);
        # Calculate Latitude and Longitude
        e2 = pow((e*a/b), 2);
        C1 = pow(e2*cmath.cos(fp), 2);
        T1 = pow(cmath.tan(fp), 2);
        R1 = a*(1-pow(e, 2))/pow((1-pow(e, 2)*pow(cmath.sin(fp), 2)), (3.0/2.0));
        N1 = a/pow((1-pow(e, 2)*pow(cmath.sin(fp), 2)), 0.5);
        D = x/(N1*k0);
        # lat
        Q1 = N1*cmath.tan(fp)/R1;
        Q2 = (pow(D, 2)/2.0);
        Q3 = (5 + 3*T1 + 10*C1 - 4*pow(C1, 2) - 9*e2)*pow(D, 4)/24.0;
        Q4 = (61 + 90*T1 + 298*C1 + 45*pow(T1, 2) - 3*pow(C1, 2) - 252*e2)*pow(D, 6)/720.0;
        lat = fp - Q1*(Q2 - Q3 + Q4);
        # long
        Q5 = D;
        Q6 = (1 + 2*T1 + C1)*pow(D, 3)/6;
        Q7 = (5 - 2*C1 + 28*T1 - 3*pow(C1, 2) + 8*e2 + 24*pow(T1, 2))*pow(D, 5)/120.0;
        lon = lon0 + (Q5 - Q6 + Q7)/cmath.cos(fp);
        lat = (lat/(cmath.pi)*180).real
        lon = (lon/(cmath.pi)*180 + 121).real
        return lat, lon


class PortFisheryOutput(M.Model):
    #漁港歷年漁業產量
    fishingport = M.ForeignKey(FishingPort, verbose_name='漁港')
    year = M.IntegerField(verbose_name='年度', null=True)
    output = M.IntegerField(verbose_name='產量(公噸)', null=True)
    value = M.IntegerField(verbose_name='產值(千元)', null=True)


class FishingPortBoat(M.Model):
    #漁船資料
    fishingport = M.ForeignKey(FishingPort, verbose_name='漁港')
    year = M.IntegerField(verbose_name='年度', null=True)
    boat_type = M.ForeignKey(Option, verbose_name='漁船種類')
    num = M.IntegerField(verbose_name='數量', null=True)


class MainProject(M.Model):
    #歷年主要工程項目
    fishingport = M.ForeignKey(FishingPort, verbose_name='漁港')
    year = M.CharField(verbose_name='年度', null=True, max_length=1024)
    item = M.CharField(verbose_name='項目', null=True, max_length=1024)
    num = M.CharField(verbose_name='數量', null=True, max_length=1024)
    memo = M.CharField(verbose_name='備註', null=True, max_length=1024)


class Project(M.Model):
    # 歷年工程計畫
    name = M.CharField(verbose_name='工程名稱', null=False, max_length=256)
    year = M.IntegerField(verbose_name='年度', null=True)
    fishingport = M.ForeignKey(FishingPort, verbose_name='漁港')
    note = M.CharField(verbose_name='備註', null=True, max_length=1024)
    plan = M.CharField(verbose_name='計畫名稱', null=True, max_length=1024)
    schedule_item = M.CharField(verbose_name='預定工作項目', null=True, max_length=1024)
    reality_item = M.CharField(verbose_name='實際工作項目', null=True, max_length=1024)
    funds_source = M.CharField(verbose_name='經費來源', null=True, max_length=1024)
    funds = M.IntegerField(verbose_name='經費', null=True)
    plan_fund = M.IntegerField(verbose_name='計畫經費', null=True)
    reality_budget_fund = M.IntegerField(verbose_name='實列預算經費', null=True)
    supply_material_fund = M.IntegerField(verbose_name='供給材料經費', null=True)
    manage_fund = M.IntegerField(verbose_name='管理經費', null=True)
    other_fund = M.IntegerField(verbose_name='其它經費', null=True)
    contract_fund = M.IntegerField(verbose_name='發包工作費', null=True)
    first_change_design = M.IntegerField(verbose_name='一次追加變更設計費', null=True)
    second_change_design = M.IntegerField(verbose_name='二次追加變更設計費', null=True)
    settlement_fund = M.IntegerField(verbose_name='結算經費', null=True)
    contract_date = M.DateField(verbose_name='發包日期', null=True)
    design_finish_date = M.DateField(verbose_name='預定完工日期', null=True)
    first_change_design_date = M.DateField(verbose_name='第一次追加日期', null=True)
    second_change_design_date = M.DateField(verbose_name='第二次追加日期', null=True)
    act_finish_date = M.DateField(verbose_name='實際完工日期', null=True)


class Waves(M.Model):
    #波浪
    fishingport = M.ForeignKey(FishingPort, verbose_name='漁港')
    type = M.CharField(verbose_name='類別', null=True, max_length=256)
    angle = M.CharField(verbose_name='波向', null=True, max_length=256)
    high = M.DecimalField(verbose_name='波高(M)', max_digits=10 , decimal_places=2)
    cycle = M.DecimalField(verbose_name='週期', max_digits=10 , decimal_places=2)


class Tide(M.Model):
    #潮汐
    fishingport = M.ForeignKey(FishingPort, verbose_name='漁港')
    max_tide = M.DecimalField(verbose_name='最高潮位', null=True , max_digits=16 , decimal_places=2)
    big_tide_hign_avg = M.DecimalField(verbose_name='大潮平均高潮位', null=True , max_digits=16 , decimal_places=2)
    small_tide_hign_avg = M.DecimalField(verbose_name='小潮平均高潮位', null=True , max_digits=16 , decimal_places=2)
    tide_avg = M.DecimalField(verbose_name='平均潮位', null=True , max_digits=16 , decimal_places=2)
    big_tide_down_avg = M.DecimalField(verbose_name='大潮平均低潮位', null=True , max_digits=16 , decimal_places=2)
    small_tide_down_avg = M.DecimalField(verbose_name='小潮平均低潮位', null=True , max_digits=16 , decimal_places=2)
    min_tide = M.DecimalField(verbose_name='最低潮位', null=True , max_digits=16 , decimal_places=2)
    zero_elevation = M.DecimalField(verbose_name='築港高程零點', null=True, max_digits=16 , decimal_places=2)
    memo = M.CharField(verbose_name='備註欄', null=True, max_length=1024)


_PORT_UPLOAD_TO = os.path.join(_UPLOAD_TO, 'fishingportphoto', 'harbor', '%Y%m%d')
class FishingPortPhoto(M.Model):
    fishingport = M.ForeignKey(FishingPort, verbose_name='漁港')
    type = M.ForeignKey(Option, verbose_name='照片種類')
    name = M.CharField(verbose_name='檔案名', max_length=256, null=True, default='')
    file = M.ImageField(upload_to=_PORT_UPLOAD_TO, null=True)
    extname = M.CharField(verbose_name='副檔名', max_length=256, null=True, default='')
    memo = M.CharField(verbose_name='備註說明', null=True, max_length=2048)

    def rUrl(self):
        return self.file.name.split('apps/harbor/')[-1]

    def rThumbUrl(self):

        thumbsrc = thumb(self.file.name, "width=1024,height=768")
        if thumbsrc == 'media/images/error.png':
            return self.file.name.split('apps/harbor/')[-1]
        else:
            return thumbsrc.split('apps/harbor/')[-1]

    def calSize(self):
        if self.file:
            return calsize(self.file.size)
        else:
            return calsize(0)

        
class AverageRainfall(M.Model):
    #平均降雨量
    observatory = M.ForeignKey(Observatory, verbose_name='觀測站')
    month = M.IntegerField(verbose_name='月份')
    rain_average = M.DecimalField(verbose_name='平均降雨量', default=0 , max_digits=16 , decimal_places=2)
    rain_memo = M.CharField(verbose_name='平均雨量說明', null=True, max_length=1024)
    day_average = M.DecimalField(verbose_name='平均降雨日數', default=0 , max_digits=16 , decimal_places=2)
    day_memo = M.CharField(verbose_name='平均降雨日數說明', null=True, max_length=1024)


class AverageTemperature(M.Model):
    #平均氣溫
    observatory = M.ForeignKey(Observatory, verbose_name='觀測站')
    memo = M.CharField(verbose_name='平均氣溫說明', null=True, max_length=1024)
    month = M.IntegerField(verbose_name='月份')
    min = M.DecimalField(verbose_name='測站最低氣溫', default=0 , max_digits=16 , decimal_places=2)
    max = M.DecimalField(verbose_name='測站最高氣溫', default=0 , max_digits=16 , decimal_places=2)
    average = M.DecimalField(verbose_name='測站平均氣溫', default=0 , max_digits=16 , decimal_places=2)


class AveragePressure(M.Model):
    #平均氣壓
    observatory = M.ForeignKey(Observatory, verbose_name='觀測站')
    memo = M.CharField(verbose_name='平均氣溫說明', null=True, max_length=1024)
    month = M.IntegerField(verbose_name='月份')
    min = M.DecimalField(verbose_name='測站最低氣壓', default=0 , max_digits=16 , decimal_places=2)
    max = M.DecimalField(verbose_name='測站最高氣壓', default=0 , max_digits=16 , decimal_places=2)
    average = M.DecimalField(verbose_name='測站平均氣壓', default=0 , max_digits=16 , decimal_places=2)
    sea_average = M.DecimalField(verbose_name='海平面平均氣壓', default=0 , max_digits=16 , decimal_places=2)


class City(M.Model):
    #縣市資料
    place = M.ForeignKey(Place, verbose_name='縣市')
    people = M.CharField(verbose_name='人文概述', null=True, max_length=4096)
    fishingport_location = M.CharField(verbose_name='漁港位置', null=True, max_length=4096)

    def rPortinList(self):
        return [port for port in FishingPort.objects.filter(place=self.place)]

    def rPortNum(self):
        return FishingPort.objects.filter(place=self.place).count()


class FisheryOutput(M.Model):
    #縣市歷年漁業產量
    place = M.ForeignKey(Place, verbose_name='縣市')
    year = M.IntegerField(verbose_name='年度', null=True)
    aquaculture_num = M.IntegerField(verbose_name='養殖數量(噸數)', null=True)
    aquaculture_value = M.IntegerField(verbose_name='養殖價值(仟元)', null=True)
    coastwise_num = M.IntegerField(verbose_name='沿岸數量(噸數)', null=True)
    coastwise_value = M.IntegerField(verbose_name='沿岸價值(仟元)', null=True)
    inshore_num = M.IntegerField(verbose_name='近海數量(噸數)', null=True)
    inshore_value = M.IntegerField(verbose_name='近海價值(仟元)', null=True)
    pelagic_num = M.IntegerField(verbose_name='遠洋數量(噸數)', null=True)
    pelagic_value = M.IntegerField(verbose_name='遠洋價值(仟元)', null=True)


class FishType(M.Model):
    #魚類別
    place = M.ForeignKey(Place, verbose_name='縣市')
    fish = M.CharField(verbose_name='魚類別', null=False, max_length=256)
    output = M.IntegerField(verbose_name='產量(公噸)', null=True)
    value = M.IntegerField(verbose_name='產值(千元)', null=True)


class FisheryType(M.Model):
    #漁業別
    place = M.ForeignKey(Place, verbose_name='縣市')
    fishery = M.CharField(verbose_name='漁業別', null=False, max_length=256)
    output = M.IntegerField(verbose_name='產量(公噸)', null=True)
    value = M.IntegerField(verbose_name='產值(千元)', null=True)


class AquaculturePublic(M.Model):
    #養殖工程歷年公共設施項目
    year = M.IntegerField(verbose_name='年度')
    place = M.ForeignKey(Place, verbose_name='縣市')
    project_name = M.CharField(verbose_name='工程名稱', null=False, max_length=256)
    contents = M.CharField(verbose_name='工程項目', null=True, max_length=1024)
    value = M.DecimalField(verbose_name='工程經費(萬元)', default=0 , max_digits=16 , decimal_places=2)
    memo = M.CharField(verbose_name='備註', null=True, max_length=4096)


class AquaculturePublicWork(M.Model):
    #養殖漁業公共工程
    year = M.IntegerField(verbose_name='年度')
    place = M.ForeignKey(Place, verbose_name='縣市')
    area = M.CharField(verbose_name='生產區', null=True, max_length=256)
    project_item = M.CharField(verbose_name='工程項目', null=True, max_length=256)
    unit = M.CharField(verbose_name='單位', null=True, max_length=20)
    project_num = M.DecimalField(verbose_name='工程數量', default=0 , max_digits=16 , decimal_places=2)
    project_cost = M.DecimalField(verbose_name='工程金額(萬元)', default=0 , max_digits=16 , decimal_places=2)
    memo = M.CharField(verbose_name='備註', null=True, max_length=2048)


class PortInstallationRecord(M.Model):
    #漁港設施記錄
    fishingport = M.ForeignKey(FishingPort, verbose_name='漁港')
    organization = M.ForeignKey(Unit, verbose_name='漁會別', null=True)
    date = M.DateField(verbose_name='填表日期')
    time = M.TimeField(verbose_name=u'填表時間', null=True)
    arrival_port = M.IntegerField(verbose_name='船舶進港艘數', null=True)
    leave_port = M.IntegerField(verbose_name='船舶出港艘數', null=True)
    anchor = M.IntegerField(verbose_name='泊區停泊艘數', null=True)
    boat_supplies = M.ForeignKey(Option, verbose_name='船隻補給情形(加油加水加冰)', null=True, related_name='boat_supplies')
    boat_supplies_memo = M.CharField(verbose_name='補給備註', null=True, max_length=2048)
#    inport_boat_supplies = M.CharField(verbose_name='輸入船隻補給情形(加油加水加冰)', null=True, max_length=256)
    port_environment = M.ForeignKey(Option, verbose_name='港區環境清潔情形', null=True, related_name='port_environment')
#    inport_port_environment = M.CharField(verbose_name='輸入港區環境清潔情形', null=True, max_length=256)
    emergency_measures = M.ForeignKey(Option, verbose_name='港區突發情形處理方式', null=True, related_name='emergency_measures')
#    inport_emergency_measures = M.CharField(verbose_name='輸入港區突發情形處理方式', null=True, max_length=256)
    emergency = M.ForeignKey(Option, verbose_name='港區突發情況', null=True, related_name='emergency')
#    inport_emergency = M.CharField(verbose_name='輸入港區突發情況', null=True, max_length=256)
    memo = M.CharField(verbose_name='備註', null=True, max_length=2048)

    def rTotalBoat(self):
        #船舶進出港總艘數
        total = self.arrival_port + self.leave_port
        return total

    def rAvgBoat(self):
        #船舶進出港平均數
        avg = self.rTotalBoat()/2.0
        return avg


_FILE_UPLOAD_TO = os.path.join(_UPLOAD_TO, 'tempfile', '%Y%m%d')
class TempFile(M.Model):
    #臨時檔案上傳區
    upload_user = M.ForeignKey(User, verbose_name='上傳者')
    fishingport = M.ForeignKey(FishingPort, verbose_name='漁港')
    upload_date = M.DateField(verbose_name='上傳日期')
    name = M.CharField(verbose_name='檔案名', max_length=256, null=True, default='')
    file = M.ImageField(upload_to=_FILE_UPLOAD_TO, null=True)
    memo = M.CharField(verbose_name='備註說明', null=True, max_length=2048)

    def rUrl(self):
        return self.file.name.split('apps/harbor/')[-1]

    def rThumbUrl(self):
        thumbsrc = thumb(self.file.name, "width=1024,height=768")
        if thumbsrc == 'media/images/error.png':
            return self.file.name.split('apps/harbor/')[-1]
        else:
            return thumbsrc.split('apps/harbor/')[-1]

    def rExt(self):
        return self.file.name.split('.')[-1].lower()

    def calSize(self):
        if self.file:
            return calsize(self.file.size)
        else:
            return calsize(0)


_DATASHARE_UPLOAD_TO = os.path.join(_UPLOAD_TO, 'datashare', '%Y%m%d')
class DataShare(M.Model):
    #臨時檔案上傳區
    upload_user = M.ForeignKey(User, verbose_name='上傳者')
    upload_date = M.DateField(verbose_name='上傳日期')
    name = M.CharField(verbose_name='檔案名', max_length=256, null=True, default='')
    file = M.ImageField(upload_to=_DATASHARE_UPLOAD_TO, null=True)
    memo = M.CharField(verbose_name='備註說明', null=True, max_length=2048)

    def rUrl(self):
        return self.file.name.split('apps/harbor/')[-1]

    def rThumbUrl(self):
        thumbsrc = thumb(self.file.name, "width=1024,height=768")
        if thumbsrc == 'media/images/error.png':
            return self.file.name.split('apps/harbor/')[-1]
        else:
            return thumbsrc.split('apps/harbor/')[-1]

    def rExt(self):
        return self.file.name.split('.')[-1].lower()

    def calSize(self):
        if self.file:
            return calsize(self.file.size)
        else:
            return calsize(0)


# god damn aquaculture
class Aquaculture(M.Model):
    name = M.CharField(verbose_name='魚塭名稱', null=False, max_length=256)
    code = M.CharField(verbose_name='魚塭代碼', null=True, max_length=256)
    xcoord = M.DecimalField(verbose_name='X座標', null=True , max_digits=20 , decimal_places=12)
    ycoord = M.DecimalField(verbose_name='y座標', null=True , max_digits=20 , decimal_places=12)
    place = M.ForeignKey(Place, verbose_name='縣市', null=True)
    location = M.CharField(verbose_name='地理位置', null=True, max_length=4096)
    history = M.CharField(verbose_name='魚塭沿革', null=True, max_length=4096)
    range = M.CharField(verbose_name='魚塭區域範圍', null=True, max_length=4096)

    def twd97(self):
        if self.xcoord == None or self.ycoord == None:
            class C(): (x, y) = ('','')
        else:
            lon = radians(float(self.xcoord))
            lat = radians(float(self.ycoord))
            a = 6378137.0
            b = 6356752.314245
            long0 = radians(121)
            k0 = 0.9999
            dx = 250000
            e = (1-b**2/a**2)**0.5
            e2 = e**2/(1-e**2)
            n = (a-b)/(a+b)
            nu = a/(1-(e**2)*(sin(lat)**2))**0.5
            p = lon-long0
            A = a*(1 - n + (5/4.0)*(n**2 - n**3) + (81/64.0)*(n**4  - n**5))
            B = (3*a*n/2.0)*(1 - n + (7/8.0)*(n**2 - n**3) + (55/64.0)*(n**4 - n**5))
            C = (15*a*(n**2)/16.0)*(1 - n + (3/4.0)*(n**2 - n**3))
            D = (35*a*(n**3)/48.0)*(1 - n + (11/16.0)*(n**2 - n**3))
            E = (315*a*(n**4)/51.0)*(1 - n)
            S = A*lat - B*sin(2*lat) + C*sin(4*lat) - D*sin(6*lat) + E*sin(8*lat)
            K1 = S*k0
            K2 = k0*nu*sin(2*lat)/4.0
            K3 = (k0*nu*sin(lat)*(cos(lat)**3)/24.0) * \
                (5 - tan(lat)**2 + 9*e2*(cos(lat)**2) + 4*(e2**2)*(cos(lat)**4))
            Y = K1 + K2*(p**2) + K3*(p**4)
            K4 = k0*nu*cos(lat)
            K5 = (k0*nu*(cos(lat)**3)/6.0) * \
                (1 - tan(lat)**2 + e2*(cos(lat)**2))
            X = K4*p + K5*(p**3) + dx

            class C(): (x, y) = (int(X),int(Y))
        return C()

    def twd97_2_googlemap(self):
        # ref from: http://blog.ez2learn.com/2009/08/15/lat-lon-to-twd97/
        # Cerberus: This code is for TWD97 cartesian transfer to a WGS84 base coordinates. This code can
        # get a similar answer, but it is not tested and verified.
        x = self.xcoord and self.xcoord or 0
        y = self.ycoord and self.ycoord or 0
        a = 6378137.0
        b = 6356752.314245
        lon0 = 121/180*3.1415
        k0 = 0.9999
        dx = 250000
        dy = 0
        e = (1-b**2/a**2)**0.5
        M = y/k0
        x = x - dx
        mu = M/(a*(1.0 - pow(e, 2)/4.0 - 3*pow(e, 4)/64.0 - 5*pow(e, 6)/256.0))
        e1 = (1.0 - pow((1.0 - pow(e, 2)), 0.5)) / (1.0 + pow((1.0 - pow(e, 2)), 0.5))
        J1 = (3*e1/2 - 27*pow(e1, 3)/32.0)
        J2 = (21*pow(e1, 2)/16 - 55*pow(e1, 4)/32.0)
        J3 = (151*pow(e1, 3)/96.0)
        J4 = (1097*pow(e1, 4)/512.0)
        fp = mu + J1*cmath.sin(2*mu) + J2*cmath.sin(4*mu) + J3*cmath.sin(6*mu) + J4*cmath.sin(8*mu);
        # Calculate Latitude and Longitude
        e2 = pow((e*a/b), 2);
        C1 = pow(e2*cmath.cos(fp), 2);
        T1 = pow(cmath.tan(fp), 2);
        R1 = a*(1-pow(e, 2))/pow((1-pow(e, 2)*pow(cmath.sin(fp), 2)), (3.0/2.0));
        N1 = a/pow((1-pow(e, 2)*pow(cmath.sin(fp), 2)), 0.5);
        D = x/(N1*k0);
        # lat
        Q1 = N1*cmath.tan(fp)/R1;
        Q2 = (pow(D, 2)/2.0);
        Q3 = (5 + 3*T1 + 10*C1 - 4*pow(C1, 2) - 9*e2)*pow(D, 4)/24.0;
        Q4 = (61 + 90*T1 + 298*C1 + 45*pow(T1, 2) - 3*pow(C1, 2) - 252*e2)*pow(D, 6)/720.0;
        lat = fp - Q1*(Q2 - Q3 + Q4);
        # long
        Q5 = D;
        Q6 = (1 + 2*T1 + C1)*pow(D, 3)/6;
        Q7 = (5 - 2*C1 + 28*T1 - 3*pow(C1, 2) + 8*e2 + 24*pow(T1, 2))*pow(D, 5)/120.0;
        lon = lon0 + (Q5 - Q6 + Q7)/cmath.cos(fp);
        lat = (lat/(cmath.pi)*180).real
        lon = (lon/(cmath.pi)*180 + 121).real
        return lat, lon



class Reef(M.Model):
    #人工魚礁區
    place = M.ForeignKey(Place, verbose_name='縣市', null=True)
    name = M.CharField(verbose_name='魚礁名稱', null=False, max_length=256)
    lon = M.CharField(verbose_name='中心點經度', null=True , max_length=256)
    lat = M.CharField(verbose_name='中心點緯度', null=True , max_length=256)
    history = M.TextField(verbose_name=u'簡介', null=True, default='')
    marked_point = M.CharField(verbose_name='標示點', null=True, max_length=256)



class ReefLocation(M.Model):
    #魚礁座標(因為必須支援多座標的紀錄)
    reef = M.ForeignKey(Reef, verbose_name='魚礁')
    name = M.CharField(verbose_name='座標名稱', null=True, max_length=256)
    lon = M.CharField(verbose_name='中心點經度', null=True , max_length=256)
    lat = M.CharField(verbose_name='中心點緯度', null=True , max_length=256)



class ReefPut(M.Model):
    #年度魚礁投放
    year = M.IntegerField(verbose_name='年度')
    reef = M.ForeignKey(Reef, verbose_name='魚礁')
    location = M.TextField(verbose_name=u'投礁位置', null=True, default='')
    a_num = M.IntegerField(verbose_name='A型數量', default=0)
    b_num = M.IntegerField(verbose_name='B型數量', default=0)
    deep = M.DecimalField(verbose_name='水深(M)', null=True , max_digits=16, decimal_places=2)


class ReefPutNum(M.Model):
    #年度魚礁投放的型式數量
    reefput = M.ForeignKey(ReefPut, verbose_name='魚礁投放紀錄')
    name = M.CharField(verbose_name='型式名稱', null=False, max_length=256)
    num = M.IntegerField(verbose_name='A型數量', default=0)



class ReefProject(M.Model):
    #魚礁工程
    year = M.IntegerField(verbose_name='年度')
    reef = M.ForeignKey(Reef, verbose_name='魚礁')
    name = M.CharField(verbose_name='工程名稱', null=False, max_length=512)
    price = M.IntegerField(verbose_name='工程經費(元)', default=0)



def _FRRFDATA_UPLOAD_TO(instance, filename):
    ext = filename.split('.')[-1].lower()
    reef = instance.reef
    return os.path.join(_UPLOAD_TO, 'reefdata', str(reef.id), '%s.%s' % (instance.id, ext))
        
class ReefData(M.Model):
    #魚礁檔案上傳區
    reef = M.ForeignKey(Reef, verbose_name='魚礁')
    upload_date = M.DateField(verbose_name='上傳日期')
    name = M.CharField(verbose_name='檔案名', max_length=256, null=True, default='')
    file = M.ImageField(upload_to=_FRRFDATA_UPLOAD_TO, null=True)
    memo = M.CharField(verbose_name='備註說明', null=True, max_length=2048)

    def rUrl(self):
        return self.file.name.split('apps/harbor/')[-1]

    def rExt(self):
        return self.file.name.split('.')[-1].lower()

    def calSize(self):
        if self.file:
            return calsize(self.file.size)
        else:
            return calsize(0)