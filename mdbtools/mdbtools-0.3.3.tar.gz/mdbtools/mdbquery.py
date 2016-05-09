#!/usr/bin/env python
# encoding: utf-8

# Front Matter {{{
'''
Copyright (c) 2016 The Broad Institute, Inc.  All rights are reserved.

mdbquery: this file is part of mdbtools.  See the <root>/COPYRIGHT
file for the SOFTWARE COPYRIGHT and WARRANTY NOTICE.

@author: Michael S. Noble
@date:  2016_03_06
'''

# }}}

import sys
import os
import pprint
from bson import SON
from MDButils import *
from MDBtool import MDBtool
from tictoc import TicToc

SEC_scale = 1000
MIN_scale = 1000*60
HOUR_scale = 1000*60*60
Headers  = ['Collection', 'Query', 'Index', 'Retrieved', 'Matched', 'Total', 'Fraction', 'Time', 'Hinted' ]

def scaleCount(value):
    if value >= .9*1e9:
        value = '%4.2f billion' % (value / 1e9)
    elif value >= .9*1e6:
        value = '%4.2f million' % (value / 1e6)
    elif value >= .9*1e5:
        value = '%4.2f thousand' % (value / 1e3)

    return value

def parse_keyvals(keyvals):
    if not keyvals:
        return []
    query_terms = []
    for keyval in keyvals.split(','):
        key, _ ,value = keyval.partition('=')
        query_terms.append( ( key.strip(), value.strip() ) )
    return query_terms
    
def emitStats(collection, query, values, pretty=False):

    found = values['nFound']
    matched = values['nMatched']
    total = values['numTotal']
    percent = 100.0 * matched / total
    matched = scaleCount(matched)
    total = scaleCount(total)

    if pretty:
        print '%-16s%-50s%-24s%-12s%-18s%-16s%7.2f%%%+11s%+9s' % (collection.name, query[1:49],
                    values['index'],
                    found, matched, total, percent, values['time'], values['hint'])
    else:
        print '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s' % (collection.name, query,
                    values['index'], 
                    found, matched, total, percent, values['time'], values['hint'])

