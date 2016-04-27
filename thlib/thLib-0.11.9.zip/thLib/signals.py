'''
Utilities for signal processing 
'''

'''
Author: Thomas Haslwanter
Version: 1.2
Date: Nov-2013
'''

import numpy as np
import matplotlib.pyplot as plt

import math 
from numpy import dot

def savgol(x, window_size=3, order=2, deriv=0, rate=1):
    '''
    Smooth (and optionally differentiate) data with a Savitzky-Golay filter.
    The Savitzky-Golay filter removes high frequency noise from data.
    It has the advantage of preserving the original shape and
    features of the signal better than other types of filtering
    approaches, such as moving averages techhniques.

    Parameters
    ----------
    y : array_like, shape (N,) or (N,m)
        the values of the time history of the signal.
    window_size : int
        the length of the window. Must be an odd integer number.
    order : int
        the order of the polynomial used in the filtering.
        Must be less then `window_size` - 1.
    deriv : int
        the order of the derivative to compute (default = 0 means only smoothing)
    rate : sampling rate (in Hz; only used for derivatives)

    Returns
    -------
    ys : ndarray, shape same as y
        the smoothed signal (or it's n-th derivative).

    Notes
    -----
    The Savitzky-Golay is a type of low-pass filter, particularly
    suited for smoothing noisy data. The main idea behind this
    approach is to make for each point a least-square fit with a
    polynomial of high order over a odd-sized window centered at
    the point.

    The data at the beginning / end of the sample are deterimined from
    the best polynomial fit to the first / last datapoints. This makes the code
    a bit more complicated, but avoids wild artefacts at the beginning and the
    end.

    **Cutoff-frequencies**
    For smoothing (deriv=0), the frequency where
    the amplitude is reduced by 10% is approximately given by:

    *f_cutoff = sampling_rate / (1.5 * look)*

    For the first derivative (deriv=1), the frequency where 
    the amplitude is reduced by 10% is approximately given by:

    *f_cutoff = sampling_rate / (4 * look)*

    Examples
    --------
    >>> t = np.linspace(-4, 4, 500)
    >>> y = np.exp( -t**2 ) + np.random.normal(0, 0.05, t.shape)
    >>> ysg = savgol(y, window_size=31, order=4)
    >>> import matplotlib.pyplot as plt
    >>> plt.plot(t, y, label='Noisy signal')
    >>> plt.plot(t, np.exp(-t**2), 'k', lw=1.5, label='Original signal')
    >>> plt.plot(t, ysg, 'r', label='Filtered signal')
    >>> plt.legend()
    >>> plt.show()

    References
    ----------
    .. [1] A. Savitzky, M. J. E. Golay, Smoothing and Differentiation of
       Data by Simplified Least Squares Procedures. Analytical
       Chemistry, 1964, 36 (8), pp 1627-1639.
    .. [2] Numerical Recipes 3rd Edition: The Art of Scientific Computing
       W.H. Press, S.A. Teukolsky, W.T. Vetterling, B.P. Flannery
       Cambridge University Press ISBN-13: 9780521880688
    .. [3] Siegmund Brandt, Datenanalyse, pp 435

    '''
        
    import warnings
    warnings.warn(
        'This function is deprecated! Please use "scipy.signal.savgol_filter" instead.',
        DeprecationWarning)
    
    # Check the input
    try:
        window_size = np.abs(np.int(window_size))
        order = np.abs(np.int(order))
    except ValueError:
        raise ValueError("window_size and order have to be of type int")
    if window_size > len(x):
        raise TypeError("Not enough data points!")
    if window_size % 2 != 1 or window_size < 1:
        raise TypeError("window_size size must be a positive odd number")
    if window_size < order + 1:
        raise TypeError("window_size is too small for the polynomials order")
    if order <= deriv:
        raise TypeError("The 'deriv' of the polynomial is too high.")


    # Calculate some required parameters
    order_range = range(order+1)
    half_window = (window_size -1) // 2
    num_data = len(x)
    
    # Construct Vandermonde matrix, its inverse, and the Savitzky-Golay coefficients   
    a = [[ii**jj for jj in order_range] for ii in range(-half_window, half_window+1)]
    pa = np.linalg.pinv(a)
    sg_coeff = pa[deriv] * rate**deriv * math.factorial(deriv)
      
    # Get the coefficients for the fits at the beginning and at the end of the data
    coefs = np.array(order_range)**np.sign(deriv)
    coef_mat = np.zeros((order+1, order+1))
    row = 0
    for ii in range(deriv,order+1):
        coef = coefs[ii]
        for jj in range(1,deriv):
            coef *= (coefs[ii]-jj)
        coef_mat[row,row+deriv]=coef
        row += 1
    coef_mat *= rate**deriv
    
    if len(x.shape)==1:
        flag_1d = True
        x = np.atleast_2d(x).T
    else:
        flag_1d = False
        
    y = np.nan * np.ones(x.shape)
    
    for ii in range(x.shape[1]):
        # Add the first and last point half_window times
        firstvals = np.ones(half_window) * x[0,ii] 
        lastvals  = np.ones(half_window) * x[-1,ii]
        x_calc = np.concatenate((firstvals, x[:,ii], lastvals))
    
        y_temp = np.convolve( sg_coeff[::-1], x_calc, mode='full')
        
        # chop away intermediate data
        y[:,ii]  = y_temp[window_size-1:window_size+num_data-1]
    
        # filtering for the first and last few datapoints
        y[0:half_window,ii] = dot(dot(dot(a[0:half_window], coef_mat), \
                                       np.mat(pa)), x[0:window_size,ii])
        y[len(y)-half_window:len(y),ii] = dot(dot(dot(a[half_window+1:window_size], \
                            coef_mat), pa), x[len(x)-window_size:len(x),ii])
    
    if flag_1d:
        y = y.flatten()
        
    return y

   
