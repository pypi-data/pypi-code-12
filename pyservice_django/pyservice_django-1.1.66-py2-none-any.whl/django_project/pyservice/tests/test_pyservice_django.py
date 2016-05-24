# -*- coding: utf-8 -*-
import datetime
import pytest
from django.test.client import RequestFactory

from pyservice.models import ClassA
from pyservice_django import pyservice_django
from pyservice_django.pyservice_django import post, config_classes, toObj, normalize_objects


def test_POST():
    url = 'http://service-cep-dot-sigeflex-erp.appspot.com/consulta_cidade'
    params = ["Moss"]
    assert post(url, params) != None


def test_post_exception():
    url = 'http://www.akdckdjdmd.com'
    params = ["Moss"]
    with pytest.raises(Exception):
        post(url, params) != None


def test_config_classes__i18n():
    class Teste():
        def teste(self):
            return self.i18n('USUARIO_JA_ATIVADO', ['Jose'])

        def teste2(self):
            return self.i18n('USUARIO_REGISTRO_TITULO')

    config_classes([Teste])
    teste = Teste()
    mensagem = teste.i18n('USUARIO_JA_ATIVADO', ['Jose'])
    assert mensagem == u'O usuario Jose já está registrado e ativado, você já pode utilizar o sistema!'

    mensagem = teste.teste()
    assert mensagem == u'O usuario Jose já está registrado e ativado, você já pode utilizar o sistema!'

    mensagem = teste.teste2()
    assert mensagem == u'Confirmação de registro'


def test_send_email():
    pass


def test_process_request_exception():
    factory = RequestFactory()

    def teste_exception1():
        a = {}
        a = a['teste']

    def teste_exception_raise():
        raise Exception('PARAM1', 'PARAM2')

    request = factory.post('/teste/teste1', None)
    pyservice_django.add_route('/teste/teste1', teste_exception1)
    result = pyservice_django.processa_django_request(request)

    result = result.content
    result = toObj(result)
    assert result['result'] == 'ERRO'
    assert result['data']['message'] == 'teste'
    assert result['data']['code'] == 'NOT_EXPECTED'

    request = factory.post('/teste/teste2', None)
    pyservice_django.add_route('/teste/teste2', teste_exception_raise)
    result = pyservice_django.processa_django_request(request)

    result = result.content
    result = toObj(result)
    assert result['result'] == 'ERRO'
    assert result['data']['code'] == 'PARAM1'
    assert result['data']['message'] == 'PARAM2'


def test_process_request():
    factory = RequestFactory()
    pyservice_django.service_name = 'myservice'
    pyservice_django.service_description = 'descriptions'
    pyservice_django.Version = '1.0'

    # Test with root mapping
    request = factory.post('/', None)
    result = pyservice_django.processa_django_request(request)
    result = result.content
    result = toObj(result)
    assert result['Service Name'] == 'myservice'
    assert result['Description'] == 'descriptions'
    assert result['Version'] == '1.0'

    # Servico nao encontrado:
    request = factory.post('/teste', None)
    result = pyservice_django.processa_django_request(request)
    result = result.content
    result = toObj(result)
    assert result['data'] == 'Servico nao encontrado : /{0}'.format('teste')

    # Servico
    def test():
        return 'Ola Rodrigo'

    pyservice_django.add_route('/teste', test)
    request = factory.post('/teste', None)
    result = pyservice_django.processa_django_request(request)
    result = result.content
    result = toObj(result)
    assert result['data'] == 'Ola Rodrigo'


