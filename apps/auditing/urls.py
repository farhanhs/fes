# -*- coding: utf8 -*-
from django.conf.urls import *
from os.path import dirname, split

from os.path import dirname
from tastypie.api import Api 
from auditing.resource import __enable__
from auditing import views as auditing_views

api = Api(api_name='v1')
resource = __import__('auditing.resource', fromlist=['resource'])
for name in __enable__:
    r = getattr(resource, name)
    api.register(r())


urlpatterns = patterns('auditing.views',
    url(r'^search_page/$', auditing_views.search_page, name='search_page'), #查詢督導案
    url(r'^search_case/$', auditing_views.search_case, name='search_case'), #查詢督導案_動作
    url(r'^view_profile/(?P<case_id>[0-9]+)/$', auditing_views.view_profile, name='view_profile'), #觀看督導案內容
)

urlpatterns += patterns('',
    (r'api/', include(api.urls)),
)   