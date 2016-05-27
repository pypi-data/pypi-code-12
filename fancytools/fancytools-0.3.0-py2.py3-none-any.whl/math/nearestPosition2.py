# -*- coding: utf-8 -*-


class NearestPosition2(object):
    '''
    return the index of that value that is most similar in the array
    starting from the last known position, checking the right direction
    
    * assumes that new values to sort are close the the old ones
    * for this case and in case the array is sorted this approach is much faster
      than the normal nearestPosition

    >>> import numpy
    >>> a = numpy.array([1,3,7,12,15,20,33])
    >>> n = NearestPosition2(a)
    >>> n(5)
    2
    >>> n(22)
    5
    >>> n(24)
    5
    '''

    def __init__(self, array, lastPos=0):
        self.array = array
        self.lastPos = lastPos
    
 
    def __call__(self, value):
        #get initial direction
        d1 = abs(value - self.array[self.lastPos])
        if self.lastPos == 0:
            p = 1 #increase
        elif self.lastPos == self.array.size-1:
            p = -1 #decrease
        else: #check direction
            d0 = abs(value - self.array[self.lastPos-1])
            d2 = abs(value - self.array[self.lastPos+1])
            if d0 >= d1 <= d2:
                return self.lastPos # new pos is last position
            elif d0 < d1:
                    p = -1 #decrease
                    self.lastPos -= 1
                    d1 = d0
            else:
                p = 1 #increase
                self.lastPos += 1
                d1 = d2
        while True:
            self.lastPos += p
            if self.lastPos < 0:
                self.lastPos = 0
                return 0
            try:
                d2 = abs(value - self.array[self.lastPos])
                if d2 > d1:
                    self.lastPos-=p
                    return self.lastPos #- p
            except IndexError:# hit the border
                self.lastPos = len(self.array)-1
                return self.lastPos#self.lastPos - p
            d1 = d2



if __name__ == "__main__":
    import doctest
    doctest.testmod()