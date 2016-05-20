__author__ = 'schlitzer'

from el_aap.app import app, str_index


@app.put('/_template/<dummy>')
@app.put('/_warmer')
def admin_put(m_aa, m_elproxy, dummy=None):
    m_aa.require_permission(':', '')
    return m_elproxy.put()


@app.put(str_index+'/_warmer')
@app.put(str_index+'/<_type>/_warmer')
@app.put(str_index)
@app.put(str_index+'/')
@app.put(str_index+'/_mapping/<_type>')
@app.put(str_index+'/_settings')
def put(m_aa, m_elproxy, _index, _type=None):
    m_aa.require_permission(':index:manage:', _index)
    return m_elproxy.put()


@app.post('/_aliases')
@app.post('/_flush')
@app.post('/_forcemerge')
@app.post('/_optimize')
@app.post('/_refresh')
@app.post('/_cache/clear')
def admin_post(m_aa, m_elproxy):
    m_aa.require_permission(':', '')
    return m_elproxy.post()


@app.post(str_index+'')
@app.post(str_index+'/')
@app.post(str_index+'/_cache/clear')
@app.post(str_index+'/_flush')
@app.post(str_index+'/_refresh')
@app.post(str_index+'/_optimize')
@app.post(str_index+'/_upgrade')
@app.post(str_index+'/_close')
@app.post(str_index+'/_open')
@app.post(str_index+'/_forcemerge')
def post(m_aa, m_elproxy, _index):
    m_aa.require_permission(':index:manage:', _index)
    return m_elproxy.post()


@app.delete(str_index+'')
@app.delete(str_index+'/')
@app.delete('/_template/<dummy>')
def delete(m_aa, m_elproxy, _index, dummy=None):
    for index in _index.split(','):
        m_aa.require_permission(':index:manage:', index)
    return m_elproxy.delete()


@app.get('/_aliases')
@app.get('/_analyze')
@app.get('/_mapping')
@app.get('/_segments')
@app.get('/_recovery')
@app.get('/_settings')
@app.get('/_shard_stores')
@app.get('/_stats')
@app.get('/_stats/')
@app.get('/_stats/<dummy:path>')
@app.get('/_template')
@app.get('/_template/')
@app.get('/_template/<dummy>')
@app.get('/_all/_mapping')
@app.get('/_all/_settings')
@app.get('/_all/_settings/<dummy:path')
def admin_get(m_aa, m_elproxy, dummy=None):
    m_aa.require_permission(':', '')
    return m_elproxy.get()


@app.get(str_index)
@app.get(str_index+'/')
@app.get(str_index+'/_aliases')
@app.get(str_index+'/_analyze')
@app.get(str_index+'/_segments')
@app.get(str_index+'/_recovery')
@app.get(str_index+'/_shard_stores')
@app.get(str_index+'/_stats')
@app.get(str_index+'/_stats/')
@app.get(str_index+'/_stats/<dummy:path>')
@app.get(str_index+'/_mapping')
@app.get(str_index+'/_mapping/')
@app.get(str_index+'/_mapping/<dummy:path>')
@app.get(str_index+'/_settings')
@app.get(str_index+'/_settings/')
@app.get(str_index+'/_settings/<dummy:path')
@app.get(str_index+'/_warmer')
@app.get(str_index+'/_warmer/')
@app.get(str_index+'/_warmer/<dummy:path>')
@app.get(str_index+'/<dummy>')
def get(m_aa, m_elproxy, _index, dummy=None):
    for index in _index.split(','):
        m_aa.require_permission(':index:manage:monitor', index)
    return m_elproxy.get()
