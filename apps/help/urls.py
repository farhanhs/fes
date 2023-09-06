#!-*- coding:utf8 -*-
from django.conf.urls import include, url
from tastypie.api import Api
from help.resource import __enable__
from help import views as help_views


api = Api(api_name='v2')
resource = __import__('help.resource', fromlist=['resource'])
for name in __enable__:
    r = getattr(resource, name)
    api.register(r())


urlpatterns = [
    url(r'api/', include(api.urls)),
    url(r'interduce/$', help_views.interduce, name='interduce'),
    url(r'frcm/$', help_views.frcm, name='frcm'),
    url(r'harbor/$', help_views.harbor, name='harbor'),
    url(r'old_index/$', help_views.index, name='index'),
    url(r'faq/$', help_views.faq, name='faq'), # 常見問題頁面
    url(r'new_file_upload/$', help_views.new_file_upload, name='new_file_upload'),
    url(r'download_question_file/(?P<file_id>.+)/$', help_views.download_question_file, name='download_question_file'), # 下載檔案
    url(r'i_have_question/$', help_views.i_have_question, name='i_have_question'), # 線上提問
    url(r'answer_question/$', help_views.answer_question, name='answer_question'), # 回答問題
    url(r'ask_question/$', help_views.ask_question, name='ask_question'), # 提出問題
    url(r'email_to_asker/$', help_views.email_to_asker, name='email_to_asker'), # 回信給提問者
]