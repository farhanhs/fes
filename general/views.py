#! -*- coding: utf8 -*-
from django.template import Context
from django.template.loader import get_template
from django.http import HttpResponse
from general.models import Unit
from general.models import Place
from general.models import Option
from common.models import Log

import os
import json
if not hasattr(json, "write"):
    #for python2.6
    json.write = json.dumps
    json.read = json.loads

import datetime
import re

def rJSON(R):
    submit = R.GET.get('submit', '')
    if not submit: submit = R.POST.get('submit', '')

    if submit == 'rCitysSelect':
        result = rCitysSelect(R)
    else:
        result = {'status': False, 'message': u'未指定方法'}

    return HttpResponse(json.write(result))

def rCitysSelect(R):
    taiwan = Place.objects.get(name=u'臺灣地區')
    return {'status': True,
        'citys': [c.rHashInHtml() for c in taiwan.uplevel_subregion.all().order_by('zipcode')]}
