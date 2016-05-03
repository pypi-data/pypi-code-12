import json
import logging
import types
from functools import wraps

import urllib3
import sys


class Remotipy(object):
    http = urllib3.PoolManager(10, None, maxsize=15)


def _remote_call(endpoint, models, extras, method, *params):
    """
    Private method: execute the remote method
    :param endpoint:
    :param models:
    :param extras:
    :param method:
    :param params:
    :return:
    """
    method_params = []

    for i in range(0, len(params)):
        method_params.append(params[i])
    req = {'method': method, 'params': method_params}

    logging.debug("REQUEST GET: " + endpoint)
    logging.debug("BODY: " + str(req))
    headers = {}
    if 'headers' in extras:
        headers = extras['headers']

    body = json.dumps(req, default=_object_serializer)

    logging.debug("RAW Request body: " + str(body))

    r = Remotipy.http.request('POST', endpoint,
                                     headers=headers,
                                     body=body)
    content = r.data

    try:
        return json.loads(content, object_hook=lambda x: _object_deserializer(models, x))
    except ValueError:
        return SerializableException({'cls': 'ValueError',
                                      'message': 'The server response is not a restipy object: ' + content})


def _object_serializer(o):
    """
    Private method: Custom json serializer
    :param o:
    :return:
    """
    if isinstance(o, object) and hasattr(o, '__serializable__'):
        result = {'_class': o.__class__.__name__, '_data': o.__dict__}
        if isinstance(o, SerializableException):
            result['exception'] = True
        return result


# types that do not need complex in json (and not iterable)
primitive = (int, str, bool, float)


def is_primitive(thing):
    return isinstance(thing, primitive)


def _object_deserializer(models_module, obj):
    """
    Private method: Json deserializer
    :param models_module:
    :param obj:
    :return:
    """
    if obj is None or is_primitive(obj) or '_class' not in obj:
        return obj
    else:
        # if it's an exception the DTO is in this module (should be possible only on client side)
        if obj['_class'] == 'SerializableException' and obj['exception']:
            models_module = sys.modules[__name__]

        # get the class reference
        cls = getattr(models_module, obj['_class'])
        # instantiate the object
        result = cls()
        # fill the object
        for k, v in obj['_data'].iteritems():
            setattr(result, k, v)

        return result


def _query_decorator(func, rpc_endpoint, models_module, rpc_extras):
    """
    Private method: Call decorator
    :param func:
    :return:
    """

    is_static = isinstance(func, types.FunctionType)

    @wraps(func)
    def run_query(*v):

        # if not static remove the instance reference (this will not be serialized)
        if not is_static:
            v = tuple(list(v)[1:])

        response_object = _remote_call(
            rpc_endpoint,
            models_module,
            rpc_extras,
            func.__name__, *v)
        # return func(*v)
        if isinstance(response_object, SerializableException):
            raise RemoteException(response_object.message, response_object.cls)
        else:
            return response_object

    return run_query


def remote(endpoint, module, **extras):
    """
    Decorator used to declare a RPC class (class level)
    :param endpoint:
    :param module:
    :param extras:
    :return:
    """

    def decorate(cls):
        cls.__rpc_endpoint__ = endpoint
        cls.__rpc_extras__ = extras
        cls.__models_module__ = module
        for attr in cls.__dict__:
            if callable(getattr(cls, attr)):
                # keep the static / class method definition
                if isinstance(getattr(cls, attr), types.FunctionType):
                    method = staticmethod(_query_decorator(getattr(cls, attr), endpoint, module, extras))
                else:
                    method = _query_decorator(getattr(cls, attr), endpoint, module, extras)

                setattr(cls, attr, method)
        return cls

    return decorate


def serializable(original_class):
    """
    Decorator used to declare a serializable model (class level)
    :param original_class:
    :return:
    """
    orig_init = original_class.__init__

    # This pre-init is called both in standard initialization and from the json-to-object converter
    # (reason why we need support for empty constructor)
    def __init__(self, *args, **kws):
        setattr(original_class, "__serializable__", classmethod(lambda: True))

        try:
            # Call the original __init__
            orig_init(self, *args, **kws)
        except TypeError:
            raise TypeError("Number of arguments error. Does your class <" +
                            original_class.__name__ +
                            "> support empty __init__() call?")

    original_class.__init__ = __init__
    return original_class


def dispatch(controller_class, models_module, params):
    """
    Server side: dispatch the request to the destination method
    :param controller_class:
    :param models_module:
    :param params:
    :return:
    """

    print params
    req = json.loads(params)

    controller_method = req['method']
    params_list_dict = req['params']
    params_list = []
    for i in params_list_dict:
        # TODO: fix this
        obj = json.loads(json.dumps(i), object_hook=lambda x: _object_deserializer(models_module, x))
        params_list.append(obj)

    logging.debug('Calling ' + controller_class.__name__ +
                  '.' + str(controller_method) + '(' +
                  str(params_list) + ')')

    try:

        if not hasattr(controller_class, controller_method):
            raise MethodNotFound(controller_method)

        # is it static?
        if isinstance(getattr(controller_class, controller_method), types.FunctionType):
            method_reference = getattr(controller_class, controller_method)
            print params_list
        else:
            controller = controller_class()
            method_reference = getattr(controller, controller_method)
        return method_reference(*params_list)

    except Exception as e:
        logging.exception(e)
        logging.error('Exception ' + e.__class__.__name__ +
                      ' managed in method ' + controller_method +
                      ": " + e.message)
        return SerializableException({'cls': e.__class__.__name__,
                                      'message': e.message})


def response(obj):
    """
    Format the response compatible with remotipy
    :param obj:
    :return:
    """
    return json.dumps(obj, default=_object_serializer)


@serializable
class SerializableException(object):
    """
    Exception DTO
    """

    def __init__(self, info={}):
        self.cls = info.get('cls')
        self.message = info.get('message')


class MethodNotFound(Exception):
    """
    Raised when the requested method is not present in the remote controller (SERVER SIDE)
    """
    pass


class RemoteException(Exception):
    """
    Raised on the client side if we had an exception on the server
    """

    def __init__(self, message, cls):
        # Call the base class constructor with the parameters it needs
        super(RemoteException, self).__init__(message)
        self.cls = cls

    def __str__(self):
        return self.cls + ": " + self.message
