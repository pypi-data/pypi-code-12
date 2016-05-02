# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('server_guardian', '0004_remove_server_logging'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='server',
            name='response_body',
        ),
        migrations.RemoveField(
            model_name='server',
            name='status_code',
        ),
        migrations.AddField(
            model_name='serverlog',
            name='response_body',
            field=models.TextField(verbose_name='server response', blank=True),
        ),
        migrations.AddField(
            model_name='serverlog',
            name='status_code',
            field=models.CharField(default='200', max_length=3, verbose_name='status code'),
            preserve_default=False,
        ),
    ]
