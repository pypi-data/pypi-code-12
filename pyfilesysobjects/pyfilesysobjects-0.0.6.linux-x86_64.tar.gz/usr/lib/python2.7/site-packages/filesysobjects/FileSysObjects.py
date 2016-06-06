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
__version__ = '0.0.6'
__uuid__='9de52399-7752-4633-9fdc-66c87a9200b8'

__docformat__ = "restructuredtext en"

import os,sys
version = '{0}.{1}'.format(*sys.version_info[:2])
if version < '2.7': # pragma: no cover
    raise Exception("Requires Python-2.7.* or higher")

from filesysobjects.PySourceInfo import getCallerFilePathName

class FileSysObjectsException(Exception):
    pass

def addPathToSearchPath(spath,plist=None,**kargs):
    """Adds a path to plist. 

    Args:
        spath: A path to be added to 'plist'.
            The following casess are supported.
            
            0. spath is absolute, just added.
            1. spath is relative and present in
                current working directory, added
                py prefixing 'pwd'.
            2. spath is relative, searched in plist
                for an insertion hook, added when 
                found as absolute.
        
        searched in plist, and
            included when found. The path could be 
            either relative, or absolute. When a 
            relative is provided, the plist is used
            as prefix-base for the search.

            default := caller-file-position.
        
        plist: List to for the storage.
        
            default := sys.path

        **kargs:
            searchplist: Defines a search list 
                different from plist.
            
            prepend: Prepend, this is equal to
                pos=0.
                
            append: Append, this is equal to
                pos=len(plist).
                
            pos=#pos: A specific position for insertion
                within range(0,len(plist)).
            
            'matchcnt'=#num: Increment of hook 
                matched insertion when a relative path 
                is provided. Range:{0..}

    Returns:
        When successful returns insertion position, else a 'value<0'.

    Raises:
        passed through exceptions:
    """
    if plist == None:
        plist = sys.path

    _splist = kargs.get('searchplist',plist)

    pos = 0
    matchcnt = 0
    for k,v in kargs.items():
        if k == 'prepend':
            pos = 0
        elif k == 'append':
            pos = -1
        elif k == 'pos':
            if not type(v) is int:
                raise FileSysObjectsException("Digits required for 'pos'*"+str(pos)+")")
            pos = v
        elif k == 'matchcnt':
            if not type(v) is int:
                raise FileSysObjectsException("Digits required for 'matchcnt'*"+str(matchcnt)+")")
            matchcnt = v

    if spath and len(spath) >6 and spath[0:7] == 'file://':
        spath = os.sep + spath[7:].lstrip(os.sep) 

    if os.path.isabs(spath):
        pass
    elif os.path.exists(os.path.curdir+os.sep+spath):
        spath = os.path.normpath(os.path.curdir+os.sep+spath)
    else:
        for s in _splist:
            if os.path.exists(s+os.sep+spath):
                spath = s+os.sep+spath
                break
    
    if pos == -1:
        plist.append(spath)
        pos = len(plist)-1
    else:
        plist.insert(pos,spath)

    #TODO: possible error conditions 
    return pos

def findRelPathInSearchPath(spath,plist=None,**kargs):
    """Searches the upper tree path list for matching objects in side-branches

    Args:
        spath: A relative path to a directory or file.
            Some examples are 'myscript.sh', 
            'epyunit/myscript.sh',or 'bin/epyunit'.

            The following casess are supported.
            
            0. spath is absolute, just returned.
            1. spath is relative and present in
                current working directory, added
                py prefixing 'pwd'.
            2. spath is relative, searched in plist
                for a insertion hook, added when 
                found as absolute.

        plist: List with path entries to search each, first 
            match condition wins.

            default := sys.path

        **kargs:
            'matchcnt'=#num: Increment of hook 
                matched insertion when a relative path 
                is provided. Range:{0..}

    Returns:
        When successful returns the absolute pathname, else 'None'.

    Raises:
        passed through exceptions:
    """
    if plist == None:
        plist = sys.path
    matchcnt = kargs.get('matchcnt',0)
    _minc=0

    if spath and len(spath) >6 and spath[0:7] == 'file://':
        spath = os.sep + spath[7:].lstrip(os.sep) 

    if os.path.exists(spath):
        return os.path.normpath(spath)
    elif os.path.exists(os.path.curdir+os.sep+spath):
        return os.path.normpath(os.path.curdir+os.sep+spath)
    else:
        for p in plist:
            if os.path.exists(p+os.sep+object):
                if _minc == matchcnt:
                    return os.path.normpath(os.path.abspath(p+os.sep+object))
                _minc += 1
    return None

