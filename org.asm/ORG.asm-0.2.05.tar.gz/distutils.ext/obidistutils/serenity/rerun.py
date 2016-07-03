'''
Created on 24 mai 2015

@author: coissac
'''

import sys
import os
from distutils import log
from distutils.errors import DistutilsError


from obidistutils.serenity.globals import saved_args
from obidistutils.serenity.checkpython import is_python_version,\
    lookfor_good_python


def rerun_with_anothe_python(path, minversion='3.4',maxversion=None, fork=False):
        
    if saved_args:
        args = saved_args
    else:
        args = list(sys.argv)
        
          
    assert is_python_version(path,minversion,maxversion), \
           'the selected python is not adapted to the installation of this package'
                   
    args.insert(0, path)
        
    sys.stderr.flush()
    sys.stdout.flush()
    
    if fork:
        log.info('Forking a new install process')
        os.system(' '.join(list(args)))
        log.info('External process ended')
        sys.exit(0)
    else:
        log.info('Install script restarting...')
        os.execv(path,list(args))

def enforce_good_python(minversion='3.4',maxversion=None, fork=False):
    if is_python_version(minversion=minversion,maxversion=maxversion):
        log.info('You are running the good python')
        return True
    
    goodpython = lookfor_good_python(minversion,maxversion)
    
    if not goodpython:
        raise DistutilsError('No good python identified on your system')

    goodpython=goodpython[0]
    
    log.warn("========================================")    
    log.warn("")
    log.warn("    Switching to python : %s" % goodpython)
    log.warn("")
    log.warn("========================================")    

    rerun_with_anothe_python(goodpython)
