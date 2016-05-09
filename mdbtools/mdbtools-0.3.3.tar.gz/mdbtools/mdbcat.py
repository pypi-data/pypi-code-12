#!/usr/bin/env python
# encoding: utf-8

# Front Matter {{{
'''
Copyright (c) 2016 The Broad Institute, Inc.  All rights are reserved.

mdbcat: this file is part of mdbtools.  See the <root>/COPYRIGHT
file for the SOFTWARE COPYRIGHT and WARRANTY NOTICE.

@author: Michael S. Noble
@date:  2016_05_08
'''

# }}}

import sys
import os
import pprint
from MDButils import *
from MDBtool import MDBtool

class mdbcat(MDBtool):

    def __init__(self):
        super(mdbcat, self).__init__(version="0.2.0")

        cli = self.cli
        cli.description = 'Display the contents of one or more collections, '+\
            'in concatenated form, optionally saving to a new collection.'

        # Optional arguments
        cli.add_argument('-c', '--chunkSize', type=int, default=500,
                help='specify the number of documents to retrieve per '+\
                'iteration of the read loop [default: %(default)s]')
        cli.add_argument('-e', '--extend', help='extend an existing '+\
                'named collection by appending the results from here')
        #cli.add_argument('-o', '--output', help='save the results to a '+\
        #        'new collection with the given name')
        cli.add_argument('-l', '--limit', default=None, type=int,
                help='display only LIMIT # of records, instead of all]')

        # Positional (required) arguments
        cli.add_argument('collections', nargs=cli.ALL_REMAINING_ARGS,
                                help='one or more collection names\n\n')

    def validate(self):
        validCollections = []
        for collection in self.options.collections:
            if collection not in self.collection_names:
                eprint("No such collection: "+collection)
                continue
            validCollections.append(collection)
        self.options.collections = validCollections

        # Remainder of this code is for when --extend/--output are enabled
        # Destination collection already exists: oh my, what to do?
        #if opts.force:
        #    self.db[opts.To].drop()
        #else:
        #    eAbort("%s collection already exists in %s:%s" % \
        #                (opts.To, opts.server, opts.dbname), err=102)

    def index(self):
        # Not used yet: but when --extend/--output options are enabled
        # this will be used to replicate indexes from source collections
        index_info = From.index_information()
        index_info.pop("_id_", None)
        indexes = []
        for idx in index_info.values():
            indexes.append( IndexModel(idx["key"]) )

        # Add all indexes in one call, to iterate single time over data
        To.create_indexes(indexes)

    def cat(self, collection):

        opts = self.options
        numSeen = 0
        collection = self.db[collection]
        numTotal = collection.find().count()
        if opts.limit:
            numTotal = min(numTotal, int(opts.limit))

        chunkSize = min(opts.chunkSize, numTotal)

        while True:
            documents = collection.find().skip(numSeen).limit(chunkSize)
            if not documents or documents.count()==0:
                break
            pprint.pprint(list(documents))
            numSeen += documents.count(with_limit_and_skip=True)
            if numSeen >= numTotal:
                break

    def execute(self):
        super(mdbcat, self).execute()
        self.validate()
        for collection in self.options.collections:
            self.cat(collection)

if __name__ == "__main__":
    mdbcat().execute()
