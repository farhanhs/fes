#!-*- coding:utf8 -*-
from django.conf.urls import include, url
from monitor import views as monitor_views


urlpatterns = [
    url(r'^matchAJAX/$', monitor_views.matchAJAX),
    url(r'^record_action/(?P<action>(start|stop))/(?P<monitor_id>[0-9]+)/$', monitor_views.record_action),
    url(r'^change_camera_name/(?P<action>(start|stop))/(?P<monitor_id>[0-9]+)/$', monitor_views.change_camera_name),
    url(r'^update_quality/$', monitor_views.uQuality),
    url(r'^index/$', monitor_views.rIndex),
]