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

# NOTE: you should start rngd before running automated GPG tests

import gnupg
import tempfile
import os

def make_test_dir( testname ):
    """
    Set up a suitable keyring path
    """
    return os.path.join("/tmp/blockstack-gpg-test-%s" % testname)


def make_test_keys( path, num_keys ):
    """
    Set up a test gpg keyring directory.
    Return the list of key fingerprints.
    """
    keydir = os.path.join( path, "keys" )
    gpg = gnupg.GPG( gnupghome=keydir )
    ret = []

    for i in xrange(0, num_keys):
        print "Generating key %s" % i
        key_input = gpg.gen_key_input()
        key_res = gpg.gen_key( key_input )
        ret.append( key_res.fingerprint )

    return ret


