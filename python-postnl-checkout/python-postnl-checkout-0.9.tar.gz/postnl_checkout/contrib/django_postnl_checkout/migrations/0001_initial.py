# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('order_token', models.CharField(max_length=255, serialize=False, primary_key=True)),
                ('order_ext_ref', models.CharField(max_length=255, db_index=True)),
                ('order_date', models.DateField(db_index=True)),
                ('customer_ext_ref', models.CharField(max_length=255, db_index=True)),
                ('prepare_order_request', jsonfield.fields.JSONField(default=dict)),
                ('prepare_order_response', jsonfield.fields.JSONField(default=dict)),
                ('read_order_response', jsonfield.fields.JSONField(default=dict)),
                ('update_order_request', jsonfield.fields.JSONField(default=dict)),
            ],
        ),
    ]
