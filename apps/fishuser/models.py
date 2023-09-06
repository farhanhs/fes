# -*- coding:utf8 -*-
'''
具體設定：
    1.帳號群組分為
        1.	上層管理者         當然就是只能看
        1.	協同主辦工程師      針對一件工程的身分是協同主辦工程師
        1.	主辦工程師        一般的主辦工程師的自身群組
        1.	營造廠商          針對一件工程的身分是營造廠商
        1.	監造廠商          針對一件工程的身分是監造廠商
        1.	管考填寫員         只能填寫管考系統的人
        1.	漁船填寫員         只能填寫harbor的每日漁船數
        1.	漁港資訊填寫員      只能填寫harbor
        1.	本署帳號管理員      大帳號管理人
        1.	縣市帳號管理員      小帳號管理人
        1.	自辦主辦工程師      當工程為自辦時(沒有監造帳號)，的主辦工程師
        1.	自辦監造廠商        當工程被轉為自辦監造，原本的監造身分改變
        1.	註冊              只要是註冊來的預設群組
        1.  負責主辦工程師      針對一件工程的身分是負責主辦工程師

    1.帳號的權限由權限table來制定，所以會有一個table(Option)記錄著所有可以用的權限動作，然後再由另一個表來記錄誰可以幹麻
      ，這種設定可以讓同一個帳號針對不同工程案設定不同的權限，但是基本上我們目前讓他都一致(UserGroup)，並不打算開放讓他們自由設定
      ，現階段為所有營造廠商能做的事情都一樣(寫死的)，將來再新增讓他們可以自由編及權限的頁面(等他們長大一點)

    1.'帳號管理員'分為兩種，一種為本署的，負責新進人員或舊帳號的管理(新增、修改、關閉等)，另一種為縣市政府的，負責開創她們那個縣市的
      主辦工程師帳號，縣市帳號都會有一個帶頭碼(身分證字號英文碼+'_')，代表他是哪個縣市的，固每個縣市不會開到重複的帳號名稱，每個縣市都會擁有一個這個帳號(我們預先開好)

    1. '註冊'由使用者進我們的系統申請帳號，申請是自由的，誰都可以申請，申請完畢後是沒有任何'功能'及'工程'的
      ，當'主辦工程師'將工程匯入至FRCM系統後，系統自動產生兩組驗證碼(6碼，無大小寫之分)，分別是監造認證(a-z)及營造認證(0-9)，
      ，此時'主辦工程師'有義務告知'營造廠商'、'監造廠商'使用自己申請的帳號登入後，登錄認證碼來認領工程，目前這樣就完成認領，
      現階段不設計'主辦工程師'需再認可的機制(以後再說)

    1.'營造廠商'、'監造廠商'可以(也惟獨這兩者可以)分享工程給其他同樣是申請類型的帳號，只需給予認證碼即可完成認證，
      這裡設計讓他們可以填寫給系統中已經有的帳號

    1.'漁船填寫員'可以填寫漁港即時漁船數量，也惟獨只能填寫這裡(注定失敗的東西)

'''
import os, datetime, decimal, random

from PIL import Image
from types import IntType
from django.db import models as M
from django.db.models import Q
from django.contrib.auth.models import User, Group
from django.contrib.sessions.models import Session
from guardian.shortcuts import assign
from guardian.shortcuts import remove_perm
from guardian.shortcuts import get_perms
from settings import WRONGLOGINTIMELIMIT
from settings import WRONGLOGINDURATION
from common.models import Log
from common.models import SelfBaseObject
from common.models import JsonModel
from common.lib import findSublevel
from common.lib import calsize
from common.templatetags.utiltags import thumb
from general.models import Place, Unit, FishCityMenuManager
from harbor.models import FishingPort
from harbor.models import Aquaculture
from pccmating.models import Project as PCCProject
from pccmating.sync import getProjectInfo



def TODAY(): return datetime.date.today()


def _getProjectStatusInList():
    sort_by = [ '待審查',
                '審查通過',
                '辦理委託設計程序中',
                '設計招標準備中',
                '設計招標中',
                '設計執行中(含勞務)',
                '預算書圖審查及修正中',
                '設計書圖已送署審查完畢',
                '工程招標準備中',
                '工程招標中',
                '工程施工中',
                '工程停工中',
                '已峻工',
                '完工待驗中',
                '已驗收結算',
                '結案(含勞務)',
                '已解約',
                ]
    list = []
    for i in sort_by:
        list.append(Option.objects.get(swarm='project_status', value=i))
    return list



class Option(M.Model):
    swarm= M.CharField(verbose_name=u'群', max_length=128)
    value = M.CharField(verbose_name=u'選項', max_length=128)

    def __unicode__(self):
        return self.value


    class Meta:
        verbose_name = u'選項'
        verbose_name_plural = u'選項'
        unique_together = (("swarm", "value"),)
        permissions = (
            ('top_menu_management_system', u'第一層選單_工程管考系統'),
            ('top_menu_remote_control_system', u'第一層選單_遠端管理系統'),
            ('top_menu_auditing_system', u'第一層選單_查核系統'),
            ('top_menu_supervise_system', u'第一層選單_督導系統'),
            ('top_menu_harbor_system', u'第一層選單_漁港資訊系統'),
            ('top_menu_account', u'第一層選單_帳號管理'),
            ('sub_menu_management_system_search', u'第二層選單_工程管考系統_搜尋管考工程'),
            ('sub_menu_management_system_plan', u'第二層選單_工程管考系統_計畫列表'),
            ('sub_menu_management_system_draft', u'第二層選單_工程管考系統_草稿匣'),
            ('sub_menu_management_system_create', u'第二層選單_工程管考系統_新增工程案'),
            ('sub_menu_management_system_city', u'第二層選單_工程管考系統_縣市進度追蹤'),
            ('sub_menu_management_system_manage_money', u'第二層選單_工程管考系統_自辦工程管理費'),
            ('sub_menu_management_system_manage_money_commission', u'第二層選單_工程管考系統_委辦工程管理費'),
            ('sub_menu_management_system_control_form', u'第二層選單_工程管考系統_漁港管控表'),
            ('sub_menu_remote_control_system_my', u'第二層選單_遠端管理系統_我的工程'),
            ('sub_menu_remote_control_system_import', u'第二層選單_遠端管理系統_匯入工程'),
            ('sub_menu_remote_control_system_claim', u'第二層選單_遠端管理系統_認領工程'),
            ('sub_menu_remote_control_system_search', u'第二層選單_遠端管理系統_搜尋遠端工程'),
            ('sub_menu_remote_control_system_file', u'第二層選單_遠端管理系統_檔案管理'),
            ('sub_menu_remote_control_system_proposal', u'第二層選單_遠端管理系統_工程提案區'),
            ('sub_menu_remote_control_system_statisticstable_money', u'第二層選單_遠端管理系統_廠商得標金額排行'),
            ('sub_menu_supervise_system_create', u'第二層選單_督導系統_新增'),
            ('sub_menu_harbor_system_edit', u'第二層選單_漁港資訊系統_編輯資訊'),
            ('sub_menu_harbor_system_edit_portinstallationrecord', u'第二層選單_漁港資訊系統_填報漁港設施記錄'),
            ('sub_menu_warning_system_warninginfo', u'第二層選單_工程預警內容'),
        )


class ResetPasswordUser(M.Model):
    user = M.OneToOneField(User, verbose_name=u'帳號', related_name=u'user_reset')
    code = M.CharField(verbose_name=u'重設定碼', max_length=128)
    time = M.DateTimeField()



class UserProfile(M.Model, SelfBaseObject):
    user = M.OneToOneField(User, verbose_name=u'帳號', unique=True, related_name=u'user_profile')
    title = M.CharField(verbose_name=u'職稱', max_length=64, null=True)
    unit = M.ForeignKey(Unit, verbose_name=u'公司機關單位', null=True)
    phone = M.CharField(verbose_name=u'電話', max_length=64, null=True)
    fax = M.CharField(verbose_name=u'傳真', max_length=64, null=True)
    login = M.IntegerField(verbose_name=u'登入次數', default=0)
    need_resetpassword = M.BooleanField(default=True)
    group = M.ForeignKey(Group, verbose_name=u'群組', null=True)
    project_score = M.IntegerField(verbose_name=u'對工程的幫助滿意度', null=True)
    app_score = M.IntegerField(verbose_name=u'功能滿意度', null=True)
    all_score = M.IntegerField(verbose_name=u'整體滿意度', null=True)
    system_memo = M.TextField(verbose_name=u'系統建議', max_length=256, null=True)
    is_satisfaction = M.BooleanField(verbose_name=u'是否填寫滿意度調查表', default=False)

    def __unicode__(self):
        return self.user.username

    def rName(self):
        return u'%s%s' % (self.user.last_name, self.user.first_name)

    #以下還沒用到------------------------------
    def rJson(self):
        return self.__dict__

    def rJsonInHtml(self):
        json = self.rJson()
        json['username'] = self.user.username
        json['unit_name'] = self.unit.name if self.unit else ''
        json['group_name'] = self.group.name if self.group else ''

        keys = [k for k in json.keys() if k[0] == '_']
        for k in keys: del json[k]

        return json

    def rLastLogin(self):
        if self.user.last_login:
            return self.user.last_login.strftime(u'%Y-%m-%d %H:%M:%S')
        else:
            return ''

    def rIdentity(self, project_id=None):
        try:
            return FRCMUserGroup.objects.get(user=self.user, project__id=project_id).group.name
        except:
            if self.group.name:
                return self.group.name
            else:
                return None

    def is_contractor(self):
        contractor = FRCMUserGroup.objects.filter(user=self.user, group__id=4)
        if len(contractor) != 0:
            return True
        else:
            return False

    def is_inspector(self):
        inspector = FRCMUserGroup.objects.filter(user=self.user, group__id=5)
        if len(inspector) != 0:
            return True
        else:
            return False

#在這表裡面的人就是取消Email通知的人
class CencelLoginEmail(M.Model):
    user = M.OneToOneField(User, verbose_name=u'帳號')

class LoginHistory(M.Model):
    user = M.ForeignKey(User, verbose_name=u'帳號', unique=False)
    ip = M.CharField(verbose_name=u'IP', max_length=128, null=True)
    datetime = M.DateTimeField()


class WrongLogin(M.Model):
    session = M.OneToOneField(Session)
    start_time = M.DateTimeField()
    times = M.PositiveIntegerField(default=1)

    #以下還沒用到------------------------------
    def rTypeStatus(self):
        now = datetime.datetime.now()
        if self.times < WRONGLOGINTIMELIMIT:
            return True
        else:
            if (self.start_time + datetime.timedelta(minutes=5)) >= now:
                return False
            else:
                self.times = 0
                self.start_time = now
                self.save()
                return True

def _ca(user=None, project=u'', project_id=0, right_type_value=u''):
    if user.is_staff: return True

    if not user: return False
    if user.__class__ == UserProfile: user = user.user
    # because the Project model is import later than fishuser.models so we can't use Project at here
    if project and project.__class__ and project.__class__.__name__== 'Project':
        project_id = project.id

    identity = UserProfile.objects.get(user=user).rIdentity(project_id=project_id)
    try:
        Option.objects.get(swarm=str(identity+u'_權限'), value=right_type_value)
        return True
    except:
        return False


#<------------------------ Project Models ------------------------>
#TODO null=False 可不須定義，因為 django Model 預設就是 null=False

class DocumentOfProjectModels:
    ''' 在這裡先大略介紹 Project Models 有那些東西，它們的關聯是什麼!
        每個 Model 的詳細內容再寫到各自的 __doc__
        
        Plan 計畫案
        Project 標案
        Reserve 工程跨年度保留資料
        Fund 款項資料
        Appropriate 工程撥付數
        Progress 工程進度
        FRCMUserGroup
        Factory 相關廠商，承包與監造
        FundDetail 發包決標金細目
    '''
    pass


class Plan(M.Model):
    """ ＊計畫案資料 Plan
            -計畫名稱
            -計畫說明
            -上層計畫(F)

            1.因為各個計畫的深度不一致，依決議採以工程案為根向上串連上層計畫的方式記錄。
    """
    year = M.IntegerField(verbose_name='年度', default=107)
    name = M.CharField(verbose_name=u'計畫名稱', max_length=128)
    code = M.CharField(verbose_name=u'計畫代號', max_length=128)
    note = M.TextField(verbose_name=u'計畫說明', null=True)
    budget_type = M.ForeignKey(Option, related_name="plan_budget_type_set", verbose_name='預算類別', null=False, default=186) # 新增欄位
    project_serial = M.IntegerField(verbose_name=u'工程流水號', null=True)
    sort = M.DecimalField(verbose_name=u'排版序號', default=0 , max_digits=16 , decimal_places=5)
    uplevel = M.ForeignKey('self', verbose_name=u'上層計畫', related_name=u'sublevel_set', null=True)
    host = M.CharField(verbose_name=u'主辦機關', max_length=128, null=True)
    budget = M.DecimalField(verbose_name='計畫總預算(元)', max_digits=16 , decimal_places=3, null=True)
    no = M.CharField(verbose_name=u'計畫編號', max_length=20, null=True)
    auto_sum = M.BooleanField(verbose_name=u'是否為自動加總欄位', default=False)
    plan_class = M.ForeignKey(Option, related_name="plan_plan_class_set", verbose_name='計畫類別', null=True) # 新增漁港工程大表欄位
    
    def __unicode__(self):
        return self.name

    def rSubPlanInList(self):
        '''
            讀取所有下層計畫
        '''
        return findSublevel(self, sublevel_string=u'sublevel_set', order_by=u'pk')

    def have_sub_plan(self):
        '''
            讀取是否有下層計畫
        '''
        if Plan.objects.filter(uplevel=self):
            return True
        else:
            return False

    #以下還沒用到------------------------------
    def updatePlanBudgetInfo(self):
        for i in self.rSubPlanInList():
            for j in PlanBudget.objects.filter(plan=i):
                try:
                    row = PlanBudget.objects.get(plan=self, year=j.year)
                except:
                    row = PlanBudget(
                        plan = self,
                        year = j.year,
                    )
                    row.save()
        return True

    def rLevelNumber(self):
        level = 0
        parent = self
        while 1:
            if parent.uplevel:
                level += 1
                parent = parent.uplevel
            else:
                break
        return level

    def candelete(self):
        if self.rSubPlanInList() or Project.objects.filter(plan=self, deleter=None):
            return False
        return True

    def rBGcolor(self):
        bgcolors = ['#DFFFEA', '#FFDDDD', '#DDDDFF', '#FFF9E1', '#E8F9FF', '#F2F2F2', '#F2F2F2', '#F2F2F2', '#F2F2F2', '#F2F2F2', '#F2F2F2']
        return bgcolors[self.rLevelNumber()]



class PlanReserve(M.Model):
    """ ＊計畫案年度保留數
    """
    plan = M.ForeignKey(Plan, verbose_name='計畫', related_name="planreserve_plan")
    year = M.IntegerField(verbose_name='年度')
    value = M.DecimalField(verbose_name='資本門 自辦預算額(元)', max_digits=16 , decimal_places=3, null=True)
    memo = M.TextField(verbose_name=u'備註', null=True)
    


