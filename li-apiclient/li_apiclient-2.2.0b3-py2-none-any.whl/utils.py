# -*- coding: utf-8 -*-
import json
import requests
from urllib import urlencode
from django.conf import settings


class AutenticacaoFalhou(Exception):
    pass


class ApiClientBase(object):
    NOME = "API_BASE"
    AUTENTICA_APLICACAO = False
    AUTENTICA_LOJA = False
    AUTENTICA_USUARIO = False

    def __init__(self, request=None, conta=None):

        self.conta = None
        self.usuario = None

        if conta is not None:
            self.conta = conta

        elif request and hasattr(request, 'conta'):
            self.conta = request.conta

        if request and hasattr(request, 'usuario'):
            self.usuario = request.usuario

    @property
    def usa_autenticacao(self):
        return self.AUTENTICA_APLICACAO or self.AUTENTICA_LOJA or self.AUTENTICA_USUARIO

    @property
    def url_base(self):
        return getattr(settings, self.NOME, "")

    @property
    def chave_aplicacao(self):
        return getattr(settings, "{}_CHAVE_APLICACAO".format(self.NOME), None)

    @property
    def chave_loja(self):
        return str(self.conta.chave)

    @property
    def chave_usuario(self):
        return str(self.usuario.chave)

    def to_dict(self, path, method="get", meta=False, **kwargs):
        if method == "post":
            resposta = self._post(path, **kwargs)
        elif method == "put":
            resposta = self._put(path, **kwargs)
        elif method == "delete":
            resposta = self._delete(path)
        else:
            resposta = self._get(path, **kwargs)

        if meta is True:
            resposta_dict = {
                'status_code': resposta.status_code,
                'content': json.loads(resposta.content)
            }
        else:
            resposta_dict = json.loads(resposta.content)
            resposta_dict["status_code"] = resposta.status_code

        if resposta.status_code == 401:
            raise AutenticacaoFalhou(resposta.content)

        return resposta_dict

    def autenticacao(self):
        autorizacao = ""
        message = u"O valor de {} não foi definido no entanto {} está como True."

        if self.AUTENTICA_APLICACAO:
            if not self.chave_aplicacao:
                raise ValueError(message.format("CHAVE_APLICACAO", "AUTENTICA_APLICACAO"))
            autorizacao = "chave_aplicacao {} ".format(self.chave_aplicacao)
        if self.AUTENTICA_LOJA:
            if not self.chave_loja:
                raise ValueError(message.format("CHAVE_LOJA", "AUTENTICACAO_LOJA"))
            autorizacao = "{}chave_loja {} ".format(autorizacao, self.chave_loja)
        if self.AUTENTICA_USUARIO:
            if not self.chave_usuario:
                raise ValueError(message.format("CHAVE_USUARIO", "AUTENTICACAO_USUARIO"))
            autorizacao = "{}chave_usuario {} ".format(autorizacao, self.chave_usuario)

        return {'Authorization': autorizacao}

    def _get(self, path, **kwargs):
        if kwargs:
            args = {}

            for k, v in kwargs.items():
                if v is bool:
                    args[k] = str(v)
                elif type(v) is list:
                    args[k] = ','.join(v)
                elif v:
                    args[k] = v.encode('utf-8')

            path += "?" + urlencode(args)

        if self.usa_autenticacao:
            return requests.get('{}{}'.format(self.url_base, path), headers=self.autenticacao())

        return requests.get('{}{}'.format(self.url_base, path))

    def _delete(self, path):
        if self.usa_autenticacao:
            return requests.delete('{}{}'.format(self.url_base, path), headers=self.autenticacao())
        return requests.delete('{}{}'.format(self.url_base, path))

    def _post(self, path, *args, **kwargs):
        headers = {"Content-Type": "application/json"}
        if self.usa_autenticacao:
            headers.update(self.autenticacao())
        data = None
        if args:
            data = str(list(args))
        if kwargs:
            data = json.dumps(kwargs)
        return requests.post('{}{}'.format(self.url_base, path), data=data, headers=headers)

    def _put(self, path, *args, **kwargs):
        headers = {"Content-Type": "application/json"}
        if self.usa_autenticacao:
            headers.update(self.autenticacao())
        data = None
        if args:
            data = str(list(args))
        if kwargs:
            data = json.dumps(kwargs)
        return requests.put('{}{}'.format(self.url_base, path), data=data, headers=headers)
