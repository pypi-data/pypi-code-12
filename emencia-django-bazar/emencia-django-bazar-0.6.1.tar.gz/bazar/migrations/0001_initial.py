# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import bazar.models
import django.core.files.storage
from django.conf import settings
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0002_auto_20150616_2121'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Entity',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(verbose_name='created', null=True, editable=False, blank=True)),
                ('modified', models.DateTimeField(verbose_name='modified', null=True, editable=False, blank=True)),
                ('kind', models.CharField(default=b'customer', max_length=40, verbose_name='kind', choices=[(b'customer', 'Customer'), (b'supplier', 'Supplier'), (b'internal', 'Internal'), (b'administration', 'Administration')])),
                ('name', models.CharField(unique=True, max_length=255, verbose_name='name')),
                ('adress', models.TextField(verbose_name='full adress', blank=True)),
                ('phone', models.CharField(max_length=15, verbose_name='phone', blank=True)),
                ('fax', models.CharField(max_length=15, verbose_name='fax', blank=True)),
                ('town', models.CharField(max_length=75, verbose_name='town', blank=True)),
                ('zipcode', models.CharField(max_length=6, verbose_name='zipcode', blank=True)),
            ],
            options={
                'verbose_name': 'Entity',
                'verbose_name_plural': 'Entities',
            },
        ),
        migrations.CreateModel(
            name='Note',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(verbose_name='created', null=True, editable=False, blank=True)),
                ('modified', models.DateTimeField(verbose_name='modified', null=True, editable=False, blank=True)),
                ('title', models.CharField(max_length=150, verbose_name='title')),
                ('content', models.TextField(verbose_name='content', blank=True)),
                ('file', models.FileField(upload_to=bazar.models.get_file_uploadto, storage=django.core.files.storage.FileSystemStorage(base_url=b'/protected_medias', location=b'/home/emencia/projects/new-extranet/project/protected_medias'), max_length=255, blank=True, null=True, verbose_name='file')),
                ('author', models.ForeignKey(verbose_name='author', to=settings.AUTH_USER_MODEL)),
                ('entity', models.ForeignKey(verbose_name='entity', blank=True, to='bazar.Entity', null=True)),
                ('tags', taggit.managers.TaggableManager(to='taggit.Tag', through='taggit.TaggedItem', help_text='A comma-separated list of tags.', verbose_name='Tags')),
            ],
            options={
                'verbose_name': 'Note',
                'verbose_name_plural': 'Notes',
            },
        ),
    ]
