"""
Provides some visualization capabilities.
"""

# IMPORTS
try:
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D
    from matplotlib import cm
except ImportError as err:
    # Could not import pyplot
    # ... do some stuff here
    raise err

# DEBUGGING
from IPython import embed as IPS

import numpy as np

import pysofe
from pysofe import utils

def show(obj, *args, **kwargs):
    """
    Wrapper function for the visualization of 
    various pysofe objects.

    Parameters
    ----------

    obj
        The pysofe object to visualize
    """

    # select appropriate visualizer and call its `show()` method
    if isinstance(obj, pysofe.elements.base.Element):
        V = ElementVisualizer()
        V.show(element=obj, **kwargs)
    elif isinstance(obj, pysofe.meshes.mesh.Mesh):
        V = MeshVisualizer()
        V.show(obj, *args, **kwargs)
    elif isinstance(obj, pysofe.quadrature.gaussian.GaussQuadSimp):
        V = QuadRuleVisualizer()
        V.show(obj, *args, **kwargs)
    elif isinstance(obj, pysofe.spaces.space.FESpace):
        V = FESpaceVisualizer()
        V.show(obj, *args, **kwargs)
    elif isinstance(obj, pysofe.spaces.functions.FEFunction):
        V = FunctionVisualizer()
        V.show(obj, **kwargs)
    else:
        raise NotImplementedError()

class Visualizer(object):
    """
    Base class for all visualizers.
    """

    def plot(self, *args, **kwargs):
        fig, axes = self._plot(*args, **kwargs)

        return fig, axes

    def _plot(self, *args, **kwargs):
        raise NotImplementedError()
    
    def show(self, *args, **kwargs):
        fig, axes = self.plot(*args, **kwargs)

        fig.show()

class MeshVisualizer(Visualizer):
    """
    Visualizes the :py:class:`pysofe.meshes.Mesh` class.
    """

    def _plot(self, mesh, *args, **kwargs):
        fontsize = kwargs.get('fontsize', 9)
        
        fig = plt.figure()
        ax = fig.add_subplot(111)

        if mesh.dimension == 1:
            nodes = mesh.nodes[:,0]
            zeros = np.zeros_like(nodes)
            ax.plot(nodes, zeros, '-o')
        elif mesh.dimension == 2:
            cols = range(3)
            ax.triplot(mesh.nodes[:,0], mesh.nodes[:,1], np.asarray(mesh.cells[:,cols] - 1))
        else:
            raise NotImplementedError()
            
        # zoom out to make outer faces visible
        xlim = list(ax.get_xlim()); ylim = list(ax.get_ylim())
        xlim[0] -= 0.1; xlim[1] += 0.1
        ylim[0] -= 0.1; ylim[1] += 0.1
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)
    
        show_all = ('all' in args)
    
        # nodes
        if 'nodes' in args or show_all:
            for i in xrange(mesh.nodes.shape[0]):
                if mesh.dimension == 1:
                    ax.text(x=mesh.nodes[i,0], y=0., s=i+1,
                            color='red', fontsize=fontsize)
                elif mesh.dimension == 2:
                    ax.text(x=mesh.nodes[i,0], y=mesh.nodes[i,1], s=i+1,
                            color='red', fontsize=fontsize)
                else:
                    raise NotImplementedError()
                    
        # edges
        if 'edges' in args or show_all:
            edges = mesh.edges
            bary = 0.5 * mesh.nodes[edges - 1,:].sum(axis=1)
            for i in xrange(edges.shape[0]):
                if mesh.dimension == 1:
                    ax.text(x=bary[i,0], y=0, s=i+1,
                            color='green', fontsize=fontsize)
                elif mesh.dimension == 2:
                    ax.text(x=bary[i,0], y=bary[i,1], s=i+1,
                            color='green', fontsize=fontsize)

        # elements
        if mesh.dimension > 1 and ('cells' in args or show_all):
            cells = mesh.cells
            bary = mesh.nodes[cells - 1,:].sum(axis=1) / 3.
            for i in xrange(cells.shape[0]):
                ax.text(x=bary[i,0], y=bary[i,1], s=i+1,
                        color='blue', fontsize=fontsize)
        
        if 'local vertices' in args:
            cells = mesh.cells
            cell_nodes = mesh.nodes.take(cells - 1, axis=0)
            bary = cell_nodes.sum(axis=1) / 3.
            nE = cells.shape[0]
            
            # calculate positions where to put the local vertex numbers
            local_1 = cell_nodes[:,0] + 0.4 * (bary - cell_nodes[:,0])
            local_2 = cell_nodes[:,1] + 0.4 * (bary - cell_nodes[:,1])
            local_3 = cell_nodes[:,2] + 0.4 * (bary - cell_nodes[:,2])
            
            for i in xrange(nE):
                ax.text(x=local_1[i,0], y=local_1[i,1], s=1, color='red', fontsize=fontsize)
                ax.text(x=local_2[i,0], y=local_2[i,1], s=2, color='red', fontsize=fontsize)
                ax.text(x=local_3[i,0], y=local_3[i,1], s=3, color='red', fontsize=fontsize)

        return fig, ax

