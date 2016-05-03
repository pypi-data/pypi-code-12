__author__ = 'schlitzer'

import json

from bottle import request

from el_aap.app import app, str_index, str_id
from el_aap_api.errors import *


@app.get(str_index+'/<_type>/'+str_id+'/count')
@app.get(str_index+'/<_type>/'+str_id+'/_explain')
@app.get(str_index+'/<_type>/'+str_id+'/_percolate')
@app.get(str_index+'/_count')
@app.get(str_index+'/<_type>/_count')
@app.get(str_index+'/_field_stats')
@app.get(str_index+'/<_type>/_field_stats')
@app.get(str_index+'/_search')
@app.get(str_index+'/<_type>/_search')
@app.get(str_index+'/_search/exists')
@app.get(str_index+'/<_type>/_search/exists')
@app.get(str_index+'/_search_shards')
@app.get(str_index+'/<_type>/_search_shards')
@app.get(str_index+'/_validate/query')
@app.get(str_index+'/<_type>/_validate/query')
def get(m_aa, m_elproxy, _index, _type=None, _id=None):
    for index in _index.split(','):
        m_aa.require_permission(':index:crud:search', index)
    return m_elproxy.get()


@app.post(str_index+'/_count')
@app.post(str_index+'/<_type>/_count')
@app.post(str_index+'/_field_stats')
@app.post(str_index+'/<_type>/_field_stats')
@app.post(str_index+'/_search')
@app.post(str_index+'/<_type>/_search')
@app.post(str_index+'/_search/exists')
@app.post(str_index+'/<_type>/_search/exists')
@app.post(str_index+'/_search_shards')
@app.post(str_index+'/<_type>/_search_shards')
@app.post(str_index+'/_validate/query')
@app.post(str_index+'/<_type>/_validate/query')
def post(m_aa, m_elproxy, _index, _type=None):
    for index in _index.split(','):
        m_aa.require_permission(':index:crud:search', index)
    return m_elproxy.post()


@app.get('/_count')
@app.get('/_field_stats')
@app.get('/_search')
@app.get('/_search/exists')
@app.get('/_validate/query')
def admin_get(m_aa, m_elproxy):
    m_aa.require_permission(':', '')
    return m_elproxy.get()


@app.post('/_count')
@app.post('/_field_stats')
@app.post('/_search')
@app.post('/_search/exists')
@app.post('/_validate/query')
def admin_post(m_aa, m_elproxy):
    m_aa.require_permission(':', '')
    return m_elproxy.post()


@app.get('/_msearch')
@app.get(str_index+'/_msearch')
@app.get(str_index+'/<_type>/_msearch')
@app.get('/_mpercolate')
@app.get(str_index+'/_mpercolate')
@app.get(str_index+'/<_type>/_mpercolate')
def m_search(m_aa, m_elproxy, _index=None, _type=None):
    if _index:
        for index in _index.split(','):
            m_aa.require_permission(':index:crud:search', index)
    header = True
    for data in request.body.readlines():
        if not header:
            header = True
            continue
        try:
            for index in json.loads(data.decode('utf8'))['index'].split(','):
                m_aa.require_permission(':index:crud:search', index)
        except (KeyError, ValueError):
            if not _index:
                raise PermError
        header = False
    request.body.seek(0)
    return m_elproxy.get()
