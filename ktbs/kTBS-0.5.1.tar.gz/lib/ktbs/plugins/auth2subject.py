#    This file is part of KTBS <http://liris.cnrs.fr/sbt-dev/ktbs>
#    Copyright (C) 2011-2012 Pierre-Antoine Champin <pchampin@liris.cnrs.fr> /
#    Universite de Lyon <http://www.universite-lyon.fr>
#
#    KTBS is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    KTBS is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with KTBS.  If not, see <http://www.gnu.org/licenses/>.

"""
This kTBS plugin injects the REMOTE_USER value of the WSGI environment into rdfrest.parameters.

Also, monkeypatch StoredTrace to inject this parameter as the subject of POSTed obsels.
"""

from hashlib import sha1

from ktbs.engine.trace import StoredTrace
from ktbs.namespace import KTBS
from logging import getLogger
from rdflib import Literal
from rdfrest.http_server import \
    register_middleware, unregister_middleware, BOTTOM

LOG = getLogger(__name__)

class Auth2SubjectMiddleware(object):
    #pylint: disable=R0903
    #  too few public methods

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        if environ['REQUEST_METHOD'] == 'POST' \
        and environ['rdfrest.resource'].RDF_MAIN_TYPE == KTBS.StoredTrace \
        and 'REMOTE_USER' in environ:
            environ['rdfrest.parameters']['user'] = environ['REMOTE_USER']
        return self.app(environ, start_response)

salt = ""

old_check_parameters = None

def new_check_parameters(self, to_check, parameters, method):
    """I implement :meth:`ILocalCore.check_parameters`.

    I support the 'user' parameter for 'post_graph'
    """
    LOG.debug("in new_check_parameters %s %s", to_check, method)
    if (method == 'post_graph' or method == 'force_state_refresh') and to_check:
        to_check = [ i for i in to_check if i != 'user' ]
    return old_check_parameters(self, to_check, parameters, method)

old_check_posted_graph = None


def new_check_posted_graph(self, parameters, created, graph):
    """I override :meth:`GraphPostableMixin.check_posted_graph`.

    I set :hasSubject with a hashed version of parameters['user'].
    """
    LOG.debug("in new_check_posted_graph %s", parameters)
    if parameters:
        user = parameters.get('user')
        if user:
            subject = sha1(salt + user).hexdigest()
            graph.set((created, KTBS.hasSubject, Literal(subject)))
        LOG.debug('%s %s -> %s' % (salt, user, subject))
    return old_check_posted_graph(self, parameters, created, graph)



def start_plugin(config):
    LOG.info("plugin started")
    global salt, old_check_parameters, old_check_posted_graph
    if config.has_section('auth2subject') and config.has_option('auth2subject', 'salt'):
        salt = config.get('auth2subject', 'salt', 1)
    # monkey patch StoredTrace untill we have a clean way to extend it
    old_check_parameters = StoredTrace.check_parameters.im_func
    StoredTrace.check_parameters = new_check_parameters
    old_check_posted_graph = StoredTrace.check_posted_graph.im_func
    StoredTrace.check_posted_graph= new_check_posted_graph
    register_middleware(BOTTOM, Auth2SubjectMiddleware)


def stop_plugin():
    if StoredTrace.check_posted_graph.im_func is not new_check_posted_graph \
    and StoredTrace.check_parameters.im_func is not new_check_parameters:
        LOG.warn("StoredTrace or Obsel have been further monkey-patched, "
                 "can not stop plugin")
        return
    StoredTrace.check_parameters = old_check_parameters
    StoredTrcae.check_posted_graph = old_check_posted_graph
    unregister_middleware(Auth2SubjectMiddleware)
    LOG.info("plugin stoped")
