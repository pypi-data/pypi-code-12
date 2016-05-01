# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Action',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('actor_object_id', models.CharField(max_length=500, null=True, blank=True)),
                ('verb', models.CharField(max_length=500)),
                ('action_object_id', models.CharField(max_length=500, null=True, blank=True)),
                ('target_object_id', models.CharField(max_length=500, null=True, blank=True)),
                ('is_public', models.BooleanField(default=True)),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now, blank=True)),
                ('action_content_type', models.ForeignKey(related_name='action', blank=True, to='contenttypes.ContentType', null=True)),
                ('actor_content_type', models.ForeignKey(related_name='actor', blank=True, to='contenttypes.ContentType', null=True)),
                ('target_content_type', models.ForeignKey(related_name='target', blank=True, to='contenttypes.ContentType', null=True)),
            ],
            options={
                'ordering': ('-timestamp',),
            },
        ),
    ]
