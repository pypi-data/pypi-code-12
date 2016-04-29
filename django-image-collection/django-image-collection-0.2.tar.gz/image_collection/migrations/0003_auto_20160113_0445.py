# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('image_collection', '0002_auto_20160113_0239'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='imagecollection',
            options={'ordering': ('name', 'identifier'), 'verbose_name': 'image collection', 'verbose_name_plural': 'image collections'},
        ),
        migrations.AlterField(
            model_name='imageslide',
            name='caption_headline',
            field=models.CharField(help_text='This text is displayed as title of the image.', max_length=256, verbose_name='caption headline', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='imageslide',
            name='link',
            field=models.URLField(help_text='Enter URL, that the image should link to.', verbose_name='link', blank=True),
            preserve_default=True,
        ),
    ]
