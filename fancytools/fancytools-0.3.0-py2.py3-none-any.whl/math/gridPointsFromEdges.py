import numpy as np


def gridPointsFromEdges(edges, nCells, dtype=float): 
    '''
    creates a regular 2d grid from given edge points (4*(x0,y0))
    and number of cells in x and y
    
    returns horizontal and vertical lines as (x0,y0,x1,y1)
    '''
    e =  edges
    sx,sy =  nCells[0]+1, nCells[1]+1 
    #horizontal lines
    x0 = np.linspace(e[0,0],e[3,0],sy, dtype=dtype)
    x1 = np.linspace(e[1,0],e[2,0],sy, dtype=dtype)

    y0 = np.linspace(e[0,1],e[3,1],sy, dtype=dtype)
    y1 = np.linspace(e[1,1],e[2,1],sy, dtype=dtype)
    #points:
    p = np.empty(shape=(sx*sy,2))
    n0 = 0
    n1 = sx
    for x0i,x1i,y0i,y1i in zip(x0,x1, y0,y1):
        p[n0:n1,0] = np.linspace(x0i,x1i,sx)
        p[n0:n1,1] = np.linspace(y0i,y1i,sx)
        n0=n1
        n1+=sx
    return p

    

if __name__ == '__main__':
    import pylab as plt
    
    edges =  np.array([(0,0),
                       (1,0.1),
                       (2,2),
                       (0.1,1)])
    ncells = (10,5)
    
    p = gridPointsFromEdges(edges,ncells)

    plt.figure('create grid with %s cells within given edge points' %str(ncells))
    plt.scatter(p[:,0],p[:,1])

    plt.scatter(edges[:,0],edges[:,1],color='r')
    plt.show()