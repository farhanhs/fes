# -*- coding: utf8 -*-
from hashlib import md5
from types import NoneType
from base64 import b64decode
from urllib import urlencode
import urllib2
from urllib2 import Request
from urllib2 import HTTPError
import os
import shutil
from django.http import HttpResponse
import datetime, time, re
from calendar import monthrange
from cStringIO import StringIO
from django.conf import settings

def TODAY(): return datetime.date.today()


def readDateRange(start, end):
    range = []
    date = start
    while date <= end:
        range.append(date)
        date += datetime.timedelta(1)
    return range


def updateFirstWordByUpper(s):
    return s[0].upper() + s[1:].lower()


DAYTYPEONDAY = {
    u'日曆天(包含六日)':         {1: True, 2: True, 3: True, 4: True, 5: True, 6: True, 7: True},
    u'工作天':                   {1: True, 2: True, 3: True, 4: True, 5: True, 6: False, 7: False},
    u'限期完工(日曆天每日施工)': {1: True, 2: True, 3: True, 4: True, 5: True, 6: True, 7: True},
    u'日曆天(僅周日不計)':       {1: True, 2: True, 3: True, 4: True, 5: True, 6: True, 7: False},
    u'日曆天(不含六日)':         {1: True, 2: True, 3: True, 4: True, 5: True, 6: False,7: False},
}

class WorkingDate:
    def __init__(self, **kw):
        self._start_date = kw.get('start_date')
        self._end_date = kw.get('end_date', None)
        self._range = kw.get('range', 0)
        self._date_type = kw.get('date_type')
        self._holiday = kw.get('holiday', [])
        self._holiday_on = kw.get('holiday_on', [])
        self._date_off = kw.get('date_off', [])
        self._date_on = kw.get('date_on', [])

    def decideDate(self, date):
        type = self._date_type
        res = DAYTYPEONDAY[type][date.isoweekday()]
        message = ''
        if not res:
            message = type

        if type != u'限期完工(日曆天每日施工)':
            if self._holiday.count(date):
                res = False
                message = u'國定假日'
            if self._holiday_on.count(date):
                res = True
                message = u'補假'

        if self._date_off.count(date):
            res = False
            message = u'停工'
        if self._date_on.count(date):
            res = True
            message = u'強制開工'

        return res, message

    def readWorkingDate(self):
        date = self._start_date
        workingdates = []
        i = 1
        if self._end_date:
            while i <= self._range or date <= self._end_date:
                if self.decideDate(date)[0]:
                    workingdates.append(date)
                    i += 1
                date += datetime.timedelta(1)
        else:
            while i <= self._range:
                if self.decideDate(date)[0]:
                    workingdates.append(date)
                    i += 1
                date += datetime.timedelta(1)
        self.workingdates = workingdates

        return workingdates


import os.path
from PIL import Image, ImageDraw, ImageFont

