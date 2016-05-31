# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalogo', '0002_auto_20160401_1103'),
        ('plataforma', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductImportHistory',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, db_column=b'historico_importacao_id')),
                ('date_created', models.DateTimeField(db_column=b'historico_importacao_data_criacao', auto_now_add=True, help_text='Data da importa\xe7\xe3o do arquivo', verbose_name='Data da Cria\xe7\xe3o')),
                ('date_start', models.DateTimeField(help_text='Data do in\xedcio da importa\xe7\xe3o do arquivo', null=True, verbose_name='Data de In\xedcio', db_column=b'historico_importacao_data_inicio', blank=True)),
                ('date_end', models.DateTimeField(help_text='Data da finaliza\xe7\xe3o da importa\xe7\xe3o do arquivo', null=True, verbose_name='Data da Finaliza\xe7\xe3o', db_column=b'historico_importacao_data_final', blank=True)),
                ('status', models.TextField(default=b'received', help_text='O status da importa\xe7\xe3o do arquivo. "Falha" significa que nenhum Produto foi importado. "Importa\xe7\xe3o Parcial" significa que nem todos os produtosdo arquivo foram importados. "Sucesso" significa que todos os produtos no arquivo foram importados.', verbose_name='Status da Importa\xe7\xe3o', db_column=b'historico_importacao_status', choices=[(b'received', 'Arquivo recebido'), (b'processing', 'Em processamento'), (b'fail', 'Falha'), (b'partial', 'Importado Parcialmente'), (b'success', 'Sucesso')])),
                ('log', models.TextField(help_text='Mensagem sobre o status da importa\xe7\xe3o,', null=True, verbose_name='Log da importa\xe7\xe3o', db_column=b'historico_importacao_mensagem', blank=True)),
                ('error_file', models.TextField(help_text='Arquivo Excel contendo as linhas que n\xe3o foram importadas devido a erros.', null=True, verbose_name='Arquivo com Erros', db_column=b'historico_importacao_arquivo_erro', blank=True)),
                ('original_file', models.TextField(help_text='Arquivo Excel enviado pela Loja.', null=True, verbose_name='Arquivo Original', db_column=b'historico_importacao_arquivo_original', blank=True)),
                ('total_quantity', models.IntegerField(help_text='Total de Linhas no arquivo Excel enviado', null=True, verbose_name='Linhas Excel', db_column=b'historico_importacao_quantidade_total', blank=True)),
                ('success_quantity', models.IntegerField(help_text='Linhas do Excel importadas com sucesso', null=True, verbose_name='Linhas importadas', db_column=b'historico_importacao_quantidade_sucesso', blank=True)),
                ('error_quantity', models.IntegerField(help_text='Linhas do Excel com erros', null=True, verbose_name='Linhas com Erro', db_column=b'historico_importacao_quantidade_erro', blank=True)),
                ('account', models.ForeignKey(db_column=b'conta_id', verbose_name=b'Conta', to='plataforma.Conta', help_text='N\xfamero da Loja')),
                ('contract', models.ForeignKey(db_column=b'contrato_id', verbose_name=b'Contrato', to='plataforma.Contrato', help_text='N\xfamero do Contrato')),
            ],
            options={
                'ordering': ['date_created'],
                'db_table': 'plataforma"."tb_importacao_historico',
                'verbose_name': ('Hist\xf3rico das Importa\xe7\xe3o',),
                'verbose_name_plural': ('Hist\xf3rico das Importa\xe7\xf5es',),
            },
        ),
        migrations.CreateModel(
            name='ProductImportRelation',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, db_column=b'produto_importacao_id')),
                ('status', models.TextField(default=b'created', verbose_name='Resultado da Importa\xe7\xe3o', db_column=b'produto_importacao_status', choices=[(b'created', 'Produto criado'), (b'updated', 'Produto atualizado')])),
                ('account', models.ForeignKey(db_column=b'conta_id', verbose_name=b'Conta', to='plataforma.Conta', help_text='N\xfamero da Loja')),
                ('contract', models.ForeignKey(db_column=b'contrato_id', verbose_name=b'Contrato', to='plataforma.Contrato', help_text='N\xfamero do Contrato')),
                ('importacao', models.ForeignKey(db_column=b'historico_importacao_id', to='plataforma.ProductImportHistory', help_text='Importa\xe7\xe3o que gerou/atualizou o Produto')),
                ('product', models.ForeignKey(db_column=b'produto_id', verbose_name=b'Produto', to='catalogo.Produto', help_text='Produto')),
            ],
            options={
                'db_table': 'plataforma"."tb_importacao_produto',
                'verbose_name': 'Rela\xe7\xe3o de Produto por Importacao',
                'verbose_name_plural': 'Rela\xe7\xe3o de Produtos por Importacao',
            },
        ),
        migrations.AlterUniqueTogether(
            name='productimporthistory',
            unique_together=set([('account', 'contract', 'original_file')]),
        ),
    ]
