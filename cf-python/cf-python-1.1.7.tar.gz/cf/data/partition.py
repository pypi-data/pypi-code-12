import atexit

from numpy import array       as numpy_array
from numpy import dtype       as numpy_dtype
from numpy import expand_dims as numpy_expand_dims
from numpy import ndarray     as numpy_ndarray
from numpy import number      as numpy_number
from numpy import transpose   as numpy_transpose
from numpy import vectorize   as numpy_vectorize

from numpy.ma import expand_dims as numpy_ma_expand_dims
from numpy.ma import is_masked   as numpy_ma_is_masked
from numpy.ma import isMA        as numpy_ma_isMA
from numpy.ma import masked_all  as numpy_ma_masked_all
from numpy.ma import nomask      as numpy_ma_nomask 

from copy      import deepcopy
from sys       import getrefcount
from os        import remove
from operator  import mul
from itertools import izip
from itertools import product as itertools_product

from ..units     import Units
from ..functions import get_subspace
from ..functions import inspect as cf_inspect

from .filearray import FileArray, TempFileArray

_Units_conform = Units.conform

_dtype_object = numpy_dtype(object)

# --------------------------------------------------------------------
# Set of partitions' temporary files
#
# For example:
# >>> _temporary_files
# set(['/tmp/cf_array_B8SSw2.npy',
#      '/tmp/cf_array_iRekAW.npy'])
# --------------------------------------------------------------------
_temporary_files = set()

def _remove_temporary_files(filename=None):
    '''Remove temporary partition files from disk.

The removed files' names are deleted from the _temporary_files set.

It is intended to delete individual files as part of the garbage
collection process and to delete all files when python exits.

This is quite brutal and may break partitions if used unwisely. It is
not recommended to be used as a general tidy-up function.

:Parameters:

    filename : str, optional
        The name of file to remove. The file name must be in the
        _temporary_files set. By default all files given in the
        _temporary_files set are removed.

:Returns:

    None

:Examples:

>>> _temporary_files
set(['/tmp/cf_array_B8SSw2.npy',
     '/tmp/cf_array_G756ks.npy',
     '/tmp/cf_array_iRekAW.npy'])
>>> _remove_temporary_files('/tmp/cf_array_G756ks.npy')
>>> _temporary_files
set(['/tmp/cf_array_B8SSw2.npy',
     '/tmp/cf_array_iRekAW.npy'])
>>> _remove_temporary_files()
>>> _temporary_files
set()

    '''
    if filename is not None:
        if filename in _temporary_files:
            # Remove the given temporary file
            try:
                remove(filename)
            except OSError:
                pass
            _temporary_files.remove(filename)
        #--- End: if
        return
    #--- End: if

    # Still here? Then remove all temporary files
    for filename in _temporary_files:
        try:
            remove(filename)
        except OSError:
            pass
    #--- End: for

    _temporary_files.clear()
#--- End: def

# --------------------------------------------------------------------
# Instruction to remove all of the temporary files from all partition
# arrays at exit.
# --------------------------------------------------------------------
atexit.register(_remove_temporary_files)

# --------------------------------------------------------------------
# Create a deep copy function for numpy arrays which contain object
# types
# --------------------------------------------------------------------
_copy = numpy_vectorize(deepcopy, otypes=[object])

# ====================================================================
#
# Partition objectg
#
# ====================================================================