class ProgressChart:
    """ 先決定資料結構。
    預定進度數據以 [(design_percent, act_percent, date, True/False), ] 傳入
    """

    def __init__(self):
        dir = os.path.dirname(__file__)
        self._datas = []
        self._initday = ''
        c = {
            'width' : 1600, # 全圖寬度
            'height' : 1200, # 全圖高度
            'enddate_x': 20, # 電腦計算預定完工日期的 X
            'enddate_y': 70, # 電腦計算預定完工日期的 Y
            'title_x': 680, # 標題的 X
            'title_y': 10, # 標題的 Y
            #右上角 線條說明文字設定
            'design_x': 750, #
            'design_y': 60, #
            'design_x1': 720, # 
            'design_x2': 740, # 
            'design_y1': 65, # 
            'design_y2': 75, # 
            'act_x': 750, # 
            'act_y': 85, # 
            'act_x1': 720, # 
            'act_x2': 740, # 
            'act_y1': 90, # 
            'act_y2': 100, # 
            'titlefontsize': ImageFont.truetype(os.path.join(dir, 'bkai00mp.ttf'), 32), # 標題文字的大小
            'leftwidth': 70, # 最左邊留白的寬度
            'bottomheight': 100, # 最下面留白的高度(從 X 軸線到最下面)
            'dayaxiswidth': 1460, # 日期軸的寬度
            'dayaxisscaleheight': 4,  # 絕對日期座標軸的標線高度
            'dayaxistextheight': 0,  # 絕對日期座標軸的文字高度層級
            'percentaxisheight': 940, # 進度軸的高度
            'dayaxisfontsize': ImageFont.truetype(os.path.join(dir, 'bkai00mp.ttf'), 22),    # 絕對天座標軸中的文字的大小
            'dayaxiscolor': (0, 0, 0, 150), # 絕對日期座標軸的顏色
            'act_percent_linecolor' : (255, 0, 0, 255), # 實際進度曲線的顏色
            'design_percent_linecolor' : (20, 64, 191, 255), # 預定進度曲線的顏色
            'gantt_bar_dir_color' : (0, 170, 0, 255), # 甘特bar資料夾的顏色
            'gantt_bar_item_color' : (0, 216, 255, 255), # 甘特bar工項的顏色
            'gantt_bar_height' : 18, # 甘特bar的高度
            'gantt_bar_dir_fontsize': ImageFont.truetype(os.path.join(dir, 'bkai00mp.ttf'), 14),    # 甘特bar的資料夾文字的大小
            'gantt_bar_item_fontsize': ImageFont.truetype(os.path.join(dir, 'bkai00mp.ttf'), 12),    # 甘特bar的工項文字的大小
            'scale_day_fontsize': ImageFont.truetype(os.path.join(dir, 'bkai00mp.ttf'), 8),    # 甘特bar的工項文字的大小
            'yearfontcolor' : (20, 64, 191, 255), # 工項說明文字的顏色
            'bgcolor': (255, 255, 255, 255), # 底色
            'dayaxisbetweentext': 16, # 絕對天座標軸與天數的距離
            'gridcolor' : (230, 230, 230, 230), # 格線顏色
            'changeordercolor' : (0, 0, 0, 255), # 變更設計日期線顏色
            'fileformat': 'png', # 輸出檔案格式
        }
        c['dayaxis_y'] = c['height'] - c['bottomheight']
        self._config = c

    def NewChart(self):
        c = self._config
        self._im = Image.new('RGBA', (c['width'], c['height']), c['bgcolor'])
        self._dw = ImageDraw.Draw(self._im)
        
    def DrawDayAxis(self):
        c = self._config
        self._dw.line((c['leftwidth'], c['height']-c['bottomheight'],
        c['leftwidth']+c['dayaxiswidth'], c['height']-c['bottomheight']), fill=c['dayaxiscolor'])

    def DrawX(self):
        c = self._config
        design_percents, act_percents, workingdates, change_date, engs_price = self._datas
        design_percents.reverse()
        act_percents.reverse()
        workingdates.reverse()

        y = c['dayaxis_y']
        c['daywidth'] = c['dayaxiswidth'] * 1.0 / len(workingdates)
        for i, data in enumerate(workingdates):
            x = c['leftwidth'] + c['dayaxiswidth'] - c['daywidth'] * i
            self._dw.line((x, c['height']-c['bottomheight'], x, c['height']-c['bottomheight']-c['percentaxisheight']),
                fill=c['gridcolor'])

            height = c['dayaxisscaleheight']

            if i == 0:
                self._drawlittleXtext(data.strftime('%y/%m/%d'), x, y, c['dayaxisbetweentext']) 
            elif i == len(workingdates) - 1:
                pass
            elif workingdates[i+1].year != workingdates[i].year:
                self._drawlittleXtext(data.strftime('%y%m%d'), x, y, c['dayaxisbetweentext']) 
            elif workingdates[i+1].month != workingdates[i].month:
                height *= 2
                self._drawlittleXtext(data.strftime('%m%d'), x, y, c['dayaxisbetweentext']) 

            self._drawlittleXscale(x, y, height)

        x = c['leftwidth'] + c['dayaxiswidth'] - c['daywidth'] * (i + 1)
        self._drawlittleXtext(workingdates[-1].strftime('%y/%m/%d'), x, y, c['dayaxisbetweentext']) 

        for i, data in enumerate(design_percents):
            backward_range = 0
            while 1:
                _d = data[u'日期'] - datetime.timedelta(days=backward_range)
                if _d <= workingdates[-1]:
                    x = c['leftwidth'] + c['dayaxiswidth'] - c['daywidth'] * (len(workingdates) - 1)
                    break
                try:
                    x = c['leftwidth'] + c['dayaxiswidth'] - c['daywidth'] * workingdates.index(_d)
		    break
                except ValueError:
                    backward_range += 1

            x0 = x
            design_y0 = c['dayaxis_y'] - data[u'預定累計進度'] * c['pixel_per_percent']
            try:
                x1 = c['leftwidth'] + c['dayaxiswidth'] - c['daywidth'] * ( workingdates.index(design_percents[i+1][u'日期']))
            except:
                x1 = c['leftwidth']

            if i < len(design_percents)-1:
                design_y1 = c['dayaxis_y'] - design_percents[i+1][u'預定累計進度'] * c['pixel_per_percent']
            else:
                design_y1 = c['dayaxis_y']
            self._dw.line((x0,design_y0,x1,design_y1), width=1, fill=c['design_percent_linecolor'])
            #給曲線圖加上預定地具體進度和累計金額
            x = c['leftwidth'] + c['dayaxiswidth'] - c['daywidth'] * i
            try:
                if workingdates[i+1].month != workingdates[i].month:
                    self._dw.line((x, design_y0 - 6, x, design_y1 + 3), fill=self._config['dayaxiscolor'])
                    #預定累積金額 = 預定進度 * 預定金額 / 100
                    s_money = format(int(float(data[u'預定累計進度']) * engs_price / 100), ',') + u'元'
                    self._dw.text((x - 70, design_y1 + 15),  str(data[u'預定累計進度']) + '%(' + s_money + ')',font=c['dayaxisfontsize'], fill=self._config['design_percent_linecolor'])
            except:
                pass
        if change_date:
            for cd in change_date:
                while cd not in workingdates:
                    cd -= datetime.timedelta(1)
                x0 = c['leftwidth'] + c['dayaxiswidth'] - c['daywidth'] * workingdates.index(cd)
                self._dw.line((x0, c['height']-c['bottomheight'], x0, c['height']-c['bottomheight']-c['percentaxisheight']), fill=c['changeordercolor'])
                self._dw.text((x0-50, 1110), unicode('變更設計日'), font=c['dayaxisfontsize'], fill=self._config['dayaxiscolor'])

        draw_act = False
        for i, data in enumerate(act_percents):
            backward_range = 0
            while 1:
                _d = data[u'日期'] - datetime.timedelta(days=backward_range)
                if _d <= workingdates[-1]:
                    x = c['leftwidth'] + c['dayaxiswidth'] - c['daywidth'] * (len(workingdates) - 1)
                    break
                try:
                    x = c['leftwidth'] + c['dayaxiswidth'] - c['daywidth'] * workingdates.index(_d)
		    break
                except ValueError:
                    backward_range += 1

            x0 = x
            act_y0 = c['dayaxis_y'] - data[u'實際累計進度'] * c['pixel_per_percent']
            try:
                x1 = c['leftwidth'] + c['dayaxiswidth'] - c['daywidth'] * ( workingdates.index(act_percents[i+1][u'日期']))
            except:
                x1 = c['leftwidth']

            if i < len(act_percents)-1:
                act_y1 = c['dayaxis_y'] - act_percents[i+1][u'實際累計進度'] * c['pixel_per_percent']
            else:
                act_y1 = c['dayaxis_y']

            if data['has_reported']: draw_act = True
            if draw_act: self._dw.line((x0,act_y0,x1,act_y1), width=1, fill=c['act_percent_linecolor'])
            #給曲線圖加上實際地具體進度和累計金額
            if draw_act:
                x = c['leftwidth'] + c['dayaxiswidth'] - c['daywidth'] * i
                try:
                    if workingdates[i+1].month != workingdates[i].month:
                        self._dw.line((x, act_y0 - 5, x, act_y1 + 5), fill=self._config['dayaxiscolor'])
                        #實際累積金額 = 實際進度 * 契約金額 / 100
                        a_money = format(int(data[u'實際累計進度'] * engs_price / 100), ',') + u'元'
                        self._dw.text((x - 70, act_y1 + 10 ),  str(data[u'實際累計進度']) + '%(' + a_money + ')',font=c['dayaxisfontsize'], fill=self._config['act_percent_linecolor'])       
                except:
                    pass
                

    def DrawTitle(self):
        design_percents, act_percents, workingdates, change_date, engs_price = self._datas
        design_percents.reverse()
        act_percents.reverse()
        workingdates.reverse()
        c = self._config
        self._dw.text((c['title_x'], c['title_y']), unicode('進度實績管理系統'),
        font=c['titlefontsize'], fill=self._config['dayaxiscolor'])

        self._dw.rectangle(((c['design_x1'], c['design_y1']), (c['design_x2'], c['design_y2'])), fill=c['design_percent_linecolor'])
        self._dw.rectangle(((c['act_x1'], c['act_y1']), (c['act_x2'], c['act_y2'])), fill=c['act_percent_linecolor'])
        self._dw.text((c['design_x'], c['design_y']), unicode('預定進度(預定累計金額) BCWS(Budget-Cost-Work-Schedueled)'),
        font=c['dayaxisfontsize'], fill=self._config['dayaxiscolor'])
        self._dw.text((c['act_x'], c['act_y']), unicode('實際進度(實際累計金額) BCWP(Budget-Cost-Work-Performed)'),
        font=c['dayaxisfontsize'], fill=self._config['dayaxiscolor'])
        
    def DrawPercentAxis(self):
        engs_price = self._datas[4]
        c = self._config
        x = c['leftwidth']
        init_y = c['height']-c['bottomheight']
        self._dw.line((x, init_y, x,
        init_y-c['percentaxisheight']),
        fill=c['dayaxiscolor'])

        c['pixel_per_percent'] = c['percentaxisheight'] * 1.0 / self._maxpercent

        for i in xrange(1,11):
            y = init_y - c['pixel_per_percent'] * i * 10
            self._drawlittleYscale(x, y, c['dayaxisscaleheight'])
            self._drawlittleYtext(str(i*10), x, y,
            c['dayaxisbetweentext'])
            #加上100%的
            if i*10 == 100:
                self._dw.text((1400, 130),  '100%(' + format(int(engs_price), ',') + u'元)',font=c['dayaxisfontsize'], fill=(148,0,211,255))

            self._dw.line((c['leftwidth'], y, c['leftwidth']+c['dayaxiswidth'],y), fill=c['gridcolor'])
        if self._maxpercent >= 103:
            y = init_y - c['pixel_per_percent'] * self._maxpercent
            self._drawlittleYscale(x, y, c['dayaxisscaleheight'])
            self._drawlittleYtext(str(int(self._maxpercent)), x, y,
            c['dayaxisbetweentext'])

            self._dw.line((c['leftwidth'], y, c['leftwidth']+c['dayaxiswidth'],y), fill=c['gridcolor'])
            

    def _drawlittleYtext(self, text, x, y, width):
        c = self._config
        (text_w, text_h) = self._dw.textsize(unicode(text),font=c['dayaxisfontsize'])
        self._dw.text((x-width/2-text_w, y-(text_h/2)), unicode(text),\
            font=c['dayaxisfontsize'], fill=self._config['dayaxiscolor'])
        
    def _drawlittleYscale(self, x, y, height):
        self._dw.line((x-height, y, x+height, y), fill=self._config['dayaxiscolor'])

    def _drawlittleXscale(self, x, y, height):
        self._dw.line((x, y-height, x, y+height), fill=self._config['dayaxiscolor'])

    def DrawStartDate(self):
        c = self._config
        (text_w, text_h) = self._dw.textsize(unicode('開工日期: %s'%self._start_date),font=c['dayaxisfontsize'])
        self._dw.text((c['enddate_x'], c['enddate_y']-text_h), unicode('開工日期: %s'%self._start_date),
        font=c['dayaxisfontsize'], fill=self._config['dayaxiscolor'])
        
    def DrawEndDate(self):
        c = self._config
        self._dw.text((c['enddate_x'], c['enddate_y']), unicode('預定完工日期(考量停工/強制開工): %s'%self._enddate),
        font=c['dayaxisfontsize'], fill=self._config['dayaxiscolor'])
        
    def DrawDaytype(self):
        c = self._config
        (text_w, text_h) = self._dw.textsize(unicode('工期計算方式: %s'%self._date_type),font=c['dayaxisfontsize'])
        self._dw.text((c['enddate_x'], c['enddate_y']+text_h), unicode('工期計算方式: %s'%self._date_type),
        font=c['dayaxisfontsize'], fill=self._config['dayaxiscolor'])
        
    def DrawDuration(self):
        c = self._config
        (text_w, text_h) = self._dw.textsize(unicode('契約載明工期天數:%s (進度規劃項目之結束天數:%s)'%(self._duration, self._ef)),font=c['dayaxisfontsize'])
        self._dw.text((c['enddate_x'], c['enddate_y']+2*text_h), unicode('契約載明工期天數:%s (進度規劃項目之結束天數:%s)'%(self._duration, self._ef)),
        font=c['dayaxisfontsize'], fill=self._config['dayaxiscolor'])
        
    def DrawDeadline(self):
        c = self._config
        (text_w, text_h) = self._dw.textsize(unicode('契約載明限期完工日期: %s'%self._deadline),font=c['dayaxisfontsize'])
        self._dw.text((c['enddate_x'], c['enddate_y']+2*text_h), unicode('契約載明限期完工日期: %s'%self._deadline),
        font=c['dayaxisfontsize'], fill=self._config['dayaxiscolor'])
        
    def _drawlittleXtext(self, text, x, y, height):
        c = self._config
        (text_w, text_h) = self._dw.textsize(unicode(text),font=c['dayaxisfontsize'])
        i = c['dayaxistextheight'] % 4 + 1
        if len(text) == 8:
            self._dw.text((x-(text_w/2), y+height*i), unicode(text),\
                font=c['dayaxisfontsize'], fill=self._config['yearfontcolor'])
        else:
            self._dw.text((x-(text_w/2), y+height*i), unicode(text),\
                font=c['dayaxisfontsize'], fill=self._config['dayaxiscolor'])
        c['dayaxistextheight'] += 1
        
    def SaveChart(self, filename='test.png'):
        self._im.save(filename, self._config['fileformat'])
        
    def SetItem(self, datas):
        self._maxpercent = datas[1][-1][u'實際累計進度']
        if self._maxpercent < 100: self._maxpercent = 100
        self._datas = datas

    def SetDuration(self, type, ef):
        self._duration = type
        self._ef = ef

    def SetDaytype(self, type):
        self._date_type = type

    def SetDeadline(self, type):
        self._deadline = type

    def SetStartDate(self, type):
        self._start_date = type

    def SetEndDate(self, type):
        self._enddate = type

    def SetEngName(self, type):
        self._engname = type
        
    def SetEngSn(self, type):
        self._engsn = type

    def SetMakeDate(self):
        self._makedate = datetime.date.now()


