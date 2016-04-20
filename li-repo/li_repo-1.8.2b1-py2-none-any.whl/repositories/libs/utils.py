# -*- coding: utf-8 -*-

import os
import logging
import string
import urllib
import urllib2
import json
import re
import pprint
import base64
import hashlib
import urlparse
import mimetypes
import random

from django.conf import settings
from django import forms
from django.contrib import messages
from django.db import IntegrityError, transaction
from django.forms import CharField
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.http import HttpResponse, Http404
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile
from django.core.paginator import Paginator, EmptyPage
from django.utils import formats
from django.core import validators
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.utils.encoding import smart_str
from localflavor.br.forms import (
    BRPhoneNumberField as BaseBRPhoneNumberField,
    BRCPFField as BaseBRCPFField,
    BRCNPJField as BaseBRCNPJField)

from repositories.libs.correios import Correios
from repositories.libs.aws import AWS

try:
    from PIL import Image
except ImportError:
    import Image

import calendar
from collections import OrderedDict
from contextlib import contextmanager
from decimal import Decimal
from hashlib import sha1
import time as time_2
from datetime import datetime, date, timedelta, time
from unicodedata import normalize
from li_common.helpers import send_email
from li_common.conexoes.worker import WorkerConnect

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
TEMPORARY_FOLDER = '/tmp/'


ESTADOS_BRASILEIROS = [(estado, estado)
                       for estado in '--,AC,AL,AP,AM,BA,CE,DF,ES,GO,MA,MT,MS,MG,PA,PB,PR,PE,PI,RJ,RN,RS,RO,RR,SC,SP,SE,TO'.split(',')]


class ApiChavesInvalidas(Exception):
    pass


class ClienteNaoAutorizado(Exception):
    pass


def publish_to_cache(key_name, **kwargs):
    from cachekeys import CACHEKEYS
    key_format, data_fn, key_timeout = CACHEKEYS[key_name]
    key = key_format % kwargs

    data = data_fn(**kwargs)
    cache.set(key, data, key_timeout)
    return data


def consume_from_cache(key_name, **kwargs):
    from cachekeys import CACHEKEYS
    key_format, data_fn, key_timeout = CACHEKEYS[key_name]
    key = key_format % kwargs

    data = cache.get(key)
    if data is None:
        data = publish_to_cache(key_name, **kwargs)
    return data


class PaginacaoFracionada(Paginator):

    def __init__(self, *args, **kwargs):
        self.pagina = kwargs.pop('pagina', 1)
        super(PaginacaoFracionada, self).__init__(*args, **kwargs)

    @property
    def page_range(self, *args, **kwargs):
        paginas = super(PaginacaoFracionada, self).page_range
        inicio = self.pagina - 4 if self.pagina - 4 > 0 else 0
        fim = self.pagina + 5
        saida = paginas[inicio:fim]
        if saida[0] != 1:
            saida.insert(0, 1)
            saida.insert(1, None)
        if saida[-1] != self.num_pages:
            saida.append(None)
            saida.append(self.num_pages)
        return saida


def paginar(lista, pagina, por_pagina):
    if not isinstance(pagina, int):
        pagina = ''.join([x for x in pagina if x.isdigit()])
        pagina = len(pagina) > 0 and int(pagina) or 1

    paginator = PaginacaoFracionada(lista, por_pagina, pagina=pagina)
    pagina = int(pagina)
    try:
        itens = paginator.page(pagina)
    except EmptyPage:
        itens = paginator.page(paginator.num_pages)
    return paginator, itens


def base64_url_decode(inp):
    padding_factor = (4 - len(inp) % 4) % 4
    inp += "=" * padding_factor
    return base64.b64decode(unicode(inp).translate(dict(zip(map(ord, u'-_'), u'+/'))))


def facebook_get_url(service, permissions=False, app_id=True,
                     app_secret=False, client_id=False,
                     client_secret=False, contrato=None, **kwargs):

    base_url = 'https://www.facebook.com/%s' % service
    params = kwargs

    facebook_app_id, facebook_app_secret = contrato.credenciais_facebook()

    if permissions:
        params['scope'] = ','.join(settings.FACEBOOK_PERMISSIONS_REQUIRED)
    if app_id:
        params['app_id'] = facebook_app_id
    if app_secret:
        params['app_secret'] = facebook_app_secret
    if client_secret:
        params['client_secret'] = facebook_app_secret
    if client_id:
        params['client_id'] = facebook_app_id

    full_url = base_url + '?' + '&'.join(['%s=%s' %(k,v) for k,v in params.items()])

    return full_url


def facebook_get_url_api(service, permissions=False, app_id=True,
                         app_secret=False, client_id=False,
                         client_secret=False, contrato=None, **kwargs):

    base_url = 'https://graph.facebook.com/%s' % service
    params = kwargs
    facebook_app_id, facebook_app_secret = contrato.credenciais_facebook()

    if permissions:
        params['scope'] = ','.join(settings.FACEBOOK_PERMISSIONS_REQUIRED)
    if app_id:
        params['app_id'] = facebook_app_id
    if app_secret:
        params['app_secret'] = facebook_app_secret
    if client_secret:
        params['client_secret'] = facebook_app_secret
    if client_id:
        params['client_id'] = facebook_app_id

    full_url = base_url + '?' + '&'.join(['%s=%s' % (k, v) for k,v in params.items()])
    return full_url


def facebook_get_token(url):
    try:
        page = urllib2.urlopen(url, timeout=3).read()
    except Exception as e:
        return None
    return urlparse.parse_qs(page)


class ExtendedJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        if isinstance(obj, datetime) or isinstance(obj, date):
            return obj.isoformat()
        return super(ExtendedJSONEncoder, self).default(obj)


def to_json(data):
    """Retorna um json."""
    try:
        j = json.dumps(data, cls=ExtendedJSONEncoder)
    except Exception as e:
        j = json.dumps({"error": e.message})
    return j


def from_json(data):
    """Retorna um objeto."""
    try:
        j = json.loads(data)
    except Exception:
        return None
    return j


def debug(string=None, **kwargs):
    """ Função de debug, print melhorado """
    if settings.DEBUG:
        print "########################### DEBUG ################################"
        if string:
            pprint.pprint(string)
        elif not string and len(kwargs) > 0:
            for k, v in kwargs.items():
                print '%s = %s' % (k, v)
                print
        print "##################################################################"


def remover_prefixo(item, prefixo):
    if type(item) == dict:
        new_item = {}
        for k, v in item.items():
            k = re.sub(r'^%s' % prefixo, '', k)
            new_item[k] = v

        return new_item

    if type(item) in (str, unicode):
        return item


def get_pais(request, default="BR"):
    """Retorna o código do Pais usando como calculo o IP do visitante."""
    ip = request.META.get('HTTP_X_FORWARDED_FOR', '0.0.0.0')
    url_base = 'http://api.hostip.info/get_json.php?ip=%s' % ip

    try:
        resultado = json.loads(urllib2.urlopen(url_base, timeout=2).read())
    except:
        return default

    if resultado.get("country_code") and resultado["country_code"] != "XX":
        return resultado["country_code"]
    else:
        return default


def formatar_decimal(valor):
    """
    Substitui casa decimal de virgula para ponto.

    >>> print formatar_decimal(3)
    3
    >>> print formatar_decimal('  29,9  ')
    29.9
    >>> print formatar_decimal('abc')
    Traceback (most recent call last):
      File '<stdin>', line 1, in ?
      File '<stdin>', line 7, in formatar_decimal
    ValueError: Numero decimal invalido.
    """
    if not valor:
        return Decimal(0)

    valor_negativo = False

    if str(valor)[:1] == "-":
        valor_negativo = True

    valor = str(valor).replace('.', '')
    valor = str(valor).strip().replace(',', '.')

    valor = re.sub(r'[^0-9\.\,]+','',str(valor))
    valor = Decimal(valor)

    if valor_negativo is True:
        valor = valor * -1

    return valor


def formatar_decimal_ab(valor):
    """
    Verifica sempre os ultimos 3 caracteres
    se o terceiro(da direita para esquerda)
    for ponto ou virgula coloca o que ta a direita
    scomo float e o que ta a esquerda como inteiro.
    (usado exclusivamente na importação dos produtos)
    """
    valor = str(valor)
    if not valor:
        return Decimal('0.00')
    if len(valor) <= 3:
        try:
            return Decimal(valor.replace(',', '.'))
        except:
            return Decimal(valor.replace('.', '').replace(',', '.'))
    if valor[-3] in [',', '.']:
        casas_decimais = valor[-2:]
        inteiro = valor[:-3].replace('.', '').replace(',', '')
    elif valor[-2] in [',', '.']:
        casas_decimais = '%s0' % valor[-1]
        inteiro = valor[:-2].replace('.', '').replace(',', '')
    else:
        casas_decimais = '00'
        inteiro = valor.replace('.', '').replace(',', '')
    return Decimal('%s.%s' % (inteiro, casas_decimais))

def formatar_decimal_br(valor, casas_decimais=2, separador_milhar=True):
    """
    Formata valor com duas casas decimais e virgula.

    >>> formatar_decimal_br(3)
    '3,00'
    >>> formatar_decimal_br(29.9)
    '29,90'
    >>> formatar_decimal_br('abc')
    Traceback (most recent call last):
      File "<stdin>", line 1, in ?
    ValueError: Numero decimal invalido.

    """
    if casas_decimais is None or casas_decimais < 0:
        casas_decimais = 0

    if not valor:
        return '0%s%s' % (casas_decimais and ',' or '', '0' * casas_decimais)

    valor = re.sub(r'[^0-9\.\,\-]+','',str(valor))
    valor = float(valor)

    valor = (('%%.%sf' % casas_decimais) % valor).replace('.', ',')
    if ',' in valor:
        inteiro, decimal = valor.split(',')
    else:
        inteiro, decimal = valor, None

    if len(inteiro) > 3:
        if not separador_milhar:
            valor_convertido = inteiro
        else:
            # inverte o valor para contar as casas de 3 em 3
            rev = inteiro[::-1]
            vezes = len(rev) / 3

            if len(rev) % 3 == 0:
                vezes -= 1

            valor_convertido = ''
            cont = 0

            # a cada três casas adiciona um '.'
            for i in range(vezes):
                valor_convertido += rev[cont: 3 + cont] + '.'
                cont += 3

            # adiciona o resto do valor
            valor_convertido += rev[cont: 3 + cont]

            # retorna o valor revertido e correto
            # agora pode se receber zilhões como valor
            valor_convertido = valor_convertido[::-1]
    else:
        return valor

    if decimal:
        return valor_convertido + ',' + decimal
    else:
        return valor_convertido