class Partition(object):
    '''

A partition of a master data array.

The partition spans all or part of exactly one sub-array of the master
data array

'''
    def __init__(self, subarray=None, flip=None, location=None,
                 shape=None, Units=None, part=None, axes=None):
        ''' 

**Initialization**

:Parameters:

    subarray : numpy array-like, optional
        The sub-array for the partition. Must be a numpy array or any
        array storing object with a similar interface. DO NOT UPDATE
        INPLACE.

    location : list, optional
        The location of the partition's data array in the master
        array. DO NOT UPDATE INPLACE.

    axes : list, optional
        The identities of the axes of the partition's sub-array. If
        the partition's sub-array a scalar array then it is an empty
        list. DO NOT UPDATE INPLACE.

    part : list, optional
        The part of the partition's sub-array which comprises its data
        array. If the partition's data array is to the whole sub-array
        then *part* may be an empty list. DO NOT UPDATE INPLACE.

    shape : list, optional
        The shape of the partition's data array as a subspace of the
        master array. If the master array is a scalar array then
        *shape* is an empty list. By default the shape is inferred
        from *location*. DO NOT UPDATE INPLACE.

    Units : Units, optional
        The units of the partition's sub-array. DO NOT UPDATE INPLACE.

:Examples:

>>> p = Partition(subarray   = numpy.arange(20).reshape(2,5,1),
...               location   = [(0, 6), (1, 3), (4, 5)],
...               axes       = ['dim1', 'dim0', 'dim2'],
...               part       = [],
...               Units      = cf.Units('K'))

>>> p = Partition(subarray       = numpy.arange(20).reshape(2,5,1),
...               location   = [(0, 6), (1, 3), (4, 5)],
...               axes       = ['dim1', 'dim0', 'dim2'],
...               shape      = [5, 2, 1],
...               part       = [slice(None, None, -1), [0,1,3,4], slice(None)],
...               Units      = cf.Units('K'))

>>> p = Partition(subarray   = numpy.array(4),
...               location   = [(4, 5)],
...               axes = ['dim1'],
...               part       = [],
...               Units      = cf.Units('K'))

'''
        self.axes     = axes      # DO NOT UPDATE INPLACE
        self.flip     = flip      # DO NOT UPDATE INPLACE
        self.part     = part      # DO NOT UPDATE INPLACE
        self.location = location  # DO NOT UPDATE INPLACE
        self.shape    = shape     # DO NOT UPDATE INPLACE
        self.Units    = Units     # DO NOT UPDATE INPLACE
        self.subarray = subarray  # DO NOT UPDATE INPLACE
  
        if shape is None and location is not None:
            self.shape = [i[1]-i[0] for i in location]

        self._original      = None
        self._write_to_disk = None
    #--- End: def

    def __deepcopy__(self, memo):
        '''

Used if copy.deepcopy is called on the variable.

''' 
        return self.copy()
    #--- End: def

    def __del__(self):
        '''

Called when the partition's reference count reaches zero.

If the partition contains a temporary file which is not referenced by
any other partition then the temporary file is removed from disk.

If the partition contains a non-temporary file which is not referenced
by any other partition then the file is closed.

'''     
        subarray = getattr(self, 'subarray', None)

        if getrefcount is not None:
            if subarray is None or getrefcount(subarray) > 2:
                return
        else:
            # getrefcount has itself been deleted or is in the process
            # of being torn down
            return

        _partition_file = getattr(subarray, '_partition_file', None)
        if _partition_file is not None:
            # This partition contains a temporary file which is not
            # referenced by any other partition, so remove the file
            # from disk.
            _remove_temporary_files(_partition_file)

        elif (numpy_ndarray is not None and 
              not isinstance(subarray, numpy_ndarray)):
            # This partition contains a non-temporary file which is
            # not referenced by any other partition, so close the
            # file.
            subarray.close()           
    #--- End: def

