# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('postman', '0003_auto_20160510_1448'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='message',
            name='subject1',
        ),
    ]
