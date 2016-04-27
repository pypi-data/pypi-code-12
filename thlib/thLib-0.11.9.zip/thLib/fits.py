''' Collection of fitting functions '''
"""

Author : Thomas Haslwanter
Date : Nov-2015
Version: 1.5
"""

# Standard packages
import numpy as np
import scipy as sp
import matplotlib.pyplot as plt
import pandas as pd
import os

# Special package
from collections import namedtuple
from statsmodels.formula.api import ols
try:
    from skimage import filters
except ImportError:     # for backwards capability to old installations
    from skimage import filter as filters
    
def demo_ransac():
    '''Find the best-fit circle in an image, using the RANSAC algorithm '''

    debug_flag = 1

    # Since this function is only used in demo_ransac, define it here
    def drawCircle(center,r):
        '''Draw a circle'''
        nPts = 100
        phi = np.linspace(0,2*np.pi,nPts)
        x = center[0] + r*np.cos(phi)
        y = center[1] + r*np.sin(phi)
        plt.hold(True)
        plt.plot(y,x,'r')

    # Get the data
    os.chdir(r'C:\Users\p20529\Coding\Matlab\imProc\ransac_fitCircle')
    data = plt.imread('0_5.bmp')
    
    # Eliminate edge artefacts
    rim = 20
    data = data[rim:-rim, rim:-rim]
    imSize = data.shape
    
    # Find edges
    edges = filters.sobel(data)
    edgePnts = edges>0.15
    np.sum(edgePnts)
    [x,y] = np.where(edgePnts==True)
       
    # set RANSAC parameters
    par={'eps': 3, 
         'ransac_threshold': 0.1, 
         'nIter': 500, 
         'lowerRadius': 5,
         'upperRadius': 200   
    }
    
    # Allocate memory, for center(2D), radius, numPoints (structured array)
    fitted = np.zeros(par['nIter'], \
    dtype={'names':['center', 'radius', 'nPts'], 'formats':['2f8', 'f8', 'i4']})
    
    for ii in range(par['nIter']):
        # Takes 3 random points, and find the corresponding circle
        randEdges = np.random.permutation(len(x))[:3]
        (center, radius) = fitCircle(x[randEdges], y[randEdges])
        
        # Eliminate very small and very large circles, and centers outside the image
        if not (par['lowerRadius'] < radius < par['upperRadius'] and \
                0 <= center[0] < imSize[0] and \
                0 <= center[1] < imSize[1]):
            continue

        # Make sure a reasonable number of points lies near that circle
        centerDistance = np.sqrt((x-center[0])**2 + (y-center[1])**2)
        inCircle = np.where(np.abs(centerDistance-radius)<par['eps'])[0]
        inPts = len(inCircle)
        if inPts < par['ransac_threshold'] *4*np.pi*radius*par['eps'] or inPts < 3:
            continue
        
        # Fit a circle to all good points, and save the corresponding parameters
        (center, radius) = fitCircle(x[inCircle], y[inCircle])        
        fitted[ii] = (center, radius, inPts)
    
        # If you want to see these points:
        if debug_flag == 1:
            plt.plot(y,x,'.')
            plt.hold(True)
            plt.plot(y[inCircle], x[inCircle],'r.')
            plt.plot(y[randEdges], x[randEdges], 'g+', ms=15)
            plt.axis('equal')
            plt.show()
        
    # Sort the circles, according to number of points included
    fitted = np.sort(fitted,order='nPts')
        
    # Show the best-fitting circle
    plt.imshow(data, cmap='gray', origin='lower')
    drawCircle(fitted[-1]['center'], fitted[-1]['radius'])
    plt.show()
    
