# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Request',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('uuid', models.CharField(default=uuid.uuid4, max_length=127, verbose_name=b'UUID')),
                ('url', models.URLField(verbose_name=b'URL')),
                ('max_retries', models.PositiveIntegerField(default=3)),
                ('retries', models.PositiveIntegerField(default=0)),
                ('last_try', models.DateTimeField(null=True, blank=True)),
                ('status', models.PositiveIntegerField(default=0, choices=[(0, b'New'), (1, b'Running'), (2, b'Retrying'), (3, b'Failed'), (4, b'Ready')])),
                ('comment', models.TextField(blank=True)),
            ],
        ),
    ]
