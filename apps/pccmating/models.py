#!-*- coding:utf8 -*-
# cimcore.modules.pccmating.models

# [foundation]

# [django]
from django.db import models

class Cofiguration(models.Model):
    key = models.CharField(verbose_name=u'Key', max_length=255, primary_key=True)
    value = models.CharField(verbose_name=u'Value', max_length=255)

class OnairProject(models.Model):
    uid = models.CharField(verbose_name=u'標案編號', max_length=255, primary_key=True, unique=True)
    lastsync = models.DateTimeField(verbose_name=u'最後更新', null=True)
    
    @classmethod
    def cProject(self, project_uid):
        ps = self.objects.filter(uid=project_uid)
        if(len(ps)==1): return ps[0]
        return self(uid=project_uid).save()
    
    @classmethod
    def dProject(self, project_uid):
        self.objects.filter(uid=project_uid).delete()
    
    def __unicode__(self):
        return self.uid
    
class Project(models.Model):
    on_pcc_now = models.BooleanField(verbose_name=u'目前在工程會上可查詢', default=False)
    chase = models.BooleanField(verbose_name=u'標註為重點追蹤', default=False)
    host_department = models.CharField(max_length=255, verbose_name=u'主辦機關',  null=True)
    implementation_department = models.CharField(max_length=255, verbose_name=u'執行機關',  null=True)
    implementation_department_code = models.CharField(max_length=255, verbose_name=u'執行機關代碼',  null=True)
    uid = models.CharField(verbose_name=u'標案編號', max_length=255, primary_key=True, unique=True)
    plan_name = models.CharField(max_length=255, verbose_name=u'歸屬計畫',  null=True)
    name = models.CharField(max_length=255, verbose_name=u'標案名稱',  null=True)
    s_design_complete_date = models.DateField(verbose_name=u'預定完成設計日期',null=True)
    r_design_complete_date = models.DateField(verbose_name=u'實際完成設計日期', null=True)
    s_public_date = models.DateField(verbose_name=u'預定公告日期', null=True)
    r_public_date = models.DateField(verbose_name=u'實際公告日期', null=True)
    public_times = models.IntegerField(verbose_name=u'實際公告次數', default=0)
    s_tenders_method = models.CharField(max_length=255, verbose_name=u'預定招標方式',  null=True)
    r_tenders_method = models.CharField(max_length=255, verbose_name=u'實際招標方式',  null=True)
    s_decide_tenders_date = models.DateField(verbose_name=u'預定決標日期', null=True)
    r_decide_tenders_date = models.DateField(verbose_name=u'實際決標日期', null=True)
    decide_tenders_method = models.CharField(max_length=255, verbose_name=u'實際決標方式',  null=True)

    main_rate = models.FloatField(verbose_name=u'中央比', null=True)
    sub_rate = models.FloatField(verbose_name=u'地方比', null=True)
    this_year_budget = models.FloatField(verbose_name=u'本年度可用預算', null=True)
    use_duration = models.IntegerField(verbose_name=u'累計天數', default=0)
    total_sch_price = models.FloatField(verbose_name=u'總累計預定完成金額', null=True)
    year_sch_price = models.FloatField(verbose_name=u'年累計預定完成金額', null=True)
    total_act_price = models.FloatField(verbose_name=u'總累計實際完成金額', null=True)
    year_act_price = models.FloatField(verbose_name=u'年累計實際完成金額', null=True)
    invoice_price = models.FloatField(verbose_name=u'已估驗計價金額', null=True)
    wait_pay_price = models.FloatField(verbose_name=u'待支付金額', null=True)
    cancel_reason = models.TextField(verbose_name=u'解約原因', null=True)

    total_budget = models.FloatField(verbose_name=u'工程總預算', null=True)
    contract_budget = models.FloatField(verbose_name=u'發包預算', null=True)
    decide_tenders_price = models.FloatField(verbose_name=u'決標金額', null=True)
    planning_unit = models.CharField(verbose_name=u'規劃單位', max_length=128, null=True)
    design_unit = models.CharField(verbose_name=u'設計單位', max_length=128, null=True)
    inspector_name = models.CharField(max_length=255, verbose_name=u'監造單位',  null=True)
    project_manage_unit = models.CharField(verbose_name=u'專案管理單位', max_length=128, null=True)
    constructor = models.CharField(max_length=255, verbose_name=u'得標廠商',  null=True)
    project_type = models.CharField(verbose_name=u'標案類別', max_length=64, null=True)
    engineering_county = models.CharField(max_length=255, verbose_name=u'縣市鄉鎮',  null=True)
    x_coord = models.FloatField(verbose_name=u'X座標', null=True)
    y_coord = models.FloatField(verbose_name=u'Y座標', null=True)
    engineering_location = models.CharField(max_length=255, verbose_name=u'施工地點',  null=True)
    project_memo = models.TextField(verbose_name=u'工程概要',  null=True)
    s_start_date = models.DateField(verbose_name=u'預定開工日期',  null=True)
    r_start_date = models.DateField(verbose_name=u'實際開工日期',  null=True)
    s_end_date = models.DateField(verbose_name=u'原合約預定完工日',  null=True)
    s_end_date2 = models.DateField(verbose_name=u'變更後預定完工日',  null=True)
    r_end_date = models.DateField(verbose_name=u'實際完工日期',  null=True)
    frcm_duration_type = models.CharField(max_length=255, verbose_name=u'工期類別', null=True)
    frcm_duration = models.IntegerField(verbose_name=u'總天數', default=0)
    month = models.IntegerField(verbose_name=u'進度月份',  null=True)
    percentage_of_predict_progress = models.FloatField(verbose_name=u'預定進度%', null=True)
    percentage_of_real_progress = models.FloatField(verbose_name=u'實際進度%', null=True)
    percentage_of_dulta = models.FloatField(verbose_name=u'差異%', null=True)
    status = models.CharField(verbose_name=u'狀態', max_length=64, null=True)
    s_executive_summary = models.TextField(verbose_name=u'預定執行摘要', null=True)
    r_executive_summary = models.TextField(verbose_name=u'實際執行摘要', null=True)
    delay_factor = models.TextField(verbose_name=u'落後因素', null=True)
    delay_reason = models.TextField(verbose_name=u'原因分析', null=True)
    delay_solution = models.TextField(verbose_name=u'解決辦法', null=True)
    improve_date = models.DateField(verbose_name=u'改進期限', null=True)
    r_checked_and_accepted_date = models.DateField(verbose_name=u'實際驗收完成日期',  null=True)
    s_last_pay_date = models.DateField(verbose_name=u'預定決算日期',  null=True)
    r_last_pay_date = models.DateField(verbose_name=u'實際決算日期',  null=True)
    head_of_agency = models.CharField(verbose_name=u'機關首長', max_length=64, null=True)
    manager = models.CharField(max_length=255, verbose_name=u'聯絡人',  null=True)
    telphone = models.CharField(max_length=255, verbose_name=u'聯絡電話',  null=True)
    manager_email = models.CharField(verbose_name=u'聯絡Email', max_length=64, null=True)
    fill_date = models.DateField(verbose_name=u'內容填報日', null=True)
    progress_date = models.DateField(verbose_name=u'進度填報日', null=True)
    lastsync = models.DateTimeField(verbose_name=u'最後更新', null=True)
    supervise_record = models.TextField(verbose_name=u'查核', null=True)
    supervise_score = models.TextField(verbose_name=u'分數', null=True)
    
    head_department = models.CharField(max_length=255, verbose_name=u'主管機關',  null=True)
    budget_from = models.CharField(max_length=255, verbose_name=u'經費來源機關',  null=True)
    host_department_code = models.CharField(max_length=255, verbose_name=u'招標公告單位代碼',  null=True)
    contract_id = models.CharField(max_length=255, verbose_name=u'契約編號',  null=True)
    decide_tenders_price2 = models.FloatField(verbose_name=u'變更設計後之契約金額', null=True)
    pay_method = models.CharField(max_length=255, verbose_name=u'契約費用給付方式',  null=True)
    s_base_price = models.FloatField(verbose_name=u'預估底價', null=True)
    r_base_price = models.FloatField(verbose_name=u'會核底價', null=True)
    balancing_price = models.FloatField(verbose_name=u'結算金額', null=True)
    last_pay_price = models.FloatField(verbose_name=u'決算金額', null=True)

    def __unicode__(self):
        return "[%s] %s"%(self.uid, self.name)

    def mapping_supervise_record(self):
        records = []
        if self.supervise_record:
            supervise_record = self.supervise_record.split(u'　')
            supervise_score = self.supervise_score.split(u'　')
            for n, i in enumerate(supervise_record):
                if not supervise_record[n]: continue
                try:
                    records.append({
                        'date': supervise_record[n],
                        'score': supervise_score[n],
                        'level': self.get_score_level(score=supervise_score[n])
                        })
                except: pass
        return records

    def get_fes_supervise_record(self):
        records = []
        for i in models.get_model(app_label="supervise", model_name="SuperviseCase").objects.filter(uid=self.uid).order_by('date'):
            try:
                records.append({
                    'date': '%s%s%s' % (i.date.year-1911, str(i.date.month).zfill(2), str(i.date.day).zfill(2)),
                    'score': int(i.score),
                    'level': self.get_score_level(score=str(i.score))
                    })
            except: pass
        return records

    def get_score_level(self, score):
        try:
            score = float(score.replace('(', '').replace(')', '').replace(' ', ''))
        except: return u'不評分'
        if score >= 90:
            score_level = u'優等'
        elif score >= 80:
            score_level = u'甲等'
        elif score >= 70:
            score_level = u'乙等'
        elif score >= 60:
            score_level = u'丙等'
        elif score >= 1:
            score_level = u'丁等'
        else:
            score_level = u'不評分'
        return score_level


