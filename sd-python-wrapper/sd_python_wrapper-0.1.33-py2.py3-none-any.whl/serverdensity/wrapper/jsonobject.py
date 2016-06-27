try:
    from collections.abc import Mapping
except ImportError:
    from collections import Mapping
try:
    unicode
except NameError:
    unicode = str
import os.path
import json
import sys

from jsonschema import Draft4Validator
from jsonschema import FormatChecker
from jsonschema.compat import str_types
from jsonschema.exceptions import ValidationError

import serverdensity

PY3 = sys.version_info[0] == 3


@FormatChecker.cls_checks(format='mongoId', raises=())
def is_mongoid(instance):
    if not isinstance(instance, str_types):
        return True
    if len(instance) == 24:
        if PY3:
            try:
                bytes.fromhex(instance)
            except ValueError:
                return False
        else:
            try:
                instance.decode('hex')
            except TypeError:
                return False
    else:
        return False

    return True

FORMATCHECKER = FormatChecker()


class JsonObject(Mapping):

    _protected = [
        'values',
        'items',
        'keys',
        'get'
    ]

    _set_internally = [
        'api'
    ]

    _schemapath = ''
    _schemaobj = {}
    _validator = None
    _api = None

    def __init__(self, api=None, *arrgs, **kwargs):
        self._data = {}
        if isinstance(api, dict):
            kwargs.update(api)
        else:
            self.api = api
        if kwargs:
            self._data.update(kwargs)
            self._validation(kwargs)
        if arrgs:
            for arg in arrgs:
                if isinstance(arg, dict):
                    self._data.update(arg)
            self._validation(self._data)

    @property
    def api(self):
        if not self._api:
            raise TypeError('Token or ApiClient must be set to use the Api')
        return self._api

    @api.setter
    def api(self, value):
        if isinstance(value, serverdensity.wrapper.ApiClient):
            self._api = value
        elif isinstance(value, str) or isinstance(value, unicode):
            self._api = serverdensity.wrapper.ApiClient(value)
        elif value is None:
            self._api = None
        else:
            raise TypeError('Must either be a token or an ApiClient')

    def _set_schemaobj(self, path):
        path = os.path.dirname(__file__) + self._schemapath
        with open(path, 'r') as f:
            self._schemaobj = json.load(f)

    def _validation(self, data):
        if not self._schemaobj:
            self._set_schemaobj(self._schemapath)
        if not self._validator:
            self._validator = Draft4Validator(
                schema=self._schemaobj,
                format_checker=FORMATCHECKER
            )
        try:
            self._validator.validate(self._data)
        except ValidationError as e:
            path = ' > '.join(e.relative_schema_path)
            message = 'The schema {} gives the error: {}'.format(
                path, e.message)
            raise AttributeError(message)

    def __iter__(self):
        return (key for key in self._data.keys())

    def __len__(self):
        return len(self._data)

    def __repr__(self):
        return str(self._data)

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        if key in self._protected:
            raise AttributeError('This is a protected property')
        if self._data:
            self._validation(dict(self._data))
            self._data[key] = value

    def __getattr__(self, name):
        attr = self._data.get(name)
        if attr:
            return attr
        else:
            raise AttributeError('Attribute does not exist')

    def __setattr__(self, name, value):
        if name in self._protected:
            raise AttributeError('This is a protected property')

        if name in self._set_internally or name[0] == '_':
            object.__setattr__(self, name, value)
        else:
            self._data[name] = value
            self._validation(self._data)