def fit_circle(x,y):
    '''
    Determine the best-fit circle to given datapoints.
    
    Parameters
    ----------
    x : array (N,)
        x-values.
    y : array (N,)
        corresponding y-values.

    Returns
    -------
    center : array (2,)
        x/y coordinates of center of the circle
    radius : float
        Circle radius.

    Examples
    --------
    >>> r = 2
    >>> center = np.r_[5,5]
    >>> theta = np.r_[0:2*np.pi:10j]
    >>> x = r*np.cos(theta)+center[0]
    >>> y = r*np.sin(theta)+center[1]
    >>> cFit,rFit = thLib.fits.fit_circle(x,y)
    
    '''
    M = np.vstack((2*x,2*y,np.ones(len(x)))).T
    (par,_,_,_) = np.linalg.lstsq(M,x**2+y**2)
    center = par[:2]
    radius = np.sqrt(par[2]+np.sum(center**2))
    return(center, radius)


def fit_exp(tFit, yFit, plotFlag=False): 
    '''
    Calculates best-fit parameters for the exponential decay to an offset.
    This can serve as an example for a general non-linear fit.

    Parameters
    ----------
    tFit : array (N,)
        Time values.
    yFit : array (N,)
        Function values

    Returns
    -------
    offset : float
        Function offset/bias.
    amp : float
        Amplitude of exponential function
    tau : float
        Decay time.

    Examples
    --------
    
    >>> t = np.arange(10)
    >>> tau = 2.
    >>> amp = 1.
    >>> offset = 2.
    >>> x = offset + amp*np.exp(-t/tau)    
    >>> fitted =  thLib.fits.fit_exp(t,x)

    ''' 

    from scipy import optimize 
     
    # Define the fit-function and the error-function 
    fitfunc = lambda p, x: p[0] + p[1]*np.exp(-x/p[2]) 
    errfunc  = lambda p,x,y: fitfunc(p,x) - y 
     
    pInit = np.r_[0, 1, 1]  # Initial values 
     
    # Make the fit 
    pFit, success = optimize.leastsq(errfunc, pInit, args=(tFit, yFit)) 
     
    if plotFlag:
        # Plot the data and the fit 
        plt.plot(tFit, yFit, label='rawdata')
        plt.hold(True)
        plt.plot(tFit, fitfunc(pFit,tFit), label='fit') 
        plt.legend()
        plt.show() 

    ExpFit = namedtuple('ExpFit', ['offset', 'amplitude', 'tau'])
    return ExpFit(*pFit)

def fit_line(x, y, alpha=0.05, newx=[], plotFlag=False):
    """
    Linear regression fit.

    Parameters
    ----------
    x : ndarray
        Input / Predictor.
    y : ndarray
        Input / Estimator.
    alpha : float
        Confidence limit [default=0.05]
    newx : float or ndarray
        Values for which the fit and the prediction limits are calculated (optional)
    plotFlag: int, optional
        1 = plot, 0 = no_plot [default]
        
    Returns
    -------
    a : float
        Intercept
    b : float
        Slope
    ci : ndarray
        Lower and upper confidence interval for the slope
    info : dictionary
        contains return information on
        - residuals
        - var_res
        - sd_res
        - alpha
        - tval
        - df
    newy : list(ndarray)
        Predictions for (newx, newx-ciPrediction, newx+ciPrediction)

    Examples
    --------
    >>> x = np.r_[0:10:11j]
    >>> y = x**2
    >>> (a,b,(ci_a, ci_b),_) = thLib.fits.fit_line(x,y)    
    Summary: a=-15.0000+/-12.4590, b=10.0000+/-2.1060
    Confidence intervals: ci_a=(-27.4590 - -2.5410), ci_b=(7.8940 - 12.1060)
    Residuals: variance = 95.3333, standard deviation = 9.7639
    alpha = 0.050, tval = 2.2622, df=9


    Notes
    -----
    Example data and formulas are taken from
    D. Altman, "Practical Statistics for Medicine"
    """
    
    # Summary data
    n = len(x)			   # number of samples     
    
    Sxx = np.sum(x**2) - np.sum(x)**2./n
