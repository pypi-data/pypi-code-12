'''
Copyright (C) 2015-2016 Skylable Ltd. <info-copyright@skylable.com>
License: Apache 2.0, see LICENSE for more details.
'''
from requests.compat import urlencode, quote, quote_plus

from sxclient.tools import toutf8

__all__ = ['QueryParameters']

SAFE_CHARS = ':/-_~'


class QueryParameters(object):
    '''For a given API function, store its query parameters.'''

    def __init__(
        self, sx_verb, path_items=None, bool_params=None, dict_params=None
    ):
        path_items = [] if path_items is None else path_items
        bool_params = set() if bool_params is None else bool_params
        dict_params = {} if dict_params is None else dict_params

        path_items = [toutf8(elt) for elt in path_items]
        bool_params = {toutf8(elt) for elt in bool_params}
        dict_params = {toutf8(key): toutf8(value)
                       for key, value in dict_params.iteritems()}

        self.sx_verb = sx_verb
        self.path_items = path_items
        self.bool_params = bool_params
        self.dict_params = dict_params

    @property
    def path(self):
        path = '/'.join(
            quote(item, safe=SAFE_CHARS) for item in self.path_items
        )
        return path

    @property
    def params(self):
        items_to_join = {quote_plus(item) for item in self.bool_params}
        param_string = urlencode(self.dict_params)
        items_to_join.add(param_string)
        param_string = '&'.join(item for item in items_to_join if item)
        return param_string

    @property
    def verb(self):
        if self.sx_verb.startswith('JOB_'):
            verb = self.sx_verb.split('_', 1)[-1]
        else:
            verb = self.sx_verb
        return verb

    @property
    def is_complex(self):
        if self.sx_verb.startswith('JOB_'):
            is_complex = True
        else:
            is_complex = False
        return is_complex

    @property
    def sx_verb(self):
        return self._sx_verb

    @sx_verb.setter
    def sx_verb(self, value):
        self._sx_verb = value.upper()

    def __repr__(self):
        attr_string_pairs = (
            '%s=%r' % (key, getattr(self, key))
            for key in dir(self)
            if not key.startswith('_')
        )
        attr_string = ', '.join(attr_string_pairs)
        text_repr = '%s(%s)' % (self.__class__.__name__, attr_string)
        return text_repr
