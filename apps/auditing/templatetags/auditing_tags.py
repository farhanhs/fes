#-*- coding: utf8 -*-
from django import template
import re
import math
from random import random
register = template.Library()


@register.filter
def cutzero(value, args=''):
    value = str(value)
    if '.' not in value: return value
    else: return re.sub('\.$', '', re.sub('0+$', '', value))

register.filter('cutzero', cutzero)


@register.filter
def ch_sort(value, args=''):
    list_0 = [u'', u'一', u'二', u'三', u'四', u'五', u'六', u'七', u'八', u'九']
    list_1 = [u'零', u'十', u'二十', u'三十', u'四十', u'五十', u'六十', u'七十', u'八十', u'九十']
    list_2 = [u'', u'一百', u'二百', u'三百', u'四百', u'五百', u'六百', u'七百', u'八百', u'九百']
    try:
        value = int(value)
    except: return u''
    if value <= 9: return list_0[value]
    elif value <= 99: return list_1[value/10] + list_0[value%10]
    elif value <= 999:
        if value in range(100, 999, 100):
            return list_2[value/100]
        elif (value/10)%10 == 1:
            return list_2[value/100] + u'一十' + list_0[value%10]
        return list_2[value/100] + list_1[(value/10)%10] + list_0[value%10]
   
register.filter('ch_sort', ch_sort)


