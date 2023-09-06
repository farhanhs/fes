# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand, CommandError
import os, datetime, decimal, random
from fishuser.models import *
from django.conf import settings
import smtplib
import xlsxwriter
from cStringIO import StringIO
from fishuser.models import Project

from project.lib import make_chase_excel_file, make_custom_report_excel_file, make_project_manage_money_excel, make_port_engineering_excel_file
from pccmating.models import ProjectProgress as PCCProgress


def TODAY(): return datetime.date.today()

class Command(BaseCommand):
    help = u"make port engineering excel monthly"

    def handle(self, *args, **kw):
        year = TODAY().year-1911
        month = TODAY().month-1
        if(month==0):
            month=12
        if month == 12:
            year -= 1
        exclude_id = [2346, 2583, 2899, 2511] #測試用工程案

        projects = Project.objects.filter(year=year, deleter=None).exclude(id__in=exclude_id)
        file_name = '%s年漁港大表-進度-%s月' % (year, month)
        for p in projects:
            port_name = ' '
            fund = Fund.objects.get(project=p)
            budget = Budget.objects.filter(fund=fund).first()
            chase_project = CountyChaseProjectOneByOne.objects.get(project_id=p.id)
            try:
                engprofile = EngProfile.objects.get(project=p)
            except:
                engprofile = None

            #計畫歸屬與分類
            # try:
            first_plan = Plan.objects.get(id=p.plan_id).uplevel_id
            # second_plan = Plan.objects.get(id=first_plan).uplevel_id
            if first_plan:
                p.plan_name = Plan.objects.get(id=first_plan).name
                plan_class_id = Plan.objects.get(id=first_plan).plan_class_id
                p.plan_class = Option.objects.get(id=plan_class_id).value if plan_class_id else ' '
            else:
                p.plan_name = Plan.objects.get(id=p.plan_id).name
                plan_class_id = Plan.objects.get(id=p.plan_id).plan_class_id
                p.plan_class = Option.objects.get(id=plan_class_id).value if plan_class_id else ' '
            # except:
            #     p.plan_name = ' '
            #     p.plan_class = ' '



            #補助比例
            if p.pcc_no:
                p.allowance_scale = str(PCCProject.objects.get(uid=p.pcc_no).main_rate) + '%'
            else:
                capital_ratify_revision = budget.capital_ratify_revision if budget.capital_ratify_revision else 0
                capital_ratify_local_revision = budget.capital_ratify_local_revision if budget.capital_ratify_local_revision else 0

                if capital_ratify_revision != 0 and capital_ratify_local_revision != 0:
                    p.allowance_scale = str(round((capital_ratify_revision - capital_ratify_local_revision) / capital_ratify_revision * 100, 2)) + '%'
                else:
                    p.allowance_scale = ''
            
            #經費類別
            p.undertake = Option.objects.get(id=p.undertake_type_id).value
            
            #採購類別
            p.purchase = Option.objects.get(id=p.purchase_type_id).value

            #核定日期
            p.act_eng_plan_approved_plan = str(chase_project.act_eng_plan_approved_plan) if chase_project.act_eng_plan_approved_plan else str(chase_project.sch_eng_plan_approved_plan)

            #工程執行機關
            p.unit = Unit.objects.get(id=p.unit_id)

            #工程案漁港
            for port in p.fishing_port.all():
                port_name += port.name + '\n'
            p.port = port_name

            #辦理情形
            if chase_project.act_eng_do_closed:
                p.handling = '已結案'
            elif chase_project.act_eng_do_completion:
                p.handling = '已完工'
            elif chase_project.stat_illus_memo:
                p.handling = chase_project.stat_illus_memo
            else:
                p.handling = ' '

            #工程進度
            progress = PCCProgress.objects.filter(project__uid=p.pcc_no).order_by('-year', '-month')
            pcc_s_percent = 0
            pcc_a_percent = 0
            if progress:
                #第一步 找看看工程會同步資料有沒有
                progress = progress.first()
                pcc_s_percent = round(progress.percentage_of_predict_progress*100, 2)
                pcc_a_percent = round(progress.percentage_of_real_progress*100, 2)
            elif engprofile:
                #第二步 找日報表有沒有
                if engprofile.design_percent or pcc_s_percent:
                    pcc_s_percent = round(float(str(engprofile.design_percent)), 2)
                    pcc_a_percent = round(float(str(pcc_s_percent)), 2)
            #第三步 找看看進度追蹤
            if not pcc_s_percent and not pcc_a_percent:
                chases = CountyChaseProjectOneToMany.objects.filter(complete=True, project=p).order_by('-id')
                if chases:
                    chase = chases.first()
                    pcc_s_percent = round(float(str(chase.schedul_progress_percent)), 2)
                    pcc_a_percent = round(float(str(chase.actual_progress_percent)), 2)
            
            p.pcc_s_percent = str(pcc_s_percent) + '%'
            p.pcc_a_percent = str(pcc_a_percent) + '%'
            p.difference_percent = str(pcc_a_percent - pcc_s_percent) + '%'

            #工期
            if p.frcm_duration_type_id:
                p.duration_type = Option.objects.get(id=p.frcm_duration_type_id).value
            else:
                p.duration_type = ''
            
            #屬標餘款
            if p.tender_excess_funds == 0:
                p.tender_excess_funds = False
            elif p.tender_excess_funds == 1:
                p.tender_excess_funds = True
            else:
                p.tender_excess_funds = 'null'

            #招標預算
            if p.pcc_no:
                p.bidding_budget = PCCProject.objects.get(uid=p.pcc_no).contract_budget / 1000
            elif p.tender_budget:
                p.bidding_budget = p.tender_budget/1000
            else:
                p.bidding_budget = ' '

            #決標金額
            if p.pcc_no:
                p.decide_tenders_price = PCCProject.objects.get(uid=p.pcc_no).decide_tenders_price / 1000
            elif p.construction_bid != 0 and p.construction_bid:
                p.decide_tenders_price = p.construction_bid / 1000
            else:
                p.decide_tenders_price = ''

            #契約金額
            if p.pcc_no:
                if PCCProject.objects.get(uid=p.pcc_no).decide_tenders_price2:
                    p.decide_tenders_price2 = PCCProject.objects.get(uid=p.pcc_no).decide_tenders_price2 / 1000
                else:
                    p.decide_tenders_price2 = PCCProject.objects.get(uid=p.pcc_no).decide_tenders_price / 1000
            elif p.construction_bid != 0 and p.construction_bid:
                p.decide_tenders_price2 = p.construction_bid / 1000
            else:
                p.decide_tenders_price2 = ''

            #年度預算
            p.nine_budget = 0
            p.ten_budget = 0
            p.eleven_budget = 0
            p.twelve_budget = 0

            budget_list = Budget.objects.filter(fund=fund)
            for year_budget in budget_list:
                if year_budget.year <= 109 and year_budget.capital_ratify_budget:  #109年以前
                    p.nine_budget += year_budget.capital_ratify_budget
                elif year_budget.year == 110 and year_budget.capital_ratify_budget: #110年
                    p.ten_budget += year_budget.capital_ratify_budget
                elif year_budget.year == 111 and year_budget.capital_ratify_budget: #111年
                    p.eleven_budget += year_budget.capital_ratify_budget
                elif year_budget.year >= 112 and year_budget.capital_ratify_budget: #112年之後
                    p.twelve_budget += year_budget.capital_ratify_budget

            #結算金額
            p.balancing_price = 0
            if p.pcc_no:
                p.balancing_price = PCCProject.objects.get(uid=p.pcc_no).balancing_price if PCCProject.objects.get(uid=p.pcc_no).balancing_price else 0
            elif p.settlement_total_money:
                p.balancing_price = p.settlement_total_money
            elif p.settlement_construction_bid:
                p.balancing_price += p.settlement_construction_bid if p.settlement_construction_bid else 0
                p.balancing_price += p.settlement_planning_design_inspect if p.settlement_planning_design_inspect else 0
                p.balancing_price += p.settlement_manage if p.settlement_manage else 0
                p.balancing_price += p.settlement_pollution if p.settlement_pollution else 0
                try:
                    p.balancing_price += ProjectBidMoney.objects.get(project_id=p.id).settlement_value if ProjectBidMoney.objects.get(project_id=p.id).settlement_value else 0
                except:
                    pass
            
            #核定函勞務決標期限
            p.eng_plan_final_deadline = chase_project.act_eng_plan_final_deadline if chase_project.act_eng_plan_final_deadline else chase_project.sch_eng_plan_final_deadline

            #預計勞務決標日期
            p.sch_eng_plan_final = chase_project.sch_eng_plan_final

            #實際勞務決標日期
            p.act_eng_plan_final = chase_project.act_eng_plan_final

            #核定函工程決標期限
            p.eng_do_approved_plan = chase_project.act_eng_do_approved_plan if chase_project.act_eng_do_approved_plan else chase_project.sch_eng_do_approved_plan

            #預計工程決標日期
            p.sch_eng_do_final = chase_project.sch_eng_do_final

            #實際工程決標日期
            p.act_eng_do_final = chase_project.act_eng_do_final

            #預計工程簽約日期
            p.sch_eng_do_promise = chase_project.sch_eng_do_promise
            
            #實際工程簽約日期
            p.act_eng_do_promise = chase_project.act_eng_do_promise

            #預定開工日期
            p.sch_eng_do_start = chase_project.sch_eng_do_start

            #實際開工日期
            p.act_eng_do_start = chase_project.act_eng_do_start

            #預定完工日期
            p.sch_eng_do_completion = chase_project.sch_eng_do_completion

            #實際完工日期
            p.act_eng_do_completion = chase_project.act_eng_do_completion

            #勞務公告上網
            if chase_project.act_eng_plan_announcement_tender:
                p.eng_plan_announcement_tender = chase_project.act_eng_plan_announcement_tender 
            elif chase_project.sch_eng_plan_announcement_tender :
                p.eng_plan_announcement_tender = chase_project.sch_eng_plan_announcement_tender 
            else:
                p.eng_plan_announcement_tender = ' '

            #勞務履約中
            p.stat_wrk_per = chase_project.stat_wrk_per
            p.stat_wrk_per_date = chase_project.stat_wrk_per_date
            p.stat_wrk_per_memo = chase_project.stat_wrk_per_memo
            
            #工程標案招標文件準備中
            p.stat_file_prep = chase_project.stat_file_prep
            p.stat_file_prep_date = chase_project.stat_file_prep_date
            p.stat_file_prep_memo = chase_project.stat_file_prep_memo
            
            #工程標案招標文件公開預覽中
            p.stat_file_prvw = chase_project.stat_file_prvw
            p.stat_file_prvw_date = chase_project.stat_file_prvw_date
            p.stat_file_prvw_memo = chase_project.stat_file_prvw_memo
            
            #工程標案招標文件上網公告中
            p.stat_file_oln = chase_project.stat_file_oln
            p.stat_file_oln_date = chase_project.stat_file_oln_date
            p.stat_file_oln_memo = chase_project.stat_file_oln_memo
            
            #工程標案已決標，訂約中(含待開工)
            p.stat_res_ctr = chase_project.stat_res_ctr
            p.stat_res_ctr_date = chase_project.stat_res_ctr_date
            p.stat_res_ctr_memo = chase_project.stat_res_ctr_memo
            
            #施工中
            p.stat_cnst = chase_project.stat_cnst
            p.stat_cnst_date = chase_project.stat_cnst_date
            p.stat_cnst_memo = chase_project.stat_cnst_memo
            
            #停工中
            p.stat_stop = chase_project.stat_stop
            p.stat_stop_date = chase_project.stat_stop_date
            p.stat_stop_memo = chase_project.stat_stop_memo
            
            #履約爭議中
            p.stat_cnfl = chase_project.stat_cnfl
            p.stat_cnfl_date = chase_project.stat_cnfl_date
            p.stat_cnfl_memo = chase_project.stat_cnfl_memo
            
            #解約中
            p.stat_term_ing = chase_project.stat_term_ing
            p.stat_term_ing_date = chase_project.stat_term_ing_date
            p.stat_term_ing_memo = chase_project.stat_term_ing_memo
            
            #已申報竣工，竣工查驗中或準備驗收資料
            p.stat_cmplt = chase_project.stat_cmplt
            p.stat_cmplt_date = chase_project.stat_cmplt_date
            p.stat_cmplt_memo = chase_project.stat_cmplt_memo
            
            #驗收中(含初驗)
            p.stat_acpt = chase_project.stat_acpt
            p.stat_acpt_date = chase_project.stat_acpt_date
            p.stat_acpt_memo = chase_project.stat_acpt_memo
            
            #結算付款中
            p.stat_pay = chase_project.stat_pay
            p.stat_pay_date = chase_project.stat_pay_date
            p.stat_pay_memo = chase_project.stat_pay_memo
            
            #已結案
            if chase_project.act_eng_do_closed:
                p.eng_do_closed = True
                p.act_eng_do_closed = chase_project.act_eng_do_closed
            else:
                p.eng_do_closed = False
            
            #已解約(請加註日期)
            p.stat_term_ed = chase_project.stat_term_ed
            p.stat_term_ed_date = chase_project.stat_term_ed_date
            p.stat_term_ed_memo = chase_project.stat_term_ed_memo

            #其他(請加註日期)
            p.stat_oth = chase_project.stat_oth
            p.stat_oth_date = chase_project.stat_oth_date
            p.stat_oth_memo = chase_project.stat_oth_memo

            #停工或落後原因
            p.stat_stop_reason_memo = chase_project.stat_stop_reason_memo

            #解決對策
            p.stat_solution_memo = chase_project.stat_solution_memo

        output = StringIO()
        workbook = xlsxwriter.Workbook(output, 
            {'strings_to_numbers':  True,
            'strings_to_formulas': False,
            'strings_to_urls':     False})
        workbook = make_port_engineering_excel_file(workbook=workbook, projects=projects, month=month)
        workbook.close()
        output.seek(0)
        dir = '/var/www/fes/apps/project/exceltemp/%s' %(year)
        if not os.path.isdir(dir):
            os.mkdir(dir)
        with open('/var/www/fes/apps/project/exceltemp/%s/month_%s.xlsx' %(year, month), 'wb') as ff:
            print('write')
            ff.write(output.read())
        print('finish')