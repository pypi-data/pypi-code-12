# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('integration', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='integration',
            name='active',
            field=models.BooleanField(
                default=False,
                db_column=b'integration_active'),
        ),
        migrations.AddField(
            model_name='integrationhistory',
            name='contract_id',
            field=models.BigIntegerField(
                default=1,
                db_column=b'integration_history_contract_id'),
            preserve_default=False,
        ),
    ]
