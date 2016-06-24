# -*- coding: utf-8 -*-
from li_api_client.utils import ApiClientBase


class ApiCatalogo(ApiClientBase):
    NOME = "API_CATALOGO"
    AUTENTICA_APLICACAO = True
    # AUTENTICA_USUARIO = True

    def marcas(self, conta_id, **kwargs):
        path = 'loja/{}/catalogo/marcas/'.format(conta_id)
        return self.to_dict(path, "get", meta=True, **kwargs)

    def marca(self, conta_id, marca_id, **kwargs):
        path = 'loja/{}/catalogo/marcas/{}/'.format(conta_id, marca_id)
        return self.to_dict(path, "get", meta=True, **kwargs)

    def produtos(self, conta_id, **kwargs):
        path = 'loja/{}/catalogo/produtos/'.format(conta_id)
        return self.to_dict(path, "get", meta=True, **kwargs)

    def produto(self, conta_id, produto_id, **kwargs):
        path = 'loja/{}/catalogo/produtos/{}/'.format(conta_id, produto_id)
        return self.to_dict(path, "get", meta=True, **kwargs)

    def categorias(self, conta_id, **kwargs):
        path = 'loja/{}/catalogo/categorias/'.format(conta_id)
        return self.to_dict(path, "get", meta=True, **kwargs)

    def categoria(self, conta_id, categoria_id, **kwargs):
        path = 'loja/{}/catalogo/categorias/{}/'.format(conta_id, categoria_id)
        return self.to_dict(path, "get", meta=True, **kwargs)
