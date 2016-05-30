# -*- coding: utf-8 -*-
from li_api_client.utils import ApiClientBase


class ApiPedido(ApiClientBase):
    NOME = "API_PEDIDO"
    AUTENTICA_APLICACAO = True

    def alterar_situacao(self, loja_id, pedido_numero, situacao_id, por, **kwargs):
        path = '/loja/{}/order/{}/status/{}/{}'.format(loja_id, pedido_numero, situacao_id, por)
        return self.to_dict(path, method="put", meta=True, **kwargs)
