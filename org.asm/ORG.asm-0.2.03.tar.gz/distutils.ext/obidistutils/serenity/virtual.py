'''
Created on 2 oct. 2014

@author: coissac
'''

import os
import sys
import venv

from distutils.errors import DistutilsError
from .globals import local_virtualenv  # @UnusedImport
from .checkpython import   which_virtualenv,\
                           is_python_version, \
                           is_a_virtualenv_python
                                                

    
    
def serenity_virtualenv(envname,package,version,minversion='3.4',maxversion=None):
        
    #
    # Checks if we are already running under the good virtualenv
    #
    ve = which_virtualenv(full=True)
    if ve == os.path.realpath(envname) and is_python_version(minversion=minversion,maxversion=maxversion):
        return sys.executable
        
    #
    # Check if the virtualenv exist
    # 
        
    python = None
    
    if os.path.isdir(envname):
        python = os.path.join(envname,'bin','python')
        ok = (is_python_version(python,
                                minversion=minversion,
                                maxversion=maxversion) and 
              is_a_virtualenv_python(python))
        
        
        #
        # The virtualenv already exist but it is not ok
        #
        if not ok:
            raise DistutilsError("A virtualenv %s already exists but not with the required python")
                 
    else:
        ok = False
                
        
    #
    # Creates a new virtualenv
    #
    if not ok:
        venv.create(envname, 
                    system_site_packages=False, 
                    clear=True, 
                    symlinks=False, 
                    with_pip=True)
                
        # check the newly created virtualenv
        return serenity_virtualenv(envname,package,version)
    
    return os.path.realpath(python)
    
    
    