class ElementVisualizer(Visualizer):
    """
    Visualizes :py:class:`pysofe.elements.base.Element` classes.
    """

    def _plot(self, element, **kwargs):
        """
        Plots the basis function or their derivatives of the given element.
        
        Parameters
        ----------

        element : pysofe.base.Element
            The finite element of which to plot the basis functions

        codim : int
            The codimension of the entity for which to plot the respective basis functions

        d : int
            The derivation order

        indices : array_like
            Specify certain basis function to show

        resolution : int
            Resolution of the grid points for the plot

        typ : str
            The plotting type ('surface' or 'scatter')

        shadow : bool
            Whether to plot a shadow of the surface
        """
        
        # get arguments
        dim = kwargs.get('dim', element.dimension)
        d = kwargs.get('d', 0)
        indices = kwargs.get('indices', None)
        resolution = kwargs.get('resolution', 10*np.ceil(np.log(element.order+1)))
        typ = kwargs.get('typ', 'surface')
        shadow = kwargs.get('shadow', False)
        layout = kwargs.get('layout', None)

        if d != 0:
            raise NotImplementedError()

        if element.dimension > 2:
            raise NotImplementedError()

        codim = element.dimension - dim
        
        if element.dimension == 1:
            project = None
        elif element.dimension == 2:
            if codim == 0:
                project = '3d'
            elif codim == 1:
                project = None

        # create grid points at which to evaluate the basis functions
        ls = np.linspace(0., 1., num=resolution)

        if element.dimension == 1:
            points = ls
        
        elif element.dimension == 2:
            if codim == 0:
                X,Y = np.meshgrid(ls, ls)
                XY = np.vstack([np.hstack(X), np.hstack(Y)])
                points = XY.compress(XY.sum(axis=0) <= 1., axis=1)
            elif codim == 1:
                points = ls

        # evaluate all basis function at all points
        basis = element.eval_basis(points, deriv=d)    # nB x nP

        if indices is not None:
            assert hasattr(indices, '__iter__')
            indices = np.asarray(indices, dtype=int) - 1
            assert indices.min() >= 0

            basis = basis.take(indices, axis=0)
        else:
            indices = np.arange(np.size(basis, axis=0))

        # create a subplot for each basis function
        nB = np.size(basis, axis=0)

        fig = plt.figure()
        
        if layout is None:
            nB_2 = int(0.5*(nB+1))

            for i in xrange(1, nB_2+1):
                if codim == 0:
                    fig.add_subplot(nB_2,2,2*i-1, projection=project)
                    if 2*i <= nB:
                        fig.add_subplot(nB_2,2,2*i, projection=project)
                elif codim == 1:
                    fig.add_subplot(nB_2,2,2*i-1, projection=project)
                    if 2*i <= nB:
                        fig.add_subplot(nB_2,2,2*i, projection=project)
            
            
        else:
            assert 1 <= len(layout) <= 2
        
            if len(layout) == 1:
                layout = (1,layout[0])
        
            assert np.multiply(*layout) >= nB
        
            for j in xrange(nB):
                if codim == 0:
                    fig.add_subplot(layout[0], layout[1], j+1, projection=project)
                elif codim == 1:
                    fig.add_subplot(layout[0], layout[1], j+1, projection=project)


        if element.dimension == 1:
            for i in xrange(nB):
                fig.axes[i].plot(points.ravel(), basis[i].ravel())
                #fig.axes[i].set_title(r"$\varphi_{{ {} }}$".format(i+1), fontsize=32)
                fig.axes[i].set_title(r"$\varphi_{{ {} }}$".format(indices[i]+1), fontsize=32)
        
        elif element.dimension == 2:
            if codim == 0:
                for i in xrange(nB):
                    if typ == 'scatter':
                        fig.axes[i].scatter(points[0], points[1], basis[i])
                    elif typ == 'surface':
                        fig.axes[i].plot_trisurf(points[0], points[1], basis[i],
                                                 cmap=cm.jet, linewidth=0., antialiased=False)
                        if shadow:
                            c = fig.axes[i].tricontourf(points[0], points[1], basis[i],
                                                        zdir='z', offset=0., colors='gray')
                    fig.axes[i].autoscale_view(True,True,True)
                    #fig.axes[i].set_title(r"$\varphi_{{ {} }}$".format(i+1), fontsize=32)
                    fig.axes[i].set_title(r"$\varphi_{{ {} }}$".format(indices[i]+1), fontsize=32)
            elif codim == 1:
                for i in xrange(nB):
                    fig.axes[i].plot(points.ravel(), basis[i].ravel())
                    #fig.axes[i].set_title(r"$\psi_{{ {} }}$".format(i+1), fontsize=32)
                    fig.axes[i].set_title(r"$\psi_{{ {} }}$".format(indices[i]+1), fontsize=32)
    
        return fig, fig.axes

