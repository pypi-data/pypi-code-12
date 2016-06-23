
result.partitions = PartitionMatrix(numpy_empty(new_pmshape, dtype=object),
                                    pmaxes)

result.partitions[:, :, 0] = data0.partitions.matrix

for partition in result.partitions.matrix[:, :, 0].flat:
    indices = partition.indices
    array0  = partition.dataarray(**pda_args)

    if broadcasting:
        indices = tuple([
                (index if not broadcast_index else broadcast_index) 
                for index, broadcast_index in izip(
                    indices[align_offset:], broadcast_indices)
                ])
        indices = (Ellipsis,) + indices
    #--- End: if

    hhh = other[indices]

    if not broadcasting or hhh.smaller_than_a_chunk():
        array1 = hhh.array
        array0 = poop(array0, array1, method)
    else:
        for partition1 in hhh.partitions.flat:
            array1 = asdasds
            partition.subarray = poop(array0.copy(), array1, method)            
            result.partitions.matrix[i, j, k] = partition1
    

def poop(array0, array1, method):
    # --------------------------------------------------------
    # Do the binary operation on this partition's data
    # --------------------------------------------------------
    try:
        array0 = getattr(array0, method)(array1)
    except FloatingPointError as error:
        # Floating point point errors have been trapped
        if _mask_fpe[0]:
            # Redo the calculation ignoring the errors and
            # then set invalid numbers to missing data
            numpy_seterr(**_seterr_raise_to_ignore)
            array0 = getattr(array0, method)(array1)
            array0 = numpy_ma_masked_invalid(array0, copy=False)
            numpy_seterr(**_seterr) 
        else:
            # Raise the floating point error exception
            raise FloatingPointError(error)
    #--- End: try

    if new_isdt:
        # Convert result array to a date-time object array
        array0 = rt2dt(array0, data0.Units)
        
    if array0 is NotImplemented:
        array0 = numpy_zeros(partition.shape, dtype=bool)
        
    return array0 
#--- End: def
