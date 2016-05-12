# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('image_collection', '0008_auto_20160306_2156'),
    ]

    operations = [
        migrations.AddField(
            model_name='imageslide',
            name='update_date',
            field=models.DateTimeField(null=True, verbose_name='update date', blank=True),
        ),
    ]
