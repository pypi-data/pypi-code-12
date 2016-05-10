__author__ = 'schlitzer'

from el_aap.app import app


@app.get('/')
def slash(m_aa, m_elproxy, dummy=None):
    m_aa.check_auth()
    return m_elproxy.get()


@app.get('/_cluster')
@app.get('/_cluster/')
@app.get('/_cluster/<dummy:path>')
@app.get('/_cluster/<dummy:path>/')
@app.get('/_nodes')
@app.get('/_nodes/')
@app.get('/_nodes/<dummy:path>')
@app.get('/_nodes/<dummy:path>/')
def get(m_aa, m_elproxy, dummy=None):
    m_aa.require_permission(':cluster:monitor', '')
    return m_elproxy.get()


@app.post('/_cluster')
@app.post('/_cluster/')
@app.post('/_cluster/<dummy:path>')
@app.post('/_cluster/<dummy:path>/')
@app.post('/_nodes')
@app.post('/_nodes/')
@app.post('/_nodes/<dummy:path>')
@app.post('/_nodes/<dummy:path>/')
def post(m_aa, m_elproxy, dummy=None):
    m_aa.require_permission(':cluster:', '')
    return m_elproxy.post()


@app.put('/_cluster')
@app.put('/_cluster/')
@app.put('/_cluster/<dummy:path>')
@app.put('/_cluster/<dummy:path>/')
@app.put('/_nodes')
@app.put('/_nodes/')
@app.put('/_nodes/<dummy:path>')
@app.put('/_nodes/<dummy:path>/')
def put(m_aa, m_elproxy, dummy=None):
    m_aa.require_permission(':cluster:', '')
    return m_elproxy.put()


@app.delete('/_cluster')
@app.delete('/_cluster/')
@app.delete('/_cluster/<dummy:path>')
@app.delete('/_cluster/<dummy:path>/')
@app.delete('/_nodes')
@app.delete('/_nodes/')
@app.delete('/_nodes/<dummy:path>')
@app.delete('/_nodes/<dummy:path>/')
def delete(m_aa, m_elproxy, dummy=None):
    m_aa.require_permission(':cluster:', '')
    return m_elproxy.delete()
