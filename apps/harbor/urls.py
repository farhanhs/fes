#!-*- coding:utf8 -*-
from django.conf.urls import include, url
from tastypie.api import Api
from harbor.resource import __enable__
from harbor import views as harbor_views


api = Api(api_name='v2')
resource = __import__('harbor.resource', fromlist=['resource'])
for name in __enable__:
    r = getattr(resource, name)
    api.register(r())


urlpatterns = [
    url(r'api/', include(api.urls)),
    url(r'^index/$', harbor_views.index, name='index'), # 資訊主頁
    url(r'^port_profile/(?P<port_id>.+)/$', harbor_views.port_profile, name='port_profile'), #漁港基本資料
    url(r'^place_profile/(?P<place_id>.+)/$', harbor_views.place_profile, name='place_profile'), #縣市基本資料
    url(r'^reef_profile/(?P<reef_id>.+)/$', harbor_views.reef_profile, name='reef_profile'), #漁礁基本資料
    url(r'^download_file/(?P<table_name>.+)/(?P<file_id>.+)/$', harbor_views.download_file, name='downliad_file'), # 下載檔案
    url(r'^new_file_upload/$', harbor_views.new_file_upload, name='new_file_upload'),
    url(r'^webcam/$', harbor_views.webcam, name='webcam'), #港區監控系統
    url(r'^webcam_record/$', harbor_views.webcam_record, name='webcam_record'), #港區錄影系統
    url(r'^datashare/$', harbor_views.datashare, name='datashare'), #資料交換區
    url(r'^edit_information/$', harbor_views.edit_information, name='edit_information'), #編輯資訊
    url(r'^observatory_file_upload/$', harbor_views.observatory_file_upload, name='observatory_file_upload'), #替換觀測站風花圖
    url(r'^webcam_create/$', harbor_views.webcam_create, name='webcam_create'), #新增攝影機
    url(r'^portinstallationrecord/$', harbor_views.portinstallationrecord, name='portinstallationrecord'), #漁港設施記錄
]

# urlpatterns = patterns('harbor.views',
#     #轉移開始
#     url(r'^index/$', 'index', name='index'), # 資訊主頁
#     url(r'^port_profile/(?P<port_id>.+)/$', 'port_profile', name='port_profile'), #漁港基本資料
#     url(r'^place_profile/(?P<place_id>.+)/$', 'place_profile', name='place_profile'), #縣市基本資料
#     url(r'^reef_profile/(?P<reef_id>.+)/$', 'reef_profile', name='reef_profile'), #漁礁基本資料
#     url(r'^download_file/(?P<table_name>.+)/(?P<file_id>.+)/$',"download_file", name='downliad_file'), # 下載檔案
#     url(r'^new_file_upload/$', 'new_file_upload', name='new_file_upload'),
#     url(r'^webcam/$', 'webcam', name='webcam'), #港區監控系統
#     url(r'^webcam_record/$', 'webcam_record', name='webcam_record'), #港區錄影系統
#     url(r'^datashare/$', 'datashare', name='datashare'), #資料交換區
#     url(r'^edit_information/$', 'edit_information', name='edit_information'), #編輯資訊
#     url(r'^observatory_file_upload/$', 'observatory_file_upload', name='observatory_file_upload'), #替換觀測站風花圖
#     url(r'^webcam_create/$', 'webcam_create', name='webcam_create'), #新增攝影機
#     url(r'^portinstallationrecord/$', 'portinstallationrecord', name='portinstallationrecord'), #漁港設施記錄


    #以下舊分頁
#     (r'^readjson/$', 'readJson', {'right_type_value': u'menu1_漁港資訊系統'}),
#     (r'^editinfo/$', 'rIndex', {'right_type_value': u'進入編輯頁面'}),
#     (r'^installation/$', 'vInstallation', {'right_type_value': u'menu1_漁港資訊系統'}),
#     (r'^port/(?P<port_id>[0-9]+)/$', 'port', {'right_type_value': u'填寫漁港資訊系統資料'}),
#     (r'^port/add/$', 'addport', {'right_type_value': u'填寫漁港資訊系統資料'}),
#     (r'^observatory/(?P<observatory_id>[0-9]+)/$', 'observatory', {'right_type_value': u'填寫漁港資訊系統資料'}),
#     (r'^observatory/add/$', 'addobservatory', {'right_type_value': u'填寫漁港資訊系統資料'}),
#     (r'^city/(?P<place_id>[0-9]+)/$', 'city', {'right_type_value': u'填寫漁港資訊系統資料'}),
#     (r'^(?P<row_id>[0-9]+)/delrow/$', 'delRow', {'right_type_value': u'填寫漁港資訊系統資料'}),
#     (r'^(?P<edit_classification>[a-z]+)/(?P<target_id>[0-9]+)/(?P<edit_type>[a-z]+)/$', 'edit', {'right_type_value': u'填寫漁港資訊系統資料'}),
#     (r'^portinstallation/new/(?P<port_id>[0-9]+)/$', 'addPortInstallation', {'right_type_value': u'填寫船舶資訊'}),
#     (r'^portinstallation/record/(?P<port_id>[0-9]+)/$', 'recordPortInstallation', {'right_type_value': u'填寫船舶資訊'}),
#     (r'^portinstallation/record/(?P<port_id>[0-9]+)/(?P<year>[0-9]+)/(?P<month>[0-9]+)/$', 'getInstallationRecord', {'right_type_value': u'填寫船舶資訊'}),

