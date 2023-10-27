# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('frcm', '0002_auto_20230717_1147'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cityfiles',
            name='file',
            field=models.ImageField(null=True, upload_to=b'apps\\frcm\\media\\frcm\\cityfile\\%Y%m%d'),
        ),
    ]
