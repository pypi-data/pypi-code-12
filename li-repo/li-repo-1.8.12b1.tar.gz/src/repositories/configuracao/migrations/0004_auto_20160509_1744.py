# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pedido', '0002_auto_20160426_2259'),
        ('plataforma', '0003_auto_20160426_2259'),
        ('configuracao', '0003_auto_20160426_2259'),
    ]

    operations = [
        migrations.AddField(
            model_name='enviocontrato',
            name='contrato',
            field=models.ForeignKey(related_name='envio_contrato_contrato_fk', default=1, to='plataforma.Contrato'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='formapagamento',
            name='_pedidos',
            field=models.ManyToManyField(related_name='_pedidos', through='pedido.PedidoVendaFormaPagamento', to='pedido.PedidoVenda'),
        ),
        migrations.AddField(
            model_name='formapagamentoconfiguracao',
            name='eh_padrao',
            field=models.BooleanField(default=False, db_column=b'pagamento_configuracao_eh_padrao'),
        ),
        migrations.AddField(
            model_name='formapagamentoconfiguracao',
            name='ordem',
            field=models.IntegerField(default=0, db_column=b'pagamento_configuracao_ordem'),
        ),
        migrations.AddField(
            model_name='formapagamentoconfiguracao',
            name='token_expiracao',
            field=models.DateTimeField(null=True, db_column=b'pagamento_configuracao_token_expiracao'),
        ),
        migrations.AddField(
            model_name='formapagamentoconfiguracao',
            name='usar_antifraude',
            field=models.NullBooleanField(default=False, db_column=b'pagamento_configuracao_usar_antifraude'),
        ),
        migrations.AlterField(
            model_name='envio',
            name='tipo',
            field=models.CharField(default=b'faixa_cep', max_length=128, db_column=b'envio_tipo', choices=[(b'correios_api', 'API dos Correios'), (b'faixa_cep', 'Faixa de CEP e peso'), (b'mercadoenvios_api', 'API do Mercado Envios')]),
        ),
    ]
