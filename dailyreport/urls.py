# -*- coding:utf8 -*-
from django.conf.urls import include, url
from tastypie.api import Api
from dailyreport.resource import __enable__
from dailyreport import views as dailyreport_views


api = Api(api_name='v1')
resource = __import__('dailyreport.resource', fromlist=['resource'])
for name in __enable__:
    r = getattr(resource, name)
    api.register(r())


urlpatterns = [
    url(r'api/', include(api.urls)),
    
    url(r'start_page/(?P<project_id>[0-9]+)/$', dailyreport_views.start_page, name='start_page'),
    url(r'engprofile/(?P<project_id>[0-9]+)/(?P<report_type>.+)/$', dailyreport_views.read_eng_profile, name='read_eng_profile'),
    url(r'item/(?P<report_type>.+)/(?P<version_id>[0-9]+)/$', dailyreport_views.read_and_edit_item, name='read_and_edit_item'),
    url(r'scheduleitem_/(?P<report_type>.+)/(?P<version_id>[0-9]+)/$', dailyreport_views.read_and_edit_schedule_item, name='read_and_edit_schedule_item'),
    url(r'report/(?P<project_id>[0-9]+)/(?P<report_type>.+)/$', dailyreport_views.read_and_edit_report, name='read_and_edit_report'),
    url(r'range_report_output/(?P<project_id>[0-9]+)/(?P<report_type>.+)/$', dailyreport_views.range_report_output, name='range_report_output'),
    url(r'progress/(?P<project_id>[0-9]+)/(?P<report_type>.+)/$', dailyreport_views.read_progress, name='read_progress'),
    url(r'progress_photo/(?P<project_id>[0-9]+)/(?P<report_type>.+)/[0-9\.]+/.+.png$', dailyreport_views.read_progress_chart, name='read_progress_chart'),
    url(r'online_print_range/(?P<project_id>[0-9]+)/(?P<report_type>.+)/(?P<info_type>.+)/(?P<start_report_date>.+)/(?P<end_report_date>.+)/$', dailyreport_views.online_print_range, name='online_print_range'),
    url(r'make_excel_range/(?P<project_id>[0-9]+)/(?P<report_type>.+)/(?P<info_type>.+)/(?P<start_report_date>.+)/(?P<end_report_date>.+)/$', dailyreport_views.make_excel_range, name='make_excel_range'),
    url(r'online_print_range2/(?P<project_id>[0-9]+)/(?P<report_type>.+)/(?P<info_type>.+)/(?P<start_report_date>.+)/(?P<end_report_date>.+)/$', dailyreport_views.online_print_range2, name='online_print_range2'),
    url(r'make_excel_range2/(?P<project_id>[0-9]+)/(?P<report_type>.+)/(?P<info_type>.+)/(?P<start_report_date>.+)/(?P<end_report_date>.+)/$', dailyreport_views.make_excel_range2, name='make_excel_range2'),
    url(r'calender/(?P<project_id>[0-9]+)/(?P<report_type>.+)/$', dailyreport_views.calender, name='calender'),
    url(r'progress_information/(?P<project_id>[0-9]+)/(?P<report_type>.+)/(?P<date_range>.+)/$', dailyreport_views.read_progress_information, name='read_progress_information'),
    url(r'calendar_information/(?P<project_id>[0-9]+)/(?P<report_type>.+)/(?P<date_range>.+)/$', dailyreport_views.calendar_information, name='calendar_information'),
    
    url(r'update_engprofile/$', dailyreport_views.update_engprofile, name='update_engprofile'),
    url(r'update_priority/$', dailyreport_views.update_priority, name='update_priority'),
    url(r'create_item/$', dailyreport_views.create_item, name='create_item'),
    url(r'create_extension/$', dailyreport_views.create_extension, name='create_extension'),
    url(r'create_item_by_pcces/$', dailyreport_views.create_item_by_pcces, name='create_item_by_pcces'),
    url(r'create_item_by_csv/$', dailyreport_views.create_item_by_csv, name='create_item_by_csv'),
    url(r'update_report_page/$', dailyreport_views.update_report_page, name='update_report_page'),
    url(r'get_report_template/$', dailyreport_views.get_report_template, name='get_report_template'), #讀取樣板
    url(r'get_report_data/$', dailyreport_views.get_report_data, name='get_report_data'), #讀取填報的值
    url(r'get_item_sum/$', dailyreport_views.get_item_sum, name='get_item_sum'), #讀取填報的值
    url(r'get_all_item_sum/$', dailyreport_views.get_all_item_sum, name='get_all_item_sum'), #讀取全部填報的值
    
    url(r'make_excel_working_date/(?P<project_id>[0-9]+)/$', dailyreport_views.make_excel_working_date, name='make_excel_working_date'),
    url(r'update_report_page_progress/$', dailyreport_views.update_report_page_progress, name='update_report_page_progress'),
    url(r'update_report_data/$', dailyreport_views.update_report_data, name='update_report_data'),
    url(r'create_labor_or_equip/$', dailyreport_views.create_labor_or_equip, name='create_labor_or_equip'),
    url(r'create_special_date/$', dailyreport_views.create_special_date, name='create_special_date'),
    url(r'create_site_material/$', dailyreport_views.create_site_material, name='create_site_material'),
    url(r'create_test_record/$', dailyreport_views.create_test_record, name='create_test_record'),
]


