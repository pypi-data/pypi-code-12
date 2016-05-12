# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('image_collection', '0007_auto_20160306_2059'),
    ]

    operations = [
        migrations.AlterField(
            model_name='imageslide',
            name='data_class',
            field=models.CharField(help_text='Set this if you want to handle click events on this image via JavaScript.', max_length=512, verbose_name='data class', blank=True),
        ),
    ]
