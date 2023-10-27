# -*- coding: utf-8 -*-
import sys, os, random, json, re, datetime, math, smtplib, decimal, xlsxwriter, calendar
from os import makedirs
from os.path import join, exists, basename
from io import StringIO
from time import time

from django.db.models import Q, Sum
from optparse import make_option
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Group, Permission
from django.conf import settings

from supervise.models import *

def TODAY(): return datetime.date.today()


export_path = join(settings.MEDIA_ROOT, 'supervise', 'error_info')
if not exists(export_path): makedirs(export_path)

  
class Command(BaseCommand):
    help = 'export 匯出督導缺失資訊'
    def add_arguments(self, parser):
        parser.add_argument(
            '--from',
            dest='from',
            help='input from like --from=2019-01-01',
        )
        parser.add_argument(
            '--to',
            dest='to',
            help='input to like --to=2019-12-31',
        )

    def handle(self, *args, **kw):
        from_date = kw['from']
        to_date = kw['to']
        if not from_date:
            from_date = '%s-01-01' % TODAY().year

        if not to_date:
            to_date = '%s-12-31' % TODAY().year

        output = join(export_path, u'%s.xlsx' % (TODAY()))

        workbook = xlsxwriter.Workbook(output, 
                    {'strings_to_numbers':  True,
                    'strings_to_formulas': False,
                    'strings_to_urls':     False})

        #設定每個cell的格式
        def myfmt(border_single=[0,0,0,0], underline="", border=1, bg_color="", indent="", shrink="", align="center", valign="vcenter", text_wrap="", font_name=u"標楷體", font_size=12, num_format="", bold=False, color=False):
            fmt = workbook.add_format()
            if border: fmt.set_border(border) #邊框
            else:
                if border_single[0]: fmt.set_top(border_single[0]) #邊框上
                if border_single[1]: fmt.set_bottom(border_single[1]) #邊框下
                if border_single[2]: fmt.set_left(border_single[2]) #邊框左
                if border_single[3]: fmt.set_right(border_single[3]) #邊框右
            if bg_color: fmt.set_bg_color(bg_color) #背景顏色
            if shrink: fmt.set_shrink(shrink) #自動縮小符合欄寬
            if align: fmt.set_align(align) #左右對齊
            if valign: fmt.set_align(valign) #上下對齊
            if text_wrap: fmt.set_text_wrap(text_wrap) #自動換列
            if font_name: fmt.set_font_name(font_name) #字型
            if font_size: fmt.set_font_size(font_size) #字體大小
            if num_format: fmt.set_num_format(num_format) #格式化顯示
            if bold: fmt.set_bold(bold) #粗體
            if indent: fmt.set_indent(indent) #縮排
            if color: fmt.set_font_color(color) #文字顏色
            if underline: fmt.set_underline(underline) #文字加底線 1  2  33  34
            return fmt

        errors = Error.objects.filter(case__date__gte=from_date, case__date__lte=to_date).order_by('ec__no', 'level__id')

        # 新增一個sheet
        worksheet = workbook.add_worksheet(u"%s-%s全缺失" % (from_date, to_date))
        worksheet.set_margins(left=0.5, right=0.5, top=0.5, bottom=0.5)
        worksheet.set_header(header='',margin=0.0)   
        worksheet.set_paper(9) 
        row = 0 #第一列的編號為0
        break_lines = [] #插入分頁符號位置

        column_width=[
           #  A   B   C   D   E   F   G
              7, 15, 25, 65, 15, 10, 65
        ]  
        for i, e in enumerate(column_width):
            worksheet.set_column(i, i, e)

        worksheet.write(row, 0, u'序號', myfmt())
        worksheet.write(row, 1, u'督導日期', myfmt())
        worksheet.write(row, 2, u'標案編號', myfmt())
        worksheet.write(row, 3, u'工程名稱', myfmt())
        worksheet.write(row, 4, u'缺失編號', myfmt())
        worksheet.write(row, 5, u'缺失程度', myfmt())
        worksheet.write(row, 6, u'缺失內容', myfmt())
        row += 1

        for n, e in enumerate(errors):
            worksheet.write(row, 0, n+1, myfmt())
            worksheet.write(row, 1, e.case.date, myfmt(num_format="YYYY-MM-DD"))
            worksheet.write_formula(row, 2, '="%s"' % (e.case.uid), myfmt(align="left"))
            worksheet.write(row, 3, e.case.project, myfmt(align="left"))
            worksheet.write(row, 4, e.ec.no, myfmt())
            worksheet.write(row, 5, e.level.name, myfmt())
            worksheet.write(row, 6, e.context.replace('\n', '').replace('\r', ''), myfmt(align="left"))
            row += 1

        worksheet.center_horizontally() #置中
        workbook.close()