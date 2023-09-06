from django import template
import re
from random import random
register = template.Library()


@register.filter
def cutzero(value, args=''):
    value = str(value)
    if '.' not in value: return value
    else: return re.sub('\.$', '', re.sub('0+$', '', value))

register.filter('cutzero', cutzero)

@register.filter
def dateformat(value, args=''):
    value = str(value)
    if value:
        value = value.split('-')
        value = '%s-%s-%s' % (int(value[0])-1911, value[1], value[2])
    return value

register.filter('dateformat', dateformat)