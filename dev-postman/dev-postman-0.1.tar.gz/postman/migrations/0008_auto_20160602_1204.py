# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('postman', '0007_message_response'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='response',
            field=models.CharField(max_length=10, default=None, blank=True, choices=[('YES', 'Yes, I have it'), ('NO', "No, I don't have it")]),
        ),
    ]
