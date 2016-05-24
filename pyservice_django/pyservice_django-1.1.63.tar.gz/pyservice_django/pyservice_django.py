import copy
import datetime
import importlib
import inspect
import json
import logging
import urllib2
from datetime import date
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives
from django.db import models
from django.db.models.query import QuerySet
from django.http.response import HttpResponse

urls = {}
service_name = 'Service Sample'
service_description = ''
service_version = '1.0'

services = {}

on_before_process = None


def add_route(url, method):
    urls[url] = method


def add_route_service(url, service, uri):
    urls[url] = {'service': service, 'uri': uri}


def add_service(service_name, url):
    services[service_name] = url


def get_service_info():
    return {
        'Service Name': service_name,
        'Description': service_description,
        'Version': service_version,
    }


def post_service(self, service_name, action, params=[]):
    try:
        url = services[service_name]
        url += action
        return post(url, params)
    except Exception as e:
        return {
            "Error making request to service '{0}' action '{1}' ".format(service_name, action)
        }


def post(url, params):
    headers = {'content-type': 'application/json'}
    params = toJson(params)
    try:
        req = urllib2.Request(url, data=params)
        response = urllib2.urlopen(req)
        response = response.read()
        result = toObj(response)
        return result
    except urllib2.URLError:
        raise Exception('INVALID_URL', 'The url {0} was not found'.format(url))
    except Exception as e:
        raise Exception('POST_REQUEST_ERROR', e)


def processa_django_request(request):
    decoded_request = decode_django_request(request)
    return processa_request(decoded_request)


def decode_django_request(request):
    # Get the service requested
    action_requested = request.path

    # PROCESSA OS PARAMETROS
    params = []
    logger = logging.getLogger(__name__)

    if request.method == 'POST':
        params = request.body.decode()
        params = Serializer.json_to_object(params)

    if not params:
        params = []

    if not len(params):
        params = []

    if not isinstance(params, list):
        params = [params]

    return {
        'action': action_requested,
        'params': params,
        'method': request.method,
        'headers': request.META
    }


def processa_request(request):
    action_requested = request.get('action')
    params = request.get('params')

    action = urls.get(action_requested, None)

    # Retorno
    result = {"result": "OK",
              "data": ""}
    try:
        if on_before_process:
            on_before_process()

        if action_requested == '/':
            result = get_service_info()
        elif isinstance(action, dict):  # LOCAL SERVICES OR REMOTE SERVICES
            service_call = action['service']
            uri_call = action['uri']
            result = post_service(None, service_call, uri_call, params)
        elif inspect.isfunction(action) or inspect.ismethod(action):
            result['data'] = action(*params)
        else:
            result['data'] = 'Servico nao encontrado : {0}'.format(action_requested)
            result['result'] = 'ERRO'

        result = Serializer.object_to_json(result)
    except Exception as e:
        result['result'] = 'ERRO'
        result['data'] = {}

        # if got an exception not expected
        if len(e.args) == 1:
            result['data']['code'] = 'NOT_EXPECTED'
            result['data']['message'] = e.args[0]
        else:
            try:
                result['data']['code'] = e.args[0]
            except:
                pass

            try:
                result['data']['message'] = e.args[1]
            except:
                pass

        message = ''

        if 'positional arguments but' in e.message \
                or 'must be a sequence, not NoneType' in e.message \
                or 'positional argument' in e.message:
            message = 'Number of parameters incorrect'

        if not result['data'].get('message', None):
            result['data']['message'] = message
        result = toJson(result)
        logger.error(e.message)
    finally:
        response = HttpResponse()
        response.content_type = 'application/json'
        response.status_code = 200
        response.write(result)

        # response = JsonResponse(result, safe=False)

        return response


def i18n(self, code, params=[]):
    modulo = self.__module__[:self.__module__.rfind('.')]
    modulo = '{0}.i18n.i18n_pt_br'.format(modulo)
    modulo = importlib.import_module(modulo)
    try:
        mensagem = getattr(modulo, code)
    except:
        raise Exception('I18N_NOT_FOUND', 'O codigo de i18n {0} nao foi encontrado!'.format(code))

    if params:
        mensagem = mensagem.format(*params)

    if isinstance(mensagem, str):
        return mensagem.decode('utf-8')

    return ''


def send_mail(self, subject='', body='', from_email=None, to=None, bcc=None,
              connection=None, attachments=None, headers=None, cc=None,
              reply_to=None, html=True):
    if not isinstance(to, (list, tuple)):
        to = [to]

    mail = EmailMultiAlternatives(
        subject=subject,
        # body="This is a simple text email body.",
        from_email=from_email,  # "Yamil Asusta <hello@yamilasusta.com>",
        to=to,
        # headers={"Reply-To": "support@sendgrid.com"}
    )
    mail.attach_alternative(body, "text/html")
    try:
        mail.send()
    except Exception as e:
        raise Exception(e)

        # if not isinstance(to, (list, tuple)):
        #     email_to = [to]
        #
        # conn = mail.get_connection()
        # msg = mail.EmailMessage(subject, body, from_email, to,
        #                         connection=conn)
        # if html:
        #     msg.content_subtype = "text/html"
        #
        # try:
        #     msg.send()
        # except Exception as e:
        #     raise Exception(e)


