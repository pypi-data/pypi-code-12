# -*- coding: utf-8 -*-
from li_api_client.utils import ApiClientBase


class ApiPlataforma(ApiClientBase):
    NOME = "API_PLATAFORMA"
    AUTENTICA_APLICACAO = True

    def verificacao_alterar(self, conta_id, verificada):
        path = '/contas/{}/verificada/{}/'.format(conta_id, verificada)
        return self.to_dict(path, method="put", meta=True)

    def situacao_alterar(self, conta_id, situacao):
        path = '/contas/{}/situacao/{}/'.format(conta_id, situacao)
        return self.to_dict(path, method="put", meta=True)

    def recurso_alterar(self, conta_id, recurso):
        path = '/contas/{}/habilitar/{}/'.format(conta_id, recurso)
        return self.to_dict(path, method="put", meta=True)

    def contas(self, **kwargs):
        path = '/contas/'
        return self.to_dict(path, method="get", meta=True, **kwargs)

    def contratos(self, **kwargs):
        path = '/contratos/'
        return self.to_dict(path, method="get", meta=True, **kwargs)

    def contrato(self, contrato_id):
        path = '/contrato/{}/'.format(contrato_id)
        return self.to_dict(path, method="get", meta=True)

    def conta_reindexar(self, conta_id):
        path = '/contas/{}/reindexar/'.format(conta_id)
        return self.to_dict(path, method="post", meta=True)

    # Refazer
    def reenviar_email_aprovacao(self, conta_id):
        path = '/doing/certificado.reenviar_email_aprovacao/delay'
        return self._post(path, conta_id=conta_id)
