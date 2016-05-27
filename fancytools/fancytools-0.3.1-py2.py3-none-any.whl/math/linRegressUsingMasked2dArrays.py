import numpy as np
from scipy.stats import linregress



def linRegressUsingMasked2dArrays(xVals, arrays, badMask):
    '''
    if you have multiple 2d arrays each with position given by 
    xVals[array-index]
    and you want to do a linear regression on all cells
    but you also might mask different areas in each 2darray
    
    returns ascent, offset, RMS-error
    '''
    
    assert arrays.ndim == 3, 'need multiple 2d arrays'
    assert arrays.shape == badMask.shape, 'mask needs to have same shape'
    
    s = arrays.shape
    #flatten to create array of 1d arrays:
    y = arrays.reshape(s[0],s[1]*s[2]).astype(float)
    s = s[1:]
    #solve linear regression:
    A = np.vstack([xVals, np.ones(len(xVals))]).T
    solution = np.linalg.lstsq(A, y)[0]

    offset = solution[1].reshape(s)
    ascent = solution[0].reshape(s) 

    #do linear regression for all masked areas
    #trying to find multiple 2d arrays that are not masked together
    x,y = np.where(np.sum(badMask, axis=0))
    for xi,yi in zip(x,y):
        valid = ~badMask[:,xi,yi]
        asc, offs, _, _, _ = linregress(x[valid],arrays[valid,xi,yi])
        ascent[xi,yi]=asc
        offset[xi,yi]=offs

    #calculate RMSE of the regression:
    error = np.empty(shape=arrays.shape)
    for n, (y,x) in enumerate(zip(arrays,xVals)):
        error[n] = (y - (x*ascent + offset))**2    
    error = error.mean(axis=0)**0.5
    
    return ascent, offset, error

#TODO: test case