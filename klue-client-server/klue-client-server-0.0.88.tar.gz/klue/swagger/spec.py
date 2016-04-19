import pprint
import logging
from klue.exceptions import ValidationError
from bravado_core.spec import Spec
from bravado_core.operation import Operation
from bravado_core.marshal import marshal_model
from bravado_core.unmarshal import unmarshal_model


log = logging.getLogger(__name__)


class EndpointData():
    """Just holding some info about an api endpoint"""
    path = None
    method = None
    handler_server = None
    handler_client = None
    decorate_server = None
    decorate_request = None
    operation = None

    param_in_body = False
    param_in_query = False
    param_in_path = False
    no_params = False

    def __init__(self, path, method):
        self.path = path
        self.method = method.upper()

class ApiSpec():
    """Object holding the swagger spec as a YAML dict and a bravado-core Spec object,
    as well as methods for exploring the spec.
    """
    swagger_dict = None
    spec = None
    definitions = None

    host = None
    port = None
    protocol = None
    version = None

    def __init__(self, swagger_dict, formats=None, host=None, port=None):
        self.swagger_dict = swagger_dict

        config = {
            'validate_responses': True,
            'validate_requests': True,
            'validate_swagger_spec': False,
            'use_models': True,
        }

        if formats:
            assert type(formats).__name__ == 'list'
            config['formats'] = formats

        self.spec = Spec.from_dict(self.swagger_dict, config=config)
        self.definitions = self.spec.definitions

        self.host = swagger_dict.get('host', None)
        if not self.host:
            raise Exception("Swagger file has no 'host' entry")
        if host:
            self.host = host

        schemes = swagger_dict.get('schemes', None)
        if 'https' in schemes:
            self.port = 443
            self.protocol = 'https'
        elif 'http' in schemes:
            self.port = 80
            self.protocol = 'http'
        else:
            raise Exception("Swagger schemes contain neither http nor https: %s" % pprint.pformat(schemes))
        if port:
            self.port = port

        self.version = swagger_dict.get('info', {}).get('version', '')


    def model_to_json(self, object):
        """Take a model instance and return it as a json struct"""
        model_name = type(object).__name__
        if model_name not in self.swagger_dict['definitions']:
            raise ValidationError("Swagger spec has no definition for model %s" % model_name)
        model_def = self.swagger_dict['definitions'][model_name]
        log.debug("Marshalling %s into json" % model_name)
        return marshal_model(self.spec, model_def, object)


    def json_to_model(self, model_name, j):
        """Take a json strust and a model name, and return a model instance"""
        if model_name not in self.swagger_dict['definitions']:
            raise ValidationError("Swagger spec has no definition for model %s" % model_name)
        model_def = self.swagger_dict['definitions'][model_name]
        log.debug("Unmarshalling json into %s" % model_name)
        return unmarshal_model(self.spec, model_def, j)


    def call_on_each_endpoint(self, callback):
        """Find all server endpoints defined in the swagger spec and calls 'callback' for each,
        with an instance of EndpointData as argument.
        """

        if 'paths' not in self.swagger_dict:
            return

        for path, d in self.swagger_dict['paths'].items():
            for method, op_spec in d.items():
                data = EndpointData(path, method)

                # Which server method handles this endpoint?
                if 'x-bind-server' not in op_spec:
                    if 'x-no-bind-server' in op_spec:
                        # That route should not be auto-generated
                        log.info("Skipping generation of %s %s" % (method, path))
                        continue
                    else:
                        raise Exception("Swagger api defines no x-bind-server for %s %s" % (method, path))
                data.handler_server = op_spec['x-bind-server']

                # Make sure that endpoint only produces 'application/json'
                if 'produces' not in op_spec:
                    raise Exception("Swagger api has no 'produces' section for %s %s" % (method, path))
                if len(op_spec['produces']) != 1:
                    raise Exception("Expecting only one type under 'produces' for %s %s" % (method, path))
                if 'application/json' not in op_spec['produces']:
                    raise Exception("Only 'application/json' is supported. See %s %s" % (method, path))

                # Which client method handles this endpoint?
                if 'x-bind-client' in op_spec:
                    data.handler_client = op_spec['x-bind-client']

                # Should we decorate the server handler?
                if 'x-decorate-server' in op_spec:
                    data.decorate_server = op_spec['x-decorate-server']

                # Should we manipulate the grequests parameters?
                if 'x-decorate-request' in op_spec:
                    data.decorate_request = op_spec['x-decorate-request']

                # Generate a bravado-core operation object
                data.operation = Operation.from_spec(self.spec, path, method, op_spec)

                # Figure out how parameters are passed: one json in body? one or
                # more values in query?
                if 'parameters' in op_spec:
                    params = op_spec['parameters']
                    for p in params:
                        if p['in'] == 'body':
                            data.param_in_body = True
                        if p['in'] == 'query':
                            data.param_in_query = True
                        if p['in'] == 'path':
                            data.param_in_path = True

                    if data.param_in_path:
                        # Substitute {...} with <...> in path, to make a Flask friendly path
                        data.path = data.path.replace('{', '<').replace('}', '>')

                    if data.param_in_body and data.param_in_query:
                        raise Exception("Cannot support params in both body and param (%s %s)" % (method, path))

                else:
                    data.no_params = True

                callback(data)
