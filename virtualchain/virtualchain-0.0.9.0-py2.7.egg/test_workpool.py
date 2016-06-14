#!/usr/bin/python

import sys
import os
import time
import traceback

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + "/.."))

import lib.workpool as workpool

wp = workpool.Workpool( 10, sys.argv[1], sys.argv[1:] )

futs = []

for j in xrange(0, 10):
    futs = []
    for i in xrange(0, 100):
        f = wp.apply_async( "message=%s,%s" % (j, i) )
        futs.append( f )

    for f in futs:
        try:
            f.wait(100000000000L)
            result = f.get(1000000000L)
            print "result: %s" % result[:100]
        except:
            traceback.print_exc()
            wp.close()
            wp.terminate()
            wp.join()
            sys.exit(1)

print "all results acquired"
wp.close()
wp.terminate()
wp.join()

