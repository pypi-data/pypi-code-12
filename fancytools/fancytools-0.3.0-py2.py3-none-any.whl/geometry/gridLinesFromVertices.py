import numpy as np


def gridLinesFromVertices(edges, nCells, dtype=float):
    '''creates a regular 2d grid from given edge points (4*(x0,y0))
    and number of cells in x and y

    Returns:
        tuple(4lists): horizontal and vertical lines as (x0,y0,x1,y1)
    '''
    e = edges
    sx, sy = nCells[0]+1, nCells[1]+1
    # horizontal lines
    x0 = np.linspace(e[0, 0], e[3, 0], sy, dtype=dtype)
    x1 = np.linspace(e[1, 0], e[2, 0], sy, dtype=dtype)

    y0 = np.linspace(e[0, 1], e[3, 1], sy, dtype=dtype)
    y1 = np.linspace(e[1, 1], e[2, 1], sy, dtype=dtype)

    horiz = np.array(zip(x0, y0, x1, y1))

    # vertical lines
    x0 = np.linspace(e[0, 0], e[1, 0], sx, dtype=dtype)
    x1 = np.linspace(e[3, 0], e[2, 0], sx, dtype=dtype)

    y0 = np.linspace(e[0, 1], e[1, 1], sx, dtype=dtype)
    y1 = np.linspace(e[3, 1], e[2, 1], sx, dtype=dtype)

    vert = np.array(zip(x0, y0, x1, y1))

    return horiz, vert


if __name__ == '__main__':
    import sys
    import pylab as plt

    edges = np.array([(0, 0),
                      (1, 0.1),
                      (2, 2),
                      (0.1, 1)])
    ncells = (10, 5)

    h, v = gridLinesFromVertices(edges, ncells)
    print h[0]

    if 'no_window' not in sys.argv:
        plt.figure('create grid with %s cells within given edge points' % str(ncells))
        for l in v:
            plt.plot((l[0], l[2]), (l[1], l[3]), 'r')
        for l in h:
            plt.plot((l[0], l[2]), (l[1], l[3]), 'g')

        plt.scatter(edges[:, 0], edges[:, 1])
        plt.show()