#    Syy = np.sum(y**2) - np.sum(y)**2./n    # not needed here
    Sxy = np.sum(x*y) - np.sum(x)*np.sum(y)/np.float(n)
    mean_x = np.mean(x)
    mean_y = np.mean(y)
    
    # Linefit
    b = Sxy/Sxx
    a = mean_y - b*mean_x
    
    # Residuals
    fit = lambda xx: a + b*xx    
    residuals = y - fit(x)
    
    var_res = np.sum(residuals**2)/np.float((n-2))
    sd_res = np.sqrt(var_res)
    
    # Confidence intervals
    se_b = sd_res/np.sqrt(Sxx)
    se_a = sd_res*np.sqrt(np.sum(x**2)/np.float(n*Sxx))
    
    df = n-2                            # degrees of freedom
    tval = sp.stats.t.isf(alpha/2., df) 	# appropriate t value
    
    ci_a = a + tval*se_a*np.array([-1,1])
    ci_b = b + tval*se_b*np.array([-1,1])

    # create series of new test x-values to predict for
    npts = 100
    px = np.linspace(np.min(x),np.max(x),num=npts)
    
    se_fit     = lambda x: sd_res * np.sqrt(  1./n + (x-mean_x)**2./Sxx)
    se_predict = lambda x: sd_res * np.sqrt(1+1./n + (x-mean_x)**2./Sxx)
    
    print('Summary: a={0:5.4f}+/-{1:5.4f}, b={2:5.4f}+/-{3:5.4f}'.format(a,tval*se_a,b,tval*se_b))
    print('Confidence intervals: ci_a=({0:5.4f} - {1:5.4f}), ci_b=({2:5.4f} - {3:5.4f})'.format(ci_a[0], ci_a[1], ci_b[0], ci_b[1]))
    print('Residuals: variance = {0:5.4f}, standard deviation = {1:5.4f}'.format(var_res, sd_res))
    print('alpha = {0:.3f}, tval = {1:5.4f}, df={2:d}'.format(alpha, tval, df))
    
    # Return info
    ri = {'residuals': residuals, 
        'var_res': var_res,
        'sd_res': sd_res,
        'alpha': alpha,
        'tval': tval,
        'df': df}
    
    if plotFlag:
        # Plot the data
        plt.figure()
        
        plt.plot(px, fit(px),'k', label='Regression line')
        #plt.plot(x,y,'k.', label='Sample observations', ms=10)
        plt.plot(x,y,'k.')
        
        x.sort()
        limit = (1-alpha)*100
        plt.plot(x, fit(x)+tval*se_fit(x), 'r--', lw=2, label='Confidence limit ({0:.1f}%)'.format(limit))
        plt.plot(x, fit(x)-tval*se_fit(x), 'r--', lw=2 )
        
        plt.plot(x, fit(x)+tval*se_predict(x), '--', lw=2, color=(0.2,1,0.2), label='Prediction limit ({0:.1f}%)'.format(limit))
        plt.plot(x, fit(x)-tval*se_predict(x), '--', lw=2, color=(0.2,1,0.2))

        plt.xlabel('X values')
        plt.ylabel('Y values')
        plt.title('Linear regression and confidence limits')
        
        # configure legend
        plt.legend(loc=0)
        leg = plt.gca().get_legend()
        ltext = leg.get_texts()
        plt.setp(ltext, fontsize=10)

        # show the plot
        plt.show()
     
    if newx != []:
        try:
            newx.size
        except AttributeError:
            newx = np.array([newx])
    
        print('Example: x = {0}+/-{1} => se_fit = {2:5.4f}, se_predict = {3:6.5f}'\
        .format(newx[0], tval*se_predict(newx[0]), se_fit(newx[0]), se_predict(newx[0])))
        
        newy = (fit(newx), fit(newx)-se_predict(newx), fit(newx)+se_predict(newx))
        
        LineFit = namedtuple('LineFit',['intercept', 'slope', 'CIs', 'info', 'yFitted'])
        return LineFit(a,b,(ci_a, ci_b), ri, newy)
    else:
        LineFit = namedtuple('LineFit',['intercept', 'slope', 'CIs', 'info'])
        return LineFit(a,b,(ci_a, ci_b), ri)

 