#     (r'^$', 'vIndex', {'right_type_value': u'menu1_漁港資訊系統'}),
#     (r'^typeport/(?P<port_type>[0-9]+)/$', 'vTypePort', {'right_type_value': u'menu1_漁港資訊系統'}),

#     (r'^portinfo/(?P<port_id>[0-9]+)/$', 'rPortInfo', {'right_type_value': u'menu1_漁港資訊系統'}),
#     (r'^portsfnc/(?P<port_id>[0-9]+)/$', 'rPortClimate', {'right_type_value': u'menu1_漁港資訊系統'}),
#     (r'^portfishery/(?P<port_id>[0-9]+)/$', 'rPortFishery', {'right_type_value': u'menu1_漁港資訊系統'}),
#     (r'^portboat/(?P<port_id>[0-9]+)/$', 'rPortBoat', {'right_type_value': u'menu1_漁港資訊系統'}),
#     (r'^portdevelopment/(?P<port_id>[0-9]+)/$', 'rPortDevelopment', {'right_type_value': u'menu1_漁港資訊系統'}),
#     (r'^portphotos/(?P<port_id>[0-9]+)/$', 'rPortPhotos', {'right_type_value': u'menu1_漁港資訊系統'}),
#     (r'^portphotos/(?P<port_id>[0-9]+)/(?P<type>[0-9]+)/$', 'rPortTypePhotos', {'right_type_value': u'menu1_漁港資訊系統'}),
#     (r'^portfiles/(?P<port_id>[0-9]+)/$', 'UploadPortFile', {'right_type_value': u'menu1_漁港資訊系統'}),

#     (r'^cityinfo/(?P<place_id>[0-9]+)/$', 'rCityInfo', {'right_type_value': u'menu1_漁港資訊系統'}),
#     (r'^cityfishery/(?P<place_id>[0-9]+)/$', 'rCityFisheryType', {'right_type_value': u'menu1_漁港資訊系統'}),
#     (r'^cityfish/(?P<place_id>[0-9]+)/$', 'rCityFishType', {'right_type_value': u'menu1_漁港資訊系統'}),
#     (r'^cityfishop/(?P<place_id>[0-9]+)/$', 'rCityFisheryOutput', {'right_type_value': u'menu1_漁港資訊系統'}),
#     (r'^cityaquapub/(?P<place_id>[0-9]+)/$', 'rCityAquaculturePublicWorks', {'right_type_value': u'menu1_漁港資訊系統'}),
#     (r'^cityports/(?P<place_id>[0-9]+)/$', 'rCityPorts', {'right_type_value': u'menu1_漁港資訊系統'}),
# #    (r'^cityfiles/(?P<place_id>[0-9]+)/$', 'UploadCityFile', {'right_type_value': u'menu1_漁港資訊系統'}),
# #    (r'^cityfiles/js/$', 'UploadCityFileWithJS', {'right_type_value': u'js上傳檔案'}),
# #    (r'^cityfiles/jsexample/$', 'UploadCityFileWithJSFormExample', {'right_type_value': u'js上傳檔案'}),

#     (r'^external/port/(?P<port_code>[0-9,a-z,A-Z]+)/$', 'TransformToPort', {'right_type_value': u'menu1_漁港資訊系統'}),
#     (r'^live_webcam/$', 'rLiveWebcamLink', {'right_type_value': u'menu1_漁港資訊系統'}),
#     (r'^replay/$', 'rReplayLink', {'right_type_value': u'menu1_漁港資訊系統'}),
#     (r'^data_share/$', 'rDataShare', {'right_type_value': u'menu1_漁港資訊系統'}),

#     (r'^fish_pool/list/$', 'fish_pool_list_201012_by_cerberus', {}),
#     (r'^fish_pool/create/$', 'fish_pool_create_201012_by_cerberus', {}),
#     (r'^fish_pool/edit/$', 'fish_pool_edit_201012_by_cerberus', {}),
#     (r'^fish_pool/update/$', 'fish_pool_update_201012_by_cerberus', {}),
#     (r'^fish_pool/delete/$', 'fish_pool_delete_201012_by_cerberus', {}),
#     (r'^import_temp_project/$', 'ImportTempProject', {}),


    # 會計系統 移除
    # (r'^accouting/$', 'accounting_20101230_by_cerberus', {}),

    # 以下路徑為縮圖之用，將讀取全部圖片並縮圖轉存，請慎用！
    # (r'^MakeMiddlePhoto_take_a_long_break/$', 'makeMiddlePhoto', {'right_type_value': u'menu1_漁港資訊系統'}),


    # (r'^portcam/(?P<port_id>[0-9]+)/$', 'rPortCam', {'right_type_value': u'menu1_漁港資訊系統'}),
    # (r'^portcam/(?P<port_id>[0-9]+)/(?P<cam_id>[0-9]+)$', 'rCam', {'right_type_value': u'menu1_漁港資訊系統'}),

    # (r'^cam/add/$', 'addcam', {'right_type_value': u'填寫漁港資訊系統資料'}),
    # (r'^cam/edit/$', 'editcam', {'right_type_value': u'填寫漁港資訊系統資料'}),
    # (r'^cam/show_password/$', 'show_password', {'right_type_value': u'填寫漁港資訊系統資料'}),

# )


# urlpatterns += patterns('',
#     (r'api/', include(api.urls)),
# )   
