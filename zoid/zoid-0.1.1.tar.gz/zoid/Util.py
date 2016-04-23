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

import os
import threading
import httplib
from urlparse import urlparse
import zipfile

def unzip(source_filename, dest_dir):
    with zipfile.ZipFile(source_filename) as zf:
        for member in zf.infolist():
            # Path traversal defense copied from
            # http://hg.python.org/cpython/file/tip/Lib/http/server.py#l789
            words = member.filename.split('/')
            path = dest_dir
            for word in words[:-1]:
                _, word = os.path.splitdrive(word)
                _, word = os.path.split(word)
                if word in (os.curdir, os.pardir, ''):
                    continue
                path = os.path.join(path, word)
            zf.extract(member, path)

class EventHook(object):
    def __init__(self):
        self.handlers = []

    def __iadd__(self, handler):
        self.handlers.append(handler)
        return self

    def __isub__(self, handler):
        self.handlers.remove(handler)
        return self

    def fire(self, *args, **keywargs):
        for handler in self.handlers:
            handler(*args, **keywargs)

class Download(threading.Thread):
    def __init__(self, remote, local):
        threading.Thread.__init__(self)

        self.remote = remote
        self.local = local

        self.content_length = 0
        self.bytes_received = 0
        self.running = False
        self.exception = None

    def run(self):
        self.running = True

        connection = None
        try:
            url = urlparse(self.remote)

            if url.scheme == "http":
                connection = httplib.HTTPConnection(url.hostname)
            elif url.scheme == "https":
                connection = httplib.HTTPSConnection(url.hostname)
            else:
                raise Exception("unknown url scheme '%s'" % url.scheme)
            
            connection.request("GET", url.path)
            response = connection.getresponse()
            
            if response.status != 200:
                raise Exception("server respond with other statuscode then 200")
            
            content_length = int(response.getheader("Content-Length", 0))
            if content_length == 0:
                raise Exception("error while retriving content length header")
            
            self.content_length = content_length
    
            block_size = 8192
            bytes_received = 0
            with open(self.local, "wb") as fp:
                while True:
                    buf = response.read(block_size)
                    if not buf:
                        break
                    elif len(buf) == 0:
                        break
                    bytes_received += len(buf)
                    fp.write(buf)
                    self.bytes_received = bytes_received
        except Exception as e:
            self.exception = e
        finally:
            if not connection is None:
                connection.close()
            self.running = False
