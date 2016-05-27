from scipy.stats import linregress


def linregressIgnoringOutliers(x, y, n_iter=3, nstd=2):
    '''
    do linear regression [n_iter] times
    successive removing [outliers]
    return result of normal linregress
    '''
    for _ in range(n_iter):
        m, n = linregress(x, y)[:2]
        y_fit = x*m+n
        dy = y-y_fit
        std = (dy**2).mean()**0.5
        inliers = abs(dy) < nstd*std
        if inliers.sum() > 2:
            x = x[inliers]
            y = y[inliers]
        else:
            break
    return linregress(x, y)



if __name__ == '__main__':
    import numpy as np
    import pylab as plt
    import sys

    x = np.arange(100)
    y = np.linspace(0, 10, 100)

    # add noise:
    y += np.random.rand(100)*3

    # add some outliers:
    pos = np.random.randint(0, 10, 100) > 4
    vals = np.random.rand(pos.sum())*20
    y[pos] = vals

    # ACTION
    m, n = linregress(x, y)[:2]
    y_fit1 = m*x+n

    m, n = linregressIgnoringOutliers(x, y)[:2]
    y_fit2 = m*x+n

    if 'no_window' not in sys.argv:
        # PLOT
        plt.plot(x, y, label='values')
        plt.plot(x, y_fit1, label='normal fit')
        plt.plot(x, y_fit2, label='fit ignoring outliers')
        plt.legend()
        plt.show()
