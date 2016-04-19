# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import jsonfield.fields
import repositories.domain.models
import repositories.custom_models


class Migration(migrations.Migration):

    dependencies = [
        ('cliente', '0001_initial'),
        ('faturamento', '0001_initial'),
        ('catalogo', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL("CREATE SCHEMA IF NOT EXISTS plataforma;"),
        migrations.CreateModel(
            name='Atividade',
            fields=[
                ('id', repositories.custom_models.BigAutoField(serialize=False, primary_key=True, db_column=b'atividade_id')),
                ('nome', models.CharField(max_length=255, db_column=b'atividade_nome')),
                ('descricao', models.CharField(max_length=1024, db_column=b'atividade_descricao')),
            ],
            options={
                'ordering': ['nome'],
                'db_table': 'plataforma"."tb_atividade',
                'verbose_name': 'Atividade da loja',
                'verbose_name_plural': 'Atividades das lojas',
            },
        ),
        migrations.CreateModel(
            name='Certificado',
            fields=[
                ('id', repositories.custom_models.BigAutoField(serialize=False, primary_key=True, db_column=b'certificado_id')),
                ('ativo', models.BooleanField(default=True, db_column=b'certificado_ativo')),
                ('nome', models.CharField(max_length=64, db_column=b'certificado_nome')),
                ('codigo', models.CharField(unique=True, max_length=64, db_column=b'certificado_codigo')),
                ('fornecedor', models.CharField(max_length=128, db_column=b'certificado_fornecedor')),
                ('fornecedor_site', models.CharField(max_length=256, null=True, db_column=b'certificado_fornecedor_site')),
                ('descricao', models.TextField(default=None, null=True, db_column=b'certificado_descricao')),
                ('valor', models.DecimalField(decimal_places=2, max_digits=16, db_column=b'certificado_valor')),
                ('validade_anos', models.IntegerField(db_column=b'certificado_validade_anos')),
                ('crt_intermediario', models.TextField(null=True, db_column=b'certificado_crt_intermediario')),
                ('crt_raiz', models.TextField(null=True, db_column=b'certificado_crt_raiz')),
            ],
            options={
                'ordering': ['valor'],
                'db_table': 'plataforma"."tb_certificado',
                'verbose_name': 'Certificado',
                'verbose_name_plural': 'Certificados',
            },
        ),
        migrations.CreateModel(
            name='Conta',
            fields=[
                ('id', repositories.custom_models.BigAutoField(serialize=False, primary_key=True, db_column=b'conta_id')),
                ('apelido', models.CharField(max_length=32, db_column=b'conta_apelido')),
                ('logo', models.CharField(default=None, max_length=128, null=True, db_column=b'conta_logo')),
                ('situacao', models.CharField(default=b'ATIVA', max_length=32, db_column=b'conta_situacao', choices=[(b'ATIVA', b'Loja ATIVA'), (b'BLOQUEADA', b'Loja BLOQUEADA'), (b'CANCELADA', b'Loja CANCELADA')])),
                ('data_criacao', models.DateTimeField(auto_now_add=True, db_column=b'conta_data_criacao')),
                ('data_modificacao', models.DateTimeField(auto_now=True, null=True, db_column=b'conta_data_modificacao')),
                ('data_cancelamento', models.DateTimeField(null=True, db_column=b'conta_data_cancelamento')),
                ('verificada', models.BooleanField(default=False, db_column=b'conta_verificada')),
                ('tema_id', models.IntegerField(default=None, null=True, db_column=b'tema_id')),
                ('tema', models.CharField(default=b'v1', max_length=128, db_column=b'conta_loja_tema')),
                ('dominio', models.CharField(default=None, max_length=128, null=True, db_column=b'conta_loja_dominio')),
                ('nome_loja', models.CharField(default=None, max_length=128, null=True, db_column=b'conta_loja_nome')),
                ('nome_loja_title', models.CharField(default=None, max_length=128, null=True, db_column=b'conta_loja_nome_title')),
                ('telefone', models.CharField(default=None, max_length=20, null=True, db_column=b'conta_loja_telefone')),
                ('whatsapp', models.CharField(default=None, max_length=20, null=True, db_column=b'conta_loja_whatsapp')),
                ('skype', models.CharField(default=None, max_length=128, null=True, db_column=b'conta_loja_skype')),
                ('endereco', models.CharField(default=None, max_length=128, null=True, db_column=b'conta_loja_endereco')),
                ('email', models.CharField(default=None, max_length=128, null=True, db_column=b'conta_loja_email')),
                ('css', models.TextField(default=None, null=True, db_column=b'conta_loja_css', blank=True)),
                ('descricao', models.TextField(default=None, null=True, db_column=b'conta_loja_descricao')),
                ('loja_tipo', models.CharField(default=None, max_length=2, null=True, db_column=b'conta_loja_tipo', choices=[(b'PF', 'Pessoa F\xedsica'), (b'PJ', 'Pessoa Jur\xeddica')])),
                ('loja_cpf_cnpj', models.CharField(default=None, max_length=15, null=True, db_column=b'conta_loja_cpf_cnpj')),
                ('loja_razao_social', models.CharField(default=None, max_length=128, null=True, db_column=b'conta_loja_razao_social')),
                ('loja_nome_responsavel', models.CharField(default=None, max_length=128, null=True, db_column=b'conta_loja_nome_responsavel')),
                ('loja_layout', models.TextField(default=None, null=True, db_column=b'conta_loja_layout')),
                ('ultimo_pedido', models.IntegerField(default=0, db_column=b'conta_loja_ultimo_pedido')),
                ('tipo_listagem', models.CharField(default=b'alfabetica', max_length=32, db_column=b'conta_loja_tipo_listagem_produto', choices=[(b'alfabetica', 'Ordem Alfab\xe9tica'), (b'ultimos_produtos', '\xdaltimos produtos'), (b'destaque', 'Produtos em Destaque'), (b'mais_vendidos', 'Produtos mais vendidos')])),
                ('quantidade_destaque', models.IntegerField(default=24, db_column=b'conta_loja_quantidade_destaque')),
                ('ranking_json', jsonfield.fields.JSONField(default=None, db_column=b'conta_ranking_json')),
                ('produtos_linha', models.IntegerField(default=4, db_column=b'conta_loja_produtos_linha')),
                ('banner_ebit', models.TextField(null=True, db_column=b'conta_loja_banner_ebit', blank=True)),
                ('selo_ebit', models.TextField(null=True, db_column=b'conta_loja_selo_ebit', blank=True)),
                ('selo_google_safe', models.BooleanField(default=False, db_column=b'conta_loja_selo_google_safe')),
                ('selo_norton_secured', models.BooleanField(default=False, db_column=b'conta_loja_selo_norton_secured')),
                ('selo_seomaster', models.BooleanField(default=True, db_column=b'conta_loja_selo_seomaster')),
                ('comentarios_produtos', models.BooleanField(default=True, db_column=b'conta_loja_comentarios_produtos')),
                ('blog', models.URLField(max_length=256, null=True, db_column=b'conta_loja_blog')),
                ('favicon', models.TextField(default=None, db_column=b'conta_loja_favicon', blank=True)),
                ('facebook', models.CharField(default=None, max_length=128, null=True, db_column=b'conta_loja_facebook')),
                ('twitter', models.CharField(default=None, max_length=128, null=True, db_column=b'conta_loja_twitter')),
                ('pinterest', models.CharField(default=None, max_length=128, null=True, db_column=b'conta_loja_pinterest')),
                ('instagram', models.CharField(default=None, max_length=128, null=True, db_column=b'conta_loja_instagram')),
                ('google_plus', models.CharField(default=None, max_length=128, null=True, db_column=b'conta_loja_google_plus')),
                ('youtube', models.CharField(default=None, max_length=128, null=True, db_column=b'conta_loja_youtube')),
                ('pedido_valor_minimo', models.DecimalField(decimal_places=3, max_digits=16, db_column=b'conta_pedido_valor_minimo', blank=True)),
                ('ultimo_acesso', models.DateTimeField(default=None, null=True, db_column=b'conta_ultimo_acesso')),
                ('modo', models.CharField(default=b'loja', max_length=32, db_column=b'conta_loja_modo')),
                ('ultima_exportacao', models.DateTimeField(null=True, db_column=b'conta_ultima_exportacao')),
                ('utm_campaign', models.CharField(max_length=255, null=True, db_column=b'conta_utm_campaign')),
                ('utm_source', models.CharField(max_length=255, null=True, db_column=b'conta_utm_source')),
                ('utm_medium', models.CharField(max_length=255, null=True, db_column=b'conta_utm_medium')),
                ('utm_term', models.CharField(max_length=255, null=True, db_column=b'conta_utm_term')),
                ('principal_redirect', models.CharField(max_length=64, null=True, db_column=b'conta_principal_redirect')),
                ('conteudo_json', jsonfield.fields.JSONField(default=None, null=True, db_column=b'conta_conteudo_json')),
                ('email_webmaster_verificado', models.NullBooleanField(default=False, db_column=b'conta_email_webmaster_verificado')),
                ('gerenciar_cliente', models.BooleanField(default=False, db_column=b'conta_gerenciar_cliente')),
                ('chave', repositories.domain.models.UUIDField(max_length=64, db_column=b'conta_chave', blank=True)),
                ('wizard_finalizado', models.BooleanField(default=False, db_column=b'conta_wizard_finalizado')),
                ('manutencao', models.BooleanField(default=False, db_column=b'conta_loja_manutencao')),
                ('habilitar_facebook', models.BooleanField(default=False, db_column=b'conta_habilitar_facebook')),
                ('habilitar_mercadolivre', models.BooleanField(default=False, db_column=b'conta_habilitar_mercadolivre')),
                ('habilitar_mobile', models.BooleanField(default=True, db_column=b'conta_habilitar_mobile')),
                ('origem_pro', models.BooleanField(default=False, db_column=b'conta_origem_pro')),
                ('valor_produto_restrito', models.BooleanField(default=False, db_column=b'conta_valor_produto_restrito')),
            ],
            options={
                'get_latest_by': 'data_criacao',
                'ordering': ['id'],
                'verbose_name_plural': 'Contas',
                'db_table': 'plataforma"."tb_conta',
                'verbose_name': 'Conta',
            },
        ),
        migrations.CreateModel(
            name='ContaAtividade',
            fields=[
                ('id', repositories.custom_models.BigAutoField(serialize=False, primary_key=True, db_column=b'id')),
                ('atividade', models.ForeignKey(related_name='contas_atividade', to='plataforma.Atividade')),
                ('conta', models.ForeignKey(related_name='conta_atividades', to='plataforma.Conta')),
            ],
            options={
                'db_table': 'plataforma"."tb_conta_atividade',
                'verbose_name': 'Atividade da conta',
                'verbose_name_plural': 'Atividades da contas',
            },
        ),
        migrations.CreateModel(
            name='ContaCertificado',
            fields=[
                ('id', repositories.custom_models.BigAutoField(serialize=False, primary_key=True, db_column=b'conta_certificado_id')),
                ('dominio', models.CharField(max_length=128, db_column=b'conta_certificado_dominio')),
                ('key', models.TextField(null=True, db_column=b'conta_certificado_key')),
                ('csr', models.TextField(null=True, db_column=b'conta_certificado_csr')),
                ('crt', models.TextField(null=True, db_column=b'conta_certificado_crt')),
                ('data_inicio', models.DateTimeField(auto_now_add=True, db_column=b'conta_certificado_data_inicio')),
                ('data_expiracao', models.DateTimeField(null=True, db_column=b'conta_certificado_data_expiracao')),
                ('situacao', models.CharField(default='pendente', max_length=32, db_column=b'conta_certificado_situacao', choices=[('ativo', 'Ativo'), ('pendente', 'Pendete'), ('aguardando_aprovacao', 'Aguardando aprova\xe7\xe3o'), ('vencido', 'Vencido')])),
                ('nc_compra_id', models.IntegerField(null=True, db_column=b'conta_certificado_namecheap_compra_id')),
                ('nc_certificado_id', models.IntegerField(null=True, db_column=b'conta_certificado_namecheap_certificado_id')),
                ('nc_transacao_id', models.IntegerField(null=True, db_column=b'conta_certificado_namecheap_transacao_id')),
                ('certificado', models.ForeignKey(related_name='contas', to='plataforma.Certificado')),
                ('conta', models.ForeignKey(related_name='conta_certificado', to='plataforma.Conta')),
            ],
            options={
                'db_table': 'plataforma"."tb_conta_certificado',
                'verbose_name': 'Certificado SSL',
                'verbose_name_plural': 'Certificados SSL',
            },
        ),
        migrations.CreateModel(
            name='ContaUsuario',
            fields=[
                ('id', repositories.custom_models.BigAutoField(serialize=False, primary_key=True, db_column=b'conta_usuario_id')),
                ('administrador', models.BooleanField(default=False, db_column=b'conta_usuario_administrador')),
                ('conta', models.ForeignKey(related_name='conta_usuarios', db_column=b'conta_id', to='plataforma.Conta')),
            ],
            options={
                'db_table': 'plataforma"."tb_conta_usuario',
            },
        ),
        migrations.CreateModel(
            name='ContaUsuarioConvite',
            fields=[
                ('id', repositories.custom_models.BigAutoField(serialize=False, primary_key=True, db_column=b'conta_usuario_convite_id')),
                ('email', models.EmailField(max_length=254, db_column=b'conta_usuario_convite_email')),
                ('chave', models.CharField(max_length=64, db_column=b'conta_usuario_convite_chave')),
                ('data_criacao', models.DateTimeField(auto_now_add=True, db_column=b'conta_usuario_convite_data_criacao')),
                ('conta', models.ForeignKey(related_name='convites', db_column=b'conta_id', to='plataforma.Conta')),
            ],
            options={
                'ordering': ['id'],
                'db_table': 'plataforma"."tb_conta_usuario_convite',
                'verbose_name': 'Convite',
                'verbose_name_plural': 'Convites',
            },
        ),
        migrations.CreateModel(
            name='Contrato',
            fields=[
                ('id', repositories.custom_models.BigAutoField(serialize=False, primary_key=True, db_column=b'contrato_id')),
                ('ativo', models.BooleanField(default=True, verbose_name='Ativo?', db_column=b'contrato_ativo')),
                ('data_inicio', models.DateField(verbose_name='Data de in\xedcio do contrato', db_column=b'contrato_data_inicio')),
                ('validade_meses', models.IntegerField(default=12, verbose_name='Tempora de validade', db_column=b'contrato_validade_meses', choices=[(6, '6'), (12, '12'), (18, '18'), (24, '24'), (32, '32')])),
                ('colecao_id', models.IntegerField(default=1, verbose_name='ID da Cole\xe7\xe3o', db_column=b'colecao_id')),
                ('tipo', models.CharField(default=b'revenda', max_length=32, verbose_name='Tipo', db_column=b'contrato_tipo', choices=[(b'revenda', 'Revenda'), (b'whitelabel', 'Whitelabel')])),
                ('dia_vencimento', models.IntegerField(db_column=b'contrato_dia_vencimento', default=None, choices=[(None, ' - Vazio - '), (1, 'Dia 1'), (2, 'Dia 2'), (3, 'Dia 3'), (4, 'Dia 4'), (5, 'Dia 5'), (6, 'Dia 6'), (7, 'Dia 7'), (8, 'Dia 8'), (9, 'Dia 9'), (10, 'Dia 10'), (11, 'Dia 11'), (12, 'Dia 12'), (13, 'Dia 13'), (14, 'Dia 14'), (15, 'Dia 15'), (16, 'Dia 16'), (17, 'Dia 17'), (18, 'Dia 18'), (19, 'Dia 19'), (20, 'Dia 20'), (21, 'Dia 21'), (22, 'Dia 22'), (23, 'Dia 23'), (24, 'Dia 24'), (25, 'Dia 25'), (26, 'Dia 26'), (27, 'Dia 27'), (28, 'Dia 28')], blank=True, null=True, verbose_name='Dia do vencimento da fatura')),
                ('cadastro_restrito', models.BooleanField(default=False, verbose_name='Cadastro restrito pelo administrador?', db_column=b'contrato_cadastro_restrito')),
                ('minimo_mensal_valor', models.DecimalField(null=0.0, decimal_places=2, max_digits=16, db_column=b'contrato_minimo_mensal_valor')),
                ('minimo_mensal_inicio_em_meses', models.IntegerField(default=0, null=True, db_column=b'contrato_minimo_mensal_inicio_em_meses')),
                ('razao_social', models.CharField(max_length=255, verbose_name='Raz\xe3o social', db_column=b'contrato_razao_social')),
                ('tipo_pessoa', models.CharField(db_column=b'contrato_tipo_pessoa', default=b'PJ', choices=[(b'PF', 'Pessoa F\xedsica'), (b'PJ', 'Pessoa Jur\xeddica')], max_length=2, null=True, verbose_name='Tipo de pessoa')),
                ('cpf_cnpj', models.CharField(default=None, max_length=15, null=True, verbose_name='CNPJ', db_column=b'contrato_cpf_cnpj')),
                ('nome_responsavel', models.CharField(default=None, max_length=128, null=True, verbose_name='Respons\xe1vel financeiro', db_column=b'contrato_nome_responsavel')),
                ('email_nota_fiscal', models.CharField(db_column=b'contrato_email_nota_fiscal', default=None, max_length=128, help_text='Ser\xe1 usado para envio de fatura e boleto quando existente.', null=True, verbose_name='Email do financeiro')),
                ('telefone_principal', models.CharField(default=None, max_length=11, null=True, verbose_name='Telefone principal', db_column=b'contrato_telefone_principal')),
                ('telefone_celular', models.CharField(default=None, max_length=11, null=True, verbose_name='Telefone celular', db_column=b'contrato_telefone_celular')),
                ('endereco_logradouro', models.CharField(default=None, max_length=128, null=True, verbose_name='Endere\xe7o', db_column=b'contrato_endereco_logradouro')),
                ('endereco_numero', models.CharField(default=None, max_length=32, null=True, verbose_name='N\xfamero', db_column=b'contrato_endereco_numero')),
                ('endereco_complemento', models.CharField(default=None, max_length=128, null=True, verbose_name='Complemento', db_column=b'contrato_endereco_complemento')),
                ('endereco_bairro', models.CharField(default=None, max_length=50, null=True, verbose_name='Bairro', db_column=b'contrato_endereco_bairro')),
                ('endereco_cep', models.CharField(db_column=b'contrato_endereco_cep', default=None, max_length=8, help_text='Somente n\xfameros.', null=True, verbose_name='CEP')),
                ('endereco_cidade', models.CharField(default=None, max_length=50, null=True, verbose_name='Cidade', db_column=b'contrato_endereco_cidade')),
                ('endereco_cidade_ibge', models.IntegerField(default=None, help_text='Somente n\xfameros.', null=True, verbose_name='C\xf3digo da cidade no IBGE', db_column=b'contrato_endereco_cidade_ibge')),
                ('endereco_estado', models.CharField(default=None, max_length=2, null=True, verbose_name='Estado', db_column=b'contrato_endereco_estado')),
                ('comentario', models.TextField(db_column=b'contrato_comentario', default=None, blank=True, help_text='Preencha com alguma informa\xe7\xe3o relevante do contrato ou outros meios de contato como celular, skype, email alternativo, etc...', null=True, verbose_name='Outras informa\xe7\xf5es')),
                ('nome', models.CharField(max_length=255, verbose_name='Nome da plataforma', db_column=b'contrato_nome')),
                ('codigo', models.CharField(help_text='Exemplo: plataforma-exemplo', unique=True, max_length=255, verbose_name='C\xf3digo interno', db_column=b'contrato_codigo')),
                ('dominio', models.CharField(max_length=255, verbose_name='Dom\xednio', db_column=b'contrato_dominio')),
                ('url_institucional', models.CharField(max_length=255, verbose_name='Site institucional', db_column=b'contrato_url_institucional')),
                ('url_termo', models.CharField(max_length=255, verbose_name='URL Termo de uso', db_column=b'contrato_url_termo')),
                ('headtags', models.TextField(default=None, null=True, verbose_name='Headtags', db_column=b'contrato_headtags', blank=True)),
                ('parametros', jsonfield.fields.JSONField(help_text='Os parametros informados v\xe3o sobreescrever os do contrato principal.', null=True, verbose_name='Parametros do contrato', db_column=b'contrato_parametros')),
                ('certificado_ssl', models.TextField(db_column=b'contrato_certificado_ssl', default=None, blank=True, help_text='Certificado SSL WildCard para *.dominioexemplo.com.br em formato PEM. Sugest\xe3o de compra: https://www.namecheap.com/security/ssl-certificates/wildcard.aspx', null=True, verbose_name='Certificado SSL')),
                ('chave', repositories.domain.models.UUIDField(max_length=64, db_column=b'contrato_chave', blank=True)),
                ('html', models.TextField(default=None, null=True, verbose_name='C\xf3digo HTML', db_column=b'contrato_html', blank=True)),
            ],
            options={
                'ordering': ['id'],
                'db_table': 'plataforma"."tb_contrato',
                'verbose_name': 'Contrato',
                'verbose_name_plural': 'Contratos',
            },
        ),
        migrations.CreateModel(
            name='Email',
            fields=[
                ('id', repositories.custom_models.BigAutoField(serialize=False, primary_key=True, db_column=b'email_id')),
                ('de', models.CharField(max_length=256, db_column=b'email_de')),
                ('para', models.CharField(max_length=256, db_column=b'email_para')),
                ('responder_para', models.CharField(max_length=256, null=True, db_column=b'email_responder_para')),
                ('conteudo_html', models.TextField(db_column=b'email_conteudo_html')),
                ('conteudo_txt', models.TextField(null=True, db_column=b'email_conteudo_txt')),
                ('assunto', models.CharField(max_length=128, db_column=b'email_tipo')),
                ('lido', models.BooleanField(default=False, db_column=b'email_lido')),
                ('erro', models.TextField(null=True, db_column=b'email_erro')),
                ('data_criacao', models.DateTimeField(auto_now_add=True, db_column=b'email_data_criacao')),
                ('prioridade', models.IntegerField(default=1, db_column=b'email_prioridade')),
                ('cliente', models.ForeignKey(related_name='emails', db_column=b'cliente_id', default=None, to='cliente.Cliente', null=True)),
                ('conta', models.ForeignKey(related_name='emails', db_column=b'conta_id', default=None, to='plataforma.Conta', null=True)),
                ('contrato', models.ForeignKey(related_name='emails', to='plataforma.Contrato')),
            ],
            options={
                'get_latest_by': 'data_criacao',
                'verbose_name': 'Email',
                'verbose_name_plural': 'Emails',
                'db_table': 'plataforma"."tb_email',
            },
        ),
        migrations.CreateModel(
            name='EmailTemplate',
            fields=[
                ('id', repositories.custom_models.BigAutoField(serialize=False, primary_key=True, db_column=b'email_template_id')),
                ('ativo', models.BooleanField(default=True, db_column=b'email_template_ativo')),
                ('codigo', models.CharField(max_length=256, db_column=b'email_template_codigo')),
                ('descricao', models.TextField(null=True, db_column=b'email_template_descricao')),
                ('assunto', models.CharField(max_length=512, db_column=b'email_template_assunto')),
                ('conteudo_html', models.TextField(db_column=b'email_template_conteudo_html')),
                ('conteudo_txt', models.TextField(null=True, db_column=b'email_template_conteudo_txt')),
                ('de', models.CharField(max_length=256, db_column=b'email_template_de', choices=[(b'sistema_contato', 'Plataforma - contato'), (b'sistema_suporte', 'Plataforma - suporte'), (b'lojista_contato', 'Lojista - contato'), (b'lojista_suporte', 'Lojista - suporte'), (b'lojista_vendas', 'Lojista - vendas'), (b'cliente', 'Cliente')])),
                ('para', models.CharField(max_length=256, db_column=b'email_template_para', choices=[(b'sistema_contato', 'Plataforma - contato'), (b'sistema_suporte', 'Plataforma - suporte'), (b'lojista_contato', 'Lojista - contato'), (b'lojista_suporte', 'Lojista - suporte'), (b'lojista_vendas', 'Lojista - vendas'), (b'cliente', 'Cliente')])),
                ('responder_para', models.CharField(max_length=256, null=True, db_column=b'email_template_responder_para', choices=[(b'sistema_contato', 'Plataforma - contato'), (b'sistema_suporte', 'Plataforma - suporte'), (b'lojista_contato', 'Lojista - contato'), (b'lojista_suporte', 'Lojista - suporte'), (b'lojista_vendas', 'Lojista - vendas'), (b'cliente', 'Cliente')])),
                ('data_criacao', models.DateTimeField(auto_now_add=True, db_column=b'email_template_data_criacao')),
                ('data_modificacao', models.DateTimeField(auto_now=True, db_column=b'email_template_data_modificacao')),
                ('contrato', models.ForeignKey(related_name='emails_templates', default=1, to='plataforma.Contrato', null=True)),
            ],
            options={
                'ordering': ['codigo'],
                'db_table': 'plataforma"."tb_email_template',
                'verbose_name': 'Template de email',
                'verbose_name_plural': 'Templates de emails',
            },
        ),
        migrations.CreateModel(
            name='Index',
            fields=[
                ('id', repositories.custom_models.BigAutoField(serialize=False, primary_key=True, db_column=b'index_id')),
                ('status', models.IntegerField(default=1, db_column=b'index_status')),
                ('data_atualizacao', models.DateTimeField(auto_now=True, db_column=b'index_data_atualizacao')),
                ('mensagem_erro', models.TextField(db_column=b'index_mensagem_erro')),
                ('categoria', models.ForeignKey(to='catalogo.Categoria', db_column=b'categoria_id')),
                ('categoria_global', models.ForeignKey(to='catalogo.CategoriaGlobal', db_column=b'cateogria_global_id')),
                ('conta', models.ForeignKey(to='plataforma.Conta', db_column=b'conta_id')),
                ('plano', models.ForeignKey(to='faturamento.Plano', db_column=b'plano_id')),
                ('produto', models.ForeignKey(to='catalogo.Produto', db_column=b'produto_id')),
            ],
            options={
                'ordering': ['id'],
                'db_table': 'plataforma"."tb_index',
                'verbose_name': 'Indice',
                'verbose_name_plural': 'Indices',
            },
        ),
        migrations.CreateModel(
            name='Observacao',
            fields=[
                ('id', repositories.custom_models.BigAutoField(serialize=False, primary_key=True, db_column=b'observacao_id')),
                ('tabela', models.CharField(max_length=64, db_column=b'observacao_tabela')),
                ('linha_id', models.BigIntegerField(db_column=b'observacao_linha_id')),
                ('conteudo', models.TextField(null=True, db_column=b'observacao_conteudo')),
                ('encaminhada', models.BooleanField(default=False, db_column=b'observacao_encaminhada')),
                ('data_criacao', models.DateTimeField(auto_now_add=True, db_column=b'observacao_data_criacao')),
                ('conta', models.ForeignKey(related_name='observacoes', db_column=b'conta_id', to='plataforma.Conta')),
                ('contrato', models.ForeignKey(related_name='observacoes', db_column=b'contrato_id', to='plataforma.Contrato')),
            ],
            options={
                'ordering': ['id'],
                'db_table': 'plataforma"."tb_observacao',
                'verbose_name': 'Observa\xe7\xe3o',
                'verbose_name_plural': 'Observa\xe7\xf5es',
            },
        ),
        migrations.CreateModel(
            name='Pagina',
            fields=[
                ('id', repositories.custom_models.BigAutoField(serialize=False, primary_key=True, db_column=b'pagina_id')),
                ('url', models.CharField(max_length=500, db_column=b'pagina_url')),
                ('titulo', models.CharField(max_length=500, db_column=b'pagina_titulo')),
                ('conteudo', models.TextField(db_column=b'pagina_conteudo')),
                ('posicao', models.IntegerField(null=True, db_column=b'pagina_posicao')),
                ('ativo', models.BooleanField(default=False, db_column=b'pagina_ativo')),
                ('data_criacao', models.DateTimeField(auto_now_add=True, db_column=b'pagina_data_criacao')),
                ('data_modificacao', models.DateTimeField(auto_now=True, db_column=b'pagina_data_modificacao')),
                ('conta', models.ForeignKey(related_name='paginas', to='plataforma.Conta')),
                ('contrato', models.ForeignKey(related_name='paginas', to='plataforma.Contrato')),
            ],
            options={
                'ordering': ['posicao', 'titulo'],
                'db_table': 'plataforma"."tb_pagina',
                'verbose_name': 'P\xe1gina',
                'verbose_name_plural': 'P\xe1ginas',
            },
        ),
        migrations.CreateModel(
            name='Parceiro',
            fields=[
                ('id', repositories.custom_models.BigAutoField(serialize=False, primary_key=True, db_column=b'parceiro_id')),
                ('nome', models.CharField(unique=True, max_length=128, db_column=b'parceiro_nome')),
                ('nome_responsavel', models.CharField(unique=True, max_length=128, db_column=b'parceiro_nome_responsavel')),
                ('categoria', models.CharField(max_length=64, db_column=b'parceiro_categoria', choices=[(b'design', 'Design'), (b'consultoria', 'Consultoria'), (b'email_marketing', b'Email marketing'), (b'catalogo', 'ERP'), (b'marketing_digital', 'Marketing digital'), (b'servico', 'Servi\xe7o'), (b'outros', 'Outros')])),
                ('ativo', models.BooleanField(default=False, db_column=b'parceiro_ativo')),
                ('data_contrato', models.DateField(null=True, db_column=b'parceiro_data_contrato')),
                ('url', models.CharField(max_length=256, db_column=b'parceiro_url')),
                ('logo', models.CharField(max_length=256, db_column=b'parceiro_logo')),
                ('descricao', models.TextField(null=True, db_column=b'parceiro_descricao')),
                ('telefone', models.CharField(default=None, max_length=11, null=True, verbose_name='Telefone principal', db_column=b'parceiro_telefone')),
                ('email', models.EmailField(max_length=254, db_column=b'parceiro_email')),
            ],
            options={
                'ordering': ['nome'],
                'db_table': 'plataforma"."tb_parceiro',
                'verbose_name': 'Parceiro',
                'verbose_name_plural': 'Parceiros',
            },
        ),
        migrations.CreateModel(
            name='URL',
            fields=[
                ('id', repositories.custom_models.BigAutoField(serialize=False, primary_key=True, db_column=b'url_id')),
                ('data_criacao', models.DateTimeField(auto_now_add=True, db_column=b'url_data_criacao')),
                ('data_modificacao', models.DateTimeField(auto_now=True, db_column=b'url_data_modificacao')),
                ('url', models.CharField(max_length=1024, db_column=b'url_canonical_url')),
                ('principal', models.BooleanField(default=True, db_column=b'url_principal')),
                ('categoria', models.ForeignKey(related_name='urls', to='catalogo.Categoria', null=True)),
                ('conta', models.ForeignKey(related_name='urls', to='plataforma.Conta')),
                ('contrato', models.ForeignKey(related_name='urls', to='plataforma.Contrato')),
                ('marca', models.ForeignKey(related_name='urls', to='catalogo.Marca', null=True)),
                ('pagina', models.ForeignKey(related_name='urls', to='plataforma.Pagina', null=True)),
                ('produto', models.ForeignKey(related_name='urls', to='catalogo.Produto', null=True)),
            ],
            options={
                'ordering': ['-data_criacao'],
                'db_table': 'plataforma"."tb_url',
                'verbose_name': 'URL',
                'verbose_name_plural': 'URLs',
            },
        ),
        migrations.CreateModel(
            name='Usuario',
            fields=[
                ('id', repositories.custom_models.BigAutoField(serialize=False, primary_key=True, db_column=b'usuario_id')),
                ('nome', models.CharField(max_length=128, db_column=b'usuario_nome')),
                ('email', models.EmailField(max_length=254, db_column=b'usuario_email')),
                ('_senha', models.CharField(max_length=128, db_column=b'usuario_senha')),
                ('tipo', models.CharField(default=b'cliente', max_length=32, db_column=b'usuario_tipo', choices=[(b'admin_global', 'Administrador global'), (b'admin', 'Administrador do Contrato'), (b'staff', 'Funcion\xe1rio do Contrato'), (b'cliente', 'Cliente')])),
                ('feedback', models.BooleanField(default=True, db_column=b'usuario_feedback')),
                ('cancelado', models.BooleanField(default=False, db_column=b'usuario_cancelado')),
                ('confirmado', models.BooleanField(default=False, db_column=b'usuario_confirmado')),
                ('data_criacao', models.DateTimeField(auto_now_add=True, db_column=b'usuario_data_criacao')),
                ('data_modificacao', models.DateTimeField(auto_now=True, null=True, db_column=b'usuario_data_modificacao')),
                ('data_ultimo_login', models.DateTimeField(default=None, null=True, db_column=b'usuario_data_ultimo_login')),
                ('chave', repositories.domain.models.UUIDField(max_length=64, db_column=b'usuario_chave', blank=True)),
                ('contas', models.ManyToManyField(related_name='usuarios', through='plataforma.ContaUsuario', to='plataforma.Conta')),
                ('contrato', models.ForeignKey(related_name='usuarios', to='plataforma.Contrato')),
            ],
            options={
                'ordering': ['id'],
                'db_table': 'plataforma"."tb_usuario',
                'verbose_name': 'Usu\xe1rio',
                'verbose_name_plural': 'Usu\xe1rios',
            },
        ),
        migrations.CreateModel(
            name='Visita',
            fields=[
                ('id', repositories.custom_models.BigAutoField(serialize=False, primary_key=True, db_column=b'visita_id')),
                ('chave', models.CharField(unique=True, max_length=32, db_column=b'visita_chave')),
                ('dominio', models.CharField(max_length=255, db_column=b'visita_dominio')),
                ('expirado', models.BooleanField(default=False, db_column=b'visita_expirado')),
                ('primeiro_acesso', models.DateTimeField(db_column=b'visita_primeiro_acesso')),
                ('ultimo_acesso', models.DateTimeField(db_column=b'visita_ultimo_acesso')),
                ('pageviews', models.BigIntegerField(db_column=b'visita_pageviews')),
                ('trafego', models.BigIntegerField(db_column=b'visita_trafego')),
            ],
            options={
                'db_table': 'plataforma"."tb_visita',
                'verbose_name': 'Visita atual nas lojas',
                'verbose_name_plural': 'Visitas atuais nas lojas',
            },
        ),
        migrations.AddField(
            model_name='observacao',
            name='usuario',
            field=models.ForeignKey(related_name='observacoes', db_column=b'usuario_id', to='plataforma.Usuario'),
        ),
        migrations.AddField(
            model_name='email',
            name='template',
            field=models.ForeignKey(related_name='emails', db_column=b'email_template_id', default=None, to='plataforma.EmailTemplate', null=True),
        ),
        migrations.AddField(
            model_name='email',
            name='usuario',
            field=models.ForeignKey(related_name='emails', db_column=b'usuario_id', default=None, to='plataforma.Usuario', null=True),
        ),
        migrations.AddField(
            model_name='contausuarioconvite',
            name='contrato',
            field=models.ForeignKey(related_name='convites', to='plataforma.Contrato'),
        ),
        migrations.AddField(
            model_name='contausuarioconvite',
            name='usuario',
            field=models.ForeignKey(related_name='convites', db_column=b'usuario_id', default=None, to='plataforma.Usuario', null=True),
        ),
        migrations.AddField(
            model_name='contausuario',
            name='contrato',
            field=models.ForeignKey(related_name='contas_usuarios', to='plataforma.Contrato'),
        ),
        migrations.AddField(
            model_name='contausuario',
            name='usuario',
            field=models.ForeignKey(related_name='contas_usuario', db_column=b'usuario_id', to='plataforma.Usuario'),
        ),
        migrations.AddField(
            model_name='contacertificado',
            name='contrato',
            field=models.ForeignKey(related_name='contas_certificados', to='plataforma.Contrato'),
        ),
        migrations.AddField(
            model_name='contaatividade',
            name='contrato',
            field=models.ForeignKey(related_name='contas_atividades', to='plataforma.Contrato'),
        ),
        migrations.AddField(
            model_name='conta',
            name='atividades',
            field=models.ManyToManyField(related_name='contas', through='plataforma.ContaAtividade', to='plataforma.Atividade'),
        ),
        migrations.AddField(
            model_name='conta',
            name='contrato',
            field=models.ForeignKey(related_name='contas', to='plataforma.Contrato'),
        ),
        migrations.AddField(
            model_name='certificado',
            name='contrato',
            field=models.ForeignKey(related_name='certificados', to='plataforma.Contrato'),
        ),
        migrations.AlterUniqueTogether(
            name='usuario',
            unique_together=set([('email', 'contrato')]),
        ),
        migrations.AlterUniqueTogether(
            name='url',
            unique_together=set([('url', 'conta', 'contrato')]),
        ),
        migrations.AlterUniqueTogether(
            name='pagina',
            unique_together=set([('conta', 'url')]),
        ),
        migrations.AlterUniqueTogether(
            name='emailtemplate',
            unique_together=set([('codigo', 'contrato')]),
        ),
        migrations.AlterUniqueTogether(
            name='contausuarioconvite',
            unique_together=set([('conta', 'email')]),
        ),
        migrations.AlterUniqueTogether(
            name='contausuario',
            unique_together=set([('conta', 'usuario')]),
        ),
        migrations.AlterUniqueTogether(
            name='contaatividade',
            unique_together=set([('conta', 'atividade')]),
        ),
        migrations.AlterUniqueTogether(
            name='conta',
            unique_together=set([('apelido', 'contrato')]),
        ),
    ]
