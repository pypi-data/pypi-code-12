# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import multiselectfield.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('postman', '0014_auto_20160609_0943'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='response',
            field=multiselectfield.db.fields.MultiSelectField(null=True, blank=True, choices=[('YES', 'Yes, I have it'), ('NO', "No, I don't have it")], max_length=6),
        ),
    ]
