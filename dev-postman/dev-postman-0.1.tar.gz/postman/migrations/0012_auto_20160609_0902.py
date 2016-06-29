# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import multiselectfield.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('postman', '0011_auto_20160602_1342'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='response',
            field=multiselectfield.db.fields.MultiSelectField(blank=True, max_length=6, default=0, null=True, choices=[('YES', 'Yes, I have it'), ('NO', "No, I don't have it")]),
        ),
    ]
