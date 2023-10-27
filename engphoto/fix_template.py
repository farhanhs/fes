# -*- coding: utf8 -*-
if __name__ == '__main__':
    import sys, os
    sys.path.extend(['../..'])
    import settings
    from django.core.management import setup_environ
    setup_environ(settings)

from engphoto.models import *

def fixTemplateName():
    BEFORE = Template.objects.get(name=u'施工前')
    PROCESS = Template.objects.get(name=u'施工中')
    AFTER = Template.objects.get(name=u'施工後')
    UPLEVEL = Template.objects.get(name=u'施工前中後')
    i = 0
    for checkpoint in CheckPoint.objects.filter(name__startswith=u'施工').order_by('id'):
        if checkpoint.uplevel.name == u'施工前中後':
            if checkpoint.name == u'施工前' and checkpoint.need >= BEFORE.floor:
                checkpoint.template = BEFORE
                checkpoint.name = ''
                if checkpoint.help == BEFORE.help: checkpoint.help = ''
                checkpoint.uplevel.template = UPLEVEL
                checkpoint.uplevel.name = ''
                checkpoint.save()
                checkpoint.uplevel.save()
                i += 1
            elif checkpoint.name == u'施工中' and checkpoint.need >= PROCESS.floor:
                checkpoint.template = PROCESS
                checkpoint.name = ''
                if checkpoint.help == PROCESS.help: checkpoint.help = ''
                checkpoint.uplevel.template = UPLEVEL
                checkpoint.uplevel.name = ''
                checkpoint.save()
                checkpoint.uplevel.save()
                i += 1
            elif checkpoint.name == u'施工後' and checkpoint.need >= AFTER.floor:
                checkpoint.template = AFTER
                checkpoint.name = ''
                if checkpoint.help == AFTER.help: checkpoint.help = ''
                checkpoint.uplevel.template = UPLEVEL
                checkpoint.uplevel.name = ''
                checkpoint.save()
                checkpoint.uplevel.save()
                i += 1
    print i

if __name__ == '__main__':
    fixTemplateName()
