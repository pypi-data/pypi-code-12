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

import sys
import os
import threading
import httplib
from urlparse import urlparse
import zipfile
import random
import xml.etree.ElementTree as ET

def create_password(length=16):
    return "".join([ random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz") for _ in xrange(length) ])

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

def zipdir(fp, path, arcpath=None, followlinks=False):
    for root, _, files in os.walk(path, followlinks=followlinks):
        for f in files:
            f_in = os.path.join(root, f)
            if arcpath is None:
                fp.write(f_in)
                continue
            arcname = os.path.join(arcpath, root[len(path)+1:], f)
            fp.write(f_in, arcname)

def get_processes():
    if os.name == "nt":
        #-- just to say: I HATE WINDOWS!!! I REALY DO! just look at this mess only for getting a process listing oO
        xml = os.popen("wmic path win32_process get Caption,ProcessId,CommandLine /format:rawxml").read()

        root = ET.fromstring( xml )
        for xn_instance in root.findall("RESULTS")[0].findall("CIM")[0].findall("INSTANCE"):

            instance_properties = {}
            for xn_prop in xn_instance.findall("PROPERTY"):
                name = xn_prop.attrib["NAME"]
                values = xn_prop.findall("VALUE")
                if len(values) == 0:
                    instance_properties[name] = ""
                else:
                    instance_properties[name] = values[0].text

            yield {"pid": int(instance_properties["ProcessId"]), "cmd": instance_properties["CommandLine"]}
    elif os.name == "posix":
        for pid in [pid for pid in os.listdir('/proc') if pid.isdigit()]:
            try:
                cmd = open(os.path.join('/proc', pid, 'cmdline'), 'rb').read()
                if cmd.endswith("\x00"):
                    cmd = cmd[:-1]
                yield {"pid": int(pid), "cmd": cmd.replace("\x00", " ")}
            except IOError: # proc has already terminated
                continue
    else:
        raise NotImplementedError()

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

def print_table(headers, rows):
    column_lengths = [ 0 for _ in headers ]
    for i,header in enumerate(headers):
        column_lengths[i] = max(column_lengths[i], len(header))
    for row in rows:
        for c,col in enumerate(row):
            column_lengths[c] = max(column_lengths[c], len(str(col)))

    header = ""
    for i,head in enumerate(headers):
        if i > 0:
            header += " | "
        header += ("%-"+str(column_lengths[i])+"s") % head

    sys.stdout.write("-"*len(header) + "\n")
    sys.stdout.write(header + "\n")
    sys.stdout.write("-"*len(header) + "\n")

    for row in rows:
        for c,col in enumerate(row):
            if c > 0:
                sys.stdout.write(" | ")
            sys.stdout.write(("% "+str(column_lengths[c])+"s") % (col))
        sys.stdout.write("\n")

    sys.stdout.write("-"*len(header) + "\n")

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

#if __name__ == '__main__':
#    print_table(["name", "ip", "port"], [["test","127.0.0.1", 777],["longservername","127.0.0.1", 777]])