# urlpatterns = patterns('dailyreport.views',
#     url(r'start_page/(?P<project_id>[0-9]+)/$', 'start_page', name='start_page'),
#     url(r'engprofile/(?P<project_id>[0-9]+)/(?P<report_type>.+)/$', 'read_eng_profile', name='read_eng_profile'),
#     url(r'item/(?P<report_type>.+)/(?P<version_id>[0-9]+)/$', 'read_and_edit_item', name='read_and_edit_item'),
#     url(r'scheduleitem_/(?P<report_type>.+)/(?P<version_id>[0-9]+)/$', 'read_and_edit_schedule_item', name='read_and_edit_schedule_item'),
#     url(r'report/(?P<project_id>[0-9]+)/(?P<report_type>.+)/$', 'read_and_edit_report', name='read_and_edit_report'),
#     url(r'range_report_output/(?P<project_id>[0-9]+)/(?P<report_type>.+)/$', 'range_report_output', name='range_report_output'),
#     url(r'progress/(?P<project_id>[0-9]+)/(?P<report_type>.+)/$', 'read_progress', name='read_progress'),
#     url(r'progress_photo/(?P<project_id>[0-9]+)/(?P<report_type>.+)/[0-9\.]+/.+.png$', 'read_progress_chart', name='read_progress_chart'),
#     url(r'online_print_range/(?P<project_id>[0-9]+)/(?P<report_type>.+)/(?P<info_type>.+)/(?P<start_report_date>.+)/(?P<end_report_date>.+)/$', 'online_print_range', name='online_print_range'),
#     url(r'make_excel_range/(?P<project_id>[0-9]+)/(?P<report_type>.+)/(?P<info_type>.+)/(?P<start_report_date>.+)/(?P<end_report_date>.+)/$', 'make_excel_range', name='make_excel_range'),

#     url(r'update_engprofile/$', 'update_engprofile', name='update_engprofile'),
#     url(r'update_priority/$', 'update_priority', name='update_priority'),
#     url(r'create_item/$', 'create_item', name='create_item'),
#     url(r'create_extension/$', 'create_extension', name='create_extension'),
#     url(r'create_item_by_pcces/$', 'create_item_by_pcces', name='create_item_by_pcces'),
#     url(r'create_item_by_csv/$', 'create_item_by_csv', name='create_item_by_csv'),
#     url(r'update_report_page/$', 'update_report_page', name='update_report_page'),
#     url(r'get_report_template/$', 'get_report_template', name='get_report_template'), #讀取樣板
#     url(r'get_report_data/$', 'get_report_data', name='get_report_data'), #讀取填報的值
#     url(r'get_item_sum/$', 'get_item_sum', name='get_item_sum'), #讀取填報的值
#     url(r'get_all_item_sum/$', 'get_all_item_sum', name='get_all_item_sum'), #讀取全部填報的值
    
#     url(r'update_report_page_progress/$', 'update_report_page_progress', name='update_report_page_progress'),
#     url(r'update_report_data/$', 'update_report_data', name='update_report_data'),
#     url(r'create_labor_or_equip/$', 'create_labor_or_equip', name='create_labor_or_equip'),
#     url(r'create_special_date/$', 'create_special_date', name='create_special_date'),
#     url(r'create_site_material/$', 'create_site_material', name='create_site_material'),
#     url(r'create_test_record/$', 'create_test_record', name='create_test_record'),
# )   

# urlpatterns += patterns('',
#     (r'api/', include(api.urls)),
# )   