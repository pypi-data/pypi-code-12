from scipy import interpolate


def findXAt(xArr, yArr, yVal):
    '''
    return all x values where y would be equal to given yVal
    if arrays are spline interpolated
    '''
    f = interpolate.UnivariateSpline(xArr, yArr-yVal)
    return f.roots()[0]