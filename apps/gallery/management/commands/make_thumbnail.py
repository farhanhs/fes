# -*- coding: utf-8 -*-
# from sys import stdout
from django.core.management.base import BaseCommand, CommandError
from gallery.models import Photo

import sys, time

class Command(BaseCommand):
    help = "Make all photos' thumbnails."

    def handle(self, *args, **kw):
        for i in range(5):
            print i,
            sys.stdout.flush()
            time.sleep(1)
        # photos = Photo.objects.all()
        # # total = len(photos)
        # # for index, photo in enumerate(photos):
        # #     stdout.write("Making thumbnails... \b%s/\b%s" % (index, total))
        # #     stdout.flush()
        # #     try: photo.cAllSizeThumbnail()
        # #     except: pass#print "Something go wrong in %s" % photo.id
        # # stdout.write("\n")

        # for index in range(5) :
        #     print index
        #     # stdout.write(str(index))
        #     stdout.flush()
        #     time.sleep(1)
