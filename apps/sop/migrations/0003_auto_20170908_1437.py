# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('sop', '0002_auto_20170908_1318'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sop',
            name='release_date',
            field=models.DateField(default=datetime.datetime(2017, 9, 8, 14, 37, 12, 788000)),
        ),
    ]
