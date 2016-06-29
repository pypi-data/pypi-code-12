# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import multiselectfield.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('postman', '0015_auto_20160609_0945'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='response',
            field=multiselectfield.db.fields.MultiSelectField(verbose_name='response', null=True, choices=[('YES', 'Yes, I have it'), ('NO', "No, I don't have it")], max_length=6, blank=True),
        ),
    ]
