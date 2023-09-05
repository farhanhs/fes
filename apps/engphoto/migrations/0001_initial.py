# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import common.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('fishuser', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='CheckPoint',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=128, null=True, verbose_name=b'\xe6\x9f\xa5\xe9\xa9\x97\xe9\xbb\x9e\xe5\x90\x8d\xe7\xa8\xb1', db_index=True)),
                ('need', models.IntegerField(verbose_name=b'\xe9\x9c\x80\xe6\xb1\x82\xe5\xbc\xb5\xe6\x95\xb8')),
                ('help', models.CharField(max_length=256, null=True, verbose_name=b'\xe8\xaa\xaa\xe6\x98\x8e')),
                ('priority', models.IntegerField(verbose_name=b'\xe5\x84\xaa\xe5\x85\x88\xe5\x80\xbc')),
                ('project', models.ForeignKey(verbose_name=b'\xe5\xb7\xa5\xe7\xa8\x8b\xe6\xa1\x88', to='fishuser.Project')),
            ],
            bases=(models.Model, common.models.SelfBaseObject),
        ),
        migrations.CreateModel(
            name='Option',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('swarm', models.CharField(max_length=32, verbose_name=b'\xe7\xbe\xa4')),
                ('value', models.CharField(max_length=64, verbose_name=b'\xe9\x81\xb8\xe9\xa0\x85')),
            ],
            options={
                'verbose_name': '\u9078\u9805',
                'verbose_name_plural': '\u9078\u9805',
            },
        ),
        migrations.CreateModel(
            name='Photo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('position', models.CharField(default=b'', max_length=128, null=True, verbose_name=b'\xe6\xa4\xbf\xe8\x99\x9f\xe4\xbd\x8d\xe7\xbd\xae')),
                ('uploadname', models.CharField(default=b'', max_length=256, null=True, verbose_name=b'\xe4\xb8\x8a\xe5\x82\xb3\xe6\x99\x82\xe6\xaa\x94\xe6\xa1\x88\xe5\x90\x8d')),
                ('file', models.ImageField(null=True, upload_to=b'apps\\engphoto\\photo\\file')),
                ('photodate', models.DateField(null=True, verbose_name=b'\xe6\x8b\x8d\xe7\x85\xa7\xe6\x99\x82\xe9\x96\x93')),
                ('uploadtime', models.DateTimeField(null=True, verbose_name=b'\xe4\xb8\x8a\xe5\x82\xb3\xe6\x99\x82\xe9\x96\x93')),
                ('updatetime', models.DateTimeField(auto_now=True, verbose_name=b'\xe6\xac\x84\xe4\xbd\x8d\xe8\xb3\x87\xe8\xa8\x8a\xe6\x9c\x80\xe5\xbe\x8c\xe6\x9b\xb4\xe6\x96\xb0\xe6\x99\x82\xe9\x96\x93')),
                ('inspector_check', models.NullBooleanField(default=0, verbose_name=b'\xe7\x9b\xa3\xe9\x80\xa0\xe4\xba\xba\xe5\x93\xa1\xe6\x98\xaf\xe5\x90\xa6\xe6\xaa\xa2\xe8\xa6\x96')),
                ('note_con', models.TextField(default=b'', null=True, verbose_name=b'\xe7\x87\x9f\xe9\x80\xa0\xe5\xbb\xa0\xe5\x95\x86\xe6\x84\x8f\xe8\xa6\x8b')),
                ('note_ins', models.TextField(default=b'', null=True, verbose_name=b'\xe7\x9b\xa3\xe9\x80\xa0\xe5\xbb\xa0\xe5\x95\x86\xe6\x84\x8f\xe8\xa6\x8b')),
                ('note_eng', models.TextField(default=b'', null=True, verbose_name=b'\xe4\xb8\xbb\xe8\xbe\xa6\xe6\x84\x8f\xe8\xa6\x8b')),
                ('note_exp', models.TextField(default=b'', null=True, verbose_name=b'\xe5\xb0\x88\xe5\xae\xb6\xe6\x84\x8f\xe8\xa6\x8b')),
                ('priority', models.IntegerField(default=0, verbose_name=b'\xe9\xa0\x86\xe5\xba\x8f')),
                ('checkpoint', models.ForeignKey(verbose_name=b'\xe6\x9f\xa5\xe9\xa9\x97\xe9\xbb\x9e', to='engphoto.CheckPoint')),
                ('duplicatetype', models.ForeignKey(related_name='duplicatetype_set', to='engphoto.Option', null=True)),
                ('enoughtype', models.ForeignKey(related_name='enoughtype_set', to='engphoto.Option', null=True)),
                ('extensiontype', models.ForeignKey(related_name='extensiontype_set', verbose_name=b'\xe9\x99\x84\xe6\xaa\x94\xe5\x90\x8d', to='engphoto.Option', null=True)),
                ('owner', models.ForeignKey(related_name='photo_set', to=settings.AUTH_USER_MODEL, null=True)),
                ('phototype', models.ForeignKey(related_name='phototype_set', verbose_name=b'\xe7\x85\xa7\xe7\x89\x87\xe5\x88\x86\xe9\xa1\x9e', to='engphoto.Option')),
                ('project', models.ForeignKey(verbose_name=b'\xe5\xb7\xa5\xe7\xa8\x8b\xe6\xa1\x88', to='fishuser.Project')),
            ],
            bases=(models.Model, common.models.SelfBaseObject),
        ),
        migrations.CreateModel(
            name='Template',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=64, verbose_name=b'\xe6\x9f\xa5\xe9\xa9\x97\xe9\xbb\x9e\xe5\x90\x8d\xe7\xa8\xb1', db_index=True)),
                ('floor', models.IntegerField(verbose_name=b'\xe6\x9c\x80\xe4\xbd\x8e\xe5\xa5\x97\xe6\x95\xb8/\xe5\xbc\xb5\xe6\x95\xb8')),
                ('help', models.CharField(max_length=512, verbose_name=b'\xe8\xaa\xaa\xe6\x98\x8e')),
                ('require', models.BooleanField(verbose_name=b'\xe5\xbf\x85\xe8\xa6\x81')),
                ('uplevel', models.ForeignKey(related_name='sublevel', to='engphoto.Template', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Verify',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('md5', models.CharField(max_length=34, verbose_name=b'md5\xe7\xa2\xbc', db_index=True)),
            ],
        ),
        migrations.AddField(
            model_name='photo',
            name='verify',
            field=models.ForeignKey(verbose_name=b'\xe7\x9b\xb8\xe7\x89\x87\xe9\xa9\x97\xe8\xad\x89\xe7\xa2\xbc', to='engphoto.Verify', null=True),
        ),
        migrations.AlterUniqueTogether(
            name='option',
            unique_together=set([('swarm', 'value')]),
        ),
        migrations.AddField(
            model_name='checkpoint',
            name='template',
            field=models.ForeignKey(verbose_name=b'\xe6\x89\x80\xe5\xbc\x95\xe8\x87\xaa\xe7\x9a\x84\xe9\x90\xb5\xe7\x89\x88', to='engphoto.Template', null=True),
        ),
        migrations.AddField(
            model_name='checkpoint',
            name='uplevel',
            field=models.ForeignKey(related_name='sublevel', to='engphoto.CheckPoint', null=True),
        ),
    ]
