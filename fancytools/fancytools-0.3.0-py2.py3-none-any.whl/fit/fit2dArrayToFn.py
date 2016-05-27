from scipy.optimize.minpack import curve_fit
from scipy.ndimage.interpolation import zoom
import numpy as np



def fit2dArrayToFn(arr, fn, mask=None, down_scale_factor=1,
                   output_shape=None, guess=None):
    '''Fit a 2d array to a 2d function

    *Ignore masked values
    * [down_scale_factor] map to speed up fitting procedure
    * [output_shape] shape of the output array
    * [guess] must be scaled using [scale_factor]

    Returns:
        Fitted map, fitting params (scaled), error
    '''
    if mask is None:
        mask = np.ones(shape=arr.shape, dtype=bool)

    if down_scale_factor != 1:
        # SCALE TO DECREASE AMOUNT OF POINTS TO FIT:
        arr2 = zoom(arr, down_scale_factor)
        mask = zoom(mask, down_scale_factor, output=bool)
    else:
        arr2 = arr
    # USE ONLY VALID POINTS:
    x, y = np.where(mask)
    z = arr2[mask]
    # FIT:
    parameters, cov_matrix = curve_fit(fn, (x, y), z, p0=guess)
    # ERROR:
    perr = np.sqrt(np.diag(cov_matrix))

    if output_shape is None:
        output_shape = arr.shape

    fx = float(arr2.shape[0]) / output_shape[0]
    fy = float(arr2.shape[1]) / output_shape[1]

    rebuilt = np.fromfunction(lambda x, y: fn((x*fx, y*fy),
                                              *parameters), output_shape )

    return rebuilt, parameters, perr


if __name__ == '__main__':
    import sys
    import pylab as plt
    a, b = 10, 5
    f = 0.3  # down scale factor

    shape = (100, 200)
    guess = (a*f, b*f)


    def fn((x, y), a, b):
        return np.sin(x/a)+np.cos(y/b)

    fn2 = lambda x,y: fn((x, y),a, b)

    # build noisy image:
    img = np.fromfunction(fn2, shape)
    img += np.random.rand(*shape)

    # fit equation using noise image:
    fit, parameters, perr = fit2dArrayToFn(img, fn, guess=guess, down_scale_factor=f)

    if 'no_window' not in sys.argv:
        plt.figure('original')
        plt.imshow(img)

        plt.figure('fit')
        plt.imshow(fit)

        plt.show()
