#!-*- coding:utf8 -*-
from django.conf.urls import url

from replay import views as replay_views

urlpatterns = [
    url(r'^(?P<site_id>[0-9]+)/?$', replay_views.index),
    url(r'^video_repository/(.*)$', replay_views.video_repository),
    url(r'^$', replay_views.index, {'site_id': '1'}),
]
