#!-*- coding:utf8 -*-
from django.conf.urls import include, url
from common import views as common_views


urlpatterns = [
    url(r'^login/$', common_views.pureLogin, name='pureLogin'),
    url(r'^logout/$', common_views.pureLogout, name='pureLogout'),
    url(r'^vi/(?P<verifycode_id>\d+).png$', common_views.verifyImage, name='verifyImage'), #生成驗證圖檔
    url(r'^ann/$', common_views.askNewNumber, name='askNewNumber'), #重新要求驗證圖檔
    url(r'^ct(?P<ContentType_id>\d+)_(?P<fieldname>[\w_]+)_r(?P<row_id>\d+)/(setvalue/)?$', common_views.setValue, name='setValue'),
    url(r'^ct(?P<ContentType_id>\d+)(_[\w_]+)?_r(?P<row_id>\d+)/deleterow/$', common_views.deleteRow, name='url_deleteRow'),
    url(r'^deleterow/$', common_views.deleteRow, name='data_deleteRow'),
    url(r'^bugpage/(?P<code>[0-9A-Z]+)/$', common_views.rBugPage, name='rBugPage'),
    url(r'^buglist/$', common_views.rBugList, name='rBugList'),
    url(r'^bugstate/$', common_views.rBugState, name='rBugState'),
    url(r'^test_expando_model/$', common_views.testExpandoModel, name='testExpandoModel'),
]