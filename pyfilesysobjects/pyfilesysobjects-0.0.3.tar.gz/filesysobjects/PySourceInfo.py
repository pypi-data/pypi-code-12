# -*- coding: utf-8 -*-
"""PySourceInfo - runtime type information on Python source location: package, module, and caller.  

This modules provides for the location of Python execution 
by means of the package 'inspect' extended by additional sources
for a simple API.

The stack frame of inspect is in particular reduced to the common 
parameter 'spos', which is an abstraction of the 'stack-position'
representing the level of history within the caller level.
The value 'spos==0' is the function itself, whereas 'spos==1' is the 
first level caller. Consequently 'spos==2' is the caller of the caller,
etc.  

The categories of provided RTTI comprise:
 
* **packages** - Python packages.

* **modules** - Python modules - a.k.a. source files.

* **callers** - Python functions and class/object methods.


Where the following attributes are available:

* name(package, module, function)

* OID - dotted relative path to matching item of sys.path

* filename

* filepathname

* item of sys.path

* relative path to item of sys.path

* line number

Dependent on the call context, some of the attribute values may 
not be available.
E.g. when called from within the python/ipython shell, or 'main'.

The API is designed here as a collection of slim functions 
only in order to avoid any overhead for generic application.

"""
from __future__ import absolute_import

__author__ = 'Arno-Can Uestuensoez'
__license__ = "Artistic-License-2.0 + Forced-Fairplay-Constraints"
__copyright__ = "Copyright (C) 2010-2016 Arno-Can Uestuensoez @Ingenieurbuero Arno-Can Uestuensoez"
__version__ = '0.0.3'
__uuid__='9de52399-7752-4633-9fdc-66c87a9200b8'

__docformat__ = "restructuredtext en"

import os,sys
version = '{0}.{1}'.format(*sys.version_info[:2])
if version < '2.7': # pragma: no cover
    raise Exception("Requires Python-2.7.* or higher")

import inspect 


class PySourceInfoException(Exception):
    pass

def getSourceFilePathName(spos=1):
    """Returns the pathname of caller source file.

    Args:
        spos: Start position in the stack.

    Returns:
        Returns the filepathname.

    Raises:
        passed through exceptions:
    """
    return inspect.stack()[spos][1]

def getSourceFuncName(spos=1):
    """Returns the name of caller function.

    Args:
        spos: Start position in the stack.

    Returns:
        Returns the filepathname.

    Raises:
        passed through exceptions:
    """
    return inspect.stack()[spos][3]

def getSourceLinenumber(spos=1):
    """Returns the line number of caller.

    Args:
        spos: Start position in the stack.

    Returns:
        Returns the filepathname.

    Raises:
        passed through exceptions:
    """
    return inspect.stack()[spos][2]

def getCallerName(spos=1):
    """Returns the name of the caller.

    Args:
        spos: Start position in the stack.

    Returns:
        Returns the filepathname.

    Raises:
        passed through exceptions:
    """
    return inspect.stack()[spos][0].f_globals['__name__']

def getCallerNameOID(spos=1):
    """Returns the name of the package containing the caller.

    Args:
        spos: Start position in the stack.

    Returns:
        Returns the package name.

    Raises:
        passed through exceptions:
    """
    _spos = spos
    _sf = inspect.stack()
    if len(_sf) < _spos:
        return None
    _pf = _sf[_spos][0]
    _coid = inspect.getmodule(_pf)
    if _coid:
        _coid = _coid.__name__
    if 'self' in _pf.f_locals:
        _coid += "." + str(_pf.f_locals['self'].__class__.__name__)
    if _pf.f_code.co_name != '<module>':
        _coid += "." + str(_pf.f_code.co_name)
    del _pf
    return _coid

def getCallerPackageName(spos=1):
    """Returns the name of the package containing the caller.

    Args:
        spos: Start position in the stack.

    Returns:
        Returns the package name when defined, else None.

    Raises:
        passed through exceptions:
    """
    _sf = inspect.stack()
    if len(_sf) < spos:
        return None
    module = inspect.getmodule(_sf[spos][0])
    if module:
        return module.__package__
    
