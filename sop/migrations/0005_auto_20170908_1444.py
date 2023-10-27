# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('sop', '0004_auto_20170908_1443'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sop',
            name='release_date',
            field=models.DateField(default=datetime.datetime.now),
        ),
    ]
