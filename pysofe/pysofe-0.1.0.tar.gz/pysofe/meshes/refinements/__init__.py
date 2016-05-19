"""
Provides refinement methods for the finite element meshes.
"""

import uniform

from .uniform import uniform_refine_simplices

def refine(mesh, method='uniform', inplace=True, **kwargs):
    '''
    Wrapper to call various refinement methods.
    
    Parameters
    ----------
    
    mesh : pysofe.meshes.Mesh
        The mesh that should be refined

    method : str
        Which refinement method to use 

    inplace : bool
        Whether to create new mesh or alter the given one
        (pay attention to possible side-effects)
    '''
    
    if method == 'uniform':
        times = kwargs.get('times', 1)

        for i in xrange(times):
            new_nodes, new_cells = uniform_refine_simplices(mesh)
            
            if inplace:
                # inplace refinement
                mesh.geometry._nodes = new_nodes
                mesh.topology._reset()
                mesh.topology._init_incidence(cells=new_cells)
            else:
                mesh = Mesh(new_nodes, new_cells)
    else:
        msg = 'Refinement method is not available! ({})'
        raise NotImplementedError(msg.format(method))

    return mesh

