# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import mptt.fields


class Migration(migrations.Migration):

    dependencies = [
        ('domain', '0001_initial'),
        ('plataforma', '0001_initial'),
        ('catalogo', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='produtopreco',
            name='conta',
            field=models.ForeignKey(related_name='produtos_preco', to='plataforma.Conta'),
        ),
        migrations.AddField(
            model_name='produtopreco',
            name='contrato',
            field=models.ForeignKey(related_name='produtos_preco', to='plataforma.Contrato'),
        ),
        migrations.AddField(
            model_name='produtopreco',
            name='moeda',
            field=models.ForeignKey(related_name='produtos_preco', default=b'BRL', to='domain.Moeda'),
        ),
        migrations.AddField(
            model_name='produtopreco',
            name='produto',
            field=models.OneToOneField(related_name='preco', to='catalogo.Produto'),
        ),
        migrations.AddField(
            model_name='produtolistaespera',
            name='conta',
            field=models.ForeignKey(related_name='produtos_lista_espera', to='plataforma.Conta'),
        ),
        migrations.AddField(
            model_name='produtolistaespera',
            name='contrato',
            field=models.ForeignKey(related_name='produtos_lista_espera', to='plataforma.Contrato'),
        ),
        migrations.AddField(
            model_name='produtolistaespera',
            name='produto',
            field=models.ForeignKey(related_name='lista_espera', db_column=b'produto_id', to='catalogo.Produto'),
        ),
        migrations.AddField(
            model_name='produtoimagem',
            name='conta',
            field=models.ForeignKey(related_name='produtos_imagens', to='plataforma.Conta'),
        ),
        migrations.AddField(
            model_name='produtoimagem',
            name='contrato',
            field=models.ForeignKey(related_name='produtos_imagens', to='plataforma.Contrato'),
        ),
        migrations.AddField(
            model_name='produtoimagem',
            name='imagem',
            field=models.ForeignKey(related_name='produtos_imagem', to='domain.Imagem'),
        ),
        migrations.AddField(
            model_name='produtoimagem',
            name='produto',
            field=models.ForeignKey(related_name='produto_imagens', to='catalogo.Produto'),
        ),
        migrations.AddField(
            model_name='produtogradevariacaoimagem',
            name='conta',
            field=models.ForeignKey(related_name='produto_grades_imagens', to='plataforma.Conta'),
        ),
        migrations.AddField(
            model_name='produtogradevariacaoimagem',
            name='contrato',
            field=models.ForeignKey(related_name='produto_grades_imagens', to='plataforma.Contrato'),
        ),
        migrations.AddField(
            model_name='produtogradevariacaoimagem',
            name='imagem',
            field=models.ForeignKey(related_name='produtos_grade_imagem', to='domain.Imagem'),
        ),
        migrations.AddField(
            model_name='produtogradevariacaoimagem',
            name='produto',
            field=models.ForeignKey(related_name='produto_grades_imagens', to='catalogo.Produto'),
        ),
        migrations.AddField(
            model_name='produtogradevariacaoimagem',
            name='variacao',
            field=models.ForeignKey(related_name='grade_variacao_id', db_column=b'grade_variacao_id', to='catalogo.GradeVariacao'),
        ),
        migrations.AddField(
            model_name='produtogradevariacao',
            name='conta',
            field=models.ForeignKey(related_name='produtos_grades_variacoes', to='plataforma.Conta'),
        ),
        migrations.AddField(
            model_name='produtogradevariacao',
            name='contrato',
            field=models.ForeignKey(related_name='produtos_grades_variacoes', to='plataforma.Contrato'),
        ),
        migrations.AddField(
            model_name='produtogradevariacao',
            name='grade',
            field=models.ForeignKey(related_name='produtos_grade_variacoes', to='catalogo.Grade'),
        ),
        migrations.AddField(
            model_name='produtogradevariacao',
            name='produto',
            field=models.ForeignKey(related_name='produto_grades_variacoes', to='catalogo.Produto'),
        ),
        migrations.AddField(
            model_name='produtogradevariacao',
            name='produto_grade',
            field=models.ForeignKey(related_name='produto_grades_variacoes', to='catalogo.ProdutoGrade'),
        ),
        migrations.AddField(
            model_name='produtogradevariacao',
            name='produto_pai',
            field=models.ForeignKey(related_name='produto_grades_variacoes_filhos', db_column=b'produto_id_pai', to='catalogo.Produto'),
        ),
        migrations.AddField(
            model_name='produtogradevariacao',
            name='variacao',
            field=models.ForeignKey(related_name='produtos_grade_variacoes', db_column=b'grade_variacao_id', to='catalogo.GradeVariacao'),
        ),
        migrations.AddField(
            model_name='produtograde',
            name='conta',
            field=models.ForeignKey(related_name='produtos_grades', to='plataforma.Conta'),
        ),
        migrations.AddField(
            model_name='produtograde',
            name='contrato',
            field=models.ForeignKey(related_name='produtos_grades', to='plataforma.Contrato'),
        ),
        migrations.AddField(
            model_name='produtograde',
            name='grade',
            field=models.ForeignKey(related_name='produtos_grade', to='catalogo.Grade'),
        ),
        migrations.AddField(
            model_name='produtograde',
            name='produto',
            field=models.ForeignKey(related_name='produto_grades', to='catalogo.Produto'),
        ),
        migrations.AddField(
            model_name='produtoestoque',
            name='conta',
            field=models.ForeignKey(related_name='produtos_estoque', to='plataforma.Conta'),
        ),
        migrations.AddField(
            model_name='produtoestoque',
            name='contrato',
            field=models.ForeignKey(related_name='produtos_estoques', to='plataforma.Contrato'),
        ),
        migrations.AddField(
            model_name='produtoestoque',
            name='produto',
            field=models.OneToOneField(related_name='estoque', to='catalogo.Produto'),
        ),
        migrations.AddField(
            model_name='produtocategoria',
            name='categoria',
            field=models.ForeignKey(related_name='produtos_categoria', to='catalogo.Categoria'),
        ),
        migrations.AddField(
            model_name='produtocategoria',
            name='conta',
            field=models.ForeignKey(related_name='produtos_categorias', to='plataforma.Conta'),
        ),
        migrations.AddField(
            model_name='produtocategoria',
            name='contrato',
            field=models.ForeignKey(related_name='produtos_categorias', to='plataforma.Contrato'),
        ),
        migrations.AddField(
            model_name='produtocategoria',
            name='produto',
            field=models.ForeignKey(related_name='produto_categorias', to='catalogo.Produto'),
        ),
        migrations.AddField(
            model_name='produtocaracteristicavalor',
            name='caracteristica',
            field=models.ForeignKey(related_name='produtos_caracteristica', db_column=b'caracteristica_id', to='catalogo.Caracteristica'),
        ),
        migrations.AddField(
            model_name='produtocaracteristicavalor',
            name='categoria_global',
            field=models.ForeignKey(related_name='produtos_caracteristicas', db_column=b'categoria_global_id', to='catalogo.CategoriaGlobal'),
        ),
        migrations.AddField(
            model_name='produtocaracteristicavalor',
            name='conta',
            field=models.ForeignKey(related_name='produtos_opcoes', db_column=b'conta_id', to='plataforma.Conta'),
        ),
        migrations.AddField(
            model_name='produtocaracteristicavalor',
            name='contrato',
            field=models.ForeignKey(related_name='produtos_opcoes', blank=True, to='plataforma.Contrato', null=True),
        ),
        migrations.AddField(
            model_name='produtocaracteristicavalor',
            name='produto',
            field=models.ForeignKey(related_name='caracteristicas_valores', db_column=b'produto_id', to='catalogo.Produto'),
        ),
        migrations.AddField(
            model_name='produtocaracteristicavalor',
            name='valor',
            field=models.ForeignKey(related_name='produtos', db_column=b'caracteristica_valor_id', to='catalogo.CaracteristicaValor', null=True),
        ),
        migrations.AddField(
            model_name='produto',
            name='categoria_global',
            field=models.ForeignKey(db_column=b'categoria_global_id', to='catalogo.CategoriaGlobal', null=True),
        ),
        migrations.AddField(
            model_name='produto',
            name='categorias',
            field=models.ManyToManyField(related_name='produtos', through='catalogo.ProdutoCategoria', to='catalogo.Categoria'),
        ),
        migrations.AddField(
            model_name='produto',
            name='conta',
            field=models.ForeignKey(related_name='produtos', to='plataforma.Conta'),
        ),
        migrations.AddField(
            model_name='produto',
            name='contrato',
            field=models.ForeignKey(related_name='produtos', to='plataforma.Contrato'),
        ),
        migrations.AddField(
            model_name='produto',
            name='grades',
            field=models.ManyToManyField(related_name='produtos', through='catalogo.ProdutoGrade', to='catalogo.Grade'),
        ),
        migrations.AddField(
            model_name='produto',
            name='imagens',
            field=models.ManyToManyField(related_name='produtos', through='catalogo.ProdutoImagem', to='domain.Imagem'),
        ),
        migrations.AddField(
            model_name='produto',
            name='marca',
            field=models.ForeignKey(related_name='produtos', on_delete=django.db.models.deletion.SET_NULL, to='catalogo.Marca', null=True),
        ),
        migrations.AddField(
            model_name='produto',
            name='pai',
            field=models.ForeignKey(related_name='filhos', db_column=b'produto_id_pai', to='catalogo.Produto', null=True),
        ),
        migrations.AddField(
            model_name='marca',
            name='conta',
            field=models.ForeignKey(related_name='marcas', to='plataforma.Conta'),
        ),
        migrations.AddField(
            model_name='marca',
            name='contrato',
            field=models.ForeignKey(related_name='marcas', to='plataforma.Contrato'),
        ),
        migrations.AddField(
            model_name='gradevariacao',
            name='conta',
            field=models.ForeignKey(related_name='variacoes', to='plataforma.Conta', null=True),
        ),
        migrations.AddField(
            model_name='gradevariacao',
            name='contrato',
            field=models.ForeignKey(related_name='variacoes', to='plataforma.Contrato'),
        ),
        migrations.AddField(
            model_name='gradevariacao',
            name='grade',
            field=models.ForeignKey(related_name='variacoes', to='catalogo.Grade'),
        ),
        migrations.AddField(
            model_name='grade',
            name='conta',
            field=models.ForeignKey(related_name='grades', to='plataforma.Conta', null=True),
        ),
        migrations.AddField(
            model_name='grade',
            name='contrato',
            field=models.ForeignKey(related_name='grades', to='plataforma.Contrato'),
        ),
        migrations.AddField(
            model_name='categoriaglobal',
            name='parent',
            field=mptt.fields.TreeForeignKey(related_name='children', blank=True, to='catalogo.CategoriaGlobal', null=True),
        ),
        migrations.AddField(
            model_name='categoria',
            name='conta',
            field=models.ForeignKey(related_name='categorias', db_column=b'conta_id', to='plataforma.Conta'),
        ),
        migrations.AddField(
            model_name='categoria',
            name='contrato',
            field=models.ForeignKey(related_name='categorias', to='plataforma.Contrato'),
        ),
        migrations.AddField(
            model_name='categoria',
            name='parent',
            field=mptt.fields.TreeForeignKey(related_name='children', on_delete=django.db.models.deletion.PROTECT, blank=True, to='catalogo.Categoria', null=True),
        ),
        migrations.AddField(
            model_name='caracteristicavalor',
            name='caracteristica',
            field=models.ForeignKey(related_name='valores', db_column=b'caracteristica_id', to='catalogo.Caracteristica'),
        ),
        migrations.AddField(
            model_name='caracteristicavalor',
            name='idioma',
            field=models.ForeignKey(related_name='categorias_globais_filtros_opcoes', default=b'pt-br', to='domain.Idioma'),
        ),
        migrations.AddField(
            model_name='caracteristica',
            name='categoria_global',
            field=models.ForeignKey(related_name='caracteristicas', db_column=b'categoria_global_id', to='catalogo.CategoriaGlobal'),
        ),
        migrations.AlterUniqueTogether(
            name='produtogradevariacaoimagem',
            unique_together=set([('conta', 'variacao', 'produto')]),
        ),
        migrations.AlterUniqueTogether(
            name='produtograde',
            unique_together=set([('produto', 'grade')]),
        ),
        migrations.AlterUniqueTogether(
            name='produtocategoria',
            unique_together=set([('produto', 'categoria')]),
        ),
        migrations.AlterUniqueTogether(
            name='produto',
            unique_together=set([('conta', 'sku')]),
        ),
        migrations.AlterUniqueTogether(
            name='gradevariacao',
            unique_together=set([('conta', 'grade', 'nome')]),
        ),
        migrations.AlterUniqueTogether(
            name='grade',
            unique_together=set([('conta', 'nome')]),
        ),
    ]
