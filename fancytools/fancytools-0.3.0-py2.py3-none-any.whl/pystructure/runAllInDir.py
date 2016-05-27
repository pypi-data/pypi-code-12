# -*- coding: utf-8 -*-

import sys
import pkgutil
import runpy
from time import time


thismodname = __name__.split('.')[-2:]
thismodname = '.'.join(thismodname)


# Note there is a bug in pkgutil.walk_packages
# excluding all modules that have the same name as modules in 
# the standard library, see
# http://bugs.python.org/issue14787
# that's why 'os' and 'utils' are not tested at the moment

def runAllInDir(dir_path, exclude=[], add_args=(), ignoreErrors=True):
    '''
    execute all modules as __main__ within a given package path 
    '''
    print 'testing all modules of %s' %dir_path
    
    if type(add_args) in (tuple, list):
        sys.argv.extend(add_args)
    else:
        sys.argv.append(add_args)
    t = 0
    failed = []
    for _, modname, ispkg in pkgutil.walk_packages(
            [dir_path],
            #onerror=lambda x: None
            ):
        if not ispkg and modname != thismodname and not modname in exclude: # don't test this module
            print '... %s' %modname
            t0 = time()
            try:
                runpy.run_module(modname, init_globals=None, run_name='__main__', alter_sys=False)
            except Exception,err:
                if ignoreErrors:
                    print "FAILED: %s" %err
                else: 
                    raise(err), None, sys.exc_info()[2]
                failed.append((modname, err))
            dt = time()-t0
            t += dt
            print 'execution time=%s' %dt
    print '----------------'
    print 'time needed=%s' %t
    if failed:
        print '======================='
        print 'failed for %s modules' %len(failed)
        print '-----------------------'
        for mod, err in failed:
            print mod, err
