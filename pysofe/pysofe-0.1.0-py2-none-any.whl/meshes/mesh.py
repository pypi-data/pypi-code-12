"""
Provides the data structure for approximating the spatial domain
of the partial differential equation.
"""

# IMPORTS
import numpy as np

import refinements
from .geometry import MeshGeometry
from .topology import MeshTopology
from .reference_map import ReferenceMap

# DEBUGGING
from IPython import embed as IPS

class Mesh(object):
    """
    Provides a class for general meshes.

    Basically clues together the MeshGeometry and MeshTopology
    classes and provides interfaces for mesh refinement and
    function evaluation.

    Parameters
    ----------

    nodes : array_like
        The coordinates of the mesh nodes

    connectivity : array_like
        The connectivity array defining the mesh cells via their vertex indices
    """

    def __init__(self, nodes, connectivity):
        # transform input arguments if neccessary
        nodes = np.atleast_2d(nodes)
        connectivity = np.asarray(connectivity, dtype=int)

        # check input arguments
        assert 1 <= nodes.shape[1] <= 3
        
        # get mesh dimension from nodes
        self._dimension = nodes.shape[1]

        # init mesh geometry and topology
        self.geometry = MeshGeometry(nodes)
        self.topology = MeshTopology(cells=connectivity, dimension=self._dimension)

        # init reference maps class
        self.ref_map = ReferenceMap(self)

    @property
    def dimension(self):
        """
        The spatial dimension fo the mesh.
        """
        return self._dimension

    @property
    def nodes(self):
        """
        The coordinates of the mesh nodes.
        """
        return self.geometry.nodes

    @property
    def cells(self):
        """
        The incident vertex indices of the mesh cells.
        """
        # the mesh cells have the same topological dimension as the mesh dimension
        return self.topology.get_entities(d=self.dimension)

    @property
    def facets(self):
        """
        The incident vertex indices of the mesh facets.
        """
        # the mesh facets have topological codimension 1
        return self.topology.get_entities(d=self.dimension - 1)

    @property
    def faces(self):
        """
        The incident vertex indices of the mesh faces.
        """
        # faces are mesh entities of topological dimension 2
        return self.topology.get_entities(d=2)

    @property
    def edges(self):
        """
        The incident vertex indices of the mesh edges.
        """
        # edges are mesh entities of topological dimension 1
        return self.topology.get_entities(d=1)

    def boundary(self, fnc=None):
        """
        Determines the mesh facets that are part of the boundary specified
        by the function `fnc` and returns a corresponding boolean array.

        Parameters
        ----------

        fnc : callable
            Function specifying some part of the boundary for which
            to return the corresponding facets
        """

        # get a mask specifying the boundary facets
        boundary_mask = self.topology.get_boundary(d=self.dimension-1)

        if fnc is not None:
            assert callable(fnc)

            # to determine the facets that belong to the desired
            # part of the boundary we compute the centroids of
            # all boundary facets and pass them as arguments to
            # the given function which shall return True for all
            # those that belong to the specified part

            # to compute the centroids we need the vertex indices of
            # every facet and the corresponding node coordinates
            facet_vertices = self.facets.compress(boundary_mask, axis=0)
            facet_vertex_coordinates = self.nodes.take(facet_vertices - 1, axis=0)
            centroids = facet_vertex_coordinates.mean(axis=1)

            # pass them to the given function (column-wise)
            try:
                part_mask = fnc(centroids.T)
            except:
                # given function might not be vectorized
                # so try looping over the centroids
                # --> may be slow
                ncentroids = np.size(centroids, axis=0)
                part_mask = np.empty(shape=(ncentroids,), dtype=bool)

                for i in xrange(ncentroids):
                    part_mask[i] = fnc(centroids[i,:])

            boundary_mask[boundary_mask] = np.logical_and(boundary_mask[boundary_mask], part_mask)

        return boundary_mask

    def refine(self, method='uniform', **kwargs):
        """
        Refines the mesh using the given method.

        Parameters
        ----------

        method : str
            A string specifying the refinement method to use
        """
        refinements.refine(mesh=self, method=method, inplace=True, **kwargs)

    def eval_function(self, fnc, points):
        """
        Evaluates a given function in the global mesh points corresponding
        to the given local points on the reference domain.

        Parameters
        ----------

        fnc : callable
            The function to evaluate

        points : array_like
            The local points on the reference domain
        
        Returns
        -------

        numpy.ndarray
            nE x nP [x ...]
        """

        # first we need the global counterparts to the given local points
        # --> nE x nP x nD
        global_points = self.ref_map.eval(points, deriv=0)
        nE, nP, nD = global_points.shape

        # stack and transpose them so they can be passed to the function
        # --> nD x (nE * nP)
        global_points = np.vstack(global_points).T
        assert global_points.shape == (nD, nE * nP)

        # evaluate the function
        if callable(fnc):
            # if the given function is callable, call it
            try:
                values = fnc(global_points)
            except Exception as err:
                # TODO: maybe do some stuff here...
                raise err

            # we are assuming it is a scalar function
            # TODO: add test or get rid of this restriction?
            values = values.reshape((nE, nP))

        else:
            values = np.zeros((nE, nP))
            
            if np.isscalar(fnc):
                # if the given function is somehow constant
                # return a broadcasted version that matches the
                # return shape nE x nP
                _, values = np.broadcast_arrays(values[:,:],
                                                np.asarray(fnc))
            elif isinstance(fnc, (np.ndarray, list, tuple)):
                # if it is an array like object (assuming vector or matrix)
                # also broadcast it
                if not isinstance(fnc, np.ndarray):
                    fnc = np.asarray(fnc)
                
                ndim = fnc.ndim

                if ndim == 1:
                    # assuming vector
                    _, values = np.broadcast_arrays(values[:,:,None],
                                                    fnc[None,None,:])
                elif ndim == 2:
                    # assuming matrix
                    _, values = np.broadcast_arrays(values[:,:,None,None],
                                                    fnc[None,None,:,:])
                else:
                    raise ValueError("Invalid number of dimensions of fnc!")

            else:
                raise TypeError("Invalid function type!")

        return values            # nE x nP x nD
        # return np.vstack(values) # (nE*nP) x nD

class UnitSquareMesh(Mesh):
    """
    Discretizes the domain of the unit square in 2D.

    Parameters
    ----------

    nx : int
        Number of nodes in the x-direction

    ny : int
        Number of nodes in the y-direction
    """

    def __init__(self, nx=10, ny=10):
        nodes = self._create_nodes(nx, ny)
        cells = self._create_cells(nx, ny)

        Mesh.__init__(self, nodes, cells)

    @staticmethod
    def _create_nodes(nx, ny):
        ls_x = np.linspace(0., 1., nx)
        ls_y = np.linspace(0., 1., ny)

        x, y = np.meshgrid(ls_x, ls_y)

        nodes = np.vstack([x.flat, y.flat]).T

        return nodes

    @staticmethod
    def _create_cells(nx, ny):
        indices = np.arange(nx * ny, dtype='int') + 1

        tmp = np.where(indices[:-nx] % nx)[0] + 1
        first_nodes  = np.hstack([tmp,    tmp+1])
        second_nodes = np.hstack([tmp+1,  tmp+nx])
        third_nodes  = np.hstack([tmp+nx, tmp+nx+1])

        cells = np.vstack([first_nodes,
                           second_nodes,
                           third_nodes]).T

        return cells