class FunctionVisualizer(Visualizer):
    '''
    Base class for visualizing functions.
    '''

    def _plot(self, fnc, **kwargs):
        '''
        Plots the function.

        Parameters
        ----------

        ...

        '''

        self.fnc = fnc

        if fnc.fe_space.mesh.dimension == 1:
            mode = '1dplot'
        elif fnc.fe_space.mesh.dimension == 2:
            mode = kwargs.get('mode', 'trisurface')
        else:
            raise NotImplementedError()

        # get visualization data
        #----------------------------------------------------
        points, values, cells = self._get_visualizetion_data(mode, **kwargs)

        # set up figure and axes
        #----------------------------------------------------

        # get number of plots
        n_values = values.shape[0]
        
        layout = kwargs.get('layout', None)

        if layout is None:
            if n_values == 1:
                nrows = 1
                ncols = 1
            elif 1 < n_values < 9:
                nrows = int(np.ceil(n_values/2.))
                ncols = 2
            else:
                nrows = int(np.ceil(n_values/3.))
                ncols = 3
        else:
            nrows, ncols = layout

        # create figure and subplots (if neccessary)
        fig = kwargs.get('fig', None)
        axes = kwargs.get('ax', None)
        if axes is None:
            if mode in ('trisurface', 'surface', 'wireframe'):
                subplot_kw = {'projection' : '3d'}
            else:
                subplot_kw = {}
            
            fig, axes = plt.subplots(nrows, ncols, squeeze=False, subplot_kw=subplot_kw)
        else:
            axes = np.atleast_2d(axes)
                
            assert axes.ndim == 2
            assert nrows <= axes.shape[0]
            assert ncols <= axes.shape[1]

        # called plotting routine specified by `mode`
        #----------------------------------------------------
        if mode == '1dplot':
            axes[0,0].plot(points[0], values[0])
        elif mode == 'trisurface':
            self._plot_trisurf(axes=axes, X=points[0], Y=points[1], triangles=cells,
                               Z=values, **kwargs)
        elif mode in ('tripcolor', 'heatmap'):
            self._plot_tripcolor(axes=axes, X=points[0], Y=points[1], triangles=cells,
                                 Z=values, **kwargs)

        return fig, axes

    def _get_visualizetion_data(self, mode, **kwargs):
        if mode in ('1dplot',):
            local_points = np.linspace(0., 1., 10)[None,:]

            points = self.fnc.fe_space.mesh.ref_map.eval(local_points)
            _, I = np.unique(points.flat, return_index=True)
            points = points.ravel().take(I)[None,:]
            
            values = self.fnc(points=local_points, deriv=0).ravel().take(I)
            values = np.atleast_2d(values)
            
            cells = np.arange(points.size, dtype='int').repeat(2)[1:-1].reshape((-1,2))

            return points, values, cells
        elif mode in ('trisurface', 'tripcolor', 'heatmap'):
            # get points, values and triangles for the plot

            return self._get_triangulation_data(**kwargs)
        else:
            msg = "Invalid visualization mode for functions! ({})"
            raise ValueError(msg.format(mode))

    def _get_triangulation_data(self, **kwargs):
        # generate local points for the function evaluation
        n_sub_grid = kwargs.get('n_sub_grid', self.fnc.order + 1)
            
        local_points = utils.lagrange_nodes(dimension=2, order=n_sub_grid)
        
        # project them to their global counterparts
        order = 'C'

        points = self.fnc.fe_space.mesh.ref_map.eval(points=local_points,
                                                     deriv=0)
            
        points = np.vstack([points[:,:,0].ravel(order=order), points[:,:,1].ravel(order=order)])

        # get unique points indices
        _, I = utils.unique_rows(points.T, return_index=True)
        points = points.take(I, axis=1)

        # evaluate the function w.r.t the unique points
        d = kwargs.get('d', 0)

        if 0:
            if isinstance(self.fnc, pysofe.spaces.functions.FEFunction):
                eval_local = kwargs.get('eval_local', True)
                
                if eval_local:
                    values = self.fnc(points=local_points, d=d, local=True)
                else:
                    values = self.fnc(points=points, d=d, local=False)
            elif isinstance(self.fnc, pysofe.spaces.functions.MeshFunction):
                values = self.fnc(points=points, d=d)
        else:
            fnc_args = kwargs.get('fnc_args', dict())
            
            if kwargs.get('eval_local', True):
                values = self.fnc(points=local_points, deriv=d, **fnc_args)
            else:
                values = self.fnc(points=points, d=d, local=False, **fnc_args)
                
        if d == 0:
            values = values.ravel(order=order).take(I, axis=0)
        elif d == 1:
            values = np.asarray([values.take(i, axis=-1).ravel(order=order).take(I, axis=0) for i in xrange(values.shape[-1])])
        else:
            raise ValueError('Invalid derivation order for visualization! ({})'.format(d))

        # get cells corresponding to the unique points
        from scipy.spatial import Delaunay
        cells = Delaunay(points.T).simplices

        values = np.atleast_2d(values)
        
        return points, values, cells

    def _plot_trisurf(self, axes, X, Y, triangles, Z, **kwargs):
        '''
        Wrapper for the :py:meth:`plot_trisurf` method of
        the :py:class:`Axes3D` class.

        Parameters
        ----------

        X, Y : array_like
            1D arrays of the triangulation node coordinates

        triangles : array_like
            Connectivity array of the triangulation

        Z : array_like
            1D array of the values at the triangulation nodes
        '''

        # set default values
        cmap = kwargs.get('cmap', cm.jet)
    
        # get layout
        n_values = Z.shape[0]
        nrows, ncols = axes.shape

        # iterate over axes and plot
        for i in xrange(nrows):
            for j in xrange(ncols):
                if i * ncols + j < n_values:
                    # call mpl_toolkit's plot_trisurf
                    axes[i,j].plot_trisurf(X, Y, triangles, Z[i * ncols + j],
                                           shade=True, cmap=cmap,
                                           linewidth=0., antialiased=False)

    def _plot_tripcolor(self, axes, X, Y, triangles, Z, **kwargs):
        '''
        Wrapper for the :py:meth:`pyplot.tripcolor` method.

        Parameters
        ----------

        X, Y : array_like
            1D arrays of the triangulation node coordinates

        triangles : array_like
            Connectivity array of the triangulation

        Z : array_like
            1D array of the values at the triangulation nodes
        '''

        # set default values
        shading = kwargs.get('shading', 'flat')
        cmap = kwargs.get('cmap', cm.jet)
        axis_off = kwargs.get('axis_off', True)
        
        # get layout
        n_values = Z.shape[0]
        nrows, ncols = axes.shape

        # iterate over axes and plot
        for i in xrange(nrows):
            for j in xrange(ncols):
                if i * ncols + j < n_values:
                    # call matplotlib.pyplot's tripcolor
                    axes[i,j].tripcolor(X, Y, triangles, Z[i * ncols + j],
                                        shading=shading, cmap=cmap)

                    if axis_off:
                        # don't show axis
                        axes[i,j].set_axis_off()