def digits(s, decimal=False, decimal_length=2):
    """
    Return only the digits of the string.

    >>> digits('10.000')
    10000
    >>> digits('R$ 10,00')
    1000
    >>> digits('R$ 10,00', decimal=True)
    10.0
    >>> digits('R$ 10,00', decimal=True, decimal_length=3)
    1.0
    """
    i = int(''.join(re.findall(r'\d+', s)))
    if decimal and decimal_length:
        i = i / (10.0 ** decimal_length)

    return i


class BRPhoneNumberField(BaseBRPhoneNumberField):
    def __init__(self, *args, **kwargs):
        if 'max_length' in kwargs:
            self.max_length = kwargs['max_length']
            del kwargs['max_length']
        else:
            self.max_length = None
        super(BRPhoneNumberField, self).__init__(*args, **kwargs)

    def clean(self, value):
        """Cleans the value to validation."""
        value = ''.join([x for x in (value or '') if x.isdigit()])
        if not value and self.required:
            raise ValidationError(self.error_messages['required'])
        if self.max_length and len(value) > self.max_length:
            raise ValidationError(u'Número inválido')
        return value

    def to_python(self, value):
        """Returns only the digits."""
        return ''.join([x for x in (value or '') if x.isdigit()])


class BRZipCodeField(forms.RegexField):
    default_error_messages = {
        'invalid': 'Entre um CEP no formato XXXXX-XXX.',
    }

    def __init__(self, *args, **kwargs):
        super(BRZipCodeField, self).__init__(r'^\d{5}-?\d{3}$',
                                             max_length=None, min_length=None, *args, **kwargs)

    def to_python(self, value):
        """Returns only the digits."""
        return ''.join([x for x in (value or '') if x.isdigit()])


class BRCPFField(BaseBRCPFField):
    default_error_messages = {
        'invalid': u'O número do CPF é inválido.',
        'required': u'Este campo é obrigatório.',
        'max_digits': u'Este campo tem que ter no mínimo 11 digitos ou 14 caracteres.',
        'digits_only': u'Este campo só aceita números.'
    }

    def to_python(self, value):
        """Returns only the digits."""
        value = super(BRCPFField, self).to_python(value)
        return ''.join([x for x in (value or '') if x.isdigit()])

    def clean(self, value):
        value = super(BRCPFField, self).clean(value)
        pattern = re.compile(r"(.)\1{2,}", re.DOTALL)
        match = pattern.match(value)
        if match and len(match.group()) == 11:
            raise ValidationError(self.error_messages['invalid'])
        return value


class BRCNPJField(BaseBRCNPJField):
    default_error_messages = {
        'invalid': 'O número do CNPJ é inválido.',
        'required': 'Este campo é obrigatório.',
        'max_digits': u'Este campo tem que ter no mínimo 14 digitos.',
        'digits_only': u'Este campo só aceita números.'
    }

    def to_python(self, value):
        """Returns only the digits."""
        return ''.join([x for x in (value or '') if x.isdigit()])

    def clean(self, value):
        value = super(BRCNPJField, self).clean(value)
        pattern = re.compile(r"^(.)\1{2,}", re.DOTALL)
        match = pattern.match(value)
        if match and len(match.group()) >= 8:
            raise ValidationError(self.error_messages['invalid'])
        return value


class BRDecimalField(forms.DecimalField):

    def to_python(self, value):
        """
        Validates that the input is a decimal number. Returns a Decimal
        instance. Returns None for empty values. Ensures that there are no more
        than max_digits in the number, and no more than decimal_places digits
        after the decimal point.
        """
        if value in forms.fields.validators.EMPTY_VALUES:
            return None
        if self.localize:
            value = forms.fields.formats.sanitize_separators(value)
        value = smart_str(value).strip()
        try:
            value = formatar_decimal(value)
        except (forms.fields.DecimalException, ValueError):
            raise ValidationError(self.error_messages['invalid'])
        return value


class TextInputBRDecimalField(forms.widgets.Input):
    input_type = 'text'

    def __init__(self, *args, **kwargs):
        if 'decimal_places' in kwargs:
            self.decimal_places = kwargs.get('decimal_places')
            kwargs.pop('decimal_places')
        else:
            self.decimal_places = 2
        super(TextInputBRDecimalField, self).__init__(*args, **kwargs)

    def _format_value(self, value):
        if self.is_localized:
            value = formats.localize_input(value)

        try:
            return formatar_decimal_br(value, self.decimal_places)
        except ValueError:
            return value


def randomz(x):
    """ Função que gera dados aleatorios para os graficos """
    import random

    lista = range(0, 99)
    dias = range(1, 31)
    saida = []
    for i in dias:
        n = random.choice(lista)
        saida.append([i, n])
    return saida


def mercado_livre_vendedor_existe(seller_id):

    v = "https://api.mercadolibre.com/users/%s" % seller_id
    try:
        page = urllib2.urlopen(v, timeout=3).read()
        vendedor = json.loads(page)
    except:
        return False

    if "erro" in vendedor:
        return False

    return vendedor


def get_seller_id(link, only_code=False):
    link = link.split('/')[-1]
    codigo = re.search(r'(ML[A-Z][-]?[0-9]+)', link)
    if codigo:
        codigo = codigo.group(0).replace('-', '')
        if only_code:
            return codigo
    else:
        return None
    try:
        page = urllib2.urlopen(
            'https://api.mercadolibre.com/items/%s' % codigo, timeout=3).read()
        j = json.loads(page)
    except:
        return None
    if 'seller_id' not in j:
        return None
    return j['seller_id']


def only_digits(string=None):
    if string:
        return re.sub('\D', '', string)


class Form(forms.Form):

    """ Classe genérica para criação de formularios com a possibilidade de setar choices
    de campos de escolha. """

    def __init__(self, *args, **kwargs):


        if "choices" in kwargs.keys():
            self.choices = kwargs["choices"]
            del kwargs["choices"]
            super(Form, self).__init__(*args, **kwargs)
            for c, v in self.choices.items():

                self.fields[c].choices = v
        else:
            super(Form, self).__init__(*args, **kwargs)


def pode_vender(function):
    """Decorator que verifica se a loja pode vender e deixa ou não entrar na view"""

    def new(*args, **kwargs):
        request = args[0]
        conta = request.conta
        if not conta.pode_vender():
            return redirect('/')
        return function(*args, **kwargs)
    return new


def login_required(function):
    """
    Decorator for views that checks that the user is logged in, redirecting
    to the log-in page if necessary.
    """
    def new(*args, **kwargs):
        # O request sempre é o primeiro argumento.
        request = args[0]
        # Removendo o parâmetro apelido_conta pois ele é usado apelido no
        # middleware ApiAccess.
        # FIXME: Isto deveria ser colocado em outro decorator, mas deixamos assim
        #        para não ter que colocar um outro decorator em todas as funções.
        if 'apelido_conta' in kwargs.keys():
            del kwargs['apelido_conta']

        # Caso o usuário não esteja autenticado, redireciona para o Login.
        if not request.session.get('autenticado'):
            messages.error(request, 'Você deve estar autenticado para acessar esta página.')
            login_url = settings.APP_LOGIN_URL
            if request.META['PATH_INFO']:
                next = request.META['PATH_INFO']

                if request.META['QUERY_STRING']:
                    next = '%s?%s' % (next, request.META['QUERY_STRING'])

                next = urllib.urlencode({ 'next': next })

                login_url = login_url + '?' + next

            # Troquei o formato do redirect para testar no Safari.
            response = HttpResponse('Location: %s' % login_url, status=302)
            response['Location'] = login_url

            response.delete_cookie('sessionid', path='/', domain='.%s' % request.contrato.dominio)

            response['Pragma'] = 'no-cache'
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate, proxy-revalidate, max-age=0'
            return response

        return function(*args, **kwargs)
    return new


def revenda_required(function):
    """
    Decorator for views that checks that the user is logged in, redirecting
    to the log-in page if necessary.
    """
    def new(*args, **kwargs):
        # O request sempre é o primeiro argumento.
        request = args[0]

        if request.conta.contrato.tipo == 'whitelabel':
            return redirect('painel_index')

        return function(*args, **kwargs)

    return new


def never_cache(function):
    """
    Decorator for views that checks that the user is logged in, redirecting
    to the log-in page if necessary.
    """
    def new(*args, **kwargs):
        request = args[0]
        response = function(*args, **kwargs)

        if not request.session.get('autenticado'):
            # Removendo cookies desnecessários e retirando cache de algumas páginas.
            response.delete_cookie('sessionid', path='/', domain='.%s' % request.contrato.dominio)

        response['Pragma'] = 'no-cache'
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate, proxy-revalidate, max-age=0'

        return response
    return new


