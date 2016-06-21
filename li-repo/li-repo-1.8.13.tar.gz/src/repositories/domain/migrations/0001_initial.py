# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import repositories.custom_models
import repositories.domain.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ApiAplicacao',
            fields=[
                ('id', repositories.custom_models.BigAutoField(serialize=False, primary_key=True, db_column=b'api_aplicacao_id')),
                ('chave', repositories.custom_models.UUIDField(unique=True, max_length=64, db_column=b'api_aplicacao_chave', blank=True)),
                ('nome', models.CharField(max_length=255, db_column=b'api_aplicacao_nome')),
                ('data_criacao', models.DateTimeField(auto_now_add=True, db_column=b'api_aplicacao_data_criacao')),
                ('data_modificacao', models.DateTimeField(auto_now=True, null=True, db_column=b'api_aplicacao_data_modificacao')),
            ],
            options={
                'ordering': ['nome'],
                'db_table': 'plataforma"."tb_api_aplicacao',
                'verbose_name': 'Aplica\xe7\xe3o da API',
                'verbose_name_plural': 'Aplica\xe7\xf5es da API',
            },
        ),
        migrations.CreateModel(
            name='Cidade',
            fields=[
                ('id', repositories.custom_models.BigAutoField(serialize=False, primary_key=True, db_column=b'cidade_id')),
                ('nome', models.CharField(max_length=100, db_column=b'cidade')),
                ('nome_alt', models.CharField(max_length=100, db_column=b'cidade_alt')),
                ('uf', models.CharField(max_length=2, db_column=b'uf')),
                ('uf_munic', models.IntegerField(db_column=b'uf_munic')),
                ('munic', models.IntegerField(db_column=b'munic')),
            ],
            options={
                'ordering': ['nome'],
                'db_table': 'tb_cidade',
                'verbose_name': 'Cidade',
                'verbose_name_plural': 'Cidades',
            },
        ),
        migrations.CreateModel(
            name='Estado',
            fields=[
                ('id', repositories.custom_models.BigAutoField(serialize=False, primary_key=True, db_column=b'estado_id')),
                ('uf_id', models.IntegerField(unique=True, db_column=b'uf_id')),
                ('nome', models.CharField(max_length=100, db_column=b'estado_nome')),
                ('uf', models.CharField(max_length=2, db_column=b'estado_uf')),
            ],
            options={
                'ordering': ['nome'],
                'db_table': 'tb_estado',
                'verbose_name': 'Estado',
                'verbose_name_plural': 'Estados',
            },
        ),
        migrations.CreateModel(
            name='Idioma',
            fields=[
                ('id', models.CharField(max_length=5, serialize=False, primary_key=True, db_column=b'idioma_id')),
                ('nome', models.CharField(max_length=64, db_column=b'idioma_nome')),
            ],
            options={
                'ordering': ['nome'],
                'db_table': 'tb_idioma',
                'verbose_name': 'Idioma',
                'verbose_name_plural': 'Idiomas',
            },
        ),
        migrations.CreateModel(
            name='Imagem',
            fields=[
                ('id', repositories.custom_models.BigAutoField(serialize=False, primary_key=True, db_column=b'imagem_id')),
                ('tabela', models.CharField(max_length=64, null=True, db_column=b'imagem_tabela')),
                ('campo', models.CharField(max_length=64, null=True, db_column=b'imagem_campo')),
                ('linha_id', models.IntegerField(null=True, db_column=b'imagem_linha_id')),
                ('data_criacao', models.DateTimeField(auto_now_add=True, db_column=b'imagem_data_criacao')),
                ('data_modificacao', models.DateTimeField(auto_now=True, db_column=b'imagem_data_modificacao')),
                ('nome', models.CharField(max_length=255, null=True, db_column=b'imagem_nome')),
                ('alt', models.CharField(max_length=512, null=True, db_column=b'imagem_alt')),
                ('title', models.CharField(max_length=512, null=True, db_column=b'imagem_title')),
                ('mime', models.CharField(max_length=256, null=True, db_column=b'imagem_mime')),
                ('caminho', models.CharField(max_length=255, null=True, db_column=b'imagem_caminho')),
                ('tipo', models.CharField(default='produto', max_length=32, db_column=b'imagem_tipo', choices=[(b'logo', 'Logo'), (b'produto', 'Produto'), (b'banner', 'Banner'), (b'marca', 'Marca'), (b'upload', 'Upload')])),
                ('processada', models.BooleanField(default=False, db_column=b'imagem_processada')),
            ],
            options={
                'ordering': ['data_criacao'],
                'db_table': 'plataforma"."tb_imagem',
                'verbose_name': 'Imagem',
                'verbose_name_plural': 'Imagens',
            },
        ),
        migrations.CreateModel(
            name='Logradouro',
            fields=[
                ('nome_local', models.CharField(max_length=128, serialize=False, primary_key=True, db_column=b'nome_local')),
                ('uf', models.CharField(max_length=2, null=True, db_column=b'uf_log')),
                ('cep_log', models.IntegerField(null=True, db_column=b'cep8_log')),
                ('cep_ini', models.IntegerField(null=True, db_column=b'cep8_ini')),
                ('cep_fim', models.IntegerField(null=True, db_column=b'cep8_fim')),
                ('tipo', models.CharField(max_length=256, null=True, db_column=b'tipo_log')),
                ('logradouro', models.CharField(max_length=256, null=True, db_column=b'logradouro')),
                ('bairro', models.CharField(max_length=256, null=True, db_column=b'bairro')),
                ('complemento', models.CharField(max_length=256, null=True, db_column=b'complemento')),
            ],
            options={
                'db_table': 'tb_logradouro',
            },
        ),
        migrations.CreateModel(
            name='Moeda',
            fields=[
                ('id', models.CharField(max_length=3, serialize=False, primary_key=True, db_column=b'moeda_id')),
                ('nome', models.CharField(max_length=64, db_column=b'moeda_nome')),
            ],
            options={
                'ordering': ['nome'],
                'db_table': 'tb_moeda',
                'verbose_name': 'Moeda',
                'verbose_name_plural': 'Moedas',
            },
        ),
        migrations.CreateModel(
            name='Pais',
            fields=[
                ('id', models.CharField(max_length=3, serialize=False, primary_key=True, db_column=b'pais_id')),
                ('nome', models.CharField(max_length=64, db_column=b'pais_nome')),
                ('numero', models.CharField(max_length=3, db_column=b'pais_numero')),
                ('codigo', models.CharField(unique=True, max_length=2, db_column=b'pais_codigo')),
            ],
            options={
                'ordering': ['nome'],
                'db_table': 'tb_pais',
                'verbose_name': 'Pa\xeds',
                'verbose_name_plural': 'Pa\xedses',
            },
        ),
    ]
