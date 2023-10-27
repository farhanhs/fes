# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import harbor.models


class Migration(migrations.Migration):

    dependencies = [
        ('general', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Aquaculture',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=256, verbose_name=b'\xe9\xad\x9a\xe5\xa1\xad\xe5\x90\x8d\xe7\xa8\xb1')),
                ('code', models.CharField(max_length=256, null=True, verbose_name=b'\xe9\xad\x9a\xe5\xa1\xad\xe4\xbb\xa3\xe7\xa2\xbc')),
                ('xcoord', models.DecimalField(null=True, verbose_name=b'X\xe5\xba\xa7\xe6\xa8\x99', max_digits=20, decimal_places=12)),
                ('ycoord', models.DecimalField(null=True, verbose_name=b'y\xe5\xba\xa7\xe6\xa8\x99', max_digits=20, decimal_places=12)),
                ('location', models.CharField(max_length=4096, null=True, verbose_name=b'\xe5\x9c\xb0\xe7\x90\x86\xe4\xbd\x8d\xe7\xbd\xae')),
                ('history', models.CharField(max_length=4096, null=True, verbose_name=b'\xe9\xad\x9a\xe5\xa1\xad\xe6\xb2\xbf\xe9\x9d\xa9')),
                ('range', models.CharField(max_length=4096, null=True, verbose_name=b'\xe9\xad\x9a\xe5\xa1\xad\xe5\x8d\x80\xe5\x9f\x9f\xe7\xaf\x84\xe5\x9c\x8d')),
                ('place', models.ForeignKey(verbose_name=b'\xe7\xb8\xa3\xe5\xb8\x82', to='general.Place', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='AquaculturePublic',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('year', models.IntegerField(verbose_name=b'\xe5\xb9\xb4\xe5\xba\xa6')),
                ('project_name', models.CharField(max_length=256, verbose_name=b'\xe5\xb7\xa5\xe7\xa8\x8b\xe5\x90\x8d\xe7\xa8\xb1')),
                ('contents', models.CharField(max_length=1024, null=True, verbose_name=b'\xe5\xb7\xa5\xe7\xa8\x8b\xe9\xa0\x85\xe7\x9b\xae')),
                ('value', models.DecimalField(default=0, verbose_name=b'\xe5\xb7\xa5\xe7\xa8\x8b\xe7\xb6\x93\xe8\xb2\xbb(\xe8\x90\xac\xe5\x85\x83)', max_digits=16, decimal_places=2)),
                ('memo', models.CharField(max_length=4096, null=True, verbose_name=b'\xe5\x82\x99\xe8\xa8\xbb')),
                ('place', models.ForeignKey(verbose_name=b'\xe7\xb8\xa3\xe5\xb8\x82', to='general.Place')),
            ],
        ),
        migrations.CreateModel(
            name='AquaculturePublicWork',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('year', models.IntegerField(verbose_name=b'\xe5\xb9\xb4\xe5\xba\xa6')),
                ('area', models.CharField(max_length=256, null=True, verbose_name=b'\xe7\x94\x9f\xe7\x94\xa2\xe5\x8d\x80')),
                ('project_item', models.CharField(max_length=256, null=True, verbose_name=b'\xe5\xb7\xa5\xe7\xa8\x8b\xe9\xa0\x85\xe7\x9b\xae')),
                ('unit', models.CharField(max_length=20, null=True, verbose_name=b'\xe5\x96\xae\xe4\xbd\x8d')),
                ('project_num', models.DecimalField(default=0, verbose_name=b'\xe5\xb7\xa5\xe7\xa8\x8b\xe6\x95\xb8\xe9\x87\x8f', max_digits=16, decimal_places=2)),
                ('project_cost', models.DecimalField(default=0, verbose_name=b'\xe5\xb7\xa5\xe7\xa8\x8b\xe9\x87\x91\xe9\xa1\x8d(\xe8\x90\xac\xe5\x85\x83)', max_digits=16, decimal_places=2)),
                ('memo', models.CharField(max_length=2048, null=True, verbose_name=b'\xe5\x82\x99\xe8\xa8\xbb')),
                ('place', models.ForeignKey(verbose_name=b'\xe7\xb8\xa3\xe5\xb8\x82', to='general.Place')),
            ],
        ),
        migrations.CreateModel(
            name='AveragePressure',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('memo', models.CharField(max_length=1024, null=True, verbose_name=b'\xe5\xb9\xb3\xe5\x9d\x87\xe6\xb0\xa3\xe6\xba\xab\xe8\xaa\xaa\xe6\x98\x8e')),
                ('month', models.IntegerField(verbose_name=b'\xe6\x9c\x88\xe4\xbb\xbd')),
                ('min', models.DecimalField(default=0, verbose_name=b'\xe6\xb8\xac\xe7\xab\x99\xe6\x9c\x80\xe4\xbd\x8e\xe6\xb0\xa3\xe5\xa3\x93', max_digits=16, decimal_places=2)),
                ('max', models.DecimalField(default=0, verbose_name=b'\xe6\xb8\xac\xe7\xab\x99\xe6\x9c\x80\xe9\xab\x98\xe6\xb0\xa3\xe5\xa3\x93', max_digits=16, decimal_places=2)),
                ('average', models.DecimalField(default=0, verbose_name=b'\xe6\xb8\xac\xe7\xab\x99\xe5\xb9\xb3\xe5\x9d\x87\xe6\xb0\xa3\xe5\xa3\x93', max_digits=16, decimal_places=2)),
                ('sea_average', models.DecimalField(default=0, verbose_name=b'\xe6\xb5\xb7\xe5\xb9\xb3\xe9\x9d\xa2\xe5\xb9\xb3\xe5\x9d\x87\xe6\xb0\xa3\xe5\xa3\x93', max_digits=16, decimal_places=2)),
            ],
        ),
        migrations.CreateModel(
            name='AverageRainfall',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('month', models.IntegerField(verbose_name=b'\xe6\x9c\x88\xe4\xbb\xbd')),
                ('rain_average', models.DecimalField(default=0, verbose_name=b'\xe5\xb9\xb3\xe5\x9d\x87\xe9\x99\x8d\xe9\x9b\xa8\xe9\x87\x8f', max_digits=16, decimal_places=2)),
                ('rain_memo', models.CharField(max_length=1024, null=True, verbose_name=b'\xe5\xb9\xb3\xe5\x9d\x87\xe9\x9b\xa8\xe9\x87\x8f\xe8\xaa\xaa\xe6\x98\x8e')),
                ('day_average', models.DecimalField(default=0, verbose_name=b'\xe5\xb9\xb3\xe5\x9d\x87\xe9\x99\x8d\xe9\x9b\xa8\xe6\x97\xa5\xe6\x95\xb8', max_digits=16, decimal_places=2)),
                ('day_memo', models.CharField(max_length=1024, null=True, verbose_name=b'\xe5\xb9\xb3\xe5\x9d\x87\xe9\x99\x8d\xe9\x9b\xa8\xe6\x97\xa5\xe6\x95\xb8\xe8\xaa\xaa\xe6\x98\x8e')),
            ],
        ),
        migrations.CreateModel(
            name='AverageTemperature',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('memo', models.CharField(max_length=1024, null=True, verbose_name=b'\xe5\xb9\xb3\xe5\x9d\x87\xe6\xb0\xa3\xe6\xba\xab\xe8\xaa\xaa\xe6\x98\x8e')),
                ('month', models.IntegerField(verbose_name=b'\xe6\x9c\x88\xe4\xbb\xbd')),
                ('min', models.DecimalField(default=0, verbose_name=b'\xe6\xb8\xac\xe7\xab\x99\xe6\x9c\x80\xe4\xbd\x8e\xe6\xb0\xa3\xe6\xba\xab', max_digits=16, decimal_places=2)),
                ('max', models.DecimalField(default=0, verbose_name=b'\xe6\xb8\xac\xe7\xab\x99\xe6\x9c\x80\xe9\xab\x98\xe6\xb0\xa3\xe6\xba\xab', max_digits=16, decimal_places=2)),
                ('average', models.DecimalField(default=0, verbose_name=b'\xe6\xb8\xac\xe7\xab\x99\xe5\xb9\xb3\xe5\x9d\x87\xe6\xb0\xa3\xe6\xba\xab', max_digits=16, decimal_places=2)),
            ],
        ),
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('people', models.CharField(max_length=4096, null=True, verbose_name=b'\xe4\xba\xba\xe6\x96\x87\xe6\xa6\x82\xe8\xbf\xb0')),
                ('fishingport_location', models.CharField(max_length=4096, null=True, verbose_name=b'\xe6\xbc\x81\xe6\xb8\xaf\xe4\xbd\x8d\xe7\xbd\xae')),
                ('place', models.ForeignKey(verbose_name=b'\xe7\xb8\xa3\xe5\xb8\x82', to='general.Place')),
            ],
        ),
        migrations.CreateModel(
            name='DataShare',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('upload_date', models.DateField(verbose_name=b'\xe4\xb8\x8a\xe5\x82\xb3\xe6\x97\xa5\xe6\x9c\x9f')),
                ('name', models.CharField(default=b'', max_length=256, null=True, verbose_name=b'\xe6\xaa\x94\xe6\xa1\x88\xe5\x90\x8d')),
                ('file', models.ImageField(null=True, upload_to=b'apps\\harbor\\media\\harbor\\datashare\\%Y%m%d')),
                ('memo', models.CharField(max_length=2048, null=True, verbose_name=b'\xe5\x82\x99\xe8\xa8\xbb\xe8\xaa\xaa\xe6\x98\x8e')),
                ('upload_user', models.ForeignKey(verbose_name=b'\xe4\xb8\x8a\xe5\x82\xb3\xe8\x80\x85', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='FisheryOutput',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('year', models.IntegerField(null=True, verbose_name=b'\xe5\xb9\xb4\xe5\xba\xa6')),
                ('aquaculture_num', models.IntegerField(null=True, verbose_name=b'\xe9\xa4\x8a\xe6\xae\x96\xe6\x95\xb8\xe9\x87\x8f(\xe5\x99\xb8\xe6\x95\xb8)')),
                ('aquaculture_value', models.IntegerField(null=True, verbose_name=b'\xe9\xa4\x8a\xe6\xae\x96\xe5\x83\xb9\xe5\x80\xbc(\xe4\xbb\x9f\xe5\x85\x83)')),
                ('coastwise_num', models.IntegerField(null=True, verbose_name=b'\xe6\xb2\xbf\xe5\xb2\xb8\xe6\x95\xb8\xe9\x87\x8f(\xe5\x99\xb8\xe6\x95\xb8)')),
                ('coastwise_value', models.IntegerField(null=True, verbose_name=b'\xe6\xb2\xbf\xe5\xb2\xb8\xe5\x83\xb9\xe5\x80\xbc(\xe4\xbb\x9f\xe5\x85\x83)')),
                ('inshore_num', models.IntegerField(null=True, verbose_name=b'\xe8\xbf\x91\xe6\xb5\xb7\xe6\x95\xb8\xe9\x87\x8f(\xe5\x99\xb8\xe6\x95\xb8)')),
                ('inshore_value', models.IntegerField(null=True, verbose_name=b'\xe8\xbf\x91\xe6\xb5\xb7\xe5\x83\xb9\xe5\x80\xbc(\xe4\xbb\x9f\xe5\x85\x83)')),
                ('pelagic_num', models.IntegerField(null=True, verbose_name=b'\xe9\x81\xa0\xe6\xb4\x8b\xe6\x95\xb8\xe9\x87\x8f(\xe5\x99\xb8\xe6\x95\xb8)')),
                ('pelagic_value', models.IntegerField(null=True, verbose_name=b'\xe9\x81\xa0\xe6\xb4\x8b\xe5\x83\xb9\xe5\x80\xbc(\xe4\xbb\x9f\xe5\x85\x83)')),
                ('place', models.ForeignKey(verbose_name=b'\xe7\xb8\xa3\xe5\xb8\x82', to='general.Place')),
            ],
        ),
        migrations.CreateModel(
            name='FisheryType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('fishery', models.CharField(max_length=256, verbose_name=b'\xe6\xbc\x81\xe6\xa5\xad\xe5\x88\xa5')),
                ('output', models.IntegerField(null=True, verbose_name=b'\xe7\x94\xa2\xe9\x87\x8f(\xe5\x85\xac\xe5\x99\xb8)')),
                ('value', models.IntegerField(null=True, verbose_name=b'\xe7\x94\xa2\xe5\x80\xbc(\xe5\x8d\x83\xe5\x85\x83)')),
                ('place', models.ForeignKey(verbose_name=b'\xe7\xb8\xa3\xe5\xb8\x82', to='general.Place')),
            ],
        ),
        migrations.CreateModel(
            name='FishingPort',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=256, verbose_name=b'\xe6\xbc\x81\xe6\xb8\xaf\xe5\x90\x8d\xe7\xa8\xb1')),
                ('code', models.CharField(max_length=256, verbose_name=b'\xe6\xbc\x81\xe6\xb8\xaf\xe4\xbb\xa3\xe7\xa2\xbc')),
                ('xcoord', models.DecimalField(null=True, verbose_name=b'X\xe5\xba\xa7\xe6\xa8\x99', max_digits=20, decimal_places=12)),
                ('ycoord', models.DecimalField(null=True, verbose_name=b'y\xe5\xba\xa7\xe6\xa8\x99', max_digits=20, decimal_places=12)),
                ('location', models.CharField(max_length=4096, null=True, verbose_name=b'\xe5\x9c\xb0\xe7\x90\x86\xe4\xbd\x8d\xe7\xbd\xae')),
                ('history', models.CharField(max_length=4096, null=True, verbose_name=b'\xe5\xbb\xba\xe6\xb8\xaf\xe6\xb2\xbf\xe9\x9d\xa9')),
                ('range', models.CharField(max_length=4096, null=True, verbose_name=b'\xe6\xbc\x81\xe6\xb8\xaf\xe5\x8d\x80\xe5\x9f\x9f\xe7\xaf\x84\xe5\x9c\x8d')),
                ('update_time', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='FishingPortBoat',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('year', models.IntegerField(null=True, verbose_name=b'\xe5\xb9\xb4\xe5\xba\xa6')),
                ('num', models.IntegerField(null=True, verbose_name=b'\xe6\x95\xb8\xe9\x87\x8f')),
            ],
        ),
        migrations.CreateModel(
            name='FishingPortPhoto',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(default=b'', max_length=256, null=True, verbose_name=b'\xe6\xaa\x94\xe6\xa1\x88\xe5\x90\x8d')),
                ('file', models.ImageField(null=True, upload_to=b'apps\\harbor\\media\\harbor\\fishingportphoto\\harbor\\%Y%m%d')),
                ('extname', models.CharField(default=b'', max_length=256, null=True, verbose_name=b'\xe5\x89\xaf\xe6\xaa\x94\xe5\x90\x8d')),
                ('memo', models.CharField(max_length=2048, null=True, verbose_name=b'\xe5\x82\x99\xe8\xa8\xbb\xe8\xaa\xaa\xe6\x98\x8e')),
                ('fishingport', models.ForeignKey(verbose_name=b'\xe6\xbc\x81\xe6\xb8\xaf', to='harbor.FishingPort')),
            ],
        ),
        migrations.CreateModel(
            name='FishType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('fish', models.CharField(max_length=256, verbose_name=b'\xe9\xad\x9a\xe9\xa1\x9e\xe5\x88\xa5')),
                ('output', models.IntegerField(null=True, verbose_name=b'\xe7\x94\xa2\xe9\x87\x8f(\xe5\x85\xac\xe5\x99\xb8)')),
                ('value', models.IntegerField(null=True, verbose_name=b'\xe7\x94\xa2\xe5\x80\xbc(\xe5\x8d\x83\xe5\x85\x83)')),
                ('place', models.ForeignKey(verbose_name=b'\xe7\xb8\xa3\xe5\xb8\x82', to='general.Place')),
            ],
        ),
        migrations.CreateModel(
            name='MainProject',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('year', models.CharField(max_length=1024, null=True, verbose_name=b'\xe5\xb9\xb4\xe5\xba\xa6')),
                ('item', models.CharField(max_length=1024, null=True, verbose_name=b'\xe9\xa0\x85\xe7\x9b\xae')),
                ('num', models.CharField(max_length=1024, null=True, verbose_name=b'\xe6\x95\xb8\xe9\x87\x8f')),
                ('memo', models.CharField(max_length=1024, null=True, verbose_name=b'\xe5\x82\x99\xe8\xa8\xbb')),
                ('fishingport', models.ForeignKey(verbose_name=b'\xe6\xbc\x81\xe6\xb8\xaf', to='harbor.FishingPort')),
            ],
        ),
        migrations.CreateModel(
            name='Observatory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=256, verbose_name=b'\xe6\xb8\xac\xe7\xab\x99\xe5\x90\x8d\xe7\xa8\xb1')),
                ('wind_memo', models.CharField(max_length=1024, null=True, verbose_name=b'\xe9\xa2\xa8\xe8\x8a\xb1\xe5\x9c\x96\xe8\xaa\xaa\xe6\x98\x8e')),
                ('rainday_memo', models.CharField(max_length=1024, null=True, verbose_name=b'\xe6\x9c\x88\xe5\xb9\xb3\xe5\x9d\x87\xe9\x99\x8d\xe9\x9b\xa8\xe6\x97\xa5\xe6\x95\xb8\xe8\xaa\xaa\xe6\x98\x8e')),
                ('file', models.ImageField(null=True, upload_to=b'apps\\harbor\\media\\harbor\\observatory')),
                ('extname', models.CharField(default=b'', max_length=256, null=True, verbose_name=b'\xe5\x89\xaf\xe6\xaa\x94\xe5\x90\x8d')),
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
            name='PortFisheryOutput',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('year', models.IntegerField(null=True, verbose_name=b'\xe5\xb9\xb4\xe5\xba\xa6')),
                ('output', models.IntegerField(null=True, verbose_name=b'\xe7\x94\xa2\xe9\x87\x8f(\xe5\x85\xac\xe5\x99\xb8)')),
                ('value', models.IntegerField(null=True, verbose_name=b'\xe7\x94\xa2\xe5\x80\xbc(\xe5\x8d\x83\xe5\x85\x83)')),
                ('fishingport', models.ForeignKey(verbose_name=b'\xe6\xbc\x81\xe6\xb8\xaf', to='harbor.FishingPort')),
            ],
        ),
        migrations.CreateModel(
            name='PortInstallationRecord',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField(verbose_name=b'\xe5\xa1\xab\xe8\xa1\xa8\xe6\x97\xa5\xe6\x9c\x9f')),
                ('time', models.TimeField(null=True, verbose_name='\u586b\u8868\u6642\u9593')),
                ('arrival_port', models.IntegerField(null=True, verbose_name=b'\xe8\x88\xb9\xe8\x88\xb6\xe9\x80\xb2\xe6\xb8\xaf\xe8\x89\x98\xe6\x95\xb8')),
                ('leave_port', models.IntegerField(null=True, verbose_name=b'\xe8\x88\xb9\xe8\x88\xb6\xe5\x87\xba\xe6\xb8\xaf\xe8\x89\x98\xe6\x95\xb8')),
                ('anchor', models.IntegerField(null=True, verbose_name=b'\xe6\xb3\x8a\xe5\x8d\x80\xe5\x81\x9c\xe6\xb3\x8a\xe8\x89\x98\xe6\x95\xb8')),
                ('boat_supplies_memo', models.CharField(max_length=2048, null=True, verbose_name=b'\xe8\xa3\x9c\xe7\xb5\xa6\xe5\x82\x99\xe8\xa8\xbb')),
                ('memo', models.CharField(max_length=2048, null=True, verbose_name=b'\xe5\x82\x99\xe8\xa8\xbb')),
                ('boat_supplies', models.ForeignKey(related_name='boat_supplies', verbose_name=b'\xe8\x88\xb9\xe9\x9a\xbb\xe8\xa3\x9c\xe7\xb5\xa6\xe6\x83\x85\xe5\xbd\xa2(\xe5\x8a\xa0\xe6\xb2\xb9\xe5\x8a\xa0\xe6\xb0\xb4\xe5\x8a\xa0\xe5\x86\xb0)', to='harbor.Option', null=True)),
                ('emergency', models.ForeignKey(related_name='emergency', verbose_name=b'\xe6\xb8\xaf\xe5\x8d\x80\xe7\xaa\x81\xe7\x99\xbc\xe6\x83\x85\xe6\xb3\x81', to='harbor.Option', null=True)),
                ('emergency_measures', models.ForeignKey(related_name='emergency_measures', verbose_name=b'\xe6\xb8\xaf\xe5\x8d\x80\xe7\xaa\x81\xe7\x99\xbc\xe6\x83\x85\xe5\xbd\xa2\xe8\x99\x95\xe7\x90\x86\xe6\x96\xb9\xe5\xbc\x8f', to='harbor.Option', null=True)),
                ('fishingport', models.ForeignKey(verbose_name=b'\xe6\xbc\x81\xe6\xb8\xaf', to='harbor.FishingPort')),
                ('organization', models.ForeignKey(verbose_name=b'\xe6\xbc\x81\xe6\x9c\x83\xe5\x88\xa5', to='general.Unit', null=True)),
                ('port_environment', models.ForeignKey(related_name='port_environment', verbose_name=b'\xe6\xb8\xaf\xe5\x8d\x80\xe7\x92\xb0\xe5\xa2\x83\xe6\xb8\x85\xe6\xbd\x94\xe6\x83\x85\xe5\xbd\xa2', to='harbor.Option', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=256, verbose_name=b'\xe5\xb7\xa5\xe7\xa8\x8b\xe5\x90\x8d\xe7\xa8\xb1')),
                ('year', models.IntegerField(null=True, verbose_name=b'\xe5\xb9\xb4\xe5\xba\xa6')),
                ('note', models.CharField(max_length=1024, null=True, verbose_name=b'\xe5\x82\x99\xe8\xa8\xbb')),
                ('plan', models.CharField(max_length=1024, null=True, verbose_name=b'\xe8\xa8\x88\xe7\x95\xab\xe5\x90\x8d\xe7\xa8\xb1')),
                ('schedule_item', models.CharField(max_length=1024, null=True, verbose_name=b'\xe9\xa0\x90\xe5\xae\x9a\xe5\xb7\xa5\xe4\xbd\x9c\xe9\xa0\x85\xe7\x9b\xae')),
                ('reality_item', models.CharField(max_length=1024, null=True, verbose_name=b'\xe5\xaf\xa6\xe9\x9a\x9b\xe5\xb7\xa5\xe4\xbd\x9c\xe9\xa0\x85\xe7\x9b\xae')),
                ('funds_source', models.CharField(max_length=1024, null=True, verbose_name=b'\xe7\xb6\x93\xe8\xb2\xbb\xe4\xbe\x86\xe6\xba\x90')),
                ('funds', models.IntegerField(null=True, verbose_name=b'\xe7\xb6\x93\xe8\xb2\xbb')),
                ('plan_fund', models.IntegerField(null=True, verbose_name=b'\xe8\xa8\x88\xe7\x95\xab\xe7\xb6\x93\xe8\xb2\xbb')),
                ('reality_budget_fund', models.IntegerField(null=True, verbose_name=b'\xe5\xaf\xa6\xe5\x88\x97\xe9\xa0\x90\xe7\xae\x97\xe7\xb6\x93\xe8\xb2\xbb')),
                ('supply_material_fund', models.IntegerField(null=True, verbose_name=b'\xe4\xbe\x9b\xe7\xb5\xa6\xe6\x9d\x90\xe6\x96\x99\xe7\xb6\x93\xe8\xb2\xbb')),
                ('manage_fund', models.IntegerField(null=True, verbose_name=b'\xe7\xae\xa1\xe7\x90\x86\xe7\xb6\x93\xe8\xb2\xbb')),
                ('other_fund', models.IntegerField(null=True, verbose_name=b'\xe5\x85\xb6\xe5\xae\x83\xe7\xb6\x93\xe8\xb2\xbb')),
                ('contract_fund', models.IntegerField(null=True, verbose_name=b'\xe7\x99\xbc\xe5\x8c\x85\xe5\xb7\xa5\xe4\xbd\x9c\xe8\xb2\xbb')),
                ('first_change_design', models.IntegerField(null=True, verbose_name=b'\xe4\xb8\x80\xe6\xac\xa1\xe8\xbf\xbd\xe5\x8a\xa0\xe8\xae\x8a\xe6\x9b\xb4\xe8\xa8\xad\xe8\xa8\x88\xe8\xb2\xbb')),
                ('second_change_design', models.IntegerField(null=True, verbose_name=b'\xe4\xba\x8c\xe6\xac\xa1\xe8\xbf\xbd\xe5\x8a\xa0\xe8\xae\x8a\xe6\x9b\xb4\xe8\xa8\xad\xe8\xa8\x88\xe8\xb2\xbb')),
                ('settlement_fund', models.IntegerField(null=True, verbose_name=b'\xe7\xb5\x90\xe7\xae\x97\xe7\xb6\x93\xe8\xb2\xbb')),
                ('contract_date', models.DateField(null=True, verbose_name=b'\xe7\x99\xbc\xe5\x8c\x85\xe6\x97\xa5\xe6\x9c\x9f')),
                ('design_finish_date', models.DateField(null=True, verbose_name=b'\xe9\xa0\x90\xe5\xae\x9a\xe5\xae\x8c\xe5\xb7\xa5\xe6\x97\xa5\xe6\x9c\x9f')),
                ('first_change_design_date', models.DateField(null=True, verbose_name=b'\xe7\xac\xac\xe4\xb8\x80\xe6\xac\xa1\xe8\xbf\xbd\xe5\x8a\xa0\xe6\x97\xa5\xe6\x9c\x9f')),
                ('second_change_design_date', models.DateField(null=True, verbose_name=b'\xe7\xac\xac\xe4\xba\x8c\xe6\xac\xa1\xe8\xbf\xbd\xe5\x8a\xa0\xe6\x97\xa5\xe6\x9c\x9f')),
                ('act_finish_date', models.DateField(null=True, verbose_name=b'\xe5\xaf\xa6\xe9\x9a\x9b\xe5\xae\x8c\xe5\xb7\xa5\xe6\x97\xa5\xe6\x9c\x9f')),
                ('fishingport', models.ForeignKey(verbose_name=b'\xe6\xbc\x81\xe6\xb8\xaf', to='harbor.FishingPort')),
            ],
        ),
        migrations.CreateModel(
            name='Reef',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=256, verbose_name=b'\xe9\xad\x9a\xe7\xa4\x81\xe5\x90\x8d\xe7\xa8\xb1')),
                ('lon', models.CharField(max_length=256, null=True, verbose_name=b'\xe4\xb8\xad\xe5\xbf\x83\xe9\xbb\x9e\xe7\xb6\x93\xe5\xba\xa6')),
                ('lat', models.CharField(max_length=256, null=True, verbose_name=b'\xe4\xb8\xad\xe5\xbf\x83\xe9\xbb\x9e\xe7\xb7\xaf\xe5\xba\xa6')),
                ('history', models.TextField(default=b'', null=True, verbose_name='\u7c21\u4ecb')),
                ('marked_point', models.CharField(max_length=256, null=True, verbose_name=b'\xe6\xa8\x99\xe7\xa4\xba\xe9\xbb\x9e')),
                ('place', models.ForeignKey(verbose_name=b'\xe7\xb8\xa3\xe5\xb8\x82', to='general.Place', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ReefData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('upload_date', models.DateField(verbose_name=b'\xe4\xb8\x8a\xe5\x82\xb3\xe6\x97\xa5\xe6\x9c\x9f')),
                ('name', models.CharField(default=b'', max_length=256, null=True, verbose_name=b'\xe6\xaa\x94\xe6\xa1\x88\xe5\x90\x8d')),
                ('file', models.ImageField(null=True, upload_to=harbor.models._FRRFDATA_UPLOAD_TO)),
                ('memo', models.CharField(max_length=2048, null=True, verbose_name=b'\xe5\x82\x99\xe8\xa8\xbb\xe8\xaa\xaa\xe6\x98\x8e')),
                ('reef', models.ForeignKey(verbose_name=b'\xe9\xad\x9a\xe7\xa4\x81', to='harbor.Reef')),
            ],
        ),
        migrations.CreateModel(
            name='ReefLocation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=256, null=True, verbose_name=b'\xe5\xba\xa7\xe6\xa8\x99\xe5\x90\x8d\xe7\xa8\xb1')),
                ('lon', models.CharField(max_length=256, null=True, verbose_name=b'\xe4\xb8\xad\xe5\xbf\x83\xe9\xbb\x9e\xe7\xb6\x93\xe5\xba\xa6')),
                ('lat', models.CharField(max_length=256, null=True, verbose_name=b'\xe4\xb8\xad\xe5\xbf\x83\xe9\xbb\x9e\xe7\xb7\xaf\xe5\xba\xa6')),
                ('reef', models.ForeignKey(verbose_name=b'\xe9\xad\x9a\xe7\xa4\x81', to='harbor.Reef')),
            ],
        ),
        migrations.CreateModel(
            name='ReefProject',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('year', models.IntegerField(verbose_name=b'\xe5\xb9\xb4\xe5\xba\xa6')),
                ('name', models.CharField(max_length=512, verbose_name=b'\xe5\xb7\xa5\xe7\xa8\x8b\xe5\x90\x8d\xe7\xa8\xb1')),
                ('price', models.IntegerField(default=0, verbose_name=b'\xe5\xb7\xa5\xe7\xa8\x8b\xe7\xb6\x93\xe8\xb2\xbb(\xe5\x85\x83)')),
                ('reef', models.ForeignKey(verbose_name=b'\xe9\xad\x9a\xe7\xa4\x81', to='harbor.Reef')),
            ],
        ),
        migrations.CreateModel(
            name='ReefPut',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('year', models.IntegerField(verbose_name=b'\xe5\xb9\xb4\xe5\xba\xa6')),
                ('location', models.TextField(default=b'', null=True, verbose_name='\u6295\u7901\u4f4d\u7f6e')),
                ('a_num', models.IntegerField(default=0, verbose_name=b'A\xe5\x9e\x8b\xe6\x95\xb8\xe9\x87\x8f')),
                ('b_num', models.IntegerField(default=0, verbose_name=b'B\xe5\x9e\x8b\xe6\x95\xb8\xe9\x87\x8f')),
                ('deep', models.DecimalField(null=True, verbose_name=b'\xe6\xb0\xb4\xe6\xb7\xb1(M)', max_digits=16, decimal_places=2)),
                ('reef', models.ForeignKey(verbose_name=b'\xe9\xad\x9a\xe7\xa4\x81', to='harbor.Reef')),
            ],
        ),
        migrations.CreateModel(
            name='ReefPutNum',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=256, verbose_name=b'\xe5\x9e\x8b\xe5\xbc\x8f\xe5\x90\x8d\xe7\xa8\xb1')),
                ('num', models.IntegerField(default=0, verbose_name=b'A\xe5\x9e\x8b\xe6\x95\xb8\xe9\x87\x8f')),
                ('reefput', models.ForeignKey(verbose_name=b'\xe9\xad\x9a\xe7\xa4\x81\xe6\x8a\x95\xe6\x94\xbe\xe7\xb4\x80\xe9\x8c\x84', to='harbor.ReefPut')),
            ],
        ),
        migrations.CreateModel(
            name='TempFile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('upload_date', models.DateField(verbose_name=b'\xe4\xb8\x8a\xe5\x82\xb3\xe6\x97\xa5\xe6\x9c\x9f')),
                ('name', models.CharField(default=b'', max_length=256, null=True, verbose_name=b'\xe6\xaa\x94\xe6\xa1\x88\xe5\x90\x8d')),
                ('file', models.ImageField(null=True, upload_to=b'apps\\harbor\\media\\harbor\\tempfile\\%Y%m%d')),
                ('memo', models.CharField(max_length=2048, null=True, verbose_name=b'\xe5\x82\x99\xe8\xa8\xbb\xe8\xaa\xaa\xe6\x98\x8e')),
                ('fishingport', models.ForeignKey(verbose_name=b'\xe6\xbc\x81\xe6\xb8\xaf', to='harbor.FishingPort')),
                ('upload_user', models.ForeignKey(verbose_name=b'\xe4\xb8\x8a\xe5\x82\xb3\xe8\x80\x85', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Tide',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('max_tide', models.DecimalField(null=True, verbose_name=b'\xe6\x9c\x80\xe9\xab\x98\xe6\xbd\xae\xe4\xbd\x8d', max_digits=16, decimal_places=2)),
                ('big_tide_hign_avg', models.DecimalField(null=True, verbose_name=b'\xe5\xa4\xa7\xe6\xbd\xae\xe5\xb9\xb3\xe5\x9d\x87\xe9\xab\x98\xe6\xbd\xae\xe4\xbd\x8d', max_digits=16, decimal_places=2)),
                ('small_tide_hign_avg', models.DecimalField(null=True, verbose_name=b'\xe5\xb0\x8f\xe6\xbd\xae\xe5\xb9\xb3\xe5\x9d\x87\xe9\xab\x98\xe6\xbd\xae\xe4\xbd\x8d', max_digits=16, decimal_places=2)),
                ('tide_avg', models.DecimalField(null=True, verbose_name=b'\xe5\xb9\xb3\xe5\x9d\x87\xe6\xbd\xae\xe4\xbd\x8d', max_digits=16, decimal_places=2)),
                ('big_tide_down_avg', models.DecimalField(null=True, verbose_name=b'\xe5\xa4\xa7\xe6\xbd\xae\xe5\xb9\xb3\xe5\x9d\x87\xe4\xbd\x8e\xe6\xbd\xae\xe4\xbd\x8d', max_digits=16, decimal_places=2)),
                ('small_tide_down_avg', models.DecimalField(null=True, verbose_name=b'\xe5\xb0\x8f\xe6\xbd\xae\xe5\xb9\xb3\xe5\x9d\x87\xe4\xbd\x8e\xe6\xbd\xae\xe4\xbd\x8d', max_digits=16, decimal_places=2)),
                ('min_tide', models.DecimalField(null=True, verbose_name=b'\xe6\x9c\x80\xe4\xbd\x8e\xe6\xbd\xae\xe4\xbd\x8d', max_digits=16, decimal_places=2)),
                ('zero_elevation', models.DecimalField(null=True, verbose_name=b'\xe7\xaf\x89\xe6\xb8\xaf\xe9\xab\x98\xe7\xa8\x8b\xe9\x9b\xb6\xe9\xbb\x9e', max_digits=16, decimal_places=2)),
                ('memo', models.CharField(max_length=1024, null=True, verbose_name=b'\xe5\x82\x99\xe8\xa8\xbb\xe6\xac\x84')),
                ('fishingport', models.ForeignKey(verbose_name=b'\xe6\xbc\x81\xe6\xb8\xaf', to='harbor.FishingPort')),
            ],
        ),
        migrations.CreateModel(
            name='Waves',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.CharField(max_length=256, null=True, verbose_name=b'\xe9\xa1\x9e\xe5\x88\xa5')),
                ('angle', models.CharField(max_length=256, null=True, verbose_name=b'\xe6\xb3\xa2\xe5\x90\x91')),
                ('high', models.DecimalField(verbose_name=b'\xe6\xb3\xa2\xe9\xab\x98(M)', max_digits=10, decimal_places=2)),
                ('cycle', models.DecimalField(verbose_name=b'\xe9\x80\xb1\xe6\x9c\x9f', max_digits=10, decimal_places=2)),
                ('fishingport', models.ForeignKey(verbose_name=b'\xe6\xbc\x81\xe6\xb8\xaf', to='harbor.FishingPort')),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='option',
            unique_together=set([('swarm', 'value')]),
        ),
        migrations.AddField(
            model_name='fishingportphoto',
            name='type',
            field=models.ForeignKey(verbose_name=b'\xe7\x85\xa7\xe7\x89\x87\xe7\xa8\xae\xe9\xa1\x9e', to='harbor.Option'),
        ),
        migrations.AddField(
            model_name='fishingportboat',
            name='boat_type',
            field=models.ForeignKey(verbose_name=b'\xe6\xbc\x81\xe8\x88\xb9\xe7\xa8\xae\xe9\xa1\x9e', to='harbor.Option'),
        ),
        migrations.AddField(
            model_name='fishingportboat',
            name='fishingport',
            field=models.ForeignKey(verbose_name=b'\xe6\xbc\x81\xe6\xb8\xaf', to='harbor.FishingPort'),
        ),
        migrations.AddField(
            model_name='fishingport',
            name='observatory',
            field=models.ForeignKey(verbose_name=b'\xe8\xa7\x80\xe6\xb8\xac\xe7\xab\x99', to='harbor.Observatory', null=True),
        ),
        migrations.AddField(
            model_name='fishingport',
            name='place',
            field=models.ForeignKey(verbose_name=b'\xe7\xb8\xa3\xe5\xb8\x82', to='general.Place'),
        ),
        migrations.AddField(
            model_name='fishingport',
            name='type',
            field=models.ForeignKey(verbose_name=b'\xe7\xac\xac\xe5\xb9\xbe\xe9\xa1\x9e\xe6\xbc\x81\xe6\xb8\xaf', to='harbor.Option'),
        ),
        migrations.AddField(
            model_name='averagetemperature',
            name='observatory',
            field=models.ForeignKey(verbose_name=b'\xe8\xa7\x80\xe6\xb8\xac\xe7\xab\x99', to='harbor.Observatory'),
        ),
        migrations.AddField(
            model_name='averagerainfall',
            name='observatory',
            field=models.ForeignKey(verbose_name=b'\xe8\xa7\x80\xe6\xb8\xac\xe7\xab\x99', to='harbor.Observatory'),
        ),
        migrations.AddField(
            model_name='averagepressure',
            name='observatory',
            field=models.ForeignKey(verbose_name=b'\xe8\xa7\x80\xe6\xb8\xac\xe7\xab\x99', to='harbor.Observatory'),
        ),
    ]
