# -*- coding: utf8 -*-
if __name__ == '__main__':
    import sys, os
    sys.path.extend(['../..'])
    import settings
    from django.core.management import setup_environ
    setup_environ(settings)

from engphoto.models import *

for v in [Verify.objects.all()[0]]:
    for i, photo in enumerate(v.photo_set.all().order_by('id')):
        try:
            photo.updatetime = photo.uploadtime \
            = TmpPhoto.objects.filter(verify=v.md5).order_by('updatetime')[i].updatetime
            photo.save()
        except IndexError:
            break

