# -*- coding: utf-8 -*-

"""
Componentes para a criação de recursos para serem usados nas APIs Rest
"""
from functools import wraps
from urllib import urlencode
from flask import request, make_response, redirect
import flask_restful
from werkzeug import exceptions

from li_api_flask import serializacao
from li_common.padroes import json_encoder
from repositories.plataforma.models import Contrato

class ErrosHTTP(object):
    """
    Encapsula métodos para erros de HTTP
    """

    def __init__(self, nome_api=None, versao_api=None, usa_metadados=False):
        self.nome_api = nome_api
        self.versao_api = versao_api
        self.usa_metadados = usa_metadados

    def erro_400(self, chaves):
        """
        Retorna uma tupla para ser usada como retorno de requisição de API com uma mensagem padrão de erro 400
        :param chaves: As chaves necessárias para fazer a autenticação.
        :type chaves: list
        :return: Uma tupla com dicionário com a mensagem de erro, citando um exemplo de como fazer a requisição correta e o status code 400.
        :rtype: tuple
        """
        modelos = ["{} XXXXXXXX-YYYY-ZZZZ-AAAA-BBBBBBBBBBBB".format(chave) for chave in chaves]
        conteudo = {
            'mensagem': u"Adicione um cabeçalho Authorization com {} para acessar essa api. Ex.: Authorization: {}".format(", ".join(chaves), " ".join(modelos))
        }
        conteudo, status = serializacao.ResultadoDeApi.resposta(conteudo, self.nome_api or 'Autenticador', self.versao_api or '0.0.1', 400, usa_metadados=self.usa_metadados)
        headers = {'Content-Type': 'text/json; charset=utf-8'}
        return make_response(conteudo, status, headers)

    def erro_401(self):
        """
        Retorna uma tupla para ser usada como retorno de requisição de API com uma mensagem padrão de erro 401
        :return: Uma tupla com dicionário com a mensagem 'Você não está autorizado a acessar essa url.' e o status code 401.
        :rtype: tuple
        """
        conteudo = {
            'mensagem': u"Você não está autorizado a acessar essa url."
        }
        conteudo, status = serializacao.ResultadoDeApi.resposta(conteudo, self.nome_api or 'Autenticador', self.versao_api or '0.0.1', 401, usa_metadados=self.usa_metadados)
        headers = {'Content-Type': 'text/json; charset=utf-8'}
        return make_response(conteudo, status, headers)


class Autenticacao(object):
    """
    Fornece as funcionalidades para executar a autenticação da API
    """
    def __init__(self, nome_api=None, versao_api=None, usa_metadados=False):
        self.nome_api = nome_api
        self.versao_api = versao_api
        self.valores = {}
        self.usa_metadados = usa_metadados

    def define_valor(self, nome, valor):
        """
        Define o uma chave/valor que deverá ser validada em um cabeçalho AUTHORIZATION. Esse método deve ser chamado na inicialização da api que precisa da autenticação.
        :param nome: O nome da chave que deverá existir no cabeçalho AUTHORIZATION
        :type nome: str, list
        :param valor: O valor da chave
        :type valor: str
        :return: None
        """
        self.valores[nome] = valor

    def chaves_validas(self, chaves):
        """
        Verifica se as chaves passadas foram definidas para a API e se os valores são válidos
        :param chaves: As chaves extraídas do cabeçalho AUTHORIZATION
        :type chaves: dict
        :return: True caso a chave exista e o valor seja o mesmo definido. De outro jeito, False
        :rtype: bool
        """
        for chave in self.valores.keys():
            if chave not in chaves:
                return False
            if isinstance(self.valores[chave], str) and chaves[chave] != self.valores[chave]:
                return False
            if isinstance(self.valores[chave], list) and chaves[chave] not in self.valores[chave]:
                return False
        return True

    def extrai_chaves(self, chaves, headers):
        """
        Tenta extrair as chaves de autenticação do cabeçalho HTTP passado. O cabeçalho deve conter um elemento AUTHORIZATION
        :param chaves: Lista com as chaves que se espera existir no cabeçalho. As mesmas definidas com o Autenticador.define_valor(nome, valor)
        :type chaves: list
        :param headers: O cabeçalho HTTP
        :type headers: dict
        :return: As chaves extraídas do cabeçalho como um dicionário
        :rtype: dict
        """
        try:
            authorization = headers["AUTHORIZATION"]
        except KeyError:
            return None
        if not authorization:
            return None
        authorization = authorization.split()
        if len(authorization) != len(chaves) * 2:
            return None
        resultado = {}
        for chave in chaves:
            if chave in authorization:
                indice = authorization.index(chave) + 1
                resultado[chave] = authorization[indice]
        return resultado

    def requerido(self, function):
        """
        Decorator para ser usado na função que deve exigir autenticação.
        """
        @wraps(function)
        def decorated(*args, **kwargs):
            """
            Valida a autenticação para o método decorado
            """
            # import ipdb; ipdb.set_trace()
            chaves = self.extrai_chaves(self.valores.keys(), request.headers)
            if not chaves:
                return ErrosHTTP(self.nome_api, self.versao_api, self.usa_metadados).erro_400(self.valores.keys())
            if not self.chaves_validas(chaves):
                return ErrosHTTP(self.nome_api, self.versao_api, self.usa_metadados).erro_401()
            return function(*args, **kwargs)

        return decorated

    # # # TODO: Ciente de que isto nao deveria estar aqui
    # Foi feito em carater emergencial para manter compatibilidade de /v2/whitelabel.
    # unattis
    def whitelabel_requerido(self, function):
        """
        Decorator para ser usado na função que deve exigir autenticação.
        """

        @wraps(function)
        def decorated(*args, **kwargs):
            """
            Valida a autenticação para o método decorado
            """
            chaves = self.extrai_chaves(['chave_whitelabel'], request.headers)

            if not chaves:
                return ErrosHTTP(self.nome_api, self.versao_api, self.usa_metadados).erro_400(self.valores.keys())

            # Verifica se whitelabel esta valido
            contrato = self.retorna_dados_contrato(chaves)

            if contrato is None:
                return ErrosHTTP(self.nome_api, self.versao_api, self.usa_metadados).erro_401()

            if function.__name__ != 'put' and contrato.tipo == 'revenda':
                return ErrosHTTP(self.nome_api, self.versao_api, self.usa_metadados).erro_401()

            kwargs['contrato_id'] = contrato.id

            return function(*args, **kwargs)

        return decorated

    def retorna_dados_contrato(self, chaves):
        """
        retorna_dados_contrato
        :param chaves: chaves
        :return: id
        """
        if chaves.get("chave_whitelabel"):
            try:
                return Contrato.objects.only('id', 'tipo').get(chave=chaves.get('chave_whitelabel'),
                                                               tipo__in=['whitelabel', 'revenda'],
                                                               ativo=True)
            except:
                return None
        else:
            return None


