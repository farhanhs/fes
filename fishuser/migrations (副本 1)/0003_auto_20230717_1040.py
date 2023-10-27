# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import fishuser.models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('general', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('fishuser', '0002_auto_20221104_1044'),
    ]

    operations = [
        migrations.CreateModel(
            name='CountyChaseProjectOneToManyPayout',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('self_payout', models.DecimalField(default=b'0', verbose_name='\u672c\u7f72\u5be6\u652f\u6578(\u5143)(G)', max_digits=16, decimal_places=3)),
                ('self_unpay', models.DecimalField(default=b'0', verbose_name='\u672c\u7f72\u61c9\u4ed8\u672a\u4ed8\u6578(\u5143)(\u88dc\u52a9\u6b3e)(H)=(E)*(F)-(G)', max_digits=16, decimal_places=3)),
                ('local_payout', models.DecimalField(default=b'0', verbose_name='\u5730\u65b9\u5be6\u652f\u6578(\u5143)(G)', max_digits=16, decimal_places=3)),
                ('local_unpay', models.DecimalField(default=b'0', verbose_name='\u5730\u65b9\u61c9\u4ed8\u672a\u4ed8\u6578(\u5143)(\u88dc\u52a9\u6b3e)(H)=(E)*(F)-(G)', max_digits=16, decimal_places=3)),
                ('surplus', models.DecimalField(default=b'0', verbose_name='\u7d50\u9918\u6578', max_digits=16, decimal_places=3)),
            ],
        ),
        migrations.CreateModel(
            name='PlanReserve',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('year', models.IntegerField(verbose_name=b'\xe5\xb9\xb4\xe5\xba\xa6')),
                ('value', models.DecimalField(null=True, verbose_name=b'\xe8\xb3\x87\xe6\x9c\xac\xe9\x96\x80 \xe8\x87\xaa\xe8\xbe\xa6\xe9\xa0\x90\xe7\xae\x97\xe9\xa1\x8d(\xe5\x85\x83)', max_digits=16, decimal_places=3)),
                ('memo', models.TextField(null=True, verbose_name='\u5099\u8a3b')),
            ],
        ),
        migrations.CreateModel(
            name='SystemInformation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start_date', models.DateField(null=True, verbose_name=b'\xe4\xba\x8b\xe4\xbb\xb6\xe9\x96\x8b\xe5\xa7\x8b\xe6\x97\xa5\xe6\x9c\x9f')),
                ('on_login_page', models.BooleanField(default=False, verbose_name='\u662f\u5426\u8981\u986f\u793a\u518d\u767b\u5165\u9801\u9762')),
                ('title', models.TextField(null=True, verbose_name='\u767c\u4f48\u8a0a\u606f\u77ed\u5167\u5bb9')),
                ('memo', models.TextField(null=True, verbose_name='\u767c\u4f48\u8a0a\u606f\u9577\u5167\u5bb9')),
                ('user', models.ForeignKey(verbose_name='\u767c\u4f48\u8005', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='SystemInformationFile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(default=b'', max_length=256, null=True, verbose_name=b'\xe6\xaa\x94\xe6\xa1\x88\xe5\x90\x8d')),
                ('file', models.FileField(null=True, upload_to=fishuser.models._UPLOAD_TO_SYSTEM_INFORMATION)),
                ('systeminformation', models.ForeignKey(verbose_name='\u7cfb\u7d71\u516c\u544a', to='fishuser.SystemInformation', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='UnitManager',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=64, null=True, verbose_name='\u59d3\u540d')),
                ('phone', models.CharField(max_length=64, null=True, verbose_name='\u9023\u7d61\u96fb\u8a71')),
                ('email', models.CharField(max_length=64, null=True, verbose_name='Email')),
                ('unit', models.ForeignKey(related_name='unitmanager_unit', verbose_name=b'\xe5\x96\xae\xe4\xbd\x8d', to='general.Unit')),
            ],
        ),
        migrations.AlterModelOptions(
            name='option',
            options={'verbose_name': '\u9078\u9805', 'verbose_name_plural': '\u9078\u9805', 'permissions': (('top_menu_management_system', '\u7b2c\u4e00\u5c64\u9078\u55ae_\u5de5\u7a0b\u7ba1\u8003\u7cfb\u7d71'), ('top_menu_remote_control_system', '\u7b2c\u4e00\u5c64\u9078\u55ae_\u9060\u7aef\u7ba1\u7406\u7cfb\u7d71'), ('top_menu_auditing_system', '\u7b2c\u4e00\u5c64\u9078\u55ae_\u67e5\u6838\u7cfb\u7d71'), ('top_menu_supervise_system', '\u7b2c\u4e00\u5c64\u9078\u55ae_\u7763\u5c0e\u7cfb\u7d71'), ('top_menu_harbor_system', '\u7b2c\u4e00\u5c64\u9078\u55ae_\u6f01\u6e2f\u8cc7\u8a0a\u7cfb\u7d71'), ('top_menu_account', '\u7b2c\u4e00\u5c64\u9078\u55ae_\u5e33\u865f\u7ba1\u7406'), ('sub_menu_management_system_search', '\u7b2c\u4e8c\u5c64\u9078\u55ae_\u5de5\u7a0b\u7ba1\u8003\u7cfb\u7d71_\u641c\u5c0b\u7ba1\u8003\u5de5\u7a0b'), ('sub_menu_management_system_plan', '\u7b2c\u4e8c\u5c64\u9078\u55ae_\u5de5\u7a0b\u7ba1\u8003\u7cfb\u7d71_\u8a08\u756b\u5217\u8868'), ('sub_menu_management_system_draft', '\u7b2c\u4e8c\u5c64\u9078\u55ae_\u5de5\u7a0b\u7ba1\u8003\u7cfb\u7d71_\u8349\u7a3f\u5323'), ('sub_menu_management_system_create', '\u7b2c\u4e8c\u5c64\u9078\u55ae_\u5de5\u7a0b\u7ba1\u8003\u7cfb\u7d71_\u65b0\u589e\u5de5\u7a0b\u6848'), ('sub_menu_management_system_city', '\u7b2c\u4e8c\u5c64\u9078\u55ae_\u5de5\u7a0b\u7ba1\u8003\u7cfb\u7d71_\u7e23\u5e02\u9032\u5ea6\u8ffd\u8e64'), ('sub_menu_management_system_manage_money', '\u7b2c\u4e8c\u5c64\u9078\u55ae_\u5de5\u7a0b\u7ba1\u8003\u7cfb\u7d71_\u81ea\u8fa6\u5de5\u7a0b\u7ba1\u7406\u8cbb'), ('sub_menu_management_system_manage_money_commission', '\u7b2c\u4e8c\u5c64\u9078\u55ae_\u5de5\u7a0b\u7ba1\u8003\u7cfb\u7d71_\u59d4\u8fa6\u5de5\u7a0b\u7ba1\u7406\u8cbb'), ('sub_menu_management_system_control_form', '\u7b2c\u4e8c\u5c64\u9078\u55ae_\u5de5\u7a0b\u7ba1\u8003\u7cfb\u7d71_\u6f01\u6e2f\u7ba1\u63a7\u8868'), ('sub_menu_remote_control_system_my', '\u7b2c\u4e8c\u5c64\u9078\u55ae_\u9060\u7aef\u7ba1\u7406\u7cfb\u7d71_\u6211\u7684\u5de5\u7a0b'), ('sub_menu_remote_control_system_import', '\u7b2c\u4e8c\u5c64\u9078\u55ae_\u9060\u7aef\u7ba1\u7406\u7cfb\u7d71_\u532f\u5165\u5de5\u7a0b'), ('sub_menu_remote_control_system_claim', '\u7b2c\u4e8c\u5c64\u9078\u55ae_\u9060\u7aef\u7ba1\u7406\u7cfb\u7d71_\u8a8d\u9818\u5de5\u7a0b'), ('sub_menu_remote_control_system_search', '\u7b2c\u4e8c\u5c64\u9078\u55ae_\u9060\u7aef\u7ba1\u7406\u7cfb\u7d71_\u641c\u5c0b\u9060\u7aef\u5de5\u7a0b'), ('sub_menu_remote_control_system_file', '\u7b2c\u4e8c\u5c64\u9078\u55ae_\u9060\u7aef\u7ba1\u7406\u7cfb\u7d71_\u6a94\u6848\u7ba1\u7406'), ('sub_menu_remote_control_system_proposal', '\u7b2c\u4e8c\u5c64\u9078\u55ae_\u9060\u7aef\u7ba1\u7406\u7cfb\u7d71_\u5de5\u7a0b\u63d0\u6848\u5340'), ('sub_menu_remote_control_system_statisticstable_money', '\u7b2c\u4e8c\u5c64\u9078\u55ae_\u9060\u7aef\u7ba1\u7406\u7cfb\u7d71_\u5ee0\u5546\u5f97\u6a19\u91d1\u984d\u6392\u884c'), ('sub_menu_supervise_system_create', '\u7b2c\u4e8c\u5c64\u9078\u55ae_\u7763\u5c0e\u7cfb\u7d71_\u65b0\u589e'), ('sub_menu_harbor_system_edit', '\u7b2c\u4e8c\u5c64\u9078\u55ae_\u6f01\u6e2f\u8cc7\u8a0a\u7cfb\u7d71_\u7de8\u8f2f\u8cc7\u8a0a'), ('sub_menu_harbor_system_edit_portinstallationrecord', '\u7b2c\u4e8c\u5c64\u9078\u55ae_\u6f01\u6e2f\u8cc7\u8a0a\u7cfb\u7d71_\u586b\u5831\u6f01\u6e2f\u8a2d\u65bd\u8a18\u9304'), ('sub_menu_warning_system_warninginfo', '\u7b2c\u4e8c\u5c64\u9078\u55ae_\u5de5\u7a0b\u9810\u8b66\u5167\u5bb9'))},
        ),
        migrations.RemoveField(
            model_name='countychaseprojectonebyone',
            name='check',
        ),
        migrations.RemoveField(
            model_name='countychaseprojectonebyone',
            name='close',
        ),
        migrations.RemoveField(
            model_name='countychaseprojectonebyone',
            name='total_money',
        ),
        migrations.AddField(
            model_name='budget',
            name='new',
            field=models.NullBooleanField(verbose_name='\u662f\u5426\u70ba\u6700\u65b0\u4e00\u7b46'),
        ),
        migrations.AddField(
            model_name='budget',
            name='plan',
            field=models.ForeignKey(related_name='budget_plan', verbose_name='\u8a08\u756b', to='fishuser.Plan', null=True),
        ),
        migrations.AddField(
            model_name='budget',
            name='priority',
            field=models.IntegerField(default=10000, verbose_name=b'\xe6\x8e\x92\xe5\xba\x8f'),
        ),
        migrations.AddField(
            model_name='budget',
            name='proportion',
            field=models.DecimalField(null=True, verbose_name=b'\xe8\xa3\x9c\xe5\x8a\xa9\xe6\xaf\x94\xe4\xbe\x8b', max_digits=16, decimal_places=3),
        ),
        migrations.AddField(
            model_name='countychaseprojectonebyone',
            name='act_eng_do_agree_plan',
            field=models.DateField(null=True, verbose_name='\u5be6\u969b_\u5de5\u7a0b_(\u5de5\u7a0b\u65bd\u505a)\u540c\u610f\u8a08\u756b'),
        ),
        migrations.AddField(
            model_name='countychaseprojectonebyone',
            name='act_eng_do_approved_plan',
            field=models.DateField(null=True, verbose_name='\u5be6\u969b_\u5de5\u7a0b_(\u5de5\u7a0b\u65bd\u505a)\u6838\u5b9a\u8a08\u756b'),
        ),
        migrations.AddField(
            model_name='countychaseprojectonebyone',
            name='act_eng_do_final',
            field=models.DateField(null=True, verbose_name='\u5be6\u969b_\u5de5\u7a0b_(\u5de5\u7a0b\u65bd\u505a)\u6c7a\u6a19'),
        ),
        migrations.AddField(
            model_name='countychaseprojectonebyone',
            name='act_eng_plan_acceptance',
            field=models.DateField(null=True, verbose_name='\u5be6\u969b_\u5de5\u7a0b_(\u8a2d\u8a08\u898f\u5283)\u9a57\u6536'),
        ),
        migrations.AddField(
            model_name='countychaseprojectonebyone',
            name='act_eng_plan_agree_plan',
            field=models.DateField(null=True, verbose_name='\u5be6\u969b_\u5de5\u7a0b_(\u8a2d\u8a08\u898f\u5283)\u540c\u610f\u8a08\u756b'),
        ),
        migrations.AddField(
            model_name='countychaseprojectonebyone',
            name='act_eng_plan_final',
            field=models.DateField(null=True, verbose_name='\u5be6\u969b_\u5de5\u7a0b_(\u8a2d\u8a08\u898f\u5283)\u6c7a\u6a19'),
        ),
        migrations.AddField(
            model_name='countychaseprojectonebyone',
            name='act_ser_do_acceptance',
            field=models.DateField(null=True, verbose_name='\u5be6\u969b_\u52de\u52d9_\u9a57\u6536'),
        ),
        migrations.AddField(
            model_name='countychaseprojectonebyone',
            name='eng_do_agree_plan_memo',
            field=models.CharField(max_length=256, null=True, verbose_name='\u5be6\u969b_\u5de5\u7a0b_(\u5de5\u7a0b\u65bd\u505a)\u540c\u610f\u8a08\u756b/\u5099\u8a3b'),
        ),
        migrations.AddField(
            model_name='countychaseprojectonebyone',
            name='eng_do_approved_plan_memo',
            field=models.CharField(max_length=256, null=True, verbose_name='\u5de5\u7a0b_(\u5de5\u7a0b\u65bd\u505a)\u6838\u5b9a\u8a08\u756b/\u5099\u8a3b'),
        ),
        migrations.AddField(
            model_name='countychaseprojectonebyone',
            name='eng_do_final_memo',
            field=models.CharField(max_length=256, null=True, verbose_name='\u5be6\u969b_\u5de5\u7a0b_(\u5de5\u7a0b\u65bd\u505a)\u6c7a\u6a19/\u5099\u8a3b'),
        ),
        migrations.AddField(
            model_name='countychaseprojectonebyone',
            name='eng_plan_acceptance_memo',
            field=models.CharField(max_length=256, null=True, verbose_name='\u5de5\u7a0b_(\u8a2d\u8a08\u898f\u5283)\u9a57\u6536/\u5099\u8a3b'),
        ),
        migrations.AddField(
            model_name='countychaseprojectonebyone',
            name='eng_plan_agree_plan_memo',
            field=models.CharField(max_length=256, null=True, verbose_name='\u5be6\u969b_\u5de5\u7a0b_(\u8a2d\u8a08\u898f\u5283)\u540c\u610f\u8a08\u756b/\u5099\u8a3b'),
        ),
        migrations.AddField(
            model_name='countychaseprojectonebyone',
            name='eng_plan_final_memo',
            field=models.CharField(max_length=256, null=True, verbose_name='\u5be6\u969b_\u5de5\u7a0b_(\u8a2d\u8a08\u898f\u5283)\u6c7a\u6a19/\u5099\u8a3b'),
        ),
        migrations.AddField(
            model_name='countychaseprojectonebyone',
            name='give_up_times',
            field=models.IntegerField(default=0, verbose_name=b'\xe6\x8b\x9b\xe6\xa8\x99\xe6\x9c\x9f\xe9\x96\x93\xe6\xb5\x81\xe6\xa8\x99\xe6\xac\xa1\xe6\x95\xb8'),
        ),
        migrations.AddField(
            model_name='countychaseprojectonebyone',
            name='sch_eng_do_agree_plan',
            field=models.DateField(null=True, verbose_name='\u9810\u8a08_\u5de5\u7a0b_(\u5de5\u7a0b\u65bd\u505a)\u540c\u610f\u8a08\u756b'),
        ),
        migrations.AddField(
            model_name='countychaseprojectonebyone',
            name='sch_eng_do_approved_plan',
            field=models.DateField(null=True, verbose_name='\u9810\u8a08_\u5de5\u7a0b_(\u5de5\u7a0b\u65bd\u505a)\u6838\u5b9a\u8a08\u756b'),
        ),
        migrations.AddField(
            model_name='countychaseprojectonebyone',
            name='sch_eng_do_final',
            field=models.DateField(null=True, verbose_name='\u9810\u8a08_\u5de5\u7a0b_(\u5de5\u7a0b\u65bd\u505a)\u6c7a\u6a19'),
        ),
        migrations.AddField(
            model_name='countychaseprojectonebyone',
            name='sch_eng_plan_acceptance',
            field=models.DateField(null=True, verbose_name='\u9810\u8a08_\u5de5\u7a0b_(\u8a2d\u8a08\u898f\u5283)\u9a57\u6536'),
        ),
        migrations.AddField(
            model_name='countychaseprojectonebyone',
            name='sch_eng_plan_agree_plan',
            field=models.DateField(null=True, verbose_name='\u9810\u8a08_\u5de5\u7a0b_(\u8a2d\u8a08\u898f\u5283)\u540c\u610f\u8a08\u756b'),
        ),
        migrations.AddField(
            model_name='countychaseprojectonebyone',
            name='sch_eng_plan_final',
            field=models.DateField(null=True, verbose_name='\u9810\u8a08_\u5de5\u7a0b_(\u8a2d\u8a08\u898f\u5283)\u6c7a\u6a19'),
        ),
        migrations.AddField(
            model_name='countychaseprojectonebyone',
            name='sch_ser_do_acceptance',
            field=models.DateField(null=True, verbose_name='\u9810\u8a08_\u52de\u52d9_\u9a57\u6536'),
        ),
        migrations.AddField(
            model_name='countychaseprojectonebyone',
            name='ser_do_acceptance_memo',
            field=models.CharField(max_length=256, null=True, verbose_name='\u5de5\u7a0b_\u52de\u52d9_\u9a57\u6536/\u5099\u8a3b'),
        ),
        migrations.AddField(
            model_name='countychaseprojectonebyone',
            name='test_date',
            field=models.DateField(null=True, verbose_name='\u6e2c\u8a66\u65e5\u671f'),
        ),
        migrations.AddField(
            model_name='countychaseprojectonebyone',
            name='total_budget',
            field=models.PositiveIntegerField(default=0, verbose_name=b'\xe5\xb7\xa5\xe7\xa8\x8b(\xe8\xa8\x88\xe7\x95\xab)\xe7\xb8\xbd\xe9\xa0\x90\xe7\xae\x97'),
        ),
        migrations.AddField(
            model_name='countychaseprojectonebyone',
            name='work_info',
            field=models.TextField(default='', verbose_name=b'\xe5\xb7\xa5\xe4\xbd\x9c(\xe8\xa8\x88\xe7\x95\xab)\xe5\x85\xa7\xe5\xae\xb9'),
        ),
        migrations.AddField(
            model_name='countychaseprojectonetomany',
            name='behind_memo',
            field=models.CharField(default='', max_length=2048, verbose_name='\u843d\u5f8c10%\u4ee5\u4e0a\u3001\u5c65\u7d04\u722d\u8b70\u6216\u505c\u5de5\u7b49\u8acb\u586b\u539f\u56e0\u53ca\u89e3\u6c7a\u5c0d\u7b56'),
        ),
        migrations.AddField(
            model_name='countychaseprojectonetomany',
            name='self_memo',
            field=models.CharField(default='', max_length=2048, verbose_name='\u7ba1\u8003\u5efa\u8b70(\u7531\u672c\u7f72\u586b\u5beb)'),
        ),
        migrations.AddField(
            model_name='countychaseprojectonetomany',
            name='surplus',
            field=models.DecimalField(default=b'0', verbose_name='\u7d50\u9918\u6578', max_digits=16, decimal_places=3),
        ),
        migrations.AddField(
            model_name='managemoney',
            name='is_commission',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='plan',
            name='year',
            field=models.IntegerField(default=107, verbose_name=b'\xe5\xb9\xb4\xe5\xba\xa6'),
        ),
        migrations.AddField(
            model_name='project',
            name='allowance',
            field=models.DecimalField(null=True, verbose_name=b'\xe8\xa3\x9c\xe5\x8a\xa9(\xe5\x8d\x83\xe5\x85\x83)', max_digits=16, decimal_places=4),
        ),
        migrations.AddField(
            model_name='project',
            name='allowance_revise',
            field=models.DecimalField(null=True, verbose_name=b'\xe8\xaa\xbf\xe8\xa3\x9c\xe5\x8a\xa9(\xe5\x8d\x83\xe5\x85\x83)', max_digits=16, decimal_places=4),
        ),
        migrations.AddField(
            model_name='project',
            name='cm_memo',
            field=models.CharField(max_length=512, null=True, verbose_name='\u8cbb\u7528\u5099\u8a3b'),
        ),
        migrations.AddField(
            model_name='project',
            name='cm_settlement_value',
            field=models.DecimalField(null=True, verbose_name='\u7d50\u7b97\u8cbb\u7528(\u5143)', max_digits=16, decimal_places=3),
        ),
        migrations.AddField(
            model_name='project',
            name='cm_value',
            field=models.DecimalField(null=True, verbose_name='\u5951\u7d04\u8cbb\u7528(\u5143)', max_digits=16, decimal_places=3),
        ),
        migrations.AddField(
            model_name='project',
            name='commission',
            field=models.DecimalField(null=True, verbose_name=b'\xe5\xa7\x94\xe8\xbe\xa6(\xe5\x8d\x83\xe5\x85\x83)', max_digits=16, decimal_places=4),
        ),
        migrations.AddField(
            model_name='project',
            name='commission_revise',
            field=models.DecimalField(null=True, verbose_name=b'\xe8\xaa\xbf\xe5\xa7\x94\xe8\xbe\xa6(\xe5\x8d\x83\xe5\x85\x83)', max_digits=16, decimal_places=4),
        ),
        migrations.AddField(
            model_name='project',
            name='control_form_memo',
            field=models.CharField(max_length=128, null=True, verbose_name='\u5099\u8a3b'),
        ),
        migrations.AddField(
            model_name='project',
            name='fund_1',
            field=models.DecimalField(null=True, verbose_name=b'\xe5\x9f\xba\xe9\x87\x911(\xe5\x8d\x83\xe5\x85\x83)', max_digits=16, decimal_places=4),
        ),
        migrations.AddField(
            model_name='project',
            name='fund_2',
            field=models.DecimalField(null=True, verbose_name=b'\xe5\x9f\xba\xe9\x87\x912(\xe5\x8d\x83\xe5\x85\x83)', max_digits=16, decimal_places=4),
        ),
        migrations.AddField(
            model_name='project',
            name='is_public',
            field=models.BooleanField(default=False, verbose_name=b'\xe6\x98\xaf\xe5\x90\xa6\xe5\x85\xac\xe9\x96\x8b'),
        ),
        migrations.AddField(
            model_name='project',
            name='local_manager',
            field=models.CharField(max_length=64, null=True, verbose_name=b'\xe7\xb8\xa3\xe5\xb8\x82\xe4\xb8\xbb\xe7\xae\xa1'),
        ),
        migrations.AddField(
            model_name='project',
            name='local_manager_email',
            field=models.EmailField(max_length=128, null=True, verbose_name=b'\xe7\xb8\xa3\xe5\xb8\x82\xe4\xb8\xbb\xe7\xae\xa1email'),
        ),
        migrations.AddField(
            model_name='project',
            name='local_manager_phone',
            field=models.CharField(max_length=64, null=True, verbose_name=b'\xe7\xb8\xa3\xe5\xb8\x82\xe4\xb8\xbb\xe7\xae\xa1\xe9\x9b\xbb\xe8\xa9\xb1'),
        ),
        migrations.AddField(
            model_name='project',
            name='matching_fund_1',
            field=models.DecimalField(null=True, verbose_name=b'\xe9\x85\x8d\xe5\x90\x88\xe6\xac\xbe1(\xe5\x8d\x83\xe5\x85\x83)', max_digits=16, decimal_places=4),
        ),
        migrations.AddField(
            model_name='project',
            name='matching_fund_2',
            field=models.DecimalField(null=True, verbose_name=b'\xe9\x85\x8d\xe5\x90\x88\xe6\xac\xbe2(\xe5\x8d\x83\xe5\x85\x83)', max_digits=16, decimal_places=4),
        ),
        migrations.AddField(
            model_name='project',
            name='selfpay',
            field=models.DecimalField(null=True, verbose_name=b'\xe8\x87\xaa\xe8\xbe\xa6(\xe5\x8d\x83\xe5\x85\x83)', max_digits=16, decimal_places=4),
        ),
        migrations.AddField(
            model_name='project',
            name='selfpay_revise',
            field=models.DecimalField(null=True, verbose_name=b'\xe8\xaa\xbf\xe8\x87\xaa\xe8\xbe\xa6(\xe5\x8d\x83\xe5\x85\x83)', max_digits=16, decimal_places=4),
        ),
        migrations.AddField(
            model_name='project',
            name='use_gallery',
            field=models.BooleanField(default=True, verbose_name='\u662f\u5426\u4f7f\u7528\u65b0\u7248\u76f8\u7247\u7cfb\u7d71'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='all_score',
            field=models.IntegerField(null=True, verbose_name='\u6574\u9ad4\u6eff\u610f\u5ea6'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='app_score',
            field=models.IntegerField(null=True, verbose_name='\u529f\u80fd\u6eff\u610f\u5ea6'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='is_satisfaction',
            field=models.BooleanField(default=False, verbose_name='\u662f\u5426\u586b\u5beb\u6eff\u610f\u5ea6\u8abf\u67e5\u8868'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='project_score',
            field=models.IntegerField(null=True, verbose_name='\u5c0d\u5de5\u7a0b\u7684\u5e6b\u52a9\u6eff\u610f\u5ea6'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='system_memo',
            field=models.TextField(max_length=256, null=True, verbose_name='\u7cfb\u7d71\u5efa\u8b70'),
        ),
        migrations.AlterField(
            model_name='budget',
            name='capital_ratify_budget',
            field=models.DecimalField(null=True, verbose_name='\u6838\u5b9a\u6578(\u9810\u7b97\u6578)', max_digits=16, decimal_places=3),
        ),
        migrations.AlterField(
            model_name='budget',
            name='capital_ratify_local_budget',
            field=models.DecimalField(null=True, verbose_name='\u5730\u65b9\u914d\u5408\u6b3e(\u9810\u7b97\u6578)', max_digits=16, decimal_places=3),
        ),
        migrations.AlterField(
            model_name='budget',
            name='capital_ratify_local_revision',
            field=models.DecimalField(null=True, verbose_name='\u5730\u65b9\u5be6\u969b\u914d\u5408\u6b3e\u91d1\u984d', max_digits=16, decimal_places=3),
        ),
        migrations.AlterField(
            model_name='budget',
            name='capital_ratify_revision',
            field=models.DecimalField(null=True, verbose_name='\u5be6\u969b\u88dc\u52a9\u91d1\u984d', max_digits=16, decimal_places=3),
        ),
        migrations.AlterField(
            model_name='countychaseprojectonebyone',
            name='act_eng_do_announcement_tender',
            field=models.DateField(null=True, verbose_name='\u5be6\u969b_\u5de5\u7a0b_(\u5de5\u7a0b\u65bd\u505a)\u516c\u544a\u4e0a\u7db2'),
        ),
        migrations.AlterField(
            model_name='countychaseprojectonebyone',
            name='act_eng_plan_acceptance_closed',
            field=models.DateField(null=True, verbose_name='\u5be6\u969b_\u5de5\u7a0b_(\u8a2d\u8a08\u898f\u5283)\u7d50\u6848'),
        ),
        migrations.AlterField(
            model_name='countychaseprojectonebyone',
            name='act_eng_plan_announcement_tender',
            field=models.DateField(null=True, verbose_name='\u5be6\u969b_\u5de5\u7a0b_(\u8a2d\u8a08\u898f\u5283)\u516c\u544a\u4e0a\u7db2'),
        ),
        migrations.AlterField(
            model_name='countychaseprojectonebyone',
            name='act_eng_plan_detail_design',
            field=models.DateField(null=True, verbose_name='\u5be6\u969b_\u5de5\u7a0b_(\u8a2d\u8a08\u898f\u5283)\u63d0\u9001\u9810\u7b97\u66f8\u5716'),
        ),
        migrations.AlterField(
            model_name='countychaseprojectonebyone',
            name='act_ser_acceptance_closed',
            field=models.DateField(null=True, verbose_name='\u5be6\u969b_\u52de\u52d9_\u7d50\u6848'),
        ),
        migrations.AlterField(
            model_name='countychaseprojectonebyone',
            name='act_ser_announcement_tender',
            field=models.DateField(null=True, verbose_name='\u5be6\u969b_\u52de\u52d9_\u52de\u52d9\u516c\u544a\u4e0a\u7db2'),
        ),
        migrations.AlterField(
            model_name='countychaseprojectonebyone',
            name='eng_do_announcement_tender_memo',
            field=models.CharField(max_length=256, null=True, verbose_name='\u5de5\u7a0b_(\u5de5\u7a0b\u65bd\u505a)\u516c\u544a\u4e0a\u7db2/\u5099\u8a3b'),
        ),
        migrations.AlterField(
            model_name='countychaseprojectonebyone',
            name='eng_plan_acceptance_closed_memo',
            field=models.CharField(max_length=256, null=True, verbose_name='\u5de5\u7a0b_(\u8a2d\u8a08\u898f\u5283)\u7d50\u6848/\u5099\u8a3b'),
        ),
        migrations.AlterField(
            model_name='countychaseprojectonebyone',
            name='eng_plan_announcement_tender_memo',
            field=models.CharField(max_length=256, null=True, verbose_name='\u5de5\u7a0b_(\u8a2d\u8a08\u898f\u5283)\u516c\u544a\u4e0a\u7db2/\u5099\u8a3b'),
        ),
        migrations.AlterField(
            model_name='countychaseprojectonebyone',
            name='eng_plan_detail_design_memo',
            field=models.CharField(max_length=256, null=True, verbose_name='\u5de5\u7a0b_(\u8a2d\u8a08\u898f\u5283)\u63d0\u9001\u9810\u7b97\u66f8\u5716/\u5099\u8a3b'),
        ),
        migrations.AlterField(
            model_name='countychaseprojectonebyone',
            name='sch_eng_do_announcement_tender',
            field=models.DateField(null=True, verbose_name='\u9810\u8a08_\u5de5\u7a0b_(\u5de5\u7a0b\u65bd\u505a)\u516c\u544a\u4e0a\u7db2'),
        ),
        migrations.AlterField(
            model_name='countychaseprojectonebyone',
            name='sch_eng_plan_acceptance_closed',
            field=models.DateField(null=True, verbose_name='\u9810\u8a08_\u5de5\u7a0b_(\u8a2d\u8a08\u898f\u5283)\u7d50\u6848'),
        ),
        migrations.AlterField(
            model_name='countychaseprojectonebyone',
            name='sch_eng_plan_announcement_tender',
            field=models.DateField(null=True, verbose_name='\u9810\u8a08_\u5de5\u7a0b_(\u8a2d\u8a08\u898f\u5283)\u516c\u544a\u4e0a\u7db2'),
        ),
        migrations.AlterField(
            model_name='countychaseprojectonebyone',
            name='sch_eng_plan_detail_design',
            field=models.DateField(null=True, verbose_name='\u9810\u8a08_\u5de5\u7a0b_(\u8a2d\u8a08\u898f\u5283)\u63d0\u9001\u9810\u7b97\u66f8\u5716'),
        ),
        migrations.AlterField(
            model_name='countychaseprojectonebyone',
            name='sch_ser_acceptance_closed',
            field=models.DateField(null=True, verbose_name='\u9810\u8a08_\u52de\u52d9_\u7d50\u6848'),
        ),
        migrations.AlterField(
            model_name='countychaseprojectonebyone',
            name='sch_ser_announcement_tender',
            field=models.DateField(null=True, verbose_name='\u9810\u8a08_\u52de\u52d9_\u52de\u52d9\u516c\u544a\u4e0a\u7db2'),
        ),
        migrations.AlterField(
            model_name='countychaseprojectonebyone',
            name='ser_acceptance_closed_memo',
            field=models.CharField(max_length=256, null=True, verbose_name='\u52de\u52d9_\u7d50\u6848/\u5099\u8a3b'),
        ),
        migrations.AlterField(
            model_name='countychaseprojectonetomany',
            name='actual_progress_percent',
            field=models.DecimalField(default=b'0', verbose_name='\u5be6\u969b\u9032\u5ea6\u767e\u5206\u6bd4(%)', max_digits=16, decimal_places=2),
        ),
        migrations.AlterField(
            model_name='countychaseprojectonetomany',
            name='expected_to_end_percent',
            field=models.DecimalField(default=b'0', verbose_name='\u9810\u8a08\u81f3\u5e74\u5e95\u57f7\u884c\u7387\u767e\u5206\u6bd4(%)', max_digits=16, decimal_places=2),
        ),
        migrations.AlterField(
            model_name='countychaseprojectonetomany',
            name='local_payout',
            field=models.DecimalField(default=b'0', verbose_name='\u5730\u65b9\u5be6\u652f\u6578(\u5143)(G)', max_digits=16, decimal_places=3),
        ),
        migrations.AlterField(
            model_name='countychaseprojectonetomany',
            name='local_unpay',
            field=models.DecimalField(default=b'0', verbose_name='\u5730\u65b9\u61c9\u4ed8\u672a\u4ed8\u6578(\u5143)(\u88dc\u52a9\u6b3e)(H)=(E)*(F)-(G)', max_digits=16, decimal_places=3),
        ),
        migrations.AlterField(
            model_name='countychaseprojectonetomany',
            name='memo',
            field=models.CharField(default='', max_length=2048, verbose_name='\u76ee\u524d\u8fa6\u7406\u60c5\u5f62(\u9032\u5ea6)'),
        ),
        migrations.AlterField(
            model_name='countychaseprojectonetomany',
            name='schedul_progress_percent',
            field=models.DecimalField(default=b'0', verbose_name='\u9810\u8a08\u9032\u5ea6\u767e\u5206\u6bd4(%)', max_digits=16, decimal_places=2),
        ),
        migrations.AlterField(
            model_name='countychaseprojectonetomany',
            name='self_payout',
            field=models.DecimalField(default=b'0', verbose_name='\u672c\u7f72\u5be6\u652f\u6578(\u5143)(G)', max_digits=16, decimal_places=3),
        ),
        migrations.AlterField(
            model_name='countychaseprojectonetomany',
            name='self_unpay',
            field=models.DecimalField(default=b'0', verbose_name='\u672c\u7f72\u61c9\u4ed8\u672a\u4ed8\u6578(\u5143)(\u88dc\u52a9\u6b3e)(H)=(E)*(F)-(G)', max_digits=16, decimal_places=3),
        ),
        migrations.AlterField(
            model_name='frcmtempfile',
            name='file',
            field=models.ImageField(null=True, upload_to=b'apps/frcm/media/frcm/tempfile/%Y%m%d'),
        ),
        migrations.AlterField(
            model_name='loginhistory',
            name='ip',
            field=models.CharField(max_length=128, null=True, verbose_name='IP'),
        ),
        migrations.AlterField(
            model_name='projectphoto',
            name='file',
            field=models.ImageField(null=True, upload_to=b'apps/project/media/project/photo/%Y%m%d'),
        ),
        migrations.AddField(
            model_name='planreserve',
            name='plan',
            field=models.ForeignKey(related_name='planreserve_plan', verbose_name=b'\xe8\xa8\x88\xe7\x95\xab', to='fishuser.Plan'),
        ),
        migrations.AddField(
            model_name='countychaseprojectonetomanypayout',
            name='budget',
            field=models.ForeignKey(verbose_name='\u7d93\u8cbb\u4f86\u6e90', to='fishuser.Budget'),
        ),
        migrations.AddField(
            model_name='countychaseprojectonetomanypayout',
            name='chase',
            field=models.ForeignKey(verbose_name='\u8ffd\u8e64\u7d00\u9304', to='fishuser.CountyChaseProjectOneToMany'),
        ),
    ]
