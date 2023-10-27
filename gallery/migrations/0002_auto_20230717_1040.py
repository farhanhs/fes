# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gallery', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='case',
            options={'permissions': (('view_case', '\u89c0\u770b\u6848\u4ef6'), ('create_node', '\u5efa\u7acb\u7bc0\u9ede'), ('update_node', '\u7de8\u8f2f\u7bc0\u9ede'), ('remove_node', '\u522a\u9664\u7bc0\u9ede'), ('upload_photo', '\u4e0a\u50b3\u7167\u7247'), ('update_photo', '\u7de8\u8f2f\u7167\u7247'), ('verify_public', '\u6838\u53ef\u516c\u958b'))},
        ),
        migrations.AddField(
            model_name='photo',
            name='is_public',
            field=models.BooleanField(default=False, verbose_name=b'\xe6\x98\xaf\xe5\x90\xa6\xe6\xa0\xb8\xe5\x8f\xaf\xe5\x85\xac\xe9\x96\x8b'),
        ),
    ]
