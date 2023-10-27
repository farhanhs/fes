# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from fishuser.models import Project



class Command(BaseCommand):
    help = "Set use_gallery value in Project."

    def handle(self, *args, **kw):
        for project in Project.objects.all():
            if project.photo_set.all():
                project.use_gallery = False
                project.save()