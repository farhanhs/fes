# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('fishuser', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ExportCustomReport',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=64, verbose_name='\u540d\u7a31')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='\u5275\u5efa\u6642\u9593')),
            ],
        ),
        migrations.CreateModel(
            name='ExportCustomReportField',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('priority', models.IntegerField(verbose_name='\u512a\u5148\u6b0a')),
                ('export_custom_report', models.ForeignKey(to='project.ExportCustomReport')),
            ],
        ),
        migrations.CreateModel(
            name='Option2',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('swarm', models.CharField(max_length=128, verbose_name='\u7fa4')),
                ('value', models.CharField(max_length=128, verbose_name='\u9078\u9805')),
            ],
            options={
                'verbose_name': '\u9078\u9805',
                'verbose_name_plural': '\u9078\u9805',
            },
        ),
        migrations.CreateModel(
            name='RecordProjectProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=64, verbose_name='\u540d\u7a31')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='\u5275\u5efa\u6642\u9593')),
                ('owner', models.ForeignKey(verbose_name='\u4f7f\u7528\u8005', to=settings.AUTH_USER_MODEL)),
                ('projects', models.ManyToManyField(to='fishuser.Project', verbose_name='\u7d00\u9304\u5de5\u7a0b\u6848')),
            ],
        ),
        migrations.CreateModel(
            name='ReportField',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128, verbose_name='\u540d\u7a31')),
                ('value_method', models.CharField(max_length=256, verbose_name='\u53d6\u503c\u65b9\u5f0f')),
                ('tag', models.ForeignKey(to='project.Option2')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='option2',
            unique_together=set([('swarm', 'value')]),
        ),
        migrations.AddField(
            model_name='exportcustomreportfield',
            name='report_field',
            field=models.ForeignKey(to='project.ReportField'),
        ),
        migrations.AddField(
            model_name='exportcustomreport',
            name='fields',
            field=models.ManyToManyField(to='project.ReportField', verbose_name='\u81ea\u5b9a\u6b04\u4f4d', through='project.ExportCustomReportField'),
        ),
        migrations.AddField(
            model_name='exportcustomreport',
            name='owner',
            field=models.ForeignKey(verbose_name='\u4f7f\u7528\u8005', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='reportfield',
            unique_together=set([('tag', 'name')]),
        ),
    ]
