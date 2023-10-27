#!-*- coding:utf8 -*-
from django.conf.urls import include, url
from tastypie.api import Api
from project.resource import __enable__
from project import views as project_views


api = Api(api_name='v2')
resource = __import__('project.resource', fromlist=['resource'])
for name in __enable__:
    r = getattr(resource, name)
    api.register(r())


urlpatterns = [
    url(r'api/', include(api.urls)),
    url(r'^default_project/$', project_views.default_project, name='default_project'), # 我的追蹤工程
    url(r'^plan_list/$', project_views.plan_list, name='plan_list'), # 計畫列表
    url(r'^plan_list/get_plan_info/$', project_views.get_plan_info, name='get_plan_info'), # 計畫列表-取得計畫資訊
    url(r'^plan_list/create_plan/$', project_views.create_plan, name='create_plan'), # 計畫列表-新增計畫
    url(r'^plan_list/make_sort_table/$', project_views.make_sort_table, name='make_sort_table'), # 計畫列表-製造排序選擇表格
    url(r'^search_project/$', project_views.search_project, name='search_project'), # 搜尋工程
    url(r'^recycled_project/$', project_views.recycled_project, name='recycled_project'), # 工程回收桶
    url(r'^project_profile/(?P<project_id>[0-9]+)/$', project_views.project_profile, name='project_profile'), # 工程基本資料
    url(r'^new_file_upload/$', project_views.new_file_upload, name='new_file_upload'), # 檔案上傳
    url(r'^create_project/$', project_views.create_project, name='create_project'), # 新增工程案
    url(r'^draft_project/$', project_views.draft_project, name='draft_project'), #草稿匣
    url(r'^draft_project_place/$', project_views.draft_project_place, name='draft_project_place`'), #草稿匣-縣市政府
    url(r'^draft_project_profile/(?P<draft_project_id>[0-9]+)/$', project_views.draft_project_profile, name='draft_project_profile'), # 草稿匣編輯
    url(r'^create_project_from_draft/$', project_views.create_project_from_draft, name='create_project_from_draft'), #新增工程案 從 草稿匣
    url(r'^chase/$', project_views.chase, name='chase'), #縣市進度追蹤
    url(r'^chase_table/$', project_views.chase_table, name='chase_table'), #縣市進度追蹤-追蹤表格

    url(r'^chase_select_project/$', project_views.chase_select_project, name='chase_select_project'), #縣市進度追蹤-選擇追蹤工程
    # url(r'^chase_complete/$', project_views.chase_complete, name='chase_complete'), #縣市進度追蹤-申請填寫完畢
    # url(r'^chase_close/$', project_views.chase_close, name='chase_close'), #縣市進度追蹤-申請結案
    url(r'^chase_print/$', project_views.chase_print, name='chase_print'), #縣市進度追蹤-列印報表
    url(r'^get_chart_data/$', project_views.get_chart_data, name='get_chart_data'),
    url(r'^chase_connecter/$', project_views.chase_connecter, name='chase_connecter'), #縣市進度追蹤-各單位主管
    url(r'^chase_make_excel/$', project_views.chase_make_excel, name='chase_make_excel'), #縣市進度追蹤-製造Excel報表
    url(r'^print_custom_report/$', project_views.print_custom_report, name='print_custom_report'), #列印自定義報表
    url(r'^set_manage_money/$', project_views.set_manage_money, name='set_manage_money'), #工程管理費設定頁面
    url(r'^set_manage_money_remain/$', project_views.set_manage_money_remain, name='set_manage_money_remain'), #工程管理費保留款設定頁面
    url(r'^get_manage_info/$', project_views.get_manage_info, name='get_manage_info'), #讀取工程管理費資訊
    url(r'^get_project_for_manage_money/$', project_views.get_project_for_manage_money, name='get_project_for_manage_money'), #讀取待選工程管理費工程列表
    url(r'^project_for_manage_money/$', project_views.project_for_manage_money, name='project_for_manage_money'), #讀取工程管理費工程列表
    url(r'^project_for_manage_money_excel/$', project_views.project_for_manage_money_excel, name='project_for_manage_money_excel'), #匯出工程管理費工程列表Excel
    #new 委辦工程管理費
    url(r'^set_manage_money_commission/$', project_views.set_manage_money_commission, name='set_manage_money_commission'), #工程管理費設定頁面
    url(r'^set_manage_money_commission_remain/$', project_views.set_manage_money_commission_remain, name='set_manage_money_commission_remain'), #工程管理費保留款設定頁面
    url(r'^get_manage_commission_info/$', project_views.get_manage_commission_info, name='get_manage_commission_info'), #讀取工程管理費資訊
    url(r'^get_project_for_manage_money_commission/$', project_views.get_project_for_manage_money_commission, name='get_project_for_manage_money_commission'), #讀取待選工程管理費工程列表
    url(r'^project_for_manage_money_commission/$', project_views.project_for_manage_money_commission, name='project_for_manage_money_commission'), #讀取工程管理費工程列表
    url(r'^project_for_manage_money_commission_excel/$', project_views.project_for_manage_money_commission_excel, name='project_for_manage_money_commission_excel'), #匯出工程管理費工程列表Excel
    
    url(r'^renew_bid_money_statistic_table/$', project_views.renew_bid_money_statistic_table, name='renew_bid_money_statistic_table'), #讀取標案金額使用狀況表
    url(r'^add_projectbidmoneyversion/$', project_views.add_projectbidmoneyversion, name='add_projectbidmoneyversion'), #新增金額資訊版本
    url(r'^get_projectbidmoneyversion/$', project_views.get_projectbidmoneyversion, name='get_projectbidmoneyversion'), #取得金額資訊版本列表
    url(r'^data_connect_for_aerc$', project_views.dispatcher_handler, name='dispatcher_handler'),

    url(r'^project_deleter_use/$', project_views.project_deleter_use, name='project_deleter_use'), # 工程回收桶用的生成認領碼
    url(r'^manage_money/$', project_views.manage_money, name='manage_money'), #工程管理費工程頁面

    url(r'^control_form/$', project_views.control_form, name='control_form'), #漁港管控表
    url(r'^control_form_online_print/(?P<year>.+)/(?P<budget_type>.+)/(?P<top_plan_id>.+)/$', project_views.control_form_online_print, name='control_form_online_print'), #漁港管控表-線上列印
    url(r'^control_form_make_excel/(?P<year>.+)/(?P<budget_type>.+)/(?P<top_plan_id>.+)/$', project_views.control_form_make_excel, name='control_form_make_excel'), #漁港管控表-匯出excel
    url(r'^get_work_no_info/$', project_views.get_work_no_info, name='get_work_no_info'), #取得計畫編號
    url(r'^get_control_form_info/$', project_views.get_control_form_info, name='get_control_form_info'), #讀取漁港管控表資訊

    url(r'^port_engineering_make_excel/(?P<year>.+)/$', project_views.port_engineering_make_excel, name='port_engineering_make_excel'), #匯出漁港工程大表excel
    url(r'^port_engineering_download_excel/(?P<year>.+)/(?P<month>.+)/$', project_views.port_engineering_download_excel, name='port_engineering_download_excel'), #下載漁港工程大表excel
    url(r'^plan_type_edit/$', project_views.plan_type_edit, name='plan_type_edit'), # 編輯計畫類別
    url(r'^create_plan_type/(?P<value>.+)/$', project_views.create_plan_type, name='create_plan_type'), # 新增類別
    url(r'^delete_plan_type/(?P<id>.+)/$', project_views.delete_plan_type, name='delete_plan_type'), # 刪除類別
    url(r'^plan_query/(?P<plan_id>.+)/(?P<year>.+)/$', project_views.plan_query, name='plan_query'), # query

    # url(r'^copy_money/(?P<budget_id>.+)/$', project_views.copy_money, name='copy_money'), #備份金額資訊
    url(r'^add_manage_money/$', project_views.add_manage_money, name='add_manage_money'), #新增工程管理費


]





