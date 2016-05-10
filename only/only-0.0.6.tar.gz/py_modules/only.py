#!/usr/bin/env python
import sys
from decorator import decorator
from objectname import objectname
from public import public

PLATFORM=sys.platform # linux,win32,cygwin,darwin

def raise_OSError(f,msg):
    raise OSError("%s %s" % (objectname(f,fullname=True),msg))


@decorator
@public
def linux(f,*args,**kw):
    if PLATFORM!="linux":
        raise_OSError(f,"is Linux only :(")
    return f(*args,**kw)


@decorator
@public
def osx(f,*args,**kw):
    if PLATFORM!="darwin":
        raise_OSError(f,"is OS X only :(")
    return f(*args,**kw)


@decorator
@public
def unix(f,*args,**kw):
    if PLATFORM=="win32":
        raise_OSError(f,"is Unix only :(")
    return f(*args,**kw)

@decorator
@public
def windows(f,*args,**kw):
    if PLATFORM!="win32":
        raise_OSError(f,"is Windows only :(")
    return f(*args,**kw)

