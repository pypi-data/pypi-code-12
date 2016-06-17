from numpy import empty   as numpy_empty
from numpy import full    as numpy_full
from numpy import load    as numpy_load
from numpy import ndarray as numpy_ndarray
from numpy import save    as numpy_save

from numpy.ma import array     as numpy_ma_array
from numpy.ma import is_masked as numpy_ma_is_masked

from tempfile import mkstemp
from os       import close

from ..functions import parse_indices, get_subspace
from ..functions import inspect as cf_inspect
from ..constants import CONSTANTS


# ====================================================================
#
# FileArray object
#
# ====================================================================

class FileArray(object):
    '''

A sub-array stored in a file.
    
.. note:: Subclasses must define the following methods:
          `!__getitem__`, `!__str__`, `!close` and `!open`.
    
'''
    def __init__(self, **kwargs):
        '''
        
**Initialization**

:Parameters:

    file : str
        The netCDF file name in normalized, absolute form.

    dtype : numpy.dtype
        The numpy data type of the data array.

    ndim : int
        Number of dimensions in the data array.

    shape : tuple
        The data array's dimension sizes.

    size : int
        Number of elements in the data array.

'''
        self.__dict__ = kwargs
    #--- End: def
            
    def __deepcopy__(self, memo):
        '''

Used if copy.deepcopy is called on the variable.

'''
        return self.copy()
    #--- End: def

    def __repr__(self):
        '''

x.__repr__() <==> repr(x)

'''      
        return "<CF %s: %s>" % (self.__class__.__name__, str(self))
    #--- End: def
     
    def __str__(self):
        '''

x.__str__() <==> str(x)

'''
        return "%s in %s" % (self.shape, self.file)
    #--- End: def
    
    def copy(self):
        '''

Return a deep copy.

``f.copy() is equivalent to ``copy.deepcopy(f)``.

:Returns:

    out :
        A deep copy.

:Examples:

>>> g = f.copy()

'''
        C = self.__class__
        new = C.__new__(C)
        new.__dict__ = self.__dict__.copy()
        return new
#        return type(self)(**self.__dict__)
    #--- End: def
    
    def inspect(self):
        '''

Inspect the object for debugging.

.. seealso:: `cf.inspect`

:Returns: 

    None

'''
        print cf_inspect(self)
    #--- End: def
        
    def fff():
        pass

    def close(self):
        pass
    #--- End: def

    def open(self):
        pass
    #--- End: def

#--- End: class

# ====================================================================
#
# TempFileArray object
#
# ====================================================================

class TempFileArray(FileArray):
    ''' 

A indexable N-dimensional array supporting masked values.

The array is stored on disk in a temporary file until it is
accessed. The directory containing the temporary file may be found and
set with the `cf.TEMPDIR` function.

'''

    def __init__(self, array):
        '''

**Initialization**

:Parameters:

    array : numpy array
        The array to be stored on disk in a temporary file.        

:Examples:

>>> f = TempFileArray(numpy.array([1, 2, 3, 4, 5]))
>>> f = TempFileArray(numpy.ma.array([1, 2, 3, 4, 5]))

'''
#        array = kwargs.pop('array')
#
#        super(TempFileArray, self).__init__()

        # ------------------------------------------------------------
        # Use mkstemp because we want to be responsible for deleting
        # the temporary file when done with it.
        # ------------------------------------------------------------
        fd, _partition_file = mkstemp(prefix='cf_array_', suffix='.npy', 
                                      dir=CONSTANTS['TEMPDIR'])
        close(fd)

        # The name of the temporary file storing the array
        self._partition_file = _partition_file

        # Numpy data type of the array
        self.dtype = array.dtype

        # Tuple of the array's dimension sizes
        self.shape = array.shape

        # Number of elements in the array
        self.size = array.size

        # Number of dimensions in the array
        self.ndim = array.ndim

        if numpy_ma_is_masked(array):
            # Array is a masked array. Save it as record array with
            # 'data' and 'mask' elements because this seems much
            # faster than using numpy.ma.dump.
            self._masked_as_record = True
            numpy_save(_partition_file, array.toflex())
        else:
            self._masked_as_record = False
            if hasattr(array, 'mask'):
                # Array is a masked array with no masked elements
                numpy_save(_partition_file, array.view(numpy_ndarray))
            else:
                # Array is not a masked array.
                numpy_save(_partition_file, array)
    #--- End: def

    def __getitem__(self, indices):
        '''

x.__getitem__(indices) <==> x[indices]

Returns a numpy array.

'''
        array = numpy_load(self._partition_file)

        indices = parse_indices(array, indices)

        array = get_subspace(array, indices)

        if self._masked_as_record:
            # Convert a record array to a masked array
            array = numpy_ma_array(array['_data'], mask=array['_mask'],
                                   copy=False)
            array.shrink_mask()
        #--- End: if

        # Return the numpy array
        return array
    #--- End: def

    def __str__(self):
        '''

x.__str__() <==> str(x)

'''
        return '%s in %s' % (self.shape, self._partition_file)
    #--- End: def

    def close(self):
        '''

Close all referenced open files.

:Returns:

    None

:Examples:

>>> f.close()

'''     
        # No open files are referenced
        pass
    #--- End: def
   
#--- End: class

class CreateArray(FileArray):
    '''
**Initialization**

:Parameters:

    dtype : numpy.dtype
        The numpy data type of the data array.

    ndim : int
        Number of dimensions in the data array.

    shape : tuple
        The data array's dimension sizes.

    size : int
        Number of elements in the data array.

    fill_value : scalar, optional

'''

    def __getitem__(self, indices):
        '''

x.__getitem__(indices) <==> x[indices]

Returns a numpy array.

        '''
        array_shape = []
        for index in parse_indices(self, indices):
            if isinstance(index, slice):                
                step = index.step
                if step == 1:
                    array_shape.append(index.stop - index.start)
                elif step == -1:
                    stop = index.stop
                    if stop is None:
                        array_shape.append(index.start + 1)
                    else:
                        array_shape.append(index.start - index.stop)
                else:                    
                    stop = index.stop
                    if stop is None:
                        stop = -1
                       
                    a, b = divmod(stop - index.start, step)
                    if b:
                        a += 1
                    array_shape.append(a)
            else:
                array_shape.append(len(index))
        #-- End: for

        if self.fill_value is not None:
            return numpy_full(array_shape, fill_value=self.fill_value, dtype=self.dtype)
        else:
            return numpy_empty(array_shape, dtype=self.dtype)
    #--- End: def

    def __repr__(self):
        '''

x.__repr__() <==> repr(x)

'''
        return "<CF {0}: shape={1}, dtype={2}, fill_value={3}>".format(
            self.__class__.__name__, self.shape, self.dtype, self.fill_value)
    #--- End: def

    def __str__(self):
        '''

x.__str__() <==> str(x)

'''
        return repr(self)
    #--- End: def

    def reshape(self, newshape):
        '''
'''
        new = self.copy()        
        new.shape = newshape
        new.ndim  = len(newshape)
        return new
    #--- End: def

    def resize(self, newshape):
        '''
'''
        self.shape = newshape
        self.ndim  = len(newshape)
    #--- End: def
#--- End: class
