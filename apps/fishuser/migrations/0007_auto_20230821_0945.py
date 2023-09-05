# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fishuser', '0006_auto_20230717_1219'),
    ]

    operations = [
        migrations.AlterField(
            model_name='frcmtempfile',
            name='file',
            field=models.ImageField(null=True, upload_to=b'apps\\frcm\\media\\frcm\\tempfile\\%Y%m%d'),
        ),
        migrations.AlterField(
            model_name='projectphoto',
            name='file',
            field=models.ImageField(null=True, upload_to=b'apps\\project\\media\\project\\photo\\%Y%m%d'),
        ),
    ]
