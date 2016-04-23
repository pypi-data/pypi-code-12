#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright (c) 2016, David Ewelt
All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

from __future__ import unicode_literals, print_function, division

from SocketServer import ThreadingMixIn
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from urlparse import urlparse, parse_qs

import time
import threading
import json

import PyV8

import v8bot

LOG = v8bot.LOG.getChild("API")

class Request(object):
    def __init__(self):
        self._handler = None
        self.method = ""
        self.hostname = ""
        self.path = ""
        self.query = ""
        self.headers = []
        self.rfile = None
        self.wfile = None

    @staticmethod
    def create(handler):
        url = ("http://%s:%s" % handler.server.address) + handler.path
        r = urlparse(url)
        q = parse_qs(r.query)

        handler.server_version = "V8Bot/%s" % v8bot.__version__
        request = Request()
        request._handler = handler
        request.method = "GET"
        request.hostname = r.hostname
        request.path = r.path
        request.query = q
        request.headers = handler.headers
        request.rfile = handler.rfile
        request.wfile = handler.wfile
        return request

    def response(self, obj, status=200, headers=[]):
        if isinstance(obj, PyV8.JSArray):
            obj = list(obj)
        if isinstance(obj, PyV8.JSObject):
            obj = dict(obj)
        self._handler.send_response(status)
        for k,v in headers:
            self._handler.send_header(k,v)
        self._handler.send_header("Content-Type", "application/json")
        self._handler.end_headers()
        json.dump(obj, self.wfile)

    def __str__(self, *args, **kwargs):
        return "<Request(%s %s q=%s)>" % (self.method, self.path, self.query)

class BaseRequestHandler(BaseHTTPRequestHandler):
    def __init__(self, request, client_address, server):
        BaseHTTPRequestHandler.__init__(self, request, client_address, server)

    def do_GET(self):
        if self.path == "/favicon.ico":
            return

        self.on_request(Request.create(self))

    def do_POST(self):
        if self.path == "/favicon.ico":
            return

        self.on_request(Request.create(self))

    def on_request(self, request):
        """
            @type request: Request
        """
        pass

    def log_message(self, f, *args):
        return

#--------------------------------------------------------------------------------------------------------------------------------
#-- Normal Synchronous API
#--------------------------------------------------------------------------------------------------------------------------------

class RequestHandler(BaseRequestHandler):
    def on_request(self, request):
        self.server.on_request(request)

class Server(HTTPServer, threading.Thread):
    def __init__(self, address):
        HTTPServer.__init__(self, address, RequestHandler)
        threading.Thread.__init__(self)
        self.address = address

    def on_request(self, request):
        pass

    def run(self):
        self.allow_reuse_address = True
        self.serve_forever()

#--------------------------------------------------------------------------------------------------------------------------------
#-- Long Polling
#--------------------------------------------------------------------------------------------------------------------------------

class LongPollingRequestHandler(BaseRequestHandler):
    def get_messages(self):
        messages = []
        for message_number,channel,message in self.server.messages:
            if message_number < self.message_number:
                continue
            if channel in self.subscriptions:
                messages.append( (channel, message) )
        self.message_number = self.server.message_number
        return messages

    def on_request(self, request):
        self.message_number = self.server.message_number
        self.subscriptions = request.query.get("c", [])

        t_start = time.time()
        while True:
            messages = self.get_messages()
            if len(messages) == 0:
                if time.time() - t_start >= 5:
                    request.response([], headers=[("Access-Control-Allow-Origin", "*")])
                    return
                time.sleep(0.1)
                continue
            request.response(messages, headers=[("Access-Control-Allow-Origin", "*")])
            return

class LongPollingServer(ThreadingMixIn, HTTPServer, threading.Thread):
    def __init__(self, address):
        HTTPServer.__init__(self, address, LongPollingRequestHandler)
        threading.Thread.__init__(self)
        self.address = address
        self.message_number = 0
        self.messages = []

    def send_message(self, channel, message):
        LOG.debug("added message #%s on channel %s: %s", self.message_number, channel, message)
        self.messages.append( (self.message_number, channel, message) )
        if len(self.messages) > 100:
            self.messages.pop(0)
        self.message_number += 1

    def run(self):
        self.allow_reuse_address = True
        self.serve_forever()

#--------------------------------------------------------------------------------------------------------------------------------

def test_start_synchronous():
    def on_request(r):
        for i in list("ABCD"):
            r.wfile.write('["%s"]\n' % i)
            time.sleep(5)

    s = Server(("127.0.0.1", 80))
    s.on_request = on_request
    s.run()

def test_start_longpolling():
    s = LongPollingServer(("127.0.0.1", 80))
    s.start()

    while True:
        inp = raw_input("> ")
        s.send_message("main", inp)

if __name__ == '__main__':
    #test_start_synchronous()
    test_start_longpolling()
