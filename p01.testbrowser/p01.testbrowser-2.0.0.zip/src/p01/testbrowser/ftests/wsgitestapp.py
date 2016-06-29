##############################################################################
#
# Copyright (c) 2014 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""A minimal WSGI application used as a test fixture."""

import os
import cgi
import json
import mimetypes
from datetime import datetime

from webob import Request
from webob import Response

from p01.testbrowser._compat import html_escape

class NotFound(Exception):
    pass

_HERE = os.path.dirname(__file__)


class WSGITestApplication(object):

    def __init__(self):
        self.request_log = []

    def getHandler(self, path):
        return {
            '/set_status.html': set_status,
            '/echo.html': echo,
            '/echo_one.html': echo_one,
            '/redirect.html': redirect,
            '/@@/testbrowser/forms.html': forms,
            '/set_header.html': set_header,
            '/set_cookie.html': set_cookie,
            '/get_cookie.html': get_cookie,
            '/inner/set_cookie.html': set_cookie,
            '/inner/get_cookie.html': get_cookie,
            '/inner/path/set_cookie.html': set_cookie,
            '/inner/path/get_cookie.html': get_cookie,
            # j01form.html
            '/j01form.html': j01form,
            '/j01form.html/j01LoadContent/load': j01formload,
            '/j01form.html/j01FormProcessor/save': j01formsave,
            # j01form.html
            '/j01controls.html': j01controls,
            '/j01controls.html/j01LoadContent/load': j01formload,
            '/j01controls.html/j01FormProcessor/save': j01formsave,
            }.get(path)

    def doJSONRPC(self, environ, start_response):
        req = Request(environ)
        hName = req.path_info
        data = req.json
        params = data.get('params', {})
        method = data.get('method')
        hName = '%s/%s' % (hName, method)
        j01FormHandlerName = params.get('j01FormHandlerName')
        if j01FormHandlerName is not None:
            hName = '%s/%s' % (hName, j01FormHandlerName)
        handler = self.getHandler(hName)
        try:
            resp = handler(req)
        except Exception as exc:
            if environ.get('wsgi.handleErrors') is False:
                raise
            elif environ.get('paste.throw_errors', False):
                raise
            resp = Response()
            status = 500
            if isinstance(exc, NotFound):
                status = 404
            resp.status = status
        return resp(environ, start_response)

    def doHTML(self, environ, start_response):
        req = Request(environ)
        self.request_log.append(req)
        handler = self.getHandler(req.path_info)
        if handler is None and req.path_info.startswith('/@@/testbrowser/'):
            handler = handle_resource
        if handler is None:
            handler = handle_notfound
        try:
            resp = handler(req)
        except Exception as exc:
            if environ.get('wsgi.handleErrors') is False:
                raise
            elif environ.get('paste.throw_errors', False):
                raise
            resp = Response()
            status = 500
            if isinstance(exc, NotFound):
                status = 404
            resp.status = status
        return resp(environ, start_response)

    def __call__(self, environ, start_response):
        if environ.get('CONTENT_TYPE') == 'application/json-rpc':
            return self.doJSONRPC(environ, start_response)
        else:
            return self.doHTML(environ, start_response)

def handle_notfound(req):
    raise NotFound(req.path_info)

class ParamsWrapper(object):

    def __init__(self, params):
        self.params = params

    def __getitem__(self, key):
        if key in self.params:
            return html_escape(self.params[key])
        return ''

def handle_resource(req, extra=None):
    filename = req.path_info.split('/')[-1]
    type, _ = mimetypes.guess_type(filename)
    path = os.path.join(_HERE, filename)
    with open(path, 'rb') as f:
        contents = f.read()
    if type == 'text/html':
        params = {}
        params.update(req.params)
        if extra is not None:
            params.update(extra)
        contents = contents.decode('latin1')
        contents = contents % ParamsWrapper(params)
        contents = contents.encode('latin1')
    return Response(contents, content_type=type)

def forms(req):
    extra = {}
    if 'hidden-4' in req.params and 'submit-4' not in req.params:
        extra['no-submit-button'] = 'Submitted without the submit button.'
    return handle_resource(req, extra)

def get_cookie(req):
    cookies = ['%s: %s' % i for i in sorted(req.cookies.items())]
    return Response('\n'.join(cookies))

def set_cookie(req):
    cookie_parms = {'path': None}
    cookie_parms.update(dict((str(k), str(v)) for k, v in req.params.items()))
    name = cookie_parms.pop('name')
    value = cookie_parms.pop('value')
    if 'max-age' in cookie_parms:
        cookie_parms['max_age'] = int(cookie_parms.pop('max-age'))
    if 'expires' in cookie_parms:
        cookie_parms['expires'] = datetime.strptime(cookie_parms.pop('expires'), '%a, %d %b %Y %H:%M:%S GMT')
    resp = Response()
    resp.set_cookie(name, value, **cookie_parms)
    return resp

