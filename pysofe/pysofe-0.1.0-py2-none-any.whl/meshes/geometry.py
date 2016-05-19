"""
Provides the data structure that supplies geometrical information on the meshes.
"""

# IMPORTS
import numpy as np

class MeshGeometry(object):
    """
    Stores geometrical information of a mesh.

    Parameters
    ----------

    nodes : array_like
        The coordinates of the mesh grid points
    """

    def __init__(self, nodes):
        # check input
        if not isinstance(nodes, np.ndarray):
            nodes = np.atleast_2d(nodes)

        if nodes.ndim > 2:
            raise ValueError("Invalid dimension of nodes array ({})".format(nodes.ndim))

        self._nodes = nodes

    @property
    def nodes(self):
        """
        The coordinates of the mesh grid points
        """
        return self._nodes
