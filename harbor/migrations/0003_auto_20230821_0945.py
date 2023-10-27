# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('harbor', '0002_auto_20230717_1040'),
    ]

    operations = [
        migrations.AlterField(
            model_name='datashare',
            name='file',
            field=models.ImageField(null=True, upload_to=b'apps\\harbor\\media\\harbor\\datashare\\%Y%m%d'),
        ),
        migrations.AlterField(
            model_name='fishingportphoto',
            name='file',
            field=models.ImageField(null=True, upload_to=b'apps\\harbor\\media\\harbor\\fishingportphoto\\harbor\\%Y%m%d'),
        ),
        migrations.AlterField(
            model_name='observatory',
            name='file',
            field=models.ImageField(null=True, upload_to=b'apps\\harbor\\media\\harbor\\observatory'),
        ),
        migrations.AlterField(
            model_name='tempfile',
            name='file',
            field=models.ImageField(null=True, upload_to=b'apps\\harbor\\media\\harbor\\tempfile\\%Y%m%d'),
        ),
    ]
