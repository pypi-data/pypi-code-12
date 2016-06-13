#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    The MIT License (MIT)
    Copyright (c) 2014-2015 by Halfmoon Labs, Inc.
    Copyright (c) 2016 by Blocktatck.org

    Permission is hereby granted, free of charge, to any person obtaining a
    copy of this software and associated documentation files (the "Software"),
    to deal in the Software without restriction, including without limitation
    the rights to use, copy, modify, merge, publish, distribute, sublicense,
    and/or sell copies of the Software, and to permit persons to whom the
    Software is furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included
    in all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
    OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
    THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
    THE SOFTWARE.
"""

# use Blockstack Labs as a storage proxy

import os
import sys 
import traceback
import logging
import xmlrpclib

# stop common XML attacks 
from defusedxml import xmlrpc
xmlrpc.monkey_patch()

from .common import get_logger, DEBUG

if os.environ.get("BLOCKSTACK_TEST", None) == "1":
    SERVER_NAME = "localhost"
    SERVER_PORT = 16264

else:
    SERVER_NAME = "node.blockstack.org"
    SERVER_PORT = 6264

log = get_logger("blockstack-storage-driver-blockstack-server")


def get_data( data_id, zonefile=False ):
    """
    Get data or a zonefile from the server.
    """
    url = "http://%s:%s/RPC2" % (SERVER_NAME, SERVER_PORT)
    ses = xmlrpclib.ServerProxy( url, allow_none=True )
    
    if zonefile:
        data = ses.get_zonefiles( [data_id] )
        if 'error' in data:
            log.error("Get zonefile %s: %s" % (data_id, data['error']))
            return None
        else:
            try:
                return data['zonefiles'][0]
            except:
                log.error("Failed to parse zonefile")
                return None

    else:
        data = ses.get_profile( data_id )
        if 'error' in data:
            log.error("Get profile %s: %s" % (data_id, data['error']))
            return None 
        else:
            try:
                return data['profile']
            except:
                log.error("Failed to parse profile")
                return None


def put_data( data_id, data_txt, zonefile=False ):
    """
    Put data or a zoneflie to the server.
    """
    url = "http://%s:%s/RPC2" % (SERVER_NAME, SERVER_PORT)
    ses = xmlrpclib.ServerProxy( url, allow_none=True )

    if zonefile:
        res = ses.put_zonefiles( [data_txt] )
        if 'error' in res:
            log.error("Failed to put %s: %s" % (data_id, data_txt))
            return False
        else:
            return True

    else:
        res = ses.put_profile( data_id, data_txt )
        if 'error' in res:
            log.error("Failed to put %s: %s" % (data_id, data_txt))
            return False
        else:
            return True


def storage_init(conf):
    pass

def handles_url( url ):
    if url.startswith("http://") and len(url.split("#")) == 2 and url.split("#")[1].endswith("/RPC2"):
        return True
    else:
        return False

def make_mutable_url( data_id ):
    # xmlrpc endpoint
    return "http://%s:%s/RPC2#%s" % (SERVER_NAME, SERVER_PORT, data_id)

def get_immutable_handler( key ):
    return get_data( key, zonefile=True )

def get_mutable_handler( url ):
    parts = url.split("#")
    if len(parts) != 2:
        log.error("Invalid url '%s'" % url)
        return None

    data_id = parts[1]
    return get_data( data_id, zonefile=False )


def put_immutable_handler( key, data, txid ):
    return put_data( key, data, zonefile=True )

def put_mutable_handler( data_id, data_bin ):
    return put_data( data_id, data_bin, zonefile=False )

def delete_immutable_handler( key, txid, sig_key_txid ):
    return True

def delete_mutable_handler( data_id, signature ):
    return True
