
def incrementName(nameList, name):
    '''    
    return a name that is unique in a given nameList through 
    attaching a number to it
    
    >>> l = []

    now we will add 3xfoo 2xbar and one klaus to our list:

    >>> l.append( incrementName(l,'foo') )
    >>> l.append( incrementName(l,'bar') )
    >>> l.append( incrementName(l,'foo') )
    >>> l.append( incrementName(l,'foo') )
    >>> l.append( incrementName(l,'bar') )
    >>> l.append( incrementName(l,'klaus') )

    >>> print sorted(l)
    ['bar', 'bar2', 'foo', 'foo2', 'foo3', 'klaus']
    '''
    if not name in nameList:
        return name
    newName = name + str(1)
    for n in range(1,len(nameList)+2):
        found = False
        for b in nameList:
            newName = name + str(n)
            if b == newName:
                found = True
        if not found:
            break
    return newName



if __name__ == "__main__":
    import doctest
    doctest.testmod()