class PlanBudget(M.Model):
    """ ＊計畫案年度預算項目 PlanBudget
    """
    plan = M.ForeignKey(Plan, verbose_name='計畫')
    year = M.IntegerField(verbose_name='年度', null=True)
    capital_self = M.DecimalField(verbose_name='資本門 自辦預算額(元)', max_digits=16 , decimal_places=3, null=True)
    capital_trust = M.DecimalField(verbose_name='資本門 委辦預算額(元)', max_digits=16 , decimal_places=3, null=True)
    capital_grant = M.DecimalField(verbose_name='資本門 補助預算額(元)', max_digits=16 , decimal_places=3, null=True)
    regular_self = M.DecimalField(verbose_name='經常門 自辦預算額(元)', max_digits=16 , decimal_places=3, null=True)
    regular_trust = M.DecimalField(verbose_name='經常門 委辦預算額(元)', max_digits=16 , decimal_places=3, null=True)
    regular_grant = M.DecimalField(verbose_name='經常門 補助預算額(元)', max_digits=16 , decimal_places=3, null=True)
    memo = M.TextField(verbose_name=u'備註', null=True)


    def read_sum_budget(self):
        '''
            讀取自己的下層計畫預算總計金額
        '''
        year = self.year
        plans = PlanBudget.objects.filter(year=year, plan__uplevel=self.plan)
        values = {
            'capital_self': sum([float(str(i.capital_self)) if i.capital_self else 0 for i in plans]),
            'capital_trust': sum([float(str(i.capital_trust)) if i.capital_trust else 0 for i in plans]),
            'capital_grant': sum([float(str(i.capital_grant)) if i.capital_grant else 0 for i in plans]),
            'regular_self': sum([float(str(i.regular_self)) if i.regular_self else 0 for i in plans]),
            'regular_trust': sum([float(str(i.regular_trust)) if i.regular_trust else 0 for i in plans]),
            'regular_grant': sum([float(str(i.regular_grant)) if i.regular_grant else 0 for i in plans]),
        }
        return values


    #以下還沒用到------------------------------
    def rTotal(self):
        return float(self.capital_self or 0) + float(self.capital_trust or 0) + float(self.capital_grant or 0) + float(self.regular_self or 0) + float(self.regular_trust or 0) + float(self.regular_grant or 0)

    def rAuto_Sum(self, field_name):
        sum = 0
        for i in self.plan.rSubPlanInList():
            try:
                row = PlanBudget.objects.get(plan=i, year=self.year)
                if row.plan.auto_sum:
                    num = row.rAuto_Sum(field_name)
                else:
                    if field_name=='capital_self': num = row.capital_self or 0
                    elif field_name=='capital_trust': num = row.capital_trust or 0
                    elif field_name=='capital_grant': num = row.capital_grant or 0
                    elif field_name=='regular_self': num = row.regular_self or 0
                    elif field_name=='regular_trust': num = row.regular_trust or 0
                    elif field_name=='regular_grant': num = row.regular_grant or 0
                    elif field_name=='public_self': num = row.public_self or 0
                    elif field_name=='public_trust': num = row.public_trust or 0
                    elif field_name=='public_grant': num = row.public_grant or 0
            except: num = 0
            sum += num
        return sum

    def rCapitalTotal(self):
        return float(self.capital_self or 0) + float(self.capital_trust or 0) + float(self.capital_grant or 0)

    def rRegularTotal(self):
        return float(self.regular_self or 0) + float(self.regular_trust or 0) + float(self.regular_grant or 0)

    def rPublicTotal(self):
        return float(self.public_self or 0) + float(self.public_trust or 0) + float(self.public_grant or 0)



