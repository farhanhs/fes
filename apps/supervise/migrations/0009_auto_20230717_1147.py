# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import supervise.models


class Migration(migrations.Migration):

    dependencies = [
        ('supervise', '0008_auto_20230717_1136'),
    ]

    operations = [
        migrations.AlterField(
            model_name='errorphotofile',
            name='file',
            field=models.ImageField(null=True, upload_to=supervise.models._FILE_UPLOAD_TO),
        ),
    ]
