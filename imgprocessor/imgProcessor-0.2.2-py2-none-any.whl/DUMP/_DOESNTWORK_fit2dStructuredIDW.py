from numba import jit


def fit2dStructuredIDW(arr, mask, kernel=15, power=2, fx=1, fy=1):
    '''
    replace all values in [arr] indicated by [mask]
    with the inverse distance weighted interpolation of all values within 
    px+-kernel
    [power] -> distance weighting factor: 1/distance**[power]

    '''

    dists = np.empty(shape=((2*kernel,2*kernel)))
    for xi in xrange(-kernel,kernel):
        for yi in xrange(-kernel,kernel):
            dist = ((fx*xi)**2+(fy*yi)**2)
            dists[xi+kernel,yi+kernel] = dist
            
    dists = dists.flatten()            
    weights = 1.0 / dists**(0.5*power)   
    
  
#     plt.imshow(weights.reshape(40,40))
#     plt.show()

    weightInd = np.argsort(weights)
    
    weights = weights[weightInd]    
    dists = dists[weightInd]
    ddists = np.diff(dists)  
    print ddists, dists
#     plt.plot(weightInd)#.reshape(40,40))
#     plt.show()

    weightInd = weightInd.reshape(2*kernel, 2*kernel)

    values = np.empty(len(weights))
    
    
    
    return  _calc(arr, mask, kernel, values, weights, 
                  weightInd, dists, ddists)


@jit(nopython=True)
def _calc(arr, mask, kernel, values, weights, weightInd, dists, ddists):
    gx = arr.shape[0]
    gy = arr.shape[0]


    l = len(weights)
    
    #FOR EVERY PIXEL
    for i in xrange(gx):
        for j in xrange(gy):
            
            if mask[i,j]:
                
                xmn = i-kernel
                if xmn < 0:
                    xmn = 0
                xmx = i+kernel
                if xmx > gx:
                    xmx = gx
                    
                ymn = j-kernel
                if ymn < 0:
                    ymn = 0
                ymx = j+kernel
                if ymx > gx:
                    ymx = gy

                
                #FOR EVERY NEIGHBOUR IN KERNEL 
            
                for xi in xrange(xmn,xmx):
                    for yi in xrange(ymn,ymx):
                        wi = weightInd[xi-i+kernel,yi-j+kernel]

                        if  (xi != i or yi != j) and not mask[xi,yi]:
                            values[wi] = arr[xi,yi]
                        else:
                            values[wi] = 123#np.nan

                sumGrad = 0 
                sumWeights = 0                           
                #from big to smaller distance
                v0 = values[0]
                lastc = 0
                lastd = dists[0]
                for c in xrange(1,l):
                    v1 = values[c]
                    if v1 != 123:
                        d = dists[c]
                        dd = d-lastd
                        if dd:
                            grad = (v1-v0)/dd
                            sumWeights += weights[c-1]
                            sumGrad += grad*weights[c-1]
                        
                        v0 = v1
                        lastc = c
                        lastd = d

                if sumWeights:
                    grad = sumGrad / sumWeights
                    arr[i,j] = 1#v1 *grad#*dists[lastc]             

    return arr



if __name__ == '__main__':
    import numpy as np
    import pylab as plt
    import sys

    shape = (100,100)



    arr = np.fromfunction(lambda x,y: (x-50)**2+1.5*(y-50)**2, shape)

    mask = arr > 2000

    arrin = arr.copy()
    arrin[mask] = np.nan

    arrout = fit2dStructuredIDW(arrin.copy(), mask)

    plt.figure('original')
    plt.imshow(arr)
    plt.colorbar()

    plt.figure('input')
    plt.imshow(arrin)
    plt.colorbar()

    plt.figure('fit')
    plt.imshow(arrout)
    plt.colorbar()

    plt.show()

    #mask containing valid cells: 
    mask = np.random.randint(100, size=shape)
    mask[mask<1]=False
    mask = mask.astype(bool)


    #substituting all cells with mask==True with interpolated value:
    arr1 = interpolate2dStructuredIDW(arr.copy(), mask, kernel=20,power=1)
    arr2 = interpolate2dStructuredIDW(arr.copy(), mask, kernel=20,power=2)
    arr3 = interpolate2dStructuredIDW(arr.copy(), mask, kernel=20,power=3)
    arr5 = interpolate2dStructuredIDW(arr.copy(), mask, kernel=20,power=5)
    
    
    
    if 'no_window' not in sys.argv:
        plt.figure('power=1')
        arr1[~mask] = np.nan
        plt.imshow(arr1)
        
        plt.figure('power=2')
        arr2[~mask] = np.nan
        
        plt.imshow(arr2)        
        plt.figure('power=3')
        arr3[~mask] = np.nan
        plt.imshow(arr3) 
               
        plt.figure('power=5')
        arr5[~mask] = np.nan
        plt.imshow(arr5)
        
        plt.show()
    