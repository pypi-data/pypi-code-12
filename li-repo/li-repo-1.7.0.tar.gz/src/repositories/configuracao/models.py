# -*- coding: utf-8 -*-

from ..models import MyObjects
from django.db import models
from jsonfield import JSONField
from django.utils.text import slugify


class Banco(models.Model):
    id = models.AutoField(db_column="banco_id", primary_key=True)
    nome = models.CharField(db_column="banco_nome", max_length=128)
    imagem = models.CharField(db_column='banco_imagem', max_length=256)
    codigo = models.CharField(db_column='banco_codigo', max_length=3)

    objects = MyObjects()

    class Meta:
        app_label = "repositories_configuracao"
        db_table = u"configuracao\".\"tb_banco"
        verbose_name = u'Banco'
        verbose_name_plural = u'Bancos'
        ordering = ['nome']

    def __unicode__(self):
        return self.nome

    def natural_key(self):
        return self.nome


class BoletoCarteira(models.Model):
    id = models.AutoField(db_column="boleto_carteira_id", primary_key=True)

    numero = models.CharField(db_column="boleto_carteira_numero", max_length=32, null=False)
    nome = models.CharField(db_column="boleto_carteira_nome", max_length=128, null=False)
    convenio = models.BooleanField(db_column="boleto_carteira_convenio", default=False, null=False)
    ativo = models.BooleanField(db_column="boleto_carteira_ativo", default=False, null=False)

    objects = MyObjects()

    banco = models.ForeignKey('repositories_configuracao.Banco', db_column="banco_id", related_name='carteiras')

    class Meta:
        app_label = "repositories_configuracao"
        db_table = u"configuracao\".\"tb_boleto_carteira"
        verbose_name = u'Carteira de boleto'
        verbose_name_plural = u'Carteiras de boletos'
        unique_together = (('banco', 'numero', 'convenio'),)

    def __unicode__(self):
        return self.nome


class Parcela(models.Model):
    id = models.AutoField(db_column="pagamento_parcela_id", primary_key=True)
    numero_parcelas = models.IntegerField(db_column="pagamento_parcela_numero_parcelas")
    fator = models.DecimalField(db_column="pagamento_parcela_fator", max_digits=16, decimal_places=6)

    objects = MyObjects()

    forma_pagamento = models.ForeignKey('repositories_configuracao.FormaPagamento', db_column="pagamento_id", related_name="parcelas")

    class Meta:
        app_label = "repositories_configuracao"
        db_table = u"configuracao\".\"tb_pagamento_parcela"
        verbose_name = u'Parcela'
        verbose_name_plural = u"Parcelas"
        ordering = ['id']


class FormaPagamento(models.Model):
    """Forma de pagamento."""

    CODIGOS_GATEWAYS = ['pagseguro', 'pagamento_digital', 'mercadopago', 'paypal', 'mercado_pago']

    PRINCIPAIS_FORMAS_PAGAMENTO = {
        'pagamento_digital': {
            'cartoes': ['visa', 'mastercard', 'hipercard', 'amex'],
            'bancos': ['itau', 'bradesco', 'banco-do-brasil'],
            'outros': ['boleto']
        },
        'pagseguro': {
            'cartoes': ['visa', 'mastercard', 'hipercard', 'amex'],
            'bancos': ['itau', 'bradesco', 'banco-do-brasil'],
            'outros': ['boleto']
        },
        'paypal': {
            'cartoes': ['visa', 'mastercard', 'amex']
        },
        'mercadopago': {
            'cartoes': ['visa', 'mastercard', 'amex', 'elo'],
            'outros': ['boleto']
        },
        'mercado_pago': {
            'cartoes': ['visa', 'mastercard', 'amex', 'elo'],
            'outros': ['boleto']
        }
    }

    id = models.AutoField(db_column="pagamento_id", primary_key=True)
    nome = models.CharField(db_column="pagamento_nome", max_length=128)
    codigo = models.CharField(db_column="pagamento_codigo", max_length=128, unique=True)
    ativo = models.BooleanField(db_column="pagamento_ativado", default=False)
    valor_minimo_parcela = models.DecimalField(db_column='pagamento_parcela_valor_minimo_parcela', max_digits=16, decimal_places=2, null=True)
    valor_minimo_parcelamento = models.DecimalField(db_column='pagamento_parcela_valor_minimo', max_digits=16, decimal_places=2, null=True)
    plano_indice = models.IntegerField(db_column='pagamento_plano_indice', default=1)
    posicao = models.IntegerField(db_column='pagamento_posicao', default=1000, null=False)

    objects = MyObjects()

    conta = models.ForeignKey("repositories_plataforma.Conta", related_name="formas_pagamentos", null=True, default=None)
    contrato = models.ForeignKey("repositories_plataforma.Contrato", related_name="formas_pagamentos", null=True, default=None)

    pedidos = models.ManyToManyField('repositories_pedido.PedidoVenda', through='repositories_pedido.PedidoVendaFormaPagamento', related_name='pedidos')

    class Meta:
        app_label = 'repositories_configuracao'
        db_table = u"configuracao\".\"tb_pagamento"
        verbose_name = u"Forma de pagamento"
        verbose_name_plural = u"Formas de pagamentos"
        ordering = ["posicao", "nome"]

    def __unicode__(self):
        return self.nome


