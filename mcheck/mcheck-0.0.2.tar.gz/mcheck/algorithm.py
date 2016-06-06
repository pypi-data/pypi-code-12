#!/usr/bin/env python
# -*- coding: utf-8 -*-

import hashlib

def md5compute(str):
    m = hashlib.md5()
    m.update(str)
    return m.hexdigest()

def sha1compute(str):
    s = hashlib.sha1()
    s.update(str)
    return s.hexdigest()

def sha224compute(str):
    s = hashlib.sha224()
    s.update(str)
    return s.hexdigest()

def sha256compute(str):
    s = hashlib.sha256()
    s.update(str)
    return s.hexdigest()

def sha384compute(str):
    s = hashlib.sha384()
    s.update(str)
    return s.hexdigest()

def sha512compute(str):
    s = hashlib.sha512()
    s.update(str)
    return s.hexdigest()


def isSignatureExist(signature):
    if signature in strategy or signature == None:
        return True
    else:
        return False

strategy = {
    "md5": md5compute,
    "sha1": sha1compute,
    "sha224": sha224compute,
    "sha256": sha256compute,
    "sha384": sha384compute,
    "sha512": sha512compute
}