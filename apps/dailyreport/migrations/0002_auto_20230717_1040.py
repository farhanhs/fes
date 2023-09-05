# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from decimal import Decimal


class Migration(migrations.Migration):

    dependencies = [
        ('dailyreport', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='engprofile',
            name='schedule_progress',
            field=models.DecimalField(default=Decimal('0'), verbose_name='\u9810\u5b9a\u9032\u5ea6', max_digits=16, decimal_places=2),
        ),
        migrations.AddField(
            model_name='engprofile',
            name='scheduled_completion_day',
            field=models.DateField(null=True, verbose_name='\u9810\u8a08\u5b8c\u5de5\u65e5\u671f'),
        ),
        migrations.AddField(
            model_name='report',
            name='has_insurance',
            field=models.IntegerField(default=3, verbose_name='\u78ba\u8a8d\u65b0\u9032\u52de\u5de5\u662f\u5426\u63d0\u5831\u52de\u5de5\u4fdd\u96aa(\u6216\u5176\u4ed6\u5546\u696d\u4fdd\u96aa)\u8cc7\u6599\u53ca\u5b89\u5168\u885b\u751f\u6559\u80b2\u8a13\u7df4\u7d00\u9304'),
        ),
        migrations.AddField(
            model_name='report',
            name='i_pre_check',
            field=models.TextField(null=True, verbose_name='(\u4e00)\u65bd\u5de5\u5ee0\u5546\u65bd\u5de5\u524d\u6aa2\u67e5\u4e8b\u9805\u8fa6\u7406\u60c5\u5f62\uff1a'),
        ),
        migrations.AddField(
            model_name='report',
            name='i_project_status',
            field=models.TextField(null=True, verbose_name='\u4e00\u3001\u5de5\u7a0b\u9032\u884c\u60c5\u6cc1(\u542b\u7d04\u5b9a\u4e4b\u91cd\u8981\u65bd\u5de5\u9805\u76ee\u53ca\u6578\u91cf)\uff1a'),
        ),
        migrations.AddField(
            model_name='report',
            name='pre_check',
            field=models.BooleanField(default=False, verbose_name='\u65bd\u5de5\u5ee0\u5546\u65bd\u5de5\u524d\u6aa2\u67e5\u4e8b\u9805\u8fa6\u7406\u60c5\u5f62'),
        ),
        migrations.AddField(
            model_name='report',
            name='pre_education',
            field=models.BooleanField(default=False, verbose_name='\u5be6\u65bd\u52e4\u524d\u6559\u80b2(\u542b\u5de5\u5730\u9810\u9632\u707d\u8b8a\u53ca\u5371\u5bb3\u544a\u77e5)'),
        ),
        migrations.AddField(
            model_name='report',
            name='safety_equipment',
            field=models.BooleanField(default=False, verbose_name='\u6aa2\u67e5\u52de\u5de5\u500b\u4eba\u9632\u8b77\u5177'),
        ),
        migrations.AddField(
            model_name='reportholiday',
            name='has_insurance',
            field=models.IntegerField(default=3, verbose_name='\u78ba\u8a8d\u65b0\u9032\u52de\u5de5\u662f\u5426\u63d0\u5831\u52de\u5de5\u4fdd\u96aa(\u6216\u5176\u4ed6\u5546\u696d\u4fdd\u96aa)\u8cc7\u6599\u53ca\u5b89\u5168\u885b\u751f\u6559\u80b2\u8a13\u7df4\u7d00\u9304'),
        ),
        migrations.AddField(
            model_name='reportholiday',
            name='i_pre_check',
            field=models.TextField(null=True, verbose_name='(\u4e00)\u65bd\u5de5\u5ee0\u5546\u65bd\u5de5\u524d\u6aa2\u67e5\u4e8b\u9805\u8fa6\u7406\u60c5\u5f62\uff1a'),
        ),
        migrations.AddField(
            model_name='reportholiday',
            name='i_project_status',
            field=models.TextField(null=True, verbose_name='\u4e00\u3001\u5de5\u7a0b\u9032\u884c\u60c5\u6cc1(\u542b\u7d04\u5b9a\u4e4b\u91cd\u8981\u65bd\u5de5\u9805\u76ee\u53ca\u6578\u91cf)\uff1a'),
        ),
        migrations.AddField(
            model_name='reportholiday',
            name='pre_check',
            field=models.BooleanField(default=False, verbose_name='\u65bd\u5de5\u5ee0\u5546\u65bd\u5de5\u524d\u6aa2\u67e5\u4e8b\u9805\u8fa6\u7406\u60c5\u5f62'),
        ),
        migrations.AddField(
            model_name='reportholiday',
            name='pre_education',
            field=models.BooleanField(default=False, verbose_name='\u5be6\u65bd\u52e4\u524d\u6559\u80b2(\u542b\u5de5\u5730\u9810\u9632\u707d\u8b8a\u53ca\u5371\u5bb3\u544a\u77e5)'),
        ),
        migrations.AddField(
            model_name='reportholiday',
            name='safety_equipment',
            field=models.BooleanField(default=False, verbose_name='\u6aa2\u67e5\u52de\u5de5\u500b\u4eba\u9632\u8b77\u5177'),
        ),
        migrations.AlterField(
            model_name='report',
            name='c_describe_subcontractor',
            field=models.TextField(null=True, verbose_name='\u4e94\u3001\u5de5\u5730\u8077\u696d\u5b89\u5168\u885b\u751f\u4e8b\u9805\u4e4b\u7763\u5c0e\u3001\u516c\u5171\u74b0\u5883\u8207\u5b89\u5168\u4e4b\u7dad\u8b77\u53ca\u5176\u4ed6\u5de5\u5730\u884c\u653f\u4e8b\u52d9\uff1a'),
        ),
        migrations.AlterField(
            model_name='report',
            name='c_note',
            field=models.TextField(null=True, verbose_name='\u516b\u3001\u91cd\u8981\u4e8b\u9805\u7d00\u9304\uff1a'),
        ),
        migrations.AlterField(
            model_name='report',
            name='c_notify',
            field=models.TextField(null=True, verbose_name='\u4e03\u3001\u901a\u77e5\u5354\u529b\u5ee0\u5546\u8fa6\u7406\u4e8b\u9805\uff1a'),
        ),
        migrations.AlterField(
            model_name='report',
            name='c_sampling',
            field=models.TextField(null=True, verbose_name='\u516d\u3001\u65bd\u5de5\u53d6\u6a23\u8a66\u9a57\u7d00\u9304\uff1a'),
        ),
        migrations.AlterField(
            model_name='report',
            name='describe_subcontractor',
            field=models.TextField(null=True, verbose_name='\u56db\u3001\u7763\u5c0e\u5de5\u5730\u8077\u696d\u5b89\u5168\u885b\u751f\u4e8b\u9805\uff1a'),
        ),
        migrations.AlterField(
            model_name='report',
            name='note',
            field=models.TextField(null=True, verbose_name='\u4e8c\u3001\u76e3\u7763\u4f9d\u7167\u8a2d\u8a08\u5716\u8aaa\u65bd\u5de5(\u542b\u7d04\u5b9a\u4e4b\u6aa2\u9a57\u505c\u7559\u9ede\u53ca\u65bd\u5de5\u62bd\u67e5\u7b49\u60c5\u5f62)\uff1a'),
        ),
        migrations.AlterField(
            model_name='report',
            name='notify',
            field=models.TextField(null=True, verbose_name='\u4e94\u3001\u5176\u4ed6\u7d04\u5b9a\u76e3\u9020\u4e8b\u9805(\u542b\u91cd\u8981\u4e8b\u9805\u7d00\u9304\u3001\u4e3b\u8fa6\u6a5f\u95dc\u6307\u793a\u53ca\u901a\u77e5\u5ee0\u5546\u8fa6\u7406\u4e8b\u9805\u7b49)\uff1a'),
        ),
        migrations.AlterField(
            model_name='report',
            name='sampling',
            field=models.TextField(null=True, verbose_name='\u4e09\u3001\u67e5\u6838\u6750\u6599\u898f\u683c\u53ca\u54c1\u8cea(\u542b\u7d04\u5b9a\u4e4b\u6aa2\u9a57\u505c\u7559\u9ede\u3001\u6750\u6599\u8a2d\u5099\u7ba1\u5236\u53ca\u6aa2\uff08\u8a66\uff09\u9a57\u7b49\u62bd\u9a57\u60c5\u5f62)\uff1a'),
        ),
        migrations.AlterField(
            model_name='version',
            name='engs_price',
            field=models.DecimalField(verbose_name='\u8a72\u7248\u672c\u5951\u7d04\u7e3d\u50f9', max_digits=16, decimal_places=4),
        ),
        migrations.AlterField(
            model_name='version',
            name='schedule_price',
            field=models.DecimalField(verbose_name='\u8a72\u7248\u672c\u9032\u5ea6\u7e3d\u50f9', max_digits=16, decimal_places=4),
        ),
    ]
