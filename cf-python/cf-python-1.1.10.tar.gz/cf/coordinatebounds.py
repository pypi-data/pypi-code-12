from .variable import Variable


# ====================================================================
#
# CoordinateBounds object
#
# ====================================================================

class CoordinateBounds(Variable):
    '''
    
A CF coordinate's bounds object containing cell boundaries or
intervals of climatological time. The parent coordinate's
`!climatology` attribute indicates which type of bounds are present.

'''
    # ----------------------------------------------------------------
    # Attribute (read only)
    # ----------------------------------------------------------------
    @property
    def lower_bounds(self):
        '''

The lower coordinate bounds in a `cf.Data` object.

``b.lower_bounds`` is equivalent to ``b.data.min(axes=-1)``.

.. seealso:: `upper_bounds`

:Examples:

>>> print b.array
[[ 5  3]
 [ 3  1]
 [ 1 -1]]
>>> b.lower_bounds
<CF Data: [3, ..., -1]>
>>> print b.lower_bounds.array
[ 3  1 -1]

'''
        if not self._hasData:
            raise ValueError("Can't get lower bounds when there are no bounds")

        return self.data.min(-1).squeeze(-1, i=True)
    #--- End: def

    # ----------------------------------------------------------------
    # Attribute (read only)
    # ----------------------------------------------------------------
    @property
    def upper_bounds(self):
        '''

The upper coordinate bounds in a `cf.Data` object.

``b.upper_bounds`` is equivalent to ``b.data.max(axes=-1)``.

.. seealso:: `lower_bounds`

:Examples:

>>> print b.array
[[ 5  3]
 [ 3  1]
 [ 1 -1]]
>>> b.upper_bounds      
<CF Data: [5, ..., 1]>
>>> b.upper_bounds.array     
array([5, 3, 1])

'''
        if not self._hasData:
            raise ValueError("Can't get upper bounds when there are no bounds")

        return self.data.max(-1).squeeze(-1, i=True)
    #--- End: def

    def contiguous(self, overlap=True, direction=None):
        '''
      
Return True if the bounds are contiguous.

Bounds are contiguous if the cell boundaries match up, or
overlap, with the boundaries of adjacent cells.

In general, it is only possible for 1 or 0 dimensional coordinates
with bounds to be contiguous, but size 1 coordinates with any number
of dimensions are always contiguous.

An exception occurs if the coordinate is multdimensional and has more
than one element.

'''
        if not self._hasData:
            return False    

        nbounds = self.shape[-1]

        if self.size == nbounds:
            return True

        if nbounds == 4 and self.ndim ==3:
            if overlap == True:
                raise ValueError("Cannot tell if 2D coordinate bounds are" +
                                 " contiguous if overlap is True.")
            bnd = self.array
            for j in xrange(self.shape[0] - 1):
                for i in xrange(self.shape[1] - 1):
                    # check cells (j, i) and cells (j, i+1) are contiguous
                    if bnd[j,i,1] != bnd[j,i+1,0] or \
                       bnd[j,i,2] != bnd[j,i+1,3]:
                        return False
                    # check cells (j, i) and (j+1, i) are contiguous
                    if bnd[j,i,3] != bnd[j+1,i,0] or \
                       bnd[j,i,2] != bnd[j+1,i,1]:
                        return False
            return True

        if  nbounds > 2 or self.ndim > 2:
            raise ValueError(
"Can't tell if a multidimensional coordinate bounds are contiguous")

        data = self.Data
        
        if not overlap: 
            return data[1:, 0].equals(data[:-1, 1])
        else:
            if direction is None:
                b = data[(0,)*(data.ndim-1)].array
                direction =  b.item(0,) < b.item(1,)
            #--- End: if
        
            if direction:
                return (data[1:, 0] <= data[:-1, 1]).all()
            else:
                return (data[1:, 0] >= data[:-1, 1]).all()
    #--- End: def

#--- End: class
