# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('image_collection', '0009_imageslide_update_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='imageslide',
            name='update_date',
            field=models.DateTimeField(auto_now=True, verbose_name='update date', null=True),
        ),
    ]
