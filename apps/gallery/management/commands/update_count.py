# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from gallery.models import Node



class Command(BaseCommand):
    help = "Update all nodes' image count."

    def handle(self, *args, **kw):
        for node in Node.objects.filter(child_nodes__isnull=True):
            node.uImageCount()

