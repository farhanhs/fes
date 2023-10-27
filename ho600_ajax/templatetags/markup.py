# -*- coding: utf-8 -*-
from google.appengine.api import users
from google.appengine.api import memcache
from google.appengine.ext.db import BadKeyError
from google.appengine.ext.db import BadValueError
from google.appengine.ext import db

from django import template
from django import forms
from django.template.defaultfilters import stringfilter
register = template.Library()

import settings

if 'django.contrib.markup' not in settings.INSTALLED_APPS:
    @register.filter(name='restructuredtext')
    def restructuredtext(value):
        return 'no restructuredtext: <pre>' + value + '</pre>'