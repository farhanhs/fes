#!-*- coding:utf8 -*-
from django.conf.urls import include, url
from tastypie.api import Api 
from pccmating.resource import __enable__


api = Api(api_name='v2')
resource = __import__('pccmating.resource', fromlist=['resource'])
for name in __enable__:
    r = getattr(resource, name)
    api.register(r())


urlpatterns = [
    url(r'api/', include(api.urls)),
]



# urlpatterns = patterns('',
#     (r'^index/$', 'index'),
# )