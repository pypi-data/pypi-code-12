#!/usr/bin/env python
# encoding: utf-8

# Front Matter {{{
'''
Copyright (c) 2016 The Broad Institute, Inc.  All rights are reserved.

MDBtool.py: this file is part of mdbtools.  See the <root>/COPYRIGHT
file for the SOFTWARE COPYRIGHT and WARRANTY NOTICE.

@author: Michael S. Noble
@date:  2016-03-04
'''

# }}}

import sys
import os
import traceback
from pymongo import MongoClient, version as pyMongoClientVersion, IndexModel
from MDBnetrc import MDBnetrc
from MDBcli import MDBcli
from MDButils import *

class MDBtool(object):
    ''' Base class for each tool '''

    def __init__(self, version=None):

        self.cli = MDBcli(version=version)
        # Derived classes can/should add custom options/description/version &
        # behavior in their respective __init__()/execute() implementations

    def __connect(self):

        opts = self.options

        try:
            # Connect to database, authenticating if necessary
            user, _, password = MDBnetrc().authenticators(opts.server)
            connection = MongoClient(opts.server, opts.port)

            if opts.authenticate:
                db = connection[opts.dbname]
                db.authenticate(user, password)
            else:
                # There was a time when MongoDB would silently create a DB at
                # connect time if it did not already exist; we guard against
                # that absurdity here, but only for non-authenticated servers
                if opts.dbname not in connection.database_names():
                    raise NameError(opts.dbname +" database does not exist in "+
                                                opts.server+": Mongo instance")
                db = connection[opts.dbname]

        except Exception as e:
            eprint("Could not connect to %s:%s " %  (self.options.server,
                                                     self.options.dbname))
            if self.options.verbose:
                traceback.format_exc()
            sys.exit(1)

        self.db = db
        self.connection = connection
        self.collection_names = db.collection_names()

    def collectionExists(self, collectionName):
        return (collectionName in self.collection_names)

    def execute(self):
        self.options = self.cli.parse_args()
        self.__connect()

    def status(self):
        # Emit system info (as header comments suitable for TSV, etc) ...
        db_server_version = self.connection.server_info()['version']
        print '#' 
        print '# %-22s = %s' % (self.__class__.__name__ + ' version ', \
                                                self.cli.version)
        print '# Server Name            = %s' % self.options.server
        print '# Database Name          = %s' % self.options.dbname
        print '# MongoDB server version = %s' % db_server_version
        print '# PyMongo client version = %s' % pyMongoClientVersion
        print '#'

if __name__ == "__main__":
    tool = MDBtool()
    tool.execute()
    tool.status()
