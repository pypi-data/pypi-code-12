from numpy import argmax      as numpy_argmax
from numpy import array       as numpy_array
from numpy import can_cast    as numpy_can_cast
from numpy import diff        as numpy_diff
from numpy import empty       as numpy_empty
from numpy import ndarray     as numpy_ndarray
from numpy import size        as numpy_size
from numpy import squeeze     as numpy_squeeze
from numpy import unique      as numpy_unique
from numpy import where       as numpy_where
from numpy import zeros       as numpy_zeros
from numpy import array_equal as numpy_array_equal
from numpy import arange      as numpy_arange
from numpy import tile        as numpy_tile
from numpy.ma import MaskedArray as numpy_MaskedArray
from numpy.ma import is_masked as numpy_is_masked

from copy            import deepcopy
from itertools       import izip
from operator        import mul as operator_mul
from operator        import itemgetter as operator_itemgetter
from matplotlib.path import Path
#from scipy.ndimage.filters import convolve1d 

from .cellmeasure  import CellMeasure
from .cellmethods  import CellMethods
from .constants    import masked as cf_masked
from .domain       import Domain
from .flags        import Flags
from .functions    import parse_indices, CHUNKSIZE, equals, RTOL, ATOL
from .functions    import _section
from .query        import Query, ge, gt, le, lt, ne, eq, wi
from .timeduration import TimeDuration
from .units        import Units
from .variable     import Variable, SubspaceVariable, RewriteDocstringMeta

from .data.data import Data
from .regrid import Regrid
from .coordinate import DimensionCoordinate

# --------------------------------------------------------------------
# Commonly used units
# --------------------------------------------------------------------
_units_days    = Units('days')
_units_radians = Units('radians')
_units_m       = Units('m')
_units_m2      = Units('m2')

_1_day = Data(1, 'day')

# --------------------------------------------------------------------
# Map each allowed input collapse method name to its corresponding
# cf.Data method. Input collapse methods not in this sictionary are
# assumed to have a corresponding cf.Data method with the same name.
# --------------------------------------------------------------------
_collapse_methods = {
    'mean'              : 'mean',
    'avg'               : 'mean',
    'average'           : 'mean',
    'max'               : 'max',
    'maximum'           : 'max',
    'min'               : 'min',
    'minimum'           : 'min',
    'mid_range'         : 'mid_range',
    'range'             : 'range',
    'standard_deviation': 'sd',
    'sd'                : 'sd',
    'sum'               : 'sum',
    'variance'          : 'var',
    'var'               : 'var',
    'sample_size'       : 'sample_size', 
    'sum_of_weights'    : 'sum_of_weights',
    'sum_of_weights2'   : 'sum_of_weights2',
}

# --------------------------------------------------------------------
# Map each allowed input collapse method name to its corresponding
# cf.Data method. Input collapse methods not in this sictionary are
# assumed to have a corresponding cf.Data method with the same name.
# --------------------------------------------------------------------
_collapse_cell_methods = {
    'point'             : 'point',
    'mean'              : 'mean',
    'avg'               : 'mean',
    'average'           : 'mean',
    'max'               : 'maximum',
    'maximum'           : 'maximum',
    'min'               : 'minimum',
    'minimum'           : 'minimum',
    'mid_range'         : 'mid_range',
    'range'             : 'range',
    'standard_deviation': 'standard_deviationd',
    'sd'                : 'standard_deviation',
    'sum'               : 'sum',
    'variance'          : 'variance',
    'var'               : 'variance',
    'sample_size'       : None,
    'sum_of_weights'    : None,
    'sum_of_weights2'   : None,
}

# --------------------------------------------------------------------
# Map each cf.Data method to its corresponding minimum number of
# elements. cf.Data methods not in this dictionary are assumed to have
# a minimum number of elements equal to 1.
# --------------------------------------------------------------------
_collapse_min_size = {'sd' : 2,
                      'var': 2,
                      }

# --------------------------------------------------------------------
# These cf.Data methods may be weighted
# --------------------------------------------------------------------
_collapse_weighted_methods = set(('mean',
                                  'avg',
                                  'average',
                                  'sd',
                                  'standard_deviation',
                                  'var',
                                  'variance',
                                  'sum_of_weights',
                                  'sum_of_weights2',
                                  ))

# --------------------------------------------------------------------
# These cf.Data methods may specify a number of degrees of freedom
# --------------------------------------------------------------------
_collapse_ddof_methods = set(('sd',
                              'var',
                              ))

# ====================================================================
#
# Field object
#
# ====================================================================

class Field(Variable):
    '''

A field construct according to the CF data model.

A field is a container for a data array and metadata comprising
properties to describe the physical nature of the data and a
coordinate system (called a domain) which describes the positions of
each element of the data array.

The field's domain may contain dimensions and auxiliary coordinate and
cell measure objects (which themselves contain data arrays and
properties to describe them) and coordinate reference objects.

All components of a field are optional.

**Miscellaneous**

Field objects are picklable.

'''

    _special_properties = Variable._special_properties.union(        
        ('ancillary_variables',
         'cell_methods',
         'flag_values',
         'flag_masks',
         'flag_meanings')
         )
    
    def __init__(self, properties={}, attributes={}, data=None, domain=None,
                 flags=None, ancillary_variables=None, axes=None,
                 auto_cyclic=True, copy=True):
        '''**Initialization**

:Parameters:

    properties : dict, optional
        Provide the new field with CF properties from the dictionary's
        key/value pairs.

    data : cf.Data, optional
        Provide the new field with an N-dimensional data array in a
        `cf.Data` object.

    domain : cf.Domain, optional
        Provide the new field with a coordinate system in a
        `cf.Domain` object. By default an empty domain is created.

    attributes : dict, optional
        Provide the new field with attributes from the dictionary's
        key/value pairs.

    flags : cf.Flags, optional
        Provide the new field with self-describing flag values.

    ancillary_variables : cf.FieldList, optional
        Provide the new field with ancillary variable fields.

    axes : sequence of str, optional
        A list of domain axis identifiers (``'dimN'``), stating the
        axes, in order, of field's data array. By default these axis
        identifiers will be the sequence of consecutive axis
        identifiers ``'dim0'`` up to ``'dimM'``, where ``M`` is the
        number of axes of the data array, or an empty sequence if the
        data array is a scalar.

        If an axis of the data array already exists in the domain then
        the it must have the same size as the domain axis. If it does
        not exist in the domain then a new axis will be created.

        By default the axes will either be those defined for the data
        array by the domain or, if these do not exist, the domain axis
        identifiers whose sizes unambiguously match the data array.

    auto_cyclic : bool, optional
        If False then do not auto-detect cyclic axes. By default
        cyclic axes are auto-detected with the `autocyclic` method.

    copy : bool, optional
        If False then do not deep copy arguments prior to
        initialization. By default arguments are deep copied.

        '''
        # Initialize the new field with attributes and CF properties
        super(Field, self).__init__(properties=properties,
                                    attributes=attributes,
                                    copy=copy)   
    
        # Domain
        if domain is not None:
            if not copy:
                self.domain = domain
            else:
                self.domain = domain.copy()
        else:
            # A field always has a domain
            self.domain = Domain()

        # Data array
        if data is not None:
            self.insert_data(data, axes=axes, copy=copy)
           
        # Flags
        if flags is not None:
            if not copy:
                self.Flags = flags
            else:
                self.Flags = flags.copy()
        #--- End: if

        # Ancillary variables
        if ancillary_variables is not None:
            if not copy:
                self.ancillary_variables = ancillary_variables
            else:
                self.ancillary_variables = ancillary_variables.copy()
        #--- End: if

        # Cyclic axes
        if auto_cyclic:
            self.autocyclic()
    #--- End: def

    def __getitem__(self, index):
        '''

Called to implement evaluation of f[index].

f.__getitem__(index) <==> f[index]

The field is treated as if it were a single element field list
containing itself, i.e. ``f[index]`` is equivalent to
``cf.FieldList(f)[index]``.

:Examples 1:

>>> g = f[0]
>>> g = f[:1]
>>> g = f[1:]

:Returns:

    out : cf.Field or cf.FieldList
        If *index* is the integer 0 or -1 then the field itself is
        returned. If *index* is a slice then a field list is returned
        which is either empty or else contains a single element of the
        field itself.
          
.. seealso:: `cf.FieldList.__getitem__`, `subspace`

:Examples 2:

>>> f[0] is f[-1] is f
True
>>> f[0:1].equals(cf.FieldList(f))   
True
>>> f[0:1][0] is f
True
>>> f[1:].equals(cf.FieldList())
True
>>> f[1:]       
[]
>>> f[-1::3][0] is f
True

'''
#        if isinstance(index, slice):
#            n = len((None,)[index])
#            if n == 1:
#                return FieldList(self)
#            elif not n:
#                return FieldList()
#            else:
#                raise IndexError("%s index out of range: %s" %
#                                 (self.__class__.__name__, index))
#        #--- End: if
#
#        return super(Field, self).__getitem__(index)

        return FieldList((self,))[index]
    #--- End: def

    def broadcastable(self, g):
        '''
'''
        # ------------------------------------------------------------
        # Analyse each domain
        # ------------------------------------------------------------
        s = self.domain.analyse()
        v = g.domain.analyse()

        if s['warnings'] or v['warnings']:
            return False

        matching_size_gt1_ids = []
        for x, coord0 in s['id_to_coord']:
            size0 = coord0.size
            if size0 == 1:
                continue
            
            if x in v['id_to_coord']:
                coord1 = v['id_to_coord']['x']
                size1 = coord1.size
                if size1 == 1:
                    continue
                if size0 != size1:
                    return False

                matching_size_gt1_ids.append(x)
        #--- End: for                    

        for x, coord1 in v['id_to_coord']:
            if x in matching_size_gt1_ids:
                continue
            
            size1 = coord1.size
            if size1 == 1:
                continue
            
            if x in s['id_to_coord']:
                coord0 = s['id_to_coord']['x']
                size0 = coord0.size
                if size0 == 1:
                    continue
                if size0 != size1:
                    return False

                matching_size_gt1_ids.append(x)
        #--- End: for                    

        # Check that at most one field has undefined axes
        if s['undefined_axes'] and v['undefined_axes']:
            raise ValueError(
"Can't combine fields: Both fields have undefined axes")

        # Find the axis names which are present in both fields
        matching_ids = set(s['id_to_axis']).intersection(v['id_to_axis'])
        
        # Check that any matching axes defined by an auxiliary
        # coordinate are done so in both fields.
        for identity in set(s['id_to_aux']).symmetric_difference(v['id_to_aux']):
            if identity in matching_ids:
                raise ValueError(
"Can't combine fields: %r axis defined by auxiliary in only 1 field" %
standard_name) ########~WRONG
        #--- End: for


        #-------------------------------------------------------------
        #
        #-------------------------------------------------------------
        for identity in matching_size_gt1_ids:
            coord0 = s['id_to_coord'][identity]
            coord1 = v['id_to_coord'][identity]

            # Check that the defining coordinate data arrays are
            # compatible
            if not coord0._equivalent_data(coord1):
                # Can't broadcast: The defining coordinates have
                # unequivalent data arrays and are both size > 1.
                return False

            # Still here? Then the defining coordinates have
            # equivalent data arrays

            # If the defining coordinates are attached to
            # coordinate references then check that those coordinate references are
            # equivalent
            key0 = s['id_to_key'][identity]                
            key1 = v['id_to_key'][identity]

            equivalent_refs = True
            for ref0 in self.refs().itervalues():
                if key0 not in ref0.coords:
                    continue

                equivalent_refs = False
                for ref1 in g.refs().itervalues():
                    if key1 not in ref1.coords:
                        continue

                    # Each defining coordinate is referenced by a
                    # coordinate reference ...
                    if self.domain.equivalent_refs(ref0,
                                                        ref1,
                                                        g.domain):
                        # ... and those coordinate references are equivalent
                        equivalent_refs = True
                    #--- End: if

                    break
                #--- End: for

                break
            #--- End: for

            if not equivalent_refs:
                # Can't broadcast: Defining coordinates have
                # incompatible coordinate references are and are both size >
                # 1.
                return False
        #--- End: for

        # --------------------------------------------------------
        # Still here? Then the two fields are broadcastable!
        # --------------------------------------------------------
        return True
    #--- End: def

    def _binary_operation(self, other, method):
        '''

Implement binary arithmetic and comparison operations on the master
data array with metadata-aware broadcasting.

It is intended to be called by the binary arithmetic and comparison
methods, such as `__sub__`, `__imul__`, `__rdiv__`, `__lt__`, etc.

:Parameters:

    other : standard Python scalar object, cf.Field or cf.Query or cf.Data

    method : str
        The binary arithmetic or comparison method name (such as
        ``'__idiv__'`` or ``'__ge__'``).

:Returns:

    out : cf.Field
        The new field, or the same field if the operation was an in
        place augmented arithmetic assignment.

:Examples:

>>> h = f._binary_operation(g, '__add__')
>>> h = f._binary_operation(g, '__ge__')
>>> f._binary_operation(g, '__isub__')
>>> f._binary_operation(g, '__rdiv__')

'''
        debug = False

        if (isinstance(other, (float, int, long, bool, basestring)) or
            other is self):
            # ========================================================
            # CASE 1a: No changes are to the field's domain are
            #          required so can use the metadata-unaware
            #          Variable._binary_operation method.
            # ========================================================
            return super(Field, self)._binary_operation(other, method)
        #--- End: if

        if isinstance(other, Data) and other.size == 1:
            # ========================================================
            # CASE 1b: No changes are to the field's domain are
            #          required so can use the metadata-unaware
            #          Variable._binary_operation method.
            # ========================================================
            if other.ndim > 0:
                other = other.squeeze()

            return super(Field, self)._binary_operation(other, method)
        #--- End: if

        if isinstance(other, Query):
            # ========================================================
            # CASE 2: Combine the field with a cf.Query object
            # ========================================================
            return NotImplemented
        #--- End: if

        if isinstance(other, FieldList):
            # ========================================================
            # CASE 3: Combine the field with a cf.FieldList object
            # ========================================================
            return NotImplemented
        #--- End: if

        if not isinstance(other, self.__class__):
            raise ValueError(
                "Can't combine %r with %r" %
                (self.__class__.__name__, other.__class__.__name__))
        #--- End: if

        # ============================================================
        # Still here? Then combine the field with another field
        # ============================================================

        # ------------------------------------------------------------
        # Analyse each domain
        # ------------------------------------------------------------
        s = self.domain.analyse()
        v = other.domain.analyse()

        if s['warnings'] or v['warnings']:
            raise ValueError("Can't combine fields: %s" % 
                             (s['warnings'] or v['warnings']))

        # Check that at most one field has undefined axes
        if s['undefined_axes'] and v['undefined_axes']:
            raise ValueError(
"Can't combine fields: Both fields have undefined axes")

        # Find the axis names which are present in both fields
        matching_ids = set(s['id_to_axis']).intersection(v['id_to_axis'])
        if debug:
            print "s['id_to_axis'] =", s['id_to_axis']
            print "v['id_to_axis'] =", v['id_to_axis']
            print 'matching_ids    =', matching_ids
        
        # Check that any matching axes defined by an auxiliary
        # coordinate are done so in both fields.
        for identity in set(s['id_to_aux']).symmetric_difference(v['id_to_aux']):
            if identity in matching_ids:
                raise ValueError(
"Can't combine fields: %r axis defined by auxiliary in only 1 field" %
standard_name) ########~WRONG
        #--- End: for

        # ------------------------------------------------------------
        # For matching dimension coordinates check that they have
        # consistent coordinate references and that one of the following is
        # true:
        #
        # 1) They have equal size > 1 and their data arrays are
        #    equivalent
        #
        # 2) They have unequal sizes and one of them has size 1
        #
        # 3) They have equal size = 1. In this case, if the data
        #    arrays are not equivalent then the axis will be omitted
        #    from the result field's domain.
        #-------------------------------------------------------------

        # List of size 1 axes to be completely removed from the result
        # field. Such an axis's size 1 defining coordinates have
        # unequivalent data arrays.
        #
        # For example:
        # >>> remove_size1_axes
        # ['dim2']
        remove_size1_axes = []

        # List of matching axes with equivalent defining dimension
        # coordinate data arrays.
        #
        # Note that we don't need to include matching axes with
        # equivalent defining *auxiliary* coordinate data arrays.
        #
        # For example:
        # >>> 
        # [('dim2', 'dim0')]
        matching_axes_with_equivalent_data = []

        # For each field, list those of its matching axes which need
        # to be broadcast against the other field. I.e. those axes
        # which are size 1 but size > 1 in the other field.
        #
        # For example:
        # >>> s['broadcast_axes']
        # ['dim1']
        s['broadcast_axes'] = []
        v['broadcast_axes'] = []

        # Map axes in field1 to axes in field0 and vice versa
        #
        # For example:
        # >>> axis1_to_axis0
        # {'dim1': 'dim0', 'dim2': 'dim1', 'dim0': 'dim2'}
        # >>> axis0_to_axis1
        # {'dim0': 'dim1', 'dim1': 'dim2', 'dim2': 'dim0'}
        axis1_to_axis0 = {}
        axis0_to_axis1 = {}

        for identity in matching_ids:
            coord0 = s['id_to_coord'][identity]
            coord1 = v['id_to_coord'][identity]

            axis0  = s['id_to_axis'][identity]
            axis1  = v['id_to_axis'][identity]

            axis1_to_axis0[axis1] = axis0
            axis0_to_axis1[axis0] = axis1

            # Check the sizes of the defining coordinates
            size0 = coord0.size
            size1 = coord1.size
            if size0 != size1:
                # Defining coordinates have different sizes
                if size0 == 1:
                    # Can broadcast
                    s['broadcast_axes'].append(s['id_to_axis'][identity])
                elif size1 == 1:
                    # Can broadcast
                    v['broadcast_axes'].append(v['id_to_axis'][identity])
                else:
                    # Can't broadcast
                    raise ValueError(
"Can't combine fields: Can't broadcast %r axes with sizes %d and %d" %
(identity, size0, size1))

                continue
            #--- End: if
            if debug:
                print "s['broadcast_axes'] =", s['broadcast_axes']
                print "v['broadcast_axes'] =", v['broadcast_axes']

            # Still here? Then these defining coordinates have the
            # same size.

            # Check that the defining coordinate data arrays are
            # compatible
            if coord0._equivalent_data(coord1):
                # The defining coordinates have equivalent data
                # arrays

                # If the defining coordinates are attached to
                # coordinate references then check that those coordinate references are
                # equivalent
                key0 = s['id_to_key'][identity]                
                key1 = v['id_to_key'][identity]

                equivalent_refs = True
                for ref0 in self.refs().itervalues():
                    if key0 not in ref0.coords:
                        continue

                    equivalent_refs = False
                    for ref1 in other.refs().itervalues():
                        if key1 not in ref1.coords:
                            continue

                        # Each defining coordinate is referenced by a
                        # coordinate reference ...
                        if self.domain.equivalent_refs(ref0, ref1,
                                                       other.domain):
                            # ... and those coordinate references are equivalent
                            equivalent_refs = True
                        #--- End: if

                        break
                    #--- End: for

                    break
                #--- End: for

                if not equivalent_refs:
                    # The defining coordinates have incompatible
                    # coordinate references
                    if coord0.size > 1:
                        # They are both size > 1
                        raise ValueError(
"Can't combine fields: Incompatible coordinate references for %r coordinates" % identity)
                    else:
                        # They are both size 1 so flag this axis to be
                        # omitted from the result field
                        remove_size1_axes.append(axis0)

                elif identity not in s['id_to_aux']:
                    # The defining coordinates 1) are both dimension
                    # coordinates, 2) have equivalent data arrays and
                    # 3) have compatible coordinate references (if any).
                    matching_axes_with_equivalent_data.append((axis0, axis1))

            else:
                # The defining coordinates have unequivalent data
                # arrays
                if coord0.size > 1:
                    # They are both size greater than 1
                    raise ValueError(
"Can't combine fields: Incompatible %r coordinates: %r, %r" %
(identity, coord0.data, coord1.data))
                else:
                    # They are both size 1 so flag this axis to be
                    # omitted from the result field
                    remove_size1_axes.append(axis0)
        #--- End: for

        # --------------------------------------------------------
        # Still here? Then the two fields are combinable!
        # --------------------------------------------------------

        # ------------------------------------------------------------
        # 2.1 Create copies of the two fields, unless it is an in
        #     place combination, in which case we don't want to copy
        #     self)
        # ------------------------------------------------------------
        field1 = other.copy()

        inplace = method[2] == 'i'
        if not inplace:
            field0 = self.copy()
        else:
            field0 = self

        # Aliases for the field's domain and data array
        domain0 = field0.domain
        domain1 = field1.domain

        # 
        s['new_axes'] = []
            
#        for axis1 in domain1._axes_sizes:
#            if axis1 in v['axis_to_id']:
#                identity = v['axis_to_id'][axis1]
#                if identity in matching_ids:
#                    axis0 = s['id_to_axis'][identity]
#                    axis1_to_axis0[axis1] = axis0
#                    axis0_to_axis1[axis0] = axis1
#        #--- End: for

        # ------------------------------------------------------------
        # Permute the axes of the data array of field0 so that:
        #
        # * All of the matching axes are the inner (fastest varying)
        #   axes
        #
        # * All of the undefined axes are the outer (slowest varying)
        #   axes
        #
        # * All of the defined but unmatched axes are in the middle
        # ------------------------------------------------------------
        data_axes0 = domain0.data_axes()
        axes_unD = []                     # Undefined axes
        axes_unM = []                     # Defined but unmatched axes
        axes0_M  = []                     # Defined and matched axes
        for axis0 in data_axes0:
            if axis0 in axis0_to_axis1:
                # Matching axis                
                axes0_M.append(axis0)
            elif axis0 in s['undefined_axes']:
                # Undefined axis
                axes_unD.append(axis0)
            else:
                # Defined but unmatched axis
                axes_unM.append(axis0)
        #--- End: for
        if debug:
            print 'axes_unD , axes_unM , axes0_M =', axes_unD , axes_unM , axes0_M

        field0.transpose(axes_unD + axes_unM + axes0_M, i=True)

        end_of_undefined0   = len(axes_unD)
        start_of_unmatched0 = end_of_undefined0
        start_of_matched0   = start_of_unmatched0 + len(axes_unM)
        if debug: 
            print 'end_of_undefined0   =', end_of_undefined0   
            print 'start_of_unmatched0 =', start_of_unmatched0 
            print 'start_of_matched0   =', start_of_matched0  

        # ------------------------------------------------------------
        # Permute the axes of the data array of field1 so that:
        #
        # * All of the matching axes are the inner (fastest varying)
        #   axes and in corresponding positions to data0
        #
        # * All of the undefined axes are the outer (slowest varying)
        #   axes
        #
        # * All of the defined but unmatched axes are in the middle
        # ------------------------------------------------------------
        data_axes1 = domain1.data_axes()
        axes_unD = []
        axes_unM = []
        axes1_M  = [axis0_to_axis1[axis0] for axis0 in axes0_M]
        for  axis1 in data_axes1:          
            if axis1 in axes1_M:
                pass
            elif axis1 in axis1_to_axis0:
                # Matching axis
                axes_unM.append(axis1)
            elif axis1 in v['undefined_axes']:
                # Undefined axis
                axes_unD.append(axis1) 
            else:
                # Defined but unmatched axis
                axes_unM.append(axis1)
        #--- End: for
        if debug:
            print 'axes_unD , axes_unM , axes0_M =',axes_unD , axes_unM , axes0_M

        field1.transpose(axes_unD + axes_unM + axes1_M, i=True)

        start_of_unmatched1 = len(axes_unD)
        start_of_matched1   = start_of_unmatched1 + len(axes_unM)
        undefined_indices1  = slice(None, start_of_unmatched1)
        unmatched_indices1  = slice(start_of_unmatched1, start_of_matched1)
        if debug: 
            print 'start_of_unmatched1 =', start_of_unmatched1 
            print 'start_of_matched1   =', start_of_matched1   
            print 'undefined_indices1  =', undefined_indices1  
            print 'unmatched_indices1  =', unmatched_indices1  

        # ------------------------------------------------------------
        # Make sure that each pair of matching axes run in the same
        # direction 
        #
        # Note that the axis0_to_axis1 dictionary currently only maps
        # matching axes
        # ------------------------------------------------------------
        if debug:
            print '2: axis0_to_axis1 =',axis0_to_axis1

        for axis0, axis1 in axis0_to_axis1.iteritems():
             if domain1.direction(axis1) != domain0.direction(axis0):
                field1.flip(axis1, i=True)
        #--- End: for
    
        # ------------------------------------------------------------
        # 2f. Insert size 1 axes into the data array of field0 to
        #     correspond to defined but unmatched axes in field1
        #
        # For example, if   field0.Data is      1 3         T Y X
        #              and  field1.Data is          4 1 P Z   Y X
        #              then field0.Data becomes 1 3     1 1 T Y X
        # ------------------------------------------------------------
        unmatched_axes1 = data_axes1[unmatched_indices1]
        if debug: print '2: unmatched_axes1=', unmatched_axes1

        if unmatched_axes1:
            for axis1 in unmatched_axes1:
                field0.expand_dims(end_of_undefined0, i=True)
                if debug: print '2: axis1, field0.shape =', axis1, field0.shape

                axis0 = set(field0.data_axes()).difference(data_axes0).pop()

                axis1_to_axis0[axis1] = axis0
                axis0_to_axis1[axis0] = axis1
                s['new_axes'].append(axis0)

                start_of_unmatched0 += 1
                start_of_matched0   += 1 

                data_axes0 = domain0.data_axes()
            #--- End: for
        #--- End: if

        # ------------------------------------------------------------
        # Insert size 1 axes into the data array of field1 to
        # correspond to defined but unmatched axes in field0
        #
        # For example, if   field0.Data is      1 3     1 1 T Y X
        #              and  field1.Data is          4 1 P Z   Y X 
        #              then field1.Data becomes     4 1 P Z 1 Y X 
        # ------------------------------------------------------------
        unmatched_axes0 = data_axes0[start_of_unmatched0:start_of_matched0]
        if debug: print '2: unmatched_axes0 =', unmatched_axes0

        if unmatched_axes0:
            for axis0 in unmatched_axes0:
                field1.expand_dims(start_of_matched1, i=True)
                if debug: print '2: axis0, field1.shape =',axis0, field1.shape

                axis1 = set(field1.data_axes()).difference(data_axes1).pop()

                axis0_to_axis1[axis0] = axis1
                axis1_to_axis0[axis1] = axis0

                start_of_unmatched1 += 1

                data_axes1 = field1.data_axes()
            #--- End: for
         #--- End: if

        # ------------------------------------------------------------
        # Insert size 1 axes into the data array of field0 to
        # correspond to undefined axes (of any size) in field1
        #
        # For example, if   field0.Data is      1 3     1 1 T Y X
        #              and  field1.Data is          4 1 P Z 1 Y X 
        #              then field0.Data becomes 1 3 1 1 1 1 T Y X
        # ------------------------------------------------------------
        axes1 = data_axes1[undefined_indices1]
        if axes1:
            for axis1 in axes1:
                field0.expand_dims(end_of_undefined0, i=True)

                axis0 = set(field0.data_axes()).difference(data_axes0).pop()

                axis0_to_axis1[axis0] = axis1
                axis1_to_axis0[axis1] = axis0
                s['new_axes'].append(axis0)

                data_axes0 = field0.data_axes()
            #--- End: for
        #--- End: if
        if debug:
            print '2: axis0_to_axis1 =', axis0_to_axis1
            print '2: axis1_to_axis0 =', axis1_to_axis0
            print "2: s['new_axes']  =", s['new_axes']

        # ============================================================
        # 3. Combine the data objects
        #
        # Note that, by now, field0.ndim >= field1.ndim.
        # ============================================================
#dch        field0.Data = getattr(field0.Data, method)(field1.Data)
        if debug:
            print '3: repr(field0) =', repr(field0)
            print '3: repr(field1) =', repr(field1)

        field0 = super(Field, field0)._binary_operation(field1, method)

        # Must rest domain0, because we have reset field0.
        domain0 = field0.domain

        if debug:
            print '3: field0.shape =', field0.shape
            print '3: repr(field0) =', repr(field0)

        # ============================================================
        # 4. Adjust the domain of field0 to accommodate its new data
        # ============================================================
        insert_dim = {}
        insert_aux = {}
        remove_aux = []

        # ------------------------------------------------------------
        # 4a. Remove any size 1 axes which are matching axes but with
        #     different coordinate data array values
        # ------------------------------------------------------------
        field0.remove_axes(remove_size1_axes)

        # ------------------------------------------------------------
        # 4b. If broadcasting has grown any size 1 axes in domain0
        #     then replace their size 1 coordinates with the
        #     corresponding size > 1 coordinates from domain1.
        # ------------------------------------------------------------
        refs1 = field1.refs()
        refs = []

        for axis0 in s['broadcast_axes'] + s['new_axes']:        
            axis1 = axis0_to_axis1[axis0]
            size = domain1._axes_sizes[axis1]
            domain0.insert_axis(size, key=axis0, replace=True)
            if debug:
                print '4: domain1._axes_sizes =',domain1._axes_sizes
                print '4: domain0._axes_sizes =',domain0._axes_sizes

            for tkey in refs1:
                if axis1 in domain1.ref_axes(tkey):
                    refs.append(tkey)

            # Copy the domain1 dimension coordinate to
            # domain0, if it exists.
            if axis1 in domain1.d:
                insert_dim[axis1] = axis0

            # Remove any domain0 1-d auxiliary coordinates for
            # this axis
            if axis0 in s['aux_coords']:
                for aux0 in s['aux_coords'][axis0]['1-d'].keys():
                    remove_aux.append(aux0)
                    del s['aux_coords'][axis0]['1-d'][aux0]
            #--- End: if

            # Copy to domain0 any domain1 1-d auxiliary coordinates
            # for this axis
            if axis1 in v['aux_coords']:
                for aux1 in v['aux_coords'][axis1]['1-d']:
                    insert_aux[aux1] = [axis0]
        #--- End: for

        # ------------------------------------------------------------
        # Consolidate any 1-d auxiliary coordinates for matching axes
        # whose defining dimension coordinates have equivalent data
        # arrays.
        #
        # A domain0 1-d auxiliary coordinate is retained if there is a
        # corresponding domain1 1-d auxiliary with the same standard
        # name and equivalent data array.
        # ------------------------------------------------------------
        for axis0, axis1 in matching_axes_with_equivalent_data:

            for aux0, coord0 in s['aux_coords'][axis0]['1-d'].iteritems():
                if coord0.identity() is None:
                    # Remove this domain0 1-d auxiliary coordinate
                    # because it has no identity
                    remove_aux.append(aux0)
                    continue

                # Still here?
                aux0_has_equivalent_pair = False

                for aux1, coord1 in v['aux_coords'][axis1]['1-d'].items():
                    if coord1.identity() is None:
                        continue
                    
                    if coord0._equivalent_data(coord1): 
                        del v['aux_coords'][axis1]['1-d'][aux1]
                        aux0_has_equivalent_pair = True
                        break
                #--- End: for

                if not aux0_has_equivalent_pair:
                    # Remove this domain0 1-d auxiliary coordinate
                    # because it has no equivalent in domain1
                    remove_aux.append(aux0)                    
        #--- End: for

        # ------------------------------------------------------------
        # Consolidate N-d auxiliary coordinates for matching axes
        # which have the same size
        # ------------------------------------------------------------
        # Remove any N-d auxiliary coordinates which span broadcasted
        # axes
        for broadcast_axes, aux_coords, domain in izip((s['broadcast_axes'], v['broadcast_axes']),
                                                       (s['aux_coords']    , v['aux_coords']),
                                                       (domain0            , domain1)):
            for axis in broadcast_axes:
                if axis not in aux_coords:
                    continue

                for aux in aux_coords[axis]['N-d']:
                    del aux_coords['N-d'][aux]
                    if domain is domain0:
                        remove_aux.append(aux)
        #--- End: for

        # Remove any N-d auxiliary coordinates which span a mixture of
        # matching and non-matching axes
        for aux_coords, domain, axis_to_id in izip((s['aux_coords'], v['aux_coords']),
                                                   (domain0         , domain1         ),
                                                   (s['axis_to_id'] , v['axis_to_id'] )):
            for aux in aux_coords['N-d'].keys():
                # Count how many of this N-d auxiliary coordinate's
                # axes are matching axes
#                n_matching_dims = len([True for axis in domain.dimensions[aux]
#                                       if axis_to_id[axis] in matching_ids])
                n_matching_dims = len([True for axis in domain._axes[aux]
                                       if axis_to_id[axis] in matching_ids])
                
#                if 1 <= n_matching_dims < len(domain.dimensions[aux]):
                if 1 <= n_matching_dims < len(domain._axes[aux]):
                    # At least one axis is a matching axis and at
                    # least one axis isn't => so remove this domain0
                    # auxiliary coordinate
                    del aux_coords['N-d'][aux]
                    if domain is domain0:
                        remove_aux.append(aux)
            #--- End: for
        #--- End: for

        # Forget about
        for aux0 in s['aux_coords']['N-d'].keys():
             n_matching_axes = len(s['aux_coords']['N-d'][aux0])
             if not n_matching_axes:
                 del s['aux_coords']['N-d'][aux0]
        #--- End: for

        # Copy to domain0 any domain1 N-d auxiliary coordinates which
        # do not span any matching axes
        for aux1, coord1 in v['aux_coords']['N-d'].items():
             n_matching_axes = len(v['aux_coords']['N-d'][aux1])
             if not n_matching_axes:
                 axes = [axis1_to_axis0[axis1] for axis1 in domain1._axes[aux1]]
                 insert_auxs[aux1] = axes
                 del v['aux_coords']['N-d'][aux1]
        #--- End: for

        # By now, aux_coords0['N-d'] contains only those N-d auxiliary
        # coordinates which span equal sized matching axes.
 
        # Remove from domain0 any N-d auxiliary coordinates which span
        # same-size matching axes and do not have an equivalent N-d
        # auxiliary coordinate in domain1 (i.e. one which spans the
        # same axes, has the same standard name and has equivalent
        # data)
        for aux0, coord0 in s['aux_coords']['N-d'].iteritems():

            # Remove domain0 N-d auxiliary coordinate if it has no
            # standard name
            if coord0.identity() is None:
                remove_aux.append(aux0)
                continue

            # Still here?
            aux0_has_equivalent_pair = False
            for aux1, coord1 in v['aux_coords']['N-d'].items():
                if coord1.identity() is None:
                    continue

                copy = True
                axes1 = domain1.item_axes(aux1)
                transpose_axes = [axes1.index(axis0_to_axis1[axis0])
                                  for axis0 in domain1.item_axes(aux0)]
                if transpose_axes != range(coord1.ndim):
#                    coord1 = coord1.copy()
                    coord1 = coord1.transpose(transpose_axes)
                    copy = False  # necessary?

                if coord0._equivalent_data(coord1, copy=copy):
                    del v['aux_coords']['N-d'][aux1]
                    aux0_has_equivalent_pair = True
                    break
            #--- End: for

            # Remove domain0 N-d auxiliary coordinate if it has no
            # equivalent in domain1
            if not aux0_has_equivalent_pair:
                remove_aux.append(aux0)
        #--- End: for
                
        key1_to_key0 = {}

        if debug:
            print 'insert_dim =', insert_dim
            print 'insert_aux =', insert_aux

        for axis1, axis in insert_dim.iteritems():
            axis0 = domain0.insert_dim(domain1.d[axis1], key=axis)
            key1_to_key0[axis1] = axis0
            if debug:
                print 'axis0, domain1.d[axis1] =', axis0, repr(domain1.d[axis1])
                print 'domain0.items() =', domain0.items()
                print 'field0.items() =', field0.items()
        for aux1, axes in insert_aux.iteritems():
            aux0 = domain0.insert_aux(domain1.a[aux1], axes=axes)
            key1_to_key0[aux1] = aux0
            if debug:
                print 'axis0, domain1.a[axis1] =', axis0, repr(domain1.a[axis1])

        domain0.remove_items(set(remove_aux))

        # Coordinate References from domain1 -> domain0
        for tkey in set(refs):
            new_ref = other.ref[tkey].copy()
#            for key1 in ref.coords:
#                new_ref.change_coord(key1, key1_to_key0.get(key1, None))
            new_ref.change_coord_identities(key1_to_key0, i=True)
                    
            domain0.insert_ref(new_ref, copy=False)
        #--- End: for

        return field0
    #--- End: def

    def _conform_for_assignment(self, other):
        '''Conform *other* so that it is ready for metadata-unaware assignment
broadcasting across *self*.

*other* is not changed in place.

:Parameters:

    other : cf.Field
        The field to conform.

:Returns:

    out : cf.Field
        The conformed version of *other*.

:Examples:

>>> g = _conform_for_assignment(f)

        '''
        # Analyse each domain
        domain0 = self.domain
        domain1 = other.domain
        s = domain0.analyse()
        v = domain1.analyse()
    
        if s['warnings'] or v['warnings']:
            raise ValueError("Can't setitem: %s" % (s['warnings'] or v['warnings']))
    
        # Find the set of matching axes
        matching_ids = set(s['id_to_axis']).intersection(v['id_to_axis'])
        if not matching_ids:
             raise ValueError("Can't assign: No matching axes")
    
        # ------------------------------------------------------------
        # Check that any matching axes defined by auxiliary
        # coordinates are done so in both fields.
        # ------------------------------------------------------------
        for identity in matching_ids:
            if (identity in s['id_to_aux']) + (identity in v['id_to_aux']) == 1:
                raise ValueError(
"Can't assign: %r axis defined by auxiliary in only 1 field" %
identity)
        #--- End: for
    
        copied = False
    
        # ------------------------------------------------------------
        # Check that 1) all undefined axes in other have size 1 and 2)
        # that all of other's unmatched but defined axes have size 1
        # and squeeze any such axes out of its data array.
        #
        # For example, if   self.Data is        P T     Z Y   X   A
        #              and  other.Data is     1     B C   Y 1 X T
        #              then other.Data becomes            Y   X T
        # ------------------------------------------------------------
        squeeze_axes1 = []
        for axis1 in v['undefined_axes']:
            if domain1._axes_sizes[axis1] != 1:            
                raise ValueError(
                    "Can't assign: Can't broadcast size %d undefined axis" %
                    domain1._axes_sizes[axis1])

            squeeze_axes1.append(axis1)
        #--- End: for

        for identity in set(v['id_to_axis']).difference(matching_ids):
            axis1 = v['id_to_axis'][identity]
            if domain1._axes_sizes[axis1] != 1:
               raise ValueError(
                    "Can't assign: Can't broadcast size %d %r axis" %
                    (domain1._axes_sizes[axis1], identity))
            
            squeeze_axes1.append(axis1)    
        #--- End: for

        if squeeze_axes1:
            if not copied:
                other = other.copy()
                copied = True

            other.squeeze(squeeze_axes1, i=True)
        #--- End: if

        # ------------------------------------------------------------
        # Permute the axes of other.Data so that they are in the same
        # order as their matching counterparts in self.Data
        #
        # For example, if   self.Data is       P T Z Y X   A
        #              and  other.Data is            Y X T
        #              then other.Data becomes   T   Y X
        # ------------------------------------------------------------
        data_axes0 = domain0.data_axes()
        data_axes1 = domain1.data_axes()
        transpose_axes1 = []       
        for axis0 in data_axes0:
            identity = s['axis_to_id'][axis0]
            if identity in matching_ids:
                axis1 = v['id_to_axis'][identity]                
                if axis1 in data_axes1:
                    transpose_axes1.append(axis1)
        #--- End: for

        if transpose_axes1 != data_axes1: 
            if not copied:
                other = other.copy()
                copied = True

            other.transpose(transpose_axes1, i=True)
        #--- End: if

        # ------------------------------------------------------------
        # Insert size 1 axes into other.Data to match axes in
        # self.Data which other.Data doesn't have.
        #
        # For example, if   self.Data is       P T Z Y X A
        #              and  other.Data is        T   Y X
        #              then other.Data becomes 1 T 1 Y X 1
        # ------------------------------------------------------------
        expand_positions1 = []
        for i, axis0 in enumerate(data_axes0):
            identity = s['axis_to_id'][axis0]
            if identity in matching_ids:
                axis1 = v['id_to_axis'][identity]
                if axis1 not in data_axes1:
                    expand_positions1.append(i)
            else:     
                expand_positions1.append(i)
        #--- End: for

        if expand_positions1:
            if not copied:
                other = other.copy()
                copied = True

            for i in expand_positions1:
                other.expand_dims(i, i=True)
        #--- End: if

        # ----------------------------------------------------------------
        # Make sure that each pair of matching axes has the same
        # direction
        # ----------------------------------------------------------------
        flip_axes1 = []
        for identity in matching_ids:
            axis1 = v['id_to_axis'][identity]
            axis0 = s['id_to_axis'][identity]
            if domain1.direction(axis1) != domain0.direction(axis0):
                flip_axes1.append(axis1)
         #--- End: for

        if flip_axes1:
            if not copied:
                other = other.copy()
                copied = True

            other = other.flip(flip_axes1, i=True)
        #--- End: if

        return other
    #--- End: def
 
    def __repr__(self):
        '''
Called by the :py:obj:`repr` built-in function.

x.__repr__() <==> repr(x)

'''
        if self._hasData:
            domain = self.domain
            x = ['%s(%d)' % (domain.axis_name(axis),
                             domain._axes_sizes[axis])
                 for axis in domain.data_axes()]
            axis_names = '(%s)' % ', '.join(x)
        else:
            axis_names = ''
        #--- End: if
            
        # Field units
        units = getattr(self, 'units', '')
        calendar = getattr(self, 'calendar', None)
        if calendar:
            units += '%s calendar' % calendar

        return '<CF Field: %s%s %s>' % (self.name(''), axis_names, units)
    #--- End: def

    def __str__(self):
        '''

Called by the :py:obj:`str` built-in function.

x.__str__() <==> str(x)

'''
        string = ["%s field summary" % self.name('')]
        string.append(''.ljust(len(string[0]), '-'))

        # Units
        units = getattr(self, 'units', '')
        calendar = getattr(self, 'calendar', None)
        if calendar:
            units += ' %s calendar' % calendar

        domain = self.domain

        # Data
        if self._hasData:
            x = ['%s(%d)' % (domain.axis_name(axis),
                             domain._axes_sizes[axis])
                 for axis in domain.data_axes()]
            
            string.append('Data           : %s(%s) %s' % (self.name(''),
                                                          ', '.join(x), units))
        elif units:
            string.append('Data           : %s' % units)

        # Cell methods
        cell_methods = getattr(self, 'cell_methods', None)
        if cell_methods is not None:
            string.append('Cell methods   : %s' % str(cell_methods))

        # Domain
        if domain:
            string.append(str(domain))
            
        # Ancillary variables
        ancillary_variables = getattr(self, 'ancillary_variables', None)
        if ancillary_variables is not None:
            y = ['Ancillary vars : ']
            y.append('\n               : '.join(
                    [repr(a) for a in ancillary_variables]))
            string.append(''.join(y))

        string.append('')

        return '\n'.join(string)
    #--- End def

    # ----------------------------------------------------------------
    # Attribute: Flags
    # ----------------------------------------------------------------
    @property
    def Flags(self):
        '''

A `cf.Flags` object containing self-describing CF flag values.

Stores the `flag_values`, `flag_meanings` and `flag_masks` CF
properties in an internally consistent manner.

:Examples:

>>> f.Flags
<CF Flags: flag_values=[0 1 2], flag_masks=[0 2 2], flag_meanings=['low' 'medium' 'high']>

'''
        return self._get_special_attr('Flags')
    @Flags.setter
    def Flags(self, value):
        self._set_special_attr('Flags', value)
    @Flags.deleter
    def Flags(self):
        self._del_special_attr('Flags')

    # ----------------------------------------------------------------
    # Attribute: read only
    # ----------------------------------------------------------------
    @property
    def rank(self):
        '''

The number of axes in the domain.

There may be greater the number of data array dimensions.

.. seealso:: `ndim`

:Examples:

>>> print f
air_temperature field summary
-----------------------------
Data           : air_temperature(time(12), latitude(64), longitude(128)) K
Cell methods   : time: mean
Axes           : time(12) = [ 450-11-16 00:00:00, ...,  451-10-16 12:00:00] noleap
               : latitude(64) = [-87.8638000488, ..., 87.8638000488] degrees_north
               : longitude(128) = [0.0, ..., 357.1875] degrees_east
               : height(1) = [2.0] m
>>> f.rank
4
>>> f.ndim
3
>>> f.unsqueeze(i=True)
<CF Field: air_temperature(height(1), time(12), latitude(64), longitude(128)) K>
>>> f.ndim
4

'''
        return self.domain.rank
    #--- End: def

    # ----------------------------------------------------------------
    # CF property: flag_values
    # ----------------------------------------------------------------
    @property
    def flag_values(self):
        '''

The flag_values CF property.

Stored as a 1-d numpy array but may be set as any array-like object.

:Examples:

>>> f.flag_values = ['a', 'b', 'c']
>>> f.flag_values
array(['a', 'b', 'c'], dtype='|S1')
>>> f.flag_values = numpy.arange(4)
>>> f.flag_values
array([1, 2, 3, 4])
>>> del f.flag_values

>>> f.setprop('flag_values', 1)
>>> f.getprop('flag_values')
array([1])
>>> f.delprop('flag_values')

'''
        try:
            return self.Flags.flag_values
        except AttributeError:
            raise AttributeError(
                "%s doesn't have CF property 'flag_values'" %
                self.__class__.__name__)
    #--- End: def
    @flag_values.setter
    def flag_values(self, value):
        try:
            flags = self.Flags
        except AttributeError:
            self.Flags = Flags(flag_values=value)
        else:
            flags.flag_values = value
    #--- End: def
    @flag_values.deleter
    def flag_values(self):
        try:
            del self.Flags.flag_values
        except AttributeError:
            raise AttributeError(
                "Can't delete non-existent %s CF property 'flag_values'" %
                self.__class__.__name__)
        else:
            if not self.Flags:
                del self.Flags
    #--- End: def

    # ----------------------------------------------------------------
    # CF property: flag_masks
    # ----------------------------------------------------------------
    @property
    def flag_masks(self):
        '''
The flag_masks CF property.

Stored as a 1-d numpy array but may be set as array-like object.

:Examples:

>>> f.flag_masks = numpy.array([1, 2, 4], dtype='int8')
>>> f.flag_masks
array([1, 2, 4], dtype=int8)
>>> f.flag_masks = (1, 2, 4, 8)
>>> f.flag_masks
array([1, 2, 4, 8], dtype=int8)
>>> del f.flag_masks

>>> f.setprop('flag_masks', 1)
>>> f.getprop('flag_masks')
array([1])
>>> f.delprop('flag_masks')

'''
        try:
            return self.Flags.flag_masks
        except AttributeError:
            raise AttributeError(
                "%s doesn't have CF property 'flag_masks'" %
                self.__class__.__name__)
    #--- End: def
    @flag_masks.setter
    def flag_masks(self, value):
        try:
            flags = self.Flags
        except AttributeError:
            self.Flags = Flags(flag_masks=value)
        else:
            flags.flag_masks = value
    #--- End: def
    @flag_masks.deleter
    def flag_masks(self):
        try:
            del self.Flags.flag_masks
        except AttributeError:
            raise AttributeError(
                "Can't delete non-existent %s CF property 'flag_masks'" %
                self.__class__.__name__)
        else:
            if not self.Flags:
                del self.Flags
    #--- End: def

    # ----------------------------------------------------------------
    # CF property: flag_meanings
    # ----------------------------------------------------------------
    @property
    def flag_meanings(self):
        '''

The flag_meanings CF property.

Stored as a 1-d numpy string array but may be set as a space delimited
string or any array-like object.

:Examples:

>>> f.flag_meanings = 'low medium      high'
>>> f.flag_meanings
array(['low', 'medium', 'high'],
      dtype='|S6')
>>> del flag_meanings

>>> f.flag_meanings = ['left', 'right']
>>> f.flag_meanings
array(['left', 'right'],
      dtype='|S5')

>>> f.flag_meanings = 'ok'
>>> f.flag_meanings
array(['ok'],
      dtype='|S2')

>>> f.setprop('flag_meanings', numpy.array(['a', 'b'])
>>> f.getprop('flag_meanings')
array(['a', 'b'],
      dtype='|S1')
>>> f.delprop('flag_meanings')

'''
        try:
            return self.Flags.flag_meanings
        except AttributeError:
            raise AttributeError(
                "%s doesn't have CF property 'flag_meanings'" %
                self.__class__.__name__)
    #--- End: def
    @flag_meanings.setter
    def flag_meanings(self, value): 
        try:
            flags = self.Flags
        except AttributeError:
            self.Flags = Flags(flag_meanings=value)
        else:
            flags.flag_meanings = value
    #--- End: def
    @flag_meanings.deleter
    def flag_meanings(self):
        try:
            del self.Flags.flag_meanings
        except AttributeError:
            raise AttributeError(
                "Can't delete non-existent %s CF property 'flag_meanings'" %
                self.__class__.__name__)
        else:
            if not self.Flags:
                del self.Flags
    #--- End: def

    # ----------------------------------------------------------------
    # CF property: cell_methods
    # ----------------------------------------------------------------
    @property
    def cell_methods(self):
        '''

The `cf.CellMethods` object containing the CF cell methods of the data
array.

:Examples:

>>> f.cell_methods
<CF CellMethods: time: maximum (interval: 1.0 month) area: mean (area-weighted)>

'''
        return self._get_special_attr('cell_methods')
    #--- End: def
    @cell_methods.setter
    def cell_methods(self, value):
        self._set_special_attr('cell_methods', value)
    @cell_methods.deleter
    def cell_methods(self):
        self._del_special_attr('cell_methods')

    # ----------------------------------------------------------------
    # CF property: Conventions	
    # ----------------------------------------------------------------
    @property
    def Conventions(self):
        '''

The Conventions CF property.

:Examples:

>>> f.Conventions = 'CF-1.5'
>>> f.Conventions
'CF-1.5'
>>> del f.Conventions

>>> f.setprop('Conventions', 'CF-1.5')
>>> f.getprop('Conventions')
'CF-1.5'
>>> f.delprop('Conventions')

'''
        return self.getprop('Conventions')
    #--- End: def

    @Conventions.setter
    def Conventions(self, value): self.setprop('Conventions', value)
    @Conventions.deleter
    def Conventions(self):        self.delprop('Conventions')

    # ----------------------------------------------------------------
    # CF property: institution (a simple attribute)
    # ----------------------------------------------------------------
    @property
    def institution(self):
        '''

The institution CF property.

:Examples:

>>> f.institution = 'University of Reading'
>>> f.institution
'University of Reading'
>>> del f.institution

>>> f.setprop('institution', 'University of Reading')
>>> f.getprop('institution')
'University of Reading'
>>> f.delprop('institution')

'''
        return self.getprop('institution')
    #--- End: def
    @institution.setter
    def institution(self, value): self.setprop('institution', value)
    @institution.deleter
    def institution(self):        self.delprop('institution')

    # ----------------------------------------------------------------
    # CF property: references (a simple attribute)
    # ----------------------------------------------------------------
    @property
    def references(self):
        '''

The references CF property.

:Examples:

>>> f.references = 'some references'
>>> f.references
'some references'
>>> del f.references

>>> f.setprop('references', 'some references')
>>> f.getprop('references')
'some references'
>>> f.delprop('references')

'''
        return self.getprop('references')
    #--- End: def
    @references.setter
    def references(self, value): self.setprop('references', value)
    @references.deleter
    def references(self):        self.delprop('references')

    # ----------------------------------------------------------------
    # CF property: standard_error_multiplier	
    # ----------------------------------------------------------------
    @property
    def standard_error_multiplier(self):
        '''

The standard_error_multiplier CF property.

:Examples:

>>> f.standard_error_multiplier = 2.0
>>> f.standard_error_multiplier
2.0
>>> del f.standard_error_multiplier

>>> f.setprop('standard_error_multiplier', 2.0)
>>> f.getprop('standard_error_multiplier')
2.0
>>> f.delprop('standard_error_multiplier')

'''
        return self.getprop('standard_error_multiplier')
    #--- End: def

    @standard_error_multiplier.setter
    def standard_error_multiplier(self, value):
        self.setprop('standard_error_multiplier', value)
    @standard_error_multiplier.deleter
    def standard_error_multiplier(self):
        self.delprop('standard_error_multiplier')

    # ----------------------------------------------------------------
    # CF property: source	
    # ----------------------------------------------------------------
    @property
    def source(self):
        '''

The source CF property.

:Examples:

>>> f.source = 'radiosonde'
>>> f.source
'radiosonde'
>>> del f.source

>>> f.setprop('source', 'surface observation')
>>> f.getprop('source')
'surface observation'
>>> f.delprop('source')

'''
        return self.getprop('source')
    #--- End: def

    @source.setter
    def source(self, value): self.setprop('source', value)
    @source.deleter
    def source(self):        self.delprop('source')

    # ----------------------------------------------------------------
    # CF property: title	
    # ----------------------------------------------------------------
    @property
    def title(self):
        '''

The title CF property.

:Examples:

>>> f.title = 'model data'
>>> f.title
'model data'
>>> del f.title

>>> f.setprop('title', 'model data')
>>> f.getprop('title')
'model data'
>>> f.delprop('title')

'''
        return self.getprop('title')
    #--- End: def

    @title.setter
    def title(self, value): self.setprop('title', value)
    @title.deleter
    def title(self):        self.delprop('title')

    # ----------------------------------------------------------------
    # Attribute: domain
    # ----------------------------------------------------------------
    @property
    def domain(self):
        '''

The `cf.Domain` object containing the field's domain.

:Examples:

>>> print f
air_temperature field summary
-----------------------------
Data           : air_temperature(time(12), latitude(64), longitude(128)) K
Cell methods   : time: mean (interval: 1.0 month)
Axes           : height(1) = [2.0] m
               : time(12) = [ 450-11-16 00:00:00, ...,  451-10-16 12:00:00] noleap
               : latitude(64) = [-87.8638000488, ..., 87.8638000488] degrees_north
               : longitude(128) = [0.0, ..., 357.1875] degrees_east
>>> f.domain
<CF Domain: height(1), time(12), latitude(64), longitude(128)>

'''
        return self._get_special_attr('domain')
    #--- End: def
    @domain.setter
    def domain(self, value):
        self._set_special_attr('domain', value)
    @domain.deleter
    def domain(self):
        self._del_special_attr('domain')

    # ----------------------------------------------------------------
    # Attribute: subspace (read only)
    # ----------------------------------------------------------------
    @property
    def subspace(self):
        '''Return a new object which will get or set a subspace of the field.

The returned object is a `!SubspaceField` object which may be
**indexed** to select a subspace by axis index values
(``f.subspace[indices]``) or **called** to select a subspace by
metadata values (``f.subspace(*exact, **metadata_values)``).

**Subspacing by indexing**

Subspacing by indices allows a subspaced field to be defined via index
values for the axes of the field's data array.

Indices to the returned `!SubspaceField` object have an extended
Python slicing syntax, which is similar to :ref:`numpy array indexing
<numpy:arrays.indexing>`, but with three extensions:

* Size 1 axes are never removed.

  An integer index i takes the i-th element but does not reduce the
  rank of the output array by one:

* The indices for each axis work independently.

  When more than one axis's slice is a 1-d boolean sequence or 1-d
  sequence of integers, then these indices work independently along
  each axis (similar to the way vector subscripts work in Fortran),
  rather than by their elements:

* Boolean indices may be any object which exposes the numpy array
  interface.

**Subspacing by metadata values**

A subspaced field may be defined via data array values of its domain
items (dimension coordinate, auciliary coordinate and cell measured
objects) by calling the `!SubspaceField` object.

``f.subspace(*exact, **metadata_values)`` is a shorthand for
``f.subspace[f.indices(*exact, **metadata_values)]``. See
`cf.Field.indices` for details.

**Assignment to subspaces**

Elements of a field's data array may be changed by assigning values to
a subspace of the field.

Assignment is only possible to a subspace defined by indices of the
returned `!SubspaceField` object. For example, ``f.subspace[indices] =
0`` is possible, but ``f.subspace(*exact, **metadata_values) = 0`` is
*not* allowed. However, assigning to a subspace defined by metadata
values may be done as follows: ``f.subspace[f.indices(*exact,
**metadata_values)] = 0``.

**Missing data**

The treatment of missing data elements during assignment to a subspace
depends on the value of field's `hardmask` attribute. If it is True
then masked elements will not be unmasked, otherwise masked elements
may be set to any value.

In either case, unmasked elements may be set, (including missing
data).

Unmasked elements may be set to missing data by assignment to the
`cf.masked` constant or by assignment to a value which contains masked
elements.

.. seealso:: `cf.masked`, `hardmask`, `indices`, `where`

:Examples:

>>> print f
Data            : air_temperature(time(12), latitude(73), longitude(96)) K
Cell methods    : time: mean
Dimensions      : time(12) = [15, ..., 345] days since 1860-1-1
                : latitude(73) = [-90, ..., 90] degrees_north
                : longitude(96) = [0, ..., 356.25] degrees_east
                : height(1) = [2] m

>>> f.shape
(12, 73, 96)
>>> f.subspace[...].shape
(12, 73, 96)
>>> f.subspace[slice(0, 12), :, 10:0:-2].shape
(12, 73, 5)
>>> lon = f.coord('X').array
>>> f.subspace[..., lon<180]

>>> f.shape
(12, 73, 96)
>>> f.subspace[0, ...].shape
(1, 73, 96)
>>> f.subspace[3, slice(10, 0, -2), 95].shape
(1, 5, 1)

>>> f.shape
(12, 73, 96)
>>> f.subspace[:, [0, 72], [5, 4, 3]].shape
(12, 2, 3)

>>> f.subspace().shape
(12, 73, 96)
>>> f.subspace(latitude=0).shape
(12, 1, 96)
>>> f.subspace(latitude=cf.wi(-30, 30)).shape
(12, 25, 96)
>>> f.subspace(long=cf.ge(270, 'degrees_east'), lat=cf.set([0, 2.5, 10])).shape
(12, 3, 24)
>>> f.subspace(latitude=cf.lt(0, 'degrees_north'))
(12, 36, 96)
>>> f.subspace(latitude=[cf.lt(0, 'degrees_north'), 90])
(12, 37, 96)
>>> import math
>>> f.subspace(longitude=cf.lt(math.pi, 'radian'), height=2)
(12, 73, 48)
>>> f.subspace(height=cf.gt(3))
IndexError: No indices found for 'height' values gt 3

>>> f.subspace(dim2=3.75).shape
(12, 1, 96)

>>> f.subspace[...] = 273.15
    
>>> f.subspace[f.indices(longitude=cf.wi(210, 270, 'degrees_east'),
...                      latitude=cf.wi(-5, 5, 'degrees_north'))] = cf.masked

>>> index = f.indices(longitude=0)
>>> f.subspace[index] = f.subspace[index] * 2

        '''
        return SubspaceField(self)
    #--- End: def

    def cell_area(self, radius=6371229.0, insert=False, force=False):
        '''{+Fef,}For each fiel

.. versionadded:: 1.0

.. seealso:: `weights`

:Examples 1:

>>> a = f.cell_area()

:Parameters:

    radius : data-like, optional
        The radius used for calculating spherical surface areas when
        both of the horizontal axes are part of a spherical polar
        coordinate system. By default *radius* has a value of
        6371229 metres. If units are not specified then units of
        metres are assumed.

        {+data-like}

          *Example:*         
            Five equivalent ways to set a radius of 6371200 metres:
            ``radius=6371200``, ``radius=numpy.array(6371200)``,
            ``radius=cf.Data(6371200)``, ``radius=cf.Data(6371200,
            'm')``, ``radius=cf.Data(6371.2, 'km')``.

    insert : bool, optional
        If True then{+,fef,} the calculated cell areas are also
        inserted in place as an area cell measure object. An existing
        area cell measure object for the horizontal axes will not be
        overwritten.

    force : bool, optional
        If True the always calculate the cell areas. By
        default{+,fef,} if there is already an area cell measure
        object for the horizontal axes then it will provide the area
        values.
        
:Returns:

    out : cf.{+Variable}

:Examples:

>>> a = f.cell_area()
>>> a = f.cell_area(insert=True)
>>> a = f.cell_area(force=True)
>>> a = f.cell_area(radius=cf.Data(3389.5, 'km'))

        '''
        # List functionality
        if self._list:
            kwargs2 = self._parameters(locals())
            return self._list_method('cell_area', kwargs2)
            
        area_clm = self.measure('area', axes=('X', 'Y'))

        if not force and area_clm:
            w = self.weights('area')
        else:
            x = self.dim('X')
            y = self.dim('Y')
            if (x is None or y is None or 
                not x.Units.equivalent(_units_radians) or
                not y.Units.equivalent(_units_radians)):
                raise ValueError("sd---------------------")
            
            # Got x and y coordinates in radians, so we can calc.
    
            # Parse the radius of the planet
            radius = Data.asdata(radius).squeeze()
            radius.dtype = float
            if radius.size != 1:
                raise ValueError("Multiple radii: radius=%r" % radius)
            if not radius.Units:
                radius.override_units(_units_m, i=True)
            elif not radius.Units.equivalent(_units_m):
                raise ValueError(
                    "Invalid units for radius: %r" % radius.Units)
                    
            w = self.weights('area')
            radius **= 2
            w *= radius
            w.override_units(radius.Units, i=True)   
        #--- End: if               

        if insert:
            # ----------------------------------------------------
            # Insert new cell measure
            # ----------------------------------------------------
            if area_clm:
                raise ValueError(
                    "Can't overwrite an existing area cell measure object")

            clm = CellMeasure(data=w.data, copy=True)
            clm.measure = 'area'
            map_axes = w.domain.map_axes(self.domain)
            data_axes = w.data_axes()
            axes = (map_axes[data_axes[0]], map_axes[data_axes[1]])
            self.insert_measure(clm, axes=axes, copy=False)
        #--- End: if               

        w.standard_name = 'area'
        w.long_name     = 'area'

        return w
    #--- End: def

    def close(self):
        '''

{+Fef,}Close all files referenced by the field.

Note that a closed file will be automatically reopened if its contents
are subsequently required.

:Examples 1:

>>> f.close()

:Returns:

    None
'''
        # List functionality
        if self._list:
            for f in self:
                f.close()
            return 

        new = super(Field, self).close()

        self.domain.close()

        ancillary_variables = getattr(self, 'ancillary_variables', None)
        if ancillary_variables is not None:
            ancillary_variables.close()
    #--- End: def

    def iscyclic(self, axes=None, **kwargs):
        '''
Returns True if the given axis is cyclic.

.. versionadded:: 1.0

.. seealso:: `axis`, `cyclic`, `period`

:Examples 1:

>>> b = f.iscyclic('X')

:Parameters:

    {+axes, kwargs}

:Returns:

    out : bool
        True if the selected axis is cyclic, otherwise False.
        
:Examples 2:

>>> f.cyclic()
{}
>>> f.iscyclic('X')
False
>>> f.cyclic('X', period=360)
{}
>>> f.iscyclic('X')
True

'''
        axis = self.domain.axis(axes, **kwargs)
        if axis is None:
            raise ValueError("Can't identify unique %r axis" % axes)

        return axis in self.cyclic()
    #--- End: def

    @classmethod
    def concatenate(cls, fields, axis=0, _preserve=True):
        '''

Join a sequence of fields together.

This is different to `cf.aggregate` because it does not account for
all metadata. For example, it assumes that the axis order is the same
in each field.

.. versionadded:: 1.0

.. seealso:: `cf.aggregate`, `cf.Data.concatenate`

:Parameters:

    axis : int, optional

:Returns:

    out : cf.Field

:Examples:

'''         
        field0 = fields[0]

        # List functionality
        if field0._list:
            return field0.concatenate(fields, axis=axis, _preserve=_preserve)

        if len(fields) == 1:
            return fields0.copy()
                                            
        out = super(cls, field0).concatenate(fields, axis=axis, _preserve=_preserve)
            
        # Change the axis size
        dim = field0.data_axes()[axis]        
        out.insert_axis(out.shape[axis], key=dim, replace=True)

        # ------------------------------------------------------------
        # Concatenate dimension coordinates, auxiliary coordinates and
        # cell measures
        # ------------------------------------------------------------
        for key, item in field0.items(role=('d', 'a', 'm')).iteritems():
            axes = field0.item_axes(key)

            if dim not in axes:
                # This item does not span the concatenating axis in
                # the first field
                continue

            items = [item]
            for f in fields[1:]:
                i = f.item(key)
                if i is not None:
                    items.append(i)                    
                else:
                    # This field does not have this item
                    items = None
                    break
            #--- End: for

            if not items:
                # Not every field has this item, so remove it from the
                # output field.
                out.remove_item(key)
                continue
                
            # Still here?
            try:
                item = item.concatenate(items, axis=axes.index(dim),
                                        _preserve=_preserve)
            except ValueError:
                # Couldn't concatenate this item, so remove it from
                # the output field.
                out.remove_item(key)
                continue

            if item.isdimension:
                out.insert_dim(item, key=key, copy=False, replace=True)
            elif item.isauxiliary:
                out.insert_aux(item, key=key, axes=axes, copy=False,
                               replace=True)
            elif item.ismeasure:
                out.insert_measure(item, key=key, axes=axes,
                                   copy=False, replace=True)
        #--- End: for

        # ------------------------------------------------------------
        # Concatenate ancillary variables
        # ------------------------------------------------------------
        ancillary_variables = getattr(out, 'ancillary_variables', None)
        if ancillary_variables:
            domain = out.domain
            n_avs = len(ancillary_variables)

            avs = [av]   #BBBBBBBUUUUUUUGGGGGGGGGGGGG I'm sure. What is av?
            for f in fields[1:]:
                avs1 = getattr(f, 'ancillary_variables', None)
                if avs1 is not None and len(avs1) == n_avs:
                    avs.append(avs1)
                else:
                    avs = None
                    break
            #--- End: for

            if not avs:
                del out.ancillary_variables
            else:
                out_avs = []
                for i in range(n_avs):
                    av0 = avs[0][i]
                    try:
                        iaxis = av0.data_axes().index(domain.map_axes(av0)[dim])
                        new_av = av0.concatenate([a[i] for a in avs],
                                                 axis=iaxis,
                                                 _preserve=_preserve)
                    except (KeyError, ValueError):
                        # Couldn't concatenate these ancillary
                        # variable fields
                        continue
                    else:
                        # Successfully concatenated these ancillary
                        # variable fields, so put the result in the
                        # output field.
                        out_avs.append(new_av)
                #--- End: for

                if out_avs:
                    out.ancillary_variables = FieldList(out_avs)
                else:
                    del out.ancillary_variables 
            #--- End: if
        #--- End: if        

        # ------------------------------------------------------------
        # Concatenate coordinate references
        # ------------------------------------------------------------

        return out
    #--- End: def

    def cyclic(self, axes=None, iscyclic=True, period=None, **kwargs):
        '''Set the cyclicity of an axis.

A unique axis is selected with the *axes* and *kwargs* parameters.

.. versionadded:: 1.0

.. seealso:: `autocyclic`, `axis`, `iscyclic`, `period`

`int`

:Examples 1:

Set the X axis to be periodic, with a period of 360:

>>> s = f.cyclic('X', period=360)

:Parameters:

    {+axes, kwargs}

    iscyclic : bool, optional
        If False then the axis is set to be non-cyclic. By default the
        selected axis is set to be cyclic.

    period : data-like object, optional       
        The period for a dimension coordinate object which spans the
        selected axis. The absolute value of *period* is used. If
        *period* has units then they must be compatible with those of
        the dimension coordinates, otherwise it is assumed to have the
        same units as the dimension coordinates.

        {+data-like}

:Returns:

    out : set
        The axes of the field which were cyclic prior to the new
        setting, or the current cyclic axes if no axis was specified.

:Examples:

>>> f.axes('X')
{'dim3'}
>>> f.cyclic()
{}
>>> f.cyclic('X', period=360)
{}
>>> f.cyclic()
{'dim3'}
>>> f.cyclic('X', False)
{'dim3'}
>>> f.cyclic()
{}
>>> f.cyclic('longitude', period=360, exact=True)
{}
>>> f.cyclic()
{'dim3'}
>>> f.cyclic('dim3', False)
{'dim3'}
>>> f.cyclic()
{}

        '''       
        try:
            data = self.Data
        except AttributeError:
            return set()

        data_axes = self.data_axes()
        old = set([data_axes[i] for i in data.cyclic()])

        if axes is None and not kwargs:            
            return old
        
        axis = self.domain.axis(axes, **kwargs)
        if axis is None:
            raise ValueError("879534 k.j asdm,547`")

        try:
            data.cyclic(data_axes.index(axis), iscyclic)
        except ValueError:
            pass

        if iscyclic:
            dim = self.dim(axis)
            if dim is not None:
                if period is not None:
                    dim.period(period)
                elif dim.period() is None:
                    raise ValueError(
                        "A cyclic dimension coordinate must have a period")
        #--- End: if

        return old
    #--- End: def

    def weights(self, weights='auto', scale=False, components=False,
                methods=False, **kwargs):
        '''{+Fef,}Return weights for the data array values.

By default weights components are created for all axes of the field by
one or more of the following methods, in order of preference,
                        
  1. Volume cell measures
  2. Area cell measures
  3. Area calculated from (grid) latitude and (grid) longitude
     dimension coordinates with bounds
  4. Cell sizes of dimension coordinates with bounds
  5. Equal weights

and the outer product of these weights components is returned in a
field which is broadcastable to the orginal field (see the
*components* parameter).

The methods used by the default behaviour may differ between fields,
depending on which metadata they contain (see the *methods*
parameter), so it is possible to force weights to be created with
particular methods (see the *weights* parameter).

.. versionadded:: 1.0

.. seealso:: `cell_area`, `collapse`

:Examples 1:

>>> g = f.weights()

:Parameters:

    weights, kwargs : *optional*
        Specify the weights to be created. There are two distinct
        methods: **type 1** will always succeed in creating weights
        for all axes of the field, at the expense of not always being
        able to control exactly how the weights are created (see the
        *methods* parameter); **type 2** allows particular types of
        weights to be defined for particular axes and an exception
        will be raised if it is not possible to the create weights.

          * **Type 1**: *weights* may be one of:
        
               ==========  ==================================================
               *weights*   Description
               ==========  ==================================================
               ``'auto'``  This the default. Weights are created for
                           non-overlapping subsets of the axes by the methods
                           enumerated in the above notes. Set the *methods*
                           parameter to find out how the weights were
                           actually created.
                               
               `None`      Equal weights for all axes.
               ==========  ==================================================

       ..

          * **Type 2**: *weights* may be one, or a sequence, of:
          
              ============  ==============================================
              *weights*     Description     
              ============  ==============================================
              ``'area'``    Cell area weights from the field's area cell
                            measure construct or, if one doesn't exist,
                            from (grid) latitude and (grid) longitude
                            dimension coordinates. Set the *methods*
                            parameter to find out how the weights were
                            actually created.
              
              ``'volume'``  Cell volume weights from the field's volume
                            cell measure construct.
              
              items         Weights from the cell sizes of the dimension
                            coordinate objects that would be selected by
                            this call of the field's `~cf.Field.dims`
                            method: ``f.dims(items, **kwargs)``. See
                            `cf.Field.dims` for details.
              
              `cf.Field`    Take weights from the data array of another
                            field, which must be broadcastable to this
                            field.
              ============  ==============================================
 
            If *weights* is a sequence of any combination of the above
            then the returned field contains the outer product of the
            weights defined by each element of the sequence. The
            ordering of the sequence is irrelevant.

              *Example:*
                To create to 2-dimensional weights based on cell
                areas: ``f.weights('area')``. To create to
                3-dimensional weights based on cell areas and linear
                height: ``f.weights(['area', 'Z'])``.

    scale : bool, optional
        If True then scale the returned weights so that they are less
        than or equal to 1.

    components : bool, optional
        If True then a dictionary of orthogonal weights components is
        returned instead of a field. Each key is a tuple of integers
        representing axes positions in the field's data array with
        corresponding values of weights in `cf.Data` objects. The axes
        of weights match the axes of the field's data array in the
        order given by their dictionary keys.

    methods : bool, optional
        If True, then return a dictionary describing methods used to
        create the weights.

:Returns:

    out : cf.Field or dict
        The weights field or, if *components* is True, orthogonal
        weights in a dictionary.

:Examples 2:

>>> f
[+1]<CF Field: air_temperature(time(1800), latitude(145), longitude(192)) K>
[+N][<CF Field: air_temperature(time(1800), latitude(145), longitude(192)) K>]
>>> f.weights()
[+1]<CF Field: long_name:weight(time(1800), latitude(145), longitude(192)) 86400 s.rad>
[+N][<CF Field: long_name:weight(time(1800), latitude(145), longitude(192)) 86400 s.rad>]
>>> f.weights('auto', scale=True)
[+1]<CF Field: long_name:weight(time(1800), latitude(145), longitude(192)) 1>
[+N][<CF Field: long_name:weight(time(1800), latitude(145), longitude(192)) 1>]
[+1]>>> f.weights('auto', components=True)
[+1]{(0,): <CF Data: [1.0, ..., 1.0] d>,
[+1] (1,): <CF Data: [5.94949998503e-05, ..., 5.94949998503e-05]>,
[+1] (2,): <CF Data: [0.0327249234749, ..., 0.0327249234749] radians>}
[+1]>>> f.weights('auto', components=True, scale=True)
[+1]{(0,): <CF Data: [1.0, ..., 1.0]>,
[+1] (1,): <CF Data: [0.00272710399807, ..., 0.00272710399807]>,
[+1] (2,): <CF Data: [1.0, ..., 1.0]>}
[+1]>>> f.weights('auto', methods=True)
[+1]{(0,): 'linear time',
[+1] (1,): 'linear sine latitude',
[+1] (2,): 'linear longitude'}

        '''
        def _field_of_weights(data, domain=None, axes=None):
            '''Return a field of weights with long_name ``'weight'``.

    :Parameters:
    
        data : cf.Data
            The weights which comprise the data array of the weights
            field.

        domain : cf.Domain, optional
            The domain for the weights field. Not required if *data*
            is scalar.

        axes : list, optional

    :Returns:

        out : cf.Field

            '''
            w = type(self)(domain=domain, data=data, axes=axes, copy=False)
            w.long_name = 'weight'
            w.comment   = 'Weights for %r' % self
            return w
        #--- End: def

        def _measure_weights(self, measure, comp, weights_axes, auto=False):
            '''
Cell measure weights
'''
            m = self.domain.items(measure, role='m', exact=True)
           
            if not m:
                if measure == 'area':
                    return False
                if auto:
                    return
                raise ValueError(
                    "Can't get weights: No %r cell measure" % measure)
            
            key, clm = m.popitem()    
            
            if m:
                if auto:
                    return False
                raise ValueError("Multiple area cell measures")
                
            clm_axes0 = self.domain.item_axes(key)
            
            clm_axes = [axis for axis, n in izip(clm_axes0, clm.shape)
                        if n > 1]
                
            for axis in clm_axes:
                if axis in weights_axes:
                    if auto:
                        return False
                    raise ValueError(
                        "Multiple weights specifications for %r axis" % 
                        self.domain.axis_name(axis))
                
            clm = clm.Data.copy()
            if clm_axes != clm_axes0:
                iaxes = [clm_axes0.index(axis) for axis in clm_axes]
                clm.squeeze(iaxes, i=True)
            
            if methods:
                comp[tuple(clm_axes)] = measure+' cell measure'
            else:    
                comp[tuple(clm_axes)] = clm
                
            weights_axes.update(clm_axes)
            
            return True
        #--- End: def
        
        def _linear_weights(self, axis, comp, weights_axes, auto=False):
            # ------------------------------------------------------------
            # 1-d linear weights from dimension coordinates
            # ------------------------------------------------------------            
            d = self.dims(axis)
            if not d:
                if auto:
                    return
                raise ValueError("Can't find axis matching %r" % axis)

            axis, dim = d.popitem()

            if d:         
                if auto:
                    return
                raise ValueError("Multiple axes matching %r" % axis)
            
            if dim.size == 1:
                return

            if axis in weights_axes:
                if auto:
                    return
                raise ValueError(
                    "Multiple weights specifications for %r axis" % 
                    self.domain.axis_name(axis))            

            if not dim.hasbounds:
                if auto:
                    return
                raise ValueError(
                    "Can't find linear weights for %r axis: No bounds" % 
                    dim.name(default=''))

            if dim.hasbounds:
                if methods:
                    comp[(axis,)] = 'linear '+dim.name(default='')
                else: 
                    comp[(axis,)] = dim.cellsize
            #--- End: if

            weights_axes.add(axis)
        #--- End: def
            
        def _area_weights_XY(self, comp, weights_axes, auto=False): 
            # ----------------------------------------------------
            # Calculate area weights from X and Y dimension
            # coordinates
            # ----------------------------------------------------
            xdims = self.dims({None: 'X', 'units': 'radians'})
            ydims = self.dims({None: 'Y', 'units': 'radians'})
            
            if not (xdims and ydims):
                if auto:
                    return
                raise ValueError(
"Insufficient coordinate constructs for calculating area weights")
                
            xaxis, xcoord = xdims.popitem()
            yaxis, ycoord = ydims.popitem()
                
            if xdims or ydims:
                if auto:
                    return
                raise ValueError(
"Ambiguous coordinate constructs for calculating area weights")
            
            for axis in (xaxis, yaxis):                
                if axis in weights_axes:
                    if auto:
                        return
                    raise ValueError(
                        "Multiple weights specifications for %r axis" % 
                        self.axis_name(axis))

            if xcoord.size > 1:
                if not xcoord.hasbounds: 
                    if auto:
                        return
                    raise ValueError(
                        "Can't find area weights: No bounds for %r axis" % 
                        xcoord.name(default=''))

                if methods:
                    comp[(xaxis,)] = 'linear '+xcoord.name(default='')
                else:
                    cells = xcoord.cellsize
                    cells.Units = _units_radians
                    comp[(xaxis,)] = cells

                weights_axes.add(xaxis)
            #--- End: if

            if ycoord.size > 1:
                if not ycoord.hasbounds:
                    if auto:
                        return
                    raise ValueError(
                        "Can't find area weights: No bounds for %r axis" % 
                        ycoord.name(default=''))

                ycoord = ycoord.clip(-90, 90, units=Units('degrees'))
                ycoord = ycoord.sin(i=True)
    
                if methods:
                    comp[(yaxis,)] = 'linear sine '+ycoord.name(default='')
                else:            
                    comp[(yaxis,)] = ycoord.cellsize

                weights_axes.add(yaxis)
            #--- End: if
        #--- End: def

        def _field_weights(self, fields, comp, weights_axes):
            # ------------------------------------------------------------
            # Field weights
            # ------------------------------------------------------------
            s = self.domain.analyse()

            for f in fields:
                t = f.domain.analyse()
    
                if t['undefined_axes']:
                    if t.axes(size=gt(1)).intersection(t['undefined_axes']):
                        raise ValueError("345jn456jn")
    
                f = f.squeeze()
    
                axes_map = {}
                
                for axis1 in f.data_axes():
                    identity = t['axis_to_id'].get(axis1, None)
                    if identity is None:
                        raise ValueError(
                            "Weights field has unmatched, size > 1 %r axis" %
                            f.axis_name(axis1))
                    
                    axis0 = s['id_to_axis'].get(identity, None)
                    if axis0 is None:
                        raise ValueError(
                            "Weights field has unmatched, size > 1 %r axis" %
                            identity)
                                    
                    axes_map[axis1] = axis0
    
                    if f.axis_size(axis1) != self.axis_size(axis0):
                        raise ValueError(
"Weights field has incorrectly sized %r axis (%d != %d)" % 
(identity, f.axis_size(axis1), self.axis_size(axis0)))
    
                    # Check that the defining coordinate data arrays are
                    # compatible
                    coord0 = s['axis_to_coord'][axis0]
                    coord1 = t['axis_to_coord'][axis1]
    
                    if not coord0._equivalent_data(coord1):
                        raise ValueError(
                            "Weights field has incompatible %r coordinates" %
                            identity)
    
                    # Still here? Then the defining coordinates have
                    # equivalent data arrays
    
                    # If the defining coordinates are attached to
                    # coordinate references then check that those coordinate references are
                    # equivalent
                    key0 = s['id_to_key'][identity]                
                    key1 = t['id_to_key'][identity]
    
                    equivalent_refs = True
                    for ref0 in self.refs().itervalues():
                        if key0 not in ref0.coords:
                            continue
    
                        equivalent_refs = False
                        for ref1 in g.refs().itervalues():
                            if key1 not in ref1.coords:
                                continue
    
                            # Each defining coordinate has a
                            # coordinate reference ...
                            if self.domain.equivalent_refs(ref0, ref1, f.domain):
                                # ... and those coordinate references are equivalent
                                equivalent_refs = True
                            #--- End: if
    
                            break
                        #--- End: for
    
                        break
                    #--- End: for
       
                    if not equivalent_refs:
                        raise ValueError(
"Input weights field has incompatible coordinate references")
                #--- End: for
    
                f_axes = tuple([axes_map[axis1] for axis1 in f.data_axes()])
            
                for axis1 in f_axes:
                    if axis1 in weights_axes:
                        raise ValueError(
                            "Multiple weights specified for %r axis" % 
                            self.axis_name(axes_map[axis1]))
                #--- End: if
    
                comp[f_axes] = f.Data
            
                weights_axes.update(f_axes)
        #--- End: def

        # List functionality
        if self._list:
            kwargs2 = self._parameters(locals())
            if components:
                raise ValueError("oooo 2")
            if methods:
                raise ValueError("oooo 3")
            return self._list_method('weights', kwargs2)

        if weights is None:
            # --------------------------------------------------------
            # All equal weights
            # --------------------------------------------------------
            if components:
                # Return an empty components dictionary
                return {}
            
            # Return a field containing a single weight of 1
            return _field_of_weights(Data(1.0, '1'))
        #--- End: if

        # Still here?
        if methods:
            components = True

        comp         = {}
        data_axes    = self.domain.data_axes()
        weights_axes = set()

        if isinstance(weights, basestring) and weights == 'auto':
            # --------------------------------------------------------
            # Autodetect all weights
            # --------------------------------------------------------

            # Volume weights
            _measure_weights(self, 'volume', comp, weights_axes, auto=True)

            # Area weights
            if not _measure_weights(self, 'area', comp, weights_axes, auto=True):
                _area_weights_XY(self, comp, weights_axes, auto=True)

            # 1-d linear weights from dimension coordinates
            for axis in self.dims(): #.keys():                
                _linear_weights(self, axis, comp, weights_axes, auto=True)
 
        elif isinstance(weights, dict):
            # --------------------------------------------------------
            # Dictionary of components
            # --------------------------------------------------------
            for key, value in weights.iteritems():                
                try:
                    key = [data_axes[iaxis] for iaxis in key]
                except IndexError:
                    raise ValueError("s ^^^^^^ csdcvd 3456 4")

                multiple_weights = weights_axes.intersection(key)
                if multiple_weights:
                    raise ValueError(
                        "Multiple weights specifications for %r axis" % 
                        self.domain.axis_name(multiple_weights.pop()))
                #--- End: if
                weights_axes.update(key)

                comp[tuple(key)] = value.copy()
            #--- End: for
        else:

            fields = []
            axes   = []
            
            if isinstance(weights, basestring) and weights in ('area', 'volume'):
                cell_measures = (weights,)
            else:
                cell_measures = []
                for w in tuple(weights):
                    if isinstance(w, self.__class__):
                        fields.append(w)
                    elif w in ('area', 'volume'):
                        cell_measures.append(w)
                    else:
                        axes.append(w)
            #--- End: if
            
            # Field weights
            _field_weights(self, fields, comp, weights_axes)

            # Volume weights
            if 'volume' in cell_measures:
                _measure_weights(self, 'volume', comp, weights_axes)
            
            # Area weights
            if 'area' in cell_measures:
                if not _measure_weights(self, 'area', comp, weights_axes):
                    _area_weights_XY(self, comp, weights_axes)      

            # 1-d linear weights from dimension coordinates
            for axis in axes:
                _linear_weights(self, axis, comp, weights_axes, auto=False)
        #--- End: if

        # ------------------------------------------------------------
        # Scale the weights so that they are <= 1.0
        # ------------------------------------------------------------
        if scale and not methods:
            # What to do about -ve weights? dch
            for key, w in comp.items(): 
                wmax = w.data.max()    
                if wmax > 0:
                    wmax.dtype = float
                    if not numpy_can_cast(wmax.dtype, w.dtype):
                        w = w / wmax
                    else:
                        w /= wmax
                    comp[key] = w
        #--- End: if

        if components:
            # --------------------------------------------------------
            # Return a dictionary of component weights, which may be
            # empty.
            # -------------------------------------------------------- 
            components = {}
            for key, v in comp.iteritems():
                key = [data_axes.index(axis) for axis in key]
                if not key:
                    continue

                components[tuple(key)] = v
            #--- End: for

            return components
        #--- End: if

        if methods:
            return components

        if not comp:
            # --------------------------------------------------------
            # No component weights have been defined so return an
            # equal weights field
            # --------------------------------------------------------
            return _field_of_weights(Data(1.0, '1'))
        
        # ------------------------------------------------------------
        # Return a weights field which is the outer product of the
        # component weights
        # ------------------------------------------------------------
        pp = sorted(comp.items())       
        waxes, wdata = pp.pop(0)
        while pp:
            a, y = pp.pop(0)
            wdata.outerproduct(y, i=True)
            waxes += a
        #--- End: while

        wdomain = self.domain.copy()

        asd = wdomain.axes().difference(weights_axes)

#        wdomain.dimensions.pop('data', None)
        wdomain._axes.pop('data', None)
        wdomain.remove_items(wdomain.items(axes=asd).keys())
        wdomain.remove_axes(asd) 

        return _field_of_weights(wdata, wdomain, waxes)
    #--- End: def
#(any object which may be used to
#            initialise a `cf.Data` instance)
   
# rolling_window=None, window_weights=None,
#
#    rolling_window : *optional*
#        Group the axis elements for a "rolling window" collapse. The
#        axis is grouped into **consecutive** runs of **overlapping**
#        elements. The first group starts at the first element of the
#        axis and each following group is offset by one element from
#        the previous group, so that an element may appear in multiple
#        groups. The collapse operation is applied to each group
#        independently and the collapsed axis in the returned field
#        will have a size equal to the number of groups. If weights
#        have been given by the *weights* parameter then they are
#        applied to each group, unless alternative weights have been
#        provided with the *window_weights* parameter. The
#        *rolling_window* parameter may be one of:
#
#          * An `int` defining the number of elements in each
#            group. Each group will have exactly this number of
#            elements. Note that if the group size does does not divide
#            exactly into the axis size then some elements at the end
#            of the axis will not be included in any group.
#            
#              Example: To define groups of 5 elements:
#              ``rolling_window=5``.
#
#        .. 
#
#          * A `cf.Data` defining the group size. Each group contains a
#            consecutive run of elements whose range of coordinate
#            bounds does not exceed the group size. Note that 1) if the
#            group size is sufficiently small then some groups may be
#            empty and some elements may not be inside any group may
#            not be inside any group; 2) different groups may contain
#            different numbers of elements.
#
#              Example: To create 10 kilometre windows:
#              ``rolling_window=cf.Data(10, 'km')``.
#
#    window_weights : ordered sequence of numbers, optional
#        Specify the weights for a rolling window collapse. Each
#        non-empty group uses these weights in its collapse, and all
#        non-empty groups must have the same number elements as the
#        window weights. If *window_weights* is not set then the groups
#        take their weights from the *weights* parameter, and in this
#        case the groups may have different sizes.
#
#          Example: To define a 1-2-1 smoothing filter:
#          ``rolling_window=3, window_weights=[1, 2, 1]``.

    def collapse(self, method, axes=None, squeeze=False, mtol=1,
                 weights='auto', ddof=1, a=None, i=False, group=None,
                 regroup=False, within_days=None, within_years=None,
                 over_days=None, over_years=None,
                 coordinate='mid_range', group_by='coords', **kwargs):
        r'''

{+Fef,}Collapse axes of the field. 

Collapsing an axis involves reducing its size with a given (typically
statistical) method.

By default all axes with size greater than 1 are collapsed completely
with the given method. For example, to find the minumum of the data
array:

>>> g = f.collapse('min')

By default the calculations of means, standard deviations and
variances use a combination of volume, area and linear weights based
on the field's metadata. For example to find the mean of the data
array, weighted where possible:

>>> g = f.collapse('mean')

Specific weights may be forced with the weights parameter. For example
to find the variance of the data array, weighting the X and Y axes by
cell area, the T axis linearly and leaving all other axes unweighted:

>>> g = f.collapse('variance', weights=['area', 'T'])

A subset of the axes may be collapsed. For example, to find the mean
over the time axis:

>>> f
[+1]<CF Field: air_temperature(time(12), latitude(73), longitude(96) K>
[+N][<CF Field: air_temperature(time(12), latitude(73), longitude(96) K>]
>>> g = f.collapse('T: mean')
>>> g
[+1]<CF Field: air_temperature(time(1), latitude(73), longitude(96) K>
[+N][<CF Field: air_temperature(time(1), latitude(73), longitude(96) K>]

For example, to find the maximum over the time and height axes:

>>> g = f.collapse('T: Z: max')

or, equivalently:

>>> g = f.collapse('max', axes=['T', 'Z'])

An ordered sequence of collapses over different (or the same) subsets
of the axes may be specified. For example, to first find the mean over
the time axis and subequently the standard deviation over the latitude
and longitude axes:

>>> g = f.collapse('T: mean area: sd')

or, equivalently, in two steps:

>>> g = f.collapse('mean', axes='T').collapse('sd', axes='area')

Grouped collapses are possible, whereby groups of elements along an
axis are defined and each group is collapsed independently. The
collapsed groups are concatenated so that the collapsed axis in the
output field has a size equal to the number of groups. For example, to
find the variance along the longitude axis within each group of size
10 degrees:

>>> g = f.collapse('longitude: variance', group=cf.Data(10, 'degrees'))

Climatological statistics (a type of grouped collapse) as defined by
the CF conventions may be specified. For example, to collapse a time
axis into multiannual means of calendar monthly minima:

>>> g = f.collapse('time: minimum within years T: mean over years',
...                 within_years=cf.M())

In all collapses, missing data array elements are accounted for in the
calculation.

The following collapse methods are available, over any subset of the
axes:

=========================  =====================================================
Method                     Notes
=========================  =====================================================
Maximum                    The maximum of the values.
                           
Minimum                    The minimum of the values.
                                    
Sum                        The sum of the values.
                           
Mid-range                  The average of the maximum and the minimum of the
                           values.
                           
Range                      The absolute difference between the maximum and
                           the minimum of the values.
                           
Mean                       The unweighted mean, :math:`m`, of :math:`N`
                           values :math:`x_i` is
                           
                           .. math:: m=\frac{1}{N}\sum_{i=1}^{N} x_i
                           
                           The weighted mean, :math:`\tilde{m}`, of :math:`N`
                           values :math:`x_i` with corresponding weights
                           :math:`w_i` is
                           

                           .. math:: \tilde{m}=\frac{1}{\sum_{i=1}^{N} w_i}
                                               \sum_{i=1}^{N} w_i x_i
                           
Standard deviation         The unweighted standard deviation, :math:`s`, of
                           :math:`N` values :math:`x_i` with mean :math:`m`
                           and with :math:`N-ddof` degrees of freedom
                           (:math:`ddof\ge0`) is
                           
                           .. math:: s=\sqrt{\frac{1}{N-ddof}
                                       \sum_{i=1}^{N} (x_i - m)^2}
                           
                           The weighted standard deviation,
                           :math:`\tilde{s}_N`, of :math:`N` values
                           :math:`x_i` with corresponding weights
                           :math:`w_i`, weighted mean
                           :math:`\tilde{m}` and with :math:`N`
                           degrees of freedom is
                           
                           .. math:: \tilde{s}_N=\sqrt{\frac{1}
                                         {\sum_{i=1}^{N} w_i}
                                         \sum_{i=1}^{N} w_i(x_i -
                                         \tilde{m})^2}
                           
                           The weighted standard deviation,
                           :math:`\tilde{s}`, of :math:`N` values
                           :math:`x_i` with corresponding weights
                           :math:`w_i` and with :math:`N-ddof` degrees
                           of freedom :math:`(ddof>0)` is
                           
                           .. math:: \tilde{s}=\sqrt{ \frac{a
                                     \sum_{i=1}^{N} w_i}{a
                                     \sum_{i=1}^{N} w_i - ddof}}
                                     \tilde{s}_N
                           
                           where :math:`a` is the smallest positive
                           number whose product with each weight is an
                           integer. :math:`a \sum_{i=1}^{N} w_i` is
                           the size of a new sample created by each
                           :math:`x_i` having :math:`aw_i` repeats. In
                           practice, :math:`a` may not exist or may be
                           difficult to calculate, so :math:`a` is
                           either set to a predetermined value or an
                           approximate value is calculated (see the
                           *a* parameter for details).
                           
Variance                   The variance is the square of the standard
                           deviation.
                           
Sample size                The sample size, :math:`N`, as would be used for 
                           other statistical calculations.
                           
Sum of weights             The sum of sample weights,
                           :math:`\sum_{i=1}^{N} w_i`, as would be
                           used for other statistical calculations.

Sum of squares of weights  The sum of squares of sample weights,
                           :math:`\sum_{i=1}^{N} {w_i}^{2}`,
                           as would be used for other statistical
                           calculations.
=========================  =====================================================


.. versionadded:: 1.0

.. seealso:: `cell_area`, `weights`, `max`, `mean`, `mid_range`,
             `min`, `range`, `sample_size`, `sd`, `sum`, `var`


:Parameters:

    method : str
        Define the collapse method. All of the axes specified by the
        *axes* parameter are collapsed simultaneously by this
        method. The method is given by one of the following strings:

          ========================================  =========================
          *method*                                  Description
          ========================================  =========================
          ``'max'`` or ``'maximum'``                Maximum                  
          ``'min'`` or ``'minimum'``                Minimum                      
          ``'sum'``                                 Sum                      
          ``'mid_range'``                           Mid-range                
          ``'range'``                               Range                    
          ``'mean'`` or ``'average'`` or ``'avg'``  Mean                         
          ``'sd'`` or ``'standard_deviation'``      Standard deviation       
          ``'var'`` or ``'variance'``               Variance                 
          ``'sample_size'``                         Sample size                      
          ``'sum_of_weights'``                      Sum of weights           
          ``'sum_of_weights2'``                     Sum of squares of weights
          ========================================  =========================

        An alternative form is to provide a CF cell methods-like
        string. In this case an ordered sequence of collapses may be
        defined and both the collapse methods and their axes are
        provided. The axes are interpreted as for the *axes*
        parameter, which must not also be set. For example:
          
        >>> g = f.collapse('time: max (interval 1 hr) X: Y: mean dim3: sd')
        
        is equivalent to:
        
        >>> g = f.collapse('max', axes='time')
        >>> g = g.collapse('mean', axes=['X', 'Y'])
        >>> g = g.collapse('sd', axes='dim3')    

        Climatological collapses are carried out if a *method* string
        contains any of the modifiers ``'within days'``, ``'within
        years'``, ``'over days'`` or ``'over years'``. For example, to
        collapse a time axis into multiannual means of calendar
        monthly minima:

        >>> g = f.collapse('time: minimum within years T: mean over years',
        ...                 within_years=cf.M())
          
        which is equivalent to:
          
        >>> g = f.collapse('time: minimum within years', within_years=cf.M())
        >>> g = g.collapse('mean over years', axes='T')

    axes, kwargs : optional  
        The axes to be collapsed. The axes are those that would be
        selected by this call of the field's `axes` method:
        ``f.axes(axes, **kwargs)``. See `cf.Field.axes` for
        details. If an axis has size 1 then it is ignored. By default
        all axes with size greater than 1 are collapsed. If *axes* has
        the special value ``'area'`` then it is assumed that the X and
        Y axes are intended.

          *Example:*

            ``axes='area'`` is equivalent to ``axes=['X',
            'Y']``. ``axes=['area', Z']`` is equivalent to
            ``axes=['X', 'Y', 'Z']``.


    weights : *optional*
        Specify the weights for the collapse. The weights are those
        that would be returned by this call of the field's
        `~cf.Field.weights` method: ``f.weights(weights,
        components=True)``. By default weights is ``'auto'``, meaning
        that weights for all axes are created from the field's
        metadata by one or more of the following methods, in order of
        preference,
                        
          1. Cell volume (from cell measures)
          2. Cell area (from cell measures)
          3. Cell area calculated from (grid) latitude and (grid)
             longitude dimension coordinates with bounds
          4. Cell sizes of dimension coordinates with bounds
          5. Equal weights

        See `cf.Field.weights` for details.

          *Example:*
            To specify weights based on cell areas use
            ``weights='area'``. To specify weights based on cell areas
            and linearly in the vertical you could set
            ``weights=('area', 'Z')``.

    squeeze : bool, optional
        If True then size 1 collapsed axes are removed from the output
        data array. By default the axes which are collapsed are
        retained in the result's data array.

    mtol : number, optional        
        Set the fraction of input array elements which is allowed to
        contain missing data when contributing to an individual output
        array element. Where this fraction exceeds *mtol*, missing
        data is returned. The default is 1, meaning that a missing
        datum in the output array only occurs when its contributing
        input array elements are all missing data. A value of 0 means
        that a missing datum in the output array occurs whenever any
        of its contributing input array elements are missing data. Any
        intermediate value is permitted.

          *Example:*
            To ensure that an output array element is a missing datum
            if more than 25% of its input array elements are missing
            data: ``mtol=0.25``.

    ddof : number, *optional*
        The delta degrees of freedom in the calculation of a standard
        deviation or variance. The number of degrees of freedom used
        in the calculation is (N-*ddof*) where N represents the number
        of non-missing elements. By default *ddof* is 1, meaning the
        standard deviation and variance of the population is estimated
        according to the usual formula with (N-1) in the denominator
        to avoid the bias caused by the use of the sample mean
        (Bessel's correction).

    a : *optional*
        Specify the value of :math:`a` in the calculation of a
        weighted standard deviation or variance when the *ddof*
        parameter is greater than 0. See the notes above for
        details. A value is required each output array element, so *a*
        must be a single number or else a field which is broadcastable
        to the collapsed field. By default the calculation of each
        output array element uses an approximate value of *a* which is
        the smallest positive number whose products with the smallest
        and largest of the contributing weights, and their sum, are
        all integers. In this case, a positive number is considered to
        be an integer if its decimal part is sufficiently small (no
        greater than 10\ :sup:`-8` plus 10\ :sup:`-5` times its
        integer part).

          *Example:*            
             To guarantee that :math:`\tilde{s}` is exact when the
             weights for each output array element are collectively
             coprime integers: ``a=1``.

          *Note:*
            * The default approximation will never overestimate
              :math:`a`, so :math:`\tilde{s}` will always greater than
              or equal to its true value when :math:`a` is not
              specified.

    coordinate : str, optional
        Set how the cell coordinate values for collapsed axes are
        defined. This has no effect on the cell bounds for the
        collapsed axes, which always represent the extrema of the
        input coordinates. Valid values are:

          ===============  ===========================================
          *coordinate*     Description
          ===============  ===========================================        
          ``'mid_range'``  An output coordinate is the average of the
                           first and last input coordinate bounds (or
                           the first and last coordinates if there are
                           no bounds). This is the default.
                           
          ``'min'``        An output coordinate is the minimum of the
                           input coordinates.
                           
          ``'max'``        An output coordinate is the maximum of the
                           input coordinates.
          ===============  ===========================================
       
    group : *optional*        
        Independently collapse groups of axis elements. Upon output,
        the results of the collapses are concatenated so that the
        output axis has a size equal to the number of groups. The
        *group* parameter defines how the elements are partitioned
        into groups, and may be one of:

          * A `cf.Data` defining the group size in terms of ranges of
            coordinate values. The first group starts at the first
            coordinate bound of the first axis element (or its
            coordinate if there are no bounds) and spans the defined
            group size. Each susbsequent group immediately follows the
            preceeeding one. By default each group contains the
            consective run of elements whose coordinate values lie
            within the group limits (see the *group_by* parameter).

              *Example:*
                To define groups of 10 kilometres: ``group=cf.Data(10,
                'km')``.

              *Note:*
                * By default each element will be in exactly one
                  group (see the *group_by* parameter).
                * Groups may contain different numbers of elements.
                * If no units are specified then the units of the
                  coordinates are assumed.

        ..

          * A `cf.TimeDuration` defining the group size in terms of
            calendar months and years or other time intervals. The
            first group starts at or before the first coordinate bound
            of the first axis element (or its coordinate if there are
            no bounds) and spans the defined group size. Each
            susbsequent group immediately follows the preceeeding
            one. By default each group contains the consective run of
            elements whose coordinate values lie within the group
            limits (see the *group_by* parameter).

              *Example:*
                To define groups of 5 days, starting and ending at
                midnight on each day: ``group=cf.D(5)`` (see `cf.D`).

              *Example:*
                To define groups of 1 calendar month, starting and
                ending at day 16 of each month: ``group=cf.M(day=16)``
                (see `cf.M`).

              *Note:*
                * By default each element will be in exactly one
                  group (see the *group_by* parameter).
                * Groups may contain different numbers of elements.
                * The start of the first group may be before the first
                  first axis element, depending on the offset defined
                  by the time duration. For example, if
                  ``group=cf.Y(month=12)`` then the first group will
                  start on the closest 1st December to the first axis
                  element.

        ..

          * A (sequence of) `cf.Query`, each of which is a condition
            defining one or more groups. Each query selects elements
            whose coordinates satisfy its condition and from these
            elements multiple groups are created - one for each
            maximally consecutive run within these elements.

              *Example:*
                To define groups of the season MAM in each year:
                ``group=cf.mam()`` (see `cf.mam`).
              
              *Example:*
                To define groups of the seasons DJF and JJA in each
                year: ``group=[cf.jja(), cf.djf()]``. To define groups
                for seasons DJF, MAM, JJA and SON in each year:
                ``group=cf.seasons()`` (see `cf.djf`, `cf.jja` and
                `cf.season`).
              
              *Example:*
                To define groups for longitude elements less than or
                equal to 90 degrees and greater than 90 degrees:
                ``group=[cf.le(90, 'degrees'), cf.gt(90, 'degrees')]``
                (see `cf.le` and `cf.gt`).

              *Note:*
                * If a coordinate does not satisfy any of the
                  conditions then its element will not be in a group.
                * Groups may contain different numbers of elements.
                * If no units are specified then the units of the
                  coordinates are assumed.
                * If an element is selected by two or more queries
                  then the latest one in the sequence defines which
                  group it will be in.

        .. 

          * An `int` defining the number of elements in each
            group. The first group starts with the first axis element
            and spans the defined number of consecutive elements. Each
            susbsequent group immediately follows the preceeeding
            one.

              *Example:*
                To define groups of 5 elements: ``group=5``.

              *Note:*
                * Each group has the defined number of elements, apart
                  from the last group which may contain fewer
                  elements.

        .. 

          * A `numpy.array` of integers defining groups. The array
            must have the same length as the axis to be collapsed and
            its sequence of values correspond to the axis
            elements. Each group contains the elements which
            correspond to a common non-negative integer value in the
            numpy array. Upon output, the collapsed axis is arranged
            in order of increasing group number.

              *Example:*
                For an axis of size 8, create two groups, the first
                containing the first and last elements and the second
                containing the 3rd, 4th and 5th elements, whilst
                ignoring the 2nd, 6th and 7th elements:
                ``group=numpy.array([0, -1, 4, 4, 4, -1, -2, 0])``.

              *Note:* 
                * The groups do not have to be in runs of consective
                  elements; they may be scattered throughout the axis.
                * An element which corresponds to a negative integer
                  in the array will not be in a group.

    group_by : str, optional
        Specify how coordinates are assigned to the groups defined by
        the *group*, *within_days* or *within_years*
        parameter. Ignored unless one of these parameters is a
        `cf.Data` or `cf.TimeDuration` object. The *group_by*
        parameter may be one of:

          * ``'coords'``. This is the default. Each group contains the
            axis elements whose coordinate values lie within the group
            limits. Every element will be in a group.

        ..

          * ``'bounds'``. Each group contains the axis elements whose
            upper and lower coordinate bounds both lie within the
            group limits. Some elements may not be inside any group,
            either because the group limits do not coincide with
            coordinate bounds or because the group size is
            sufficiently small.

    regroup : bool, optional
        For grouped collapses, return a `numpy.array` of integers
        which identifies the groups defined by the *group*
        parameter. The array is interpreted as for a numpy array value
        of the *group* parameter, and thus may subsequently be used by
        *group* parameter in a separate collapse. For example:

        >>> groups = f.collapse('time: mean', group=10, regroup=True)
        >>> g = f.collapse('time: mean', group=groups)

        is equivalent to:

        >>> g = f.collapse('time: mean', group=10)

    within_days : *optional*
        Independently collapse groups of reference-time axis elements
        for CF "within days" climatological statistics. Each group
        contains elements whose coordinates span a time interval of up
        to one day. Upon output, the results of the collapses are
        concatenated so that the output axis has a size equal to the
        number of groups.

        *Note:*
          For CF compliance, a "within days" collapse should be
          followed by an "over days" collapse.

        The *within_days* parameter defines how the elements are
        partitioned into groups, and may be one of:

          * A `cf.TimeDuration` defining the group size in terms of a
            time interval of up to one day. The first group starts at
            or before the first coordinate bound of the first axis
            element (or its coordinate if there are no bounds) and
            spans the defined group size. Each susbsequent group
            immediately follows the preceeeding one. By default each
            group contains the consective run of elements whose
            coordinate values lie within the group limits (see the
            *group_by* parameter).

              *Example:*
                To define groups of 6 hours, starting at 00:00, 06:00,
                12:00 and 18:00: ``within_days=cf.h(6)`` (see `cf.h`).

              *Example:*
                To define groups of 1 day, starting at 06:00:
                ``within_days=cf.D(1, hour=6)`` (see `cf.D`).

              *Note:*
                * Groups may contain different numbers of elements.
                * The start of the first group may be before the first
                  first axis element, depending on the offset defined
                  by the time duration. For example, if
                  ``group=cf.D(hour=12)`` then the first group will
                  start on the closest midday to the first axis
                  element.

        ..

          * A (sequence of) `cf.Query`, each of which is a condition
            defining one or more groups. Each query selects elements
            whose coordinates satisfy its condition and from these
            elements multiple groups are created - one for each
            maximally consecutive run within these elements.

              *Example:*
                To define groups of 00:00 to 06:00 within each day,
                ignoring the rest of each day:
                ``within_days=cf.hour(cf.le(6))`` (see `cf.hour` and
                `cf.le`).

              *Example:*
                To define groups of 00:00 to 06:00 and 18:00 to 24:00
                within each day, ignoring the rest of each day:
                ``within_days=[cf.hour(cf.le(6)),
                cf.hour(cf.gt(18))]`` (see `cf.gt`, `cf.hour` and
                `cf.le`).

              *Note:*
                * Groups may contain different numbers of elements.
                * If no units are specified then the units of the
                  coordinates are assumed.
                * If a coordinate does not satisfy any of the
                  conditions then its element will not be in a group.
                * If an element is selected by two or more queries
                  then the latest one in the sequence defines which
                  group it will be in.

    within_years : *optional* 
        Independently collapse groups of reference-time axis elements
        for CF "within years" climatological statistics. Each group
        contains elements whose coordinates span a time interval of up
        to one calendar year. Upon output, the results of the
        collapses are concatenated so that the output axis has a size
        equal to the number of groups.

          *Note:*
            For CF compliance, a "within years" collapse should be
            followed by an "over years" collapse.

        The *within_years* parameter defines how the elements are
        partitioned into groups, and may be one of:

          * A `cf.TimeDuration` defining the group size in terms of a
            time interval of up to one calendar year. The first group
            starts at or before the first coordinate bound of the
            first axis element (or its coordinate if there are no
            bounds) and spans the defined group size. Each susbsequent
            group immediately follows the preceeeding one. By default
            each group contains the consective run of elements whose
            coordinate values lie within the group limits (see the
            *group_by* parameter).

              *Example:*
                To define groups of 90 days: ``within_years=cf.D(90)``
                (see `cf.D`).

              *Example:*  
                To define groups of 3 calendar months, starting on the
                15th of a month: ``within_years=cf.M(3, day=15)`` (see
                `cf.M`).

              *Note:*
                * Groups may contain different numbers of elements.
                * The start of the first group may be before the first
                  first axis element, depending on the offset defined
                  by the time duration. For example, if
                  ``group=cf.Y(month=12)`` then the first group will
                  start on the closest 1st December to the first axis
                  element.

        ..

          * A (sequence of) `cf.Query`, each of which is a condition
            defining one or more groups. Each query selects elements
            whose coordinates satisfy its condition and from these
            elements multiple groups are created - one for each
            maximally consecutive run within these elements.

              *Example:*
                To define groups for the season MAM within each year:
                ``within_years=cf.mam()`` (see `cf.mam`).

              *Example:*
                To define groups for February and for November to
                December within each year:
                ``within_years=[cf.month(2), cf.month(cf.ge(11))]``
                (see `cf.month` and `cf.ge`).

              *Note:*
                * The first group may start outside of the range of
                  coordinates (the start of the first group is
                  controlled by parameters of the `cf.TimeDuration`).
                * If group boundaries do not coincide with coordinate
                  bounds then some elements may not be inside any
                  group.
                * If the group size is sufficiently small then some
                  elements may not be inside any group.
                * Groups may contain different numbers of elements.

    over_days : *optional*
        Independently collapse groups of reference-time axis elements
        for CF "over days" climatological statistics. Each group
        contains elements whose coordinates are **matching**, in that
        their lower bounds have a common time of day but different
        dates of the year, and their upper bounds also have a common
        time of day but different dates of the year. Upon output, the
        results of the collapses are concatenated so that the output
        axis has a size equal to the number of groups.

          *Example:*
            An element with coordinate bounds {1999-12-31 06:00:00,
            1999-12-31 18:00:00} **matches** an element with
            coordinate bounds {2000-01-01 06:00:00, 2000-01-01
            18:00:00}.

          *Example:*
            An element with coordinate bounds {1999-12-31 00:00:00,
            2000-01-01 00:00:00} **matches** an element with
            coordinate bounds {2000-01-01 00:00:00, 2000-01-02
            00:00:00}.

          *Note:*       
            * A *coordinate* parameter value of ``'min'`` is assumed,
              regardless of its given value.
             
            * A *group_by* parameter value of ``'bounds'`` is assumed,
              regardless of its given value.
            
            * An "over days" collapse must be preceded by a "within
              days" collapse, as described by the CF conventions. If the
              field already contains sub-daily data, but does not have
              the "within days" cell methods flag then it may be added,
              for example, as follows (this example assumes that the
              appropriate cell method is the most recently applied,
              which need not be the case; see `cf.CellMethods` for
              details):
            
              >>> f.cell_methods[-1].within = 'days'

        The *over_days* parameter defines how the elements are
        partitioned into groups, and may be one of:

          * `None`. This is the default. Each collection of
            **matching** elements forms a group.

        ..

          * A `cf.TimeDuration` defining the group size in terms of a
            time duration of at least one day. Multiple groups are
            created from each collection of **matching** elements -
            the first of which starts at or before the first
            coordinate bound of the first element and spans the
            defined group size. Each susbsequent group immediately
            follows the preceeeding one. By default each group
            contains the **matching** elements whose coordinate values
            lie within the group limits (see the *group_by*
            parameter).

              *Example:*
                To define groups spanning 90 days:
                ``over_days=cf.D(90)`` or
                ``over_days=cf.h(2160)``. (see `cf.D` and `cf.h`).

              *Example:*
                To define groups spanning 3 calendar months, starting
                and ending at 06:00 in the first day of each month:
                ``over_days=cf.M(3, hour=6)`` (see `cf.M`).

              *Note:*
                * Groups may contain different numbers of elements.
                * The start of the first group may be before the first
                  first axis element, depending on the offset defined
                  by the time duration. For example, if
                  ``group=cf.M(day=15)`` then the first group will
                  start on the closest 15th of a month to the first
                  axis element.

        ..

          * A (sequence of) `cf.Query`, each of which is a condition
            defining one or more groups. Each query selects elements
            whose coordinates satisfy its condition and from these
            elements multiple groups are created - one for each subset
            of **matching** elements.

              *Example:*
                To define groups for January and for June to December,
                ignoring all other months: ``over_days=[cf.month(1),
                cf.month(cf.wi(6, 12))]`` (see `cf.month` and
                `cf.wi`).

              *Note:*
                * If a coordinate does not satisfy any of the
                  conditions then its element will not be in a group.
                * Groups may contain different numbers of elements.
                * If an element is selected by two or more queries
                  then the latest one in the sequence defines which
                  group it will be in.

    over_years : *optional*
        Independently collapse groups of reference-time axis elements
        for CF "over years" climatological statistics. Each group
        contains elements whose coordinates are **matching**, in that
        their lower bounds have a common sub-annual date but different
        years, and their upper bounds also have a common sub-annual
        date but different years. Upon output, the results of the
        collapses are concatenated so that the output axis has a size
        equal to the number of groups.

          *Example:*
            An element with coordinate bounds {1999-06-01 06:00:00,
            1999-09-01 06:00:00} **matches** an element with
            coordinate bounds {2000-06-01 06:00:00, 2000-09-01
            06:00:00}.

          *Example:*
            An element with coordinate bounds {1999-12-01 00:00:00,
            2000-12-01 00:00:00} **matches** an element with
            coordinate bounds {2000-12-01 00:00:00, 2001-12-01
            00:00:00}.

          *Note:*       
            * A *coordinate* parameter value of ``'min'`` is assumed,
              regardless of its given value.
             
            * A *group_by* parameter value of ``'bounds'`` is assumed,
              regardless of its given value.
            
            * An "over years" collapse must be preceded by a "within
              years" or an "over days" collapse, as described by the
              CF conventions. If the field already contains sub-annual
              data, but does not have the "within years" or "over
              days" cell methods flag then it may be added, for
              example, as follows (this example assumes that the
              appropriate cell method is the most recently applied,
              which need not be the case; see `cf.CellMethods` for
              details):

              >>> f.cell_methods[-1].over = 'days'

        The *over_years* parameter defines how the elements are
        partitioned into groups, and may be one of:

          * `None`. Each collection of **matching** elements forms a
            group. This is the default.

        ..

          * A `cf.TimeDuration` defining the group size in terms of a
            time interval of at least one calendar year. Multiple
            groups are created from each collection of **matching**
            elements - the first of which starts at or before the
            first coordinate bound of the first element and spans the
            defined group size. Each susbsequent group immediately
            follows the preceeeding one. By default each group
            contains the **matching** elements whose coordinate values
            lie within the group limits (see the *group_by*
            parameter).

              *Example:*
                To define groups spanning 10 calendar years:
                ``over_years=cf.Y(10)`` or ``over_years=cf.M(120)``
                (see `cf.M` and `cf.Y`).

              *Example:*
                To define groups spanning 5 calendar years, starting
                and ending at 06:00 on 01 December of each year:
                ``over_years=cf.Y(5, month=12, hour=6)`` (see `cf.Y`).

              *Note:*
                * Groups may contain different numbers of elements.
                * The start of the first group may be before the first
                  first axis element, depending on the offset defined
                  by the time duration. For example, if
                  ``group=cf.Y(month=12)`` then the first group will
                  start on the closest 1st December to the first axis
                  element.

        ..

          * A (sequence of) `cf.Query`, each of which is a condition
            defining one or more groups. Each query selects elements
            whose coordinates satisfy its condition and from these
            elements multiple groups are created - one for each subset
            of **matching** elements.

              *Example:*
                To define one group spanning 1981 to 1990 and another
                spanning 2001 to 2005:
                ``over_years=[cf.year(cf.wi(1981, 1990),
                cf.year(cf.wi(2001, 2005)]`` (see `cf.year` and
                `cf.wi`).

              *Note:*
                * If a coordinate does not satisfy any of the
                  conditions then its element will not be in a group.
                * Groups may contain different numbers of elements.
                * If an element is selected by two or more queries
                  then the latest one in the sequence defines which
                  group it will be in.

    {+i}

:Returns:
 
[+1]    out : cf.Field or numpy array
[+N]    out : cf.{+variable} or list
           {+Fef,}The collapsed field. If the *regroup* parameter is
           True then a numpy array is returned.

:Examples:

Calculate the unweighted  mean over a the entire field:

>>> g = f.collapse('mean')

Five equivalent ways to calculate the unweighted  mean over a CF latitude axis:

>>> g = f.collapse('latitude: mean')
>>> g = f.collapse('lat: avg')
>>> g = f.collapse('Y: average')
>>> g = f.collapse('mean', 'Y')
>>> g = f.collapse('mean', ['latitude'])

Three equivalent ways to calculate an area weighted mean over CF
latitude and longitude axes:

>>> g = f.collapse('area: mean', weights='area')
>>> g = f.collapse('lat: lon: mean', weights='area')
>>> g = f.collapse('mean', axes=['Y', 'X'], weights='area')

Two equivalent ways to calculate a time weighted mean over CF
latitude, longitude and time axes:

>>> g = f.collapse('X: Y: T: mean', weights='T')
>>> g = f.collapse('mean', axes=['T', 'Y', 'X'], weights='T')

Find how many non-missing elements in each group of a grouped
collapse:

>>> f.collapse('latitude: sample_size', group=cf.Data(5 'degrees'))

'''
        # List functionality
        if self._list:
            kwargs2 = self._parameters(locals())
            if regroup:
                raise ValueError("oooo")
            return self._list_method('collapse', kwargs2)

        if i:
            f = self
        else:
            f = self.copy()

        # ------------------------------------------------------------
        # Parse the methods and axes
        # ------------------------------------------------------------
        if ':' in method:
            # Convert a cell methods string (such as 'area: mean dim3:
            # dim2: max T: minimum height: variance') to a CellMethods
            # object
            if axes is not None:
                raise ValueError(
"Can't collapse: Can't set axes when method is CF cell methods-like string")

            method = CellMethods(method)
        
            all_methods = method.method
            all_axes    = method.names
            all_within  = method.within
            all_over    = method.over
        else:            
            x = method.split(' within ')
            if method == x[0]:
                within = None
                x = method.split(' over ')
                if method == x[0]:
                    over = None
                else:
                    method, over = x
            else:
                method, within = x
           
            if isinstance(axes, basestring):
                axes = (axes,)

            all_methods = (method,)
            all_within  = (within,)
            all_over    = (over,)
            all_axes    = (axes,)
        #--- End: if
        
        # Parse special axes values
        all_axes2 = []
        for axes in all_axes:
            if axes is None:
                all_axes2.append(axes)
                continue

            axes2 = []
            for axis in axes:
                if axis == 'area':
                    axes2.extend(('X', 'Y'))
                # Not yet in CF
                #elif axis == 'volume':
                #    axes2.extend(('X', 'Y', 'Z'))
                else:
                    axes2.append(axis)
            #--- End: for
            all_axes2.append(axes2)
        #--- End: for
        all_axes = all_axes2

        if group is not None and len(all_axes) > 1:
            raise ValueError(
                "Can't use group parameter for multiple collapses")

        # ------------------------------------------------------------
        #
        # ------------------------------------------------------------
        for method, axes, within, over in izip(all_methods, all_axes,
                                               all_within, all_over):
            domain = f.domain

            method2 = _collapse_methods.get(method, None)
            if method2 is None:
                raise ValueError("Can't collapse: Unknown method: %s" % method)

            method = method2

            kwargs['ordered'] = True
            if method not in ('sample_size', 'sum_of_weights', 'sum_of_weights2'):
                kwargs['size'] = gt(1)

            collapse_axes = domain.axes(axes, **kwargs)

            if not collapse_axes:
                # Do nothing if there are no collapse axes
                continue
    
#            if axes != (None,) and len(collapse_axes) != len(axes):
#                raise ValueError("Can't collapse: Ambiguous collapse axes")

            # Check that there are enough elements to collapse
            size = reduce(operator_mul, domain.axes_sizes(collapse_axes).values(), 1)
            min_size = _collapse_min_size.get(method, 1)
            if size < min_size:
                raise ValueError(
                    "Can't calculate %s from fewer than %d elements" %
                    (_collapse_cell_methods[method], min_size))
    
            grouped_collapse = (within is not None or
                                over   is not None or
                                group  is not None)

            if grouped_collapse:
                if len(collapse_axes) > 1:
                    raise ValueError(
                        "Can't group collapse multiple axes simultaneously")

                # ------------------------------------------------------------
                # Calculate weights
                # ------------------------------------------------------------
                g_weights = weights
                if method in _collapse_weighted_methods:
                    g_weights = f.weights(weights, scale=True, components=True)
                    if not g_weights:
                        g_weights = None
                #--- End: if

                f = f._grouped_collapse(method, collapse_axes[0],
                                        within=within,
                                        over=over,
                                        within_days=within_days,
                                        within_years=within_years,
                                        over_days=over_days,
                                        over_years=over_years,
                                        group=group,
                                        regroup=regroup,
                                        mtol=mtol,
                                        ddof=ddof,
                                        weights=g_weights,
                                        a=a,
                                        squeeze=squeeze,
                                        coordinate=coordinate,
                                        group_by=group_by)

                continue
            elif regroup:
                raise ValueError(
                    "Can't return n array of groups for a non-grouped collapse")

#            method = _collapse_methods.get(method, None)
#            if method is None:
#                raise ValueError("uih luh hbblui")
#
#            # Check that there are enough elements to collapse
#            size = reduce(operator_mul, domain.axes_sizes(collapse_axes).values())
#            min_size = _collapse_min_size.get(method, 1)
#            if size < min_size:
#                raise ValueError(
#                    "Can't calculate %s from fewer than %d elements" %
#                    (_collapse_cell_methods[method], min_size))
    
            data_axes = domain.data_axes()
            iaxes = [data_axes.index(axis) for axis in collapse_axes]

            # ------------------------------------------------------------
            # Calculate weights
            # ------------------------------------------------------------
            d_kwargs = {}
            if weights is not None:
                if method in _collapse_weighted_methods:
                    d_weights = f.weights(weights, scale=True, components=True)
                    if d_weights:
                        d_kwargs['weights'] = d_weights
                elif not equals(weights, 'auto'):  # doc this
                    raise ValueError(
"Can't collapse: Can't weight {0!r} collapse method".format(method))
            #--- End: if

            if method in _collapse_ddof_methods:
                d_kwargs['ddof'] = ddof
                d_kwargs['a']    = a

            # --------------------------------------------------------
            # Collapse the data array
            # --------------------------------------------------------
            getattr(f.Data, method)(axes=iaxes, squeeze=squeeze, mtol=mtol,
                                    i=True, **d_kwargs)
        
            if squeeze:
                # ----------------------------------------------------
                # Remove the collapsed axes from the field's list of
                # data array axes
                # ----------------------------------------------------
                domain._axes['data'] = [axis for axis in data_axes
                                        if axis not in collapse_axes]
        
            # --------------------------------------------------------
            # Update ancillary variables
            # --------------------------------------------------------
            f._conform_ancillary_variables(collapse_axes)
    
            # ------------------------------------------------------------
            # Update fields in coordinate references
            # ------------------------------------------------------------
            f._conform_ref_fields(collapse_axes)
                    
            #---------------------------------------------------------
            # Update dimension coordinates, auxiliary coordinates and
            # cell measures
            # ---------------------------------------------------------
            for axis in collapse_axes:
                # Ignore axes which are already size 1
                if domain.axis_size(axis) == 1:
                    continue
                
                # REMOVE all cell measures which span this axis
                domain.remove_items(role=('m',), axes=axis)
    
                # REMOVE all 2+ dimensional auxiliary coordinates
                # which span this axis
                domain.remove_items(role=('a',), axes=axis, ndim=gt(1))
                    
                # REMOVE all 1 dimensional auxiliary coordinates which
                # span this axis and have different values in their
                # data array and bounds.
                #
                # KEEP, after changing their data arrays, all 1
                # dimensional auxiliary coordinates which span this
                # axis and have the same values in their data array
                # and bounds.    
                for key, aux in domain.items(role=('a',), axes=axis, ndim=1).iteritems():
                    d = aux.subspace[0]

                    if ((aux.subspace[:-1] != aux.subspace[1:]).any() or 
                        aux.hasbounds and (aux.bounds != d.bounds).any()):
                        domain.remove_item(key)
                    else:
                        # Change the data array for this auxiliary
                        # coordinate
                        aux.insert_data(d.data, copy=False)
                        if d.hasbounds:
                            aux.insert_bounds(d.bounds.data, copy=False)
                #--- End: for

                dim_coord = domain.item(axis, role=('d',))
                if dim_coord is None:
                    continue
        
                # Create a new dimension coordinate for this axis
                if dim_coord.hasbounds:
                    bounds = [dim_coord.bounds.datum(0),
                              dim_coord.bounds.datum(-1)]
                else:
                    bounds = [dim_coord.datum(0),
                              dim_coord.datum(-1)]

                units = dim_coord.Units

                if coordinate == 'mid_range':
                    data = Data([(bounds[0] + bounds[1])*0.5], units)
                elif coordinate == 'min':
                    data = dim_coord.data.min()
                elif coordinate == 'max':
                    data = dim_coord.data.max()
                else:
                    raise ValueError(
"Can't collapse: Bad parameter value: coordinate={0!r}".format(coordinate))

                bounds = Data([bounds], units)

                dim_coord.insert_data(data, bounds=bounds, copy=False)
        
                # Put the new dimension coordinate into the domain
                domain.insert_axis(1, key=axis, replace=True)
                domain.insert_dim(dim_coord, key=axis, copy=False, replace=True)
            #--- End: for
        
            # --------------------------------------------------------
            # Update the cell methods
            # --------------------------------------------------------
            cell_method = _collapse_cell_methods[method]
            if cell_method is not None:
                # This collapse method has an associated cell method
                if not hasattr(f, 'cell_methods'):
                    f.cell_methods = CellMethods()
    
                collapse_axes = sorted(collapse_axes)
                
                name = []
                for axis in collapse_axes:
                    item = domain.item(axis)
                    if item is not None:
                        name.append(item.identity(default=axis))
                    else:
                        name.append(axis)
                #--- End: for
                        
                string = '%s: %s' % (': '.join(name), cell_method)           
                cell_method = CellMethods(string)        
                cell_method.axes = collapse_axes

                if not f.cell_methods or not f.cell_methods[-1].equivalent(cell_method):
                    f.cell_methods += cell_method
            #--- End: if

        #--- End: for

        # ------------------------------------------------------------
        # Return the collapsed field (or the classification array)
        # ------------------------------------------------------------
        return f
    #--- End: def

    def _grouped_collapse(self, method, axis, within=None, over=None,
                          within_days=None, within_years=None,
                          over_days=None, over_years=None, group=None,
                          mtol=None, ddof=None, a=None, regroup=None,
                          coordinate=None, weights=None,
                          squeeze=None, group_by=None):
        '''
:Parameters:

    method : str

    axis : str

    over : str

    within : str


'''
        def _ddddd(classification, n, lower, upper, increasing, coord,
                   group_by_coords, extra_condition): 
            '''
    :Returns:

        out : (numpy.ndarray, int, date-time, date-time)

    '''         
            if group_by_coords:
                q = ge(lower) & lt(upper)
            else:
                q = (ge(lower, attr='lower_bounds') & 
                     le(upper, attr='upper_bounds'))
                
            if extra_condition:
                q &= extra_condition

            index = q.evaluate(coord).array
            classification[index] = n

            if increasing:
                lower = upper 
            else:
                upper = lower

            n += 1

            return classification, n, lower, upper
        #--- End: def

        def _time_interval(classification, n,
                           coord, interval,
                           lower, upper,
                           lower_limit, upper_limit,
                           group_by,
                           extra_condition=None):
            '''
    :Returns:

        out : 2-tuple of numpy array, int

    '''            
            group_by_coords = group_by == 'coords'

            months  = interval.Units == Units('calendar_months')
            years   = interval.Units == Units('calendar_years')
            days    = interval.Units == Units('days')
            hours   = interval.Units == Units('hours')
            minutes = interval.Units == Units('minutes')
            seconds = interval.Units == Units('seconds')

            calendar = coord.Units._calendar
                
            if coord.increasing:
                # Increasing dimension coordinate 
                if months or years:
                    lower, upper = interval.interval(lower.year,
                                                     calendar=calendar,
                                                     end=True)
                elif days:
                    lower, upper = interval.interval(lower.year,
                                                     lower.month,
                                                     calendar=calendar,
                                                     end=True)
                elif hours:
                    lower, upper = interval.interval(lower.year,
                                                     lower.month,
                                                     lower.day,
                                                     calendar=calendar,
                                                     end=True)

                elif minutes:
                    lower, upper = interval.interval(lower.year,
                                                     lower.month,
                                                     lower.day,
                                                     lower.hour,
                                                     calendar=calendar,
                                                     end=True)

                elif seconds:
                    lower, upper = interval.interval(lower.year,
                                                     lower.month,
                                                     lower.day,
                                                     lower.hour,
                                                     lower.minute,
                                                     calendar=calendar,
                                                     end=True)

                while lower <= upper_limit:
                    lower, upper = interval.interval(*lower.timetuple()[:6],
                                                      calendar=calendar)
                    classification, n, lower, upper = _ddddd(
                        classification, n, lower, upper, True,
                        coord, group_by_coords, extra_condition)
            else: 
                # Decreasing dimension coordinate
                if months or years:
                    lower, upper = interval.interval(upper.year,
                                                     calendar=calendar)
                elif days:
                    lower, upper = interval.interval(upper.year,
                                                     upper.month,
                                                     calendar=calendar)
                elif hours:
                    lower, upper = interval.interval(upper.year,
                                                     upper.month,
                                                     upper.day,
                                                     calendar=calendar)

                elif minutes:
                    lower, upper = interval.interval(upper.year,
                                                     upper.month,
                                                     upper.day,
                                                     upper.hour,
                                                     calendar=calendar)

                elif seconds:
                    lower, upper = interval.interval(upper.year,
                                                     upper.month,
                                                     upper.day,
                                                     upper.hour,
                                                     upper.minute,
                                                     calendar=calendar)

                while upper >= lower_limit:
                    lower, upper = interval.interval(*upper.timetuple()[:6],
                                                      calendar=calendar, end=True)
                    classification, n, lower, upper = _ddddd(
                        classification, n, lower, upper, False,
                        coord, group_by_coords, extra_condition)
            #--- End: if
                        
            return classification, n
        #--- End: def

        def _data_interval(classification, n,
                           coord, interval,
                           lower, upper,
                           lower_limit, upper_limit,
                           group_by,
                           extra_condition=None):
            '''
    :Returns:

        out : 2-tuple of numpy array, int

    '''          
            group_by_coords = group_by == 'coords'

            if coord.increasing:
                # Increasing dimension coordinate 
                lower= lower.squeeze()
                while lower <= upper_limit:
                    upper = lower + interval 
                    classification, n, lower, upper = _ddddd(
                        classification, n, lower, upper, True,
                        coord, group_by_coords, extra_condition)
            else: 
                # Decreasing dimension coordinate
                upper = upper.squeeze()
                while upper >= lower_limit:
                    lower = upper - interval
                    classification, n, lower, upper = _ddddd(
                        classification, n, lower, upper, False,
                        coord, group_by_coords, extra_condition)
            #--- End: if
                        
            return classification, n
        #--- End: def

        def _selection(classification, n, coord, selection, parameter,
                       extra_condition=None):
            '''

    :Parameters:

        classification : numpy.ndarray

        n : int
        
        coord : cf.DimensionCoordinate

        selection : sequence of cf.Query

        parameter : str
            The name of the `cf.collapse` parameter which defined
            *selection*. This is used in error messages.

        extra_condition : cf.Query, optional

    :Returns:

        out : (numpy.ndarray, int)

    '''        
            # Create an iterator for stepping through each cf.Query
            try:
                iterator = iter(selection)
            except TypeError:
                raise ValueError(
                    "Can't collapse: Bad value for {0} parameter: {1!r}".format(
                        parameter, selection))
            
            for c in iterator:
                if not isinstance(c, Query):
                    raise ValueError(
"Can't collapse: {0} parameter contains a non-{1} object: {2!r}".format(
    parameter, Query.__name__, c))
                                
                if extra_condition:
                    c &= extra_condition

                index = c.evaluate(coord).array

                classification[index] = n

                n += 1
            #--- End: for

            return classification, n
        #--- End: def
        
        def _discern_runs(classification):
            '''
    :Returns:

        out : numpy array

    '''            
            x =  numpy_where(numpy_diff(classification))[0] + 1

            if not x.size:
                if classification[0] >= 0:
                    classification[:] = 0
                return classification           

            if classification[0] >= 0:
                classification[0:x[0]] = 0

            for n, (i, j) in enumerate(zip(x[:-1], x[1:])):
                if classification[i] >= 0:
                    classification[i:j] = n+1
            #-- End: for

            if classification[x[-1]] >= 0:
                classification[x[-1]:] = n+2

            return classification
        #--- End: def

        def _tyu(coord, group_by, time_interval):
            '''
'''
            if coord.hasbounds:
                bounds = coord.bounds                       
                lower_bounds = bounds.lower_bounds
                upper_bounds = bounds.upper_bounds               
                lower = lower_bounds[0]
                upper = upper_bounds[0]
                lower_limit = lower_bounds[-1]
                upper_limit = upper_bounds[-1]
            elif group_by == 'coords':
                if coord.increasing:
                    lower = coord.data[0]
                    upper = coord.data[-1]
                else:
                    lower = coord.data[-1]
                    upper = coord.data[0]
                    
                lower_limit = lower
                upper_limit = upper
            else:
                raise ValueError(
"Can't collapse: %r coordinate bounds are required with group_by=%r" %
(coord.name(''), group_by))
                
            if time_interval:
                units = coord.Units
                if units.isreftime:
                    lower       = lower.dtarray[0]
                    upper       = upper.dtarray[0]
                    lower_limit = lower_limit.dtarray[0]
                    upper_limit = upper_limit.dtarray[0]
                elif not units.istime:
                    raise ValueError(
                        "Can't group by %s when coordinates have units %r" %
                        (TimeDuration.__name__, coord.Units))
            #--- End: if

            return lower, upper, lower_limit, upper_limit
        #--- End: def
    
        def _group_weights(weights, iaxis, index):
            '''
            
Subspace weights components.

    :Parameters:

        weights : dict or None

        iaxis : int

        index : list

    :Returns:

        out : dict or None

    :Examples: 

    >>> print weights
    None
    >>> print _group_weights(weights, 2, [2, 3, 40])
    None
    >>> print _group_weights(weights, 1, slice(2, 56))    
    None

    >>> weights
    
    >>> _group_weights(weights, 2, [2, 3, 40])
    
    >>> _group_weights(weights, 1, slice(2, 56))    


    '''
            if not isinstance(weights, dict):
                return weights

            weights = weights.copy()
            for iaxes, value in weights.iteritems():
                if iaxis in iaxes:
                    indices = [slice(None)] * len(iaxes)
                    indices[iaxes.index(iaxis)] = index
                    weights[iaxes] = value.subspace[tuple(indices)]
                    break
            #--- End: for

            return weights
        #--- End: def

        # START OF MAIN CODE        

        axis_size = self.domain.axis_size(axis)  # Size of uncollapsed axis
        iaxis     = self.data_axes().index(axis) # Integer position of collapse axis

        fl = []

        # If group, rolling window, classification, etc, do something
        # special for size one axes - either return unchanged
        # (possibly mofiying cell methods with , e.g, within_dyas', or
        # raising an exception for 'can't match', I suppose.

        classification = None

        if group is not None:
            if within is not None or over is not None:
                raise ValueError(
                    "Can't set group parameter for a climatological time collapse")

            if isinstance(group, numpy_ndarray):
                classification = numpy_squeeze(group.copy())
                coord = self.dim(axis)

                if classification.dtype.kind != 'i':
                    raise ValueError(
                        "Can't collapse: Can't group by numpy array of type %s" %
                        classification.dtype.name)
                elif classification.shape != (axis_size,):
                    raise ValueError(
"Can't collapse: group by numpy array of integers has incorrect shape: %s" %
classification.shape)

                # Set group to None
                group = None
        #-- End: if

        if group is not None:
            if isinstance(group, Query):
                group = (group,)

            if isinstance(group, (int, long)):
                # ----------------------------------------------------
                # E.g. group=3
                # ----------------------------------------------------
                coord = None
                classification = numpy_empty((axis_size,), int)
                
                start = 0
                end   = group
                n = 0
                while start < axis_size:
                    classification[start:end] = n
                    start = end
                    end  += group
                    n += 1
                #--- End: while

            elif isinstance(group, TimeDuration):
                # ----------------------------------------------------
                # E.g. group=cf.M()
                # ----------------------------------------------------
                coord = self.dim(axis)
                if coord is None:
                    raise ValueError("dddddd siduhfsuildfhsuil dhfdui ") 
                 
#                # Get the bounds
#                if not coord.hasbounds:
#                    coord = coord.copy()
#
#                bounds = coord.get_bounds(create=True, insert=True)
    
                classification = numpy_empty((axis_size,), int)
                classification.fill(-1)

                lower, upper, lower_limit, upper_limit = _tyu(coord, group_by, True)

                classification, n = _time_interval(classification, 0,
                                                   coord=coord,
                                                   interval=group,
                                                   lower=lower,
                                                   upper=upper,
                                                   lower_limit=lower_limit,
                                                   upper_limit=upper_limit,
                                                   group_by=group_by)
            elif isinstance(group, Data):
                # ----------------------------------------------------
                # Chunks of 
                # ----------------------------------------------------
                coord = self.dim(axis)
                if coord is None:
                    raise ValueError("dddddd siduhfsuildfhsuil dhfdui ") 
                if group.size != 1:
                    raise ValueError(
                        "Can't group by SIZE > 1")                    
                if group.Units and not group.Units.equivalent(coord.Units):
                    raise ValueError(
                        "Can't group by %r when coordinates have units %r" %
                        (interval, coord.Units))

                classification = numpy_empty((axis_size,), int)
                classification.fill(-1)

                group = group.squeeze()
  
                lower, upper, lower_limit, upper_limit = _tyu(coord, group_by, False)

                classification, n = _data_interval(classification, 0,
                                                   coord=coord,
                                                   interval=group,
                                                   lower=lower,
                                                   upper=upper,
                                                   lower_limit=lower_limit,
                                                   upper_limit=upper_limit,
                                                   group_by=group_by)
            else:
                # ----------------------------------------------------
                # E.g. group=[cf.month(4), cf.month(cf.wi(9, 11))]
                # ----------------------------------------------------
                coord = self.dim(axis)
                if coord is None:
                    coord = self.aux(axes_all=axis)
                    if coord is None:
                        raise ValueError("Need a defining 1-d coordinate")

                classification = numpy_empty((axis_size,), int)
                classification.fill(-1)
                
                classification, n = _selection(classification, 
                                               n=0,
                                               coord=coord,
                                               selection=group,
                                               parameter='group')
                
                classification = _discern_runs(classification)
            #--- End: if
        #--- End: if

        if classification is None:
            if over == 'days': 
                # ----------------------------------------------------
                # Over days
                # ----------------------------------------------------
                coord = self.dim(axis)
                if coord is None or not coord.Units.isreftime:
                    raise ValueError(
"Can't collapse: Reference-time dimension coordinates are required for an \"over days\" collapse")
                if not coord.hasbounds:
                    raise ValueError(
"Can't collapse: Reference-time dimension coordinate bounds are required for an \"over days\" collapse")

                cell_methods = getattr(self, 'cell_methods', None)
                if not cell_methods or 'days' not in cell_methods.within:
                    raise ValueError(
"Can't collapse: An \"over days\" collapse must come after a \"within days\" collapse")

                # Parse the over_days parameter
                if isinstance(over_days, Query):
                    over_days = (over_days,)              
                elif isinstance(over_days, TimeDuration):
                    if over_days.Units.istime and over_days < Data(1, 'day'):
                        raise ValueError(
                            "Can't collapse: Bad parameter value: over_days=%r" %
                            over_days)
                #--- End: if

                coordinate = 'min'
                
                classification = numpy_empty((axis_size,), int)
                classification.fill(-1)
                
                if isinstance(over_days, TimeDuration):
                    lower, upper, lower_limit, upper_limit = _tyu(coord, group_by, True)

                bounds = coord.bounds
                lower_bounds = bounds.lower_bounds.dtarray
                upper_bounds = bounds.upper_bounds.dtarray

                HMS0 = None

#            * An "over days" collapse must be preceded by a "within
#              days" collapse, as described by the CF conventions. If the
#              field already contains sub-daily data, but does not have
#              the "within days" cell methods flag then it may be added,
#              for example, as follows (this example assumes that the
#              appropriate cell method is the most recently applied,
#              which need not be the case; see `cf.CellMethods` for
#              details):
#            
#              >>> f.cell_methods[-1].within = 'days'

                n = 0
                for lower, upper in izip(lower_bounds, upper_bounds):
                    HMS_l = (eq(lower.hour  , attr='hour') & 
                             eq(lower.minute, attr='minute') & 
                             eq(lower.second, attr='second')).addattr('lower_bounds')
                    HMS_u = (eq(upper.hour  , attr='hour') & 
                             eq(upper.minute, attr='minute') & 
                             eq(upper.second, attr='second')).addattr('upper_bounds')
                    HMS = HMS_l & HMS_u

                    if not HMS0:
                        HMS0 = HMS
                    elif HMS.equals(HMS0):
                        break

                    if over_days is None:
                        # --------------------------------------------
                        # over_days=None
                        # --------------------------------------------
                        # Over all days
                        index = HMS.evaluate(coord).array
                        classification[index] = n
                        n += 1         
                    elif isinstance(over_days, TimeDuration):
                        # --------------------------------------------
                        # E.g. over_days=cf.M()
                        # --------------------------------------------
                        classification, n = _time_interval(classification, n,
                                                           coord=coord,
                                                           interval=over_days,
                                                           lower=lower,
                                                           upper=upper,
                                                           lower_limit=lower_limit,
                                                           upper_limit=upper_limit,
                                                           group_by=group_by,
                                                           extra_condition=HMS)
                    else:
                        # --------------------------------------------
                        # E.g. over_days=[cf.month(cf.wi(4, 9))]
                        # --------------------------------------------
                        classification, n = _selection(classification, n,
                                                       coord=coord,
                                                       selection=over_days,
                                                       parameter='over_days',
                                                       extra_condition=HMS)
                        
            elif over == 'years':
                # ----------------------------------------------------
                # Over years
                # ----------------------------------------------------
                coord = self.dim(axis)
                if coord is None or not coord.Units.isreftime:
                    raise ValueError(
"Can't collapse: Reference-time dimension coordinates are required for an \"over years\" collapse")
                if not coord.hasbounds:
                    raise ValueError(
"Can't collapse: Reference-time dimension coordinate bounds are required for an \"over years\" collapse")

                cell_methods = getattr(self, 'cell_methods', None)
                if (not cell_methods or ('years' not in cell_methods.within and
                                         'days'  not in cell_methods.over)):
                    raise ValueError(
"Can't collapse: An \"over years\" collapse must come after a \"within years\" or \"over days\" collapse")

                # Parse the over_years parameter
                if isinstance(over_years, Query):
                    over_years = (over_years,)
                elif isinstance(over_years, TimeDuration):
                    if over_years.Units.iscalendartime:
                        over_years.Units = Units('calendar_years')
                        if not over_years.isint or over_years < 1:
                            raise ValueError(
"Can't collapse: over_years is not a whole number of calendar years: %r" % over_years)
                    else:
                        raise ValueError(
"Can't collapse: over_years is not a whole number of calendar years: %r" % over_years)
                #--- End: if
                
                coordinate = 'min'
                
                classification = numpy_empty((axis_size,), int)
                classification.fill(-1)
                
                if isinstance(over_years, TimeDuration):
                    lower, upper, lower_limit, upper_limit = _tyu(coord, group_by, True)

#                if coord.increasing:
#                    bounds_max = upper_bounds[-1]
#                else:
#                    bounds_min = lower_bounds[-1]
                 
                bounds = coord.bounds
                lower_bounds = bounds.lower_bounds.dtarray
                upper_bounds = bounds.upper_bounds.dtarray
                mdHMS0 = None
                    
                n = 0
                for lower, upper in izip(lower_bounds, upper_bounds):
                    mdHMS_l = (eq(lower.month , attr='month') & 
                               eq(lower.day   , attr='day') & 
                               eq(lower.hour  , attr='hour') & 
                               eq(lower.minute, attr='minute') & 
                               eq(lower.second, attr='second')).addattr('lower_bounds')
                    mdHMS_u = (eq(upper.month , attr='month') & 
                               eq(upper.day   , attr='day') & 
                               eq(upper.hour  , attr='hour') & 
                               eq(upper.minute, attr='minute') & 
                               eq(upper.second, attr='second')).addattr('upper_bounds')
                    mdHMS = mdHMS_l & mdHMS_u
                    if not mdHMS0:
                        mdHMS0 = mdHMS                        
                    elif mdHMS.equals(mdHMS0):
                        break
            
                    if over_years is None:
                        # --------------------------------------------
                        # E.g. over_years=None
                        # --------------------------------------------
                        # Over all years
                        index = mdHMS.evaluate(coord).array
                        classification[index] = n
                        n += 1
                    elif isinstance(over_years, TimeDuration):
                        # --------------------------------------------
                        # E.g. over_years=cf.Y(2)
                        # --------------------------------------------
#                        lower_bounds = bounds.lower_bounds
#                        upper_bounds = bounds.upper_bounds               
#                        
#                        lower = lower_bounds[0].dtarray[0]
#                        upper = upper_bounds[0].dtarray[0]
#                        bounds_min = lower_bounds[-1].dtarray[0]
#                        bounds_max = upper_bounds[-1].dtarray[0]

                        classification, n = _time_interval(classification, n,
                                                           coord=coord,
                                                           interval=over_years,
                                                           lower=lower,
                                                           upper=upper,
                                                           lower_limit=lower_limit,
                                                           upper_limit=upper_limit,
                                                           group_by=group_by,
                                                           extra_condition=mdHMS)
                    else:
                        # --------------------------------------------
                        # E.g. over_years=cf.year(cf.lt(2000))
                        # --------------------------------------------
                        classification, n = _selection(classification, n,
                                                       coord=coord,
                                                       selection=over_years,
                                                       parameter='over_years',
                                                       extra_condition=mdHMS)
                #--- End: for
    
            elif within == 'days':
                # ----------------------------------------------------
                # Within days
                # ----------------------------------------------------
                coord = self.dim(axis)
                if coord is None or not coord.Units.isreftime:
                    raise ValueError(
"Can't collapse: Reference-time dimension coordinates are required for an \"over years\" collapse")

#                # Get the bounds
#                if not coord.hasbounds:
#                    coord = coord.copy()
#
#                bounds = coord.get_bounds(create=True, insert=True)
    
                classification = numpy_empty((axis_size,), int)
                classification.fill(-1)
    
                # Parse the within_days parameter
                if isinstance(within_days, Query):
                    within_days = (within_days,)
                elif isinstance(within_days, TimeDuration):
                    if within_days.Units.istime and Data(1, 'day') % within_days:
                        raise ValueError(
"Can't collapse: within_days is not a factor of 1 day: %r" %
within_days)
                #--- End: if
                    
                if isinstance(within_days, TimeDuration):
                    # ------------------------------------------------
                    # E.g. within_days=cf.h(6)
                    # ------------------------------------------------ 
                    lower, upper, lower_limit, upper_limit = _tyu(coord, group_by, True)
                        
                    classification, n = _time_interval(classification, 0,
                                                       coord=coord,
                                                       interval=within_days,
                                                       lower=lower,
                                                       upper=upper,
                                                       lower_limit=lower_limit,
                                                       upper_limit=upper_limit,
                                                       group_by=group_by)
                else:
                    # ------------------------------------------------
                    # E.g. within_days=cf.hour(cf.lt(12))
                    # ------------------------------------------------
                    classification, n = _selection(classification, 0,
                                                   coord=coord,
                                                   selection=within_days,
                                                   parameter='within_days') 
                    
                    classification = _discern_runs(classification)
                           
            elif within == 'years':
                # ----------------------------------------------------
                # Within years
                # ----------------------------------------------------
                coord = self.dim(axis)
                if coord is None or not coord.Units.isreftime:
                    raise ValueError(
"Can't collapse: Reference-time dimension coordinates are required for an \"over years\" collapse")

#                # Get the bounds
#                if not coord.hasbounds:
#                    coord = coord.copy()
#
#                bounds = coord.get_bounds(create=True, insert=True)
    
                classification = numpy_empty((axis_size,), int)
                classification.fill(-1)

                # Parse within_years
                if isinstance(within_years, Query):
                    over_years = (within_years,)               
                elif within_years is None:
                    raise ValueError(
                        "Can't collapse: Bad parameter value: within_years=%r" %
                        within_years)
                  
                if isinstance(within_years, TimeDuration):
                    # ------------------------------------------------
                    # E.g. within_years=cf.M()
                    # ------------------------------------------------
                    lower, upper, lower_limit, upper_limit = _tyu(coord, group_by, True)
                        
                    classification, n = _time_interval(classification, 0,
                                                       coord=coord,
                                                       interval=within_years,
                                                       lower=lower,
                                                       upper=upper,
                                                       lower_limit=lower_limit,
                                                       upper_limit=upper_limit,
                                                       group_by=group_by)
                else:
                    # ------------------------------------------------
                    # E.g. within_years=cf.season()
                    # ------------------------------------------------
                    classification, n = _selection(classification, 0,
                                                   coord=coord,
                                                   selection=within_years,
                                                   parameter='within_years')
                    
                    classification = _discern_runs(classification)

            elif over is not None:
                raise ValueError(
                    "Can't collapse: Bad 'over' syntax: {0!r}".format(over))
                
            elif within is not None: 
                raise ValueError(
                    "Can't collapse: Bad 'within' syntax: {0!r}".format(within))
            #--- End: if
        #--- End: if
                 
        if classification is not None:
            if regroup:
                return classification

            #---------------------------------------------------------
            # Collapse each group
            #---------------------------------------------------------            
            unique = numpy_unique(classification)
            unique = unique[numpy_where(unique >= 0)[0]]
            unique.sort()

            for u in unique:
                index = numpy_where(classification==u)[0].tolist()

                pc = self.subspace(**{axis: index})

                w = _group_weights(weights, iaxis, index)
                     
                fl.append(pc.collapse(method, axis, weights=w,
                                      mtol=mtol, a=a, ddof=ddof,
                                      coordinate=coordinate, squeeze=False,
                                      i=True))
            #--- End: for
        elif regroup:
            raise ValueError("Can't return classification 2453456 ")

        if not fl:
            raise ValueError(
                "Can't do grouped collapse: No groups were identified")
            
        if len(fl) == 1:
            f = fl[0]
        else:
            #---------------------------------------------------------
            # Sort the list of collapsed fields
            #---------------------------------------------------------
            if coord is not None and coord.isdimension:
                fl.sort(key=lambda g: g.dim(axis).datum(0),
                        reverse=coord.decreasing)
                
            #---------------------------------------------------------
            # Concatenate the partial collapses
            # --------------------------------------------------------
            try:
                f = self.concatenate(fl, axis=iaxis, _preserve=False)
            except ValueError as error:
                raise ValueError("Can't collapse: %s" % error)
        #--- End: if
                      
        # --------------------------------------------------------
        # Update the cell methods
        # --------------------------------------------------------
        if within or over:
            cell_methods = getattr(f, 'cell_methods', None)
            if cell_methods is None:                                                   
                # The input field has no cell methods so create one                    
                name = f.axis_name(axis)                                               
                if within:                                                             
                    c = CellMethods("{0}: {1} within {2}".format(name, method, within))
                else:                                                                  
                    c = CellMethods("{0}: {1} over {2}".format(name, method, over))    
                c.axes = (axis,)                                                       
                f.cell_methods = c                                                     
            else:                                                                      
                lastcm = cell_methods[-1]
                if (_collapse_cell_methods.get(lastcm.method[0], None) == _collapse_cell_methods.get(method, None)  and
                    lastcm.axes   == ((axis,),) and
                    lastcm.within == (None,)    and
                    lastcm.over   == (None,)
                    ):
                    if within:
                        lastcm.within = within
                    else:
                        lastcm.over = over
        #--- End: if
  
        if squeeze and f.axis_size(axis) == 1:
            # Remove a totally collapsed axis from the field's
            # data array
            f.squeeze(axis, i=True)

        # ------------------------------------------------------------
        # Return the collapsed field
        # ------------------------------------------------------------
        self.__dict__ = f.__dict__
        return self
    #--- End: def

    def _conform_ancillary_variables(self, axes, keep_size_1=False):
        '''

Remove ancillary variable fields which span the given axes.

.. versionadded:: 1.0

.. seealso:: `_conform_ref_fields`

:Parameters:

    axes : sequence of str
        Sequence of domain axis identifiers.

    keep_size_1 : bool, optional

:Returns:

    out : None

:Examples:

>>> f._conform_ancillary_variables(['dim2', 'dim1'])
>>> f._conform_ancillary_variables(['dim2'])
>>> f._conform_ancillary_variables([])

'''
        ancillary_variables = getattr(self, 'ancillary_variables', None)        
        if not ancillary_variables:
            return self

        new_av = []
        
        if keep_size_1:
            size = gt(1)
        else:
            size = None

        self_domain = self.domain
            
        for av in ancillary_variables:
            axis_map = av.domain.map_axes(self_domain)

            keep = True
            for av_axis in av.axes(size=size):
                if av_axis not in axis_map or axis_map[av_axis] in axes:
                    # Don't keep this ancillary variable field because
                    # either it has an axis which doesn't match any
                    # axis in the parent field or it has an axis which
                    # matches one of the given axes.
                    keep = False
                    break
            #--- End: for
            if keep:
                new_av.append(av)
        #--- End: for

        if new_av:
            self.ancillary_variables = FieldList(new_av)
        else:
            del self.ancillary_variables 
    #--- End: def
    
    def _conform_ref_fields(self, axes, keep_size_1=False):
        '''

Remove fields in coordinate reference objects which span the given
axes.

.. seealso:: `_conform_ancillary_variables`

:Parameters:

    axes : sequence of str
        Sequence of domain axis identifiers.

    keep_size_1 : bool, optional

:Returns:

    out : None

:Examples:

>>> f._conform_ref_fields(['dim2', 'dim1'])
>>> f._conform_ref_fields(['dim2'])
>>> f._conform_ref_fields([])

'''       
        if keep_size_1:
            size = gt(1)
        else:
            size = None

        self_domain = self.domain
            
        for ref in self.refs().itervalues():
            for term, value in ref.iteritems():
                if not isinstance(value, Field):
                    # Keep the term because it's not a field
                    continue 
    
                axis_map = value.domain.map_axes(self_domain)
                for axis in value.axes(size=size):
                    if axis not in axis_map or axis_map[axis] in axes:
                        # Don't keep this coordinate reference field
                        # because either it has an axis which doesn't
                        # match any axis in the parent field or it has
                        # an axis which matches one of the given axes.
                        ref[term] = None
                        break
                #--- End: for
            #--- End: for
    #--- End: def
        
    def data_axes(self):
        '''Return the domain axis identifiers for the data array dimensions.

.. seealso:: `axes`, `axis`, `item_axes`

:Examples 1:

>>> d = f.data_axes()

:Returns:

[+1]    out : list or None
        The ordered axes of the data array. If there is no data array
        then `None` is returned.

:Examples 2:

>>> f.ndim
3
>>> f.data_axes()
['dim2', 'dim0', 'dim1']
>>> del f.Data
>>> print f.data_axes()
None

>>> f.ndim
0
>>> f.data_axes()
[]

        '''    
        if not self._hasData:
            return None

        return self.domain.data_axes()
    #--- End: def

    def dump(self, complete=False, display=True,
             _level=0, _title='Field', _q='='):
        '''{+Fef,}Print or return a string containing a description of the field.

By default, the description is given without abbreviation with the
exception of data arrays (which are abbreviated to their first and
last values) and fields contained in coordinate references and
ancillary variables (which are given as one-line summaries).

:Examples 1:
        
>>> f.dump()

:Parameters:
 
    complete : bool, optional
        Output a complete dump. Fields contained in coordinate references and
        ancillary variables are themselves described with their dumps.

    display : bool, optional
        If False then{+,fef,} return the description as a string. By default
        the description is printed.

          *Example:*
[+1]            ``f.dump()`` is equivalent to ``print
[+1]            f.dump(display=False)``.
[+N]            ``f.dump()`` is equivalent to ``for g in f: print
[+N]            g.dump(display=False)``.

:Returns:

[+1]    out : None or str
[+1]        If *display* is False then the description is printed and
[+1]        `None` is returned. Otherwise the description is restured as a
[+1]        string.
[+N]    out : None or list
[+N]        If *display* is False then{+,fef,} the description is printed
[+N]        and `None` is returned. Otherwise a list of strings containing
[+N]        the description for each field is returned.

        '''
        # List functionality
        if self._list:
            kwargs2 = self._parameters(locals())
            if display:
                for f in self:
                    f.dump(**kwargs2)
                return
            else:
                return [f.dump(**kwargs2) for f in self]
        #--- End: if 

        indent = '    '      
        indent0 = indent * _level
        indent1 = indent0 + indent

        domain = self.domain

        title = '%s%s: %s' % (indent0, _title, self.name(''))
        line  = '%s%s'     % (indent0, ''.ljust(len(title)-_level*4, _q))

        # Title
        string = [line, title, line]

        # Axes
        if domain.axes():
            string.extend((domain.dump_axes(display=False, _level=_level), ''))

        # Data
        if self._hasData:
            axis_name = domain.axis_name
            axis_size = domain.axis_size
            x = ['%s(%d)' % (axis_name(axis), axis_size(axis))
                 for axis in domain.data_axes()]
            string.append('%sData(%s) = %s' % (indent0, ', '.join(x),
                                               str(self.Data)))

        # Cell methods
        cell_methods = getattr(self, 'cell_methods', None)
        if cell_methods is not None:            
            string.append('%scell_methods = %s' % (indent0, cell_methods))

        # Simple properties
        if self._simple_properties():
            string.extend(
                ('', self._dump_simple_properties(_level=_level,
                                                  omit=('Conventions',))))
            
        # Flags
        flags = getattr(self, 'Flags', None)
        if flags is not None:            
            string.extend(('', flags.dump(display=False, _level=_level)))

        # Domain
        string.append(domain.dump_components(complete=complete, display=False,
                                             _level=_level))

        # Ancillary variables
        ancillary_variables = getattr(self, 'ancillary_variables', None)
        if ancillary_variables is not None:
            string.extend(('', '%sAncillary variables:' % indent0))
            if not complete:
                x = ['%s%r' % (indent1, f) for f in ancillary_variables]
                string.extend(x)
            else:
                for f in ancillary_variables:
                    string.append(f.dump(display=False, complete=False,
                                         _level=_level+1,
                                         _title='Ancillary field', _q='-'))
        #--- End: if

        string.append('')
        
        string = '\n'.join(string)
       
        if display:
            print string
        else:
            return string
    #--- End: def

    def equals(self, other, rtol=None, atol=None,
               ignore_fill_value=False, traceback=False,
               ignore=('Conventions',), _set=False):
        # Note: map(None, f, g) only works at python 2.x
        '''True if two {+variable}s are equal, False otherwise.

[+N]Two {+variable}s are equal if they have the same number of elements
[+N]and the field elements are equal pairwise, i.e. ``f.equals(g)`` is
[+N]equivalent to ``all(x.equals(y) for x, y in map(None, f, g))``.

Two fields are equal if ...

[+1]Note that a {+variable} may be equal to a single element field list,
[+1]for example ``f.equals(f[0:1])`` and ``f[0:1].equals(f)`` are always
[+1]True.

[+N]Note that a single element {+variable} may be equal to field, for
[+N]example ``f[0:1].equals(f[0])`` and ``f[0].equals(f[0:1])`` are always
[+N]True.

[+1].. seealso:: `cf.FieldList.equals`, `set_equals`
[+N].. seealso:: `cf.Field.equals`, `set_equals`

:Examples 1:

>>> b = f.equals(g)

:Parameters:

    other : object
        The object to compare for equality.

    {+atol}

    {+rtol}

    ignore_fill_value : bool, optional
        If True then data arrays with different fill values are
        considered equal. By default they are considered unequal.

    traceback : bool, optional
        If True then print a traceback highlighting where the two
        {+variable}s differ.

    ignore : tuple, optional
        The names of CF properties to omit from the comparison. By
        default, the CF Conventions property is omitted.

:Returns: 
  
    out : bool
        Whether or not the two {+variable}s are equal.

:Examples 2:

>>> f.Conventions
'CF-1.0'
>>> g = f.copy()
>>> g.Conventions = 'CF-1.5'
>>> f.equals(g)
True

In the following example, two fields differ only by the long name of
their time coordinates. The traceback shows that they differ in their
domains, that they differ in their time coordinates and that the long
name could not be matched.

>>> g = f.copy()
>>> g.coord('time').long_name += ' different'
>>> f.equals(g, traceback=True)
Domain: Different coordinate: <CF Coordinate: time(12)>
Field: Different domain properties: <CF Domain: (128, 1, 12, 64)>, <CF Domain: (128, 1, 12, 64)>
False

        '''
        kwargs2 = self._parameters(locals())
        return super(Field, self).equals(**kwargs2)
    #---End: def

    def equivalent(self, other, rtol=None, atol=None, traceback=False):
        '''

True if two {+variable}s are equivalent, False otherwise

two fields are equivalent if:

  * They have the same identity, as defined by their
    `~cf.Field.identity` methods.

  * The same rank, as given by their `~cf.Field.rank` attributes.

  * Their data arrays are the same after accounting for different but
    equivalent:

    * Units

    * Number of size one dimensions (if *squeeze* is True),
    
    * Dimension directions (if *use_directions* is True) 
    
    * Dimension orders (if *transpose* is set to a dictionary).

  * Both fields' domains must have the same rankdimensionality and where a
    dimension in one field has an identity inferred a 1-d coordinate,
    the other field has a matching dimension whose identity inferred
    is inferred from a 1-d coordinate with an equivalent data array.

    * The rank, as given by their `~cf.Field.rank

[+1].. seealso:: `~cf.Field.equals`, `set_equals`
[+N].. seealso:: `~cf.FieldList.equals`, `set_equals`

:Examples 1:

>>> b = f.equivalent(g)

:Parameters:

    other : object
        The object to compare for equivalence.

    {+atol}

    {+rtol}

    traceback : bool, optional
        If True then print a traceback highlighting where the two
        {+variable}s differ.

:Returns: 

    out : bool
        Whether or not the two {+variable}s are equivalent.
      
:Examples 2:

>>>

'''
        if not self.equivalent_domain(other, rtol=rtol, atol=atol,
                                      traceback=traceback):
            if traceback:
                print("%s: Nonequivalent domains: %r, %r" % 
                      (self.__class__.__name__,
                       self.domain, other.domain))
            return False

        if not self.equivalent_data(other, rtol=rtol, atol=atol,
                                    traceback=False):
            if traceback:
                print("%s: Nonequivalent data arrays: %r, %r" % 
                      (self.__class__.__name__,
                       getattr(self, 'data', None),
                       getattr(other, 'data', None)))
            return False
                
        return True
    #--- End_def

    def equivalent_domain(self, other, rtol=None, atol=None,
                          traceback=False):
        '''

Return True if two fields have equivalent data domains.

:Parameters:

    other : cf.Field

    atol : float, optional
        The absolute tolerance for all numerical comparisons, By
        default the value returned by the `cf.ATOL` function is used.

    rtol : float, optional
        The relative tolerance for all numerical comparisons, By
        default the value returned by the `cf.RTOL` function is used.

    traceback : bool, optional
        If True then print a traceback highlighting where the two
        domains differ.

:Returns:

    out : bool
        Whether or not the two fields' data arrays are equivalent.

:Examples:

>>> f.equivalent_domain(g)

'''
        return self.domain.equivalent(other.domain, rtol=rtol,
                                      atol=atol, traceback=traceback)
    #--- End_def

    def equivalent_data(self, other, rtol=None, atol=None, traceback=False):
        '''

Return True if two fields have equivalent data arrays.

Equivalence is defined as both fields having the same data arrays
after accounting for different but equivalent units, size one
dimensions, different dimension directions and different dimension
orders.

:Parameters:

    other : cf.Field

    atol : float, optional
        The absolute tolerance for all numerical comparisons, By
        default the value returned by the `cf.ATOL` function is used.

    rtol : float, optional
        The relative tolerance for all numerical comparisons, By
        default the value returned by the `cf.RTOL` function is used.

    traceback : bool, optional
        If True then print a traceback highlighting where the two
        data arrays differ.

:Returns:

    out : bool
        Whether or not the two fields' data arrays are equivalent.

:Examples:

>>> f.equivalent_data(g)

'''
        if self._hasData != other._hasData:
            if traceback:
                print("%s: Only one field has data: %s, %s" %
                      (self.__class__.__name__, self._hasData, other._hasData))
            return False
        
        if not self._hasData:
            # Neither field has a data array
            return True

        if self.size != other.size:
            if traceback:
                print("%s: Different data array sizes (%d, %d)" %
                      (self.__class__.__name__, self.size, other.size))
            return False

        s = self.domain.analyse()
        t = other.domain.analyse()

        data0 = self.data
        data1 = other.data
        if 1 in data0._shape:
            data0 = data0.squeeze()
            
        copy = True
        if 1 in data1._shape:
            data1 = data1.squeeze()
            copy = False

        data_axes0 = self.domain.data_axes()
        data_axes1 = other.domain.data_axes()

        transpose_axes = []
        for axis0 in data_axes0:
            axis1 = t['id_to_axis'].get(s['axis_to_id'][axis0], None)
            if axis1 is not None:
                transpose_axes.append(data_axes1.index(axis1))
            else:
                if traceback:
                    print("%s: woooooooooooooooo" % self.__class__.__name__)
                return False
        #--- End: for
       
        if transpose_axes != range(other.ndim):
            if copy:
                data1 = data1.copy()
                copy = False

            data1.transpose(transpose_axes, i=True)
        #--- End: if

        if self.size > 1:            
            self_directions  = self.domain.directions()
            other_directions = other.domain.directions()

            flip_axes = [i for i, (axis1, axis0) in enumerate(izip(data_axes1,
                                                                   data_axes0))
                         if other_directions[axis1] != self_directions[axis0]]
        
            if flip_axes:
                if copy:
                    data1 = data1.copy()                
                    copy = False

                data1.flip(flip_axes, i=True)
        #--- End: if

        return data0.equals(data1, rtol=rtol, atol=atol, ignore_fill_value=True)
    #--- End: def

    def expand_dims(self, position=0, axes=None, i=False, **kwargs):
        '''{+Fef,}Insert a size 1 axis into the data array.

By default default a new size 1 axis is inserted which doesn't yet
exist, but a unique existing size 1 axis which is not already spanned
by the data array may be selected.

.. seealso:: `axes`, `flip`, `squeeze`, `transpose`, `unsqueeze`

:Examples 1:

Insert a new size axis in position 0:

>>> g = f.expand_dims()

Insert  the existing, size 1 time axis in position 2:

>>> g = f.expand_dims(2, axes='T')

:Parameters:

    position : int, optional
        Specify the position that the new axis will have in the data
        array. By default the new axis has position 0, the slowest
        varying position.

    {+axes, kwargs}

    {+i}

:Returns:

    out : cf.{+Variable}
        {+Fef,}, the expanded field.

:Examples 2:

        '''
        # List functionality
        if self._list:
            kwargs2 = self._parameters(locals())
            return self._list_method('expand_dims', kwargs2)

        domain = self.domain

        if axes is None and not kwargs:
            axis = domain.new_axis_identifier()
        else:
            axis = domain.axis(axes, **kwargs)
            if axis is None:
                raise ValueError("Can't identify a unique axis to insert")
            elif domain.axis_size(axis) != 1:
                raise ValueError("Can't insert an axis of size %d: %r" %
                                 (domain.axis_size(axis), axis))
            elif axis in domain.data_axes():
                raise ValueError(
                    "Can't insert a duplicate axis: %r" % axis)
        #--- End: if
       
        # Expand the dims in the field's data array
        f = super(Field, self).expand_dims(position, i=i)

        domain = f.domain
        domain._axes['data'].insert(position, axis)
        domain._axes_sizes[axis] = 1

        return f
    #--- End: def

    def indices(self, *args, **kwargs):
        '''Create data array indices based on domain metadata.

If metadata values are specified for an axis then a full slice
(``slice(None)``) is assumed for that axis.

Values for size 1 axes which are not spanned by the field's data array
may be specified, but only indices for axes which span the field's
data array will be returned.

The coordinate value conditions may be given in any order.

.. seealso:: `where`, `subspace`

:Parameters:

    args : *optional*

        ===========  =================================================
        *arg*        Description
        ===========  =================================================

        ``'exact'`` -Keyword parameter names are not treated as
                     abbreviations of item identities. By default,
                     keyword parameter names are allowed to be
                     abbreviations of item identities.
        ===========  =================================================

    kwargs : *optional*
        Keyword parameters identify items of the domain () and set
        conditions on their data arrays. Indices are created which,
        for each axis, select where the conditions are met.

        A keyword name is a string which selects a unique item of the
        domain. The string may be any string value allowed by *items*
        parameter of the field's `item` method, which is used to
        select a unique domain item. See `cf.Field.item` for details.
        
          *Example:*           
            The keyword ``lat`` will select the item returned by
            ``f.item('lat', role='dam')``. See the *exact* parameter.

        In general, a keyword value specifies a test on the selected
        item's data array which identifies axis elements. The returned
        indices for this axis are the positions of these elements.

          *Example:*
            To create indices for the northern hemisphere, assuming
            that there is a coordinate with identity "latitude":
            ``f.indices(latitude=cf.ge(0))``

          *Example:*
            To create indices for the northern hemisphere, identifying
            the latitude coordinate by its long name:
            ``f.indices(**{'long_name:latitude': cf.ge(0)})``. In this
            case it is necessary to use the ``**`` syntax because the
            ``:`` characeter is not allowed in keyword parameter
            names.

        If the value is a `slice` object then it is used as the axis
        indices, without testing the item's data array.

          *Example:*
            To create indices for every even numbered element along
            the "Z" axis: ``f.indices(Z=slice(0, None, 2))``.


        **Multidimensional items**
          Indices based on items which span two or more axes are
          possible if the result is a single element index for each of
          the axes spanned. In addition, two or more items must be
          provided, each one spanning the same axes  (in any order).

            *Example:*          
              To create indices for the unique location 45 degrees
              north, 30 degrees east when latitude and longitude are
              stored in 2-dimensional auxiliary coordiantes:
              ``f.indices(latitude=45, longitude=30)``. Note that this
              example would also work if latitude and longitude were
              stored in 1-dimensional dimensional or auxiliary
              coordinates, but in this case the location would not
              have to be unique.

    exact : str, *optional*

:Returns:

    out : tuple
        
:Examples:

These examples use the following field, which includes a dimension
coordinate object with no identity (``ncvar:model_level_number``) and
which has a data array which doesn't span all of the domain axes:


>>> print f
eastward_wind field summary
---------------------------
Data           : eastward_wind(time(3), air_pressure(5), grid_latitude(110), grid_longitude(106)) m s-1
Cell methods   : time: mean
Axes           : time(3) = [1979-05-01 12:00:00, ..., 1979-05-03 12:00:00] gregorian
               : air_pressure(5) = [850.0, ..., 50.0] hPa
               : grid_longitude(106) = [-20.54, ..., 25.66] degrees
               : grid_latitude(110) = [23.32, ..., -24.64] degrees
Aux coords     : latitude(grid_latitude(110), grid_longitude(106)) = [[67.12, ..., 22.89]] degrees_N
               : longitude(grid_latitude(110), grid_longitude(106)) = [[-45.98, ..., 35.29]] degrees_E
Coord refs     : <CF CoordinateReference: rotated_latitude_longitude>


>>> f.indices(lat=23.32, lon=-20.54)
(slice(0, 3, 1), slice(0, 5, 1), slice(0, 1, 1), slice(0, 1, 1))

>>> f.indices(grid_lat=slice(50, 2, -2), grid_lon=[0, 1, 3, 90]) 
(slice(0, 3, 1), slice(0, 5, 1), slice(50, 2, -2), [0, 1, 3, 90])

>>> f.indices('exact', grid_latitude=slice(50, 2, -2), grid_longitude=[0, 1, 3, 90]) 
(slice(0, 3, 1), slice(0, 5, 1), slice(50, 2, -2), [0, 1, 3, 90])

>>> f.indices(grid_lon=cf.wi(0, 10, 'degrees'), air_pressure=850)
(slice(0, 3, 1), slice(0, 1, 1), slice(0, 110, 1), slice(47, 70, 1))

>>> f.indices(grid_lon=cf.wi(0, 10), air_pressure=cf.eq(85000, 'Pa')
(slice(0, 3, 1), slice(0, 1, 1), slice(0, 110, 1), slice(47, 70, 1))

>>> f.indices(grid_long=cf.gt(0, attr='lower_bounds'))
(slice(0, 3, 1), slice(0, 5, 1), slice(0, 110, 1), slice(48, 106, 1))

        '''
        exact = 'exact' in args

        domain = self.domain

        data_axes = domain.data_axes()

        # Initialize indices
        indices = [slice(None)] * self.ndim
        
        wee = {}
        unique_axes = set()
        n_axes = 0
        for identity, value in kwargs.iteritems():
            items = domain.items(identity, role=('d', 'a'), exact=exact)
            if len(items) != 1:
                raise ValueError(
                    "Can't find indices: Ambiguous axis or axes: %r" %
                    identity)

            key, coord = items.popitem()
            axes = domain.item_axes(key)
            sorted_axes = tuple(sorted(axes))
            if sorted_axes not in wee:
                n_axes += len(sorted_axes)

            wee.setdefault(sorted_axes, []).append((tuple(axes), coord, value))

            unique_axes.update(sorted_axes)
        #--- End: for

        if len(unique_axes) < n_axes:
            raise ValueError("Ambiguous axis specification")

        for key, axes_coord_value in wee.iteritems():
            axes, coords, point = zip(*axes_coord_value)
                
            n_coords = len(coords)
            n_axes   = len(key)

            if n_coords != n_axes:
                raise IndexError(
"Must specify %d %d-d coordinate objects to find %d-d indices (got %d)" %
(n_axes, n_axes, n_axes, n_coords))
                
            if n_coords == 1:
                #-----------------------------------------------------
                # 1-d coordinate
                #-----------------------------------------------------
                coord = coords[0]
                value = point[0]
                axis  = axes[0][0]    

                if isinstance(value, (slice, list)):
                    # CASE 1: Subspace criterion is already a valid index
                    # (i.e. it is a slice object or a list (of ints, but
                    # this isn't checked for)).
                    index = value
    
                elif (isinstance(value, Query) and 
                    value.operator in ('wi', 'wo') and
                    coord.isdimension and
                    self.iscyclic(key)):
                    # CASE 2: Axis is cyclic and subspace criterion is
                    # a 'within' or 'without' cf.Query instance
                    if coord.increasing:
                        anchor0 = value.value[0]
                        anchor1 = value.value[1]
                    else:
                        anchor0 = value.value[1]
                        anchor1 = value.value[0]
                        
                    a = self.anchor(axis, anchor0, dry_run=True)['roll']
                    b = self.flip(axis).anchor(axis, anchor1, dry_run=True)['roll']
                    
                    size = coord.size 
                    if abs(anchor1 - anchor0) >= coord.period():
                        if value.operator == 'wo':
                            start = 0
                            stop  = 0
                        else:
                            start = -a
                            stop  = -a
                    elif a + b == size:
                        b = self.anchor(axis, anchor1, dry_run=True)['roll']
                        if b == a:
                            if value.operator == 'wo':
                                start= -a
                                stop = -a
                            else:
                                start = 0
                                stop  = 0
                        else:
                            if value.operator == 'wo':
                                start= 0
                                stop = 0
                            else:
                                start = -a
                                stop  = -a
                    else:
                        if value.operator == 'wo':
                            start = b - size
                            stop  = -a + size
                        else:
                            start = -a
                            stop  = b - size
    
                    index = slice(start, stop, 1)
                else:        
                    # CASE 3: All other cases
                    item_match = (value == coord)
                
                    if not item_match.any():
                        raise IndexError(
                            "No %r axis indices found from: %r" %
                            (identity, value))
                
                    index = item_match.array
                #--- End: if
    
                # Put the index in to the correct place in the list of
                # indices
                if axis in data_axes:
                    indices[data_axes.index(axis)] = index
                                    
            else:
                #-----------------------------------------------------
                # N-d coordinate
                #-----------------------------------------------------
                
                # Make sure that each auxiliary coordinate has the
                # same axis order
                coords2 = [coords[0]]
                axes0   = axes[0]
                for a, coord in zip(axes[1:], coords[1:]):
                    if a != axes0:
                        coord = coord.transpose([axes0.index(axis) for axis in a])

                    coords2.append(coord)
                #--- End: for
                coords = coords2

                item_matches = [v == c for v, c in zip(point, coords)]
                    
                item_match = item_matches.pop()
                for m in item_matches:
                    item_match &= m
 
                ind = numpy_where(item_match)

                bounds = [coord.bounds.array[ind] for coord in coords
                          if coord.hasbounds]

                contain = False
                if bounds:
                    point2 = []
                    for v, coord in zip(point, coords):  
                        if isinstance(v, Query):
                            if v.operator == 'contain':                                
                                contain = True
                                v = v.value
                            elif v.operator == 'eq':
                                v = v.value
                            else:
                                contain = False
                                break
                        #--- End: if

                        v = Data.asdata(v)
                        if v.Units:
                            v.Units = coord.Units
                        
                        point2.append(v.datum())
                    #--- End: for
                #--- End: if

                if contain:
                    # The coordinates have bounds and a 'contain'
                    # cf.Query object has been given. Check each
                    # possibly matching cell for actully including the
                    # point.
                    if n_coords > 2:
                        raise IndexError(
                            "333Can't geasasdast index for cell from %d-d coordinate objects" %
                            n_axes)

                    if 0 < len(bounds) < n_coords:
                        raise ValueError("bounds alskdaskds")

                    n_cells = 0
                    for cell, vertices in enumerate(zip(*zip(*bounds))):
                        n_cells += Path(zip(*vertices)).contains_point(point2)
                        if n_cells > 1:
                            # The point is apparently in more than one
                            # cell
                            break
                else:
                    n_cells = len(ind[0])
                    cell = 0
                #--- End: if

                if not n_cells:
                    raise IndexError(
                        "No index found for the point %r" % (point,))
                elif n_cells > 1:
                    raise IndexError("Multiple indices found for %r" % (point,))
                
                # Put the indices in to the correct place in the list
                # of indices
                for axis, index in zip(axes0, numpy_array(ind)[:, cell]):
                    if axis in data_axes:
                        indices[data_axes.index(axis)] = index
                #--- End: for
            #--- End: if
        #--- End: for
                    
#        # Loop round slice criteria
#        for identity, value in kwargs.iteritems():
#            coords = domain.items(identity, role=('d', 'a'),
#                                  exact=exact)
#
#            if len(coords) != 1:
#                raise ValueError(
#                    "Can't find indices: Ambiguous axis identity: %r" %
#                    identity)
#
#            key, coord = coords.popitem()
#
#            if coord.ndim == 1:
#                axis = domain.item_axes(key)[0]
#    
#                if axis in seen_axes:
#                    raise ValueError(
#                        "Can't find indices: Duplicate %r axis" % axis)
#                else:
#                    seen_axes.append(axis)
#    
#                if isinstance(value, (slice, list)):
#                    # ----------------------------------------------------
#                    # Case 1: Subspace criterion is already a valid index
#                    # (i.e. it is a slice object or a list (of ints, but
#                    # this isn't checked for)).
#                    # ----------------------------------------------------
#                    index = value
#    
#                elif (isinstance(value, Query) and 
#                    value.operator in ('wi', 'wo') and
#                    coord.isdimension and
#                    self.iscyclic(key)):
#                    # ----------------------------------------------------
#                    # Case 2: Axis is cyclic and subspace criterion is a
#                    # 'within' or 'without' cf.Query instance
#                    # ----------------------------------------------------
#                    if coord.increasing:
#                        anchor0 = value.value[0]
#                        anchor1 = value.value[1]
#                    else:
#                        anchor0 = value.value[1]
#                        anchor1 = value.value[0]
#                        
#                    a = self.anchor(axis, anchor0, dry_run=True)['roll']
#                    b = self.flip(axis).anchor(axis, anchor1, dry_run=True)['roll']
#                    
#                    size = coord.size 
#                    if abs(anchor1 - anchor0) >= coord.period():
#                        if value.operator == 'wo':
#                            start = 0
#                            stop  = 0
#                        else:
#                            start = -a
#                            stop  = -a
#                    elif a + b == size:
#                        b = self.anchor(axis, anchor1, dry_run=True)['roll']
#                        if b == a:
#                            if value.operator == 'wo':
#                                start= -a
#                                stop = -a
#                            else:
#                                start = 0
#                                stop  = 0
#                        else:
#                            if value.operator == 'wo':
#                                start= 0
#                                stop = 0
#                            else:
#                                start = -a
#                                stop  = -a
#                    else:
#                        if value.operator == 'wo':
#                            start = b - size
#                            stop  = -a + size
#                        else:
#                            start = -a
#                            stop  = b - size
#    
#                    index = slice(start, stop, 1)
#                else:        
#                    # ----------------------------------------------------
#                    # Case 3: All other cases
#                    # ----------------------------------------------------
#                    item_match = (value == coord)
#                
#                    if not item_match.any():
#                        raise IndexError(
#                            "No %r axis indices found from: %r" %
#                            (identity, value))
#                
#                    index = item_match.array
#                #--- End: if
#    
#                # Put the index in to the correct place in the list of
#                # indices
#                if axis in data_axes:
#                    indices[data_axes.index(axis)] = index
#                    
#            else:
#                axes = domain.item_axes(key)[0]
#                item_match = (value == coord)
#                if not item_match.any():
#                    raise IndexError(
#                        "No %r axis indices found from: %r" %
#                        (identity, value))                    
#        #--- End: for

        # Return a tuple of the indices
        return tuple(parse_indices(self, tuple(indices), False))
    #--- End: def

    def insert_data(self, data, axes=None, copy=True, replace=True):
        '''Insert a new data array into the field in place.

Note that the data array's missing data value, if it has one, is not
transferred to the field.

:Parameters:

    data : cf.Data
        The new data array.

    axes : sequence of str, optional
        A list of axis identifiers (``'dimN'``), stating the axes, in
        order, of the data array.

        The ``N`` part of each identifier should be replaced by an
        integer greater then or equal to zero such that either a) each
        axis identifier is the same as one in the field's domain, or
        b) if the domain has no axes, arbitrary integers greater then
        or equal to zero may be used, the only restriction being that
        the resulting identifiers are unique.

        If an axis of the data array already exists in the domain then
        the it must have the same size as the domain axis. If it does
        not exist in the domain then a new axis will be created.

        By default the axes will either be those defined for the data
        array by the domain or, if these do not exist, the domain axis
        identifiers whose sizes unambiguously match the data array.

    copy : bool, optional
        If False then the new data array is not deep copied prior to
        insertion. By default the new data array is deep copied.

    replace : bool, optional
        If False then do not replace an existing data array. By
        default an data array is replaced with *data*.
   
:Returns:

    None

:Examples:

>>> f.domain._axes_sizes
{'dim0': 1, 'dim1': 3}
>>> f.insert_data(cf.Data([[0, 1, 2]]))

>>> f.domain._axes_sizes
{'dim0': 1, 'dim1': 3}
>>> f.insert_data(cf.Data([[0, 1, 2]]), axes=['dim0', 'dim1'])

>>> f.domain._axes_sizes
{}
>>> f.insert_data(cf.Data([[0, 1], [2, 3, 4]]))
>>> f.domain._axes_sizes
{'dim0': 2, 'dim1': 3}

>>> f.insert_data(cf.Data(4))

>>> f.insert_data(cf.Data(4), axes=[])

>>> f.domein._axes_sizes
{'dim0': 3, 'dim1': 2}
>>> data = cf.Data([[0, 1], [2, 3, 4]])
>>> f.insert_data(data, axes=['dim1', 'dim0'], copy=False)

>>> f.insert_data(cf.Data([0, 1, 2]))
>>> f.insert_data(cf.Data([3, 4, 5]), replace=False)
ValueError: Can't initialize data: Data already exists
>>> f.insert_data(cf.Data([3, 4, 5]))

        '''
        if self._hasData and not replace:
            raise ValueError(
                "Can't set data: Data already exists and replace=%s" %
                replace)

        domain = self.domain

        if data.isscalar:
            # --------------------------------------------------------
            # The data array is scalar
            # --------------------------------------------------------
            if axes: 
                raise ValueError(
"Can't set data: Wrong number of axes for scalar data array: {0}".format(axes))

            axes = []

        elif axes is not None:
            # --------------------------------------------------------
            # The axes have been set
            # --------------------------------------------------------
            axes = self.axes(axes, ordered=True)

            if not axes:
                # The domain has no axes: Ignore the provided axes and
                # make some up for the data array
                axes = []
                for size in data.shape:
                    axes.append(self.insert_axis(size))

                axes = axes[:]
            else:
                len_axes = len(axes)
                if len_axes != len(set(axes)):
                    raise ValueError(
"Can't set data: Ambiguous axes: {0}".format(axes))

                    if len_axes != data.ndim:
                        raise ValueError(
"Can't set data: Wrong number of axes for data array: {0!r}".format(axes))
                        
                for axis, size in izip(axes, data.shape):
                    axis_size = self.axis_size(axis)
                    if size != axis_size:
                        raise ValueError(
"Can't set data: Incompatible domain size for axis %r (%d)" %
(axis, size))
                #--- End: for

        elif domain.data_axes() is None:
            # --------------------------------------------------------
            # The data is not scalar and axes have not been set and
            # the domain does not have data axes defined => infer the
            # axes.
            # --------------------------------------------------------
            if not self.axes():
                # The domain has no axes, so make some up for the data
                # array
                axes = []
                for size in data.shape:
                    axes.append(self.insert_axis(size))

                axes = axes[:]
            else:
                # The domain already has some axes
                data_shape = data.shape
                if len(data_shape) != len(set(data_shape)):
                    raise ValueError(
"Can't set data: Ambiguous shape: %s. Consider setting the axes parameter." %
(data_shape,))

                axes = []
                domain_sizes = domain._axes_sizes.values()
                for n in data_shape:
                    if domain_sizes.count(n) == 1:
                        axes.append(domain.axis(size=n))
                    else:
                        raise ValueError(
"Can't set data: Ambiguous shape: %s. Consider setting the axes parameter." %
(data_shape,))
                 #--- End: for
        else:
            # --------------------------------------------------------
            # The data is not scalar and axes have not been set, but
            # the domain has data axes defined.
            # --------------------------------------------------------
            axes = domain.data_axes()
            if len(axes) != data.ndim:
                raise ValueError(
                    "Can't set data: Wrong number of axes for data array: %r" %
                    axes)
            
            for axis, size in izip(axes, data.shape):
                try:
                    domain.insert_axis(size, axis, replace=False)
                except ValueError:
                    raise ValueError(
"Can't set data: Incompatible domain size for axis %r (%d)" %
(axis, size))
            #--- End: for
        #--- End: if

        domain._axes['data'] = axes

        if copy:
            data = data.copy()

        self.Data = data
    #--- End: def

    def domain_mask(self, *args, **kwargs):
        '''{+Fef,}The mask of the data array.

.. versionadded:: 1.1

.. seealso:: `indices`, `mask`, `subspace`

:Examples 1:

Creat a which is True within 30 degrees of the equator:

>>> m = f.domain_mask(latitude=cf.wi(-30, 30))

:Parameters:

    args, kwargs: *optional*

:Returns:

    out : cf.{+Variable}
        {+Fef,}The domain mask.

:Examples 2:

        '''
        # List functionality
        if self._list:
            kwargs2 = self._parameters(locals())
            return self._list_method('domain_mask', kwargs2)

        m = self.copy(_omit_Data=True,
                      _omit_properties=True, _omit_attributes=True)

        m.Data = Data.zeros(self.shape, dtype=bool)
        m.Data[m.indices(*args, **kwargs)] = True

        m.long_name = 'mask'

        return m
    #--- End: def


    def match(self, match=None, items=None, rank=None, ndim=None,
              exact=False, match_and=True, inverse=False):
        '''{+Fef,}Test whether or not the field satisfies the given conditions.

Different types of conditions may be set with the parameters:
         
===========  =========================================================
Parameter    What gets tested
===========  =========================================================
*match*      Field properties and attributes
             
*items*      Field domain items
         
*rank*       The number of field domain axes

*ndim*       The number of field data array axes
===========  =========================================================

By default, when multiple criteria are given the field matches if it
satisfies the conditions given by each one.

.. seealso:: `items`, `select`

**Quick start examples**

There is great flexibility in the types of test which can be
specified, and as a result the documentation is very detailed in
places. These preliminary, simple examples show that the usage need
not always be complicated and may help with understanding the keyword
descriptions.

1. Test if a field contains air temperature data, as given determined
   by its `identity` method:

   >>> f.match('air_temperature')

2. Test if a field contains air temperature data, as given determined
   by its `identity` method, or has a long name which contains the
   string "temp":

   >>> f.match(['air_temperature', {'long_name': cf.eq('.*temp.*', regex=true)}])

3. Test if a field has at least one longitude grid cell point on the
   Greenwich meridian:

   >>> f.match(items={'longitude': 0})

4. Test if a field has latitude grid cells which all have a resolution
   of less than 1 degree:

   >>> f.match(items={'latitude': cf.cellsize(cf.lt(1, 'degree'))})

5. Test if a field has exactly 4 domain axes:

   >>> f.match(rank=4)

6. Examples 1 to 4 may be combined to test if a field has exactly 4
   domain axes, contains air temperature data, has at least one
   longitude grid cell point on the Greenwich meridian and all
   latitude grid cells have a resolution of less than 1 degree:

   >>> f.match('air_temperature',
   ...         items={'longitude': 0,
   ...                'latitude': cf.cellsize(cf.lt(1, 'degree'))},
   ...         rank=4)

7. Test if a field contains Gregorian calendar monthly mean data array
   values:

   >>> f.match({'cell_methods': cf.CellMethods('time: mean')},
   ...         items={'time': cf.cellsize(cf.wi(28, 31, 'days'))})

Further examples are given within and after the description of the
arguments.


:Parameters:

    match : *optional*
        Set conditions on the field's CF property and attribute
        values. *match* may be one, or a sequence of:

          * `None` or an empty dictionary. Always matches the
            field. This is the default.

     ..

          * A string which identifies string-valued metadata of the
            field and a value to compare it against. The value may
            take one of the following forms:

              ==============  ======================================
              *match*         Interpretation
              ==============  ======================================
              Contains ``:``  Selects on the CF property specified
                              before the first ``:``
                                
              Contains ``%``  Selects on the attribute specified
                              before the first ``%``              
              
              Anything else   Selects on identity as returned by the
                              `identity` method
              ==============  ======================================

            By default the part of the string to be compared with the
            item is treated as a regular expression understood by the
            :py:obj:`re` module and the field matches if its
            appropriate value matches the regular expression using the
            :py:obj:`re.match` method (i.e. if zero or more characters
            at the beginning of field's value match the regular
            expression pattern). See the *exact* parameter for
            details.
            
              *Example:*
                To match a field with `identity` beginning with "lat":
                ``match='lat'``.

              *Example:*
                To match a field with long name beginning with "air":
                ``match='long_name:air'``.

              *Example:*
                To match a field with netCDF variable name of exactly
                "tas": ``match='ncvar%tas$'``.

              *Example:*
                To match a field with `identity` which ends with the
                letter "z": ``match='.*z$'``.

              *Example:*
                To match a field with long name which starts with the
                string ".*a": ``match='long_name%\.\*a'``. 

        ..

          * A `cf.Query` object to be compared with field's identity,
            as returned by its `identity` method.

              *Example:*
                To match a field with `identity` of exactly
                "air_temperature" you could set
                ``match=cf.eq('air_temperature')`` (see `cf.eq`).

              *Example:*
                To match a field with `identity` ending with
                "temperature" you could set
                ``match=cf.eq('.*temperature$', exact=False)`` (see
                `cf.eq`).

     ..

          * A dictionary which identifies properties of the field with
            corresponding tests on their values. The field matches if
            **all** of the tests in the dictionary are passed.

            In general, each dictionary key is a CF property name with
            a corresponding value to be compared against the field's
            CF property value. 

            If the dictionary value is a string then by default it is
            treated as a regular expression understood by the
            :py:obj:`re` module and the field matches if its
            appropriate value matches the regular expression using the
            :py:obj:`re.match` method (i.e. if zero or more characters
            at the beginning of field's value match the regular
            expression pattern). See the *exact* parameter for
            details.
            
              *Example:*
                To match a field with standard name of exactly
                "air_temperature" and long name beginning with the
                letter "a": ``match={'standard_name':
                cf.eq('air_temperature'), 'long_name': 'a'}`` (see
                `cf.eq`).

            Some key/value pairs have a special interpretation:

              ==================  ====================================
              Special key         Value
              ==================  ====================================
              ``'units'``         The value must be a string and by
                                  default is evaluated for
                                  equivalence, rather than equality,
                                  with the field's `units` property,
                                  for example a value of ``'Pa'``
                                  will match units of Pascals or
                                  hectopascals, etc. See the *exact*
                                  parameter.
                            
              ``'calendar'``      The value must be a string and by
                                  default is evaluated for
                                  equivalence, rather than equality,
                                  with the field's `calendar`
                                  property, for example a value of
                                  ``'noleap'`` will match a calendar
                                  of noleap or 365_day. See the
                                  *exact* parameter.
                              
              ``'cell_methods'``  The value must be a `cf.CellMethods`
                                  object containing *N* cell methods
                                  and by default is evaluated for
                                  equivalence with the last *N* cell
                                  methods contained within the field's
                                  `cell_methods` property. See the
                                  *exact* parameter.

              `None`              The value is interpreted as for a
                                  string value of the *match*
                                  parameter. For example,
                                  ``match={None: 'air'}`` is
                                  equivalent to ``match='air'`` and
                                  ``match={None: 'ncvar%pressure'}``
                                  is equivalent to
                                  ``match='ncvar%pressure'``.
              ==================  ====================================
            
              *Example:*
                To match a field with standard name starting with
                "air", units of temperature and a netCDF variable name
                beginning with "tas" you could set
                ``match={'standard_name': 'air', 'units': 'K', None:
                'ncvar%tas'}``.

              *Example:*
                To match a field whose last two cell methods are
                equivalent to "time: minimum area: mean":
                ``match={'cell_methods': cf.Cellmethods('time: minimum
                area: mean')``. This would match a field which has,
                for example, cell methods of "height: mean time:
                minimum area: mean".

        If *match* is a sequence of any combination of the above then
        the field matches if it matches **at least one** element of
        the sequence:

          *Example:* 

            >>> f.match('air_temperature')
            True
            >>> f.match('air_pressure')
            False
            >>> f.match({'units': 'hPa', 'long_name': 'foo'})
            False
            >>> f.match(['air_temperature',
            ...          'air_pressure',
            ...          {'units': 'hPa', 'long_name': 'foo'}])
            True
  
        If the sequence is empty then the field always matches.
 
    items : dict, optional
        A dictionary which identifies domain items of the field
        (dimension coordinate, auxiliary coordinate, cell measure or
        coordinate reference objects) with corresponding tests on
        their elements. The field matches if **all** of the specified
        items exist and their tests are passed.

        Each dictionary key specifies an item to test as the one that
        would be returned by this call of the field's `item` method:
        ``f.item(key, exact=exact)`` (see `cf.Field.item`).

        The corresponding value is, in general, any object for which
        the item may be compared with for equality (``==``). The test
        is passed if the result evaluates to True, or if the result is
        an array of values then the test is passed if at least one
        element evaluates to true.

        If the value is `None` then the test is always passed,
        i.e. this case tests for item existence.

          *Example:*
             To match a field which has a latitude coordinate value of
             exactly 30: ``items={'latitude': 30}``.

          *Example:*
             To match a field whose longitude axis spans the Greenwich
             meridien: ``items={'longitude': cf.contain(0)}`` (see
             `cf.contain`).

          *Example:*
             To match a field which has a time coordinate value of
             2004-06-01: ``items={'time': cf.dt('2004-06-01')}`` (see
             `cf.dt`).

          *Example:*
             To match a field which has a height axis: ``items={'Z':
             None}``.

          *Example:*
             To match a field which has a time axis and depth
             coordinates greater then 1000 metres: ``items={'T': None,
             'depth': cf.gt(1000, 'm')}`` (see `cf.gt`).

          *Example:*
            To match a field with time coordinates after than 1989 and
            cell sizes of between 28 and 31 days: ``items={'time':
            cf.dtge(1990) & cf.cellsize(cf.wi(28, 31, 'days'))}`` (see
            `cf.dtge`, `cf.cellsize` and `cf.wi`).

    rank : *optional*
        Specify a condition on the number of axes in the field's
        domain. The field matches if its number of domain axes equals
        *rank*. A range of values may be selected if *rank* is a
        `cf.Query` object. Not to be confused with the *ndim*
        parameter (the number of data array axes may be fewer than the
        number of domain axes).

          *Example:*
            ``rank=2`` matches a field with exactly two domain axes
            and ``rank=cf.wi(3, 4)`` matches a field with three or
            four domain axes (see `cf.wi`).

    ndim : *optional*
        Specify a condition on the number of axes in the field's data
        array. The field matches if its number of data array axes
        equals *ndim*. A range of values may be selected if *ndim* is
        a `cf.Query` object. Not to be confused with the *rank*
        parameter (the number of domain axes may be greater than the
        number of data array axes).

          *Example:*
            ``ndim=2`` matches a field with exactly two data array
            axes and ``ndim=cf.le(2)`` matches a field with fewer than
            three data array axes (see `cf.le`).

    exact : bool, optional
        The *exact* parameter applies to the interpretation of string
        values of the *match* parameter and of keys of the *items*
        parameter. By default *exact* is False, which means that:

          * A string value is treated as a regular expression
            understood by the :py:obj:`re` module. 

          * Units and calendar values in a *match* dictionary are
            evaluated for equivalence rather then equality
            (e.g. "metre" is equivalent to "m" and to "km").

          * A cell methods value containing *N* cell methods in a
            *match* dictionary is evaluated for equivalence with the
            last *N* cell methods contained within the field's
            `cell_methods` property.

        ..

          *Example:*
            To match a field with a standard name which begins with
            "air" and any units of pressure:
            ``f.match({'standard_name': 'air', 'units': 'hPa'})``.

          *Example:*          
            ``f.match({'cell_methods': cf.CellMethods('time: mean
            (interval 1 hour)')})`` would match a field with cell
            methods of "area: mean time: mean (interval 60 minutes)".

        If *exact* is True then:

          * A string value is not treated as a regular expression.

          * Units and calendar values in a *match* dictionary are
            evaluated for exact equality rather than equivalence
            (e.g. "metre" is equal to "m", but not to "km").

          * A cell methods value in a *match* dictionary is evaluated
            for exact equality to the field's cell methods.
          
        ..

          *Example:*          
            To match a field with a standard name of exactly
            "air_pressure" and units of exactly hectopascals:
            ``f.match({'standard_name': 'air_pressure', 'units':
            'hPa'}, exact=True)``.

          *Example:*          
            To match a field with a cell methods of exactly "time:
            mean (interval 1 hour)": ``f.match({'cell_methods':
            cf.CellMethods('time: mean (interval 1 hour)')``.

        Note that `cf.Query` objects provide a mechanism for
        overriding the *exact* parameter for individual values.

          *Example:*
            ``f.match({'standard_name': cf.eq('air', exact=False),
            'units': 'hPa'}, exact=True)`` will match a field with a
            standard name which begins "air" but has units of exactly
            hectopascals (see `cf.eq`).
    
          *Example:*
            ``f.match({'standard_name': cf.eq('air_pressure'),
            'units': 'hPa'})`` will match a field with a standard name
            of exactly "air_pressure" but with units which equivalent
            to hectopascals (see `cf.eq`).

    match_and : bool, optional
        By default *match_and* is True and the field matches if it
        satisfies the conditions specified by each test parameter
        (*match*, *items*, *rank* and *ndim*).

        If *match_and* is False then the field will match if it
        satisfies at least one test parameter's condition.

          *Example:*
            To match a field with a standard name of "air_temperature"
            **and** 3 data array axes: ``f.match('air_temperature',
            ndim=3)``. To match a field with a standard name of
            "air_temperature" **or** 3 data array axes:
            ``f.match('air_temperature", ndim=3, match_and=False)``.
    
    inverse : bool, optional
        If True then return the field matches if it does **not**
        satisfy the given conditions.

          *Example:*
          
            >>> f.match('air', ndim=4, inverse=True) == not f.match('air', ndim=4)
            True

:Returns:

[+1]    out : bool
[+N]    out : list of bool
        {+Fef,}True if the field satisfies the given criteria, False
        otherwise.

:Examples:

Field identity starts with "air":

>>> f.match('air')

Field identity ends contains the string "temperature":

>>> f.match('.*temperature')

Field identity is exactly "air_temperature":

>>> f.match('^air_temperature$')
>>> f.match('air_temperature', exact=True)

Field has units of temperature:

>>> f.match({'units': 'K'}):

Field has units of exactly Kelvin:

>>> f.match({'units': 'K'}, exact=True)

Field identity which starts with "air" and has units of temperature:

>>> f.match({None: 'air', 'units': 'K'})

Field identity starts with "air" and/or has units of temperature:

>>> f.match(['air', {'units': 'K'}])

Field standard name starts with "air" and/or has units of exactly Kelvin:

>>> f.match([{'standard_name': cf.eq('air', exact=False), {'units': 'K'}],
...         exact=True)

Field has height coordinate values greater than 63km:

>>> f.match(items={'height': cf.gt(63, 'km')})

Field has a height coordinate object with some values greater than
63km and a north polar point on its horizontal grid:

>>> f.match(items={'height': cf.gt(63, 'km'),
...                'latitude': cf.eq(90, 'degrees')})

Field has some longitude cell sizes of 3.75:

>>> f.match(items={'longitude': cf.cellsize(3.75)})

Field latitude cell sizes within a tropical region are all no greater
than 1 degree:

>>> f.match(items={'latitude': (cf.wi(-30, 30, 'degrees') &
...                             cf.cellsize(cf.le(1, 'degrees')))})

Field contains monthly mean air pressure data and all vertical levels
within the bottom 100 metres of the atmosphere have a thickness of 20
metres or less:

>>> f.match({None: '^air_pressure$', 'cell_methods': cf.CellMethods('time: mean')},
...         items={'height': cf.le(100, 'm') & cf.cellsize(cf.le(20, 'm')),
...                'time': cf.cellsize(cf.wi(28, 31, 'days'))})

        '''
        conditions_have_been_set = False
        something_has_matched    = False

        if rank is not None:
            conditions_have_been_set = True
            found_match = len(self.axes()) == rank
            if match_and and not found_match:
                return bool(inverse)

            something_has_matched = True
        #--- End: if

        if match:
            conditions_have_been_set = True
             
        # --------------------------------------------------------
        # Try to match other properties and attributes
        # --------------------------------------------------------
        found_match = super(Field, self).match(
            match=match, ndim=ndim, exact=exact,
            match_and=match_and, inverse=False,
            _Flags=True, _CellMethods=True)

        if match_and and not found_match:
            return bool(inverse)

        something_has_matched = found_match
        #--- End: if

        # ------------------------------------------------------------
        # Try to match items
        # ------------------------------------------------------------
        if items:
            conditions_have_been_set = True

            found_match = False

            for identity, condition in items.iteritems():
                c = self.item(identity, exact=exact)

                if condition is None:
                    field_matches = True
                elif c is None:
                    field_matches = False
                else:
                    field_matches = condition == c
                    try:
                        field_matches = field_matches.any()
                    except AttributeError:
                        pass
                #--- End: if
                
                if match_and:                    
                    if field_matches:
                        found_match = True 
                    else:
                        found_match = False
                        break
                elif field_matches:
                    found_match = True
                    break
            #--- End: for 

            if match_and and not found_match:
                return bool(inverse)

            something_has_matched = found_match
        #--- End: if

        if conditions_have_been_set:
            if something_has_matched:            
                return not bool(inverse)
            else:
                return bool(inverse)
        else:
            return not bool(inverse)
    #--- End: def

#In [66]: w  
#Out[66]: array([ 0.125,  0.25 ,  0.375,  0.25 ])
#In [67]: convolve1d(a, w, mode='mirror')        
#Out[67]: array([ 1.75,  2.25,  3.25,  4.25,  5.25,  6.25,  7.  ,  7.25])
#
#In [68]: (w[::-1] * [5, 6, 7, 8]).sum()  
#Out[68]: 6.25
#
#In [69]: (w[::-1] * [6, 7, 8, 7]).sum() 
#Out[69]: 7.0
#
#In [70]: (w[::-1] * [7, 8, 7, 6]).sum()  
#Out[70]: 7.25





#In [60]: convolve1d(a, t, mode='mirror') 
#Out[60]: array([ 1.5,  2. ,  3. ,  4. ,  5. ,  6. ,  7. ,  7.5])
#
#In [61]: (t[::-1] * [5, 6, 7]).sum()   
#Out[61]: 6.0
#
#In [62]: (t[::-1] * [6, 7, 8]).sum()  
#Out[62]: 7.0
#
#In [63]: (t[::-1] * [7, 8, 7]).sum()  
#Out[63]: 7.5
#
#In [64]: t                           
#Out[64]: array([ 0.25,  0.5 ,  0.25])
#
#In [65]: a                            
#Out[65]: array([ 1.,  2.,  3.,  4.,  5.,  6.,  7.,  8.])


#In [75]: convolve1d(a, w, mode='reflect')   
#Out[75]: array([ 1.5  ,  2.25 ,  3.25 ,  4.25 ,  5.25 ,  6.25 ,  7.125,  7.625])
#
#In [76]: (w[::-1] * [5, 6, 7, 8]).sum()  
#Out[76]: 6.25
#
#In [77]: (w[::-1] * [6, 7, 8, 8]).sum()   
#Out[77]: 7.125
#
#In [78]: (w[::-1] * [7, 8, 8, 7]).sum()   
#Out[78]: 7.625
#In [81]: w     
#Out[81]: array([ 0.125,  0.25 ,  0.375,  0.25 ])
#
#In [82]: a     
#Out[82]: array([ 1.,  2.,  3.,  4.,  5.,  6.,  7.,  8.])

#In [94]: u                                                                                                        
#Out[94]: array([ 0.11111111,  0.22222222,  0.33333333,  0.22222222,  0.11111111])
#
#In [95]: convolve#convolve1d(a, w, mode='reflect')eflect')                                                        
#
#In [96]: convolve1d(a, u, mode='mirror')                                                                          
#Out[96]: 
#array([ 1.88888889,  2.22222222,  3.        ,  4.        ,  5.        ,
#        6.        ,  6.77777778,  7.11111111])
#
#In [97]: (u[::-1] * [4, 5, 6, 7, 8]).sum()                                                                        
#Out[97]: 6.0
#
#In [98]: (u[::-1] * [5, 6, 7, 8, 7]).sum()                                                                        
#Out[98]: 6.7777777777777768
#
#In [99]: (u[::-1] * [6, 7, 8, 7, 6]).sum()                                                                        
#Out[99]: 7.1111111111111107
#
#In [100]:                                        
#
#    def smooth(self, n, weights='boxcar', axis=None, mode='reflect', constant=0.0, mtol=0.0,
#               beta=None, std=None, power=None, width=None,
#               attenuation=None, return_weights=False):
## http://docs.scipy.org/doc/scipy-0.14.0/reference/signal.html      
##scipy.ndimage.filters.convolve1d
##ocs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.filters.convolve.html        
##http://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.filters.convolve1d.html
#
#        '''Smooth the field along one of its axes.
#
# By default the field is smoothed with an unweighted moving average.
#
# The smoothing is the discrete convolution of values along the axis
# with a normalised weights function defined over an interval (window)
# of the axis.
#
#
#
#:Parameters:
#
#    window : str, optional
#
#          ====================  ==============================  ===============================
#          weights               Description                     Reference
#          ====================  ==============================  ===============================
#          ``barthann``          Modified Bartlett-Hann weights  `scipy.signal.barthann`        
#          ``bartlett``          Bartlett weights                `scipy.signal.bartlett`        
#          ``blackman``          Blackman weights                `scipy.signal.blackman`       
#          ``blackmanharris``    Minimum 4-term Blackman-Harris  `scipy.signal.blackmanharris`  
#                                weights                           
#          ``bohman``            Bohman weights                  `scipy.signal.bohman`          
#          ``boxcar``            Boxcar or rectangular weights   `scipy.signal.boxcar`
#          ``chebwin``           Dolph-Chebyshev weights         `scipy.signal.chebwin`         
#          ``cosine``            Weights with a simple cosine    `scipy.signal.cosine`          
#                                shape                                   
#          ``flattop``           Flat top weights                `scipy.signal.flattop`         
#          ``gaussian``          Gaussian weights                `scipy.signal.gaussian`        
#          ``general_gaussian``  Weights with a generalized      `scipy.signal.general_gaussian`
#                                Gaussian shape                   
#          ``hamming``           Hamming weights                 `scipy.signal.hamming`         
#          ``hann``              Hann weights                    `scipy.signal.hann`           
#          ``kaiser``            Kaiser weights                  `scipy.signal.kaiser`          
#          ``nuttall``           Minimum 4-term Blackman-Harris  `scipy.signal.nuttall`         
#                                weights according to Nuttall      
#          ``parzen``            Parzen weights                  `scipy.signal.parzen`         
#          ``slepian``           Digital Slepian (DPSS) weights  `scipy.signal.slepian`         
#          ``triang``            Triangular weights              `scipy.signal.triang`          
#          ???/                  User-defined weights
#          ====================  ==============================  ===============================
#
#        The default weights are ``'boxcar'``, which are create an
#        unweighted moving average

#        Some weights require extra parameters to be set for their calculation:
#        
#          ======================  ================  ===============================
#          *weights*               Extra parameters  Reference                      
#          ======================  ================  ===============================
#          ``'chebwin'``           *attenuation*     `scipy.signal.chebwin`
#          ``'gaussian'``          *std*             `scipy.signal.gaussian`    
#          ``'general_gaussian'``  *power*, *std*    `scipy.signal.general_gaussian`
#          ``'kaiser'``            *beta*            `scipy.signal.kaiser`   
#          ``'slepian'``           *width*           `scipy.signal.slepian`   
#          ======================  ================  ===============================
#
#    attenuation : number, optional
#        Required for a Dolph-Chebyshev weights, otherwise
#        ignored. *attenuation* is in decibels.
#    
#          Example: ``n=51, weights='chebwin', attenuation=100``
#
#    beta : number, optional
#        Required for Kaiser weights, otherwise ignored. *beta* is a
#        shape parameter which determines the trade-off between
#        main-lobe width and side lobe level.
#    
#          Example: ``n=51, weights='Kaiser', beta=14``
#
#    power : number, optional
#        Required for a generalized Gaussian weights, otherwise
#        ignored. *power* is a shape parameter: 1 is identical to
#        Gaussian weights, 0.5 is the same shape as the Laplace
#        distribution.
#
#          Example: ``n=52, weights='general_gaussian', power=1.5, std=7``
#
#    std : number, optional
#        Required for Gaussian and generalized Gaussian weights,
#        otherwise ignored. *std* is the standard deviation, sigma.
#
#          Example: ``n=52, weights='gaussian', std=7``
#
#    width : float, optional
#        Required for digital Slepian (DPSS) weights, otherwise
#        ignored. *wodth* is the bandwidth.
#
#          Example: ``n=51, weights='slepian', width=0.3``
#
#    rolling_window : *optional*
#        Group the axis elements for a "rolling window" collapse. The
#        axis is grouped into **consecutive** runs of **overlapping**
#        elements. The first group starts at the first element of the
#        axis and each following group is offset by one element from
#        the previous group, so that an element may appear in multiple
#        groups. The collapse operation is applied to each group
#        independently and the collapsed axis in the returned field
#        will have a size equal to the number of groups. If weights
#        have been given by the *weights* parameter then they are
#        applied to each group, unless alternative weights have been
#        provided with the *window_weights* parameter. The
#        *rolling_window* parameter may be one of:
#
#          * An `int` defining the number of elements in each
#            group. Each group will have exactly this number of
#            elements. Note that if the group size does does not divide
#            exactly into the axis size then some elements at the end
#            of the axis will not be included in any group.
#            
#              Example: To define groups of 5 elements:
#              ``rolling_window=5``.
#
#        .. 
#
#          * A `cf.Data` defining the group size. Each group contains a
#            consecutive run of elements whose range of coordinate
#            bounds does not exceed the group size. Note that 1) if the
#            group size is sufficiently small then some groups may be
#            empty and some elements may not be inside any group may
#            not be inside any group; 2) different groups may contain
#            different numbers of elements.
#
#              Example: To create 10 kilometre windows:
#              ``rolling_window=cf.Data(10, 'km')``.
#
#    window_weights : ordered sequence of numbers, optional
#        Specify the weights for a rolling window collapse. Each
#        non-empty group uses these weights in its collapse, and all
#        non-empty groups must have the same number elements as the
#        window weights. If *window_weights* is not set then the groups
#        take their weights from the *weights* parameter, and in this
#        case the groups may have different sizes.
#
#          Example: To define a 1-2-1 filter: ``rolling_window=3,
#          window_weights=[1, 2, 1]``.
#
#'''
#        if weights == 'user':
#            weights = numpy_array(weights, float)
#            if weights.size != n:
#                raise ValueError("jb ")
#            if weights.ndim > 1:
#                raise ValueError("bad shape")
#        else:
#            weights = getattr(signal, window)(n, **window_args)

#        if return_weights:
#            return weights

#        http://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.filters.convolve1d.html

#        http://docs.scipy.org/doc/scipy/reference/generated/scipy.ndimage.filters.convolve.html

#        smoothed_array = convolve1d(array, weights/weights.sum(), axis=iaxis,
        #                            mode=mode, cval=constant)
#        
#        f.Data = Data(smoothed_array, f.Units)
#http://mail.scipy.org/pipermail/scipy-user/2008-November/018601.html
#Sorry for the long overdue reply.
#
#Reflect means:
#
#1 | 2 | 3 | 2 | 1
#
#While mirror means:
#
#1 | 2 | 3 | 3| 2 | 1
#
#(or the other way around, can't remember). IT IS THE OTHER WAY ROUND!!!!
#
#http://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.savgol_filter.html#scipy.signal.savgol_filter

#The problem with the last approach is the interpolation between 3 and
#3, which is currently broken, so I'd advise against using it.
#
#
#        # Coordinate bounds
#        dim = f.dim(axis)
#
#
#        n_by_2 = 0.5 * n
#        i = int(n_by_2)
#        j = axis_size - i
#        d1 = i
#        if not i < n_by_2:
#            # Window has even number of points
#            i -= 1
#
#        d0 = i
# 
#        new_bounds[:i, 0] = bounds[0, 0]
#
#        new_bounds[i:j, 0] = bounds[i-d0:j-d0, 0]
#        new_bounds[i:j, 1] = bounds[i+d1:j+d1, 1]
#
#        new_bounds[j:, 1] = bounds[-1, 1]
#
#        if mode == 'mirror':
#            new_bounds[:i, 1] = bounds[i+d1, 1]
#            new_bounds[j:, 0] = bounds[j-d0, 0]
#        elif mode in ('nearest', 'reflect', 'constant'):
#            new_bounds[:i, 1] = bounds[d1:i+d1, 1]
#            new_bounds[j:, 0] = bounds[j-d0:axis_size-d0, 0]
#                
#            wrap?
##        if dim:
#            if dim.hasbounds:            
#                data       = dim.array
#                bounds     = dim.bounds.array
#                new_bounds = numpy_empty(bounds.shape, dtype=float)
#                
#                half_window = 0.5 * n * float(cell_sizes[0])
#                
#                if dim.increasing:
#                    a_min, a_max = bounds[[0, -1], [0, 1]]
#                else:
#                    half_window = -half_window 
#                    a_min, a_max = bounds[[-1, 0], [0, 1]]
#                    
#                new_bounds[0] = data - half_window
#                new_bounds[1] = data + half_window
#                numpy_clip(new_bounds, a_min, a_max, new_bounds)
#                
#                dim.insert_bounds(Data(new_bounds, dim.Units), copy=False)
#            #--- End: if   
#
#            f.remove_items(role='c', axes=axis)
#            
#            for b in f.auxs(axes=axis):
#                if b.hasbounds:
#                    del b.bounds
#       #--- End: if   

#        cell_methods = getattr(f, 'cell_methods', None)
#        if cell_methods is None:
#            cell_methods = CellMethods()
#
#        f.cell_methods += CellMethods(
#            'name: mean (+'+weights+' weights '+', '.join([str(x) for x in weights])+')')
#
##    #--- End: def

    def field(self, items=None, role=None, axes=None, axes_all=None,
              axes_subset=None, axes_superset=None, exact=False,
              inverse=False, match_and=True, ndim=None, bounds=False):
        '''{+Fef,}Create an independent field from a domain item.

An item is either a dimension coordinate, an auxiliary coordinate or a
cell measure object of the domain.

{+item_selection}

If a unique item can not be found then no field is created and `None`
is returned.

A field may also be created from coordinate bounds (see the *bounds*
parameter).

.. versionadded:: 1.1

.. seealso:: `cf.read`, `item`

:Examples 1:

:Parameters:

    {+items}

    {+role}

    {+axes}

    {+axes_all}

    {+axes_subset}

    {+axes_superset}

    {+ndim}

    {+match_and}

    {+exact}
       
    {+inverse}

    bounds : bool, optional
        If true then create a field from a coordinate object's bounds.

:Returns:

    out : cf.{+Variable}
        {+Fef,}The field based on the selected domain item.
        
:Examples 2:

::

   >>> print f 
   eastward_wind field summary
   ---------------------------
   Data           : eastward_wind(time(3), grid_latitude(110), grid_longitude(106)) m s-1
   Cell methods   : time: mean
   Axes           : time(3) = [1979-05-01 12:00:00, ..., 1979-05-03 12:00:00] gregorian
                  : grid_longitude(106) = [-20.54, ..., 25.66] degrees
                  : grid_latitude(110) = [23.32, ..., -24.64] degrees
   Aux coords     : latitude(grid_latitude(110), grid_longitude(106)) = [[67.12, ..., 22.89]] degrees_north
                  : longitude(grid_latitude(110), grid_longitude(106)) = [[-45.98, ..., 35.29]] degrees_east
   Coord refs     : <CF CoordinateReference: rotated_latitude_longitude>
   
   >>> print f.field('X')
   grid_longitude field summary
   ----------------------------
   Data           : grid_longitude(grid_longitude(106)) degrees
   Axes           : grid_longitude(106) = [-20.54, ..., 25.66] degrees
   Coord refs     : <CF CoordinateReference: rotated_latitude_longitude>
   
   >>> print f.field('X', bounds=True)
   grid_longitude field summary
   ----------------------------
   Data           : grid_longitude(grid_longitude(106), domain%dim1(2)) degrees
   Axes           : domain%dim1(2)
                  : grid_longitude(106) = [-20.54, ..., 25.66] degrees
   Coord refs     : <CF CoordinateReference: rotated_latitude_longitude>
   
   >>> print f.field('lat')
   latitude field summary
   ----------------------
   Data           : latitude(grid_latitude(110), grid_longitude(106)) degrees_north
   Axes           : grid_longitude(106) = [-20.54, ..., 25.66] degrees
                  : grid_latitude(110) = [23.32, ..., -24.64] degrees
   Aux coords     : latitude(grid_latitude(110), grid_longitude(106)) = [[67.12, ..., 22.89]] degrees_north
                  : longitude(grid_latitude(110), grid_longitude(106)) = [[-45.98, ..., 35.29]] degrees_east
   Coord refs     : <CF CoordinateReference: rotated_latitude_longitude>

To multiply the field by the cosine of its latitudes:

>>> latitude = f.field({'units': 'radian', None: 'Y'})
>>> latitude
<CF Field: grid_latitude(grid_latitude(110)) degrees>
>>> g = f * latitude.cos()

        '''
        kwargs2 = self._parameters(locals())

        # List functionality
        if self._list:
            return self._list_method('field', kwargs2)

        del kwargs2['bounds']
 
        items = self.items(**kwargs2)
        if not items:
            return

        key, item = items.popitem()

        if items:
            return

        domain = self.domain.copy()

        # Remove domain items which span any axis not spanned by the
        # item
        axes = self.axes(key, ordered=True)
        unused_axes = self.axes().difference(axes)
        for key in self.items(axes=unused_axes):
            domain.remove_item(key)

        # Remove coordinate references which do not span any of the
        # item's axes
        for key in self.refs():
            if not self.domain.ref_axes(key).intersection(axes):
                domain.remove_item(key)

        # Remove the unused axes
        domain._axes.pop('data', None)
        domain.remove_axes(unused_axes)

        if bounds and item.hasbounds:
            item = item.bounds
            axes.append(domain.insert_axis(item.shape[-1]))

        # Create the field
        f = type(self)(properties=item.properties,
                       domain=domain,
                       axes=axes,
                       data=getattr(item, 'Data', None),
                       copy=True)
        
        # Set the field's ncvar attribute
        ncvar = getattr(item, 'ncvar', None)
        if ncvar is not None:
            f.ncvar = ncvar

        return f
    #--- End: def

    def flip(self, axes=None, i=False, **kwargs):
        '''

{+Fef,}Flip (reverse the direction of) axes of the field.

.. seealso:: `axes`, `expand_dims`, `squeeze`, `transpose`,
             `unsqueeze`
        
:Examples:

>>> f.flip()
>>> f.flip('time')
>>> f.flip(1)
>>> f.flip('dim2')
>>> f.flip(['time', 1, 'dim2'])

:Parameters:

    {+axes, kwargs}

    {+i}
 
:Returns:

    out : cf.{+Variable}
        {+Fef,}The flipped field.

'''
        # List functionality
        if self._list:
            kwargs2 = self._parameters(locals())
            return self._list_method('flip', kwargs2)

        domain  = self.domain

        if axes is None and not kwargs:
            # Flip all the axes
            axes = domain.axes()
            iaxes = range(self.ndim)
        else:
            axes = domain.axes(axes, **kwargs)

            data_axes = domain.data_axes()
            iaxes = [data_axes.index(axis) for axis in
                     axes.intersection(data_axes)]
        #--- End: if

        # Flip the requested axes in the field's data array
        f = super(Field, self).flip(iaxes, i=i)

        # Flip any coordinate and cell measures which span the flipped
        # axes
        domain = f.domain
        domain_axes = domain._axes
        for key, item in domain.items(role=('d', 'a', 'm')).iteritems():
            item_axes = domain_axes[key]
            item_flip_axes = axes.intersection(item_axes)
            if item_flip_axes:
                iaxes = [item_axes.index(axis) for axis in item_flip_axes]
                item.flip(iaxes, i=True)
        #--- End: for

        return f
    #--- End: def

    def remove_data(self):
        '''

Remove and return the data array.

:Returns: 

    out : cf.Data or None
        The removed data array, or `None` if there isn't one.

:Examples:

>>> f._hasData
True
>>> f.data
<CF Data: [0, ..., 9] m>
>>> f.remove_data()
<CF Data: [0, ..., 9] m>
>>> f._hasData
False
>>> print f.remove_data()
None

'''
        self.domain._axes.pop('data', None)

        return super(Field, self).remove_data()
    #--- End: def

    def select(self, match=None, items=None, rank=None, ndim=None,
               exact=False, match_and=True, inverse=False):
        '''{+Fef,}Return the field if it satisfies the given conditions.

The conditions are defined in the same manner as for `cf.Field.match`,
which tests whether or not a field matches the given criteria.

If the field does not satisfy the conditions then an empty
`cf.FieldList` object is returned.

[+1]Note that ``f.select(**kwargs)`` is equivalent to ``f if
[+1]f.match(**kwargs) else cf.FieldList()``.
[+N]Note that ``f.select(**kwargs)`` is equivalent to ``FieldList(g for g
[+N]in f if g.match(**kwargs))``

.. seealso:: `match`

:Parameters:

    match : *optional*
        Set conditions on the field's CF property and attribute
        values. See the *match* parameter of `cf.Field.match` for
        details.

    items : dict, optional
        A dictionary which identifies domain items of the field
        (dimension coordinate, auxiliary coordinate, cell measure or
        coordinate reference objects) with corresponding tests on
        their elements. See the *items* parameter of `cf.Field.match`
        for details.
      
    rank : int or cf.Query, optional
        Specify a condition on the number of axes in the field's
        domain. See `cf.Field.match` for details.

    ndim : *optional*
        Specify a condition on the number of axes in the field's data
        array. See `cf.Field.match` for details.

    exact : bool, optional
        The exact parameter applies to the interpretation of string
        values of the *match* parameter and of keys of the *items*
        parameter. See the *exact* parameter of `cf.Field.match` for
        details.
     
    match_and : bool, optional
        By default *match_and* is True and the field matches if it
        satisfies the conditions specified by each test parameter
        (*match*, *items*, *rank* and *ndim*). If *match_and* is False
        then the field will match if it satisfies at least one test
        parameter's condition. See the *match_and* parameter of
        `cf.Field.match` for details.

    inverse : bool, optional
        If True then return the field matches if it does **not**
        satisfy the given conditions. See the *inverse* parameter of
        `cf.Field.match` for details.


:Returns:

    out : cf.Field or cf.FieldList
[+1]        If the field matches the given conditions then it is returned.
[+1]        Otherwise an empty field list is returned.
[+N]        If a single field matches the given conditions then it is
[+N]        returned, otherwise a {+variable} of the matching fields is
[+N]        returned.

:Examples:

Select the field if has exactly four domain axes:

>>> f.select(rank=4)

See `cf.Field.match` for further examples.

        '''
        kwargs2 = self._parameters(locals())

        # List functionality
        if self._list:
            fl = [f for f in self if f.match(**kwargs2)]
            if len(fl) == 1:
                return fl[0]
            else:
                return type(self)(fl)

        if self.match(**kwargs2):
            return self
        else:
            return FieldList()
    #--- End: def

    def set_equals(self, other, rtol=None, atol=None, ignore_fill_value=False, 
                   traceback=False, ignore=('Conventions',)):
        '''
        '''
        return self.equals(other, rtol=rtol, atol=atol, 
                           ignore_fill_value=ignore_fill_value,
                           traceback=traceback, ignore=ignore,
                           _set=True)
    #---End: def

    def anchor(self, axes, value, i=False, dry_run=False, **kwargs):
        '''

{+Fef,}Roll a cyclic axis so that the given value lies in the first
coordinate cell.

{+Fef,}A unique axis is selected with the *axes* and *kwargs* parameters.

.. versionadded:: 1.0

[+1].. seealso:: `axis`, `cyclic`, `iscyclic`, `period`, `roll`
[+N].. seealso:: `cf.Field.axis`, `cf.Field.cyclic`, `cf.Field.iscyclic`,
[+N]             `cf.Field.period`, `roll`

:Examples 1:

Anchor the cyclic X axis to a value of 180:

>>> g = f.anchor('X', 180)

:Parameters:

    {+axes, kwargs}

    value : data-like object
        Anchor the dimension coordinate values for the selected cyclic
        axis to the *value*. If *value* has units then they must be
        compatible with those of the dimension coordinates, otherwise
        it is assumed to have the same units as the dimension
        coordinates. The coordinate values are transformed so that
        *value* is "equal to or just before" the new first coordinate
        value. More specifically:
        
          * Increasing dimension coordinates with positive period, P,
            are transformed so that *value* lies in the half-open
            range (L-P, F], where F and L are the transformed first
            and last coordinate values, respectively.

          * Decreasing dimension coordinates with positive period, P,
            are transformed so that *value* lies in the half-open
            range (L+P, F], where F and L are the transformed first
            AND last coordinate values, respectively.

        ..

            *Example:*
              If the original dimension coordinates are ``0, 5, ...,
              355`` (evenly spaced) and the period is ``360`` then
              ``value=0`` implies transformed coordinates of ``0, 5,
              ..., 355``; ``value=-12`` implies transformed coordinates
              of ``-10, -5, ..., 345``; ``value=380`` implies
              transformed coordinates of ``380, 385, ..., 715``.

            *Example:*
              If the original dimension coordinates are ``355, 350,
              ..., 0`` (evenly spaced) and the period is ``360`` then
              ``value=355`` implies transformed coordinates of ``355,
              350, ..., 0``; ``value=0`` implies transformed
              coordinates of ``0, -5, ..., -355``; ``value=392``
              implies transformed coordinates of ``390, 385, ...,
              30``.

        {+data-like}

    {+i}

    dry_run : bool, optional
        Return a dictionary of parameters which describe the anchoring
        process. The field is not changed, even if *i* is True.

:Returns:

[+1]    out : cf.{+Variable} or dict
[+N]    out : cf.{+Variable}

:Examples 2:

>>> f[+0].iscyclic('X')
True
>>> f[+0].dim('X').data
<CF Data: [0, ..., 315] degrees_east>
>>> print f[+0].dim('X').array
[  0  45  90 135 180 225 270 315]
>>> g = f.anchor('X', 230)
>>> print g[+0].dim('X').array
[270 315   0  45  90 135 180 225]
>>> g = f.anchor('X', cf.Data(590, 'degreesE'))
>>> print g[+0].dim('X').array
[630 675 360 405 450 495 540 585]
>>> g = f.anchor('X', cf.Data(-490, 'degreesE'))
>>> print g[+0].dim('X').array
[-450 -405 -720 -675 -630 -585 -540 -495]

>>> f[+0].iscyclic('X')
True
>>> f[+0].dim('X').data
<CF Data: [0.0, ..., 357.1875] degrees_east>
>>> f.anchor('X', 10000)[+0].dim('X').data
<CF Data: [10001.25, ..., 10358.4375] degrees_east>
>>> d = f[+0].anchor('X', 10000, dry_run=True)
>>> d
{'axis': 'dim2',
 'nperiod': <CF Data: [10080.0] 0.0174532925199433 rad>,
 'roll': 28}
>>> (f.roll(d['axis'], d['roll'])[+0].dim(d['axis']) + d['nperiod']).data
<CF Data: [10001.25, ..., 10358.4375] degrees_east>

        '''
        # List functionality
        if self._list:
            kwarsg2 = self._parameters(locals())
            if kwargs2['dry_run']:
                raise ValueError(
"Can't do a dry run on a {}".format(self.__class__.__name__))
            return self._list_method('anchor', kwargs2)

        axis = self.domain.axis(axes, **kwargs)
        if axis is None:
            raise ValueError(
"Can't anchor: Bad axis specification")

        if i or dry_run:
            f = self
        else:
            f = self.copy()
        
        domain = f.domain

        dim = domain.item(axis)
        if dim is None:
            raise ValueError(
"Can't shift non-cyclic {!r} axis".format(f.axis_name(axis)))
        
        period = dim.period()
        if period is None:
            raise ValueError(
"Cyclic {!r} axis has no period".format(dim.name()))

        value = Data.asdata(value)
        if not value.Units:
            value = value.override_units(dim.Units)
        elif not value.Units.equivalent(dim.Units):
            raise ValueError(
"Anchor value has incompatible units: {!r}".format(value.Units))

        axis_size = domain.axis_size(axis)
        if axis_size <= 1:
            # Don't need to roll a size one axis
            if dry_run:
                return {'axis': axis, 'roll': 0, 'nperiod': 0}
            else:
                return f
        
        c = dim.data

        if dim.increasing:
            # Adjust value so it's in the range [c[0], c[0]+period) 
            n = ((c[0] - value) / period).ceil(i=True)
            value1 = value + n * period

            shift = axis_size - numpy_argmax(c - value1 >= 0)
            if not dry_run:
                f.roll(axis, shift, i=True)     

            dim = domain.item(axis)
            n = ((value - dim.data[0]) / period).ceil(i=True)
        else:
            # Adjust value so it's in the range (c[0]-period, c[0]]
            n = ((c[0] - value) / period).floor(i=True)
            value1 = value + n * period

            shift = axis_size - numpy_argmax(value1 - c >= 0)
            if not dry_run:
                f.roll(axis, shift, i=True)     

            dim = domain.item(axis)
            n = ((value - dim.data[0]) / period).floor(i=True)
        #--- End: if

        if dry_run:
            return  {'axis': axis, 'roll': shift, 'nperiod': n*period}

        if n:
            np = n * period
            dim += np
            if dim.hasbounds:
                bounds = dim.bounds
                bounds += np
        #--- End: if
                
        return f
    #--- End: def

    def autocyclic(self):
        '''

{+Fef,}Set axes to be cyclic if they meet conditions.

An axis is set to be cyclic if and only if the following is true:

* It has a unique, 1-d, longitude dimension coordinate object with
  bounds and the first and last bounds values differ by 360 degrees
  (or an equivalent amount in other units).
   
.. versionadded:: 1.0

[+1].. seealso:: `cyclic`, `iscyclic`, `period`
[+N].. seealso:: `cf.Field.cyclic`, `cf.Field.iscyclic`, `cf.Field.period`

:Examples 1:

>>> f.autocyclic()

:Returns:

   `None`

'''
        # List functionality
        if self._list:
            for f in self:
                f.autocyclic()
            return

        dims = self.dims('X')

        if len(dims) != 1:
            return

        key, dim = dims.popitem()

        if not self.Units.islongitude:
            if dim.getprop('standard_name', None) not in ('longitude', 'grid_longitude'):
                self.cyclic(key, iscyclic=False)
                return

        if not dim.hasbounds:
            self.cyclic(key, iscyclic=False)
            return
        
        bounds = dim.bounds
        if not bounds._hasData:
            self.cyclic(key, iscyclic=False)
            return 
        
        period = Data(360, 'degrees')
        if abs(bounds.datum(-1) - bounds.datum(0)) != period:
            self.cyclic(key, iscyclic=False)
            return

        self.cyclic(key, iscyclic=True, period=period)
    #--- End: def

    def sort(self, cmp=None, key=None, reverse=False):
        '''Sort the field, viewed as a single element field list, in place.

Note that ``f.sort(cmp, key, reverse)`` is equivalent to ``f``, thus
providing compatiblity with a single element field list.

.. versionadded:: 1.0.4

.. seealso:: `reverse`, `cf.FieldList.sort`, :py:obj:`sorted`

:Examples 1:

>>> f.sort()

:Parameters:

    cmp : function, optional
        Specifies a custom comparison function of two arguments
        (iterable elements) which should return a negative, zero or
        positive number depending on whether the first argument is
        considered smaller than, equal to, or larger than the second
        argument. The default value is `None`.
        
          *Example:*
            ``cmp=lambda x,y: cmp(x.lower(), y.lower())``.

    key : function, optional
        Specifies a function of one argument that is used to extract a
        comparison key from each list element. The default value is
        `None` (compare the elements directly).

          *Example:*
            ``key=str.lower``.

    reverse : bool, optional
        If set to True, then the list elements are sorted as if each
        comparison were reversed.

:Returns:

    `None`

:Examples 2:

>>> id0 = id(f)
>>> f.sort()
>>> id0 == id(f)
True
>>> g = cf.FieldList(f)
>>> id0 = id(g)
>>> g.sort()
>>> id0 == id(g)
True

        '''
        return
    #--- End: def

    def squeeze(self, axes=None, i=False, **kwargs):
        '''{+Fef,}Remove size 1 axes from the data array.

By default all size 1 axes are removed, but particular size 1 axes may
be selected for removal.

{+Fef,}The axes are selected with the *axes* parameter.

Squeezed axes are not removed from the coordinate and cell measure
objects, nor are they removed from the domain. To completely remove
axes, use the `remove_axes` method.

.. seealso:: `expand_dims`, `flip`, `remove_axes`, `transpose`,
             `unsqueeze`

:Examples 1:

Remove all size axes from the data array:

>>> g = f.squeeze()

Remove the size 1 time axis:

>>> g = f.squeeze('T')

:Parameters:

    {+axes, kwargs}

    {+i}

:Returns:

    out : cf.{+Variable}
        {+Fef,}The squeezed field.

:Examples 2:

        '''     
        # List functionality
        if self._list:
            kwargs2 = self._parameters(locals())
            return self._list_method('squeeze', kwargs2)

        domain = self.domain
        data_axes = domain.data_axes()

        if axes is None and not kwargs:
            axes_sizes = domain._axes_sizes
            axes = [axis for axis in data_axes if axes_sizes[axis] == 1]
        else:
            axes = domain.axes(axes, **kwargs).intersection(data_axes)

        iaxes = [data_axes.index(axis) for axis in axes]      

        # Squeeze the field's data array
        f = super(Field, self).squeeze(iaxes, i=i)

        f.domain._axes['data'] = [axis for axis in data_axes
                                  if axis not in axes]
        return f
    #--- End: def

    def transpose(self, axes=None, i=False, **kwargs):
        '''{+Fef,}Permute the axes of the data array.

By default the order of the axes is reversed, but any ordering may be
specified by selecting the axes of the output in the required order.

{+Fef,}The axes are selected with the *axes* parameter.

.. seealso:: `expand_dims`, `flip`, `squeeze`, `transpose`, `unsqueeze`

:Examples 1:

Reverse the order of the axes:

>>> g = f.transpose()

Specify a particular axes order:

>>> g = f.transpose(['T', 'X', 'Y'])

.. seealso:: `axes`, `expand_dims`, `flip`, `squeeze`, `unsqueeze`

:Parameters:

    {+axes, kwargs}

    {+i}

:Returns:

    out : cf.{+Variable}
        {+Fef,}, the transposed field.

:Examples 2:

>>> f.items()
{'dim0': <CF DimensionCoordinate: time(12) noleap>,
 'dim1': <CF DimensionCoordinate: latitude(64) degrees_north>,
 'dim2': <CF DimensionCoordinate: longitude(128) degrees_east>,
 'dim3': <CF DimensionCoordinate: height(1) m>}
>>> f.data_axes()
['dim0', 'dim1', 'dim2']
>>> f.transpose()
>>> f.transpose(['Y', 'T', 'X'])
>>> f.transpose(['latitude', 'time', 'longitude'])
>>> f.transpose([1, 0, 2])
>>> f.transpose((1, 'time', 'dim2'))

        '''     
        # List functionality
        if self._list:
            kwargs2 = self._parameters(locals())
            return self._list_method('transpose', kwargs2)
 
        domain = self.domain
        data_axes = domain.data_axes()

        if axes is None and not kwargs:
            axes2 = data_axes[::-1]
            iaxes = range(self.ndim-1, -1, -1)
        else:
            axes2 = domain.axes(axes, ordered=True, **kwargs)
            if set(axes2) != set(data_axes):
                raise ValueError("Can't transpose %r: Bad axis specification: %r" %
                                 (self.__class__.__name__, axes))
            
            iaxes = [data_axes.index(axis) for axis in axes2]
        #---- End: if
            
        # Transpose the field's data array
        f = super(Field, self).transpose(iaxes, i=i)

        # Reorder the list of axes in the domain
        f.domain._axes['data'] = axes2

        return f
    #--- End: def

    def unsqueeze(self, axes=None, i=False, **kwargs):
        '''{+Fef,}Insert size 1 axes into the data array.

By default all size 1 domain axes which are not spanned by the field's
data array are inserted, but existing size 1 axes may be selected for
insertion.

{+Fef,}The axes are selected with the *axes* parameter.

The axes are inserted into the slowest varying data array positions.

.. seealso:: `expand_dims`, `flip`, `squeeze`, `transpose`

:Examples 1:

Insert size all size 1 axes:

>>> g = f.unsqueeze()

Insert size 1 time axes:

>>> g = f.unsqueeze('T', size=1)

:Parameters:

    {+axes, kwargs}

    {+i}

:Returns:

    out : cf.{+Variable}
        {+Fef,}The unsqueezed field.

:Examples 2:

>>> print f
Data            : air_temperature(time, latitude, longitude)
Cell methods    : time: mean
Dimensions      : time(1) = [15] days since 1860-1-1
                : latitude(73) = [-90, ..., 90] degrees_north
                : longitude(96) = [0, ..., 356.25] degrees_east
                : height(1) = [2] m
Auxiliary coords:
>>> f.unsqueeze()
>>> print f
Data            : air_temperature(height, time, latitude, longitude)
Cell methods    : time: mean
Dimensions      : time(1) = [15] days since 1860-1-1
                : latitude(73) = [-90, ..., 90] degrees_north
                : longitude(96) = [0, ..., 356.25] degrees_east
                : height(1) = [2] m
Auxiliary coords:

        '''     
        # List functionality
        if self._list:
            kwargs2 = self._parameters(locals())
            return self._list_method('unsqueeze', kwargs2)
 
        domain = self.domain

        data_axes = domain.data_axes()
        axes = domain.axes(axes, size=1, **kwargs).difference(data_axes)

        if i:
            f = self
        else:
            f = self.copy()

        for axis in axes:
            f.expand_dims(0, axis, i=True)

        return f
    #--- End: def

    def aux(self, items=None, axes=None, axes_all=None,
            axes_subset=None, axes_superset=None, exact=False,
            inverse=False, match_and=True, ndim=None, key=False,
            copy=False):
        '''{+Fef,}Return an auxiliary coordinate object, or its domain identifier.

In this documentation, an auxiliary coordinate object is referred to
as an item.

{+item_selection}

{+item_criteria}

If no unique item can be found then `None` is returned.

To find multiple items, use the `{+name}s` method.

Note that ``f.aux(inverse=False, **kwargs)`` is equivalent to
``f.item(role='a', inverse=False, **kwargs)``.
 

.. seealso:: `auxs`, `measure`, `coord`, `ref`, `dim`, `item`,
             `remove_item`

:Examples 1:

A latitude item could potentially be selected with any of:

>>> a = f.{+name}('Y')
>>> a = f.{+name}('latitude')
>>> a = f.{+name}('long_name:latitude')
>>> a = f.{+name}('aux1')
>>> a = f.{+name}(axes_all='Y')

:Parameters:

    {+items}

    {+ndim}

    {+axes}

    {+axes_all}

    {+axes_subset}

    {+axes_superset}

    {+match_and}

    {+exact}
       
    {+inverse}

    {+key}
        
    {+copy}

:Returns:

[+1]    out : cf.AuxiliaryCoordinate or str or None
[+N]    out : list
           {+Fef,}The unique auxiliary coordinate object or its domain
           identifier or, if there is not one, `None`.

:Examples 2:

        '''
        kwargs2 = self._parameters(locals())
        return self.domain.item(role='a', _restrict_inverse=True, **kwargs2)
    #--- End: def

    def measure(self, items=None, axes=None, axes_all=None,
                axes_subset=None, axes_superset=None, exact=False,
                inverse=False, match_and=True, ndim=None,
                key=False, copy=False):
        '''{+Fef,}Return a cell measure object, or its domain identifier.

In this documentation, a cell measure object is referred to as an
item.

{+item_selection}

If no unique item can be found then `None` is returned.

To find multiple items, use the `{+name}s` method.

Note that ``f.measure(inverse=False, **kwargs)`` is equivalent to
``f.item(role='m', inverse=False, **kwargs)``.

.. seealso:: `aux`, `measures`, `coord`, `ref`, `dims`, `item`,
             `remove_item`

:Parameters:

    {+items}

    {+axes}

    {+axes_all}

    {+axes_subset}

    {+axes_superset}

    {+ndim}

    {+match_and}

    {+exact}
       
    {+inverse}

    {+key}
        
    {+copy}

:Returns:

[+1]    out :
[+N]    out : list
        {+Fef,}The unique cell measure object or its domain identifier or, if
        there is not one, `None`.
        
:Examples 2:

>>> f.measure('area')
<CF CellMeasure: area(73, 96) m 2>

        '''
        kwargs2 = self._parameters(locals())
        return self.domain.item(role='m', _restrict_inverse=True, **kwargs2)
    #--- End: def   

    def coord(self, items=None, axes=None, axes_all=None,
              axes_subset=None, axes_superset=None, ndim=None, match_and=True, 
              exact=False,
              inverse=False, key=False, copy=False):
        '''

{+Fef,}Return a dimension or auxiliary coordinate object, or its domain identifier.

In this documentation, a dimension or auxiliary coordinate object is
referred to as an item.

{+item_selection}

If no unique item can be found then `None` is returned.

To find multiple items, use the `{+name}s` method.

Note that ``f.coord(inverse=False, **kwargs)`` is equivalent to
``f.item(role='da', inverse=False, **kwargs)``.

.. seealso:: `aux`, `coords`, `dim`, `item`, `measure`, `ref`,
             `remove_item`,

:Examples 1:

:Parameters:

    {+items}

    {+axes}

    {+axes_all}

    {+axes_subset}

    {+axes_superset}

    {+ndim}

    {+match_and}

    {+exact}
       
    {+inverse}

    {+key}

    {+copy}

:Returns:

[+1]    out : 
[+N]    out : list
        {+Fef,}The unique dimension or auxiliary coordinate object or
        its domain identifier or, if there is not one, `None`.

:Examples 2:

'''
        kwargs2 = self._parameters(locals())
        return self.domain.item(role=('d', 'a'), _restrict_inverse=True,
                                **kwargs2)
    #--- End: def

    def dim(self, items=None, axes=None, axes_all=None,
            axes_subset=None, axes_superset=None, ndim=None,
            match_and=True, exact=False, inverse=False,
            key=False, copy=False):
        '''

Return a dimension coordinate object, or its domain identifier.

In this documentation, a dimension coordinate object is referred to as
an item.

{+item_selection}

If no unique item can be found then `None` is returned.

To find multiple items, use the `{+name}s` method.

Note that ``f.{+name}(inverse=False, **kwargs)`` is equivalent to
``f.item(role='d', inverse=False, **kwargs)``.

.. seealso:: `aux`, `measure`, `coord`, `ref`, `dims`, `item`,
             `remove_item`

:Examples 1:

A latitude item could potentially be selected with any of:

>>> d = f.{+name}('Y')
>>> d = f.{+name}('latitude')
>>> d = f.{+name}('long_name:latitude')
>>> d = f.{+name}('dim1')
>>> d = f.{+name}(axes_all='Y')

:Parameters:

    {+items}

    {+ndim}

    {+axes}

    {+axes_all}

    {+axes_subset}

    {+axes_superset}

    {+match_and}

    {+exact}
       
    {+inverse}

    {+key}

    {+copy}
        
:Returns:

[+1]    out : 
[+N]    out : list
        {+Fef,}The unique dimension coordinate object or its domain
        identifier or, if there is not one, `None`.

:Examples 2:

'''
        kwargs2 = self._parameters(locals())
        return self.domain.item(role='d', _restrict_inverse=True, **kwargs2)
    #--- End: def

#    def transform(self, *args, **kwargs):
#        raise NotImplementedError("Deprecated. Use cf.Field.ref instead.")

    def ref(self,items=None, exact=False, inverse=False, match_and=True,
            key=False, copy=False):
        '''{+Fef,}Return a coordinate reference object, or its domain identifier.

In this documentation, a coordinate reference object is referred to as
an item.

{+item_selection}

If no unique item can be found then `None` is returned.

To find multiple items, use the `{+name}s` method.

Note that ``f.ref(inverse=False, **kwargs)`` is equivalent to
``f.item(role='r', inverse=False, **kwargs)``.

.. seealso:: `aux`, `measure`, `coord`, `ref`, `dims`, `item`,
             `remove_item`

:Examples 1:

A latitude item could potentially be selected with any of:

>>> c = f.ref('rotated_latitude_longitude')
>>> c = f.ref('ref1')

:Parameters:

    {+items}

    {+ndim}

    {+axes}

    {+axes_all}

    {+axes_subset}

    {+axes_superset}

    {+match_and}

    {+exact}
       
    {+inverse}

    {+key}

    {+copy}
        
:Returns:

[+1]    out : 
[+N]    out : list
        {+Fef,}The unique dimension coordinate object or its domain
        identifier or, if there is not one, `None`.

:Examples 2:

        '''
        kwargs2 = self._parameters(locals())
        return self.domain.item(role='r', _restrict_inverse=True, **kwargs2)
    #--- End: def

    def auxs(self, items=None, axes=None, axes_all=None,
             axes_subset=None, axes_superset=None, ndim=None, match_and=True, 
             exact=False, inverse=False, copy=False):
        '''Return auxiliary coordinate objects.

In this documentation, an auxiliary coordinate object is referred to
as an item.

{+item_selection}

{+item_criteria}

Note that ``f.{+name}(inverse=False, **kwargs)`` is equivalent to
``f.items(role='a', inverse=False, **kwargs)``.
 
.. seealso:: `aux`, `axes`, `measures` , `refs`, `coords`, `dims`,
             `items`, `remove_items`
:Examples 1:

To select all auxiliary coordinate objects:

>>> d = f.auxs()

:Parameters:

    {+items}

          *Example:* 

            >>> x = f.items(['aux1',
            ...             'time',
            ...             {'units': 'degreeN', 'long_name': 'foo'}])
            >>> y = {}
            >>> for items in ['aux1', 'time', {'units': 'degreeN', 'long_name': 'foo'}]:
            ...     y.update(f.items(items))
            ...
            >>> set(x) == set(y)
            True

    {+axes}

    {+axes_all}

    {+axes_subset}

    {+axes_superset}

    {+ndim}

    {+match_and}

    {+exact}

    {+inverse}

    {+copy}

:Returns:

    out : dict
        A dictionary whose keys are domain item identifiers with
        corresponding values of auxiliary coordinates of the
        domain. The dictionary will be empty if no items were
        selected.

:Examples:

        '''
        kwargs2 = self._parameters(locals())
        return self.domain.items(role='a', _restrict_inverse=True, **kwargs2)
    #--- End: def

    def measures(self, items=None, axes=None, axes_all=None,
                 axes_subset=None, axes_superset=None, ndim=None, 
                 match_and=True, exact=False, inverse=False, copy=False):
        '''Return cell measure objects.

In this documentation, a cell measure object is referred to as an
item.

{+item_selection}

{+item_criteria}

Note that ``f.{+name}(inverse=False, **kwargs)`` is equivalent to
``f.items(role='m', inverse=False, **kwargs)``.
 
.. seealso:: `auxs`, `coords`, `dims`, `items`, `measure`, `refs`, 
             `remove_items`

:Examples 1:

To select all cell measure objects:

>>> d = f.measures()

:Parameters:

    {+items}

    {+axes}

    {+axes_all}

    {+axes_subset}

    {+axes_superset}

    {+ndim}

    {+match_and}

    {+exact}

    {+inverse}

    {+copy}

:Returns:

    out : dict
        A dictionary whose keys are domain item identifiers with
        corresponding values of cell measure objects of the
        domain. The dictionary will be empty if no items were
        selected.


:Examples 2:

        '''
        kwargs2 = self._parameters(locals())
        return self.domain.items(role='m', _restrict_inverse=True, **kwargs2)
    #--- End: def

    def coords(self, items=None, axes=None, axes_all=None,
               axes_subset=None, axes_superset=None, ndim=None,
               match_and=True, exact=False, inverse=False, copy=False):
        '''Return dimension and auxiliary coordinate objects of the domain.

.. seealso:: `auxs`, `axes`, `measures`, `coord`, `refs`, `dims`,
             `items`, `remove_items`

:Parameters:

    {+items}

    {+axes}

    {+axes_all}

    {+axes_subset}

    {+axes_superset}

    {+ndim}

    {+match_and}

    {+exact}

    {+inverse}

    {+copy}

:Returns:

    out : dict
        A dictionary whose keys are domain item identifiers with
        corresponding values of coordinates of the domain. The
        dictionary may be empty.

:Examples:

        '''      
        kwargs2 = self._parameters(locals())
        return self.domain.items(role=('d', 'a'), _restrict_inverse=True,
                                 **kwargs2)
    #--- End: def

    def dims(self, items=None, axes=None, axes_all=None,
             axes_subset=None, axes_superset=None, ndim=None,
             match_and=True, exact=False, inverse=False, copy=False):
        '''Return dimension coordinate objects.

In this documentation, a dimension coordinate object is referred to as
an item.

{+item_selection}

{+item_criteria}

Note that ``f.{+name}(inverse=False, **kwargs)`` is equivalent to
``f.items(role='d', inverse=False, **kwargs)``.
 
.. seealso:: `auxs`, `axes`, `measures`, `refs`, `coords`, `dim`,
             `items`, `remove_items`

:Examples 1:

To select all dimension coordinate objects:

>>> d = f.dims()

:Parameters:

    {+items}

    {+axes}

    {+axes_all}

    {+axes_subset}

    {+axes_superset}

    {+ndim}

    {+match_and}

    {+exact}

    {+inverse}

    {+copy}

:Returns:

    out : dict
        A dictionary whose keys are domain item identifiers with
        corresponding values of items of the domain. The dictionary
        may be empty.

:Examples:

        '''
        kwargs2 = self._parameters(locals())
        return self.domain.items(role='d', _restrict_inverse=True, **kwargs2)
    #--- End: def

#    def transforms(self, items=None, key=False, **kwargs):
#        '''
#Deprecated. Use `cf.Field.refs` instead.
#'''
#        raise NotImplementedError("Deprecated. Use cf.Field.refs instead.")
#    #--- End: def

    def refs(self, items=None, exact=False, inverse=False, match_and=True, 
             copy=False):
        '''Return coordinate reference objects.

In this documentation, a coordinate reference object is referred to as
an item.

{+item_selection}

Note that ``f.{+name}(inverse=False, **kwargs)`` is equivalent to
``f.items(role='r', inverse=False, **kwargs)``.
 
.. seealso:: `auxs`, `coords`, `dims`, `items`, `measures`, `ref`, 
             `remove_items`

:Examples 1:

To select all coordinate reference objects:

>>> d = f.refs()

:Parameters:
         
    {+items}

          *Example:* 

            >>> x = f.items(['ref1', 'latitude_longitude'])
            >>> y = {}
            >>> for items in ['ref1', 'latitude_longitude']:
            ...     y.update(f.items(items))
            ...
            >>> set(x) == set(y)
            True

    {+match_and}

    {+exact}
       
    {+inverse}

    {+copy}

:Returns:
 
    out :
        A dictionary whose keys are domain item identifiers with
        corresponding values of coordinate references of the
        domain. The dictionary may be empty.

:Examples:

        '''  
        kwargs2 = self._parameters(locals())
        return self.domain.items(role='r', _restrict_inverse=True, **kwargs2)
    #--- End: def
    
    def item(self, items=None, role=None, axes=None, axes_all=None,
             axes_subset=None, axes_superset=None, exact=False,
             inverse=False, match_and=True, ndim=None,
             key=False, copy=False):
        '''Return an item, or its domain identifier, from the field.

An item is either a dimension coordinate, an auxiliary coordinate, a
cell measure or a coordinate reference object.

{+item_selection}
 
If no unique item can be found then `None` is returned.

To find multiple items, use the `~cf.Field.{+name}s` method.

.. seealso:: `aux`, `measure`, `coord`, `ref`, `dim`, `item_axes`,
             `items`, `remove_item`

:Examples 1:

>>> 

:Parameters:

    {+items}

    {+role}

    {+axes}

    {+axes_all}

    {+axes_subset}

    {+axes_superset}

    {+ndim}

    {+match_and}

    {+exact}
       
    {+inverse}

    {+key}

    {+copy}

:Returns:

    out : 
        The unique item or its domain identifier or, if there is no
        unique item, `None`.

:Examples:

        '''
        kwargs2 = self._parameters(locals())
        return self.domain.item(**kwargs2)
    #--- End: def

    def axis_name(self, axes=None, **kwargs):
        '''Return the canonical name for an axis.

{+axis_selection}

.. seealso:: `axis`, `axis_size`, `item`

:Parameters:

    {+axes, kwargs}

:Returns:

    out : str
        The canonical name for the axis.

:Examples:

>>> f.axis_name('dim0')
'time'
>>> f.axis_name('X')
'domain%dim1'
>>> f.axis_name('long_name%latitude')
'ncdim%lat'

        '''        
        kwargs2 = self._parameters(locals())
        return self.domain.axis_name(**kwargs2)
    #-- End: def

    def axis_size(self, axes=None, **kwargs):
        '''Return the size of a domain axis.

{+axis_selection}

.. seealso:: `axis`, `axis_name`, `axes_sizes`, `axis_identity`

:Parameters:

    {+axes, kwargs}

:Returns:
    
    out : int
        The size of the axis.

:Examples:

>>> f
<CF Field: eastward_wind(time(3), air_pressure(5), latitude(110), longitude(106)) m s-1>
>>> f.axis_size('longitude')
106
>>> f.axis_size('Z')
5

        '''
        kwargs2 = self._parameters(locals())
        return self.domain.axis_size(**kwargs2)
    #--- End: def

    def axes_sizes(self, axes=None, size=None, key=False, **kwargs):
        '''Return the sizes of domain axes.

{+axis_selection}

:Examples 1:

>>> x = f.axes_sizes()

:Parameters:

    {+axes, kwargs}

          *Example:*

            >>> x = f.axes(['dim2', 'time', {'units': 'degree_north'}])
            >>> y = set()
            >>> for axes in ['dim2', 'time', {'units': 'degree_north'}]:
            ...     y.update(f.axes(axes))
            ...
            >>> x == y
            True
 
    {+size}
             
    key : bool, optional
        If True then identify each axis by its domain identifier
        rather than its name.

:Returns:
    
    out : dict
        The sizes of the each selected domain axis.

:Examples 2:

>>> f
<CF Field: eastward_wind(time(3), air_pressure(5), latitude(110), longitude(106)) m s-1>
>>> f.axes_sizes()
{'air_pressure': 5, 'latitude': 110, 'longitude': 106, 'time': 3}
>>> f.axes_sizes(size=3)
{'time': 3}
>>> f.axes_sizes(size=cf.lt(10), key=True)
{'dim0': 3, 'dim1': 5}
>>> f.axes_sizes('latitude')
{'latitude': 110}

        '''
        kwargs2 = self._parameters(locals())
        return self.domain.axes_sizes(**kwargs2)
    #---End: def

    def axes(self, axes=None, size=None, ordered=False, **kwargs):
        '''Return domain axis identifiers from the field.

The output is a set of domain axis identifiers, which may be empty.

{+axis_selection}

.. seealso:: `axis`, `data_axes`, `item_axes`, `items`, `remove_axes`

:Parameters:

    {+axes, kwargs}

          *Example:*

            >>> x = f.axes(['dim2', 'time', {'units': 'degree_north'}])
            >>> y = set()
            >>> for axes in ['dim2', 'time', {'units': 'degree_north'}]:
            ...     y.update(f.axes(axes))
            ...
            >>> x == y
            True
 
    {+size}

    ordered : bool, optional
        Return an ordered list of axes instead of an unordered
        set. The order of the list will reflect any ordering specified
        by the *axes* and *kwargs* parameters.

          *Example:*
            If the data array axes, as returned by the field's
            `data_axes` method, are ``['dim0', 'dim1', 'dim2']``, then
            ``f.axes([2, 0, 1, 2])`` will return ``set(['dim0',
            'dim1', 'dim2'])``, but ``f.axes([2, 0, 1, 2],
            ordered=True)`` will return ``['dim2', 'dim0', 'dim1',
            'dim2']``.

:Returns:

    out : set or list
        A set of domain axis identifiers, or a list if *ordered* is
        True. The set or list may be empty.

:Examples:

All axes and their identities:

>>> f.axes()
set(['dim0', 'dim1', 'dim2', 'dim3'])
>>> dict([(axis, f.domain.axis_name(axis)) for axis in f.axes()])
{'dim0': time(12)
 'dim1': height(19)
 'dim2': latitude(73)
 'dim3': longitude(96)}

Axes which are not spanned by the data array:

>>> f.axes().difference(f.data_axes())

        '''
        kwargs2 = self._parameters(locals())
        return self.domain.axes(**kwargs2)
    #--- End: def

    def axis(self, axes=None, size=None, **kwargs):
        '''Return a domain axis identifier from the field.

{+axis_selection}

.. seealso:: `axes`, `data_axes`, `item_axes`, `item`, `remove_axis`

:Examples 1:

>>> a = f.axis('time')

:Parameters:

    {+axes, kwargs}
 
    {+size}

:Returns:

    out : str or None
        The domain identifier of the unique axis or, if there isn't
        one, `None`.

:Examples 2:

>>> f
<CF Field: air_temperature(time(12), latitude(64), longitude(128)) K>
>>> f.data_axes()
['dim0', 'dim1', 'dim2']
>>> f.axis('time')
'dim0'
>>> f.axis('Y')
'dim1'
>>> f.axis(size=64)
'dim1'
>>> f.axis('X', size=128)
'dim2'
>>> print f.axis('foo')
None
>>> print f.axis('T', size=64)
None

        '''
        kwargs2 = self._parameters(locals())
        return self.domain.axis(**kwargs2)
    #--- End: def

    def insert_axis(self, size, key=None, replace=True):
        '''Insert an axis into the domain in place.

.. seealso:: `insert_aux`, `insert_measure`, `insert_ref`,
             `insert_data`, `insert_dim`

:Parameters:

    size : int
        The size of the new axis.

    key : str, optional
        The domain identifier for the new axis. By default a new,
        unique identifier is generated.
  
    replace : bool, optional
        If False then do not replace an existing axis with the same
        identifier but a different size. By default an existing axis
        with the same identifier is changed to have the new size.

:Returns:

    out :
        The domain identifier of the new axis.


:Examples:

>>> f.insert_axis(1)
>>> f.insert_axis(90, key='dim4')
>>> f.insert_axis(23, key='dim0', replace=False)

        '''
        kwargs2 = self._parameters(locals())
        return self.domain.insert_axis(**kwargs2)
    #--- End: def

    def insert_aux(self, item, key=None, axes=None, copy=True, replace=True):
        '''Insert an auxiliary coordinate object into the domain in place.

.. seealso:: `insert_axis`, `insert_measure`, `insert_data`,
             `insert_dim`, `insert_ref`

:Parameters:

    item : cf.AuxiliaryCoordinate or cf.Coordinate or cf.DimensionCoordinate
        The new auxiliary coordinate object. If it is not already a
        auxiliary coordinate object then it will be converted to one.

    key : str, optional
        The domain identifier for the *item*. By default a new, unique
        identifier will be generated.

    axes : sequence of str, optional
        The ordered list of axes for the *item*. Each axis is given by
        its domain identifier. By default the axes are assumed to be
        ``'dim0'`` up to ``'dimM-1'``, where ``M-1`` is the number of
        axes spanned by the *item*.

    copy: bool, optional
        If False then the *item* is not copied before insertion. By
        default it is copied.
      
    replace : bool, optional
        If False then do not replace an existing auxiliary coordinate
        object of domain which has the same identifier. By default an
        existing auxiliary coordinate object with the same identifier
        is replaced with *item*.
    
:Returns:

    out : str
        The domain identifier for the inserted *item*.

:Examples:

>>>

        '''
        kwargs2 = self._parameters(locals())
        return self.domain.insert_aux(**kwargs2)
    #--- End: def

    def insert_measure(self, item, key=None, axes=None, copy=True, replace=True):
        '''

Insert an cell measure object into the domain in place.

.. seealso:: `insert_axis`, `insert_aux`, `insert_data`, `insert_dim`,
             `insert_ref`

:Parameters:

    item : cf.CellMeasure
        The new cell measure object.

    key : str, optional
        The domain identifier for the *item*. By default a new, unique
        identifier will be generated.

    axes : sequence of str, optional
        The ordered list of axes for the *item*. Each axis is given by
        its domain identifier. By default the axes are assumed to be
        ``'dim0'`` up to ``'dimM-1'``, where ``M-1`` is the number of
        axes spanned by the *item*.

    copy: bool, optional
        If False then the *item* is not copied before insertion. By
        default it is copied.
      
    replace : bool, optional
        If False then do not replace an existing cell measure object
        of domain which has the same identifier. By default an
        existing cell measure object with the same identifier is
        replaced with *item*.
    
:Returns:

    out : 
        The domain identifier for the *item*.

:Examples:

>>>

'''
        kwargs2 = self._parameters(locals())
        return self.domain.insert_measure(**kwargs2)
    #--- End: def

    def insert_dim(self, item, key=None, axis=None, copy=True, replace=True):
        '''Insert a dimension coordinate object into the domain in place.

.. seealso:: `insert_aux`, `insert_axis`, `insert_measure`,
             `insert_data`, `insert_ref`

:Parameters:

    item : cf.DimensionCoordinate or cf.Coordinate or cf.AuxiliaryCoordinate
        The new dimension coordinate object. If it is not already a
        dimension coordinate object then it will be converted to one.

    axis : str, optional
        The axis for the *item*. The axis is given by its domain
        identifier. By default the axis will be the same as the given
        by the *key* parameter.

    key : str, optional
        The domain identifier for the *item*. By default a new, unique
        identifier will be generated.

    copy: bool, optional
        If False then the *item* is not copied before insertion. By
        default it is copied.
      
    replace : bool, optional
        If False then do not replace an existing dimension coordinate
        object of domain which has the same identifier. By default an
        existing dimension coordinate object with the same identifier
        is replaced with *item*.
    
:Returns:

    out : 
        The domain identifier for the inserted *item*.

:Examples:

>>>

        '''
        kwargs2 = self._parameters(locals())
        key = self.domain.insert_dim(**kwargs2)

        self.autocyclic()

        return key
    #--- End: def

    def insert_ref(self, item, key=None, copy=True, replace=True):
        '''Insert a coordinate reference object into the domain in place.

.. seealso:: `insert_axis`, `insert_aux`, `insert_measure`,
             `insert_data`, `insert_dim`
             
:Parameters:

    item : cf.CoordinateReference
        The new coordinate reference object.

    key : str, optional
        The domain identifier for the *item*. By default a new, unique
        identifier will be generated.

    copy: bool, optional
        If False then the *item* is not copied before insertion. By
        default it is copied.
      
    replace : bool, optional
        If False then do not replace an existing coordinate reference object of
        domain which has the same identifier. By default an existing
        coordinate reference object with the same identifier is replaced with
        *item*.
    
:Returns:

    out : 
        The domain identifier for the *item*.


:Examples:

>>>

        '''
        kwargs2 = self._parameters(locals())
        return self.domain.insert_ref(**kwargs2)
    #--- End: def

    def item_axes(self, items=None, role=None, axes=None,
                  axes_all=None, axes_subset=None, axes_superset=None,
                  exact=False, inverse=False, match_and=True,
                  ndim=None):
        '''Return the axes of a domain item of the field.

An item is a dimension coordinate, an auxiliary coordinate, a cell
measure or a coordinate reference object.

.. seealso:: `axes`, `data_axes`, `item`, `items_axes`

:Parameters:

    {+items}

    {+role}

    {+axes}

    {+axes_all}

    {+axes_subset}

    {+axes_superset}

    {+ndim}

    {+match_and}

    {+exact}
       
    {+inverse}

:Returns:

    out : list or None
        The ordered list of axes for the item or, if there is no
        unique item or the item is a coordinate reference then `None`
        is returned.

:Examples:

        '''    
        kwargs2 = self._parameters(locals())
        return self.domain.item_axes(**kwargs2)
    #--- End: def

    def items_axes(self, items=None, role=None, axes=None,
                   axes_all=None, axes_subset=None,
                   axes_superset=None, exact=False, inverse=False,
                   match_and=True, ndim=None):
        '''Return the axes of domain items of the field.

An item is a dimension coordinate, an auxiliary coordinate, a cell
measure or a coordinate reference object.

.. seealso:: `axes`, `data_axes`, `item_axes`, `items`

:Parameters:

    {+items}

    {+role}

    {+axes}

    {+axes_all}

    {+axes_subset}

    {+axes_superset}

    {+ndim}

    {+match_and}

    {+exact}
       
    {+inverse}

:Returns:

    out : dict
        A dictionary whose keys are domain item identifiers with
        corresponding values of the ordered list of axes for each
        selected. The dictionary may be empty.

:Examples:

>>> f.domain.items_axes()
{'aux0': ['dim2', 'dim3'],
 'aux1': ['dim2', 'dim3'],
 'dim0': ['dim0'],
 'dim1': ['dim1'],
 'dim2': ['dim2'],
 'dim3': ['dim3']}

>>> f.domain.items_axes(role='d')
{'dim0': ['dim0'],
 'dim1': ['dim1'],
 'dim2': ['dim2'],
 'dim3': ['dim3']}

        '''    
        kwargs2 = self._parameters(locals())
        return self.domain.items_axes(**kwargs2)
    #--- End: def

    def items(self, items=None, role=None, axes=None, axes_all=None,
              axes_subset=None, axes_superset=None, ndim=None, match_and=True,
              exact=False, inverse=False, copy=False):
        '''Return domain items from the field.

An item is a dimension coordinate, an auxiliary coordinate, a cell
measure or a coordinate reference object.

The output is a dictionary whose key/value pairs are domain
identifiers with corresponding values of items of the domain.

{+item_selection}

{+items_criteria}

.. seealso:: `auxs`, `axes`, `measures`, `coords`, `dims`, `item`, `match`
             `remove_items`, `refs`

:Examples 1:

Select all items whose identities (as returned by their `!identity`
methods) start "height":

>>> f.items('height')

Select all items which span only one axis:

>>> f.items(ndim=1)

Select all cell measure objects:

>>> f.items(role='m')

Select all items which span the "time" axis:

>>> f.items(axes='time')

Select all CF latitude coordinate objects:

>>> f.items('Y')

Select all multidimensional dimension and auxiliary coordinate objects
which span at least the "time" and/or "height" axes and whose long
names contain the string "qwerty":

>>> f.items('long_name:.*qwerty', 
...         role='da',
...         axes=['time', 'height'],
...         ndim=cf.ge(2))

:Parameters:

    {+items}

          *Example:* 

            >>> x = f.items(['aux1',
            ...             'time',
            ...             {'units': 'degreeN', 'long_name': 'foo'}])
            >>> y = {}
            >>> for items in ['aux1', 'time', {'units': 'degreeN', 'long_name': 'foo'}]:
            ...     y.update(f.items(items))
            ...
            >>> set(x) == set(y)
            True

    {+role}

    {+axes}

    {+axes_all}

    {+axes_subset}

    {+axes_superset}

    {+ndim}

    {+match_and}

    {+exact}

    {+inverse}

          *Example:*
            ``f.items(role='da', inverse=True)`` selects the same
            items as ``f.items(role='mr')``.

    {+copy}

:Returns:

    out : dict
        A dictionary whose keys are domain item identifiers with
        corresponding values of items of the domain. The dictionary
        may be empty.

:Examples:

        '''
        kwargs2 = self._parameters(locals())
        return self.domain.items(**kwargs2)
    #--- End: def

    def period(self, axes=None, **kwargs):
        '''Return the period of an axis.

Note that a non-cyclic axis may have a defined period.

.. versionadded:: 1.0

.. seealso:: `axis`, `cyclic`, `iscyclic`,
             `cf.DimensionCoordinate.period`

:Parameters:

    {+axes, kwargs}

:Returns:

    out : cf.Data or None
        The period of the cyclic axis's dimension coordinates, or
        `None` no period has been set.

:Examples 2:

>>> f.cyclic()
{}
>>> print f.period('X')
None
>>> f.dim('X').Units
<CF Units: degrees_east>
>>> f.cyclic('X', period=360)
{}
>>> print f.period('X')
<CF Data: 360.0 'degrees_east'>
>>> f.cyclic('X', False)
{'dim3'}
>>> print f.period('X')
<CF Data: 360.0 'degrees_east'>
>>> f.dim('X').period(None)
<CF Data: 360.0 'degrees_east'>
>>> print f.period('X')
None

        '''
        axis = self.domain.axis(axes=axes, **kwargs)
        if axis is None:
            raise ValueError("Can't identify axis")

        dim = self.dim(axis)
        if dim is None:
            return
            
        return dim.period()       
    #--- End: def

    def remove_item(self, items=None, role=None, axes=None,
                    axes_all=None, axes_subset=None,
                    axes_superset=None, ndim=None, match_and=True,
                    exact=False, inverse=False, key=False, copy=False):
        '''Remove and return a domain item from the field.

An item is either a dimension coordinate, an auxiliary coordinate, a
cell measure or a coordinate reference object of the domain.

The item may be selected with the keyword arguments. If no unique item
can be found then no items are removed and `None` is returned.

.. seealso:: `item`, `remove_axes`, `remove_axis`, `remove_items`

:Parameters:

    {+items}

    {+role}

    {+axes}

    {+axes_all}

    {+axes_subset}

    {+axes_superset}

    {+ndim}

    {+match_and}

    {+exact}
       
    {+inverse}

    {+key}

    {+copy}

:Returns:

    out : 
        The unique item or its domain identifier or, if there is no
        unique item, `None`.

:Examples:

        '''
        kwargs2 = self._parameters(locals())
        return self.domain.remove_item(**kwargs2)
    #--- End: def

    def remove_axes(self, axes=None, size=None, **kwargs):
        '''

Remove and return axes from the field.

By default all axes of the domain are removed, but particular axes may
be selected with the keyword arguments.

The axis may be selected with the keyword arguments. If no unique axis
can be found then no axis is removed and `None` is returned.

If an axis has size greater than 1 then it is not possible to remove
it if it is spanned by the field's data array or any multidimensional
coordinate or cell measure object of the field.

.. seealso:: `axes`, `remove_axis`, `remove_item`, `remove_items`

:Parameters:

    {+axes, kwargs}

    {+size}

:Returns:

    out : set
        The removed axes. The set may be empty.

:Examples:

'''
        domain = self.domain

        axes = domain.axes(axes, size=size, **kwargs)
        if not axes:
            return set()

        size1_data_axes = []
        axes_sizes = domain._axes_sizes
        for axis in axes.intersection(domain.data_axes()):
            if axes_sizes[axis] == 1:
                size1_data_axes.append(axis)
            else:
                raise ValueError(
"Can't remove an axis with size > 1 which is spanned by the data array")
        #---End: for

        if size1_data_axes:
            self.squeeze(size1_data_axes, i=True)

        axes = domain.remove_axes(axes, i=True)

        return axes
    #--- End: def

    def remove_axis(self, axes=None, size=None, **kwargs):
        '''

Remove and return a unique axis from the field.

The axis may be selected with the keyword arguments. If no unique axis
can be found then no axis is removed and `None` is returned.

If the axis has size greater than 1 then it is not possible to remove
it if it is spanned by the field's data array or any multidimensional
coordinate or cell measure object of the field.

.. seealso:: `axis`, `remove_axes`, `remove_item`, `remove_items`

:Parameters:

    {+axes, kwargs}

    {+size}

:Returns:

    out : str
        The domain identifier of the removed axis, or `None` if there
        isn't one.

:Examples:

'''      
        axis = self.domain.axis(axis, size=size, **kwargs)
        if axis is None:
            return

        return self.remove_axes(axis).pop()
    #--- End: def

    def remove_items(self, items=None, role=None, axes=None,
                     axes_all=None, axes_subset=None,
                     axes_superset=None, ndim=None, exact=False,
                     inverse=False, match_and=True):
        '''

Remove and return domain items from the domain.

An item is either a dimension coordinate, an auxiliary coordinate, a
cell measure or a coordinate reference object of the domain.

By default all items of the domain are removed, but particular items
may be selected with the keyword arguments.

.. seealso:: `items`, `remove_axes`, `remove_axis`, `remove_item`

:Parameters:

    {+items}

    {+role}

    {+axes}

    {+axes_all}

    {+axes_subset}

    {+axes_superset}

    {+ndim}

    {+match_and}

    {+exact}

    {+inverse}

:Returns:

    out : dict
        A dictionary whose keys are domain item identifiers with
        corresponding values of the removed items of the domain. The
        dictionary may be empty.

:Examples:

        '''
        kwargs2 = self._parameters(locals())
        return self.domain.remove_items(**kwargs2)
    #--- End: def

    def reverse(self):
        '''L.reverse() -- reverse *IN PLACE*

Note that ``f.reverse()`` is equivalent to ``f``, thus providing
compatiblity with a single element field list.

.. versionadded:: 1.0.4

.. seealso:: `cf.FieldList.reverse`, :py:obj:`reversed`, `sort`

:Examples 1:

>>> f.reverse()

:Returns:

    `None`

:Examples 2:

>>> id0 = id(f)
>>> f.reverse()
>>> id0 == id(f)
True
>>> g = cf.FieldList(f)
>>> id0 = id(g)
>>> g.reverse()
>>> id0 == id(g)
True

'''
        return
    #--- End: def
    
    def roll(self, axes, shift, i=False, **kwargs):
        '''{+Fef,}Roll the field along a cyclic axis.

{+Fef,}A unique axis is selected with the axes and kwargs parameters.

.. versionadded:: 1.0

[+1].. seealso:: `anchor`, `axis`, `cyclic`, `iscyclic`, `period`
[+N].. seealso:: `anchor`, `cf.Field.axis`, `cf.Field.cyclic`,
[+N]             `cf.Field.iscyclic`, `cf.Field.period`

:Parameters:

    {+axes, kwargs}

    shift : int
        The number of places by which the selected cyclic axis is to
        be rolled.

    {+i}

:Returns:

    out : cf.{+Variable}
        The rolled field.

:Examples:

        '''          
        if self._list:
            kwargs2 = self._parameters(locals())
            return self._list_method('roll', kwargs2)

        axis = self.domain.axis(axes, **kwargs)
        if axis is None:
            raise ValueError("Can't roll: Bad axis specification")

        if i:
            f = self
        else:
            f = self.copy()
        
        domain = f.domain

        if domain.axis_size(axis) <= 1:
            return f
        
        dim = domain.item(axis)
        if dim is not None and dim.period() is None:
            raise ValueError(
                "Can't roll %r axis with non-periodic dimension coordinates" % 
                dim.name())

        try:
            iaxis = domain.data_axes().index(axis)
        except ValueError:
            return f

        f = super(Field, f).roll(iaxis, shift, i=True)

        item_axes = domain.item_axes
        for key, item in domain.items(role=('d', 'a', 'm')).iteritems():
            axes = item_axes(key)
            if axis in axes:
                item.roll(axes.index(axis), shift, i=True)
        #--- End: for

        return f
    #--- End: def

    def where(self, condition, x=None, y=None, i=False):
        '''{+Fef,}Set data array elements depending on a condition.

Elements are set differently depending on where the condition is True
or False. Two assignment values are given. From one of them, the
field's data array is set where the condition is True and where the
condition is False, the data array is set from the other.

Each assignment value may either contain a single datum, or is an
array-like object which is broadcastable shape of the field's data
array.

**Missing data**

The treatment of missing data elements depends on the value of field's
`hardmask` attribute. If it is True then masked elements will not
unmasked, otherwise masked elements may be set to any value.

In either case, unmasked elements may be set to any value (including
missing data).

Unmasked elements may be set to missing data by assignment to the
`cf.masked` constant or by assignment to a value which contains masked
elements.

[+1].. seealso:: `cf.masked`, `hardmask`, `indices`, `mask`, `subspace`
[+N].. seealso:: `cf.masked`, `cf.Field.hardmask`, `cf.Field.indices`,
[+N]             `mask`, ``subspace`

:Examples 1:

>>> 

:Parameters:

    condition : 
        The condition which determines how to set the data array. The
        *condition* parameter may be one of:

          * Any object which is broadcastable to the field's shape
            using the metadata-aware `cf` broadcasting rules (i.e. a
            suitable `cf.Field` object or any object, ``a``, for which
            ``numpy.size(a)`` is 1). The condition is True where the
            object broadcast to the field's data array evaluates to
            True.

              *Example:*                
                To set all data array values of 10 to -999:
                ``f.where(10, -999)``.

              *Example:*
                To set all data array values of 100 metres to -999
                metres: ``f.where(cf.Data(100, 'm'), -999)``.

              *Example:*
                To set all data array values to -999 where another
                field, ``g`` (which is broadcastable to ``f``),
                evaluates to true: ``f.where(g, -999)``.

        ..

          * A `cf.Query` object which is evaluated against the field
            and the resulting field of booleans (which will always
            have the same shape as the original field) defines the
            condition.
   
              *Example:*
                ``f.where(cf.lt(0), -999)`` will set all data array
                values less than zero to -999. This will often be
                equivalent to ``f.where(f==cf.lt(0), -999)``, but the
                latter will fail if the field ``f`` has insufficient
                domain metadata whilst the former will always work.

    x, y : *optional*
        Specify the assignment values. Where the condition evaluates
        to True, set the field's data array from *x* and where the
        condition evaluates to False, set the field's data array from
        *y*. The *x* and *y* parameters are each one of:

          * `None`. The appropriate elements of the field's data
            array are unchanged. This the default.
        ..

          * Any object which is broadcastable to the field's data
            array using the metadata-aware `cf` broadcasting rules
            (i.e. a suitable `cf.Field` object or any object, ``a``,
            for which ``numpy.size(a)`` is 1). The appropriate
            elements of the field's data array are set to the
            corresponding values from the object broadcast to the
            field's data array shape.

    {+i}

:Returns:

    out : cf.{+Variable}
        {+Fef,}The field with updated data array.

:Examples 2:

Set data array values to 15 everywhere:

>>> f.where(True, 15)

This example could also be done with subspace assignment:

>>> f.subspace[...] = 15

Set all negative data array values to zero and leave all other
elements unchanged:

>>> g = f.where(f<0, 0)

Multiply all positive data array elements by -1 and set other data
array elements to 3.14:

>>> g = f.where(f>0, -f, 3.14)

Set all values less than 280 and greater than 290 to missing data:

>>> g = f.where((f < 280) | (f > 290), cf.masked)

This example could also be done with a `cf.Query` object:

>>> g = f.where(cf.wo(280, 290), cf.masked)

or equivalently:

>>> g = f.where(f==cf.wo(280, 290), cf.masked)

Set data array elements in the northern hemisphere to missing data
in-place:
[+1]
[+1]>>> # Create a condition which is True only in the northern hemisphere
[+1]>>> condition = f.domain_mask(latitude=cf.ge(0))
[+1]>>> # Set the data
[+1]>>> f.where(condition, cf.masked, i=True)
[+N]
[+N]>>> for g, northern_hemisphere in zip(f, f.domain_mask(latitude=cf.ge(0))):
[+N]...     g.where(condition, cf.masked, i=True)

This in-place example could also be done with subspace assignment by
indices:
[+1]
[+1]>>> northern_hemisphere = f.indices(latitude=cf.ge(0))
[+1]>>> f.subspace[northern_hemisphere] = cf.masked
[+N]
[+N]>>> for g in f:
[+N]...     northern_hemisphere = g.indices(latitude=cf.ge(0))
[+N]...     g.subspace[northern_hemisphere] = cf.masked

Set a polar rows to their zonal-mean values:
[+1]
[+1]>>> # Create a condition which is True only on polar rows
[+1]>>> condition = f.domain_mask(latitude=cf.set([-90, 90]))
[+1]>>> #Set each data polar row element to the polar row zonal mean 
[+1]>>> # and mask all other points
[+1]>>> g = f.where(condition, f.collapse('longitude: mean'))
[+N]
[+N]>>> # Initialize the new field list
[+N]>>> g = cf.FieldList()
[+N]>>> for x in f:
[+N]...     # Create a condition which is True only on the polar rows
[+N]...     condition = x.domain_mask(latitude=cf.set([-90, 90]))
[+N]...     # Set each data polar row element to the polar row zonal mean 
[+N]...     # and mask all other points
[+N]...     g.append(x.where(condition, x.collapse('longitude: mean')))

        '''   
        # List functionality
        if self._list:
            kwargs2 = self._parameters(locals())            
            return self._list_method('where', kwargs2)
 
        if i:
            f = self
        else:
            f = self.copy()

        if x is None and y is None:
            return f

        self_class = f.__class__

        if isinstance(condition, self_class):
            if len(condition) != 1:
                raise ValueError(
                    "Can't where: FieldList 'condition' must contain exactly 1 element")
            condition = f._conform_for_assignment(condition[0])

        elif isinstance(condition, Query):
            condition = condition.evaluate(f).Data            
 
        if x is not None and isinstance(x, self_class):
            if len(x) != 1:
                raise ValueError(
                    "Can't where: FieldList 'x' must contain exactly 1 element")
            x = f._conform_for_assignment(x[0])
               
        if y is not None and isinstance(y, self_class):
            if len(y) != 1:
                raise ValueError(
                    "Can't where: FieldList 'y' must contain exactly 1 element")
            y = f._conform_for_assignment(y[0])

        return super(Field, f).where(condition, x, y, i=True)
    #--- End: def

    def section(self, axes=None, stop=None, chunks=False, min_step=1,
                **kwargs):
        '''

{+Fef,}Return a FieldList of m dimensional sections of a Field of n
dimensions, where m <= n.

:Parameters:

    axes : *optional*
        A query for the m axes that define the sections of the Field
        as accepted by the Field object's axes method. The keyword
        arguments are also passed to this method. See cf.Field.axes
        for details. If an axis is returned that is not a data axis it
        is ignored, since it is assumed to be a dimension coordinate
        of size 1.

    stop : int, optional
        Stop after taking this number of sections and return. If stop
        is None all sections are taken.

    chunks : bool, optional
        If True return sections that are of the maximum possible size
        that will fit in one chunk of memory instead of sectioning
        into slices of size 1 along the dimensions that are being
        sectioned.
    
    min_step : int, optional
        The minimum step size when making chunks. By default this is
        1. Can be set higher to avoid size 1 dimensions, which are
        problematic for bilinear regridding.

:Returns:

    out : FieldList
        The FieldList of m dimensional sections of the Field.

:Examples:

Section a field into 2D longitude/time slices, checking the
units:

>>> f.section({None: 'longitude', units: 'radians'},
...           {None: 'time',
...            'units': 'days since 2006-01-01 00:00:00'})

Section a field into 2D longitude/latitude slices, requiring
exact names:

>>> f.section(['latitude', 'longitude'], exact=True)

Section a field into 2D longitude/latitude slices, showing
the results:

>>> f
<CF Field: eastward_wind(model_level_number(6), latitude(145),
longitude(192)) m s-1>

>>> f.section(('X', 'Y'))
[<CF Field: eastward_wind(model_level_number(1), latitude(145),
longitude(192)) m s-1>,
 <CF Field: eastward_wind(model_level_number(1), latitude(145),
longitude(192)) m s-1>,
 <CF Field: eastward_wind(model_level_number(1), latitude(145),
longitude(192)) m s-1>,
 <CF Field: eastward_wind(model_level_number(1), latitude(145),
longitude(192)) m s-1>,
 <CF Field: eastward_wind(model_level_number(1), latitude(145),
longitude(192)) m s-1>,
 <CF Field: eastward_wind(model_level_number(1), latitude(145),
longitude(192)) m s-1>]

        '''
        return FieldList(_section(self, axes, data=False, stop=stop,
                                  chunks=chunks, min_step=min_step, **kwargs))
    #--- End: def

    def regrids(self, dst, src_cyclic=None, dst_cyclic=None,
                method='auto', use_dst_mask=False,
                _compute_field_mass=None, i=False):
        '''

{+Fef,}Returns the field regridded onto a new latitude-longitude grid.

Regridding, also called remapping or interpolation, is the process of
changing the grid underneath field data values while preserving the
qualities of the original data.

By default the the regridding is a first-order conservative
interpolation, but bilinear interpolation is available. The latter
method is particular useful for cases when the latitude and longitude
coordinate cell boundaries are not known nor inferrable. Nearest
neighbour interpolation is also available.

**Metadata**

The field's domain must have well defined X and Y axes with latitude
and longitude coordinate values, which may be stored as dimension
coordinate objects or two dimensional auxiliary coordinate
objects. The same is true for the destination grid, if it provided as
part of another field.

The cyclicity of the X axes of the source field and destination grid
is taken into account. If an X axis is in fact cyclic but is
registered as such by its parent field (see `cf.Field.iscyclic`), then
the cyclicity may be set with the *src_cyclic* or *dst_cyclic*
parameters.

The output field's coordinate objects which span the X and/or Y axes
are replaced with those from the destination grid. Any fields
contained in coordinate reference objects will also be regridded, if
possible.

**Mask**

The data array mask of the field is automatically taken into account,
such that the regridded data array will be masked in regions where the
input data array is masked. By default the mask of the destination
grid is not taken into account. If the destination field data has
more than two dimensions then the mask, if used, is taken from the two
dimensionsal section of the data where the indices of all axes other
than X and Y are zero.

**Method**

The interpolation is carried by out using the `ESMF` package - a
Python interface to the Earth System Modeling Framework (ESMF)
regridding utility.

**Logging**

Whether ESMF logging is enabled or not is determined by
`cf.REGRID_LOGGING`. If it is logging takes place after every call. By
default logging is disabled.

.. versionadded:: 1.0.4

:Examples 1:

Regrid field ``f`` conservatively onto a grid contained in field
``g``:

>>> h = f.regrids(g)

:Parameters:

    dst : Field or dict
        The field containing the new grid. If dst is a field list the
        first field in the list is used. Alternatively a dictionary
        can be passed containing the keywords 'longitude' and
        'latitude' with either two 1D dimension coordinates or two 2D
        auxiliary coordinates. In the 2D case both coordinates must
        have their axes in the same order and this must be specified
        by the keyword 'axes' as either ``('X', 'Y')`` or ``('Y',
        'X')``.

    src_cyclic : bool, optional
        Force the use of a periodic X axis for the source field,
        without altering the original field.

    dst_cyclic : bool, optional
        Force the use of a periodic X axis for the destination grid,
        without altering the original field.

    method : string, optional
        By default the regridding method is set to 'auto'. In this case
        conservative regridding will be used unless one or both of the
        fields does not have contiguous bounds, in which case bilinear
        regridding will be used. If a 1D dimension coordinate does not
        have bounds then contiguous bounds will be created
        automatically. If this parameter is set to conservative then
        first-order conservative regridding is used. If it is set to
        'bilinear' then multilinear interpolation is used. If it is set
        to 'nearest_stod' then nearest neighbor interpolation is used
        where each destination point is mapped to the closest source
        point. A given source point may map to multiple destination
        points, but no destination point will receive input from more
        than one source point. If it is set to 'nearest_dtos' then
        nearest neighbor interpolation is used where each source
        point is mapped to the closest destination point. A given
        destination point may receive input from multiple source
        points, but no source point will map to more than one
        destination point.

    use_dst_mask : bool, optional
        By default the mask of the data on the destination grid is not
        taken into account when performing regridding. If this option
        is set to true then it is. If the destination field has more
        than two dimensions then the first 2D slice in index space is
        used for the mask e.g. for an field varying with (X, Y, Z, T)
        the mask is taken from the slice (X, Y, 0, 0).

    {+i}

    _compute_field_mass : dict, optional
        If this is a dictionary then the field masses of the source
        and destination fields are computed and returned within the
        dictionary. The keys of the dictionary indicates the lat/long
        slice of the field and the corresponding value is a tuple
        containing the source field's mass and the destination field's
        mass. The calculation is only done if conservative regridding
        is being performed. This is for debugging purposes.

:Returns:

    out : cf.{+Variable}
        The regridded {+variable}.

:Examples 2:

Regrid f to the grid of g using bilinear regridding and forcing the
source field f to be treated as cyclic.

>>> h = f.regrids(g, src_cyclic=True, method='bilinear')

Regrid f to the grid of g using the mask of g.

>>> h = f.regrids(g, use_dst_mask=True)

Regrid f to 2D auxiliary coordinates lat and lon, which have their
dimensions ordered 'Y' first then 'X'.

>>> lat
<CF AuxiliaryCoordinate: latitude(110, 106) degrees_north>
>>> lon
<CF AuxiliaryCoordinate: longitude(110, 106) degrees_east>
>>> h = f.regrids({'longitude': lon, 'latitude': lat, 'axes': ('Y', 'X')})

        '''
        # List functionality
        if self._list:
            kwargs2 = self._parameters(locals())
            return self._list_method('regrids', kwargs2)
        
        # Initialise ESMPy for regridding if found
        manager = Regrid.initialize()
        
        # If dst is a dictionary set flag
        if isinstance(dst, self.__class__):
            dst_dict = False
            # If dst is a field list use the first field
            dst = dst[0]
        else:
            dst_dict = True
        
        # Retrieve the source field's latitude and longitude coordinates
        x_s, y_s, x_axis_s, y_axis_s, x_key_s, y_key_s, x_size_s, y_size_s, \
            src_2D_latlong = Regrid.get_latlong(self, 'source')
        
        # Retrieve the source field's z and t indices
        zt_indices = []
        
        z_key = self.dim('Z', key=True)
        if z_key is not None:
            try:
                z_index = self.data_axes().index(z_key)
            except ValueError:
                self = self.unsqueeze(z_key, i=i)
                z_index = self.data_axes().index(z_key)
            zt_indices.append(z_index)
        
        t_key = self.dim('T', key=True)
        if t_key is not None:
            try:
                t_index = self.data_axes().index(t_key)
            except ValueError:        
                self = self.unsqueeze(t_key, i=i)
                t_index = self.data_axes().index(t_key)
            zt_indices.append(t_index)
        
        # Retrieve the destination field's latitude and longitude coordinates
        if dst_dict:
            try:
                x_d = dst['longitude']
                y_d = dst['latitude']
            except KeyError:
                raise ValueError("Keywords 'longitude' and 'latitude' " +
                                 "must be specified for destination.")
            #--- End: if
            if x_d.ndim == 1:
                dst_2D_latlong = False
                x_size_d = x_d.size
                y_size_d = y_d.size
            elif x_d.ndim == 2:
                try:
                    dst_axes = dst['axes']
                except KeyError:
                    raise ValueError("Keyword 'axes' must be specified " +
                                     "for 2D latitude/longitude coordinates.")
                dst_2D_latlong = True
                if dst_axes == ('X', 'Y'):
                    x_size_d = x_d.shape[0]
                    y_size_d = x_d.shape[1]
                elif dst_axes == ('Y', 'X'):
                    x_size_d = x_d.shape[1]
                    y_size_d = x_d.shape[0]
                else:
                    raise ValueError("Keyword 'axes' must either be " +
                                     "('X', 'Y') or ('Y', 'X').")                
                if x_d.shape != y_d.shape:
                    raise ValueError('Longitude and latitude coordinates for ' +
                                     'destination must have the same shape.')
            else:
                raise ValueError('Longitude and latitude coordinates for ' +
                                 'destination must have 1 or 2 dimensions.')
            #--- End: if
        else:
            x_d, y_d, x_axis_d, y_axis_d, x_key_d, y_key_d, x_size_d, y_size_d, \
                dst_2D_latlong = Regrid.get_latlong(dst, 'destination')
        #--- End: if
        
        # Set src_cyclic and/or dst_cyclic to true if it has been automatically
        # detected that the fields are cyclic.
        if self.iscyclic('X'):
            src_cyclic = True
        if not dst_dict and dst.iscyclic('X'):
            dst_cyclic = True
        
        # Preserve order of axes
        try:
            x_index_s= self.data_axes().index(x_axis_s)
        except ValueError:        
            self = self.unsqueeze(x_axis_s, i=i)
            x_index_s = self.data_axes().index(x_axis_s)
        
        try:
            y_index_s = self.data_axes().index(y_axis_s)
        except ValueError:        
            self = self.unsqueeze(y_axis_s, i=i)
            y_index_s = self.data_axes().index(y_axis_s)
        
        if not dst_dict:
            try:
                x_index_d = dst.data_axes().index(x_axis_d)
            except ValueError:        
                dst = dst.unsqueeze(x_axis_d)
                x_index_d = dst.data_axes().index(x_axis_d)
            
            try:
                y_index_d = dst.data_axes().index(y_axis_d)
            except ValueError:        
                dst = dst.unsqueeze(y_axis_d)
                y_index_d = dst.data_axes.index(y_axis_d)
        #--- End: if
        
        shape = [1]*self.ndim
        shape[x_index_s] = x_size_d
        shape[y_index_s] = y_size_d
        order_s = (0, 1) if x_index_s < y_index_s else (1, 0)
        if not dst_dict:
            order_d = (0, 1) if x_index_d < y_index_d else (1, 0)
        #--- End: if
        
        if src_2D_latlong:
            x_axes_s = self.item_axes(x_key_s)
            x_order_s = (x_axes_s.index(x_axis_s), x_axes_s.index(y_axis_s))
            y_axes_s = self.item_axes(y_key_s)
            y_order_s = (y_axes_s.index(x_axis_s), y_axes_s.index(y_axis_s))
        if dst_2D_latlong:
            if dst_dict:
                if dst_axes == ('X', 'Y'):
                    x_order_d = (0, 1)
                    y_order_d = (0, 1)
                elif dst_axes == ('Y', 'X'):
                    x_order_d = (1, 0)
                    y_order_d = (1, 0)
                else:
                    raise ValueError("Keyword 'axes' must either be " +
                                     "('X', 'Y') or ('Y', 'X').")
            else:
                x_axes_d = dst.item_axes(x_key_d)
                x_order_d = (x_axes_d.index(x_axis_d), x_axes_d.index(y_axis_d))
                y_axes_d = dst.item_axes(y_key_d)
                y_order_d = (y_axes_d.index(x_axis_d), y_axes_d.index(y_axis_d))
        #--- End: if
        
        # Slice the source data into 2D latitude/longitude sections
        sections = self.Data.section((x_index_s, y_index_s))
        
        # Check whether the coordinates all have appropriate bounds
        if method == 'auto':
            method = 'conservative'
            for coord in [x_s, y_s]:
                if src_2D_latlong:
                    if not coord.hasbounds or not coord.contiguous(overlap=False):
                        method = 'bilinear'
                        break
                    #--- End: if
                else:
                    if coord.hasbounds and not coord.contiguous(overlap=False):
                        method = 'bilinear'
                        break
                    #--- End: if
                #--- End: if
            #--- End: for
            for coord in [x_d, y_d]:
                if dst_2D_latlong:
                    if not coord.hasbounds or not coord.contiguous(overlap=False):
                        method = 'bilinear'
                        break
                    #--- End: if
                else:
                    if coord.hasbounds and not coord.contiguous(overlap=False):
                        method = 'bilinear'
                        break
                    #--- End: if
                #--- End: if
            #--- End: for
        elif method == 'conservative':
            for coord in [x_s, y_s]:
                if src_2D_latlong:
                    if not coord.hasbounds or not coord.contiguous(overlap=False):
                        raise ValueError('2D source latitude and longitude' +
                                         ' coordinates must have contiguous' +
                                         ' bounds for conservative regridding.')
                    #--- End: if
                else:
                    if coord.hasbounds and not coord.contiguous(overlap=False):
                        raise ValueError('Existing bounds of 1D source' +
                                         ' latitude and longitude coordinates' +
                                         ' must be contiguous for conservative' +
                                         ' regridding.')
                    #--- End: if
                #--- End: if
            #--- End: for
            for coord in [x_d, y_d]:
                if dst_2D_latlong:
                    if not coord.hasbounds or not coord.contiguous(overlap=False):
                        raise ValueError('2D destination latitude and longitude' +
                                         ' coordinates must have contiguous' +
                                         ' bounds for conservative regridding.')
                    #--- End: if
                else:
                    if coord.hasbounds and not coord.contiguous(overlap=False):
                        raise ValueError('Existing bounds of 1D destination' +
                                         ' latitude and longitude coordinates' +
                                         ' must be contiguous for conservative' +
                                         ' regridding.')
                    #--- End: if
                #--- End: if
            #--- End: for
        #--- End: if

        # Retrieve the destination field's grid and create the ESMPy grid
        use_bounds = method == 'conservative'
        dst_mask = None
        if not dst_dict and use_dst_mask and dst.Data.ismasked:
            dst_mask = dst.section(('X', 'Y'), stop=1, ndim=1)[0].squeeze().array.mask
            dst_mask = dst_mask.transpose(order_d)
        #--- End: if
        if dst_2D_latlong:
            dstgrid = Regrid.create_2Dgrid(x_d, y_d, x_order_d, y_order_d,
                                           dst_cyclic, dst_mask, use_bounds)
        else:
            dstgrid = Regrid.create_grid(x_d, y_d, dst_cyclic, dst_mask, use_bounds)
        #--- End: if
        dstfield = Regrid.create_field(dstgrid, 'dstfield')
        dstfracfield = Regrid.create_field(dstgrid, 'dstfracfield')

        def initialise_regridder(src_mask=None):
            '''
            Initialise the source grid and the regridder.
            '''
            # Create the source grid
            if src_2D_latlong:
                srcgrid = Regrid.create_2Dgrid(x_s, y_s, x_order_s, y_order_s,
                                               src_cyclic, src_mask, use_bounds)
            else:
                srcgrid = Regrid.create_grid(x_s, y_s, src_cyclic, src_mask, use_bounds)
            #--- End: if
            srcfield = Regrid.create_field(srcgrid, 'srcfield')
            srcfracfield = Regrid.create_field(srcgrid, 'srcfracfield')
            
            # Initialise the regridder
            regridSrc2Dst = Regrid(srcfield, dstfield, srcfracfield,
                                   dstfracfield, method=method)
            
            return srcgrid, srcfield, srcfracfield, regridSrc2Dst
        
        # Reorder keys by Z and then T to minimise how often the mask is
        # likely to change.
        if zt_indices:
            section_keys = sorted(sections.keys(),
                                  key=operator_itemgetter(*zt_indices))
        else:
            section_keys = sections.keys()
        
        # Regrid each section
        old_mask = None
        unmasked_grid_created = False
        for k in section_keys:
            d = sections[k]
            # Retrieve the source field's grid, create the ESMPy grid and a
            # handle to regridding.dst_dict
            src_data = d.squeeze().transpose(order_s).array
            if numpy_is_masked(src_data):
                mask = src_data.mask
                if not numpy_array_equal(mask, old_mask):
                    # Release old memory
                    if old_mask is not None:
                        regridSrc2Dst.destroy()
                        srcfracfield.destroy()
                        srcfield.destroy()
                        srcgrid.destroy()
                    #--- End: if
                    
                    # (Re)initialise the regridder
                    srcgrid, srcfield, srcfracfield, regridSrc2Dst = \
                        initialise_regridder(mask)
                    old_mask = mask
                #--- End: if
            else:
                if not unmasked_grid_created or old_mask is not None:
                    # Initialise the regridder
                    srcgrid, srcfield, srcfracfield, regridSrc2Dst = \
                        initialise_regridder()
                    unmasked_grid_created = True
                    old_mask = None
                #--- End: if
            #--- End: if
            
            # Fill the source and destination fields and regrid
            srcfield.data[...] = numpy_MaskedArray(src_data, copy=False).filled(self.fill_value(default='netCDF'))
            dstfield.data[...] = self.fill_value(default='netCDF')
            dstfield = regridSrc2Dst.run_regridding(srcfield, dstfield)
            
            # Check field mass
            if _compute_field_mass is not None and method == 'conservative':
                if not type(_compute_field_mass) == dict:
                    raise ValueError('Expected compute_field_mass to be a dictoinary.')
                srcareafield = Regrid.create_field(srcgrid, 'srcareafield')
                srcmass = Regrid.compute_mass_grid(srcfield, srcareafield,
                                                   dofrac=True,
                                                   fracfield=srcfracfield,
                                                   uninitval=self.fill_value(default='netCDF'))
                dstareafield = Regrid.create_field(dstgrid, 'dstareafield')
                dstmass = Regrid.compute_mass_grid(dstfield, dstareafield,
                                               uninitval=self.fill_value(default='netCDF'))
                _compute_field_mass[k] = (srcmass, dstmass)
            
            # Correct destination field data if doing conservative regridding
            # and add mask
            if method == 'conservative':
                frac = dstfracfield.data[...]
                frac[frac == 0.0] = 1.0
                regridded_data = numpy_MaskedArray(dstfield.data[...].copy()/frac,
                                                   mask=(dstfield.data ==
                                                         self.fill_value(default='netCDF')))
            else:
                regridded_data = numpy_MaskedArray(dstfield.data[...].copy(),
                                                   mask=(dstfield.data ==
                                                         self.fill_value(default='netCDF')))
            
            # Insert regridded data, with axes in correct order
            sections[k] = Data(regridded_data.transpose(order_s).reshape(shape),
                               units=self.Units)
        #--- End: for
        
        # Construct new data from regridded sdst_dictections
        new_data = Regrid.reconstruct_sectioned_data(sections)
        
        # Construct new field
        if i:
            f = self
        else:
            f = self.copy(_omit_Data=True)
        #--- End:if
        
        # Update ancillary variables and coordinate references of source
        f._conform_ancillary_variables([x_axis_s, y_axis_s], keep_size_1=False)
        for key, ref in f.refs().iteritems():
            axes = f.domain.ref_axes(key)
            if x_axis_s in axes or y_axis_s in axes:
                f.remove_item(key)
            else:
                for term, value in ref.iteritems():
                    if not isinstance(value, type(self)):
                        continue 
                    
                    axes2 = value.axes(('X', 'Y'))
                    if len(axes2) == 1:
                        ref[term] = None
                    elif len(axes2) == 2:
                        # only want to do this if value spans both X and Y
                        try:
                            value2 = value.regrids(dst, src_cyclic=src_cyclic,
                                                   dst_cyclic=dst_cyclic,
                                                   method=method,
                                                   use_dst_mask=use_dst_mask,
                                                   i=i)
                        except ValueError:
                            ref[term] = None
                        else:
                            ref[term] = value2
                    #--- End: if
                #--- End: for
            #--- End: if
        #--- End: for
        
        # Remove X and Y coordinates of new field
        f.remove_items(axes=('X', 'Y'))
        
        # Give destination grid latitude and longitude standard names
        x_d.standard_name = 'longitude'
        y_d.standard_name = 'latitude'
        
        # Insert 'X' and 'Y' coordinates from dst into new field
        f.domain._axes_sizes[x_axis_s] = x_size_d
        f.domain._axes_sizes[y_axis_s] = y_size_d
        if dst_dict:
            if dst_2D_latlong:
                if x_order_d == (0, 1):
                    x_axes_s = (x_axis_s, y_axis_s)
                else:
                    x_axes_s = (y_axis_s, x_axis_s)
                if y_order_d == (0, 1):
                    y_axes_s = (x_axis_s, y_axis_s)
                else:
                    y_axes_s = (y_axis_s, x_axis_s)
                f.insert_aux(x_d, axes=x_axes_s)
                f.insert_aux(y_d, axes=y_axes_s)
            else:
                f.insert_dim(x_d, key=x_axis_s)
                f.insert_dim(y_d, key=y_axis_s)
        else:
            x_dim = dst.dim('X')
            f.insert_dim(x_dim, key=x_axis_s)
            
            y_dim = dst.dim('Y')
            f.insert_dim(y_dim, key=y_axis_s)
            
            for aux_key, aux in dst.auxs(axes_all=('X', 'Y')).iteritems():
                aux_axes = dst.domain.item_axes(aux_key)
                if aux_axes == [x_axis_d, y_axis_d]:
                    f.insert_aux(aux, axes=(x_axis_s, y_axis_s))
                else:
                    f.insert_aux(aux, axes=(y_axis_s, x_axis_s))
            #--- End: for
            for aux in dst.auxs(axes_all='X').values():
                f.insert_aux(aux, axes=x_axis_s)
            #--- End: for
            for aux in dst.auxs(axes_all='Y').values():
                f.insert_aux(aux, axes=y_axis_s)
            #--- End: for
        #--- End: if
        
        # Copy across the destination fields coordinate references if necessary
        if not dst_dict:
            for key, ref in dst.refs().iteritems():
                axes = dst.domain.ref_axes(key)
                if axes and axes.issubset([x_axis_d, y_axis_d]):
                    f.insert_ref(ref.copy(domain=dst.domain))
                #--- End: if
            #--- End: for
        #--- End: if
        
        # Insert regridded data into new field
        f.insert_data(new_data)
        
        # Set the cyclicity of the destination longitude
        f.cyclic('X', iscyclic=dst_cyclic, period=Data(360, 'Degrees'))
        
        # Release old memory
        regridSrc2Dst.destroy()
        dstfracfield.destroy()
        srcfracfield.destroy()
        dstfield.destroy()
        srcfield.destroy()
        dstgrid.destroy()
        srcgrid.destroy()
        
        return f
    #--- End: def

    def regridc(self, dst, axes, method='auto', use_dst_mask=False,
                _compute_field_mass=None, i=False):
        '''

{+Fef,}Returns the field with the specified Cartesian axes regridded
onto a new grid. Between 1 and 3 dimensions may be regridded.

Regridding, also called remapping or interpolation, is the process of
changing the grid underneath field data values while preserving the
qualities of the original data.

By default the the regridding is a first-order conservative
interpolation, but bilinear and nearest neighbour interpolation is
available.

**Metadata**

The field's domain must have axes matching those specified in
src_axes. The same is true for the destination grid, if it provided
as part of another field. Optionally the axes to use from the
destination grid may be specified separately in dst_axes.

The output field's coordinate objects which span the specified axes
are replaced with those from the destination grid. Any fields
contained in coordinate reference objects will also be regridded, if
possible.

**Mask**

The data array mask of the field is automatically taken into account,
such that the regridded data array will be masked in regions where the
input data array is masked. By default the mask of the destination
grid is not taken into account. If the destination field data has
more dimensions than the number of axes specified then, if used, its
mask is taken from the 1-3 dimensional section of the data where the
indices of all axes other than X and Y are zero.

**Method**

The interpolation is carried by out using the `ESMF` package - a
Python interface to the Earth System Modeling Framework (ESMF)
regridding utility.

**Logging**

Whether ESMF logging is enabled or not is determined by
`cf.REGRID_LOGGING`. If it is logging takes place after every call. By
default logging is disabled.

:Examples 1:

Regrid the time axes of field ``f`` conservatively onto a grid
contained in field ``g``:

>>> h = f.regridc(g, axes='T')

:Parameters:

    dst : Field or dict
        The field containing the new grid or a dictionary with the
        axes specifiers as keys referencing dimension coordinates.
        If dst is a field list the first field in the list is used.

    axes
        Select dimension coordinates from the source and destination
        fields for regridding. See cf.Field.axes for options for
        selecting specific axes. However, the number of axes returned
        by cf.Field.axes must be the same as the number of specifiers
        passed in.

    method : string, optional
        By default the regridding method is set to 'auto'. In this case
        conservative regridding will be used unless one or both of the
        fields does not have contiguous bounds, in which case bilinear
        regridding will be used. If a 1D dimension coordinate does not
        have bounds then contiguous bounds will be created
        automatically. If this parameter is set to conservative then
        first-order conservative regridding is used. If it is set to
        'bilinear' then multilinear interpolation is used. If it is set
        to 'nearest_stod' then nearest neighbor interpolation is used
        where each destination point is mapped to the closest source
        point. A given source point may map to multiple destination
        points, but no destination point will receive input from more
        than one source point. If it is set to 'nearest_dtos' then
        nearest neighbor interpolation is used where each source
        point is mapped to the closest destination point. A given
        destination point may receive input from multiple source
        points, but no source point will map to more than one
        destination point.

    use_dst_mask : bool, optional
        By default the mask of the data on the destination grid is not
        taken into account when performing regridding. If this option
        is set to true then it is.

    {+i}

    _compute_field_mass : dict, optional
        If this is a dictionary then the field masses of the source
        and destination fields are computed and returned within the
        dictionary. The keys of the dictionary indicates the lat/long
        slice of the field and the corresponding value is a tuple
        containing the source field's mass and the destination field's
        mass. The calculation is only done if conservative regridding
        is being performed. This is for debugging purposes.

:Returns:

    out : cf.{+Variable}
        The regridded {+variable}.

:Examples 2:

Regrid the T axis of field ``f`` conservatively onto the grid
specified in the dimension coordinate ``t``:

>>> h = f.regridc({'T': t}, axes=('T'))

Regrid the T axis of field ``f`` using bilinear interpolation onto
a grid contained in field ``g``:

>>> h = f.regridc(g, axes=('T'), method='bilinear')

Regrid the X and Y axes of field ``f`` conservatively onto a grid
contained in field ``g``:

>>> h = f.regridc(g, axes=('X','Y'))

Regrid the X and T axes of field ``f`` conservatively onto a grid
contained in field ``g`` using the destination mask:

>>> h = f.regridc(g, axes=('X','Y'), use_dst_mask=True)

        '''
        # List functionality
        if self._list:
            kwargs2 = self._parameters(locals())
            return self._list_method('regrids', kwargs2)
        
        # Initialise ESMPy for regridding if found
        manager = Regrid.initialize()
        
        # If dst is a dictionary set flag
        if isinstance(dst, self.__class__):
            dst_dict = False
            # If dst is a field list use the first field
            dst = dst[0]
        else:
            dst_dict = True
        
        # Get the number of axes
        n_axes = len(axes)
        if n_axes < 1 or n_axes > 3:
            raise ValueError('Between 1 and 3 axes must be individually ' +
                             'specified.')
        
        # Retrieve the source axis keys and dimension coordinates
        axis_keys_s, coords_s = Regrid.get_cartesian_coords(self, 'source',
                                                            axes)
        
        # Retrieve the destination axis keys and dimension coordinates
        if dst_dict:
            coords_d = []
            for axis in axes:
                try:
                    coords_d.append(dst[axis])
                except KeyError:
                    raise ValueError('Axis ' + str(axis) + ' not specified in dst.')
                #--- End: try
            #--- End: for
        else:
            axis_keys_d, coords_d = Regrid.get_cartesian_coords(dst, 'destination',
                                                                axes)
        #--- End: if
        
        def get_axis_positions(f, axis_keys):
            """
            Get the axis positions and their orders in rank of a field f.
            """
            # Get the positions of the axes
            axis_positions = []
            for k in axis_keys:
                axis_positions.append(f.data_axes().index(k))
                
            # Get the rank order of the positions of the axes
            temp = numpy_array(axis_positions)
            temp = temp.argsort()
            order = numpy_empty(len(temp), int)
            order[temp] = numpy_arange(len(temp))
            
            return axis_positions, order
        
        # Get the axis positions for the source field
        axis_positions_s, order_s = get_axis_positions(self, axis_keys_s)
        
        # Get the axis positions for the destination field
        if not dst_dict:
            axis_positions_d, order_d = get_axis_positions(dst, axis_keys_d)
        
        # Pad out a single dimension with an extra one
        axis_keys_ext = []
        coords_ext = []
        axis_positions_s_ext = axis_positions_s
        order_s_ext = order_s
        if n_axes == 1 and self.squeeze().ndim > 1:
            src_shape = numpy_array(self.shape)
            tmp = src_shape.copy()
            tmp[axis_positions_s] = -1
            max_length = -1
            max_ind = -1
            for ind, length in enumerate(tmp):
                if length > max_length:
                    max_length = length
                    max_ind = ind
            if src_shape[axis_positions_s].prod()*max_length*8 < CHUNKSIZE():
                axis_keys_ext, coords_ext = \
                    Regrid.get_cartesian_coords(self, 'source', [max_ind])
                axis_positions_s_ext, order_s_ext = \
                    get_axis_positions(self, axis_keys_ext + axis_keys_s)
        
        # Check whether the coordinates all have appropriate bounds
        if method == 'auto':
            method = 'conservative'
            for coord in coords_s + coords_d + coords_ext:
                if coord.hasbounds and not coord.contiguous(overlap=False):
                    method = 'bilinear'
                    break
                #--- End: if
            #--- End: for
        elif method == 'conservative':
            for coord in coords_s + coords_d + coords_ext:
                if coord.hasbounds and not coord.contiguous(overlap=False):
                    raise ValueError('All existing bounds of dimension' +
                                     ' coordinates must be contiguous for' +
                                     ' conservative regridding.')
                #--- End: if
            #--- End: for
        #--- End: if

        # Calculate shape of each section
        shape = [1]*self.ndim
        tmp = coords_ext + coords_d
        for ind, p in enumerate(axis_positions_s_ext):
            shape[p] = tmp[ind].size
        
        # Deal with case of 1D linear regridding
        linear = False
        if method == 'bilinear' and n_axes == 1 and coords_ext == []:
            linear = True
            coords_ext = [DimensionCoordinate(data=Data([-1e-6,1e-6]))]
        
        # Section the data into slices of up to three dimensions
        sections = self.Data.section(axis_positions_s_ext)
        
        # Retrieve the destination field's grid and create the ESMPy grid
        dst_mask = None
        if not dst_dict and use_dst_mask and dst.Data.ismasked:
            dst_mask = dst.section(axes, stop=1, ndim=1)[0].squeeze().array.mask
            dst_mask = dst_mask.transpose(order_d)
            tmp = []
            for coord in coords_ext:
                tmp.append(coord.size)
            dst_mask = numpy_tile(dst_mask, tmp + [1]*dst_mask.ndim)
            
        #--- End: if
        if method == 'conservative':
            dstgrid = Regrid.create_cartesian_grid(coords_ext + coords_d,
                                                   dst_mask, use_bounds=True)
        else:
            dstgrid = Regrid.create_cartesian_grid(coords_ext + coords_d,
                                                   dst_mask, use_bounds=False)

        dstfield = Regrid.create_field(dstgrid, 'dstfield')
        dstfracfield = Regrid.create_field(dstgrid, 'dstfracfield')
        
        def initialise_regridder(src_mask=None):
            '''
            Initialise the source grid and the regridder.
            '''
            # Initialise the source grid
            if method == 'conservative':
                srcgrid = Regrid.create_cartesian_grid(coords_ext + coords_s,
                                                       src_mask, use_bounds=True)
            else:
                srcgrid = Regrid.create_cartesian_grid(coords_ext + coords_s,
                                                       src_mask, use_bounds=False)
            srcfield = Regrid.create_field(srcgrid, 'srcfield')
            srcfracfield = Regrid.create_field(srcgrid, 'srcfracfield')
            
            # Initialise the regridder
            regridSrc2Dst = Regrid(srcfield, dstfield, srcfracfield,
                                   dstfracfield, method=method)
            
            return srcgrid, srcfield, srcfracfield, regridSrc2Dst
        
        # Regrid each segment.
        old_mask = None
        unmasked_grid_created = False
        for k in sections.keys():
            d = sections[k]
            subsections = d.Data.section(axis_positions_s, chunks=True,
                                         min_step=2)
            for k2 in subsections.keys():
                d2 = subsections[k2]
                # Retrieve the source field's grid, create the ESMPy grid and a
                # handle to regridding.
                src_data = d2.squeeze().transpose(order_s_ext).array
                if linear:
                    src_data = numpy_tile(src_data, (2,1))
                if numpy_is_masked(src_data):
                    mask = src_data.mask
                    if not numpy_array_equal(mask, old_mask):
                        # Release old memory
                        if old_mask is not None:
                            regridSrc2Dst.destroy()
                            srcfracfield.destroy()
                            srcfield.destroy()
                            srcgrid.destroy()
                        #--- End: if
                        
                        # (Re)initialise the regridder
                        srcgrid, srcfield, srcfracfield, regridSrc2Dst = \
                            initialise_regridder(mask)
                        old_mask = mask
                    #--- End: if
                else:
                    if not unmasked_grid_created or old_mask is not None:
                        # Initialise the regridder
                        srcgrid, srcfield, srcfracfield, regridSrc2Dst = \
                            initialise_regridder()
                        unmasked_grid_created = True
                        old_mask = None
                    #--- End: if
                #--- End: if
                
                # Fill the source and destination fields and regrid
                srcfield.data[...] = numpy_MaskedArray(src_data, copy=False).filled(self.fill_value(default='netCDF'))
                dstfield.data[...] = self.fill_value(default='netCDF')
                dstfield = regridSrc2Dst.run_regridding(srcfield, dstfield)
                
                # Check field mass
                if _compute_field_mass is not None and method == 'conservative':
                    if not type(_compute_field_mass) == dict:
                        raise ValueError('Expected compute_field_mass to be a dictoinary.')
                    srcareafield = Regrid.create_field(srcgrid, 'srcareafield')
                    srcmass = Regrid.compute_mass_grid(srcfield, srcareafield,
                                                       dofrac=True,
                                                       fracfield=srcfracfield,
                                                       uninitval=self.fill_value(default='netCDF'))
                    dstareafield = Regrid.create_field(dstgrid, 'dstareafield')
                    dstmass = Regrid.compute_mass_grid(dstfield, dstareafield,
                                                   uninitval=self.fill_value(default='netCDF'))
                    _compute_field_mass[k] = (srcmass, dstmass)
                
                # Correct destination field data if doing conservative regridding
                # and add mask
                if method == 'conservative':
                    frac = dstfracfield.data[...]
                    frac[frac == 0.0] = 1.0
                    regridded_data = numpy_MaskedArray(dstfield.data[...].copy()/frac,
                                                       mask=(dstfield.data ==
                                                             self.fill_value(default='netCDF')))
                else:
                    regridded_data = numpy_MaskedArray(dstfield.data[...].copy(),
                                                       mask=(dstfield.data ==
                                                             self.fill_value(default='netCDF')))
                
                if linear:
                    regridded_data = regridded_data[0]
                
                # Insert regridded data, with axes in correct order
                subsections[k2] = Data(regridded_data.squeeze().transpose(order_s_ext).reshape(shape),
                                       units=self.Units)
            #--- End: for
            sections[k] = Regrid.reconstruct_sectioned_data(subsections)
        #--- End: for
        
        # Construct new data from regridded sections
        new_data = Regrid.reconstruct_sectioned_data(sections)
        
        # Construct new field
        if i:
            f = self
        else:
            f = self.copy(_omit_Data=True)
        #--- End:if
        
        # Update ancillary variables and coordinate references of source
        f._conform_ancillary_variables(axis_keys_s, keep_size_1=False)
        for key, ref in f.refs().iteritems():
            tmp = f.domain.ref_axes(key)
            if tmp.intersection(axis_keys_s):
                f.remove_item(key)
            else:
                for term, value in ref.iteritems():
                    if not isinstance(value, type(self)):
                        continue 
                    
                    tmp2 = value.axes(axes)
                    if tmp2 and len(tmp2) < n_axes:
                        ref[term] = None
                    elif len(tmp2) == n_axes:
                        # FOR NOW only want to do this if value spans all axes
                        # IN FUTURE: any subset
                        try:
                            value2 = value.regridc(dst, axes=axes,
                                                   method=method,
                                                   use_dst_mask=use_dst_mask,
                                                   i=i)
                        except ValueError:
                            ref[term] = None
                        else:
                            ref[term] = value2
                    #--- End: if
                #--- End: for
            #--- End: if
        #--- End: for
                        
        # Remove src coordinates of new field
        f.remove_items(axes=axes)
        
        # Make axes map
        if not dst_dict:
            axis_map = {}
            for k_s, k_d in zip(axis_keys_s, axis_keys_d):
                axis_map[k_d] = k_s
            #--- End: for
        #--- End: if
        
        # Insert coordinates from dst into new field
        if dst_dict:
            for k_s, d in zip(axis_keys_s, coords_d):
                f.domain._axes_sizes[k_s] = d.size
                f.insert_dim(d, key=k_s)
            #--- End: for
        else:
            for k_d in axis_keys_d:
                d = dst.dim(k_d)
                k_s = axis_map[k_d]
                f.domain._axes_sizes[k_s] = d.size
                f.insert_dim(d, key=k_s)
            #--- End: for
            for aux_key, aux in dst.auxs(axes_superset=axes).iteritems():
                tmp = [axis_map[k_d] for k_d in dst.domain.item_axes(aux_key)]
                f.insert_aux(aux, axes=tmp)
            #--- End: for
        #--- End: if
        
        # Copy across the destination fields coordinate references if necessary
        if not dst_dict:
            for key, ref in dst.refs().iteritems():
                tmp = dst.domain.ref_axes(key)
                if tmp and tmp.issubset(axis_keys_d):
                    f.insert_ref(ref.copy(domain=dst.domain))
                #--- End: if
            #--- End: for
        #--- End: if
                
        # Insert regridded data into new field
        f.insert_data(new_data)
        
        # Release old memory
        regridSrc2Dst.destroy()
        dstfracfield.destroy()
        srcfracfield.destroy()
        dstfield.destroy()
        srcfield.destroy()
        dstgrid.destroy()
        srcgrid.destroy()
        
        return f
    #--- End: def

#--- End: class


# ====================================================================
#
# SubspaceField object
#
# ====================================================================

class SubspaceField(SubspaceVariable):
    '''

An object which will get or set a subspace of a field.

The returned object is a `!SubspaceField` object which may be indexed
to select a subspace by axis index values (``f.subspace[indices]``) or
called to select a subspace by coordinate object array values
(``f.subspace(**coordinate_values)``).

**Subspacing by indexing**

Subspacing by indices allows a subspaced field to be defined via index
values for the axes of the field's data array.

Indices have an extended Python slicing syntax, which is similar to
:ref:`numpy array indexing <numpy:arrays.indexing>`, but with two
important extensions:

* Size 1 axes are never removed.

  An integer index i takes the i-th element but does not reduce the
  rank of the output array by one:

* When advanced indexing is used on more than one axis, the advanced
  indices work independently.

  When more than one axis's slice is a 1-d boolean sequence or 1-d
  sequence of integers, then these indices work independently along
  each axis (similar to the way vector subscripts work in Fortran),
  rather than by their elements:

**Subspacing by coordinate values**

Subspacing by values of one dimensional coordinate objects allows a
subspaced field to be defined via coordinate values of its domain.

Coordinate objects and their values are provided as keyword arguments
to a call to a `SubspaceField` object. Coordinate objects may be
identified by their identities, as returned by their `!identity`
methods. See `cf.Field.indices` for details, since
``f.subspace(**coordinate_values)`` is exactly equivalent to
``f.subspace[f.indices(**coordinate_values)]``.

**Assignment to subspaces**

Elements of a field's data array may be changed by assigning values to
a subspace of the field.

Assignment is only possible to a subspace defined by indices of the
returned `!SubspaceField` object. For example, ``f.subspace[indices] =
0`` is possible, but ``f.subspace(**coordinate_values) = 0`` is *not*
allowed. However, assigning to a subspace defined by coordinate values
may be done as follows: ``f.subspace[f.indices(**coordinate_values)] =
0``.

**Missing data**

The treatment of missing data elements during assignment to a subspace
depends on the value of field's `hardmask` attribute. If it is True
then masked elements will not be unmasked, otherwise masked elements
may be set to any value.

In either case, unmasked elements may be set, (including missing
data).

Unmasked elements may be set to missing data by assignment to the
`cf.masked` constant or by assignment to a value which contains masked
elements.

.. seealso:: `cf.masked`, `hardmask`, `indices`, `where`

:Examples:

>>> print f
Data            : air_temperature(time(12), latitude(73), longitude(96)) K
Cell methods    : time: mean
Dimensions      : time(12) = [15, ..., 345] days since 1860-1-1
                : latitude(73) = [-90, ..., 90] degrees_north
                : longitude(96) = [0, ..., 356.25] degrees_east
                : height(1) = [2] m

>>> f.shape
(12, 73, 96)
>>> f.subspace[...].shape
(12, 73, 96)
>>> f.subspace[slice(0, 12), :, 10:0:-2].shape
(12, 73, 5)
>>> lon = f.coord('X').array
>>> f.subspace[..., lon<180]

>>> f.shape
(12, 73, 96)
>>> f.subspace[0, ...].shape
(1, 73, 96)
>>> f.subspace[3, slice(10, 0, -2), 95].shape
(1, 5, 1)

>>> f.shape
(12, 73, 96)
>>> f.subspace[:, [0, 72], [5, 4, 3]].shape
(12, 2, 3)

>>> f.subspace().shape
(12, 73, 96)
>>> f.subspace(latitude=0).shape
(12, 1, 96)
>>> f.subspace(latitude=cf.wi(-30, 30)).shape
(12, 25, 96)
>>> f.subspace(long=cf.ge(270, 'degrees_east'), lat=cf.set([0, 2.5, 10])).shape
(12, 3, 24)
>>> f.subspace(latitude=cf.lt(0, 'degrees_north'))
(12, 36, 96)
>>> f.subspace(latitude=[cf.lt(0, 'degrees_north'), 90])
(12, 37, 96)
>>> import math
>>> f.subspace(longitude=cf.lt(math.pi, 'radian'), height=2)
(12, 73, 48)
>>> f.subspace(height=cf.gt(3))
IndexError: No indices found for 'height' values gt 3

>>> f.subspace(dim2=3.75).shape
(12, 1, 96)

>>> f.subspace[...] = 273.15
    
>>> f.subspace[f.indices(longitude=cf.wi(210, 270, 'degrees_east'),
...                      latitude=cf.wi(-5, 5, 'degrees_north'))] = cf.masked

>>> index = f.indices(longitude=0)
>>> f.subspace[index] = f.subspace[index] * 2

'''
    __slots__ = []

    def __call__(self, *exact, **kwargs):
        '''

Return a subspace of the field defined by coordinate values.

:Parameters:

    kwargs : *optional*
        Keyword names identify coordinates; and keyword values specify
        the coordinate values which are to be reinterpreted as indices
        to the field's data array.


~~~~~~~~~~~~~~ /??????
        Coordinates are identified by their exact identity or by their
        axis's identifier in the field's domain.

        A keyword value is a condition, or sequence of conditions,
        which is evaluated by finding where the coordinate's data
        array equals each condition. The locations where the
        conditions are satisfied are interpreted as indices to the
        field's data array. If a condition is a scalar ``x`` then this
        is equivalent to the `cf.Query` object ``cf.eq(x)``.

:Returns:

    out : cf.{+Variable}

:Examples:

>>> f.indices(lat=0.0, lon=0.0)
>>> f.indices(lon=cf.lt(0.0), lon=cf.set([0, 3.75]))
>>> f.indices(lon=cf.lt(0.0), lon=cf.set([0, 356.25]))
>>> f.indices(lon=cf.lt(0.0), lon=cf.set([0, 3.75, 356.25]))

'''
        field = self.variable

        if not kwargs:
            return field.copy()    

        # List functionality
        if field._list:
            return type(field)([f.subspace(*exact, **kwargs) for f in field])

        return field.subspace[field.indices(*exact, **kwargs)]
    #--- End: def

    def __getitem__(self, indices):
        '''

Called to implement evaluation of x[indices].

x.__getitem__(indices) <==> x[indices]

Returns a `cf.Field` object.

'''
        field = self.variable

        if indices is Ellipsis:
            return field.copy()

        # List functionality
        if field._list:
            return type(field)([f.subspace[indices] for f in field])

        data = field.Data
        shape = data.shape

        # Parse the index
        indices, roll = parse_indices(field, indices, True)

        if roll:
            axes = data._axes
            cyclic_axes = data._cyclic
            for iaxis, shift in roll.iteritems():
                if axes[iaxis] not in cyclic_axes:
                    raise IndexError(
                        "Can't take a cyclic slice from non-cyclic %r axis" %
                        field.axis_name(iaxis))

                field = field.roll(iaxis, shift)
            #--- End: for
            new = field
        else:            
            new = field.copy(_omit_Data=True)

#        cyclic_axes = []
#        for i, axis in field.data_axes():
#            if field.iscyclic(axis):
#                cyclic_axes.append(i)                
#
#        indices, roll = parse_indices(field, indices, cyclic_axes)
#
#        if roll:
#            for iaxis, x in roll.iteritems():
#                field = field.roll(iaxis, x)
#
#            new = field
#        else:            
#            # Initialise the output field
#            new = field.copy(_omit_Data=True)
        
        # Initialise the output field
#        new = field.copy(_omit_Data=True)

        ## Work out if the indices are equivalent to Ellipsis and
        ## return if they are.
        #ellipsis = True
        #for index, size in izip(indices, field.shape):
        #    if index.step != 1 or index.stop-index.start != size:
        #        ellipsis = False
        #        break
        ##--- End: for
        #if ellipsis:
        #    return new

        # ------------------------------------------------------------
        # Subspace the field's data
        # ------------------------------------------------------------
        new.Data = field.Data[tuple(indices)]
        
        domain = new.domain

        data_axes = domain.data_axes()

        # ------------------------------------------------------------
        # Subspace ancillary variables.
        # 
        # If this is not possible for a particular ancillary variable
        # then it will be discarded from the output field.
        # ------------------------------------------------------------
        if hasattr(field, 'ancillary_variables'):
            new.ancillary_variables = FieldList()

            for av in field.ancillary_variables:
                axis_map = av.domain.map_axes(field.domain)
                av_indices = []
                flip_axes = []

                for avaxis in av.domain.data_axes(): #dimensions['data']:
                    if av.domain._axes_sizes[avaxis] == 1:
                        # Size 1 axes are always ok
                        av_indices.append(slice(None))
                        continue

                    if avaxis not in axis_map:
                        # Unmatched size > 1 axes are not ok
                        av_indices = None
                        break

                    faxis = axis_map[avaxis]
                    if faxis in data_axes:
                        # Matched axes spanning the data arrays are ok
                        i = data_axes.index(faxis)
                        av_indices.append(indices[i])
                        if av.domain.direction(avaxis) != domain.direction(faxis):
                            flip_axes.append(avaxis)
                    else:
                        av_indices = None
                        break                      
                #--- End: for

                if av_indices is not None:
                    # We have successfully matched up each axis of the
                    # ancillary variable's data array with a unique
                    # axis in the parent field's data array, so we can
                    # keep a subspace of this ancillary field
                    if flip_axes:
                        av = av.flip(flip_axes)

                    new.ancillary_variables.append(av.subspace[tuple(av_indices)])
            #--- End: for

            if not new.ancillary_variables:
                del new.ancillary_variables
        #--- End: if

        # ------------------------------------------------------------
        # Subspace fields in coordinate references
        # ------------------------------------------------------------
        refs = new.refs()
        if refs:
            broken = []

            for key, ref in refs.iteritems():
                for term, variable in ref.iteritems():
                    if not isinstance(variable, Field):
                        continue

                    # Still here? Then try to subspace a formula_terms
                    # field.
                    dim_map = variable.domain.map_axes(domain)
                    v_indices = []
                    flip_dims = []

                    for vdim in variable.domain.data_axes():
                        if variable.domain._axes_sizes[vdim] == 1:
                            # We can always index a size 1 axis of the
                            # data array
                            v_indices.append(slice(None))
                            continue
                        
                        if vdim not in dim_map:
                            # Unmatched size > 1 axes are not ok
                            v_indices = None
                            break

                        axis = dim_map[vdim]
                        data_axes = domain.data_axes()
                        if axis in data_axes:
                            # We can index a matched axis which spans
                            # the data array
                            i = data_axes.index(axis)
                            v_indices.append(indices[i])
                            if variable.domain.direction(vdim) != domain.direction(axis):
                                flip_dims.append(vdim)
                        else:
                            v_indices = None
                            break                      
                    #--- End: for

                    if v_indices is not None:
                        # This term is subspaceable
                        if flip_dims:
                            variable = variable.flip(flip_dims)

                        ref[term] = variable.subspace[tuple(v_indices)]
                    else:
                        # This term is broken
                        ref[term] = None
                #--- End: for
            #--- End: for
        #--- End: if

        # ------------------------------------------------------------
        # Subspace the coordinates and cell measures
        # ------------------------------------------------------------
        for key, item in domain.items(role=('d', 'a', 'm'),
                                      axes=data_axes).iteritems():
            item_axes = domain.item_axes(key)

            dice = []
            for axis in item_axes:
                if axis in data_axes:
                    dice.append(indices[data_axes.index(axis)])
                else:
                    dice.append(slice(None))
            #--- End: for

            domain._set(key, item.subspace[tuple(dice)])
        #--- End: for

        for axis, size  in izip(data_axes, new.shape):
            domain._axes_sizes[axis] = size
            
        return new
    #--- End: def

    def __setitem__(self, indices, value):
        '''

Called to implement assignment to x[indices]

x.__setitem__(indices, value) <==> x[indices]

'''
        field = self.variable

        # List functionality
        if field._list:
            for f in field:
                f.subspace[indices] = value
            return

        if isinstance(value, field.__class__):
           value = field._conform_for_assignment(value)
           value = value.Data

        elif numpy_size(value) != 1:
            raise ValueError(
                "Can't assign a size %d %r to a %s data array" %
                (numpy_size(value), value.__class__.__name__,
                 field.__class__.__name__))

        elif isinstance(value, Variable):
            value = value.Data

        field.Data[indices] = value
    #--- End: def

#--- End: class


# ====================================================================
#
# FieldList object
#
# ====================================================================

class FieldList(Field, list):
    '''An ordered sequence of fields.

Each element of a field list is a `cf.Field` object.

A field list supports the python list-like operations (such as
indexing and methods like `!append`), but not the python list
arithmetic and comparison behaviours. Any field list arithmetic and
comparison operation is applied independently to each field element,
so all of the operators defined for a field are allowed.

    '''   

    # Do not ever change this:
    _list = True

    # Do not ever change this:
    _hasData = False

    def __init__(self, fields=None):
        '''
**Initialization**

:Parameters:

    fields : (sequence of) cf.Field, optional
         Create a new field list with these fields.

:Examples:

>>> fl = cf.FieldList()
>>> len(fl)
0
>>> f
<CF Field: air_temperature() K>
>>> fl = cf.FieldList(f)
>>> len(fl
1
>>> fl = cf.FieldList([f, f])
>>> len(fl)
2
>>> fl = cf.FieldList(cf.FieldList([f] * 3))
>>> len(fl)
3
'''
        if fields is not None:
            self.extend(fields)         
    #--- End: def

    def __repr__(self):
        '''
Called by the :py:obj:`repr` built-in function.

x.__repr__() <==> repr(x)
'''
        
        out = [repr(f) for f in self]
        out = ',\n '.join(out)
        return '['+out+']'
    #--- End: def

    def __str__(self):
        '''
Called by the :py:obj:`str` built-in function.

x.__str__() <==> str(x)
'''
        return '\n'.join(str(f) for f in self)
    #--- End: def

    # ================================================================
    # Overloaded list methods
    # ================================================================
    def __getslice__(self, i, j):
        '''

Called to implement evaluation of f[i:j]

f.__getslice__(i, j) <==> f[i:j]

:Examples 1:

>>> g = f[0:1]
>>> g = f[1:-4]
>>> g = f[:1]
>>> g = f[1:]

:Returns:

    out : cf.FieldList

'''
        return type(self)(list.__getslice__(self, i, j))
    #--- End: def

    def __getitem__(self, index):
        '''

Called to implement evaluation of f[index]

f.__getitem_(index) <==> f[index]

:Examples 1:

>>> g = f[0]
>>> g = f[-1:-4:-1]
>>> g = f[2:2:2]

:Returns:

    out : cf.Field or cf.FieldList
        If *index* is an integer then a field is returned. If *index*
        is a slice then a field list is returned, which may be empty.

'''
        out = list.__getitem__(self, index)
        if isinstance(out, list):
            return type(self)(out)
        return out
    #--- End: def

    __len__     = list.__len__
    __setitem__ = list.__setitem__    
    append      = list.append
    extend      = list.extend
    insert      = list.insert
    pop         = list.pop
    reverse     = list.reverse
    sort        = list.sort


    def __contains__(self, y):
        '''

Called to implement membership test operators.

x.__contains__(y) <==> y in x

Each field in the field list is compared with the field's
`~cf.Field.equals` method (as aopposed to the ``==`` operator).

Note that ``y in x`` is equivalent to ``any(g.equals(x) for g in f)``.

'''
        for f in self:
            if f.equals(y):
                return True
        return False
    #--- End: def

    def count(self, x):
        '''

L.count(value) -- return number of occurrences of value

Each field in the {+variable} is compared to *x* with the field's
`~cf.Field.equals` method (as opposed to the ``==`` operator).

Note that ``f.count(x)`` is equivalent to ``sum(g.equals(x) for g in
f)``.

.. seealso:: `cf.Field.equals`, :py:obj:`list.count`

:Examples:

>>> f = cf.FieldList([a, b, c, a])
>>> f.count(a)
2
>>> f.count(b)
1
>>> f.count(a+1)
0

'''
        return len([None for f in self if f.equals(x)])
    #--- End def

    def index(self, x, start=0, stop=None):
        '''
L.index(value, [start, [stop]]) -- return first index of value.

Each field in the {+variable} is compared with the field's
`~cf.Field.equals` method (as aopposed to the ``==`` operator).

It is an error if there is no such field.

.. seealso:: :py:obj:`list.index`

:Examples:

>>> 

'''      
        if start < 0:
            start = len(self) + start

        if stop is None:
            stop = len(self)
        elif stop < 0:
            stop = len(self) + stop

        for i, f in enumerate(self[start:stop]):
            if f.equals(x):
               return i + start
        #--- End: for

        raise ValueError(
            "{0!r} is not in {1}".format(x, self.__class__.__name__))
    #--- End: def

    def remove(self, x):
        '''
L.remove(value) -- remove first occurrence of value.

Each field in the {+variable} is compared with the field's
`~cf.Field.equals` method (as aopposed to the ``==`` operator).

It is an error if there is no such field.

.. seealso:: :py:obj:`list.remove`

'''
        for i, f in enumerate(self):
            if f.equals(x):
                del self[i]
                return

        raise ValueError(
            "{0}.remove(x): x not in {0}".format(self.__class__.__name__))
    #--- End: def

    # ================================================================
    # Special methods
    # ================================================================
    def __array__(self): self._forbidden('special method', '__array__')
    def __data__(self): self._forbidden('special method', '__data__')

    # ================================================================
    # Private methods
    # ================================================================
    def _binary_operation(self, y, method):
        if isinstance(y, self.__class__):
            if len(y) != 1:
                raise ValueError(
                    "Can't {0}: Incompatible {1} lengths ({2}, {3})".format(
                        method, self.__class__.__name__, len(self), len(y)))
            y = y[0]


        if method[2] == 'i':
            # In place
            for f in self:
                f._binary_operation(y, method)
            return self
        else:         
            # Not in place
            return type(self)([f._binary_operation(y, method) for f in self])
    #--- End: def

    def _unary_operation(self, method):
        return type(self)([f._unary_operation(method) for f in self])
    #--- End: def

    def _forbidden(self, x, name):
        raise AttributeError(
            "{0} has no {1} {2!r}. {2!r} may be accessed on each field element.".format(
                self.__class__.__name__, x, name))
    #--- End: def

    # ================================================================
    # CF properties
    # ================================================================
    @property
    def add_offset(self): self._forbidden('CF property', 'add_offset')
    @property
    def calendar(self): self._forbidden('CF property', 'calendar')
    @property
    def cell_methods(self): self._forbidden('CF property', 'cell_methods')
    @property
    def comment(self): self._forbidden('CF property', 'comment')
    @property
    def Conventions(self): self._forbidden('CF property', 'Conventions')
    @property
    def _FillValue(self): self._forbidden('CF property', '_FillValue')
    @property
    def flag_masks(self): self._forbidden('CF property', 'flag_masks')
    @property
    def flag_meanings(self): self._forbidden('CF property', 'flag_meanings')
    @property
    def flag_values(self): self._forbidden('CF property', 'flag_values')
    @property
    def history(self): self._forbidden('CF property', 'history')
    @property
    def institution(self): self._forbidden('CF property', 'institution')
    @property
    def leap_month(self): self._forbidden('CF property', 'leap_month')
    @property
    def leap_year(self): self._forbidden('CF property', 'leap_year')
    @property
    def long_name(self): self._forbidden('CF property', 'long_name')
    @property
    def missing_value(self): self._forbidden('CF property', 'missing_value')
    @property
    def month_lengths(self): self._forbidden('CF property', 'month_lengths')
    @property
    def references(self): self._forbidden('CF property', 'references')
    @property
    def scale_factor(self): self._forbidden('CF property', 'scale_factor')
    @property
    def source(self): self._forbidden('CF property', 'source')
    @property
    def standard_error_multiplier(self): self._forbidden('CF property', 'standard_error_multiplier')
    @property
    def standard_name(self): self._forbidden('CF property', 'standard_name')
    @property
    def title(self): self._forbidden('CF property', 'title')
    @property
    def units(self): self._forbidden('CF property', 'units')
    @property
    def valid_max(self): self._forbidden('CF property', 'valid_max')
    @property
    def valid_min(self): self._forbidden('CF property', 'valid_min')
    @property
    def valid_range(self): self._forbidden('CF property', 'valid_range')

    # ================================================================
    # Attributes
    # ================================================================
    @property
    def ancillary_variables(self): self._forbidden('attribute', '')
    @property
    def array(self): self._forbidden('attribute', 'array')
    @property
    def attributes(self): self._forbidden('attribute', 'attributes')
    @property
    def Data(self): self._forbidden('attribute', 'Data')
    @property
    def data(self): self._forbidden('attribute', 'data')
    @property
    def day(self): self._forbidden('attribute', 'day')
    @property
    def domain(self): self._forbidden('attribute', 'domain')
    @property
    def dtarray(self): self._forbidden('attribute', 'dtarray')
    @property
    def dtvarray(self): self._forbidden('attribute', 'dtvarray')
    @property
    def dtype(self): self._forbidden('attribute', 'dtype')
    @property
    def Flags(self): self._forbidden('attribute', 'Flags')
    @property
    def hardmask(self): self._forbidden('attribute', 'hardmask')
    @property
    def hour(self): self._forbidden('attribute', 'hour')
    @property
    def isscalar(self): self._forbidden('attribute', 'isscalar')
    @property
    def Flags(self): self._forbidden('attribute', 'Flags')
    @property
    def minute(self): self._forbidden('attribute', 'minute')
    @property
    def month(self): self._forbidden('attribute', 'month')
    @property
    def ndim(self): self._forbidden('attribute', 'ndim')
    @property
    def properties(self): self._forbidden('attribute', 'properties')
    @property
    def rank(self): self._forbidden('attribute', 'rank')
    @property
    def second(self): self._forbidden('attribute', 'second')
    @property
#    def subspace(self): self._forbidden('attribute', 'subspace')
#    @property
    def shape(self): self._forbidden('attribute', 'shape')
    @property
    def size(self): self._forbidden('attribute', 'size') 
    @property
    def T(self): self._forbidden('attribute', 'T')
    @property
    def Units(self): self._forbidden('attribute', 'Units')
    @property
    def varray(self): self._forbidden('attribute', 'varray')
    @property
    def X(self): self._forbidden('attribute', 'X')
    @property
    def Y(self): self._forbidden('attribute', 'Y')
    @property
    def year(self): self._forbidden('attribute', 'year')
    @property
    def Z(self): self._forbidden('attribute', 'Z')
    
    # ================================================================
    # Methods
    # ================================================================
    def all(self, *args, **kwargs): self._forbidden('method', 'all')
    def any(self, *args, **kwargs): self._forbidden('method', 'any')
    def allclose(self, *args, **kwargs): self._forbidden('method', 'allclose')
    def aux(self, *args, **kwargs): self._forbidden('method', 'aux')
    def auxs(self, *args, **kwargs): self._forbidden('method', 'auxs')
    def axes(self, *args, **kwargs): self._forbidden('method', 'axes')
    def axes_sizes(self, *args, **kwargs): self._forbidden('method', 'axes_sizes')
    def axis(self, *args, **kwargs): self._forbidden('method', 'axis')
    def axis_name(self, *args, **kwargs): self._forbidden('method', 'axis_name')
    def axis_size(self, *args, **kwargs): self._forbidden('method', 'axis_size')
    def coord(self, *args, **kwargs): self._forbidden('method', 'coord')
    def coords(self, *args, **kwargs): self._forbidden('method', 'coords')
    def cyclic(self, *args, **kwargs): self._forbidden('method', 'cyclic')
    def data_axes(self, *args, **kwargs): self._forbidden('method', 'data_axes')
    def dim(self, *args, **kwargs): self._forbidden('method', 'dim')
    def dims(self, *args, **kwargs): self._forbidden('method', 'dims')
    def field(self, *args, **kwargs): self._forbidden('method', 'field')
    def iscyclic(self, *args, **kwargs): self._forbidden('method', 'iscyclic')
    def insert_aux(self, *args, **kwargs): self._forbidden('method', 'insert_aux')
    def insert_axis(self, *args, **kwargs): self._forbidden('method', 'insert_axis')
    def insert_data(self, *args, **kwargs): self._forbidden('method', 'insert_data')
    def insert_dim(self, *args, **kwargs): self._forbidden('method', 'insert_dim')
    def insert_measure(self, *args, **kwargs): self._forbidden('method', 'insert_measure')
    def insert_ref(self, *args, **kwargs): self._forbidden('method', 'insert_ref')
    def indices(self, *args, **kwargs): self._forbidden('method', 'indices')
    def item(self, *args, **kwargs): self._forbidden('method', 'item')
    def item_axes(self, *args, **kwargs): self._forbidden('method', 'item_axes')
    def items(self, *args, **kwargs): self._forbidden('method', 'items')
    def items_axes(self, *args, **kwargs): self._forbidden('method', 'items_axes')
    def match(self, *args, **kwargs): self._forbidden('method', 'match')
    def max(self, *args, **kwargs): self._forbidden('method', 'max')
    def mean(self, *args, **kwargs): self._forbidden('method', 'mean')
    def measure(self, *args, **kwargs): self._forbidden('method', 'measure')
    def measures(self, *args, **kwargs): self._forbidden('method', 'measures')
    def mid_range(self, *args, **kwargs): self._forbidden('method', 'mid_range')
    def min(self, *args, **kwargs): self._forbidden('method', 'min')
    def period(self, *args, **kwargs): self._forbidden('method', 'period')
    def range(self, *args, **kwargs): self._forbidden('method', 'range')
    def ref(self, *args, **kwargs): self._forbidden('method', 'ref')
    def refs(self, *args, **kwargs): self._forbidden('method', 'refs')
    def remove_axes(self, *args, **kwargs): self._forbidden('method', 'remove_axes')
    def remove_axis(self, *args, **kwargs): self._forbidden('method', 'remove_axis')
    def remove_data(self, *args, **kwargs): self._forbidden('method', 'remove_data')
    def remove_item(self, *args, **kwargs): self._forbidden('method', 'remove_item')
    def remove_items(self, *args, **kwargs): self._forbidden('method', 'remove_items')
    def sample_size(self, *args, **kwargs): self._forbidden('method', 'sample_size')
    def sd(self, *args, **kwargs): self._forbidden('method', 'sd')
    def sum(self, *args, **kwargs): self._forbidden('method', 'sum')
    def unique(self, *args, **kwargs): self._forbidden('method', 'unique')
    def var(self, *args, **kwargs): self._forbidden('method', 'var')
    
    @property
    def binary_mask(self):
        '''For each field, a field of the binary (0 and 1) mask of the data
array.

Values of 1 indicate masked elements.

.. seealso:: `mask`

:Examples:

>>> f[0].shape
(12, 73, 96)
>>> m = f.binary_mask
>>> m[0].long_name
'binary_mask'
>>> m[0].shape
(12, 73, 96)
>>> m[0].dtype
dtype('int32')
>>> m[0].data
<CF Data: [[[1, ..., 0]]] >

        '''
        return self._list_attribute('binary_mask')
    #--- End: def


    @property
    def mask(self):
        '''For each field, a field of the mask of the data array.

Values of True indicate masked elements.

.. seealso:: `binary_mask`

:Examples:

>>> f[0].shape
(12, 73, 96)
>>> m = f.mask
>>> m[0].long_name
'mask'
>>> m[0].shape
(12, 73, 96)
>>> m[0].dtype
dtype('bool')
>>> m[0].data
<CF Data: [[[True, ..., False]]] >

        '''
        return self._list_attribute('mask')
    #--- End: def

#--- End: class