class Project(M.Model, JsonModel):
    """ ＊標案資料 Project
        此為記錄一個標案所有基本資料的 table ，包含各時期可能需要填入的資料欄位，可能會被持續的被更改或寫入。
    """
    # <{--- 工程基本資料 ---}>
    name = M.CharField(verbose_name='工作名稱', max_length=128)
    no = M.CharField(verbose_name='會計序號', max_length=64, null=True)# 轉作與會計系統比對之序號
    bid_no = M.CharField(verbose_name='契約編號(署內案號)', max_length=64, null=True)
    work_no = M.CharField(verbose_name='計畫編號', max_length=64, null=True)# 新增欄位，取代原有的"計畫編號"(漁業屬此處所指之"計畫"意指該"標案")
    year = M.IntegerField(verbose_name='年度')
    plan = M.ForeignKey(Plan, verbose_name='上層計畫')
    project_type = M.ForeignKey(Option, verbose_name='工程屬性分類', related_name='new_project_type', null=False)
    project_sub_type = M.ForeignKey(Option, verbose_name='工程屬性別', related_name='project_sub_type', null=True)# 更名，plan_type -> project_sub_type
    type_other = M.CharField(verbose_name='工程屬性別其他欄', max_length=64, null=True)# 新增欄位，紀錄工程屬性別的"其他"選項之說明
    undertake_type = M.ForeignKey(Option, verbose_name='承辦方式', related_name='new_undertake_type')#自委補
    budget_type = M.ForeignKey(Option, verbose_name='預算別', related_name='new_budget_type', default=168)
    budget_sub_type = M.ForeignKey(Option, verbose_name='預算別(資本門or經常門)', related_name='new_budget_sub_type', null=False, default=269)# 新增欄位，紀錄資本門or經常門，Option要新增兩筆資料id = 269,270
    purchase_type = M.ForeignKey(Option, verbose_name='採購類別(工程or勞務)', related_name='purchase_type', null=False, default=277)# 新增欄位，紀錄工程or勞務，Option要新增3筆資料id = 277,278,320
    place = M.ForeignKey(Place, verbose_name='縣市')
    fishing_port = M.ManyToManyField(FishingPort, verbose_name='漁港', related_name='new_project_fishing_port')# 新增欄位，取代 Project_Port，紀錄所在漁港
    aquaculture = M.ManyToManyField(Aquaculture, verbose_name='養殖區', related_name='new_project_aquaculture')# 新增欄位，紀錄所在養殖區
    location = M.CharField(verbose_name='工程施作地點', max_length=64, null=True)
    x_coord = M.IntegerField(verbose_name='X座標', null=True)
    y_coord = M.IntegerField(verbose_name='Y座標', null=True)
    unit = M.ForeignKey(Unit, verbose_name='主管機關')# 原定義為"執行機關"，但層級有別。
    project_memo = M.CharField(verbose_name='工程備註', max_length=4096, null=True)
    status = M.ForeignKey(Option, verbose_name='執行狀態', related_name='new_project_status', null=True)
    state_memo = M.CharField(verbose_name='狀態備註', max_length=4096, null=True)
    deleter = M.ForeignKey(User, verbose_name='刪除人', related_name='new_delete_user', null=True)
    ex_project = M.ForeignKey('self', verbose_name='前年度工程案', null=True)

    # <{--- 聯絡資料 ---}>
    self_contacter = M.CharField(verbose_name='署內連絡人', max_length=64, null=True)
    self_contacter_phone = M.CharField(verbose_name='署內連絡電話', max_length=64, null=True)
    self_contacter_email = M.EmailField(verbose_name='署內連絡email', max_length=128, null=True)
    self_charge = M.CharField(verbose_name='署內負責人', max_length=64, null=True)
    local_manager = M.CharField(verbose_name='縣市主管', max_length=64, null=True)
    local_manager_phone = M.CharField(verbose_name='縣市主管電話', max_length=64, null=True)
    local_manager_email = M.EmailField(verbose_name='縣市主管email', max_length=128, null=True)
    local_contacter = M.CharField(verbose_name='縣市連絡人', max_length=64, null=True)
    local_contacter_phone = M.CharField(verbose_name='縣市連絡電話', max_length=64, null=True)
    local_contacter_email = M.EmailField(verbose_name='縣市連絡email', max_length=128, null=True)
    local_charge = M.CharField(verbose_name='縣市負責人', max_length=64, null=True)
    contractor_contacter = M.CharField(verbose_name='廠商連絡人', max_length=64, null=True)
    contractor_contacter_phone = M.CharField(verbose_name='廠商連絡電話', max_length=64, null=True)
    contractor_contacter_email = M.EmailField(verbose_name='廠商連絡email', max_length=128, null=True)
    contractor_charge = M.CharField(verbose_name='廠商負責人', max_length=64, null=True)
    # <{--- 標案資訊 ---}>
    pcc_no = M.CharField(verbose_name='工程會編號', max_length=64, null=True)# 新增欄位，紀錄 PCC 標案編號
    
    abandoned_tender_count = M.IntegerField(verbose_name='流廢標次數', null=True)
    tender_excess_funds = M.NullBooleanField(verbose_name=u'是否為屬標餘款再使用之工程', null=True)
    tender_budget = M.DecimalField(verbose_name='招標預算(元)', null=True , max_digits=16 , decimal_places=3)
    construction_bid = M.DecimalField(verbose_name='工程金額(元)', null=True , max_digits=16 , decimal_places=3)# 改為允許 null
    settlement_construction_bid = M.DecimalField(verbose_name='工程金額結算(元)', null=True , max_digits=16 , decimal_places=3)# 改為允許 null
    construction_bid_memo = M.CharField(verbose_name='工程金額備註', max_length=512, null=True)
    
    # <{--- 新增S ---}>
    safety_fee = M.DecimalField(verbose_name='保險費(元)', null=True , max_digits=16 , decimal_places=3)# 新增欄位
    settlement_safety_fee = M.DecimalField(verbose_name='保險費結算(元)', null=True , max_digits=16 , decimal_places=3)# 新增欄位，區分契約價格與及算價格
    safety_fee_memo = M.CharField(verbose_name='保險費備註', max_length=512, null=True)
    business_tax = M.DecimalField(verbose_name='營業稅(元)', null=True , max_digits=16 , decimal_places=3)# 新增欄位
    settlement_business_tax = M.DecimalField(verbose_name='營業稅結算(元)', null=True , max_digits=16 , decimal_places=3)# 新增欄位，區分契約價格與及算價格
    business_tax_memo = M.CharField(verbose_name='營業稅備註', max_length=512, null=True)
    planning_design_inspect = M.DecimalField(verbose_name='規劃設計監造費(元)', null=True , max_digits=16 , decimal_places=3)# 新增欄位
    settlement_planning_design_inspect = M.DecimalField(verbose_name='規劃設計監造費結算(元)', null=True , max_digits=16 , decimal_places=3)# 新增欄位，區分契約價格與及算價格
    planning_design_inspect_memo = M.CharField(verbose_name='規劃費備註', max_length=512, null=True)# 新增欄位
    # <{--- 新增E ---}>

    manage = M.DecimalField(verbose_name='工程管理費(元)', null=True , max_digits=16 , decimal_places=3)# 改為允許 null
    settlement_manage = M.DecimalField(verbose_name='工程管理費結算(元)', null=True , max_digits=16 , decimal_places=3)# 改為允許 null
    manage_memo = M.CharField(verbose_name='工程管理費備註', max_length=512, null=True)
    pollution = M.DecimalField(verbose_name='空污費(元)', null=True , max_digits=16 , decimal_places=3)# 改為允許 null
    settlement_pollution = M.DecimalField(verbose_name='空污費結算(元)', null=True , max_digits=16 , decimal_places=3)# 改為允許 null
    pollution_memo = M.CharField(verbose_name='空污費備註', max_length=512, null=True)

    # <{--- 移到選填S ---}>
    planning_fee = M.DecimalField(verbose_name='規劃費(元)', null=True , max_digits=16 , decimal_places=3)# 新增欄位
    settlement_planning_fee = M.DecimalField(verbose_name='規劃費結算(元)', null=True , max_digits=16 , decimal_places=3)# 新增欄位，區分契約價格與及算價格
    planning_fee_memo = M.CharField(verbose_name='規劃費備註', max_length=512, null=True)# 新增欄位
    commissioned_research = M.DecimalField(verbose_name='委託研究費(元)', null=True , max_digits=16 , decimal_places=3)# 新增欄位
    settlement_commissioned_research = M.DecimalField(verbose_name='委託研究結算(元)', null=True , max_digits=16 , decimal_places=3)# 新增欄位，區分契約價格與及算價格
    commissioned_research_memo = M.CharField(verbose_name='委託研究備註', max_length=512, null=True)# 新增欄位
    design_bid = M.DecimalField(verbose_name='設計金額(元)', null=True , max_digits=16 , decimal_places=3)# 改為允許 null
    settlement_design_bid = M.DecimalField(verbose_name='設計金額結算(元)', null=True , max_digits=16 , decimal_places=3)# 新增欄位，區分契約價格與及算價格
    design_bid_memo = M.CharField(verbose_name='設計金額備註', max_length=512, null=True)
    inspect_bid = M.DecimalField(verbose_name='監造決標金額(元)', null=True , max_digits=16 , decimal_places=3)# 改為允許 null
    settlement_inspect_bid = M.DecimalField(verbose_name='監造決標金額結算(元)', null=True , max_digits=16 , decimal_places=3)# 改為允許 null
    inspect_bid_memo = M.CharField(verbose_name='監造決標金額備註', max_length=512, null=True)
    subsidy = M.DecimalField(verbose_name='外水電補助費(元)', null=True , max_digits=16 , decimal_places=3)# 新增欄位
    settlement_subsidy = M.DecimalField(verbose_name='外水電補助費結算(元)', null=True , max_digits=16 , decimal_places=3)# 新增欄位
    subsidy_memo = M.CharField(verbose_name='外水電補助費備註', max_length=512, null=True)# 新增欄位
    other_defray = M.DecimalField(verbose_name='其他費用(元)', null=True , max_digits=16 , decimal_places=3)# 改為允許 null
    settlement_other_defray = M.DecimalField(verbose_name='其他費用結算(元)', null=True , max_digits=16 , decimal_places=3)# 改為允許 null
    other_defray_memo = M.CharField(verbose_name='其他費用備註', max_length=512, null=True)
    
    cm_value = M.DecimalField(verbose_name=u'契約費用(元)', null=True , max_digits=16 , decimal_places=3)
    cm_settlement_value = M.DecimalField(verbose_name=u'結算費用(元)', null=True , max_digits=16 , decimal_places=3)
    cm_memo = M.CharField(verbose_name=u'費用備註', max_length=512, null=True)
    # <{--- 移到選填E ---}>

    total_money = M.DecimalField(verbose_name='發包及其他費用(元)', null=True , max_digits=16 , decimal_places=3)# 新增欄位，本應為計算值，若無詳細資料則以此值為用
    settlement_total_money = M.DecimalField(verbose_name='發包及其他費用結算(元)', null=True , max_digits=16 , decimal_places=3)# 新增欄位，本應為計算值，若無詳細資料則以此值為用
    allot_rate = M.DecimalField(verbose_name='本署負擔比例', max_digits=16 , decimal_places=6, null=True, default=100) # 修改預設為 100%
    subsidy_limit = M.DecimalField(verbose_name='補助上限(元)', null=True , max_digits=16 , decimal_places=3)# 新增欄位，補助款除了依照比例計算，若有設上限則超過(此)上限則以(此)上限為準。
    bid_type = M.ForeignKey(Option, verbose_name='招標方式', related_name='new_bid_type', null=True)
    contract_type = M.ForeignKey(Option, verbose_name='發包方式', related_name='new_contract_type', null=True)
    bid_on = M.CharField(verbose_name='投標廠商', max_length=2048, null=True)
    bid_final = M.CharField(verbose_name='決標廠商', max_length=256, null=True)
    bid_discount = M.CharField(verbose_name='決標折數', max_length=256, null=True)
    
    # <{--- FRCM ---}>
    contractor = M.ForeignKey(Unit, verbose_name='營造廠商', related_name='new_contractor', null=True)
    contractor_open = M.BooleanField(verbose_name='營造廠商帳號是否啟用', default=True)
    contractor_code = M.CharField(verbose_name='營造廠商FRCM認證碼', max_length=6, null=True, unique=True)
    inspector = M.ForeignKey(Unit, verbose_name='監造廠商', related_name='new_inspector', null=True)
    inspector_open = M.BooleanField(verbose_name='監造廠商帳號是否啟用', default=True)
    inspector_code = M.CharField(verbose_name='監造廠商FRCM認證碼', max_length=6, null=True, unique=True)
    frcm_inspector_type = M.ForeignKey(Option, verbose_name='監造方式', related_name='new_frcm_inspector_type', null=True)
    frcm_duration_type = M.ForeignKey(Option, verbose_name='工期計算方式', related_name='new_frcm_duration_type', null=True)
    frcm_duration = M.IntegerField(verbose_name='工期', null=True, default=0)
    frcm_duration_limit = M.DateField(verbose_name='限期完工期限', null=True)

    # <{--- 參數型資料 ---}>
    count_type = M.IntegerField(verbose_name='會計資料計算方式', default=0, null=True)# 暫時無用
    progress_type = M.ForeignKey(Option, verbose_name='進度來源', related_name='new_progress_type', default=199, null=True)# 暫時無用
    use_gallery = M.BooleanField(verbose_name=u'是否使用新版相片系統', default=True)
    is_public = M.BooleanField(verbose_name="是否公開", default=False)

    # <{--- 漁港管控表 ---}>
    control_form_memo = M.CharField(verbose_name=u'備註', max_length=128, null=True)
    allowance = M.DecimalField(verbose_name='補助(千元)', max_digits=16 , decimal_places=4, null=True)
    allowance_revise = M.DecimalField(verbose_name='調補助(千元)', max_digits=16 , decimal_places=4, null=True)
    matching_fund_1 = M.DecimalField(verbose_name='配合款1(千元)', max_digits=16 , decimal_places=4, null=True)
    matching_fund_2 = M.DecimalField(verbose_name='配合款2(千元)', max_digits=16 , decimal_places=4, null=True)
    fund_1 = M.DecimalField(verbose_name='基金1(千元)', max_digits=16 , decimal_places=4, null=True)
    fund_2 = M.DecimalField(verbose_name='基金2(千元)', max_digits=16 , decimal_places=4, null=True)
    commission = M.DecimalField(verbose_name='委辦(千元)', max_digits=16 , decimal_places=4, null=True)
    commission_revise	 = M.DecimalField(verbose_name='調委辦(千元)', max_digits=16 , decimal_places=4, null=True)
    selfpay = M.DecimalField(verbose_name='自辦(千元)', max_digits=16 , decimal_places=4, null=True)
    selfpay_revise = M.DecimalField(verbose_name='調自辦(千元)', max_digits=16 , decimal_places=4, null=True)


    class Meta:
        permissions = (
            ('view_all_project_in_management_system', u'在(工程管理系統)中_觀看_所有_工程案資訊'),
            ('edit_all_project_in_management_system', u'在(工程管理系統)中_編輯_所有_工程案資訊'),
            ('view_all_project_in_remote_control_system', u'在(遠端工程系統)中_觀看_所有_工程案資訊'),
            ('edit_single_project_in_remote_control_system', u'在(遠端工程系統)中_編輯_單一_工程案資訊'),
            ('view_single_project_in_remote_control_system', u'在(遠端工程系統)中_觀看_單一_工程案資訊'),
            )


    def __unicode__(self):
        return self.name

    def get_plan_name(self):
        #列出計畫名稱
        return u''.join([u'●%s' % i.plan.name for i in Budget.objects.filter(fund__project=self, plan__isnull=False)])

    def read_importer(self):
        try:
            return project.frcmusergroup_set.get(group__name__in=[u'負責主辦工程師', u'自辦主辦工程師']).user.user_profile.rName()
        except:
            return u'→'

    def sync_pcc_info(self):
        '''同步pcc欄位'''
        #extr = getProjectInfo(self.pcc_no)
        p = self
        pcc_p = PCCProject.objects.get(uid=self.pcc_no)
        p.project_memo = pcc_p.project_memo
        try: p.frcm_duration_type = Option.objects.get(name=pcc_p.frcm_duration_type)
        except: pass
        p.frcm_duration = pcc_p.frcm_duration
        p.location = pcc_p.engineering_location
        p.bid_final = pcc_p.constructor
        p.project_memo = pcc_p.project_memo
        if pcc_p.x_coord: p.x_coord = pcc_p.x_coord
        if pcc_p.y_coord: p.y_coord = pcc_p.y_coord
        if pcc_p.constructor: p.bid_final = pcc_p.constructor

        try: p.bid_type = Option.objects.get(swarm="bid_type", name=pcc_p.r_tenders_method)
        except: pass
        p.save()

        fields = [
            ['sch_eng_plan_acceptance_closed', 's_design_complete_date'],
            ['act_eng_plan_acceptance_closed', 'r_design_complete_date'],
            ['sch_eng_do_announcement_tender', 's_public_date'],
            ['sch_ser_announcement_tender', 's_public_date'],
            ['act_eng_do_announcement_tender', 'r_public_date'],
            ['act_ser_announcement_tender', 'r_public_date'],
            ['sch_eng_do_final', 's_decide_tenders_date'],
            ['act_eng_do_final', 'r_decide_tenders_date'],
            ['sch_eng_do_start', 's_start_date'],
            ['act_eng_do_start', 'r_start_date'],
            ['sch_eng_do_completion', 's_end_date'],
            ['act_eng_do_completion', 'r_end_date'],
            ['act_eng_do_acceptance', 'r_checked_and_accepted_date'],
        ]
        try:
            obo = p.countychaseprojectonebyone_set.get()
            for f in fields:
                try:
                    obo.__setattr__(f[0], getattr(pcc_p, f[1]))
                except: pass
            obo.save()
        except: pass

        return True

    def read_total_money(self):
        '''
            讀取發包及其他金額 或沒 結算金額 則取 契約金額
        '''
        #1.採用工程結算金額
        money = self.read_settlement_total_money()
        if not money:#2.採用工程契約金額
            money = self.read_contract_total_money()
        if not money: #3.採budget的核定/實際補助金額
            money = decimal.Decimal('0')
            budgets = Budget.objects.filter(fund__project=self)
            for b in budgets:
                #本署
                if b.capital_ratify_revision:
                    money += b.capital_ratify_revision
                else:
                    money += b.capital_ratify_budget or decimal.Decimal('0')
                #地方
                if b.capital_ratify_local_revision:
                    money += b.capital_ratify_local_revision
                else:
                    money += b.capital_ratify_local_budget or decimal.Decimal('0')

        return money

    def set_manage_money(self, obj=False):
        if obj: self = obj
        if self.undertake_type.value == u'自辦':
            A = float(self.construction_bid or 0)#工程金額
            B = float(self.safety_fee or 0)#保險額
            C = float(self.business_tax or 0)#營業稅額
            D = A-B-C
            if D < 5000000:
                E = D * 0.03
            elif D < 25000000:
                E = 5000000 * 0.03 + (D-5000000) * 0.015
            elif D < 100000000:
                E = 5000000 * 0.03 + (25000000-5000000) * 0.015 + (D-25000000) * 0.01
            elif D < 500000000:
                E = 5000000 * 0.03 + (25000000-5000000) * 0.015 + (100000000-25000000) * 0.01 + (D-100000000) * 0.007
            else:
                E = 5000000 * 0.03 + (25000000-5000000) * 0.015 + (100000000-25000000) * 0.01 + (500000000-100000000) * 0.007 + (D-500000000) * 0.005
            self.manage = int(max([0, E]))
        return self.save()

    def set_settlement_manage_money(self, obj=False):
        if obj: self = obj
        if self.undertake_type.value == u'自辦':
            A = float(self.settlement_construction_bid or 0)#工程金額
            B = float(self.settlement_safety_fee or 0)#保險額
            C = float(self.settlement_business_tax or 0)#營業稅額
            D = A-B-C
            if D < 5000000:
                E = D * 0.03
            elif D < 25000000:
                E = 5000000 * 0.03 + (D-5000000) * 0.015
            elif D < 100000000:
                E = 5000000 * 0.03 + (25000000-5000000) * 0.015 + (D-25000000) * 0.01
            elif D < 500000000:
                E = 5000000 * 0.03 + (25000000-5000000) * 0.015 + (100000000-25000000) * 0.01 + (D-100000000) * 0.007
            else:
                E = 5000000 * 0.03 + (25000000-5000000) * 0.015 + (100000000-25000000) * 0.01 + (500000000-100000000) * 0.007 + (D-500000000) * 0.005
            self.settlement_manage = int(max([0, E]))
        return self.save()

    def read_contract_total_money(self):
        '''
            契約金額
            工程金額 + 規劃設計監造費用 + 工程管理費 + 空污費 + 選填欄位
        '''
        if self.total_money: return float(self.total_money or 0)
        return float(self.construction_bid or 0) + float(self.planning_design_inspect or 0) + float(self.manage or 0) + float(self.pollution or 0) + float(str(sum([i.value or 0 for i in ProjectBidMoney.objects.filter(project=self)])))

    def read_settlement_total_money(self):
        '''
            結算金額
            工程金額 + 規劃設計監造費用 + 工程管理費 + 空污費 + 選填欄位
        '''
        if self.settlement_total_money: return float(self.settlement_total_money or 0)
        return float(self.settlement_construction_bid or 0) + float(self.settlement_planning_design_inspect or 0) + float(self.settlement_manage or 0) + float(self.settlement_pollution or 0) + float(str(sum([i.settlement_value or 0 for i in ProjectBidMoney.objects.filter(project=self)])))
        
    def create_i_code(self):
        '''
            製造i_code
        '''
        english = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z']
        again = True
        while again == True:
            i_code = ''
            for i in xrange(6):
                i_code += english[int(random.random()*26)]
            try:
                k = Project.objects.get(inspector_code=i_code)
                again = True
            except:
                again = False
        self.inspector_code = i_code
        self.save()
        return i_code

    def create_c_code(self):
        '''
            製造c_code
        '''
        again = True
        while again == True:
            c_code = ''
            for i in xrange(6):
                c_code += str(int(random.random()*10))
            try:
                k = Project.objects.get(contractor_code=c_code)
                again = True
            except:
                again = False
        self.contractor_code = c_code
        self.save()
        return c_code

    def get_images_count(self):
        '''
            取得相片系統已上傳相片的數量
        '''
        return self.rGalleryPics() if self.use_gallery else self.rFRCMAlreadyUploadPics()

    def get_design_percent(self):
        '''
            取得日報表系統監造日誌的預定進度
        '''
        try:
            return self.dailyreport_engprofile.get().design_percent
        except:
            return '0.00'

    def get_act_inspector_percent(self):
        '''
            取得日報表系統監造日誌的實際進度
        '''
        try:
            return self.dailyreport_engprofile.get().act_inspector_percent
        except:
            return '0.00'


    def get_act_contractor_percent(self):
        '''
            取得日報表系統施工日誌的實際進度
        '''
        try:
            return self.dailyreport_engprofile.get().act_contractor_percent
        except:
            return '0.00'

    def get_frcm_engneer(self):
        ''' 取得遠端匯入者 '''
        try:
            return self.frcmusergroup_set.get(group__name__in=[u'負責主辦工程師', u'自辦主辦工程師']).user
        except:
            return False

    def rFRCMAlreadyUploadPics(self):
        return self.photo_set.filter(phototype__value='正常').exclude(file='').count()

    def rFRCMNormalPics(self):
        return self.photo_set.filter(phototype__value='正常').count()


    def rGalleryPics(self):
        try:
            return self.photo_case.rRootNode().total_count
        except:
            return 0
        #return self.photo_case.rRootNode().total_count
    def rNowProgress(self):
        #回傳進度資訊中的最後一筆進度
        if len(list(self.progress_set.all().order_by('-date'))) > 0:
            return list(self.progress_set.all().order_by('-date'))[0]
        else: return False


    #以下還沒用到------------------------------
    def isdefault(self, user):
        #TODO 應該用 isDefault 吧!
        try:
            DefaultProject.objects.get(user=user, project=self)
            return True
        except:
            return False

    def rplanning_fee(self):
        #規劃費
        if self.settlement_planning_fee: return self.settlement_planning_fee
        elif self.planning_fee: return self.planning_fee
        else: return 0

    def rcommissioned_research(self):
        #委託研究費
        if self.settlement_commissioned_research: return self.settlement_commissioned_research
        elif self.commissioned_research: return self.commissioned_research
        else: return 0

    def rdesign_bid(self):
        #設計決標金額
        if self.settlement_design_bid: return self.settlement_design_bid
        elif self.design_bid: return self.design_bid
        else: return 0

    def rinspect_bid(self):
        #監造決標金額
        if self.settlement_inspect_bid: return self.settlement_inspect_bid
        elif self.inspect_bid: return self.inspect_bid
        else: return 0

    def rconstruction_bid(self):
        #工程決標金額
        if self.settlement_construction_bid: return self.settlement_construction_bid
        elif self.construction_bid: return self.construction_bid
        else: return 0

    def rpollution(self):
        #空污費
        if self.settlement_pollution: return self.settlement_pollution
        elif self.pollution: return self.pollution
        else: return 0

    def rmanage(self):
        #工程管理費
        if self.settlement_manage: return self.settlement_manage
        elif self.manage: return self.manage
        else: return 0

    def rsubsidy(self):
        #外水電補助費
        if self.settlement_subsidy: return self.settlement_subsidy
        elif self.subsidy: return self.subsidy
        else: return 0
    
    def rother_defray(self):
        #其他費用
        if self.settlement_other_defray: return self.settlement_other_defray
        elif self.other_defray: return self.other_defray
        else: return 0

    def rContractTotalMoney(self):
        # 發包及其他金額(契約金額):工程發包時之總費用；直接讀取 "發包及其他費用" 或計算 "規劃 + 委託研究 + 設計 + 監造 + 工程決標 + 空污費 + 施工管理費 + 外水電補助 + 其他" 費用
        if self.total_money and float(self.total_money) != 0.0: return float(self.total_money)
        else:
            money = float(self.planning_fee or 0) + float(self.commissioned_research or 0) + float(self.design_bid or 0) + float(self.inspect_bid or 0) + float(self.construction_bid or 0) + float(self.pollution or 0) + float(self.manage or 0) + float(self.subsidy or 0) + float(self.other_defray or 0)
            money += float(sum([i.value for i in ProjectBidMoney.objects.filter(project=self)]))
            return money

    def rSettlementTotalMoney(self):
        # 發包及其他金額(結算金額):工程結算後之總費用；直接讀取 "發包及其他費用結算" 或計算 "規劃結算 + 委託研究結算 + 設計結算 + 監造結算 + 工程決標結算 + 空污費結算 + 施工管理費結算 + 外水電補助結算 + 其他結算" 費用
        if self.settlement_total_money and float(self.settlement_total_money) != 0.0: return float(self.settlement_total_money)
        else:
            money = float(self.settlement_planning_fee or 0) + float(self.settlement_commissioned_research or 0) + float(self.settlement_design_bid or 0) + float(self.settlement_inspect_bid or 0) + float(self.settlement_construction_bid or 0) + float(self.settlement_pollution or 0) + float(self.settlement_manage or 0) + float(self.settlement_subsidy or 0) + float(self.settlement_other_defray or 0)
            money += float(sum([i.settlement_value or decimal.Decimal('0') for i in ProjectBidMoney.objects.filter(project=self)]))
            return money

    def rselftotal_money(self):
        #讀取發包及其他金額 或沒 結算金額 則取 契約金額
        if self.rSettlementTotalMoney():
            return self.rSettlementTotalMoney()
        else:
            return self.rContractTotalMoney()

    def rTotalMoneyInProject(self):
        # 發包及其他金額: 若有結算金額則採結算金額，若無則採契約金額
        if self.rSettlementTotalMoney() != 0: return self.rSettlementTotalMoney()
        else: return self.rContractTotalMoney()
    
    def rTotalMoney(self):
        # 工程款總計: 讀取 Fund 中的款項總計 rTotalProjectBudget
        return self.fund_set.get().rTotalProjectBudget()

    def rSubLocation(self):
        # 讀取所在的漁港或是養殖區
        if self.project_type.id == 227: sub = self.fishing_port.all()
        elif self.project_type.id == 228: sub = self.aquaculture.all()
        return sub

    def rTendersPrice(self):
        # 決標金額，直接由工程會讀取
        try: return list(self.relay_info.all().order_by('-date'))[0].getTendersPrice()
        except IndexError: return None

    def rActualProgress(self):
        # 目前的累計實際進度
        progress = Progress.objects.filter(project=self).order_by('-date')
        try: return progress[0].actual_progress_percent
        except IndexError: return None

    def rTotalSMoney(self):
        #讀取工程會抓下來資料的累計分配數
        fundrecords = self.fundrecord_set.all()
        return sum([float(f.total_s_money or 0) for f in fundrecords]) or 0
    
    def rTotalAppropriate(self):
        appropriates = Appropriate.objects.filter(project=self)
        total = 0.0
        for i in appropriates: total += float(i.num)
        return total

    


