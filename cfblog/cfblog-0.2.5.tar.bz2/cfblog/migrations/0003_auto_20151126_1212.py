# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('cfblog', '0002_create_static_page_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='content',
            name='auth_data',
            field=jsonfield.fields.JSONField(default={}, help_text="Don't edit this unless you know what this means", verbose_name='author data', blank=True),
        ),
        migrations.AlterField(
            model_name='content',
            name='public_data',
            field=jsonfield.fields.JSONField(default={}, help_text="Don't edit this unless you know what this means", verbose_name='public data', blank=True),
        ),
        migrations.AlterField(
            model_name='content',
            name='publish',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='publish'),
        ),
    ]
