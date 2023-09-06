# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('general', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('harbor', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('account', models.CharField(max_length=256, null=True, verbose_name=b'\xe5\xb8\xb3\xe8\x99\x9f')),
                ('passwd', models.CharField(max_length=256, null=True, verbose_name=b'\xe5\xaf\x86\xe7\xa2\xbc')),
                ('update_time', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Monitor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('machine_no', models.CharField(max_length=16, verbose_name='\u4f9b\u61c9\u6a5f\u578b', choices=[(b'BE3204', b'BE3204'), (b'PELCO-O', b'PELCO-O')])),
                ('name', models.CharField(max_length=512, null=True, verbose_name=b'\xe5\x90\x8d\xe7\xa8\xb1')),
                ('location', models.CharField(max_length=512, null=True, verbose_name=b'\xe4\xbd\x8d\xe7\xbd\xae\xe6\x95\x98\xe8\xbf\xb0')),
                ('video_url', models.CharField(max_length=512, null=True, verbose_name=b'\xe5\xbd\xb1\xe7\x89\x87\xe5\x84\xb2\xe5\xad\x98\xe4\xbd\x8d\xe7\xbd\xae')),
                ('lat', models.DecimalField(null=True, verbose_name=b'\xe7\xb7\xaf\xe5\xba\xa6', max_digits=20, decimal_places=12)),
                ('lng', models.DecimalField(null=True, verbose_name=b'\xe7\xb6\x93\xe5\xba\xa6', max_digits=20, decimal_places=12)),
                ('ip', models.CharField(max_length=256, null=True, verbose_name=b'IP\xe4\xbd\x8d\xe7\xbd\xae')),
                ('active', models.BooleanField(default=True, verbose_name=b'\xe5\x95\x9f\xe7\x94\xa8\xe8\x88\x87\xe5\x90\xa6')),
                ('update_time', models.DateTimeField(auto_now=True)),
                ('place', models.ForeignKey(verbose_name=b'\xe7\xb8\xa3\xe5\xb8\x82', to='general.Place', null=True)),
                ('port', models.ForeignKey(verbose_name=b'\xe6\xbc\x81\xe6\xb8\xaf', to='harbor.FishingPort', null=True)),
                ('taken', models.ForeignKey(verbose_name=b'\xe6\x93\x8d\xe4\xbd\x9c\xe4\xba\xba', to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Option',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('swarm', models.CharField(max_length=32, verbose_name=b'\xe7\xbe\xa4')),
                ('value', models.CharField(max_length=64, verbose_name=b'\xe9\x81\xb8\xe9\xa0\x85')),
            ],
            options={
                'verbose_name': '\u9078\u9805',
                'verbose_name_plural': '\u9078\u9805',
            },
        ),
        migrations.CreateModel(
            name='Preset',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=256, null=True, verbose_name=b'\xe8\xa8\xad\xe5\xae\x9a\xe5\x90\x8d\xe7\xa8\xb1')),
                ('no', models.CharField(max_length=256, null=True, verbose_name=b'\xe8\xa8\xad\xe5\xae\x9a\xe5\xb0\x8d\xe6\x87\x89\xe7\xa2\xbc')),
                ('update_time', models.DateTimeField(auto_now=True)),
                ('monitor', models.ForeignKey(verbose_name=b'\xe6\x94\x9d\xe5\xbd\xb1\xe6\xa9\x9f', to='monitor.Monitor')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='option',
            unique_together=set([('swarm', 'value')]),
        ),
        migrations.AddField(
            model_name='account',
            name='monitor',
            field=models.ForeignKey(verbose_name=b'\xe6\x94\x9d\xe5\xbd\xb1\xe6\xa9\x9f', to='monitor.Monitor'),
        ),
        migrations.AddField(
            model_name='account',
            name='type',
            field=models.ForeignKey(verbose_name=b'\xe5\xb8\xb3\xe8\x99\x9f\xe9\xa1\x9e\xe5\x88\xa5', to='monitor.Option', null=True),
        ),
    ]
