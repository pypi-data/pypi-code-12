# -*- coding: utf-8 -*-
import os
import json
from li_api_client.integration import ApiIntegration
from repositories.integration.models import (
    AccountIntegration, ModelIntegration, IntegrationHistory)


class BaseNotificationService(object):
    def __init__(
            self,
            instance=None,
            delete_id=None,
            account_id=None,
            *args,
            **kwargs):
        super(BaseNotificationService, self).__init__(*args, **kwargs)
        self.instance = instance
        self.sandbox = os.environ.get('ENVIRONMENT') != 'production'
        if hasattr(instance, 'conta'):
            self.account_id = instance.conta.id
        else:
            self.account_id = account_id
        self.crud = '',
        self.integration_list = []
        self.model_dict = {}
        self.instance_id = delete_id if delete_id else instance.id
        self.delete = True if delete_id else False
        self.instance_model = self.model._meta.model_name \
            if delete_id else self.instance._meta.model_name

    # Checar se os dados são válidos
    def validate_args(self):
        if not self.serializer:
            raise ValueError(
                u"É preciso definir o serializador usando nesta classe")
        if not self.model:
            raise ValueError(u"É preciso definir o modelo usando nesta classe")
        if not self.delete:
            if self.model != self.instance._meta.model:
                raise ValueError(
                    u"A instância enviada não é compativel com o modelo")
        if not self.account_id:
            raise ValueError("Informe a conta")

    # Se for sandbox, adicionar o produto as integracoes ativas
    def process_sandbox(self):
        print("GRAVANDO SANDBOX PARA ID {}".format(self.instance_id))
        active_integrations = AccountIntegration.objects.filter(active=True)
        for account_integration in active_integrations:
            new_model_integration, \
                created = ModelIntegration.objects.get_or_create(
                    account_id=self.account_id,
                    model_selected=self.instance_model,
                    model_selected_id=self.instance_id,
                    integration=account_integration.integration
                )
            if created:
                print(
                    "GRAVOU SANDBOX {}".format(
                        account_integration.integration))
            else:
                print("NAO GRAVOU")

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
                account_id=self.account_id,
                model_selected=self.instance_model,
                model_selected_id=self.instance_id,
            )
            if model_for_integration.active() and (
                (self.delete and model_for_integration.external_id) or
                self.model_select_is_valid(
                    model_for_integration.get_object(
                        self.model),
                    model_for_integration.integration.slug)
            )
        ]
        return self.integration_list

    # Definir Create, Update, Delete (Removed) ou Delete (Model)
    def set_crud(self, crud=None):
        self.crud = crud

    # Gerar o dicionario
    def model_to_dict(self):
        if self.delete:
            self.model_dict = self.serializer(
                delete_id=self.instance_id).serialize()
        else:
            self.model_dict = self.serializer(
                self.instance).serialize()

    # Enviar notificação
    def send_notification(self):
        # Uma mensagem para todos os conectores
        self.model_dict['connector_list'] = [
            model_integration.integration.slug
            for model_integration in self.integration_list
        ]
        for model_integration in self.integration_list:
            integration_history, \
                created = IntegrationHistory.objects.get_or_create(
                    account_id=self.account_id,
                    model_selected=self.instance_model,
                    model_selected_id=self.instance_id,
                    integration=model_integration.integration,
                    message_body=json.dumps(self.model_dict),
                    status="WAIT"
                )
            print("CRIOU HISTORICO: {}".format(integration_history.id))

    def use_internal_api(self):
        history_list = IntegrationHistory.objects.filter(
            account_id=self.account_id,
            status="WAIT"
        )
        for history in history_list:
            # Criar a notificação via API interna
            ApiIntegration().send_notification(
                crud=self.crud,
                history_id=history.id,
                model_dict=json.dumps(self.model_dict)
            )

    # Processar Notificacao
    def notify(self, crud):
        print("VALIDANDO DADOS")
        self.validate_args()
        if self.sandbox:
            print("PROCESSANDO SANDBOX")
            self.process_sandbox()
        print("PEGANDO CONECTORES")
        self.get_connectors()
        if self.integration_list:
            print("DEFININDO CRUD")
            self.set_crud(crud)
            print("TRANSFORMANDO MODELO {} EM DICT".format(
                self.instance_model.upper()
            ))
            self.model_to_dict()
            print("ENVIANDO NOTIFICACAO")
            self.send_notification()
            print("USANDO API INTERNA")
            self.use_internal_api()
