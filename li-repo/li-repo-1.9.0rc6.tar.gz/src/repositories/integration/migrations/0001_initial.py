# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import repositories.custom_models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AccountIntegration',
            fields=[
                ('id', repositories.custom_models.BigAutoField(serialize=False, primary_key=True, db_column=b'account_integration_id')),
                ('account_id', models.BigIntegerField(db_column=b'account_integration_account_id')),
                ('contract_id', models.BigIntegerField(db_column=b'account_integration_contract_id')),
                ('active', models.BooleanField(default=False, db_column=b'account_integration_active')),
                ('client_id', models.CharField(max_length=255, null=True, db_column=b'account_integration_client_id', blank=True)),
                ('secret_id', models.CharField(max_length=255, null=True, db_column=b'account_integration_secret_id', blank=True)),
                ('token', models.CharField(max_length=255, null=True, db_column=b'account_integration_token', blank=True)),
                ('url', models.URLField(null=True, verbose_name=b'URL de acesso', db_column=b'account_integration_url', blank=True)),
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
                ('sandbox_token', models.CharField(max_length=255, null=True, verbose_name=b'token teste', db_column=b'integration_sandbox_token', blank=True)),
                ('sandbox_url', models.URLField(null=True, verbose_name=b'URL do sandbox', db_column=b'integration_sandbox_url', blank=True)),
                ('production_token', models.CharField(max_length=255, null=True, verbose_name=b'token teste', db_column=b'integration_production_token', blank=True)),
                ('production_url', models.URLField(null=True, verbose_name=b'URL do sandbox', db_column=b'integration_production_url', blank=True)),
                ('active', models.BooleanField(default=False, db_column=b'integration_active')),
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
                ('id', repositories.custom_models.BigAutoField(serialize=False, primary_key=True, db_column=b'integration_history_id')),
                ('account_id', models.BigIntegerField(db_column=b'integration_history_account_id')),
                ('model_selected', models.CharField(max_length=50, db_column=b'integration_history_model_selected')),
                ('model_selected_id', models.BigIntegerField(db_column=b'integration_history_model_selected_id')),
                ('start_date', models.DateTimeField(auto_now_add=True, db_column=b'integration_history_start_date')),
                ('end_date', models.DateTimeField(null=True, db_column=b'integration_history_end_date', blank=True)),
                ('status', models.CharField(default=b'WAIT', max_length=35, db_column=b'integration_history_status', choices=[('WAIT', 'Aguardando envio para {}'), ('QUEUE', 'Em fila para {}'), ('RETRY', 'Nova tentativa para {}'), ('SUCCESS', 'Integrado com sucesso para {}'), ('FAIL', '{} n\xe3o aceitou os dados'), ('ERROR', 'Ocorreu um erro no envio')])),
                ('message_body', models.TextField(null=True, db_column=b'integration_history_message_body', blank=True)),
                ('duration', models.DurationField(null=True, db_column=b'integration_history_duration', blank=True)),
                ('contract_id', models.BigIntegerField(null=True, db_column=b'integration_history_contract_id', blank=True)),
                ('response', models.TextField(null=True, db_column=b'integration_history_web_response', blank=True)),
                ('integration', models.ForeignKey(related_name='integration_integration_history', db_column=b'integration_id', to='integration.Integration')),
            ],
            options={
                'db_table': 'integration"."tb_integration_history',
                'verbose_name': 'Integration History',
                'verbose_name_plural': 'Integrations History',
            },
        ),
        migrations.CreateModel(
            name='ModelIntegration',
            fields=[
                ('id', repositories.custom_models.BigAutoField(serialize=False, primary_key=True, db_column=b'model_integration_id')),
                ('account_id', models.BigIntegerField(db_column=b'model_integration_account_id')),
                ('model_selected', models.CharField(max_length=50, db_column=b'model_integration_model_selected')),
                ('model_selected_id', models.BigIntegerField(db_column=b'model_integration_model_selected_id')),
                ('start_date', models.DateTimeField(auto_now_add=True, null=True, db_column=b'model_integration_start_date')),
                ('end_date', models.DateTimeField(null=True, db_column=b'model_integration_end_date', blank=True)),
                ('block_integration', models.BooleanField(default=False, db_column=b'model_integration_block_integration')),
                ('removed', models.BooleanField(default=False, db_column=b'model_integration_removed')),
                ('external_id', models.BigIntegerField(null=True, db_column=b'model_integration_external_id', blank=True)),
                ('external_sku_id', models.BigIntegerField(null=True, db_column=b'model_integration_external_sku_id', blank=True)),
                ('integration', models.ForeignKey(related_name='integration_model_integration', db_column=b'integration_id', to='integration.Integration')),
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
            field=models.ForeignKey(related_name='integration_account_integration', db_column=b'integration_id', to='integration.Integration'),
        ),
        migrations.AlterUniqueTogether(
            name='modelintegration',
            unique_together=set([('model_selected', 'model_selected_id', 'integration', 'account_id')]),
        ),
        migrations.AlterUniqueTogether(
            name='accountintegration',
            unique_together=set([('account_id', 'integration')]),
        ),
    ]
