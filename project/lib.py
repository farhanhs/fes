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
from cStringIO import StringIO
from project.models import ExportCustomReportField

def TODAY(): return datetime.date.today()


#製造縣市進度追蹤Excel.xlsx
def make_chase_excel_file(workbook='', records=''):
    #設定每個cell的格式
    def myfmt(border=1, bg_color="", shrink="", align="center", text_wrap=True, font_name=u"標楷體", font_size=10, num_format="", bold=False):
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

    engs = []
    sers = []
    for i in records:
        if i.project.purchase_type.value in [u'工程', u'工程勞務']:
            engs.append(i)
        else:
            sers.append(i)
    


    # 新增一個sheet
    worksheet = workbook.add_worksheet(u'工程')
    worksheet.set_margins(left=0.5, right=0.5, top=0.5, bottom=0.5)
    worksheet.set_header(header='',margin=0.0)  
    row = 0 #第一列的編號為0
    # Basic format
    column_width=[
        #   A   B   C   D   E   F   G   H   I   J   K   L   M   N
            4, 12,  4,  7, 10, 35, 35,  9,  6,  9,  9,  9, 25, 25,
        #   O   P   Q   R   S   T   U   V   W
           12, 12, 12, 12, 12, 12, 12,  8,  8,
        #   X   Y   Z  AA  AB  AC  AD  AE  AF
           12, 12,  8, 12, 12, 35, 20, 12, 20,
        #  AG  AH  AI  AJ  AK  AL  AM  AN  AO  AP  AQ  AR  AS  AT  AU  AV  AW
           15, 15, 15, 15, 15, 15, 15, 15, 15,  8, 15, 15, 22, 15, 15, 15, 15]
    # set cloumn width 
    for i, e in enumerate(column_width):
        worksheet.set_column(i, i, e)

    # 標題列
    worksheet.set_row(row, 39)
    worksheet.set_row(row+1, 52)
    c1 = -1
    worksheet.merge_range(row, c1+1, row+1, c1+1, u"項次", myfmt(bg_color="#CDFEFF"))
    worksheet.merge_range(row, c1+2, row+1, c1+2, u"最\n後\n更\n新\n日\n期", myfmt(bg_color="#CDFEFF"))
    worksheet.merge_range(row, c1+3, row+1, c1+3, u"年度", myfmt(bg_color="#CDFEFF"))
    worksheet.merge_range(row, c1+4, row+1, c1+4, u"縣市別", myfmt(bg_color="#CDFEFF"))
    worksheet.merge_range(row, c1+5, row+1, c1+5, u"漁港別\n養殖區別", myfmt(bg_color="#CDFEFF"))
    worksheet.merge_range(row, c1+6, row+1, c1+6, u"計畫名稱", myfmt(bg_color="#CDFEFF"))
    worksheet.merge_range(row, c1+7, row+1, c1+7, u"工程名稱", myfmt(bg_color="#CDFEFF"))
    worksheet.merge_range(row, c1+8, row+1, c1+8, u"經費來源\n經常\n資本", myfmt(bg_color="#CDFEFF"))
    worksheet.merge_range(row, c1+9, row+1, c1+9, u"辦理別\n自\n委\n補", myfmt(bg_color="#CDFEFF"))
    worksheet.merge_range(row, c1+10, row+1, c1+10, u"採購類型\n勞務\n工程\n財物", myfmt(bg_color="#CDFEFF"))
    worksheet.merge_range(row, c1+11, row+1, c1+11, u"預定進度%", myfmt(bg_color="#CDFEFF"))
    worksheet.merge_range(row, c1+12, row+1, c1+12, u"實際進度%", myfmt(bg_color="#CDFEFF"))
    worksheet.merge_range(row, c1+13, row+1, c1+13, u"目前辦理情形(進度)", myfmt(bg_color="#CDFEFF"))
    worksheet.merge_range(row, c1+14, row+1, c1+14, u"落後10%以上、履約爭議或停工等請填原因及解決對策", myfmt(bg_color="#CDFEFF"))

    c2 = c1 + 14
    worksheet.merge_range(row, c2+1, row, c2+2, u"實支數\n(仟元)", myfmt(bg_color="#b5b5b5"))
    worksheet.write(row+1, c2+1, u"本署", myfmt(bg_color="#b5b5b5"))
    worksheet.write(row+1, c2+2, u"縣府", myfmt(bg_color="#b5b5b5"))
    worksheet.merge_range(row, c2+3, row, c2+4, u"應付未付數\n(仟元)", myfmt(bg_color="#b5b5b5"))
    worksheet.write(row+1, c2+3, u"本署", myfmt(bg_color="#b5b5b5"))
    worksheet.write(row+1, c2+4, u"縣府", myfmt(bg_color="#b5b5b5"))
    worksheet.write(row, c2+5, u"賸餘款\n(仟元)", myfmt(bg_color="#b5b5b5"))
    worksheet.write(row+1, c2+5, u"本署", myfmt(bg_color="#b5b5b5"))
    worksheet.merge_range(row, c2+6, row+1, c2+6, u"結餘數\n(仟元)", myfmt(bg_color="#b5b5b5"))
    worksheet.merge_range(row, c2+7, row+1, c2+7, u"本署經費執行數\n(仟元)", myfmt(bg_color="#b5b5b5"))
    worksheet.merge_range(row, c2+8, row+1, c2+8, u"執行率\n(%)", myfmt(bg_color="#b5b5b5"))
    worksheet.merge_range(row, c2+9, row+1, c2+9, u"預計至年底執行率\n(%)", myfmt(bg_color="#b5b5b5"))

    c3 = c2 + 9
    worksheet.merge_range(row, c3+1, row+1, c3+1, u"工程(計畫)總預算\n(仟元)", myfmt(bg_color="#b5b5b5"))
    worksheet.merge_range(row, c3+2, row+1, c3+2, u"漁業署編列預算\n(仟元)", myfmt(bg_color="#b5b5b5"))
    worksheet.merge_range(row, c3+3, row+1, c3+3, u"補助比例\n(%)", myfmt(bg_color="#b5b5b5"))
    worksheet.merge_range(row, c3+4, row+1, c3+4, u"工程(計畫)發包金額\n(仟元)", myfmt(bg_color="#b5b5b5"))
    worksheet.merge_range(row, c3+5, row+1, c3+5, u"漁業署實際補助金額\n(仟元)", myfmt(bg_color="#b5b5b5"))
    worksheet.merge_range(row, c3+6, row+1, c3+6, u"工作(計畫)內容", myfmt(bg_color="#CDFEFF"))
    worksheet.merge_range(row, c3+7, row+1, c3+7, u"執行單位", myfmt(bg_color="#CDFEFF"))
    worksheet.merge_range(row, c3+8, row+1, c3+8, u"執行單位聯絡窗口", myfmt(bg_color="#CDFEFF"))
    worksheet.merge_range(row, c3+9, row+1, c3+9, u"縣市政府聯絡方式(mail及電話)", myfmt(bg_color="#CDFEFF"))

    c4 = c3 + 9
    worksheet.merge_range(row, c4+1, row+1, c4+1, u"同意計畫", myfmt(bg_color="#D6FFAF"))
    worksheet.merge_range(row, c4+2, row+1, c4+2, u"核定計畫", myfmt(bg_color="#D6FFAF"))
    worksheet.merge_range(row, c4+3, row+1, c4+3, u"勞務公告上網", myfmt(bg_color="#D6FFAF"))
    worksheet.merge_range(row, c4+4, row+1, c4+4, u"勞務決標", myfmt(bg_color="#D6FFAF"))
    worksheet.merge_range(row, c4+5, row+1, c4+5, u"勞務定約", myfmt(bg_color="#D6FFAF"))
    worksheet.merge_range(row, c4+6, row+1, c4+6, u"提送預算書圖", myfmt(bg_color="#D6FFAF"))
    worksheet.merge_range(row, c4+7, row+1, c4+7, u"勞務驗收", myfmt(bg_color="#D6FFAF"))
    worksheet.merge_range(row, c4+8, row+1, c4+8, u"勞務結案", myfmt(bg_color="#D6FFAF"))
    worksheet.merge_range(row, c4+9, row+1, c4+9, u"工程公告上網", myfmt(bg_color="#E7CDFF"))
    worksheet.merge_range(row, c4+10, row+1, c4+10, u"招標期間流標次數", myfmt(bg_color="#E7CDFF"))
    worksheet.merge_range(row, c4+11, row+1, c4+11, u"工程決標", myfmt(bg_color="#E7CDFF"))
    worksheet.merge_range(row, c4+12, row+1, c4+12, u"工程定約", myfmt(bg_color="#E7CDFF"))
    worksheet.merge_range(row, c4+13, row+1, c4+13, u"工期", myfmt(bg_color="#E7CDFF"))
    worksheet.merge_range(row, c4+14, row+1, c4+14, u"開工", myfmt(bg_color="#E7CDFF"))
    worksheet.merge_range(row, c4+15, row+1, c4+15, u"完工", myfmt(bg_color="#E7CDFF"))
    worksheet.merge_range(row, c4+16, row+1, c4+16, u"驗收", myfmt(bg_color="#E7CDFF"))
    worksheet.merge_range(row, c4+17, row+1, c4+17, u"結案", myfmt(bg_color="#E7CDFF"))

    row += 2
    for n, p in enumerate(engs):
        #如果未填完者使用上次紀錄
        rows = p.project.countychaseprojectonetomany_set.filter(countychasetime__id__lt=p.countychasetime.id, complete=True).order_by('-id')
        if rows: 
            otm = rows[0]
            otm.new_record = False
        else:
            otm = p
            if otm.complete: otm.new_record = True
            else: otm.new_record = False

        project = p.project
        obo = project.countychaseprojectonebyone_set.get()
        fund = project.fund_set.get()
        budget = fund.budget_set.all().order_by('id')[0]

        worksheet.write(row, c1+1, n+1, myfmt())
        if otm.new_record: color = 'white'
        else: color = '#A0A0A0'
        worksheet.write(row, c1+2, str(otm.update_time) if otm.update_time else '', myfmt(bg_color=color))
        worksheet.write(row, c1+3, project.year, myfmt())
        worksheet.write(row, c1+4, project.place.name, myfmt())
        port_and_aqua = ''
        for port in project.fishing_port.all():
            port_and_aqua += port.name + '\n'
        for aqua in project.aquaculture.all():
            port_and_aqua += aqua.name + '\n'
        worksheet.write(row, c1+5, port_and_aqua, myfmt())
        worksheet.write(row, c1+6, project.plan.name, myfmt(align="left"))
        worksheet.write(row, c1+7, project.name, myfmt(align="left"))
        worksheet.write(row, c1+8, project.budget_sub_type.value, myfmt())
        worksheet.write(row, c1+9, project.undertake_type.value, myfmt())
        worksheet.write(row, c1+10, project.purchase_type.value, myfmt())
        worksheet.write(row, c1+11, float(str(otm.schedul_progress_percent))/100 if otm.schedul_progress_percent else '', myfmt(num_format='0.00%', align="right"))
        worksheet.write(row, c1+12, float(str(otm.actual_progress_percent))/100 if otm.actual_progress_percent else '', myfmt(num_format='0.00%', align="right"))
        worksheet.write(row, c1+13, otm.memo if otm.memo else '', myfmt(align="left"))
        worksheet.write(row, c1+14, otm.behind_memo if otm.behind_memo else '', myfmt(align="left"))

        worksheet.write(row, c2+1, float(str(otm.self_payout))/1000 if otm.self_payout else '', myfmt(num_format='#,##0', align="right"))
        worksheet.write(row, c2+2, float(str(otm.local_payout))/1000 if otm.local_payout else '', myfmt(num_format='#,##0', align="right"))
        worksheet.write(row, c2+3, float(str(otm.self_unpay))/1000 if otm.self_unpay else '', myfmt(num_format='#,##0', align="right"))
        worksheet.write(row, c2+4, float(str(otm.local_unpay))/1000 if otm.local_unpay else '', myfmt(num_format='#,##0', align="right"))
        worksheet.write(row, c2+5, float(str(otm.rSelf_Surplus()))/1000 if otm.rSelf_Surplus() else '', myfmt(num_format='#,##0', align="right"))
        worksheet.write(row, c2+6, float(str(otm.surplus))/1000 if otm.surplus else '', myfmt(num_format='#,##0', align="right"))
        worksheet.write(row, c2+7, float(str(otm.getSelfExecutionMoney()))/1000 if otm.getSelfExecutionMoney() else '', myfmt(num_format='#,##0', align="right"))
        worksheet.write(row, c2+8, float(str(otm.getExecutionRate()))/100 if otm.getExecutionRate() else '', myfmt(num_format='0.00%', align="right"))
        worksheet.write(row, c2+9, float(str(otm.expected_to_end_percent))/1000 if otm.expected_to_end_percent else '', myfmt(num_format='#,##0', align="right"))

        worksheet.write(row, c3+1, float(str(budget.rPlanMoney()))/1000 if budget.rPlanMoney() else '', myfmt(num_format='#,##0', align="right"))
        if budget.capital_ratify_revision:
            value = float(str(budget.capital_ratify_revision))/1000
        elif budget.capital_ratify_budget:
            value = float(str(budget.capital_ratify_budget))/1000
        else:
            value = ''
        worksheet.write(row, c3+2, value, myfmt(num_format='#,##0', align="right"))
        worksheet.write(row, c3+3, float(str(project.allot_rate)) if project.allot_rate else '', myfmt(num_format='#,##0', align="right"))
        worksheet.write(row, c3+4, float(str(project.read_total_money())), myfmt(num_format='#,##0', align="right"))
        worksheet.write(row, c3+5, float(str(fund.rSelfLoad()))/1000 if fund.rSelfLoad() else '', myfmt(num_format='#,##0', align="right"))
        worksheet.write(row, c3+6, obo.work_info, myfmt(align="left")) #TODO: 工作(計畫)內容
        worksheet.write(row, c3+7, project.unit.name, myfmt())
        try:
            frcm = project.frcmusergroup_set.get(group__name='負責主辦工程師')
            name = frcm.user.user_profile.rName()
            phone_mail = frcm.user.user_profile.phone + '\n' + frcm.user.email
        except: name, phone_mail = '', ''
        worksheet.write(row, c3+8, name, myfmt())
        worksheet.write(row, c3+9, phone_mail, myfmt(align="left"))

        if not obo.act_eng_plan_agree_plan and obo.sch_eng_plan_agree_plan and obo.sch_eng_plan_agree_plan < TODAY():
            bg_color = u'#FF7F7F'
        else: bg_color = u''
        worksheet.write(row, c4+1, u"預計：%s\n實際：%s" % (obo.sch_eng_plan_agree_plan or '', obo.act_eng_plan_agree_plan or ''), myfmt(align="left", font_size="8", bg_color=bg_color))
        if not obo.act_eng_plan_approved_plan and obo.sch_eng_plan_approved_plan and obo.sch_eng_plan_approved_plan < TODAY():
            bg_color = u'#FF7F7F'
        else: bg_color = u''
        worksheet.write(row, c4+2, u"預計：%s\n實際：%s" % (obo.sch_eng_plan_approved_plan or '', obo.act_eng_plan_approved_plan or ''), myfmt(align="left", font_size="8", bg_color=bg_color))
        if not obo.act_eng_plan_announcement_tender and obo.sch_eng_plan_announcement_tender and obo.sch_eng_plan_announcement_tender < TODAY():
            bg_color = u'#FF7F7F'
        else: bg_color = u''
        worksheet.write(row, c4+3, u"預計：%s\n實際：%s" % (obo.sch_eng_plan_announcement_tender or '', obo.act_eng_plan_announcement_tender or ''), myfmt(align="left", font_size="8", bg_color=bg_color))
        if not obo.act_eng_plan_selection_meeting and obo.sch_eng_plan_selection_meeting and obo.sch_eng_plan_selection_meeting < TODAY():
            bg_color = u'#FF7F7F'
        else: bg_color = u''
        worksheet.write(row, c4+4, u"預計：%s\n實際：%s" % (obo.sch_eng_plan_selection_meeting or '', obo.act_eng_plan_selection_meeting or ''), myfmt(align="left", font_size="8", bg_color=bg_color))
        if not obo.act_eng_plan_final and obo.sch_eng_plan_final and obo.sch_eng_plan_final < TODAY():
            bg_color = u'#FF7F7F'
        else: bg_color = u''
        worksheet.write(row, c4+5, u"預計：%s\n實際：%s" % (obo.sch_eng_plan_final or '', obo.act_eng_plan_final or ''), myfmt(align="left", font_size="8", bg_color=bg_color))
        if not obo.act_eng_plan_detail_design and obo.sch_eng_plan_detail_design and obo.sch_eng_plan_detail_design < TODAY():
            bg_color = u'#FF7F7F'
        else: bg_color = u''
        worksheet.write(row, c4+6, u"預計：%s\n實際：%s" % (obo.sch_eng_plan_detail_design or '', obo.act_eng_plan_detail_design or ''), myfmt(align="left", font_size="8", bg_color=bg_color))
        if not obo.act_eng_plan_acceptance and obo.sch_eng_plan_acceptance and obo.sch_eng_plan_acceptance < TODAY():
            bg_color = u'#FF7F7F'
        else: bg_color = u''
        worksheet.write(row, c4+7, u"預計：%s\n實際：%s" % (obo.sch_eng_plan_acceptance or '', obo.act_eng_plan_acceptance or ''), myfmt(align="left", font_size="8", bg_color=bg_color))
        if not obo.act_eng_plan_acceptance_closed and obo.sch_eng_plan_acceptance_closed and obo.sch_eng_plan_acceptance_closed < TODAY():
            bg_color = u'#FF7F7F'
        else: bg_color = u''
        worksheet.write(row, c4+8, u"預計：%s\n實際：%s" % (obo.sch_eng_plan_acceptance_closed or '', obo.act_eng_plan_acceptance_closed or ''), myfmt(align="left", font_size="8", bg_color=bg_color))
        if not obo.act_eng_do_announcement_tender and obo.sch_eng_do_announcement_tender and obo.sch_eng_do_announcement_tender < TODAY():
            bg_color = u'#FF7F7F'
        else: bg_color = u''
        worksheet.write(row, c4+9, u"預計：%s\n實際：%s" % (obo.sch_eng_do_announcement_tender or '', obo.act_eng_do_announcement_tender or ''), myfmt(align="left", font_size="8", bg_color=bg_color))
        if not obo.act_eng_do_final and obo.sch_eng_do_final and obo.sch_eng_do_final < TODAY():
            bg_color = u'#FF7F7F'
        else: bg_color = u''
        worksheet.write(row, c4+11, u"預計：%s\n實際：%s" % (obo.sch_eng_do_final or '', obo.act_eng_do_final or ''), myfmt(align="left", font_size="8", bg_color=bg_color))
        if not obo.act_eng_do_promise and obo.sch_eng_do_promise and obo.sch_eng_do_promise < TODAY():
            bg_color = u'#FF7F7F'
        else: bg_color = u''
        worksheet.write(row, c4+12, u"預計：%s\n實際：%s" % (obo.sch_eng_do_promise or '', obo.act_eng_do_promise or ''), myfmt(align="left", font_size="8", bg_color=bg_color))
        if not obo.act_eng_do_start and obo.sch_eng_do_start and obo.sch_eng_do_start < TODAY():
            bg_color = u'#FF7F7F'
        else: bg_color = u''
        worksheet.write(row, c4+14, u"預計：%s\n實際：%s" % (obo.sch_eng_do_start or '', obo.act_eng_do_start or ''), myfmt(align="left", font_size="8", bg_color=bg_color))
        if not obo.act_eng_do_completion and obo.sch_eng_do_completion and obo.sch_eng_do_completion < TODAY():
            bg_color = u'#FF7F7F'
        else: bg_color = u''
        worksheet.write(row, c4+15, u"預計：%s\n實際：%s" % (obo.sch_eng_do_completion or '', obo.act_eng_do_completion or ''), myfmt(align="left", font_size="8", bg_color=bg_color))
        if not obo.act_eng_do_acceptance and obo.sch_eng_do_acceptance and obo.sch_eng_do_acceptance < TODAY():
            bg_color = u'#FF7F7F'
        else: bg_color = u''
        worksheet.write(row, c4+16, u"預計：%s\n實際：%s" % (obo.sch_eng_do_acceptance or '', obo.act_eng_do_acceptance or ''), myfmt(align="left", font_size="8", bg_color=bg_color))
        if not obo.act_eng_do_closed and obo.sch_eng_do_closed and obo.sch_eng_do_closed < TODAY():
            bg_color = u'#FF7F7F'
        else: bg_color = u''
        worksheet.write(row, c4+17, u"預計：%s\n實際：%s" % (obo.sch_eng_do_closed or '', obo.act_eng_do_closed or ''), myfmt(align="left", font_size="8", bg_color=bg_color))
        
        worksheet.write(row, c4+10, obo.give_up_times, myfmt(align="right"))
        duration_type = project.frcm_duration_type
        if duration_type and duration_type.value == u'限期完工(日曆天每日施工)':
            worksheet.write(row, c4+13, u'%s\n%s' % (duration_type.value if duration_type else '', project.frcm_duration_limit if project.frcm_duration_limit else ''), myfmt(align='left', font_size="8"))
        else:
            worksheet.write(row, c4+13, u'%s\n%s' % (duration_type.value if duration_type else '', project.frcm_duration), myfmt(align='left', font_size="8"))
            
        row += 1

    worksheet.autofilter('B2:AW2') #加入篩選器


    # 新增一個sheet
    worksheet = workbook.add_worksheet(u'勞務')
    worksheet.set_margins(left=0.5, right=0.5, top=0.5, bottom=0.5)
    worksheet.set_header(header='',margin=0.0)  
    row = 0 #第一列的編號為0
    # Basic format
    column_width=[
        #   A   B   C   D   E   F   G   H   I   J   K   L   M   N
            4, 12,  4,  7, 10, 35, 35,  9,  6,  9,  9,  9, 25, 25,
        #   O   P   Q   R   S   T   U   V   W
           12, 12, 12, 12, 12, 12, 12,  8,  8,
        #   X   Y   Z  AA  AB  AC  AD  AE  AF
           12, 12,  8, 12, 12, 35, 20, 12, 20,
        #  AG  AH  AI  AJ  AK  AL  AM  AN  AO  AP  AQ  AR 
           15, 15, 15,  8, 15, 15, 22, 15, 15, 15, 15, 15]
    # set cloumn width 
    for i, e in enumerate(column_width):
        worksheet.set_column(i, i, e)

    # 標題列
    worksheet.set_row(row, 39)
    worksheet.set_row(row+1, 52)
    c1 = -1
    worksheet.merge_range(row, c1+1, row+1, c1+1, u"項次", myfmt(bg_color="#CDFEFF"))
    worksheet.merge_range(row, c1+2, row+1, c1+2, u"最\n後\n更\n新\n日\n期", myfmt(bg_color="#CDFEFF"))
    worksheet.merge_range(row, c1+3, row+1, c1+3, u"年度", myfmt(bg_color="#CDFEFF"))
    worksheet.merge_range(row, c1+4, row+1, c1+4, u"縣市別", myfmt(bg_color="#CDFEFF"))
    worksheet.merge_range(row, c1+5, row+1, c1+5, u"漁港別\n養殖區別", myfmt(bg_color="#CDFEFF"))
    worksheet.merge_range(row, c1+6, row+1, c1+6, u"計畫名稱", myfmt(bg_color="#CDFEFF"))
    worksheet.merge_range(row, c1+7, row+1, c1+7, u"工程名稱", myfmt(bg_color="#CDFEFF"))
    worksheet.merge_range(row, c1+8, row+1, c1+8, u"經費來源\n經常\n資本", myfmt(bg_color="#CDFEFF"))
    worksheet.merge_range(row, c1+9, row+1, c1+9, u"辦理別\n自\n委\n補", myfmt(bg_color="#CDFEFF"))
    worksheet.merge_range(row, c1+10, row+1, c1+10, u"採購類型\n勞務\n工程\n財物", myfmt(bg_color="#CDFEFF"))
    worksheet.merge_range(row, c1+11, row+1, c1+11, u"預定進度%", myfmt(bg_color="#CDFEFF"))
    worksheet.merge_range(row, c1+12, row+1, c1+12, u"實際進度%", myfmt(bg_color="#CDFEFF"))
    worksheet.merge_range(row, c1+13, row+1, c1+13, u"目前辦理情形(進度)", myfmt(bg_color="#CDFEFF"))
    worksheet.merge_range(row, c1+14, row+1, c1+14, u"落後10%以上、履約爭議或停工等請填原因及解決對策", myfmt(bg_color="#CDFEFF"))

    c2 = c1 + 14
    worksheet.merge_range(row, c2+1, row, c2+2, u"實支數\n(仟元)", myfmt(bg_color="#b5b5b5"))
    worksheet.write(row+1, c2+1, u"本署", myfmt(bg_color="#b5b5b5"))
    worksheet.write(row+1, c2+2, u"縣府", myfmt(bg_color="#b5b5b5"))
    worksheet.merge_range(row, c2+3, row, c2+4, u"應付未付數\n(仟元)", myfmt(bg_color="#b5b5b5"))
    worksheet.write(row+1, c2+3, u"本署", myfmt(bg_color="#b5b5b5"))
    worksheet.write(row+1, c2+4, u"縣府", myfmt(bg_color="#b5b5b5"))
    worksheet.write(row, c2+5, u"賸餘款\n(仟元)", myfmt(bg_color="#b5b5b5"))
    worksheet.write(row+1, c2+5, u"本署", myfmt(bg_color="#b5b5b5"))
    worksheet.merge_range(row, c2+6, row+1, c2+6, u"結餘數\n(仟元)", myfmt(bg_color="#b5b5b5"))
    worksheet.merge_range(row, c2+7, row+1, c2+7, u"本署經費執行數\n(仟元)", myfmt(bg_color="#b5b5b5"))
    worksheet.merge_range(row, c2+8, row+1, c2+8, u"執行率\n(%)", myfmt(bg_color="#b5b5b5"))
    worksheet.merge_range(row, c2+9, row+1, c2+9, u"預計至年底執行率\n(%)", myfmt(bg_color="#b5b5b5"))

    c3 = c2 + 9
    worksheet.merge_range(row, c3+1, row+1, c3+1, u"工程(計畫)總預算\n(仟元)", myfmt(bg_color="#b5b5b5"))
    worksheet.merge_range(row, c3+2, row+1, c3+2, u"漁業署編列預算\n(仟元)", myfmt(bg_color="#b5b5b5"))
    worksheet.merge_range(row, c3+3, row+1, c3+3, u"補助比例\n(%)", myfmt(bg_color="#b5b5b5"))
    worksheet.merge_range(row, c3+4, row+1, c3+4, u"工程(計畫)發包金額\n(仟元)", myfmt(bg_color="#b5b5b5"))
    worksheet.merge_range(row, c3+5, row+1, c3+5, u"漁業署實際補助金額\n(仟元)", myfmt(bg_color="#b5b5b5"))
    worksheet.merge_range(row, c3+6, row+1, c3+6, u"工作(計畫)內容", myfmt(bg_color="#CDFEFF"))
    worksheet.merge_range(row, c3+7, row+1, c3+7, u"執行單位", myfmt(bg_color="#CDFEFF"))
    worksheet.merge_range(row, c3+8, row+1, c3+8, u"執行單位聯絡窗口", myfmt(bg_color="#CDFEFF"))
    worksheet.merge_range(row, c3+9, row+1, c3+9, u"縣市政府聯絡方式(mail及電話)", myfmt(bg_color="#CDFEFF"))

    c4 = c3 + 9
    worksheet.merge_range(row, c4+1, row+1, c4+1, u"核定計畫", myfmt(bg_color="#D6FFAF"))
    worksheet.merge_range(row, c4+2, row+1, c4+2, u"簽辦招標", myfmt(bg_color="#D6FFAF"))
    worksheet.merge_range(row, c4+3, row+1, c4+3, u"公告招標", myfmt(bg_color="#D6FFAF"))
    worksheet.merge_range(row, c4+4, row+1, c4+4, u"招標期間流標次數", myfmt(bg_color="#E7CDFF"))
    worksheet.merge_range(row, c4+5, row+1, c4+5, u"公開評選會議", myfmt(bg_color="#E7CDFF"))
    worksheet.merge_range(row, c4+6, row+1, c4+6, u"定約", myfmt(bg_color="#E7CDFF"))
    worksheet.merge_range(row, c4+7, row+1, c4+7, u"工期", myfmt(bg_color="#E7CDFF"))
    worksheet.merge_range(row, c4+8, row+1, c4+8, u"工作計畫書", myfmt(bg_color="#E7CDFF"))
    worksheet.merge_range(row, c4+9, row+1, c4+9, u"期中報告", myfmt(bg_color="#E7CDFF"))
    worksheet.merge_range(row, c4+10, row+1, c4+10, u"期末報告", myfmt(bg_color="#E7CDFF"))
    worksheet.merge_range(row, c4+11, row+1, c4+11, u"驗收", myfmt(bg_color="#E7CDFF"))
    worksheet.merge_range(row, c4+12, row+1, c4+12, u"結案", myfmt(bg_color="#E7CDFF"))

    row += 2
    for n, p in enumerate(sers):
        #如果未填完者使用上次紀錄
        # rows = p.project.countychaseprojectonetomany_set.filter(countychasetime__chase_date__lt=p.countychasetime.chase_date).order_by('-countychasetime__chase_date')
        # if rows: otm = rows[0]
        # else: otm = p
        otm = p
        project = p.project
        obo = project.countychaseprojectonebyone_set.get()
        fund = project.fund_set.get()
        budget = fund.budget_set.all().order_by('id')[0]

        worksheet.write(row, c1+1, n+1, myfmt())
        worksheet.write(row, c1+2, str(otm.update_time) if otm.update_time else '', myfmt())
        worksheet.write(row, c1+3, project.year, myfmt())
        worksheet.write(row, c1+4, project.place.name, myfmt())
        port_and_aqua = ''
        for port in project.fishing_port.all():
            port_and_aqua += port.name + '\n'
        for aqua in project.aquaculture.all():
            port_and_aqua += aqua.name + '\n'
        worksheet.write(row, c1+5, port_and_aqua, myfmt())
        worksheet.write(row, c1+6, project.plan.name, myfmt(align="left"))
        worksheet.write(row, c1+7, project.name, myfmt(align="left"))
        worksheet.write(row, c1+8, project.budget_sub_type.value, myfmt())
        worksheet.write(row, c1+9, project.undertake_type.value, myfmt())
        worksheet.write(row, c1+10, project.purchase_type.value, myfmt())
        worksheet.write(row, c1+11, float(str(otm.schedul_progress_percent))/100 if otm.schedul_progress_percent else '', myfmt(num_format='0.00%', align="right"))
        worksheet.write(row, c1+12, float(str(otm.actual_progress_percent))/100 if otm.actual_progress_percent else '', myfmt(num_format='0.00%', align="right"))
        worksheet.write(row, c1+13, otm.memo if otm.memo else '', myfmt(align="left"))
        worksheet.write(row, c1+14, otm.behind_memo if otm.behind_memo else '', myfmt(align="left"))

        worksheet.write(row, c2+1, float(str(otm.self_payout))/1000 if otm.self_payout else '', myfmt(num_format='#,##0', align="right"))
        worksheet.write(row, c2+2, float(str(otm.local_payout))/1000 if otm.local_payout else '', myfmt(num_format='#,##0', align="right"))
        worksheet.write(row, c2+3, float(str(otm.self_unpay))/1000 if otm.self_unpay else '', myfmt(num_format='#,##0', align="right"))
        worksheet.write(row, c2+4, float(str(otm.local_unpay))/1000 if otm.local_unpay else '', myfmt(num_format='#,##0', align="right"))
        worksheet.write(row, c2+5, float(str(otm.rSelf_Surplus()))/1000 if otm.rSelf_Surplus() else '', myfmt(num_format='#,##0', align="right"))
        worksheet.write(row, c2+6, float(str(otm.surplus))/1000 if otm.surplus else '', myfmt(num_format='#,##0', align="right"))
        worksheet.write(row, c2+7, float(str(otm.getSelfExecutionMoney()))/1000 if otm.getSelfExecutionMoney() else '', myfmt(num_format='#,##0', align="right"))
        worksheet.write(row, c2+8, float(str(otm.getExecutionRate()))/100 if otm.getExecutionRate() else '', myfmt(num_format='0.00%', align="right"))
        worksheet.write(row, c2+9, float(str(otm.expected_to_end_percent))/1000 if otm.expected_to_end_percent else '', myfmt(num_format='#,##0', align="right"))

        worksheet.write(row, c3+1, float(str(budget.rPlanMoney()))/1000 if budget.rPlanMoney() else '', myfmt(num_format='#,##0', align="right"))
        if budget.capital_ratify_revision:
            value = float(str(budget.capital_ratify_revision))/1000
        elif budget.capital_ratify_budget:
            value = float(str(budget.capital_ratify_budget))/1000
        else:
            value = ''
        worksheet.write(row, c3+2, value, myfmt(num_format='#,##0', align="right"))
        worksheet.write(row, c3+3, float(str(project.allot_rate)) if project.allot_rate else '', myfmt(num_format='#,##0', align="right"))
        worksheet.write(row, c3+4, float(str(project.read_total_money())), myfmt(num_format='#,##0', align="right"))
        worksheet.write(row, c3+5, float(str(fund.rSelfLoad()))/1000 if fund.rSelfLoad() else '', myfmt(num_format='#,##0', align="right"))
        worksheet.write(row, c3+6, obo.work_info, myfmt(align="left")) #TODO: 工作(計畫)內容
        worksheet.write(row, c3+7, project.unit.name, myfmt())
        try:
            frcm = project.frcmusergroup_set.get(group__name='負責主辦工程師')
            name = frcm.user.user_profile.rName()
            phone_mail = frcm.user.user_profile.phone + '\n' + frcm.user.email
        except: name, phone_mail = '', ''
        worksheet.write(row, c3+8, name, myfmt())
        worksheet.write(row, c3+9, phone_mail, myfmt(align="left"))

        if not obo.act_ser_approved_plan and obo.sch_ser_approved_plan and obo.sch_ser_approved_plan < TODAY():
            bg_color = u'#FF7F7F'
        else: bg_color = u''
        worksheet.write(row, c4+1, u"預計：%s\n實際：%s" % (obo.sch_ser_approved_plan or '', obo.act_ser_approved_plan or ''), myfmt(align="left", font_size="8", bg_color=bg_color))
        if not obo.act_ser_signed_tender and obo.sch_ser_signed_tender and obo.sch_ser_signed_tender < TODAY():
            bg_color = u'#FF7F7F'
        else: bg_color = u''
        worksheet.write(row, c4+2, u"預計：%s\n實際：%s" % (obo.sch_ser_signed_tender or '', obo.act_ser_signed_tender or ''), myfmt(align="left", font_size="8", bg_color=bg_color))
        if not obo.act_ser_announcement_tender and obo.sch_ser_announcement_tender and obo.sch_ser_announcement_tender < TODAY():
            bg_color = u'#FF7F7F'
        else: bg_color = u''
        worksheet.write(row, c4+3, u"預計：%s\n實際：%s" % (obo.sch_ser_announcement_tender or '', obo.act_ser_announcement_tender or ''), myfmt(align="left", font_size="8", bg_color=bg_color))
        if not obo.act_ser_selection_meeting and obo.sch_ser_selection_meeting and obo.sch_ser_selection_meeting < TODAY():
            bg_color = u'#FF7F7F'
        else: bg_color = u''
        worksheet.write(row, c4+5, u"預計：%s\n實際：%s" % (obo.sch_ser_selection_meeting or '', obo.act_ser_selection_meeting or ''), myfmt(align="left", font_size="8", bg_color=bg_color))
        if not obo.act_ser_promise and obo.sch_ser_promise and obo.sch_ser_promise < TODAY():
            bg_color = u'#FF7F7F'
        else: bg_color = u''
        worksheet.write(row, c4+6, u"預計：%s\n實際：%s" % (obo.sch_ser_promise or '', obo.act_ser_promise or ''), myfmt(align="left", font_size="8", bg_color=bg_color))
        if not obo.act_ser_work_plan and obo.sch_ser_work_plan and obo.sch_ser_work_plan < TODAY():
            bg_color = u'#FF7F7F'
        else: bg_color = u''
        worksheet.write(row, c4+8, u"預計：%s\n實際：%s" % (obo.sch_ser_work_plan or '', obo.act_ser_work_plan or ''), myfmt(align="left", font_size="8", bg_color=bg_color))
        if not obo.act_ser_interim_report and obo.sch_ser_interim_report and obo.sch_ser_interim_report < TODAY():
            bg_color = u'#FF7F7F'
        else: bg_color = u''
        worksheet.write(row, c4+9, u"預計：%s\n實際：%s" % (obo.sch_ser_interim_report or '', obo.act_ser_interim_report or ''), myfmt(align="left", font_size="8", bg_color=bg_color))
        if not obo.act_ser_final_report and obo.sch_ser_final_report and obo.sch_ser_final_report < TODAY():
            bg_color = u'#FF7F7F'
        else: bg_color = u''
        worksheet.write(row, c4+10, u"預計：%s\n實際：%s" % (obo.sch_ser_final_report or '', obo.act_ser_final_report or ''), myfmt(align="left", font_size="8", bg_color=bg_color))
        if not obo.act_ser_do_acceptance and obo.sch_ser_do_acceptance and obo.sch_ser_do_acceptance < TODAY():
            bg_color = u'#FF7F7F'
        else: bg_color = u''
        worksheet.write(row, c4+11, u"預計：%s\n實際：%s" % (obo.sch_ser_do_acceptance or '', obo.act_ser_do_acceptance or ''), myfmt(align="left", font_size="8", bg_color=bg_color))
        if not obo.act_ser_acceptance_closed and obo.sch_ser_acceptance_closed and obo.sch_ser_acceptance_closed < TODAY():
            bg_color = u'#FF7F7F'
        else: bg_color = u''
        worksheet.write(row, c4+12, u"預計：%s\n實際：%s" % (obo.sch_ser_acceptance_closed or '', obo.act_ser_acceptance_closed or ''), myfmt(align="left", font_size="8", bg_color=bg_color))
        
        worksheet.write(row, c4+4, obo.give_up_times, myfmt(align="right"))
        duration_type = project.frcm_duration_type
        if duration_type and duration_type.value == u'限期完工(日曆天每日施工)':
            worksheet.write(row, c4+7, u'%s\n%s' % (duration_type.value if duration_type else '', project.frcm_duration_limit if project.frcm_duration_limit else ''), myfmt(align='left', font_size="8"))
        else:
            worksheet.write(row, c4+7, u'%s\n%s' % (duration_type.value if duration_type else '', project.frcm_duration), myfmt(align='left', font_size="8"))
            
        row += 1
    worksheet.autofilter('B2:AR2') #加入篩選器

    return workbook























