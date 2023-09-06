# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Account',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('fes_id', models.IntegerField(verbose_name='fes row id')),
                ('account', models.CharField(max_length=256, null=True, verbose_name=b'\xe5\xb8\xb3\xe8\x99\x9f')),
                ('passwd', models.CharField(max_length=256, null=True, verbose_name=b'\xe5\xaf\x86\xe7\xa2\xbc')),
                ('type', models.IntegerField(null=True, verbose_name=b'\xe5\xb8\xb3\xe8\x99\x9f\xe9\xa1\x9e\xe5\x88\xa5')),
                ('update_time', models.DateTimeField(null=True, verbose_name=b'update_time of FES row')),
            ],
        ),
        migrations.CreateModel(
            name='AliveLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('uuid', models.CharField(max_length=256, verbose_name='UUID')),
                ('create_time', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='FishingPort',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('fes_id', models.IntegerField(verbose_name='fes row id')),
                ('name', models.CharField(max_length=256, verbose_name=b'\xe6\xbc\x81\xe6\xb8\xaf\xe5\x90\x8d\xe7\xa8\xb1')),
                ('code', models.CharField(max_length=256, verbose_name=b'\xe6\xbc\x81\xe6\xb8\xaf\xe4\xbb\xa3\xe7\xa2\xbc')),
                ('xcoord', models.DecimalField(null=True, verbose_name=b'X\xe5\xba\xa7\xe6\xa8\x99', max_digits=20, decimal_places=12)),
                ('ycoord', models.DecimalField(null=True, verbose_name=b'y\xe5\xba\xa7\xe6\xa8\x99', max_digits=20, decimal_places=12)),
                ('update_time', models.DateTimeField(null=True, verbose_name=b'update_time of FES row')),
            ],
        ),
        migrations.CreateModel(
            name='Monitor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('fes_id', models.IntegerField(verbose_name='fes row id')),
                ('machine_no', models.CharField(max_length=16, verbose_name='\u4f9b\u61c9\u6a5f\u578b', choices=[(b'BE3204', b'BE3204')])),
                ('name', models.CharField(max_length=512, null=True, verbose_name=b'\xe5\x90\x8d\xe7\xa8\xb1')),
                ('location', models.CharField(max_length=512, null=True, verbose_name=b'\xe4\xbd\x8d\xe7\xbd\xae\xe6\x95\x98\xe8\xbf\xb0')),
                ('video_url', models.CharField(max_length=512, null=True, verbose_name=b'\xe5\xbd\xb1\xe7\x89\x87\xe5\x84\xb2\xe5\xad\x98\xe4\xbd\x8d\xe7\xbd\xae')),
                ('lat', models.DecimalField(null=True, verbose_name=b'\xe7\xb7\xaf\xe5\xba\xa6', max_digits=20, decimal_places=12)),
                ('lng', models.DecimalField(null=True, verbose_name=b'\xe7\xb6\x93\xe5\xba\xa6', max_digits=20, decimal_places=12)),
                ('ip', models.CharField(max_length=256, null=True, verbose_name=b'IP\xe4\xbd\x8d\xe7\xbd\xae')),
                ('active', models.BooleanField(default=True, verbose_name=b'\xe5\x95\x9f\xe7\x94\xa8\xe8\x88\x87\xe5\x90\xa6')),
                ('update_time', models.DateTimeField(null=True, verbose_name=b'update_time of FES row')),
            ],
        ),
        migrations.CreateModel(
            name='Place',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('fes_id', models.IntegerField(verbose_name='fes row id')),
                ('name', models.CharField(max_length=128, verbose_name='\u5340\u57df\u540d\u7a31')),
                ('zipcode', models.CharField(max_length=20, verbose_name='\u90f5\u905e\u5340\u865f')),
                ('update_time', models.DateTimeField(null=True, verbose_name=b'update_time of FES row')),
                ('parent', models.ForeignKey(related_name='child_set', to='weblive.Place', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Preset',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('fes_id', models.IntegerField(verbose_name='fes row id')),
                ('name', models.CharField(max_length=256, null=True, verbose_name=b'\xe8\xa8\xad\xe5\xae\x9a\xe5\x90\x8d\xe7\xa8\xb1')),
                ('no', models.CharField(max_length=256, null=True, verbose_name=b'\xe8\xa8\xad\xe5\xae\x9a\xe5\xb0\x8d\xe6\x87\x89\xe7\xa2\xbc')),
                ('update_time', models.DateTimeField(null=True, verbose_name=b'update_time of FES row')),
                ('monitor', models.ForeignKey(verbose_name=b'\xe6\x94\x9d\xe5\xbd\xb1\xe6\xa9\x9f', to='weblive.Monitor')),
            ],
        ),
        migrations.CreateModel(
            name='SyncLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('model_name', models.CharField(max_length=64)),
                ('count', models.IntegerField(default=0)),
                ('running_second', models.IntegerField(default=0)),
                ('maximal_update_time', models.DateTimeField(null=True, verbose_name='update_time of FES row')),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('done_time', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.AddField(
            model_name='monitor',
            name='place',
            field=models.ForeignKey(verbose_name=b'\xe7\xb8\xa3\xe5\xb8\x82', to='weblive.Place', null=True),
        ),
        migrations.AddField(
            model_name='monitor',
            name='port',
            field=models.ForeignKey(verbose_name=b'\xe6\xbc\x81\xe6\xb8\xaf', to='weblive.FishingPort', null=True),
        ),
        migrations.AddField(
            model_name='fishingport',
            name='place',
            field=models.ForeignKey(verbose_name=b'\xe7\xb8\xa3\xe5\xb8\x82', to='weblive.Place'),
        ),
        migrations.AddField(
            model_name='alivelog',
            name='monitor',
            field=models.ForeignKey(verbose_name=b'\xe6\x94\x9d\xe5\xbd\xb1\xe6\xa9\x9f', to='weblive.Monitor'),
        ),
        migrations.AddField(
            model_name='account',
            name='monitor',
            field=models.ForeignKey(verbose_name=b'\xe6\x94\x9d\xe5\xbd\xb1\xe6\xa9\x9f', to='weblive.Monitor'),
        ),
    ]