class PagamentoBanco(models.Model):

    id = models.AutoField(db_column="pagamento_banco_id", primary_key=True)
    agencia = models.CharField(db_column="pagamento_banco_agencia", max_length=11, null=False)
    numero_conta = models.CharField(db_column="pagamento_banco_conta", max_length=11, null=False)
    poupanca = models.BooleanField(db_column="pagamento_banco_poupanca", default=True, null=False)
    operacao = models.CharField(db_column="pagamento_banco_variacao", max_length=10, null=True)
    favorecido = models.CharField(db_column="pagamento_banco_favorecido", max_length=256)
    cpf = models.CharField(db_column="pagamento_banco_cpf", max_length=11, null=True)
    cnpj = models.CharField(db_column="pagamento_banco_cnpj", max_length=14, null=True)
    ativo = models.BooleanField(db_column="pagamento_banco_ativo", null=False, default=False)

    objects = MyObjects()

    banco = models.ForeignKey('repositories_configuracao.Banco', db_column="banco_id", related_name='bancos_pagamentos')
    conta = models.ForeignKey('repositories_plataforma.Conta', related_name='pagamento_bancos')
    pagamento = models.ForeignKey('repositories_configuracao.FormaPagamento', db_column="pagamento_id", related_name='bancos')
    contrato = models.ForeignKey("repositories_plataforma.Contrato", related_name="pagamento_bancos")

    class Meta:
        app_label = "repositories_configuracao"
        db_table = u"configuracao\".\"tb_pagamento_banco"
        verbose_name = u'Banco para depósito'
        verbose_name_plural = u'Bancos para depósito'
        unique_together = (('banco', 'conta'),)

    def __unicode__(self):
        return unicode(self.banco.nome)

    def __repr__(self):
        return slugify(self.banco.nome)

    def save(self, *args, **kwargs):
        if self.conta and not self.contrato_id:
            self.contrato_id = self.conta.contrato_id
        super(PagamentoBanco, self).save(*args, **kwargs)

    @property
    def cpf_cnpj(self):
        return self.cpf or self.cnpj or None


