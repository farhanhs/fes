# -*- coding: utf-8 -*-
import sys, datetime

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Group, Permission
from django.conf import settings
import xlsxwriter
from cStringIO import StringIO

from supervise.models import *

import smtplib
from email import encoders
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.utils import COMMASPACE, formatdate

TODAY = lambda: datetime.date.today()

class Command(BaseCommand):
    help = u'寄信督導紀錄尚未填報完成改善紀錄的'


    def handle(self, *args, **kw):

        #開始製造EXCEL
        output = StringIO()
        workbook = xlsxwriter.Workbook(output, 
                    {'strings_to_numbers':  True,
                    'strings_to_formulas': False,
                    'strings_to_urls':     False})

        #設定每個cell的格式
        def myfmt(border=1, bg_color="", shrink="", align="center", valign="top", text_wrap="", font_name=u"標楷體", font_size=12, num_format="", bold=False):
            fmt = workbook.add_format()
            if border: fmt.set_border(border)
            if bg_color: fmt.set_bg_color(bg_color)
            if shrink: fmt.set_shrink(shrink)
            if align: fmt.set_align(align)
            if valign: fmt.set_align(valign)
            if text_wrap: fmt.set_text_wrap(text_wrap)
            if font_name: fmt.set_font_name(font_name)
            if font_size: fmt.set_font_size(font_size)
            if num_format: fmt.set_num_format(num_format)
            if bold: fmt.set_bold(bold)

            return fmt

        # 新增一個sheet---------
        worksheet = workbook.add_worksheet(u'督導尚未改善')
        worksheet.set_margins(left=0.5, right=0.5, top=0.5, bottom=0.5)
        worksheet.set_header(header='',margin=0.0)  
        worksheet.set_paper(9)
        row = 0 #第一列的編號為0

        column_width=[7,15,70,70,10,12,12,60]

        for i, e in enumerate(column_width):
            worksheet.set_column(i, i, e)

        worksheet.write(row, 0, u'項次', myfmt(align="center", valign="midle", bg_color="#FEFFCD"))
        worksheet.write(row, 1, u'督導日期', myfmt(align="center", valign="midle", bg_color="#FEFFCD"))
        worksheet.write(row, 2, u'列管計畫名稱', myfmt(align="center", valign="midle", bg_color="#FEFFCD"))
        worksheet.write(row, 3, u'標案名稱', myfmt(align="center", valign="midle", bg_color="#FEFFCD"))
        worksheet.write(row, 4, u'縣市', myfmt(align="center", valign="midle", text_wrap=True, bg_color="#FEFFCD"))
        worksheet.write(row, 5, u'缺失數量', myfmt(align="center", valign="midle", text_wrap=True, bg_color="#FEFFCD"))
        worksheet.write(row, 6, u'已改善數量', myfmt(align="center", valign="midle", text_wrap=True, bg_color="#FEFFCD"))
        worksheet.write(row, 7, u'連結FES工程案', myfmt(align="center", valign="midle", text_wrap=True, bg_color="#FEFFCD"))
        row += 1

        for n, c in enumerate(SuperviseCase.objects.filter(date__gte=TODAY()-datetime.timedelta(days=62)).order_by('date')):
            worksheet.write(row, 0, n+1, myfmt())
            worksheet.write(row, 1, c.date, myfmt(num_format="YYYY-MM-DD"))
            worksheet.write(row, 2, c.plan, myfmt(align="left"))
            worksheet.write(row, 3, c.project, myfmt(align="left"))
            worksheet.write(row, 4, c.place.name, myfmt())
            worksheet.write(row, 5, c.error_set.all().count(), myfmt())
            worksheet.write(row, 6, c.error_set.all().count() - c.error_set.filter(date__isnull=True).count(), myfmt())
            worksheet.write(row, 7, 'https://fes.fa.gov.tw/frcm/project_profile/%s/' % (c.fes_project.id) if c.fes_project else u'', myfmt(align="left"))
            row += 1

        worksheet.freeze_panes(1, 0) #凍結視窗
        workbook.close()
        output.seek(0)

        smtpserver = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
        smtpserver.ehlo()
        # smtpserver.starttls()
        # smtpserver.ehlo()
        #登入系統
        smtpserver.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)

        #寄件人資訊
        fromaddr = settings.EMAIL_HOST_USER

        #收件人列表，格式為list即可
        toaddrs = [u'johnisacoolboy@gmail.com', 'fes@ms1.fa.gov.tw']

        msg = MIMEMultipart()
        msg['From']=fromaddr
        msg['To']=COMMASPACE.join(toaddrs)
        msg['Date']=formatdate(localtime=True)
        msg['Subject']=u'漁業署FES工程管理-督導紀錄改善填報情形彙整'

        #你要寫的內容
        info = u''
        info += u'<br>您好，這封信由系統自動寄出，請勿回信<br><br>'
        info += u'督導紀錄改善填報情形彙整如附件<br>'

        def containsnonasciicharacters(str):
            return not all(ord(c) < 128 for c in str)

        if containsnonasciicharacters(info):
            htmltext = MIMEText(info.encode('utf-8', 'replace'), 'html','utf-8')
        else:
            htmltext = MIMEText(info, 'html')

        msg.attach(htmltext)

        file_part = MIMEBase('application', "octet-stream")
        file_part.set_payload(output.read())
        encoders.encode_base64(file_part)
        filename = u'%s-records.xlsx' % (TODAY())
        file_part.add_header('Content-Disposition', 'attachment; filename="%s"' % (filename))
        msg.attach(file_part)

        smtpserver.sendmail(fromaddr, toaddrs, msg.as_string())

        #記得要登出
        smtpserver.quit()




        
            

