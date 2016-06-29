# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import multiselectfield.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('postman', '0016_auto_20160609_1033'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='response',
            field=multiselectfield.db.fields.MultiSelectField(null=True, choices=[('YES', 'Yes, I have it'), ('NO', "No, I don't have it")], blank=True, max_length=6),
        ),
    ]
