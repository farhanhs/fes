# -*- coding:utf8 -*-
from django.db import models

from django.db import models as M
from django.db.models import Q
import datetime
import os
from PIL import Image
from types import IntType
from django.contrib.auth.models import User
from common.lib import calsize
import datetime
TODAY = lambda: datetime.date.today()
NOW = lambda: datetime.datetime.now()

class Document(M.Model):
    model = M.CharField(verbose_name=u'針對模組', max_length=128)
    name = M.CharField(verbose_name=u'功能名稱', max_length=256)
    sort = M.DecimalField(verbose_name=u'排版序號', default=0 , max_digits=16 , decimal_places=5)
    file_name = M.CharField(verbose_name=u'檔案名稱', max_length=256)
    memo = M.CharField(verbose_name=u'教學簡介', max_length=256)
    


class Question(M.Model):
    user = M.ForeignKey(User, verbose_name=u'提問者', related_name='completer_user')
    ask = M.TextField(verbose_name=u'提問', null=True)
    ask_time = M.DateTimeField(verbose_name=u'提問時間', default=datetime.datetime.now)
    answer = M.TextField(verbose_name=u'回答', null=True)
    answer_time = M.DateTimeField(verbose_name=u'回答時間', null=True)
    completer = M.ForeignKey(User, verbose_name=u'解決/回答問題的人', related_name='completer_question', null=True)
    is_good_question = M.BooleanField(verbose_name=u'是否為常見問題', default=False)



def _UPLOAD_TO(instance, filename):
    try:
        ext = filename.split('.')[-1]
    except:
        ext = 'zip'
    return os.path.join('apps', 'help', 'media', 'help', 'question_file', str(TODAY()), str(instance.id)+'.'+ext)

class QuestionFile(M.Model):
    question = M.ForeignKey(Question, verbose_name=u'工程案', null=True)
    name = M.CharField(verbose_name='檔案名', max_length=256, null=True, default='')
    file = M.FileField(upload_to=_UPLOAD_TO, null=True)

    def rUrl(self):
        return self.file.name.split('apps/help/')[-1]

    def calSize(self):
        if self.file:
            return calsize(self.file.size)
        else:
            return calsize(0)

    def rExt(self):
        return self.file.name.split('.')[-1]