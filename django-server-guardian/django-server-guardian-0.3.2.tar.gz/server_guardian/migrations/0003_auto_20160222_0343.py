# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('server_guardian', '0002_auto_20160222_0336'),
    ]

    operations = [
        migrations.AlterField(
            model_name='serverlog',
            name='time_logged',
            field=models.DateTimeField(auto_now=True, verbose_name='time_logged'),
        ),
    ]
