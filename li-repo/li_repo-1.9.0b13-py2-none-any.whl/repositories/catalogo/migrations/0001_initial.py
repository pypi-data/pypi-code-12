# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import repositories.custom_models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.RunSQL("CREATE SCHEMA IF NOT EXISTS catalogo;"),
        migrations.CreateModel(
            name='Caracteristica',
            fields=[
                ('id', repositories.custom_models.BigAutoField(serialize=False, primary_key=True, db_column=b'caracteristica_id')),
                ('tipo', models.CharField(max_length=32, db_column=b'caracteristica_tipo')),
                ('posicao', models.IntegerField(default=0, db_column=b'caracteristica_posicao')),
                ('filtrar', models.BooleanField(default=False, db_column=b'caracteristica_pode_filtrar')),
                ('data_criacao', models.DateTimeField(auto_now_add=True, db_column=b'caracteristica_data_criacao')),
                ('data_modificacao', models.DateTimeField(auto_now=True, db_column=b'caracteristica_data_modificacao')),
                ('nome', models.CharField(max_length=128, db_column=b'caracteristica_nome')),
            ],
            options={
                'ordering': ['posicao', 'id'],
                'db_table': 'catalogo"."tb_caracteristica',
                'verbose_name': 'Caracteristica',
                'verbose_name_plural': 'Caracteristicas',
            },
        ),
        migrations.CreateModel(
            name='CaracteristicaValor',
            fields=[
                ('id', repositories.custom_models.BigAutoField(serialize=False, primary_key=True, db_column=b'caracteristica_valor_id')),
                ('valor', models.CharField(max_length=64, db_column=b'caracteristica_valor_valor')),
            ],
            options={
                'ordering': ['valor'],
                'db_table': 'catalogo"."tb_caracteristica_valor',
                'verbose_name': 'Valor da caracteristica',
                'verbose_name_plural': 'Valores das caracteristicas',
            },
        ),
        migrations.CreateModel(
            name='Categoria',
            fields=[
                ('id', repositories.custom_models.BigAutoField(serialize=False, primary_key=True, db_column=b'categoria_id')),
                ('id_externo', models.IntegerField(null=True, db_column=b'categoria_id_externo')),
                ('data_criacao', models.DateTimeField(auto_now_add=True, db_column=b'categoria_data_criacao')),
                ('data_modificacao', models.DateTimeField(auto_now=True, db_column=b'categoria_data_modificacao')),
                ('ativa', models.BooleanField(default=True, db_column=b'categoria_ativa')),
                ('posicao', models.IntegerField(default=0, db_column=b'categoria_posicao')),
                ('destaque', models.BooleanField(default=False, db_column=b'categoria_em_destaque')),
                ('url', models.CharField(max_length=255, null=True, db_column=b'categoria_url')),
                ('nome', models.CharField(max_length=255, db_column=b'categoria_nome')),
                ('descricao', models.TextField(null=True, db_column=b'categoria_descricao')),
                ('lft', models.PositiveIntegerField(editable=False, db_index=True)),
                ('rght', models.PositiveIntegerField(editable=False, db_index=True)),
                ('tree_id', models.PositiveIntegerField(editable=False, db_index=True)),
                ('level', models.PositiveIntegerField(editable=False, db_index=True)),
            ],
            options={
                'ordering': ['posicao'],
                'db_table': 'catalogo"."tb_categoria',
                'verbose_name': 'Categoria',
                'verbose_name_plural': 'Categorias',
                'get_latest_by': 'id',
            },
        ),
        migrations.CreateModel(
            name='CategoriaGlobal',
            fields=[
                ('id', repositories.custom_models.BigAutoField(serialize=False, primary_key=True, db_column=b'categoria_global_id')),
                ('nome', models.CharField(max_length=128, db_column=b'categoria_global_nome')),
                ('data_criacao', models.DateTimeField(auto_now_add=True, db_column=b'categoria_global_data_criacao')),
                ('data_modificacao', models.DateTimeField(auto_now=True, db_column=b'categoria_global_data_modificacao')),
                ('lft', models.PositiveIntegerField(editable=False, db_index=True)),
                ('rght', models.PositiveIntegerField(editable=False, db_index=True)),
                ('tree_id', models.PositiveIntegerField(editable=False, db_index=True)),
                ('level', models.PositiveIntegerField(editable=False, db_index=True)),
            ],
            options={
                'db_table': 'catalogo"."tb_categoria_global',
                'verbose_name': 'Categoria global',
                'verbose_name_plural': 'Categorias globais',
            },
        ),
        migrations.CreateModel(
            name='Grade',
            fields=[
                ('id', repositories.custom_models.BigAutoField(serialize=False, primary_key=True, db_column=b'grade_id')),
                ('id_externo', models.IntegerField(default=None, null=True, db_column=b'grade_id_externo')),
                ('nome', models.CharField(max_length=255, db_column=b'grade_nome')),
                ('nome_visivel', models.CharField(max_length=255, db_column=b'grade_nome_visivel')),
                ('data_criacao', models.DateTimeField(auto_now_add=True, db_column=b'grade_data_criacao')),
                ('data_modificacao', models.DateTimeField(auto_now=True, null=True, db_column=b'grade_data_modificacao')),
                ('pode_ter_imagens', models.BooleanField(default=False, db_column=b'grade_pode_ter_imagens')),
                ('tipo', models.CharField(default=b'normal', max_length=32, db_column=b'grade_tipo')),
                ('posicao', models.IntegerField(default=1000, null=None, db_column=b'grade_posicao')),
            ],
            options={
                'ordering': ['posicao', 'nome'],
                'db_table': 'catalogo"."tb_grade',
                'verbose_name': 'Grade',
                'verbose_name_plural': 'Grades',
            },
        ),
        migrations.CreateModel(
            name='GradeVariacao',
            fields=[
                ('id', repositories.custom_models.BigAutoField(serialize=False, primary_key=True, db_column=b'grade_variacao_id')),
                ('id_externo', models.IntegerField(default=None, null=True, db_column=b'grade_variacao_id_externo')),
                ('nome', models.CharField(max_length=255, db_column=b'grade_variacao_nome')),
                ('data_criacao', models.DateTimeField(auto_now_add=True, db_column=b'grade_variacao_data_criacao')),
                ('data_modificacao', models.DateTimeField(auto_now=True, null=True, db_column=b'grade_variacao_data_modificacao')),
                ('posicao', models.IntegerField(default=0, null=True, db_column=b'grade_variacao_posicao')),
                ('cor', models.CharField(default=None, max_length=32, null=True, db_column=b'grade_variacao_cor')),
                ('cor_secundaria', models.CharField(default=None, max_length=32, null=True, db_column=b'grade_variacao_cor_secundaria')),
            ],
            options={
                'ordering': ['posicao', 'nome'],
                'db_table': 'catalogo"."tb_grade_variacao',
                'verbose_name': 'Varia\xe7\xe3o da grade',
                'verbose_name_plural': 'Varia\xe7\xf5es de grade',
            },
        ),
        migrations.CreateModel(
            name='Marca',
            fields=[
                ('id', repositories.custom_models.BigAutoField(serialize=False, primary_key=True, db_column=b'marca_id')),
                ('id_externo', models.IntegerField(null=True, db_column=b'marca_id_externo')),
                ('data_criacao', models.DateTimeField(auto_now_add=True, db_column=b'marca_data_criacao')),
                ('data_modificacao', models.DateTimeField(auto_now=True, db_column=b'marca_data_modificacao')),
                ('ativo', models.BooleanField(default=False, db_column=b'marca_ativo')),
                ('destaque', models.BooleanField(default=False, db_column=b'marca_destaque')),
                ('imagem', models.CharField(max_length=256, null=True, db_column=b'marca_imagem_caminho', blank=True)),
                ('nome', models.CharField(max_length=255, verbose_name=b'nome', db_column=b'marca_nome')),
                ('apelido', models.CharField(max_length=255, null=True, db_column=b'marca_apelido')),
                ('descricao', models.TextField(null=True, db_column=b'marca_descricao')),
            ],
            options={
                'ordering': ['id'],
                'db_table': 'catalogo"."tb_marca',
                'verbose_name': 'Marca',
                'verbose_name_plural': 'Marcas',
                'get_latest_by': 'id',
            },
        ),
        migrations.CreateModel(
            name='Produto',
            fields=[
                ('id', repositories.custom_models.BigAutoField(serialize=False, primary_key=True, db_column=b'produto_id')),
                ('id_externo', models.IntegerField(null=True, db_column=b'produto_id_externo')),
                ('nome', models.CharField(default=None, max_length=255, null=True, db_column=b'produto_nome')),
                ('apelido', models.CharField(default=None, max_length=255, null=True, db_column=b'produto_apelido')),
                ('descricao', models.TextField(default=None, null=True, db_column=b'produto_descricao')),
                ('descricao_completa', models.TextField(default=None, null=True, db_column=b'produto_descricao_completa')),
                ('url_video_youtube', models.CharField(default=None, max_length=255, null=True, db_column=b'produto_url_video_youtube')),
                ('modelo', models.CharField(default=None, max_length=255, null=True, db_column=b'produto_modelo')),
                ('sku', models.CharField(default=None, max_length=255, null=True, db_column=b'produto_sku')),
                ('ncm', models.CharField(default=None, max_length=10, null=True, db_column=b'produto_ncm', blank=True)),
                ('gtin', models.CharField(default=None, max_length=14, null=True, db_column=b'produto_gtin', blank=True)),
                ('ativo', models.BooleanField(default=False, db_column=b'produto_ativo')),
                ('removido', models.BooleanField(default=False, db_column=b'produto_removido')),
                ('data_criacao', models.DateTimeField(auto_now_add=True, db_column=b'produto_data_criacao')),
                ('data_modificacao', models.DateTimeField(auto_now=True, null=True, db_column=b'produto_data_modificacao')),
                ('peso', models.DecimalField(default=None, null=True, decimal_places=3, max_digits=16, db_column=b'produto_peso')),
                ('altura', models.IntegerField(default=None, null=True, db_column=b'produto_altura')),
                ('largura', models.IntegerField(default=None, null=True, db_column=b'produto_largura')),
                ('profundidade', models.IntegerField(default=None, null=True, db_column=b'produto_comprimento')),
                ('template', models.CharField(default=None, max_length=255, null=True, db_column=b'produto_template')),
                ('tipo', models.CharField(default=b'normal', max_length=255, null=True, db_column=b'produto_tipo', choices=[(b'normal', 'Produto simples'), (b'atributo', 'Produto com op\xe7\xf5es'), (b'virtual', 'Produto virtual'), (b'atributo_opcao', 'Op\xe7\xe3o'), (b'kit', 'Kit de produtos')])),
                ('bloqueado', models.BooleanField(default=False, db_column=b'produto_bloqueado')),
                ('usado', models.BooleanField(default=False, db_column=b'produto_usado')),
                ('destaque', models.BooleanField(default=False, db_column=b'produto_destaque')),
            ],
            options={
                'get_latest_by': 'id',
                'ordering': ['-data_criacao'],
                'verbose_name_plural': 'Produtos',
                'db_table': 'catalogo"."tb_produto',
                'verbose_name': 'Produto',
            },
        ),
        migrations.CreateModel(
            name='ProdutoCaracteristicaValor',
            fields=[
                ('id', repositories.custom_models.BigAutoField(serialize=False, primary_key=True, db_column=b'produto_caracteristica_valor_id')),
                ('texto', models.CharField(max_length=128, null=True, db_column=b'caracteristica_valor_texto')),
            ],
            options={
                'db_table': 'catalogo"."tb_produto_caracteristica_valor',
                'verbose_name': 'Produto categoria global opcao',
                'verbose_name_plural': 'Produtos categorias globais op\xe7\xf5es',
            },
        ),
        migrations.CreateModel(
            name='ProdutoCategoria',
            fields=[
                ('id', repositories.custom_models.BigAutoField(serialize=False, primary_key=True, db_column=b'produto_categoria_id')),
                ('principal', models.BooleanField(default=False, db_column=b'produto_categoria_principal')),
            ],
            options={
                'ordering': ['id'],
                'db_table': 'catalogo"."tb_produto_categoria',
                'verbose_name': 'Categoria de um produto',
                'verbose_name_plural': 'Categorias dos produtos',
            },
        ),
        migrations.CreateModel(
            name='ProdutoEstoque',
            fields=[
                ('id', repositories.custom_models.BigAutoField(serialize=False, primary_key=True, db_column=b'produto_estoque_id')),
                ('gerenciado', models.BooleanField(default=False, db_column=b'produto_estoque_gerenciado')),
                ('quantidade', models.DecimalField(default=0, decimal_places=4, max_digits=16, db_column=b'produto_estoque_quantidade')),
                ('situacao_em_estoque', models.IntegerField(default=0, db_column=b'produto_estoque_situacao_em_estoque')),
                ('situacao_sem_estoque', models.IntegerField(default=0, db_column=b'produto_estoque_situacao_sem_estoque')),
            ],
            options={
                'ordering': ['id'],
                'db_table': 'catalogo"."tb_produto_estoque',
                'verbose_name': 'Estoque do Produto',
                'verbose_name_plural': 'Estoque dos Produtos',
            },
        ),
        migrations.CreateModel(
            name='ProdutoGrade',
            fields=[
                ('id', repositories.custom_models.BigAutoField(serialize=False, primary_key=True, db_column=b'produto_grade_id')),
                ('posicao', models.IntegerField(default=0, db_column=b'produto_grade_posicao')),
            ],
            options={
                'ordering': ['produto', 'grade'],
                'db_table': 'catalogo"."tb_produto_grade',
                'verbose_name': 'Grade de um produto',
                'verbose_name_plural': 'Grades dos produtos',
            },
        ),
        migrations.CreateModel(
            name='ProdutoGradeVariacao',
            fields=[
                ('id', repositories.custom_models.BigAutoField(serialize=False, primary_key=True, db_column=b'produto_grade_variacao_id')),
            ],
            options={
                'ordering': ['grade', 'variacao'],
                'db_table': 'catalogo"."tb_produto_grade_variacao',
                'verbose_name': 'Varia\xe7\xe3o da grade de um produto',
                'verbose_name_plural': 'Varia\xe7\xf5es das grades dos produtos',
            },
        ),
        migrations.CreateModel(
            name='ProdutoGradeVariacaoImagem',
            fields=[
                ('id', repositories.custom_models.BigAutoField(serialize=False, primary_key=True, db_column=b'produto_grade_variacao_imagem_id')),
            ],
            options={
                'db_table': 'catalogo"."tb_produto_grade_variacao_imagem',
                'verbose_name': 'Imagem da grade do Produto',
                'verbose_name_plural': 'Imagens das grades dos produtos',
            },
        ),
        migrations.CreateModel(
            name='ProdutoImagem',
            fields=[
                ('id', repositories.custom_models.BigAutoField(serialize=False, primary_key=True, db_column=b'produto_imagem_id')),
                ('posicao', models.IntegerField(default=None, null=True, db_column=b'produto_imagem_posicao')),
                ('principal', models.NullBooleanField(default=False, db_column=b'produto_imagem_principal')),
            ],
            options={
                'ordering': ['produto', '-principal', 'posicao', 'id'],
                'db_table': 'catalogo"."tb_produto_imagem',
                'verbose_name': 'Imagem do produto',
                'verbose_name_plural': 'Imagens dos produtos',
            },
        ),
        migrations.CreateModel(
            name='ProdutoListaEspera',
            fields=[
                ('id', repositories.custom_models.BigAutoField(serialize=False, primary_key=True, db_column=b'produto_lista_espera_id')),
                ('nome', models.CharField(max_length=256, db_column=b'produto_lista_espera_nome')),
                ('email', models.CharField(max_length=256, db_column=b'produto_lista_espera_email')),
                ('data_solicitacao', models.DateTimeField(auto_now_add=True, db_column=b'produto_lista_espera_data_solicitacao')),
            ],
            options={
                'ordering': ['data_solicitacao'],
                'db_table': 'catalogo"."tb_produto_lista_espera',
                'verbose_name': 'Avise-me por Produto',
                'verbose_name_plural': 'Avise-me por Produtos',
            },
        ),
        migrations.CreateModel(
            name='ProdutoPreco',
            fields=[
                ('id', repositories.custom_models.BigAutoField(serialize=False, primary_key=True, db_column=b'produto_preco_id')),
                ('cheio', models.DecimalField(null=True, decimal_places=4, max_digits=16, db_column=b'produto_preco_cheio')),
                ('promocional', models.DecimalField(null=True, decimal_places=4, max_digits=16, db_column=b'produto_preco_promocional')),
                ('custo', models.DecimalField(null=True, decimal_places=4, max_digits=16, db_column=b'produto_preco_custo')),
                ('sob_consulta', models.BooleanField(default=False, db_column=b'produto_preco_sob_consulta')),
            ],
            options={
                'ordering': ['id'],
                'db_table': 'catalogo"."tb_produto_preco',
                'verbose_name': 'Pre\xe7o do produto',
                'verbose_name_plural': 'Pre\xe7os dos Produtos',
            },
        ),
    ]
