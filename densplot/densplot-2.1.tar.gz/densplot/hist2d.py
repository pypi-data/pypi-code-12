import sys
import numpy as np
import warnings

from scipy.sparse import spdiags

kb = 6.022141*1.380650/(4.184*1000.0)

def smooth2a(arrayin, nr, nc):

    # Building matrices that will compute running sums.  The left-matrix, eL,
    # smooths along the rows.  The right-matrix, eR, smooths along the
    # columns.  You end up replacing element "i" by the mean of a (2*Nr+1)-by- 
    # (2*Nc+1) rectangle centered on element "i".


    row = arrayin.shape[0]
    col = arrayin.shape[1]

    el = spdiags(np.ones((2*nr+1, row)),range(-nr,nr+1), row, row).todense()
    er = spdiags(np.ones((2*nc+1, col)), range(-nc,nc+1), col, col).todense()

    # Setting all "nan" elements of "arrayin" to zero so that these will not
    # affect the summation.  (If this isn't done, any sum that includes a nan
    # will also become nan.)

    a = np.isnan(arrayin)
    arrayin[a] = 0.

    # For each element, we have to count how many non-nan elements went into
    # the sums.  This is so we can divide by that number to get a mean.  We use
    # the same matrices to do this (ie, "el" and "er").

    nrmlize = el.dot((~a).dot(er))
    nrmlize[a] = None

    # Actually taking the mean.

    arrayout = el.dot(arrayin.dot(er))
    arrayout = arrayout/nrmlize

    return arrayout


def make(x, y, nbinsx, nbinsy, weight=None, free_energy_plot=False, plot_style=None, temperature=300, nextrabins=5, upperbound=None, idx_smoothing=2):

    x = np.array(x)
    y = np.array(y)
    npoints = x.shape[0]

    if y.shape[0] != npoints:
        raise ValueError('Number of x coordinates and y coordinates are different')

    if weight is not None:
        weight = np.array(weight)
        sum_weights = np.sum(weight)
        if np.absolute(sum_weights-npoints) >= 1: 
            warnings.warn('probability is not conserved, sum of weights = %i / number of points = %i' %(sum_weights, npoints))
        if weight.shape[0] != npoints:
           raise ValueError('Number of weights provided are different from the number of points')

    nextrabinsx = nextrabins
    nextrabinsy = nextrabinsx

    if plot_style:
        plot_style = plot_style.lower()
    else:
        plot_style = 'contour'

    xmin = np.amin(x)
    xmax = np.amax(x)

    diffx = xmax - xmin
    dbinsx = diffx / nbinsx
    xmin = xmin - nextrabinsx*dbinsx
    xmax = xmax + nextrabinsx*dbinsx
    nbinsx = nbinsx + 2*nextrabinsx

    ymin = np.amin(y)
    ymax = np.amax(y)

    diffy = ymax - ymin
    dbinsy = diffy / nbinsy
    ymin = ymin - nextrabinsy*dbinsy
    ymax = ymax + nextrabinsy*dbinsy
    nbinsy = nbinsy + 2*nextrabinsy

    idxs_grid = [[[] for jdx in xrange(nbinsy)] for idx in xrange(nbinsx)]
    idxx = np.floor((x-xmin)/dbinsx).astype(int)
    idxy = np.floor((y-ymin)/dbinsy).astype(int)

    for num, [i, j] in enumerate(zip(idxx, idxy)):
        idxs_grid[i][j].append(num)

    grid = np.zeros((nbinsx, nbinsy))

    if weight is None:
        for idx, row in enumerate(idxs_grid):
            for jdx, col in enumerate(row):
                _npoints = len(col)
                if free_energy_plot is False:
                    grid[idx, jdx] = _npoints
                else:
                    if _npoints == 0:
                        grid[idx, jdx] = None
                    else:
                        grid[idx, jdx] = -kb * temperature*np.log(_npoints)
    else:
        for idx, row in enumerate(idxs_grid):
            for jdx, col in enumerate(row):
                _npoints = len(col)
                _weight = 0
                for grid_idx in col:
                    _weight += weight[grid_idx]
                if free_energy_plot is False:
                    grid[idx, jdx] = _weight
                else:
                    if _npoints == 0:
                        grid[idx, jdx] = None
                    else:
                        grid[idx, jdx] = -kb * temperature*np.log(_weight)



    if free_energy_plot is True:
        grid = grid - np.nanmin(grid)
        if plot_style == 'contour':
            if not upperbound:
                grid[np.isnan(grid)] = np.nanmax(grid) + 0.1
            else:
                grid[grid>upperbound] = upperbound + 0.1
                grid[np.isnan(grid)] = upperbound + 0.1

    #grid[np.isnan(grid)] = np.nanmax(grid) + 0.1
    grid = smooth2a(grid, idx_smoothing, idx_smoothing);
    grid = np.copy(grid) # without this line the contour plot (masked array) fails

    if free_energy_plot is True:
        grid = grid - np.nanmin(grid)

    if plot_style == 'contour':
        x_grid = np.linspace(xmin,xmax,nbinsx)[:, np.newaxis].dot(np.ones((1, nbinsy)))
        y_grid = np.ones((nbinsx,1)).dot(np.linspace(ymin,ymax,nbinsy)[np.newaxis])
        return x_grid, y_grid, grid
    elif plot_style == 'scatter':
        vector = np.empty(npoints)
        for idx, row in enumerate(idxs_grid):
            for jdx, col in enumerate(row):
                _weight = grid[idx, jdx]
                for grid_idx in col:
                    vector[grid_idx] = _weight
        return x, y, vector 
