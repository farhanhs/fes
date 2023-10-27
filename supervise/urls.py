#!-*- coding:utf8 -*-
from django.conf.urls import include, url
from tastypie.api import Api
from supervise.resource import __enable__
from supervise import views as supervise_views


api = Api(api_name='v2')
resource = __import__('supervise.resource', fromlist=['resource'])
for name in __enable__:
    r = getattr(resource, name)
    api.register(r())


urlpatterns = [
    url(r'api/', include(api.urls)),
    url(r'^search/$', supervise_views.search, name='search'), #查詢督導案
    url(r'^search_unit/$', supervise_views.search_unit, name='search_unit'), #查詢廠商統計
    url(r'^statistics/(?P<table_id>[0-9]+)/(?P<date_from>.+)/(?P<date_to>.+)/$', supervise_views.statistics, name='statistics'), #統計表格
    url(r'^statistics_chart/$', supervise_views.statistics_chart, name='statistics_chart'), #統計圖表
    url(r'^statistics_chart_a/$', supervise_views.statistics_chart_a, name='statistics_chart_a'), #統計圖表_a
    url(r'^get_chart_data/$', supervise_views.get_chart_data, name='get_chart_data'), #取得統計圖表數據
    url(r'^statistics_only_chart/$', supervise_views.statistics_only_chart, name='statistics_only_chart'), #統計圖表頁面
    
    url(r'^search_supervise_form_pcc/$', supervise_views.search_supervise_form_pcc, name='search_supervise_form_pcc'), #發起督導案
    url(r'^sync_fishery_project_from_pcc/$', supervise_views.sync_fishery_project_from_pcc, name='sync_fishery_project_from_pcc'), #從工程會擷取漁業署所屬所有工程案
    url(r'^project_profile/(?P<project_id>[0-9]+)/$', supervise_views.project_profile, name='project_profile'), #觀看督導案詳細資料
    url(r'^record/(?P<project_id>[0-9]+)/$', supervise_views.project_profile_record, name='project_profile_record'), #觀看督導案同步紀錄
    url(r'^error_imporve/(?P<project_id>[0-9]+)/$', supervise_views.error_imporve, name='error_imporve'), #缺失改善紀錄表
    url(r'^download_error_improve/(?P<project_id>[0-9]+)/$', supervise_views.download_error_improve, name='download_error_improve'), #下載改善WORD檔案
    url(r'^create_from_pcc/$', supervise_views.create_from_pcc, name='create_from_pcc'), #新增督導案
    url(r'^get_supervise_info_from_pcc/$', supervise_views.get_supervise_info_from_pcc, name='get_supervise_info_from_pcc'), #從工程會擷取督導資料
    url(r'^new_file_upload/$', supervise_views.new_file_upload, name='new_file_upload'), #缺失相片上傳
    url(r'^download_file/(?P<table_name>.+)/(?P<file_id>.+)/$', supervise_views.download_file, name='downliad_file'), # 下載檔案
    url(r'^creat/$', supervise_views.CreatSuperviseCase, name='CreatSuperviseCase'), # 自己新增督導案頁面
    url(r'^create_by_self/$', supervise_views.create_by_self, name='create_by_self'), #自己新增督導案
    url(r'^edit_profile/(?P<project_id>[0-9]+)/$', supervise_views.edit_profile, name='edit_profile'), #編輯督導案內容
    url(r'^add_error_by_self/$', supervise_views.add_error_by_self, name='add_error_by_self'), #新增缺失
    url(r'^search_error/$', supervise_views.search_error, name='search_error'), #缺失搜尋小工具
    url(r'^get_image/(?P<table_name>.+)/(?P<field_name>.+)/(?P<is_thumb>.+)/(?P<row_id>.+)/$', supervise_views.get_image, name='get_image'),#讀取圖檔

    url(r'^export_case_excel/$', supervise_views.export_case_excel, name='export_case_excel'), #匯出督導紀錄EXCEL
    url(r'^export_pcc_project_excel/$', supervise_views.export_pcc_project_excel, name='export_pcc_project_excel'), #匯出工程會工程EXCEL 督導選案表
    url(r'^export_pcc_project_excel2/$', supervise_views.export_pcc_project_excel2, name='export_pcc_project_excel2'), #匯出工程會工程EXCEL 進度控管表

    url(r'^unit_error_sort/$', supervise_views.unit_error_sort, name='unit_error_sort'), #缺失搜尋小工具
    
    url(r'^pcc_settings/$', supervise_views.pcc_settings, name='pcc_settings'), #設定工程會同步帳密
]