def _progresscharttest():
    pc = ProgressChart()
    Items = [
        (10.0, 9., datetime.date(2007,3,3), True),
        (10.0, 19., datetime.date(2007,3,4), False),
        (45.0, 19., datetime.date(2007,3,9), True),
        (88.0, 79.0, datetime.date(2007,3,12), False),
        (90.5, 93.0, datetime.date(2007,3,15), False),
        (100.0, -1, datetime.date(2007,3,25), True),
    ]
    pc.SetItem(Items)
    pc.NewChart()
    pc.DrawDayAxis()
    pc.DrawPercentAxis()
    pc.DrawX()
    pc.SaveChart() 


#製造施工日誌Excel.xlsx
def make_contractor_excel_file(workbook="", data={}):
    #設定每個cell的格式
    def myfmt(border=1, bg_color="", shrink="", align="center", text_wrap="", font_name=u"標楷體", font_size=10, num_format="", bold=False):
        fmt = workbook.add_format()
        if border:
            fmt.set_border(border)
        if bg_color:
            fmt.set_bg_color(bg_color)
        if shrink:
            fmt.set_shrink(shrink)
        if align:
            fmt.set_align(align)
        if text_wrap:
            fmt.set_text_wrap(text_wrap)
        if font_name:
            fmt.set_font_name(font_name)
        if font_size:
            fmt.set_font_size(font_size)
        if num_format:
            fmt.set_num_format(num_format)
        if bold:
            fmt.set_bold(bold)
        fmt.set_align('top')

        return fmt 

    #列印大標題用的
    def plug_head(x, row, myheight=17, bold=True):
        worksheet.set_row(row, myheight)
        worksheet.merge_range(row, 0, row, 9, x, myfmt(text_wrap=True, align="left", bold=bold))

    mydata=data["reports"]
    date_keys = [datetime.datetime.strptime(date_key, '%Y-%m-%d').date() for date_key in mydata]
    date_keys.sort() #要照日期排序
    for d in date_keys:
        dd = mydata[str(d)]["replace"]
        # 新增一個sheet
        worksheet = workbook.add_worksheet(dd["reportdate"])
        worksheet.set_margins(left=0.5, right=0.5, top=0.5, bottom=0.5)
        worksheet.set_header(header='',margin=0.0)
        worksheet.set_paper(9)
        row = 0 #第一列的編號為0

        # Basic format
        column_width=[11.75, 11.75, 11.75, 5.8, 5.8, 5.8, 5.8, 11.75, 11.75, 11.75]
        # set cloumn width 
        for i, e in enumerate(column_width):
            worksheet.set_column(i, i, e)

        # 第一列合併
        worksheet.merge_range(row, 0, row, 9, u'公共工程施工日誌', myfmt(border=0, font_size=14)) 
        
        # basic information 
        worksheet.write(row+1, 0, u"報表編號：", myfmt(border=0))
        row += 2
        worksheet.write(row, 0, u"本日天氣：", myfmt(border=0))
        worksheet.merge_range(row, 1, row, 5, u"上午：%s 下午：%s" % (dd["morning_weather"], dd["afternoon_weather"]), myfmt(border=0, align="left")) 
        worksheet.merge_range(row, 6, row, 9, u"填報日期： %s" % dd["reportdate"], myfmt(border=0, align="left", font_size="14")) 
        row += 1
        worksheet.write(row, 0, u"工程名稱", myfmt())
        worksheet.merge_range(row, 1, row, 9, dd["project_name"], myfmt(align="left"))
        row += 1
        worksheet.write(row, 0, u"承攬廠商名稱", myfmt(shrink=True))
        worksheet.merge_range(row, 1, row, 9, dd["project_contractor_name"], myfmt(align="left"))
        row += 1
        worksheet.write(row, 0, u"核定工期", myfmt())
        worksheet.write(row, 1, u"%s 天\n(%s)" % (dd["duration"], dd["date_type"]), myfmt(text_wrap=True))
        worksheet.write(row, 2, u"累計工期", myfmt())
        worksheet.merge_range(row, 3, row, 4, "%s 天" % dd["used_duration"], myfmt())
        worksheet.merge_range(row, 5, row, 6, u"剩餘工期", myfmt())
        worksheet.write(row, 7, u"%s 天" % dd["unused_duration"], myfmt())
        worksheet.write(row, 8, u"工期展延天數", myfmt(shrink=True))
        worksheet.write(row, 9, u"%s 天" % dd["extension"], myfmt())
        row += 1
        worksheet.write(row,0, "開工日期", myfmt())
        worksheet.merge_range(row, 1, row, 4, dd["start_date"], myfmt())
        worksheet.merge_range(row, 5, row, 6, "完工日期", myfmt(shrink=True))
        worksheet.merge_range(row, 7, row, 9, dd["end_date"], myfmt())
        row += 1
        worksheet.write(row,0, "預定進度(%)", myfmt())
        worksheet.merge_range(row, 1, row, 4, str(dd["design_percent"]) + " %", myfmt())
        worksheet.merge_range(row, 5, row, 6, "實際進度(%)", myfmt())
        worksheet.merge_range(row, 7, row, 9, str(dd["act_percent"]) + " %", myfmt())
        row += 1
        plug_head(u"一、依施工計畫書執行按圖施工概況（含約定之重要施工項目及完成數量等）：", row)
        row += 1
        worksheet.merge_range(row, 0, row, 3, u"施工項目", myfmt())
        worksheet.write(row, 4, u"單位", myfmt())
        worksheet.merge_range(row, 5, row, 6, u"契約數量",myfmt())
        worksheet.write(row, 7, u"本日完成", myfmt())
        worksheet.write(row, 8, u"累計完成", myfmt())
        worksheet.write(row, 9, u"備註", myfmt())
        row += 1
        for k, s in enumerate(mydata[str(d)]["item_table"]):
            i = row + k
            worksheet.merge_range(i, 0, i, 3, s[0], myfmt(align="left", shrink=True))
            if s[-1] == 'dir':
                worksheet.merge_range(i, 4, i, 9, "", myfmt())
            else:
                worksheet.write(i, 4, s[1], myfmt(shrink=True))
                worksheet.merge_range(i, 5, i, 6, s[2], myfmt(shrink=True, align="right"))
                worksheet.write(i, 7, s[3], myfmt(shrink=True, align="right"))
                worksheet.write(i, 8, s[4], myfmt(shrink=True, align="right"))
                worksheet.write(i, 9, s[5], myfmt(shrink=True, align="left"))
                
        row += len(mydata[str(d)]["item_table"])
        for i in xrange(row, row+2):
            worksheet.merge_range(i, 0, i, 3, "", myfmt(align="left", shrink=True))
            worksheet.write(i, 4, "", myfmt(shrink=True))
            worksheet.merge_range(i, 5, i, 6, "", myfmt(shrink=True, align="right"))
            worksheet.write(i, 7, "", myfmt(shrink=True, align="right"))
            worksheet.write(i, 8, "", myfmt(shrink=True, align="right"))
            worksheet.write(i, 9, "", myfmt(shrink=True, align="left"))
        row += 2
        plug_head(u"二、工地材料管理概況(含約定之重要材料使用狀況及數量等)：", row)
        row += 1
        worksheet.merge_range(row, 0, row, 3, u"材料名稱", myfmt())
        worksheet.write(row, 4, u"單位", myfmt())
        if dd['over_20190501']:
            worksheet.merge_range(row, 5, row, 6, u"契約數量",myfmt())
        else:
            worksheet.merge_range(row, 5, row, 6, u"設計數量",myfmt())
        worksheet.write(row, 7, u"本日完成數量", myfmt(shrink=True))
        worksheet.write(row, 8, u"累計完成數量", myfmt(shrink=True))
        worksheet.write(row, 9, u"備註", myfmt())
        row += 1
        for k, s in enumerate(mydata[str(d)]["site_material_table"]):
            i = row + k
            worksheet.merge_range(i, 0, i, 3, s[0], myfmt(align="left", shrink=True))
            worksheet.write(i, 4, s[1], myfmt(shrink=True))
            worksheet.merge_range(i, 5, i, 6, s[2], myfmt(shrink=True, align="right"))
            worksheet.write(i, 7, s[3], myfmt(shrink=True, align="right"))
            worksheet.write(i, 8, s[4], myfmt(shrink=True, align="right"))
            worksheet.write(i, 9, s[5], myfmt(shrink=True, align="left"))
        row += len(mydata[str(d)]["site_material_table"])
        for i in xrange(row, row+2):
            worksheet.merge_range(i, 0, i, 3, "", myfmt(align="left", shrink=True))
            worksheet.write(i, 4, "", myfmt(shrink=True))
            worksheet.merge_range(i, 5, i, 6, "", myfmt(shrink=True, align="right"))
            worksheet.write(i, 7, "", myfmt(shrink=True, align="right"))
            worksheet.write(i, 8, "", myfmt(shrink=True, align="right"))
            worksheet.write(i, 9, "", myfmt(shrink=True, align="left"))
        row += 2
        plug_head(u"三、工地人員及機具管理(含約定之出工人數及機具使用情形及數量)：", row)
        row += 1
        worksheet.merge_range(row, 0, row, 1, u"工別", myfmt())
        worksheet.write(row, 2, u"本日人數", myfmt())
        worksheet.merge_range(row, 3, row, 4, u"累計人數", myfmt())
        worksheet.merge_range(row, 5, row, 7, u"機具名稱", myfmt())
        worksheet.write(row, 8, u"本日使用數量", myfmt(shrink=True))
        worksheet.write(row, 9, u"累計使用數量", myfmt(shrink=True))
        row += 1
        for k, s in enumerate(mydata[str(d)]["manmachine_table"]):
            i = row + k
            worksheet.merge_range(i, 0, i, 1, s[0], myfmt(shrink=True))
            worksheet.write(i, 2, s[1], myfmt())
            worksheet.merge_range(i, 3, i, 4, s[2], myfmt())
            worksheet.merge_range(i, 5, i, 7, s[3], myfmt(shrink=True))
            worksheet.write(i, 8, s[4], myfmt())
            worksheet.write(i, 9, s[5], myfmt())
        row += len(mydata[str(d)]["manmachine_table"])
        plug_head(u"四、本日施工項目是否有須依「營造業專業工程特定施工項目應置之技術士種類、比率或人數標準表」規定應設置技術士之專業工程：%s（此項如勾選”有”，則應填寫後附「建築物施工日誌之技術士簽章表」）" % dd['has_professional_item'], row, 46)
        row += 1
        plug_head(u"五、工地職業安全衛生事項之督導、公共環境與安全之維護及其他工地行政事務：", row)
        describe_subcontractor = u'(一)施工前檢查事項：'
        describe_subcontractor += u'\n    1.實施勤前教育(含工地預防災變及危害告知)：' + dd['pre_education']
        describe_subcontractor += u'\n    2.確認新進勞工是否提報勞工保險(或其他商業保險)資料及安全衛生教育訓練紀錄：' + dd['has_insurance']
        describe_subcontractor += u'\n    3.檢查勞工個人防護具：' + dd['safety_equipment']
        describe_subcontractor += u'\n(二)其他事項：\n    ' + dd['describe_subcontractor'].replace('\n', '\n    ')
        plug_head(describe_subcontractor, row+1, (describe_subcontractor.count('\n') + 2) * 17, bold=False)
        plug_head(u"六、施工取樣試驗紀錄：", row+2)
        plug_head(dd['sampling'], row+3, (dd['sampling'].count('\n') + 2) * 17, bold=False)
        plug_head(u"七、通知協力廠商辦理事項：", row+4)
        plug_head(dd['notify'], row+5, (dd['notify'].count('\n') + 2) * 17, bold=False)
        plug_head(u"八、重要事項紀錄：", row+6, 29)
        plug_head(dd['note'], row+7, (dd['note'].count('\n') + 2) * 17, bold=False)
        plug_head(u"簽章：【工地主任】：", row+8, 55)
    return workbook


