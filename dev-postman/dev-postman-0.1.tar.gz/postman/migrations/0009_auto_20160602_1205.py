# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('postman', '0008_auto_20160602_1204'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='response',
            field=models.CharField(null=True, blank=True, choices=[('YES', 'Yes, I have it'), ('NO', "No, I don't have it")], max_length=10),
        ),
    ]
