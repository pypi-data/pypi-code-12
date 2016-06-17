#!/usr/bin/env python
# encoding: utf-8
"""
*Setup the selective sync with dropbox -- using a list of included folders, will exclude all others*

:Author:
    David Young

:Date Created:
    September 8, 2014

.. todo::
    
    @review: when complete pull all general functions and classes into dryxPython
"""
################# GLOBAL IMPORTS ####################
import sys
import os
from docopt import docopt
from fundamentals import tools, times
from dryxDropboxCL import start_if_not_running
from dryxDropboxCL.original import dropbox
# from ..__init__ import *


def main(arguments=None):
    """
    *The main function used when ``setup_selective_sync.py`` is run as a single script from the cl, or when installed as a cl command*
    """
    # setup the command-line util settings
    su = tools(
        arguments=arguments,
        docString=__doc__,
        logLevel="DEBUG"
    )
    arguments, settings, log, dbConn = su.setup()

    # unpack remaining cl arguments using `exec` to setup the variable names
    # automatically
    for arg, val in arguments.iteritems():
        if arg[0] == "-":
            varname = arg.replace("-", "") + "Flag"
        else:
            varname = arg.replace("<", "").replace(">", "")
        if isinstance(val, str) or isinstance(val, unicode):
            exec(varname + " = '%s'" % (val,))
        else:
            exec(varname + " = %s" % (val,))
        if arg == "--dbConn":
            dbConn = val
        log.debug('%s = %s' % (varname, val,))

    ## START LOGGING ##
    startTime = times.get_now_sql_datetime()
    log.info(
        '--- STARTING TO RUN THE setup_selective_sync.py AT %s' %
        (startTime,))

    # call the worker function
    # x-if-settings-or-database-credientials
    setup_selective_sync(
        log=log,
        settings=settings
    )

    if "dbConn" in locals() and dbConn:
        dbConn.commit()
        dbConn.close()
    ## FINISH LOGGING ##
    endTime = times.get_now_sql_datetime()
    runningTime = times.calculate_time_difference(startTime, endTime)
    log.info('-- FINISHED ATTEMPT TO RUN THE setup_selective_sync.py AT %s (RUNTIME: %s) --' %
             (endTime, runningTime, ))

    return

###################################################################
# CLASSES                                                         #
###################################################################
# xt-class-module-worker-tmpx
# xt-class-tmpx


###################################################################
# PUBLIC FUNCTIONS                                                #
###################################################################
# LAST MODIFIED : September 8, 2014
# CREATED : September 8, 2014
# AUTHOR : DRYX
def setup_selective_sync(
        log,
        settings):
    """
    *setup selective sync*

    **Key Arguments:**
        - ``log`` -- logger

    **Return:**
        - None

    .. todo::

        - @review: when complete, clean setup_selective_sync function
        - @review: when complete add logging
        - @review: when complete, decide whether to abstract function to another module
    """
    log.info('starting the ``setup_selective_sync`` function')

    # start the daemon if not running
    start_if_not_running.start_if_not_running(log=log)

    # get list of currently excluded folders
    with dropbox.closing(dropbox.DropboxCommand()) as dc:
        try:
            log.debug("attempting to list dropbox excluded folders")
            currentlyExcluded = dc.get_ignore_set()[u'ignore_set']
        except Exception, e:
            log.error(
                "could not list dropbox excluded folders - failed with this error: %s " % (str(e),))
            return
    log.debug('currentlyExcluded: %(currentlyExcluded)s' % locals())

    # get list of currently included folders and files (i.e. what's in the
    # dropbox folder now)
    dropboxPath = settings["dropbox path"]
    basePath = dropboxPath
    tmpCurrentlyIncluded = os.listdir(basePath)
    currentlyIncluded = []
    currentlyIncluded[:] = [
        """%(dropboxPath)s/%(c)s""" % locals() for c in tmpCurrentlyIncluded]
    log.debug('currentlyIncluded: %(currentlyIncluded)s' % locals())

    # get the list of folders that should be included
    settingsIncludedFolders = settings["dropbox folders to sync"]
    shouldBeincludedFolders = []
    shouldBeincludedFolders[:] = [
        """%(dropboxPath)s/%(i)s""" % locals() for i in settingsIncludedFolders]
    log.debug('settingsIncludedFolders: %(settingsIncludedFolders)s' % locals())

    # get the list of folders that should be excluded
    settingsExcludedFolders = settings["dropbox folders to unsync"]
    shouldBeExcludedFolders = []
    shouldBeExcludedFolders[:] = [
        """%(dropboxPath)s/%(i)s""" % locals() for i in settingsExcludedFolders]
    log.debug('settingsExcludedFolders: %(settingsExcludedFolders)s' % locals())

    # step 1. remove shouldBeincludedFolders from currentlyExcluded
    for include in shouldBeincludedFolders:
        if include.lower() in [l.lower() for l in currentlyExcluded]:
            log.debug("SHOULD NOT BE EXCLUDED: %(include)s" % locals())
            dropbox.exclude(["remove", include])

    # step 2. add shouldBeExcludedFolders in currentlyExcluded
    for exclude in shouldBeExcludedFolders:
        if exclude.lower() not in [l.lower() for l in currentlyExcluded]:
            log.debug("SHOULD BE EXCLUDED: %(exclude)s" % locals())
            dropbox.exclude(["add", exclude])

    # step 3. add to currentlyIncluded to currentlyExcluded if not in
    # shouldBeincludedFolders
    for currentInclude in currentlyIncluded:
        if currentInclude.lower() not in [l.lower() for l in shouldBeincludedFolders] and "dropbox.cache" not in currentInclude and ".dropbox" not in currentInclude:
            log.debug("SHOULD BE EXCLUDED: %(currentInclude)s" % locals())
            dropbox.exclude(["add", currentInclude])

    log.info('completed the ``setup_selective_sync`` function')
    return None

# use the tab-trigger below for new function
# xt-def-with-logger

###################################################################
# PRIVATE (HELPER) FUNCTIONS                                      #
###################################################################

if __name__ == '__main__':
    main()