class mdbquery(MDBtool):

    def __init__(self):
        super(mdbquery, self).__init__(version='0.2.0')

        cli = self.cli
        cli.description = 'Perform and analyze queries of MongoDB databases, '+\
                          'using simple syntax from\nthe *NIX CLI\n\n'

        # Optional arguments
        cli.add_argument('-e', '--explain', default=True, action='store_false',
                    help='TOGGLE OFF calls to cursor.explain(); when used with '+
                         'other options like --retrieve, this can help isolate'+
                         ' the runtime of find() (lookup/match) from retrieval'+
                         ' e.g. cursor.next() or list(cursor)')
        cli.add_argument('-H', '--Hint', default=0, type=int,
                    help="force the HINT'th key to be primary search index "+ \
                    '[default: no hint]')
        cli.add_argument('-i', '--iters', default=1, type=int,
                    help='iteratively perform query [default: %(default)s]')
        cli.add_argument('-l', '--list', default=False, action='store_true',
                    help='list documents as they are retrieved, implicitly '+
                         'turning on --retrieve option [default: %(default)s]')
        cli.add_argument('-n', '--numrecs', default=50, type=int,
                    help='Specify the max # documents that the query should '+\
                    'find [0 == all, default: %(default)s]')
        cli.add_argument('-r', '--retrieve', default=False, action='store_true',
                    help='after performing find() query, iteratively retrieve '+
                    'all of the docs in the result set [default: %(default)s]')
        cli.add_argument('-t', '--time', default=False, action='store_true',
                    help='include more timing info in output [default: %(default)s]')
        cli.add_argument('-w', '--what', default='all',
                    help='what info to obtain: '+
                    'all, global, collections [default: %(default)s]')
        cli.add_argument('-u', '--unique', default=False, dest='unique',
                    action='store_true',
                   help='find all unique (distinct) values for given key')

        # Positional (required) arguments
        cli.add_argument('queries',
                    help='one or more query expressions, separated by the | '+\
                    'delimiter. Each query expression has the form\n'+ \
                    '   collection_name:key=value[,key=value].')

    def normalize(self, results):

        if self.options.verbose:
            print '\n\nexecutionStats explain results:'
            pprint.pprint(results)

        #['executionTimeMillis', 'nReturned', 'totalDocsExamined', 'executionStages', 'hint'])
        normed = {}

        # Index used in query, if any
        value  = results['executionStages']['inputStage'].get('inputStage', None)
        if value and value['stage'] == 'IXSCAN':
            normed['index'] = value['indexName']
        else:
            normed['index'] = 'none'

        # Execution time
        value = results['executionTimeMillis']
        if value >= .9*HOUR_scale:
            value = '%2.2f hours' % (1.0 * value / HOURS_scale)
        elif value >= .9*MIN_scale:
            value = '%2.2f mins' % (1.0 * value / MIN_scale)
        elif value >= .9*SEC_scale:
            value = '%2.2f sec' % (1.0 * value / SEC_scale)
        else:
            value = str(value) + ' msec'
        normed['time'] = value

        # Number of docs inspected (in database) and returned (in results set)
        normed['nExamined'] = results['totalDocsExamined']
        normed['nFound'] = results['nReturned']

        return normed

    def do_query(self, collection, terms, hint=0):
        opts = self.options
        collection = self.db[collection]
        SON_terms = SON(terms)
        SON_terms_str = str(SON_terms)
        terms_str = str(terms)
        n = opts.numrecs

        if opts.verbose:
            print '\nQuery:: ' + collection.name + ':' + terms_str
            print 'SON-ified Query:: ' + collection.name + ':' + SON_terms_str

        if opts.time:
            t = TicToc(incremental=True)

        # Perform query
        if opts.unique:
            key = terms[0][0]
            results = collection.distinct(key)
            print '%d distinct results found for key %s:' % (len(results), key)
            pprint.pprint(results)
            return

        if hint:
            if opts.verbose:
                print '\tHINTED: '+terms[hint-1][0]
            cursor = collection.find(SON_terms)
            cursor.hint( [(terms[hint-1][0], pymongo.ASCENDING)] )
            cursor.limit(n)
            hint = str(hint > 0) + ':%d' % hint
        else:
            cursor = collection.find( SON_terms, limit=n)
            hint = False

        if opts.time:
            t.toc('initial find() command')

        if opts.explain:
            results = cursor.explain()
            if opts.verbose:
                print 'FULL explain results:'
                pprint.pprint(results)

            results = self.normalize( results['executionStats'] )
            # Splice in extra fields: total num records/objs in collection, and hint
            results['nMatched'] = cursor.count()
            results['numTotal'] = collection.count()
            results['hint'] = hint
            emitStats(collection, str(terms), results, opts.pretty)

        if opts.time:
            t.toc('explain() command and emitStats() function')

        if opts.retrieve:
            results = list(cursor)
            if opts.time:
                t.toc('retrieve %s documents' % len(results))
            if opts.list:
                print 'RESULTS are: '
                pprint.pprint(results)
                if opts.time:
                    t.toc('listing %s documents' % len(results))

    def do_queries(self):
        opts = self.options
        if not opts.unique:
            if opts.pretty:
                print '%-16s%-50s%-24s%-12s%-18s%-16s%-11s%-11s%-7s' % \
                    (Headers[0], Headers[1], Headers[2], Headers[3], \
                    Headers[4], Headers[5], Headers[6], Headers[7], Headers[8])
            else:
                print '\t'.join(Headers)

        queries = opts.queries
        if os.path.isfile(queries):
            queries = open(queries, 'rb').read().split('\n')
        else:
            queries = queries.split('|')

        # Multiple queries can be specified at CLI or in file, separated by |
        for q in queries:

            # Partition each query into Collection:key=value [,key=value ...]
            q = q.split(':')
            if len(q) < 2:
                q.append('')

            collection = q[0]
            if collection not in self.collection_names:
                eprint('Skipping query on non-existing collection: '+collection)
                continue

            for _ in range(opts.iters):
                self.do_query(collection, parse_keyvals( q[1] ), opts.Hint)

    def execute(self):
        super(mdbquery, self).execute()
        self.options.pretty = sys.stdout.isatty()
        if self.options.list:
            self.options.retrieve = True
        self.do_queries()

if __name__ == '__main__':
    tool = mdbquery()
    tool.execute()
