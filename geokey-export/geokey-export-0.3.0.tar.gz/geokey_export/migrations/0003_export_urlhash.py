# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('geokey_export', '0002_export_isoneoff'),
    ]

    operations = [
        migrations.AddField(
            model_name='export',
            name='urlhash',
            field=models.CharField(default=1, max_length=40),
            preserve_default=False,
        ),
    ]
