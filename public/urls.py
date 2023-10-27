#!-*- coding:utf8 -*-
from django.conf.urls import include, url
from public import views as public_views


urlpatterns = [
    url(r'^$', public_views.public_list, name='public_list'), # 公開工程列表
    url(r'^photo/(?P<project_id>[0-9]+)/$', public_views.public_photo, name='public_photo'),
]