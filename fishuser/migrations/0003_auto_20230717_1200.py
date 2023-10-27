# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fishuser', '0002_auto_20230717_1147'),
    ]

    operations = [
        migrations.AlterField(
            model_name='countychaseprojectonebyone',
            name='test_date',
            field=models.DateField(verbose_name='\u6e2c\u8a66\u65e5\u671f'),
        ),
    ]
