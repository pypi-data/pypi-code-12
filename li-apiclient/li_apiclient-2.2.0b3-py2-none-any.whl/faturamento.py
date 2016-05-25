# -*- coding: utf-8 -*-
from li_api_client.utils import ApiClientBase


class ApiFaturamento(ApiClientBase):
    NOME = "API_FATURAMENTO"
    AUTENTICA_APLICACAO = True

    def colecoes(self):
        path = '/colecoes/'
        return self.to_dict(path, "get", meta=True)

    def colecao(self, colecao_id):
        path = '/colecoes/{}'.format(colecao_id)
        return self.to_dict(path, "get", meta=True)

    def planos(self, colecao_id):
        path = '/colecoes/{}/planos/'.format(colecao_id)
        return self.to_dict(path, "get", meta=True)

    def plano(self, colecao_id, plano_id):
        path = '/colecoes/{}/planos/{}/'.format(colecao_id, plano_id)
        return self.to_dict(path, method="get", meta=True)

    def plano_assinaturas(self, conta_id):
        path = '/contas/{}/plano/assinaturas/'.format(conta_id)
        return self.to_dict(path, method="get", meta=True)

    def plano_assinatura(self, conta_id, assinatura_id):
        path = '/contas/{}/plano/assinaturas/{}/'.format(conta_id, assinatura_id)
        return self.to_dict(path, method="get", meta=True)

    def faturas(self, **kwargs):
        path = '/faturas/'
        return self.to_dict(path, method="get", meta=True, **kwargs)

    def fatura(self, fatura_id, **kwargs):
        path = '/faturas/{}/'.format(fatura_id)
        return self.to_dict(path, method="get", meta=True, **kwargs)

    def banners(self, **kwargs):
        path = '/banners/'
        return self.to_dict(path, method="get", meta=True, **kwargs)

    def banner(self, banner_id, **kwargs):
        path = '/banners/{}/'.format(banner_id)
        return self.to_dict(path, method="get", meta=True, **kwargs)

    def temas(self, **kwargs):
        path = '/temas/'
        return self.to_dict(path, method="get", meta=True, **kwargs)

    def tema(self, tema_id, **kwargs):
        path = '/temas/{}/'.format(tema_id)
        return self.to_dict(path, method="get", meta=True, **kwargs)

    def certificados(self, **kwargs):
        path = '/certificados/'
        return self.to_dict(path, method="get", meta=True, **kwargs)

    def certificado(self, certificado_id, **kwargs):
        path = '/certificados/{}/'.format(certificado_id)
        return self.to_dict(path, method="get", meta=True, **kwargs)

    def loja_faturas(self, conta_id, **kwargs):
        path = '/contas/{}/faturas/'.format(conta_id)
        return self.to_dict(path, method="get", meta=True, **kwargs)

    def loja_fatura(self, conta_id, fatura_id):
        path = '/contas/{}/faturas/{}/'.format(conta_id, fatura_id)
        return self.to_dict(path, method="get", meta=True)

    def loja_fatura_cancelar(self, conta_id, fatura_id):
        path = '/contas/{}/faturas/{}/cancelar/'.format(conta_id, fatura_id)
        return self.to_dict(path, method="put", meta=True)

    def certificado_faturas(self, conta_id, **kwargs):
        path = '/contas/{}/certificado/faturas/'.format(conta_id)
        return self.to_dict(path, method="get", meta=True, **kwargs)

    def tema_faturas(self, conta_id, **kwargs):
        path = '/contas/{}/tema/faturas/'.format(conta_id)
        return self.to_dict(path, method="get", meta=True, **kwargs)

    def banner_faturas(self, conta_id, **kwargs):
        path = '/contas/{}/banner/faturas/'.format(conta_id)
        return self.to_dict(path, method="get", meta=True, **kwargs)

    def dados_cobranca_consultar(self, conta_id, **kwargs):
        path = '/contas/{}/dados_cobranca/'.format(conta_id)
        return self.to_dict(path, method="get", meta=True, **kwargs)

    def dados_cobranca_editar(self, conta_id, **kwargs):
        path = '/contas/{}/dados_cobranca/'.format(conta_id)
        return self.to_dict(path, method="put", meta=True, **kwargs)

    def dados_cobranca_cartao_consultar(self, conta_id):
        path = '/contas/{}/dados_cobranca/cartao/'.format(conta_id)
        return self.to_dict(path, method="get", meta=True)

    def dados_cobranca_cartao_editar(self, conta_id, **kwargs):
        path = '/contas/{}/dados_cobranca/cartao/'.format(conta_id)
        return self.to_dict(path, method="put", meta=True, **kwargs)

    def plano_vigente(self, conta_id, **kwargs):
        path = '/contas/{}/plano/vigente/'.format(conta_id)
        return self.to_dict(path, method="get", meta=True, **kwargs)

    def plano_pago_vigente(self, conta_id):
        path = '/contas/{}/plano/pago_vigente/'.format(conta_id)
        return self.to_dict(path, method="get", meta=True)

    def simular_proximo_ciclo(self, conta_id, plano_id):
        path = '/contas/{}/planos/{}/simular_proximo_ciclo/'.format(conta_id, plano_id)
        return self.to_dict(path, method="get", meta=True)

    def assinar(self, conta_id, plano_id, method="post"):
        path = '/contas/{}/planos/{}/assinar/'.format(conta_id, plano_id)
        return self.to_dict(path, method=method, meta=True)

    def comprar_certificado(self, conta_id, certificado_id):
        path = '/contas/{}/certificados/{}/comprar/'.format(conta_id, certificado_id)
        return self.to_dict(path, method="post", meta=True)

    def comprar_tema(self, conta_id, tema_id):
        path = '/contas/{}/temas/{}/comprar/'.format(conta_id, tema_id)
        return self.to_dict(path, method="post", meta=True)

    def comprar_banner(self, conta_id, banner_id):
        path = '/contas/{}/banners/{}/comprar/'.format(conta_id, banner_id)
        return self.to_dict(path, method="post", meta=True)

    def fatura_enviar_lancamento(self, fatura_id, **kwargs):
        path = '/faturas/{}/enviar_lancamento/'.format(fatura_id)
        return self.to_dict(path, method="post", meta=True, **kwargs)

    def fatura_quitar_lancamento(self, fatura_id, **kwargs):
        path = '/faturas/{}/quitar_lancamento/'.format(fatura_id)
        return self.to_dict(path, method="post", meta=True, **kwargs)

    def conta_consumo_reduzir_visitas(self, conta_id, porcento, **kwargs):
        path = '/contas/{}/consumo/reduzir/{}/porcento/'.format(conta_id, porcento)
        return self.to_dict(path, method="put", meta=True, **kwargs)

    def tarifa_enviar(self, id, **kwargs):
        path = '/tarifa/{}/enviar/'.format(id)
        return self.to_dict(path, method="post", meta=True, **kwargs)