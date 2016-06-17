#!/usr/bin/env python
# encoding: utf-8
"""
*Start dropbox daemon if not running*

:Author:
    David Young

:Date Created:
    September 5, 2014

.. todo::
    
    @review: when complete pull all general functions and classes into dryxPython
"""
################# GLOBAL IMPORTS ####################
import sys
import os
import time
from docopt import docopt
from fundamentals import tools, times
from .original import dropbox
# from ..__init__ import *


###################################################################
# PUBLIC FUNCTIONS                                                #
###################################################################
# LAST MODIFIED : September 5, 2014
# CREATED : September 5, 2014
# AUTHOR : DRYX
def start_if_not_running(
        log):
    """
    *start if not running*

    **Key Arguments:**
        - ``log`` -- logger

    **Return:**
        - None

    .. todo::

        - @review: when complete, clean start_if_not_running function
        - @review: when complete add logging
        - @review: when complete, decide whether to abstract function to another module
    """
    log.info('starting the ``start_if_not_running`` function')

    isRunning = dropbox.is_dropbox_running()
    if isRunning is False:
        log.warning('dropbox was not running - starting now' % locals())
        try:
            log.debug("attempting to start dropbox")
            dropbox.start([])
            time.sleep(10)
        except Exception, e:
            log.error(
                "could not start dropbox - failed with this error: %s " % (str(e),))
            return
    else:
        log.info('dropbox is running fine')

    log.info('completed the ``start_if_not_running`` function')
    return None

# use the tab-trigger below for new function
# xt-def-with-logger

###################################################################
# PRIVATE (HELPER) FUNCTIONS                                      #
###################################################################

if __name__ == '__main__':
    main()
