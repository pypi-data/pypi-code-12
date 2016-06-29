# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import multiselectfield.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('postman', '0013_auto_20160609_0907'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='response',
            field=multiselectfield.db.fields.MultiSelectField(max_length=6, default='YES', choices=[('YES', 'Yes, I have it'), ('NO', "No, I don't have it")]),
        ),
    ]