#製造自定義報表Excel.xlsx
def make_custom_report_excel_file(workbook='', report='', projects=''):
    #設定每個cell的格式
    def myfmt(border=1, bg_color="", shrink="", align="center", text_wrap=True, font_name=u"標楷體", font_size=10, num_format="", bold=False):
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
        fmt.set_align('vcenter')

        return fmt 

    # 新增一個sheet
    worksheet = workbook.add_worksheet(u'sheet1')
    worksheet.set_margins(left=0.5, right=0.5, top=0.5, bottom=0.5)
    worksheet.set_header(header='',margin=0.0)
    row = 0

    fields = [i.report_field for i in ExportCustomReportField.objects.filter(export_custom_report=report).order_by('report_field__tag__id', 'report_field__id')]
    
    def change_taiwan_year(date):
        #轉換民國年
        if not date: return u""
        else:
            year, month, day = str(date).split('-')
            return u"%s-%s-%s" % (int(year)-1911, month, day)

    worksheet.set_row(row, 40)
    for i, e in enumerate(fields):
        worksheet.set_column(i, i, 20)
        worksheet.write(row, i, e.name, myfmt(bg_color="#CDFEFF"))

    row += 1
    for p in projects:
        fund = p.fund_set.get()
        budget = fund.budget_set.all().order_by('-year')[0]
        obo = p.countychaseprojectonebyone_set.get()
        for i, e in enumerate(fields):
            worksheet.write(row, i, eval(e.value_method), myfmt(align="left", text_wrap=True))
        row += 1

    worksheet.freeze_panes(1, 0) # 凍結視窗

    return workbook



