# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
import help.models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('model', models.CharField(max_length=128, verbose_name='\u91dd\u5c0d\u6a21\u7d44')),
                ('name', models.CharField(max_length=256, verbose_name='\u529f\u80fd\u540d\u7a31')),
                ('sort', models.DecimalField(default=0, verbose_name='\u6392\u7248\u5e8f\u865f', max_digits=16, decimal_places=5)),
                ('file_name', models.CharField(max_length=256, verbose_name='\u6a94\u6848\u540d\u7a31')),
                ('memo', models.CharField(max_length=256, verbose_name='\u6559\u5b78\u7c21\u4ecb')),
            ],
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ask', models.TextField(null=True, verbose_name='\u63d0\u554f')),
                ('ask_time', models.DateTimeField(default=datetime.datetime.now, verbose_name='\u63d0\u554f\u6642\u9593')),
                ('answer', models.TextField(null=True, verbose_name='\u56de\u7b54')),
                ('answer_time', models.DateTimeField(null=True, verbose_name='\u56de\u7b54\u6642\u9593')),
                ('is_good_question', models.BooleanField(default=False, verbose_name='\u662f\u5426\u70ba\u5e38\u898b\u554f\u984c')),
                ('completer', models.ForeignKey(related_name='completer_question', verbose_name='\u89e3\u6c7a/\u56de\u7b54\u554f\u984c\u7684\u4eba', to=settings.AUTH_USER_MODEL, null=True)),
                ('user', models.ForeignKey(related_name='completer_user', verbose_name='\u63d0\u554f\u8005', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='QuestionFile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(default=b'', max_length=256, null=True, verbose_name=b'\xe6\xaa\x94\xe6\xa1\x88\xe5\x90\x8d')),
                ('file', models.FileField(null=True, upload_to=help.models._UPLOAD_TO)),
                ('question', models.ForeignKey(verbose_name='\u5de5\u7a0b\u6848', to='help.Question', null=True)),
            ],
        ),
    ]
