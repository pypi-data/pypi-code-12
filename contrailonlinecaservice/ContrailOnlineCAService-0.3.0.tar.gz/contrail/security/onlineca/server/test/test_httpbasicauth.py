#!/usr/bin/env python
"""Unit tests for Online CA service configured with HTTP Basic Auth
"""
__author__ = "P J Kershaw"
__date__ = "21/05/10"
__copyright__ = "(C) 2010 Science and Technology Facilities Council"
__license__ = "BSD - see LICENSE file in top-level directory"
__contact__ = "Philip.Kershaw@stfc.ac.uk"
__revision__ = '$Id: $'
import unittest
import os
import base64

import paste.fixture
from paste.deploy import loadapp
from paste.httpexceptions import HTTPUnauthorized

from contrail.security.onlineca.server import unicode_for_py3
from contrail.security.onlineca.server.wsgi.httpbasicauth import (
                                                HttpBasicAuthMiddleware,
                                                HttpBasicAuthResponseException)


class TestApp(object):
    """Test WSGI Application for use with the unit tests for the HTTP Basic
    Auth middleware developed for the 
    contrail.security.onlineca.server.wsgi.httpbasicauth.HttpBasicAuthMiddleware
    middleware
    """
    def __init__(self, global_conf, **app_conf):
        """Follow standard Paste Deploy app factory function signature"""
    
    def __call__(self, environ, start_response):
        """Make a simple response for unit test code to trap and validate 
        against.  If this method is executed then the HTTP Basic Auth step in
        the upstream middleware has succeeded.
        """
        contentType = 'text/plain'
        response = b'Authenticated!'
        status = '200 OK'
        start_response(status,
                       [('Content-type', contentType),
                        ('Content-Length', str(len(response)))])
        return [response]
    
            
class TestHttpBasicAuthCallBackAppMiddleware(object):
    """Add an authentication function to the environ for HttpBasicAuthMiddleware
    to pick up and use.  It behaves as an application returning a response
    """    
    USERNAME = b'testuser'
    PASSWORD = b'changeme'
    SUCCESS_RESPONSE = 'Authenticated!'
    FAILURE_RESPONSE = 'FAILED'
    
    def __init__(self, app, global_conf, **app_conf):
        """Follow standard Paste Deploy app factory function signature"""
        self.app = app
        
    def __call__(self, environ, start_response):
        def authenticationApp(environ, start_response, username, password):
            """Authentication callback application - its responsible for the
            response message and response code
            """
            if (unicode_for_py3(username) == unicode_for_py3(
                                                self.__class__.USERNAME) and
                unicode_for_py3(password) == unicode_for_py3(
                                                self.__class__.PASSWORD)):
                pass
            else:
                raise HTTPUnauthorized()
            
        environ['HTTPBASICAUTH_FUNC'] = authenticationApp
        
        return self.app(environ, start_response)


class TestHttpBasicAuthCallBackMiddleware(object):
    """Add an authentication function to the environ for HttpBasicAuthMiddleware
    to pick up and use.  The callback does not return a response leaving control
    with the HttpBasicAuthMiddleware
    """    
    USERNAME = b'testuser'
    PASSWORD = b'changeme'
    
    def __init__(self, app, global_conf, **app_conf):
        """Follow standard Paste Deploy app factory function signature"""
        self.app = app
        
    def __call__(self, environ, start_response):
        """Create HTTP Basic Auth callback"""
        def authenticate(environ, start_response, username, password):
            """HTTP Basic Auth callback function"""
            if (unicode_for_py3(username) != self.__class__.USERNAME or
                unicode_for_py3(password) != self.__class__.PASSWORD):
                raise HttpBasicAuthResponseException("Invalid credentials")
            
        environ['HTTPBASICAUTH_FUNC'] = authenticate
        
        return self.app(environ, start_response)
    

class HttpBasicAuthMiddlewareTestCase(unittest.TestCase):
    """Unit tests for HTTP Basic Auth middleware used with the Online CA service
    package
    """
    CONFIG_FILE = 'httpbasicauth-server.ini'
    
    def __init__(self, *args, **kwargs):
        """Set-up Paste fixture from ini file settings"""
        here_dir = os.path.dirname(os.path.abspath(__file__))
        configFilePath = ('config:%s' % 
                          HttpBasicAuthMiddlewareTestCase.CONFIG_FILE)
        wsgiapp = loadapp(configFilePath, relative_to=here_dir)
        self.app = paste.fixture.TestApp(wsgiapp)
         
        unittest.TestCase.__init__(self, *args, **kwargs)
        
    def test01NoHttpBasicAuthHeader(self):
        # Try with no HTTP Basic Auth HTTP header
        response = self.app.get('/certificate/', status=401)
        self.assertTrue(response, 'Null response')
            
    def test02ValidCredentials(self):
        # Try with no HTTP Basic Auth HTTP header
        username = TestHttpBasicAuthCallBackAppMiddleware.USERNAME
        password = TestHttpBasicAuthCallBackAppMiddleware.PASSWORD
        
        base64String = base64.encodestring(b'%s:%s' % (username, password))[:-1]
        authHeader =  "Basic %s" % unicode_for_py3(base64String)
        headers = {'Authorization': authHeader}
        
        response = self.app.get('/certificate/', headers=headers, status=200)
        self.assertTrue((
                    TestHttpBasicAuthCallBackAppMiddleware.SUCCESS_RESPONSE in
                    response))
                      
    def test03InvalidCredentials(self):
        # Try with no HTTP Basic Auth HTTP header
        username = b'x'
        password = b'y'
        
        base64String = base64.encodestring(b'%s:%s' % (username, password))[:-1]
        authHeader =  "Basic %s" % unicode_for_py3(base64String)
        headers = {'Authorization': authHeader}
        
        response = self.app.get('/certificate/', headers=headers, status=401)
        self.assertTrue(response)
        
    def _createCallbackMiddleware(self):
        # Test creating app independently of PasteScript and using an 
        # alternate middleware which doesn't return a response but simply 
        # raises a 401 exception type if input credentials don't match
        app = TestApp({})
        app = HttpBasicAuthMiddleware.filter_app_factory(app, {},
                                prefix='',
                                rePathMatchList='/certificate/',
                                authnFuncEnvironKeyName='HTTPBASICAUTH_FUNC',
                                realm='test-realm')
        app = TestHttpBasicAuthCallBackMiddleware(app, {})

        self.app2 = paste.fixture.TestApp(app)
        
    def test04SimpleCBMiddlewareWithValidCredentials(self):
        self._createCallbackMiddleware()
        username = TestHttpBasicAuthCallBackAppMiddleware.USERNAME
        password = TestHttpBasicAuthCallBackAppMiddleware.PASSWORD
        
        base64String = base64.encodestring(b'%s:%s' % (username, password))[:-1]
        authHeader =  "Basic %s" % unicode_for_py3(base64String)
        headers = {'Authorization': authHeader}
        
        response = self.app.get('/certificate/', headers=headers, status=200)
        self.assertTrue(response, 'Null response')
        
    def test05SimpleCBMiddlewareWithInvalidCredentials(self):
        self._createCallbackMiddleware()
        username = b'a'
        password = b'b'
        
        base64String = base64.encodestring(b'%s:%s' % (username, password))[:-1]
        authHeader =  "Basic %s" % unicode_for_py3(base64String)
        headers = {'Authorization': authHeader}
        
        response = self.app.get('/certificate/', headers=headers, status=401)       
        self.assert_(response, 'Null response')

    