#        try: return list(self.progress_set.all().order_by('-date'))[0]
#        except: return False
    
# TODO 以下要重新整理
    def rSelfPay(self):
        # 本署實支數
        try: record = list(FundRecord.objects.filter(project=self).order_by('date'))[-1]
        except IndexError: return None
        return record.rSelfPay()

    def rLocalPay(self):
        # 地方實支數
        try: record = list(FundRecord.objects.filter(project=self).order_by('date'))[-1]
        except IndexError: return None
        return record.rLocalPay()

    def rTotalPay(self):
        # 地方實支數
        try: record = list(FundRecord.objects.filter(project=self).order_by('date'))[-1]
        except IndexError: return None
        return record.total_pay

    def rSelfUnpay(self):
        # 本署應付未付數
        try: record = list(FundRecord.objects.filter(project=self).order_by('date'))[-1]
        except IndexError: return None
        return record.rSelfUnpay()

    def rLocalUnpay(self):
        # 地方應付未付數
        try: record = list(FundRecord.objects.filter(project=self).order_by('date'))[-1]
        except IndexError: return None
        return record.rLocalUnpay()

    def rTotalUnpay(self):
        # 總應付未付數
        try: record = list(FundRecord.objects.filter(project=self).order_by('date'))[-1]
        except IndexError: return None
        return record.rTotalUnpay()

    def rImplementationRate(self):
        # 執行率
        try: record = list(FundRecord.objects.filter(project=self).order_by('date'))[-1]
        except IndexError: return None
        return record.rImplementationRate()

    def rAchievementRate(self):
        # 達成率
        try: record = list(FundRecord.objects.filter(project=self).order_by('date'))[-1]
        except IndexError: return None
        return record.rAchievementRate()

    def rSchedulProgress(self):
        # (累計)預定進度
        try: progress = list(Progress.objects.filter(project=self).order_by('date'))[-1]
        except IndexError: return None
        return progress.schedul_progress_percent

    def rActualProgress(self):
        # (累計)實際進度
        try: progress = list(Progress.objects.filter(project=self).order_by('date'))[-1]
        except IndexError: return None
        return progress.actual_progress_percent

    def rDailyReportProgress(self):
        # 監造報表進度
        try: progress = list(Progress.objects.filter(project=self).order_by('date'))[-1]
        except IndexError: return None
        return progress.rDailyReportProgress()

    def rTotalAppropriate(self):
        # 已撥款項
        appropriates = Appropriate.objects.filter(project=self)
        total = 0.0
        for i in appropriates: total += float(i.num)
        return total

    def rUnappropriate(self):
        # 未撥款項
        return self.fund_set.get().rSelfLoad() - self.rTotalAppropriate()
#    # <--- Old Function
#    def rTrueRate(self):
#        try: return float(list(Progress.objects.filter(project=self).order_by('-date'))[0].actual_progress_percent)
#        except: return 0.0
#
#    def rTotalRatifyBudget(self):
#        return self.fund_set.get().rTotalRatifyBudget()
#
#    def rTotalRatifyRevision(self):
#        return self.fund_set.get().rTotalRatifyRevision()
#
#    def getProgressPercent(self, date=TODAY(), type='actual'):
#        if type == 'actual':
#            percents = list(Progress.objects.filter(project=self).exclude(date=None).order_by('-date'))
#            if not percents or percents[-1].date > date:
#                return round(0,2)
#            for p in percents:
#                if p.date <= date:
#                    return float(p.actual_progress_percent)
#        elif type == 'schedul':
#            percents = list(ScheduledProgress.objects.filter(project=self).exclude(schedul_date=None).order_by('-schedul_date'))
#            if not percents or percents[-1].schedul_date > date:
#                return round(0,2)
#            for p in percents:
#                if p.schedul_date <= date:
#                    return float(p.schedul_progress_percent)
#
#    def rPortInList(self):
#        return [p.port for p in self.project_port_set.all()]
#
#    def rDailyreport(self):
#        return self.dailyreport_engprofile.get()



class ProjectBidMoney(M.Model):
    #額外新增的標案資訊金額
    project = M.ForeignKey(Project, verbose_name=u'工程案')
    field_type = M.ForeignKey(Option, verbose_name=u'金額種類swarm="bid_money_type"')
    value = M.DecimalField(verbose_name=u'契約費用(元)', null=True , max_digits=16 , decimal_places=3)
    settlement_value = M.DecimalField(verbose_name=u'結算費用(元)', null=True , max_digits=16 , decimal_places=3)
    memo = M.CharField(verbose_name=u'費用備註', max_length=512, null=True)



    class Meta:
        unique_together = (("project", "field_type"),)



class ProjectBidMoneyVersion(M.Model):
    #額外新增的標案資訊金額
    project = M.ForeignKey(Project, verbose_name=u'工程案')
    date = M.DateField(verbose_name=u'紀錄日期')
    no = M.CharField(verbose_name=u'文號', max_length=512, null=True)
    memo = M.TextField(verbose_name=u'費用備註', null=True)



class ProjectBidMoneyVersionDetail(M.Model):
    #額外新增的標案資訊金額
    version = M.ForeignKey(ProjectBidMoneyVersion, verbose_name=u'版本')
    field_name = M.CharField(verbose_name=u'欄位名稱', max_length=512)
    value = M.DecimalField(verbose_name=u'契約費用(元)', null=True , max_digits=16 , decimal_places=3)
    settlement_value = M.DecimalField(verbose_name=u'結算費用(元)', null=True , max_digits=16 , decimal_places=3)
    memo = M.CharField(verbose_name=u'費用備註', max_length=512, null=True)



class Draft_Project(M.Model):
    """ ＊玉慈的草稿區 Project
        此為記錄一個標案最基本的資料的table，玉慈專用，可以直接延續到新增工程。
    """
    # <{--- 工程基本資料 ---}>
    place = M.ForeignKey(Place, verbose_name='縣市')
    fishing_port = M.ManyToManyField(FishingPort, verbose_name='漁港', related_name='draft_project_fishing_port')# 新增欄位，取代 Project_Port，紀錄所在漁港
    aquaculture = M.ManyToManyField(Aquaculture, verbose_name='養殖區', related_name='_draftproject_aquaculture')# 新增欄位，紀錄所在養殖區
    project_type = M.ForeignKey(Option, verbose_name='工程屬性分類', related_name='draft_project_type', null=False)
    project_sub_type = M.ForeignKey(Option, verbose_name='工程屬性別', related_name='draft_project_sub_type', null=True)
    name = M.CharField(verbose_name='工作名稱', max_length=128, null=True)
    info = M.CharField(verbose_name='主要工作內容', max_length=4096, null=True)#(請填主要工作項目之明細及數量，如疏浚土方量、碼頭改善長度、加拋消波塊數量等)
    review_results = M.CharField(verbose_name='初審結果(請填優先順序及理由)', max_length=4096, null=True)
    sort = M.IntegerField(verbose_name=u'優先順序', null=True)
    self_money = M.DecimalField(verbose_name=u'概算經費(中央)', null=True , max_digits=16 , decimal_places=3, default=0)
    local_money = M.DecimalField(verbose_name=u'概算經費(地方配合款)', null=True , max_digits=16 , decimal_places=3, default=0)
    design = M.CharField(verbose_name='設計準備情形', max_length=2048, null=True)#(請填報是否已完成設計及是否已報漁業署同意在案)
    project = M.ForeignKey(Project, verbose_name='是否為前年延續性計畫',  null=True)
    fish_boat = M.CharField(verbose_name='設籍漁船資料(最新之設籍各噸級船筏數)', max_length=2048, null=True)
    real_fish_boat = M.CharField(verbose_name='實際作業漁船數(平均每日進出漁船筏資料)', max_length=2048, null=True)
    other_memo = M.CharField(verbose_name='其他補充說明', max_length=2048, null=True)#(如該港之漁產量/值、魚市場交易資料、設施使用情形)
    fect = M.CharField(verbose_name='工程預期效益', max_length=2048, null=True)
    memo = M.CharField(verbose_name='備註', max_length=2048, null=True)

    year = M.IntegerField(verbose_name='年度', null=True)
    plan = M.ForeignKey(Plan, verbose_name='上層計畫', null=True)
    undertake_type = M.ForeignKey(Option, verbose_name='承辦方式', related_name='draft_undertake_type', null=True)
    capital_ratify_budget = M.DecimalField(verbose_name=u'核定數', null=True , max_digits=16 , decimal_places=3, default=0)
    budget_sub_type = M.ForeignKey(Option, verbose_name='預算別(資本門or經常門)', related_name='draft_budget_sub_type', null=False, default=269)# 新增欄位，紀錄資本門or經常門，Option要新增兩筆資料id = 269,270
    purchase_type = M.ForeignKey(Option, verbose_name='採購類別(工程or勞務)', related_name='draft_purchase_type', null=False, default=277)# 新增欄位，紀錄工程or勞務，Option要新增兩筆資料id = 277,278
    unit = M.ForeignKey(Unit, verbose_name='主管機關', null=True)# 原定義為"執行機關"，但層級有別。
    type = M.ForeignKey(Option, verbose_name='草稿區縣市還是漁業署', related_name='draft_type', default=287)# 預設287，287(縣市提案草稿)或288(漁業署草稿)
#    deleter = M.ForeignKey(User, verbose_name='刪除人', related_name='draft_delete_user', null=True)
    
    #以下還沒用到------------------------------
    def get_sort_num(self):
        return Draft_Project.objects.filter(place=self.place, sort__lte=self.sort).count()



class Project_Port(M.Model):
    project = M.ForeignKey(Project, verbose_name=u'工程案')
    port = M.ForeignKey(FishingPort, verbose_name='漁港', null=True, related_name='port')


    
class DefaultProject(M.Model):
    user = M.ForeignKey(User, verbose_name=u'帳號')
    project = M.ForeignKey(Project, verbose_name=u'工程案')



class FRCMUserGroup(M.Model):
    user = M.ForeignKey(User, verbose_name=u'帳號')
    group = M.ForeignKey(Group, verbose_name=u'群組')
    project = M.ForeignKey(Project, verbose_name=u'工程案')
    
    #TODO 這裡的 date 應當指的是某使用者被授權可管理某工程案的日期，
    # 因為在這裡的紀錄會讓一個工程案有多個"匯入FRCM日期"。
    is_active = M.BooleanField(verbose_name=u'是否啟用', default=True)
    # A :
    # date 僅記錄最後一次被匯入 FRCM 的時間，作為使否被匯入的判別。
    date = M.DateField(verbose_name=u'匯入FRCM日期')

    def save(self, *args, **kw):
        assign('project.view_single_project_in_remote_control_system', self.user, self.project)
        group_name = self.group.name
        if u'負責主辦工程師' == group_name or u'自辦主辦工程師' == group_name or u'協同主辦工程師' == group_name:
            assign('project.edit_single_project_in_remote_control_system', self.user, self.project)

        if not self.is_active:
            remove_perm('project.view_single_project_in_remote_control_system', self.user, self.project)

        super(FRCMUserGroup, self).save(*args, **kw)


    def delete(self):
        remove_perm('project.view_single_project_in_remote_control_system', self.user, self.project)
        remove_perm('project.edit_single_project_in_remote_control_system', self.user, self.project)

        super(FRCMUserGroup, self).delete()


class Factory(M.Model):
    project = M.ForeignKey(Project, verbose_name=u'標案編號')
    unit = M.ForeignKey(Unit, verbose_name=u'廠商')
    status = M.ForeignKey(Option, verbose_name=u'身分')


class RelayInfo(M.Model):
    """ ＊資料暫存區 RelayInfo
    """
    # 資料暫存區，當工程資料從工程會擷取回來後，會經整理並暫時存放於此，帶主辦審核，通過後轉存為正式資料
    project = M.ForeignKey(Project, verbose_name=u'工程案', related_name='relay_info')
    pcc_record = M.ForeignKey(PCCProject, verbose_name=u'PCC紀錄', null=True)
    pcc_sync_date = M.DateTimeField(verbose_name=u'更新工程會資料時間', null=True)
    check_sync_date = M.DateTimeField(verbose_name=u'確核/同步資料時間', null=True)
    year = M.IntegerField(verbose_name=u'年度', null=True)
    month = M.IntegerField(verbose_name=u'月份', null=True)
    date = M.DateField(verbose_name=u'進度時間', null=True)
    total_s_progress = M.DecimalField(verbose_name=u'年累計預定進度', max_digits=16 , decimal_places=2, null=True)
    total_r_progress = M.DecimalField(verbose_name=u'年累計實際進度', max_digits=16 , decimal_places=2, null=True)
    s_memo = M.CharField(max_length=255, verbose_name=u'預定工作摘要',  null=True)
    r_memo = M.CharField(max_length=255, verbose_name=u'實際執行摘要',  null=True)
    total_s_money = M.DecimalField(verbose_name=u'年累計預定金額(元)', max_digits=16 , decimal_places=3, null=True)# 應該就是傳說中的"分配數"
    total_r_money = M.DecimalField(verbose_name=u'年累計實際金額(元)', max_digits=16 , decimal_places=3, null=True)
    total_pay = M.DecimalField(verbose_name=u'累計估驗計價金額(元)', max_digits=16 , decimal_places=3, null=True)# 這個應該就是"實支數"了
    status = M.ForeignKey(Option, verbose_name='執行狀態', related_name='pcc_status', null=True)
    check_sync_date = M.DateTimeField(verbose_name=u'確核/同步資料時間', null=True)
    checker = M.ForeignKey(User, verbose_name=u'確核人', related_name='pcc_checker', null=True)

    #以下還沒用到------------------------------
    def getTendersPrice(self):
        # 決標金額，直接由工程會讀取
        return self.pcc_record.decide_tenders_price