#    def __getstate__(self):
#        '''
#
#Called when pickling.
#
#:Parameters:
#
#    None
#
#:Returns:
#
#    out : dict
#        A dictionary of the instance's attributes
#
#:Examples:
#
#'''
#        return dict([(attr, getattr(self, attr))
#                     for attr in self.__slots__ if hasattr(self, attr)])
#    #--- End: def        
#
#    def __setstate__(self, odict):
#        '''
#
#Called when unpickling.
#
#:Parameters:
#
#    odict : dict
#        The output from the instance's `__getstate__` method.
#
#:Returns:
#
#    None
#
#'''
#        for attr, value in odict.iteritems():
#            setattr(self, attr, value)
#    #--- End: def

    def __str__(self):
        '''

x.__str__() <==> str(x)

'''
        return '%s: %s' % (self.__class__.__name__, self.__dict__)
    #--- End: def

    # ----------------------------------------------------------------
    # Attribute: read only
    # ----------------------------------------------------------------
    @property
    def indices(self):
        '''

The indices of the master array which correspond to this partition's
data array.

:Returns:

    out : tuple
        A tuple of slice objects or, if the master data array is a
        scalar array, an empty tuple.

:Examples:

>>> p.location
[(0, 5), (2, 9)]
>>> p.indices
(slice(0, 5), slice(2, 9))

>>> p.location
[()]
>>> p.indices
()

'''
        return tuple([slice(*r) for r in self.location])
    #--- End: def

    # ----------------------------------------------------------------
    # Attribute: read only
    # ----------------------------------------------------------------
    @property
    def in_memory(self):
        '''

True if and only if the partition's sub-array is in memory as opposed
to on disk.

:Examples:

>>> p.in_memory
False

'''
        return isinstance(self.subarray, numpy_ndarray)
    #--- End: if

    # ----------------------------------------------------------------
    # Attribute: read only
    # ----------------------------------------------------------------
    @property
    def on_disk(self):
        '''

True if and only if the partition's sub-array is on disk as opposed to
in memory.

:Examples:

>>> p.on_disk
True
>>> p.to_disk()
>>> p.on_disk
False

'''
        return not isinstance(self.subarray, numpy_ndarray) # return not self.in_memory
    #--- End: if

    # ----------------------------------------------------------------
    # Attribute: read only
    # ----------------------------------------------------------------
    @property
    def isscalar(self):
        '''

True if and only if the partition's data array is a scalar array.

:Examples:

>>> p.axes
[]
>>> p.isscalar
True

>>> p.axes
['dim2']
>>> p.isscalar
False

'''
        return not self.axes
    #--- End: def

    # ----------------------------------------------------------------
    # Attribute: read only
    # ----------------------------------------------------------------
    @property
    def size(self):
        '''

Number of elements in the partition's data array.

:Examples:

>>> p.shape
(73, 48)
>>> p.size
3504

'''
        shape = self.shape
        
        if not shape:
            return 0

        return long(reduce(mul, shape, 1))
    #--- End: def

    # ----------------------------------------------------------------
    # Attribute: read only
    # ----------------------------------------------------------------
    @property
    def subarray_in_external_file(self):
        '''

True if and only if the partition's sub-array is in an external file.

:Examples:

>>> p.subarray_in_external_file
False

'''

        return not (self.in_memory or isinstance(self.subarray, FileArray))
    #--- End: def

    def change_axis_names(self, axis_map):
        '''

Change the axis names.

The axis names are arbitrary, so mapping them to another arbitrary
collection does not change the data array values, units, nor axis
order.

:Parameters:

    axis_map : dict

:Returns:

    None

:Examples:

>>> p.axes
['dim0', 'dim1']
>>> p._change_axis_names({'dim0': 'dim2', 'dim1': 'dim0'})
>>> p.axes
['dim2', 'dim0']

>>> p.axes
['dim0', 'dim1']
>>> p._change_axis_names({'dim0': 'dim1'})
>>> p.axes
['dim1', 'dim2']

'''
        axes = self.axes

        # Partition axes
        self.axes = [axis_map[axis] for axis in axes]
        
        # Flipped axes
        flip = self.flip
        if flip:
            self.flip = [axis_map[axis] for axis in flip]
        #--- End: if             
    #--- End: def

    def close(self, keep_in_memory=True):
        '''

Close the partition after it has been conformed.

The partition should usually be closed after its `dataarray` method
has been called to prevent memory leaks.

Closing the partition does one of the following, depending on the
values of the partition's `!_original` attribute and on the
*keep_in_memory* argument:

* Nothing.

* Stores the partition's data array in a temporary file.

* Reverts the entire partition to a previous state.

:Parameters:

    keep_in_memory : bool, optional
        If False and the partition is not to be reverted to a previous
        state then force its data array to be stored in a temporary
        file.

:Returns:

    None

:Examples:

>>> p.dataarray(...)
>>> p.close()

'''
        if self._original:
            # The whole partition is to replaced with its
            # pre-conformed state
            self.is_partition(self._original)

        elif not keep_in_memory or self._write_to_disk:
            # The partition's data array is to be saved to a temporary
            # file
            self.to_disk()
            self._write_to_disk = None
            if hasattr(self, 'masked'):
                del self.masked
    #--- End: def

    def copy(self):
        '''

Return a deep copy.

``p.copy()`` is equivalent to ``copy.deepcopy(p)``.

:Returns:

    out :
        A deep copy.

:Examples:

>>> q = p.copy()

'''
        new = Partition.__new__(Partition)
        new.__dict__ = self.__dict__.copy()

        return new
    #--- End: def

    def dataarray(self, axes=None, flip=None, units=None,
                  revert_to_file=False, hardmask=True, dtype=None,
                  readonly=False, copy_regardless=False,
                  func=None, update=True, keep_in_memory=True):
        '''

Returns the partition's data array.

    
After a partition has been conformed, the partition must be closed
(with the `close` method) before another partition is conformed,
otherwise a memory leak could occur. For example:

>>> for partition in partition_array.flat:
...
...    # Conform the partition
...    partition.dataarray(**pda_args)
...
...    # [ Some code to operate on the conformed partition ]
...
...    # Close the partition
...    partition.close()
...
...    # Now move on to conform the next partition 
...
>>>  

:Parameters:

    axes : list

    flip : list

    units : Units

    keep_in_memory : bool, optional
        If True then the sub-array will be kept in memory as a numpy
        array when the `close` method is called.

        If False then sub-array will be replaced by a file pointer
        when the `close` method is called. This will either be a
        pointer to an existing file (see *revert_to_file*) or a new
        file will be created.

    revert_to_file : bool, optional
        If True and the sub-array was on disk and *keep_in_memory* is
        False then the file pointer will be reinstated when partition
        the is closed with th `close` method.

    dtype : numpy.dtype, optional
        Convert the partition's data array to this data type. By
        default no conversion occurs.

    hardmask : bool, optional
        If False then force the partition's data array's mask to be
        soft. By default the mask is forced to be hard.
    
:Returns: 

    out : numpy array
        The partition's data array as a numpy array.

:Raises:

   ValueError :
       A ValueError is raised if the data type conversion specified
       with the *dtype* parameter is not possible (as would be the
       case when attempting to convert a string to a float, for
       example).

'''
        unique = getrefcount(self.subarray) <= 2
        
        p_axes   = self.axes
        p_flip   = self.flip
        p_part   = self.part
        p_units  = self.Units
        p_shape  = self.shape
        subarray = self.subarray

        len_p_axes = len(p_axes)

        if self.on_disk:
            # --------------------------------------------------------
            # The sub-array is in a file on disk
            # --------------------------------------------------------
            if keep_in_memory:
                # Upon closure, keep the data array in memory
                _partition_file = getattr(subarray, '_partition_file', None)
            elif revert_to_file:
                # Upon closure, revert the partition back to its
                # original state.
                self._original = self.copy()
                _partition_file = None
            else:
                # Upon closure, write the data array to a new file
                # on disk.
                self._write_to_disk = True
                _partition_file = None

            if not p_part:
                indices = Ellipsis
            else:
                indices = tuple(p_part)
            #--- End: if

            # Read from a file into a numpy array
            p_data = subarray[indices]

            if _partition_file and unique:
                # This partition contains a temporary file which is
                # not referenced by any other partition, so we can
                # remove the file from disk.
                _remove_temporary_files(_partition_file)
            #--- End: if
                
            update = True
            unique = True
            copy   = False
        else:
            # --------------------------------------------------------
            # The sub-array is a numpy array in memory
            # --------------------------------------------------------
            if not keep_in_memory:
                # Upon closure, write the data array to a new file on
                # disk.
                self._write_to_disk = True

            if copy_regardless:
                copy = True
            else:
                copy = not unique

            p_data = subarray

            if p_part:
                p_data = get_subspace(p_data, p_part)
            elif not unique:
                p_data = subarray.view()
        #--- End: if

        if not p_data.ndim and isinstance(p_data, numpy_number):
            # p_data is a numby number (like numpy.int64) which does
            # not support assignment, so convert to a numpy array.
            p_data = numpy_array(p_data)

        masked = numpy_ma_isMA(p_data)
        if masked:
            # --------------------------------------------------------
            # The array is a masked array
            # --------------------------------------------------------
            if p_data.mask is numpy_ma_nomask or not numpy_ma_is_masked(p_data):
                # There are no missing data points so recast as a
                # normal numpy array
                p_data = p_data.data
                masked = False
            else:
                # Set the hardness of the mask
                if hardmask:
                    p_data.harden_mask()
                else:
                    p_data.soften_mask()
        #--- End: if
        self.masked = masked

        # ------------------------------------------------------------
        # Make sure that the data array has the correct units. This
        # process will deep copy the data array if required (e.g. if
        # another partition is referencing this numpy array), even if
        # the units are already correct.
        # ------------------------------------------------------------
        if func is None:
            if not p_units.equals(units) and bool(p_units) is bool(units):
                func = _Units_conform
                if (not unique or not update or
                    not p_data.flags['C_CONTIGUOUS'] or p_data.dtype.kind == 'i'):
                    inplace = False
                else:
                    inplace = True
        else:
             inplace = update and unique
        #--- End: if

        if func is not None:
            p_data  = func(p_data, p_units, units, inplace)
            p_units = units
            copy = False
        #--- End: if

        if p_data.size > 1:
            if flip or p_flip:
                # ----------------------------------------------------
                # Flip axes
                # ----------------------------------------------------
                flip_axes = set(p_flip).symmetric_difference(flip)
                if flip_axes:
                    indices = [(slice(None, None, -1) if axis in flip_axes
                                else slice(None))
                               for axis in p_axes]
                    p_data = p_data[tuple(indices)]
            #--- End: if

            if p_axes != axes:
                # ----------------------------------------------------
                # Reorder axes
                # ----------------------------------------------------
                iaxes = [p_axes.index(axis) for axis in axes if axis in p_axes]
                       
                if len_p_axes > len(iaxes):
                    for i in xrange(len_p_axes):
                        if i not in iaxes:
                            iaxes.append(i)
                #--- End: if
            
                p_data = numpy_transpose(p_data, iaxes)
        #--- End: if

        # ------------------------------------------------------------
        # Remove excessive/insert missing size 1 axes
        # ------------------------------------------------------------
        if len_p_axes != len(p_shape):
            p_data = p_data.reshape(p_shape)

        # ------------------------------------------------------------
        # Convert the array's data type
        # ------------------------------------------------------------
        if dtype is not None and dtype != p_data.dtype:
            try:
                p_data = p_data.astype(dtype) # Copy ought to work!
            except ValueError:
                raise ValueError("Can't recast data array from %s to %s" % 
                                 (p_data.dtype.name, dtype.name))
            else:
                copy = False
        #--- End: if

        # ------------------------------------------------------------
        # Copy the array
        # ------------------------------------------------------------
        if copy:
            if p_data.dtype.char != 'O':
                if not masked or p_data.ndim > 0:
                    p_data = p_data.copy()
                else:
                    # This is because numpy.ma.copy doesn't work for
                    # scalar arrays (<=1.8)
                    p_data = numpy_ma_masked_all((), p_data.dtype)
            else:
                # whilst netCDF4.netcdftime.datetime is mucking bout, don't copy!!!!
                #p_data = _copy(p_data)
                pass
        #--- End: if

        # ------------------------------------------------------------
        # Update the partition
        # ------------------------------------------------------------
        if update:
            self.subarray = p_data
            self.Units    = p_units
            self.part     = []
            self.axes     = axes
            self.flip     = flip
        #--- End: if

        # ------------------------------------------------------------
        # Return the numpy array
        # ------------------------------------------------------------
        return p_data
    #--- End: def

    @property
    def isdt(self):
        '''

True if the subarray contains date-time objects.

:Examples:

>>> p.Units.isreftime
True
>>> p.subarray.dtype == numpy.dtype(object)
True
>>> p.isdt
True

'''
        if self.Units.isreftime and self.subarray.dtype == _dtype_object:
            return True
        else:
            return False
    #--- End: def

    def file_close(self):
        '''

Close all file containing the sub-array, if there is one.

:Returns:

    None

:Examples:

>>> p.file_close()

'''
        if self.on_disk:
            self.subarray.close()
    #--- End: def

