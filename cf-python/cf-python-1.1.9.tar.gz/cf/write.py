from .netcdf.write import write as netcdf_write

def write(fields, filename, fmt='NETCDF3_CLASSIC', overwrite=True,
          verbose=False, cfa_options=None, mode='w',
          least_significant_digit=None, endian='native',
          compress=0, fletcher32=False, no_shuffle=False,
          datatype=None, single=False, double=False):
    '''Write fields to a CF-netCDF or CFA-netCDF file.
    
NetCDF dimension and variable names will be taken from variables'
`~Variable.ncvar` attributes and the domain attribute
`~Domain.nc_dimensions` if present, otherwise they are inferred from
standard names or set to defaults. NetCDF names may be automatically
given a numerical suffix to avoid duplication.

Output netCDF file global properties are those which occur in the set
of CF global properties and non-standard data variable properties and
which have equal values across all input fields.

Logically identical field components are only written to the file
once, apart from when they need to fulfil both dimension coordinate
and auxiliary coordinate roles for different data variables.

.. seealso:: `cf.read`

:Parameters:

    fields : (arbitrarily nested sequence of) Field or FieldList
        The field or fields to write to the file.

    filename : str
        The output netCDF file. Various type of expansion are applied
        to the file names:
        
          ====================  ======================================
          Expansion             Description
          ====================  ======================================
          Tilde                 An initial component of ``~`` or
                                ``~user`` is replaced by that *user*'s
                                home directory.
           
          Environment variable  Substrings of the form ``$name`` or
                                ``${name}`` are replaced by the value
                                of environment variable *name*.
          ====================  ======================================
    
        Where more than one type of expansion is used in the same
        string, they are applied in the order given in the above
        table.

          Example: If the environment variable *MYSELF* has been set
          to the "david", then ``'~$MYSELF/out.nc'`` is equivalent to
          ``'~david/out.nc'``.
  
    fmt : str, optional
        The format of the output file. One of:

           =====================  ================================================
           fmt                    Description
           =====================  ================================================
           ``'NETCDF3_CLASSIC'``  Output to a CF-netCDF3 classic format file     
           ``'NETCDF3_64BIT'``    Output to a CF-netCDF3 64-bit offset format file 
           ``'NETCDF4_CLASSIC'``  Output to a CF-netCDF4 classic format file      
           ``'NETCDF4'``          Output to a CF-netCDF4 format file              
           ``'CFA3'``             Output to a CFA-netCDF3 classic format file 
           ``'CFA4'``             Output to a CFA-netCDF4 format file 
           =====================  ================================================

        By default the *fmt* is ``'NETCDF3_CLASSIC'``. Note that the
        netCDF3 formats may be slower than any of the other options.

    overwrite: bool, optional
        If False then raise an exception if the output file
        pre-exists. By default a pre-existing output file is over
        written.

    verbose : bool, optional
        If True then print one-line summaries of each field written.

    cfa_options : dict, optional
        A dictionary giving parameters for configuring the output
        CFA-netCDF file:

           ==========  ===============================================
           Key         Value
           ==========  ===============================================
           ``'base'``  * If ``None`` (the default) then file names
                         within CFA-netCDF files are stored with
                         absolute paths.

                       * If set to an empty string then file names
                         within CFA-netCDF files are given relative to
                         the directory or URL base containing the
                         output CFA-netCDF file.

                       * If set to a string then file names within
                         CFA-netCDF files are given relative to the
                         directory or URL base described by the
                         value. For example: ``'../archive'``.
           ==========  ===============================================        

        By default no parameters are specified.
    
    mode : str, optional
        Specify the mode of write access for the output file. One of:

           =======  =====================================================
           mode     Description
           =======  =====================================================
           ``'w'``  Open a new file for writing to. If it exists and
                    *overwrite* is True then the file is deleted prior to
                    being recreated.
           =======  =====================================================
       
        By default the file is opened with write access mode ``'w'``.

    endian : str, optional
        The endian-ness of the output file. Valid values are
        ``'little'``, ``'big'`` or ``'native'``. By default the output
        is native endian.

    compress : int, optional
        Regulate the speed and efficiency of compression. Must be an
        integer between ``0`` and ``9``. ``0`` means no compression;
        ``1`` is the fastest, but has the lowest compression ratio;
        ``9`` is the slowest but best compression ratio. The default
        value is ``0``. An exception is raised if compression is
        requested for a netCDF3 output file format.
    
    least_significant_digit : int, optional
        Truncate the input field data arrays. For a positive integer,
        N the precision that is retained in the compressed data is '10
        to the power -N'. For example, a value of ``2`` will retain a
        precision of 0.01. In conjunction with the *compress*
        parameter this produces 'lossy', but significantly more
        efficient compression.

    fletcher32 : bool, optional
        If True then the Fletcher-32 HDF5 checksum algorithm is
        activated to detect compression errors. Ignored if *compress*
        is ``0``.

    no_shuffle : bool, optional
        If True then the HDF5 shuffle filter (which de-interlaces a
        block of data before compression by reordering the bytes by
        storing the first byte of all of a variable's values in the
        chunk contiguously, followed by all the second bytes, and so
        on) is turned off. By default the filter is applied because if
        the data array values are not all wildly different, using the
        filter can make the data more easily compressible.  Ignored if
        *compress* is ``0``.

    datatype : dict, optional
        Specify data type conversions to be applied prior to writing
        data to disk. Arrays with data types which are not specified
        remain unchanged. By default, input data types are
        preserved. Data types defined by `numpy.dtype` objects in a
        dictionary whose are input data types with values of output
        data types.

          **Example:**
            To convert 64-bit floats and 64-bit integers to their
            32-bit counterparts: ``datatype={numpy.dtype('float64'):
            numpy.dtype('float32'), numpy.dtype('int64'):
            numpy.dtype('int32')}``.
       
    single : bool, optional
        Write 64-bit floats as 32-bit floats and 64-bit integers as
        32-bit integers. By default, input data types are
        preserved. Note that ``single=True`` is exactly equivalent to
        ``datatype={numpy.dtype('float64'): numpy.dtype('float32'),
        numpy.dtype('int64'): numpy.dtype('int32')}``.
       
    double : bool, optional
        Write 32-bit floats as 64-bit floats and 32-bit integers as
        64-bit integers. By default, input data types are
        preserved. Note that ``double=True`` is exactly equivalent to
        ``datatype={numpy.dtype('float32'): numpy.dtype('float64'),
        numpy.dtype('int32'): numpy.dtype('int64')}``.
 
:Returns:

    None

:Raises:

    IOError :
        If *overwrite* is False and the output file pre-exists.

:Examples:

>>> f
[<CF Field: air_pressure(30, 24)>,
 <CF Field: u_compnt_of_wind(19, 29, 24)>,
 <CF Field: v_compnt_of_wind(19, 29, 24)>,
 <CF Field: potential_temperature(19, 30, 24)>]
>>> write(f, 'file')

>>> type(f)
<class 'cf.field.FieldList'>
>>> type(g)
<class 'cf.field.Field'>
>>> cf.write([f, g], 'file.nc', verbose=True)
[<CF Field: air_pressure(30, 24)>,
 <CF Field: u_compnt_of_wind(19, 29, 24)>,
 <CF Field: v_compnt_of_wind(19, 29, 24)>,
 <CF Field: potential_temperature(19, 30, 24)>]

    '''      
    if fields:
        netcdf_write(fields, filename, fmt=fmt, overwrite=overwrite,
                     verbose=verbose, cfa_options=cfa_options,
                     mode=mode,
                     least_significant_digit=least_significant_digit,
                     endian=endian, compress=compress,
                     no_shuffle=no_shuffle, fletcher32=fletcher32,
                     datatype=datatype, single=single, double=double)
#--- End: def
