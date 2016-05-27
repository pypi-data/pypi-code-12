import numpy as np


def boundingBox(booleanArray):
    '''
    return indices of the smallest bounding box enclosing all 
    non-zero values within an array

    >>> a = np.array([ [0,0,0,0],
    ...                [0,1,0,1],
    ...                [0,0,1,0],
    ...                [1,0,0,0],
    ...                [0,0,0,0] ])
    >>> print boundingBox(a)
    (slice(1, 3, None), slice(0, 3, None))
    '''
    
    w = np.where(booleanArray)
    p = []
    for i in w:
        if len(i):
            p.append(slice(i.min(),i.max()))
        else:
            p.append(slice(0,0))
            return None
    return tuple(p)
    

 
if __name__ == '__main__':
    import doctest
    doctest.testmod()