class FormaPagamentoConfiguracao(models.Model):
    """Configuração da forma de pagamento."""
    TIPO_VALOR_FIXO = 'fixo'
    TIPO_PORCENTAGEM = 'porcentagem'

    id = models.AutoField(db_column="pagamento_configuracao_id", primary_key=True)
    usuario = models.CharField(db_column="pagamento_configuracao_usuario", max_length=128, null=True)
    senha = models.CharField(db_column="pagamento_configuracao_senha", max_length=128, null=True)
    token = models.CharField(db_column="pagamento_configuracao_token", max_length=128, null=True)
    token_expiracao = models.DateTimeField(db_column="pagamento_configuracao_token_expiracao", null=True)
    assinatura = models.CharField(db_column="pagamento_configuracao_assinatura", max_length=128, null=True)
    codigo_autorizacao = models.CharField(db_column="pagamento_configuracao_codigo_autorizacao", max_length=128, null=True)
    usar_antifraude = models.BooleanField(db_column='pagamento_configuracao_usar_antifraude', null=True, default=False)
    aplicacao = models.CharField(db_column="pagamento_configuracao_aplicacao_id", max_length=128, null=True, default=None)
    ativo = models.BooleanField(db_column="pagamento_configuracao_ativo", default=False)
    eh_padrao = models.BooleanField(db_column="pagamento_configuracao_eh_padrao", default=False)
    mostrar_parcelamento = models.BooleanField(db_column='pagamento_coonfiguracao_mostrar_parcelamento', default=False, null=False)
    maximo_parcelas = models.IntegerField(db_column="pagamento_configuracao_quantidade_parcela_maxima", default=None, null=True)
    parcelas_sem_juros = models.IntegerField(db_column="pagamento_configuracao_quantidade_parcela_sem_juros", default=None, null=True)
    desconto = models.BooleanField(db_column="pagamento_configuracao_desconto", default=False, null=False)
    desconto_tipo = models.CharField(db_column="pagamento_configuracao_desconto_tipo", max_length=32, default=TIPO_PORCENTAGEM)
    desconto_valor = models.DecimalField(db_column='pagamento_configuracao_desconto_valor', max_digits=16, decimal_places=2, null=True)
    juros_valor = models.DecimalField(db_column='pagamento_configuracao_juros_valor', max_digits=16, decimal_places=6, null=True)
    email_comprovante = models.EmailField(db_column='pagamento_configuracao_email_comprovante', null=True)
    informacao_complementar = models.TextField(db_column='pagamento_configuracao_informacao_complementar', null=True)
    aplicar_no_total = models.BooleanField(db_column='pagamento_configuracao_desconto_aplicar_no_total', null=False, default=False)
    valor_minimo_aceitado = models.DecimalField(db_column='pagamento_configuracao_valor_minimo_aceitado', max_digits=16, decimal_places=2, null=True)
    valor_minimo_parcela = models.DecimalField(db_column='pagamento_configuracao_valor_minimo_parcela', max_digits=16, decimal_places=2, null=True)
    ordem = models.IntegerField(db_column='pagamento_configuracao_ordem', default=0)

    json = JSONField(db_column='pagamento_configuracao_json', null=True, default=None)

    objects = MyObjects()

    forma_pagamento = models.ForeignKey('repositories_configuracao.FormaPagamento', db_column="pagamento_id", related_name="configuracoes")
    conta = models.ForeignKey("repositories_plataforma.Conta", related_name="formas_pagamentos_configuracoes")
    contrato = models.ForeignKey("repositories_plataforma.Contrato", related_name="formas_pagamentos_configuracoes")

    data_criacao = models.DateTimeField(db_column='pagamento_configuracao_data_criacao', auto_now_add=True)
    data_modificacao = models.DateTimeField(db_column='pagamento_configuracao_data_modificacao', null=True, auto_now=True)

    class Meta:
        app_label = "repositories_configuracao"
        db_table = u"configuracao\".\"tb_pagamento_configuracao"
        verbose_name = u"Configuração da forma de pagamento"
        verbose_name_plural = u"Configurações das formas de pagamentos"
        ordering = ["id"]
        unique_together = (("conta", "forma_pagamento"),)

    def __unicode__(self):
        return unicode(self.id)