#製造監造報表Excel.xlsx
def make_inspector_excel_file(workbook="", data={}):
    #設定每個cell的格式
    def myfmt(border=1, bg_color="", shrink="", align="center", text_wrap="", font_name=u"標楷體", font_size=10, num_format="", bold=False):
        fmt = workbook.add_format()
        if border:
            fmt.set_border(border)
        if bg_color:
            fmt.set_bg_color(bg_color)
        if shrink:
            fmt.set_shrink(shrink)
        if align:
            fmt.set_align(align)
        if text_wrap:
            fmt.set_text_wrap(text_wrap)
        if font_name:
            fmt.set_font_name(font_name)
        if font_size:
            fmt.set_font_size(font_size)
        if num_format:
            fmt.set_num_format(num_format)
        if bold:
            fmt.set_bold(bold)
        fmt.set_align('top')

        return fmt 

    #列印大標題用的
    def plug_head(x, row, myheight=17, bold=True):
        worksheet.set_row(row, myheight)
        worksheet.merge_range(row, 0, row, 9, x, myfmt(text_wrap=True, align="left", bold=bold))

    mydata=data["reports"]
    date_keys = [datetime.datetime.strptime(date_key, '%Y-%m-%d').date() for date_key in mydata]
    date_keys.sort() #要照日期排序
    for d in date_keys:
        dd = mydata[str(d)]["replace"]
        # 新增一個sheet
        worksheet = workbook.add_worksheet(dd["reportdate"])
        worksheet.set_margins(left=0.5, right=0.5, top=0.5, bottom=0.5)
        worksheet.set_header(header='',margin=0.0) 
        worksheet.set_paper(9) 
        row = 0 #第一列的編號為0

        # Basic format
        column_width=[11.75, 11.75, 11.75, 5.8, 5.8, 5.8, 5.8, 11.75, 11.75, 11.75]
        # set cloumn width 
        for i, e in enumerate(column_width):
            worksheet.set_column(i, i, e)

        # 第一列合併
        worksheet.merge_range(row, 0, row, 9, u'公共工程監造報表', myfmt(border=0, font_size=14)) 
        
        # basic information 
        worksheet.write(row+1, 0, u"報表編號：", myfmt(border=0))
        row += 2
        worksheet.write(row, 0, u"本日天氣：", myfmt(border=0))
        worksheet.merge_range(row, 1, row, 5, u"上午：%s 下午：%s" % (dd["morning_weather"], dd["afternoon_weather"]), myfmt(border=0, align="left")) 
        worksheet.merge_range(row, 6, row, 9, u"填報日期： %s" % dd["reportdate"], myfmt(border=0, align="left", font_size="14")) 
        row += 1
        worksheet.write(row, 0, u"工程名稱", myfmt())
        worksheet.merge_range(row, 1, row, 9, dd["project_name"], myfmt(align="left"))
        row += 1
        worksheet.write(row, 0, u"契約工期", myfmt())
        worksheet.write(row, 1, u"%s 天\n(%s)" % (dd["duration"], dd["date_type"]), myfmt(text_wrap=True))
        worksheet.write(row, 2, u"開工日期", myfmt())
        worksheet.merge_range(row, 3, row, 4, dd["start_date"], myfmt())
        worksheet.merge_range(row, 5, row, 6, u"預定完工日期", myfmt(shrink=True))
        worksheet.write(row, 7, dd["end_date"], myfmt())
        worksheet.write(row, 8, u"實際完工日期", myfmt(shrink=True))
        worksheet.write(row, 9, u"", myfmt())
        row += 1
        worksheet.write(row, 0, u"契約變更次數", myfmt(shrink=True))
        worksheet.write(row, 1, u"%s 次" % dd["change_version_times"], myfmt())
        worksheet.write(row, 2, u"工期展延天數", myfmt(shrink=True))
        worksheet.merge_range(row, 3, row, 4, u"%s 天" % dd["extension"], myfmt())
        worksheet.merge_range(row, 5, row+1, 6, u"契約金額", myfmt())
        worksheet.write(row, 7, u"原契約：", myfmt(shrink=True))
        worksheet.merge_range(row, 8, row, 9, dd["init_version_price"], myfmt(shrink=True, align="right", num_format="#,##0 元"))
        row += 1
        worksheet.write(row, 0, u"預定進度(%)", myfmt())
        worksheet.write(row, 1, str(dd["design_percent"]) + " %", myfmt(shrink=True))
        worksheet.write(row, 2, u"實際進度(%)", myfmt())
        worksheet.merge_range(row, 3, row, 4, str(dd["act_percent"]) + " %", myfmt(shrink=True))
        worksheet.write(row, 7, u"變更後契約：", myfmt())
        worksheet.merge_range(row, 8, row, 9, dd["change_version_price"], myfmt(shrink=True, align="right", num_format="#,##0 元"))
        row += 1
        plug_head(u"一、工程進行情況(含約定之重要施工項目及數量)：", row)
        row += 1
        worksheet.merge_range(row, 0, row, 3, u"施工項目", myfmt())
        worksheet.write(row, 4, u"單位", myfmt())
        worksheet.merge_range(row, 5, row, 6, u"契約數量",myfmt())
        worksheet.write(row, 7, u"本日完成", myfmt())
        worksheet.write(row, 8, u"累計完成", myfmt())
        worksheet.write(row, 9, u"備註", myfmt())
        row += 1
        for k, s in enumerate(mydata[str(d)]["item_table"]):
            i = row + k
            worksheet.merge_range(i, 0, i, 3, s[0], myfmt(align="left", shrink=True))
            if s[-1] == 'dir':
                worksheet.merge_range(i, 4, i, 9, "", myfmt())
            else:
                worksheet.write(i, 4, s[1], myfmt(shrink=True))
                worksheet.merge_range(i, 5, i, 6, s[2], myfmt(shrink=True, align="right"))
                worksheet.write(i, 7, s[3], myfmt(shrink=True, align="right"))
                worksheet.write(i, 8, s[4], myfmt(shrink=True, align="right"))
                worksheet.write(i, 9, s[5], myfmt(shrink=True, align="left"))
                
        row += len(mydata[str(d)]["item_table"])
        for i in xrange(row, row+2):
            worksheet.merge_range(i, 0, i, 3, "", myfmt(align="left", shrink=True))
            worksheet.write(i, 4, "", myfmt(shrink=True))
            worksheet.merge_range(i, 5, i, 6, "", myfmt(shrink=True, align="right"))
            worksheet.write(i, 7, "", myfmt(shrink=True, align="right"))
            worksheet.write(i, 8, "", myfmt(shrink=True, align="right"))
            worksheet.write(i, 9, "", myfmt(shrink=True, align="left"))
        row += 2
        plug_head(dd['i_project_status'], row, (dd['i_project_status'].count('\n') + 2) * 17, bold=False)
        row += 1
        if dd['over_20190501']:
            plug_head(u"二、監督依照設計圖說及核定施工圖說施工（含約定之檢驗停留點及施工抽查等情形）：", row, 29)
        else:
            plug_head(u"二、監督依照設計圖說施工(含約定之檢驗停留點及施工抽查等情形)：", row, 29)
        plug_head(dd['note'], row+1, (dd['note'].count('\n') + 2) * 17, bold=False)
        plug_head(u"三、查核材料規格及品質(含約定之檢驗停留點、材料設備管制及檢（試）驗等抽驗情形)：", row+2)
        plug_head(dd['sampling'], row+3, (dd['sampling'].count('\n') + 2) * 17, bold=False)
        plug_head(u"四、督導工地職業安全衛生事項：", row+4)
        describe_subcontractor = u'(一)施工廠商施工前檢查事項辦理情形：' + dd['pre_check'] + '\n    '
        describe_subcontractor += dd['i_pre_check'].replace('\n', '\n    ')
        describe_subcontractor += u'\n(二)其他工地安全衛生督導事項：\n    ' + dd['describe_subcontractor'].replace('\n', '\n    ')
        plug_head(describe_subcontractor, row+5, (describe_subcontractor.count('\n') + 2) * 17, bold=False)
        plug_head(u"五、其他約定監造事項(重要事項紀錄、主辦機關指示及通知廠商辦理事項等)：", row+6)
        plug_head(dd['notify'], row+7, (dd['notify'].count('\n') + 2) * 17, bold=False)
        plug_head(u"監造單位簽章：", row+8, 55)
    return workbook


