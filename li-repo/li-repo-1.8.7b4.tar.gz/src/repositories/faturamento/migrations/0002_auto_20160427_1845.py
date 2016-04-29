# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('plataforma', '0001_initial'),
        ('faturamento', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='planoassinatura',
            name='conta',
            field=models.ForeignKey(to='plataforma.Conta', db_column=b'conta_id'),
        ),
        migrations.AddField(
            model_name='planoassinatura',
            name='fatura',
            field=models.ForeignKey(to='faturamento.Fatura', db_column=b'fatura_id'),
        ),
        migrations.AddField(
            model_name='planoassinatura',
            name='plano',
            field=models.ForeignKey(to='faturamento.Plano', db_column=b'plano_id'),
        ),
        migrations.AddField(
            model_name='plano',
            name='colecao',
            field=models.ForeignKey(to='faturamento.Colecao', db_column=b'colecao_id'),
        ),
        migrations.AddField(
            model_name='faturaitem',
            name='conta',
            field=models.ForeignKey(to='plataforma.Conta', db_column=b'conta_id'),
        ),
        migrations.AddField(
            model_name='faturaitem',
            name='fatura',
            field=models.ForeignKey(related_name='itens', db_column=b'fatura_id', to='faturamento.Fatura'),
        ),
        migrations.AddField(
            model_name='fatura',
            name='conta',
            field=models.ForeignKey(to='plataforma.Conta', db_column=b'conta_id'),
        ),
        migrations.AddField(
            model_name='fatura',
            name='contrato',
            field=models.ForeignKey(to='plataforma.Contrato', db_column=b'contrato_id'),
        ),
        migrations.AddField(
            model_name='dadoscobrancacartao',
            name='conta',
            field=models.OneToOneField(db_column=b'conta_id', to='plataforma.Conta'),
        ),
        migrations.AddField(
            model_name='dadoscobrancacartao',
            name='dados_cobranca',
            field=models.ForeignKey(to='faturamento.DadosCobranca', db_column=b'dados_cobranca_id'),
        ),
        migrations.AddField(
            model_name='dadoscobranca',
            name='conta',
            field=models.OneToOneField(db_column=b'conta_id', to='plataforma.Conta'),
        ),
        migrations.AddField(
            model_name='consumo',
            name='conta',
            field=models.ForeignKey(to='plataforma.Conta', db_column=b'conta_id'),
        ),
        migrations.AddField(
            model_name='banner',
            name='colecao',
            field=models.ForeignKey(to='faturamento.Colecao', db_column=b'colecao_id'),
        ),
        migrations.AlterIndexTogether(
            name='planoassinatura',
            index_together=set([('ciclo_inicio', 'ciclo_fim')]),
        ),
    ]
