# -*- coding: utf-8 -*-
from django.db import models
from repositories import custom_models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify
from django.utils import timezone


class Integracao(models.Model):

    id = custom_models.BigAutoField(
        db_column='integracao_id', primary_key=True)
    nome = models.CharField(
        db_column='integracao_nome',
        max_length=255,
        verbose_name='nome')
    slug = models.SlugField(
        db_column='integracao_slug',
        unique=True,
        editable=False, null=True, blank=True)
    sandbox_nome = models.CharField(
        db_column='integracao_integracao_sandbox_nome',
        max_length=255,
        verbose_name='nome usuario teste',
        null=True, blank=True)
    sandbox_secret = models.CharField(
        db_column='integracao_sandbox_secret',
        max_length=255,
        verbose_name='senha usuario teste',
        null=True, blank=True)
    sandbox_token = models.CharField(
        db_column='integracao_sandbox_token',
        max_length=255,
        verbose_name='token teste',
        null=True, blank=True)
    sandbox_url = models.URLField(
        db_column='integracao_sandbox_url',
        verbose_name='URL do sandbox',
        null=True, blank=True
    )

    class Meta:
        db_table = u"integration\".\"tb_integracao"
        verbose_name = u'Integracao'
        verbose_name_plural = u'Integracoes'

    def __unicode__(self):
        return "{}".format(self.nome)


class ContaIntegracao(models.Model):

    id = custom_models.BigAutoField(
        db_column='conta_integracao_id',
        primary_key=True)
    conta = models.ForeignKey(
        'plataforma.Conta',
        related_name='conta_conta_integracao',
        on_delete=models.CASCADE)
    contrato = models.ForeignKey(
        'plataforma.Contrato',
        related_name="contrato_conta_integracao")
    integracao = models.ForeignKey(
        'integration.Integracao',
        related_name='integracao_conta_integracao',
        on_delete=models.CASCADE
    )
    ativo = models.BooleanField(
        db_column='conta_integracao_ativo',
        default=False)
    nome_usuario = models.CharField(
        db_column='conta_integracao_sandbox_nome',
        max_length=255,
        verbose_name='nome usuario', null=True, blank=True)
    senha_usuario = models.CharField(
        db_column='conta_integracao_sandbox_secret',
        max_length=255,
        verbose_name='conta_integracao_senha usuario',
        null=True, blank=True)
    token = models.CharField(
        db_column='conta_integracao_sandbox_token',
        max_length=255,
        verbose_name='token',
        null=True, blank=True)
    url = models.URLField(
        db_column='conta_integracao_url',
        verbose_name='URL de acesso',
        null=True, blank=True
    )

    class Meta:
        db_table = u"integration\".\"tb_conta_integracao"
        verbose_name = u'Conta Integracao'
        verbose_name_plural = u'Conta Integracoes'
        unique_together = ('conta', 'integracao')

    def __unicode__(self):
        return "{}/{}".format(self.conta, self.integracao)


class ProdutoIntegracao(models.Model):

    id = custom_models.BigAutoField(
        db_column='produto_integracao_id',
        primary_key=True)
    conta = models.ForeignKey(
        'plataforma.Conta',
        related_name='conta_produto_integracao',
        on_delete=models.CASCADE)
    produto = models.ForeignKey(
        'catalogo.Produto',
        related_name='produto_produto_integracao',
        on_delete=models.CASCADE)
    integracao = models.ForeignKey(
        'integration.Integracao',
        related_name='integracao_produto_integracao',
        on_delete=models.CASCADE
    )
    data_inicio = models.DateTimeField(
        db_column='produto_integracao_data_inicio', null=True, blank=True)
    data_fim = models.DateTimeField(
        db_column='produto_integracao_data_fim', null=True, blank=True)
    bloquear = models.BooleanField(
        db_column='produto_integracao_bloquear',
        default=False)
    removido = models.BooleanField(
        db_column='produto_integracao_removido',
        default=False)

    def ativo(self):
        result = True
        if not ContaIntegracao.objects.filter(
                conta=self.conta,
                integracao=self.integracao,
                ativo=True
        ).exists():
            result = False
        if not self.produto.ativo \
                or self.bloquear or self.removido:
            result = False
        if self.data_inicio and self.data_inicio > timezone.now():
            result = False
        if self.data_fim and self.data_fim < timezone.now():
            result = False

        return result

    class Meta:
        db_table = u"integration\".\"tb_produto_integracao"
        verbose_name = u'Produto Integracao'
        verbose_name_plural = u'Produto Integracoes'
        unique_together = ('conta', 'integracao', 'produto')

    def __unicode__(self):
        return "{}/{}".format(self.produto.sku, self.integracao)


@receiver(post_save, sender=Integracao)
def post_save_integracao(self, sender, instance, created, *args, **kwargs):
    if not instance.slug:
        instance.slug = slugify(instance.name[:30])
        instance.save()
