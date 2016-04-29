try:
    import numpy as _np
except ImportError:
    print "Numpy did not import, some functions may not work - continuing..."

def conv_to_bandsfirst(img):
    """Convert a numpy array to bands first format - this is useful for
    converting an array used by matplotlib into a "standard" gdal format.
    """
    return _np.transpose(img,(2,0,1))

def conv_to_bandslast(img):
    """Convert a numpy array to bands last format - this is useful for passing
    an array pulled by gdal into a format the can easily be used with
    matplotlib.
    """
    return _np.transpose(img,(1,2,0))

def flip_xy(img):
    """Flip the xy components of a numpy array pulled from an image.  If the
    image has three dims, this is done on the seond and third dims.  If it
    is only two, then they are just flipped.
    """
    raise ValueError("Not value error... just not implemented for now.")
    if img.ndim == 2:
        return _np.transpose(img)
    elif ndims == 3:
        return _np.transpose(img,(0,2,1))
    else:
        raise ValueError("This function is not defined for arrays with "
                         "dimensions other than 2 or 3.")