class QuadRuleVisualizer(Visualizer):
    """
    Visualizes the numerical integration scheme by plotting the
    quadrature points.
    """

    def _plot(self, quad_rule, *args, **kwargs):
        assert isinstance(quad_rule, pysofe.quadrature.gaussian.GaussQuadSimp)
        
        # get entity dimension for which to plot points
        dim = kwargs.get('d', quad_rule.dimension)

        if not dim in (1, 2):
            msg = "Visualization not supported for this dimension, yet ({})"
            raise ValueError(msg.format(dim))
        
        # get quadrature points
        points = quad_rule.points[dim]
        
        # check if mesh is given
        mesh = kwargs.get('mesh', None)

        if mesh is not None and isinstance(mesh, pysofe.meshes.mesh.Mesh):
            # is so, plot points on whole mesh
            V = MeshVisualizer()
            fig, axes = V.plot(mesh)

            # transfer local points to global ponts on the mesh
            points = np.vstack(mesh.ref_map.eval(points)).T

            axes.plot(points[0], points[1], 'r.')
            
        else:
            # if not, plot points on reference domain
            # set up figure and axes
            fig = plt.figure()
            axes = fig.add_subplot(111)

            if dim == 1:
                nodes = np.array([[0.], [1.]])
                cells = np.array([[1, 2]])
                axes.plot(nodes[:,0], np.zeros_like(nodes[:,0]))
                axes.plot(points[0], np.zeros_like(points[0]), 'r.')
            elif dim == 2:
                nodes = np.array([[0., 0.], [1., 0.], [0., 1.]])
                cells = np.array([[1, 2, 3]])
                axes.triplot(nodes[:,0], nodes[:,1], cells-1)
                axes.plot(points[0], points[1], 'r.')

            # zoom out to make outer faces visible
            xlim = list(axes.get_xlim()); ylim = list(axes.get_ylim())
            xlim[0] -= 0.1; xlim[1] += 0.1
            ylim[0] -= 0.1; ylim[1] += 0.1
            axes.set_xlim(xlim)
            axes.set_ylim(ylim)


        return fig, axes

