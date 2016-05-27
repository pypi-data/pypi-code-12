from numba import jit





@jit(nopython=True)   
def evalPatternInArray(pattern, arr):
    '''
    returns similarity parameter of given pattern to be
    repeated in given array
    the index is scalled between 0-1
    with 0 = identical
    and val>1 = different


    >>> arr = [0,0.5,1,  0, 0.5,1,   0,0.5,1]
    >>> pattern = [0,0.5,1]
    >>> evalPatternInArray(pattern, arr)
    0

    >>> arr = [0,0.5,1,  0, 0.6,1,   0,0.5,1]
    >>> pattern = [0,0.5,1]
    >>> evalPatternInArray(pattern, arr)
    0.09090909090909088


    >>> arr = [0,0.5,1,  0, 0.6,1,   0,0.5,1]
    >>> pattern = [1,0.5,-2]
    >>> evalPatternInArray(pattern, arr)
    162.2057359307358
    
    '''
    l = len(pattern)
    ll = len(arr)
    #print l, ll
    mx_additions = 3
    sim = 0
    i = 0
    j = 0
    c = 0
    p = pattern[j]
    v = arr[i]

    while True:
        #relative difference:
        if p == v:
            d = 0
        elif v+p == 0:
            d = v
        else:
            d = (p-v)/(v+p)
        #print d
        if abs(d) < 0.15:
            c = mx_additions
            j += 1
            i += 1
            if j == l:
                j = 0
            if i == ll:
                #print sim, v, p,a
                return sim
            p = pattern[j]
            v = arr[i]
            
        elif d < 0:
            #surplus line
            c += 1
            j += 1
            if j == l:
                j = 0
            p += pattern[j]
            sim += abs(d)
        else:
            #line missing
            c += 1
            i += 1
            if i == ll:
                return sim
            v += arr[i]
            sim += abs(d)
        if c == mx_additions:
            sim += abs(d)


    
if __name__ == "__main__":
#     import numpy as np
#     
#     p = np.array([  53.54507214,   35.17027143,  147.04964467,  147.10031907,
#              80.81610302])
#     d = np.array([  72.,  146.,  150.,   73.,   85.,  157.,  147.,   70.,   85.,
#             155.,  141.,   85.,   73.,  150.,  154.,   68.,   87.,  142.,
#             154.,   72.,   85.,  147.,  147.,   30.,   40.])
# 
#     p2 = np.array([  53.54507214+35.17027143,  147.04964467,  147.10031907,
#              80.81610302])
# 
#     print evalPatternInArray(p2, d)

    import doctest
    doctest.testmod()