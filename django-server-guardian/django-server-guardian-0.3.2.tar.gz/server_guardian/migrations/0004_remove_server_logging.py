# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('server_guardian', '0003_auto_20160222_0343'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='server',
            name='logging',
        ),
    ]
