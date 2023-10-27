# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('supervise', '0010_auto_20230825_1043'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='errorphotofile',
            name='supervisecase',
        ),
        migrations.DeleteModel(
            name='ErrorPhotoFile',
        ),
    ]
