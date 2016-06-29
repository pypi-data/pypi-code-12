# -*- coding: utf-8 -*-
"""
    obscheme.util
    ~~~~~~~~~~~~~

    :copyright: (c) 2016 by Thomas Wiebe.
    :license: BSD, see LICENSE for more details.
"""


########################################################################
class InitializationEnforcer(object):

    #----------------------------------------------------------------------
    def __getattribute__(self, name):
        raise RuntimeError('Schema not correctly initialized. Please make sure to call __init__() on Schema.')