def make_project_manage_money_excel(workbook='', projects=''):
    #設定每個cell的格式
    def myfmt(border=1, bg_color="", shrink="", align="center", text_wrap=True, font_name=u"標楷體", font_size=10, num_format="", bold=False):
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
        fmt.set_align('vcenter')

        return fmt 

    # 新增一個sheet
    worksheet = workbook.add_worksheet(u'工程案')
    worksheet.set_margins(left=0.5, right=0.5, top=0.5, bottom=0.5)
    worksheet.set_header(header='',margin=0.0)
    row = 0 #第一列的編號為0
    # Basic format
    column_width=[62, 11, 11, 11]

    # set cloumn width 
    for i, e in enumerate(column_width):
        worksheet.set_column(i, i, e)

    # 標題列
    worksheet.set_row(row, 35)
    worksheet.write(row, 0, u"工程名稱", myfmt(bg_color="#CDFEFF"))
    worksheet.write(row, 1, u"可用管理費", myfmt(bg_color="#CDFEFF"))
    worksheet.write(row, 2, u"已用管理費", myfmt(bg_color="#CDFEFF"))
    worksheet.write(row, 3, u"剩餘管理費", myfmt(bg_color="#CDFEFF"))

    for p in projects:
        row += 1
        worksheet.write(row, 0, p.name, myfmt(align="left", text_wrap=True))
        worksheet.write(row, 1, p.manage, myfmt(align="right", num_format='#,##0'))
        worksheet.write(row, 2, p.use_manage, myfmt(align="right", num_format='#,##0'))
        worksheet.write(row, 3, p.limit_money, myfmt(align="right", num_format='#,##0'))

    return workbook

