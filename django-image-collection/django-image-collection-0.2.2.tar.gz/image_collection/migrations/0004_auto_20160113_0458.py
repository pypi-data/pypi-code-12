# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import image_collection.models


class Migration(migrations.Migration):

    dependencies = [
        ('image_collection', '0003_auto_20160113_0445'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='imageslide',
            name='link',
        ),
        migrations.AddField(
            model_name='imageslide',
            name='external_link',
            field=models.URLField(help_text='E.g. "http://www.example.com/my-page/". Enter absolute URL, that the image should link to.', verbose_name='external link', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='imageslide',
            name='internal_link',
            field=image_collection.models.RelativeURLField(help_text='E.g. "/my-page/". Enter slug of internal pager, that the image should link to.', verbose_name='internal link', blank=True),
            preserve_default=True,
        ),
    ]
