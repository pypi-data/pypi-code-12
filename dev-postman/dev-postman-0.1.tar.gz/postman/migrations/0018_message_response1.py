# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import multiselectfield.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('postman', '0017_auto_20160609_1049'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='response1',
            field=multiselectfield.db.fields.MultiSelectField(blank=True, max_length=6, null=True, choices=[('YES', 'Yes, I have it'), ('NO', "No, I don't have it")]),
        ),
    ]