#製造施工日誌Excel.xlsx
def make_contractor_excel_file2(workbook="", data={}):
    #設定每個cell的格式
    def myfmt(border=1, bg_color="", shrink="", align="center", text_wrap="", font_name=u"標楷體", font_size=10, num_format="", bold=False):
        fmt = workbook.add_format()
        if border:
            fmt.set_border(border)
        if bg_color:
            fmt.set_bg_color(bg_color)
        if shrink:
            fmt.set_shrink(shrink)
        if align:
            fmt.set_align(align)
        if text_wrap:
            fmt.set_text_wrap(text_wrap)
        if font_name:
            fmt.set_font_name(font_name)
        if font_size:
            fmt.set_font_size(font_size)
        if num_format:
            fmt.set_num_format(num_format)
        if bold:
            fmt.set_bold(bold)
        fmt.set_align('top')

        return fmt 

    #列印大標題用的
    def plug_head(x, row, myheight=17, bold=True):
        worksheet.set_row(row, myheight)
        worksheet.merge_range(row, 0, row, 9, x, myfmt(text_wrap=True, align="left", bold=bold))

    mydata=data["reports"]
    date_keys = [datetime.datetime.strptime(date_key, '%Y-%m-%d').date() for date_key in mydata]
    date_keys.sort() #要照日期排序
    for d in date_keys:
        dd = mydata[str(d)]["replace"]
        # 新增一個sheet
        worksheet = workbook.add_worksheet(dd["reportdate"])
        worksheet.set_margins(left=0.5, right=0.5, top=0.5, bottom=0.5)
        worksheet.set_header(header='',margin=0.0)
        worksheet.set_paper(9)
        row = 0 #第一列的編號為0

        # Basic format
        column_width=[11.75, 11.75, 11.75, 5.8, 5.8, 5.8, 5.8, 11.75, 11.75, 11.75]
        # set cloumn width 
        for i, e in enumerate(column_width):
            worksheet.set_column(i, i, e)

        # 第一列合併
        worksheet.merge_range(row, 0, row, 9, u'公共工程施工日誌', myfmt(border=0, font_size=14)) 
        
        # basic information 
        worksheet.write(row+1, 0, u"報表編號：", myfmt(border=0))
        row += 2
        worksheet.write(row, 0, u"本日天氣：", myfmt(border=0))
        worksheet.merge_range(row, 1, row, 5, u"上午：%s 下午：%s" % (dd["morning_weather"], dd["afternoon_weather"]), myfmt(border=0, align="left")) 
        worksheet.merge_range(row, 6, row, 9, u"填報日期： %s" % dd["reportdate"], myfmt(border=0, align="left", font_size="14")) 
        row += 1
        worksheet.write(row, 0, u"工程名稱", myfmt())
        worksheet.merge_range(row, 1, row, 9, dd["project_name"], myfmt(align="left"))
        row += 1
        worksheet.write(row, 0, u"承攬廠商名稱", myfmt(shrink=True))
        worksheet.merge_range(row, 1, row, 9, dd["project_contractor_name"], myfmt(align="left"))
        row += 1
        worksheet.write(row, 0, u"核定工期", myfmt())
        worksheet.write(row, 1, u"%s 天" % dd["duration"], myfmt())
        worksheet.write(row, 2, u"累計工期", myfmt())
        worksheet.merge_range(row, 3, row, 4, "%s 天" % dd["used_duration"], myfmt())
        worksheet.merge_range(row, 5, row, 6, u"剩餘工期", myfmt())
        worksheet.write(row, 7, u"%s 天" % dd["unused_duration"], myfmt())
        worksheet.write(row, 8, u"工期展延天數", myfmt(shrink=True))
        worksheet.write(row, 9, u"%s 天" % dd["extension"], myfmt())
        row += 1
        worksheet.write(row,0, "開工日期", myfmt())
        worksheet.merge_range(row, 1, row, 4, dd["start_date"], myfmt())
        worksheet.merge_range(row, 5, row, 6, "預定完工日期", myfmt(shrink=True))
        worksheet.merge_range(row, 7, row, 9, dd["end_date"], myfmt())
        row += 1
        worksheet.write(row,0, "預定進度", myfmt())
        worksheet.merge_range(row, 1, row, 4, str(dd["design_percent"]) + " %", myfmt())
        worksheet.merge_range(row, 5, row, 6, "實際進度", myfmt())
        worksheet.merge_range(row, 7, row, 9, str(dd["act_percent"]) + " %", myfmt())
        row += 1
        plug_head(u"一、依施工計畫書執行按圖施工概況（含約定之重要施工項目及完成數量等）：", row)
        row += 1
        worksheet.merge_range(row, 0, row, 3, u"施工項目", myfmt())
        worksheet.write(row, 4, u"單位", myfmt())
        worksheet.merge_range(row, 5, row, 6, u"契約數量",myfmt())
        worksheet.write(row, 7, u"本日完成", myfmt())
        worksheet.write(row, 8, u"累計完成", myfmt())
        worksheet.write(row, 9, u"備註", myfmt())
        row += 1
        for k, s in enumerate(mydata[str(d)]["item_table"]):
            i = row + k
            worksheet.merge_range(i, 0, i, 3, s[0], myfmt(align="left", shrink=True))
            if s[-1] == 'dir':
                worksheet.merge_range(i, 4, i, 9, "", myfmt())
            else:
                worksheet.write(i, 4, s[1], myfmt(shrink=True))
                worksheet.merge_range(i, 5, i, 6, s[2], myfmt(shrink=True, align="right"))
                worksheet.write(i, 7, s[3], myfmt(shrink=True, align="right"))
                worksheet.write(i, 8, s[4], myfmt(shrink=True, align="right"))
                worksheet.write(i, 9, s[5], myfmt(shrink=True, align="left"))
                
        row += len(mydata[str(d)]["item_table"])
        for i in xrange(row, row+2):
            worksheet.merge_range(i, 0, i, 3, "", myfmt(align="left", shrink=True))
            worksheet.write(i, 4, "", myfmt(shrink=True))
            worksheet.merge_range(i, 5, i, 6, "", myfmt(shrink=True, align="right"))
            worksheet.write(i, 7, "", myfmt(shrink=True, align="right"))
            worksheet.write(i, 8, "", myfmt(shrink=True, align="right"))
            worksheet.write(i, 9, "", myfmt(shrink=True, align="left"))
        row += 2
        plug_head(u"二、工地材料管理概況(含約定之重要材料使用狀況及數量等)：", row)
        row += 1
        worksheet.merge_range(row, 0, row, 3, u"材料名稱", myfmt())
        worksheet.write(row, 4, u"單位", myfmt())
        worksheet.merge_range(row, 5, row, 6, u"設計數量",myfmt())
        worksheet.write(row, 7, u"本日完成數量", myfmt(shrink=True))
        worksheet.write(row, 8, u"累計完成數量", myfmt(shrink=True))
        worksheet.write(row, 9, u"備註", myfmt())
        row += 1
        for k, s in enumerate(mydata[str(d)]["site_material_table"]):
            i = row + k
            worksheet.merge_range(i, 0, i, 3, s[0], myfmt(align="left", shrink=True))
            worksheet.write(i, 4, s[1], myfmt(shrink=True))
            worksheet.merge_range(i, 5, i, 6, s[2], myfmt(shrink=True, align="right"))
            worksheet.write(i, 7, s[3], myfmt(shrink=True, align="right"))
            worksheet.write(i, 8, s[4], myfmt(shrink=True, align="right"))
            worksheet.write(i, 9, s[5], myfmt(shrink=True, align="left"))
        row += len(mydata[str(d)]["site_material_table"])
        for i in xrange(row, row+2):
            worksheet.merge_range(i, 0, i, 3, "", myfmt(align="left", shrink=True))
            worksheet.write(i, 4, "", myfmt(shrink=True))
            worksheet.merge_range(i, 5, i, 6, "", myfmt(shrink=True, align="right"))
            worksheet.write(i, 7, "", myfmt(shrink=True, align="right"))
            worksheet.write(i, 8, "", myfmt(shrink=True, align="right"))
            worksheet.write(i, 9, "", myfmt(shrink=True, align="left"))
        row += 2
        plug_head(u"三、工地人員及機具管理(含約定之出工人數及機具使用情形及數量)：", row)
        row += 1
        worksheet.merge_range(row, 0, row, 1, u"工別", myfmt())
        worksheet.write(row, 2, u"本日人數", myfmt())
        worksheet.merge_range(row, 3, row, 4, u"累計人數", myfmt())
        worksheet.merge_range(row, 5, row, 7, u"機具名稱", myfmt())
        worksheet.write(row, 8, u"本日使用數量", myfmt(shrink=True))
        worksheet.write(row, 9, u"累計使用數量", myfmt(shrink=True))
        row += 1
        for k, s in enumerate(mydata[str(d)]["manmachine_table"]):
            i = row + k
            worksheet.merge_range(i, 0, i, 1, s[0], myfmt(shrink=True))
            worksheet.write(i, 2, s[1], myfmt())
            worksheet.merge_range(i, 3, i, 4, s[2], myfmt())
            worksheet.merge_range(i, 5, i, 7, s[3], myfmt(shrink=True))
            worksheet.write(i, 8, s[4], myfmt())
            worksheet.write(i, 9, s[5], myfmt())
        row += len(mydata[str(d)]["manmachine_table"])
        plug_head(u"四、本日施工項目是否有須依「營造業專業工程特定施工項目應置之技術士種類、比率或人數標準表」規定應設置技術士之專業工程：%s（此項如勾選”有”，則應填寫後附「建築物施工日誌之技術士簽章表」）" % dd['has_professional_item'], row, 46)
        row += 1
        plug_head(u"五、工地勞工安全衛生事項之督導、公共環境與安全之維護及其他工地行政事務：", row)
        plug_head(dd['describe_subcontractor'], row+1, (dd['describe_subcontractor'].count('\n') + 2) * 17, bold=False)
        plug_head(u"六、施工取樣試驗紀錄：", row+2)
        plug_head(dd['sampling'], row+3, (dd['sampling'].count('\n') + 2) * 17, bold=False)
        plug_head(u"七、通知分包商辦理事項：", row+4)
        plug_head(dd['notify'], row+5, (dd['notify'].count('\n') + 2) * 17, bold=False)
        plug_head(u"八、重要事項紀錄：", row+6, 29)
        plug_head(dd['note'], row+7, (dd['note'].count('\n') + 2) * 17, bold=False)
        plug_head(u"簽章：【工地主任】：", row+8, 55)
    return workbook


