#!/usr/bin/env python
# encoding: utf-8

# Front Matter {{{
'''
Copyright (c) 2016 The Broad Institute, Inc.  All rights are reserved.

mdbrm: this file is part of mdbtools.  See the <root>/COPYRIGHT
file for the SOFTWARE COPYRIGHT and WARRANTY NOTICE.

@author: Michael S. Noble
@date:  2016_03_06
'''

# }}}

import sys
from MDBtool import *

class mdbrm(MDBtool):

    def __init__(self):
        super(mdbrm, self).__init__(version="0.2.0")
        cli = self.cli

        # Optional args
        cli.add_argument('-f', '--force', action='store_true',
            help='force: remove collections without confirming first')
        
        desc = 'Quickly remove one or more collections from given database\n'
        cli.description = desc

        # Treat all remaining positional args as names of collections to delete
        cli.add_argument('collections',type=str, nargs=cli.ALL_REMAINING_ARGS,
            help="comma-separated name(s) of collections to remove")

    def parse_and_confirm(self):

        opts = self.options

        # For flexibility collection names are permitted to be both
        # space- and comma-delimted on the CL; here we disentangle
        # that, and handle edge cases of empty & duplicate names
        collections = []
        for c in opts.collections:
            collections.extend(c.strip(', \t').split(','))
        collections = list(set(collections))

        if not collections:
            mprint("Please specify one or more collections to delete.")
            sys.exit(101)

        opts.collections = collections
        if opts.force:
            return

        question = "\nAttempting to delete collections\n\t%s \nfrom %s::%s\n" %\
                            (','.join(collections), opts.server, opts.dbname)

        self.cli.ok_to_continue(question)

    def perform_delete(self):
        opts = self.options
        for coll in self.options.collections:
            if self.collectionExists(coll):
                self.db[coll].drop()
            elif not opts.force:
                mprint("Collection <%s> does not exist in %s::%s"
                        % (coll, opts.server, opts.dbname))

    def execute(self):
        super(mdbrm, self).execute()
        self.parse_and_confirm()
        self.perform_delete()

if __name__ == "__main__":
    tool = mdbrm()
    tool.execute()
