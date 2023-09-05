# -*- coding: utf8 -*-
if __name__ == '__main__':
    import sys, os
    sys.path.extend(['../..'])
    import settings
    from django.core.management import setup_environ
    setup_environ(settings)

from general.models import *
import re

for u in Unit.objects.filter(chairman__isnull=False):
    html = u.html.replace('\r', '').replace('\n', '')
    #print html
    g = int(re.match(u'^.*資本額\(千元\)<[^>]+><[^>]+>([^<]+)<.*$', unicode(html)).groups()[0].replace(',', ''))*1000
    print u.no
    u.capital = g
    u.save()

