# -*- coding: utf-8 -*-

class MultiList(object):
    '''
    create a list of named lists.
    can be used as like a normal list but allows to get entries from direct from sublists

    >>> l = MultiList('spam','eggs')
    >>> l.extend( ([1,2],[3,4]) )
    >>> print l.spam
    [1, 2]
    >>> print l.eggs
    [3, 4]
    >>> print l[1]
    [2, 4]
    '''
    
    #TODO: better as named numpy.array
    def __init__(self, *names):
        self._lists = []
        for name in names:
            self.__setattr__(name,[])
            self._lists.append(self.__getattribute__(name))


    def extend(self, args):
        for l,arg in zip(self._lists, args):
            l.extend(arg)


    def append(self, args):
        for l,arg in zip(self._lists, args):
            l.append(arg)


    def pop(self, index):
        for l in self._lists:
            l.pop(index)


    def insert(self, index, args):
        for l,arg in zip(self._lists, args):
            l.insert(index, arg)


    def __setitem__(self, index, args):
        for l,arg in zip(self._lists, args):
            l[index] = arg


    def __getitem__(self, index):
        out = []
        for l in self._lists:
            out.append(l[index])
        return out


    def __len__(self):
        return len(self._lists[0])


    def __iter__(self):
        self._n = -1
        self._l = len(self._lists[0])-1
        return self


    def next(self):
        self._n+=1
        if self._n > self._l:
            raise StopIteration()
        return (x[self._n] for x in self._lists)



if __name__ == "__main__":
    import doctest
    doctest.testmod()