# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import repositories.custom_models
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('plataforma', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL("CREATE SCHEMA IF NOT EXISTS marketplace;"),
        migrations.CreateModel(
            name='MercadolivreAnuncio',
            fields=[
                ('id', repositories.custom_models.BigAutoField(serialize=False, primary_key=True, db_column=b'mercadolivre_anuncio_id')),
                ('item_id', models.TextField(db_column=b'mercadolivre_anuncio_item_id')),
                ('produto_id', models.BigIntegerField(db_column=b'produto_id')),
                ('produto_id_pai', models.BigIntegerField(db_column=b'produto_id_pai')),
                ('categoria_id', models.TextField(db_column=b'mercadolivre_anuncio_categoria_id')),
                ('tipo', models.CharField(max_length=64, db_column=b'mercadolivre_anuncio_tipo')),
                ('status', models.CharField(max_length=32, db_column=b'mercadolivre_anuncio_status')),
                ('prazo_alteracao', models.DateTimeField(auto_now_add=True, null=True, db_column=b'mercadolivre_anuncio_prazo_alteracao')),
                ('data_vencimento', models.DateTimeField(null=True, db_column=b'mercadolivre_anuncio_data_vencimento')),
                ('data_criacao', models.DateTimeField(auto_now_add=True, db_column=b'mercadolivre_anuncio_data_criacao')),
                ('data_modificacao', models.DateTimeField(auto_now=True, db_column=b'mercadolivre_anuncio_data_modificacao')),
                ('title', models.TextField(db_column=b'mercadolivre_anuncio_title')),
                ('price', models.DecimalField(decimal_places=3, max_digits=16, db_column=b'mercadolivre_anuncio_price')),
                ('quantity', models.IntegerField(db_column=b'mercadolivre_anuncio_quantity')),
                ('variations', jsonfield.fields.JSONField(default=None, null=True, db_column=b'mercadolivre_anuncio_variations')),
                ('conta', models.ForeignKey(to='plataforma.Conta', db_column=b'conta_id')),
                ('contrato', models.ForeignKey(to='plataforma.Contrato', db_column=b'contrato_id')),
            ],
            options={
                'db_table': 'marketplace"."tb_mercadolivre_anuncio',
            },
        ),
        migrations.CreateModel(
            name='MercadolivreConfiguracao',
            fields=[
                ('id', repositories.custom_models.BigAutoField(serialize=False, primary_key=True, db_column=b'mercadolivre_configuracao_id')),
                ('access_token', models.TextField(db_column=b'mercadolivre_configuracao_access_token')),
                ('apelido', models.TextField(null=True, db_column=b'mercadolivre_configuracao_apelido')),
                ('refresh_token', models.TextField(db_column=b'mercadolivre_configuracao_refresh_token')),
                ('access_token_invalido', models.BooleanField(default=False, db_column=b'mercadolivre_configuracao_access_token_invalido')),
                ('user_id', models.BigIntegerField(db_column=b'mercadolivre_configuracao_user_id')),
                ('token_expires', models.DateTimeField(db_column=b'mercadolivre_configuracao_token_expires')),
                ('prazo_remocao', models.DateTimeField(null=True, db_column=b'mercadolivre_configuracao_prazo_remocao')),
                ('prazo_cadastro', models.DateTimeField(db_column=b'mercadolivre_configuracao_prazo_cadastro')),
                ('relistar_automaticamente', models.BooleanField(default=False, db_column=b'mercadolivre_configuracao_relistar_automaticamente')),
                ('data_criacao', models.DateTimeField(auto_now_add=True, db_column=b'mercadolivre_configuracao_data_criacao')),
                ('data_modificacao', models.DateTimeField(auto_now=True, db_column=b'mercadolivre_configuracao_data_modificacao')),
                ('conta', models.ForeignKey(to='plataforma.Conta', db_column=b'conta_id')),
                ('contrato', models.ForeignKey(to='plataforma.Contrato', db_column=b'contrato_id')),
            ],
            options={
                'db_table': 'marketplace"."tb_mercadolivre_configuracao',
            },
        ),
    ]
