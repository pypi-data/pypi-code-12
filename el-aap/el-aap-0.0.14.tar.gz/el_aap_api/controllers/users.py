__author__ = 'schlitzer'
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from bottle import request, response
from jinja2 import Template
import jsonschema
import jsonschema.exceptions


from el_aap_api.app import app
from el_aap_api.errors import *
from el_aap_api.schemas import *


@app.get('/elaap/api/v1/users/_search')
def search(m_aa, m_users):
    m_aa.require_admin()
    return m_users.search(
        _ids=request.query.get('_id', None),
        admin=request.query.get('admin', None),
        fields=request.query.get('f', None),
        sort=request.query.get('sort', None),
        page=request.query.get('page', None),
        limit=request.query.get('limit', None)
    )


@app.post('/elaap/api/v1/users/_lostpw')
def lostpw(m_config, m_lostpw, m_users):
    if 'pw_recovery' not in m_config:
        raise LostPWRecoveryDisabledError
    jsonschema.validate(request.json, LOSTPW_REQUEST, format_checker=jsonschema.draft4_format_checker)
    try:
        user = m_users.get(request.json['_id'])
        username = user['name']
        email = user['email']
    except ResourceNotFound:
        return
    token = m_lostpw.create(user['_id'])

    text_tmpl = Template(m_config['pw_recovery']['text_tmpl'])
    html_tmpl = Template(m_config['pw_recovery']['html_tmpl'])
    text_mail = text_tmpl.render(
        api_url=m_config['pw_recovery']['api_url'],
        www_url=m_config['pw_recovery']['www_url'],
        user_id=user, username=username, token=token
    )
    html_mail = html_tmpl.render(
        api_url=m_config['pw_recovery']['api_url'],
        www_url=m_config['pw_recovery']['www_url'],
        user_id=user['_id'], username=username, token=token
    )
    msg = MIMEMultipart('alternative')
    msg['Subject'] = m_config['pw_recovery']['subject']
    msg['From'] = m_config['pw_recovery']['from']
    msg['To'] = email
    msg.attach(MIMEText(text_mail, 'plain'))
    msg.attach(MIMEText(html_mail, 'html'))
    try:
        s = smtplib.SMTP(m_config['pw_recovery']['smtp_host'], m_config['pw_recovery']['smtp_port'])
        s.sendmail(m_config['pw_recovery']['from'], email, msg.as_string())
        s.quit()
    except ConnectionRefusedError as err:
        raise MailServerConnError(err)


@app.put('/elaap/api/v1/users/_lostpw')
def lostpw(m_config, m_lostpw, m_users):
    if 'pw_recovery' not in m_config:
        raise LostPWRecoveryDisabledError
    password = request.json['password']
    token = request.json['token']
    user = m_lostpw.get(token)
    try:
        m_users.update(user, {'password': password})
    except ResourceNotFound:
        raise
    finally:
        m_lostpw.delete(token)


@app.get('/elaap/api/v1/users/<user>')
def get(m_aa, m_users, user):
    if user == '_self':
        user = m_aa.get_user()
    else:
        m_aa.require_admin()
    return m_users.get(user, request.query.get('f', None))


@app.put('/elaap/api/v1/users/<user>')
def update(m_aa, m_users, user):
    payload = request.json
    if user == '_self':
        user = m_aa.get_user()
        payload.pop('admin', None)
    else:
        m_aa.require_admin()
    jsonschema.validate(request.json, USERS_UPDATE, format_checker=jsonschema.draft4_format_checker)
    return m_users.update(user, payload)


@app.delete('/elaap/api/v1/users/<user>')
def delete(m_aa, m_users, m_roles, user):
    if user == '_self':
        user = m_aa.get_user()
    else:
        m_aa.require_admin()
    m_roles.remove_user_from_all(user)
    return m_users.delete(user)


@app.post('/elaap/api/v1/users')
def create(m_aa, m_users):
    m_aa.require_admin()
    jsonschema.validate(request.json, USERS_CREATE, format_checker=jsonschema.draft4_format_checker)
    result = m_users.create(request.json)
    response.status = 201
    return result
