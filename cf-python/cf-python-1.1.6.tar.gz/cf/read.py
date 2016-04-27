from struct import unpack as struct_unpack

from glob import glob
from os   import SEEK_SET

from os.path import expandvars as os_path_expandvars
from os.path import expanduser as os_path_expanduser

from .field     import Field, FieldList
#from .fieldlist import FieldList
from .functions import flat
from .aggregate import aggregate as cf_aggregate

from .netcdf.read import read as netcdf_read
from .netcdf.read import is_netcdf_file
from .um.read     import read as um_read
from .um.read     import is_um_file

def read(files, verbose=False, ignore_read_error=False,
         aggregate=True, umversion=4.5, nfields=None, squeeze=False,
         unsqueeze=False, fmt=None, select=None, select_options={},
         top_level=None, height_at_top_of_model=None):
    '''Read fields from files into `cf.Field` objects.

A file may be on disk or on a OPeNDAP server.

Any amount of any combination of CF-netCDF, CFA-netCDF and Met Office
(UK) PP format files may be read.

**netCDF files**
   * The netCDF variable names of the field and its components are
     stored in their `!ncvar` attributes.
   
   * Fields referenced within coordinate reference or ancillary
     variables objects are not included in the returned list of
     fields.

**PP files**
   * If any PP files are read then the *aggregate* option
     ``'relaxed_units'`` is set to True for all input files.
    
   * STASH code to standard conversion uses the table in
     ``cf/etc/STASH_to_CF.txt``.

**Files on OPeNDAP servers**
   * All files on OPeNDAP servers are assumed to be netCDF files.

.. seealso:: `cf.write`

:Parameters:

    files : (arbitrarily nested sequence of) str

        A string or arbitrarily nested sequence of strings giving the
        file names or OPenDAP URLs from which to read fields. Various
        type of expansion are applied to the file names:
        
          ====================  ======================================
          Expansion             Description
          ====================  ======================================
          Tilde                 An initial component of ``~`` or
                                ``~user`` is replaced by that *user*'s
                                home directory.
           
          Environment variable  Substrings of the form ``$name`` or
                                ``${name}`` are replaced by the value
                                of environment variable *name*.

          Pathname              A string containing UNIX file name
                                metacharacters as understood by the
                                :py:obj:`glob` module is replaced by
                                the list of matching file names. This
                                type of expansion is ignored for
                                OPenDAP URLs.
          ====================  ======================================
    
        Where more than one type of expansion is used in the same
        string, they are applied in the order given in the above
        table.

          Example: If the environment variable *MYSELF* has been set
          to the "david", then ``'~$MYSELF/*.nc'`` is equivalent to
          ``'~david/*.nc'``, which will read all netCDF files in the
          user david's home directory.
  
    verbose : bool, optional
        If True then print information to stdout.
    
    umversion : int or float, optional
        Met Office (UK) PP files and Met Office (UK) fields files
        only, the Unified Model (UM) version to be used when decoding
        the PP header. Valid versions are, for example, ``402`` or
        ``4.2`` (v4.2), ``606.3`` (v6.6.3) and ``1001`` or ``10.1``
        (v10.1). The default version is ``4.5`` (v4.5). The version is
        ignored if it can be inferred from the PP headers, which will
        generally be the case for files created at v5.3 and
        later. Note that the PP header can not encode tertiary version
        elements (such as the ``3`` in ``606.3``), so it may be
        necessary to provide a UM version in such cases.
    
        Ignored for any other type of input files.

    ignore_read_error : bool, optional
        If True then ignore any file which raises an IOError whilst
        being read, as would be the case for an empty file, unknown
        file format, etc. By default the IOError is raised.
    
    fmt : str, optional
        Only read files of the given format, ignoring all other
        files. Valid formats are ``'NETCDF'`` for CF-netCDF files,
        ``'CFA'`` for CFA-netCDF files and ``'PP'`` for PP files and
        'FF' for UM fields files. By default files of any of these
        formats are read.  default files of any of these formats are
        read.

    aggregate : bool or dict, optional
        If True (the default) or a (possibly empty) dictionary then
        aggregate the fields read in from all input files into as few
        fields as possible using the CF aggregation rules. If
        *aggregate* is a dictionary then it is passed as keyword
        arguments to the `cf.aggregate` function. If False then the
        fields are not aggregated.

    squeeze : bool, optional
        If True then remove size 1 axes from each field's data array.

    unsqueeze : bool, optional
        If True then insert size 1 axes from each field's domain into
        its data array.

    select, select_options : *optional*
        Only return fields which satisfy the given conditions on their
        property values. Only fields which, prior to any aggregation,
        satisfy ``f.match(select, **select_options) == True`` are
        returned. See `cf.Field.match` for details.

    top_level : (sequence of) str, optional
        Promote field components to independent top-level fields. The
        *top_level* parameter may be or, or a sequence, of:

          ===============  ===========================================
          *top_level*      Extra top-level fields
          ===============  ===========================================
          ``'reference'``  Fields in coordinate reference objects
          ``'ancillary'``  Ancillary data fields
          ``'field'``      Fields in coordinate references and
                           ancillary data fields
          ``'auxiliary'``  Auxiliary coordinate objects
          ``'measure'``    Cell measure objects
          ``'all'``        All of the above
          ===============  ===========================================

            *Example:*
              To promote fields in coordinate reference objects:
              ``top_level='reference'`` or ``top_level=['reference']``.

            *Example:*
              To promote ancillary data fields and cell measure
              objects: ``top_level=['ancillary', 'measure']``.

        .. versionadded:: 1.0.4

:Returns:
    
    out : cf.FieldList or cf.Field
        A list of fields, or if there is only one field, the
        individual field.

:Examples:

>>> f = cf.read('file*.nc')
>>> f
[<CF Field: pmsl(30, 24)>,
 <CF Field: z-squared(17, 30, 24)>,
 <CF Field: temperature(17, 30, 24)>,
 <CF Field: temperature_wind(17, 29, 24)>]

>>> cf.read('file*.nc')[0:2]
[<CF Field: pmsl(30, 24)>,
 <CF Field: z-squared(17, 30, 24)>]

>>> cf.read('file*.nc')[-1]
<CF Field: temperature_wind(17, 29, 24)>

>>> cf.read('file*.nc', select='units:K)
[<CF Field: temperature(17, 30, 24)>,
 <CF Field: temperature_wind(17, 29, 24)>]

>>> cf.read('file*.nc', select='ncvar%ta')
<CF Field: temperature(17, 30, 24)>

>>> cf.read('file*.nc', select={'standard_name': '.*pmsl*', 'units':['K', 'Pa']})
<CF Field: pmsl(30, 24)>

>>> cf.read('file*.nc', select={'units':['K', 'Pa']})
[<CF Field: pmsl(30, 24)>,
 <CF Field: temperature(17, 30, 24)>,
 <CF Field: temperature_wind(17, 29, 24)>]

    '''
    if squeeze and unsqueeze:
        raise ValueError("Can't squeeze and unsqueeze whilst reading")

    # Initialize the output list of fields
    field_list = FieldList()

    if isinstance(aggregate, dict):
        aggregate_options = aggregate.copy()
        aggregate         = True
    else:
        aggregate_options = {}

    aggregate_options['copy'] = False
    
    # Parse umversion
    if umversion is not None:
        umversion = float(str(umversion).replace('.', '0', 1))

    # ----------------------------------------------------------------
    # Parse top_level
    # ----------------------------------------------------------------
    promote = top_level
    if promote is None:
        promote = ()
    elif isinstance(promote, basestring):
        promote = (promote,)

