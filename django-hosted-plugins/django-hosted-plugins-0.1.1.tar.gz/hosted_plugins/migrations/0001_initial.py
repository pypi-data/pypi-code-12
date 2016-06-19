# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Platform',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('platform', models.SlugField(max_length=255)),
                ('plugin', models.SlugField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Update',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('min_reqd', models.CharField(max_length=32)),
                ('max_tested', models.CharField(default=b'', max_length=32, blank=True)),
                ('version', models.CharField(max_length=32)),
                ('release_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('archive_type', models.SmallIntegerField(choices=[(1, b'zip'), (2, b'tar.gz')])),
                ('filesize', models.IntegerField(default=0)),
                ('downloads', models.IntegerField(default=0)),
                ('platform', models.ForeignKey(related_name='updates', to='hosted_plugins.Platform')),
            ],
        ),
        migrations.CreateModel(
            name='Checksum',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('checksum_type', models.SmallIntegerField(choices=[(1, b'crc32'), (2, b'md5'), (3, b'sha1'), (4, b'sha256')])),
                ('checksum', models.CharField(max_length=64)),
                ('update', models.ForeignKey(related_name='checksums', to='hosted_plugins.Update')),
            ],
        ),
        migrations.CreateModel(
            name='Documentation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=100)),
                ('slug', models.SlugField()),
                ('content', models.TextField()),
                ('created_on', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.AddField(
            model_name='update',
            name='docs',
            field=models.ManyToManyField(related_name='updates', to='hosted_plugins.Documentation', blank=True),
        ),
    ]
