'''
Created on 2 oct. 2014

@author: coissac
'''

import imp
import importlib

from distutils.errors import DistutilsError
from distutils.version import StrictVersion  
from distutils import log       

from obidistutils.serenity.globals import local_cython  # @UnusedImport

from obidistutils.serenity.checkpip import get_a_pip_module

from obidistutils.serenity.checkpackage import get_package_requirement
from obidistutils.serenity.checkpackage import parse_package_requirement
from obidistutils.serenity.checkpackage import is_installed
from obidistutils.serenity.checkpackage import pip_install_package

from obidistutils.serenity.util import get_serenity_dir


def get_a_cython_module(pip=None):
    
    global local_cython

    if not local_cython:
        if pip is None:
            pip = get_a_pip_module()
         
        
        cython_req = get_package_requirement('Cython',pip)
        if cython_req is None:
            cython_req='Cython'
        
        requirement_project,requirement_relation,minversion = parse_package_requirement(cython_req)  # @UnusedVariable
        
        
        
        if cython_req is None or not is_installed(cython_req, pip):
            tmpdir = get_serenity_dir()
            
            ok = pip_install_package(cython_req,directory=tmpdir,pip=pip)
            
            log.debug('temp install dir : %s' % tmpdir)
                
            if ok!=0:
                raise DistutilsError, "I cannot install a cython package"
    
            f, filename, description = imp.find_module('Cython', [tmpdir])
            
            cythonmodule = imp.load_module('Cython', f, filename, description)
            
            if minversion is not None:
                assert StrictVersion(cythonmodule.__version__) >= minversion, \
                       "Unable to find suitable version of cython get %s instead of %s" % (cythonmodule.__version__,
                                                                                        minversion)
    
        else:
            cythonmodule = importlib.import_module('Cython') 
            
        local_cython.append(cythonmodule)
           
    return local_cython[0]

        

    
    
