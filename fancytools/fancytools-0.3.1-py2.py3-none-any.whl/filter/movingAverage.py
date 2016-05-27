import numpy as np

def movingAverage(x, N=3, mode='reflect'):
    '''
    moving average filter for 1d arrays
    supported modes for boundary handling: 'reflect' , 'constant'

    '''
    assert N>1
    x2 = np.empty(shape=x.shape[0]+N, dtype=x.dtype)
    
    start = N-2
    if N==2:
        start = 1
    end = N-start

    x2[start:-end]=x
    #boundaries
    if mode == 'reflect':
        x2[:start]= x[start-1::-1]
        x2[-end:]=  x[-1:-end-1:-1]
    elif mode == 'nearest':
        x2[:start]= x[0]
        x2[-end:]=  x[-1]    
    else:
        raise NotImplementedError("mode='%s' not supported" %mode)

    cumsum = np.cumsum(x2) 
    return  (cumsum[N:] - cumsum[:-N]) / N