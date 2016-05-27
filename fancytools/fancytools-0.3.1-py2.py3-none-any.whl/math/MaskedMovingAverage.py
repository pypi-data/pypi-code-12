import numpy as np

class MaskedMovingAverage(object):
    '''
    Calculating the moving average and variance on (optional masked) ndArray
    allowing to update different areas every time
    
    moving average and variance
    taken from http://stackoverflow.com/a/14638138
    referring to http://www.johndcook.com/blog/standard_deviation/
    '''
    def __init__(self, shape, calcVariance=False, dtype=np.float64):
        #number of added array layers:
        self.n = np.zeros(shape=shape, dtype=int)
        #reference array containing x0 or first values 
        #average
        self.avg = np.zeros(shape=shape, dtype=dtype)
        self.var = None
        if calcVariance:
            #variance
            self.var = np.zeros(shape=shape, dtype=dtype)


    def update(self, arr, mask=None):
        '''
        update moving average (and variance) with new ndarray 
        (of the same shape as the init array) and an optional mask 
        '''
        if mask is not None:
            refI = np.logical_and(mask,self.n==0)
        else:
            refI = self.n==0
        if refI.any():
            #fill areas of the reference array that where empty before
            #create initial average value:
            self.avg[refI] = arr[refI]
        #the density of the marked array increases by one:
        self.n[mask] += 1
        #only consider filled areas:
        if mask is not None:
            i = mask#np.logical_and(mask,self.n>0)
        else:
            i = self.n>0
        #current value:
        xn = arr[i]
        #initial value:
        x0 = self.avg[i]
        n = self.n[i]
        #calculate the new average:
        new_Avg = self.avg[i] + (xn-x0)/n

        if self.var is not None:
            t = (xn-new_Avg + x0-self.avg[i])*(xn - x0)/(n-1)
            t = np.nan_to_num(t)
            self.var[i] += t
            
        #assign the new average now to remain the old average 
        #for calculating variance above:
        self.avg[i] = new_Avg



if __name__ == '__main__':
    import sys
    from matplotlib import pyplot as plt

    m = MaskedMovingAverage(shape=(30,30))
    arr = np.ones(shape=(30,30))
    ma = np.zeros((30,30), dtype=bool)
    
    ma[:15,:]=1
    arr*=2
    
    m.update(arr, ma)
    print m.avg
    ma[:15,:]=0
    ma[:,:15]=1
    arr*=2
    m.update(arr, ma)
    
    m.update(arr*2, ma)
    print m.avg
    m.update(arr*3, ma)
    print m.avg
    m.update(arr*3, ma)
    print m.avg

    if 'no_window' not in sys.argv:
        plt.imshow(m.avg, interpolation='none')
        plt.show()
 
    