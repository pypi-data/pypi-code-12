# -*- coding: utf-8 -*-
from ..models import MyObjects
from django.db import models
import json
from jsonfield import JSONField


class CupomDesconto(models.Model):
    """Cupom de desconto."""
    TIPO_VALOR_FIXO = 'fixo'
    TIPO_PORCENTAGEM = 'porcentagem'
    TIPO_FRETE_GRATIS = 'frete_gratis'

    CHOICES_CUPOM_TIPOS = [
        (TIPO_VALOR_FIXO, u'Valor fixo'),
        (TIPO_PORCENTAGEM, u'Porcentagem'),
        (TIPO_FRETE_GRATIS, u'Frete grátis'),
    ]

    id = models.AutoField(db_column="cupom_desconto_id", primary_key=True)
    descricao = models.TextField(db_column="cupom_desconto_descricao")
    codigo = models.CharField(db_column="cupom_desconto_codigo", max_length=32)
    valor = models.DecimalField(db_column='cupom_desconto_valor', max_digits=16, decimal_places=2, null=True)
    tipo = models.CharField(db_column="cupom_desconto_tipo", max_length=32, choices=CHOICES_CUPOM_TIPOS)
    cumulativo = models.BooleanField(db_column="cupom_desconto_acumulativo", default=False)
    quantidade = models.IntegerField(db_column="cupom_desconto_quantidade")
    quantidade_por_cliente = models.IntegerField(db_column="cupom_desconto_quantidade_por_usuario", null=True)
    quantidade_usada = models.IntegerField(db_column="cupom_desconto_quantidade_utilizada", default=0)
    validade = models.DateTimeField(db_column="cupom_desconto_validade", null=True)
    valor_minimo = models.DecimalField(db_column='cupom_desconto_valor_minimo', max_digits=16, decimal_places=2, null=True)
    data_criacao = models.DateTimeField(db_column="cupom_desconto_data_criacao", auto_now_add=True)
    data_modificacao = models.DateTimeField(db_column="cupom_desconto_data_modificacao", auto_now=True)
    ativo = models.BooleanField(db_column="cupom_desconto_ativo", default=False)
    aplicar_no_total = models.BooleanField(db_column='cupom_desconto_aplicar_no_total', default=False, null=False)

    objects = MyObjects()

    conta = models.ForeignKey("repositories_plataforma.Conta", related_name='cupons')
    contrato = models.ForeignKey("repositories_plataforma.Contrato", related_name='cupons')

    class Meta:
        app_label = "repositories_marketing"
        db_table = u"marketing\".\"tb_cupom_desconto"
        verbose_name = u'Cupom de desconto'
        verbose_name_plural = u"Cupons de desconto"
        ordering = ['codigo']
        unique_together = (("conta", "codigo"),)

    def __unicode__(self):
        return self.codigo


class SEO(models.Model):
    """S.E.O."""
    id = models.AutoField(db_column="seo_id", primary_key=True)
    tabela = models.CharField(db_column="seo_tabela", max_length=64)
    linha_id = models.IntegerField(db_column="seo_linha_id")
    data_criacao = models.DateTimeField(db_column="seo_data_criacao", auto_now_add=True)
    data_modificacao = models.DateTimeField(db_column="seo_data_modificacao", auto_now=True)
    title = models.CharField(db_column="seo_title", max_length=255, null=True)
    keyword = models.CharField(db_column="seo_keyword", max_length=255, null=True)
    description = models.CharField(db_column="seo_description", max_length=255, null=True)
    robots = models.CharField(db_column="seo_robots", max_length=32, null=True)

    idioma = models.ForeignKey('repositories_public.Idioma', related_name="seos", default='pt-br')
    conta = models.ForeignKey("repositories_plataforma.Conta", related_name="seos")
    contrato = models.ForeignKey("repositories_plataforma.Contrato", related_name="seos")

    class Meta:
        app_label = "repositories_marketing"
        db_table = u"marketing\".\"tb_seo"


