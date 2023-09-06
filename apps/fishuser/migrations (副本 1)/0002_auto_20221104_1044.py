# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import fishuser.models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('general', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('fishuser', '0001_initial'),
    ]

    operations = [migrations.AddField(
            model_name='countychaseprojectonebyone',
            name='stat_acpt',
            field=models.NullBooleanField(verbose_name='\u9a57\u6536\u4e2d'),
        ),
        migrations.AddField(
            model_name='countychaseprojectonebyone',
            name='stat_acpt_date',
            field=models.DateField(null=True, verbose_name='\u9a57\u6536\u4e2d_\u65e5\u671f'),
        ),
        migrations.AddField(
            model_name='countychaseprojectonebyone',
            name='stat_acpt_memo',
            field=models.CharField(max_length=256, null=True, verbose_name='\u9a57\u6536\u4e2d_\u5099\u8a3b'),
        ),
        migrations.AddField(
            model_name='countychaseprojectonebyone',
            name='stat_closd',
            field=models.NullBooleanField(verbose_name='\u5df2\u7d50\u6848'),
        ),
        migrations.AddField(
            model_name='countychaseprojectonebyone',
            name='stat_closd_date',
            field=models.DateField(null=True, verbose_name='\u5df2\u7d50\u6848_\u65e5\u671f'),
        ),
        migrations.AddField(
            model_name='countychaseprojectonebyone',
            name='stat_closd_memo',
            field=models.CharField(max_length=256, null=True, verbose_name='\u5df2\u7d50\u6848_\u5099\u8a3b'),
        ),
        migrations.AddField(
            model_name='countychaseprojectonebyone',
            name='stat_cmplt',
            field=models.NullBooleanField(verbose_name='\u5df2\u7533\u5831\u7ae3\u5de5'),
        ),
        migrations.AddField(
            model_name='countychaseprojectonebyone',
            name='stat_cmplt_date',
            field=models.DateField(null=True, verbose_name='\u5df2\u7533\u5831\u7ae3\u5de5_\u65e5\u671f'),
        ),
        migrations.AddField(
            model_name='countychaseprojectonebyone',
            name='stat_cmplt_memo',
            field=models.CharField(max_length=256, null=True, verbose_name='\u5df2\u7533\u5831\u7ae3\u5de5_\u5099\u8a3b'),
        ),
        migrations.AddField(
            model_name='countychaseprojectonebyone',
            name='stat_cnfl',
            field=models.NullBooleanField(verbose_name='\u5c65\u7d04\u722d\u8b70\u4e2d'),
        ),
        migrations.AddField(
            model_name='countychaseprojectonebyone',
            name='stat_cnfl_date',
            field=models.DateField(null=True, verbose_name='\u5c65\u7d04\u722d\u8b70\u4e2d_\u65e5\u671f'),
        ),
        migrations.AddField(
            model_name='countychaseprojectonebyone',
            name='stat_cnfl_memo',
            field=models.CharField(max_length=256, null=True, verbose_name='\u5c65\u7d04\u722d\u8b70\u4e2d_\u5099\u8a3b'),
        ),
        migrations.AddField(
            model_name='countychaseprojectonebyone',
            name='stat_cnst',
            field=models.NullBooleanField(verbose_name='\u65bd\u5de5\u4e2d'),
        ),
        migrations.AddField(
            model_name='countychaseprojectonebyone',
            name='stat_cnst_date',
            field=models.DateField(null=True, verbose_name='\u65bd\u5de5\u4e2d_\u65e5\u671f'),
        ),
        migrations.AddField(
            model_name='countychaseprojectonebyone',
            name='stat_cnst_memo',
            field=models.CharField(max_length=256, null=True, verbose_name='\u65bd\u5de5\u4e2d_\u5099\u8a3b'),
        ),
        migrations.AddField(
            model_name='countychaseprojectonebyone',
            name='stat_file_oln',
            field=models.NullBooleanField(verbose_name='\u6587\u4ef6\u516c\u544a\u4e2d'),
        ),
        migrations.AddField(
            model_name='countychaseprojectonebyone',
            name='stat_file_oln_date',
            field=models.DateField(null=True, verbose_name='\u6587\u4ef6\u516c\u544a\u4e2d_\u65e5\u671f'),
        ),
        migrations.AddField(
            model_name='countychaseprojectonebyone',
            name='stat_file_oln_memo',
            field=models.CharField(max_length=256, null=True, verbose_name='\u6587\u4ef6\u516c\u544a\u4e2d_\u5099\u8a3b'),
        ),
        migrations.AddField(
            model_name='countychaseprojectonebyone',
            name='stat_file_prep',
            field=models.NullBooleanField(verbose_name='\u6587\u4ef6\u6e96\u5099\u4e2d'),
        ),
        migrations.AddField(
            model_name='countychaseprojectonebyone',
            name='stat_file_prep_date',
            field=models.DateField(null=True, verbose_name='\u6587\u4ef6\u6e96\u5099\u4e2d_\u65e5\u671f'),
        ),
        migrations.AddField(
            model_name='countychaseprojectonebyone',
            name='stat_file_prep_memo',
            field=models.CharField(max_length=256, null=True, verbose_name='\u6587\u4ef6\u6e96\u5099\u4e2d_\u5099\u8a3b'),
        ),
        migrations.AddField(
            model_name='countychaseprojectonebyone',
            name='stat_file_prvw',
            field=models.NullBooleanField(verbose_name='\u6587\u4ef6\u9810\u89bd\u4e2d'),
        ),
        migrations.AddField(
            model_name='countychaseprojectonebyone',
            name='stat_file_prvw_date',
            field=models.DateField(null=True, verbose_name='\u6587\u4ef6\u9810\u89bd\u4e2d_\u65e5\u671f'),
        ),
        migrations.AddField(
            model_name='countychaseprojectonebyone',
            name='stat_file_prvw_memo',
            field=models.CharField(max_length=256, null=True, verbose_name='\u6587\u4ef6\u9810\u89bd\u4e2d_\u5099\u8a3b'),
        ),
        migrations.AddField(
            model_name='countychaseprojectonebyone',
            name='stat_illus_memo',
            field=models.CharField(max_length=256, null=True, verbose_name='\u8fa6\u7406\u60c5\u5f62\u5099\u8a3b'),
        ),
        migrations.AddField(
            model_name='countychaseprojectonebyone',
            name='stat_oth',
            field=models.NullBooleanField(verbose_name='\u5176\u4ed6'),
        ),
        migrations.AddField(
            model_name='countychaseprojectonebyone',
            name='stat_oth_date',
            field=models.DateField(null=True, verbose_name='\u5176\u4ed6_\u65e5\u671f'),
        ),
        migrations.AddField(
            model_name='countychaseprojectonebyone',
            name='stat_oth_memo',
            field=models.CharField(max_length=256, null=True, verbose_name='\u5176\u4ed6_\u5099\u8a3b'),
        ),
        migrations.AddField(
            model_name='countychaseprojectonebyone',
            name='stat_pay',
            field=models.NullBooleanField(verbose_name='\u7d50\u7b97\u4ed8\u6b3e\u4e2d'),
        ),
        migrations.AddField(
            model_name='countychaseprojectonebyone',
            name='stat_pay_date',
            field=models.DateField(null=True, verbose_name='\u7d50\u7b97\u4ed8\u6b3e\u4e2d_\u65e5\u671f'),
        ),
        migrations.AddField(
            model_name='countychaseprojectonebyone',
            name='stat_pay_memo',
            field=models.CharField(max_length=256, null=True, verbose_name='\u7d50\u7b97\u4ed8\u6b3e\u4e2d_\u5099\u8a3b'),
        ),
        migrations.AddField(
            model_name='countychaseprojectonebyone',
            name='stat_res_ctr',
            field=models.NullBooleanField(verbose_name='\u6c7a\u6a19_\u8a02\u7d04\u4e2d'),
        ),
        migrations.AddField(
            model_name='countychaseprojectonebyone',
            name='stat_res_ctr_date',
            field=models.DateField(null=True, verbose_name='\u6c7a\u6a19_\u8a02\u7d04\u4e2d_\u65e5\u671f'),
        ),
        migrations.AddField(
            model_name='countychaseprojectonebyone',
            name='stat_res_ctr_memo',
            field=models.CharField(max_length=256, null=True, verbose_name='\u6c7a\u6a19_\u8a02\u7d04\u4e2d_\u5099\u8a3b'),
        ),
        migrations.AddField(
            model_name='countychaseprojectonebyone',
            name='stat_solution_memo',
            field=models.CharField(max_length=256, null=True, verbose_name='\u89e3\u6c7a\u5c0d\u7b56'),
        ),
        migrations.AddField(
            model_name='countychaseprojectonebyone',
            name='stat_stop',
            field=models.NullBooleanField(verbose_name='\u505c\u5de5\u4e2d'),
        ),
        migrations.AddField(
            model_name='countychaseprojectonebyone',
            name='stat_stop_date',
            field=models.DateField(null=True, verbose_name='\u505c\u5de5\u4e2d_\u65e5\u671f'),
        ),
        migrations.AddField(
            model_name='countychaseprojectonebyone',
            name='stat_stop_memo',
            field=models.CharField(max_length=256, null=True, verbose_name='\u505c\u5de5\u4e2d_\u5099\u8a3b'),
        ),
        migrations.AddField(
            model_name='countychaseprojectonebyone',
            name='stat_stop_reason_memo',
            field=models.CharField(max_length=256, null=True, verbose_name='\u505c\u5de5\u6216\u843d\u5f8c\u539f\u56e0'),
        ),
        migrations.AddField(
            model_name='countychaseprojectonebyone',
            name='stat_term_ed',
            field=models.NullBooleanField(verbose_name='\u5df2\u89e3\u7d04'),
        ),
        migrations.AddField(
            model_name='countychaseprojectonebyone',
            name='stat_term_ed_date',
            field=models.DateField(null=True, verbose_name='\u5df2\u89e3\u7d04_\u65e5\u671f'),
        ),
        migrations.AddField(
            model_name='countychaseprojectonebyone',
            name='stat_term_ed_memo',
            field=models.CharField(max_length=256, null=True, verbose_name='\u5df2\u89e3\u7d04_\u5099\u8a3b'),
        ),
        migrations.AddField(
            model_name='countychaseprojectonebyone',
            name='stat_term_ing',
            field=models.NullBooleanField(verbose_name='\u89e3\u7d04\u4e2d'),
        ),
        migrations.AddField(
            model_name='countychaseprojectonebyone',
            name='stat_term_ing_date',
            field=models.DateField(null=True, verbose_name='\u89e3\u7d04\u4e2d_\u65e5\u671f'),
        ),
        migrations.AddField(
            model_name='countychaseprojectonebyone',
            name='stat_term_ing_memo',
            field=models.CharField(max_length=256, null=True, verbose_name='\u89e3\u7d04\u4e2d_\u5099\u8a3b'),
        ),
        migrations.AddField(
            model_name='countychaseprojectonebyone',
            name='stat_wrk_per',
            field=models.NullBooleanField(verbose_name='\u52de\u52d9\u5c65\u7d04\u4e2d'),
        ),
        migrations.AddField(
            model_name='countychaseprojectonebyone',
            name='stat_wrk_per_date',
            field=models.DateField(null=True, verbose_name='\u52de\u52d9\u5c65\u7d04\u4e2d_\u65e5\u671f'),
        ),
        migrations.AddField(
            model_name='countychaseprojectonebyone',
            name='stat_wrk_per_memo',
            field=models.CharField(max_length=256, null=True, verbose_name='\u52de\u52d9\u5c65\u7d04\u4e2d_\u5099\u8a3b'),
        ),
        migrations.AddField(
            model_name='project',
            name='abandoned_tender_count',
            field=models.IntegerField(null=True, verbose_name=b'\xe6\xb5\x81\xe5\xbb\xa2\xe6\xa8\x99\xe6\xac\xa1\xe6\x95\xb8'),
        ),
        migrations.AddField(
            model_name='project',
            name='tender_budget',
            field=models.DecimalField(null=True, verbose_name=b'\xe6\x8b\x9b\xe6\xa8\x99\xe9\xa0\x90\xe7\xae\x97(\xe5\x85\x83)', max_digits=16, decimal_places=3),
        ),
        migrations.AddField(
            model_name='project',
            name='tender_excess_funds',
            field=models.NullBooleanField(verbose_name='\u662f\u5426\u70ba\u5c6c\u6a19\u9918\u6b3e\u518d\u4f7f\u7528\u4e4b\u5de5\u7a0b'),
        ),
        migrations.AddField(
            model_name='plan',
            name='plan_class',
            field=models.ForeignKey(related_name='plan_plan_class_set', verbose_name=b'\xe8\xa8\x88\xe7\x95\xab\xe9\xa1\x9e\xe5\x88\xa5', to='fishuser.Option', null=True),
        ),
        migrations.AddField(
            model_name='countychaseprojectonebyone',
            name='sch_eng_plan_final_deadline',
            field=models.DateField(null=True, verbose_name='\u9810\u8a08_\u6838\u5b9a\u51fd\u52de\u52d9\u6c7a\u6a19\u671f\u9650'),
        ),
		migrations.AddField(
            model_name='countychaseprojectonebyone',
            name='act_eng_plan_final_deadline',
            field=models.DateField(null=True, verbose_name='\u5be6\u969b_\u6838\u5b9a\u51fd\u52de\u52d9\u6c7a\u6a19\u671f\u9650'),
        ),
		migrations.AddField(
            model_name='countychaseprojectonebyone',
            name='eng_plan_final_deadline_memo',
            field=models.CharField(max_length=256, null=True, verbose_name='\u6838\u5b9a\u51fd\u52de\u52d9\u6c7a\u6a19\u671f\u9650/\u5099\u8a3b'),
        ),
    ]
