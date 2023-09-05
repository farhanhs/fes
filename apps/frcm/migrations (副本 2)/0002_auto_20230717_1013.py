# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import frcm.models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('fishuser', '0003_auto_20230717_1013'),
        ('frcm', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='NoImportProject',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('project', models.ForeignKey(related_name='noimportproject_project', verbose_name='\u5de5\u7a0b\u6848', to='fishuser.Project')),
            ],
        ),
        migrations.CreateModel(
            name='Option',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('swarm', models.CharField(max_length=128, verbose_name='\u7fa4')),
                ('value', models.CharField(max_length=128, verbose_name='\u9078\u9805')),
            ],
        ),
        migrations.CreateModel(
            name='ProjectFile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=256)),
                ('ext', models.CharField(max_length=20)),
                ('file', models.FileField(null=True, upload_to=frcm.models._PROJECTFILE_BASE)),
                ('upload_time', models.DateTimeField()),
                ('memo', models.TextField(null=True, verbose_name='\u5099\u8a3b')),
                ('file_type', models.ForeignKey(related_name='projectfile_file_type', verbose_name='\u6a94\u6848\u5206\u5340', to='frcm.Option')),
                ('project', models.ForeignKey(related_name='projectfile_project', verbose_name='\u6240\u5c6c\u5de5\u7a0b\u6848', to='fishuser.Project')),
                ('tag', models.ManyToManyField(related_name='projectfile_tag', verbose_name='\u5de5\u7a0b\u6848\u6a19\u7c64', to='frcm.Option')),
                ('user', models.ForeignKey(related_name='projectfile_user', verbose_name='\u4e0a\u50b3\u8005', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='WarningCheck',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('check_date', models.DateField(verbose_name='\u88ab\u6aa2\u67e5\u7684\u65e5\u671f')),
                ('start_check_time', models.DateTimeField(verbose_name='\u958b\u59cb\u6aa2\u67e5\u6642\u9593')),
                ('end_check_time', models.DateTimeField(null=True, verbose_name='\u7d50\u675f\u6aa2\u67e5\u6642\u9593')),
                ('email', models.BooleanField(default=False, verbose_name='\u662f\u5426\u6709Email\u901a\u77e5')),
                ('start_email_time', models.DateTimeField(null=True, verbose_name='\u958b\u59cbEmail\u6642\u9593')),
                ('end_email_time', models.DateTimeField(null=True, verbose_name='\u7d50\u675fEmail\u6642\u9593')),
            ],
        ),
        migrations.CreateModel(
            name='WarningMailList',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('user', models.ForeignKey(related_name='warningmaillist_user', verbose_name='\u5e33\u865f', to=settings.AUTH_USER_MODEL, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='WarningProject',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('diff_progress', models.BooleanField(default=False, verbose_name='\u76e3\u9020\u71df\u9020\u9032\u5ea6\u4e0d\u4e00\u81f4>10%')),
                ('diff_progress_memo', models.TextField(null=True, verbose_name='\u8aaa\u660e')),
                ('diff_progress_explanation', models.TextField(null=True, verbose_name='\u5ee0\u5546\u56de\u8986\u6539\u5584\u8aaa\u660e')),
                ('delay_progress', models.BooleanField(default=False, verbose_name='\u9032\u5ea6\u843d\u5f8c(\u76e3\u9020)>10%')),
                ('delay_progress_memo', models.TextField(null=True, verbose_name='\u8aaa\u660e')),
                ('delay_progress_explanation', models.TextField(null=True, verbose_name='\u5ee0\u5546\u56de\u8986\u6539\u5584\u8aaa\u660e')),
                ('dailyreport_no_report', models.BooleanField(default=False, verbose_name='\u65e5\u5831\u8868\u672a\u586b\u5beb\u8d85\u904e7\u65e5')),
                ('dailyreport_no_report_memo', models.TextField(null=True, verbose_name='\u8aaa\u660e')),
                ('dailyreport_no_report_explanation', models.TextField(null=True, verbose_name='\u5ee0\u5546\u56de\u8986\u6539\u5584\u8aaa\u660e')),
                ('over_progress', models.BooleanField(default=False, verbose_name='\u9032\u5ea6\u8d85\u904e110%')),
                ('over_progress_memo', models.TextField(null=True, verbose_name='\u8aaa\u660e')),
                ('over_progress_explanation', models.TextField(null=True, verbose_name='\u5ee0\u5546\u56de\u8986\u6539\u5584\u8aaa\u660e')),
                ('no_engphoto', models.BooleanField(default=False, verbose_name='\u9032\u5ea6\u8d85\u904e10%\uff0c\u76f8\u7247\u6578\u91cf\u70ba0\u5f35\u8005')),
                ('no_engphoto_memo', models.TextField(null=True, verbose_name='\u8aaa\u660e')),
                ('no_engphoto_explanation', models.TextField(null=True, verbose_name='\u5ee0\u5546\u56de\u8986\u6539\u5584\u8aaa\u660e')),
                ('schedule_progress_error', models.BooleanField(default=False, verbose_name='\u9810\u5b9a\u9032\u5ea6\u8a2d\u5b9a\u672a\u5b8c\u6574')),
                ('schedule_progress_error_memo', models.TextField(null=True, verbose_name='\u8aaa\u660e')),
                ('schedule_progress_error_explanation', models.TextField(null=True, verbose_name='\u5ee0\u5546\u56de\u8986\u6539\u5584\u8aaa\u660e')),
                ('project', models.ForeignKey(related_name='warningproject_project', verbose_name='\u5de5\u7a0b\u6848', to='fishuser.Project')),
                ('warningcheck', models.ForeignKey(related_name='warningproject_warningcheck', verbose_name='\u54ea\u4e00\u500b\u7d00\u9304', to='frcm.WarningCheck')),
            ],
        ),
        migrations.AlterField(
            model_name='cityfiles',
            name='file',
            field=models.ImageField(null=True, upload_to=b'apps/frcm/media/frcm/cityfile/%Y%m%d'),
        ),
        migrations.AddField(
            model_name='noimportproject',
            name='warningcheck',
            field=models.ForeignKey(related_name='noimportproject_warningcheck', verbose_name='\u54ea\u4e00\u500b\u7d00\u9304', to='frcm.WarningCheck'),
        ),
        migrations.AlterUniqueTogether(
            name='warningproject',
            unique_together=set([('warningcheck', 'project')]),
        ),
        migrations.AlterUniqueTogether(
            name='noimportproject',
            unique_together=set([('warningcheck', 'project')]),
        ),
    ]
