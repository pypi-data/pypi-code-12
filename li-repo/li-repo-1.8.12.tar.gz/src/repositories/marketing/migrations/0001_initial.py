# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import jsonfield.fields
import repositories.custom_models


class Migration(migrations.Migration):

    dependencies = [
        ('cliente', '0002_auto_20160401_1103'),
        ('plataforma', '0001_initial'),
        ('domain', '0002_auto_20160401_1103'),
        ('catalogo', '0002_auto_20160401_1103'),
    ]

    operations = [
        migrations.RunSQL("CREATE SCHEMA IF NOT EXISTS marketing;"),
        migrations.CreateModel(
            name='Banner',
            fields=[
                ('id', repositories.custom_models.BigAutoField(serialize=False, primary_key=True, db_column=b'banner_id')),
                ('nome', models.CharField(max_length=128, db_column=b'banner_nome')),
                ('titulo', models.CharField(max_length=512, null=True, db_column=b'banner_titulo', blank=True)),
                ('codigo', models.CharField(max_length=128, db_column=b'banner_codigo')),
                ('tipo', models.CharField(max_length=32, db_column=b'banner_tipo')),
                ('ativo', models.CharField(max_length=128, db_column=b'banner_ativo')),
                ('local_publicacao', models.CharField(max_length=32, db_column=b'banner_local_publicacao', choices=[(b'fullbanner', 'Full banner'), (b'tarja', 'Banner tarja'), (b'vitrine', 'Banner vitrine'), (b'sidebar', 'Banner lateral do Full banner'), (b'esquerda', 'Banner lateral'), (b'minibanner', 'Mini banner')])),
                ('pagina_publicacao', models.CharField(max_length=90, db_column=b'banner_pagina_publicacao')),
                ('caminho', models.CharField(max_length=128, null=True, db_column=b'banner_caminho')),
                ('link', models.CharField(max_length=256, null=True, db_column=b'banner_link')),
                ('ordenacao', models.CharField(max_length=32, null=True, db_column=b'banner_ordenacao', choices=[(b'aleatorio', 'Aleat\xf3rio'), (b'ordenado', 'Ordenado')])),
                ('ordem', models.IntegerField(null=True, db_column=b'banner_ordem')),
                ('limite', models.IntegerField(null=True, db_column=b'banner_limite')),
                ('data_inicio', models.DateTimeField(auto_now_add=True, db_column=b'banner_data_inicio')),
                ('data_fim', models.DateTimeField(auto_now=True, db_column=b'banner_data_fim')),
                ('largura', models.IntegerField(default=None, null=True, db_column=b'banner_largura')),
                ('altura', models.IntegerField(default=None, null=True, db_column=b'banner_altura')),
                ('mapa_imagem', models.TextField(default=None, null=True, db_column=b'banner_mapa_imagem')),
                ('target', models.CharField(default=None, max_length=32, null=True, db_column=b'banner_target')),
                ('conteudo_json', jsonfield.fields.JSONField(null=True, db_column=b'banner_conteudo_json')),
                ('conta', models.ForeignKey(related_name='banners', to='plataforma.Conta')),
                ('contrato', models.ForeignKey(related_name='banners', to='plataforma.Contrato')),
            ],
            options={
                'ordering': ['ordem'],
                'db_table': 'marketing"."tb_banner',
                'verbose_name': 'Banner',
                'verbose_name_plural': 'Banners',
            },
        ),
        migrations.CreateModel(
            name='CupomDesconto',
            fields=[
                ('id', repositories.custom_models.BigAutoField(serialize=False, primary_key=True, db_column=b'cupom_desconto_id')),
                ('descricao', models.TextField(db_column=b'cupom_desconto_descricao')),
                ('codigo', models.CharField(max_length=32, db_column=b'cupom_desconto_codigo')),
                ('valor', models.DecimalField(null=True, decimal_places=2, max_digits=16, db_column=b'cupom_desconto_valor')),
                ('tipo', models.CharField(max_length=32, db_column=b'cupom_desconto_tipo', choices=[(b'fixo', 'Valor fixo'), (b'porcentagem', 'Porcentagem'), (b'frete_gratis', 'Frete gr\xe1tis')])),
                ('cumulativo', models.BooleanField(default=False, db_column=b'cupom_desconto_acumulativo')),
                ('quantidade', models.IntegerField(db_column=b'cupom_desconto_quantidade')),
                ('quantidade_por_cliente', models.IntegerField(null=True, db_column=b'cupom_desconto_quantidade_por_usuario', blank=True)),
                ('quantidade_usada', models.IntegerField(default=0, db_column=b'cupom_desconto_quantidade_utilizada')),
                ('validade', models.DateTimeField(null=True, db_column=b'cupom_desconto_validade')),
                ('valor_minimo', models.DecimalField(null=True, decimal_places=2, max_digits=16, db_column=b'cupom_desconto_valor_minimo')),
                ('data_criacao', models.DateTimeField(auto_now_add=True, db_column=b'cupom_desconto_data_criacao')),
                ('data_modificacao', models.DateTimeField(auto_now=True, db_column=b'cupom_desconto_data_modificacao')),
                ('ativo', models.BooleanField(default=False, db_column=b'cupom_desconto_ativo')),
                ('aplicar_no_total', models.BooleanField(default=False, db_column=b'cupom_desconto_aplicar_no_total')),
                ('conta', models.ForeignKey(related_name='cupons', to='plataforma.Conta')),
                ('contrato', models.ForeignKey(related_name='cupons', to='plataforma.Contrato')),
            ],
            options={
                'ordering': ['codigo'],
                'db_table': 'marketing"."tb_cupom_desconto',
                'verbose_name': 'Cupom de desconto',
                'verbose_name_plural': 'Cupons de desconto',
            },
        ),
        migrations.CreateModel(
            name='FreteGratis',
            fields=[
                ('id', repositories.custom_models.BigAutoField(serialize=False, primary_key=True, db_column=b'frete_gratis_id')),
                ('nome', models.CharField(max_length=256, db_column=b'frete_gratis_nome')),
                ('codigo', models.CharField(max_length=256, db_column=b'frete_gratis_codigo', db_index=True)),
                ('ativo', models.BooleanField(default=False, db_index=True, db_column=b'frete_gratis_ativo')),
                ('valor_minimo', models.DecimalField(decimal_places=2, max_digits=16, db_column=b'frete_gratis_valor_minimo', db_index=True)),
                ('_faixas', models.TextField(default=None, null=True, db_column=b'frete_gratis_faixas')),
                ('conta', models.ForeignKey(related_name='fretes_gratis', to='plataforma.Conta')),
                ('contrato', models.ForeignKey(related_name='fretes_gratis', to='plataforma.Contrato')),
            ],
            options={
                'ordering': ['nome'],
                'db_table': 'marketing"."tb_frete_gratis',
                'verbose_name': 'Frete gr\xe1tis',
                'verbose_name_plural': 'Fretes gr\xe1tis',
            },
        ),
        migrations.CreateModel(
            name='NewsletterAssinatura',
            fields=[
                ('id', repositories.custom_models.BigAutoField(serialize=False, primary_key=True, db_column=b'newsletter_assinatura_id')),
                ('email', models.CharField(max_length=256, db_column=b'newsletter_assinatura_email')),
                ('nome', models.CharField(max_length=256, null=True, db_column=b'newsletter_assinatura_nome')),
                ('ativo', models.BooleanField(default=True, db_column=b'newsletter_assinatura_ativo')),
                ('cliente', models.OneToOneField(related_name='newsletter_assinatura', default=None, to='cliente.Cliente')),
                ('conta', models.ForeignKey(related_name='newsletter_assinaturas', to='plataforma.Conta')),
                ('contrato', models.ForeignKey(related_name='newsletter_assinaturas', to='plataforma.Contrato')),
            ],
            options={
                'ordering': ['email'],
                'db_table': 'marketing"."tb_newsletter_assinatura',
                'verbose_name': 'Assinatura de newsletter',
                'verbose_name_plural': 'Assinaturas de newsletter',
            },
        ),
        migrations.CreateModel(
            name='SEO',
            fields=[
                ('id', repositories.custom_models.BigAutoField(serialize=False, primary_key=True, db_column=b'seo_id')),
                ('tabela', models.CharField(max_length=64, db_column=b'seo_tabela')),
                ('linha_id', models.IntegerField(db_column=b'seo_linha_id')),
                ('data_criacao', models.DateTimeField(auto_now_add=True, db_column=b'seo_data_criacao')),
                ('data_modificacao', models.DateTimeField(auto_now=True, db_column=b'seo_data_modificacao')),
                ('title', models.CharField(max_length=255, null=True, db_column=b'seo_title')),
                ('keyword', models.CharField(max_length=255, null=True, db_column=b'seo_keyword')),
                ('description', models.CharField(max_length=255, null=True, db_column=b'seo_description')),
                ('robots', models.CharField(max_length=32, null=True, db_column=b'seo_robots')),
                ('conta', models.ForeignKey(related_name='seos', to='plataforma.Conta')),
                ('contrato', models.ForeignKey(related_name='seos', to='plataforma.Contrato')),
                ('idioma', models.ForeignKey(related_name='seos', default=b'pt-br', to='domain.Idioma')),
            ],
            options={
                'ordering': ['data_criacao'],
                'db_table': 'marketing"."tb_seo',
                'verbose_name': 'S.E.O.',
                'verbose_name_plural': 'S.E.O.',
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', repositories.custom_models.BigAutoField(serialize=False, primary_key=True, db_column=b'tag_id')),
                ('nome', models.CharField(max_length=32, db_column=b'tag_nome')),
                ('url_imagem', models.CharField(max_length=255, null=True, db_column=b'tag_url_imagem')),
                ('url_cadastro', models.CharField(max_length=255, null=True, db_column=b'tag_url_cadastro')),
                ('local_publicacao', models.CharField(max_length=255, db_column=b'tag_local_publicacao', choices=[(b'cabecalho', 'Cabe\xe7alho'), (b'rodape', 'Rodap\xe9')])),
                ('campos', jsonfield.fields.JSONField(db_column=b'tag_campos_json')),
                ('descricao', models.TextField(null=True, db_column=b'tag_descricao')),
                ('chamada', models.TextField(null=True, db_column=b'tag_chamada')),
                ('em_producao', models.BooleanField(default=True, db_column=b'tag_em_producao')),
                ('tag_global', models.TextField(null=True, db_column=b'tag_global', blank=True)),
                ('index', models.TextField(null=True, db_column=b'tag_index', blank=True)),
                ('catalogo', models.TextField(null=True, db_column=b'tag_catalogo', blank=True)),
                ('produto', models.TextField(null=True, db_column=b'tag_produto', blank=True)),
                ('carrinho', models.TextField(null=True, db_column=b'tag_carrinho', blank=True)),
                ('pedido', models.TextField(null=True, db_column=b'tag_pedido', blank=True)),
                ('pedido_pago', models.TextField(null=True, db_column=b'tag_pedido_pago', blank=True)),
                ('data_criacao', models.DateTimeField(auto_now_add=True, db_column=b'tag_data_criacao')),
                ('data_modificacao', models.DateTimeField(auto_now=True, db_column=b'tag_data_modificacao')),
            ],
            options={
                'db_table': 'marketing"."tb_tag',
                'verbose_name': 'Tag',
                'verbose_name_plural': 'Tags',
            },
        ),
        migrations.CreateModel(
            name='TagConfiguracao',
            fields=[
                ('id', repositories.custom_models.BigAutoField(serialize=False, primary_key=True, db_column=b'tag_configuracao_id')),
                ('dados', jsonfield.fields.JSONField(null=True, db_column=b'tag_configuracao_dados')),
                ('ativa', models.BooleanField(default=False, db_column=b'tag_configuracao_ativa')),
                ('conta', models.ForeignKey(related_name='tag_configuracoes', to='plataforma.Conta')),
                ('contrato', models.ForeignKey(related_name='tag_configuracoes', to='plataforma.Contrato')),
                ('tag', models.ForeignKey(related_name='configuracoes', to='marketing.Tag')),
            ],
            options={
                'db_table': 'marketing"."tb_tag_configuracao',
                'verbose_name': 'Tag configura\xe7\xe3o',
                'verbose_name_plural': 'Tags configura\xe7\xf5es',
            },
        ),
        migrations.CreateModel(
            name='XML',
            fields=[
                ('id', repositories.custom_models.BigAutoField(serialize=False, primary_key=True, db_column=b'xml_id')),
                ('nome', models.CharField(max_length=128, db_column=b'xml_nome')),
                ('codigo', models.CharField(unique=True, max_length=128, db_column=b'xml_codigo')),
                ('ativo', models.BooleanField(default=False, db_column=b'xml_ativo')),
                ('url_cadastro', models.URLField(null=True, db_column=b'xml_url_cadastro')),
                ('chamada', models.TextField(null=True, db_column=b'xml_chamada')),
                ('conteudo_json', jsonfield.fields.JSONField(null=True, db_column=b'xml_conteudo_json')),
                ('oculto', models.BooleanField(default=False, db_column=b'xml_oculto')),
                ('contrato', models.ForeignKey(related_name='xmls', default=None, to='plataforma.Contrato', null=True)),
            ],
            options={
                'ordering': ['nome'],
                'db_table': 'marketing"."tb_xml',
                'verbose_name': 'XML',
                'verbose_name_plural': 'XMLs',
            },
        ),
        migrations.CreateModel(
            name='XmlConfiguracao',
            fields=[
                ('id', repositories.custom_models.BigAutoField(serialize=False, primary_key=True, db_column=b'xml_configuracao_id')),
                ('ativo', models.BooleanField(default=False, db_column=b'xml_configuracao_ativo')),
                ('url', models.CharField(max_length=128, db_column=b'xml_configuracao_url')),
                ('todos_os_produtos', models.BooleanField(default=False, db_column=b'xml_configuracao_todos_os_produtos')),
                ('conteudo_json', jsonfield.fields.JSONField(null=True, db_column=b'xml_configuracao_conteudo_json')),
                ('conta', models.ForeignKey(related_name='xmls_configuracoes', to='plataforma.Conta')),
                ('contrato', models.ForeignKey(related_name='xmls_configuracoes', to='plataforma.Contrato')),
            ],
            options={
                'db_table': 'marketing"."tb_xml_configuracao',
                'verbose_name': 'Configura\xe7\xe3o do XML',
                'verbose_name_plural': 'Configura\xe7\xf5es dos XMLs',
            },
        ),
        migrations.CreateModel(
            name='XmlProduto',
            fields=[
                ('id', repositories.custom_models.BigAutoField(serialize=False, primary_key=True, db_column=b'xml_produto_id')),
                ('configuracao', models.ForeignKey(to='marketing.XmlConfiguracao', db_column=b'xml_configuracao_id')),
                ('produto', models.ForeignKey(to='catalogo.Produto', db_column=b'produto_id')),
            ],
            options={
                'db_table': 'marketing"."tb_xml_produto',
                'verbose_name': 'Produto XML',
                'verbose_name_plural': 'Produtos XML',
            },
        ),
        migrations.AddField(
            model_name='xmlconfiguracao',
            name='produtos',
            field=models.ManyToManyField(related_name='xmls_configuracoes', through='marketing.XmlProduto', to='catalogo.Produto'),
        ),
        migrations.AddField(
            model_name='xmlconfiguracao',
            name='xml',
            field=models.ForeignKey(related_name='configuracoes', to='marketing.XML'),
        ),
        migrations.AlterUniqueTogether(
            name='xmlconfiguracao',
            unique_together=set([('url', 'conta')]),
        ),
        migrations.AlterUniqueTogether(
            name='tagconfiguracao',
            unique_together=set([('tag', 'conta')]),
        ),
        migrations.AlterUniqueTogether(
            name='newsletterassinatura',
            unique_together=set([('email', 'conta')]),
        ),
        migrations.AlterUniqueTogether(
            name='fretegratis',
            unique_together=set([('codigo', 'conta')]),
        ),
        migrations.AlterUniqueTogether(
            name='cupomdesconto',
            unique_together=set([('conta', 'codigo')]),
        ),
        migrations.AlterUniqueTogether(
            name='banner',
            unique_together=set([('codigo', 'conta')]),
        ),
    ]
