# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('postman', '0006_remove_message_avatar'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='response',
            field=models.CharField(max_length=10, null=True, blank=True, choices=[('YES', 'Yes, I have it'), ('NO', "No, I don't have it")]),
        ),
    ]
