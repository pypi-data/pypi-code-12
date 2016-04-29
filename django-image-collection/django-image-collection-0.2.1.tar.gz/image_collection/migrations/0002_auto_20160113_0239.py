# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('image_collection', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='imageslide',
            name='caption_headline',
            field=models.CharField(help_text='This text is displayed as title of the image.', max_length=256, verbose_name='caption', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='imageslide',
            name='caption',
            field=models.CharField(help_text='This text is displayed as description of the image.', max_length=512, verbose_name='caption', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='imageslide',
            name='link',
            field=models.URLField(help_text='Enter URL, that the image should link to.', verbose_name='link'),
            preserve_default=True,
        ),
    ]