def fit_sin(tList, yList, freq):
    '''
    Fit a sine wave with a known frequency to a given set of data.
   
    y = amplitude * sin(2*pi*freq * tList + phase*pi/180) + bias
   
    Parameters
    ----------
    yList : array
           datapoints
    tList : float
           time base, in sec
    freq : float
          in Hz
       
    Returns
    -------
    phase : float
        in degrees
    amplitude : float
    bias : float
   
    Examples
    --------
    >>> np.random.seed(1234)
    >>> t = np.arange(0,10,0.1)
    >>> x = 3 + 4*np.sin(2*np.pi*t + 5*np.pi/180) + np.random.randn(len(t))
    >>> (phase, amp, offset) = thLib.fits.fit_sin(t, x, 1)
    
    '''

    # Get input data
    b = yList
    rows = [ [np.sin(freq*2*np.pi*t), np.cos(freq*2*np.pi*t), 1] for t in tList]
    A = np.array(rows)
    
    # Make the fit
    (w,residuals,rank,sing_vals) = np.linalg.lstsq(A,b)
    
    # Extract desired parameters ...
    phase = np.arctan2(w[1],w[0])*180/np.pi
    amplitude = np.linalg.norm([w[0],w[1]],2)
    bias = w[2]
    
    # ... and return them
    SinFit = namedtuple('SinFit', ['phase', 'amp', 'offset'])
    return SinFit(phase,amplitude,bias)
 
def fit_ellipse(x,y):
    '''
    Ellipse fit by Taubin's Method
    
    Parameters
    ----------
    x : array
        x-coordinates of the ellipse points
    y : array
        y-coordinates of the ellipse points
        
    Returns
    -------
    A : array
        Ellipse parameters
        A = [a b c d e f]
        is the vector of algebraic parameters of thefitting ellipse:
        ax^2 + bxy + cy^2 +dx + ey + f = 0
        The vector A is normed, so that ||A||=1.
    
    Notes
    -----
    Among fast non-iterative ellipse fitting methods, 
    this is perhaps the most accurate and robust.
    
    This method fits a quadratic curve (conic) to a set of points;
    if points are better approximated by a hyperbola, this fit will 
    return a hyperbola. To fit ellipses only, use "Direct Ellipse Fit".
    
    Published in
    G. Taubin, "Estimation Of Planar Curves, Surfaces And Nonplanar
    Space Curves Defined By Implicit Equations, With 
    Applications To Edge And Range Image Segmentation",
    IEEE Trans. PAMI, Vol. 13, pages 1115-1138, (1991)
    
    '''

    centroid = np.mean( np.vstack((x,y)), 1 )   # the centroid of the data set
    
    Z = np.vstack(( (x-centroid[0])**2,
                    (x-centroid[0])*(y-centroid[1]),
                    (y-centroid[1])**2,
                     x-centroid[0],
                     y-centroid[1],
                    np.ones(len(x)) )).T;

    M = Z.T.dot(Z) / len(x)
    
    P = np.array(
         [[ M[0,0]-M[0,5]**2, M[0,1]-M[0,5]*M[1,5], M[0,2]-M[0,5]*M[2,5], M[0,3], M[0,4] ],
          [ M[0,1]-M[0,5]*M[1,5], M[1,1]-M[1,5]**2, M[1,2]-M[1,5]*M[2,5], M[1,3], M[1,4] ],
          [ M[0,2]-M[0,5]*M[2,5], M[1,2]-M[1,5]*M[2,5], M[2,2]-M[2,5]**2, M[2,3], M[2,4] ],
          [ M[0,3], M[1,3], M[2,3], M[3,3], M[3,4] ],
          [ M[0,4], M[1,4], M[2,4], M[3,4], M[4,4] ]])
    
    Q = np.array(
         [[ 4*M[0,5], 2*M[1,5], 0, 0, 0],
          [ 2*M[1,5], M[0,5]+M[2,5], 2*M[1,5], 0, 0],
          [ 0, 2*M[1,5], 4*M[2,5], 0, 0],
          [ 0, 0, 0, 1, 0],
          [ 0, 0, 0, 0, 1]])
    
    w, vr = sp.linalg.eig(P,Q)
    sortID = np.argsort(w)
    
    A = vr[:,sortID[0]]
    A = np.hstack( (A, -A[:3].T.dot(M[:3,5])) )
    A4 = A[3] - 2*A[0]*centroid[0] - A[1]*centroid[1]
    A5 = A[4] - 2*A[2]*centroid[1] - A[1]*centroid[0]
    A6 = A[5] + A[0]*centroid[0]**2 +A[2]*centroid[1]**2+ \
         A[1]*centroid[0]*centroid[1] - A[3]*centroid[0]-A[4]*centroid[1]
    A[3] = A4
    A[4] = A5
    A[5] = A6

    A = A/np.linalg.norm(A);
    return A

