# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('configuracao', '0001_initial'),
        ('plataforma', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='token',
            name='conta',
            field=models.ForeignKey(related_name='tokens', to='plataforma.Conta'),
        ),
        migrations.AddField(
            model_name='token',
            name='contrato',
            field=models.ForeignKey(related_name='tokens', to='plataforma.Contrato'),
        ),
        migrations.AddField(
            model_name='parcela',
            name='forma_pagamento',
            field=models.ForeignKey(related_name='parcelas', db_column=b'pagamento_id', to='configuracao.FormaPagamento'),
        ),
        migrations.AddField(
            model_name='pagamentobanco',
            name='banco',
            field=models.ForeignKey(related_name='bancos_pagamentos', db_column=b'banco_id', to='configuracao.Banco'),
        ),
        migrations.AddField(
            model_name='pagamentobanco',
            name='conta',
            field=models.ForeignKey(related_name='pagamento_bancos', to='plataforma.Conta'),
        ),
        migrations.AddField(
            model_name='pagamentobanco',
            name='contrato',
            field=models.ForeignKey(related_name='pagamento_bancos', to='plataforma.Contrato'),
        ),
        migrations.AddField(
            model_name='pagamentobanco',
            name='pagamento',
            field=models.ForeignKey(related_name='bancos', db_column=b'pagamento_id', to='configuracao.FormaPagamento'),
        ),
        migrations.AddField(
            model_name='formapagamentoconfiguracao',
            name='conta',
            field=models.ForeignKey(related_name='formas_pagamentos_configuracoes', to='plataforma.Conta'),
        ),
        migrations.AddField(
            model_name='formapagamentoconfiguracao',
            name='contrato',
            field=models.ForeignKey(related_name='formas_pagamentos_configuracoes', to='plataforma.Contrato'),
        ),
        migrations.AddField(
            model_name='formapagamentoconfiguracao',
            name='forma_pagamento',
            field=models.ForeignKey(related_name='configuracoes', db_column=b'pagamento_id', to='configuracao.FormaPagamento'),
        ),
        migrations.AddField(
            model_name='formapagamento',
            name='conta',
            field=models.ForeignKey(related_name='formas_pagamentos', default=None, to='plataforma.Conta', null=True),
        ),
        migrations.AddField(
            model_name='formapagamento',
            name='contrato',
            field=models.ForeignKey(related_name='formas_pagamentos', default=None, to='plataforma.Contrato', null=True),
        ),
        migrations.AddField(
            model_name='facebook',
            name='conta',
            field=models.ForeignKey(related_name='contas_facebook', db_column=b'conta_id', to='plataforma.Conta'),
        ),
        migrations.AddField(
            model_name='facebook',
            name='contrato',
            field=models.ForeignKey(related_name='contas_facebook', to='plataforma.Contrato'),
        ),
        migrations.AddField(
            model_name='envioregiao',
            name='conta',
            field=models.ForeignKey(related_name='formas_envios_regioes', to='plataforma.Conta'),
        ),
        migrations.AddField(
            model_name='envioregiao',
            name='contrato',
            field=models.ForeignKey(related_name='formas_envios_regioes', to='plataforma.Contrato'),
        ),
        migrations.AddField(
            model_name='envioregiao',
            name='forma_envio',
            field=models.ForeignKey(related_name='regioes', db_column=b'envio_id', to='configuracao.Envio'),
        ),
        migrations.AddField(
            model_name='envioregiao',
            name='forma_envio_configuracao',
            field=models.ForeignKey(related_name='regioes', db_column=b'envio_configuracao_id', to='configuracao.EnvioConfiguracao'),
        ),
        migrations.AddField(
            model_name='enviofaixapeso',
            name='conta',
            field=models.ForeignKey(related_name='formas_envios_faixas_peso', to='plataforma.Conta'),
        ),
        migrations.AddField(
            model_name='enviofaixapeso',
            name='contrato',
            field=models.ForeignKey(related_name='formas_envios_faixas_peso', to='plataforma.Contrato'),
        ),
        migrations.AddField(
            model_name='enviofaixapeso',
            name='forma_envio',
            field=models.ForeignKey(related_name='faixas_peso', db_column=b'envio_id', to='configuracao.Envio'),
        ),
        migrations.AddField(
            model_name='enviofaixapeso',
            name='forma_envio_configuracao',
            field=models.ForeignKey(related_name='faixas_peso', db_column=b'envio_configuracao_id', to='configuracao.EnvioConfiguracao'),
        ),
        migrations.AddField(
            model_name='enviofaixapeso',
            name='regiao',
            field=models.ForeignKey(related_name='faixas_peso', db_column=b'envio_regiao_id', to='configuracao.EnvioRegiao'),
        ),
        migrations.AddField(
            model_name='enviofaixacep',
            name='conta',
            field=models.ForeignKey(related_name='formas_envios_faixas_cep', to='plataforma.Conta'),
        ),
        migrations.AddField(
            model_name='enviofaixacep',
            name='contrato',
            field=models.ForeignKey(related_name='formas_envios_faixas_cep', to='plataforma.Contrato'),
        ),
        migrations.AddField(
            model_name='enviofaixacep',
            name='forma_envio',
            field=models.ForeignKey(related_name='faixas_cep', db_column=b'envio_id', to='configuracao.Envio'),
        ),
        migrations.AddField(
            model_name='enviofaixacep',
            name='forma_envio_configuracao',
            field=models.ForeignKey(related_name='faixas_cep', db_column=b'envio_configuracao_id', to='configuracao.EnvioConfiguracao'),
        ),
        migrations.AddField(
            model_name='enviofaixacep',
            name='regiao',
            field=models.ForeignKey(related_name='faixas_cep', db_column=b'envio_regiao_id', to='configuracao.EnvioRegiao'),
        ),
        migrations.AddField(
            model_name='enviocontrato',
            name='forma_envio',
            field=models.ForeignKey(related_name='contratos', db_column=b'envio_id', to='configuracao.Envio'),
        ),
        migrations.AddField(
            model_name='envioconfiguracao',
            name='conta',
            field=models.ForeignKey(related_name='formas_envios_configuracoes', to='plataforma.Conta'),
        ),
        migrations.AddField(
            model_name='envioconfiguracao',
            name='contrato',
            field=models.ForeignKey(related_name='formas_envios_configuracoes', to='plataforma.Contrato'),
        ),
        migrations.AddField(
            model_name='envioconfiguracao',
            name='forma_envio',
            field=models.ForeignKey(related_name='configuracoes', db_column=b'envio_id', to='configuracao.Envio'),
        ),
        migrations.AddField(
            model_name='envio',
            name='conta',
            field=models.ForeignKey(related_name='formas_envios', default=None, to='plataforma.Conta', null=True),
        ),
        migrations.AddField(
            model_name='envio',
            name='contrato',
            field=models.ForeignKey(related_name='formas_envios', to='plataforma.Contrato', null=True),
        ),
        migrations.AddField(
            model_name='edicaotema',
            name='conta',
            field=models.OneToOneField(db_column=b'conta_id', to='plataforma.Conta'),
        ),
        migrations.AddField(
            model_name='edicaotema',
            name='contrato',
            field=models.ForeignKey(related_name='edicoes_temas', to='plataforma.Contrato'),
        ),
        migrations.AddField(
            model_name='dominio',
            name='conta',
            field=models.ForeignKey(related_name='dominios', db_column=b'conta_id', to='plataforma.Conta'),
        ),
        migrations.AddField(
            model_name='dominio',
            name='contrato',
            field=models.ForeignKey(related_name='dominios', to='plataforma.Contrato'),
        ),
        migrations.AddField(
            model_name='configuracaofacebook',
            name='conta',
            field=models.ForeignKey(related_name='configuracoes_facebook', db_column=b'conta_id', to='plataforma.Conta'),
        ),
        migrations.AddField(
            model_name='configuracaofacebook',
            name='contrato',
            field=models.ForeignKey(related_name='configuracoes_facebook', to='plataforma.Contrato'),
        ),
        migrations.AddField(
            model_name='codigohtml',
            name='conta',
            field=models.ForeignKey(related_name='codigos_html', to='plataforma.Conta'),
        ),
        migrations.AddField(
            model_name='codigohtml',
            name='contrato',
            field=models.ForeignKey(related_name='codigos_html', to='plataforma.Contrato'),
        ),
        migrations.AddField(
            model_name='boletocarteira',
            name='banco',
            field=models.ForeignKey(related_name='carteiras', db_column=b'banco_id', to='configuracao.Banco'),
        ),
        migrations.AlterUniqueTogether(
            name='pagamentobanco',
            unique_together=set([('banco', 'conta')]),
        ),
        migrations.AlterUniqueTogether(
            name='formapagamentoconfiguracao',
            unique_together=set([('conta', 'forma_pagamento')]),
        ),
        migrations.AlterUniqueTogether(
            name='envioregiao',
            unique_together=set([('pais', 'nome', 'forma_envio')]),
        ),
        migrations.AlterUniqueTogether(
            name='enviofaixapeso',
            unique_together=set([('peso_inicio', 'peso_fim', 'regiao')]),
        ),
        migrations.AlterUniqueTogether(
            name='enviofaixacep',
            unique_together=set([('cep_inicio', 'cep_fim', 'regiao')]),
        ),
        migrations.AlterUniqueTogether(
            name='envioconfiguracao',
            unique_together=set([('conta', 'forma_envio')]),
        ),
        migrations.AlterUniqueTogether(
            name='envio',
            unique_together=set([('nome', 'codigo', 'conta')]),
        ),
        migrations.AlterUniqueTogether(
            name='codigohtml',
            unique_together=set([('conta', 'descricao')]),
        ),
        migrations.AlterUniqueTogether(
            name='boletocarteira',
            unique_together=set([('banco', 'numero', 'convenio')]),
        ),
    ]