#製造監造報表Excel.xlsx
def make_inspector_excel_file2(workbook="", data={}):
    #設定每個cell的格式
    def myfmt(border=1, bg_color="", shrink="", align="center", text_wrap="", font_name=u"標楷體", font_size=10, num_format="", bold=False):
        fmt = workbook.add_format()
        if border:
            fmt.set_border(border)
        if bg_color:
            fmt.set_bg_color(bg_color)
        if shrink:
            fmt.set_shrink(shrink)
        if align:
            fmt.set_align(align)
        if text_wrap:
            fmt.set_text_wrap(text_wrap)
        if font_name:
            fmt.set_font_name(font_name)
        if font_size:
            fmt.set_font_size(font_size)
        if num_format:
            fmt.set_num_format(num_format)
        if bold:
            fmt.set_bold(bold)
        fmt.set_align('top')

        return fmt 

    #列印大標題用的
    def plug_head(x, row, myheight=17, bold=True):
        worksheet.set_row(row, myheight)
        worksheet.merge_range(row, 0, row, 9, x, myfmt(text_wrap=True, align="left", bold=bold))

    mydata=data["reports"]
    date_keys = [datetime.datetime.strptime(date_key, '%Y-%m-%d').date() for date_key in mydata]
    date_keys.sort() #要照日期排序
    for d in date_keys:
        dd = mydata[str(d)]["replace"]
        # 新增一個sheet
        worksheet = workbook.add_worksheet(dd["reportdate"])
        worksheet.set_margins(left=0.5, right=0.5, top=0.5, bottom=0.5)
        worksheet.set_header(header='',margin=0.0) 
        worksheet.set_paper(9) 
        row = 0 #第一列的編號為0

        # Basic format
        column_width=[11.75, 11.75, 11.75, 5.8, 5.8, 5.8, 5.8, 11.75, 11.75, 11.75]
        # set cloumn width 
        for i, e in enumerate(column_width):
            worksheet.set_column(i, i, e)

        # 第一列合併
        worksheet.merge_range(row, 0, row, 9, u'公共工程監造報表', myfmt(border=0, font_size=14)) 
        
        # basic information 
        worksheet.write(row+1, 0, u"報表編號：", myfmt(border=0))
        row += 2
        worksheet.write(row, 0, u"本日天氣：", myfmt(border=0))
        worksheet.merge_range(row, 1, row, 5, u"上午：%s 下午：%s" % (dd["morning_weather"], dd["afternoon_weather"]), myfmt(border=0, align="left")) 
        worksheet.merge_range(row, 6, row, 9, u"填報日期： %s" % dd["reportdate"], myfmt(border=0, align="left", font_size="14")) 
        row += 1
        worksheet.write(row, 0, u"工程名稱", myfmt())
        worksheet.merge_range(row, 1, row, 9, dd["project_name"], myfmt(align="left"))
        row += 1
        worksheet.write(row, 0, u"契約工期", myfmt())
        worksheet.write(row, 1, u"%s 天" % dd["duration"], myfmt())
        worksheet.write(row, 2, u"開工日期", myfmt())
        worksheet.merge_range(row, 3, row, 4, dd["start_date"], myfmt())
        worksheet.merge_range(row, 5, row, 6, u"預定完工日期", myfmt(shrink=True))
        worksheet.write(row, 7, dd["end_date"], myfmt())
        worksheet.write(row, 8, u"實際完工日期", myfmt(shrink=True))
        worksheet.write(row, 9, u"", myfmt())
        row += 1
        worksheet.write(row, 0, u"契約變更次數", myfmt(shrink=True))
        worksheet.write(row, 1, u"%s 次" % dd["change_version_times"], myfmt())
        worksheet.write(row, 2, u"工期展延天數", myfmt(shrink=True))
        worksheet.merge_range(row, 3, row, 4, u"%s 天" % dd["extension"], myfmt())
        worksheet.merge_range(row, 5, row+1, 6, u"契約金額", myfmt())
        worksheet.write(row, 7, u"原契約：", myfmt(shrink=True))
        worksheet.merge_range(row, 8, row, 9, dd["init_version_price"], myfmt(shrink=True, align="right", num_format="#,##0 元"))
        row += 1
        worksheet.write(row, 0, u"預定進度", myfmt())
        worksheet.write(row, 1, str(dd["design_percent"]) + " %", myfmt(shrink=True))
        worksheet.write(row, 2, u"實際進度", myfmt())
        worksheet.merge_range(row, 3, row, 4, str(dd["act_percent"]) + " %", myfmt(shrink=True))
        worksheet.write(row, 7, u"變更後契約：", myfmt())
        worksheet.merge_range(row, 8, row, 9, dd["change_version_price"], myfmt(shrink=True, align="right", num_format="#,##0 元"))
        row += 1
        plug_head(u"一、工程進行情況(含約定之重要施工項目及數量)：", row)
        row += 1
        worksheet.merge_range(row, 0, row, 3, u"施工項目", myfmt())
        worksheet.write(row, 4, u"單位", myfmt())
        worksheet.merge_range(row, 5, row, 6, u"契約數量",myfmt())
        worksheet.write(row, 7, u"本日完成", myfmt())
        worksheet.write(row, 8, u"累計完成", myfmt())
        worksheet.write(row, 9, u"備註", myfmt())
        row += 1
        for k, s in enumerate(mydata[str(d)]["item_table"]):
            i = row + k
            worksheet.merge_range(i, 0, i, 3, s[0], myfmt(align="left", shrink=True))
            if s[-1] == 'dir':
                worksheet.merge_range(i, 4, i, 9, "", myfmt())
            else:
                worksheet.write(i, 4, s[1], myfmt(shrink=True))
                worksheet.merge_range(i, 5, i, 6, s[2], myfmt(shrink=True, align="right"))
                worksheet.write(i, 7, s[3], myfmt(shrink=True, align="right"))
                worksheet.write(i, 8, s[4], myfmt(shrink=True, align="right"))
                worksheet.write(i, 9, s[5], myfmt(shrink=True, align="left"))
                
        row += len(mydata[str(d)]["item_table"])
        for i in xrange(row, row+2):
            worksheet.merge_range(i, 0, i, 3, "", myfmt(align="left", shrink=True))
            worksheet.write(i, 4, "", myfmt(shrink=True))
            worksheet.merge_range(i, 5, i, 6, "", myfmt(shrink=True, align="right"))
            worksheet.write(i, 7, "", myfmt(shrink=True, align="right"))
            worksheet.write(i, 8, "", myfmt(shrink=True, align="right"))
            worksheet.write(i, 9, "", myfmt(shrink=True, align="left"))
        row += 2
        plug_head(u"工程進行情況補充說明：", row)
        row += 1
        plug_head(dd['describe_subcontractor'], row, (dd['describe_subcontractor'].count('\n') + 2) * 17, bold=False)
        row += 1
        plug_head(u"二、監督依照設計圖說施工(含約定之檢驗停留點及施工抽查等情形)：", row, 29)
        plug_head(dd['note'], row+1, (dd['note'].count('\n') + 2) * 17, bold=False)
        plug_head(u"三、查核材料規格及品質(含約定之檢驗停留點、材料設備管制及檢（試）驗等抽驗情形)：", row+2)
        plug_head(dd['sampling'], row+3, (dd['sampling'].count('\n') + 2) * 17, bold=False)
        plug_head(u"四、其他約定監造事項(含督導工地勞工安全衛生事項、重要事項紀錄、主辦機關指示及通知廠商辦理事項等)：", row+4)
        plug_head(dd['notify'], row+5, (dd['notify'].count('\n') + 2) * 17, bold=False)
        plug_head(u"監造單位簽章：", row+6, 55)
    return workbook



