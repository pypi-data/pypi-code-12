# -*- coding: utf-8 -*-
from pyservice_django.pyservice_django import post, i18n, config_classes


def test_POST():
    url = 'https://service-cep-dot-sigeflex-erp.appspot.com/consulta_cidade'
    params = ["Moss"]
    assert post(url, params)!=None


def test_config_classes__i18n():

    class Teste():
        def teste(self):
            return self.i18n('USUARIO_JA_ATIVADO', ['Jose'])

        def teste2(self):
            return self.i18n('USUARIO_REGISTRO_TITULO')

    config_classes([Teste])
    teste = Teste()
    mensagem = teste.i18n('USUARIO_JA_ATIVADO', ['Jose'])
    assert mensagem == 'O usuario Jose já está registrado e ativado, você já pode utilizar o sistema!'

    mensagem = teste.teste()
    assert mensagem == 'O usuario Jose já está registrado e ativado, você já pode utilizar o sistema!'

    mensagem = teste.teste2()
    assert mensagem == 'Confirmação de registro'
