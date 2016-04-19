# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import shuyucms.core.fields


class Migration(migrations.Migration):

    dependencies = [
        ('generic', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assignedkeyword',
            name='_order',
            field=shuyucms.core.fields.OrderField(null=True, verbose_name='Order'),
            preserve_default=True,
        ),
    ]
