import numpy as np


def polyFitIgnoringOutliers(x, y, deg=2, niter=3, nstd=2):
    '''Returns:
        (np.poly1d): callable function of polynomal fit excluding all outliers
    Args:
        deg (int): degree of polynomal fit
        n_iter (int): do linear regression n times
                      successive removing
        nstd (float): exclude outlioers, if their deviation
            is > [nstd] * standard deviation
    '''
    for i in range(niter):
        poly = np.polyfit(x, y, deg)
        p = np.poly1d(poly)
        if i == niter - 1:
            break
        y_fit = p(x)
        dy = y-y_fit
        std = (dy**2).mean()**0.5
        inliers = abs(dy) < nstd*std
        if inliers.sum() > 2:
            x = x[inliers]
            y = y[inliers]
        else:
            break
    return p



if __name__ == '__main__':
    import pylab as plt
    import sys

    x = np.arange(100)
    y = x**2.0

    # add noise:
    y += np.random.rand(100) * 3

    # add some outliers:
    pos = np.random.randint(0, 10, 100) > 4
    vals = np.random.rand(pos.sum())*2000
    y[pos] = vals

    x2 = x[::3]
    y2 = y[::3]

    # ACTION
    p = polyFitIgnoringOutliers(x2, y2)
    y_fit = p(x)

    if 'no_window' not in sys.argv:
        plt.plot(x2, y2, label='values')
        plt.plot(x, y_fit, label='fit ignoring outliers')
        plt.legend()
        plt.show()
