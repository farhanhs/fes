#!/usr/bin/env python
# -*- coding: utf8 -*-
from django import template
register = template.Library()

from project.models import RecordProjectProfile

@register.simple_tag
def recordProjectsProfileSelect(request):
    list = []
    try:
        now_rpp_id = RecordProjectProfile.objects.get(id=request.session.get('now_record_project_profile_id', -1)).id
    except RecordProjectProfile.DoesNotExist:
        now_rpp_id = None

    for rpp in request.user.recordprojectprofile_set.all().order_by('id'):
        if rpp.id == now_rpp_id:
            list.append('\t<option value="%d" selected="selected">%s</option>' % (rpp.id, rpp.name))
        else:
            list.append('\t<option value="%d">%s</option>' % (rpp.id, rpp.name))

    return """<select class="selectRecordProjectProfile" id="id_select_record_project_profile">
    <option value="">** 請選擇紀錄名稱 **</option>
    <option value="_create">新增紀錄名稱</option>
    %s
</select>
<div id="id_create_record_project_profile" class="hidden flora">
    <div>新增紀錄名稱： <input type="text" id="id_record_project_profile_name" /></div>
</div>
""" % '\n'.join(list)

@register.simple_tag
def exportCustomReportSelect(request):
    list = []
    for ecr in request.user.exportcustomreport_set.all().order_by('id'):
        list.append('\t<option id="exportCustomReportOption_' + str(ecr.id) + '" value="%d">%s</option>' % (ecr.id, ecr.name))

    return """<select class="selectExportCustomReport">
                    <option value="">** 請選擇報表名稱 **</option>
                    <option value="_create">新增報表名稱</option>
                    %s
                </select>
                <div id="id_create_export_custom_report" class="hidden">
                    <div>新增報表名稱： <input type="text" id="id_export_custom_report_name" /></div>
                </div>
                <div id="id_update_export_custom_report_dialog" class="hidden"></div>
                <div id="id_sort_export_custom_report_dialog" class="hidden"></div>
                """ % '\n'.join(list)

@register.filter
def transToThousand(data):
    if data: return str(round(float(data)/1000.0, 3))
    else: return data

@register.filter
def getAccData(data, field):
    return data[unicode(str(field))]