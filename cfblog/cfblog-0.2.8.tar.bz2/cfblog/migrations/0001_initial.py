# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
import re
import cfblog.validators
import tagging.fields
import jsonfield.fields
from django.conf import settings
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(unique=True, max_length=100, verbose_name='title', db_index=True)),
                ('description', models.TextField(verbose_name='description')),
            ],
            options={
                'ordering': ('title',),
                'verbose_name_plural': 'categories',
            },
        ),
        migrations.CreateModel(
            name='Content',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.CharField(db_index=True, unique=True, max_length=255, verbose_name='url path', validators=[django.core.validators.RegexValidator(re.compile('^/(?:[-a-zA-Z0-9_]+/)*$'), "Enter a valid 'url path'. Path should start and end with '/'.", 'invalid')])),
                ('template', models.CharField(max_length=255, verbose_name='template', validators=[cfblog.validators.validate_and_get_template])),
                ('status', models.IntegerField(default=1, verbose_name='status', choices=[(1, 'Draft'), (2, 'Public')])),
                ('publish', models.DateTimeField(default=datetime.datetime.now, verbose_name='publish')),
                ('title', models.CharField(max_length=200, verbose_name='title')),
                ('tags', tagging.fields.TagField(max_length=255, blank=True)),
                ('tease', models.TextField(help_text='Concise text suggested. Does not appear in RSS feed.', verbose_name='tease', blank=True)),
                ('notes_todos', models.TextField(verbose_name='Notes and Todos', blank=True)),
                ('auth_data', jsonfield.fields.JSONField(default={}, help_text="Don't edit this unless you know what this means", verbose_name='author data')),
                ('public_data', jsonfield.fields.JSONField(default={}, help_text="Don't edit this unless you know what this means", verbose_name='public data')),
                ('created_on', models.DateTimeField(auto_now_add=True, verbose_name='created on')),
                ('modified_on', models.DateTimeField(auto_now=True, verbose_name='modified on')),
                ('author', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('category', models.ForeignKey(to='cfblog.Category')),
            ],
            options={
                'ordering': ('-publish',),
                'get_latest_by': 'publish',
            },
        ),
    ]