class FESpaceVisualizer(Visualizer):
    """
    Visualizes the finite element space by plotting 
    its degrees of freedom.
    """

    def _plot(self, fe_space, *args, **kwargs):
        fontsize = kwargs.get('fontsize', 9)

        # first plot the mesh
        mesh = fe_space.mesh
        V = MeshVisualizer()
        fig, axes = V.plot(mesh)

        # get number of entities for each topological dimension
        n_entities = mesh.topology.n_entities
        dof_tuple = fe_space.element.dof_tuple
        n_dof_per_dim = np.asarray(n_entities) * dof_tuple

        dofs = np.arange(fe_space.n_dof) + 1
        entity_dofs = [zip(*(arr.reshape((dof_tuple[i], -1))))
                       for i, arr in
                       enumerate(np.split(dofs, n_dof_per_dim.cumsum()[:-1]))]

        # plot dofs for each topological dimension
        
        # nodes
        for i in xrange(mesh.nodes.shape[0]):
            if mesh.dimension == 1:
                axes.text(x=mesh.nodes[i,0], y=0., s=entity_dofs[0][i],
                          color='red', fontsize=fontsize)
            elif mesh.dimension == 2:
                axes.text(x=mesh.nodes[i,0], y=mesh.nodes[i,1],
                          s=entity_dofs[0][i],
                          color='red', fontsize=fontsize)
            else:
                raise NotImplementedError()

        # edges
        edges = mesh.edges
        bary = 0.5 * mesh.nodes[edges - 1,:].sum(axis=1)
        for i in xrange(edges.shape[0]):
            if mesh.dimension == 1:
                axes.text(x=bary[i,0], y=0, s=entity_dofs[1][i],
                          color='red', fontsize=fontsize)
            elif mesh.dimension == 2:
                axes.text(x=bary[i,0], y=bary[i,1], s=entity_dofs[1][i],
                          color='red', fontsize=fontsize)

        # elements
        if mesh.dimension > 1:
            cells = mesh.cells
            bary = mesh.nodes[cells - 1,:].sum(axis=1) / 3.
            for i in xrange(cells.shape[0]):
                axes.text(x=bary[i,0], y=bary[i,1], s=entity_dofs[2][i],
                          color='red', fontsize=fontsize)


                

        return fig, axes
