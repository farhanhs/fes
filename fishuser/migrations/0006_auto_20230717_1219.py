# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fishuser', '0005_auto_20230717_1217'),
    ]

    operations = [
        migrations.RenameField(
            model_name='countychaseprojectonebyone',
            old_name='T_date',
            new_name='test_date',
        ),
    ]
