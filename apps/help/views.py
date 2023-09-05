# -*- coding: utf8 -*-
from django.template import Context
from django.template import RequestContext
from django.template.loader import get_template
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import User
from fishuser.views import login_required
from help.models import Document, Question, QuestionFile
import os
import random
import datetime
import time
import decimal
import json
from django.core import mail
from django.conf import settings
import smtplib
from email import encoders
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.utils import COMMASPACE, formatdate

ROOT = settings.ROOT
file_type = 'pdf'

TODAY = lambda: datetime.date.today()
NOW = lambda: datetime.datetime.now()

def index(R):
    models = []

    #要說明的模組
    model_list = [
                  ['general', '通用模組'],
                  ['project', '工程管考系統'],
                  ['frcm', '遠端管理系統'],
                  ['harbor', '漁港資訊系統'],
                  ['gis', '地理資訊GIS系統'],
                  ]
    for m in model_list:
        models.append({
                        'name': m[0],
                        'c_name': m[1],
                        'files': Document.objects.filter(model=m[0]).order_by('sort'),
                        })

    t = get_template(os.path.join('help', 'old_templates','index.html'))
    html = t.render(Context({
                            'file_type': file_type,
                            'models': models,
                            'model_list': [i[0] for i in model_list],
                            }))
    return HttpResponse(html)




def interduce(R):
    t = get_template(os.path.join('help', 'zh-tw', 'interduce.html'))
    html = t.render(RequestContext(R,{
        'page': 'interduce',
    }))
    return HttpResponse(html)


def frcm(R):
    t = get_template(os.path.join('help', 'zh-tw', 'frcm.html'))
    html = t.render(RequestContext(R,{
        'page': 'frcm',
    }))
    return HttpResponse(html)


def harbor(R):
    t = get_template(os.path.join('help', 'zh-tw', 'harbor.html'))
    html = t.render(RequestContext(R,{
        'page': 'harbor',
    }))
    return HttpResponse(html)


@login_required
def faq(R):
    questions = Question.objects.filter(is_good_question=True)

    t = get_template(os.path.join('help', 'zh-tw', 'faq.html'))
    html = t.render(RequestContext(R,{
        'questions': questions,
        'toppage_name': u'線上問答',
        'subpage_name': u'常見問題',
    }))
    return HttpResponse(html)


@login_required
def i_have_question(R):
    for i in QuestionFile.objects.filter(question=None):
        try:
            os.remove(os.path.join(ROOT, i.file.name))
        except: pass
        i.delete()

    t = get_template(os.path.join('help', 'zh-tw', 'i_have_question.html'))
    html = t.render(RequestContext(R,{
        'user': R.user,
        'toppage_name': u'線上問答',
        'subpage_name': u'線上提問',
    }))
    return HttpResponse(html)


#管理者回答問題
@login_required
def answer_question(R):
    if not R.user.is_staff:
        return HttpResponseRedirect('/')

    good_questions = Question.objects.filter(is_good_question=True)
    complete_questions = Question.objects.filter(is_good_question=False).exclude(completer=None)
    questions = Question.objects.filter(is_good_question=False, completer=None).order_by('answer_time')

    t = get_template(os.path.join('help', 'zh-tw', 'answer_question.html'))
    html = t.render(RequestContext(R,{
        'user': R.user,
        'good_questions': good_questions,
        'complete_questions': complete_questions,
        'questions': questions,
        'toppage_name': u'線上問答',
        'subpage_name': u'管理者回答問題',
    }))
    return HttpResponse(html)


