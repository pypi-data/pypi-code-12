#!/usr/bin/env python
"""Unit tests for Online CA WSGI Middleware classes and Application.  These are
run using paste.fixture i.e. tests stubs to a web application server
"""
__author__ = "P J Kershaw"
__date__ = "23/09/12"
__copyright__ = "(C) 2012 Science and Technology Facilities Council"
__license__ = "BSD - see LICENSE file in top-level directory"
__contact__ = "Philip.Kershaw@stfc.ac.uk"
__revision__ = '$Id$'
import logging
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger(__name__)

import base64
import os
import unittest

import six

from webob import Response
import paste.fixture
from paste.deploy import loadapp
from paste.httpexceptions import HTTPNotFound

from contrail.security.onlineca.server.wsgi.client_register import \
                                                        ClientRegisterMiddleware
from contrail.security.onlineca.server.test import TEST_DIR, TEST_CA_DIR
from contrail.security.onlineca.server import unicode_for_py3


class TestApp(object):
    """Test WSGI Application for use with the unit tests for the Client Register
    middleware developed for the 
    contrail.security.onlineca.server.app.OnlineCaApp application
    """
    def __init__(self, global_conf, **app_conf):
        """Follow standard Paste Deploy app factory function signature"""
    
    def __call__(self, environ, start_response):
        """Make a simple response for unit test code to trap and validate 
        against.  If this method is executed then the HTTP Basic Auth step in
        the upstream middleware has succeeded.
        """
        response = Response(charset='utf8', 
                            text=six.u(HTTPNotFound.explanation),
                            status=HTTPNotFound.code)

        if environ['PATH_INFO'] == '/auth':
            response.text = six.u('Authenticated!')
            response.status_code = 200        
            
        start_response(response.status, response.headerlist)
        return [response.body]
    
    
class TestClientRegisterMiddleware(unittest.TestCase):
    CONFIG_FILE = 'client_register.ini'
    
    with open(os.path.join(TEST_DIR, 'localhost.crt')) as client_cert_file:
        CLIENT_CERT = client_cert_file.read()
        
    with open(os.path.join(TEST_CA_DIR, 
                           '98ef0ee5.0')) as invalid_client_cert_file:
        INVALID_CLIENT_CERT = invalid_client_cert_file.read()
    
    def setUp(self):
        """Set-up Paste fixture from ini file settings"""
        
        config_filepath = ('config:%s' % self.__class__.CONFIG_FILE)
        wsgiapp = loadapp(config_filepath, relative_to=TEST_DIR)
        self.app = paste.fixture.TestApp(wsgiapp)
            
    def test01_valid_client(self):
        username = b'j.bloggs'
        password = b''
        base64string = base64.encodestring(b'%s:%s' % (username, password))[:-1]
        auth_header =  "Basic %s" % unicode_for_py3(base64string)
        headers = {'Authorization': auth_header}

        environ = {ClientRegisterMiddleware.DEFAULT_SSL_CLIENT_CERT_KEYNAME: 
                   self.__class__.CLIENT_CERT}
        response = self.app.get('/auth', status=200, headers=headers,
                                extra_environ=environ)
        log.debug(response)
        
    def test02_invalid_client_and_username(self):
        username = b'j.bogus'
        password = b''
        base64string = base64.encodestring(b'%s:%s' % (username, password))[:-1]
        auth_header =  "Basic %s" % unicode_for_py3(base64string)
        headers = {'Authorization': auth_header}

        environ = {ClientRegisterMiddleware.DEFAULT_SSL_CLIENT_CERT_KEYNAME: 
                   self.__class__.INVALID_CLIENT_CERT}
        self.app.get('/auth', status=401, headers=headers, 
                     extra_environ=environ)
        
    def test03_invalid_client(self):
        username = b'an_other'
        password = b''
        base64string = base64.encodestring(b'%s:%s' % (username, password))[:-1]
        auth_header =  "Basic %s" % unicode_for_py3(base64string)
        headers = {'Authorization': auth_header}

        environ = {ClientRegisterMiddleware.DEFAULT_SSL_CLIENT_CERT_KEYNAME: 
                   self.__class__.INVALID_CLIENT_CERT}
        self.app.get('/auth', status=401, headers=headers, 
                     extra_environ=environ)
            
    def test04_valid_username(self):
        username = b'asmith'
        password = b''
        base64string = base64.encodestring(b'%s:%s' % (username, password))[:-1]
        auth_header = "Basic %s" % unicode_for_py3(base64string)
        headers = {'Authorization': auth_header}

        environ = {ClientRegisterMiddleware.DEFAULT_SSL_CLIENT_CERT_KEYNAME: 
                   self.__class__.CLIENT_CERT}
        self.app.get('/auth', status=401, headers=headers, 
                     extra_environ=environ)
        
    def test05_unsecured_path(self):
        username = b'asmith'
        password = b''
        base64string = base64.encodestring(b'%s:%s' % (username, password))[:-1]
        auth_header =  "Basic %s" % unicode_for_py3(base64string)
        headers = {'Authorization': auth_header}

        environ = {ClientRegisterMiddleware.DEFAULT_SSL_CLIENT_CERT_KEYNAME: 
                   self.__class__.INVALID_CLIENT_CERT}
        self.app.get('/', status=404, headers=headers, 
                     extra_environ=environ)

