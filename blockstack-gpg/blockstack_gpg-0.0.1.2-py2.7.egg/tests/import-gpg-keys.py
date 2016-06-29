#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    gitsec
    ~~~~~
    copyright: (c) 2014-2015 by Halfmoon Labs, Inc.
    copyright: (c) 2016 by Blockstack.org

    This file is part of gitsec.

    Gitsec is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Gitsec is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    You should have received a copy of the GNU General Public License
    along with gitsec.  If not, see <http://www.gnu.org/licenses/>.
"""

import blockstack_client
import sys
import os
import json

# hack around absolute paths
pkg_dir =  os.path.abspath(os.path.dirname(__file__) + "/..")
sys.path.insert(0, pkg_dir)

import blockstack_gpg as gpg
import testlib

if __name__ == "__main__":
    tmpdir = testlib.make_test_dir( "import-gpg-keys" )
    key_id = "9862A3FB338BE9EB6C6A5E05639C89272AFEC540"
    key_server = "pgp.mit.edu"
    if len(sys.argv) == 3:
        key_id = sys.argv[1]
        key_server = sys.argv[2]

    res = gpg.gpg_fetch_key( key_server, key_id=key_id, config_dir=tmpdir ) 
    print json.dumps(res)

    sys.exit(0)
