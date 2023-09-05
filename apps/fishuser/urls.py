#!-*- coding:utf8 -*-
from django.conf.urls import include, url
from tastypie.api import Api
from fishuser.resource import __enable__
from fishuser import views as fishuser_views


api = Api(api_name='v2')
resource = __import__('fishuser.resource', fromlist=['resource'])
for name in __enable__:
    r = getattr(resource, name)
    api.register(r())


urlpatterns = [
    url(r'api/', include(api.urls)),
    url(r'^$', fishuser_views.login, name='login'),
    url(r'^logout/$', fishuser_views.logout, name='logout'),
    url(r'^index/$', fishuser_views.index, name='index'),
    url(r'^register_user/$', fishuser_views.register_user, name='register_user'),
    url(r'^user_profile/$', fishuser_views.user_profile, name='user_profile'), #觀看個人資料
    url(r'^reset_password/$', fishuser_views.reset_password, name='reset_password'), #個人自行修改密碼
    url(r'^account_reset_password/$', fishuser_views.account_reset_password, name='account_reset_password'), #管理員修改密碼
    url(r'^send_reset_password_email/$', fishuser_views.send_reset_password_email, name='send_reset_password_email'), #寄送重新設定密碼信
    url(r'^email_reset_password/(?P<code>.+)/$', fishuser_views.email_reset_password, name='email_reset_password'),
    url(r'^account_search/$', fishuser_views.account_search, name='account_search'), #帳號搜尋
    url(r'^ustu/$', fishuser_views.updateStuffToUser, name='updateStuffToUser'), #轉換帳戶
    url(r'^add_or_remove_user_group/$', fishuser_views.add_or_remove_user_group, name='add_or_remove_user_group'), #新增移除群組
    url(r'^account_create/$', fishuser_views.account_create, name='account_create'), #開創帳號
    url(r'^email_list/$', fishuser_views.email_list, name='email_list'), #叮催系統帳號管理  -  各縣市政府連絡窗口名單列表
    url(r'^email_list_info/$', fishuser_views.email_list_info, name='email_list_info'), #叮催系統 叮催資訊
    url(r'^auditing_statistics/$', fishuser_views.auditing_statistics, name='auditing_statistics'), #查核系統
    url(r'^email_to_john/$', fishuser_views.email_to_john, name='email_to_john'), #測試寄信
    url(r'^email_to_frcmuser/$', fishuser_views.email_to_frcmuser, name='email_to_frcmuser'), #每月例行進度通知信


    url(r'^system_get_all/$', fishuser_views.system_information_get_all, name='system_information_get_all'),#讀取全部系統公告頁面
    url(r'^system_edit/$', fishuser_views.system_information_edit, name='system_information_edit'),#編輯系統公告頁面
    url(r'^system_create/$', fishuser_views.system_information_create, name='system_information_create'),#新增系統公告頁面
    url(r'^set_information/$', fishuser_views.set_information, name='set_information'),#新增公告
    url(r'^new_file_upload/$', fishuser_views.new_file_upload, name='new_file_upload'), #上傳檔案
    url(r'^get_image/(?P<row_id>.+)/$', fishuser_views.get_image, name='get_image'),#讀取圖檔
    url(r'^download_file/(?P<table_name>.+)/(?P<file_id>.+)/$', fishuser_views.download_file, name='download_file'), #下載檔案
    url(r'^download_backup/$', fishuser_views.download_backup, name='download_backup'), #下載當天備份檔
    url(r'^download_backup_d1/$', fishuser_views.download_backup_d1, name='download_backup_d1'),#下載前一天備份檔
    url(r'^download_backup_d2/$', fishuser_views.download_backup_d2, name='download_backup_d2'),#下載前兩天備份檔
    url(r'^download_backup_image/$', fishuser_views.download_backup_image, name='download_backup_image'),#下載圖備份檔 
    url(r'^download_backup_pccmating/$', fishuser_views.download_backup_pccmating, name='download_backup_pccmating'),#下載pcc備份檔     

    url(r'^satisfaction/$', fishuser_views.satisfaction, name='satisfaction'), #滿意度調查表
    url(r'^satisfaction_page/$', fishuser_views.satisfaction_page, name='satisfaction_page'),#滿意度調查頁面

]
