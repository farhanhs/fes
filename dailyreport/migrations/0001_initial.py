# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from decimal import Decimal


class Migration(migrations.Migration):

    dependencies = [
        ('fishuser', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='EngProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start_date', models.DateField(null=True, verbose_name='\u5be6\u969b\u958b\u5de5\u65e5\u671f')),
                ('duration', models.IntegerField(default=0, null=True, verbose_name='\u5de5\u671f\u5929\u6578(\u4e0d\u542b\u5c55\u5ef6)')),
                ('deadline', models.DateField(null=True, verbose_name='\u9650\u671f\u5b8c\u5de5\u65e5\u671f(\u4e0d\u542b\u5c55\u5ef6)')),
                ('contractor_name', models.CharField(max_length=128, null=True, verbose_name=b'\xe7\x87\x9f\xe9\x80\xa0\xe5\xbb\xa0\xe5\x95\x86\xe5\x90\x8d\xe7\xa8\xb1')),
                ('inspector_name', models.CharField(max_length=128, null=True, verbose_name=b'\xe7\x9b\xa3\xe9\x80\xa0\xe5\xbb\xa0\xe5\x95\x86\xe5\x90\x8d\xe7\xa8\xb1')),
                ('design_percent', models.DecimalField(default=Decimal('0'), verbose_name='\u9810\u5b9a\u9032\u5ea6\u767e\u5206\u6bd4', max_digits=16, decimal_places=3)),
                ('act_contractor_percent', models.DecimalField(default=Decimal('0'), verbose_name='\u71df\u9020\u5be6\u969b\u9032\u5ea6\u767e\u5206\u6bd4', max_digits=16, decimal_places=3)),
                ('act_inspector_percent', models.DecimalField(default=Decimal('0'), verbose_name='\u76e3\u9020\u5be6\u969b\u9032\u5ea6\u767e\u5206\u6bd4', max_digits=16, decimal_places=3)),
                ('contractor_lock', models.NullBooleanField(default=False, verbose_name='\u9396\u5b9a\u71df\u9020\u5ee0\u5546\u4e0d\u7d66\u4fee\u6539')),
                ('contractor_read_inspectorReport', models.NullBooleanField(default=True, verbose_name='\u71df\u9020\u662f\u5426\u53ef\u4ee5\u89c0\u770b\u76e3\u9020\u5831\u8868')),
                ('have_change_date', models.DateField(null=True, verbose_name='\u6709\u4fee\u6539\u65e5\u5831\u8868\u7684\u65e5\u671f\uff0c\u5f8c\u9762\u7684\u9700\u8981\u66f4\u65b0')),
            ],
            options={
                'verbose_name': '\u5de5\u7a0b\u6848\u4e4b\u65e5\u5831\u8868\u57fa\u672c\u8cc7\u8a0a',
                'verbose_name_plural': '\u5de5\u7a0b\u6848\u4e4b\u65e5\u5831\u8868\u57fa\u672c\u8cc7\u8a0a',
                'permissions': [('edit_contractor_report', 'edit_contractor_report'), ('view_contractor_report', 'view_contractor_report'), ('edit_inspector_report', 'edit_inspector_report'), ('view_inspector_report', 'view_inspector_report'), ('edit_schedule_item', 'edit_schedule_item'), ('view_special_date', 'view_special_date'), ('view_item', 'view_item'), ('view_engprofile', 'view_engprofile'), ('edit_item', 'edit_item'), ('view_schedule_item', 'view_schedule_item'), ('edit_engprofile', 'edit_engprofile'), ('edit_special_date', 'edit_special_date')],
            },
        ),
        migrations.CreateModel(
            name='Extension',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField(verbose_name='\u7533\u8acb\u65e5\u671f')),
                ('day', models.IntegerField(default=0, null=True, verbose_name='\u5c55\u5ef6\u5929\u6578')),
                ('no', models.CharField(max_length=1024, null=True, verbose_name='\u6587\u865f')),
                ('memo', models.TextField(default=b'', null=True, verbose_name='\u5099\u8a3b')),
                ('project', models.ForeignKey(related_name='dailyreport_extension', verbose_name='\u5de5\u7a0b\u6848', to='fishuser.Project')),
            ],
        ),
        migrations.CreateModel(
            name='Holiday',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=256, verbose_name='\u540d\u7a31')),
                ('date', models.DateField(verbose_name='\u65e5\u671f')),
            ],
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, null=True, verbose_name='\u9805\u76ee\u540d\u7a31')),
                ('unit_name', models.CharField(default=b'---', max_length=16, verbose_name='\u55ae\u4f4d')),
                ('unit_num', models.DecimalField(default=Decimal('1'), verbose_name='\u8a2d\u8a08\u6578\u91cf', max_digits=16, decimal_places=3)),
                ('unit_price', models.DecimalField(default=Decimal('0'), verbose_name='\u55ae\u50f9', max_digits=16, decimal_places=4)),
                ('priority', models.IntegerField(verbose_name='\u512a\u5148\u6b0a\u503c')),
                ('memo', models.TextField(default=b'', null=True, verbose_name='\u5099\u8a3b')),
            ],
            options={
                'verbose_name': '\u5de5\u7a0b\u9805\u76ee',
                'verbose_name_plural': '\u5de5\u7a0b\u9805\u76ee',
                'permissions': (('edit_item', 'Edit Item'), ('view_item', 'View Item')),
            },
        ),
        migrations.CreateModel(
            name='LaborEquip',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sort', models.IntegerField(default=1, verbose_name='\u6392\u5e8f')),
                ('value', models.CharField(max_length=64, verbose_name='\u540d\u7a31')),
                ('project', models.ForeignKey(related_name='dailyreport_laborquip', verbose_name='\u5de5\u7a0b\u6848', to='fishuser.Project', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Option',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('swarm', models.CharField(max_length=32, verbose_name=b'\xe7\xbe\xa4')),
                ('value', models.CharField(max_length=64, verbose_name=b'\xe9\x81\xb8\xe9\xa0\x85')),
            ],
            options={
                'verbose_name': '\u9078\u9805',
                'verbose_name_plural': '\u9078\u9805',
            },
        ),
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField(verbose_name='\u65e5\u671f')),
                ('contractor_check', models.BooleanField(default=False, verbose_name='\u71df\u9020\u5ee0\u5546\u586b\u5beb')),
                ('inspector_check', models.BooleanField(default=False, verbose_name='\u76e3\u9020\u5ee0\u5546\u586b\u5beb')),
                ('lock_c', models.BooleanField(default=False, verbose_name='\u662f\u5426\u9396\u5b9a\u4e0d\u7d66(\u96d9\u65b9)\u4fee\u6539')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='\u6700\u5f8c\u66f4\u65b0\u6642\u9593')),
                ('has_professional_item', models.BooleanField(default=False, verbose_name='\u662f\u5426\u6709\u9808\u4f9d\u300c\u71df\u9020\u696d\u5c08\u696d\u5de5\u7a0b\u7279\u5b9a\u65bd\u5de5\u9805\u76ee\u61c9\u7f6e\u4e4b\u6280\u8853\u58eb\u7a2e\u985e\u3001\u6bd4\u7387\u6216\u4eba\u6578\u6a19\u6e96\u8868\u300d\u898f\u5b9a')),
                ('describe_subcontractor', models.TextField(null=True, verbose_name='\u5de5\u7a0b\u9032\u884c\u60c5\u6cc1\u88dc\u5145\u8aaa\u660e\uff1a')),
                ('sampling', models.TextField(null=True, verbose_name='\u67e5\u6838\u6750\u6599\u898f\u683c\u53ca\u54c1\u8cea\uff08\u542b\u7d04\u5b9a\u4e4b\u6aa2\u9a57\u505c\u7559\u9ede\u3001\u6750\u6599\u8a2d\u5099\u7ba1\u5236\u53ca\u6aa2\uff08\u8a66\uff09\u9a57\u7b49\u62bd\u9a57\u60c5\u5f62\uff09')),
                ('notify', models.TextField(null=True, verbose_name='\u5176\u4ed6\u7d04\u5b9a\u76e3\u9020\u4e8b\u9805\uff08\u542b\u7763\u5c0e\u5de5\u5730\u52de\u5de5\u5b89\u5168\u885b\u751f\u4e8b\u9805\u3001\u91cd\u8981\u4e8b\u9805\u7d00\u9304\u3001\u4e3b\u8fa6\u6a5f\u95dc\u6307\u793a\u53ca\u901a\u77e5\u5ee0\u5546\u8fa6\u7406\u4e8b\u9805\uff1a')),
                ('note', models.TextField(null=True, verbose_name='\u76e3\u7763\u4f9d\u7167\u8a2d\u8a08\u5716\u8aaa\u65bd\u5de5(\u542b\u7d04\u5b9a\u4e4b\u6aa2\u9a57\u505c\u7559\u9ede\u53ca\u65bd\u5de5\u62bd\u67e5\u7b49\u60c5\u5f62)\uff1a')),
                ('c_describe_subcontractor', models.TextField(null=True, verbose_name='\u52a6\u76db\u5de5\u7a0b\u9867\u554f\u6709\u9650\u516c\u53f8')),
                ('c_sampling', models.TextField(null=True, verbose_name='\u65bd\u5de5\u53d6\u6a23\u8a66\u9a57\u7d00\u9304\uff1a')),
                ('c_notify', models.TextField(null=True, verbose_name='\u901a\u77e5\u5206\u5305\u5546\u8fa6\u7406\u4e8b\u9805\uff1a')),
                ('c_note', models.TextField(null=True, verbose_name='\u91cd\u8981\u4e8b\u9805\u7d00\u9304(\u542b\u4e3b\u8fa6\u6a5f\u95dc\u53ca\u76e3\u9020\u55ae\u4f4d\u6307\u793a\u3001\u5de5\u5730\u9047\u7dca\u6025\u7570\u5e38\u72c0\u6cc1\u53ca\u9700\u89e3\u6c7a\u65bd\u5de5\u6280\u8853\u554f\u984c\u4e4b\u901a\u5831\u8655\u7406\u60c5\u5f62\u3001\u65bd\u5de5\u8981\u5f91\u3001\u9032\u5ea6\u843d\u539f\u56e0\u53ca\u56e0\u61c9\u5c0d\u7b56\u7b49)\uff1a')),
                ('i_sum_money', models.DecimalField(null=True, verbose_name='\u76e3\u5de5\u55ae\u65e5\u65bd\u4f5c\u91d1\u984d', max_digits=16, decimal_places=3)),
                ('c_sum_money', models.DecimalField(null=True, verbose_name='\u65bd\u5de5\u55ae\u65e5\u65bd\u4f5c\u91d1\u984d', max_digits=16, decimal_places=3)),
                ('afternoon_weather', models.ForeignKey(related_name='afternoon_weather_report', default=20, verbose_name='\u4e0b\u5348\u5929\u6c23', to='dailyreport.Option')),
                ('morning_weather', models.ForeignKey(related_name='morning_weather_report', default=20, verbose_name='\u4e0a\u5348\u5929\u6c23', to='dailyreport.Option')),
                ('project', models.ForeignKey(related_name='dailyreport_report', verbose_name='\u5de5\u7a0b\u6848', to='fishuser.Project')),
            ],
            options={
                'get_latest_by': 'date',
                'permissions': (('edit_contractor_report', 'Edit Constractor Report'), ('edit_inspector_report', 'Edit Inspector Report'), ('view_contractor_report', 'View Constractor Report'), ('view_inspector_report', 'View Inspector Report')),
            },
        ),
        migrations.CreateModel(
            name='ReportHoliday',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField(verbose_name='\u65e5\u671f')),
                ('describe_subcontractor', models.TextField(null=True, verbose_name='\u5de5\u7a0b\u9032\u884c\u60c5\u6cc1\u88dc\u5145\u8aaa\u660e\uff1a')),
                ('sampling', models.TextField(null=True, verbose_name='\u67e5\u6838\u6750\u6599\u898f\u683c\u53ca\u54c1\u8cea\uff08\u542b\u7d04\u5b9a\u4e4b\u6aa2\u9a57\u505c\u7559\u9ede\u3001\u6750\u6599\u8a2d\u5099\u7ba1\u5236\u53ca\u6aa2\uff08\u8a66\uff09\u9a57\u7b49\u62bd\u9a57\u60c5\u5f62\uff09')),
                ('notify', models.TextField(null=True, verbose_name='\u5176\u4ed6\u7d04\u5b9a\u76e3\u9020\u4e8b\u9805\uff08\u542b\u7763\u5c0e\u5de5\u5730\u52de\u5de5\u5b89\u5168\u885b\u751f\u4e8b\u9805\u3001\u91cd\u8981\u4e8b\u9805\u7d00\u9304\u3001\u4e3b\u8fa6\u6a5f\u95dc\u6307\u793a\u53ca\u901a\u77e5\u5ee0\u5546\u8fa6\u7406\u4e8b\u9805\uff1a')),
                ('note', models.TextField(null=True, verbose_name='\u76e3\u7763\u4f9d\u7167\u8a2d\u8a08\u5716\u8aaa\u65bd\u5de5(\u542b\u7d04\u5b9a\u4e4b\u6aa2\u9a57\u505c\u7559\u9ede\u53ca\u65bd\u5de5\u62bd\u67e5\u7b49\u60c5\u5f62)\uff1a')),
                ('c_describe_subcontractor', models.TextField(null=True, verbose_name='\u52a6\u76db\u5de5\u7a0b\u9867\u554f\u6709\u9650\u516c\u53f8')),
                ('c_sampling', models.TextField(null=True, verbose_name='\u65bd\u5de5\u53d6\u6a23\u8a66\u9a57\u7d00\u9304\uff1a')),
                ('c_notify', models.TextField(null=True, verbose_name='\u901a\u77e5\u5206\u5305\u5546\u8fa6\u7406\u4e8b\u9805\uff1a')),
                ('c_note', models.TextField(null=True, verbose_name='\u91cd\u8981\u4e8b\u9805\u7d00\u9304(\u542b\u4e3b\u8fa6\u6a5f\u95dc\u53ca\u76e3\u9020\u55ae\u4f4d\u6307\u793a\u3001\u5de5\u5730\u9047\u7dca\u6025\u7570\u5e38\u72c0\u6cc1\u53ca\u9700\u89e3\u6c7a\u65bd\u5de5\u6280\u8853\u554f\u984c\u4e4b\u901a\u5831\u8655\u7406\u60c5\u5f62\u3001\u65bd\u5de5\u8981\u5f91\u3001\u9032\u5ea6\u843d\u539f\u56e0\u53ca\u56e0\u61c9\u5c0d\u7b56\u7b49)\uff1a')),
                ('afternoon_weather', models.ForeignKey(related_name='afternoon_weather_reportholiday', default=20, verbose_name='\u4e0b\u5348\u5929\u6c23', to='dailyreport.Option')),
                ('morning_weather', models.ForeignKey(related_name='morning_weather_reportholiday', default=20, verbose_name='\u4e0a\u5348\u5929\u6c23', to='dailyreport.Option')),
                ('project', models.ForeignKey(related_name='dailyreport_reportholiday', verbose_name='\u5de5\u7a0b\u6848', to='fishuser.Project')),
            ],
        ),
        migrations.CreateModel(
            name='ReportItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('i_num', models.DecimalField(default=Decimal('0.00'), null=True, verbose_name='\u76e3\u9020\u586b\u5beb\u6578\u91cf', max_digits=16, decimal_places=5)),
                ('i_sum_num', models.DecimalField(default=Decimal('0.00'), null=True, verbose_name='\u7d2f\u8a08\u76e3\u9020\u6578\u91cf', max_digits=16, decimal_places=5)),
                ('i_note', models.TextField(null=True, verbose_name='\u76e3\u9020\u5099\u8a3b')),
                ('c_num', models.DecimalField(default=Decimal('0.00'), null=True, verbose_name='\u65bd\u5de5\u586b\u5beb\u6578\u91cf', max_digits=16, decimal_places=5)),
                ('c_sum_num', models.DecimalField(default=Decimal('0.00'), null=True, verbose_name='\u65bd\u5de5\u7d2f\u8a08\u6578\u91cf', max_digits=16, decimal_places=5)),
                ('c_note', models.TextField(null=True, verbose_name='\u65bd\u5de5\u5099\u8a3b')),
                ('item', models.ForeignKey(verbose_name='\u65bd\u4f5c\u5de5\u9805', to='dailyreport.Item')),
                ('report', models.ForeignKey(verbose_name='\u5831\u8868', to='dailyreport.Report')),
            ],
        ),
        migrations.CreateModel(
            name='ReportLaborEquip',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('num', models.DecimalField(null=True, verbose_name='\u6578\u91cf', max_digits=16, decimal_places=3)),
                ('report', models.ForeignKey(verbose_name='\u5831\u8868', to='dailyreport.Report')),
                ('type', models.ForeignKey(verbose_name='\u4eba\u6a5f\u9805\u76ee', to='dailyreport.LaborEquip')),
            ],
        ),
        migrations.CreateModel(
            name='ScheduleItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=256, null=True, verbose_name='\u9805\u76ee\u540d\u7a31')),
                ('unit_name', models.CharField(default=b'---', max_length=16, verbose_name='\u55ae\u4f4d')),
                ('unit_num', models.DecimalField(default=Decimal('1'), verbose_name='\u8a2d\u8a08\u6578\u91cf', max_digits=16, decimal_places=3)),
                ('unit_price', models.DecimalField(default=Decimal('0'), verbose_name='\u50f9\u683c', max_digits=16, decimal_places=4)),
                ('es', models.IntegerField(default=1, verbose_name='\u958b\u59cb\u65e5\u671f')),
                ('ef', models.IntegerField(default=1, verbose_name='\u7d50\u675f\u65e5\u671f')),
                ('priority', models.IntegerField(verbose_name='\u512a\u5148\u6b0a\u503c')),
                ('kind', models.ForeignKey(related_name='kind_scheduleitem', default=11, verbose_name='\u5de5\u9805\u7a2e\u985e', to='dailyreport.Option')),
                ('pre_item', models.ForeignKey(related_name='scheduleitem_pre_item', verbose_name='\u524d\u4e00\u500b\u7248\u672c\u662f\u8ab0', to='dailyreport.ScheduleItem', null=True)),
                ('uplevel', models.ForeignKey(related_name='scheduleitem_uplevel', to='dailyreport.ScheduleItem', null=True)),
            ],
            options={
                'verbose_name': '\u5de5\u7a0b\u9805\u76ee',
                'verbose_name_plural': '\u5de5\u7a0b\u9805\u76ee',
                'permissions': (('edit_schedule_item', 'Edit ScheduleItem'), ('view_schedule_item', 'View ScheduleItem')),
            },
        ),
        migrations.CreateModel(
            name='SiteMaterial',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=256, null=True, verbose_name=b'\xe6\x9d\x90\xe6\x96\x99\xe5\x90\x8d\xe7\xa8\xb1')),
                ('unit_name', models.CharField(max_length=16, null=True, verbose_name=b'\xe5\x96\xae\xe4\xbd\x8d')),
                ('unit_num', models.DecimalField(default=0, null=True, verbose_name=b'\xe8\xa8\xad\xe8\xa8\x88\xe6\x95\xb8\xe9\x87\x8f', max_digits=16, decimal_places=3)),
                ('today_num', models.DecimalField(default=0, null=True, verbose_name=b'\xe6\x9c\xac\xe6\x97\xa5\xe5\xae\x8c\xe6\x88\x90\xe6\x95\xb8\xe9\x87\x8f', max_digits=16, decimal_places=3)),
                ('today_sum_num', models.DecimalField(default=0, null=True, verbose_name=b'\xe7\xb4\xaf\xe8\xa8\x88\xe5\xae\x8c\xe6\x88\x90\xe6\x95\xb8\xe9\x87\x8f', max_digits=16, decimal_places=3)),
                ('note', models.CharField(max_length=128, null=True, verbose_name=b'\xe5\x82\x99\xe8\xa8\xbb')),
                ('report', models.ForeignKey(verbose_name='\u5831\u8868', to='dailyreport.Report')),
            ],
            options={
                'verbose_name': '\u5de5\u5730\u6750\u6599',
                'verbose_name_plural': '\u5de5\u5730\u6750\u6599',
            },
        ),
        migrations.CreateModel(
            name='SpecialDate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start_date', models.DateField(verbose_name='\u8d77\u59cb\u65e5\u671f')),
                ('end_date', models.DateField(verbose_name='\u7d50\u675f\u65e5\u671f')),
                ('begin_date', models.DateField(verbose_name='\u751f\u6548\u65e5\u671f')),
                ('no', models.CharField(max_length=1024, null=True, verbose_name='\u6587\u865f')),
                ('reason', models.TextField(default=b'', null=True, verbose_name='\u539f\u56e0')),
                ('project', models.ForeignKey(related_name='dailyreport_specialdate', verbose_name='\u5de5\u7a0b\u6848', to='fishuser.Project')),
                ('type', models.ForeignKey(default=221, to='dailyreport.Option')),
            ],
            options={
                'verbose_name': '\u7279\u5225\u65e5\u5b50',
                'verbose_name_plural': '\u7279\u5225\u65e5\u5b50',
                'permissions': (('edit_special_date', 'Edit SpecialDate'), ('view_special_date', 'View SpecialDate')),
            },
        ),
        migrations.CreateModel(
            name='Version',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start_date', models.DateField(null=True, verbose_name='\u7248\u672c\u8d77\u59cb\u65e5\u671f')),
                ('engs_price', models.DecimalField(verbose_name='\u8a72\u7248\u672c\u5951\u7d04\u7e3d\u50f9', max_digits=16, decimal_places=3)),
                ('schedule_price', models.DecimalField(verbose_name='\u8a72\u7248\u672c\u9032\u5ea6\u7e3d\u50f9', max_digits=16, decimal_places=3)),
                ('pre_act_percent', models.DecimalField(default=Decimal('0'), verbose_name='\u524d\u7248\u672c\u8207\u300c\u672c\u7248\u672c start_date \u300d\u7684\u5be6\u969b\u9032\u5ea6', max_digits=5, decimal_places=2)),
                ('pre_design_percent', models.DecimalField(default=Decimal('0'), verbose_name='\u524d\u7248\u672c\u5728\u300c\u672c\u7248\u672c start_date \u300d\u7684\u9810\u5b9a\u9032\u5ea6', max_digits=5, decimal_places=2)),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='\u6700\u5f8c\u66f4\u65b0\u6642\u9593', null=True)),
                ('pre_i_money', models.DecimalField(default=Decimal('0'), verbose_name='\u524d\u7248\u672cs\u5c0d\u65bc\u6b64\u7248\u672c\u5de5\u9805\u7684\u76e3\u9020\u7d2f\u7a4d\u91d1\u984d', max_digits=16, decimal_places=3)),
                ('pre_c_money', models.DecimalField(default=Decimal('0'), verbose_name='\u524d\u7248\u672cs\u5c0d\u65bc\u6b64\u7248\u672c\u5de5\u9805\u7684\u65bd\u5de5\u7d2f\u7a4d\u91d1\u984d', max_digits=16, decimal_places=3)),
                ('project', models.ForeignKey(related_name='dailyreport_version', to='fishuser.Project')),
            ],
            options={
                'get_latest_by': 'start_date',
            },
        ),
        migrations.AddField(
            model_name='scheduleitem',
            name='version',
            field=models.ForeignKey(to='dailyreport.Version'),
        ),
        migrations.AlterUniqueTogether(
            name='option',
            unique_together=set([('swarm', 'value')]),
        ),
        migrations.AddField(
            model_name='laborequip',
            name='type',
            field=models.ForeignKey(default=200, to='dailyreport.Option'),
        ),
        migrations.AddField(
            model_name='item',
            name='kind',
            field=models.ForeignKey(related_name='kind_item', default=11, verbose_name='\u5de5\u9805\u7a2e\u985e', to='dailyreport.Option'),
        ),
        migrations.AddField(
            model_name='item',
            name='pre_item',
            field=models.ForeignKey(related_name='item_pre_item', verbose_name='\u524d\u4e00\u500b\u7248\u672c\u662f\u8ab0', to='dailyreport.Item', null=True),
        ),
        migrations.AddField(
            model_name='item',
            name='uplevel',
            field=models.ForeignKey(related_name='item_uplevel', to='dailyreport.Item', null=True),
        ),
        migrations.AddField(
            model_name='item',
            name='version',
            field=models.ForeignKey(to='dailyreport.Version'),
        ),
        migrations.AddField(
            model_name='engprofile',
            name='date_type',
            field=models.ForeignKey(related_name='date_type_set', verbose_name='\u5de5\u671f\u8a08\u7b97\u65b9\u5f0f', to='dailyreport.Option', null=True),
        ),
        migrations.AddField(
            model_name='engprofile',
            name='must_fix_item',
            field=models.ManyToManyField(related_name='profile_must_fix_item', verbose_name='\u6709\u8b8a\u66f4\u7684item', to='dailyreport.Item'),
        ),
        migrations.AddField(
            model_name='engprofile',
            name='project',
            field=models.ForeignKey(related_name='dailyreport_engprofile', to='fishuser.Project'),
        ),
        migrations.AddField(
            model_name='engprofile',
            name='round_type',
            field=models.ForeignKey(related_name='round_type_set', default=211, verbose_name='\u7e3d\u50f9\u8a08\u7b97\u65b9\u5f0f', to='dailyreport.Option'),
        ),
        migrations.AlterUniqueTogether(
            name='reportitem',
            unique_together=set([('report', 'item')]),
        ),
        migrations.AlterUniqueTogether(
            name='reportholiday',
            unique_together=set([('project', 'date')]),
        ),
        migrations.AlterUniqueTogether(
            name='report',
            unique_together=set([('project', 'date')]),
        ),
    ]
