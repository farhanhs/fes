# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Cofiguration',
            fields=[
                ('key', models.CharField(max_length=255, serialize=False, verbose_name='Key', primary_key=True)),
                ('value', models.CharField(max_length=255, verbose_name='Value')),
            ],
        ),
        migrations.CreateModel(
            name='OnairProject',
            fields=[
                ('uid', models.CharField(max_length=255, unique=True, serialize=False, verbose_name='\u6a19\u6848\u7de8\u865f', primary_key=True)),
                ('lastsync', models.DateTimeField(null=True, verbose_name='\u6700\u5f8c\u66f4\u65b0')),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('uid', models.CharField(max_length=255, unique=True, serialize=False, verbose_name='\u6a19\u6848\u7de8\u865f', primary_key=True)),
                ('lastsync', models.DateTimeField(null=True, verbose_name='\u6700\u5f8c\u66f4\u65b0')),
                ('name', models.CharField(max_length=255, null=True, verbose_name='\u6a19\u6848\u540d\u7a31')),
                ('implementation_department', models.CharField(max_length=255, null=True, verbose_name='\u57f7\u884c\u6a5f\u95dc')),
                ('manager', models.CharField(max_length=255, null=True, verbose_name='\u806f\u7d61\u4eba')),
                ('telphone', models.CharField(max_length=255, null=True, verbose_name='\u806f\u7d61\u96fb\u8a71')),
                ('head_department', models.CharField(max_length=255, null=True, verbose_name='\u4e3b\u7ba1\u6a5f\u95dc')),
                ('host_department', models.CharField(max_length=255, null=True, verbose_name='\u4e3b\u8fa6\u6a5f\u95dc')),
                ('budget_from', models.CharField(max_length=255, null=True, verbose_name='\u7d93\u8cbb\u4f86\u6e90\u6a5f\u95dc')),
                ('host_department_code', models.CharField(max_length=255, null=True, verbose_name='\u62db\u6a19\u516c\u544a\u55ae\u4f4d\u4ee3\u78bc')),
                ('engineering_county', models.CharField(max_length=255, null=True, verbose_name='\u7e23\u5e02\u5225')),
                ('engineering_location', models.CharField(max_length=255, null=True, verbose_name='\u65bd\u5de5\u5730\u9ede')),
                ('contract_id', models.CharField(max_length=255, null=True, verbose_name='\u5951\u7d04\u7de8\u865f')),
                ('project_memo', models.TextField(null=True, verbose_name='\u5de5\u7a0b\u6982\u8981')),
                ('frcm_duration_type', models.CharField(max_length=255, null=True, verbose_name='\u5de5\u671f\u985e\u5225')),
                ('frcm_duration', models.IntegerField(default=0, verbose_name=b'\xe7\xb8\xbd\xe5\xa4\xa9\xe6\x95\xb8')),
                ('total_budget', models.FloatField(null=True, verbose_name='\u5de5\u7a0b\u7e3d\u9810\u7b97')),
                ('contract_budget', models.FloatField(null=True, verbose_name='\u767c\u5305\u9810\u7b97')),
                ('decide_tenders_price', models.FloatField(null=True, verbose_name='\u6c7a\u6a19\u91d1\u984d')),
                ('decide_tenders_price2', models.FloatField(null=True, verbose_name='\u8b8a\u66f4\u8a2d\u8a08\u5f8c\u4e4b\u5951\u7d04\u91d1\u984d')),
                ('inspector_name', models.CharField(max_length=255, null=True, verbose_name='\u76e3\u9020\u55ae\u4f4d')),
                ('constructor', models.CharField(max_length=255, null=True, verbose_name='\u627f\u9020\u5ee0\u5546')),
                ('s_tenders_method', models.CharField(max_length=255, null=True, verbose_name='\u9810\u5b9a\u62db\u6a19\u65b9\u5f0f')),
                ('r_tenders_method', models.CharField(max_length=255, null=True, verbose_name='\u5be6\u969b\u62db\u6a19\u65b9\u5f0f')),
                ('decide_tenders_method', models.CharField(max_length=255, null=True, verbose_name='\u6c7a\u6a19\u65b9\u5f0f')),
                ('pay_method', models.CharField(max_length=255, null=True, verbose_name='\u5951\u7d04\u8cbb\u7528\u7d66\u4ed8\u65b9\u5f0f')),
                ('s_design_complete_date', models.DateField(null=True, verbose_name='\u9810\u5b9a\u5b8c\u6210\u898f\u5283\u8a2d\u8a08\u65e5\u671f')),
                ('r_design_complete_date', models.DateField(null=True, verbose_name='\u5be6\u969b\u5b8c\u6210\u898f\u5283\u8a2d\u8a08\u65e5\u671f')),
                ('s_public_date', models.DateField(null=True, verbose_name='\u9810\u5b9a\u516c\u544a\u65e5\u671f')),
                ('r_public_date', models.DateField(null=True, verbose_name='\u5be6\u969b\u516c\u544a\u65e5\u671f')),
                ('s_decide_tenders_date', models.DateField(null=True, verbose_name='\u9810\u5b9a\u6c7a\u6a19\u65e5\u671f')),
                ('r_decide_tenders_date', models.DateField(null=True, verbose_name='\u5be6\u969b\u6c7a\u6a19\u65e5\u671f')),
                ('s_base_price', models.FloatField(null=True, verbose_name='\u9810\u4f30\u5e95\u50f9')),
                ('r_base_price', models.FloatField(null=True, verbose_name='\u6703\u6838\u5e95\u50f9')),
                ('s_start_date', models.DateField(null=True, verbose_name='\u9810\u5b9a\u958b\u5de5\u65e5\u671f')),
                ('r_start_date', models.DateField(null=True, verbose_name='\u5be6\u969b\u958b\u5de5\u65e5\u671f')),
                ('s_end_date', models.DateField(null=True, verbose_name='\u9810\u5b9a\u5b8c\u5de5\u65e5\u671f')),
                ('s_end_date2', models.DateField(null=True, verbose_name='\u8b8a\u66f4\u5f8c')),
                ('r_end_date', models.DateField(null=True, verbose_name='\u5be6\u969b\u5b8c\u5de5\u65e5\u671f')),
                ('r_checked_and_accepted_date', models.DateField(null=True, verbose_name='\u5be6\u969b\u5b8c\u6210\u9a57\u6536\u65e5\u671f')),
                ('s_last_pay_date', models.DateField(null=True, verbose_name='\u9810\u5b9a\u6c7a\u7b97\u65e5\u671f')),
                ('r_last_pay_date', models.DateField(null=True, verbose_name='\u5be6\u969b\u6c7a\u7b97\u65e5\u671f')),
                ('balancing_price', models.FloatField(null=True, verbose_name='\u7d50\u7b97\u91d1\u984d')),
                ('last_pay_price', models.FloatField(null=True, verbose_name='\u6c7a\u7b97\u91d1\u984d')),
            ],
        ),
        migrations.CreateModel(
            name='ProjectProgress',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('lastsync', models.DateTimeField(null=True, verbose_name='\u6700\u5f8c\u66f4\u65b0')),
                ('year', models.IntegerField(null=True, verbose_name='\u5e74\u5ea6')),
                ('month', models.IntegerField(null=True, verbose_name='\u6708\u4efd')),
                ('percentage_of_predict_progress', models.FloatField(null=True, verbose_name='\u5e74\u7d2f\u8a08\u9810\u5b9a\u9032\u5ea6')),
                ('percentage_of_real_progress', models.FloatField(null=True, verbose_name='\u5e74\u7d2f\u8a08\u5be6\u969b\u9032\u5ea6')),
                ('money_of_predict_progress', models.FloatField(null=True, verbose_name='\u5e74\u7d2f\u8a08\u9810\u5b9a\u91d1\u984d')),
                ('money_of_real_progress', models.FloatField(null=True, verbose_name='\u5e74\u7d2f\u8a08\u5be6\u969b\u91d1\u984d')),
                ('totale_money_paid', models.FloatField(null=True, verbose_name='\u7d2f\u8a08\u4f30\u9a57\u8a08\u50f9\u91d1\u984d(\u5be6\u652f\u6578)')),
                ('status', models.CharField(max_length=255, null=True, verbose_name='\u57f7\u884c\u72c0\u6cc1')),
                ('s_memo', models.CharField(max_length=255, null=True, verbose_name='\u9810\u5b9a\u5de5\u4f5c\u6458\u8981')),
                ('r_memo', models.CharField(max_length=255, null=True, verbose_name='\u5be6\u969b\u57f7\u884c\u6458\u8981')),
                ('project', models.ForeignKey(related_name='progress', to='pccmating.Project')),
            ],
        ),
    ]
