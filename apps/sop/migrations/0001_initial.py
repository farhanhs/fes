# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import sop.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('version', models.CharField(max_length=8)),
                ('name', models.CharField(max_length=50)),
                ('ext', models.CharField(max_length=20)),
                ('file', models.FileField(null=True, upload_to=sop.models._DOCUMENT_UPLOAD_TO)),
                ('is_use', models.BooleanField(default=True)),
                ('upload_time', models.DateTimeField()),
                ('memo', models.TextField(verbose_name='\u5099\u8a3b')),
            ],
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128, verbose_name='\u8868\u55ae')),
                ('type', models.IntegerField(choices=[(0, b'\xe6\xa8\x99\xe6\xba\x96\xe6\xb5\x81\xe7\xa8\x8b\xe5\x9c\x96'), (1, b'\xe6\xa8\x99\xe6\xba\x96\xe4\xbd\x9c\xe6\xa5\xad\xe6\x9b\xb8'), (2, b'\xe8\xa1\xa8\xe5\x96\xae'), (3, b'\xe6\xa8\x99\xe6\xba\x96\xe6\xb5\x81\xe7\xa8\x8b\xe5\x9c\x96-vsd')])),
            ],
        ),
        migrations.CreateModel(
            name='Sop',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=128, verbose_name='\u6a19\u984c')),
                ('is_use', models.BooleanField(default=False)),
                ('release_date', models.DateField(auto_now=True)),
                ('memo', models.TextField(verbose_name='\u5099\u8a3b')),
                ('priority', models.IntegerField()),
            ],
            options={
                'permissions': (('edit_sop', '\u7ba1\u7406\u7de8\u8f2fSOP'),),
            },
        ),
        migrations.AddField(
            model_name='item',
            name='sop',
            field=models.ForeignKey(related_name='item_sop', verbose_name='\u6a19\u6e96\u4f5c\u696d\u7a0b\u5e8f', to='sop.Sop', null=True),
        ),
        migrations.AddField(
            model_name='file',
            name='item',
            field=models.ForeignKey(related_name='file_item', verbose_name='\u6587\u4ef6', to='sop.Item', null=True),
        ),
    ]
