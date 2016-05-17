#!/usr/bin/env python
# -*- coding: utf-8 -*-
from field import field


def varchar(name="", comment="", length=255, default=None, not_null=False):
    return field(name=name, type="varchar",length=length, default=default, not_null=not_null, comment=comment, auto_incr=None, unsigned=None)

def text(name="",comment=""):
    return field(name=name, type="text",length=None, default=None, not_null=False, comment=comment, auto_incr=None, unsigned=None)

def id(name="", comment=""):
    return field(name=name, type="int",length=11, default=None, not_null=False, comment=comment, auto_incr=True, unsigned=True)

def int(name="", comment="", unsigned=False,length=11, default=None ,auto_incr=False):
    return field(name=name, type="int",length=length, default=default, not_null=False, comment=comment, auto_incr=auto_incr, unsigned=unsigned)

def tinyint(name="", comment="", unsigned=False, length=1, default=None):
    return field(name=name, type="tinyint",length=length, default=default, not_null=False, comment=comment, auto_incr=None, unsigned=unsigned)
def decimal(name="",comment="",unsigned=False,length="11,2", default=None):
    # print default
    return field(name=name, type="decimal",length=length, default=default, not_null=False, comment=comment, auto_incr=None, unsigned=unsigned)

def datetime(name="",comment="",default=None):
    return field(name=name, type="datetime",length=None, default=default, not_null=False, comment=comment, auto_incr=None, unsigned=None)

def guid(name="guid",comment="",length=36,default=None):
    return field(name=name, type="char",length=length, default=default, not_null=False, comment=comment, auto_incr=None, unsigned=None)
def char(name="", comment="", length=11,default=None):
    return field(name=name, type="char",length=length, default=default, not_null=False, comment=comment, auto_incr=None, unsigned=None)


def float(name="",comment="",unsigned=False,length="11,2", default=None):
    # print default
    return field(name=name, type="float",length=length, default=default, not_null=False, comment=comment, auto_incr=None, unsigned=unsigned)