def getCallerPackagePathName(spos=1):
    """Returns the pathname to the package directory of the caller.

    Args:
        spos: Start position in the stack.

    Returns:
        Returns the path name to the package.

    Raises:
        passed through exceptions:
    """
    _sf = inspect.stack()
    if len(_sf) < spos:
        return None
    module = inspect.getmodule(_sf[spos][0])
    if module:
        if module.__package__:
            #FIXME: zip-files
            return getCallerModulePathName(spos+1)

def getCallerPackagePythonPath(spos=1):
    """Returns the pathname to the package directory of the caller.

    Intentionally the same as 'getCallerPackagePathName'.
 
    Args:
        spos: Start position in the stack.

    Returns:
        Returns the path name to the package.

    Raises:
        passed through exceptions:
    """
    return os.path.dirname(getCallerPackagePathName(spos+1))

def getCallerPackageFilePathName(spos=1):
    """Returns the name of the package containing the caller.

    Args:
        spos: Start position in the stack.

    Returns:
        Returns the package name.

    Raises:
        passed through exceptions:
    """
    return os.path.dirname(getCallerModuleFilePathName(spos+1))

def getCallerModuleFilePathName(spos=1):
    """Returns the filepathname of the module.

    Args:
        spos: Start position in the stack.

    Returns:
        Returns the filepathname of the caller module.

    Raises:
        passed through exceptions:
    """
    
    _sf = inspect.stack()
    if len(_sf) < spos:
        return None
    module = inspect.getmodule(_sf[spos][0])
    if module:
        return module.__file__

def getCallerModuleName(spos=1):
    """Returns the name of the caller module.

    Args:
        spos: Module name.

    Returns:
        Returns the name of caller module.
        The dotted object path is relative to 
        the actual used sys.path item.  

    Raises:
        passed through exceptions:
    """
    _sf = inspect.stack()
    if len(_sf) < spos:
        return None
    module = inspect.getmodule(_sf[spos][0])
    if module:
        return module.__name__

def getCallerModulePythonPath(spos=1):
    """Returns the prefix item from sys.path used for the caller module.

    Args:
        spos: Module name.

    Returns:
        Returns the name of caller module.

    Raises:
        passed through exceptions:
    """
    _mn = getCallerModuleName(spos+1).split('.')[:-1]
    _mn = os.sep.join(_mn)
    _r = getCallerModulePathName(spos+1).split(_mn)[0]
    if _r[-1] != os.sep: # was rel for split
        _r += os.sep
    return _r    

def getCallerModulePathName(spos=1):
    """Returns the pathname of the module.

    Args:
        m: Module name.

    Returns:
        Returns the filepathname of module.

    Raises:
        passed through exceptions:
    """
    return os.path.dirname(getCallerModuleFilePathName(spos+1))+os.sep

def getPythonPathPrefixMatchFromSysPath(pname,plist=None):
    """Gets the first matching prefix from sys.path.
    
    Foreseen to be used for canonical base reference in unit tests.
    This enables in particular for casual tests where absolute pathnames
    are required.

    Args:
        pname: Pathname.

    Returns:
        Returns the first matching path prefix from sys.path.

    Raises:
        passed through exceptions:
    """
    if not plist:
        plist = sys.path
    for sp in plist:
        if pname.startswith(sp):
            if sp and sp[-1] == os.sep:
                return sp
            return sp+os.sep

def getPythonPathModuleRel(fpname,plist=None):
    """Returns the relative path name of the filepathname.

    Args:
        fpname: The filepathname.

    Returns:
        Returns the path prefix for fpname.

    Raises:
        passed through exceptions:
    """
    if not plist:
        plist = sys.path
    for _sp in plist:
        if fpname.startswith(_sp):
            _r = fpname.replace(_sp,"")
            if _r and _r[0] == os.sep:
                return _r[1:]
            return _r

def getPythonPathForPackage(pname,plist=None):
    """Returns the item from sys.path for package.

    ATTENTION: This version relies on the common
        naming convention of pathnames.

    Args:
        pname: The name of the package.

    Returns:
        Returns the path item.

    Raises:
        passed through exceptions:
    """
    if not plist:
        plist = sys.path    
    _pn = pname.replace('.',os.sep)
    for _sp in sys.path:
        _pp = _sp.split(pname)
        if len(_pp) > 1:
            return _pp[0]
