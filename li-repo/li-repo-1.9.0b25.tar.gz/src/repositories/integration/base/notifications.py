# -*- coding: utf-8 -*-
import os
from li_api_client.integration import ApiIntegration
from repositories.integration.models import (
    AccountIntegration, ModelIntegration, IntegrationHistory)


class BaseNotificationService(object):
    def __init__(
            self,
            instance,
            account,
            *args,
            **kwargs):
        super(BaseNotificationService, self).__init__(*args, **kwargs)
        self.instance = instance
        self.sandbox = os.environ.get('ENVIRONMENT') != 'production'
        self.account = account
        self.crud = '',
        self.integration_list = []
        self.model_dict = {}

    # Checar se os dados são válidos
    def validate_args(self):
        if not self.model:
            raise ValueError(u"É preciso definir o modelo usando nesta classe")
        elif self.model != self.instance._meta.model:
            raise ValueError(
                u"A instância enviada não é compativel com o modelo")

    # Se for sandbox, adicionar o produto as integracoes ativas
    def process_sandbox(self):
        active_integrations = AccountIntegration.objects.filter(active=True)
        for account_integration in active_integrations:
            if not ModelIntegration.objects.filter(
                account=self.account,
                model_selected=self.model._meta.model_name,
                model_selected_id=self.instance.id,
                integration=account_integration.integration
            ).exists():
                ModelIntegration.objects.create(
                    account=self.account,
                    model_selected=self.model,
                    model_selected_id=self.instance.id,
                    integration=account_integration.integration
                )

    def model_select_is_valid(self, obj):
        """
                Sobrescrever este método para validações
                específicas do modelo
        """
        return True

    # Listar conectores válidos para modelo/loja enviados
    def get_connectors(self):
        self.integration_list = [
            model_for_integration
            for model_for_integration in ModelIntegration.objects.filter(
                account=self.account,
                model_selected=self.model._meta.model_name,
                model_selected_id=self.instance.id,
            )
            if model_for_integration.active() and
            self.model_select_is_valid(model_for_integration.get_object())
        ]

        return self.integration_list

    # Definir Create, Update, Delete (Removed) ou Delete (Model)
    def set_crud(self, crud=None):
        self.crud = crud

    # Gerar o dicionario
    def model_to_dict(self):
        """
        Sobrescrever esta classe passando a
        classe serializadora correspondente
        """
        raise NotImplementedError("Implementar serialização")

    # Enviar notificação
    def send_notification(self):
        # Uma mensagem para todos os conectores
        self.model_dict['connector_list'] = [
            model_integration.integration.slug
            for model_integration in self.integration_list
        ]
        for model_integration in self.integration_list:
            integration_history = IntegrationHistory.objects.create(
                account=self.account,
                model_selected=self.instance._meta.model_name,
                model_selected_id=self.instance.pk,
                integration=model_integration.integration
            )
            return self.use_internal_api(history_id=integration_history.id)

    def use_internal_api(self, history_id):
        # Criar a notificação via API interna
        return ApiIntegration().send_notification(
            crud=self.crud,
            history_id=history_id,
            model_dict=self.model_dict
        )

    # Processar Notificacao
    def notify(self, crud=None):
        result = {}
        self.validate_args()
        if self.sandbox:
            self.process_sandbox()
        self.get_connectors()
        if self.integration_list:
            if not self.crud:
                self.set_crud(crud)
            self.model_to_dict()
            result = self.send_notification()
        return result
