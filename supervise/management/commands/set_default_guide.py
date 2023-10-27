
# -*- coding: utf-8 -*-
import sys
print sys.path

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Group, Permission
from django.conf import settings


from supervise.models import *



class Command(BaseCommand):
    help = 'set Default Guide'


    def handle(self, *args, **kw):
        #移除重複的guide
        all_names = set([i.name for i in Guide.objects.all()])
        for name in all_names:
            gs = Guide.objects.filter(name=name).order_by('id')
            g1 = gs.first()
            if gs.count() != 1:
                for dg in gs[1:]:
                    for s in SuperviseCase.objects.filter(outguide=dg):
                        s.outguide.remove(dg)
                        s.outguide.add(g1)
                        s.save()
                    for s in SuperviseCase.objects.filter(inguide=dg):
                        s.inguide.remove(dg)
                        s.inguide.add(g1)
                        s.save()
                    for s in SuperviseCase.objects.filter(captain=dg):
                        s.captain.remove(dg)
                        s.captain.add(g1)
                        s.save()
                    for s in SuperviseCase.objects.filter(worker=dg):
                        s.worker.remove(dg)
                        s.worker.add(g1)
                        s.save()

                    for e in Error.objects.filter(guide=dg):
                        e.guide = g1
                        e.save()
                    dg.delete()



        default_guides = [
            u"王冠雄", u"萬宏猷", u"林榮清", u"蘇有德", u"劉進義",
            u"劉彥忠", u"陳明信", u"林尚儀", u"楊欽銘", u"陳鴻雄", 
            u"蔡瑤堂", u"蔡易豐", u"余榮洲", u"林俶寬", u"林永德"
        ]

        for name in default_guides:
            print name,
            g, created = Guide.objects.get_or_create(name=name)
            g.is_default = True
            g.save()
            print created