# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pedido', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pedidovendasituacao',
            name='data_modificacao',
            field=models.DateTimeField(auto_now=True, null=True, db_column=b'pedido_venda_situacao_data_modificacao'),
        ),
    ]