#    if 'all' in promote:
#        promote = set(('field', 'coordinate', 'measure'))
        

    # Count the number of fields (in all files) and the number of
    # files
    field_counter = -1
    file_counter  = 0

    for file_glob in flat(files):

        # Expand variables
        file_glob = os_path_expanduser(os_path_expandvars(file_glob))

        if file_glob.startswith('http://'):
            # Do not glob a URL
            files2 = (file_glob,)
        else:
            # Glob files on disk
            files2 = glob(file_glob)
            if not files2 and not ignore_read_error:
                open(file_glob, 'rb')
        #--- End: if

        for filename in files2:
            # Print some informative messages
            if verbose:
                print 'File: %s' % filename

            # --------------------------------------------------------
            # Read the file into fields
            # --------------------------------------------------------
            fields = _read_a_file(filename,
                                  ignore_read_error=ignore_read_error,
                                  verbose=verbose,
                                  aggregate=aggregate,
                                  aggregate_options=aggregate_options,
                                  umversion=umversion,
                                  selected_fmt=fmt,
                                  promote=promote,
                                  height_at_top_of_model=height_at_top_of_model)
            
            # --------------------------------------------------------
            # Select matching fields
            # --------------------------------------------------------
            if select or select_options:
                fields = fields.select(select, **select_options)

            # --------------------------------------------------------
            # Add this file's fields to those already read from other
            # files
            # --------------------------------------------------------
            field_list.extend(fields)
   
            field_counter = len(field_list)
            file_counter += 1
        #--- End: for            
    #--- End: for     

    # Error check
    if not ignore_read_error:
        if not file_counter:
            raise RuntimeError('No files found')
        if not field_list:
            raise RuntimeError('No fields found from '+str(file_counter)+' files')
    #--- End: if

    # Print some informative messages
    if verbose:
        print("Read {0} field{1} from {2} file{3}".format( 
              (field_counter, _plural(field_counter),
               file_counter , _plural(file_counter))))
    #--- End: if
    
    # ----------------------------------------------------------------
    # Aggregate the output fields
    # ----------------------------------------------------------------
    if aggregate and len(field_list) > 1:
        if verbose:
            org_len = len(field_list)
            
        field_list = cf_aggregate(field_list, **aggregate_options)
        
        if verbose:
            n = len(field_list)
            print('{0} input field{1} aggregated into {2} field{3}'.format(
                  (org_len, _plural(org_len), 
                   n, _plural(n))))
    #--- End: if

    # ----------------------------------------------------------------
    # Add standard names to UM fields
    # ----------------------------------------------------------------
    for f in field_list:
        standard_name = getattr(f, '_standard_name', None)
        if standard_name is not None:
            f.standard_name = standard_name
            del f._standard_name
    #--- End: for

    # ----------------------------------------------------------------
    # Squeeze size one dimensions from the data arrays. Do one of:
    # 
    # 1) Squeeze the fields, i.e. remove all size one dimensions from
    #    all field data arrays
    #
    # 2) Unsqueeze the fields, i.e. Include all size 1 domain
    #    dimensions in the data array.
    #
    # 3) Nothing
    # ----------------------------------------------------------------
    if squeeze:
        field_list.squeeze(i=True)
    elif unsqueeze:
        field_list.unsqueeze(i=True)

    if nfields is not None and len(field_list) != nfields:
        raise ValueError(
            "Error whilst reading file{0}: {1} field{2} requested but {3} found".format(
                _plural(file_counter),
                nfields,
                _plural(nfields),
                len(field_list)))

    if len(field_list) == 1:
        # Return a field instead of a field list
        field_list = field_list[0]

    return field_list
