# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('image_collection', '0006_imageslide_data_class'),
    ]

    operations = [
        migrations.AddField(
            model_name='imageslide',
            name='is_visible_on_mobile',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='imageslide',
            name='mobile_link',
            field=models.CharField(help_text='i.e. "{route: "shop/cateogry", categoryName: "artworks"}"', max_length=4000, verbose_name='mobile link', blank=True),
        ),
    ]