def make_control_form_excel_file(workbook='', projects='', budget_type='', year='', top_plan_name=''):
    #設定每個cell的格式
    def myfmt(border=1, bg_color="", shrink="", align="center", text_wrap=True, font_name=u"標楷體", font_size=12, num_format="", bold=False):
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
        fmt.set_align('vcenter')

        return fmt 

    # 新增一個sheet
    worksheet = workbook.add_worksheet(u'工程案')
    worksheet.set_margins(left=0.5, right=0.5, top=0.5, bottom=0.5)
    worksheet.set_header(header='',margin=0.0)
    row = 0 #第一列的編號為0
     #總筆數
    # Basic format
    worksheet.set_row(row, 35)
    worksheet.merge_range(row, 0, row, 18, '%s年度漁業發展-漁業永續經營基礎建設計畫-建構安全永續漁港管控表'% (year), myfmt(align="center", border=0, bold=True, font_size=16)) #標題
    row += 1
    worksheet.merge_range(row, 0, row, 18, '上層計畫：%s'% (top_plan_name), myfmt(align="right", border=0)) #上層計畫
    row += 1
    worksheet.merge_range(row, 0, row, 18, '共有 %s 筆，單位：千元'% (len(projects[0])+len(projects[1])+len(projects[2])), myfmt(align="right", border=0)) #筆數，單位
    row += 1
    worksheet.merge_range(row, 0, row, 4, '%s(自辦)' %budget_type, myfmt(bg_color="#92CDDC")) #經費種類
    worksheet.merge_range(row, 5, row, 9, '%s(委辦)' %budget_type, myfmt(bg_color="#92CDDC")) #經費種類
    worksheet.merge_range(row, 10, row, 18, '%s(補助)' %budget_type, myfmt(bg_color="#92CDDC")) #經費種類
    row += 1

    column_width=[
#    A,  B,  C,  D,  E,  F,  G,  H,  I,  J,  L,  
    8, 62, 11, 11, 30, 30, 62, 11, 11, 30, 30, 
#    M,  N,  O,  P,  Q,  R,  S,  T,  U,  V,  W,
    62, 11, 11, 11, 11, 11, 11, 30,
    ]
    # set cloumn width 
    for i, e in enumerate(column_width):
        worksheet.set_column(i, i, e)

    #標題列
    worksheet.set_row(row, 35)
    worksheet.write(row, 0, u"計畫編號", myfmt(bg_color="#92CDDC"))
    worksheet.write(row, 1, u"工程名稱", myfmt(bg_color="#92CDDC"))
    worksheet.write(row, 2, u"自辦", myfmt(bg_color="#92CDDC"))
    worksheet.write(row, 3, u"調自辦1", myfmt(bg_color="#92CDDC"))
    worksheet.write(row, 4, u"備註", myfmt(bg_color="#92CDDC"))
    worksheet.write(row, 5, u"計畫編號", myfmt(bg_color="#92CDDC"))
    worksheet.write(row, 6, u"工程名稱", myfmt(bg_color="#92CDDC"))
    worksheet.write(row, 7, u"委辦", myfmt(bg_color="#92CDDC"))
    worksheet.write(row, 8, u"調委辦1", myfmt(bg_color="#92CDDC"))
    worksheet.write(row, 9, u"備註", myfmt(bg_color="#92CDDC"))
    worksheet.write(row, 10, u"計畫編號", myfmt(bg_color="#92CDDC"))
    worksheet.write(row, 11, u"工程名稱", myfmt(bg_color="#92CDDC"))
    worksheet.write(row, 12, u"補助", myfmt(bg_color="#92CDDC"))
    worksheet.write(row, 13, u"配合款", myfmt(bg_color="#92CDDC"))
    worksheet.write(row, 14, u"基金", myfmt(bg_color="#92CDDC"))
    worksheet.write(row, 15, u"調補助1", myfmt(bg_color="#92CDDC"))
    worksheet.write(row, 16, u"配合款", myfmt(bg_color="#92CDDC"))
    worksheet.write(row, 17, u"基金", myfmt(bg_color="#92CDDC"))
    worksheet.write(row, 18, u"備註", myfmt(bg_color="#92CDDC"))

    content_begins_row = row

    #內容
    #自辦
    for p in projects[0]:
        row += 1
        worksheet.write(row, 0, p.work_no, myfmt(align="left", text_wrap=False))
        worksheet.write(row, 1, p.name, myfmt(align="left", text_wrap=True))
        worksheet.write(row, 2, p.capital_ratify_revision, myfmt(align="right", num_format='#,##0'))
        worksheet.write(row, 3, p.selfpay_revise, myfmt(align="right", num_format='#,##0'))
        worksheet.write(row, 4, p.control_form_memo, myfmt(align="left", num_format='#,##0'))

    #委辦
    row = content_begins_row
    for p in projects[1]:
        row += 1
        worksheet.write(row, 5, p.work_no, myfmt(align="left", text_wrap=False))
        worksheet.write(row, 6, p.name, myfmt(align="left", text_wrap=True))
        worksheet.write(row, 7, p.capital_ratify_revision, myfmt(align="right", num_format='#,##0'))
        worksheet.write(row, 8, p.commission_revise, myfmt(align="right", num_format='#,##0'))
        worksheet.write(row, 9, p.control_form_memo, myfmt(align="left", num_format='#,##0'))

    #補助
    row = content_begins_row
    for p in projects[2]:
        row += 1
        worksheet.write(row, 10, p.work_no, myfmt(align="left", text_wrap=False))
        worksheet.write(row, 11, p.name, myfmt(align="left", text_wrap=True))
        worksheet.write(row, 12, p.capital_ratify_revision, myfmt(align="right", num_format='#,##0'))
        worksheet.write(row, 13, p.capital_ratify_local_revision, myfmt(align="right", num_format='#,##0'))
        worksheet.write(row, 14, p.fund_1, myfmt(align="right", num_format='#,##0'))
        worksheet.write(row, 15, p.allowance_revise, myfmt(align="right", num_format='#,##0'))
        worksheet.write(row, 16, p.matching_fund_2, myfmt(align="right", num_format='#,##0'))
        worksheet.write(row, 17, p.fund_2, myfmt(align="right", num_format='#,##0'))
        worksheet.write(row, 18, p.control_form_memo, myfmt(align="left", num_format='#,##0'))

    return workbook


