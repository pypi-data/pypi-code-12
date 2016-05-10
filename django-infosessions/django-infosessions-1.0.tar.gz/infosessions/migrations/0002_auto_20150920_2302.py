# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('infosessions', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sessioninfo',
            name='user_ip',
            field=models.GenericIPAddressField(default='127.0.0.1', db_index=True),
        ),
    ]
