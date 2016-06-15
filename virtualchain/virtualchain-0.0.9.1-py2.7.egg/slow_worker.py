#!/usr/bin/python

import time
import sys
import os
import random
import lib.workpool as workpool
WP = workpool.Workpool

time.sleep(1.0)

for (key, payload) in WP.worker_next_message():

    #time.sleep(0.1 * random.randint(0, 10))
    #if random.randint(0, 10) == 3:
    #    sys.exit(0)

    WP.worker_post_message( key, "worker %s finished (with %s)" % (os.getpid(), payload * 65536))

