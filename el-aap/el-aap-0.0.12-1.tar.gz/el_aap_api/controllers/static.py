__author__ = 'schlitzer'
from bottle import static_file

from el_aap_api.app import app
from el_aap_api.errors import StaticPathDisabledError


@app.route('/elaap/static/<filename:path>')
def server_static(m_config, filename):
    if m_config['main']['static_path'] == '':
        raise StaticPathDisabledError
    return static_file(filename, root=m_config['main']['static_path'])
