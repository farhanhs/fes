# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import common.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Option',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('swarm', models.CharField(max_length=32, verbose_name='\u7fa4')),
                ('value', models.CharField(max_length=64, verbose_name='\u9078\u9805')),
            ],
            options={
                'verbose_name': '\u9078\u9805',
                'verbose_name_plural': '\u9078\u9805',
            },
        ),
        migrations.CreateModel(
            name='Place',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128, verbose_name='\u5340\u57df\u540d\u7a31')),
                ('zipcode', models.CharField(max_length=20, verbose_name='\u90f5\u905e\u5340\u865f')),
                ('update_time', models.DateTimeField(auto_now=True)),
                ('uplevel', models.ForeignKey(related_name='uplevel_subregion', to='general.Place', null=True)),
            ],
            options={
                'ordering': ('name',),
                'verbose_name': '\u5340\u57df\u540d',
                'verbose_name_plural': '\u5340\u57df\u540d',
            },
        ),
        migrations.CreateModel(
            name='Unit',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128, verbose_name=b'\xe5\x90\x8d\xe7\xa8\xb1')),
                ('fullname', models.CharField(max_length=256, verbose_name=b'\xe5\x85\xa8\xe5\x90\x8d')),
                ('no', models.CharField(unique=True, max_length=8, verbose_name=b'\xe7\xb5\xb1\xe4\xb8\x80\xe7\xb7\xa8\xe8\x99\x9f')),
                ('chairman', models.CharField(max_length=64, null=True, verbose_name=b'\xe8\xb2\xa0\xe8\xb2\xac\xe4\xba\xba')),
                ('capital', models.PositiveIntegerField(null=True)),
                ('birthday', models.DateField(null=True, verbose_name=b'\xe8\xa8\xad\xe7\xab\x8b\xe6\x97\xa5\xe6\x9c\x9f')),
                ('operation', models.TextField(null=True, verbose_name=b'\xe7\x87\x9f\xe6\xa5\xad\xe9\xa0\x85\xe7\x9b\xae')),
                ('html', models.TextField(null=True, verbose_name=b'\xe8\xbc\xb8\xe5\x85\xa5 html \xe7\xa2\xbc')),
                ('address', models.CharField(max_length=256, null=True, verbose_name=b'\xe5\x9c\xb0\xe5\x9d\x80')),
                ('phone', models.CharField(max_length=20, null=True, verbose_name=b'\xe9\x9b\xbb\xe8\xa9\xb1')),
                ('fax', models.CharField(max_length=20, null=True, verbose_name=b'\xe5\x82\xb3\xe7\x9c\x9f')),
                ('website', models.URLField(null=True, verbose_name=b'\xe7\xb6\xb2\xe5\x9d\x80')),
                ('email', models.EmailField(max_length=254, null=True, verbose_name=b'E-mail')),
                ('kind', models.ForeignKey(verbose_name=b'\xe7\xb5\x84\xe7\xb9\x94\xe7\xa8\xae\xe9\xa1\x9e', to='general.Option', null=True)),
                ('place', models.ForeignKey(to='general.Place')),
                ('uplevel', models.ForeignKey(related_name='uplevel_subunit', to='general.Unit', null=True)),
            ],
            options={
                'ordering': ('fullname', 'name'),
                'verbose_name': '\u516c\u53f8\u6a5f\u95dc\u55ae\u4f4d',
                'verbose_name_plural': '\u516c\u53f8\u6a5f\u95dc\u55ae\u4f4d',
            },
            bases=(models.Model, common.models.SelfBaseObject),
        ),
        migrations.AlterUniqueTogether(
            name='option',
            unique_together=set([('swarm', 'value')]),
        ),
    ]
