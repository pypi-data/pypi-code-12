#!/usr/bin/env python
# encoding: utf-8

# Front Matter {{{
'''
Copyright (c) 2016 The Broad Institute, Inc.  All rights are reserved.

This file is part of mdbtools.  See the <root>/COPYRIGHT file for the
SOFTWARE COPYRIGHT and WARRANTY NOTICE.

@author: Michael S. Noble
@date:  2016-03-04
'''

# }}}

import os
import sys
from MDBtool import MDBtool

KB_scale = 1024
MB_scale = 1024**2
GB_scale = 1024**3
TB_scale = 1024**4
Headers  = ["Container", "ObjCount", "NumIndexes", "DataSize", "StorageSize", "IndexSize"]

def scale_size(value):
    if value >= .9*TB_scale:
        value = '%2.2f TB' % (1.0 * value / TB_scale)
    elif value >= .9*GB_scale:
        value = '%2.2f GB' % (1.0 * value / GB_scale)
    elif value >= .9*MB_scale:
        value = '%2.2f MB' % (1.0 * value / MB_scale)
    elif value >= 2*KB_scale:
        value = '%2.2f KB' % (1.0 * value / KB_scale)
    else:
        value = str(value) +' bytes'
    return value 

def normalize(dict, keys_to_keep):

    normed = {}

    for key in keys_to_keep:
        value = dict[key]
        if key == 'size':
            key = 'dataSize'
        elif key == 'objects':
            key = 'count'
        elif key == 'totalIndexSize':
            key = 'indexSize'
        elif key == 'indexes':
            key = 'nindexes'

        if 'size' in key.lower():
            value = scale_size(value)

        if 'count' in key.lower():
            if value >= .9*1e9:
                value = '%4.2f billion' % (value / 1e9)
            elif value >= .9*1e6:
                value = '%4.2f million' % (value / 1e6)
            elif value >= .9*1e5:
                value = '%4.2f thousand' % (value / 1e3)

        normed[key] = value

    return normed

def emitRow(what, values, options):

    # If user requested that size of each index be shown, not just total, then
    # to aid interpretation repeat the header per collection/batch of indexes
    if 'indexSizes' in options:
        print "\n"+options.header

    # Pretty print to interactive display (tty), TSV otherwise
    if options.pretty:
        print '%-40s %15s %+14s %14s %14s %14s' % (what, values['count'],
                    values['nindexes'], values['dataSize'],
                    values['storageSize'], values['indexSize'])
    else:
        print '%s\t%s\t%s\t%s\t%s\t%s' % (what, values['count'],
                    values['nindexes'], values['dataSize'],
                    values['storageSize'], values['indexSize'])

    if 'indexSizes' in options:
            for k,v in options.indexSizes.iteritems():
                    print "%105s:%+10s" % (k, scale_size(v))

class mdbstats(MDBtool):

    def __init__(self):
        super(mdbstats, self).__init__(version="0.2.0")
        cli = self.cli
        cli.add_argument('-c', '--collections', default=None,help='display '+
            'ONLY this comma-separated list of collection(s) [%(default)s]')
        cli.add_argument('-i', '--indexSize', action='store_true', default=False,
            help='show size of each index in the collection [%(default)s]'+
            ' WARNING: this makes TSV output unreadable')
        cli.add_argument('-w', '--what', default='all',
            help='what info to obtain: all, global, collections [%(default)s]')

        desc = 'Quicklook tool for dumping stats of MongoDB databases\n\n'
        desc += 'Sizes will be auto-scaled to MB, GB or TB as needed.\n'
        desc += 'Output to screen will be pretty-printed for readability,\n'
        desc += 'but content redirected to a file will be in TSV format.\n'
        desc += 'To aid comparisons across databases, the results will be\n'
        desc += 'case-insensitively sorted by collection name.  Note that\n'
        desc += 'errors while accessing collections will be silently\n'
        desc += 'ignored, unless -v (verbose) option is specified.\n'
        cli.description = desc

    def execute(self):
        super(mdbstats, self).execute()
        self.options.pretty = sys.stdout.isatty()
        self.get_stats()

    def get_stats(self):

        self.status()
        options = self.options
        db = self.db

        if options.pretty:
            options.header = '%-40s %15s %+14s %14s %14s %14s' % (Headers[0], Headers[1],
                                Headers[2], Headers[3], Headers[4], Headers[5])
        else:
            options.header = '\t'.join(Headers)

        print options.header

        # Global database stats
        what = options.what.lower()
        if what == 'all' or what == 'global':
            stats = db.command('dbstats')
            stats = normalize(stats, ['objects', 'dataSize', 'storageSize', 'indexes', 'indexSize'])
            emitRow('Database:%s' % options.dbname, stats, options)

        # Per-collection stats
        if what == 'all' or what == 'collections':
            collections = options.collections
            if collections == None:
                collections = db.collection_names()
            else:
                collections = collections.split(',')

            # Case-insensitively sort the list, but keep system.indexes at front 
            collections = sorted(collections, key=lambda item: item.lower())
            if "system.indexes" in collections:
                collections.remove("system.indexes")
                collections.insert(0, "system.indexes")

            # FIXME: add regex-matching, so that sth like -c mutsig can be specified instead of -c MutSig_mafs
            #for coll in db.collection_names():
            for coll in collections:
                try:
                    stats = db.command('collstats', coll)
                    if options.indexSize:
                        options.indexSizes = stats["indexSizes"]
                    stats = normalize(stats, ['count', 'storageSize', 'nindexes', 'totalIndexSize', 'size'])
                    emitRow('Collection:%s ' % coll, stats, options)
                except Exception, e:
                    if options.verbose:
                        err = '\tPROBLEM ACCESSING COLLECTION: %s\n\t%s\n' % (coll, str(e))
                        sys.stderr.write(err)

if __name__ == "__main__":
    tool = mdbstats()
    tool.execute()
