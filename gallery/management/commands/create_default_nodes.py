# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from gallery.models import Case



class Command(BaseCommand):
    help = "Update current case's default nodes."

    def handle(self, *args, **kw):
        for case in Case.objects.all():
            root = case.rRootNode()
            root.default = True
            case.cDefaultNode()