class permission_required(object):
    """Com este decorator a view precisa ser acessada por um usuário que
    tenha o mínimo de permissão de acesso para este item. Caso não tenha é
    redirecionado de volta para o referer com uma mensagem de erro.
    """

    def __init__(self, perm, redirect_url=None):
        """
        If there are decorator arguments, the function
        to be decorated is not passed to the constructor!
        """
        self.perm = perm
        self.redirect_url = redirect_url

    def __call__(self, f):
        """
        If there are decorator arguments, __call__() is only called
        once, as part of the decoration process! You can only give
        it a single argument, which is the function object.
        """
        def wrapped_f(*args, **kwargs):
            request = args[0]

            # Caso o usuário não esteja autenticado, redireciona para o Login.
            # if not request.usuario.staff:
            if not request.usuario.has_perm(self.perm):
                msg = 'Você não tem permissão para acessar a página.'
                messages.error(request, msg)

                if self.redirect_url:
                    url = self.redirect_url
                elif request.META.get('HTTP_REFERER'):
                    url = request.META['HTTP_REFERER']
                else:
                    url = '/'
                return redirect(url)

            return f(*args, **kwargs)
        return wrapped_f


class attribute_required(object):
    """Com este decorator a view precisa ser acessada por uma conta com um
    atributo definido e verdadeiro.
    """

    def __init__(self, attr, redirect_url=None):
        """
        If there are decorator arguments, the function
        to be decorated is not passed to the constructor!
        """
        self.attr = attr
        self.redirect_url = redirect_url

    def __call__(self, f):
        """
        If there are decorator arguments, __call__() is only called
        once, as part of the decoration process! You can only give
        it a single argument, which is the function object.
        """
        def wrapped_f(*args, **kwargs):
            request = args[0]

            if request.conta.contrato.tipo_whitelabel and \
                    not getattr(request.conta, self.attr) and \
                            request.conta.contrato_id != 1:
                msg = 'Você não tem permissão para acessar a página.'
                messages.error(request, msg)

                if self.redirect_url:
                    url = self.redirect_url
                elif request.META.get('HTTP_REFERER'):
                    url = request.META['HTTP_REFERER']
                else:
                    url = '/'
                return redirect(url)

            return f(*args, **kwargs)
        return wrapped_f


def staff_required(function):
    """Com este decorator a view precisa ser acessada por um usuário que tenha
    staff definido como tipo. Caso não tenha é redirecionados para index.
    """
    def new(*args, **kwargs):
        # O request sempre é o primeiro argumento.
        request = args[0]

        # Caso o usuário não esteja autenticado, redireciona para o Login.
        if not request.usuario.staff:
            messages.error(request, 'Você não tem permissão para acessar a página.')
            return redirect('/')
        return function(*args, **kwargs)
    return new


def admin_required(function):
    """Com este decorator a view precisa ser acessada por um usuário
    administrador que tenha admin definido como tipo. Caso não tenha é
    redirecionados para index.
    """
    def new(*args, **kwargs):
        # O request sempre é o primeiro argumento.
        request = args[0]

        # Caso o usuário não esteja autenticado, redireciona para o Login.
        if not request.usuario.admin:
            messages.error(request, 'Você não tem permissão para acessar a página.')
            return redirect('/')
        return function(*args, **kwargs)
    return new


def to_database_dict(obj):
    field_names = obj.__class__._meta.get_all_field_names()
    list_names = []

    for x, y in obj.__dict__.items():
        if x in field_names:
            # TODO: necessário quando migrei pro Django 1.7
            if x == 'contrato_id':
                list_names.append(('contrato_id', y))
            else:
                list_names.append((obj.__class__._meta.get_field(x).db_column, y))

    return dict(list_names)


class ContaCancelada(Exception):
    pass


class ContaBloqueada(Exception):
    pass


class UsuarioSemConta(Exception):
    pass


def verificar_contas_usuario(request, usuario):
    """Verifica as contas do usuario"""

    if not usuario.contas.exists():
        raise UsuarioSemConta

    if usuario.contas.filter(situacao='BLOQUEADA').exists():
        raise ContaBloqueada

    if usuario.contas.filter(situacao='CANCELADA').exists():
        usuario.contas.filter(situacao='CANCELADA').update(situacao='ATIVA')
        mensagem = u'Sua loja estava marcada como cancelada, após este seu acesso, voltou a ficar ativa.'
        messages.error(request, mensagem)
        # raise ContaCancelada


def gravar_sessao_login(request, usuario, conta=None):

    if not conta:
        if usuario.staff and not usuario.contas.count():
            from repositories.plataforma.models import Conta
            conta = Conta.objects.get(apelido='integrado')
        else:
            try:
                conta = usuario.contas.filter(situacao__in=['ATIVA'])[0]
            except IndexError:
                return redirect(settings.LOGOUT_URL)

    conta_dict = to_database_dict(conta)
    usuario_dict = to_database_dict(usuario)

    request.session.flush()
    request.session['autenticado'] = True
    request.session['conta'] = conta_dict
    request.session['usuario'] = usuario_dict
    request.session['apelido_conta'] = conta_dict['conta_apelido']

    from repositories.plataforma.models import Conta
    Conta.objects.only("id","ultimo_acesso").filter(id=conta.id).update(ultimo_acesso=datetime.now())

    if usuario.staff and not usuario.contas.count():
        return redirect('super_dashboard')


def atualizar_conta(request):
    """Atualiza a conta atual que está logada e as contas vinculadas."""
    conta_id = request.session['conta']['conta_id']
    # O import deve ser feito aqui para evitar import circular.
    from repositories.plataforma.models import Conta
    conta = Conta.objects.get(pk=conta_id)
    request.session['conta'] = to_database_dict(conta)


def popular_categorias(request, form, campo, raiz=True, null=False, categoria=False):
    """
    Popula as categorias em um form e campo definidos.

    Esta função deve ser usada sempre que for necessário popular categorias
    em um formulário já definido. Além das categorias, o fomrulário recebe uma
    opção 'Raiz', se a variável raiz for True.
    """
    from repositories.catalogo.models import Categoria

    if categoria:
        exclude = [x.id for x in categoria.get_descendants(include_self=True)]
        categorias = Categoria.ordenadas.flat(request.conta.id)
    else:
        categorias = Categoria.ordenadas.flat(request.conta.id)
    if not categorias:
        return None

    # Alterando o conteúdo do fomrulários com as possíveis categorias.
    categorias_choices = []
    if null:
        categorias_choices.append((u'', u'- Vazio -'))

    if raiz:
        categorias_choices.append((u'-', u'[ Raiz ]'))

    for categoria in categorias:
        tracos = u'-- ' * (categoria.level + 1)
        categorias_choices.append(
            (categoria.id, u'%s %s' % (tracos, categoria)))

    if hasattr(form, 'base_field'):
        form.base_fields[campo].choices = categorias_choices
    else:
        form.fields[campo].choices = categorias_choices


def ls_s3(bucket=None, quantidade_maxima=50, prefix=None):
    if not bucket:
        bucket = settings.AWS_S3_BUCKET_IMAGES
    aws = AWS()
    balde = aws.get_balde(bucket)

    last_keys = balde.s3_bucket.get_all_keys(
        max_keys=quantidade_maxima, prefix=prefix)

    return last_keys


def upload_to_s3(f, nome_imagem, bucket=None):
    if not bucket:
        bucket = settings.AWS_S3_BUCKET_IMAGES
    aws = AWS()
    balde = aws.get_balde(bucket)
    return balde.put(f, nome_imagem)


def delete_from_s3(nome_imagem):
    if not nome_imagem:
        return False
    aws = AWS()
    balde = aws.get_balde(settings.AWS_S3_BUCKET_IMAGES)
    return balde.delete(nome_imagem)


def handle_uploaded_file(f, default_extension='jpg'):
    """Gerencia o upload do arquivo para o disco local e retorna o caminho.

    f deve ser um file com atributo f.name que indica o nome do arquivo e
    método f.chunks() para escrever o arquivo no disco.

    Caso o arquivo não tenha extensão, adiciona a extensão padrão que é enviada
    através do parâmetro: default_extension.
    """
    # Caso não exista extensão no arquivo, é adicionada a extensão padrão.
    filename = f.name
    if '.' not in filename:
        filename = '%s.%s' % (f.name, default_extension)

    # Envia o arquivo para o disco.
    file_path = os.path.join(TEMPORARY_FOLDER, filename)
    if isinstance(file_path, unicode):
        file_path = file_path.encode('utf-8')
    destination = open(file_path, 'wb+')
    for chunk in f.chunks():
        destination.write(chunk)
    destination.seek(0)
    destination.close()

    # Retorna somente o caminho do arquivo.
    return file_path


def nome_generico_para_imagem(nome=None, tamanho=10):
    if not nome:
        nome = random.sample(string.letters + string.digits, 10)
        extensao = 'jpg'
    else:
        if '.' in nome:
            nome, extensao = nome.rsplit('.', 1)
        else:
            extensao = 'jpg'

    hora = str(datetime.now())
    if isinstance(nome, unicode):
        nome = nome.encode('utf-8')
    novo_nome = sha1('%s-%s' % (hora, nome)).hexdigest()[:tamanho]
    novo_nome = '%s.%s' % (novo_nome, extensao)
    return novo_nome


def upload_file(f, caminho_base, substituir_nome=True, converter_para=None, bucket=None, nome=None, remover_no_final=True):
    """Faz upload de uma imagem para um caminho base dentro do S3."""
    if isinstance(f, InMemoryUploadedFile) or \
            isinstance(f, TemporaryUploadedFile):
        path = handle_uploaded_file(f)
        f = open(path, 'r')
    elif isinstance(f, file):
        path = os.path.join(TEMPORARY_FOLDER, f.name)


    mime_types = {
        'JPEG': 'jpg',
        'PNG': 'png'
    }

    nome_arquivo = f.name.split('/')[-1]
    # Evita que o arquivo seja gravado com algum caracter acentuado.
    nome_arquivo = normalize('NFKD', nome_arquivo.decode('utf-8')).encode('ASCII','ignore')
    ext = nome_arquivo.split('.')[-1]

    if substituir_nome:
        if nome:
            nome_arquivo = nome
        else:
            nome_arquivo = nome_generico_para_imagem(f.name)

    if converter_para:
        img = Image.open(path)
        bg = Image.new('RGB', img.size, (255, 255, 255))
        try:
            bg.paste(img, (0, 0), img)
        except ValueError:
            img = Image.open(path).convert('RGBA')
            bg.paste(img, (0, 0), img)
        bg.save(path, converter_para, quality=80)
        nome_arquivo = nome_arquivo.replace(
            ext, mime_types.get(converter_para, 'jpg'))
        f = open(path, 'r')

    nome_imagem = '%s%s' % (caminho_base, nome_arquivo)
    upload_to_s3(f, nome_imagem, bucket=bucket)

    f.close()

    # Removendo o arquivo.
    try:
        os.unlink(f.name)
    except:
        # Ignorando caso não consiga remover o arquivo.
        pass

    logger.debug('Image uploaded to %s.' % nome_imagem)
    return nome_imagem