class FreteGratis(models.Model):
    """O Frete Grátis é uma forma de máscara as formas de envio existentes.

    Sempre que um pedido tem a possibilidade de Frete Grátis, o menor valor
    de envio assume o papel de Frete Grátis. O Frete Grátis sempre é baseado
    em faixas de CEP.

    O campo faixas é um campo JSON que tem como conteúdo uma lista de
    listas de faixas, onde cada lista interna é um início e fim de uma faixa.
    Por exemplo: `[[59150000, 59880999], [1000000, 1999999]]`
    """
    id = models.AutoField(db_column="frete_gratis_id", primary_key=True)
    nome = models.CharField(db_column="frete_gratis_nome", max_length=256, null=False)
    codigo = models.CharField(
        db_column="frete_gratis_codigo", max_length=256, null=False, db_index=True)
    ativo = models.BooleanField(db_column="frete_gratis_ativo", default=False, db_index=True)
    valor_minimo = models.DecimalField(
        db_column="frete_gratis_valor_minimo", max_digits=16, decimal_places=2,
        null=False, db_index=True)
    _faixas = models.TextField(db_column="frete_gratis_faixas", null=True, default=None)

    objects = MyObjects()

    conta = models.ForeignKey("repositories_plataforma.Conta", related_name="fretes_gratis")
    contrato = models.ForeignKey("repositories_plataforma.Contrato", related_name="fretes_gratis")

    class Meta:
        app_label = "repositories_marketing"
        db_table = u"marketing\".\"tb_frete_gratis"
        verbose_name = u"Frete grátis"
        verbose_name_plural = u"Fretes grátis"
        ordering = ["nome"]
        unique_together = (("codigo", "conta"),)

    def __unicode__(self):
        return self.nome

    def _set_faixas(self, faixas):
        try:
            self._faixas = json.dumps(faixas)
        except:
            self._faixas = None

    def _get_faixas(self):
        try:
            return json.loads(self._faixas)
        except:
            return self._faixas

    faixas = property(_get_faixas, _set_faixas)


class Tag(models.Model):

    LOCAL_PUBLICACAO = [
        ('cabecalho', u'Cabeçalho'),
        ('rodape', u'Rodapé'),
    ]

    id = models.AutoField(db_column='tag_id', primary_key=True)
    nome = models.CharField(db_column='tag_nome', max_length=32)
    url_imagem = models.CharField(db_column="tag_url_imagem", max_length=255, null=True)
    url_cadastro = models.CharField(db_column="tag_url_cadastro", max_length=255, null=True)
    local_publicacao = models.CharField(db_column="tag_local_publicacao", max_length=255, choices=LOCAL_PUBLICACAO)
    campos = JSONField(db_column='tag_campos_json')
    descricao = models.TextField(db_column='tag_descricao', null=True)
    chamada = models.TextField(db_column='tag_chamada', null=True)

    tag_global = models.TextField(db_column="tag_global", null=True, blank=True)
    index = models.TextField(db_column="tag_index", null=True, blank=True)
    catalogo = models.TextField(db_column="tag_catalogo", null=True, blank=True)
    produto = models.TextField(db_column="tag_produto", null=True, blank=True)
    carrinho = models.TextField(db_column="tag_carrinho", null=True, blank=True)
    pedido = models.TextField(db_column="tag_pedido", null=True, blank=True)
    pedido_pago = models.TextField(db_column="tag_pedido_pago", null=True, blank=True)

    data_criacao = models.DateTimeField(db_column="tag_data_criacao", auto_now_add=True)
    data_modificacao = models.DateTimeField(db_column="tag_data_modificacao", auto_now=True)

    objects = MyObjects()

    class Meta:
        app_label = "repositories_marketing"
        db_table = u"marketing\".\"tb_tag"
        verbose_name = u"Tag"
        verbose_name_plural = u"Tags"