def pSpect(data, rate):
    '''
    Power spectrum and frequency

    Parameters
    ----------
    data : array, shape (N,)
        measurement data
    rate : float
        sampling rate [Hz]

    Returns
    -------
    powerspectrum : array, shape (N,)
    frequency : array, shape (N,)

    Example
    -------
    >>> pxx, freq = pSpect(data, 1000)

    '''

    from scipy.fftpack import fft
    nData = len(data)
    window = np.hamming(nData)
    fftData = fft(data*window)
    PowerSpect = fftData * fftData.conj() / nData
    freq = np.arange(nData) * float(rate) / nData
    return (PowerSpect, freq)

def show_se(raw):
    '''Show mean and standard error, of a dataset in column form.

    Parameters
    ----------
    raw : array (N,M)
        input data, M sets of N data points

    Returns
    -------
    avg : array (N,)
        average value
    se : array (N,)
        standard error

    Examples
    --------
    >>> t = np.arange(0,20,0.1)
    >>> x = np.sin(t)
    >>> data = []
    >>> for ii in range(10):
    >>>     data.append(x + np.random.randn(len(t)))
    >>> show_se(np.array(data).T)

    Notes
    -----
    .. image:: _static/show_se.png
        :scale: 50%

    '''

    N = len(raw)

    # Calculate mean and standard error
    avg = np.mean(raw, axis=1)
    std = np.std(raw, axis=1, ddof=1)
    se = std/np.sqrt(N)

    # Calculate upper and lower limit, for showing the standard error
    upper = avg + se
    lower = avg - se

    # Plot the data
    plt.fill_between(t, lower, upper, color='gray', alpha=0.5)
    plt.hold(True)
    plt.plot(t,avg)
    plt.show()

    return (avg, se)


def corrvis(x,y):
    '''
    Visualize correlation, by calculating the cross-correlation of two signals.
    The aligned signals and the resulting cross correlation value are shown,
    and advanced when the user hits a key or clicks with the mouse.

    Parameters
    ----------
    X : array (N,)
        Comparison signal

    Y : array (M,)
        Reference signal

    Examples
    --------
    >>> x = np.r_[0:2*pi:10j]
    >>> y = np.sin(x)
    >>> corrvis(y,y)

    Notes
    -----
    Based on an idea from dpwe@ee.columbia.edu

    '''

    Nx = x.size
    Ny = y.size
    Nr = Nx + Ny -1
    
    xmin = -(Nx - 1)
    xmax = Ny + Nx -1
    
    # First plot: Signal 1
    ax1 = plt.subplot(311)
    ax1.plot(range(Ny), y)
    ax = ax1.axis()
    ax1.axis([xmin, xmax, ax[2], ax[3]])
    ax1.grid(True)
    ax1.set_xticklabels(())
    ax1.set_ylabel('Y[n]')
    
    # Precalculate limits of correlation output
    axr = [xmin, xmax, np.correlate(x,y,'full').min(), np.correlate(x,y,'full').max()]
    
    # Make a version of y padded to the full extent of X's we'll shift
    padY = np.r_[np.zeros(Nx-1), y, np.zeros(Nx-1)]
    Npad = padY.size
    R = []

    # Generate the cross-correlation, step-by-step
    for p in range(Nr):
        
        # Figure aligned X
        ax2 = plt.subplot(312)
        ax2.hold(False)
        ax2.plot(np.arange(Nx)-Nx+p+1, x)
        ax = ax2.axis()
        ax2.axis([xmin, xmax, ax[2], ax[3]])
        ax2.grid(True)
        ax2.set_ylabel('X[n-l]')
        ax2.set_xticklabels(())
        
        # Calculate correlation
        # Pad an X to the appropriate place
        padX = np.r_[np.zeros(p), x, np.zeros(Npad-Nx-p)]
        R = np.r_[R, np.sum(padX * padY)]
        
        # Third plot: cross-correlation values
        ax3 = plt.subplot(313)
        ax3.hold(False)
        ax3.plot(np.arange(len(R))-(Nx-1), R, linewidth=2)
        ax3.axis(axr)
        ax3.grid(True)
        ax3.set_ylabel('Rxy[l]')
        
        # Update the plot
        plt.draw()
        plt.waitforbuttonpress()
        
    plt.show()

if __name__ == '__main__':
    t = np.arange(0,10,0.1)
    x = np.sin(t) + 0.2*np.random.randn(len(t))
    smoothed = savgol(x, 11)
    plt.plot(t, smoothed)
    plt.show()
    print('Done')
