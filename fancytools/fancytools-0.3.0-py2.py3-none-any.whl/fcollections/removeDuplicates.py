
# This is the winner of a comparison of multiple
# methods for removing duplicates from a list, shamelessly taken from
# 
# http://www.peterbe.com/plog/uniqifiers-benchmark
# 
# remember: if you dont need to preserve the order you can simply
# type:
# 
# >>>list(set(my_list))





def removeDuplicates(seq, idfun=None): 
    '''
    removal all duplicates from a list, preserving the order:
    
    >>> a=list('ABeeECcc')
    >>> removeDuplicates(a)
    ['A', 'B', 'e', 'E', 'C', 'c']
    
    >>> removeDuplicates(a, lambda x: x.lower())
    ['A', 'B', 'e', 'C']
    '''
    
    # order preserving
    if idfun is None:
        def idfun(x): return x
    seen = {}
    result = []
    for item in seq:
        marker = idfun(item)
        # in old Python versions:
        # if seen.has_key(marker)
        # but in new ones:
        if marker in seen: continue
        seen[marker] = 1
        result.append(item)
    return result


if __name__ == '__main__':
    import doctest
    doctest.testmod()
