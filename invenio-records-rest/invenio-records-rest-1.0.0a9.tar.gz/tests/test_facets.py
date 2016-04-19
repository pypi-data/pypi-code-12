# -*- coding: utf-8 -*-
#
# This file is part of Invenio.
# Copyright (C) 2015, 2016 CERN.
#
# Invenio is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the
# Free Software Foundation, Inc., 59 Temple Place, Suite 330, Boston,
# MA 02111-1307, USA.
#
# In applying this license, CERN does not
# waive the privileges and immunities granted to it by virtue of its status
# as an Intergovernmental Organization or submit itself to any jurisdiction.


"""Facets tests."""

from __future__ import absolute_import, print_function

from elasticsearch_dsl import Search
from flask import Flask, current_app, request
from invenio_query_parser.contrib.elasticsearch import IQ
from werkzeug.datastructures import MultiDict

from invenio_records_rest.facets import _aggregations, _create_filter_dsl, \
    _post_filter, _query_filter, default_facets_factory, terms_filter


def test_terms_filter():
    """Test terms filter."""
    f = terms_filter('test')
    assert f(['a', 'b']).to_dict() == dict(terms={'test': ['a', 'b']})


def test_create_filter_dsl():
    """Test request value extraction."""
    app = Flask('testapp')
    kwargs = MultiDict([('a', '1')])
    defs = dict(
        type=terms_filter('type.type'),
        subtype=terms_filter('type.subtype'),
    )

    with app.test_request_context('?type=a&type=b&subtype=c'):
        filters, args = _create_filter_dsl(kwargs, defs)
        assert len(filters) == 2
        assert args == MultiDict([
            ('a', '1'),
            ('type', 'a'),
            ('type', 'b'),
            ('subtype', 'c')
        ])

    kwargs = MultiDict([('a', '1')])
    with app.test_request_context('?atype=a&atype=b'):
        filters, args = _create_filter_dsl(kwargs, defs)
        assert not filters
        assert args == kwargs


def test_post_filter(app, user_factory):
    """Test post filter."""
    urlargs = MultiDict()
    defs = dict(
        type=terms_filter('type'),
        subtype=terms_filter('subtype'),
    )

    with app.test_request_context('?type=test'):
        search = Search().query(IQ('value'))
        search, args = _post_filter(search, urlargs, defs)
        assert 'post_filter' in search.to_dict()
        assert search.to_dict()['post_filter'] == dict(
            terms=dict(type=['test'])
        )
        assert args['type'] == 'test'

    with app.test_request_context('?anotertype=test'):
        search = Search().query(IQ('value'))
        search, args = _post_filter(search, urlargs, defs)
        assert 'post_filter' not in search.to_dict()


def test_query_filter(app, user_factory):
    """Test post filter."""
    urlargs = MultiDict()
    defs = dict(
        type=terms_filter('type'),
        subtype=terms_filter('subtype'),
    )

    with app.test_request_context('?type=test'):
        search = Search().query(IQ('value'))
        body = search.to_dict()
        search, args = _query_filter(search, urlargs, defs)
        assert 'post_filter' not in search.to_dict()
        assert search.to_dict()['query']['bool']['must'][0] == body['query']
        assert search.to_dict()['query']['bool']['filter'] == [
            dict(terms=dict(type=['test']))
        ]
        assert args['type'] == 'test'

    with app.test_request_context('?anotertype=test'):
        search = Search().query(IQ('value'))
        body = search.to_dict()
        query, args = _query_filter(search, urlargs, defs)
        assert query.to_dict() == body


def test_aggregations(app, user_factory):
    """Test aggregations."""
    with app.test_request_context(''):
        search = Search().query(IQ('value'))
        defs = dict(
            type=dict(
                terms=dict(field='upload_type'),
            ),
            subtype=dict(
                terms=dict(field='subtype'),
            )
        )
        assert _aggregations(search, defs).to_dict()['aggs'] == defs


def test_default_facets_factory(app, user_factory):
    """Test aggregations."""
    defs = dict(
        aggs=dict(
            type=dict(
                terms=dict(field='upload_type'),
            ),
            subtype=dict(
                terms=dict(field='subtype'),
            )
        ),
        filters=dict(
            subtype=terms_filter('subtype'),
        ),
        post_filters=dict(
            type=terms_filter('type'),
        ),
    )
    app.config['RECORDS_REST_FACETS']['testidx'] = defs

    with app.test_request_context('?type=a&subtype=b'):
        search = Search().query(IQ('value'))
        search, urlkwargs = default_facets_factory(search, 'testidx')
        assert search.to_dict()['aggs'] == defs['aggs']
        assert 'post_filter' in search.to_dict()
        assert search.to_dict(
            )['query']['bool']['filter'][0]['terms']['subtype']

        search = Search().query(IQ('value'))
        search, urlkwargs = default_facets_factory(search, 'anotheridx')
        assert 'aggs' not in search.to_dict()
        assert 'post_filter' not in search.to_dict()
        assert 'bool' not in search.to_dict()['query']
