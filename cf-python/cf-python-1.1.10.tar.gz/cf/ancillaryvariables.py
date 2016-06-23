from .fieldlist import FieldList


# ====================================================================
#
# AncillaryVariables object
#
# ====================================================================

class AncillaryVariables(FieldList):
    '''

A sequence of ancillary variable fields stored in a list-like object.

'''
    def equals(self, other, rtol=None, atol=None,
               ignore_fill_value=False, traceback=False):
        '''

True if two instances are equal, False otherwise.

Two instances are equal if their attributes are equal and their
elements are equal set-wise (i.e. the order of the lists is
irrelevant).

:Parameters:

    other : 
        The object to compare for equality.

    atol : float, optional
        The absolute tolerance for all numerical comparisons, By
        default the value returned by the `ATOL` function is used.

    rtol : float, optional
        The relative tolerance for all numerical comparisons, By
        default the value returned by the `RTOL` function is used.

    ignore_fill_value : bool, optional
        If True then data arrays with different fill values are
        considered equal. By default they are considered unequal.

    traceback : bool, optional
        If True then print a traceback highlighting where the two
        instances differ.

:Returns: 

    out : bool
        Whether or not the two instances are equal.

:Examples:

'''
        return self.set_equals(other, rtol=rtol, atol=atol,
                               ignore_fill_value=ignore_fill_value,
                               traceback=traceback)
   #--- End: def

#--- End: class
