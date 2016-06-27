"""
#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=#
  This file is part of the Smart Developer Hub Project:
    http://www.smartdeveloperhub.org

  Center for Open Middleware
        http://www.centeropenmiddleware.com/
#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=#
  Copyright (C) 2015 Center for Open Middleware.
#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=#
  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at

            http://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.
#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=#
"""
import json

from agora.stoa.client import get_fragment_generator, get_query_generator

from agora.fragments.server import app
from flask import request, jsonify, Response, stream_with_context
from rdflib import Graph

__author__ = 'Fernando Serena'

STOA = app.config['STOA']


class APIError(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


class NotFound(APIError):
    def __init__(self, message, payload=None):
        super(NotFound, self).__init__(message, 404, payload)


class Conflict(APIError):
    def __init__(self, message, payload=None):
        super(Conflict, self).__init__(message, 409, payload)


@app.errorhandler(APIError)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code

    return response


@app.route('/fragment')
def get_fragment():
    def get_quads():
        for prefix in prefixes:
            yield '@prefix {}: <{}> .\n'.format(prefix, prefixes[prefix])
        yield '\n'
        for chunk in fragment_gen:
            if chunk is None:
                yield ''
            else:
                headers, (c, s, p, o) = chunk
                triple = u'{} {} {} .\n'.format(s.n3(graph.namespace_manager), p.n3(graph.namespace_manager),
                                             o.n3(graph.namespace_manager))
                print headers, triple
                yield triple

    gp_str = request.args.get('gp', '{}')
    import re

    try:
        gp_match = re.search(r'\{(.*)\}', gp_str).groups(0)
        if len(gp_match) != 1:
            raise APIError('Invalid graph pattern')

        tps = re.split('\. ', gp_match[0])
        extra_params = {k: request.args.get(k) for k in request.args.keys() if k in ['gen', 'updating', 'events']}
        extra_params['STOA'] = STOA

        prefixes, fragment_gen = get_fragment_generator(*tps, monitoring=30, **extra_params)
        graph = Graph()
        for prefix in prefixes:
            graph.bind(prefix, prefixes[prefix])

        return Response(stream_with_context(get_quads()), mimetype='text/n3')
    except Exception as e:
        raise APIError('There was a problem with the request: {}'.format(e.message), status_code=500)


@app.route('/query')
def query():
    def get_results():
        yield '['
        first_row = True
        for row in result_gen:
            if row is None:
                yield ''
            else:
                row_str = ',\n  {}'.format(json.dumps(row[1]))
                if first_row:
                    row_str = row_str.lstrip(',')
                    first_row = False
                yield row_str
        yield '\n]'

    gp_str = request.args.get('gp', '{}')
    import re

    try:
        gp_match = re.search(r'\{(.*)\}', gp_str).groups(0)
        if len(gp_match) != 1:
            raise APIError('Invalid graph pattern')

        tps = re.split('\. ', gp_match[0])
        extra_params = {k: request.args.get(k) for k in request.args.keys() if k in ['gen', 'updating', 'events']}
        extra_params['STOA'] = STOA
        prefixes, result_gen = get_query_generator(*tps, monitoring=10, **extra_params)

        return Response(stream_with_context(get_results()), mimetype='application/json')
    except Exception as e:
        raise APIError('There was a problem with the request: {}'.format(e.message), status_code=500)