def guess_mime_type(file):
    mime_type, encoding = mimetypes.guess_type(file)
    return mime_type


def resize_and_upload_file(f, caminho_base, tamanho):
    """Faz upload de uma imagem redimensionada para um caminho base dentro
    do S3.

    f - Arquivo do Django em memória ou temporário para ser enviado
        para o handle_uploaded_file().
    caminho_base - Define o caminho para onde o arquivo vai ser enviado.
    tamanho - Tamanho em uma tupla com largura x altura. Ex: (300, 300)

    Esta função pemite que o usuário envie qualquer tipo de imagem. Se o
    usuário enviar um PNG, este formato será respeitado.
    """
    if isinstance(f, InMemoryUploadedFile) or \
            isinstance(f, TemporaryUploadedFile):
        path = handle_uploaded_file(f)

        # Redimensiona a imagem.
        image = Image.open(path)
        if image.size[0] > tamanho[0] or image.size[1] > tamanho[1]:
            image.thumbnail(tamanho, Image.ANTIALIAS)
            try:
                image.save(path, quality=90)
            except KeyError:
                try:
                    image.save(path, format='JPEG', quality=90)
                except IOError:
                    image.convert('RGB').save(path, format='JPEG', quality=90)
        f = open(path)
    return upload_file(f, caminho_base)


def upload_logo_file(f, conta_id):
    """Faz upload de uma logo para um caminho base dentro do S3.

    Todas as logos enviadas através desta função são redimensionadas para
    300x300px. Esta função pemite que o usuário envie qualquer tipo de imagem.
    Se o usuário enviar um PNG, este formato será respeitado.
    """
    caminho_base = '%s/%s/logo/' % ((conta_id/1000),conta_id)
    return resize_and_upload_file(f, caminho_base, (600, 600))


def upload_favicon_file(f, conta_id):
    """Faz upload de um favicon para um caminho base dentro do S3.

    Todos os favicons são enviados através desta função são redimensionadas
    para 128x128px. Esta função pemite que o usuário envie qualquer tipo de
    imagem. Se o usuário enviar um PNG, este formato será respeitado.
    """
    caminho_base = '%s/%s/favicon/' % ((conta_id/1000),conta_id)
    if f.name.upper().endswith('.ICO'):
        return upload_file(f, caminho_base)
    return resize_and_upload_file(f, caminho_base, (128, 128))


def delete_uploaded_file(nome_imagem):
    delete_from_s3(nome_imagem)
    return True


def delete_temp_files(data):
    """
    Delete all temp files from the request session.

    This function is used to remove all garbage created from temporary folder.
    """
    for k, v in data.items():
        try:
            os.remove(os.path.join(TEMPORARY_FOLDER, v.name))
        except Exception, e:
            logger.error('ERROR: Trying to remove file. %s' % e)


def send_sqs_message(nome_fila, message):
    aws = AWS()
    fila = aws.get_fila(nome_fila)
    return fila.send_message(message)


def prepend_http(url):
    """Coloca o protocolo http: na frente da URL caso ela comece com //."""
    if url.startswith(u'//'):
        url = u'http:%s' % url
    return url


def prepend_https(url):
    """Coloca o protocolo https: na frente da URL caso ela comece com //."""
    if url.startswith(u'//'):
        url = u'https:%s' % url
    return url


def enviar_email(request, template_file=None, context=None, cliente_id=None, usuario_id=None, pedido_venda_id=None, countdown=0, to_email=None, reply_to=None, salva_evidencia=True):

    # Se o desenvolvimento for loca, nao envia email
    # if settings.ENVIRONMENT == 'local':
    #     return True

    if hasattr(request, 'conta'):
        conta_id = request.conta.id
    else:
        conta_id = None

    # Verifica se a loja eh PRO
    if (hasattr(request, 'plano_vigente') and hasattr(request.plano_vigente, 'content') and request.plano_vigente.content.plano.indice > 1) or \
            request.GET.get('pro') or request.POST.get('pro'):

        if context is not None:
            context['pro'] = True
        else:
            context = { 'pro': True }

    send_email(
        template_file=template_file,
        context=context,
        cliente_id=cliente_id,
        pedido_venda_id=pedido_venda_id,
        conta_id=conta_id,
        contrato_id=request.contrato.id,
        usuario_id=usuario_id,
        countdown=countdown,
        salva_evidencia=salva_evidencia,
        to_email=to_email,
        reply_to=reply_to
    )

    return True



def validar_tipo_desconto(tipo, valor):
    """ Faz a validação e retorna um boleano"""
    if tipo != 'frete_gratis' and not valor:
        return False
    if tipo == 'porcentagem' and float(valor) > 100:
        return False
    return True


def validar_validade_cupom(data):
    """ Valida a data do cupom de desconto """
    if data:
        if isinstance(data, date):
            data = datetime.combine(data, time.min)
        if data < datetime.now():
            return False
    return True


def contar_objetos(objetos, contar=True, somar=False, campo='id', modo=None):
    """ Retorna um dicionario com as datas e suas respectivas
    quantidades de objetos """
    if modo == 'mes':
        data_string = '%Y-%m-30'
    elif modo == 'ano':
        data_string = '%Y'
    else:
        data_string = '%Y-%m-%d'

    saida = OrderedDict()
    for obj in objetos:
        data = obj.data_criacao.date().strftime(data_string)
        if contar:
            if data in saida.keys():
                saida[data] += 1
            else:
                saida[data] = 1
        elif somar:
            if data in saida.keys():
                saida[data] += obj.__dict__.get(campo)
            else:
                saida[data] = obj.__dict__.get(campo)
        else:
            saida[data] = obj.__dict__.get(campo)
    return saida


def range_datas(inicio, fim, inverse=False):
    # se forem datetime tem que transformar em date.
    if isinstance(fim, datetime):
        fim = fim.date()
    if isinstance(inicio, datetime):
        inicio = inicio.date()
    tdelta = fim - inicio
    saida = []
    for i in range(0, tdelta.days):
        if inverse:
            data = inicio + timedelta(days=i)
        else:
            data = fim - timedelta(days=i)
        saida.append(data.strftime('%Y-%m-%d'))
    return saida


class JSONCSS(object):

    data = {}
    fields = {
        'cabecalho': '#header',
        'conteudo': '#body',
        'geral': 'body',
        'rodape': '#footer',
        'color_1': '.color1',
        'color_2': '.color2',
        'color_3': '.color3',
        'color_4': '.color4',
        'inner': '.inner'
    }

    body_class = {
        'botao_gradiante': 'btn-gradient',
        'cantos_arrendondados': 'content-radius'
    }
    css = {}

    def __init__(self, *args, **kwargs):
        self.data = {}
        self.css = {}
        if kwargs:
            self.parse_data(*args, **kwargs)
            for key, value in self.data.items():
                self.texto_color(key, value)
                self.background_repeat(key, value)
                self.background_position(key, value)
                self.background_color(key, value)
                self.background_imagem(key, value)
        self.opcoes_produto(kwargs)
        self.tipo_layout(kwargs)
        self.opcoes_body(kwargs)
        self.opcoes_categoria(kwargs)

    def parse_data(self, *args, **kwargs):
        for key, value in kwargs.items():
            name_split = key.split('__')
            element = ' '.join(name_split[:-1])
            if not value:
                continue
            if len(element) >= 2:
                if self.data.get(element):
                    self.data[element].update({name_split[-1]: value})
                else:
                    self.data[element] = {name_split[-1]: value}
            else:
                self.data[name_split[0]] = value

    def to_css(self):
        saida = []
        for k, v in self.css.items():

            if not isinstance(v, list):
                saida.append('%s {%s}' % (k, v))
            else:
                saida.append('%s {%s}' % (k, ' '.join([x for x in v])))
        return '\n'.join(saida)

    def opcoes_produto(self, kwargs):

        if 'botao_compra' in kwargs.keys():
            if kwargs['botao_compra'] == 'nao':
                self.css['.prod-info a.btn-small'] = 'display: none;'
            return True
        return False

    def texto_color(self, key, value):

        if key.startswith('color_'):
            self.css[self.fields.get(key)] = 'color: %s;' % value

    def tipo_layout(self, kwargs):

        if kwargs.get('tipo_layout') == 'fixo' and kwargs.get('width_layout_fixo'):
            self.css['.fixo .wrapper'] = 'width: %spx;' % kwargs.get('width_layout_fixo')

    def opcoes_body(self, kwargs):

        for k in self.body_class:
            if self.data.get(k):
                if not self.data.get('body_classes'):
                    self.data['body_classes'] = ''
                self.data['body_classes'] += ' %s' % self.body_class[k]

    def opcoes_categoria(self, kwargs):
        if 'estilo_categoria' in kwargs.items():
            self.data['estilo_categoria'] = kwargs.get('estilo_categoria')
            return True
        return False

    def populate(self, key):
        if not key.split(' ') > 1:
            if not self.css.get(self.fields[key]):
                self.css[self.fields[key]] = []
                return self.fields[key]
        else:
            k = ''
            for v in key.split(' '):
                k += ' %s' % self.fields[v]
            if not self.css.get(k):
                self.css[k] = []
            return k

    def background_repeat(self, key, value):
        if isinstance(value, dict):
            kv = self.populate(key)
            for k, v in value.items():
                if k == 'background_repeat':
                    self.css[kv].append('background-repeat: %s;' % v)

    def background_position(self, key, value):
        position = []
        if isinstance(value, dict):
            kv = self.populate(key)
            for k, v in value.items():
                if k == 'background_align_horizontal' or k == 'background_align_vertical':
                    position.append(v)
            if position:
                self.css[kv].append('background-position: %s;' % ' '.join(position))

    def background_color(self, key, value):
        if isinstance(value, dict):
            kv = self.populate(key)
            for k, v in value.items():
                if k == 'background_cor':
                    self.css[kv].append('background-color: %s;' % v)

    def background_imagem(self, key, value):
        if isinstance(value, dict):
            kv = self.populate(key)
            for k, v in value.items():
                if k == 'background_imagem':
                    if v:
                        self.css[kv].append('background-image: url("%s");' % v)
                    else:
                        self.css[kv].append('background-image: none;')

    def from_json(self, json_string):
        try:
            data_json = json.loads(json_string)
        except:
            return None
        else:
            self.parse_data(**data_json)
            return self

    def to_json(self):
        return json.dumps(self.data)

    def clean(self):
        dados = []
        for key, value in self.data.items():
            if isinstance(value, dict):
                for k, v in value.items():
                    if 'inner' in key:
                        dados.append(('%s__inner__%s' % (key.split(' ')[0], k), v))
                    else:
                        dados.append(('%s__%s' % (key, k), v))
            else:
                if key != 'principal':
                    dados.append((key, value))
        return dados


