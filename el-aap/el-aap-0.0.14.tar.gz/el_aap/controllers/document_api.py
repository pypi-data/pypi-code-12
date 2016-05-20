__author__ = 'schlitzer'

import json

from bottle import request

from el_aap.app import app, str_id, str_index


@app.post('/_bulk')
@app.post(str_index+'/_bulk')
@app.post(str_index+'/<_type>/_bulk')
def post_bulk(m_aa, m_elproxy, _index=None, _type=None):
    if _index:
        m_aa.require_permission(':index:crud:read', _index)
    for data in request.body.readlines():
        data = json.loads(data.decode('utf8'))
        try:
            index = data['index']['_index']
            m_aa.require_permission(':index:crud:read', index)
        except KeyError:
            continue
    request.body.seek(0)
    return m_elproxy.post()


@app.post(str_index+'/<_type>/')
def post(m_aa, m_elproxy, _index, _type):
    m_aa.require_permission(':index:crud:create', _index)
    return m_elproxy.post()


@app.get('/_mget')
@app.get(str_index+'/_mget')
@app.get(str_index+'/<_type>/_mget')
@app.get('/_mtermvectors')
@app.get(str_index+'/_mtermvectors')
@app.get(str_index+'/<_type>/_mtermvectors')
def get_multi(m_aa, m_elproxy, _index=None, _type=None):
    if _index:
        m_aa.require_permission(':index:crud:read', _index)
    data = list()
    for line in request.body.readlines():
        data.append(line.decode('utf8'))
    data = json.loads(''.join(data))
    if 'docs' in data:
        for doc in data['docs']:
            if '_index' in doc:
                m_aa.require_permission(':index:crud:read', doc['_index'])
    request.body.seek(0)
    return m_elproxy.get()


@app.get(str_index+'/<_type>/_termvectors')
@app.get(str_index+'/<_type>/'+str_id+'/_termvectors')
@app.get(str_index+'/<_type>/'+str_id)
@app.get(str_index+'/<_type>/'+str_id+'/_source')
def get(m_aa, m_elproxy, _index, _type=None, _id=None):
    m_aa.require_permission(':index:crud:read', _index)
    return m_elproxy.get()


@app.delete(str_index+'/<_type>/'+str_id)
def delete(m_aa, m_elproxy, _index, _type, _id):
    m_aa.require_permission(':index:crud:delete', _index)
    return m_elproxy.delete()


@app.put(str_index+'/<_type>/'+str_id)
def put(m_aa, m_elproxy, _index, _type, _id):
    m_aa.require_permission(':index:crud:update', _index)
    return m_elproxy.put()


@app.post(str_index+'/<_type>/'+str_id+'/_update')
def update_scripted(m_aa, m_elproxy, _index, _type, _id):
    m_aa.require_permission(':index:crud:update', _index)
    return m_elproxy.post()
