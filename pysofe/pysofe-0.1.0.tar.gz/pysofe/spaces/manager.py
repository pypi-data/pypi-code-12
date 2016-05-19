"""
Provides the data structure for the degrees of freedom manager.
"""

# IMPORTS
import numpy as np
from scipy import sparse

# DEBUGGING
from IPython import embed as IPS

class DOFManager(object):
    """
    Connects the finite element mesh and reference element
    through the assignment of degrees of freedom to individual elements.

    Parameters
    ----------

    mesh : pysofe.meshes.Mesh
        The mesh for which to provide connectivity information

    element : pysofe.elements.base.Element
        The reference element
    """

    def __init__(self, mesh, element):
        # consistency check
        if not mesh.dimension == element.dimension:
            msg = "Dimension mismatch between mesh and reference element! ({}/{})"
            raise ValueError(msg.format(mesh.dimension, element.dimension))
        elif not mesh.ref_map._shape_elem.n_verts == element.n_verts:
            msg = "Incompatible shapes between mesh and reference element!"
            raise ValueError(msg)

        self._mesh = mesh
        self._element = element

    @property
    def mesh(self):
        return self._mesh

    @property
    def element(self):
        return self._element
    
    @property
    def n_dof(self):
        """
        The total number of degrees of freedom
        """
        
        n_dof = np.abs(self.get_dof_map(d=self._mesh.dimension)).max()

        return n_dof

    def get_dof_map(self, d, mask=None):
        """
        Returns the degrees of freedom mapping that connects the global mesh
        entities of topological dimension `d` to the local reference element.
        
        Parameters
        ----------
        
        d : int
            The topological dimension of the entities for which to return
            the degrees of freedom mapping

        mask : array_like
            An 1d array marking certain entities of which to get the dof map
        """
        
        dof_map = self._compute_connectivity_array()[d]

        if mask is not None:
            mask = np.asarray(mask)
            assert mask.ndim == 1

            if mask.dtype == bool:
                dof_map = dof_map.compress(mask, axis=1)
            elif mask.dtype == int:
                dof_map = dof_map.take(mask, axis=1)
            else:
                raise TypeError("Invalid type of mask! ({})".format(mask.dtype))
        
        return dof_map

    def extract_dofs(self, d, mask=None):
        """
        Returns a boolean array specifying the degrees of freedom 
        associated with the mesh entities of topological dimension `d`.

        Parameters
        ----------

        d : int
            The topological dimension of the mesh entities

        mask : array_like
            An 1d array marking certain entities of which to get the dofs
        """

        # first we need the dof map
        dof_map = self.get_dof_map(d, mask)
        n_dof = self.n_dof

        # remove duplicates and dofs mapped to `0`
        dofs = np.unique(dof_map)
        dofs = np.setdiff1d(dofs, 0)

        # build array using coo sparse matrix capabilities
        col_ind = dofs - 1
        row_ind = np.zeros_like(col_ind)
        data = np.ones_like(col_ind, dtype=bool)

        dofs = sparse.coo_matrix((data, (row_ind, col_ind)), shape=(1, n_dof))

        # turn it into an 1d array
        dofs = dofs.toarray().ravel()
        
        return dofs

    def _compute_connectivity_array(self):
        """
        Establishes the connection between the local and global degrees of freedom
        via the connectivity array `C` where `C[i,j] = k` connects the `i`-th
        global basis function on the `j`-th element to the `k`-th local basis 
        function on the reference element.
        """

        # the assignement of the degrees of freedom from 1 to the total number
        # of dofs will be done according to the following order:
        # 1.) components (scalar- or vector-valued)
        # 2.) entities
        # 3.) topological dimension (vertices, edges, cells)

        # first the assignment of new dofs
        #----------------------------------
        global_dim = self.mesh.dimension

        # init n_dofs and a list that will hold the dof indices
        # that will be assigned to the entities of each topological
        # dimension
        n_dofs = 0
        dofs = [None] * (global_dim + 1)

        # iterate through all topological dimensions and generate
        # the needed dof indices
        for topo_dim in xrange(global_dim + 1):
            # first we need the number of entities of the current
            # topological dimension
            n_entities = self.mesh.topology.n_entities[topo_dim]

            # the entry in the dof tuple specifies how many dofs are
            # associated with one entity of the current topological dimension
            dofs_needed = self.element.dof_tuple[topo_dim] * n_entities

            # generate the new dof indices starting with the current
            # number of dofs generated
            new_dofs = n_dofs + 1 + np.arange(dofs_needed, dtype=int)

            # reshape them such that the dofs that correspond to one
            # entity are contained in the corresponding column
            dofs[topo_dim] = new_dofs.reshape((-1, n_entities))

            # raise the number of generated dofs
            n_dofs += dofs_needed

        # the dof index arrays listed in `dofs` now contain column-wise
        # the dof indices for each entity of the corresponding topological
        # dimension
            
        # assemble dof maps
        #-------------------

        # init list that will hold the connectivity arrays
        # for each topological dimension
        dof_map = [None] * (global_dim + 1)

        # iterate through the topological dimensions
        # and assemble the dof map for the associated entities
        for entity_dim in xrange(global_dim + 1):
            # init a template for the dof map of the
            # currently considered entities
            temp = [None] * (entity_dim + 1)

            # iterate over all sub-entities (using their dimension)
            # of the currently considered entities and
            # add the corresponding dof indices from the
            # dof index array to the template
            for sub_dim in xrange(entity_dim + 1):
                # first we need to get the incidence relation
                # `entity_dim -> sub_dim`
                if sub_dim < entity_dim:
                    incidence = self.mesh.topology.get_connectivity(d=entity_dim,
                                                                    dd=sub_dim,
                                                                    return_indices=True)
                    n_entities = incidence.shape[0]
                else:
                    assert sub_dim == entity_dim
                    n_entities = self.mesh.topology.n_entities[entity_dim]
                    incidence = 1 + np.arange(n_entities, dtype=int)[:,None]

                # now we take the corresponding dof indices
                # and add them to the template
                sub_dim_dofs = dofs[sub_dim].take(incidence.T - 1, axis=1)
                temp[sub_dim] = np.reshape(sub_dim_dofs, newshape=(-1, n_entities))

            dof_map[entity_dim] = np.vstack(temp)

        return dof_map
