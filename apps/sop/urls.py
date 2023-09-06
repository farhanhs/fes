#!-*- coding:utf8 -*-
from django.conf.urls import include, url
from tastypie.api import Api
from sop.resource import __enable__
from sop import views as sop_views


api = Api(api_name='v1')
resource = __import__('sop.resource', fromlist=['resource'])
for name in __enable__:
    r = getattr(resource, name)
    api.register(r())


urlpatterns = [
    url(r'api/', include(api.urls)),
    url(r'^$', sop_views.index, name='SOPadmin_index'),
    url(r'^view_file/(?P<file_id>.+)/$', sop_views.view_file, name='SOPview_file'),
    url(r'^download_file/(?P<file_id>.+)/$', sop_views.download_file, name='SOPdownliad_file'),
    url(r'^download_zip_file/(?P<sop_id>.+)/$', sop_views.download_zip_file, name='SOPdownload_zip_file'),
    url(r'^admin/$', sop_views.admin_index, name='SOPadmin_index'),
    url(r'^admin/create/$', sop_views.create, name='SOPcreate'),
    url(r'^admin/create_sop/$', sop_views.createSop, name='SOPcreateSop'),
    url(r'^admin/create_item/$', sop_views.createItem, name='SOPcreateItem'),
    url(r'^admin/load_select_form/$', sop_views.loadSelectForm, name='SOPloadSelectForm'),
    url(r'^admin/update_upload/$', sop_views.updateUpload, name='SOPupdateUpload'),
    url(r'^admin/change_item_name/$', sop_views.changeItemName, name='SOPchangeItemName'),
]