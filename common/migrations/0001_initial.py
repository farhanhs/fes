# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import common.models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BugPage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('code', models.CharField(max_length=4, null=True, verbose_name='\u932f\u8aa4\u78bc\u4ee3\u78bc')),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='\u7d00\u9304\u6642\u9593')),
                ('html', models.TextField(verbose_name='\u9664\u932f\u9801\u9762\u5167\u5bb9')),
                ('is_solved', models.BooleanField(default=False, verbose_name='\u662f\u5426\u89e3\u6c7a')),
            ],
            bases=(models.Model, common.models.SelfBaseObject),
        ),
        migrations.CreateModel(
            name='CustomField',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.IntegerField(verbose_name='\u5728 content_type \u4e2d\u7684 row id')),
                ('field_name', models.CharField(max_length=64, verbose_name='\u6b04\u4f4d\u540d\u7a31')),
                ('value', models.CharField(max_length=256)),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
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
            name='Log',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='\u7d00\u9304\u6642\u9593')),
                ('object_id', models.IntegerField(verbose_name='\u7269\u4ef6\u7de8\u865f')),
                ('object_repr', models.TextField(verbose_name='\u7269\u4ef6\u63cf\u8ff0')),
                ('action_repr', models.CharField(max_length=256, verbose_name='\u57f7\u884c\u52d5\u4f5c\u7684\u63cf\u8ff0')),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Option',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('swarm', models.CharField(max_length=32, verbose_name='\u7fa4')),
                ('value', models.CharField(max_length=64, verbose_name='\u9078\u9805')),
            ],
        ),
        migrations.CreateModel(
            name='SelfMetaModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('arriveat_user', models.CharField(max_length=128, verbose_name='\u4ee5\u9017\u865f\u5206\u9694\u7684\u6b04\u4f4d\u540d\uff0c\u7d00\u9304\u5982\u4f55\u627e\u5230 User')),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
                ('log_type', models.ManyToManyField(to='common.Option')),
            ],
        ),
        migrations.CreateModel(
            name='VerifyCode',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.CharField(max_length=32, verbose_name='\u5716\u7247\u4e0a\u6240\u986f\u73fe\u7684\u78bc')),
                ('isdone', models.BooleanField(default=False, verbose_name='\u662f\u5426\u4f7f\u7528\u904e')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='option',
            unique_together=set([('swarm', 'value')]),
        ),
        migrations.AddField(
            model_name='log',
            name='log_type',
            field=models.ForeignKey(to='common.Option'),
        ),
        migrations.AddField(
            model_name='log',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='holiday',
            name='type',
            field=models.ForeignKey(related_name='dailyreport_holiday_type', to='common.Option'),
        ),
    ]
