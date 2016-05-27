

class ProxyList(list):
    '''
    forwards an attribute/method given to this instance
    to its list-entries
    
    STRING LIST
    ===========
    create a list
    >>> a = ProxyList(('aa',11,'cc'))
    
    find 'a' in the list
    because 'find' is not a method of this instance
    all list-entries will be given this method
    

    >>> print a.find('a')
    [0, None, -1]
    
    ... this returns a list saying that...
    [0,...    --> 'a' is in the first position of the first entry
    ..., None --> there is no fitting method for the second entry
    ... ,-1 ] --> 'a' is not found in the last entry
    
    FIND MEMBERS
    ============
    show indices of list entries that are of type string
    
    >>> print a.where('__class__',str)
    [0, 2]
    

    ACCESS MEMBER FUNCTIONS
    =======================
    ...using _TestObject which has one one extra method 'foo'

    >>> p = ProxyList([_TestObject(),_TestObject(),_TestObject()])
    >>> print p.foo[0].__name__
    foo
    
    each time 'foo' is called it returns ('bar', 99)
    therefore for each member of the ProxyList the output would be:
    
    >>> print p.foo('bar')
    [('bar', 99), ('bar', 99), ('bar', 99)]
    
    Also this method sets an attribute 'a' to 'bar'->
    
    >>> print p.a
    ['bar', 'bar', 'bar']
    
    MATHEMATICAL OPERATIONS
    =======================
    + - * / etc can also be forwarded to the members of a list:
    
    >>> p = ProxyList([ 1, -20, 3 ])
    >>> p += 10
    >>> print p
    [11, -10, 13]
    
    >>> print p.__abs__()
    [11, 10, 13]


    MUTABLE MEMBERS
    ===============
    If the members are mutable their id remains the same:
    
    >>> p = ProxyList([ [1], [2], [3] ])
    >>> oldID = id(p[0])
    >>> p *= 4
    >>> newID = id(p[0])
    >>> print oldID == newID
    True
    
    
    TWO PROXYLISTS
    ==============
    A ProxyList can be used for a mathematical operation with another ProxyList:
    
    >>> p1 = ProxyList([ 1, 2, 3 ])
    >>> p2 = ProxyList([ 1, 2, 3 ])
    >>> p1-p2
    [0, 0, 0]
    '''
    
    #GET
    def __getattr__(self, attr):
            try:
                return list.__getattribute__(self, attr)
            except AttributeError:
                return _CallList( getattr(x, attr, AttributeNotFound) for x in self )

    
    #SET
    def __setattr__(self, attr, value):
        return [setattr(x, attr, value[n]) for n,x in enumerate(self)]
        #print attr, value


    #FIND IN MEMBERS 
    def where(self, attr, value):
        return [n for n,x in enumerate(self) if getattr(x, attr, AttributeNotFound) == value]
        #return next((n for n,x in enumerate(self) if getattr(x, attr, _pass) == value), None)


    #ADDITION
    def __add__(self, val):
        if isinstance(val, ProxyList):
            return [ch.__add__(v) for v,ch in zip(val, self)]
        return [ch.__add__(val) for ch in self]


    def __iadd__(self, val):
        if isinstance(val, ProxyList):
            return [ch.__iadd__(v) for v,ch in zip(val, self)]
        try:
            # mutable types
            [ch.__iadd__(val) for ch in self]
        except AttributeError:
            # immutable types or not ixxx available
            for n,ch in enumerate(self):
                if ch != AttributeNotFound:
                    self[n] = ch.__add__(val)
        return self


    #SUBTRACTION
    def __sub__(self, val):
        if isinstance(val, ProxyList):
            return [ch.__sub__(v) for v,ch in zip(val, self)]
        return [ch.__sub__(val) for ch in self]
    
    
    def __isub__(self, val):
        if isinstance(val, ProxyList):
            return [ch.__isub__(v) for v,ch in zip(val, self)]
        try:
            # mutable types
            [ch.__isub__(val) for ch in self]
        except AttributeError:
            # immutable types or not ixxx available
            for n,ch in enumerate(self):
                self[n] = ch.__sub__(val)
        return self


    #MULTIPLICATION
    def __mul__(self, val):
        if isinstance(val, ProxyList):
            return [ch.__mul__(v) for v,ch in zip(val, self)]
        return [ch.__mul__(val) for ch in self]


    def __imul__(self, val):
        if isinstance(val, ProxyList):
            return [ch.__imul__(v) for v,ch in zip(val, self)]
        try:
            # mutable types
            [ch.__imul__(val) for ch in self]
        except AttributeError:
            # immutable types or not ixxx available
            for n,ch in enumerate(self):
                self[n] = ch.__mul__(val)
        return self


    #DIVISION
    def __div__(self, val):
        if isinstance(val, ProxyList):
            return [ch.__truediv__(v) for v,ch in zip(val, self)]
        return [ch.__truediv__(val) for ch in self]


    def __idiv__(self, val):
        if isinstance(val, ProxyList):
            return [ch.__itruediv__(v) for v,ch in zip(val, self)]
        try:
            # mutable types
            [ch.__itruediv__(val) for ch in self]
        except AttributeError:
            # immutable types
            for n,ch in enumerate(self):
                self[n] = ch.__truediv__(val)
        return self       
       



class _TestObject(object):
    '''this is just a test class for the doctest of ProxyList'''
    def foo(self, x):
        self.a = x
        return x,99


class _CallList(ProxyList):
    def __call__(self, *arg, **kwarg):
        return [x(*arg, **kwarg) for x in self]


def AttributeNotFound(*args, **kwargs):
    pass


if __name__ == "__main__":

    import doctest
    doctest.testmod()