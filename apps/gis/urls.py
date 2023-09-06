#!-*- coding:utf8 -*-
from django.conf.urls import include, url
from gis import views as gis_views


urlpatterns = [
    url(r'^$', gis_views.index),
    url(r'^search$', gis_views.search),
    url(r'^searchlist$', gis_views.searchList) ,
    url(r'^option_group$', gis_views.option_group),
    url(r'^photoAddGMap/$', gis_views.PhotoUpLoad),
    url(r'^photoAddGPS/$', gis_views.EXIFPhotoUpLoad),
    url(r'^photoSearch/$', gis_views.photoSearch),
    url(r'^photoDisable/(?P<photo_id>[0-9]+)/$', gis_views.photoDisable),
    url(r'^photoImage/(?P<photo_id>[0-9]+)/$', gis_views.readImage),
    url(r'^openImage/(?P<photo_id>[0-9]+)/$', gis_views.openImage),
]

# urlpatterns = patterns('gis.views',
#     # Example:
#     # (r'^AIpro/', include('AIpro.foo.urls')),

#     # Uncomment this for admin:
# #     (r'^admin/', include('django.contrib.admin.urls')),
#     (r'^$', 'index'),
#     (r'^search$', 'search'),
#     (r'^searchlist$', 'searchList') ,
#     # (r'^setpoint$','setPoint'),
#     (r'^option_group$','option_group'),
#     (r'^photoAddGMap/$','PhotoUpLoad'),
#     (r'^photoAddGPS/$','EXIFPhotoUpLoad'),
#     (r'^photoSearch/$','photoSearch'),
#     (r'^photoDisable/(?P<photo_id>[0-9]+)/$','photoDisable'),
#     (r'^photoImage/(?P<photo_id>[0-9]+)/$','readImage'),
#     (r'^openImage/(?P<photo_id>[0-9]+)/$','openImage'),
# #    (r'^findlatlng$','findLatlng'),
# )

"""
    /gis/photoSearch
    /gis/photoImage/
    /gis/photoThumbnail
    /gis/photoAdd
    /gis/photoModify
    /gis/photoDelete
    /gis/photoList
"""