def regress(y, X, alpha=0.05, intercept=True):
    '''
    Multilinear regression and confidence intervals.
    Note that by default, an intercept is added to the design matrix!

    Parameters
    ----------
    X : ndarray (N,) or (N,p)
        predictors at each of N observations
    y : ndarray(N,)
        observed responses
    alpha : float, optional
        Defines the 100*(1-alpha)% confidence level in ci.
        Default alpha=0.05
    intercept : boolean
        If 'True', an intercept is automatically added to the design matrix.
        If 'False', the behavior is like the Matlab "regress" function, and
        no intercept is added.

    Returns
    -------
    fit : float
        best fit intercept and regression parameters
    ci : ndarray (2,)
        confidence intervals for the coefficient estimates
        at the given alpha level (default: 95%-level)

    Examples
    --------
    >>> x = np.array([0, 0, 10, 10])
    >>> y = np.array([1, 3, 11, 13])
    >>> (fit,ci) = thLib.fits.regress(y,x)    

    >>> X = np.random.randn(10,2)
    >>> mat = np.hstack( (np.ones( (len(X),1) ), X) )
    >>> pars = np.c_[[2, 4, 5]]
    >>> y = mat.dot(pars)
    >>> y += 0.1*np.random.randn(*y.shape)
    >>> (fit,ci) = thLib.fits.regress(y, mat)    

    See also
    --------
    fit_line

    '''

        
    if X.ndim == 1:
        dof = len(X)-2
        df = pd.DataFrame({'x':X, 'y':y})
        modelTxt = 'y~x'
        
        # If you want the Matlab "regress", without intercept
        if intercept == False:
            modelTxt += '-1'
            dof += 1
            
        # Fit the model
        model = ols(modelTxt,df).fit()
        ci = np.zeros((2, 2))
    else:
        # Make sure the dimensions are right
        if X.shape[0] < X.shape[1]:
            X = X.T
            
        dof = X.shape[0]-X.shape[1]-1
        if y.ndim == 1:
            y = np.c_[y]
        # For automatic labeling, put all the data into one matrix
        data = np.hstack((y,X))
        
        df = pd.DataFrame(data)
        # Make a string like 'y~x1+x2+x3'
        labels = ['y']
        modelTxt = 'y~'
        for ii in range(X.shape[1]):
            labels.append('x'+str(ii))
            modelTxt += labels[-1]+'+'
            
        # Remove the last "+"
        modelTxt = modelTxt[:-1]
        
        # Automatic column labelling
        df.columns = labels
        
        # Memory allocation for CIs
        if intercept == True:
            ci = np.zeros((1+X.shape[1],2))
        # If you want the Matlab "regress", without intercept
        else:
            dof +=1
            modelTxt += '-1'
            ci = np.zeros((X.shape[1],2))
            
        # Fit the model
        model = ols(modelTxt,df).fit()
        
    level = (1.-alpha/2.)
    # Make sure that you have the correct DOF
    tVal = sp.stats.t.ppf(level,dof)
    
    # Extract parameters and standard error from the model
    fit = model.params
    se = model.bse
    
    # Calculate CIs
    ci[:,0] = fit - se*tVal
    ci[:,1] = fit + se*tVal
    
    # Return a named tuple
    Regression= namedtuple('Regression', ['Fit', 'CIs'])
    
    return Regression(fit, ci)
    