def set_header(req):
    resp = Response()
    body = [u"Set Headers:"]
    for k, v in sorted(req.params.items()):
        body.extend([k, v])
        resp.headers.add(k, v)
    resp.unicode_body = u'\n'.join(body)
    return resp

_interesting_environ = ('CONTENT_LENGTH',
                        'CONTENT_TYPE',
                        'HTTP_ACCEPT_LANGUAGE',
                        'HTTP_CONNECTION',
                        'HTTP_HOST',
                        'HTTP_USER_AGENT',
                        'PATH_INFO',
                        'REQUEST_METHOD')

def echo(req):
    items = []
    for k in _interesting_environ:
        v = req.environ.get(k, None)
        if v is None:
            continue
        items.append('%s: %s' % (k, v))
    items.extend('%s: %s' % x for x in sorted(req.params.items()))
    if req.method == 'POST' and req.content_type == 'application/x-www-form-urlencoded':
        body = b''
    else:
        body = req.body
    items.append("Body: '%s'" % body.decode('utf8'))
    return Response('\n'.join(items))

def redirect(req):
    loc = req.params['to']
    resp = Response("You are being redirected to %s" % loc)
    resp.location = loc
    resp.status = int(req.params.get('type', 302))
    return resp

def echo_one(req):
    resp = repr(req.environ.get(req.params['var']))
    return Response(resp)

def set_status(req):
    status = req.params.get('status')
    if status:
        resp = Response('Just set a status of %s' % status)
        resp.status = int(status)
        return resp
    return Response('Everything fine')


###############################################################################
#
# json-rpc handling

RIGHT_CONTENT = """
<label for="text3">Text 3</label>
<input type="text" id="text3" name="text3"
     value="%(text3)s" />
<label for="text4">Text 4</label>
<input type="text" id="text4" name="text4"
     value="%(text4)s" />
<input type="button" name="save" value="Save"
       data-j01-testing-method="j01FormProcessor"
       data-j01-testing-error="j01RenderContentError"
       data-j01-testing-success="j01RenderContentSuccess"
       data-j01-testing-typ="JSONRPCButton"
       data-j01-testing-url="http://localhost:9090/j01form.html"
       data-j01-testing-form="form" />
"""

def j01formload(req):
    """JSON-RPC response for j01LoadContent on j01form.html page"""
    extra = {}
    params = req.params
    extra['text3'] = 'Text 3'
    extra['text4'] = 'Text 4'
    content = RIGHT_CONTENT % extra
    contentTargetExpression = '#right'
    # setup response data after render
    data = {
        'url': '',
        'nextURL': None,
        'nextContentURL': None,
        'content': content,
        'contentTargetExpression': contentTargetExpression,
        }
    contents = json.dumps({
        'jsonrpc': '2.0',
        'result': data,
        'id': 'id',
        })
    return Response(contents, content_type='application/json-rpc')


def j01formsave(req):
    """JSON-RPC response for j01FormProcessor on j01form.html page"""
    # extra = {}
    # params = req.params
    # extra['text3'] = params.get('text1', 'Text 3')
    # extra['text4'] = params.get('text2', 'Text 4')
    # content = RIGHT_CONTENT % extra
    content = u'Form saved'
    contentTargetExpression = '#right'
    # setup response data after render
    data = {
        'url': 'http://localhost/j01form.html',
        'content': content,
        'contentTargetExpression': contentTargetExpression,
        # animation
        'scrollToExpression': None,
        'scrollToOffset': None,
        'scrollToSpeed': None,
        # history setup
        'skipState': None,
        'stateURL': None,
        'stateTitle': None,
        'stateCallbackName': None,
        'nextURL': None,
        'nextContentURL': None,
        'nextHash': None,
        }
    contents = json.dumps({
        'jsonrpc': '2.0',
        'result': data,
        'id': 'id',
        })
    return Response(contents, content_type='application/json')


def j01form(req):
    """j01form.html GET/POST text/html page response"""
    extra = {}
    params = req.params
    # setup form values, get the from request if given
    extra['text1'] = params.get('text1', 'Text 1')
    extra['text2'] = params.get('text2', 'Text 2')
    extra['right'] = 'No Content'
    return handle_resource(req, extra)


def j01controls(req):
    """j01form.html GET/POST text/html page response"""
    extra = {}
    params = req.params
    # setup right content
    extra['right'] = 'No Content'
    return handle_resource(req, extra)

