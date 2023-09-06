# -*- coding: utf8 -*-
if __name__ == '__main__':
    import sys, os
    sys.path.extend(['../..'])
    import settings
    from django.core.management import setup_environ
    setup_environ(settings)

from engphoto.models import *
from engphoto.views import _makePhoto
from rcm.models import TaojrProject
import glob, os

def fix_photo_file():
    """ 因為我不小心把所有 photo 的 file 欄位給刪了。結果只好用 verify 欄位值來推得硬碟中的相片資料夾位置，
    再透過，該資料夾下的相片 md5 碼來找回真正對應的相片檔為何。
    """
    ROOT = '/wwwdata/rcm5/'
    dir = 'apps/engphoto/photo/file'
    for p in Photo.objects.filter(verify__isnull=False, file__isnull=True)[:]:
        d1 = p.verify.md5[:2]
        d2 = p.verify.md5[2:4]
        filename = '%s/%s/%s_*.*' % (d1, d2, p.project.id)
        abs_file = os.path.join(ROOT, dir, filename)

        for photo in glob.glob(abs_file):
            f = open(photo)
            content = f.read()
            f.close()
            if p.verify.md5 == md5(content).hexdigest():
                p.file = photo.replace(ROOT, '')
                p.save()
                break


if __name__ == '__main__':
    fix_photo_file()
