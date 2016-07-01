#!/usr/local/bin/python
# encoding: utf-8
"""
Documentation for bilbo can be found here: http://bilbo.readthedocs.org/en/stable

Usage:
    bilbo template [-s <pathToSettingsFile>]
    bilbo tasks [-s <pathToSettingsFile>]
    bilbo tidy [-s <pathToSettingsFile>]
    bilbo scaffold [-s <pathToSettingsFile>]
    bilbo blog [-s <pathToSettingsFile>]

    COMMANDS
    ========
    template              populate the wiki with template content and cleanup file names
    tasks                 add projects from wikis to taskpaper files to keep track of project tasks
    tidy                  tidy up the gollum wiki, updating lists, sidebars, footer, headers, cleaning filenames and md metadata
    scaffold              add and maintain sidebars, footers, headers and various listing pages in a gollum wiki
    blog                  take pages that have been flagged to be posted as a Jekyll blog post, format them correctly and post them

    OPTIONS
    =======
    -h, --help            show this help message
    -s, --settings        the settings file
"""
################# GLOBAL IMPORTS ####################
import sys
import os
os.environ['TERM'] = 'vt100'
import readline
import glob
import pickle
from docopt import docopt
from fundamentals import tools, times
from bilbo.templates import templates
from bilbo.tasks import tasks as tsks
# from ..__init__ import *


def tab_complete(text, state):
    return (glob.glob(text + '*') + [None])[state]


def main(arguments=None):
    """
    *The main function used when ``cl_utils.py`` is run as a single script from the cl, or when installed as a cl command*
    """
    # setup the command-line util settings
    su = tools(
        arguments=arguments,
        docString=__doc__,
        logLevel="DEBUG",
        options_first=False,
        projectName="bilbo",
        tunnel=False
    )
    arguments, settings, log, dbConn = su.setup()

    # tab completion for raw_input
    readline.set_completer_delims(' \t\n;')
    readline.parse_and_bind("tab: complete")
    readline.set_completer(tab_complete)

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
        '--- STARTING TO RUN THE cl_utils.py AT %s' %
        (startTime,))

    # CALL FUNCTIONS/OBJECTS
    if template:
        templates(
            log=log,
            settings=settings
        ).get()

    if tasks:
        this = tsks(
            log=log,
            settings=settings
        )
        this.get()

    if tidy:
        from bilbo import tidy as tdy
        scrubber = tdy(
            log=log,
            settings=settings
        )
        scrubber.get()

    if scaffold:
        from bilbo import scaffold as scaf
        fixer = scaf(
            log=log,
            settings=settings
        )
        fixer.get()

    if blog:
        from bilbo import blog
        poster = blog(
            log=log,
            settings=settings
        ).get()

    if "dbConn" in locals() and dbConn:
        dbConn.commit()
        dbConn.close()
    ## FINISH LOGGING ##
    endTime = times.get_now_sql_datetime()
    runningTime = times.calculate_time_difference(startTime, endTime)
    log.info('-- FINISHED ATTEMPT TO RUN THE cl_utils.py AT %s (RUNTIME: %s) --' %
             (endTime, runningTime, ))

    return


if __name__ == '__main__':
    main()
