#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals


class EC3Exception(Exception):
    pass


class InvalidInput(EC3Exception):
    pass


class UnsupportedMethod(EC3Exception):
    pass


class NoInstancesFound(EC3Exception, LookupError):
    pass
