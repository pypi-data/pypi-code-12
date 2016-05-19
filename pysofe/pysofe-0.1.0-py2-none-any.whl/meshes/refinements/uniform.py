"""
Provides methods for the uniform refinement of mesh cells.
"""

# IMPORTS
import numpy as np

# DEBUGGING
from IPython import embed as IPS

def uniform_refine_simplices(mesh):
    """
    Wrapper function to call appropriate method w.r.t.
    the maximum topological dimension of the mesh entities.

    Parameters
    ----------

    mesh : pysofe.meshes.Mesh
        The finite element mesh to refine
    """

    if mesh.dimension == 1:
        return _uniform_refine_intervals(mesh)
    elif mesh.dimension == 2:
        return _uniform_refine_triangles(mesh)
    elif mesh.dimension == 3:
        return _uniform_refine_tetrahedra(mesh)
    else:
        raise ValueError("Invalid mesh dimension! ({})".format(mesh.dimension))

def _uniform_refine_intervals(mesh):
    """
    Uniformly refines each interval of a 1d mesh into two new subintervals.
    """

    # get current cells
    cells = mesh.cells

    # create additional nodes as midpoints of the cells
    midpoints = 0.5 * mesh.nodes.take(cells - 1, axis=0).sum(axis=1)

    # add them to the existing nodes
    new_nodes = np.vstack([mesh.nodes, midpoints])

    # sort the new nodes
    new_nodes.sort(axis=0)

    # get number of new nodes
    n_nodes = np.size(new_nodes, axis=0)

    # generate new node indices
    indices = 1 + np.arange(n_nodes, dtype=int)

    # and new cells
    new_cells = indices.repeat(2)[1:-1].reshape((-1,2))

    return new_nodes, new_cells
    
def _uniform_refine_triangles(mesh):
    """
    Uniformly refines each triangle of a 2d mesh into four new triangles.
    """

    # get current cells and edges
    cells = mesh.cells
    edges = mesh.edges

    assert np.size(cells, axis=1) == 3

    # get number of current nodes
    n_nodes = np.size(mesh.nodes, axis=0)
    
    # first we create additional nodes as midpoints of the current edges
    midpoints = 0.5 * mesh.nodes.take(edges - 1, axis=0).sum(axis=1)

    # add them to the existing mesh nodes
    new_nodes = np.vstack([mesh.nodes, midpoints])
    
    # then we generate the indices of the newly created nodes
    #
    # their indices start at the current number of nodes (`n_nodes`) + 1
    # and end after additional `n_edges` nodes
    n_edges = np.size(edges, axis=0)
    new_node_indices = np.arange(n_nodes + 1, n_nodes + n_edges + 1, dtype=int)

    # refine elements
    #
    # for every element we need the indices of the edges at which the corresponding
    # new nodes are created
    indices_2_1 = mesh.topology.get_connectivity(2, 1, return_indices=True) - 1
    
    # next we augment the indices that define each element as if
    # they were defined by 6 nodes (including those of the edge midpoints)
    cells_ = np.hstack([cells, new_node_indices.take(indices_2_1, axis=0)])
    
    # now we can generate the four new elements for each existing one
    new_cells_1 = np.vstack([cells_[:,0], cells_[:,3], cells_[:,4]]).T
    new_cells_2 = np.vstack([cells_[:,1], cells_[:,3], cells_[:,5]]).T
    new_cells_3 = np.vstack([cells_[:,2], cells_[:,4], cells_[:,5]]).T
    new_cells_4 = np.vstack([cells_[:,3], cells_[:,4], cells_[:,5]]).T
    
    new_cells = np.vstack([new_cells_1, new_cells_2, new_cells_3, new_cells_4])

    return new_nodes, new_cells

def _uniform_refine_tetrahedra(mesh):
    """
    Uniformly refines each tetrahedron of a 3d mesh into eight new tetrahedra.
    """

    # get current cells and edges
    cells = mesh.cells
    edges = mesh.edges

    assert np.size(cells, axis=1) == 4

    # get number of current nodes
    n_nodes = np.size(mesh.nodes, axis=0)
    
    # first we create additional nodes as midpoints of the current edges
    midpoints = 0.5 * mesh.nodes.take(edges - 1, axis=0).sum(axis=1)

    # add them to the existing mesh nodes
    new_nodes = np.vstack([mesh.nodes, midpoints])
    
    # then we generate the indices of the newly created nodes
    #
    # their indices start at the current number of nodes (`n_nodes`) + 1
    # and end after additional `n_edges` nodes
    n_edges = np.size(edges, axis=0)
    new_node_indices = np.arange(n_nodes + 1, n_nodes + n_edges + 1, dtype=int)

    # refine elements
    #
    # for every element we need the indices of the edges at which the
    # corresponding new nodes are created
    indices_3_1 = mesh.topology.get_connectivity(3, 1, return_indices=True) - 1
    
    # next we augment the indices that define each element as if
    # they were defined by 10 nodes (including those of the edge midpoints)
    cells_ = np.hstack([cells, new_node_indices.take(indices_3_1, axis=0)])
    
    # now we can generate the eight new elements for each existing one
    new_cells_1 = np.vstack([cells_[:,0], cells_[:,4], cells_[:,5], cells_[:,6]]).T
    new_cells_2 = np.vstack([cells_[:,1], cells_[:,4], cells_[:,7], cells_[:,8]]).T
    new_cells_3 = np.vstack([cells_[:,2], cells_[:,5], cells_[:,7], cells_[:,9]]).T
    new_cells_4 = np.vstack([cells_[:,3], cells_[:,6], cells_[:,8], cells_[:,9]]).T
    new_cells_5 = np.vstack([cells_[:,4], cells_[:,5], cells_[:,6], cells_[:,9]]).T
    new_cells_6 = np.vstack([cells_[:,4], cells_[:,5], cells_[:,7], cells_[:,9]]).T
    new_cells_7 = np.vstack([cells_[:,4], cells_[:,6], cells_[:,8], cells_[:,9]]).T
    new_cells_8 = np.vstack([cells_[:,4], cells_[:,7], cells_[:,8], cells_[:,9]]).T
    
    new_cells = np.vstack([new_cells_1, new_cells_2, new_cells_3, new_cells_4,
                           new_cells_5, new_cells_6, new_cells_7, new_cells_8])

    return new_nodes, new_cells

