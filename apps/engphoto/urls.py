# -*- coding:utf8 -*-
from django.conf.urls import include, url
from engphoto import views as engphoto_views


urlpatterns = [
    url(r'^(?P<project_id>[0-9]+)/$', engphoto_views.index, {'right_type_value': u'檢視相片'}, name='engphoto_index'),
    url(r'^(?P<project_id>[0-9]+)/gettemplates/$', engphoto_views.getCheckPoint, {'kind': 'template', 'right_type_value': u'檢視相片'}),
    url(r'^(?P<project_id>[0-9]+)/getprojectcheckpoints/$', engphoto_views.getCheckPoint, {'kind': 'project', 'right_type_value': u'檢視相片'}),
    url(r'^(?P<project_id>[0-9]+)/getactualcheckpoint/$', engphoto_views.getActualCheckPoint, {'checkpoint_id': None, 'right_type_value': u'檢視相片'}),
    url(r'^(?P<project_id>[0-9]+)/exportactualcheckpoint/$', engphoto_views.exportActualCheckPoint, {'checkpoint_id': None, 'right_type_value': u'檢視相片'}),
    url(r'^getactualcheckpoint/(?P<checkpoint_id>[0-9]+)/$', engphoto_views.getActualCheckPoint, {'project_id': None, 'right_type_value': u'檢視相片'}),
    url(r'^getphotosbycheckpoint/(?P<checkpoint_id>[0-9]+)/$', engphoto_views.getPhotoByCheckPoint, {'right_type_value': u'檢視相片'}),
    url(r'^getphotos(?P<type>(bytimesort|bydefect|bytrash))/(?P<page_id>[0-9]+)/$', engphoto_views.getPhotoBySomething, {'right_type_value': u'檢視相片'}),
    url(r'^getphotonum/(?P<type>(bytimesort|bydefect|bytrash))/$', engphoto_views.getPhotoNum, {'right_type_value': u'檢視相片'}),
    url(r'^getphotosbyduplicate/(?P<photo_id>[0-9]+)/$', engphoto_views.getPhotoByDuplicate, {'right_type_value': u'檢視相片'}),
    url(r'^getphotosbynotenough/(?P<photo_id>[0-9]+)/$', engphoto_views.getPhotoByNotEnough, {'right_type_value': u'檢視相片'}),
    url(r'^getallphotolist/(?P<photo_id>[0-9]+)/$', engphoto_views.getAllPhotoList, {'right_type_value': u'檢視相片'}),
    url(r'^moveto/(?P<target_id>[0-9]+)/(?P<source_id>[0-9]+)/$', engphoto_views.moveTo, {'right_type_value': u'移至待改善相簿'}),
    url(r'^makenonduplicate/(?P<photo_id>[0-9]+)/$', engphoto_views.makeNonDuplicate, {'right_type_value': u'認定非重複相片'}),
    url(r'^makeenough/(?P<photo_id>[0-9]+)/$', engphoto_views.makeEnough, {'right_type_value': u'認定非重複相片'}),
    url(r'^updatephotoinfo/(?P<photo_id>[0-9]+)/$', engphoto_views.updatePhotoInfo, {'right_type_value': u'填寫相片意見'}),
    url(r'^deletephoto/(?P<photo_id>[0-9]+)/$', engphoto_views.deletePhoto, {'right_type_value': u'移至資源回收筒'}),
    url(r'^bigpicture/(?P<photo_id>[0-9]+)/(?P<type>(time|checkpoint|defect|trash))/$', engphoto_views.bigPicture, {'right_type_value': u'檢視相片'}),
    url(r'^bigpicture/(?P<photo_id>[0-9]+)/$', engphoto_views.bigPicture, {'type': 'checkpoint', 'right_type_value': u'檢視相片'}),
    url(r'^(?P<project_id>[0-9]+)/getphotosbyid/(?P<photos_id>[0-9\/]+)/$', engphoto_views.getPhotoById, {'right_type_value': u'檢視相片'}),
    url(r'^(?P<project_id>[0-9]+)/addby(?P<kind>(template|project))/$', engphoto_views.addCheckPoint, {'right_type_value': u'編輯查驗點'}),
    url(r'^sortcheckpoint/$', engphoto_views.sortCheckPoint, {'right_type_value': u'編輯查驗點'}),
    url(r'^getpic/(?P<filename>.*)$', engphoto_views.getPic, {'right_type_value': u'檢視相片'}),
    url(r'^(?P<project_id>[0-9]+)/getownproject/$', engphoto_views.getOwnProject, {'right_type_value': u'編輯查驗點'}),
    url(r'^getcheckpoint/(?P<checkpoint_id>[0-9]+)/$', engphoto_views.getSingleCheckPoint, {'right_type_value': u'檢視相片'}),
    url(r'^addcheckpoint/(?P<checkpoint_id>[0-9]+)/$', engphoto_views.addSingleCheckPoint, {'right_type_value': u'編輯查驗點'}),
    url(r'^changeneed/(?P<checkpoint_ct_id>[\w_]+)/$', engphoto_views.changeNeed, {'right_type_value': u'編輯查驗點'}),
]