# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import supervise.models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('fishuser', '0001_initial'),
        ('general', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Edit',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('user', models.OneToOneField(related_name='supervise_user_profile', verbose_name='\u5e33\u865f', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Error',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('context', models.CharField(max_length=1024, verbose_name='\u7f3a\u5931\u5167\u5bb9')),
                ('improve_result', models.TextField(null=True, verbose_name='\u6539\u5584\u5c0d\u7b56\u53ca\u7d50\u679c')),
                ('date', models.DateField(null=True, verbose_name='\u532f\u5165\u65e5\u671f')),
                ('memo', models.TextField(null=True, verbose_name='\u5099\u8a3b')),
            ],
            options={
                'verbose_name': '\u7f3a\u5931\u9805\u76ee',
                'verbose_name_plural': '\u7f3a\u5931\u9805\u76ee',
            },
        ),
        migrations.CreateModel(
            name='ErrorContent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('no', models.CharField(max_length=64, verbose_name='\u7f3a\u5931\u7de8\u865f')),
                ('introduction', models.TextField(verbose_name='\u7f3a\u5931\u8aaa\u660e')),
            ],
        ),
        migrations.CreateModel(
            name='ErrorImprovePhoto',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('before', models.ImageField(null=True, upload_to=supervise.models._ERROR_FILE_UPLOAD_TO)),
                ('before_memo', models.TextField(null=True, verbose_name='\u6539\u5584\u524d\u8aaa\u660e')),
                ('middle', models.ImageField(null=True, upload_to=supervise.models._ERROR_FILE_UPLOAD_TO)),
                ('middle_memo', models.TextField(null=True, verbose_name='\u6539\u5584\u4e2d\u8aaa\u660e')),
                ('after', models.ImageField(null=True, upload_to=supervise.models._ERROR_FILE_UPLOAD_TO)),
                ('after_memo', models.TextField(null=True, verbose_name='\u6539\u5584\u5f8c\u8aaa\u660e')),
            ],
        ),
        migrations.CreateModel(
            name='ErrorLevel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=4, verbose_name='\u7f3a\u5931\u7a0b\u5ea6')),
            ],
            options={
                'verbose_name': '\u7f3a\u5931\u7a0b\u5ea6',
                'verbose_name_plural': '\u7f3a\u5931\u7a0b\u5ea6',
            },
        ),
        migrations.CreateModel(
            name='ErrorPhotoFile',
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
            name='Guide',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=24, verbose_name='\u59d3\u540d')),
            ],
            options={
                'verbose_name': '\u7763\u5c0e\u4eba\u54e1',
                'verbose_name_plural': '\u7763\u5c0e\u4eba\u54e1',
            },
        ),
        migrations.CreateModel(
            name='Option',
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
            name='PCC_Project',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('uid', models.CharField(unique=True, max_length=255, verbose_name='\u6a19\u6848\u7de8\u865f')),
                ('implementation_department', models.CharField(max_length=255, null=True, verbose_name='\u57f7\u884c\u6a5f\u95dc')),
                ('name', models.CharField(max_length=255, null=True, verbose_name='\u6a19\u6848\u540d\u7a31')),
                ('s_public_date', models.DateField(null=True, verbose_name='\u9810\u5b9a\u516c\u544a\u65e5\u671f')),
                ('r_decide_tenders_date', models.DateField(null=True, verbose_name='\u5be6\u969b\u6c7a\u6a19\u65e5\u671f')),
                ('contract_budget', models.FloatField(null=True, verbose_name='\u767c\u5305\u9810\u7b97')),
                ('decide_tenders_price', models.FloatField(null=True, verbose_name='\u6c7a\u6a19\u91d1\u984d')),
                ('year', models.IntegerField(null=True, verbose_name='\u5e74\u5ea6')),
                ('month', models.IntegerField(null=True, verbose_name='\u6708\u4efd')),
                ('percentage_of_predict_progress', models.FloatField(null=True, verbose_name='\u9810\u5b9a\u9032\u5ea6')),
                ('percentage_of_real_progress', models.FloatField(null=True, verbose_name='\u5be6\u969b\u9032\u5ea6')),
                ('percentage_of_dulta', models.FloatField(null=True, verbose_name='\u5dee\u7570')),
            ],
        ),
        migrations.CreateModel(
            name='SuperviseCase',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('uid', models.CharField(max_length=255, null=True, verbose_name='\u6a19\u6848\u7de8\u865f')),
                ('date', models.DateField(verbose_name='\u7763\u5c0e\u65e5\u671f')),
                ('plan', models.CharField(max_length=512, verbose_name='\u5217\u7ba1\u8a08\u756b\u540d\u7a31')),
                ('project', models.CharField(max_length=512, verbose_name='\u6a19\u6848\u540d\u7a31')),
                ('project_organizer_agencies', models.CharField(max_length=512, verbose_name='\u6a19\u6848\u4e3b\u8fa6\u6a5f\u95dc')),
                ('project_manage_unit', models.CharField(max_length=128, verbose_name='\u5c08\u6848\u7ba1\u7406\u55ae\u4f4d')),
                ('designer', models.CharField(max_length=128, verbose_name='\u8a2d\u8a08\u55ae\u4f4d')),
                ('inspector', models.CharField(max_length=128, verbose_name='\u76e3\u9020\u55ae\u4f4d')),
                ('construct', models.CharField(max_length=512, verbose_name='\u627f\u5305\u5546')),
                ('budget_price', models.DecimalField(null=True, verbose_name='\u9810\u7b97\u91d1\u984d(\u5343\u5143)', max_digits=16, decimal_places=3)),
                ('contract_price', models.DecimalField(null=True, verbose_name='\u5951\u7d04\u91d1\u984d(\u5343\u5143)', max_digits=16, decimal_places=3)),
                ('contract_price_change', models.DecimalField(null=True, verbose_name='\u5951\u7d04\u91d1\u984d(\u5343\u5143)\u8b8a\u66f4\u5f8c', max_digits=16, decimal_places=3)),
                ('info', models.TextField(verbose_name='\u5de5\u7a0b\u6982\u8981')),
                ('progress_date', models.DateField(null=True, verbose_name='\u9032\u5ea6\u7d00\u9304\u65e5\u671f')),
                ('scheduled_progress', models.DecimalField(null=True, verbose_name='\u5de5\u7a0b\u9810\u8a08\u7d2f\u8a08\u9032\u5ea6', max_digits=16, decimal_places=4)),
                ('actual_progress', models.DecimalField(null=True, verbose_name='\u5de5\u7a0b\u5be6\u969b\u7d2f\u8a08\u9032\u5ea6', max_digits=16, decimal_places=4)),
                ('scheduled_money', models.DecimalField(null=True, verbose_name='\u5de5\u7a0b\u9810\u5b9a\u7d2f\u8a08\u91d1\u984d(\u5343\u5143)', max_digits=16, decimal_places=3)),
                ('actual_money', models.DecimalField(null=True, verbose_name='\u5de5\u7a0b\u5be6\u969b\u7d2f\u8a08\u91d1\u984d(\u5343\u5143)', max_digits=16, decimal_places=3)),
                ('progress_info', models.TextField(null=True, verbose_name='\u76ee\u524d\u65bd\u5de5\u6982\u6cc1')),
                ('start_date', models.DateField(null=True, verbose_name='\u958b\u5de5\u65e5\u671f')),
                ('expected_completion_date', models.DateField(null=True, verbose_name='\u9810\u8a08\u5b8c\u5de5\u65e5\u671f')),
                ('expected_completion_date_change', models.DateField(null=True, verbose_name='\u9810\u8a08\u5b8c\u5de5\u65e5\u671f\u8b8a\u66f4\u5f8c')),
                ('score', models.DecimalField(verbose_name='\u7763\u5c0e\u5206\u6578', max_digits=5, decimal_places=2)),
                ('merit', models.TextField(verbose_name='\u512a\u9ede')),
                ('advise', models.TextField(verbose_name='\u5efa\u8b70\u4e8b\u9805(\u898f\u5283\u8a2d\u8a08\u554f\u984c)')),
                ('advise_improve_result', models.TextField(null=True, verbose_name='\u6539\u5584\u5c0d\u7b56\u53ca\u7d50\u679c')),
                ('advise_date', models.DateField(null=True, verbose_name='\u6539\u5584\u65e5\u671f')),
                ('advise_memo', models.TextField(null=True, verbose_name='\u5099\u8a3b')),
                ('other_advise', models.TextField(verbose_name='\u5efa\u8b70\u4e8b\u9805(\u5176\u4ed6\u5efa\u8b70)')),
                ('other_improve_result', models.TextField(null=True, verbose_name='\u6539\u5584\u5c0d\u7b56\u53ca\u7d50\u679c')),
                ('other_date', models.DateField(null=True, verbose_name='\u6539\u5584\u65e5\u671f')),
                ('other_memo', models.TextField(null=True, verbose_name='\u5099\u8a3b')),
                ('cdate', models.DateField(verbose_name='\u532f\u5165\u65e5\u671f')),
                ('inspector_deduction', models.IntegerField(default=0, verbose_name='\u76e3\u9020\u6263\u9ede')),
                ('construct_deduction', models.IntegerField(default=0, verbose_name='\u71df\u9020\u6263\u9ede')),
                ('organizer_deduction', models.IntegerField(default=0, verbose_name='\u4e3b\u8fa6\u6263\u9ede')),
                ('project_manage_deduction', models.IntegerField(default=0, verbose_name='\u5c08\u6848\u7ba1\u7406\u6263\u9ede')),
                ('test', models.TextField(verbose_name='\u6aa2\u9a57\u62c6\u9a57')),
                ('captain', models.ManyToManyField(related_name='captain_set', verbose_name=b'\xe9\xa0\x98\xe9\x9a\x8a', to='supervise.Guide')),
                ('fes_project', models.ForeignKey(verbose_name='\u5c0d\u61c9FES\u7cfb\u7d71\u5de5\u7a0b\u6848', to='fishuser.Project', null=True)),
                ('inguide', models.ManyToManyField(related_name='inguide_set', verbose_name=b'\xe5\x85\xa7\xe8\x81\x98\xe5\xa7\x94\xe5\x93\xa1', to='supervise.Guide')),
                ('location', models.ForeignKey(related_name='location_set', verbose_name='\u5730\u9ede', to='general.Place', null=True)),
                ('outguide', models.ManyToManyField(related_name='outguide_set', verbose_name=b'\xe5\xa4\x96\xe8\x81\x98\xe5\xa7\x94\xe5\x93\xa1', to='supervise.Guide')),
                ('place', models.ForeignKey(related_name='place_set', verbose_name='\u7e23\u5e02', to='general.Place')),
                ('subordinate_agencies_unit', models.ForeignKey(verbose_name='\u6a19\u6848\u6240\u5c6c\u5de5\u7a0b\u4e3b\u7ba1\u6a5f\u95dc', to='general.Unit', null=True)),
                ('worker', models.ManyToManyField(related_name='worker_set', verbose_name=b'\xe5\xb7\xa5\xe4\xbd\x9c\xe4\xba\xba\xe5\x93\xa1', to='supervise.Guide')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='option',
            unique_together=set([('swarm', 'value')]),
        ),
        migrations.AddField(
            model_name='errorphotofile',
            name='supervisecase',
            field=models.ForeignKey(verbose_name='\u7763\u5c0e\u6848', to='supervise.SuperviseCase'),
        ),
        migrations.AddField(
            model_name='errorimprovephoto',
            name='case',
            field=models.ForeignKey(to='supervise.SuperviseCase', null=True),
        ),
        migrations.AddField(
            model_name='errorimprovephoto',
            name='error',
            field=models.ForeignKey(to='supervise.Error', null=True),
        ),
        migrations.AddField(
            model_name='errorimprovephoto',
            name='improve_type',
            field=models.ForeignKey(verbose_name='\u6539\u5584\u5c0d\u5411swarm="error_improve_type"', to='supervise.Option', null=True),
        ),
        migrations.AddField(
            model_name='error',
            name='case',
            field=models.ForeignKey(to='supervise.SuperviseCase'),
        ),
        migrations.AddField(
            model_name='error',
            name='ec',
            field=models.ForeignKey(to='supervise.ErrorContent'),
        ),
        migrations.AddField(
            model_name='error',
            name='level',
            field=models.ForeignKey(to='supervise.ErrorLevel'),
        ),
    ]