class Fund(M.Model):
    """ ＊工作預算 Fund (should rename to budget)
        改挪作為工作預算表
    """
    project = M.ForeignKey(Project, verbose_name=u'工程ID')
    status_memo = M.CharField(verbose_name='狀態備註', max_length=4096, null=True)# 作為統整表之備註
    contract = M.DecimalField(verbose_name=u'工程款 發包金額(元)', null=True , max_digits=16 , decimal_places=3)
    pollution = M.DecimalField(verbose_name=u'工程款 空污費(元)', null=True , max_digits=16 , decimal_places=3)
    manage = M.DecimalField(verbose_name=u'工程款 工程管理費(元)', null=True , max_digits=16 , decimal_places=3)
    entrust_design = M.DecimalField(verbose_name=u'工程款 委託設計費(元)', null=True , max_digits=16 , decimal_places=3)
    entrust_supervision = M.DecimalField(verbose_name=u'工程款 委託監造費(元)', null=True , max_digits=16 , decimal_places=3)
    other = M.DecimalField(verbose_name=u'工程款 其他(元)', null=True , max_digits=16 , decimal_places=3)
    memo_first = M.CharField(max_length=1024, verbose_name=u'計畫書備註',  null=True)
    memo_second = M.CharField(max_length=1024, verbose_name=u'另備註',  null=True)
    memo_del = M.CharField(max_length=1024, verbose_name=u'被刪除的備註',  null=True)

    def get_capital_ratify_budget(self):
        '''
        總 核定數(預算數)
        '''
        return sum([i.capital_ratify_budget or decimal.Decimal('0') for i in self.budget_set.all()])

    def get_capital_ratify_revision(self):
        '''
        總 實際補助金額
        '''
        return sum([i.capital_ratify_revision or decimal.Decimal('0') for i in self.budget_set.all()])

    def get_capital_ratify_local_budget(self):
        '''
        總 地方核定數(預算數)
        '''
        return sum([i.capital_ratify_local_budget or decimal.Decimal('0') for i in self.budget_set.all()])

    def get_capital_ratify_local_revision(self):
        '''
        總 地方實際補助金額
        '''
        return sum([i.capital_ratify_local_revision or decimal.Decimal('0') for i in self.budget_set.all()])

    def get_over_the_year(self):
        '''
        總 歷年
        '''
        return sum([i.over_the_year or decimal.Decimal('0') for i in self.budget_set.all()])

    def rSelfLoad(self):
        '''
            本署負擔總金額
            本署負擔（保留）數 = 發包及其他費用 * 本署負擔比例
            若本署負擔（保留）數 > 本署負擔上限金額
            則本署負擔（保留）數 = 本署負擔上限金額
            若發包及其他費用無值，則本署負擔（保留）數 = 核定數。
        '''
        money = self.project.read_total_money()

        # type_A money*負擔比例
        type_A = float(money)*float(self.project.allot_rate or 100.0)*0.01
        # type_B 輔助上限
        type_B = float(self.project.subsidy_limit or 0)
        if type_B == 0:
            return type_A
        elif type_A > type_B:
            return type_B
        else:
            return type_A

    def rlocalMatchFund(self):
        '''
            地方配合款 = 發包及其他費用 - 本署負擔數 (若無發包及其他費用，則地方配合款 = 核定地方配合款)
        '''
        money = self.project.read_total_money()
        return float(money) - self.rSelfLoad()

    def rTotalProjectBudget(self):
        '''
            工程款總計
        '''
        return float(self.contract or 0) + float(self.pollution or 0) + float(self.manage or 0) + float(self.entrust_design or 0) + float(self.entrust_supervision or 0) + float(self.other or 0)

    def rAllocationToNow(self):
        '''至今為止累計分配數'''
        all_allocation = self.project.allocation_set.filter(date__lte=TODAY())
        sum = 0.0
        for allocation in all_allocation:
            sum += float(allocation.allocation)
        return sum

    def rTotalAllocation(self):
        '''累計分配數'''
        all_allocation = self.project.allocation_set.all()
        sum = 0.0
        for allocation in all_allocation:
            sum += float(allocation.allocation)
        return sum

    #以下還沒用到------------------------------
    def rTotalAppropriate(self):
        #已撥付數
        all_appropriate = self.project.appropriate_set.all()
        sum = 0.0
        for appropriate in all_appropriate:
            sum += float(appropriate.num)
        return sum

    def rUnappropriate(self):
        return self.project.fund_set.get().rFinialRatify()- self.rTotalAppropriate()

    
    def rTotalCapitalRatifyBudgetInString(self):
        s = ''
        for i in self.budget_set.all():
            s += str(i.year) + "年:" + str(int(i.capital_ratify_budget or 0)) + "　"
        return s

    def rTotalCapitalRatifyRevisionInString(self):
        s = ''
        for i in self.budget_set.all():
            s += str(i.year) + "年:" + str(int(i.capital_ratify_revision or 0)) + "　"
        return s

    def rSelfSurplus(self):
        # 本署發包賸餘金
        if float(self.project.allot_rate) == 0.0: surplus = (self.rFinialRatify() - float(self.project.rTotalMoney() or 0.0))*float(0)*0.01
        else: surplus = (self.rFinialRatify() - float(self.project.rTotalMoney() or 0.0))*float(self.project.allot_rate or 100.0)*0.01
        if surplus <= 0: surplus = 0
        return surplus

    def rLocalSurplus(self):
        # 地方發包賸餘金
        surplus = self.rFinialRatify() - float(self.project.rTotalMoney() or 0.0) - self.rSelfSurplus()
        if surplus <= 0: surplus = 0
        return surplus

    def rFinialRatify(self):
        # 最後預算：如果有修正核定數即採用修正核定數，若無則採用核定數。
        if self.rTotalRatifyRevision() == 0: return float(self.rTotalRatifyBudget())
        else: return float(self.rTotalRatifyRevision())

    def rTotalSurplus(self):
        # 總發包賸餘金：核定預算 - 發包及其他金額
        surplus = self.rFinialRatify() - float(self.project.rTotalMoney() or 0.0)
        if surplus <= 0: surplus = 0
        return surplus
    
    def rTotalRatifyBudget(self):
        # 總核定數：資本門+經常門
        return float(self.capital_ratify_budget or 0) + float(self.regular_ratify_budget or 0)

    def rTotalRatifyRevision(self):
        # 總修正核定數：資本門+經常門
        return float(self.capital_ratify_revision or 0) + float(self.regular_ratify_revision or 0)



class Budget(M.Model):
    year = M.IntegerField(verbose_name=u'年度', null=True)
    fund = M.ForeignKey(Fund, verbose_name=u'預算ID')
    plan = M.ForeignKey(Plan, verbose_name=u'計畫', null=True, related_name="budget_plan")
    capital_ratify_budget = M.DecimalField(verbose_name=u'核定數(預算數)', null=True , max_digits=16 , decimal_places=3)# 新增欄位，核定數
    capital_ratify_revision = M.DecimalField(verbose_name=u'實際補助金額', null=True , max_digits=16 , decimal_places=3)# 新增欄位，修正核定數
    capital_ratify_local_budget = M.DecimalField(verbose_name=u'地方配合款(預算數)', null=True , max_digits=16 , decimal_places=3)# 新增欄位，地方核定數
    capital_ratify_local_revision = M.DecimalField(verbose_name=u'地方實際配合款金額', null=True , max_digits=16 , decimal_places=3)# 新增欄位，修正地方核定數
    over_the_year = M.DecimalField(verbose_name=u'歷年(元)', null=True , max_digits=16 , decimal_places=3)# 新增欄位，地方核定數
    proportion = M.DecimalField(verbose_name='補助比例', null=True, max_digits=16 , decimal_places=3)#補助比例欄位
    priority = M.IntegerField(verbose_name='排序', default=10000)
    new = M.NullBooleanField(verbose_name=u"是否為最新一筆", null=True) #是否為最新一筆預算資料
    # origin_budget = M.IntegerField(verbose_name=u'屬於哪筆預算的歷史資料', null=True)
    
    def get_capital_ratify(self):
        '''
            取得實際補助金額 若無值 取 核定數
        '''
        if self.capital_ratify_revision:
            return self.capital_ratify_revision
        else:
            return self.capital_ratify_budget or decimal.Decimal(0)

    def get_capital_ratify_local(self):
        '''
            取得地方實際配合款金額 若無值 取 地方配合款
        '''
        if self.capital_ratify_revision:
            return self.capital_ratify_revision
        else:
            return self.capital_ratify_budget or decimal.Decimal(0)

    def rPlanMoney(self):
        '''
            計畫經費 = 實際補助金額 + 地方配合款
        '''
        return self.get_capital_ratify() + self.get_capital_ratify_local()



    #以下還沒用到------------------------------
    def should_pay(self):
        '''
            應撥款數
        '''
        money = self.fund.rTotalProjectBudget() - self.total_appropriate()
        if money <= 0:
            return 0
        else:
            return money

    def total_appropriate(self):
        '''
            已撥款數
        '''
        project = self.fund.project
        appropriatebs = project.appropriate_set.all()
        return int(sum([float(i.num or 0) for i in appropriatebs]))

    def not_pay(self):
        '''
            未撥款數 = 應撥款數 - 已撥款數
        '''
        return self.should_pay() - self.total_appropriate()

    def rShouldPayThisYear(self, year=''):
        #今年應撥款數
        if year:
            year = int(year)
            year += 1911
        else:
            year = self.year + 1911

        if (self.fund.rTotalProjectBudget() - self.rTotalAppropriatebyLastYear(year=year-1911)) <= 0:
            return 0
        else:
            return self.fund.rTotalProjectBudget() - self.rTotalAppropriatebyLastYear(year=year-1911)

    def rTotalProjectNotPayThisYear(self, year=''):
        #尚未撥款數   #總工程費 - #明年以前已撥款數
        if year:
            year = int(year)
            year += 1911 + 1
        else:
            year = self.year + 1911 + 1

        if (self.fund.rTotalProjectBudget() - self.rTotalAppropriatebyLastYear(year=year-1911)) <= 0:
            return 0
        else:
            return self.fund.rTotalProjectBudget() - self.rTotalAppropriatebyLastYear(year=year-1911)


    def rTotalAppropriatebyThisYear(self, year=''):
        #今年已撥款數
        project = self.fund.project
        if year:
            year = int(year)
            year += 1911
        else:
            year = self.year + 1911
        appropriatebs = self.fund.project.appropriate_set.filter(allot_date__gte=str(year)+'-1-1', allot_date__lte=str(year)+'-12-31')
        sum = 0.0
        for appropriate in appropriatebs:
            sum += float(appropriate.num)
        return int(sum)

    def rTotalAppropriatebyLastYear(self, year=''):
        #今年以前已撥款數
        project = self.fund.project
        if year:
            year = int(year)
            year += 1911
        else:
            year = self.year + 1911
        appropriatebs = self.fund.project.appropriate_set.filter(allot_date__lte=str(year-1)+'-12-31')
        sum = 0.0
        for appropriate in appropriatebs:
            sum += float(appropriate.num)
        return int(sum * 1000)

#    def rSelfLoad(self):
#        # 本署負擔: 改以工程款總計(rTotalProjectBudget)*負擔比例 或 輔助上限
#        # type_A 工程款總計(rTotalProjectBudget)*負擔比例
#        type_A = float(self.capital_ratify_budget or 0.0)*float(self.fund.project.allot_rate or 100.0)*0.01
#        # type_B 輔助上限
#        type_B = float(self.fund.project.subsidy_limit or 0)
#        if type_B == 0:
#            return type_A
#        elif type_A > type_B:
#            return type_B
#        else:
#            return type_A
#
#    def rlocalMatchFund(self):
#        # 地方配合款: 改以工程款總計(rTotalProjectBudget)-本署負擔
#        return (float(self.capital_ratify_budget or 0.0)) - (float(self.rSelfLoad()))


class FundRecord(M.Model):
    """ ＊會計記錄 FundRecord
        逐次紀錄，目前採用精度為月(一個月一筆紀錄)
        -經費來源： 暫時設計進去，目前無實作。
        -記錄日期： 資料進資料庫或被修改的時間。
        -日期： 該紀錄的實際日期；目前都自動定為該月份最後一天。
        -分配數: 應由工程/計畫主辦人員於初期將預算分配於該年度之各個月，而該月所分配到之預算額及分配數。可從標案系統抓取參考(年累計預定金額)。
        -年累計實際金額: 標案系統欄位，備用。
        -實支數: 實際給付給廠商之金額，可從標案系統抓取參考(累計估驗計價金額)。
        -紀錄來源: 若為從工程會貼回之資料，則於此紀錄貼回來原。
        -編輯者: 若為從工程會貼回之資料，則紀錄操作人。
    """
    project = M.ForeignKey(Project, verbose_name=u'工程ID')
    year = M.IntegerField(verbose_name=u'年度')
    source = M.ForeignKey(Plan, verbose_name=u'經費來源', null=True)# 新增欄位，紀錄錢從哪邊扣
    record_date = M.DateField(verbose_name=u'記錄日期', null=True)
    date = M.DateField(verbose_name=u'日期', null=True)# 新增欄位
    total_s_money = M.DecimalField(verbose_name=u'分配數(元)', max_digits=16 , decimal_places=3, null=True)# 新增欄位
    total_r_money = M.DecimalField(verbose_name=u'年累計實際金額(元)', max_digits=16 , decimal_places=3, null=True)# 新增欄位，也許它才是實支數？
    total_pay = M.DecimalField(verbose_name=u'實支數(元)', max_digits=16 , decimal_places=3, null=True)# 新增欄位
    reocrd_source = M.ForeignKey(RelayInfo, verbose_name=u'紀錄來源', related_name='new_fund_pcc_source', null=True)# 新增欄位，紀錄資料來源
    status_memo = M.CharField(verbose_name='狀態備註', max_length=4096, null=True)
    editer = M.ForeignKey(User, verbose_name=u'編輯者', related_name='new_fund_record_editer', null=True)# 新增欄位，紀錄資料更新者

    #以下還沒用到------------------------------
    def rSelfPay(self):
        # 本署實支數
        if self.total_pay:
            if float(self.project.allot_rate) == 0.0: return 0
            else: return float(self.total_pay)*float(self.project.allot_rate or 100.) / 100.
        else: return 0

    def rLocalPay(self):
        # 地方實支數
        if self.total_pay: return float(self.total_pay) - self.rSelfPay()
        else: return 0

    def rTotalUnpay(self):
        # 總應付未付數：發包及其他費用*實際進度 - 累計實支數
        try: progress = Progress.objects.filter(project=self.project, date__year=self.date.year, date__month=self.date.month)
        except AttributeError: return None
        if progress.count() == 0:
            return None
        else:
            unpay = round(self.project.rTotalMoney()*float(progress.order_by('-date')[0].actual_progress_percent)*0.01 - float(self.total_pay), 3)
            if unpay < 0: unpay = 0
            return unpay

    def rSelfUnpay(self):
        # 本署應付未付數：總應付未付數*負擔比例
        if self.project.allot_rate:
            if float(self.project.allot_rate) == 0.0: return round(self.rTotalUnpay()*float(0)*0.01, 3)
            else:
                try: return round(self.rTotalUnpay()*float(self.project.allot_rate or 100.0)*0.01, 3)
                except TypeError: return None
        else: return None

    def rLocalUnpay(self):
        # 地方應付未付數：總應付未付數 - 本署應付未付數
        try: return round(self.rTotalUnpay() - self.rSelfUnpay(), 3)
        except TypeError: return None
    
    def rTotalPassPayout(self):
        # 總歷年支用數
        last = FundRecord.objects.filter(project=self.project, year__lte=self.year).order_by('date')
        if last.count() == 0: return None
        else: return last[0].rSelfPay()

    def rSelfPassPayout(self):
        # 本署歷年支用數
        if float(self.project.allot_rate) == 0.0: return self.rTotalPassPayout()*float(0)*0.01
        else: return self.rTotalPassPayout()*float(self.project.allot_rate or 100.0)*0.01

    def rLoaclPassPayout(self):
        # 地方歷年支用數
        return self.rTotalPassPayout() - self.rSelfPassPayout()

    def rFundImplementation (self):
        # 經費執行數：實支數+本署應付未付數+本署賸餘款
        try: return float(self.total_pay) + self.rSelfUnpay() + self.project.fund_set.get().rSelfSurplus()
        except TypeError: return None

    def rImplementationRate(self):
        # 執行率：經費執行數/(累計分配數+本署賸餘款)
        try: return round(self.rFundImplementation()*100.0/((float(self.total_s_money)) + self.project.fund_set.get().rSelfSurplus()), 2)
        except TypeError: return None
        except ZeroDivisionError: return None
    
    def rAchievementRate(self):
        # 達成率：經費執行數/(本署負擔 or 保留數)
        try: return round(self.rFundImplementation()*100.0/self.project.fund_set.get().rSelfLoad(), 2)
        except ZeroDivisionError: return None
        except TypeError: return None



