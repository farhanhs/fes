# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gis', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='portphotos',
            name='file',
            field=models.ImageField(null=True, upload_to=b'apps\\gis\\media\\gis\\photo\\%Y%m%d'),
        ),
    ]
