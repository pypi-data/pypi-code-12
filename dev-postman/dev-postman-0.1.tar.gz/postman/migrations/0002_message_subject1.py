# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import multiselectfield.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('postman', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='subject1',
            field=multiselectfield.db.fields.MultiSelectField(choices=[('I HAVE', 'I HAVE'), ('DONT HAVE', 'DONT HAVE')], null=True, blank=True, max_length=16),
        ),
    ]