def findRelPathInUpperTree(spath,start=None,top=None,**kargs):
    """Searches the upper tree path list for matching objects in side-branches.
    
    Args:
        spath: A relative path to a directory or file.
            Some examples are 'myscript.sh', 'epyunit/myscript.sh', or
            'bin/epyunit'.

        plist: List with path entries to search each, first match wins.
        
            default := sys.path

    Returns:
        When successful returns the absolute pathname, else 'None'.

    Raises:
        passed through exceptions:
    """
    plist = []
    matchcnt = 0
    _minc=0
    for k,v in kargs.items():
        if k == 'matchcnt':
            if not v.isdigit():
                raise FileSysObjectsException("Digits required for 'matchcnt'*"+str(matchcnt)+")")
            matchcnt = v

    if top and len(top) >6 and top[0:7] == 'file://':
        top = os.sep + top[7:].lstrip(os.sep) 
    if start and len(start) >6 and start[0:7] == 'file://':
        start = os.sep + start[7:].lstrip(os.sep) 

    if not setUpperTreeSearchPath(start,top,plist,**kargs):
        return False

    for p in plist:
        if os.path.exists(p+os.sep+spath):
            if _minc == matchcnt:
                return os.path.normpath(os.path.abspath(p+os.sep+spath))
            _minc += 1

    return None

