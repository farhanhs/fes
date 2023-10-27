# -*- coding: utf-8 -*-
"""fes_mobile URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from mobile import views
from gallery import views as gallery_views

urlpatterns = [
    url(r'^login/', views.login, name='m_login'),
    url(r'^logout/', views.logout, name='m_logout'),
    url(r'^index/', views.index, name='m_index'),
    url(r'^my_project/', views.my_project, name="m_my_project"),
    url(r'^serch_project/', views.search_project, name='m_search_project'),
    url(r'^monitor/', views.monitor, name='m_monitor'),
    url(r'^project_info/(?P<project_id>[0-9]+)/', views.project_info, name='m_project_info'),
    url(r'^search_supervise/', views.search_supervise, name="m_search_supervise"),
    url(r'^claim_project/', views.claim_project, name="m_claim_project"),
    url(r'^set_password/', views.set_password, name="m_set_password"),
    url(r'^supervise_info/(?P<project_id>[0-9]+)/', views.supervise_info, name="m_supervise_info"),
    url(r'^dailyreport/(?P<project_id>[0-9]+)/', views.dailyreport, name="m_dailyreport"),
    url(r'^gallery/(?P<project_id>[0-9]+)/', views.gallery, name="m_gallary"),
]
