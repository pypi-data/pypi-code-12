# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('codebehind', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usersecret',
            name='is_verified',
            field=models.BooleanField(default=False),
        ),
    ]
