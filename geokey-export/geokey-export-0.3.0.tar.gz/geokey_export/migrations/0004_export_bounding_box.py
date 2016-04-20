# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.contrib.gis.db.models.fields


class Migration(migrations.Migration):

    dependencies = [
        ('geokey_export', '0003_export_urlhash'),
    ]

    operations = [
        migrations.AddField(
            model_name='export',
            name='bounding_box',
            field=django.contrib.gis.db.models.fields.PolygonField(srid=4326, null=True, geography=True),
        ),
    ]