# urlpatterns = patterns('supervise.views',
#     #轉移開始
#     url(r'^search/$', 'search', name='search'), #查詢督導案
#     url(r'^statistics/(?P<table_id>[0-9]+)/(?P<date_from>.+)/(?P<date_to>.+)/$', 'statistics', name='statistics'), #統計表格
#     url(r'^search_supervise_form_pcc/$', 'search_supervise_form_pcc', name='search_supervise_form_pcc'), #發起督導案
#     url(r'^sync_fishery_project_from_pcc/$', 'sync_fishery_project_from_pcc', name='sync_fishery_project_from_pcc'), #從工程會擷取漁業署所屬所有工程案
#     url(r'^project_profile/(?P<project_id>[0-9]+)/$', 'project_profile', name='project_profile'), #觀看督導案詳細資料
#     url(r'^error_imporve/(?P<project_id>[0-9]+)/$', 'error_imporve', name='error_imporve'), #缺失改善紀錄表
#     url(r'^download_error_improve/(?P<project_id>[0-9]+)/$', 'download_error_improve', name='download_error_improve'), #下載改善WORD檔案
#     url(r'^create_from_pcc/$', 'create_from_pcc', name='create_from_pcc'), #新增督導案
#     url(r'^get_supervise_info_from_pcc/$', 'get_supervise_info_from_pcc', name='get_supervise_info_from_pcc'), #從工程會擷取督導資料
#     url(r'^new_file_upload/$', 'new_file_upload', name='new_file_upload'), #缺失相片上傳
#     url(r'^download_file/(?P<table_name>.+)/(?P<file_id>.+)/$',"download_file", name='downliad_file'), # 下載檔案
#     url(r'^creat/$',"CreatSuperviseCase", name='CreatSuperviseCase'), # 自己新增督導案頁面
#     url(r'^create_by_self/$', 'create_by_self', name='create_by_self'), #自己新增督導案
#     url(r'^edit_profile/(?P<project_id>[0-9]+)/$', 'edit_profile', name='edit_profile'), #編輯督導案內容
#     url(r'^add_error_by_self/$', 'add_error_by_self', name='add_error_by_self'), #新增缺失

#     #以下舊分頁
#     # (r'^search/$', 'SearchSuperviseCase', {'right_type_value': u'觀看管考系統資料'}),
#     (r'^profile/(?P<case_id>[0-9]+)/$', 'ReadAndEditSuperviseCase', {'right_type_value': u'觀看管考系統資料'}),
#     (r'^ajax/$', 'rJSON', {'right_type_value': u'Ajax Request'}),
    
#     (r'^upload_photo_file/(?P<supervise_id>[0-9]+)/$', 'uploadPhotoFile', {'right_type_value': u'觀看管考系統資料'}),
#     (r'^statistics_table/(?P<year>[a-z, 0-9]+)/(?P<table_id>[0-9]+)/$', 'StatisticsTable', {'right_type_value': u'觀看管考系統資料'}),
#     # (r'^make_doc_supervise_case/(?P<supervise_id>[0-9]+)/$', 'makeDocSuperviseCase', {'right_type_value': u'觀看管考系統資料'}),
#     (r'^index/$', 'TestIndex'),
# #    (r'^(?P<get_year>[0-9]+)/$', 'index'),
# #    (r'^search/$', 'search', {'page': 'search'}),
# #    (r'^asearch/$', 'search', {'page': 'asearch'}),
# #    (r'^ec/(?P<no>[0-9\.]+)/$', 'show_introduction'),
# #    (r'^mua/(?P<year>[0-9]+)/$', 'type1chart', {'idname': 'mua'}),
# #    (r'^mut/(?P<year>[0-9]+)/$', 'type1chart', {'idname': 'mut'}),
# #    (r'^uma/(?P<year>[0-9]+)/$', 'type1chart', {'idname': 'uma'}),
# #    (r'^umt/(?P<year>[0-9]+)/$', 'type1chart', {'idname': 'umt'}),
# #    (r'^ust/(?P<year>[0-9]+)/$', 'type1chart', {'idname': 'ust'}),
# #    (r'^lut/(?P<year>[0-9]+)/$', 'type1chart', {'idname': 'lut'}),
# #    (r'^cut/(?P<year>[0-9]+)/$', 'type1chart', {'idname': 'cut'}),
# #    (r'^sun/(?P<year>[0-9]+)/$', 'type2chart', {'idname': 'sun'}),
# #    (r'^sut/(?P<year>[0-9]+)/$', 'type2chart', {'idname': 'sut'}),
# #    (r'^st/(?P<year>[0-9]+)/$', 'serial_times', {'idname': 'st'}),
# #    (r'^elt/(?P<year>[0-9]+)/((?P<unit_id>3[3-8])?/)?$', 'selectUnit'),
# #    (r'^sc/(?P<id>[0-9]+)/$', 'sc_detail'),
# )
