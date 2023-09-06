#!-*- coding:utf8 -*-
from django.conf.urls import include, url
from tastypie.api import Api
from frcm.resource import __enable__
from frcm import views as frcm_views


api = Api(api_name='v2')
resource = __import__('frcm.resource', fromlist=['resource'])
for name in __enable__:
    r = getattr(resource, name)
    api.register(r())


urlpatterns = [
    url(r'api/', include(api.urls)),

    url(r'^my_project/$', frcm_views.my_project, name='my_project'), # 我的工程
    url(r'^project_profile/(?P<project_id>[0-9]+)/$', frcm_views.project_profile, name='project_profile'), # 工程基本資料
    url(r'^project_chase/(?P<project_id>[0-9]+)/$', frcm_views.project_chase, name='project_chase'), # 縣市進度追蹤
    url(r'^claim_project/$', frcm_views.claim_project, name='claim_project'), # 廠商認領工程
    url(r'^search_project/$', frcm_views.search_project, name='search_project'), # 搜尋遠端工程
    url(r'^chase_projects/$', frcm_views.chase_projects, name='chase_projects'), # 縣市進度追蹤工程
    
    url(r'^import_project/$', frcm_views.import_project, name='import_project'), # 工程師匯入工程
    url(r'^file_upload/$', frcm_views.file_upload, name='file_upload'), # 檔案管理
    url(r'^new_file_upload/$', frcm_views.new_file_upload, name='new_file_upload'),
    url(r'^draft_project/$', frcm_views.draft_project, name='draft_project'), # 工程提案區
    url(r'^draft_project_profile/(?P<draft_project_id>[0-9]+)/$', frcm_views.draft_project_profile, name='draft_project_profile'), # 工程提案區編輯
    url(r'^download_file/(?P<table_name>.+)/(?P<file_id>.+)/$', frcm_views.download_file, name='downliad_file'), # 下載檔案
    url(r'^print_pcc_information/(?P<uid>.+)/$', frcm_views.print_pcc_information, name='print_pcc_information'), # 列印功程會資料
    url(r'^go_photo/(?P<project_id>[0-9]+)/$', frcm_views.go_photo, name='go_photo'), # 導向工程相片系統
    url(r'^file_upload_project/(?P<page>.+)/(?P<project_id>.+)/$', frcm_views.file_upload_project, name='file_upload_project'),
    url(r'^chase_use_pcc_progress/$', frcm_views.chase_use_pcc_progress, name='chase_use_pcc_progress'),
    url(r'^my_unit/$', frcm_views.my_unit, name='my_unit'),
    
    url(r'^warning/warninginfo/$', frcm_views.warning_info, name='warning_info'),
    url(r'^get_rcmup_users/$', frcm_views.get_rcmup_users, name='get_rcmup_users'),

    url(r'^send_email/$', frcm_views.send_email, name='send_email'), # 結案通報
    url(r'^report_name/$', frcm_views.report_name, name='report_name'), # 需新增工程案通報

    url(r'^statisticstable_money_data/$', frcm_views.statisticstable_money_data, name='statisticstable_money_data'),#廠商得標累計金額排行
    url(r'^statisticstable_money/$', frcm_views.statisticstable_money, name='statisticstable_money'),#廠商得標累計金額排行
    
    url(r'^unit_search/(?P<id>.+)/$', frcm_views.unit_search, name='unit_search'),
    url(r'^unit_edit/(?P<id>.+)/(?P<isexec>.+)/$', frcm_views.unit_edit, name='unit_edit'),
    url(r'^unit_create/$', frcm_views.unit_create, name='unit_create'),

    #以下舊分頁
    # (r'^$', 'readMyProject', {'right_type_value': u'menu1_遠端管理系統'}),
    # (r'^import/$', 'importProject', {'right_type_value': u'匯入工程案'}),
    # (r'^getproject/$', 'getProject', {'right_type_value': u'認領工程'}),
    # (r'^(?P<project_id>[0-9]+)/profile/$', 'reProjectProfile', {'right_type_value': u'觀看工程案基本資料'}),
    # (r'^search/$', 'searchFRCMProject', {'right_type_value': u'menu2_搜尋遠端工程'}),
    # (r'^add_draft/$', 'reDraftProject', {'right_type_value': u'menu2_匯出報表'}),
    # (r'^filems/$', 'mFiles', {'right_type_value': u'menu2_檔案管理系統'}),
    # (r'^filems/(?P<place_id>[0-9]+)/$', 'mCityFiles', {'right_type_value': u'menu2_檔案管理系統'}),
    # (r'^get_file/(?P<key>.*)/$', 'getFile'),
    # (r'^county_chase/$', 'ReadAndEditCountyChase', {'right_type_value': u'使用縣市追蹤系統'}),
    # (r'^readjson/$', 'readJson'),
    # (r'^unit_no/$', 'unit_no'),
]
