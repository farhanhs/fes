#!/usr/bin/env python

import sys, os, datetime

if(len(sys.argv)>1):
    print("Automator start with cimcore locate at %s"%sys.argv[1])
    os.chdir(sys.argv[1])
    sys.path[0] = sys.argv[1]
else:
    print("Please give me the location of cimcore")
    sys.exit(1)

from django.core.management import setup_environ
import settings

setup_environ(settings)
print("CIMCore loaded.")

try:
    from core.kernel import models as km  # This import is just use to avoid a import bug
    from modules.pccmating.models import OnairProject, Project
    from modules.pccmating.sync import getHandler, syncPccInformation
except ImportError:
    from pccmating.models import OnairProject, Project
    from pccmating.sync import getHandler, syncPccInformation
    

handler = getHandler()
for project in OnairProject.objects.all():
    try:
        syncPccInformation(project.uid, handler)
        project.lastsync = datetime.datetime.now()
        project.save()
        sys.stdout.write(".")
    except:
        print("Error at project code: %s"%project.uid)
        handler = getHandler()