class ErroValidacao(Exception):
    pass

class validar_xls(object):
    """Verifica o arquivo XLS e o compara e o valida diante do padrão
    estabelecido.

    1 Célula: Nome da Região | [a-zA-Z.-]
    2 Célula: CEP inicio | [0-9]{5}-[0-9]{3}
    3 Célula: CEP FIM | [0-9]{5}-[0-9]{3}
    4 Célula: Peso inicio | Decimal
    5 Célula: Peso FIM | Decimal
    6 Célula: Valor | Decimal
    7 Célula: Prazo | Inteiro
    8 Célula: Ad Valorem | [0-9]+%? < 100 (sempre considerar como porcentagem)
        | NOT REQUIRED
    9 Célula: Kg adicional | Decimal | NOT REQUIRED"""
    PADRAO_TOTAL_ROWS = 9
    arquivo_xls = None
    resultados = {}

    REGIAO_INDEX = 0
    CEP_INICIO_INDEX = 1
    CEP_FIM_INDEX = 2
    PESO_INICIO_INDEX = 3
    PESO_FIM_INDEX = 4
    VALOR_INDEX = 5
    PRAZO_INDEX = 6
    AD_VALOREM_INDEX = 7
    KG_ADICIONAL_INDEX = 8
    ErroValidacao = ErroValidacao

    def __init__(self, arquivo_xls):
        self.arquivo_xls = arquivo_xls

    def validar_row(self, row, row_number):
        if len(row) != self.PADRAO_TOTAL_ROWS:
            return None
        # os validadores em sua respeciva ordem: Ver docstring.
        validadores = [
            self.validar_nome, self.validar_cep, self.validar_cep,
            self.validar_decimal, self.validar_decimal, self.validar_decimal,
            self.validar_inteiro, self.validar_porcentagem,
            self.validar_decimal_not_required
        ]

        d = []
        total_validadores = len(validadores)
        for n in xrange(0, total_validadores):
            # criando o indice
            validacao = validadores[n](row[n].value)
            d.append(validacao)
            if validacao is False:
                raise self.ErroValidacao(
                    'Houve um erro duranto o processamento do arquivo na linha: %s, coluna: %s.' % \
                    (row_number + 1, self._coluna(n)))
        self.resultados.setdefault(row[self.REGIAO_INDEX].value, []).append(d)
        return True

    def validar_cep(self, cep):
        if isinstance(cep, float):
            cep = '%08d' % int(cep)
        cep = unicode(cep)
        digitos = ''.join([x for x in cep if x.isdigit()])
        if re.match('^\d{8}$', digitos):
            return digitos
        return False


    def _coluna(self, coluna):
        ALFABETO = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O',
                    'P','Q','R','S','T','U','V','W','X','Y','Z']
        n = coluna
        if coluna == 0:
            return ALFABETO[0]
        digitos = []
        while n > 0:
            n, mod = divmod(n, len(ALFABETO))
            if len(digitos) <= 4:
                digitos.append(ALFABETO[mod])
            else:
                break
        digitos.reverse()
        return ''.join(digitos)

    def validar_inteiro(self, inteiro):
        try:
            inteiro = int(inteiro)
        except:
            return False
        return inteiro

    def validar_decimal(self, numero):
        if not numero:
            return 0
        try:
            numero = Decimal(repr(numero))
        except:
            return 0
        return numero

    def validar_decimal_not_required(self, peso):
        if not peso:
            return None
        try:
            peso = Decimal(repr(peso))
        except:
            return False
        return peso

    def validar_nome(self, nome):
        if not isinstance(nome, basestring):
            try:
                nome = str(nome)
            except:
                return False
        if len(nome) > 128:
            return False
        return nome

    def validar_porcentagem(self, porcentagem):
        if not porcentagem:
            return None
        if isinstance(porcentagem, basestring) and '%' in porcentagem:
            try:
                porcentagem = Decimal(repr(float(porcentagem.replace('%', ''))))
            except:
                return False
        if porcentagem > 100:
            return False
        return Decimal(repr(porcentagem))

    def is_valid(self):

        # sempre tem que ser a primeira página
        pagina = self.arquivo_xls.sheet_by_index(0)
        total_row = pagina.nrows - 1
        # ignora sempre a primeira row
        nrow = 0
        while nrow < total_row:
            nrow += 1
            row = pagina.row(nrow)
            if not self.validar_row(row, nrow):
                return False
        return True

    def kg_adicional(self, regiao):
        kg_adicional = 0
        for dados in self.resultados[regiao]:
            if dados[self.KG_ADICIONAL_INDEX]:
                kg_adicional = dados[self.KG_ADICIONAL_INDEX]
                break
        return kg_adicional

    def ad_valorem(self, regiao):
        ad_valorem = 0
        for dados in self.resultados[regiao]:
            if dados[self.AD_VALOREM_INDEX]:
                ad_valorem = dados[self.AD_VALOREM_INDEX]
                break
        return ad_valorem

    def importar(self, configuracao_transportadora):
        """ usa os dados para fazer o import para a configuracao_transportadora """
        from repositories.configuracao.models import EnvioRegiao, EnvioFaixaCEP, EnvioFaixaPeso
        conta = configuracao_transportadora.conta

        for regiao in self.resultados:
            ceps_ja_adicionados = []
            pesos_ja_adicionados = []
            regiao_model = EnvioRegiao.objects.create(
                nome=regiao, conta=conta,
                forma_envio=configuracao_transportadora.forma_envio,
                forma_envio_configuracao=configuracao_transportadora,
                kg_adicional=self.kg_adicional(regiao),
                ad_valorem=self.ad_valorem(regiao))

            for dados in self.resultados[regiao]:
                cep_hash = '%s-%s' % (dados[self.CEP_INICIO_INDEX], dados[self.CEP_FIM_INDEX])
                peso_hash = '%s-%s-%s' % (dados[self.PESO_INICIO_INDEX], dados[self.PESO_FIM_INDEX], regiao_model.id)
                if cep_hash not in ceps_ja_adicionados:
                    try:
                        faixa_cep = EnvioFaixaCEP.objects.create(
                            regiao=regiao_model, conta=conta,
                            forma_envio=configuracao_transportadora.forma_envio,
                            cep_inicio=dados[self.CEP_INICIO_INDEX],
                            cep_fim=dados[self.CEP_FIM_INDEX],
                            forma_envio_configuracao=configuracao_transportadora,
                            prazo_entrega=dados[self.PRAZO_INDEX])
                    except Exception as e:
                        pass
                    else:
                        ceps_ja_adicionados.append(cep_hash)
                if peso_hash not in pesos_ja_adicionados:
                    faixa_peso = EnvioFaixaPeso.objects.create(
                        regiao=regiao_model, conta=conta,
                        forma_envio=configuracao_transportadora.forma_envio,
                        peso_inicio=dados[self.PESO_INICIO_INDEX],
                        peso_fim=dados[self.PESO_FIM_INDEX],
                        forma_envio_configuracao=configuracao_transportadora,
                        valor=dados[self.VALOR_INDEX])
                    pesos_ja_adicionados.append(peso_hash)
        return True


def formatar_cep(cep):
    """
    Formata CEP.

    >>> formatar_cep('01301000')
    '01301-000'
    >>> formatar_cep('59152100')
    '59152-100'
    >>> formatar_cep(1301000)
    '01301-000'
    >>> formatar_cep('01234')
    '00001-234'
    >>> formatar_cep(None)
    None
    """

    if isinstance(cep, int):
        cep = str(cep)

    if not cep:
        return cep

    if len(cep) < 8:
        cep = cep.rjust(8, '0')

    # Telefone sem DDD.
    if len(cep) == 8 and cep.isdigit():
        return '%s-%s' % (cep[:5], cep[5:])
    else:
        return cep


def url_painel_de_controle(request):
    """Retorna True caso a URL acessada seja do painel de controle."""
    if not request.META.get('HTTP_HOST'):
        raise Http404

    dominio = request.META.get('HTTP_HOST').split(':')[0]
    dominio = re.sub(r'^www\.', '', dominio)
    dominio_split = dominio.split('.')
    subdominio = dominio_split[0]

    if 'lojaintegrada.com.br' in dominio and subdominio == 'app':
        return True
    else:
        return False


# ---
# UTILS DA LOJA
# ---


def TR(request, template, variables, *args, **kwargs):
    """TemplateResponse sobrescrita para adicionar o path do template"""
    # O template geral fica fora do tema selecionado.
    if not template.startswith('geral'):
        apelido = request.loja['tema']['apelido']
        if apelido in ['v0', 'v1']:
            apelido = 'estrutura/' + apelido
        if apelido in ['v0.1', 'v0.2']:
            apelido = 'estrutura/v0'
        template = apelido + template
    return TemplateResponse(request, template, variables, *args, **kwargs)