class RecursoBase(flask_restful.Resource):
    """
    Representa um recurso base de api rest
    """
    nome_api = None
    versao_api = None
    cache = None
    objeto_request = request

    def __init__(self):
        self._dados = {}
        self._headers = {}

    @property
    def dados(self):
        """
        Obtem os dados enviados em um request, analisando args, form e json e adicionando todos em um dicionário único
        :return: Um dicionário com os valores dos dados passados no request
        :rtype: dict
        """
        if not self._dados:
            self._dados = {}
            for arg in self.objeto_request.args:
                self._dados[arg] = self.objeto_request.args[arg]
            for arg in self.objeto_request.form:
                self._dados[arg] = self.objeto_request.form[arg]
            try:
                self._dados.update(self.objeto_request.get_json())
            except (TypeError, exceptions.BadRequest):
                pass
        return self._dados

    @property
    def headers(self):
        """
        Obtem os dados enviados em um request, analisando args, form e json e adicionando todos em um dicionário único
        :return: Um dicionário com os valores dos dados passados no request
        :rtype: dict
        """
        if not self._headers:
            for key, value in self.objeto_request.headers:
                self._headers[key] = value

        return self._headers

    @classmethod
    def resposta_objeto(cls, objeto, status=200):
        """
        Gera um json a partir de um objeto e envia a resposta.
        :param objeto: O objeto a ser serializado
        :type objeto: class object
        :param status: Status Code para a resposta. Padrão é 200
        :type status: int
        :return: Um objeto response do Flask
        :rtype : object
        """
        conteudo = json_encoder.serialize(objeto, data_type=False);

        return cls.resposta_json(conteudo, status)

    @classmethod
    def resposta(cls, conteudo, status=200, excecao=None, usa_metadados=False):
        """
        Gera um objeto response do Flask com um conteúdo padronizado para todos os tipos de retorno.
        Caso exista a chave 'redirect' no conteúdo, retorna um objeto redirect do Flask com status 301.
        :param conteudo: O conteudo a ser inserido no padrão de resposta. Pode ser um dict ou uma str
        :type conteudo: dict
        :param status: Status Code para a resposta. Padrão é 200
        :type status: int
        :param excecao: Caso a resposta seja 500, qual a exceção que gerou o erro 500.
        :type excecao: Exception
        :return: Um objeto response do Flask
        :rtype : object
        """
        if conteudo is None:
            conteudo = {}
        if 'redirect' in conteudo and isinstance(conteudo, dict):
            url = conteudo.pop('redirect')
            url = cls.codifica_url(conteudo, url)
            return cls.redirecionar(url)
        return cls.resposta_json(*serializacao.ResultadoDeApi.resposta(conteudo, cls.nome_api, cls.versao_api, status, excecao, usa_metadados))

    @classmethod
    def resposta_json(cls, conteudo, status=200):
        """
        Gera um objeto response do Flask com um conteúdo padronizado para todos os tipos de retorno.
        Caso exista a chave 'redirect' no conteúdo, retorna um objeto redirect do Flask com status 301.
        :param conteudo: O conteudo a ser inserido no padrão de resposta. Pode ser um dict ou uma str
        :type conteudo: str
        :param status: Status Code para a resposta. Padrão é 200
        :type status: int
        :return: Um objeto response do Flask
        :rtype : object
        """
        headers = {'Content-Type': 'application/json; charset=utf-8'}
        if cls.cache:
            cls.cache.aplica_cache(cls.objeto_request, headers)

        return make_response(conteudo, status, headers)

    @classmethod
    def codifica_url(cls, conteudo, url):
        """
        Aplica URL encode
        :param conteudo: Dicionário contendo os pares cahve valor para a querystring
        :type conteudo: dict
        :param url: A URL que deverá se codificada
        :type url: str
        :return: A URL codificada
        :rtype: str
        """
        for chave in conteudo:
            if isinstance(conteudo[chave], bool):
                conteudo[chave] = 1 if conteudo[chave] else 0
        if '?' in url and conteudo:
            url = '{}&{}'.format(url, urlencode(conteudo))
        elif conteudo:
            url = '{}?{}'.format(url, urlencode(conteudo))
        return url

    @classmethod
    def redirecionar(cls, url, status_code=301):
        """
        Redireciona uma requisção HTTP para a URL
        :param url: A URL para onde redirecionar
        :type url: str
        :param status_code: O código HTTP a ser enviado no redirect. O padrão é 301.
        :type status_code: int
        :return: Objeto redirect
        """
        return redirect(url, code=status_code)
