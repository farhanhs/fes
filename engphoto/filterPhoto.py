# -*- coding: utf8 -*-
# 請在本程式相同的目錄中，執行
# /usr/bin/python filterPhoto.py
# tar -zcf ~/otherFile.tgz otherFile
# scp ~/otherFile.tgz XXX@YYY.com:~/
#
if __name__ == '__main__':
    import sys, os
    sys.path.extend(['../..'])
    import settings
    from django.core.management import setup_environ
    setup_environ(settings)

from common.lib import mkdirByP as _mkdir
from engphoto.models import *
import shutil

def filterPhoto(projects):
    for p in projects:
        project = Project.objects.get(no=p)
        for photo in project.photo_set.filter(phototype__value=u'正常'):
            orifile = photo.file.name.replace('apps/engphoto/', '')
            newfile = orifile.replace('photo/', DESTINATION+'/')
            if os.path.isfile(orifile):
                dir = os.path.dirname(newfile)
                if not os.path.isdir(dir): _mkdir(dir)
                shutil.copy(orifile, newfile)
                

if __name__ == '__main__':
    DESTINATION = 'otherFile'
    projects = ['96RL02-16', '96S-WF-3-M31-008']
    filterPhoto(projects)
