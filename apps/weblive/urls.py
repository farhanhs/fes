#!-*- coding:utf8 -*-

from django.conf.urls import url
from weblive import views as weblive_views


urlpatterns = [
    url(r'^$', weblive_views.index, {'site_id': '1'}),
    url(r'^(?P<site_id>[0-9]+)/?$', weblive_views.index),
    url(r'^fetch_rows/(?P<model_name>[0-9a-z_]+)/', weblive_views.fetchRows),
    url(r'^show_sync_log/', weblive_views.showSyncLog),
    url(r'^camimg/(?P<browser>[0-9a-z_]+)/(?P<cam_id>[0-9]+)/?$', weblive_views.catchCamImg, name='weblive_camimg'),
    url(r'^iamalive/(?P<cam_fes_id>[0-9]+)/?$', weblive_views.iAmAlive),
    url(r'^show_alive_count/?$', weblive_views.showAliveCount),
    url(r'^show_alive_log/?$', weblive_views.showAliveLog),
    url(r'^change_camera_name/(?P<action>(start|stop))/(?P<camera_id>[0-9]+)/?$', weblive_views.change_camera_name),
    url(r'^screen/(?P<camera_id>[0-9]+)/?$', weblive_views.rMjpeg, name='weblive_screen'),
]