class Envio(models.Model):
    TIPO_CORREIOS_API = 'correios_api'
    TIPO_FAIXA_CEP = 'faixa_cep'
    TIPOS = [
        (TIPO_CORREIOS_API, u'API dos Correios'),
        (TIPO_FAIXA_CEP, u'Faixa de CEP e peso'),
    ]

    """Formas de envios."""
    id = models.AutoField(db_column="envio_id", primary_key=True)
    nome = models.CharField(db_column="envio_nome", max_length=128)
    codigo = models.CharField(db_column="envio_codigo", max_length=128)
    tipo = models.CharField(db_column="envio_tipo", max_length=128,
        choices=TIPOS, null=False, default=TIPO_FAIXA_CEP)
    ativo = models.BooleanField(db_column="envio_ativado", default=False)
    imagem = models.CharField(db_column="envio_imagem", max_length=255, default=None)
    posicao = models.IntegerField(db_column='envio_posicao', default=1000, null=False)

    objects = MyObjects()

    conta = models.ForeignKey("repositories_plataforma.Conta", related_name="formas_envios", null=True, default=None)
    pedidos = models.ManyToManyField('repositories_pedido.PedidoVenda', through='repositories_pedido.PedidoVendaFormaEnvio', related_name='pedidos')

    class Meta:
        app_label = "repositories_configuracao"
        db_table = u"configuracao\".\"tb_envio"
        ordering = ["posicao", "nome"]
        unique_together = (("nome", "codigo", "conta"),)

    def __unicode__(self):
        return self.nome

    @property
    def configuracao(self):
        configuracao = EnvioConfiguracao.objects.filter(conta=self.conta, forma_envio=self)
        if configuracao:
            return configuracao[0]
        return EnvioConfiguracao()

class EnvioConfiguracao(models.Model):
    """Configuração das formas de envios."""
    TAXA_TIPOS = [
        ('fixo', u'Valor fixo (R$)'),
        ('porcentagem', u'Porcentagem (%)')
    ]

    id = models.AutoField(db_column="envio_configuracao_id", primary_key=True)
    ativo = models.BooleanField(db_column="envio_configuracao_ativo", default=False)
    cep_origem = models.CharField(db_column="envio_configuracao_cep_origem", max_length=8, null=True)
    codigo_servico = models.CharField(db_column="envio_configuracao_codigo_servico", max_length=20, null=True)
    com_contrato = models.BooleanField(db_column="envio_configuracao_com_contrato", default=False)
    codigo = models.CharField(db_column="envio_configuracao_codigo", max_length=128, null=True)
    senha = models.CharField(db_column="envio_configuracao_senha", max_length=128, null=True)
    mao_propria = models.BooleanField(db_column="envio_configuracao_mao_propria", default=False)
    valor_declarado = models.BooleanField(db_column="envio_configuracao_valor_declarado", default=False)
    aviso_recebimento = models.BooleanField(db_column="envio_configuracao_aviso_recebimento", default=False)
    prazo_adicional = models.IntegerField(db_column="envio_configuracao_prazo_adicional", null=True)
    taxa_tipo = models.CharField(db_column="envio_configuracao_taxa_tipo", choices=TAXA_TIPOS, max_length=32, null=True)
    taxa_valor = models.DecimalField(db_column="envio_configuracao_taxa_valor", max_digits=16, decimal_places=2, null=True)
    data_criacao = models.DateTimeField(db_column="envio_data_criacao", auto_now_add=True)
    data_modificacao = models.DateTimeField(db_column="envio_data_modificacao", auto_now=True)
    valor_minimo = models.DecimalField(db_column='envio_configuracao_valor_minimo', max_digits=16, decimal_places=2, null=True, blank=True)

    objects = MyObjects()

    forma_envio = models.ForeignKey(Envio, db_column="envio_id", related_name="configuracoes", on_delete=models.CASCADE)
    conta = models.ForeignKey("repositories_plataforma.Conta", related_name="formas_envios_configuracoes")
    contrato = models.ForeignKey("repositories_plataforma.Contrato", related_name="formas_envios_configuracoes")

    class Meta:
        app_label = "repositories_configuracao"
        db_table = u"configuracao\".\"tb_envio_configuracao"
        verbose_name = u"Configuração da forma de envio"
        verbose_name_plural = u"Configurações das formas de envios"
        ordering = ["id"]
        unique_together = (("conta", "forma_envio"),)

    def __unicode__(self):
        return self.cep_origem or ''

