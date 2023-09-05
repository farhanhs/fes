# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pccmating', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='cancel_reason',
            field=models.TextField(null=True, verbose_name='\u89e3\u7d04\u539f\u56e0'),
        ),
        migrations.AddField(
            model_name='project',
            name='chase',
            field=models.BooleanField(default=False, verbose_name='\u6a19\u8a3b\u70ba\u91cd\u9ede\u8ffd\u8e64'),
        ),
        migrations.AddField(
            model_name='project',
            name='delay_factor',
            field=models.TextField(null=True, verbose_name='\u843d\u5f8c\u56e0\u7d20'),
        ),
        migrations.AddField(
            model_name='project',
            name='delay_reason',
            field=models.TextField(null=True, verbose_name='\u539f\u56e0\u5206\u6790'),
        ),
        migrations.AddField(
            model_name='project',
            name='delay_solution',
            field=models.TextField(null=True, verbose_name='\u89e3\u6c7a\u8fa6\u6cd5'),
        ),
        migrations.AddField(
            model_name='project',
            name='design_unit',
            field=models.CharField(max_length=128, null=True, verbose_name='\u8a2d\u8a08\u55ae\u4f4d'),
        ),
        migrations.AddField(
            model_name='project',
            name='fill_date',
            field=models.DateField(null=True, verbose_name='\u5167\u5bb9\u586b\u5831\u65e5'),
        ),
        migrations.AddField(
            model_name='project',
            name='head_of_agency',
            field=models.CharField(max_length=64, null=True, verbose_name='\u6a5f\u95dc\u9996\u9577'),
        ),
        migrations.AddField(
            model_name='project',
            name='implementation_department_code',
            field=models.CharField(max_length=255, null=True, verbose_name='\u57f7\u884c\u6a5f\u95dc\u4ee3\u78bc'),
        ),
        migrations.AddField(
            model_name='project',
            name='improve_date',
            field=models.DateField(null=True, verbose_name='\u6539\u9032\u671f\u9650'),
        ),
        migrations.AddField(
            model_name='project',
            name='invoice_price',
            field=models.FloatField(null=True, verbose_name='\u5df2\u4f30\u9a57\u8a08\u50f9\u91d1\u984d'),
        ),
        migrations.AddField(
            model_name='project',
            name='main_rate',
            field=models.FloatField(null=True, verbose_name='\u4e2d\u592e\u6bd4'),
        ),
        migrations.AddField(
            model_name='project',
            name='manager_email',
            field=models.CharField(max_length=64, null=True, verbose_name='\u806f\u7d61Email'),
        ),
        migrations.AddField(
            model_name='project',
            name='month',
            field=models.IntegerField(null=True, verbose_name='\u9032\u5ea6\u6708\u4efd'),
        ),
        migrations.AddField(
            model_name='project',
            name='on_pcc_now',
            field=models.BooleanField(default=False, verbose_name='\u76ee\u524d\u5728\u5de5\u7a0b\u6703\u4e0a\u53ef\u67e5\u8a62'),
        ),
        migrations.AddField(
            model_name='project',
            name='percentage_of_dulta',
            field=models.FloatField(null=True, verbose_name='\u5dee\u7570%'),
        ),
        migrations.AddField(
            model_name='project',
            name='percentage_of_predict_progress',
            field=models.FloatField(null=True, verbose_name='\u9810\u5b9a\u9032\u5ea6%'),
        ),
        migrations.AddField(
            model_name='project',
            name='percentage_of_real_progress',
            field=models.FloatField(null=True, verbose_name='\u5be6\u969b\u9032\u5ea6%'),
        ),
        migrations.AddField(
            model_name='project',
            name='plan_name',
            field=models.CharField(max_length=255, null=True, verbose_name='\u6b78\u5c6c\u8a08\u756b'),
        ),
        migrations.AddField(
            model_name='project',
            name='planning_unit',
            field=models.CharField(max_length=128, null=True, verbose_name='\u898f\u5283\u55ae\u4f4d'),
        ),
        migrations.AddField(
            model_name='project',
            name='progress_date',
            field=models.DateField(null=True, verbose_name='\u9032\u5ea6\u586b\u5831\u65e5'),
        ),
        migrations.AddField(
            model_name='project',
            name='project_manage_unit',
            field=models.CharField(max_length=128, null=True, verbose_name='\u5c08\u6848\u7ba1\u7406\u55ae\u4f4d'),
        ),
        migrations.AddField(
            model_name='project',
            name='project_type',
            field=models.CharField(max_length=64, null=True, verbose_name='\u6a19\u6848\u985e\u5225'),
        ),
        migrations.AddField(
            model_name='project',
            name='public_times',
            field=models.IntegerField(default=0, verbose_name='\u5be6\u969b\u516c\u544a\u6b21\u6578'),
        ),
        migrations.AddField(
            model_name='project',
            name='r_executive_summary',
            field=models.TextField(null=True, verbose_name='\u5be6\u969b\u57f7\u884c\u6458\u8981'),
        ),
        migrations.AddField(
            model_name='project',
            name='s_executive_summary',
            field=models.TextField(null=True, verbose_name='\u9810\u5b9a\u57f7\u884c\u6458\u8981'),
        ),
        migrations.AddField(
            model_name='project',
            name='status',
            field=models.CharField(max_length=64, null=True, verbose_name='\u72c0\u614b'),
        ),
        migrations.AddField(
            model_name='project',
            name='sub_rate',
            field=models.FloatField(null=True, verbose_name='\u5730\u65b9\u6bd4'),
        ),
        migrations.AddField(
            model_name='project',
            name='supervise_record',
            field=models.TextField(null=True, verbose_name='\u67e5\u6838'),
        ),
        migrations.AddField(
            model_name='project',
            name='supervise_score',
            field=models.TextField(null=True, verbose_name='\u5206\u6578'),
        ),
        migrations.AddField(
            model_name='project',
            name='this_year_budget',
            field=models.FloatField(null=True, verbose_name='\u672c\u5e74\u5ea6\u53ef\u7528\u9810\u7b97'),
        ),
        migrations.AddField(
            model_name='project',
            name='total_act_price',
            field=models.FloatField(null=True, verbose_name='\u7e3d\u7d2f\u8a08\u5be6\u969b\u5b8c\u6210\u91d1\u984d'),
        ),
        migrations.AddField(
            model_name='project',
            name='total_sch_price',
            field=models.FloatField(null=True, verbose_name='\u7e3d\u7d2f\u8a08\u9810\u5b9a\u5b8c\u6210\u91d1\u984d'),
        ),
        migrations.AddField(
            model_name='project',
            name='use_duration',
            field=models.IntegerField(default=0, verbose_name='\u7d2f\u8a08\u5929\u6578'),
        ),
        migrations.AddField(
            model_name='project',
            name='wait_pay_price',
            field=models.FloatField(null=True, verbose_name='\u5f85\u652f\u4ed8\u91d1\u984d'),
        ),
        migrations.AddField(
            model_name='project',
            name='x_coord',
            field=models.FloatField(null=True, verbose_name='X\u5ea7\u6a19'),
        ),
        migrations.AddField(
            model_name='project',
            name='y_coord',
            field=models.FloatField(null=True, verbose_name='Y\u5ea7\u6a19'),
        ),
        migrations.AddField(
            model_name='project',
            name='year_act_price',
            field=models.FloatField(null=True, verbose_name='\u5e74\u7d2f\u8a08\u5be6\u969b\u5b8c\u6210\u91d1\u984d'),
        ),
        migrations.AddField(
            model_name='project',
            name='year_sch_price',
            field=models.FloatField(null=True, verbose_name='\u5e74\u7d2f\u8a08\u9810\u5b9a\u5b8c\u6210\u91d1\u984d'),
        ),
        migrations.AlterField(
            model_name='project',
            name='constructor',
            field=models.CharField(max_length=255, null=True, verbose_name='\u5f97\u6a19\u5ee0\u5546'),
        ),
        migrations.AlterField(
            model_name='project',
            name='decide_tenders_method',
            field=models.CharField(max_length=255, null=True, verbose_name='\u5be6\u969b\u6c7a\u6a19\u65b9\u5f0f'),
        ),
        migrations.AlterField(
            model_name='project',
            name='engineering_county',
            field=models.CharField(max_length=255, null=True, verbose_name='\u7e23\u5e02\u9109\u93ae'),
        ),
        migrations.AlterField(
            model_name='project',
            name='r_checked_and_accepted_date',
            field=models.DateField(null=True, verbose_name='\u5be6\u969b\u9a57\u6536\u5b8c\u6210\u65e5\u671f'),
        ),
        migrations.AlterField(
            model_name='project',
            name='r_design_complete_date',
            field=models.DateField(null=True, verbose_name='\u5be6\u969b\u5b8c\u6210\u8a2d\u8a08\u65e5\u671f'),
        ),
        migrations.AlterField(
            model_name='project',
            name='s_design_complete_date',
            field=models.DateField(null=True, verbose_name='\u9810\u5b9a\u5b8c\u6210\u8a2d\u8a08\u65e5\u671f'),
        ),
        migrations.AlterField(
            model_name='project',
            name='s_end_date',
            field=models.DateField(null=True, verbose_name='\u539f\u5408\u7d04\u9810\u5b9a\u5b8c\u5de5\u65e5'),
        ),
        migrations.AlterField(
            model_name='project',
            name='s_end_date2',
            field=models.DateField(null=True, verbose_name='\u8b8a\u66f4\u5f8c\u9810\u5b9a\u5b8c\u5de5\u65e5'),
        ),
    ]
