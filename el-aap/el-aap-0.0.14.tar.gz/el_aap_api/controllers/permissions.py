__author__ = 'schlitzer'
from bottle import request, response
import jsonschema
import jsonschema.exceptions

from el_aap_api.app import app
from el_aap_api.errors import InvalidBody
from el_aap_api.schemas import *


@app.get('/elaap/api/v1/permissions/_search')
def search(m_aa, m_permissions):
    m_aa.require_admin()
    return m_permissions.search(
        _ids=request.query.get('_id', None),
        permissions=request.query.get('permissions', None),
        scope=request.query.get('scope', None),
        roles=request.query.get('roles', None),
        fields=request.query.get('f', None),
        sort=request.query.get('sort', None),
        page=request.query.get('page', None),
        limit=request.query.get('limit', None)
    )


@app.post('/elaap/api/v1/permissions')
def create(m_aa, m_permissions, m_roles):
    m_aa.require_admin()
    payload = request.json
    jsonschema.validate(payload, PERMISSIONS_CREATE, format_checker=jsonschema.draft4_format_checker)
    if 'roles' in request.json:
        if not m_roles.check_ids(request.json['roles']):
            raise InvalidBody('some roles missing')
    else:
        payload['roles'] = []
    if 'description' not in payload:
        payload['description'] = ''
    if 'permissions' not in payload:
        payload['permissions'] = []
    result = m_permissions.create(request.json)
    response.status = 201
    return result


@app.get('/elaap/api/v1/permissions/<permission>')
def get(m_aa, m_permissions, permission):
    m_aa.require_admin()
    return m_permissions.get(permission, request.query.get('f', None))


@app.put('/elaap/api/v1/permissions/<permission>')
def update(m_aa, m_permissions, m_roles, permission):
    m_aa.require_admin()
    jsonschema.validate(request.json, PERMISSIONS_UPDATE, format_checker=jsonschema.draft4_format_checker)
    if 'roles' in request.json:
        if not m_roles.check_ids(request.json['roles']):
            raise InvalidBody('some roles missing')
    return m_permissions.update(permission, request.json)


@app.put('/elaap/api/v1/permissions/<permission>/permissions')
def update_permissions(m_aa, m_permissions, permission):
    m_aa.require_admin()
    if not type(request.json) == list:
        raise InvalidBody("must be of type list")
    schematest = {'permissions': request.json}
    jsonschema.validate(schematest, PERMISSIONS_UPDATE, format_checker=jsonschema.draft4_format_checker)
    return m_permissions.add_permissions(permission, request.json)


@app.put('/elaap/api/v1/permissions/<permission>/roles')
def update_roles(m_aa, m_permissions, m_roles, permission):
    m_aa.require_admin()
    if type(request.json) == list:
        if not m_roles.check_ids(request.json):
            raise InvalidBody('some roles missing')
    else:
        raise InvalidBody("must be of type list")
    return m_permissions.add_roles(permission, request.json)


@app.delete('/elaap/api/v1/permissions/<permission>')
def delete(m_aa, m_permissions, permission):
    m_aa.require_admin()
    return m_permissions.delete(permission)


@app.delete('/elaap/api/v1/permissions/<permission>/permissions')
def delete_permissions(m_aa, m_permissions, permission):
    m_aa.require_admin()
    if not type(request.json) == list:
        raise InvalidBody("must be of type list")
    schematest = {'permissions': request.json}
    jsonschema.validate(schematest, PERMISSIONS_UPDATE, format_checker=jsonschema.draft4_format_checker)
    return m_permissions.remove_permissions(permission, request.json)


@app.delete('/elaap/api/v1/permissions/<permission>/roles')
def delete_roles(m_aa, m_permissions, permission):
    m_aa.require_admin()
    if not type(request.json) == list:
        raise InvalidBody("must be of type list")
    return m_permissions.remove_roles(permission, request.json)
