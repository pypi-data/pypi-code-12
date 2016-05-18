# -*- coding: utf-8 -*-

from b3j0f.conf import Configurable, category
from b3j0f.middleware import fromurl

from link.json import CONF_BASE_PATH

from jsonschema import RefResolver
from jsonpointer import resolve_pointer
import json


@Configurable(
    paths='{0}/resolver.conf'.format(CONF_BASE_PATH),
    conf=category('JSONRESOLVER')
)
class JsonResolver(RefResolver):
    """
    Resolve JSON references.

    See: https://tools.ietf.org/html/draft-pbryan-zyp-json-ref-03
    """

    def __init__(self, base_uri='', referrer=None, **kwargs):
        super(JsonResolver, self).__init__(base_uri, referrer, **kwargs)

        # Just make required parameters optionnal

    def resolve_remote(self, uri):
        try:
            middleware = fromurl(uri)[0]

        except ValueError:
            result = super(JsonResolver, self).resolve_remote(uri)

        else:
            result = json.loads(middleware.get())

            if middleware.fragment:
                result = resolve_pointer(result, middleware.fragment)

            if self.cache_remote:
                self.store[uri] = result

        return result

    def __call__(self, ref):
        """
        Helper method for resolving.

        :return: Resolved reference
        :rtype: any
        """

        return self.resolve(ref)[1]