#    def flat(self):
#        '''
#
#Return an iterator that yields the partition itself.
#
#This is provided as a convienience to make it easier to iterate
#through a partition matrix.
#
#:Returns:
#
#    out : generator
#        An iterator that yields the partition itself.
#
#:Examples:
#
#>>> type(p.flat())
#<generator object flat at 0x519a0a0>
#>>> for q in p.flat():
#...     print q is p
#True
#
#'''
#        yield self
#    #--- End: def
#
#    def ndindex(self):
#        '''
#
#Return an iterator over the N-dimensional indices of the partition's
#data array.
# 
#At each iteration a tuple of indices is returned, the last dimension
#is iterated over first.
#
#:Returns:
#
#    out : generator
#        An iterator over indices of the partition's data array.
#
#:Examples:
#
#>>> p.shape
#[2, 1, 3]
#>>> for index in p.ndindex():
#...     print index
#...
#(0, 0, 0)
#(0, 0, 1)
#(0, 0, 2)
#(1, 0, 0)
#(1, 0, 1)
#(1, 0, 2)
#
#>>> p.shape
#[]
#>>> for index in p.ndindex():
#...     print index
#...
#()
#
#'''
#        return itertools_product(*[xrange(0, r) for r in self.shape])
#    #--- End: def

    def inspect(self):
        '''

Inspect the object for debugging.

.. seealso:: `cf.inspect`

:Returns: 

    None

:Examples:

>>> f.inspect()

'''
        print cf_inspect(self)
    #--- End: def

    def master_ndindex(self): #itermaster_indices(self):
        '''

Return an iterator over indices of the master array which are spanned
by the data array.

:Returns:

    out : generator
        An iterator over indices of the master array which are spanned
        by the data array.

:Examples:

>>> p.location
[(3, 5), (0, 1), (0, 3)]
>>> for index in p.master_ndindex():
...     print index
...
(3, 0, 0)
(3, 0, 1)
(3, 0, 2)
(4, 0, 0)
(4, 0, 1)
(4, 0, 2)

'''
        return itertools_product(*[xrange(*r) for r in self.location])
    #--- End: def

    def new_part(self, indices, master_axis_to_position, master_flip):
        '''

Update the `!part` attribute in-place for new indices of the master
array.

:Parameters:

    indices : list

    master_axis_to_position : dict

    master_flip : list

:Returns:

    None

:Examples:

>>> p.new_part(indices, dim2position, master_flip)

''' 
        shape = self.shape

        if indices == [slice(0, stop, 1) for stop in shape]:
            return
        
        # ------------------------------------------------------------
        # If a dimension runs in the wrong direction then change its
        # index to account for this.
        #
        # For example, if a dimension with the wrong direction has
        # size 10 and its index is slice(3,8,2) then after the
        # direction is set correctly, the index needs to changed to
        # slice(6,0,-2):
        #
        # >>> a = [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
        # >>> a[slice(3, 8, 2)]          
        # [6, 4, 2]
        # >>> a.reverse()
        # >>> print a
        # >>> a = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        # >>> a[slice(6, 0, -2)]    
        # [6, 4, 2]
        # ------------------------------------------------------------

        if self.subarray.size > 1:
            indices = indices[:]

            p_flip = self.flip
  
            for axis, i in master_axis_to_position.iteritems():
                      
                if ((axis not in p_flip and axis not in master_flip) or 
                    (axis in p_flip     and axis in master_flip)):
                    # This axis runs in the correct direction
                    continue

                # Still here? Then this axis runs in the wrong
                # direction.

                # Reset the direction
                p_flip = p_flip[:]
                if axis in self.flip:
                    p_flip.remove(axis)
                else:
                    p_flip.append(axis)
                    
                # Modify the index to account for the changed
                # direction
                size = shape[i]

                if isinstance(indices[i], slice):
                    start, stop, step = indices[i].indices(size)
                    # Note that step is assumed to be always +ve here
                    div, mod = divmod(stop-start-1, step)
                    start = size - 1 - start
                    stop  = start - div*step - 1
                    if stop < 0:
                        stop = None
                    indices[i] = slice(start, stop, -step)
                else:
                    size -= 1
                    indices[i] = [size-j for j in indices[i]]
            #--- End: for

            self.flip = p_flip
        #--- End: if

        slice_None = slice(None)

        # Reorder the new indices
        indices = [(indices[master_axis_to_position[axis]] 
                    if axis in master_axis_to_position else
                    slice_None)
                   for axis in self.axes]

        part = self.part

        if not part:
            self.part = indices
            return

        # Still here? update an existing part
        p_part = []
        for part_index, index, size in izip(part,
                                            indices, 
                                            self.subarray.shape):

            if index == slice_None:
                p_part.append(part_index)
                continue

            if isinstance(part_index, slice):
                if isinstance(index, slice):

                    start , stop , step  = part_index.indices(size)

                    size1, mod = divmod(stop-start-1, step)            

                    start1, stop1, step1 = index.indices(size1+1)

                    size2, mod = divmod(stop1-start1, step1)

                    if mod != 0:
                        size2 += 1
                
                    start += start1 * step
                    step  *= step1
                    stop   = start + (size2-1)*step

                    if step > 0:
                        stop += 1
                    else:
                        stop -= 1
                    if stop < 0:
                        stop = None
                    p_part.append(slice(start, stop, step))

                    continue
                else:
                    new_part = range(*part_index.indices(size))
                    new_part = [new_part[i] for i in index]
            else:
                if isinstance(index, slice):
                    new_part = part_index[index]
                else:
                    new_part = [part_index[i] for i in index]
            #--- End: if
    
            # Still here? Then the new element of p_part is a list of
            # integers, so let's see if we can convert it to a slice
            # before appending it.
            new_part0 = new_part[0]
            if len(new_part) == 1:
                # Convert a single element list to a slice object
                new_part = slice(new_part0, new_part0+1, 1)
            else:                
                step = new_part[1] - new_part0
                if step:
                    if step > 0:
                        start, stop = new_part0, new_part[-1]+1
                    else:
                        start, stop = new_part0, new_part[-1]-1
                        if new_part == range(start, stop, step):
                            if stop < 0:
                                stop = None
                            new_part = slice(start, stop, step)
            #--- End: if

            p_part.append(new_part)
        #--- End: for
    
        self.part = p_part
    #--- End: def

    def overlaps(self, indices):
        '''
    
Return True if the sub-array overlaps a subspace of the master array.

:Parameters:

   indices : sequence
       Indices describing a subset of the master array. Each index is
       either a slice object or a list. If the sequence is empty then
       it is assumed that the master array is a scalar array.

:Returns:

    p_indices, shape : list, list or None, None
        If the partition overlaps the *indices* then return a list of
        indices which will subset the partition's data to where it
        overlaps the master indices and the subsetted partition's
        shape as a list. Otherwise return `None, None`.

:Examples:

>>> indices = (slice(None), slice(5, 1, -2), [1, 3, 4, 8])
>>> p.overlaps(indices)
(slice(), ddfsfsd), [3, 5, 4]

'''
        p_indices = []
        shape     = []
        
        if not indices:
            return p_indices, shape

        for index, (r0, r1), size in izip(indices, self.location, self.shape):
            if isinstance(index, slice):
                stop = size
                if index.stop < r1:
                    stop -= (r1 - index.stop)
                  
                start = index.start - r0
                if start < 0:
                    start %= index.step   # start is now +ve
                
                if start >= stop:
                    # This partition does not span the slice
                    return None, None
                    
                # Still here?
                step = index.step
                index = slice(start, stop, step)
                index_size, rem = divmod(stop-start, step)
                if rem:
                    index_size += 1

            else:
                
                # Still here?
                index = [i - r0 for i in index if r0 <= i < r1]
                index_size = len(index)
                if index_size == 0:
                    return None, None
                elif index_size == 1:
                    index = slice(index[0], index[0]+1)
                else:
                    index0 = index[0]
                    step = index[1] - index0
                    if step > 0:
                        start, stop = index0, index[-1]+1
                    elif step < 0:
                        start, stop = index0, index[-1]-1
                    if index == range(start, stop, step):
                        # Replace the list with a slice object
                        if stop < 0:
                            stop = None
                        index = slice(start, stop, step)
                #--- End: if
            #--- End: if

            p_indices.append(index)
            shape.append(index_size)
        #--- End: for
            
        # Still here? Then this partition does span the slice and the
        # elements of this partition specified by p_indices are in the
        # slice.
        return p_indices, shape
    #--- End: def

    def to_disk(self):
        '''

Store the partition's sub-array in a temporary file on disk in place.

Assumes that the partition's sub-array is currently in memory, but
this is not checked.

:Returns:

    None

:Examples:

>>> p.to_disk()

'''
        self.subarray = TempFileArray(self.subarray)  

        _temporary_files.add(self.subarray._partition_file)
    #--- End: if

    def is_partition(self, other):
        '''

Completely update the partition with another partition's attributes in
place.

The updated partitionasdasdasdasdasds is always dependent of the other partition.

:Parameters:

    other : Partition

:Returns:

    None

:Examples:

>>> p.is_partition(q)

'''
        self.__dict__ = other.__dict__
    #--- End: def

    def update_inplace_from(self, other):
        '''

Completely update the partition with another partition's attributes in
place.

:Parameters:

    other : Partition

:Returns:

    None

:Examples:

>>> p.update_inplace_from(q)

'''
        self.__dict__ = other.__dict__.copy()
    #--- End: def

#--- End: class