class Appropriate(M.Model):
    """ ＊工程撥付數 Appropriate
        漁業署撥予縣市政府之款項，一般而言一工程的撥付次數可能只有兩三次，款項大而不密集。
        自辦為自己新增
        其他從會計系統吃
    """
    project = M.ForeignKey(Project, verbose_name=u'工程ID')
    name = M.CharField(verbose_name='名稱', max_length=256, null=True)
    type = M.ForeignKey(Option, verbose_name='種類swarm="appropriate_type"', related_name='appropriate_type', null=True)# 工程款/勞務類
    num = M.DecimalField(verbose_name=u'撥付數(元)', null=True , max_digits=16 , decimal_places=3)
    allot_date = M.DateField(verbose_name=u'撥付日期', null=True)
    record_date = M.DateField(verbose_name=u'填表日期')
    vouch_no = M.CharField(verbose_name='撥付文號', max_length=256, null=True) # 新增欄位
    memo = M.CharField(verbose_name='撥付備註', max_length=1024, null=True) # 新增欄位


class Reserve(M.Model):
    """ ＊工程跨年度保留資料 Reserve
        工程於年底無法如期完成時即辦保留，此為紀錄保留資訊。目前僅申請保留數較重要。
        本表可延伸作讀取依工程各年度詳細金額資訊之用。
    """
    project = M.ForeignKey(Project, verbose_name=u'工程ID')
    year = M.IntegerField(verbose_name=u'年度')
    apply_date = M.DateField(verbose_name=u'申請日期')
    amount = M.DecimalField(verbose_name=u'申請保留數(元)', default=0 , max_digits=16 , decimal_places=3)
    allocation = M.DecimalField(verbose_name=u'已撥款尚未支用數(元)', null=True , max_digits=16 , decimal_places=3)# 改為容許 null
    un_allocation = M.DecimalField(verbose_name=u'未撥款尚未支用數(元)', null=True , max_digits=16 , decimal_places=3)# 改為容許 null
    reserve_date = M.DateField(verbose_name=u'保留期限', null=True)# 改為容許 null
    reason = M.CharField(verbose_name=u'保留理由', null=True, max_length=4096)# 改為容許 null
    prove = M.CharField(verbose_name=u'證明文件', null=True, max_length=4096)# 改為容許 null
    memo = M.CharField(verbose_name=u'備註', null=True, max_length=4096)

    #以下還沒用到------------------------------
    def rTotalPassPayout(self):
        # 總歷年支用數
        last = FundRecord.objects.filter(project=self.project, year__lte=self.year).order_by('date')
        if last.count() == 0: return None
        else: return last[0].rSelfPay()

    def rSelfPassPayout(self):
        # 本署歷年支用數
        if float(self.project.allot_rate) == 0.0: return self.rTotalPassPayout()*float(0)*0.01
        else: return self.rTotalPassPayout()*float(self.project.allot_rate or 100.0)*0.01

    def rLoaclPassPayout(self):
        # 地方歷年支用數
        return self.rTotalPassPayout() - self.rSelfPassPayout()


#class OldProgress(M.Model):
#    """ ＊工程進度 Progress
#        -標案編號
#        -進度日期
#        -進度百分比
#        -填表日期
#    """
#    project = M.ForeignKey(Project, verbose_name=u'工程ID')
#    actual_date = M.DateField(verbose_name=u'進度日期', null=True)
#    actual_progress_percent = M.DecimalField(verbose_name=u'進度百分比(%)', default=0 , max_digits=16 , decimal_places=2, null=True)
#    actual_record_date = M.DateField(verbose_name=u'填表日期')


#class OldScheduledProgress(M.Model):
#    """ ＊工程預定進度 Progress
#    """
#    project = M.ForeignKey(Project, verbose_name=u'工程ID')
#    schedul_date = M.DateField(verbose_name=u'進度日期', null=True)
#    schedul_progress_percent = M.DecimalField(verbose_name=u'進度百分比(%)', default=0 , max_digits=16 , decimal_places=2, null=True)
#    schedul_record_date = M.DateField(verbose_name=u'填表日期')


class Progress(M.Model):
    """ 
        ＊工程進度 Progress
        目前修正為貼近標案系統之格式，便於貼回。
    """
    project = M.ForeignKey(Project, verbose_name=u'工程ID')
    date = M.DateField(verbose_name=u'進度日期', null=True)# 更名，actual_date -> date
    schedul_progress_percent = M.DecimalField(verbose_name=u'累計預計進度百分比(%)',  null=True, max_digits=16 , decimal_places=2)# 新增欄位，將預定進度移至此
    actual_progress_percent = M.DecimalField(verbose_name=u'累計實際進度百分比(%)',  null=True, max_digits=16 , decimal_places=2) # 取消 null
    s_memo = M.CharField(max_length=255, verbose_name=u'預定工作摘要',  null=True)# 新增欄位，紀錄 PCC 摘要
    r_memo = M.CharField(max_length=255, verbose_name=u'實際執行摘要',  null=True)# 新增欄位，紀錄 PCC 摘要
    status = M.ForeignKey(Option, verbose_name='執行狀態', related_name='new_progress_status', null=True)# 新增欄位，紀錄 PCC 各階段執行狀況
    record_date = M.DateField(verbose_name=u'填表日期')# 更名，actual_record_date -> record_date
    source = M.ForeignKey(RelayInfo, verbose_name=u'紀錄來源', related_name='new_progress_pcc_source', null=True)# 新增欄位，紀錄資料來源
    editer = M.ForeignKey(User, verbose_name=u'編輯者', related_name='new_progress_editer', null=True)# 新增欄位，紀錄資料更新者

    #以下還沒用到------------------------------
    def rDailyReportProgress(self):
        if self.date:
            try: return self.project.dailyreport_engprofile.get().readInspectorProgressByDate(date=self.date)
            except: return u'尚未有日報表紀錄。'
        else: return None



_UPLOAD_TO = os.path.join('apps', 'project', 'media', 'project', 'photo', '%Y%m%d')
class ProjectPhoto(M.Model):
    project = M.ForeignKey(Project, verbose_name=u'工程案')
    memo = M.CharField(verbose_name=u'備註', max_length=4096, null=True)
    name = M.CharField(verbose_name=u'相片名稱', max_length=256, null=True, default=u'')
    extension = M.ForeignKey(Option, verbose_name=u'附檔名', null=True)
    file = M.ImageField(upload_to=_UPLOAD_TO, null=True)
    uploadtime = M.DateTimeField(verbose_name=u'上傳時間', null=True)

    def rUrl(self):
        url = self.file.name.split('apps/project')[-1]
        return url

    def rExt(self):
        return self.file.name.split('.')[-1].lower()



_FILE_UPLOAD_TO = os.path.join('apps', 'frcm', 'media', 'frcm', 'tempfile', '%Y%m%d')
class FRCMTempFile(M.Model):
    #臨時檔案上傳區
    upload_user = M.ForeignKey(User, verbose_name='上傳者')
    project = M.ForeignKey(Project, verbose_name='工程案')
    upload_date = M.DateField(verbose_name='上傳日期')
    xcoord = M.DecimalField(verbose_name='X座標', null=True , max_digits=20 , decimal_places=12)
    ycoord = M.DecimalField(verbose_name='y座標', null=True , max_digits=20 , decimal_places=12)
    name = M.CharField(verbose_name='檔案名', max_length=256, null=True, default='')
    file = M.ImageField(upload_to=_FILE_UPLOAD_TO, null=True)
    memo = M.CharField(verbose_name='備註說明', null=True, max_length=2048)

    def rUrl(self):
        return self.file.name.split('apps/frcm/')[-1]

    def rThumbUrl(self):
        thumbsrc = thumb(self.file.name, "width=1024,height=768")
        if thumbsrc == 'media/images/error.png':
            return self.file.name.split('apps/frcm/')[-1]
        else:
            return thumbsrc.split('apps/frcm/')[-1]

    def rExt(self):
        return self.file.name.split('.')[-1].lower()

    def calSize(self):
        if self.file:
            return calsize(self.file.size)
        else:
            return calsize(0)


# 可以廢掉 ScheduledProgress
class ScheduledProgress(M.Model):
    """ ＊工程預定進度 Progress
    """
    project = M.ForeignKey(Project, verbose_name=u'工程ID')
    schedul_date = M.DateField(verbose_name=u'進度日期', null=True)
    schedul_progress_percent = M.DecimalField(verbose_name=u'進度百分比(%)', default=0 , max_digits=16 , decimal_places=2, null=True)
    schedul_record_date = M.DateField(verbose_name=u'填表日期')


class BudgetProject(M.Model):
    # 暫時廢了
    capital_money = M.DecimalField(verbose_name='資本門 漁業署自辦或委辦或補助金額', default=0 , max_digits=16 , decimal_places=3)# 暫時無用
    regular_money = M.DecimalField(verbose_name='經常門 漁業署自辦或委辦或補助金額', default=0 , max_digits=16 , decimal_places=3)# 暫時無用
    year = M.IntegerField(verbose_name='年度')# 暫時無用
    fund = M.ForeignKey(Fund, verbose_name='預算資訊')# 暫時無用
    capital_coordination = M.DecimalField(verbose_name='資本門 配合款', default=0 , max_digits=16 , decimal_places=3)# 可計算，暫時無用
    regular_coordination = M.DecimalField(verbose_name='經常門 配合款', default=0 , max_digits=16 , decimal_places=3)# 可計算，暫時無用
    capital_memo = M.CharField(verbose_name='資本門 備註', max_length=4096, null=True)# 暫時無用
    regular_memo = M.CharField(verbose_name='經常門 備註', max_length=4096, null=True)# 暫時無用
    capital_project_use_money = M.DecimalField(verbose_name='資本門 工程執行經費', default=0 , max_digits=16 , decimal_places=3)# 即發包及其他費用，暫時無用
    regular_project_use_money = M.DecimalField(verbose_name='經常門 工程執行經費', default=0 , max_digits=16 , decimal_places=3)# 即發包及其他費用，暫時無用
    capital_bid_surplus = M.DecimalField(verbose_name='資本門 發包剩餘款', default=0 , max_digits=16 , decimal_places=3)# 可計算，暫時無用
    regular_bid_surplus = M.DecimalField(verbose_name='經常門 發包剩餘款', default=0 , max_digits=16 , decimal_places=3)# 可計算，暫時無用
    capital_co_adj = M.DecimalField(verbose_name='資本門 地方調整後配合款', default=0 , max_digits=16 , decimal_places=3)# 暫時無用
    regular_co_adj = M.DecimalField(verbose_name='經常門 地方調整後配合款', default=0 , max_digits=16 , decimal_places=3)# 暫時無用
    capital_adjust_memo = M.CharField(verbose_name='資本門 調整備註', max_length=4096, null=True)# 暫時無用
    regular_adjust_memo = M.CharField(verbose_name='經常門 調整備註', max_length=4096, null=True)# 暫時無用
    next_year_need = M.DecimalField(verbose_name='跨年度工程99年度以後需再編列經費額度', default=0 , max_digits=16 , decimal_places=3)# 無用
#    freeze_money = M.IntegerField(verbose_name='凍結經費', default=0)

#　原紀錄各期進度，以下為計算累計進度。現改為直接紀錄累計進度，各期進度暫不顯示。
#    def rAccumulateSchedulProgress(self):
#        if self.date:
#            prior = Progress.objects.filter(project=self.project, date__lte=self.date)
#            accumulate = decimal.Decimal(str(0))
#            for i in prior:
#                accumulate += prior.schedul_progress_percent
#            return accumulate
#        else: return None
#
#    def rAccumulateActualProgress(self):
#        if self.date:
#            prior = Progress.objects.filter(project=self.project, date__lte=self.date)
#            accumulate = decimal.Decimal(str(0))
#            for i in prior:
#                accumulate += prior.actual_progress_percent
#            return accumulate
#        else: return None



class CountyChaseTime(M.Model):
    chase_date = M.DateField(verbose_name=u'追蹤日期', null=True)
    new_update = M.TextField(verbose_name='更新資料紀錄', max_length=4096, null=True)
    user = M.ForeignKey(User, verbose_name=u'新增追蹤的人', null=True, related_name=u'Chase_user')

    def read_ex_chase(self):
        '''讀取前一個追蹤紀錄'''
        exs = CountyChaseTime.objects.filter(chase_date__lt=self.chase_date).order_by('-chase_date')
        if exs: return exs[0]
        else: return False

    def read_next_chase(self):
        '''讀取下一個追蹤紀錄'''
        exs = CountyChaseTime.objects.filter(chase_date__gt=self.chase_date).order_by('chase_date')
        if exs: return exs[0]
        else: return False



class CountyChaseTimeNewUpdate(M.Model):
    countychasetime = M.ForeignKey(CountyChaseTime, verbose_name='追蹤日期')
    project = M.ForeignKey(Project, verbose_name=u'追蹤工程案')
    field_name = M.TextField(verbose_name='更新欄位名稱', null=True)
    value = M.TextField(verbose_name='更新值', null=True)



