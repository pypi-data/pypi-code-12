# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import repositories.custom_models


class Migration(migrations.Migration):

    dependencies = [
        ('plataforma', '0001_initial'),
        ('catalogo', '0002_auto_20160602_2200'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContaIntegracao',
            fields=[
                ('id', repositories.custom_models.BigAutoField(serialize=False, primary_key=True, db_column=b'conta_integracao_id')),
                ('ativo', models.BooleanField(default=False, db_column=b'conta_integracao_ativo')),
                ('nome_usuario', models.CharField(max_length=255, null=True, verbose_name=b'nome usuario', db_column=b'conta_integracao_sandbox_nome', blank=True)),
                ('senha_usuario', models.CharField(max_length=255, null=True, verbose_name=b'conta_integracao_senha usuario', db_column=b'conta_integracao_sandbox_secret', blank=True)),
                ('token', models.CharField(max_length=255, null=True, verbose_name=b'token', db_column=b'conta_integracao_sandbox_token', blank=True)),
                ('url', models.URLField(null=True, verbose_name=b'URL de acesso', db_column=b'conta_integracao_url', blank=True)),
                ('conta', models.ForeignKey(related_name='conta_conta_integracao', to='plataforma.Conta')),
                ('contrato', models.ForeignKey(related_name='contrato_conta_integracao', to='plataforma.Contrato')),
            ],
            options={
                'db_table': 'integration"."tb_conta_integracao',
                'verbose_name': 'Conta Integracao',
                'verbose_name_plural': 'Conta Integracoes',
            },
        ),
        migrations.CreateModel(
            name='Integracao',
            fields=[
                ('id', repositories.custom_models.BigAutoField(serialize=False, primary_key=True, db_column=b'integracao_id')),
                ('nome', models.CharField(max_length=255, verbose_name=b'nome', db_column=b'integracao_nome')),
                ('slug', models.SlugField(null=True, db_column=b'integracao_slug', editable=False, blank=True, unique=True)),
                ('sandbox_nome', models.CharField(max_length=255, null=True, verbose_name=b'nome usuario teste', db_column=b'integracao_integracao_sandbox_nome', blank=True)),
                ('sandbox_secret', models.CharField(max_length=255, null=True, verbose_name=b'senha usuario teste', db_column=b'integracao_sandbox_secret', blank=True)),
                ('sandbox_token', models.CharField(max_length=255, null=True, verbose_name=b'token teste', db_column=b'integracao_sandbox_token', blank=True)),
                ('sandbox_url', models.URLField(null=True, verbose_name=b'URL do sandbox', db_column=b'integracao_sandbox_url', blank=True)),
            ],
            options={
                'db_table': 'integration"."tb_integracao',
                'verbose_name': 'Integracao',
                'verbose_name_plural': 'Integracoes',
            },
        ),
        migrations.CreateModel(
            name='ProdutoIntegracao',
            fields=[
                ('id', repositories.custom_models.BigAutoField(serialize=False, primary_key=True, db_column=b'produto_integracao_id')),
                ('data_inicio', models.DateTimeField(null=True, db_column=b'produto_integracao_data_inicio', blank=True)),
                ('data_fim', models.DateTimeField(null=True, db_column=b'produto_integracao_data_fim', blank=True)),
                ('bloquear', models.BooleanField(default=False, db_column=b'produto_integracao_bloquear')),
                ('removido', models.BooleanField(default=False, db_column=b'produto_integracao_removido')),
                ('conta', models.ForeignKey(related_name='conta_produto_integracao', to='plataforma.Conta')),
                ('integracao', models.ForeignKey(related_name='integracao_produto_integracao', to='integration.Integracao')),
                ('produto', models.ForeignKey(related_name='produto_produto_integracao', to='catalogo.Produto')),
            ],
            options={
                'db_table': 'integration"."tb_produto_integracao',
                'verbose_name': 'Produto Integracao',
                'verbose_name_plural': 'Produto Integracoes',
            },
        ),
        migrations.AddField(
            model_name='containtegracao',
            name='integracao',
            field=models.ForeignKey(related_name='integracao_conta_integracao', to='integration.Integracao'),
        ),
        migrations.AlterUniqueTogether(
            name='produtointegracao',
            unique_together=set([('conta', 'integracao', 'produto')]),
        ),
        migrations.AlterUniqueTogether(
            name='containtegracao',
            unique_together=set([('conta', 'integracao')]),
        ),
    ]
