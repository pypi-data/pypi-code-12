# -*- coding: utf-8 -*-
from datetime import timedelta
from django.db import models
from repositories import custom_models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.text import slugify
from django.utils import timezone
from repositories.catalogo.models import (
    Produto, ProdutoCategoria, Marca, ProdutoEstoque)

MODELS_FOR_INTEGRATION = [
    Marca, Produto, ProdutoCategoria, ProdutoEstoque
]

MODEL_LIST = [
    (model._meta.model_name, model)
    for model in MODELS_FOR_INTEGRATION
]

INTEGRATION_STATUS = [
    (u'WAIT', u'aguardando envio para {}'),
    (u'RETRY', u'aguardando envio para {}'),
    (u'SUCCESS', u'integrado com sucesso para {}'),
    (u'FAIL', u'{} não aceitou os dados'),
    (u'ERROR', u'Ocorreu um erro no envio'),
]


class Integration(models.Model):

    id = custom_models.BigAutoField(
        db_column='integration_id', primary_key=True)
    name = models.CharField(
        db_column='integration_name',
        max_length=255,
        verbose_name='nome')
    slug = models.SlugField(
        db_column='integration_slug',
        unique=True,
        editable=False, null=True, blank=True)
    sandbox_name = models.CharField(
        db_column='integration_sandbox_name',
        max_length=255,
        verbose_name='name usuario teste',
        null=True, blank=True)
    sandbox_secret = models.CharField(
        db_column='integration_sandbox_secret',
        max_length=255,
        verbose_name='senha usuario teste',
        null=True, blank=True)
    sandbox_token = models.CharField(
        db_column='integration_sandbox_token',
        max_length=255,
        verbose_name='token teste',
        null=True, blank=True)
    sandbox_url = models.URLField(
        db_column='integration_sandbox_url',
        verbose_name='URL do sandbox',
        null=True, blank=True
    )

    class Meta:
        db_table = u"integration\".\"tb_integration"
        verbose_name = u'integration'
        verbose_name_plural = u'Integracoes'

    def __unicode__(self):
        return "{}".format(self.name)


class AccountIntegration(models.Model):

    id = custom_models.BigAutoField(
        db_column='account_integration_id',
        primary_key=True)
    account = models.ForeignKey(
        'plataforma.Conta',
        related_name='account_integration',
        on_delete=models.CASCADE)
    contract = models.ForeignKey(
        'plataforma.Contrato',
        related_name="contract_account_integration")
    integration = models.ForeignKey(
        'integration.Integration',
        related_name='integration_account_integration',
        on_delete=models.CASCADE
    )
    active = models.BooleanField(
        db_column='account_integration_active',
        default=False)
    client_id = models.CharField(
        db_column='account_integration_client_id',
        max_length=255,
        null=True, blank=True)
    secret_id = models.CharField(
        db_column='account_integration_secret_id',
        max_length=255,
        null=True, blank=True)
    token = models.CharField(
        db_column='account_integration_token',
        max_length=255,
        null=True, blank=True)
    url = models.URLField(
        db_column='account_integration_url',
        verbose_name='URL de acesso',
        null=True, blank=True
    )

    class Meta:
        db_table = u"integration\".\"tb_account_integration"
        verbose_name = u'Account Integration'
        verbose_name_plural = u'Account Integrations'
        unique_together = ('account', 'integration')

    def __unicode__(self):
        return "{}/{}".format(self.account, self.integration)


class ModelIntegration(models.Model):

    id = custom_models.BigAutoField(
        db_column='model_integration_id',
        primary_key=True)
    account = models.ForeignKey(
        'plataforma.Conta',
        related_name='account_model_integration',
        on_delete=models.CASCADE)
    model_selected = models.CharField(
        db_column='model_integration_model_selected',
        choices=MODEL_LIST,
        max_length=50
    )
    model_selected_id = models.IntegerField(
        db_column='model_integration_model_selected_id',
    )
    integration = models.ForeignKey(
        'integration.Integration',
        related_name='integration_model_integration',
        on_delete=models.CASCADE
    )
    start_date = models.DateTimeField(
        db_column='model_integration_start_date', null=True, blank=True)
    end_date = models.DateTimeField(
        db_column='model_integration_end_date', null=True, blank=True)
    block_integration = models.BooleanField(
        db_column='model_integration_block_integration',
        default=False)
    removed = models.BooleanField(
        db_column='model_integration_removed',
        default=False)

    class Meta:
        db_table = u"integration\".\"tb_model_integration"
        verbose_name = u'Model Integration'
        verbose_name_plural = u'Model Integrations'
        unique_together = (
            'model_selected',
            'model_selected_id',
            'integration')

    def __unicode__(self):
        return "{}/{}".format(self.product.sku, self.integration)

    def active(self):
        result = True
        if not AccountIntegration.objects.filter(
                account=self.account,
                integration=self.integration,
                active=True
        ).exists():
            result = False
        if self.block_integration or self.removed:
            result = False
        if not self.start_date:
            result = False
        if self.start_date and self.start_date > timezone.now():
            result = False
        if self.end_date and self.end_date < timezone.now():
            result = False

        return result

    def get_object(self):
        selected_model = dict(INTEGRATION_STATUS).get(self.model_selected)
        default_manager = selected_model.Meta.model._default_manager
        return default_manager.get(pk=self.model_selected_id)


class IntegrationHistory(models.Model):

    id = custom_models.BigAutoField(
        db_column='product_integration_history_id',
        primary_key=True)
    account = models.ForeignKey(
        'plataforma.Conta',
        related_name='account_product_integration_history',
        on_delete=models.CASCADE)
    model_selected = models.CharField(
        db_column='account_integration_model_selected',
        choices=MODEL_LIST,
        max_length=50
    )
    model_selected_id = models.IntegerField(
        db_column='account_integration_model_selected_id',
    )
    integration = models.ForeignKey(
        'integration.Integration',
        related_name='integration_product_integration_history',
        on_delete=models.CASCADE
    )
    start_date = models.DateTimeField(
        db_column='product_integration_history_start_date',
        auto_now_add=True
    )
    end_date = models.DateTimeField(
        db_column='product_integration_history_end_date',
        null=True,
        blank=True)
    status = models.CharField(
        db_column='account_integration_status',
        choices=INTEGRATION_STATUS,
        default="WAIT",
        max_length=35
    )
    message_body = models.TextField(
        db_column='account_integration_message_body',
        null=True,
        blank=True)
    duration = models.DurationField(
        db_column='account_integration_duration',
        null=True,
        blank=True)

    class Meta:
        db_table = u"integration\".\"tb_product_integration_history"
        verbose_name = u'Product Integration History'
        verbose_name_plural = u'Product Integrations History'

    def __unicode__(self):
        return "{}/{} {}".format(self.account,
                                 self.integration,
                                 self.start_date.isoformat())

    def get_object(self):
        selected_model = dict(INTEGRATION_STATUS).get(self.model_selected)
        default_manager = selected_model.Meta.model._default_manager
        return default_manager.get(pk=self.model_selected_id)


@receiver(post_save, sender=Integration)
def post_save_integration(self, sender, instance, created, *args, **kwargs):
    if not instance.slug:
        instance.slug = slugify(instance.name[:30])
        instance.save()


@receiver(post_save, sender=IntegrationHistory)
def post_save_integrationhistory(
        self,
        sender,
        instance,
        created,
        *args,
        **kwargs):
    if not instance.duration and instance.end_date:
        instance.duration = timedelta(self.start_date - self.end_date)
        instance.save()
