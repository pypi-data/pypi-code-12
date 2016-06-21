# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('configuracao', '0004_auto_20160509_1744'),
        ('pedido', '0002_auto_20160426_2259'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pedidovendaformapagamento',
            name='banco_id',
        ),
        migrations.RemoveField(
            model_name='pedidovendaformapagamento',
            name='pagamento_banco_id',
        ),
        migrations.AddField(
            model_name='pedidovendaformapagamento',
            name='banco',
            field=models.ForeignKey(related_name='pedidos_banco', db_column=b'pagamento_banco_id', default=None, to='configuracao.PagamentoBanco', null=True),
        ),
    ]
