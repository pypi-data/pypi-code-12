# -*- coding: utf-8 -*-
from urllib import urlencode
from li_api_client.utils import ApiClientBase


class ApiPagador(ApiClientBase):
    NOME = "API_PAGADOR"
    AUTENTICA_APLICACAO = True

    def formas_de_pagamento(self, conta_id, plano_indice=None, soh_habilitados=False):
        path = '/meios-pagamento/?conta_id={}&soh_habilitados={}'.format(conta_id, soh_habilitados)
        if plano_indice:
            path = '/formas-pagamento/?conta_id={}&plano_indice={}&soh_habilitados={}'.format(conta_id, plano_indice, soh_habilitados)
        return self.to_dict(path)

    def meios_de_pagamento_da_loja(self, loja_id):
        path = '/loja/{}/meios-pagamento'.format(loja_id)
        return self.to_dict(path)

    def meios_de_pagamento_em_uso_na_loja(self, loja_id, plano_indice, valor_pagamento, loja_usa_https=False, ttl=0):
        path = '/loja/{}/meios-pagamento/em-uso/{}?valor_pagamento={}&usa_https={}&ttl={}'.format(loja_id, plano_indice, valor_pagamento, '1' if loja_usa_https else '0', ttl)
        return self.to_dict(path)

    def configuracao_de_forma_de_pagamento(self, loja_id, codigo_pagamento):
        path = '/loja/{}/meio-pagamento/{}/configurar'.format(loja_id, codigo_pagamento)
        return self.to_dict(path)

    def parcelas_disponiveis_na_loja(self, loja_id, codigo_pagamento, valor_pagamento):
        path = '/loja/{}/meio-pagamento/{}/parcelar/{}'.format(loja_id, codigo_pagamento, valor_pagamento)
        return self.to_dict(path)

    def simular_parcelas_disponiveis_na_loja(self, loja_id, codigo_pagamento, valor_pagamento, maximo_parcelas, parcelas_sem_juros):
        path = '/loja/{}/meio-pagamento/{}/simular-parcelas/{}/{}/{}'.format(loja_id, codigo_pagamento, valor_pagamento, maximo_parcelas, parcelas_sem_juros)
        return self.to_dict(path)

    def salvar_configuracao_de_forma_de_pagamento(self, loja_id, codigo_pagamento, dados):
        path = '/loja/{}/meio-pagamento/{}/configurar'.format(loja_id, codigo_pagamento)
        return self._post(path, **dados)

    def ordenar_formas_pagamento(self, loja_id, ordem):
        path = '/loja/{}/meios-pagamento'.format(loja_id)
        return self._put(path, **{'ordenacao': ordem})

    def instalar_aplicacao(self, loja_id, codigo_pagamento, next_url, dados=None):
        path = '/loja/{}/meio-pagamento/{}/instalar'.format(loja_id, codigo_pagamento)
        if not dados:
            dados = {}
        dados['fase_atual'] = '1'
        dados['next_url'] = next_url
        return self.to_dict(path, method='put', **dados)

    def desinstalar_aplicacao(self, loja_id, codigo_pagamento):
        path = '/loja/{}/meio-pagamento/{}/instalar'.format(loja_id, codigo_pagamento)
        return self.to_dict(path, method='delete')

    def enviar_pagamento(self, loja_id, codigo_pagamento, pedido_numero, plano_indice, dados):
        path = '/loja/{}/meio-pagamento/{}/enviar/{}/{}'.format(loja_id, codigo_pagamento, pedido_numero, plano_indice)
        return self.to_dict(path, method='post', **dados)