def make_port_engineering_excel_file(workbook='', projects='', month=''):
    year=TODAY().year-1911
    #設定每個cell的格式
    def myfmt(border=1, bg_color="", shrink="", align="center", text_wrap=True, font_name=u"標楷體", font_size=12, num_format="", bold=False):
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
        fmt.set_align('vcenter')

        return fmt 

    # 新增一個sheet
    worksheet = workbook.add_worksheet(u'工程案')
    worksheet.set_margins(left=0.5, right=0.5, top=0.5, bottom=0.5)
    worksheet.set_header(header='',margin=0.0)
    row = 0 #第一列的編號為0
    # Basic format
    column_width=[
    #    A,  B,  C,  D,  E,  F,  G,  H,  I,  J,  L,  
         5, 30, 30, 30, 15, 15, 30, 15, 20, 15, 30, 
    #    M,  N,  O,  P,  Q,  R,  S,  T,  U,  V,  W,
        40, 25, 25, 25, 25, 15, 10,  5,  5, 10, 10,
    #    X,  Y,  Z, AA, AB, AC, AD, AE, AF, AG, AH, 
        10, 15, 15, 15, 15, 10, 10, 10, 10, 10, 10,
    #   AI, AJ, AK, AL, AM, AN, AO, AP, AQ, AR, AS, 
        10, 10, 10, 10, 10, 25, 10, 15, 15, 15, 10,
    #   AT, AU, AV, AW, AX, AY, AZ, BA, BB, BC, BD,
        10, 10, 10, 10, 10, 10, 15, 10, 10, 10, 15, 
    #   BE, BF, BG
        10, 30, 30
    ]

    # set cloumn width 
    for i, e in enumerate(column_width):
        worksheet.set_column(i, i, e)

    boldon = workbook.add_format({'border': 1, 'bg_color':"", 'shrink':"", 'align': "vcenter", 'text_wrap':True, 'font_name':u"標楷體", 'font_size':12, 'num_format':"", 'bold':True})
    boldoff = workbook.add_format({'border': 1, 'bg_color':"", 'shrink':"", 'align':"vcenter", 'text_wrap':True, 'font_name':u"標楷體", 'font_size':12, 'num_format':"", 'bold':False})


    # 標題列
    worksheet.set_row(row, 80)
    worksheet.set_row(row+1, 80)
    worksheet.set_row(row+2, 100)
    #worksheet.write(row, 0, u"流域綜合治理計畫-水產養殖排水", myfmt(bg_color="gray"))
    #row+=1
    worksheet.merge_range(row, 0, row+1, 0, u"序號", myfmt())
    worksheet.merge_range(row, 1, row+1, 1, u"計畫歸屬", myfmt())
    worksheet.merge_range(row, 2, row+1, 2, u"計畫分類(分為1.「維護漁港營運機能及強化水產競爭力」、2.「強化設施安全及提升漁港防災能力」、3.「工程管理與規劃」4.「純工程勞務」5.「其他」)", myfmt())
    worksheet.merge_range(row, 3, row+1, 3, u"補助比例", myfmt())
    worksheet.write(row, 4, u"經費類別", myfmt())
    worksheet.write(row+1, 4, u"自辦/委辦/補助", myfmt())
    worksheet.write(row, 5, u"採購類別", myfmt())
    worksheet.write(row+1, 5, u"純勞務/純工程/工程含勞務", myfmt())
    worksheet.merge_range(row, 6, row+1, 6, u"計畫編號", myfmt())
    worksheet.merge_range(row, 7, row+1, 7, u"計畫核定日期", myfmt())
    worksheet.merge_range(row, 8, row+1, 8, u"工程執行機關", myfmt())
    worksheet.merge_range(row, 9, row+1, 9, u"漁港別", myfmt())
    worksheet.merge_range(row, 10, row+1, 10, u"工程標案名稱", myfmt())
    worksheet.merge_range(row, 11, row+1, 11, u"辦理情形(若工程尚未上網招標者，請敘明勞務辦理情形)", myfmt(bg_color="#FFE98D"))
    worksheet.merge_range(row, 12, row, 14, u"截至%s年%s月【尚未「開工」者，本欄免填】" % (year, month), myfmt(bg_color="#FFE98D"))
    worksheet.write(row+1, 12, u"工程預定進度(%)", myfmt(bg_color="#FFE98D"))
    worksheet.write(row+1, 13, u"工程實際進度(%)", myfmt(bg_color="#FFE98D"))
    worksheet.write(row+1, 14, u"差異(%)", myfmt(bg_color="#FFE98D"))
    worksheet.merge_range(row, 15, row+1, 15, u"工程標案編號", myfmt())
    worksheet.merge_range(row, 16, row+1, 16, u"工期", myfmt())
    worksheet.merge_range(row, 17, row+1, 17, u"招標期間流廢標次數", myfmt())
    worksheet.merge_range(row, 18, row, 19, u"屬標餘款再使用增辦之工程(請打「V」)", myfmt())
    worksheet.write(row+1, 18, u"是", myfmt())
    worksheet.write(row+1, 19, u"否", myfmt())
    worksheet.merge_range(row, 20, row+1, 20, u"招標預算(B)(千元)", myfmt())
    worksheet.merge_range(row, 21, row+1, 21, u"決標金額(千元)【尚未「決標」者，本欄免填】", myfmt(bg_color="#FFF4C7"))
    worksheet.merge_range(row, 22, row+1, 22, u"契約金額(A)(千元)(如有變更設計，請填列變更設計後金額)【尚未「決標」者，本欄免填】", myfmt())
    worksheet.merge_range(row, 23, row, 26, u"預算編列情形(含補助款、基金)", myfmt())
    worksheet.write_rich_string(row+1, 23, boldon, u"%s年度(含)以前" %(year-2), boldoff, u"預算額度(C)(千元)", myfmt())
    worksheet.write_rich_string(row+1, 24, boldon, u"%s年度" %(year-1), boldoff, u"預算額度(D)(千元)", myfmt())
    worksheet.write_rich_string(row+1, 25, boldon, u"%s年度" %(year), boldoff, u"預算額度(E)(千元)", myfmt())
    worksheet.write_rich_string(row+1, 26, boldon, u"%s年度以後" %(year+1), boldoff, u"預算額度(E)(千元)", myfmt())
    worksheet.merge_range(row, 27, row+1, 27, u"結算金額(千元)【尚未「正式驗收合格」者，本欄免填】", myfmt())
    worksheet.merge_range(row, 28, row+1, 28, u"核定函勞務決標期限", myfmt(bg_color="#FFF4C7"))
    worksheet.merge_range(row, 29, row+1, 29, u"預計勞務決標日期", myfmt(bg_color="#FFF4C7"))
    worksheet.merge_range(row, 30, row+1, 30, u"實際勞務決標日期【勞務尚未決標者，本欄免填】", myfmt(bg_color="#FFF4C7"))
    worksheet.merge_range(row, 31, row+1, 31, u"核定函工程決標期限", myfmt(bg_color="#FFF4C7"))
    worksheet.merge_range(row, 32, row+1, 32, u"預計工程決標日期【勞務尚未決標者，本欄免填】", myfmt(bg_color="#FFF4C7"))
    worksheet.merge_range(row, 33, row+1, 33, u"實際工程決標日期【工程尚未決標者，本欄免填】", myfmt(bg_color="#FFF4C7"))
    worksheet.merge_range(row, 34, row+1, 34, u"預定簽約日期", myfmt(bg_color="#FFF4C7"))
    worksheet.merge_range(row, 35, row+1, 35, u"實際簽約日期【尚未完成簽約者，本欄免填】", myfmt(bg_color="#FFF4C7"))
    worksheet.merge_range(row, 36, row+1, 36, u"預定開工日期", myfmt(bg_color="#FFF4C7"))
    worksheet.merge_range(row, 37, row+1, 37, u"實際開工日期【尚未開工者，本欄免填】", myfmt(bg_color="#FFF4C7"))
    worksheet.merge_range(row, 38, row+1, 38, u"預定竣工日期【如有變更設計(含契約變更)者，請填寫變更設計後(含契約變更)之預定竣工日期】", myfmt(bg_color="#FFF4C7"))
    worksheet.merge_range(row, 39, row+1, 39, u"實際竣工日期【尚未申報竣工者，本欄免填】", myfmt(bg_color="#FFF4C7"))
    worksheet.merge_range(row, 40, row, 55, u"截至%s年%s月止執行狀態，請打「V」，可複選" % (year, month), myfmt(bg_color="#FFF4C7", bold="True"))    
    worksheet.write(row+1, 40, u"勞務案上網公告中", myfmt(bg_color="#FFF4C7"))
    worksheet.write_rich_string(row+1, 41, boldoff, u"勞務履約中", boldon, u"(請加註「規劃設計預定完成日」)", myfmt(bg_color="#FFF4C7"))
    worksheet.write_rich_string(row+1, 42, boldoff, u"工程標案招標文件準備中", boldon, u"(請加註「招標文件預定上網公告日」)", myfmt(bg_color="#FFF4C7"))
    worksheet.write(row+1, 43, u"工程標案招標文件公開預覽中", myfmt(bg_color="#FFF4C7"))
    worksheet.write(row+1, 44, u"工程標案招標文件上網公告中", myfmt(bg_color="#FFF4C7"))
    worksheet.write(row+1, 45, u"工程標案已決標，訂約中(含待開工)", myfmt(bg_color="#FFF4C7"))
    worksheet.write(row+1, 46, u"施工中", myfmt(bg_color="#FFF4C7"))
    worksheet.write(row+1, 47, u"停工中", myfmt(bg_color="#FFF4C7"))
    worksheet.write(row+1, 48, u"履約爭議中", myfmt(bg_color="#FFF4C7"))
    worksheet.write(row+1, 49, u"解約中", myfmt(bg_color="#FFF4C7"))
    worksheet.write(row+1, 50, u"已申報竣工，竣工查驗中或準備驗收資料", myfmt(bg_color="#FFF4C7", bold=True))
    worksheet.write(row+1, 51, u"驗收中(含初驗)", myfmt(bg_color="#FFF4C7"))
    worksheet.write(row+1, 52, u"結算付款中", myfmt(bg_color="#FFF4C7"))
    worksheet.write(row+1, 53, u"已結案", myfmt(bg_color="#FFF4C7"))
    worksheet.write_rich_string(row+1, 54, boldoff, u"已解約", boldon, u"(請加註日期)", myfmt(bg_color="#FFF4C7"))
    worksheet.write(row+1, 55, u"其他(請簡述原因)", myfmt(bg_color="#FFF4C7"))
    worksheet.merge_range(row, 56, row, 57, u"備註\n1、工程進度落後之案件，請說明落後原因、趕工策略及預定何日可追上預定進度，尤其對於落後20%以上案件，說明廠商趕工計畫提報及執行情形。\n2、如係涉及變更設計或契約變更未辦妥，肇致落後，請說明變更設計辦理情形(含何日開始辦理)及預定何日完成變更程序，並說明變更後之預定竣工日、最新工程預定進度及實際進度。\n3、停工中案，請說明停工原因、解決對策、最新辦理情形及預定何日復工；如涉及變更設計或契約變更者，請說明變更設計辦理情形(含何日開始辦理)及預定何日完成變更程序，並說明變更後之預定竣工日、最新工程預定進度及實際進度。", myfmt(bg_color="#FFF4C7"))
    worksheet.write(row+1, 56, u"停工或落後原因(請更新至%s年%s月，如有停工或變更設計，應加註停工或變更設計日期、原因等)" %(year, month), myfmt(bg_color="#FFF4C7", bold=True))
    worksheet.write(row+1, 57, u"解決對策(請更新至%s年%s月，如有停工或變更設計，應加註預定復工或完成變更設計日期，落後者應說明預定趕上進度時程)" %(year, month), myfmt(bg_color="#FFF4C7", bold=True))
    row+=1
    
    worksheet.freeze_panes(2, 1)

    for p in projects:
        worksheet.set_row(row+1, 80)
        row += 1
        worksheet.write(row, 0, row-1, myfmt(align="center"))
        worksheet.write(row, 1, p.plan_name, myfmt(align="center"))
        worksheet.write(row, 2, p.plan_class, myfmt(align="center"))
        worksheet.write(row, 3, p.allowance_scale, myfmt(align="center"))
        worksheet.write(row, 4, p.undertake, myfmt(align="center"))
        worksheet.write(row, 5, p.purchase, myfmt(align="center"))
        worksheet.write(row, 6, p.work_no, myfmt(align="center"))
        worksheet.write(row, 7, p.act_eng_plan_approved_plan, myfmt(align="center"))
        worksheet.write(row, 8, p.unit.fullname, myfmt(align="center"))
        worksheet.write(row, 9, p.port, myfmt(align="center"))
        worksheet.write(row, 10, p.name, myfmt(align="center"))
        worksheet.write(row, 11, p.handling, myfmt(align="center"))
        worksheet.write(row, 12, p.pcc_s_percent, myfmt(align="center"))
        worksheet.write(row, 13, p.pcc_a_percent, myfmt(align="center"))
        worksheet.write(row, 14, p.difference_percent, myfmt(align="center"))
        worksheet.write(row, 15, p.pcc_no if p.pcc_no else ' ', myfmt(align="center"))
        worksheet.write(row, 16, '%d%s'% (p.frcm_duration, p.duration_type), myfmt(align="center"))
        worksheet.write(row, 17, p.abandoned_tender_count, myfmt(align="center"))
        worksheet.write(row, 18, 'V' if p.tender_excess_funds and p.tender_excess_funds != 'null' else ' ', myfmt(align="center"))
        worksheet.write(row, 19, 'V' if not p.tender_excess_funds and p.tender_excess_funds != 'null' else ' ', myfmt(align="center"))
        worksheet.write(row, 20, p.bidding_budget, myfmt(align="center"))
        worksheet.write(row, 21, p.decide_tenders_price, myfmt(align="center"))
        worksheet.write(row, 22, p.decide_tenders_price2, myfmt(align="center"))
        worksheet.write(row, 23, p.nine_budget / 1000 if p.nine_budget != 0 else ' ', myfmt(align="center"))
        worksheet.write(row, 24, p.ten_budget / 1000 if p.ten_budget != 0 else ' ', myfmt(align="center"))
        worksheet.write(row, 25, p.eleven_budget / 1000 if p.eleven_budget != 0 else ' ', myfmt(align="center"))
        worksheet.write(row, 26, p.twelve_budget / 1000 if p.twelve_budget != 0 else ' ', myfmt(align="center"))
        worksheet.write(row, 27, p.balancing_price / 1000 if p.balancing_price != 0 else ' ', myfmt(align="center"))
        worksheet.write(row, 28, str(p.eng_plan_final_deadline if p.eng_plan_final_deadline else ' '), myfmt(align="center"))
        worksheet.write(row, 29, str(p.sch_eng_plan_final if p.sch_eng_plan_final else ' '), myfmt(align="center"))
        worksheet.write(row, 30, str(p.act_eng_plan_final if p.act_eng_plan_final else ' '), myfmt(align="center"))
        worksheet.write(row, 31, str(p.eng_do_approved_plan if p.eng_do_approved_plan else ' '), myfmt(align="center"))
        worksheet.write(row, 32, str(p.sch_eng_do_final if p.sch_eng_do_final else ' '), myfmt(align="center"))
        worksheet.write(row, 33, str(p.act_eng_do_final if p.act_eng_do_final else ' '), myfmt(align="center"))
        worksheet.write(row, 34, str(p.sch_eng_do_promise  if p.sch_eng_do_promise else ' '), myfmt(align="center"))
        worksheet.write(row, 35, str(p.act_eng_do_promise if p.act_eng_do_promise else ' '), myfmt(align="center"))
        worksheet.write(row, 36, str(p.sch_eng_do_start if p.sch_eng_do_start else ' '), myfmt(align="center"))
        worksheet.write(row, 37, str(p.act_eng_do_start if p.act_eng_do_start else ' '), myfmt(align="center"))
        worksheet.write(row, 38, str(p.sch_eng_do_completion if p.sch_eng_do_completion else ' '), myfmt(align="center"))
        worksheet.write(row, 39, str(p.act_eng_do_completion if p.act_eng_do_completion else ' '), myfmt(align="center"))
        worksheet.write(row, 40, 'V\n' + str(p.eng_plan_announcement_tender) if str(p.eng_plan_announcement_tender) != ' ' else ' ', myfmt(align="center"))
        worksheet.write(row, 41, 'V\n%s\n%s'% (p.stat_wrk_per_date, p.stat_wrk_per_memo) if p.stat_wrk_per else ' ', myfmt(align="center"))
        worksheet.write(row, 42, 'V\n%s\n%s'% (p.stat_file_prep_date, p.stat_file_prep_memo) if p.stat_file_prep else ' ', myfmt(align="center"))
        worksheet.write(row, 43, 'V\n%s\n%s'% (p.stat_file_prvw_date, p.stat_file_prvw_memo) if p.stat_file_prvw else ' ', myfmt(align="center"))
        worksheet.write(row, 44, 'V\n%s\n%s'% (p.stat_file_oln_date, p.stat_file_oln_memo) if p.stat_file_oln else ' ', myfmt(align="center"))
        worksheet.write(row, 45, 'V\n%s\n%s'% (p.stat_res_ctr_date, p.stat_res_ctr_memo) if p.stat_res_ctr else ' ', myfmt(align="center"))
        worksheet.write(row, 46, 'V\n%s\n%s'% (p.stat_cnst_date, p.stat_cnst_memo) if p.stat_cnst else ' ', myfmt(align="center"))
        worksheet.write(row, 47, 'V\n%s\n%s'% (p.stat_stop_date, p.stat_stop_memo) if p.stat_stop else ' ', myfmt(align="center"))
        worksheet.write(row, 48, 'V\n%s\n%s'% (p.stat_cnfl_date, p.stat_cnfl_memo) if p.stat_cnfl else ' ', myfmt(align="center"))
        worksheet.write(row, 49, 'V\n%s\n%s'% (p.stat_term_ing_date, p.stat_term_ing_memo) if p.stat_term_ing else ' ', myfmt(align="center"))
        worksheet.write(row, 50, 'V\n%s\n%s'% (p.stat_cmplt_date, p.stat_cmplt_memo) if p.stat_cmplt else ' ', myfmt(align="center"))
        worksheet.write(row, 51, 'V\n%s\n%s'% (p.stat_acpt_date, p.stat_acpt_memo) if p.stat_acpt else ' ', myfmt(align="center"))
        worksheet.write(row, 52, 'V\n%s\n%s'% (p.stat_pay_date, p.stat_pay_memo) if p.stat_pay else ' ', myfmt(align="center"))
        worksheet.write(row, 53, 'V\n%s'% (p.act_eng_do_closed) if p.eng_do_closed else ' ', myfmt(align="center"))
        worksheet.write(row, 54, 'V\n%s\n%s'% (p.stat_term_ed_date, p.stat_term_ed_memo) if p.stat_term_ed else ' ', myfmt(align="center"))
        worksheet.write(row, 55, 'V\n%s\n%s'% (p.stat_oth_date, p.stat_oth_memo) if p.stat_oth else ' ', myfmt(align="center"))
        worksheet.write(row, 56, p.stat_stop_reason_memo, myfmt(align="center"))
        worksheet.write(row, 57, p.stat_solution_memo, myfmt(align="center"))




    worksheet.autofilter('A2:BF%d' % (row)) 

    return workbook