def test_normalize_obj():
    obj = {'empresa_id': 1, 'nome': u'RODRIGO RODRIGUES', 'created_at': datetime.datetime(2016, 5, 24, 3, 7, 21, 560012), 'updated_at': datetime.datetime(2016, 5, 24, 3, 7, 21,
                                                                                                                                                          560020), 'usuario_id': 1, 'codigo': 4, 'id': 5}
    obj = normalize_objects(obj)
    assert obj != None


    #
    # def test_toJson():
    #     result = toJson({'data': {'menu': [{'action': '', 'submenu': [{'submenu': [], 'name': 'Cliente', 'service': 'cliente'}, {'submenu': [], 'name': 'Fornecedor', 'service': 'fornecedor'},
    #                                                          {'submenu': [], 'name': 'Usu\xc3\xa1rio', 'service': 'usuario'}, {'submenu': [], 'name': 'Caixa', 'service': 'caixa'},
    #                                                          {'submenu': [], 'name': 'Transportador', 'service': 'transportador'}], 'name': 'Cadastros Gerais'},
    #                               {'submenu': [{'submenu': [], 'name': 'Produto', 'service': 'produto'}, {'submenu': [], 'name': 'Categoria', 'service': 'categoria'},
    #                                            {'submenu': [], 'name': 'Unidade', 'service': 'unidade'},
    #                                            {'submenu': [], 'name': 'Fabricante/Marca', 'service': 'fabricante'}], 'name': 'Estoque', 'service': ''},
    #                               {'submenu': [{'submenu': [], 'name': 'Contas a Pagar', 'service': 'contapagar'},
    #                                            {'submenu': [], 'name': 'Contas a Receber', 'service': 'contareceber', 'help': 'Gerencia todo o conta a receber, possibilitando administrar cheques, boletos, duplicatas'},
    #                                            {'submenu': [], 'name': 'Movimento de Caixa', 'service': 'movimentocaixa', 'help': 'Controle de toda a movimenta\xc3\xa7\xc3\xa3o de caixas, organizada por usu\xc3\xa1rio, turnos, data etc'},
    #                                            {'submenu': [], 'name': 'Fechamento de Caixa', 'service': 'fechamentocaixa', 'help': 'Controle sobre os fechamentos de caixas, sobras e perdas, organizado por usu\xc3\xa1rio, data etc'},
    #                                            {'submenu': [], 'name': 'Banco/conta', 'service': 'banco', 'help': 'Gerenciamento de cadastros de bancos, conta corrente, conv\xc3\xaanios'}], 'name': 'Financeiro', 'service': ''},
    #                               {'submenu': [{'submenu': [], 'name': 'Pedido', 'service': 'pedido'}, {'submenu': [], 'name': 'NF-e', 'service': 'nfe'},
    #                                            {'submenu': [], 'name': 'NFC-e', 'service': 'nfce'},
    #                                            {'submenu': [], 'name': 'DF-e', 'service': 'dfe', 'help': 'Gerenciamento de documentos fiscais eletr\xc3\xb4nicos'},
    #                                            {'submenu': [], 'name': 'Cupom Fiscal', 'service': 'cupomfiscal', 'help': 'Esse m\xc3\xb3dulo pode ser consultado todos os cupons fiscais emitidos pelo sistema atrav\xc3\xa9s de ECF'},
    #                                            {'submenu': [], 'name': 'Entrada', 'service': 'entrada'},
    #                                            {'submenu': [], 'name': 'Ordem de Servi\xc3\xa7o', 'service': 'ordemservico', 'help': 'M\xc3\xb3dulo que gerencia toda a parte de ordens de servi\xc3\xa7os'}], 'name': 'Movimenta\xc3\xa7\xc3\xa3o', 'service': ''},
    #                               {'submenu': [{'submenu': [], 'name': 'Sped Fiscal', 'service': 'spedfiscal'},
    #                                            {'submenu': [], 'name': 'Sintegra', 'service': 'sintegra'}], 'name': 'Fiscal', 'service': '', 'help': 'M\xc3\xb3dulo respons\xc3\xa1vel pela gera\xc3\xa7\xc3\xa3o de obriga\xc3\xa7\xc3\xb5es acess\xc3\xb3rias da empresa baseado nas informa\xc3\xa7\xc3\xb5es que cont\xc3\xa9m no sistema'},
    #                               {'submenu': [{'submenu': [], 'name': 'LMC', 'service': 'lmc'}, {'submenu': [], 'name': 'Frentista', 'service': 'frentista'},
    #                                            {'submenu': [], 'name': 'Automa\xc3\xa7\xc3\xa3o', 'service': 'automacao'},
    #                                            {'submenu': [], 'name': 'Tabela de Aferi\xc3\xa7\xc3\xa3o', 'service': 'tabelaafericao'}], 'name': 'Posto de Combust\xc3\xadvel', 'service': ''},
    #                               {'submenu': [
    #                                   {'submenu': [], 'name': 'Importa\xc3\xa7\xc3\xa3o de dados', 'service': 'importacaodados'}],
    #                                   'name': 'Utilidades', 'service': ''}], 'servicos': [], 'preferecias': {}, 'infoLogin':
    #                          {'usuario_email': u'rodrigorodriguescosta@gmail.com', 'usuario_foto': '', 'empresa_padrao_nome': u'Bit automacao', 'usuario_nome': u'Rodrigo rodrigues', 'mensagens': [], 'empresa_padrao_cnpj': None, 'alertas': [], 'empresa_namespace': u'bit', 'ultimo_acesso': None, 'inatividade_login': 5}, 'token': 'd21b8c80-20f2-11e6-b1ad-a7ed65358da7', 'infoAplicacao': {'imagem': '', 'nome': 'Sigeflex - Sistema Integrado de Gest\xc3\xa3o Empresarial'}}, 'result': 'OK'})
    #     assert result==''