def config_classes(classes=[], methods=[]):
    """
    This method injects basic functions for djgando model or others functions passed by params
    :param self:
    :param classes:
    :param methods:
    :return:
    """
    if not methods:
        methods = [create, save, delete, query, i18n, send_mail, post_service]

    for classe in classes:
        for method in methods:
            setattr(classe, method.__name__, method)


def create(self):
    obj = self.__class__()
    return obj


def save(self, data=None):
    obj = None
    if data:
        obj = self.__class__()
        for key, value in data.items():
            setattr(obj, key, value)

    try:
        if obj:
            return obj.save()
        else:
            self.full_clean()

    except ValidationError as e:
        message = e.message_dict
        raise Exception('FIELDS_VALIDATION', message)

    super(self.__class__, self).save()
    return self


def delete(self, ids=None):
    if ids:
        if not isinstance(ids, list):
            ids = [ids]

        objs = self.__class__.objects.filter(id__in=ids)
        deleted_records = objs.delete()
        return 'Excluido {0} registros'.format(deleted_records[0])
    return super(self.__class__, self).delete()


def toDjangoFilter(self, filter):
    queryFilter = {}
    # Filtro
    for where in filter.get('where', []):

        field = where.get('field', '')
        value = where.get('value', '')
        condition = ''
        where = []
        # veja se tem asterisco na consulta
        if isinstance(value, (str, unicode)):
            if '*' in value:
                values = value.split('*')
                for v in values:
                    if v:
                        condition = '__contains'
                        value = v
            else:
                condition = '__startswith'

        queryFilter[field + condition] = value

    query = self.__class__.objects.filter(**queryFilter)

    if filter.get('select', []):
        query = query.values(*filter.get('select', []))
    elif self.FIELDS:
        query = query.values(*self.FIELDS)

    query = query.distinct()
    return query


def query(self, filter=None):
    if filter:
        if isinstance(filter, dict):
            return toDjangoFilter(self, filter)
            # return self.__class__.objects.filter(**filter).all()

    return self.__class__.objects.filter(**filter).all()


def del_none(d):
    if isinstance(d, dict):
        return dict((k, v) for k, v in d.items() if v and not k.startswith('_'))

    return None


def normalize_objects(obj):
    def queryset_to_list(queryset):
        retorno = []
        obj = list(queryset)

        for m in obj:
            model = None
            if isinstance(m, models.Model):
                model = model_to_dict(m)
            else:
                model = m

            model = del_none(model)
            retorno.append(model)
        return retorno

    def model_to_dict(obj):
        obj = obj.__dict__
        if hasattr(obj, '_state'):
            del obj['_state']
        obj = del_none(obj)
        obj = normalize_objects(obj)
        return obj

    def object_to_dict(obj):
        if hasattr(obj, '__dict__'):
            return normalize_objects(obj.__dict__)
        return obj

    if isinstance(obj, QuerySet):
        obj = queryset_to_list(obj)

    elif isinstance(obj, models.Model):
        obj = model_to_dict(obj)

    elif isinstance(obj, dict):
        for key, value in obj.items():
            if isinstance(value, (QuerySet, models.Model, dict, list, type, datetime.datetime, date)) or hasattr(value, '__dict__'):
                obj[key] = normalize_objects(value)

    elif isinstance(obj, list):
        for index, value in enumerate(obj):
            if isinstance(value, (QuerySet, models.Model, dict, list, type)) or hasattr(value, '__dict__'):
                obj[index] = normalize_objects(value)

    elif isinstance(obj, (datetime.datetime, date)):  # if the object is a type(class), if it's not an object
        obj = str(obj)

    elif isinstance(obj, type):  # if the object is a type(class), if it's not an object
        obj = None

    obj = object_to_dict(obj)
    if not isinstance(obj, (str, int, float, dict, list, bool)) and obj != None:
        raise ValueError(
            'Could not convert the object {0}. Expected :  str,int,float,dict,list,bool but got : {1}'.format(
                obj.__name__), type(obj))

    return obj


class JsonEncoder(json.JSONEncoder):
    def default(self, obj):
        """
        default method is used if there is an unexpected object type
        in our example obj argument will be Decimal('120.50') and datetime
        in this encoder we are converting all Decimal to float and datetime to str
        """
        if isinstance(obj, (datetime, date, datetime.time)):
            obj = str(obj)
        elif isinstance(obj, Decimal):
            obj = float(obj)
        elif obj == None:
            return None
        else:
            obj = super(JsonEncoder, self).default(obj)
        return obj


class Serializer():
    @classmethod
    def json_to_object(self, json):
        if not json.strip():
            return None

        obj = toObj(json)
        return obj

    @classmethod
    def object_to_json(self, obj):
        newobj = copy.deepcopy(obj)
        newobj = normalize_objects(newobj)
        newobj = toJson(newobj)
        return newobj


def toJson(obj):
    if hasattr(obj, '__dict__'):
        return json.dumps(obj.__dict__, cls=JsonEncoder).encode('utf8')
    else:
        return json.dumps(obj, ensure_ascii=False, cls=JsonEncoder, sort_keys=True)


def toObj(jsonString):
    try:
        obj = json.loads(jsonString, parse_float=Decimal)
        return obj
    except:
        return None
