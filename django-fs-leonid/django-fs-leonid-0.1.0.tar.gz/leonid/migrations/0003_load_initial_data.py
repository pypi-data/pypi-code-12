# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


import os
from django.core import serializers


def load_fixture(apps, schema_editor):
    fixture_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../fixtures'))
    fixture_file_name = 'initial_data.json'
    fixture_file_path = os.path.join(fixture_dir, fixture_file_name)
    with open(fixture_file_path, 'r') as fixture_file:
        objects = serializers.deserialize('json', fixture_file, ignorenonexistent=True)
        for obj in objects:
            obj.save()


def unload_fixture(apps, schema_editor):
    LeonidFile = apps.get_model('leonid', 'LeonidFile')
    LeonidFile.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('leonid', '0002_leonidfile'),
    ]

    operations = [
        migrations.RunPython(load_fixture, reverse_code=unload_fixture),
    ]