def gravar_login_cliente(request, cliente):
    request.session['cliente_autenticado'] = True
    request.session['cliente_id'] = cliente.id
    request.session['cliente_email'] = cliente.email
    request.session['cliente_nome'] = cliente.nome
    from repositories.cliente.models import ClienteFavorito
    try:
        favorito = ClienteFavorito.objects.get(
            conta_id=request.conta.id, cliente_id=cliente.id)
    except ClienteFavorito.DoesNotExist:
        pass
    else:
        request.session['favoritos'] = favorito.id_produtos()
    request.session.modified = True


def logar_cliente(request, email, senha, show_message=True):
    """Loga o cliente na loja."""
    from repositories.cliente.models import Cliente
    def hash_senha(senha):
        return hashlib.md5(senha).hexdigest()

    try:
        senha_hash = hash_senha(senha)
    except UnicodeEncodeError:
        senha_hash = hash_senha(senha.encode('utf-8'))
    if email:
        email = email.lower()
    try:
        cliente = Cliente.objects.get(email__iexact=email, senha=senha_hash,
                                      conta=request.conta)
    except Cliente.DoesNotExist:
        if show_message:
            messages.error(request, u'O email ou senha não conferem.')
        return False

    if show_message:
        messages.success(request, u'Cliente autenticado com sucesso.')
    if not cliente.autorizado():
        if cliente.situacao == Cliente.CLIENTE_SITUACAO_PENDENTE:
            raise ClienteNaoAutorizado(u'Seu cadastro ainda não foi autorizado pela nossa equipe.')
        else:
            raise ClienteNaoAutorizado(u'Seu cadastro não foi autorizado pela nossa equipe.')
    gravar_login_cliente(request, cliente)
    return True


def deslogar_cliente(request):
    """Desloga o cliente na loja."""
    request.session['cliente_autenticado'] = False
    request.session['cliente_id'] = None
    request.session['cliente_email'] = None

    request.session.flush()
    request.session.set_expiry(1)


def digits(s, decimal=False, decimal_length=2):
    """
    Return only the digits of the string.

    >>> digits('10.000')
    10000
    >>> digits('R$ 10,00')
    1000
    >>> digits('R$ 10,00', decimal=True)
    10.0
    >>> digits('R$ 10,00', decimal=True, decimal_length=3)
    1.0
    """
    i = int(''.join(re.findall(r'\d+', s)))
    if decimal and decimal_length:
        i = i / (10.0 ** decimal_length)

    return i


def popular_choice_field(objetos, form, campo, null=False):
    """
    Popula campos de um Choice Field.

    objetos - Lista de tuplas que será usada para popular o form.
    form - Form que será populado.
    campo - Campo do Form que será populado.
    null - Se o Choice Field aceitará valor nulo (será incluído "- Vazio -").
    """
    if type(objetos) != list:
        raise ValueError(u'objetos deve ser uma lista.')

    choices = []
    if null:
        choices.append((u'', u'- Vazio -'))

    for o in objetos:
        choices.append((o[0], o[1]))

    if hasattr(form, 'base_field'):
        form.base_fields[campo].choices = choices
    else:
        form.fields[campo].choices = choices


def verificar_quantidade_estoque(request, produto, quantidade):
    # se existir uma chave ignora a verificação de estoque

    if request.session.get('chave'):
        return True
    if not produto:
        return False
    if produto.estoque.situacao_em_estoque < 0:
        messages.error(request, u'O produto está indisponível e não pode ser adicionada no carrinho')
        return False
    if produto.estoque.quantidade_disponivel() < quantidade and produto.estoque.situacao_sem_estoque < 0:
        messages.error(request, u'A quantidade que você escolheu excede a quantidade disponível no estoque.')
        return False
    return True


def aninhar_categorias(categorias):
    copia = list(categorias)
    for categoria in copia:
        categoria.categorias_filhas = []


        for categoria_filha in copia:

            if categoria_filha.parent_id and categoria_filha.parent_id == categoria.id:
                categoria.categorias_filhas += [categoria_filha]

    return [x for x in copia if not x.parent_id]

def flat_categorias(categorias):
    flat = []
    for categoria in categorias:
        flat += [categoria]
        if hasattr(categoria, 'categorias_filhas'):
            flat += flat_categorias(categoria.categorias_filhas)
    return flat


def primeiro_dia_do_mes(d):
    """Retorna o último dia do mês da data enviada."""
    return d.replace(day=1)


def ultimo_dia_do_mes(d):
    """Retorna o último dia do mês da data enviada."""
    ultimo_dia = calendar.monthrange(d.year, d.month)[1]
    return d.replace(day=ultimo_dia)


def adicionar_mes(d, n, limite_dia_28=False):
    """Adiciona n meses na data d.

    Se a flag limite_dia_28 for True e a data inicial tiver o dia maior que
    28, ela será reduzida para o dia 28 dos meses subsequentes.

    Por exemplo, data inicial 29/01/2013, adicionando 1 mês com a flag
    limite_dia_28=True, retorna 28/02/2013.
    """
    month = d.month - 1 + n
    year = d.year + month / 12
    month = month % 12 + 1

    day = min(d.day, calendar.monthrange(year, month)[1])
    if limite_dia_28 and day > 28:
        day = 28

    return date(year, month, day)


def proximo_vencimento(data_inicio):
    """Define o próximo vencimento baseado na quantidade de dias do mês."""
    qtd_dias_mes = calendar.monthrange(data_inicio.year, data_inicio.month)[1]
    return data_inicio + timedelta(qtd_dias_mes)


def adicionar_dias_uteis(data_inicio, dias_uteis):
    """Adiciona uma quantidade dias úteis em uma determinada data."""
    data_final = data_inicio
    for i in range(1, dias_uteis + 1):
        data_final = data_final + timedelta(1)
        if data_final.isoweekday() > 5:
            data_final = data_final + timedelta(8 - data_final.isoweekday())
    return data_final


def subtrair_dias_uteis(data_inicio, dias_uteis):
    """Subtrai uma quantidade dias úteis em uma determinada data."""
    data_final = data_inicio
    for i in range(1, dias_uteis + 1):
        data_final = data_final - timedelta(1)
        if data_final.isoweekday() > 5:
            data_final = data_final - timedelta(data_final.isoweekday() - 5)
    return data_final


def calcular_valor_proporcional(data_inicio, data_fim, data_processamento,
                                valor):
    """Calcula o valor proporcional para as devidas data (regra de três).

    data_inicio: Primeiro dia do mês
    data_fim: Último dia do mês
    data_processamento: Data do início da assinatura
    valor: Valor total do mês
    """
    if not data_inicio:
        data_inicio = primeiro_dia_do_mes(data_processamento)
    if not data_fim:
        data_fim = ultimo_dia_do_mes(data_processamento)

    msg_excessao = u'%s não pode ser maior que %s.'
    if data_inicio > data_fim:
        raise ValueError(msg_excessao % (u'data_inicio', u'data_fim'))
    elif data_processamento > data_fim:
        raise ValueError(msg_excessao % (u'data_processamento', u'data_fim'))
    elif valor < 0:
        raise ValueError(u'valor não pode ser negativo.' % type(valor))

    # Trasnformando o valor para decimal, para não dar
    # problema na multiplicação.
    valor = Decimal(valor)

    dias_totais = Decimal((data_fim - data_inicio).days + 1)
    dias_proporcionais = Decimal((data_fim - data_processamento).days + 1)
    valor_final = valor * (dias_proporcionais / dias_totais)
    return valor_final


def mercadolivre_status(value):
    """Tradução dos status do Mercadolivre"""
    statuses = {
        'unanswered': 'Não Respondida',
        'answered': 'Respondida',
        'closed_unanswered': 'Anuncio finalizado',
        'under_review': 'Revisando',
        'confirmed': 'Pendente',
        'payment_required': 'Aguardando Pagamento',
        'payment_in_process': 'Em análise',
        'paid': 'Pago',
        'cancelled': 'Cancelado',
        'questions': 'Perguntas',
        'orders': 'Vendas',
        'items': 'Anúncio',
        'success': 'Finalizado com sucesso',
        'info': 'Aviso',
        'aberto': 'Pendente',
        'active': 'Ativo',
        'paused': 'Pausado',
        'closed': 'Finalizado',
        'not_yet_active': 'Em processamento',
        'under_review': 'Sendo revisado',
        'inactive': 'Inativo',
        'payment_required': 'Necessário pagamento',
        'relist': 'Relistando'

    }
    if not isinstance(value, basestring):
        return ''
    if len(value.split('/')) > 1:
        if value.split('/')[1] in statuses:
            return value.split('/')[-1]
    if value.lower() in statuses:
        return statuses[value.lower()]
    return value


def validar_cartao_credito(number):
    """Validates any credit card number using LUHN method.

    From: http://code.activestate.com/recipes/577838-credit-card-validation/
    """
    # Each digit in number as an int in reverse order.
    numlist = [int(c) for c in reversed(str(number)) if c.isdigit()]
    count = 0

    for i, val in enumerate(numlist):
        if i % 2 == 0:
            count += val
        else:
            count += (2 * val) // 10
            count += (2 * val) % 10

    return (count % 10 == 0)


def criar_xls(nome, dados, conta=None):
    """Cria um xls e retorna a resposta para ser entregue para o usuário"""
    from repositories.django.http import HttpResponse
    import xlwt

    wb = xlwt.Workbook(encoding="UTF-8")
    nome_arquivo = nome.replace(' ', '_')
    pagina = wb.add_sheet(nome)

    n = -1
    # definindo os estilos
    for dado in dados:
        n += 1
        d = -1
        for field in dado:
            d += 1
            # if not field:
            #     field = ' '
            pagina.write(n, d, field)
    if not conta:
        apelido = 'sem-conta'
    else:
        apelido = conta.apelido
    nome_arquivo = '/tmp/%s-%s.xls' % (apelido, nome.replace(' ', '_').lower())
    response = HttpResponse(content_type='application/octet-stream')
    wb.save(response)
    response["Content-Disposition"] = ("attachment; filename=%s" %
                                       os.path.split(nome_arquivo)[1])
    return response



