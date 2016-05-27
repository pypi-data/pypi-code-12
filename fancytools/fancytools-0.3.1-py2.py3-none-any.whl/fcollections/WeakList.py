
from weakref import ref

class WeakList(list):
    '''
    a list that removes its entries, if they are originally removed
    
    >>> import numpy as np
    >>> arr = np.ones(100)    
    >>> l = WeakList([arr,arr])
    >>> l.append(arr)
    >>> assert len(l) == 3
    >>> l[0] is arr
    True
    >>> arr in l
    True
    >>> del arr
    >>> assert len(l) == 0
    '''
    def __init__(self, l=()):
        list.__init__(self, l)
        for n in xrange(len(self)):
            obj = list.__getitem__(self, n)
            list.__setitem__(self, n, ref(obj, self.remove))


    def append(self, obj):
        list.append(self, ref(obj, self.remove))


    def insert(self, ind, obj):
        list.insert(self, ind, ref(obj, self.remove))
  
  
    def __iter__(self):
        for ref in list.__iter__(self):
            yield ref()
        
    def __getitem__(self, ind):
        ref = list.__getitem__(self,ind)
        return ref()
       
        
    def __setitem__(self, ind, item):
        ref = list.__setitem__(self, ind, ref(item,self.remove))
        return ref()        


    def __contains__(self, item):
        for i in self:
            if i is item:
                return True
        return False



if __name__ == "__main__":
    import doctest
    doctest.testmod()
    