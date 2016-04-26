import os
import flask
import requests
import pkg_resources as pkr

from scry.utility import SCRYError

SUPPORTED_REQUEST_METHODS = ['get','url-encoded-post'] # Still have to implement 'direct-post'
SUPPORTED_RESPONSE_TYPES  = {'text/csv'                       :'csv',
                             'application/sparql-results+xml' :'xml',
                             'application/sparql-results+json':'json'}
DEFAULT_RESPONSE_TYPE     =  'application/sparql-results+json'

SERVICE_PREFIXES = ''

DEFAULT_QUERY = \
"""PREFIX scry: <http://scry.rocks/>
PREFIX in:   <http://scry.rocks/input?>
PREFIX out:  <http://scry.rocks/output?>
%s
SELECT DISTINCT ?proc ?desc WHERE {
  GRAPH scry:orb_description {
    scry:orb scry:procedure ?proc .
    OPTIONAL{?proc scry:description ?desc .}
  }
} ORDER BY ?proc""" % SERVICE_PREFIXES


get_path = lambda path: pkr.resource_filename('scry',path)
app      = flask.Flask(__name__, static_folder=get_path('resources'),template_folder=get_path(os.path.join('resources','html')))


def update_flask_g(port):
    try:
        print requests.post('http://localhost:%s/update_g' % str(port)).text
    except requests.exceptions.ConnectionError:
        pass


@app.errorhandler(Exception)
def error(e):
    r = flask.Response(e.message)
    r.status_code = int(getattr(e,'code',500))
    return r


@app.before_request
def new_request():
    ip = flask.request.remote_addr
    if ip not in flask.g['allowed_ips']:
        raise SCRYError("This IP address (%s) is not on the queried SCRY orb's whitelist." % ip, 401)
    flask.g['request_count'] += 1


import routes