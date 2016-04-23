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

from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from urlparse import urlparse, parse_qs

import re
import json

import zoid

def api_status():
    return {"version": zoid.__version__}

def api_servers():
    return [ c.name for c in zoid.get_server_configs() ] 

def api_server_info(server_name):
    srv = zoid.get_server(server_name)
    return {
        "address": srv.get_address(),
        "branch": srv.get_branch(),
        "running": srv.is_running(),
        "connections": len(srv.get_connections()),
    }

def api_server_config(server_name):
    return zoid.get_server_config(server_name).get_dict()

class RequestHandler(BaseHTTPRequestHandler):
    HANDLERS = [
        ("^/status$",             api_status),
        ("^/config$",             lambda: zoid.CONFIG.get_dict()),
        ("^/servers$",            api_servers),
        ("^/server/(.+)/info$",   api_server_info),
        ("^/server/(.+)/config$", api_server_config),
    ]

    def do_GET(self):
        url = ("http://%s:%s" % self.server.address) + self.path

        req = urlparse(url)
        query = parse_qs(req.query)
        
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()

        #if not 'key' in query:
        #    json.dump({
        #        "status": "error",
        #        "message": "no auth"
        #    }, self.wfile)
        #    return

        for p,h in RequestHandler.HANDLERS:
            m = re.match(p, req.path)

            if not m:
                continue

            try:
                r = h(*m.groups())

                json.dump({
                    "status": "ok",
                    "data": r
                }, self.wfile)

            except Exception as e:
                json.dump({
                    "status": "error",
                    "message": str(e)
                }, self.wfile)

class Server(HTTPServer):
    def __init__(self, address):
        self.address = address        
        HTTPServer.__init__(self, self.address, RequestHandler)

def run_server(address):
    Server(address).serve_forever()
