# -*- coding: utf8 -*-
from django import template

register = template.Library()


@register.filter
def multiply(value, by):
    return int(value)*int(by)