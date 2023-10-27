# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('general', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='CityFiles',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('location', models.CharField(max_length=2048, null=True, verbose_name=b'\xe5\x9c\xb0\xe6\x96\xb9')),
                ('upload_date', models.DateField(verbose_name=b'\xe4\xb8\x8a\xe5\x82\xb3\xe6\x97\xa5\xe6\x9c\x9f')),
                ('name', models.CharField(default=b'', max_length=256, null=True, verbose_name=b'\xe6\xaa\x94\xe6\xa1\x88\xe5\x90\x8d')),
                ('file', models.ImageField(null=True, upload_to=b'apps\\frcm\\static\\frcm\\cityfile\\%Y%m%d')),
                ('memo', models.CharField(max_length=2048, null=True, verbose_name=b'\xe5\x82\x99\xe8\xa8\xbb\xe8\xaa\xaa\xe6\x98\x8e')),
                ('lat', models.DecimalField(null=True, verbose_name='\u7def\u5ea6', max_digits=16, decimal_places=9)),
                ('lng', models.DecimalField(null=True, verbose_name='\u7d93\u5ea6', max_digits=16, decimal_places=9)),
                ('place', models.ForeignKey(verbose_name=b'\xe7\xb8\xa3\xe5\xb8\x82', to='general.Place')),
                ('upload_user', models.ForeignKey(verbose_name=b'\xe4\xb8\x8a\xe5\x82\xb3\xe8\x80\x85', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
