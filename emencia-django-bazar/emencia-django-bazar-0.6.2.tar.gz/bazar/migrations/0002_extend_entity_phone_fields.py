# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bazar', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='entity',
            name='fax',
            field=models.CharField(max_length=20, verbose_name='fax', blank=True),
        ),
        migrations.AlterField(
            model_name='entity',
            name='phone',
            field=models.CharField(max_length=20, verbose_name='phone', blank=True),
        ),
    ]