class ProjectProgress(models.Model):
    project = models.ForeignKey(Project, related_name="progress")
    lastsync = models.DateTimeField(verbose_name=u'最後更新', null=True)
    
    year = models.IntegerField(verbose_name=u'年度',  null=True)
    month = models.IntegerField(verbose_name=u'月份',  null=True)
    
    percentage_of_predict_progress = models.FloatField(verbose_name=u'年累計預定進度', null=True)
    percentage_of_real_progress = models.FloatField(verbose_name=u'年累計實際進度', null=True)
    
    money_of_predict_progress = models.FloatField(verbose_name=u'年累計預定金額', null=True)
    money_of_real_progress = models.FloatField(verbose_name=u'年累計實際金額', null=True)
    
    totale_money_paid = models.FloatField(verbose_name=u'累計估驗計價金額(實支數)', null=True)
    status = models.CharField(max_length=255, verbose_name=u'執行狀況',  null=True)
    s_memo = models.CharField(max_length=255, verbose_name=u'預定工作摘要',  null=True)
    r_memo = models.CharField(max_length=255, verbose_name=u'實際執行摘要',  null=True)


'''
執行狀況對照 OPTIONS：
施工中 -> 165
停工 -> 166
保固中 -> 242
未開工 -> 239
解約 -> 214
設計中 -> 162
驗收 -> 241
準備招標文件中 -> 236
準備開工中 -> 240
審標中 -> 238
公告中 -> 237
已結案 -> 213
解約重新發包 -> 235
驗收完成 -> 168
完工待驗收 -> 167
'''