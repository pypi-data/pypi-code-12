#!/usr/bin/env python
# encoding: utf-8

# Front Matter {{{
'''
Copyright (c) 2016 The Broad Institute, Inc.  All rights are reserved.

mdbtouch: this file is part of mdbtools.  See the <root>/COPYRIGHT
file for the SOFTWARE COPYRIGHT and WARRANTY NOTICE.

@author: Michael S. Noble
@date:  2016_03_06
'''

# }}}

import sys
from MDBtool import MDBtool

class mdbtouch(MDBtool):

    def __init__(self):
        super(mdbtouch, self).__init__(version="0.2.0")
        cli = self.cli

        desc  = 'Create one or more empty collections in given database,\n'
        desc += 'similar to how Unix "touch" command creates empty files\n'
        cli.description = desc

        # Treat all remaining positional args as names of collections to delete
        cli.add_argument('collections',type=str, nargs=cli.ALL_REMAINING_ARGS,
            help="comma-separated name(s) of collections to create")

    def parse(self):

        opts = self.options

        # For flexibility collection names are permitted to be both
        # space- and comma-delimted on the CL; here we disentangle
        # that, and handle edge cases of empty & duplicate names
        collections = []
        for c in opts.collections:
            collections.extend(c.strip(', \t').split(','))
        collections = list(set(collections))

        if not collections:
            print "Please specify one or more names of collections to create."
            sys.exit(101)

        opts.collections = collections

    def create(self):
        opts = self.options
        for coll in self.options.collections:
            if self.collectionExists(coll):
                print "Error, in %s::%s collection already exists: %s" \
                        % (opts.server, opts.dbname, coll)
            else:
                self.db.create_collection(coll)

    def execute(self):
        super(mdbtouch, self).execute()
        self.parse()
        self.create()

if __name__ == "__main__":
    tool = mdbtouch()
    tool.execute()
