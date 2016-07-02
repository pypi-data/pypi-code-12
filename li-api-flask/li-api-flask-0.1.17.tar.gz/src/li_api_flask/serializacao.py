# -*- coding: utf-8 -*-
import json
import sys
import traceback


class ResultadoDeApi(object):
    """
    Fornece métodos para padronizar a serialização de respostas das APIs
    """
    _resultados = {
        200: 'sucesso',
        400: 'request_invalido',
        401: 'nao_autorizado',
        403: 'nao_autenticado',
        404: 'nao_encontrado',
        405: 'metodo_nao_permitido',
        408: 'timeout',
        500: 'erro_servidor'
    }
    _mensagem_resultados = {
        403: u'A autenticação falhou: {}',
        404: u'A url acessada não existe em {}',
        405: u'Não é permitido esse método HTTP para essa URL.',
        408: u'O servidor não respondeu em tempo.',
    }

    @classmethod
    def _formata_trace_back(cls, trace_back):
        """
        Formata o trace back como uma lista de dicionários no seguinte formato:
        {
            'codigo': '    a = 1 / 0',
            'local': '..unitarios/padroes/test_serializacao.py, line 318, in test_deve_retornar_resposta_para_erro_500_com_trace_back_passado'
        }
        :param trace_back: O traceback da exceção
        :type trace_back: list
        :return: A lista de traceback formatada
        :rtype: list
        """
        resultado = []
        for stack in trace_back[-4:-1]:
            linhas = stack.split('\n')
            local = linhas[0].split(', ')
            local[0] = local[0].strip()
            local[0] = local[0].replace('File "', '').replace('"', '')
            local[0] = '..{}'.format('/'.join(local[0].split('/')[-3:]))
            local = ", ".join(local)
            if not local.startswith('..Traceback '):
                resultado.append({'local': local, 'codigo': linhas[1]})
        return resultado

    @classmethod
    def resposta(cls, conteudo, nome_api, versao, status=200, excecao=None, usa_metadados=False):
        """
        Monta a resposta para os dados do resultado.
        :param conteudo: Um dicionário com o conteúdo da resposta a ser enviado. Caso não seja passado um dicionário, o mesmo será criado com a chave 'conteudo' e o valor passado nesse parametro.
        :type conteudo: dict, str
        :param nome_api: O nome da API que está produzindo a resposta
        :type nome_api: str
        :param versao: A versão da API que está produzindo a resposta
        :type versao: str
        :param status: O status code da resposta
        :type status: int
        :param excecao: A exceção que gerou uma resposta com status code 500
        :type excecao: Exception
        :param usa_metadados: Manter compatibilidade com os chamadores que tratam a resposta com metadados. Padrão False.
        :type usa_metadados: bool
        :return: Tupla com os dados do resultado e o status code
        :rtype: tuple
        """
        if usa_metadados:
            resultado = cls._resultado_com_metadados(conteudo, excecao, nome_api, status, versao)
        else:
            resultado = cls._resultado_simples(conteudo, excecao, nome_api, status)
        if isinstance(resultado, str):
            return resultado, status
        return json.dumps(resultado), status

    @classmethod
    def _resultado_com_metadados(cls, conteudo, excecao, nome_api, status, versao):
        """
        Helper para gerar a resposta com metadados.
        :param conteudo: Um dicionário com o conteúdo da resposta a ser enviado. Caso não seja passado um dicionário, o mesmo será criado com a chave 'conteudo' e o valor passado nesse parametro.
        :type conteudo: dict
        :param nome_api: O nome da API que está produzindo a resposta
        :type nome_api: str
        :param versao: A versão da API que está produzindo a resposta
        :type versao: str
        :param status: O status code da resposta
        :type status: int
        :param excecao: A exceção que gerou uma resposta com status code 500
        :type excecao: Exception
        :return: O resultado como dicionário com metadados
        :rtype: dict
        """
        if status == 403:
            conteudo = {'conteudo': cls._mensagem_resultados[status].format(conteudo)}
        if status == 404:
            conteudo = {'conteudo': cls._mensagem_resultados[status].format(nome_api)}
        if status in [405, 408]:
            conteudo = {'conteudo': cls._mensagem_resultados[status]}
        if not isinstance(conteudo, dict):
            conteudo = {'conteudo': conteudo}
        try:
            status_resultado = cls._resultados[status]
        except KeyError:
            status_resultado = 'status_nao_definido'
        metadados = {
            'api': nome_api,
            'versao': versao,
            'resultado': status_resultado,
        }
        conteudo = conteudo
        if excecao:
            cls._empacota_excecao(conteudo, excecao)
        resultado = {
            'metadados': metadados,
            status_resultado: conteudo
        }
        return resultado

    @classmethod
    def _resultado_simples(cls, conteudo, excecao, nome_api, status):
        """
        Helper para gerar a resposta simples sem metadados.
        :param conteudo: Um dicionário com o conteúdo da resposta a ser enviado. Caso não seja passado um dicionário, o mesmo será criado com a chave 'conteudo' e o valor passado nesse parametro.
        :type conteudo: dict
        :param nome_api: O nome da API que está produzindo a resposta
        :type nome_api: str
        :param status: O status code da resposta
        :type status: int
        :param excecao: A exceção que gerou uma resposta com status code 500
        :type excecao: Exception
        :return: O resultado como dicionário com metadados
        :rtype: dict, str
        """
        if status == 403:
            conteudo = cls._mensagem_resultados[status].format(conteudo)
        if status == 404:
            conteudo = cls._mensagem_resultados[status].format(nome_api)
        if status in [405, 408]:
            conteudo = cls._mensagem_resultados[status]
        if excecao:
            conteudo = {'resultado': conteudo}
            cls._empacota_excecao(conteudo, excecao)
        return conteudo

    @classmethod
    def _empacota_excecao(cls, conteudo, excecao):
        """
        Gera a exceção em um formato de dicionário para ser incluído na resposta
        :param conteudo: O conteúdo atual da resposta onde será adicionado a exceção
        :param excecao: A exceção a ser emacotada
        :return: Um dicionário com o conteúdo formatado com a exceção
        :rtype: dict
        """
        exc_type, exc_value, trace_back = sys.exc_info()
        if exc_type:
            stack_trace = traceback.format_exception(exc_type, exc_value, trace_back)
        else:
            try:
                stack_trace = traceback.format_exception(excecao.tipo, excecao, excecao.tb)
            except AttributeError:
                stack_trace = []
        stack_trace = cls._formata_trace_back(stack_trace)
        nome_exec = excecao.__class__.__name__
        conteudo.update({'excecao': {'nome': nome_exec, 'mensagem': unicode(excecao), 'stack_trace': stack_trace}})

