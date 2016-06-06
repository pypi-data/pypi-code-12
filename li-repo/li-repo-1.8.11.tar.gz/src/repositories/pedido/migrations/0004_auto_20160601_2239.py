# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('configuracao', '0004_auto_20160509_1744'),
        ('pedido', '0003_auto_20160509_1744'),
    ]

    operations = [
        migrations.AddField(
            model_name='pedidovendaformapagamento',
            name='pagamento_banco',
            field=models.ForeignKey(related_name='pedidos_banco', db_column=b'pagamento_banco_id', default=None, to='configuracao.PagamentoBanco', null=True),
        ),
        migrations.AlterField(
            model_name='pedidovendaformapagamento',
            name='banco',
            field=models.ForeignKey(related_name='banco', db_column=b'banco_id', default=None, to='configuracao.Banco', null=True),
        ),
    ]