if __name__=='__main__':

    # Produce an ellipse
    a = 5
    b = 3
    alpha = np.deg2rad(30) 
    R = np.array([[np.cos(alpha), -np.sin(alpha)],
                   [np.sin(alpha), np.cos(alpha)]])
    
    theta = np.linspace(0, 2*np.pi, 100)
    x = a * np.cos(theta)
    y = b * np.sin(theta)    
    XY = np.vstack( (x,y) )
    ellipse = R.dot( XY )    
    
    plt.plot(ellipse[0,:], ellipse[1,:])    
    plt.show()

    A = fit_ellipse(ellipse[0,:], ellipse[1,:])
    print('The ellipse-fit parameters are:')
    print(A)
    
    # Check (equations from http://mathworld.wolfram.com/Ellipse.html)
    (a,b,c,d,e,f) = A
    
    # To match the formula from wolfram
    b /= 2
    d /= 2
    g = f
    f = e/2
    
    aFit = np.sqrt(2*(a*f**2 + c*d**2 + g*b**2 - 2*b*d*f - a*c*g)/((b**2-a*c)* (np.sqrt((a-c)**2 + 4*b**2) -(a+c))))
    
    bFit = np.sqrt(2*(a*f**2 + c*d**2 + g*b**2 - 2*b*d*f - a*c*g)/((b**2-a*c)*(-np.sqrt((a-c)**2 + 4*b**2) - (a+c))))
    
    thetaFit = np.pi/2 + 0.5*np.arctan2(2*b, a-c)
    print('a={0:3.2f}, b={1:3.2f}, theta = {2}'.format(aFit, bFit, np.rad2deg(thetaFit)))
    
    
    
    
    '''
    # Test fit_exp
    t = np.arange(10)
    tau = 2.
    amp = 1.
    offset = 2.
    x = offset + amp*np.exp(-t/float(tau))    
    print(fit_exp(t,x))
    
    import doctest
    doctest.testmod()    # Test fit_line
        
    print('Fit line ------------')
    x = np.array([0, 0, 10, 10])
    y = np.array([1, 3, 11, 13])
    out = fit_line(x,y)
    print(out)
    
    # Test regress - 1dim
    print('Plain -----------------')
    x = np.array([0, 0, 10, 10])
    y = np.array([1, 3, 11, 13])
    (fit,ci) = regress(y,x)    
    print(fit)
    print(ci)

    print('99% -----------------')
    (fit,ci) = regress(y,x, alpha=0.01)    
    print(fit)
    print(ci)
    
    print('No intercept -------')
    (fit,ci) = regress(y,x, intercept=False)    
    print(fit)
    print(ci)
    
    # Test regress - 2dim
    print('2-dim -----------')
    X = np.array([[1,1,1,1],[0,0,10,10]]).T
    y = np.array([1, 3, 11, 13])
    (fit,ci) = regress(y, X, intercept=False)    
    print(fit)
    print(ci)

    # Test regress - 2dim
    X = np.random.randn(10,2)
    mat = np.hstack( (np.ones( (len(X),1) ), X) )
    pars = np.c_[[2, 4, 5]]
    y = mat.dot(pars)
    y += 0.1*np.random.randn(*y.shape)
    (fit,ci) = regress(y, mat)    
    print(fit)     
    print(ci)
    '''
