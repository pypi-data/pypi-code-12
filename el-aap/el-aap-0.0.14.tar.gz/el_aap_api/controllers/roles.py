__author__ = 'schlitzer'
from bottle import request, response
import jsonschema
import jsonschema.exceptions

from el_aap_api.app import app
from el_aap_api.errors import InvalidBody
from el_aap_api.schemas import *


@app.get('/elaap/api/v1/roles/_search')
def search(m_aa, m_roles):
    m_aa.require_admin()
    result = m_roles.search(
        _ids=request.query.get('_id', None),
        users=request.query.get('users', None),
        fields=request.query.get('f', None),
        sort=request.query.get('sort', None),
        page=request.query.get('page', None),
        limit=request.query.get('limit', None)
    )
    return result


@app.get('/elaap/api/v1/roles/<role>')
def get(m_aa, m_roles, role):
    m_aa.require_admin()
    result = m_roles.get(role, request.query.get('f', None))
    return result


@app.post('/elaap/api/v1/roles')
def create(m_aa, m_roles, m_users):
    m_aa.require_admin()
    payload = request.json
    jsonschema.validate(payload, ROLES_CREATE, format_checker=jsonschema.draft4_format_checker)
    if 'users' in payload:
        if not m_users.check_ids(payload['users']):
            raise InvalidBody("non existing users selected")
    else:
        payload['users'] = []
    if 'description' not in payload:
        payload['description'] = ''
    result = m_roles.create(request.json)
    response.status = 201
    return result


@app.put('/elaap/api/v1/roles/<role>')
def update(m_aa, m_roles, m_users, role):
    m_aa.require_admin()
    jsonschema.validate(request.json, ROLES_UPDATE, format_checker=jsonschema.draft4_format_checker)
    if 'users' in request.json:
        if not m_users.check_ids(request.json['users']):
            raise InvalidBody("non existing users selected")
    return m_roles.update(role, request.json)


@app.put('/elaap/api/v1/roles/<role>/users')
def update_users(m_aa, m_roles, m_users, role):
    m_aa.require_admin()
    if type(request.json) == list:
        if not m_users.check_ids(request.json):
            raise InvalidBody("non existing users selected")
    else:
        raise InvalidBody("must be of type list")
    return m_roles.add_users(role, request.json)


@app.delete('/elaap/api/v1/roles/<role>')
def delete(m_aa, m_roles, m_permissions, role):
    m_aa.require_admin()
    m_permissions.remove_role_from_all(role)
    return m_roles.delete(role)


@app.delete('/elaap/api/v1/roles/<role>/users')
def delete_users(m_aa, m_roles, role):
    m_aa.require_admin()
    if not type(request.json) == list:
        raise InvalidBody("must be of type list")
    return m_roles.remove_users(role, request.json)
