# -*- coding: utf-8 -*-
#
# This file is part of jsonresolver
# Copyright (C) 2015 CERN.
#
# jsonresolver is free software; you can redistribute it and/or
# modify it under the terms of the Revised BSD License; see LICENSE
# file for more details.

"""Module that implements ``JsonLoader`` factory using ``JSONResolver``.

Use ``json_loader_factory`` if you want to take advantage of default
``JsonLoader.get_remote_json`` method for URIs that are not handled
by your ``JSONResolver`` instance.

Example:

.. code-block:: python

   >>> from jsonref import JsonRef
   >>> from jsonresolver import JSONResolver
   >>> from jsonresolver.contrib.jsonref import json_loader_factory
   >>> schema = {'$ref': 'http://localhost:4000/schema/authors.json#'}
   >>> json_resolver = JSONResolver(plugins=['demo.schema'])
   >>> loader_cls = json_loader_factory(json_resolver)
   >>> loader = loader_cls(cache_results=False)
   >>> dict(JsonRef.replace_refs(schema, loader=loader))
   {'type': 'array'}
   # if you do not want default fallback:
   >>> dict(JsonRef.replace_refs(schema, loader=json_resolver.resolve))
   {'type': 'array'}

"""

from __future__ import absolute_import

from jsonref import JsonLoader as _JsonLoader
from werkzeug.exceptions import NotFound


def json_loader_factory(resolver):
    """Generate new ``JsonLoader`` class that uses given resolver."""
    class JsonLoader(_JsonLoader):
        """Implement custom remote reference resolver."""

        def get_remote_json(self, uri, **kwargs):
            """Resolve remove uri using given resolver."""
            try:
                return resolver.resolve(uri)
            except NotFound:
                return super(JsonLoader, self).get_remote_json(uri, **kwargs)

    return JsonLoader
