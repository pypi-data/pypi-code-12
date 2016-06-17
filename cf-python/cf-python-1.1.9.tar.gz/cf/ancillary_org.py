from .variable import Variable


# ====================================================================
#
# Ancillary object
#
# ====================================================================

class Ancillary(Variable):
    '''
'''
    def __ancillary__(self):
        '''
Returns a new reference to self.
'''
        return self
    #--- End: def

    @classmethod
    def asancillary(cls, a, copy=False):
        '''Convert the input to a `cf.Ancillary` object.

:Parameters:

    a : data-like
        Input data in any form that can be converted to an cf.Data
        object. This includes `cf.Data` and `cf.Field` objects, numpy
        arrays and any object which may be converted to a numpy array.

:Returns:

    out : cf.Data
        cf.Data interpretation of *d*. No copy is performed on the
        input.

:Examples:

>>> d = cf.Data([1, 2])
>>> cf.Data.asdata(d) is d
True
>>> d.asdata(d) is d
True

>>> cf.Data.asdata([1, 2])
<CF Data: [1, 2]>

>>> cf.Data.asdata(numpy.array([1, 2]))
<CF Data: [1, 2]>

        '''
        ancillary = getattr(a, '__ancillary__', None)
        if ancillary is None:
            return cls(a)

        ancillary = ancillary()
        if copy:
            return ancillary.copy()
        else:
            return ancillary
    #--- End: def
