# -*- coding: utf-8 -*-
from li_api_client.utils import ApiClientBase


class ApiMarketplace(ApiClientBase):
    NOME = "API_MARKETPLACE"
    AUTENTICA_APLICACAO = True
    # AUTENTICA_USUARIO = True

    def mercadolivre_url_associar(self, conta_id):
        path = '/mercadolivre/conta/{}/associar/'.format(conta_id)
        return self.to_dict(path, "get", meta=True)

    def mercadolivre_associar(self, conta_id, code):
        path = '/mercadolivre/conta/{}/associar/?code={}'.format(conta_id, code)
        return self.to_dict(path, "post", meta=True)

    def mercadolivre_desassociar(self, conta_id):
        path = '/mercadolivre/conta/{}/associar/'.format(conta_id)
        return self.to_dict(path, "delete", meta=True)

    def mercadolivre_anuncio_editar(self, conta_id, item_id, dados_anuncio):
        path = '/mercadolivre/conta/{}/anuncio/{}/'.format(conta_id, item_id)
        return self.to_dict(path, "put", meta=True, dados_anuncio=dados_anuncio)

    def mercadolivre_anuncio_criar(self, conta_id, produto_id, dados_anuncio):
        path = '/mercadolivre/conta/{}/anuncio/'.format(conta_id)
        return self.to_dict(path, "post", meta=True, dados_anuncio=dados_anuncio, produto_id=produto_id)

    def mercadolivre_anuncio_remover(self, conta_id, item_id):
        path = '/mercadolivre/conta/{}/anuncio/{}/'.format(conta_id, item_id)
        return self.to_dict(path, "delete", meta=True)

    def mercadolivre_anuncio_relistar(self, conta_id, item_id):
        path = '/mercadolivre/conta/{}/anuncio/{}/relistar/'.format(conta_id, item_id)
        return self.to_dict(path, "post", meta=True)
