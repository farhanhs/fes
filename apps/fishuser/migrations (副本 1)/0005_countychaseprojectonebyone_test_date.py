# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fishuser', '0004_remove_countychaseprojectonebyone_test_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='countychaseprojectonebyone',
            name='test_date',
            field=models.DateField(null=True, verbose_name='\u6e2c\u8a66\u65e5\u671f'),
        ),
    ]
