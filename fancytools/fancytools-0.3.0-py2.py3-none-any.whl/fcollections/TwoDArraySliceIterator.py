
class TwoDArraySliceIterator(object):
    '''
    a simple iterator that build small slices from a big array


    >>> import numpy as np
    
    >>> arr = np.random.rand(100,100)
    >>> n_pieces = (2,4)
    >>> i = TwoDArraySliceIterator( arr.shape, n_pieces )
    
    than iterate through your array as follows:
    
    for  s1,s2 in i:
        print s1,s2, arr[s1,s2]
        ...
    '''
    def __init__(self, main_size, slice_size):
        self.main_size = main_size
        self.fx = main_size[0] / slice_size[0]
        self.fy = main_size[1] / slice_size[1]
        self.slice_size = slice_size
 
        if slice_size in ( None, (1,1) ):
            self.next = self._none
     
    def _none(self):
        if self._stop_next:
            raise StopIteration()
        self._stop_next = True
        return None, None, None, None
 
    def __iter__(self):
        self._reset()
        return self
 
    def _reset(self):
        self._stop_next = False
        self.i = 0
        self.j = 0
         
                 
    def next(self): 
        if self._stop_next:
            raise StopIteration()                     
        p0x = self.i*self.fx
        p0y = self.j*self.fy
        if self.i+1 == self.slice_size[0]:#at border
            p1x = self.main_size[0]
        else:
            p1x = (self.i+1)*self.fx
        if self.j+1 == self.slice_size[1]:#at border
            p1y = self.main_size[1]
        else:
            p1y = (self.j+1)*self.fy 
        self.i += 1
        if self.i == self.slice_size[0]:
            self.i = 0
            self.j += 1
            if self.j == self.slice_size[1]:
                self._reset()
                self._stop_next = True
        return slice(p0x, p1x), slice(p0y, p1y)


if __name__ == '__main__':
    import doctest
    doctest.testmod()