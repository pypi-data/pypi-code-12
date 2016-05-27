import numpy as np
from numpy import isnan

# OWN
import _sortMethods
import _mergeMethods  # used for self.mergeMethod



class GridRender(object):
    """Discretize multi-dimensional continous data in a np.array
    """

    def __init__(self,
                 dtype=np.float64, antialiasing=False,
                 method='last', fill_value=np.nan,
                 references=[], grid=None,
                 range=((0, 1), (0, 1)), resolution=(100, 100),
                 record_mean=False, record_variance=False,
                 record_density=False):
        """Args:
            method (str): Method how to merge values arriving in same cell
                one of ('last','max','min','sum')
            fill_value (float): values to be used for empty cells

        TODO: continue documenting
        """
        self.opts = {'dtype': dtype,
                     'antialiasing': antialiasing,
                     'references': references,
                     'grid': grid,
                     'method': method,
                     'fill_value': fill_value,
                     'range': range,
                     'resolution': resolution,
                     'record_mean': record_mean,
                     'record_variance': record_variance,
                     'record_density': record_density}
        self.reset()


    def reset(self):
        o = self.opts

        # ATTRIBUTES
        isuniform = False
        self.grid = o['grid']
        if self.grid is None:
            isuniform = True
            self.grid = []
            for ra, re in zip(o['range'], o['resolution']):
                self.grid.append(np.linspace(ra[0], ra[1], re))
            self.range = self.opts['range']
            self.resolution = self.opts['resolution']

        else:
            self.range = []
            self.resolution = []

            for i, dim in enumerate(self.grid):
                if isinstance(dim, np.ndarray):
                    self.grid[i] = dim = dim.flatten()

                self.range.append((dim[0], dim[-1]))
                self.resolution.append(len(dim))

        # ARRAYS
        self.values = np.zeros(shape=tuple(self.resolution), dtype=o['dtype'])

        self.density, self.mean, self.variance = None, None, None
        if o['record_density'] or o['record_variance'] or o['record_mean']:
            self.density = self.values.copy()
            if o['record_variance'] or o['record_mean']:
                o['method'] = 'last'
        if o['record_mean']:
            self.mean = self.values.copy()
        if o['record_variance']:
            self.variance = self.values.copy()

        if o['fill_value'] != 0:
            if o['method'] == 'density':
                print("set 'fill_value' to zero because of method 'density'")
            else:
                self.values.fill(o['fill_value'])

        # METHODS
        if o['antialiasing']:
            self.sortMethod = _sortMethods.AntiAliased(
                                    self.grid, self.resolution, isuniform)
        else:
            self.sortMethod = _sortMethods.Aliased(
                                    self.grid, self.resolution, isuniform)
        self.mergeMethod = eval('_mergeMethods.%s' % o['method'])


    def averageValues(self):
        '''
        return the averaged values in the grid
        '''
        assert self.opts['record_density'] and self.opts['method'] == 'sum'
        # dont increase value of partly filled cells (density 0..1):
        filled = self.density > 1
        v = self.values.copy()
        v[filled] /= self.density[filled]

        # ONLY AS OPTION??:
        v[~filled] *= self.density[~filled]
        return v


    def add(self, point, value):
        '''
        Assign all self.merge_values to the self._mergeMatrix
        Get the position/intensity of a value
        '''
        # check range
        for p,r in zip(point,self.range):
            if p < r[0] or p > r[1] :
                return
        # check nan
        if isnan(value):
            return

        refs = self.opts['references']
        # for all neighbour points (1, if antialiasting=False):
        for position, intensity in self.sortMethod.getPositionsIntensities(point):
            position = tuple(position)
            if self.mean is not None:
                old_value = self.values[position]
                if not np.isnan(old_value):
                    anz_values = self.density[position]
                    mean = old_value + intensity * ( (value
                           - old_value) / (anz_values+intensity) )
                    self.mean[position] = mean

                    if self.variance is not None:
                        self.variance[position] += abs(value - mean)/(anz_values+intensity)

            if self.mergeMethod(self.values, position, intensity, value):
                for a in refs:
                    a.mergeMethod(a, position, intensity, value)
            if self.density is not None:
                self.density[position] += intensity



if __name__ == '__main__':
    import sys
    from matplotlib import pyplot

    # create values:
    x = np.sin(np.linspace(0, 40, 10000)) * np.linspace(0, 1, 10000)
    y = np.cos(np.linspace(0, 30, 10000))
    z = np.sin(np.linspace(0, 10, 10000))

    # test on a uniform grid:
    g = GridRender(range=((-1, 1), (-1, 1)),
                   resolution=(200, 200))
    for xi, yi, zi in zip(x, y, z):
        g.add((xi, yi), zi)

    # individual grid
    g2 = GridRender(grid=np.ogrid[-1:1:3e-2, -1:1:3e-2],
                    method='max',
                    antialiasing=True,
                    #record_mean=True,
                    #record_variance=True,
                    record_density=True)

    for xi, yi, zi in zip(x, y, z):
        g2.add((xi, yi), zi)

    if 'no_window' not in sys.argv:
        pyplot.figure('1')
        pyplot.imshow(g.values)

        pyplot.figure('2')
        pyplot.imshow(g2.values)

        pyplot.figure('Density')
        pyplot.imshow(g2.density)
        pyplot.show()
