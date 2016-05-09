# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import repositories.custom_models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.RunSQL("CREATE SCHEMA IF NOT EXISTS cliente;"),
        migrations.CreateModel(
            name='Cliente',
            fields=[
                ('id', repositories.custom_models.BigAutoField(serialize=False, primary_key=True, db_column=b'cliente_id')),
                ('email', models.EmailField(max_length=255, db_column=b'cliente_email')),
                ('senha', models.CharField(max_length=64, db_column=b'cliente_senha')),
                ('nome', models.CharField(max_length=255, null=True, db_column=b'cliente_nome')),
                ('sexo', models.CharField(max_length=1, null=True, db_column=b'cliente_sexo')),
                ('telefone_principal', models.CharField(max_length=11, null=True, db_column=b'cliente_telefone_principal')),
                ('telefone_comercial', models.CharField(max_length=11, null=True, db_column=b'cliente_telefone_comercial')),
                ('telefone_celular', models.CharField(max_length=11, null=True, db_column=b'cliente_telefone_celular')),
                ('newsletter', models.BooleanField(default=True, db_column=b'cliente_newsletter')),
                ('data_nascimento', models.DateField(null=True, db_column=b'cliente_data_nascimento')),
                ('data_criacao', models.DateTimeField(auto_now_add=True, db_column=b'cliente_data_criacao')),
                ('data_modificacao', models.DateTimeField(auto_now=True, db_column=b'cliente_data_modificacao')),
                ('facebook_id', models.CharField(default=None, max_length=64, null=True, db_column=b'cliente_facebook_usuario_id')),
                ('teste', models.BooleanField(default=False, db_column=b'cliente_teste')),
                ('situacao', models.CharField(default=b'pendente', max_length=32, db_column=b'cliente_situacao')),
                ('desativado', models.BooleanField(default=False, db_column=b'cliente_desativado')),
            ],
            options={
                'get_latest_by': 'id',
                'ordering': ['email'],
                'verbose_name_plural': 'Clientes',
                'db_table': 'cliente"."tb_cliente',
                'verbose_name': 'Cliente',
            },
        ),
        migrations.CreateModel(
            name='ClienteEndereco',
            fields=[
                ('id', repositories.custom_models.BigAutoField(serialize=False, primary_key=True, db_column=b'cliente_endereco_id')),
                ('tipo', models.CharField(default=None, max_length=64, null=True, db_column=b'cliente_endereco_tipo', choices=[(b'PF', 'Pessoa F\xedsica'), (b'PJ', 'Pessoa Jur\xeddica'), (b'IN', 'Internacional')])),
                ('cpf', models.CharField(default=None, max_length=11, null=True, db_column=b'cliente_endereco_cpf')),
                ('rg', models.CharField(default=None, max_length=20, null=True, db_column=b'cliente_endereco_rg')),
                ('cnpj', models.CharField(default=None, max_length=14, null=True, db_column=b'cliente_endereco_cnpj')),
                ('razao_social', models.CharField(default=None, max_length=255, null=True, db_column=b'cliente_endereco_razao_social')),
                ('ie', models.CharField(default=None, max_length=20, null=True, db_column=b'cliente_endereco_ie')),
                ('nome', models.CharField(max_length=255, db_column=b'cliente_endereco_nome')),
                ('endereco', models.CharField(max_length=255, db_column=b'cliente_endereco_endereco')),
                ('numero', models.CharField(max_length=10, db_column=b'cliente_endereco_numero')),
                ('complemento', models.CharField(max_length=255, null=True, db_column=b'cliente_endereco_complemento')),
                ('referencia', models.CharField(max_length=255, null=True, db_column=b'cliente_endereco_referencia')),
                ('bairro', models.CharField(max_length=128, db_column=b'cliente_endereco_bairro')),
                ('cidade', models.CharField(max_length=128, db_column=b'cliente_endereco_cidade')),
                ('estado', models.CharField(max_length=2, db_column=b'cliente_endereco_estado')),
                ('cep', models.CharField(max_length=8, db_column=b'cliente_endereco_cep')),
                ('pais_extenso', models.CharField(max_length=128, null=True, db_column=b'cliente_endereco_pais')),
                ('principal', models.BooleanField(default=False, db_column=b'cliente_endereco_principal')),
            ],
            options={
                'get_latest_by': 'id',
                'ordering': ['nome'],
                'verbose_name_plural': 'Endere\xe7os do cliente',
                'db_table': 'cliente"."tb_cliente_endereco',
                'verbose_name': 'Endere\xe7o do cliente',
            },
        ),
        migrations.CreateModel(
            name='ClienteFavorito',
            fields=[
                ('id', repositories.custom_models.BigAutoField(serialize=False, primary_key=True, db_column=b'cliente_favorito_id')),
                ('codigo', models.CharField(max_length=32, null=True, db_column=b'cliente_favorito_codigo', blank=True)),
                ('data_criacao', models.DateTimeField(auto_now_add=True, db_column=b'cliente_favorito_data_criacao')),
                ('data_modificacao', models.DateTimeField(auto_now=True, db_column=b'cliente_favorito_data_modificacao')),
            ],
            options={
                'ordering': ['data_criacao'],
                'db_table': 'cliente"."tb_cliente_favorito',
                'verbose_name': 'Favorito do cliente',
                'verbose_name_plural': 'Favoritos dos clientes',
            },
        ),
        migrations.CreateModel(
            name='ClienteFavoritoProduto',
            fields=[
                ('id', repositories.custom_models.BigAutoField(serialize=False, primary_key=True, db_column=b'cliente_favorito_produto_id')),
            ],
            options={
                'db_table': 'cliente"."tb_cliente_favorito_produto',
                'verbose_name': 'Produto favorito',
                'verbose_name_plural': 'Produtos favoritos',
            },
        ),
        migrations.CreateModel(
            name='ClienteGrupo',
            fields=[
                ('id', repositories.custom_models.BigAutoField(serialize=False, primary_key=True, db_column=b'cliente_grupo_id')),
                ('nome', models.CharField(max_length=128, db_column=b'cliente_grupo_nome')),
                ('padrao', models.BooleanField(default=False, db_column=b'cliente_grupo_padrao')),
            ],
            options={
                'ordering': ['conta', 'nome'],
                'db_table': 'cliente"."tb_cliente_grupo',
                'verbose_name': 'Grupo de cliente',
                'verbose_name_plural': 'Grupo de clientes',
            },
        ),
    ]
