# -*- coding: utf-8 -*-
"""The 'FileSysObjects' module provides basic file inheritance by directory hierarchies.  

This modules manages the file system based structure semantics for 
the automation of drop-in configurations. Therefore functions and classes
are provided for the modification of the search path and the location of
files and directories. Two examples are:

* The search for files and/or relative paths from a given 
    directory on upwards.
* The extension of search paths with any sub-directory portion 
    from a given directory on upwards.  

These two features already provide for basic inheritance 
features for files in directory hierarchies.

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

from filesysobjects.PySourceInfo import getSourceFilePathName

class FileSysObjectsException(Exception):
    pass

def setUpperTreeSearchPath(start=None,top=None,plist=None):
    """Extends the search by sys.path for each subdir from 'start' on upward to 'top'.
    
    Prepends a set of search paths into sys.path. The set of search 
    paths contains of each directory beginning with provided start 
    position. This enables a "polymorphic inheritance view" onto the 
    file system structure.
    
    The typical application is the grouping of imported modules/classes
    for test cases by file-inheritance from upper tree. This provides 
    the hierarchical configuration and specialization of test cases 
    with pre-defined default components by multiple levels of 
    configuration files. 

    Args:
        start: Start directory.

            default := caller-file-position.
        
        top: End directory.
        
            default := start

        plist: List to for the storage.
        
            default := sys.path

    Returns:
        When successful returns 'True', else returns either 'False', or
        raises an exception.

    Raises:
        passed through exceptions:
    """
    if plist == None:
        plist = sys.path

    # 0. prep start dir
    if start == '':
        raise FileSysObjectsException("Empty top:''")
    elif start == None:
        start = getSourceFilePathName(2) # caller file
    s = os.path.abspath(start)
    if os.path.isfile(start):
        s = os.path.dirname(s) # we need dir
    if not os.path.exists(s):
        raise FileSysObjectsException("Missing start:"+str(s)) 

    # 1. prep top dir
    if top == '':
        raise FileSysObjectsException("Empty top:''")
    elif top == None:
        plist.insert(0,s)
        return True
    else:
        a = s.split(top)
        
        if len(a) == 1: # top is not in start
            raise FileSysObjectsException("Missing top:"+str(top))

        elif a == ['','']: # handles top==start
            plist.insert(0,top)
            return True
        
        elif len(a)>2: # multiple occurances, for not not supported
            raise FileSysObjectsException("Ambigious top:"+str(top)) # top more than once in start
        
        else: # exactly 2 - one only
            
            if a[0] == '': # top was prefix
                a = a[1]
                curp = top
                plist.insert(0,curp)
                a = a.split(os.sep)
            
                for p in a:
                    curp = os.path.join(curp,p)
                    if p != '':
                        curp += os.sep
                    plist.insert(0,curp)

            else: # actual top
                curp = os.path.normpath(a[0]+os.sep+top)
                plist.insert(0,curp)

                a = a[1].split(os.sep)
                            
                for p in a:
                    if not p:
                        continue
                    curp = os.path.join(curp,p)
                    if p != '':
                        curp += os.sep
                    plist.insert(0,curp)

    return True

def findRelPathInUpperTree(object,plist=None):
    """Searches the upper tree path list for matching objects in side-branches.
    
    Args:
        object: A relative path to a directory or file.
                Some examples are 'myscript.sh', 'epyunit/myscript.sh', or
                'bin/epyunit'.

        plist: List with path entries to search each, first match wins.
        
            default := sys.path

    Returns:
        When successful returns the absolute pathname, else 'None'.

    Raises:
        passed through exceptions:
    """
    if plist == None:
        plist = sys.path
    for p in plist:
        if os.path.exists(p+os.sep+object):
            return os.path.normpath(os.path.abspath(p+os.sep+object))

    return None

