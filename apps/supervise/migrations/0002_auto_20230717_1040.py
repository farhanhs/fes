# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import supervise.models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('supervise', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CaseFile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('upload_date', models.DateField(verbose_name='\u4e0a\u50b3\u65e5\u671f')),
                ('ext', models.CharField(max_length=10, null=True, verbose_name='\u526f\u6a94\u540d')),
                ('name', models.CharField(default=b'', max_length=256, null=True, verbose_name='\u6a94\u6848\u540d')),
                ('file', models.ImageField(null=True, upload_to=supervise.models._FILE_UPLOAD_TO)),
                ('memo', models.CharField(max_length=2048, null=True, verbose_name='\u5099\u8a3b\u8aaa\u660e')),
            ],
        ),
        migrations.CreateModel(
            name='ErrorImproveFile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('upload_date', models.DateField(verbose_name='\u4e0a\u50b3\u65e5\u671f')),
                ('ext', models.CharField(max_length=10, null=True, verbose_name='\u526f\u6a94\u540d')),
                ('name', models.CharField(default=b'', max_length=256, null=True, verbose_name='\u6a94\u6848\u540d')),
                ('file', models.FileField(null=True, upload_to=supervise.models._ERRORFILE_UPLOAD_TO)),
            ],
        ),
        migrations.CreateModel(
            name='PCC_sync_record',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ip', models.CharField(max_length=15, null=True, verbose_name='IP')),
                ('field_name', models.CharField(max_length=128, verbose_name='\u4fee\u6539\u6b04\u4f4d\u540d\u7a31')),
                ('old_value', models.TextField(null=True, verbose_name='\u820a\u503c')),
                ('new_value', models.TextField(null=True, verbose_name='\u65b0\u503c')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='\u4fee\u6539\u6642\u9593')),
            ],
        ),
        migrations.AddField(
            model_name='error',
            name='guide',
            field=models.ForeignKey(related_name='error_guide', verbose_name=b'\xe5\xa7\x94\xe5\x93\xa1', to='supervise.Guide', null=True),
        ),
        migrations.AddField(
            model_name='guide',
            name='is_default',
            field=models.BooleanField(default=False, verbose_name='\u662f\u5426\u70ba\u5e38\u7528'),
        ),
        migrations.AddField(
            model_name='supervisecase',
            name='construct_deduction_memo',
            field=models.TextField(null=True, verbose_name='\u71df\u9020\u6263\u9ede\u8aaa\u660e'),
        ),
        migrations.AddField(
            model_name='supervisecase',
            name='finish_no',
            field=models.CharField(default='', max_length=512, verbose_name='\u540c\u610f\u7d50\u6848\u6587\u865f'),
        ),
        migrations.AddField(
            model_name='supervisecase',
            name='inspector_deduction_memo',
            field=models.TextField(null=True, verbose_name='\u76e3\u9020\u6263\u9ede\u8aaa\u660e'),
        ),
        migrations.AddField(
            model_name='supervisecase',
            name='is_improve',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='supervisecase',
            name='is_test',
            field=models.BooleanField(default=False, verbose_name='\u662f\u5426\u947d\u5fc3'),
        ),
        migrations.AddField(
            model_name='supervisecase',
            name='organizer_deduction_memo',
            field=models.TextField(null=True, verbose_name='\u4e3b\u8fa6\u6263\u9ede\u8aaa\u660e'),
        ),
        migrations.AddField(
            model_name='supervisecase',
            name='project_manage_deduction_memo',
            field=models.TextField(null=True, verbose_name='\u5c08\u6848\u7ba1\u7406\u6263\u9ede\u8aaa\u660e'),
        ),
        migrations.AddField(
            model_name='supervisecase',
            name='test_date',
            field=models.DateField(null=True, verbose_name='\u6539\u5584\u65e5\u671f'),
        ),
        migrations.AddField(
            model_name='supervisecase',
            name='test_memo',
            field=models.TextField(null=True, verbose_name='\u5099\u8a3b'),
        ),
        migrations.AddField(
            model_name='supervisecase',
            name='test_result',
            field=models.TextField(null=True, verbose_name='\u947d\u5fc3\u7d50\u679c'),
        ),
        migrations.AddField(
            model_name='supervisecase',
            name='total_deduction',
            field=models.IntegerField(default=0, verbose_name='\u7e3d\u6263\u9ede'),
        ),
        migrations.AlterField(
            model_name='error',
            name='date',
            field=models.DateField(null=True, verbose_name='\u6539\u5584\u65e5\u671f'),
        ),
        migrations.AlterField(
            model_name='error',
            name='level',
            field=models.ForeignKey(default=2, to='supervise.ErrorLevel'),
        ),
        migrations.AlterField(
            model_name='errorphotofile',
            name='file',
            field=models.ImageField(null=True, upload_to=supervise.models._FILE_UPLOAD_TO),
        ),
        migrations.AddField(
            model_name='pcc_sync_record',
            name='case',
            field=models.ForeignKey(related_name='pcc_sync_record_case', verbose_name='\u7763\u5c0e\u6848', to='supervise.SuperviseCase'),
        ),
        migrations.AddField(
            model_name='pcc_sync_record',
            name='user',
            field=models.ForeignKey(related_name='pcc_sync_record_user', verbose_name='\u5e33\u865f', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='errorimprovefile',
            name='error',
            field=models.ForeignKey(verbose_name='\u7f3a\u5931', to='supervise.Error'),
        ),
        migrations.AddField(
            model_name='casefile',
            name='supervisecase',
            field=models.ForeignKey(verbose_name='\u7763\u5c0e\u6848', to='supervise.SuperviseCase'),
        ),
    ]
