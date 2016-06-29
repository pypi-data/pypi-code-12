# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('postman', '0018_message_response1'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='message',
            name='response1',
        ),
    ]
