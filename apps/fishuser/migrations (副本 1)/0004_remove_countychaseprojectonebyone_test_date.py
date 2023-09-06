# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fishuser', '0003_auto_20230717_1040'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='countychaseprojectonebyone',
            name='test_date',
        ),
    ]