# urlpatterns = patterns('project.views',

#     #以下舊分頁
#     (r'^readjson/$', 'readJson', {'right_type_value': u'觀看管考系統資料'}),
#     (r'^ajax/$', 'rJSON', {'right_type_value': u'Ajax Request'}),
#     # (r'^replan_old/$', 'ReadAndEditPlan_Old', {'right_type_value': u'觀看管考系統資料'}),
#     (r'^replan/(?P<plan_id>.+)/$', 'ReadAndEditPlan', {'right_type_value': u'觀看管考系統資料'}),
#     (r'^replanbudget/(?P<layer>.+)/$', 'ReadAndEditPlanBudget', {'right_type_value': u'觀看管考系統資料'}),
#     # (r'^rebudget/$', 'ReadAndEditBudget', {'right_type_value': u'觀看管考系統資料'}),
#     # (r'^rebudget/advanced/$', 'advancedReadAndEditBudget', {'right_type_value': u'觀看管考系統資料'}),
#     (r'^search/$', 'searchProject', {'right_type_value': u'觀看管考系統資料'}),
#     (r'^show_default_detail/$', 'readDefaultDetail', {'right_type_value': u'觀看管考系統資料'}),
#     (r'^search/advanced/$', 'searchAdvancedProject', {'right_type_value': u'觀看管考系統資料'}),
#     (r'^addproject/$', 'addProject', {'right_type_value': u'新增工程案'}),
#     (r'^addproject/(?P<dictionary_str>.+)/$', 'addProject', {'right_type_value': u'新增工程案'}),
#     (r'^draft_project/(?P<draft_type>[a-z]+)/$', 'reDraftProject', {'right_type_value': u'新增工程案'}),
#     (r'^addproject_from_draft/(?P<project_id>[0-9]+)/$', 'addProjectFromDraft', {'right_type_value': u'新增工程案'}),
#     (r'^reserve/(?P<project_id>[0-9]+)/$', 'reserveProject', {'right_type_value': u'填寫管考系統資料'}),
#     (r'^county_chase/$', 'ReadAndEditCountyChase', {'right_type_value': u'使用縣市追蹤系統'}),
#     (r'^epcounty_chase/$', 'ReadAndPrintCountyChase', {'right_type_value': u'使用縣市追蹤系統'}),
#     (r'^countychasesetcompletecheck/$', 'CountyChaseSetCompleteCheck', {'right_type_value': u'使用縣市追蹤系統'}),
#     (r'^countychasesetclosecheck/$', 'CountyChaseSetCloseCheck', {'right_type_value': u'使用縣市追蹤系統'}),
#     (r'^all_chase_info/(?P<project_id>[0-9]+)/$', 'AllChaseInfo', {'right_type_value': u'使用縣市追蹤系統'}),
    