def list_to_xls(nome, dados):
    import xlwt
    wb = xlwt.Workbook(encoding="UTF-8")
    pagina = wb.add_sheet(nome)
    n = -1
    # definindo os estilos
    for dado in dados:
        n += 1
        d = -1
        for field in dado:
            d += 1
            if not field:
                field = 0
            pagina.write(n, d, field)
    return wb

def processar_componentes(dados):
    """Retona todos os items de uma lista
    de listas"""
    componentes = ['conteudo', 'coluna', 'secundaria', 'banner']
    saida = []
    for c in componentes:
        componentes = dados.get(c, {}).get('linhas')
        if componentes:
            if isinstance(componentes, list):
                saida += [item for sublista in componentes for item in sublista]
            else:
                saida += [componentes]
    contagem = {}
    for i in saida:
        if i in contagem:
            contagem[i] += 1
        else:
            contagem[i] = 1
    return contagem


def processar_requisitos(conta):
    """Processa os requisitos para o layout da conta
    preencher todos os dados que necessita
    """
    layout = conta.layout()

    # pegando as partes interessantes
    componentes_usados = processar_componentes(layout)

    fullbaner_modulo = layout.get('fullbanner', {}).get('sidebar')

    if layout.get('fullbanner'):
        componentes_usados['fullbanner'] = True
    if fullbaner_modulo:
        componentes_usados['fullbanner_modulo'] = fullbaner_modulo

    return componentes_usados


class ArquivoInvalido(Exception):
    pass


@contextmanager
def medir_tempo(titulo):
    t1 = time_2.time()
    yield
    t2 = time_2.time()
    print str('%s: %0.2f seconds elapsed') % (titulo, t2 - t1)


def formatar_telefone(value):
    """
    Formata telefone.

    >>> formatar_telefone('31514021')
    '3151-4021'
    >>> formatar_telefone('954831232')
    '95483-1232'
    >>> formatar_telefone('1131514021')
    '(11) 4321-1234'
    >>> formatar_telefone('11954831232')
    '(11) 95483-1232'
    >>> formatar_telefone('11.95.48.31.23-2xx')
    '(11) 95483-1232'
    """
    if not value:
        return value

    value = ''.join([x for x in value if x.isdigit()])

    # Telefone sem DDD.
    if len(value) <= 9:
        return '%s-%s' % (value[:-4], value[-4:])
    elif len(value) <= 11:
        return '(%s) %s-%s' % (value[:2], value[2:-4], value[-4:])
    else:
        return value


def calcular_porcentagem(value_1, value_2):
    """Retorna o valor percentual dos dois valores, sendo o primeiro valor
    considerado 100%."""
    try:
        if not value_1:
            value_1 = 0
        if not value_2:
            value_2 = 0
        return (float(value_2) / float(value_1) * 100)
    except ZeroDivisionError:
        return 0


# -----------------------
# CARRINHO.
# -----------------------

def adicionar_produto_carrinho(request, produto, quantidade=None):
    """Adiciona o produto no carrinho com a quantidade definida."""
    produto_id = produto.id

    # quantidade atual + 1, a função espera a quantidade desejada para
    # fazer as verificações.
    # Ex: atual = 2 + 1, em estoque = 3, ou seja, compra válida.
    if not quantidade:
        quantidade = 1

    if verificar_quantidade_estoque(request, produto, quantidade):
        # Se o carrinho não existe, é criado um vazio na sessão.
        if request.session.get('carrinho') == None:
            request.session['carrinho'] = {}

        # Se o produto não estiver no carrinho, é colocado todos os
        # dados do produto na sessão.
        if produto_id not in request.session['carrinho']:
            request.session['carrinho'][produto_id] = produto
            request.session['carrinho'][produto_id].quantidade = 0

        # Incrementa quantidade.
        if quantidade:
            request.session['carrinho'][produto_id].quantidade = quantidade
        else:
            request.session['carrinho'][produto_id].quantidade += 1

        from repositories.catalogo.models import Produto
        if produto.tipo == Produto.TIPO_OPCAO:
            imagem = produto.imagem()
            if isinstance(imagem, dict):
                if not 'carrinho_imagens' in request.session:
                    request.session['carrinho_imagens'] = {}
                request.session['carrinho_imagens'][produto_id] = imagem
                request.session.modified = True

        atualizar_carrinho(request)
        return request.session['carrinho'][produto_id]
    else:
        return False


def remover_produto_carrinho(request, produto_id):
    """Remove um produto do carrinho."""
    try:
        del request.session['carrinho'][produto_id]
    except KeyError:
        pass
    atualizar_carrinho(request)


def atualizar_carrinho(request):
    """Atualiza os totais do carrinho."""
    sess = request.session
    carrinho = sess.get('carrinho')

    # Sem carrinho esta função não faz nada.
    if carrinho is None:
        return

    # Caso haja carrinho criado, são adicionadas informações de somatório
    # relacionadas aos produtos no carrinho.

    # (Re-)inicializando os dados do carrinho na sessão.
    sess['carrinho_subtotal'] = Decimal('0.00')
    sess['carrinho_quantidade'] = 0
    sess['carrinho_peso'] = Decimal('0.00')

    produtos_ids = carrinho.keys()
    if not produtos_ids:
        sess['carrinho'] = {}
        return

    from repositories.catalogo.models import Produto
    produtos = Produto.objects.defer("descricao_completa").filter(
        conta=request.conta,
        pk__in=produtos_ids)

    produtos_ids_removidos = [x for x in produtos_ids if x not in \
                              [y.id for y in produtos]]
    for produto_id_removido in produtos_ids_removidos:
        del sess['carrinho'][produto_id_removido]

    for produto in produtos:
        # Guardando a quantidade para não sobrescrever.
        quantidade = sess['carrinho'][produto.id].quantidade

        # Verifica se a quantidade escolhida do produto tem disponível
        # no estoque, caso não tenha, tenta com 1.
        verificacao_quantidade = verificar_quantidade_estoque(
            request, produto, quantidade)

        # Atualizando o produto no carrinho.
        sess['carrinho'][produto.id] = produto

        # Recolocando a quantidade.
        if not verificacao_quantidade:
            # Caso não tenha a quantidade verificada tenta novamente com apenas 1.
            # Pode ser que o produto tenha sido vendido e o estoque acacbou...
            if not verificar_quantidade_estoque(request, produto, 1):
                del sess['carrinho'][produto.id]
                continue
            quantidade = 1

        sess['carrinho'][produto.id].quantidade = quantidade
        sess['carrinho'][produto.id].estoque.quantidade_loja = quantidade

        if produto.id in sess.get('carrinho_imagens', {}):
            sess['carrinho'][produto.id].imagem = \
                sess['carrinho_imagens'][produto.id]

        produto_atributo_opcao = (produto.tipo == 'atributo_opcao')
        if produto_atributo_opcao:
            produto_pai = produto.pai
            produto.grade_variacao = produto.produto_grades_variacoes.all()

        preco = (produto.preco.promocional or produto.preco.cheio)
        if isinstance(preco, float):
            preco = Decimal(repr(preco))
        if produto.quantidade < 1 or (not produto_atributo_opcao and not preco):
            del sess['carrinho'][produto.id]
            continue

        # Subtotal do produto. Quantidade multiplicado por preço.
        sess['carrinho'][produto.id].subtotal = (preco or 0) * produto.quantidade

        # Adicionando aos subtotais do carrinho.
        sess['carrinho_subtotal'] += (preco or 0) * produto.quantidade
        sess['carrinho_peso'] += (produto.peso or 0) * produto.quantidade
        sess['carrinho_quantidade'] += produto.quantidade
    sess.modified = True


def guardar_carrinho_no_banco(request):
    from repositories.pedido.models import Carrinho, CarrinhoProduto
    try:
        with transaction.atomic():
            kw = dict(conta_id=request.conta.id)
            if request.session.get('cliente_autenticado'):
                kw['cliente_id'] = request.session['cliente_id']
            carrinho = Carrinho.objects.create(**kw)

            for produto_id, produto in request.session['carrinho'].items():
                CarrinhoProduto.objects.create(
                    carrinho=carrinho, produto_id=produto_id,
                    quantidade=produto.quantidade, conta=request.conta)
    except IntegrityError as e:
        return None
    else:
        return carrinho

def converter_mercadolivre_id(valor, reverso=False):
    """Alguns itens do mercado livre contem caracteres inválidos para o id/http-post
    esta função faz a conversão entre eles para um formato válido"""
    if reverso:
        return valor.replace('---', '/')
    return valor.replace('/', '---')


class NossoEmailField(CharField):
    """Override do emailfield padrao do DJANGO para não aceitar
    underline, pois a receita não aceita emails com underline"""
    default_error_messages = {
        'invalid': 'Digite um endereço de email válido.',
    }
    default_validators = [validators.validate_email]

    def clean(self, value):
        value = self.to_python(value).strip()
        # commetando como medida provisória
        # ja que não se sabe se pode ou não ter underline
        # nos emails da receita/prefeitura
        # if '_' in value:
        #     raise ValidationError(u'E-mail inválido.')
        return super(NossoEmailField, self).clean(value)


