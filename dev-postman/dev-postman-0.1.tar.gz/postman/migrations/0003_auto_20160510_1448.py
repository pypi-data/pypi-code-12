# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('postman', '0002_message_subject1'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='subject1',
            field=models.CharField(choices=[('I HAVE', 'I HAVE'), ('DONT HAVE', 'DONT HAVE')], max_length=120, null=True, blank=True),
        ),
    ]