#--- End: def

def _plural(n):
    return 's' if n !=1 else ''

def _read_a_file(filename,
                 aggregate=True,
                 aggregate_options={},
                 ignore_read_error=False,
                 verbose=False,
                 umversion=None,
                 selected_fmt=None,
                 promote=(),
                 height_at_top_of_model=None):
    '''

Read the contents of a single file into a field list.

:Parameters:

    filename : str
        The file name.

    aggregate_options : dict, optional
        The keys and values of this dictionary may be passed as
        keyword parameters to an external call of the aggregate
        function.

    ignore_read_error : bool, optional
        If True then return an empty field list if reading the file
        produces an IOError, as would be the case for an empty file,
        unknown file format, etc. By default the IOError is raised.
    
    verbose : bool, optional
        If True then print information to stdout.
    
:Returns:

    out : FieldList
        The fields in the file.

:Raises:

    IOError :
        If *ignore_read_error* is False and

        * The file can not be opened.

        * The file can not be opened.

'''
    # Find this file's type
    try:
        ftype = file_type(filename)        
    except Exception as error:
        if ignore_read_error: 
            if verbose:
                print('WARNING: %s' % error)
            return FieldList()
        raise error
    #--- End: try

    # ----------------------------------------------------------------
    # Still here? Read the file into fields.
    # ----------------------------------------------------------------
    if ftype == 'netCDF' and (selected_fmt in (None, 'NETCDF', 'CFA')):
        fields = netcdf_read(filename, fmt=selected_fmt, promote=promote,
                             verbose=verbose)
        
    elif ftype == 'UM' and (selected_fmt in (None, 'PP', 'FF')):
        fields = um_read(filename, um_version=umversion,
                         verbose=verbose, set_standard_name=False,
                         height_at_top_of_model=height_at_top_of_model)

        # PP fields are aggregated intrafile prior to interfile
        # aggregation
        if aggregate:
            # For PP fields, the default is strict_units=False
            if 'strict_units' not in aggregate_options:
                aggregate_options['relaxed_units'] = True
        #--- End: if

    # Add more file formats here ...

    else:
        fields = FieldList()

    # ----------------------------------------------------------------
    # Return the fields
    # ----------------------------------------------------------------
    return fields
#--- End: def

def file_type(filename):
    '''

:Parameters:

    filename : str
        The file name.

:Returns:

    out : str
        The format type of the file.

:Raises:
 
    IOError :
        If the file has an unsupported format.

:Examples:

>>> ftype = file_type(filename)

''' 
    # ----------------------------------------------------------------
    # Assume that URLs are in netCDF format
    # ----------------------------------------------------------------
    if filename.startswith('http://'):
       return 'netCDF'

    # ----------------------------------------------------------------
    # netCDF
    # ----------------------------------------------------------------
    if is_netcdf_file(filename):
        return 'netCDF'

    # ----------------------------------------------------------------
    # PP or FF
    # ----------------------------------------------------------------
    if is_um_file(filename):
        return 'UM'

    # ----------------------------------------------------------------
    # Developers: Add more file formats here ...
    # ----------------------------------------------------------------

    # Still here?
    raise IOError("File %s has unsupported format" % filename)
#--- End: def