class CountyChaseProjectOneByOne(M.Model):
    project = M.ForeignKey(Project, verbose_name=u'追蹤工程案')
    # total_money = M.DecimalField(verbose_name=u'發包及其他費用，未發包以核定數代替', null=True , max_digits=16 , decimal_places=3)
    # close = M.BooleanField(verbose_name=u'申請我已結案，不再通知', default=False)
    # check = M.BooleanField(verbose_name=u'確認結案，不再通知', default=False)
    give_up_times = M.IntegerField(verbose_name='招標期間流標次數', default=0)
    total_budget = M.PositiveIntegerField(verbose_name='工程(計畫)總預算', default=0)
    work_info = M.TextField(verbose_name='工作(計畫)內容', default=u'')

    #test_date = M.DateField(verbose_name=u'測試日期',null=True)

    sch_ser_approved_plan = M.DateField(verbose_name=u'預計_勞務_核定計畫', null=True)
    act_ser_approved_plan = M.DateField(verbose_name=u'實際_勞務_核定計畫', null=True)
    ser_approved_plan_memo = M.CharField(verbose_name=u'勞務_核定計畫/備註', max_length=256, null=True)
    sch_ser_signed_tender = M.DateField(verbose_name=u'預計_勞務_簽辦招標', null=True)
    act_ser_signed_tender = M.DateField(verbose_name=u'實際_勞務_簽辦招標', null=True)
    ser_signed_tender_memo = M.CharField(verbose_name=u'勞務_簽辦招標/備註', max_length=256, null=True)
    sch_ser_announcement_tender = M.DateField(verbose_name=u'預計_勞務_勞務公告上網', null=True)
    act_ser_announcement_tender = M.DateField(verbose_name=u'實際_勞務_勞務公告上網', null=True)
    ser_announcement_tender_memo = M.CharField(verbose_name=u'勞務_公告招標/備註', max_length=256, null=True)
    sch_ser_selection_meeting = M.DateField(verbose_name=u'預計_勞務_公開評選會議(限制性招標)', null=True)
    act_ser_selection_meeting = M.DateField(verbose_name=u'實際_勞務_公開評選會議(限制性招標)', null=True)
    ser_selection_meeting_memo = M.CharField(verbose_name=u'勞務_公開評選會議(限制性招標)/備註', max_length=256, null=True)
    sch_ser_promise = M.DateField(verbose_name=u'預計_勞務_定約', null=True)
    act_ser_promise = M.DateField(verbose_name=u'實際_勞務_定約', null=True)
    ser_promise_memo = M.CharField(verbose_name=u'勞務_定約/備註', max_length=256, null=True)
    sch_ser_work_plan = M.DateField(verbose_name=u'預計_勞務_工作計畫書', null=True)
    act_ser_work_plan = M.DateField(verbose_name=u'實際_勞務_工作計畫書', null=True)
    ser_work_plan_memo = M.CharField(verbose_name=u'勞務_工作計畫書/備註', max_length=256, null=True)
    sch_ser_interim_report = M.DateField(verbose_name=u'預計_勞務_期中報告', null=True)
    act_ser_interim_report = M.DateField(verbose_name=u'實際_勞務_期中報告', null=True)
    ser_interim_report_memo = M.CharField(verbose_name=u'勞務_期中報告/備註', max_length=256, null=True)
    sch_ser_final_report = M.DateField(verbose_name=u'預計_勞務_期末報告', null=True)
    act_ser_final_report = M.DateField(verbose_name=u'實際_勞務_期末報告', null=True)
    ser_final_report_memo = M.CharField(verbose_name=u'勞務_期末報告/備註', max_length=256, null=True)
    sch_ser_do_acceptance = M.DateField(verbose_name=u'預計_勞務_驗收', null=True)
    act_ser_do_acceptance = M.DateField(verbose_name=u'實際_勞務_驗收', null=True)
    ser_do_acceptance_memo = M.CharField(verbose_name=u'工程_勞務_驗收/備註', max_length=256, null=True)
    sch_ser_acceptance_closed = M.DateField(verbose_name=u'預計_勞務_結案', null=True)
    act_ser_acceptance_closed = M.DateField(verbose_name=u'實際_勞務_結案', null=True)
    ser_acceptance_closed_memo = M.CharField(verbose_name=u'勞務_結案/備註', max_length=256, null=True)

    sch_eng_plan_agree_plan = M.DateField(verbose_name=u'預計_工程_(設計規劃)同意計畫', null=True)
    act_eng_plan_agree_plan = M.DateField(verbose_name=u'實際_工程_(設計規劃)同意計畫', null=True)
    eng_plan_agree_plan_memo = M.CharField(verbose_name=u'實際_工程_(設計規劃)同意計畫/備註', max_length=256, null=True)
    sch_eng_plan_approved_plan = M.DateField(verbose_name=u'預計_工程_(設計規劃)核定計畫', null=True)
    act_eng_plan_approved_plan = M.DateField(verbose_name=u'實際_工程_(設計規劃)核定計畫', null=True)
    eng_plan_approved_plan_memo = M.CharField(verbose_name=u'工程_(設計規劃)核定計畫/備註', max_length=256, null=True)
    sch_eng_plan_signed_tender = M.DateField(verbose_name=u'預計_工程_(設計規劃)簽辦招標', null=True)
    act_eng_plan_signed_tender = M.DateField(verbose_name=u'實際_工程_(設計規劃)簽辦招標', null=True)
    eng_plan_signed_tender_memo = M.CharField(verbose_name=u'工程_(設計規劃)簽辦招標/備註', max_length=256, null=True)
    sch_eng_plan_announcement_tender = M.DateField(verbose_name=u'預計_工程_(設計規劃)公告上網', null=True)
    act_eng_plan_announcement_tender = M.DateField(verbose_name=u'實際_工程_(設計規劃)公告上網', null=True)
    eng_plan_announcement_tender_memo = M.CharField(verbose_name=u'工程_(設計規劃)公告上網/備註', max_length=256, null=True)
    sch_eng_plan_final = M.DateField(verbose_name=u'預計_工程_(設計規劃)決標', null=True)
    act_eng_plan_final = M.DateField(verbose_name=u'實際_工程_(設計規劃)決標', null=True)
    eng_plan_final_memo = M.CharField(verbose_name=u'實際_工程_(設計規劃)決標/備註', max_length=256, null=True)
    sch_eng_plan_selection_meeting = M.DateField(verbose_name=u'預計_工程_(設計規劃)公開評選會議(限制性招標)', null=True)
    act_eng_plan_selection_meeting = M.DateField(verbose_name=u'實際_工程_(設計規劃)公開評選會議(限制性招標)', null=True)
    eng_plan_selection_meeting_memo = M.CharField(verbose_name=u'工程_(設計規劃)公開評選會議(限制性招標)/備註', max_length=256, null=True)
    sch_eng_plan_promise = M.DateField(verbose_name=u'預計_工程_(設計規劃)定約', null=True)
    act_eng_plan_promise = M.DateField(verbose_name=u'實際_工程_(設計規劃)定約', null=True)
    eng_plan_promise_memo = M.CharField(verbose_name=u'工程_(設計規劃)定約/備註', max_length=256, null=True)
    sch_eng_plan_basic_design = M.DateField(verbose_name=u'預計_工程_(設計規劃)基本設計', null=True)
    act_eng_plan_basic_design = M.DateField(verbose_name=u'實際_工程_(設計規劃)基本設計', null=True)
    eng_plan_basic_design_memo = M.CharField(verbose_name=u'工程_(設計規劃)基本設計/備註', max_length=256, null=True)
    sch_eng_plan_detail_design = M.DateField(verbose_name=u'預計_工程_(設計規劃)提送預算書圖', null=True)
    act_eng_plan_detail_design = M.DateField(verbose_name=u'實際_工程_(設計規劃)提送預算書圖', null=True)
    eng_plan_detail_design_memo = M.CharField(verbose_name=u'工程_(設計規劃)提送預算書圖/備註', max_length=256, null=True)
    sch_eng_plan_acceptance = M.DateField(verbose_name=u'預計_工程_(設計規劃)驗收', null=True)
    act_eng_plan_acceptance = M.DateField(verbose_name=u'實際_工程_(設計規劃)驗收', null=True)
    eng_plan_acceptance_memo = M.CharField(verbose_name=u'工程_(設計規劃)驗收/備註', max_length=256, null=True)
    sch_eng_plan_acceptance_closed = M.DateField(verbose_name=u'預計_工程_(設計規劃)結案', null=True)
    act_eng_plan_acceptance_closed = M.DateField(verbose_name=u'實際_工程_(設計規劃)結案', null=True)
    eng_plan_acceptance_closed_memo = M.CharField(verbose_name=u'工程_(設計規劃)結案/備註', max_length=256, null=True)
    
    sch_eng_plan_final_deadline = M.DateField(verbose_name=u'預計_核定函勞務決標期限', null=True)
    act_eng_plan_final_deadline = M.DateField(verbose_name=u'實際_核定函勞務決標期限', null=True)
    eng_plan_final_deadline_memo = M.CharField(verbose_name=u'核定函勞務決標期限/備註', max_length=256, null=True)

    sch_eng_do_agree_plan = M.DateField(verbose_name=u'預計_工程_(工程施做)同意計畫', null=True)
    act_eng_do_agree_plan = M.DateField(verbose_name=u'實際_工程_(工程施做)同意計畫', null=True)
    eng_do_agree_plan_memo = M.CharField(verbose_name=u'實際_工程_(工程施做)同意計畫/備註', max_length=256, null=True)
    sch_eng_do_approved_plan = M.DateField(verbose_name=u'預計_工程_(工程施做)核定計畫', null=True)
    act_eng_do_approved_plan = M.DateField(verbose_name=u'實際_工程_(工程施做)核定計畫', null=True)
    eng_do_approved_plan_memo = M.CharField(verbose_name=u'工程_(工程施做)核定計畫/備註', max_length=256, null=True)
    sch_eng_do_signed_tender = M.DateField(verbose_name=u'預計_工程_(工程施做)簽辦招標', null=True)
    act_eng_do_signed_tender = M.DateField(verbose_name=u'實際_工程_(工程施做)簽辦招標', null=True)
    eng_do_signed_tender_memo = M.CharField(verbose_name=u'工程_(工程施做)簽辦招標/備註', max_length=256, null=True)
    sch_eng_do_announcement_tender = M.DateField(verbose_name=u'預計_工程_(工程施做)公告上網', null=True)
    act_eng_do_announcement_tender = M.DateField(verbose_name=u'實際_工程_(工程施做)公告上網', null=True)
    eng_do_announcement_tender_memo = M.CharField(verbose_name=u'工程_(工程施做)公告上網/備註', max_length=256, null=True)
    sch_eng_do_final = M.DateField(verbose_name=u'預計_工程_(工程施做)決標', null=True)
    act_eng_do_final = M.DateField(verbose_name=u'實際_工程_(工程施做)決標', null=True)
    eng_do_final_memo = M.CharField(verbose_name=u'實際_工程_(工程施做)決標/備註', max_length=256, null=True)
    sch_eng_do_promise = M.DateField(verbose_name=u'預計_工程_(工程施做)定約', null=True)
    act_eng_do_promise = M.DateField(verbose_name=u'實際_工程_(工程施做)定約', null=True)
    eng_do_promise_memo = M.CharField(verbose_name=u'工程_(工程施做)定約/備註', max_length=256, null=True)
    sch_eng_do_start = M.DateField(verbose_name=u'預計_工程_(工程施做)開工', null=True)
    act_eng_do_start = M.DateField(verbose_name=u'實際_工程_(工程施做)開工', null=True)
    eng_do_start_memo = M.CharField(verbose_name=u'工程_(工程施做)開工/備註', max_length=256, null=True)
    sch_eng_do_completion = M.DateField(verbose_name=u'預計_工程_(工程施做)完工', null=True)
    act_eng_do_completion = M.DateField(verbose_name=u'實際_工程_(工程施做)完工', null=True)
    eng_do_completion_memo = M.CharField(verbose_name=u'工程_(工程施做)完工/備註', max_length=256, null=True)
    sch_eng_do_acceptance = M.DateField(verbose_name=u'預計_工程_(工程施做)驗收', null=True)
    act_eng_do_acceptance = M.DateField(verbose_name=u'實際_工程_(工程施做)驗收', null=True)
    eng_do_acceptance_memo = M.CharField(verbose_name=u'工程_(工程施做)驗收/備註', max_length=256, null=True)
    sch_eng_do_closed = M.DateField(verbose_name=u'預計_工程_(工程施做)結案', null=True)
    act_eng_do_closed = M.DateField(verbose_name=u'實際_工程_(工程施做)結案', null=True)
    eng_do_closed_memo = M.CharField(verbose_name=u'工程_(工程施做)結案/備註', max_length=256, null=True)

    stat_wrk_per = M.NullBooleanField(verbose_name=u'勞務履約中', null=True)
    stat_wrk_per_date = M.DateField(verbose_name=u'勞務履約中_日期', null=True)
    stat_wrk_per_memo = M.CharField(verbose_name=u'勞務履約中_備註', max_length=256, null=True)
    stat_file_prep = M.NullBooleanField(verbose_name=u'文件準備中', null=True)
    stat_file_prep_date = M.DateField(verbose_name=u'文件準備中_日期', null=True)
    stat_file_prep_memo = M.CharField(verbose_name=u'文件準備中_備註', max_length=256, null=True)
    stat_file_prvw = M.NullBooleanField(verbose_name=u'文件預覽中', null=True)
    stat_file_prvw_date = M.DateField(verbose_name=u'文件預覽中_日期', null=True)
    stat_file_prvw_memo = M.CharField(verbose_name=u'文件預覽中_備註', max_length=256, null=True)
    stat_file_oln = M.NullBooleanField(verbose_name=u'文件公告中', null=True)
    stat_file_oln_date = M.DateField(verbose_name=u'文件公告中_日期', null=True)
    stat_file_oln_memo = M.CharField(verbose_name=u'文件公告中_備註', max_length=256, null=True)
    stat_res_ctr = M.NullBooleanField(verbose_name=u'決標_訂約中', null=True)
    stat_res_ctr_date = M.DateField(verbose_name=u'決標_訂約中_日期', null=True)
    stat_res_ctr_memo = M.CharField(verbose_name=u'決標_訂約中_備註', max_length=256, null=True)
    stat_cnst = M.NullBooleanField(verbose_name=u'施工中', null=True)
    stat_cnst_date = M.DateField(verbose_name=u'施工中_日期', null=True)
    stat_cnst_memo = M.CharField(verbose_name=u'施工中_備註', max_length=256, null=True)
    stat_stop = M.NullBooleanField(verbose_name=u'停工中', null=True)
    stat_stop_date = M.DateField(verbose_name=u'停工中_日期', null=True)
    stat_stop_memo = M.CharField(verbose_name=u'停工中_備註', max_length=256, null=True)
    stat_cnfl = M.NullBooleanField(verbose_name=u'履約爭議中', null=True)
    stat_cnfl_date = M.DateField(verbose_name=u'履約爭議中_日期', null=True)
    stat_cnfl_memo = M.CharField(verbose_name=u'履約爭議中_備註', max_length=256, null=True)
    stat_term_ing = M.NullBooleanField(verbose_name=u'解約中', null=True)
    stat_term_ing_date = M.DateField(verbose_name=u'解約中_日期', null=True)
    stat_term_ing_memo = M.CharField(verbose_name=u'解約中_備註', max_length=256, null=True)
    stat_cmplt = M.NullBooleanField(verbose_name=u'已申報竣工', null=True)
    stat_cmplt_date = M.DateField(verbose_name=u'已申報竣工_日期', null=True)
    stat_cmplt_memo = M.CharField(verbose_name=u'已申報竣工_備註', max_length=256, null=True)
    stat_acpt = M.NullBooleanField(verbose_name=u'驗收中', null=True)
    stat_acpt_date = M.DateField(verbose_name=u'驗收中_日期', null=True)
    stat_acpt_memo = M.CharField(verbose_name=u'驗收中_備註', max_length=256, null=True)
    stat_pay = M.NullBooleanField(verbose_name=u'結算付款中', null=True)
    stat_pay_date = M.DateField(verbose_name=u'結算付款中_日期', null=True)
    stat_pay_memo = M.CharField(verbose_name=u'結算付款中_備註', max_length=256, null=True)
    stat_closd = M.NullBooleanField(verbose_name=u'已結案', null=True)
    stat_closd_date = M.DateField(verbose_name=u'已結案_日期', null=True)
    stat_closd_memo = M.CharField(verbose_name=u'已結案_備註', max_length=256, null=True)
    stat_term_ed = M.NullBooleanField(verbose_name=u'已解約', null=True)
    stat_term_ed_date = M.DateField(verbose_name=u'已解約_日期', null=True)
    stat_term_ed_memo = M.CharField(verbose_name=u'已解約_備註', max_length=256, null=True)
    stat_oth = M.NullBooleanField(verbose_name=u'其他', null=True)
    stat_oth_date = M.DateField(verbose_name=u'其他_日期', null=True)
    stat_oth_memo = M.CharField(verbose_name=u'其他_備註', max_length=256, null=True)
    stat_illus_memo = M.CharField(verbose_name=u'辦理情形備註', max_length=256, null=True)
    stat_stop_reason_memo = M.CharField(verbose_name=u'停工或落後原因', max_length=256, null=True)
    stat_solution_memo = M.CharField(verbose_name=u'解決對策', max_length=256, null=True)
    


    def get_vouch_date(self):
        #取得核定日期
        if self.project.purchase_type.value == u'一般勞務':
            if self.act_ser_approved_plan and self.act_ser_approved_plan != '':
                return self.act_ser_approved_plan
            else:
                return self.sch_ser_approved_plan
        else:
            if self.act_eng_plan_approved_plan and self.act_eng_plan_approved_plan != '':
                return self.act_eng_plan_approved_plan
            else:
                return self.sch_eng_plan_approved_plan



