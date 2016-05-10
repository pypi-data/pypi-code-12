# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('infosessions', '0002_auto_20150920_2302'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='sessioninfo',
            options={'verbose_name': 'Session', 'verbose_name_plural': 'Sessions'},
        ),
        migrations.AlterField(
            model_name='sessioninfo',
            name='creation_date',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Creation date'),
        ),
        migrations.AlterField(
            model_name='sessioninfo',
            name='key',
            field=models.CharField(max_length=32, verbose_name='Key', db_index=True),
        ),
        migrations.AlterField(
            model_name='sessioninfo',
            name='user',
            field=models.ForeignKey(related_name='sessions', verbose_name='User', to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
