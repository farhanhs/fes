# -*- coding:utf8 -*-
from django import template
from django.template.defaultfilters import stringfilter
register = template.Library()

import re

@register.simple_tag
def no_js_message(feature):
    #TODO 須製作開啟 javascript 功能的說明頁。
    return ("""<p class="no_js_message">
對不起，您的瀏覽器未開啟 javascript 功能，無法使用「%s」功能。
<!--#TODO 請參照<a href="#TODO">說明</a>來開啟 javascript 功能。-->
</p>""" % feature)

@register.simple_tag
def loadDefaultJqueryUI_1_8_6():
    return """<link rel="stylesheet" title="default" type="text/css" media="screen" href="http://ajax.googleapis.com/ajax/libs/jqueryui/1.8.5/themes/ui-lightness/jquery-ui.css" />
<script type="text/javascript" src="http://www.google.com/jsapi"></script>
<script type="text/javascript">
    if (typeof(google) == 'undefined') {
        document.write(unescape('%3Cscript src="/media/jquery-1.4.2.min.js" type="text/javascript"%3E%3C/script%3E'));
        document.write(unescape('%3Cscript src="/media/jquery-ui-1.8.6.custom.min.js" type="text/javascript"%3E%3C/script%3E'));
        document.write(unescape('%3Clink rel="stylesheet" title="default" type="text/css" media="screen" href="/media/jquery-ui-1.8.6/ui-lightness/jquery-ui-1.8.6.custom.css" /%3E'));
    } else {
        google.load("jquery", "1.4.2");
        google.load("jqueryui", "1.8.6");
    }
</script>
"""

@register.simple_tag
def loading():
    return """<img id="loading" class="hidden" src="/media/images/loading.gif"/>"""
