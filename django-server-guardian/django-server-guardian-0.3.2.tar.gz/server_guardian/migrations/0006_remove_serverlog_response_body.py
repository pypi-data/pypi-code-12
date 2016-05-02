# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('server_guardian', '0005_auto_20160222_0420'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='serverlog',
            name='response_body',
        ),
    ]