def calcular_desconto(subtotal, frete=None, cupom=None, forma_envio_configuracao=None):
    """
    Calcula o desconto baseado no subtotal e frete e nas configurações do cupom
    e Forma de Envio
    """

    desconto_pedido = 0
    desconto_frete = 0
    desconto_forma_pagamento = 0
    desconto_cupom = 0

    if cupom:
        if cupom.tipo == cupom.TIPO_FRETE_GRATIS:
            desconto_frete += frete
        elif cupom.tipo == cupom.TIPO_VALOR_FIXO and not cupom.aplicar_no_total:
            desconto_pedido += Decimal('%.2f' % cupom.valor)
        elif cupom.tipo == cupom.TIPO_PORCENTAGEM:
            desconto_pedido += cupom.calcular_porcentagem(subtotal, cupom.valor)
            # Calcula tambem sobre o frete.
            if cupom.aplicar_no_total:
                desconto_frete += cupom.calcular_porcentagem(frete, cupom.valor)

        desconto_cupom = desconto_pedido + desconto_frete

    if forma_envio_configuracao and forma_envio_configuracao.desconto_valor:
        if cupom and not cupom.cumulativo:
            pass
        else:
            valor_base_pedido = subtotal - desconto_pedido
            valor_base_frete = frete - desconto_frete

            if forma_envio_configuracao.desconto_tipo == 'porcentagem':
                # Só para ter o valor no final
                desconto_forma_pagamento = forma_envio_configuracao.calcular_porcentagem(
                    valor_base_pedido, forma_envio_configuracao.desconto_valor)
                desconto_pedido += desconto_forma_pagamento

                if forma_envio_configuracao.aplicar_no_total:
                    desconto_forma_pagamento += forma_envio_configuracao.calcular_porcentagem(
                        valor_base_frete, forma_envio_configuracao.desconto_valor)
                    desconto_frete += forma_envio_configuracao.calcular_porcentagem(
                        valor_base_frete, forma_envio_configuracao.desconto_valor)

            elif forma_envio_configuracao.desconto_tipo == 'fixo' and not forma_envio_configuracao.aplicar_no_total:
                desconto_pedido += forma_envio_configuracao.desconto_valor

    valor_total = (subtotal - Decimal(desconto_pedido)) + frete
    if desconto_frete:
        valor_total -= Decimal(desconto_frete)

    return {
        'desconto_cupom': desconto_cupom,
        'desconto_forma_pagamento': desconto_forma_pagamento,
        'desconto_total': desconto_cupom + desconto_forma_pagamento,
        'total': valor_total
    }


def validar_contrato_correios(servico, codigo, senha):
    cep_origem, cep_destino = '01301000', '59152100'

    c = Correios(cep_origem)
    c.adicionar_forma_envio(servico, cep_destino, codigo_contrato=codigo, senha_contrato=senha, item_id='123')
    c.adicionar_item(5, 5, 5, 0.10)

    # Sempre será retornado apenas 1 item.
    try:
        retorno = c.calcular_frete()[0]
    except IndexError:
        return False, u"O Sistema dos correios não respondeu corretamente. Por favor, tente de novo."
    if retorno.get('msg_erro'):
        return False, retorno.get('msg_erro')
    return True, u'Os dados foram validados com sucesso.'


def to_ascii(texto):
    """Remove qualquer acentuação e qualquer caractere estranho."""
    try:
        return normalize('NFKD', texto.decode('utf-8')).encode('ASCII', 'ignore')
    except UnicodeEncodeError:
        return normalize('NFKD', texto).encode('ASCII', 'ignore')

def clean_string(texto):
    """Limpa a string deixando apenas números, letras."""
    texto = to_ascii(texto)
    caracteres_ok = r'[^a-zA-Z0-9\ \-\.\,]'
    return re.sub(caracteres_ok, '', texto)


def arredondar_listagem(produtos_linha, por_pagina):
    """
    Pega a quantidade de produtos por linha
    e arredonda para baixo dependendo da quantidade
    passada na variavel por_pagina
    """
    if isinstance(por_pagina, basestring):
        try:
            por_pagina = int(por_pagina)
        except:
            por_pagina = 25
    restante = divmod(por_pagina, produtos_linha)[1]
    return por_pagina - restante

TAMNANHOS_BANNER = {
    'fullbanner': '1140,1140',
    'tarja': '1140,1448',
    'vitrine': '1140,850',
    'sidebar': '360,1140',
    'esquerda': '360,1140',
    'minibanner': '360,270'
}


def imagem_url(imagem=None, tamanho="380,380", banner=None, caminho=None):
    if imagem:
        if isinstance(imagem, dict):
            caminho = imagem.get('caminho')
        else:
            caminho = imagem.caminho
    if banner:
        caminho = banner.caminho
        tamanho = TAMNANHOS_BANNER[banner.local_publicacao]
    largura, altura = tamanho.split(',')
    return u'{}{}x{}/{}'.format(settings.MEDIA_URL, largura, altura, caminho)


def calcular_visitas_esperadas(plano_vigente):
    ciclo_tempo_percorrido = plano_vigente['ciclo_tempo_percorrido']
    ciclo_tempo_restante = plano_vigente['ciclo_tempo_restante']
    controle_visitas = plano_vigente['controle_visitas']
    ciclo_tempo_total = ciclo_tempo_percorrido + ciclo_tempo_restante

    if ciclo_tempo_percorrido:
        return (ciclo_tempo_total * controle_visitas) / ciclo_tempo_percorrido
    else:
        return 0


def encontrar_melhor_plano(planos, plano_vigente):
    controle_visitas = plano_vigente['plano']['controle_visitas']
    visitas_esperadas = calcular_visitas_esperadas(plano_vigente)

    if visitas_esperadas > controle_visitas:
        try:
            return [p for p in planos if p['controle_visitas'] > visitas_esperadas][0]
        except IndexError:
            return None
    else:
        return None

def retornar_planos_mostrar(request, planos, todos=False):
    plano_indice = request.plano_vigente['content']['plano']['indice']
    #pro = bool(request.GET.get('pro', '')) or request.conta.origem_pro
    pro = None

    if todos:
        return planos

    if pro:
        if plano_indice >= 5:
            return planos[3:9]
        else:
            return planos[1:7]
    else:
        if plano_indice >= 5:
            return planos[:1] + planos[4:9]
        else:
            return planos[:6]

def retornar_faixas_cep(uf):
    FAIXAS = {
        'AC': { 'cep_inicio': 69900000, 'cep_fim': 69999999 },
        'AL': { 'cep_inicio': 57000000, 'cep_fim': 57999999 },
        'AM': [
            { 'cep_inicio': 69000000, 'cep_fim': 69299999 },
            { 'cep_inicio': 69400000, 'cep_fim': 69899999 },
        ],
        'AP': { 'cep_inicio': 68900000, 'cep_fim': 68999999 },
        'BA': { 'cep_inicio': 40000000, 'cep_fim': 48999999 },
        'CE': { 'cep_inicio': 60000000, 'cep_fim': 63999999 },
        'DF': [
            { 'cep_inicio': 70000000, 'cep_fim': 72799999 },
            { 'cep_inicio': 73000000, 'cep_fim': 73699999 },
        ],
        'ES': { 'cep_inicio': 29000000, 'cep_fim': 29999999 },
        'GO':  [
            { 'cep_inicio': 72800000, 'cep_fim': 72999999 },
            { 'cep_inicio': 73700000, 'cep_fim': 76799999 },
        ],
        'MA': { 'cep_inicio': 65000000, 'cep_fim': 65999999 },
        'MG': { 'cep_inicio': 30000000, 'cep_fim': 39999999 },
        'MS': { 'cep_inicio': 79000000, 'cep_fim': 79999999 },
        'MT': { 'cep_inicio': 78000000, 'cep_fim': 78899999 },
        'PA': { 'cep_inicio': 66000000, 'cep_fim': 68899999 },
        'PB': { 'cep_inicio': 58000000, 'cep_fim': 58999999 },
        'PE': { 'cep_inicio': 50000000, 'cep_fim': 56999999 },
        'PI': { 'cep_inicio': 64000000, 'cep_fim': 64999999 },
        'PR': { 'cep_inicio': 80000000, 'cep_fim': 87999999 },
        'RJ': { 'cep_inicio': 20000000, 'cep_fim': 28999999 },
        'RN': { 'cep_inicio': 59000000, 'cep_fim': 59999999 },
        'RO': { 'cep_inicio': 76800000, 'cep_fim': 76999999 },
        'RR': { 'cep_inicio': 69300000, 'cep_fim': 69399999 },
        'RS': { 'cep_inicio': 90000000, 'cep_fim': 99999999 },
        'SC': { 'cep_inicio': 88000000, 'cep_fim': 89999999 },
        'SE': { 'cep_inicio': 49000000, 'cep_fim': 49999999 },
        'SP': { 'cep_inicio': 01000000, 'cep_fim': 19999999 },
        'TO': { 'cep_inicio': 77000000, 'cep_fim': 77999999 },
    }

    return FAIXAS[uf]

def empacota_excecao(e):
    """
    :param excecao: A exceção a ser emacotada
    :return: Um dicionário com o conteúdo formatado com a exceção
    :rtype: dict
    """
    import sys
    import traceback
    stack_trace = None
    exc_type, exc_value, trace_back = sys.exc_info()
    try:

        if exc_type:
            stack_trace = traceback.format_exception(exc_type, exc_value, trace_back)
            # nome_exec = excecao.__class__.__name__
    except:
        pass

    return stack_trace


def extrai_dados_produto(produto):
    if produto.preco.promocional:
        preco = float(produto.preco.promocional)
    elif produto.preco.cheio:
        preco = float(produto.preco.cheio)
    else:
        preco = float(1)

    return {
        'id': produto.id, 'sku': produto.sku, 'quantity': 0,
        'prices': [{'type': 'boleto', 'price': preco, 'installment': 1, 'installmentValue': preco}]
    }


def desativar_integracao_buscape(conta_id, app_token, auth_token, produtos):
    params = {
        'conta_id': conta_id,
        'configuracao': {
            'app_token': app_token,
            'auth_token': auth_token
        }
    }

    produtos = [extrai_dados_produto(produto) for produto in produtos]

    total = len(produtos)

    while total > 0:
        params['produtos'] = json.dumps(produtos[:1000])

        WorkerConnect().execute('buscape.atualizacao_de_inventario', 'delay', args=params)

        del produtos[:1000]
        total = len(produtos)
