#!/usr/bin/env python
import inspect
import os
from decorator import decorator
from objectname import objectname
from public import public

OSNAME=os.uname()[0]

def raise_OSError(f,msg):
    raise OSError("%s %s" % (objectname(f,fullname=True),msg))


@decorator
@public
def linux(f,*args,**kw):
    if OSNAME!="Linux":
        raise_OSError(f,"is Linux only :(")
    return f(*args,**kw)


@decorator
@public
def osx(f,*args,**kw):
    if OSNAME!="Darwin":
        raise_OSError(f,"is OS X only :(")
    return f(*args,**kw)


@decorator
@public
def unix(f,*args,**kw):
    if OSNAME=="Windows":
        raise_OSError(f,"is Unix only :(")
    return f(*args,**kw)

@decorator
@public
def windows(f,*args,**kw):
    if OSNAME!="Windows":
        raise_OSError(f,"is Windows only :(")
    return f(*args,**kw)

