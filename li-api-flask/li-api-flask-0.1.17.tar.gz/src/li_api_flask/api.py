# -*- coding: utf-8 -*-

import sys
import logging

from flask import Flask, make_response
from flask_restful import Api
from flask_restful.utils import cors
from raven.contrib.flask import Sentry

from li_common.padroes import cadastro
from li_api_flask import http_cache, restful, serializacao


class Home(restful.RecursoBase):
    def get(self):
        return self.resposta({})


class Healthcheck(restful.RecursoBase):
    def get(self):
        return self.resposta({'status': 'OK', 'versao': self.versao_api})


class LIApi(object):
    prefixo_url = '/loja/<int:loja_id>'

    def __init__(self, settings, nome=None, prefixo_url_api=None, usa_metadados=False):
        """
        Representa um aplicativo tipo API
        :param settings: Módulo com as informações de settings
        :param nome: O nome da API
        :type nome: str
        :return:
        """
        self.nome = nome
        if not self.nome:
            self.nome = __name__
        self.versao = settings.VERSAO
        self.app = Flask(nome)
        self._api = Api(self.app)
        self.app.config.from_object(settings)
        self.app.debug = settings.DEBUG
        # self._api.decorators = [cors.crossdomain(origin='*', headers=['Authorization', 'Content-Type', 'Accept'])]
        # Needed to save handle_error dumb override
        self.flask_restful_handle_error = self._api.handle_error
        self._api.handle_error = self.trata_erros_api
        self.http_cache = http_cache.definicao(nome)
        self.logger = logging.getLogger(nome.upper())
        self.registra_excecoes()
        self.usa_metadados = usa_metadados
        self.prefixo_url_api = ''
        if prefixo_url_api:
            self.prefixo_url_api = prefixo_url_api

        self.registrar_recurso('/', Home, usa_prefixo=False, usa_prefixo_api=False)
        self.registrar_recurso('/healthcheck', Healthcheck, usa_prefixo=False, usa_prefixo_api=False)

        if settings.SENTRY_DSN_API:
            sentry = Sentry(dsn=settings.SENTRY_DSN_API)
            sentry.init_app(self.app, logging=logging, level=logging.ERROR)

    def _monta_url(self, usa_prefixo, usa_prefixo_api, *partes):
        total = []
        partes = list(partes)
        for parte in partes:
            if parte:
                total.extend([_parte for _parte in parte.split('/') if _parte])
        url = '/{}'.format('/'.join(total))
        if usa_prefixo:
            url = '/{}{}'.format(self.prefixo_url.lstrip('/'), url)
        if usa_prefixo_api:
            url = '/{}{}'.format(self.prefixo_url_api.lstrip('/'), url)
        return url

    def registrar_recurso(self, url, recurso, max_age=0, sem_cache=None, usa_prefixo=True, usa_prefixo_api=True):
        """
        Registra um recurso de API para ser usado através da URL
        :param url: A URL, no padrão do Flask, pela qual esse recurso irá responder
        :type url: str, tuple
        :param recurso: A classe do recurso que será adicionada à API
        :type recurso: restful.RecursoBase
        :param max_age: O tempo, em segundos, que deverá ser adicionado de http cache para essa URL. Passando 0, limpa o cache.
        :type max_age: int
        :param sem_cache: Um dicionário contendo o tipo de parâmetro e a chave/valor do parâmetro para identificar que a URL deve ser chamada sem cache. Mais detalhes na documentação do módulo http_cache.
        :type sem_cache: dict
        :return: None
        """
        if not isinstance(url, tuple):
            url = (url, )
        url = tuple([self._monta_url(usa_prefixo, usa_prefixo_api, _url) for _url in url])
        self.http_cache.define_cache(url, max_age=max_age, sem_cache=sem_cache)
        self._api.add_resource(recurso, *url)
        recurso.nome_api = self.nome
        recurso.versao_api = self.versao
        recurso.cache = self.http_cache

    def registrar_blueprint(self, blueprint, **options):

        if not options.get('ignore_prefix', False):
            if options.has_key('url_prefix'):
                options['url_prefix'] = self.prefixo_url + options.get('url_prefix')
            else:
                options['url_prefix'] = self.prefixo_url
        else:
            del options['ignore_prefix']

        self.app.register_blueprint(blueprint, **options)

    def registra_excecoes(self):
        @self.app.errorhandler(404)
        def recurso_nao_encontrado(erro):
            conteudo, status = serializacao.ResultadoDeApi.resposta({}, self.nome, self.versao, 404, usa_metadados=self.usa_metadados)
            return make_response(conteudo, status, {'Content-Type': 'text/json; charset=utf-8'})

    def trata_erros_api(self, erro):
        exc_type, exc_value, tb = sys.exc_info()
        nome = getattr(erro, 'name', '')
        headers = {'Content-Type': 'application/json; charset=utf-8'}
        if nome == 'Method Not Allowed':
            headers['Allow'] = erro.valid_methods
            conteudo, status = serializacao.ResultadoDeApi.resposta({}, self.nome, self.versao, 405, usa_metadados=self.usa_metadados)
            return make_response(conteudo, status, headers)
        if nome == 'Bad Request':
            conteudo, status = serializacao.ResultadoDeApi.resposta({'mensagem': u'A requisição é inválida.'}, self.nome, self.versao, 400, usa_metadados=self.usa_metadados)
            return make_response(conteudo, status, headers)
        if type(erro) is cadastro.DadosInvalidos:
            conteudo, status = serializacao.ResultadoDeApi.resposta({'mensagem': u'Ocorreram erros de validação.', 'erros': erro.erros}, self.nome, self.versao, 400, usa_metadados=self.usa_metadados)
            return make_response(conteudo, status, headers)

        execao = erro
        execao.tipo = exc_type
        execao.tb = tb
        conteudo, status = serializacao.ResultadoDeApi.resposta({'mensagem': 'Ocorreu um erro inesperado no servidor'}, self.nome, self.versao, status=500, excecao=execao, usa_metadados=self.usa_metadados)
        self.logger.error(u'{}'.format(conteudo))
        return make_response(conteudo, status, headers)


def executa_local(app, modulo_settings=None):
    from werkzeug.wsgi import DispatcherMiddleware
    from werkzeug.serving import run_simple
    from li_common import helpers
    parent_app = DispatcherMiddleware(app, {})
    porta = 8080
    host = '0.0.0.0'
    debug = True
    if modulo_settings:
        porta = modulo_settings.PORT
        host = modulo_settings.HOST
        debug = modulo_settings.DEBUG
        helpers.carregar_env()

    run_simple(host, porta, parent_app, use_reloader=True, use_debugger=True, processes=(4 if debug else 1))

def limit(request):
    if request.args.get('limit', None):
        return int(request.args.get('limit'))
    return None


def offset(request):
    return int(request.args.get('offset', 0))


def order(request, queryset):
    order = request.args.get('order', '').lower()
    sort = request.args.get('sort', '')

    if sort and order and order in ['asc', 'desc']:
        return queryset.order_by('-{}'.format(sort) if order == 'desc' else sort)
    return queryset


def get_fields(request, fields):
    keys = request.args.get('fields', None)

    return dict((k, fields[k]) for k in keys.split(',') if k in fields) if keys else fields