def setUpperTreeSearchPath(start=None,top=None,plist=None,**kargs):
    """Extends the search by sys.path for each subdir from 'start' on upward to 'top'.
    
    Prepends a set of search paths into plist. The set of search 
    paths contains of each directory beginning with provided start 
    position. The inserted path is normalized by default
    
    **REMARK**: The current version calls 'os.path.normpath' by 
        default - when 'raw' is not selected. This is consistently
        the case for the parameters:
            start
            top
            plist
        
        Thus generally clears double slashes, but also replaces 
        symbolic links, so later literal post processing e.g. for
        match based processing should be normalized too.
        
        There is one exception due to for leading '//', see option
        'ignore-app-slash':

            IEEE Std 1003.1™, 2013 Edition; 4.12 Pathname Resolution;
            see msg260024 - https://bugs.python.org/issue26329#msg260024 
        This has to be considered in particular for the parameters
            start
            top
        where a leading double slash also implies this to be an absolute
        path, thus the pattern match is performed as leading pattern
        only. 
    
    The search path extension for upward-search simulates polymorphic
    inheritance by starting at the deepest and recursively searching
    the present file at the lowest position of the directory tree.
    This is in the sense of OO the super position of the method by 
    the most specialized derivation.

    The typical application is the grouping of imported modules/classes
    for test cases by file-inheritance from upper tree. This provides 
    the hierarchical configuration and specialization of test cases 
    with pre-defined default components by multiple levels of 
    configuration files.

    Args:
        start: Start directory or file, when a file is 
            provided the directory portion is used as
            the starting pointer.

            default := caller-file-position.
        
        top: End directory name. This is used as a match string 
            for processing literally. So actually no filesystem
            semantic is applied. The path separators has to be
            in accordance to the OS, and/or os.path.normpath.
            Providing absolute paths still match, because of
            the string, but eventually match multiple times due
            to the match-string only semantics. 
        
            default := <same-as-start>

        plist: List to for the storage.
        
            default := sys.path
            
        **kargs:
            'matchcnt'=#num: Increment of match
                for top node when multiple are in 
                the path. The count begins from top, 
                so #num(1) will match M(1) in:
                
                    /a/b/M/c/M/d/M/w/e/M/bottom
                         0   1   2     3
                             *

            'matchcntupward'=#num: Increment of match
                for top node when multiple are in 
                the path. The count begins from bottom, 
                so #num(2) will match M(2) in:
                
                    /a/b/M/c/M/d/M/w/e/M/bottom
                         3   2   1     0
                             *

            'relonly': The paths are inserted relative to the
                top node only. This is mainly for test 
                purposes. The intermix of relative and
                absolute path entries is not verified.

            'prepend': Prepends the set of search paths.
                This is default.

            'append': Appends the set of search paths.
            
            'unique': Insert non-present only, else present
                entries are not checked, thus the search order
                is changed in general for 'prepend', while
                for 'append' the present still covers the new
                entry. 
            
            'reverse': This reverses the resulting search order 
                 from bottom-up to top-down.

            'raw': Suppress normalization by call of 
                'os.path.normpath'.

            'ignore-app-slash': Treats for local file names any 
                number of subsequent '/' only as one, also leading 
                pattern '//[^/]+'. URI prefixes are treated correctly.
                Current supported URIs:
                    'file://'.

                See also "IEEE Std 1003.1(TM), 2013 Edition; Chap. 4.12".

    Returns:
        When successful returns 'True', else returns either 'False', 
        or raises an exception.

    Raises:
        passed through exceptions:
    """
    if plist == None:
        plist = sys.path
    
    _relo = False
    matchcnt = 0
    matchcntupward = -1
    reverse = False
    unique = False
    prepend = True
    _raw = False
    _ias = False

    for k,v in kargs.items():
        if k == 'relonly':
            _relo = True
        elif k == 'matchcnt':
            if not type(v) is int:
                raise FileSysObjectsException("Digits only matchcnt:"+str(v))
            matchcnt = v
        elif k == 'matchcntupward':
            if not type(v) is int:
                raise FileSysObjectsException("Digits only matchcntupward:"+str(v))
            matchcntupward = v
        elif k == 'reverse':
            reverse = True
        elif k == 'unique':
            unique = True
        elif k == 'append':
            prepend = False
        elif k == 'prepend':
            prepend = True
        elif k == 'raw':
            _raw = True
        elif k == 'ignore-app-slash':
            _ias = True

    if matchcnt > 0:
        matchcntupward = -1
        

    #
    # Prepare search path list
    # if decided to normalize, and whether to ignore leading '//'
    #
    if _raw: # match basically literally
        if not _ias:
            _plst = plist
        else:
            _plst = []
            for i in plist:
                if _ias and i[0:1] == '//':
                    _plst.append(i[1:])
                else:
                    _plst.append(i)

    else: # normalize for safer match conditions
        _plst = []
        for i in plist:
            if _ias and i[0:1] == '//':
                _plst.append(os.path.normpath(i[1:]))
            else:
                _plst.append(os.path.normpath(i))


    # 0. prep start dir
    if start == '':
        raise FileSysObjectsException("Empty top:''")
    elif start == None:
        start = getCallerFilePathName(2) # caller file

    #
    # adapt match pattern when decided to ignore IEEE-1003.1-4.2
    #
    # EXCEPTIONAL CASES: for now adapt to os.path.normpath, 
    # thus ignore IEEE-1003.1-4.2, see bugs.python.org: issue 27228
    #  'file://top/x/y'       => [ '', '/x/y', ]
    #  'file:///top/x/y'      => [ '/', '/x/y', ]
    #  'file:////top/x/y'     => [ '/', '/x/y', ]
    #  'file://///top/x/y'    => [ '/', '/x/y', ]
    #
    if top and len(top) >6 and top[0:7] == 'file://':
        top = os.sep + top[7:].lstrip(os.sep) 
    if start and len(start) >6 and start[0:7] == 'file://':
        start = os.sep + start[7:].lstrip(os.sep) 

    #
    # adapt match pattern when decided to ignore IEEE-1003.1-4.2
    #
    # EXCEPTIONAL CASES: IEEE-1003.1-4.2
    #  '//'                   => [ '//', ]
    #  '//top/x/y'            => [ '//', '/x/y', ]
    #
    if _ias: # ignore IEEE1003.1-4.2, so pre-process normpath
        if top and len(top) > 1 and top[0:2] == '//':
            top = os.sep + top[1:].lstrip(os.sep) 
        if start and len(start) > 1 and start[0:2] == '//':
            start = os.sep + start[1:].lstrip(os.sep) 

    if top and len(top) > 1:
        if top[-1] == os.sep:
            top = os.path.normpath(top) + os.sep
        else:
            top = os.path.normpath(top)
    if start and len(start) > 1:
        if start[-1] == os.sep:
            start = os.path.normpath(start) + os.sep 
        else:
            start = os.path.normpath(start) 

    # for now fixed
    start = os.path.abspath(start)

    if os.path.isfile(start):
        start = os.path.dirname(start) # we need dir
    if not os.path.exists(start):
        raise FileSysObjectsException("Missing start:"+str(start)) 

    # 1. prep top dir
    if top == '':
        raise FileSysObjectsException("Empty top:''")
    
    #
    # start upward recursion now
    #
    def _addsub(x,pl=plist):
        """...same for all."""
        if unique and x in pl or x in plist:
            return False
        if reverse:
            pl.append(x)
        else:
            pl.insert(0,x)

    # find top
    if top:
        a = start.split(top)
        if len(a) == 1: # top is not in start
            raise FileSysObjectsException("Missing top:"+str(top))

        if matchcnt >= len(a): # check valid range
            raise FileSysObjectsException("Match count out of range:"+str(matchcnt)+">"+str(len(a)))
        elif matchcntupward >0 and matchcntupward >= len(a): # check valid range
            raise FileSysObjectsException("Match count out of range:"+str(matchcntupward)+">"+str(len(a)))

    else:
        if matchcnt>0:
            raise FileSysObjectsException("Match count out of range:"+str(matchcnt)+"> 0")
        if matchcntupward>0:
            raise FileSysObjectsException("Match count out of range:"+str(matchcntupward)+"> 0")
        _addsub(start)
        return True



    #
    # so we have actually at least one top within valid range and a remaining sub-path - let us start
    #
    
    #
    # IF: top as prefix, following cases are possible/tested:
    #  'top'                 => [ '', '', ]
    #  'top/x/top'           => [ '', '/x/', '', ]
    #  'top/x/top/'          => [ '', '/x/', '/', ]
    #
    # ELSE: various combinations
    #  '/top/x/y'            => [ '/', '/x/y', ]
    #  '/top/x/top/y'        => [ '/', 'x', 'y', ]
    #  '/top/x/top/y/top'    => [ '/', '/x/', '/y/', '' ]
    #  '/top/x/top'          => [ '/', '/x/' , '', ]
    #  '/top/x/y/'           => [ '/', '/x/y/', ]
    #  '/top/x/top/y/'       => [ '/', '/x/', '/y/', ]
    #  '/top/x/top/y/top/v'  => [ '/', '/x/', '/y/', '/v' ]
    #  '/top/x/top/'         => [ '/', '/x/', '/', ]
    #  '/top/x/top/'         => [ '/', '/x/', '/', ]
    #
    if a == ['','']: # top == start
        if matchcnt>0:
            raise FileSysObjectsException("Match count out of range:"+str(matchcnt)+"> 0")
        if matchcntupward>0:
            raise FileSysObjectsException("Match count out of range:"+str(matchcnt)+"> 0")
        _addsub(start)
        return True

    elif a[0] == '': # top is prefix
        _tpath = top

        if matchcntupward >=0:
            mcnt = len(a)-1-matchcntupward
        else:
            mcnt = matchcnt

        _spath = top.join(a[mcnt+1:]) # sub-path for search recursion
    else:
        if matchcntupward >=0:
            mcnt = len(a)-1-matchcntupward
        else:
            mcnt = matchcnt+1

        _tpath = top.join(a[:mcnt])+top # top path as search hook
        _spath = top.join(a[mcnt:]) # sub-path for search recursion

    if _relo: # relative paths, mainly for test
        curp = ''
    else:
        curp = os.path.normpath(_tpath)
        if curp not in plist: # insert top itself
            _addsub(curp)

    a = _spath.split(os.sep)
    if prepend:
        for p in a:
            if not p:
                continue
            curp = os.path.join(curp,p)
            _addsub(curp)
    else:
        _buf = []
        for p in a:
            if not p:
                continue
            curp = os.path.join(curp,p)
            _addsub(curp,_buf)
        plist.extend(_buf)

    return True

