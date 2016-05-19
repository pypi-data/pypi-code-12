"""
Provides some auxilliary functions that are used in various
points in the software.
"""

import numpy as np

def unique_rows(A, return_index=False, return_inverse=False):
    """
    Returns `B, I, J` where `B` is the array of unique rows from
    the input array `A` and `I, J` are arrays satisfying
    `A = B[J,:]` and `B = A[I,:]`.

    Parameters
    ----------

    A : numpy.ndarray
        The 2d array for which to determine the unique rows

    return_index : bool
        Whether to return `I`

    return_inverse : bool
        Whether to return `J`
    """
    
    A = np.require(A, requirements='C')
    assert A.ndim == 2, "Input array must be 2-dimensional"

    B = np.unique(A.view([('', A.dtype)]*A.shape[1]),
               return_index=return_index,
               return_inverse=return_inverse)

    if return_index or return_inverse:
        return (B[0].view(A.dtype).reshape((-1, A.shape[1]), order='C'),) \
            + B[1:]
    else:
        return B.view(A.dtype).reshape((-1, A.shape[1]), order='C')

def lagrange_nodes(dimension, order):
    """
    Returns the nodes that determine the Lagrange shape functions of
    given order on a simplicial domain.
    
    Parameters
    ----------

    dimension : int
        The spatial dimension of the points

    order : int
        The polynomial order of the shape functions
    """
    assert dimension in {1, 2, 3}
    assert order >= 0
    
    if dimension == 1:
        if order == 0:
            nodes = np.array([[1/3.]])
        elif order > 0:
            points1d = np.linspace(0., 1., order+1)
            nodes = np.atleast_2d(np.hstack([points1d[0], points1d[-1],
                                             points1d[1:-1]]))
    elif dimension == 2:
        if order == 0:
            nodes = np.array([[1/3.],
                              [1/3.]])
        elif order > 0:
            # 3 vertices
            vertex_nodes = np.array([[0., 1., 0.],
                                     [0., 0., 1.]])
            
            # 3 * (p-1) edge nodes
            points1d = np.linspace(0., 1., (order-1)+2)[1:-1]
            
            edge_nodes_1 = np.vstack([points1d, np.zeros_like(points1d)])
            edge_nodes_2 = np.vstack([np.zeros_like(points1d), points1d])
            edge_nodes_3 = np.vstack([points1d[::-1], points1d])
            
            # (p-1)*(p-1) / 2 interior nodes
            gridx, gridy = np.meshgrid(points1d, points1d)
            grid = np.vstack([gridx.flat, gridy.flat])
            
            interior_nodes = grid.compress(grid.sum(axis=0) < 1, axis=1)
            
            nodes = np.hstack([vertex_nodes,
                               edge_nodes_1, edge_nodes_2, edge_nodes_3,
                               interior_nodes])
    elif dimension == 3:
        if order == 0:
            nodes = np.array([[1/3.],
                              [1/3.],
                              [1/3.]])
        elif order > 0:
            # 4 vertices
            vertex_nodes = np.array([[0., 1., 0., 0.],
                                     [0., 0., 1., 0.],
                                     [0., 0., 0., 1.]])
            
            # 6 * (p-1) edge nodes
            points1d = np.linspace(0., 1., (order-1)+2)[1:-1]
            zeros1d = np.zeros_like(points1d)
            
            edge_nodes_1 = np.vstack([points1d, zeros1d, zeros1d])
            edge_nodes_2 = np.vstack([zeros1d, points1d, zeros1d])
            edge_nodes_3 = np.vstack([zeros1d, zeros1d, points1d])
            edge_nodes_4 = np.vstack([points1d[::-1], points1d, zeros1d])
            edge_nodes_5 = np.vstack([points1d[::-1], zeros1d, points1d])
            edge_nodes_6 = np.vstack([zeros1d, points1d[::-1], points1d])
            
            # (p-1)*(p-2)*(p-3) / 3 interior nodes
            gridx, gridy, gridz = np.meshgrid(points1d, points1d, points1d)
            grid = np.vstack([gridx.flat, gridy.flat, gridz.flat])
            
            interior_nodes = grid.compress(grid.sum(axis=0) < 1, axis=1)
            
            nodes = np.hstack([vertex_nodes,
                               edge_nodes_1, edge_nodes_2, edge_nodes_3,
                               edge_nodes_4, edge_nodes_5, edge_nodes_6,
                               interior_nodes])

    
    return nodes
