# -*- coding: utf-8 -*-

from obscheme.fields.integer import IntegerField


########################################################################
class Int32Field(IntegerField):

    #----------------------------------------------------------------------
    def __init__(self):
        IntegerField.__init__(self, min_value=-2147483648, max_value=2147483647)


########################################################################
class UnsignedInt32Field(IntegerField):

    #----------------------------------------------------------------------
    def __init__(self):
        IntegerField.__init__(self, min_value=0, max_value=4294967295)
