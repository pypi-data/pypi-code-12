# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import repositories.catalogo.models
import repositories.custom_models


class Migration(migrations.Migration):

    dependencies = [
        ('plataforma', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AccountIntegration',
            fields=[
                ('id', repositories.custom_models.BigAutoField(serialize=False, primary_key=True, db_column=b'account_integration_id')),
                ('active', models.BooleanField(default=False, db_column=b'account_integration_active')),
                ('client_id', models.CharField(max_length=255, null=True, db_column=b'account_integration_client_id', blank=True)),
                ('secret_id', models.CharField(max_length=255, null=True, db_column=b'account_integration_secret_id', blank=True)),
                ('token', models.CharField(max_length=255, null=True, db_column=b'account_integration_token', blank=True)),
                ('url', models.URLField(null=True, verbose_name=b'URL de acesso', db_column=b'account_integration_url', blank=True)),
                ('account', models.ForeignKey(related_name='account_integration', to='plataforma.Conta')),
                ('contract', models.ForeignKey(related_name='contract_account_integration', to='plataforma.Contrato')),
            ],
            options={
                'db_table': 'integration"."tb_account_integration',
                'verbose_name': 'Account Integration',
                'verbose_name_plural': 'Account Integrations',
            },
        ),
        migrations.CreateModel(
            name='Integration',
            fields=[
                ('id', repositories.custom_models.BigAutoField(serialize=False, primary_key=True, db_column=b'integration_id')),
                ('name', models.CharField(max_length=255, verbose_name=b'nome', db_column=b'integration_name')),
                ('slug', models.SlugField(null=True, db_column=b'integration_slug', editable=False, blank=True, unique=True)),
                ('sandbox_name', models.CharField(max_length=255, null=True, verbose_name=b'name usuario teste', db_column=b'integration_sandbox_name', blank=True)),
                ('sandbox_secret', models.CharField(max_length=255, null=True, verbose_name=b'senha usuario teste', db_column=b'integration_sandbox_secret', blank=True)),
                ('sandbox_token', models.CharField(max_length=255, null=True, verbose_name=b'token teste', db_column=b'integration_sandbox_token', blank=True)),
                ('sandbox_url', models.URLField(null=True, verbose_name=b'URL do sandbox', db_column=b'integration_sandbox_url', blank=True)),
            ],
            options={
                'db_table': 'integration"."tb_integration',
                'verbose_name': 'integration',
                'verbose_name_plural': 'Integracoes',
            },
        ),
        migrations.CreateModel(
            name='IntegrationHistory',
            fields=[
                ('id', repositories.custom_models.BigAutoField(serialize=False, primary_key=True, db_column=b'product_integration_history_id')),
                ('model_selected', models.CharField(max_length=50, db_column=b'account_integration_model_selected', choices=[(b'marca', repositories.catalogo.models.Marca), (b'produto', repositories.catalogo.models.Produto), (b'produtocategoria', repositories.catalogo.models.ProdutoCategoria), (b'produtoestoque', repositories.catalogo.models.ProdutoEstoque)])),
                ('model_selected_id', models.IntegerField(db_column=b'account_integration_model_selected_id')),
                ('start_date', models.DateTimeField(auto_now_add=True, db_column=b'product_integration_history_start_date')),
                ('end_date', models.DateTimeField(null=True, db_column=b'product_integration_history_end_date', blank=True)),
                ('status', models.CharField(default=b'WAIT', max_length=35, db_column=b'account_integration_status', choices=[('WAIT', 'aguardando envio para {}'), ('RETRY', 'aguardando envio para {}'), ('SUCCESS', 'integrado com sucesso para {}'), ('FAIL', '{} n\xe3o aceitou os dados'), ('ERROR', 'Ocorreu um erro no envio')])),
                ('message_body', models.TextField(null=True, db_column=b'account_integration_message_body', blank=True)),
                ('duration', models.DurationField(null=True, db_column=b'account_integration_duration', blank=True)),
                ('account', models.ForeignKey(related_name='account_product_integration_history', to='plataforma.Conta')),
                ('integration', models.ForeignKey(related_name='integration_product_integration_history', to='integration.Integration')),
            ],
            options={
                'db_table': 'integration"."tb_product_integration_history',
                'verbose_name': 'Product Integration History',
                'verbose_name_plural': 'Product Integrations History',
            },
        ),
        migrations.CreateModel(
            name='ModelIntegration',
            fields=[
                ('id', repositories.custom_models.BigAutoField(serialize=False, primary_key=True, db_column=b'model_integration_id')),
                ('model_selected', models.CharField(max_length=50, db_column=b'model_integration_model_selected', choices=[(b'marca', repositories.catalogo.models.Marca), (b'produto', repositories.catalogo.models.Produto), (b'produtocategoria', repositories.catalogo.models.ProdutoCategoria), (b'produtoestoque', repositories.catalogo.models.ProdutoEstoque)])),
                ('model_selected_id', models.IntegerField(db_column=b'model_integration_model_selected_id')),
                ('start_date', models.DateTimeField(null=True, db_column=b'model_integration_start_date', blank=True)),
                ('end_date', models.DateTimeField(null=True, db_column=b'model_integration_end_date', blank=True)),
                ('block_integration', models.BooleanField(default=False, db_column=b'model_integration_block_integration')),
                ('removed', models.BooleanField(default=False, db_column=b'model_integration_removed')),
                ('account', models.ForeignKey(related_name='account_model_integration', to='plataforma.Conta')),
                ('integration', models.ForeignKey(related_name='integration_model_integration', to='integration.Integration')),
            ],
            options={
                'db_table': 'integration"."tb_model_integration',
                'verbose_name': 'Model Integration',
                'verbose_name_plural': 'Model Integrations',
            },
        ),
        migrations.AddField(
            model_name='accountintegration',
            name='integration',
            field=models.ForeignKey(related_name='integration_account_integration', to='integration.Integration'),
        ),
        migrations.AlterUniqueTogether(
            name='modelintegration',
            unique_together=set([('model_selected', 'model_selected_id', 'integration')]),
        ),
        migrations.AlterUniqueTogether(
            name='accountintegration',
            unique_together=set([('account', 'integration')]),
        ),
    ]