class CountyChaseProjectOneToMany(M.Model):
    countychasetime = M.ForeignKey(CountyChaseTime, verbose_name=u'追蹤日期')
    project = M.ForeignKey(Project, verbose_name=u'追蹤工程案')
    check = M.BooleanField(verbose_name=u'確認填寫完成', default=False)
    complete = M.BooleanField(verbose_name=u'是否填寫完成', default=False)

    memo = M.CharField(verbose_name=u'目前辦理情形(進度)', max_length=2048, default=u"")
    behind_memo = M.CharField(verbose_name=u'落後10%以上、履約爭議或停工等請填原因及解決對策', max_length=2048, default=u"")
    self_memo = M.CharField(verbose_name=u'管考建議(由本署填寫)', max_length=2048, default=u"")
    schedul_progress_percent = M.DecimalField(verbose_name=u'預計進度百分比(%)', default='0', max_digits=16 , decimal_places=2)
    actual_progress_percent = M.DecimalField(verbose_name=u'實際進度百分比(%)', default='0', max_digits=16 , decimal_places=2)
    expected_to_end_percent = M.DecimalField(verbose_name=u'預計至年底執行率百分比(%)', default='0', max_digits=16 , decimal_places=2)
    update_time = M.DateField(verbose_name=u'最後更新日期', null=True)

    self_payout = M.DecimalField(verbose_name=u'本署實支數(元)(G)', default='0' , max_digits=16 , decimal_places=3)
    local_payout = M.DecimalField(verbose_name=u'地方實支數(元)(G)', default='0' , max_digits=16 , decimal_places=3)
    self_unpay = M.DecimalField(verbose_name=u'本署應付未付數(元)(補助款)(H)=(E)*(F)-(G)', default='0', max_digits=16 , decimal_places=3)
    local_unpay = M.DecimalField(verbose_name=u'地方應付未付數(元)(補助款)(H)=(E)*(F)-(G)', default='0', max_digits=16 , decimal_places=3)
    surplus = M.DecimalField(verbose_name=u'結餘數', default='0' , max_digits=16 , decimal_places=3)

    # 廢除欄位，改為自動計算
    # self_surplus = M.DecimalField(verbose_name=u'本署賸餘款(元)', null=True , max_digits=16 , decimal_places=3)
    # local_surplus = M.DecimalField(verbose_name=u'地方賸餘款(元)', null=True , max_digits=16 , decimal_places=3)

    def save(self, *args, **kw):
        '''
            再創造的時候
            取得OneByOne的追蹤資料，若沒有，則直接創一個
            若有且check == True
            則這次的追蹤直接顯示填寫完畢，並複製上次的填寫內容
        '''
        try:
            CountyChaseProjectOneToMany.objects.get(countychasetime=self.countychasetime, project=self.project)
        except:
            CountyChaseProjectOneByOne.objects.get_or_create(project=self.project)
            if CountyChaseProjectOneByOne.objects.get(project=self.project).check == True:
                all_chase_data = CountyChaseProjectOneToMany.objects.filter(project=self.project).order_by('-countychasetime__chase_date')
                if all_chase_data:
                    last_chase = all_chase_data[0]
                    self.schedul_progress_percent = last_chase.schedul_progress_percent
                    self.actual_progress_percent = last_chase.actual_progress_percent
                    self.expected_to_end_percent = last_chase.expected_to_end_percent
                    self.self_payout = last_chase.self_payout
                    self.local_payout = last_chase.local_payout
                    self.self_unpay = last_chase.self_unpay
                    self.local_unpay = last_chase.local_unpay
                    self.memo = last_chase.memo
                    self.update_time = last_chase.update_time
                self.check = True
                self.complete = True
        super(CountyChaseProjectOneToMany, self).save(*args, **kw)

    def rSelf_Surplus(self):
        '''
        若本署負擔 = 本署負擔上限金額(元)，則賸餘款(X) = 0
        否則本署賸餘款(X) = [ 計畫經費(I) - 發包及其他費用(Q) ] * 本署負擔比例(註)，若發包及其他費用(Q)無值，則本署賸餘款(X) = 0
        '''
        if not self.project.subsidy_limit or self.getFund().rSelfLoad() == float(self.project.subsidy_limit):
            return 0
        budget = list(self.getFund().budget_set.all().order_by('year'))[0]#採用第一筆
        moneyA = budget.rPlanMoney()#1.採用計畫經費
        moneyB = self.project.rTotalMoneyInProject()#1.採用工程結算金額 2.採用工程契約金額
        if not moneyB: return 0
        else: return (float(moneyA) - float(moneyB)) * float(self.project.allot_rate or 100.0)*0.01

    def getFirstBudget(self):
        '''
            讀取Budget第一年度
        '''
        return self.project.fund_set.get().budget_set.all().order_by('year')[0]

    def getFund(self):
        '''
            讀取Fund
        '''
        return self.project.fund_set.get()

    def getSelfExecutionMoney(self):
        '''
            本署經費執行數 = 本署實支數 + 本署應付未付數 + 本署賸餘款
        '''
        return float(self.self_payout or 0.0) + float(self.self_unpay or 0.0) + float(self.rSelf_Surplus())

    def getExecutionRate(self):
        '''
            執行率 = 本署經費執行數 / 累計分配數 * 100 %
        '''
        if self.getFund().rTotalAllocation() == 0:
            return 0
        else:
            return int((self.getSelfExecutionMoney() / (self.getFund().rTotalAllocation())) * 10000.)/100.

    def getReachedRate(self):
        '''
            達成率 = 本署經費執行數 / 修正核定數(無值取核定數) * 100 %
            若修正核定數無值，以核定數取代
        '''
        budget = self.getFirstBudget()
        a = budget.capital_ratify_revision
        if not a or a == 0: a = budget.capital_ratify_budget
        if not a or a == 0: return 0
        a = float(str(a))
        return int((self.getSelfExecutionMoney() / a) * 10000.)/100.


    #以下還沒用到------------------------------
    def getSelfExecutionMoney(self):
        #本署經費執行數（H）＝(Iself_payout+Lself_unpay+Fself_surplus)
        return float(self.self_payout or 0.0) + float(self.self_unpay or 0.0) + float(self.rSelf_Surplus())

    def getLastBudget(self):
        #最後一年度預算
        return list(self.project.fund_set.get().budget_set.all().order_by('year'))[-1]
        
    def rLocal_Surplus(self):
        #計算 地方賸餘款(元)
        #(Y) = (核定數L) - (發包及其他費用Q) - (本署賸餘款X)。
        budget = list(self.getFund().budget_set.all().order_by('year'))[0]#採用第一筆
        if budget.capital_ratify_revision and budget.capital_ratify_revision != 0:#1.採用修正核定數
            moneyA = budget.capital_ratify_revision
        else:#2.採用核定數
            moneyA = budget.capital_ratify_budget or 0
        moneyB = self.project.rTotalMoneyInProject()#1.採用工程結算金額 2.採用工程契約金額
        return float(moneyA) - float(moneyB) - float(self.rSelf_Surplus())



class CountyChaseProjectOneToManyPayout(M.Model):
    #追蹤紀錄實支數整理
    chase = M.ForeignKey(CountyChaseProjectOneToMany, verbose_name=u'追蹤紀錄')
    budget = M.ForeignKey(Budget, verbose_name=u'經費來源')
    self_payout = M.DecimalField(verbose_name=u'本署實支數(元)(G)', default='0' , max_digits=16 , decimal_places=3)
    
    #目前沒用 保留欄位
    self_unpay = M.DecimalField(verbose_name=u'本署應付未付數(元)(補助款)(H)=(E)*(F)-(G)', default='0', max_digits=16 , decimal_places=3)
    local_payout = M.DecimalField(verbose_name=u'地方實支數(元)(G)', default='0' , max_digits=16 , decimal_places=3)
    local_unpay = M.DecimalField(verbose_name=u'地方應付未付數(元)(補助款)(H)=(E)*(F)-(G)', default='0', max_digits=16 , decimal_places=3)
    surplus = M.DecimalField(verbose_name=u'結餘數', default='0' , max_digits=16 , decimal_places=3)



class UnitManager(M.Model):
    unit = M.ForeignKey(Unit, verbose_name='單位', related_name="unitmanager_unit")
    name = M.CharField(verbose_name=u'姓名', max_length=64, null=True)
    phone = M.CharField(verbose_name=u'連絡電話', max_length=64, null=True)
    email = M.CharField(verbose_name=u'Email', max_length=64, null=True)



class Allocation(M.Model):
    project = M.ForeignKey(Project, verbose_name='工程案')
    date = M.DateField(verbose_name=u'日期', null=True)
    allocation = M.DecimalField(verbose_name='分配數', default=0 , max_digits=16 , decimal_places=3) #單位：元
    memo = M.CharField(verbose_name=u'備註', max_length=256, null=True)


class Project_Secret_Memo(M.Model):
    #這是給丞曜秘密使用的備註區，用來記錄他聯絡的情形
    project = M.ForeignKey(Project, verbose_name='工程案')
    date = M.DateField(verbose_name=u'日期', null=True)
    memo_1 = M.CharField(verbose_name=u'備註1', max_length=2048, null=True)
    memo_2 = M.CharField(verbose_name=u'備註2', max_length=2048, null=True)
    memo_3 = M.CharField(verbose_name=u'備註3', max_length=2048, null=True)


def _DOCUMENT_UPLOAD_TO(instance, filename):
    return os.path.join('apps', 'project', 'media', 'project', 'document_file', str(instance.project.id), str(instance.id)+'.'+instance.ext)

class DocumentFile(M.Model):
    upload_user = M.ForeignKey(User, verbose_name='上傳者')
    project = M.ForeignKey(Project, verbose_name='工程案')
    no = M.CharField(verbose_name='文號', max_length=256, null=True)
    ext = M.CharField(verbose_name='副檔名', max_length=10, null=True)
    date = M.DateField(verbose_name='發文日期')
    file = M.FileField(upload_to=_DOCUMENT_UPLOAD_TO, null=True)
    memo = M.CharField(verbose_name='備註說明', null=True, max_length=2048)

    def rUrl(self):
        return self.file.name.split('apps/project/')[-1]

    def calSize(self):
        if self.file:
            return calsize(self.file.size)
        else:
            return calsize(0)


class EmailList(M.Model):
    name = M.CharField(verbose_name=u'姓名', max_length=64, null=True)
    place = M.ForeignKey(Place, verbose_name='縣市', null=True)
    departments = M.CharField(verbose_name=u'科別', max_length=64, null=True)
    title = M.CharField(verbose_name=u'職稱', max_length=64, null=True)
    tel = M.CharField(verbose_name=u'電話', max_length=64, null=True)
    phone = M.CharField(verbose_name=u'電話', max_length=64, null=True)
    fax = M.CharField(verbose_name=u'傳真', max_length=64, null=True)
    email = M.TextField(verbose_name='署內連絡email', null=True)
    need_email= M.BooleanField(default=False)
    memo = M.TextField(verbose_name=u'備註說明', null=True)

    def __unicode__(self):
        return self.name

    def rJson(self):
        return self.__dict__



class ManageMoney(M.Model):
    '''工程管理費'''
    year = M.IntegerField(verbose_name='年度')
    date = M.DateField(verbose_name=u'支出日期', null=True)
    name = M.CharField(verbose_name=u'支出名稱', max_length=256, null=True)
    is_remain = M.BooleanField(default=False)
    is_commission =  M.BooleanField(default=False)

    def get_money(self):
        return sum([i.money for i in self.projectmanagemoney_set.all()])



class ProjectManageMoney(M.Model):
    '''詳細工程管理費'''
    managemoney = M.ForeignKey(ManageMoney, verbose_name='工程管理費')
    project = M.ForeignKey(Project, verbose_name='工程案')
    money = M.DecimalField(verbose_name='實支數', default=0 , max_digits=16 , decimal_places=3) #單位：元



class ManageMoneyRemain(M.Model):
    '''工程管理費保留款'''
    year = M.IntegerField(verbose_name='年度')
    money = M.DecimalField(verbose_name='保留金額', default=0 , max_digits=16 , decimal_places=3) #單位：元


class SystemInformation(M.Model):
    '''
        系統公告區
    '''
    start_date = M.DateField(verbose_name='事件開始日期', null=True)
    user = M.ForeignKey(User, verbose_name=u'發佈者')
    on_login_page = M.BooleanField(verbose_name=u'是否要顯示再登入頁面', default=False)
    title = M.TextField(verbose_name=u'發佈訊息短內容', null=True)
    memo = M.TextField(verbose_name=u'發佈訊息長內容', null=True)



def _UPLOAD_TO_SYSTEM_INFORMATION(instance, filename):
    try:
        ext = filename.split('.')[-1]
    except:
        ext = 'zip'
    return os.path.join('system_information', str(TODAY()), '%s.%s' % (instance.id, ext))


class SystemInformationFile(M.Model):
    '''系統公告的附加檔案區'''
    systeminformation = M.ForeignKey(SystemInformation, verbose_name=u'系統公告', null=True)
    name = M.CharField(verbose_name='檔案名', max_length=256, null=True, default='')
    file = M.FileField(upload_to=_UPLOAD_TO_SYSTEM_INFORMATION, null=True)

    def rExt(self):
        try:
            return self.file.name.split('.')[-1]
        except:
            return 'zip'