#提問寄信
@login_required
def ask_question(R):
    ask = R.POST.get('ask', '')

    user = R.user
    question = Question(
            user=user,
            ask=ask,
            ask_time=NOW()
        )
    question.save()

    for i in QuestionFile.objects.filter(question=None):
        i.question = question
        i.save()

    if not user.is_staff:
        
        smtpserver = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
        # smtpserver.ehlo()
        # smtpserver.starttls()
        smtpserver.ehlo()
        #登入系統
        smtpserver.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)

        #寄件人資訊
        fromaddr = settings.EMAIL_HOST_USER

        #收件人列表，格式為list即可
        toaddrs = [u'johnisacoolboy@gmail.com']

        msg = MIMEMultipart()
        msg['From']=fromaddr
        msg['To']=COMMASPACE.join(toaddrs)
        msg['Date']=formatdate(localtime=True)
        msg['Subject']=u'漁業線上提問系統-提問通知'

        #你要寫的內容
        info = u'有人提問了'
        info += u'\n\n\n<h3>提問者</h3>'
        info += u'\n %s(%s)' % (user.user_profile.rName(), user.email)
        info += u'\n\n\n<h3>提問時間</h3>'
        info += u'\n' + str(NOW())
        info += u'\n\n\n<h3>提問內容</h3>'
        info += u'\n' + str(ask)

        def containsnonasciicharacters(str):
            return not all(ord(c) < 128 for c in str)

        if containsnonasciicharacters(info):
            htmltext = MIMEText(info.encode('utf-8', 'replace'), 'html','utf-8')
        else:
            htmltext = MIMEText(info, 'html')

        msg.attach(htmltext)
        
        smtpserver.sendmail(fromaddr, toaddrs, msg.as_string())

        #記得要登出
        smtpserver.quit()
        
    return HttpResponse(json.dumps({'status': True}))


#回信給使用者
@login_required
def email_to_asker(R):
    if not R.user.is_staff:
        return HttpResponseRedirect('/')

    row_id = R.POST.get('row_id', '')
    question = Question.objects.get(id=row_id)
    question.answer_time = NOW()
    question.save()

    smtpserver = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
    # smtpserver.ehlo()
    # smtpserver.starttls()
    smtpserver.ehlo()
    #登入系統
    smtpserver.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)

    #寄件人資訊
    fromaddr = settings.EMAIL_HOST_USER

    #收件人列表，格式為list即可
    toaddrs = [question.user.email]

    msg = MIMEMultipart()
    msg['From']=fromaddr
    msg['To']=COMMASPACE.join(toaddrs)
    msg['Date']=formatdate(localtime=True)
    msg['Subject']=u'漁業線上提問系統-回覆通知'

    #你要寫的內容
    info = u'此為線上提問系統-回覆通知信，請勿回信'
    info += u'\n\n\n<h3>提問內容</h3>'
    info += u'\n' + str(question.ask)
    info += u'\n\n\n<h3>回覆內容</h3>'
    info += u'\n' + str(question.answer)

    def containsnonasciicharacters(str):
        return not all(ord(c) < 128 for c in str)

    if containsnonasciicharacters(info):
        htmltext = MIMEText(info.encode('utf-8', 'replace'), 'html','utf-8')
    else:
        htmltext = MIMEText(info, 'html')

    msg.attach(htmltext)
    
    smtpserver.sendmail(fromaddr, toaddrs, msg.as_string())

    #記得要登出
    smtpserver.quit()

    return HttpResponse(json.dumps({'status': True}))


#上傳檔案的處理
@login_required
def new_file_upload(R):
    data = R.POST

    table_name = data.get('table_name', '')
    question_id = data.get('question_id', '')

    f = R.FILES.get('file', None)
    full_name = f.name.split(".")
    ext = full_name[-1]
    full_name.remove(full_name[-1])
    name = "".join(full_name)

    if table_name == 'QuestionFile':
        new = QuestionFile(
            name = name,
        )
        if question_id:
            new.question = Question.objects.get(id=question_id)
        new.save()
        getattr(new, 'file').save('%s.%s'%(new.id, ext), f)
        new.save()

    return HttpResponse(json.dumps({'status': True, 'id': new.id, 'name': new.name, 'rExt': ext}))


#下載檔案專用
@login_required
def download_question_file(R, **kw):
    file_id = kw['file_id']

    row = QuestionFile.objects.get(id=file_id)

    f = open(os.path.join(ROOT, row.file.name), 'rb')
    content = f.read()
    response = HttpResponse(content_type='application/' + row.rExt())
    response['Content-Type'] = ('application/' + row.rExt())
    file_name = row.name.replace(" ", "") + '.' + row.rExt()
    response['Content-Disposition'] = ('attachment; filename='+ file_name).encode('cp950')
    response.write(content)
    return response