class EnvioRegiao(models.Model):
    id = models.AutoField(db_column="envio_regiao_id", primary_key=True)
    pais = models.CharField(db_column="envio_regiao_pais", max_length=128, null=False, default='Brasil')
    nome = models.CharField(db_column="envio_regiao_nome", max_length=128, null=False)
    ad_valorem = models.DecimalField(db_column="envio_regiao_ad_valorem", max_digits=16, decimal_places=2, default=0, null=True)
    kg_adicional = models.DecimalField(db_column="envio_regiao_kg_adicional", max_digits=16, decimal_places=2, default=0, null=True)

    objects = MyObjects()

    forma_envio = models.ForeignKey(Envio, db_column="envio_id", related_name="regioes", on_delete=models.CASCADE)
    forma_envio_configuracao = models.ForeignKey("repositories_configuracao.EnvioConfiguracao", db_column="envio_configuracao_id", related_name="regioes", on_delete=models.CASCADE)
    conta = models.ForeignKey("repositories_plataforma.Conta", related_name="formas_envios_regioes")
    contrato = models.ForeignKey("repositories_plataforma.Contrato", related_name="formas_envios_regioes")

    class Meta:
        app_label = "repositories_configuracao"
        db_table = u"configuracao\".\"tb_envio_regiao"
        verbose_name = u"Região da forma de envio"
        verbose_name_plural = u"Regiões das formas de envio"
        ordering = ["pais", "nome"]
        unique_together = (("pais", "nome", "forma_envio"),)

class EnvioFaixaCEP(models.Model):
    id = models.AutoField(db_column="envio_faixa_cep_id", primary_key=True)
    cep_inicio = models.IntegerField(db_column="envio_faixa_cep_cep_inicio", null=False)
    cep_fim = models.IntegerField(db_column="envio_faixa_cep_cep_fim", null=False)
    prazo_entrega = models.IntegerField(db_column="envio_faixa_cep_prazo_entrega", default=0, null=False)

    objects = MyObjects()

    regiao = models.ForeignKey(EnvioRegiao, db_column="envio_regiao_id", related_name="faixas_cep", on_delete=models.CASCADE)
    forma_envio = models.ForeignKey(Envio, db_column="envio_id", related_name="faixas_cep")
    forma_envio_configuracao = models.ForeignKey("repositories_configuracao.EnvioConfiguracao", db_column="envio_configuracao_id", related_name="faixas_cep")
    conta = models.ForeignKey("repositories_plataforma.Conta", related_name="formas_envios_faixas_cep")
    contrato = models.ForeignKey("repositories_plataforma.Contrato", related_name="formas_envios_faixas_cep")

    class Meta:
        app_label = "repositories_configuracao"
        db_table = u"configuracao\".\"tb_envio_faixa_cep"
        verbose_name = u"Faixa de CEP para região"
        verbose_name_plural = u"Faixas de CEPs para regiões"
        ordering = ["cep_inicio"]
        unique_together = (("cep_inicio", "cep_fim", "regiao"),)

class EnvioFaixaPeso(models.Model):
    id = models.AutoField(db_column="envio_faixa_peso_id", primary_key=True)
    peso_inicio = models.DecimalField(db_column="envio_faixa_peso_peso_inicio", max_digits=16, decimal_places=3, null=False)
    peso_fim = models.DecimalField(db_column="envio_faixa_peso_peso_fim", max_digits=16, decimal_places=3, null=False)
    valor = models.DecimalField(db_column="envio_faixa_peso_valor", max_digits=16, decimal_places=2, default=0, null=False)

    objects = MyObjects()

    regiao = models.ForeignKey(EnvioRegiao, db_column="envio_regiao_id", related_name="faixas_peso", on_delete=models.CASCADE)
    forma_envio = models.ForeignKey(Envio, db_column="envio_id", related_name="faixas_peso")
    forma_envio_configuracao = models.ForeignKey("repositories_configuracao.EnvioConfiguracao", db_column="envio_configuracao_id", related_name="faixas_peso")
    conta = models.ForeignKey("repositories_plataforma.Conta", related_name="formas_envios_faixas_peso")
    contrato = models.ForeignKey("repositories_plataforma.Contrato", related_name="formas_envios_faixas_peso")

    class Meta:
        app_label = "repositories_configuracao"
        db_table = u"configuracao\".\"tb_envio_faixa_peso"
        verbose_name = u"Faixa de peso para região"
        verbose_name_plural = u"Faixas de pesos para regiões"
        ordering = ["peso_inicio"]
        unique_together = (("peso_inicio", "peso_fim", "regiao"),)


