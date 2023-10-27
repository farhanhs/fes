#!-*- coding:utf8 -*-
from django.conf.urls import include, url
from tastypie.api import Api 
from gallery.resources import __enable__
from gallery import views as gallery_views


api = Api(api_name='v1')
resource = __import__('gallery.resources', fromlist=['resource'])
for name in __enable__:
    r = getattr(resource, name)
    api.register(r())


urlpatterns = [
    url(r'api/', include(api.urls)),
    url(r'^from_rcm/(?P<project_id>[0-9]+)/$', gallery_views.from_rcm, name='from_rcm'),
    url(r'^(?P<project_id>[0-9]+)/$', gallery_views.index, name='index'),
    url(r'^examine/$', gallery_views.examine, name='examine'),
    url(r'^support/$', gallery_views.support, name='support'),
]