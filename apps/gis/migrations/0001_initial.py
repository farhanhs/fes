# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('harbor', '0002_auto_20230717_1040'),
    ]

    operations = [
        migrations.CreateModel(
            name='PortPhotos',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('lat', models.DecimalField(null=True, verbose_name='\u7def\u5ea6', max_digits=16, decimal_places=9)),
                ('lng', models.DecimalField(null=True, verbose_name='\u7d93\u5ea6', max_digits=16, decimal_places=9)),
                ('name', models.CharField(max_length=254, null=True, verbose_name='\u6a19\u984c')),
                ('memo', models.CharField(max_length=4096, null=True, verbose_name='\u5099\u8a3b')),
                ('file', models.ImageField(null=True, upload_to=b'apps/gis/media/gis/photo/%Y%m%d')),
                ('uploadtime', models.DateTimeField(null=True, verbose_name='\u4e0a\u50b3\u6642\u9593')),
                ('shoot_time', models.DateTimeField(null=True, verbose_name='\u62cd\u7167\u6642\u9593')),
                ('priority', models.IntegerField(null=True, verbose_name='\u512a\u5148\u6b0a')),
                ('disable', models.BooleanField(default=0, verbose_name='\u522a\u9664\u7d00\u9304')),
                ('fishingport', models.ForeignKey(verbose_name=b'\xe6\xbc\x81\xe6\xb8\xaf', to='harbor.FishingPort', null=True)),
                ('uploader', models.ForeignKey(verbose_name='\u4e0a\u50b3\u8005', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