#製造工期彙整Excel.xlsx
def make_working_date_excel_file(workbook="", engprofile=None):
    w_dates = engprofile.readWorkingDate()
    project = engprofile.project
    last_date = w_dates[-1]

    #設定每個cell的格式
    def myfmt(border=1, bg_color="", shrink="", align="center", text_wrap="", font_name=u"標楷體", font_size=10, num_format="", bold=False):
        fmt = workbook.add_format()
        if border:
            fmt.set_border(border)
        if bg_color:
            fmt.set_bg_color(bg_color)
        if shrink:
            fmt.set_shrink(shrink)
        if align:
            fmt.set_align(align)
        if text_wrap:
            fmt.set_text_wrap(text_wrap)
        if font_name:
            fmt.set_font_name(font_name)
        if font_size:
            fmt.set_font_size(font_size)
        if num_format:
            fmt.set_num_format(num_format)
        if bold:
            fmt.set_bold(bold)
        fmt.set_align('top')

        return fmt 

    worksheet = workbook.add_worksheet(u'工期彙整')
    worksheet.set_margins(left=0.5, right=0.5, top=0.5, bottom=0.5)
    worksheet.set_header(header='',margin=0.0)
    worksheet.set_paper(9)
    weekday_name = [u'一', u'二', u'三', u'四', u'五', u'六', u'日']
    row = 0 #第一列的編號為0

    # Basic format
    column_width=[12, 8] + ([5] * 31)
    # set cloumn width 
    for i, e in enumerate(column_width):
        worksheet.set_column(i, i, e)

    date = datetime.datetime.strptime('%s-%s-01' % (w_dates[0].year, w_dates[0].month), '%Y-%m-%d').date()
    while date < last_date:
        worksheet.merge_range(row, 0, row+2, 0, u"%s-%s月" % (date.year, date.month), myfmt(border=1, align="center", bg_color='#1EE0BE')) 
        worksheet.write(row, 1, u"日期", myfmt(border=1, align="center"))
        worksheet.write(row+1, 1, u"星期", myfmt(border=1, align="center"))
        worksheet.write(row+2, 1, u"累積", myfmt(border=1, align="center"))

        last_day_num = monthrange(date.year, date.month)[1]
        for d in xrange(1, last_day_num+1):
            worksheet.write(row, 1+d, d, myfmt(border=1, align="center", bg_color='#EFCF00'))
            worksheet.write(row+1, 1+d, weekday_name[date.isoweekday()-1], myfmt(border=1, align="center"))
            if date in w_dates:
                worksheet.write(row+2, 1+d, w_dates.index(date)+1, myfmt(border=1, align="center"))
            else:
                worksheet.write(row+2, 1+d, u'', myfmt(border=1, align="center"))
            date += datetime.timedelta(days=1)

        row += 3

    return workbook
