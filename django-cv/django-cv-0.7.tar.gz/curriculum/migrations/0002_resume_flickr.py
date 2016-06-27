# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('curriculum', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='resume',
            name='flickr',
            field=models.CharField(max_length=20, null=True, verbose_name='Flickr ID', blank=True),
        ),
    ]
