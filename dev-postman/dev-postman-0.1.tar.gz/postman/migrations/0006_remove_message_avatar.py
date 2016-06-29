# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('postman', '0005_message_avatar'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='message',
            name='avatar',
        ),
    ]
