# -*- coding: utf-8 -*-

from obscheme.fields.integer import IntegerField


########################################################################
class Int64Field(IntegerField):

    #----------------------------------------------------------------------
    def __init__(self):
        IntegerField.__init__(self, min_value=-9223372036854775808, max_value=9223372036854775807)


########################################################################
class UnsignedInt64Field(IntegerField):

    #----------------------------------------------------------------------
    def __init__(self):
        IntegerField.__init__(self, min_value=0, max_value=18446744073709551615)
