#!/usr/bin/env python
# encoding: utf-8

# Front Matter {{{
'''
Copyright (c) 2016 The Broad Institute, Inc.  All rights are reserved.

mdbmv: this file is part of mdbtools.  See the <root>/COPYRIGHT
file for the SOFTWARE COPYRIGHT and WARRANTY NOTICE.

@author: Michael S. Noble
@date:  2016_05_06
'''

# }}}

from MDBtool  import *
from MDButils import *

class mdbmv(MDBtool):

    def __init__(self):
        super(mdbmv, self).__init__(version="0.2.0")

        desc = 'Simple CLI tool to rename (mv) a MongoDB collection\n\n'
        self.cli.description = desc

        # Positional (required) arguments
        self.cli.add_argument('collection', help="name of existing collection")
        self.cli.add_argument('new_name', help="new name for this collection")

    def execute(self):
        super(mdbmv, self).execute()
        opts = self.options
        original = opts.collection
        if original in self.collection_names:
            print "Renaming collection %s to %s" % (original, opts.new_name)
            original = self.db[original]
            original .rename(opts.new_name)
        else:
            eprint("collection %s does not exist in %s:%s" %
                                        (original, opts.server, opts.dbname))

if __name__ == "__main__":
    mdbmv().execute()
