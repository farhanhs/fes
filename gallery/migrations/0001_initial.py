# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from django.conf import settings
import gallery.models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('fishuser', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Case',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('parent', models.OneToOneField(related_name='photo_case', verbose_name=b'\xe7\x88\xb6\xe5\xb1\xa4\xe7\x89\xa9\xe4\xbb\xb6', to='fishuser.Project')),
            ],
            options={
                'permissions': (('view_case', '\u89c0\u770b\u6848\u4ef6'), ('create_node', '\u5efa\u7acb\u7bc0\u9ede'), ('update_node', '\u7de8\u8f2f\u7bc0\u9ede'), ('remove_node', '\u522a\u9664\u7bc0\u9ede'), ('upload_photo', '\u4e0a\u50b3\u7167\u7247'), ('update_photo', '\u7de8\u8f2f\u7167\u7247')),
            },
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('create_time', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'\xe5\xbb\xba\xe7\xab\x8b\xe6\x99\x82\xe9\x96\x93')),
                ('update_time', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'\xe6\x9b\xb4\xe6\x96\xb0\xe6\x99\x82\xe9\x96\x93')),
                ('content', models.TextField(verbose_name=b'\xe5\x85\xa7\xe5\xae\xb9')),
                ('creator', models.ForeignKey(related_name='gallery_comment_ownership', to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'permissions': (('update_comment', '\u4fee\u6539\u8a55\u8ad6'), ('remove_comment', '\u522a\u9664\u8a55\u8ad6')),
            },
        ),
        migrations.CreateModel(
            name='Label',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('create_time', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'\xe5\xbb\xba\xe7\xab\x8b\xe6\x99\x82\xe9\x96\x93')),
                ('update_time', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'\xe6\x9b\xb4\xe6\x96\xb0\xe6\x99\x82\xe9\x96\x93')),
                ('value', models.CharField(max_length=255, verbose_name=b'\xe6\xa8\x99\xe7\xb1\xa4\xe5\x80\xbc')),
                ('name', models.CharField(max_length=255, verbose_name=b'\xe6\xa8\x99\xe7\xb1\xa4\xe5\x90\x8d\xe7\xa8\xb1')),
                ('creator', models.ForeignKey(related_name='gallery_label_ownership', to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Log',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('obj_id', models.IntegerField()),
                ('is_new', models.BooleanField(default=True)),
                ('content_type', models.ForeignKey(related_name='contenttype_log', to='contenttypes.ContentType')),
                ('user', models.ForeignKey(related_name='user_log_set', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Node',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('create_time', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'\xe5\xbb\xba\xe7\xab\x8b\xe6\x99\x82\xe9\x96\x93')),
                ('update_time', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'\xe6\x9b\xb4\xe6\x96\xb0\xe6\x99\x82\xe9\x96\x93')),
                ('name', models.CharField(max_length=255, verbose_name=b'\xe7\xaf\x80\xe9\xbb\x9e\xe5\x90\x8d\xe7\xa8\xb1')),
                ('note', models.TextField(null=True, verbose_name=b'\xe7\xaf\x80\xe9\xbb\x9e\xe5\x82\x99\xe8\xa8\xbb')),
                ('priority', models.PositiveIntegerField(default=10000000, verbose_name=b'\xe6\x8e\x92\xe5\xba\x8f')),
                ('needed_count', models.PositiveIntegerField(default=3, null=True, verbose_name=b'\xe7\x9b\xb8\xe7\x89\x87\xe9\x9c\x80\xe6\xb1\x82\xe5\xbc\xb5\xe6\x95\xb8')),
                ('images_count', models.PositiveIntegerField(default=0, verbose_name=b'\xe4\xb8\x8a\xe5\x82\xb3\xe7\x9b\xb8\xe7\x89\x87\xe5\xbc\xb5\xe6\x95\xb8')),
                ('total_count', models.PositiveIntegerField(default=0, verbose_name=b'\xe7\xb8\xbd\xe7\x9b\xb8\xe7\x89\x87\xe5\xbc\xb5\xe6\x95\xb8')),
                ('default', models.BooleanField(default=False, verbose_name=b'\xe6\x98\xaf\xe5\x90\xa6\xe7\x82\xba\xe9\xa0\x90\xe8\xa8\xad\xe7\xaf\x80\xe9\xbb\x9e')),
                ('improve', models.BooleanField(default=False, verbose_name=b'\xe6\x98\xaf\xe5\x90\xa6\xe7\x82\xba\xe7\xbc\xba\xe5\xa4\xb1\xe6\x94\xb9\xe5\x96\x84\xe8\xb3\x87\xe6\x96\x99')),
                ('case', models.ForeignKey(related_name='nodes', to='gallery.Case', null=True)),
                ('creator', models.ForeignKey(related_name='gallery_node_ownership', to=settings.AUTH_USER_MODEL, null=True)),
                ('parent', models.ForeignKey(related_name='child_nodes', to='gallery.Node', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Option',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('swarm', models.CharField(max_length=64, verbose_name='Swarm')),
                ('value', models.CharField(max_length=512, verbose_name='Value')),
            ],
        ),
        migrations.CreateModel(
            name='Photo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('create_time', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'\xe5\xbb\xba\xe7\xab\x8b\xe6\x99\x82\xe9\x96\x93')),
                ('update_time', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'\xe6\x9b\xb4\xe6\x96\xb0\xe6\x99\x82\xe9\x96\x93')),
                ('photo', models.ImageField(upload_to=gallery.models.photo_path)),
                ('origin', models.CharField(max_length=255, verbose_name=b'\xe5\x8e\x9f\xe5\xa7\x8b\xe6\xaa\x94\xe5\x90\x8d')),
                ('sha_code', models.CharField(max_length=40, verbose_name=b'\xe7\x89\xb9\xe5\xbe\xb5\xe7\xa2\xbc')),
                ('note', models.TextField(null=True, verbose_name=b'\xe5\x82\x99\xe8\xa8\xbb')),
                ('time', models.DateTimeField(null=True, verbose_name=b'\xe6\x8b\x8d\xe7\x85\xa7\xe6\x99\x82\xe9\x96\x93')),
                ('lat', models.DecimalField(null=True, verbose_name=b'\xe7\xb7\xaf\xe5\xba\xa6', max_digits=16, decimal_places=9)),
                ('lng', models.DecimalField(null=True, verbose_name=b'\xe7\xb6\x93\xe5\xba\xa6', max_digits=16, decimal_places=9)),
                ('priority', models.PositiveIntegerField(default=1000, verbose_name=b'\xe6\x8e\x92\xe5\xba\x8f')),
                ('creator', models.ForeignKey(related_name='gallery_photo_ownership', to=settings.AUTH_USER_MODEL, null=True)),
                ('label', models.ManyToManyField(related_name='label_photo', verbose_name=b'\xe9\xa1\x9e\xe5\x88\xa5\xe6\xa8\x99\xe7\xb1\xa4', to='gallery.Label')),
                ('node', models.ForeignKey(related_name='node_photos', to='gallery.Node')),
            ],
            options={
                'permissions': (('remove_photo', '\u522a\u9664\u7167\u7247'),),
            },
        ),
        migrations.CreateModel(
            name='Sample',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('create_time', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'\xe5\xbb\xba\xe7\xab\x8b\xe6\x99\x82\xe9\x96\x93')),
                ('update_time', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'\xe6\x9b\xb4\xe6\x96\xb0\xe6\x99\x82\xe9\x96\x93')),
                ('name', models.CharField(max_length=255, verbose_name=b'\xe7\xaf\x80\xe9\xbb\x9e\xe5\x90\x8d\xe7\xa8\xb1')),
                ('priority', models.PositiveIntegerField(default=10000000, verbose_name=b'\xe6\x8e\x92\xe5\xba\x8f')),
                ('creator', models.ForeignKey(related_name='gallery_sample_ownership', to=settings.AUTH_USER_MODEL, null=True)),
                ('parent', models.ForeignKey(related_name='child_samples', to='gallery.Sample', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Size',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('create_time', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'\xe5\xbb\xba\xe7\xab\x8b\xe6\x99\x82\xe9\x96\x93')),
                ('update_time', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'\xe6\x9b\xb4\xe6\x96\xb0\xe6\x99\x82\xe9\x96\x93')),
                ('name', models.CharField(unique=True, max_length=32, verbose_name=b'\xe5\xb0\xba\xe5\xaf\xb8\xe5\x90\x8d\xe7\xa8\xb1')),
                ('width', models.IntegerField(verbose_name=b'\xe5\xaf\xac\xe5\xba\xa6')),
                ('height', models.IntegerField(verbose_name=b'\xe9\xab\x98\xe5\xba\xa6')),
                ('quality', models.PositiveIntegerField(default=80, verbose_name=b'\xe5\xa3\x93\xe7\xb8\xae\xe5\x93\x81\xe8\xb3\xaa')),
                ('creator', models.ForeignKey(related_name='gallery_size_ownership', to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'permissions': (('manage_size', '\u7ba1\u7406\u7e2e\u5716\u5c3a\u5bf8'),),
            },
        ),
        migrations.CreateModel(
            name='Template',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('create_time', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'\xe5\xbb\xba\xe7\xab\x8b\xe6\x99\x82\xe9\x96\x93')),
                ('update_time', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'\xe6\x9b\xb4\xe6\x96\xb0\xe6\x99\x82\xe9\x96\x93')),
                ('name', models.CharField(max_length=255, verbose_name=b'\xe6\xa8\xa3\xe7\x89\x88\xe5\x90\x8d\xe7\xa8\xb1')),
                ('public', models.BooleanField(default=False, verbose_name=b'\xe6\x98\xaf\xe5\x90\xa6\xe5\x85\xac\xe9\x96\x8b')),
                ('creator', models.ForeignKey(related_name='gallery_template_ownership', to=settings.AUTH_USER_MODEL, null=True)),
                ('label', models.ManyToManyField(related_name='label_template', verbose_name=b'\xe9\xa1\x9e\xe5\x88\xa5\xe6\xa8\x99\xe7\xb1\xa4', to='gallery.Label')),
                ('sample', models.ManyToManyField(related_name='node_template', verbose_name=b'\xe6\xa8\xa3\xe7\x89\x88\xe7\xaf\x80\xe9\xbb\x9e', to='gallery.Sample')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Thumbnail',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('create_time', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'\xe5\xbb\xba\xe7\xab\x8b\xe6\x99\x82\xe9\x96\x93')),
                ('update_time', models.DateTimeField(default=datetime.datetime.now, verbose_name=b'\xe6\x9b\xb4\xe6\x96\xb0\xe6\x99\x82\xe9\x96\x93')),
                ('url', models.CharField(max_length=256, verbose_name=b'\xe7\xb8\xae\xe5\x9c\x96\xe8\xb7\xaf\xe5\xbe\x91')),
                ('creator', models.ForeignKey(related_name='gallery_thumbnail_ownership', to=settings.AUTH_USER_MODEL, null=True)),
                ('original', models.ForeignKey(related_name='thumbnails', to='gallery.Photo')),
                ('size', models.ForeignKey(related_name='same_size', to='gallery.Size')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='comment',
            name='photo',
            field=models.ForeignKey(related_name='photo_comments', to='gallery.Photo'),
        ),
        migrations.AlterUniqueTogether(
            name='size',
            unique_together=set([('width', 'height')]),
        ),
    ]
