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

def convert_photo():
    for project_bid_no in PROJECTS:
        try:
            project = TaojrProject.objects.get(no=project_bid_no)
        except TaojrProject.DoesNotExist:
            print 'project is not exist: %s' % project_bid_no
            continue
        project.photo_set.all().delete()
        project.checkpoint_set.all().delete()
        
        tmpitemname_dict = {}
        for item_i, tmpitem in enumerate(TmpItem.objects.filter(project_bid_no=project_bid_no)):
            print 'now project: ', tmpitem.project_bid_no
            if tmpitemname_dict.has_key(tmpitem.name):
                tmpitemname_dict[tmpitem.name] += 1
                tmpitem.name += '-' + str(tmpitemname_dict[tmpitem.name])
            else:
                tmpitemname_dict[tmpitem.name] = 1
            item = tmpitem.makeCheckpoint(item_i)
            tmpcheckpointname_dict = {}
            for checkpoint_i, tmpcheckpoint in enumerate(tmpitem.tmpcheckpoint_set.all()):
                if tmpcheckpointname_dict.has_key(tmpcheckpoint.name):
                    tmpcheckpointname_dict[tmpcheckpoint.name] += 1
                    tmpcheckpoint.name += '-' + str(tmpcheckpointname_dict[tmpcheckpoint.name])
                else:
                    tmpcheckpointname_dict[tmpcheckpoint.name] = 1
                checkpoint = tmpcheckpoint.makeCheckpoint(item, checkpoint_i)
                actual_photo_num = tmpcheckpoint.tmpphoto_set.filter(isdefective=0).count()
                if actual_photo_num > checkpoint.need:
                    checkpoint.need = actual_photo_num
                    checkpoint.save()
                _makePhoto(checkpoint)
                rcm6photos = checkpoint.photo_set.all()
                for photo_i, tmpphoto in enumerate(tmpcheckpoint.tmpphoto_set.filter(isdefective=0)):
                    try:
                        tmpphoto.makePhoto(rcm6photos[photo_i])
                    except IndexError:
                        print 'rcm4photo is to much: ', checkpoint.project, checkpoint, tmpphoto.id
                    except IOError:
                        print 'can not set photo: ', checkpoint.project, checkpoint, tmpphoto.id

if __name__ == '__main__':
    #['91AS1-05', '93WS33-002', '94ND-023', '94RN17-011', '94WE01-015', '94WE02-066',
    #'94WE27-002', '94WS02-083', '95-SME-1-H02-027', '95-SME-1-H02-033', '95-SME-1-H02-036',
    #'95-SME-1-H02-040', '95-SME-1-H02-042', '95-SME-1-J03-061', '95-WS-1-G02-003', '95-WS-1-G13-035',
    #'95-WS-1-H02-003', '95-WS-1-H13-005', '95-WS-1-J13-043', '95-WS-2-K13-049',
    allPROJECTS = \
    ['95-WS-2-L03-008',
    '95-WS-2-L13-021', '95-WS-2-L13-028', '95-WS-2-V09-052', '95-WS-3-M09-087', '95-WS-3-N04-002',
    '95-WS-3-N13-033', '95-WS-3-Q04-005', '95-WS-3-Q09-010', '95-WS-5-V06-005', '95-WS-5-V09-154',
    '95AS01-A11', '95AS01-B04', '95AS02-C03', '95LR01-2011', '95RL1-060', '95RL6-010', '95RL6-011',
    '95RL9-003', '95RN12-05', '95RR301-01', '95S-SC-2-B14-008', '95S-SC-2-K17-034', '95S-SC-3-P14-013',
    '95S-SC-3-P14-014', '95S-SC-3-Q15-006', '95S-SC-4-R17-037', '95S-WF-3-M14-022', '95S-WF-4-S17-022',
    '95S-WF-5-V17-029', '95S-WF-6-U10-009', '95WE380-001', '95WE381-001', '95WE381-005', '95WS213-007',
    '95WS216-029', '95WS217-022', '95WS283-001', '95WS283-002', '95WS378-004', '95WS381-009',
    '95WS382-018', '95WS382-024', '95WS387-005', '95WS387-006', '95WS387-014', '95WS387-017',
    '95WS387-021', '95WS387-026', '95WS906-004', '96AC13-04', '96CR01-A06', '96CR01-F10',
    '96RL01-29', '96RL01-30', '96RL02-05', '96RL02-23', '96S-SC-1-F29-001', '96S-SC-2-L24-013',
    '96S-SC-4-R23-039', '96S-SME-1-06-122', '96S-SME-1-08-140', '96S-SME-1-08-148', '96S-SME-1-08-154',
    '96S-SME-1-08-158', '96S-SME-1-08-162', '96S-WF-1-J29-007', '96S-WF-1-J30-014', '96S-WF-1-O25-001',
    '96S-WF-2-K24-002', '96S-WF-2-L33-001', '96S-WF-3-M29-024', '96S-WF-3-M30-026', '96S-WF-3-Q29-036',
    '96S-WF-4-T30-040', '96S-WF-5-V31-003', '96S-WF-5-V34-006', '96S-WF-6-U23-020', '96S-WF-6-U29-060',
    '96S-WF-6-U30-051', '96WS2013-001', '96WS2019-001', '96WS2086-001', '96WS3002-001', '96WS3004-001',
    '96WS3065-002', '97S-SC-4-R02-005', '97S-SC-4-R03-003', '97S-WF-4-T04-001', '97S-WF-6-U03-008',
    '97WS3001-023', '97WS3001-024', '97WS3003-012']

    break_num = 200
    while allPROJECTS:
        allPROJECTS_length = len(allPROJECTS)
        if  allPROJECTS_length >= break_num:
            PROJECTS = allPROJECTS[0:break_num]
            allPROJECTS = allPROJECTS[break_num:]
        else:
            PROJECTS = allPROJECTS[0:allPROJECTS_length]
            allPROJECTS = []
        convert_photo()