#     # (r'^data_connect_project_for_aerc/$', 'data_connect_project_for_aerc'),
#     # (r'^data_connect_plan_for_aerc/$', 'data_connect_plan_for_aerc'),
#     (r'^photo/(?P<project_id>[0-9]+)/$', 'uploadPhoto', {'right_type_value': u'觀看管考系統資料'}),
#     (r'^edit_project_list_budget/(?P<plan_id>[0-9]+)/(?P<year>[0-9]+)/(?P<sub_plan>[0-9]+)/(?P<budget_sub_type>[0-9]+)/(?P<undertake_type>[0-9]+)/$', 'editProjectListBudget', {'right_type_value': u'填寫管考系統資料'}),
# #<{------ 固定一段時間同步一次 ------}>
#     (r'^sync_accounting_fundrecord/$', 'syncTotalAccoutingData'),
#     (r'^sync_pcc_fundrecord/$', 'syncTotalPCCFundRecord'),
#     # (r'^sync100money/$', 'sync100money'),
# #<{------ 重新整理 ------}>
#     (r'^reproject/(?P<project_id>[0-9]+)/$', 'guideProjectURL', {'right_type_value': u'觀看管考系統資料'}),
#     (r'^basic/(?P<project_id>[0-9]+)/$', 'eProjectBasic', {'right_type_value': u'觀看管考系統資料'}),
#     (r'^fund/(?P<project_id>[0-9]+)/$', 'eProjectFund', {'right_type_value': u'觀看管考系統資料'}),
#     (r'^progress/(?P<project_id>[0-9]+)/$', 'eProjectProgress', {'right_type_value': u'觀看管考系統資料'}),
#     (r'^convertHTMLToFile/$', 'convertHTMLToFile', {'right_type_value': u'觀看管考系統資料'}),
#     (r'^upload_document_file/(?P<project_id>[0-9]+)/$', 'uploadDocumentFile', {'right_type_value': u'填寫管考系統資料'}),
# #<{------ 丞曜秘密系統 ------}>
#     (r'^uiyyeu/$', 'SecretGarden', {'right_type_value': u'觀看管考系統資料'}),
# #    (r'^reproject/(?P<project_id>[0-9]+)/$', 'ReadAndEditProject', {'right_type_value': u'觀看管考系統資料'}),
# #    (r'^remilestone/(?P<project_id>[0-9]+)/$', 'ProjectMilestone', {'right_type_value': u'觀看管考系統資料'}),
# #    (r'^rebidinfo/(?P<project_id>[0-9]+)/$', 'ProjectBidInfo', {'right_type_value': u'觀看管考系統資料'}),
#     # (r'^reappropriate/(?P<project_id>[0-9]+)/$', 'ProjectAppropriate', {'right_type_value': u'觀看管考系統資料'}),
#     (r'^makestatistics/(?P<dictionary_str>.+)/$', 'makeStatistics', {'right_type_value': u'觀看管考系統資料'}),
#     (r'^makestatisticsprojects/$', 'makeStatisticsProjects', {'right_type_value': u'觀看管考系統資料'}),
#     (r'^makecharts/(?P<chart_cache_name>.+)/$', 'makeCharts', {'right_type_value': u'觀看管考系統資料'}),
#     (r'^makeplot/(?P<chart_cache_name>.+)/$', 'makePlot', {'right_type_value': u'觀看管考系統資料'}),
#     (r'^makepie/(?P<chart_cache_name>.+)/$', 'makePie', {'right_type_value': u'觀看管考系統資料'}),
#     (r'^makebar/(?P<chart_cache_name>.+)/$', 'makeBar', {'right_type_value': u'觀看管考系統資料'}),
#     # (r'^makedownloadfile/$', 'makeDownloadFile', {'right_type_value': u'觀看管考系統資料'}),
#     # (r'^makedownloadfile/(?P<type>.+)/$', 'makeDownloadFileByType', {'right_type_value': u'觀看管考系統資料'}),
#     (r'^recover/$', 'recoverProject', {'right_type_value': u'刪除管考工程案'}),
#     (r'^makeserial/$', 'makeProjectSerial', {'right_type_value': u'刪除管考工程案'}),
#     (r'^export_custom_report/(?P<export_custom_report_id>[0-9]+)/$', 'exportCustomReport', {'right_type_value': u'觀看管考系統資料'}),
#     (r'^export_custom_report/(?P<export_type>csv)/(?P<export_custom_report_id>[0-9]+).xls$', 'exportCustomReport', {'right_type_value': u'觀看管考系統資料'}),
#     (r'^sync_chase_data/$', 'syncChaseData'),
# )
