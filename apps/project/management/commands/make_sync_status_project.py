# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
import os, datetime, decimal, random
from fishuser.models import *
from pccmating.models import ProjectProgress

from django.conf import settings
import smtplib
from email import encoders
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.utils import COMMASPACE, formatdate
import xlsxwriter

def TODAY(): return datetime.date.today()

class Command(BaseCommand):
    help = u"每月1日凌晨寄信通知尚未填寫    負責主辦"

    def handle(self, *args, **kw):

        def myfmt(border=1, bg_color="", shrink="", align="center", text_wrap=True, font_name=u"新細明體", font_size=12, num_format="", bold=False):
            fmt = workbook.add_format()
            if border: fmt.set_border(border)
            if bg_color: fmt.set_bg_color(bg_color)
            if shrink: fmt.set_shrink(shrink)
            if align: fmt.set_align(align)
            if text_wrap: fmt.set_text_wrap(text_wrap)
            if font_name: fmt.set_font_name(font_name)
            if font_size: fmt.set_font_size(font_size)
            if num_format: fmt.set_num_format(num_format)
            if bold: fmt.set_bold(bold)
            fmt.set_align('vcenter')

            return fmt 

        output = 'E:/ABC.xlsx'
        workbook = xlsxwriter.Workbook(output, 
            {'strings_to_numbers':  True,
            'strings_to_formulas': False,
            'strings_to_urls':     False})

        # 新增一個sheet
        worksheet = workbook.add_worksheet(u'工程')
        worksheet.set_margins(left=0.5, right=0.5, top=0.5, bottom=0.5)
        worksheet.set_header(header='',margin=0.0)  
        row = 0 #第一列的編號為0
        # Basic format
        column_width=[
            #   A   B   C   D   E   F   G   H   I   J   K   L   M   N   O
                9,  9, 10, 10, 10, 20, 10, 10, 10, 10, 10, 10, 10, 10, 100 ]
        # set cloumn width 
        for i, e in enumerate(column_width):
            worksheet.set_column(i, i, e)

        worksheet.set_row(row, 55)
        bg_color = "#CDFEFF"
        worksheet.write(row, 0, u"項次", myfmt(bg_color=bg_color))
        worksheet.write(row, 1, u"追蹤", myfmt(bg_color=bg_color))
        worksheet.write(row, 2, u"追蹤填報", myfmt(bg_color=bg_color))
        worksheet.write(row, 3, u"追蹤填報\n預計進度", myfmt(bg_color=bg_color))
        worksheet.write(row, 4, u"追蹤填報\n實際進度", myfmt(bg_color=bg_color))
        worksheet.write(row, 5, u"工程會\n標案編號", myfmt(bg_color=bg_color))
        worksheet.write(row, 6, u"工程會\n同步狀態", myfmt(bg_color=bg_color))
        worksheet.write(row, 7, u"工程會\n同步進度\n最後月份", myfmt(bg_color=bg_color))
        worksheet.write(row, 8, u"工程會\n同步進度\n預計進度", myfmt(bg_color=bg_color))
        worksheet.write(row, 9, u"工程會\n同步進度\n實際進度", myfmt(bg_color=bg_color))
        worksheet.write(row, 10, u"是否\n匯入遠端", myfmt(bg_color=bg_color))
        worksheet.write(row, 11, u"系統ID", myfmt(bg_color=bg_color))
        worksheet.write(row, 12, u"年度", myfmt(bg_color=bg_color))
        worksheet.write(row, 13, u"縣市", myfmt(bg_color=bg_color))
        worksheet.write(row, 14, u"工程名稱", myfmt(bg_color=bg_color))

        row += 1
        p_ids = []
        for i in CountyChaseProjectOneByOne.objects.filter(project__deleter__isnull=True, project__year__gt=101, project__purchase_type__value__in=[u"工程", u"工程勞務"], act_eng_do_closed__isnull=True):
            if i.act_eng_do_approved_plan and i.act_eng_do_approved_plan < TODAY(): continue
            p_ids.append(i.project.id)

        for i in CountyChaseProjectOneByOne.objects.filter(project__deleter__isnull=True, project__year__gt=101, project__purchase_type__value=u"一般勞務", act_ser_acceptance_closed__isnull=True):
            if i.act_ser_approved_plan and i.act_ser_approved_plan < TODAY(): continue
            p_ids.append(i.project.id)

        chase = CountyChaseTime.objects.all().order_by('-id').first()
        chase_records = chase.countychaseprojectonetomany_set.all()
        chase_project_ids = [i.project.id for i in chase_records]
        chase_project_ids_ok = [i.project.id for i in chase_records.filter(complete=True)]
        fail_code = ["022-1061115","103317","AGCO106060","107-02","1061222K","CW-1108025","1070613","108150310190"]
        projects = Project.objects.filter(id__in=p_ids).order_by('place', 'name')

        for n, p in enumerate(projects):
            worksheet.write(row, 0, n+1, myfmt())
            worksheet.write(row, 1, u"是" if p.id in chase_project_ids else u'', myfmt())
            worksheet.write(row, 2, u"完成" if p.id in chase_project_ids_ok else u'', myfmt())
            worksheet.write(row, 3, chase_records.get(project=p).schedul_progress_percent/decimal.Decimal('100')if p.id in chase_project_ids else u'', myfmt(num_format='0.00%', align="right"))
            worksheet.write(row, 4, chase_records.get(project=p).actual_progress_percent/decimal.Decimal('100')if p.id in chase_project_ids else u'', myfmt(num_format='0.00%', align="right"))
            worksheet.write(row, 5, p.pcc_no if p.pcc_no else u'', myfmt())
            worksheet.write(row, 6, u'成功' if p.pcc_no not in fail_code and p.pcc_no else u'', myfmt())
            progress = ProjectProgress.objects.filter(project__uid=p.pcc_no).order_by('-year', '-month')
            if progress:
                last_progress = progress.first()
            else:
                last_progress = None
            worksheet.write(row, 7, u'%s年-%s月' % (last_progress.year, str(last_progress.month).zfill(2)) if last_progress else u'', myfmt())
            worksheet.write(row, 8, last_progress.percentage_of_predict_progress if last_progress else u'', myfmt(num_format="0.00%", align="right"))
            worksheet.write(row, 9, last_progress.percentage_of_real_progress if last_progress else u'', myfmt(num_format="0.00%", align="right"))
            worksheet.write(row, 10, u"是" if p.frcmusergroup_set.filter(group__name__in=[u'負責主辦工程師', u'自辦主辦工程師']) else u'', myfmt())
            worksheet.write(row, 11, p.id, myfmt())
            worksheet.write(row, 12, p.year, myfmt())
            worksheet.write(row, 13, p.place.name, myfmt())
            worksheet.write(row, 14, p.name, myfmt(align="left"))
            row += 1