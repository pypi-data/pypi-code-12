__author__ = 'schlitzer'
from bottle import request, response
import jsonschema
import jsonschema.exceptions

from el_aap_api.app import app
from el_aap_api.schemas import *


@app.post('/elaap/api/v1/authenticate')
def create(m_users, m_sessions):
    jsonschema.validate(request.json, USERS_CREDENTIALS, format_checker=jsonschema.draft4_format_checker)
    user = m_users.check_credentials(request.json)
    result = m_sessions.create(user)
    response.status = 201
    response.set_cookie('sid', result['_id'])
    response.set_cookie('token', result['token'])
    return result


@app.delete('/elaap/api/v1/authenticate')
def delete(m_sessions, m_aa):
    response.delete_cookie('_id')
    response.delete_cookie('token')
    session = m_aa.get_session()
    return m_sessions.delete(session['_id'])


@app.get('/elaap/api/v1/authenticate')
def verify(m_aa):
    return m_aa.get_user()
