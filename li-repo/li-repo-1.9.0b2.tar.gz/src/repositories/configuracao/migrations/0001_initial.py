# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import jsonfield.fields
import caching.base
import repositories.custom_models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.RunSQL("CREATE SCHEMA IF NOT EXISTS configuracao;"),
        migrations.CreateModel(
            name='Banco',
            fields=[
                ('id', repositories.custom_models.BigAutoField(serialize=False, primary_key=True, db_column=b'banco_id')),
                ('nome', models.CharField(max_length=128, db_column=b'banco_nome')),
                ('imagem', models.CharField(max_length=256, db_column=b'banco_imagem')),
                ('codigo', models.CharField(max_length=3, db_column=b'banco_codigo')),
            ],
            options={
                'ordering': ['nome'],
                'db_table': 'configuracao"."tb_banco',
                'verbose_name': 'Banco',
                'verbose_name_plural': 'Bancos',
            },
        ),
        migrations.CreateModel(
            name='BoletoCarteira',
            fields=[
                ('id', repositories.custom_models.BigAutoField(serialize=False, primary_key=True, db_column=b'boleto_carteira_id')),
                ('numero', models.CharField(max_length=32, db_column=b'boleto_carteira_numero')),
                ('nome', models.CharField(max_length=128, db_column=b'boleto_carteira_nome')),
                ('convenio', models.BooleanField(default=False, db_column=b'boleto_carteira_convenio')),
                ('ativo', models.BooleanField(default=False, db_column=b'boleto_carteira_ativo')),
            ],
            options={
                'db_table': 'configuracao"."tb_boleto_carteira',
                'verbose_name': 'Carteira de boleto',
                'verbose_name_plural': 'Carteiras de boletos',
            },
        ),
        migrations.CreateModel(
            name='CodigoHTML',
            fields=[
                ('id', repositories.custom_models.BigAutoField(serialize=False, primary_key=True, db_column=b'codigo_html_id')),
                ('descricao', models.CharField(max_length=32, verbose_name='Descri\xe7\xe3o', db_column=b'codigo_html_descricao')),
                ('local_publicacao', models.CharField(default=b'rodape', max_length=32, verbose_name='Local publica\xe7\xe3o', db_column=b'codigo_html_local_publicacao', choices=[(b'cabecalho', b'Cabe\xc3\xa7alho'), (b'rodape', 'Rodap\xe9')])),
                ('pagina_publicacao', models.CharField(max_length=32, verbose_name='P\xe1gina publica\xe7\xe3o', db_column=b'codigo_html_pagina_publicacao', choices=[(b'todas', 'Todas as p\xe1ginas'), (b'loja/index', 'P\xe1gina inicial - Home'), (b'loja/produto_detalhar', 'P\xe1gina do produto'), (b'loja/categoria_listar', 'P\xe1gina da categoria'), (b'loja/carrinho_index', 'P\xe1gina do carrinho'), (b'loja/checkout_index', 'P\xe1gina de checkout'), (b'loja/checkout_finalizacao', 'P\xe1gina de finaliza\xe7\xe3o do pedido')])),
                ('data_criacao', models.DateTimeField(auto_now_add=True, verbose_name='Data cria\xe7\xe3o', db_column=b'codigo_html_data_criacao')),
                ('data_modificacao', models.DateTimeField(auto_now=True, null=True, db_column=b'codigo_html_data_modificacao')),
                ('conteudo', models.CharField(help_text=b'Tamanho m\xc3\xa1ximo de 15000 caracteres', max_length=15000, db_column=b'codigo_html_conteudo')),
                ('tipo', models.CharField(default=b'html', max_length=16, db_column=b'codigo_html_tipo', choices=[(b'html', b'HTML'), (b'css', b'Cascade Style Sheet (CSS)'), (b'javascript', b'JavaScript')])),
            ],
            options={
                'db_table': 'configuracao"."tb_codigo_html',
                'verbose_name': 'HTML Customizado',
                'verbose_name_plural': 'HTMLs Customizados',
            },
        ),
        migrations.CreateModel(
            name='ConfiguracaoFacebook',
            fields=[
                ('id', repositories.custom_models.BigAutoField(serialize=False, primary_key=True, db_column=b'conta_configuracao_facebook_id')),
                ('comentarios_produtos', models.BooleanField(default=False, db_column=b'conta_configuracao_facebook_comentarios_produtos')),
                ('usuario', models.CharField(max_length=255, db_column=b'conta_configuracao_facebook_user_admin')),
                ('pagina', models.TextField(db_column=b'conta_configuracao_facebook_pagina')),
                ('compartilhar_compra', models.BooleanField(default=False, db_column=b'conta_configuracao_facebook_compartilhar_compra')),
                ('publicar_novos_produtos', models.BooleanField(default=False, db_column=b'conta_configuracao_facebook_publicar_novos_produtos')),
            ],
            options={
                'ordering': ['id'],
                'db_table': 'configuracao"."tb_configuracao_facebook',
                'verbose_name': 'Configura\xe7\xe3o Facebook',
                'verbose_name_plural': 'Configura\xe7\xf5es Facebook',
            },
        ),
        migrations.CreateModel(
            name='Dominio',
            fields=[
                ('id', repositories.custom_models.BigAutoField(serialize=False, primary_key=True, db_column=b'dominio_id')),
                ('fqdn', models.CharField(unique=True, max_length=128, db_column=b'dominio_fqdn')),
                ('principal', models.BooleanField(default=False, db_index=True, db_column=b'dominio_principal')),
                ('verificado', models.BooleanField(default=False, db_index=True, db_column=b'dominio_verificado')),
                ('data_criacao', models.DateTimeField(auto_now_add=True, db_column=b'dominio_data_criacao')),
                ('data_modificacao', models.DateTimeField(auto_now=True, null=True, db_column=b'dominio_data_modificacao')),
            ],
            options={
                'ordering': ['principal', 'verificado', 'fqdn'],
                'db_table': 'configuracao"."tb_dominio',
                'verbose_name': 'Dom\xednio de uma conta',
                'verbose_name_plural': 'Dom\xednios de uma conta',
                'get_latest_by': 'data_modificacao',
            },
        ),
        migrations.CreateModel(
            name='EdicaoTema',
            fields=[
                ('id', repositories.custom_models.BigAutoField(serialize=False, primary_key=True, db_column=b'edicao_tema_id')),
                ('ativo', models.BooleanField(default=True, db_column=b'edicao_tema_ativo')),
                ('nome', models.CharField(max_length=64, db_column=b'edicao_tema_nome')),
                ('css', models.TextField(default=None, null=True, db_column=b'edicao_tema_css')),
                ('json', models.TextField(default=None, null=True, db_column=b'edicao_tema_json')),
                ('data_criacao', models.DateTimeField(auto_now_add=True, db_column=b'data_criacao')),
                ('data_modificacao', models.DateTimeField(auto_now=True, null=True, db_column=b'data_modificacao')),
            ],
            options={
                'ordering': ['nome'],
                'db_table': 'configuracao"."tb_edicao_tema',
                'verbose_name': 'Edi\xe7\xe3o Tema',
                'verbose_name_plural': 'Edi\xe7\xf5es Tema',
            },
        ),
        migrations.CreateModel(
            name='Envio',
            fields=[
                ('id', repositories.custom_models.BigAutoField(serialize=False, primary_key=True, db_column=b'envio_id')),
                ('nome', models.CharField(max_length=128, db_column=b'envio_nome')),
                ('codigo', models.CharField(max_length=128, db_column=b'envio_codigo')),
                ('tipo', models.CharField(default=b'faixa_cep', max_length=128, db_column=b'envio_tipo', choices=[(b'correios_api', 'API dos Correios'), (b'faixa_cep', 'Faixa de CEP e peso')])),
                ('ativo', models.BooleanField(default=False, db_column=b'envio_ativado')),
                ('imagem', models.CharField(default=None, max_length=255, null=True, db_column=b'envio_imagem')),
                ('posicao', models.IntegerField(default=1000, db_column=b'envio_posicao')),
            ],
            options={
                'ordering': ['posicao', 'nome'],
                'db_table': 'configuracao"."tb_envio',
                'verbose_name': 'Forma de envio',
                'verbose_name_plural': 'Formas de envios',
            },
        ),
        migrations.CreateModel(
            name='EnvioConfiguracao',
            fields=[
                ('id', repositories.custom_models.BigAutoField(serialize=False, primary_key=True, db_column=b'envio_configuracao_id')),
                ('ativo', models.BooleanField(default=False, db_column=b'envio_configuracao_ativo')),
                ('cep_origem', models.CharField(max_length=8, null=True, db_column=b'envio_configuracao_cep_origem')),
                ('codigo_servico', models.CharField(max_length=20, null=True, db_column=b'envio_configuracao_codigo_servico')),
                ('com_contrato', models.BooleanField(default=False, db_column=b'envio_configuracao_com_contrato')),
                ('codigo', models.CharField(max_length=128, null=True, db_column=b'envio_configuracao_codigo')),
                ('senha', models.CharField(max_length=128, null=True, db_column=b'envio_configuracao_senha')),
                ('mao_propria', models.BooleanField(default=False, db_column=b'envio_configuracao_mao_propria')),
                ('valor_declarado', models.BooleanField(default=False, db_column=b'envio_configuracao_valor_declarado')),
                ('aviso_recebimento', models.BooleanField(default=False, db_column=b'envio_configuracao_aviso_recebimento')),
                ('prazo_adicional', models.IntegerField(null=True, db_column=b'envio_configuracao_prazo_adicional')),
                ('taxa_tipo', models.CharField(max_length=32, null=True, db_column=b'envio_configuracao_taxa_tipo', choices=[(b'fixo', 'Valor fixo (R$)'), (b'porcentagem', 'Porcentagem (%)')])),
                ('taxa_valor', models.DecimalField(null=True, decimal_places=2, max_digits=16, db_column=b'envio_configuracao_taxa_valor', blank=True)),
                ('valor_minimo', models.DecimalField(null=True, decimal_places=2, max_digits=16, db_column=b'envio_configuracao_valor_minimo', blank=True)),
                ('data_criacao', models.DateTimeField(auto_now_add=True, db_column=b'envio_data_criacao')),
                ('data_modificacao', models.DateTimeField(auto_now=True, db_column=b'envio_data_modificacao')),
            ],
            options={
                'ordering': ['id'],
                'db_table': 'configuracao"."tb_envio_configuracao',
                'verbose_name': 'Configura\xe7\xe3o da forma de envio',
                'verbose_name_plural': 'Configura\xe7\xf5es das formas de envios',
            },
        ),
        migrations.CreateModel(
            name='EnvioContrato',
            fields=[
                ('id', repositories.custom_models.BigAutoField(serialize=False, primary_key=True, db_column=b'envio_contrato_id')),
                ('codigo', models.IntegerField(db_column=b'envio_contrato_servico_codigo')),
                ('descricao', models.CharField(max_length=50, db_column=b'envio_contrato_descricao')),
                ('contratado', models.BooleanField(default=False, db_column=b'envio_contrato_contratado')),
            ],
            options={
                'ordering': ['codigo'],
                'db_table': 'configuracao"."tb_envio_contrato',
                'verbose_name': 'Contrato da forma de envio',
                'verbose_name_plural': 'Contratos das formas de envios',
            },
        ),
        migrations.CreateModel(
            name='EnvioFaixaCEP',
            fields=[
                ('id', repositories.custom_models.BigAutoField(serialize=False, primary_key=True, db_column=b'envio_faixa_cep_id')),
                ('cep_inicio', models.IntegerField(db_column=b'envio_faixa_cep_cep_inicio')),
                ('cep_fim', models.IntegerField(db_column=b'envio_faixa_cep_cep_fim')),
                ('prazo_entrega', models.IntegerField(default=0, db_column=b'envio_faixa_cep_prazo_entrega')),
            ],
            options={
                'ordering': ['cep_inicio'],
                'db_table': 'configuracao"."tb_envio_faixa_cep',
                'verbose_name': 'Faixa de CEP para regi\xe3o',
                'verbose_name_plural': 'Faixas de CEPs para regi\xf5es',
            },
        ),
        migrations.CreateModel(
            name='EnvioFaixaPeso',
            fields=[
                ('id', repositories.custom_models.BigAutoField(serialize=False, primary_key=True, db_column=b'envio_faixa_peso_id')),
                ('peso_inicio', models.DecimalField(decimal_places=3, max_digits=16, db_column=b'envio_faixa_peso_peso_inicio')),
                ('peso_fim', models.DecimalField(decimal_places=3, max_digits=16, db_column=b'envio_faixa_peso_peso_fim')),
                ('valor', models.DecimalField(default=0, decimal_places=2, max_digits=16, db_column=b'envio_faixa_peso_valor')),
            ],
            options={
                'ordering': ['peso_inicio'],
                'db_table': 'configuracao"."tb_envio_faixa_peso',
                'verbose_name': 'Faixa de peso para regi\xe3o',
                'verbose_name_plural': 'Faixas de pesos para regi\xf5es',
            },
        ),
        migrations.CreateModel(
            name='EnvioRegiao',
            fields=[
                ('id', repositories.custom_models.BigAutoField(serialize=False, primary_key=True, db_column=b'envio_regiao_id')),
                ('pais', models.CharField(default=b'Brasil', max_length=128, db_column=b'envio_regiao_pais')),
                ('nome', models.CharField(max_length=128, db_column=b'envio_regiao_nome')),
                ('ad_valorem', models.DecimalField(default=0, null=True, decimal_places=2, max_digits=16, db_column=b'envio_regiao_ad_valorem')),
                ('kg_adicional', models.DecimalField(default=0, null=True, decimal_places=2, max_digits=16, db_column=b'envio_regiao_kg_adicional')),
            ],
            options={
                'ordering': ['pais', 'nome'],
                'db_table': 'configuracao"."tb_envio_regiao',
                'verbose_name': 'Regi\xe3o da forma de envio',
                'verbose_name_plural': 'Regi\xf5es das formas de envio',
            },
        ),
        migrations.CreateModel(
            name='Facebook',
            fields=[
                ('id', repositories.custom_models.BigAutoField(serialize=False, primary_key=True, db_column=b'conta_facebook_id')),
                ('access_token', models.TextField(db_column=b'conta_facebook_oauth_token')),
                ('pagina', models.CharField(max_length=255, db_column=b'conta_facebook_pagina_id')),
                ('usuario', models.CharField(max_length=255, db_column=b'conta_facebook_usuario_id')),
                ('expires', models.DateTimeField(db_column=b'conta_facebook_oauth_token_expires')),
                ('app_id', models.CharField(max_length=255, db_column=b'conta_facebook_app_id')),
                ('app_secret', models.CharField(max_length=255, db_column=b'conta_facebook_app_secret')),
                ('pro', models.BooleanField(default=False, db_column=b'conta_facebook_pro')),
            ],
            options={
                'ordering': ['id'],
                'db_table': 'configuracao"."tb_facebook',
                'verbose_name': 'Conta Facebook',
                'verbose_name_plural': 'Contas Facebook',
            },
        ),
        migrations.CreateModel(
            name='FormaPagamento',
            fields=[
                ('id', repositories.custom_models.BigAutoField(serialize=False, primary_key=True, db_column=b'pagamento_id')),
                ('nome', models.CharField(max_length=128, db_column=b'pagamento_nome')),
                ('codigo', models.CharField(unique=True, max_length=128, db_column=b'pagamento_codigo')),
                ('ativo', models.BooleanField(default=False, db_column=b'pagamento_ativado')),
                ('valor_minimo_parcela', models.DecimalField(null=True, decimal_places=2, max_digits=16, db_column=b'pagamento_parcela_valor_minimo_parcela')),
                ('valor_minimo_parcelamento', models.DecimalField(null=True, decimal_places=2, max_digits=16, db_column=b'pagamento_parcela_valor_minimo')),
                ('plano_indice', models.IntegerField(default=1, db_column=b'pagamento_plano_indice')),
                ('posicao', models.IntegerField(default=1000, db_column=b'pagamento_posicao')),
            ],
            options={
                'ordering': ['posicao', 'nome'],
                'db_table': 'configuracao"."tb_pagamento',
                'verbose_name': 'Forma de pagamento',
                'verbose_name_plural': 'Formas de pagamentos',
            },
        ),
        migrations.CreateModel(
            name='FormaPagamentoConfiguracao',
            fields=[
                ('id', repositories.custom_models.BigAutoField(serialize=False, primary_key=True, db_column=b'pagamento_configuracao_id')),
                ('usuario', models.CharField(max_length=128, null=True, db_column=b'pagamento_configuracao_usuario')),
                ('senha', models.CharField(max_length=128, null=True, db_column=b'pagamento_configuracao_senha')),
                ('token', models.CharField(max_length=128, null=True, db_column=b'pagamento_configuracao_token')),
                ('assinatura', models.CharField(max_length=128, null=True, db_column=b'pagamento_configuracao_assinatura')),
                ('codigo_autorizacao', models.CharField(max_length=128, null=True, db_column=b'pagamento_configuracao_codigo_autorizacao')),
                ('aplicacao', models.CharField(default=None, max_length=128, null=True, db_column=b'pagamento_configuracao_aplicacao_id')),
                ('ativo', models.BooleanField(default=False, db_column=b'pagamento_configuracao_ativo')),
                ('mostrar_parcelamento', models.BooleanField(default=False, db_column=b'pagamento_coonfiguracao_mostrar_parcelamento')),
                ('maximo_parcelas', models.IntegerField(default=None, null=True, db_column=b'pagamento_configuracao_quantidade_parcela_maxima')),
                ('parcelas_sem_juros', models.IntegerField(default=None, null=True, db_column=b'pagamento_configuracao_quantidade_parcela_sem_juros')),
                ('desconto', models.BooleanField(default=False, db_column=b'pagamento_configuracao_desconto')),
                ('desconto_tipo', models.CharField(default=b'porcentagem', max_length=32, db_column=b'pagamento_configuracao_desconto_tipo')),
                ('desconto_valor', models.DecimalField(null=True, decimal_places=2, max_digits=16, db_column=b'pagamento_configuracao_desconto_valor')),
                ('email_comprovante', models.EmailField(max_length=254, null=True, db_column=b'pagamento_configuracao_email_comprovante')),
                ('informacao_complementar', models.TextField(null=True, db_column=b'pagamento_configuracao_informacao_complementar')),
                ('aplicar_no_total', models.BooleanField(default=False, db_column=b'pagamento_configuracao_desconto_aplicar_no_total')),
                ('valor_minimo_aceitado', models.DecimalField(null=True, decimal_places=2, max_digits=16, db_column=b'pagamento_configuracao_valor_minimo_aceitado')),
                ('valor_minimo_parcela', models.DecimalField(null=True, decimal_places=2, max_digits=16, db_column=b'pagamento_configuracao_valor_minimo_parcela')),
                ('juros_valor', models.DecimalField(null=True, decimal_places=2, max_digits=16, db_column=b'pagamento_configuracao_juros_valor')),
                ('json', jsonfield.fields.JSONField(default=None, null=True, db_column=b'pagamento_configuracao_json')),
                ('data_criacao', models.DateTimeField(auto_now_add=True, db_column=b'pagamento_configuracao_data_criacao')),
                ('data_modificacao', models.DateTimeField(auto_now=True, null=True, db_column=b'pagamento_configuracao_data_modificacao')),
            ],
            options={
                'ordering': ['id'],
                'db_table': 'configuracao"."tb_pagamento_configuracao',
                'verbose_name': 'Configura\xe7\xe3o da forma de pagamento',
                'verbose_name_plural': 'Configura\xe7\xf5es das formas de pagamentos',
            },
        ),
        migrations.CreateModel(
            name='PagamentoBanco',
            fields=[
                ('id', repositories.custom_models.BigAutoField(serialize=False, primary_key=True, db_column=b'pagamento_banco_id')),
                ('agencia', models.CharField(max_length=11, db_column=b'pagamento_banco_agencia')),
                ('numero_conta', models.CharField(max_length=11, db_column=b'pagamento_banco_conta')),
                ('poupanca', models.BooleanField(default=True, db_column=b'pagamento_banco_poupanca')),
                ('operacao', models.CharField(max_length=10, null=True, db_column=b'pagamento_banco_variacao')),
                ('favorecido', models.CharField(max_length=256, db_column=b'pagamento_banco_favorecido')),
                ('cpf', models.CharField(max_length=11, null=True, db_column=b'pagamento_banco_cpf')),
                ('cnpj', models.CharField(max_length=14, null=True, db_column=b'pagamento_banco_cnpj')),
                ('ativo', models.BooleanField(default=False, db_column=b'pagamento_banco_ativo')),
            ],
            options={
                'db_table': 'configuracao"."tb_pagamento_banco',
                'verbose_name': 'Banco para dep\xf3sito',
                'verbose_name_plural': 'Bancos para dep\xf3sito',
            },
        ),
        migrations.CreateModel(
            name='Parcela',
            fields=[
                ('id', repositories.custom_models.BigAutoField(serialize=False, primary_key=True, db_column=b'pagamento_parcela_id')),
                ('numero_parcelas', models.IntegerField(db_column=b'pagamento_parcela_numero_parcelas')),
                ('fator', models.DecimalField(null=True, decimal_places=6, max_digits=16, db_column=b'pagamento_parcela_fator')),
            ],
            options={
                'ordering': ['id'],
                'db_table': 'configuracao"."tb_pagamento_parcela',
                'verbose_name': 'Parcela',
                'verbose_name_plural': 'Parcelas',
            },
            bases=(caching.base.CachingMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Token',
            fields=[
                ('id', repositories.custom_models.BigAutoField(serialize=False, primary_key=True, db_column=b'token_id')),
                ('descricao', models.CharField(max_length=32, db_column=b'token_descricao')),
                ('token', models.CharField(unique=True, max_length=20, db_column=b'token_token')),
            ],
            options={
                'db_table': 'configuracao"."tb_token',
                'verbose_name': 'Token de acesso',
                'verbose_name_plural': 'Tokens de acesso',
            },
        ),
    ]
