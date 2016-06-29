# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------------
#  Copyright (c) 2016, Robert Whitinger <cva_account@wmkt.com>
#
#  Distributed under the terms of the LGPL license either version 2.1 or
#  (at your option) any later version.
#
#  The full license is in the file LICENSE.txt, distributed with this software,
#  and is also available at <http://www.gnu.org/licenses/>
#-----------------------------------------------------------------------------
"""
cva.view

A matplotlib wrapper for creating graphical representations of cva solutions.
"""

# system libraries:
from __future__ import division
import numpy as np
import matplotlib as mpl
#matplotlib.use('qt4agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
import matplotlib.cbook
warnings.filterwarnings("ignore", category=matplotlib.cbook.mplDeprecation)
import itertools

# project libraries:
import cva
from cva import model

initialized = False

# here we store this module's parameter set and make it accessible
# initialize default parameters if any
_parms = {
    }
def set_parm(parm_name, parm_value):
    """
    cva.view.set_parm(parm_name, parm_value)
    """
    _parms[parm_name] = parm_value

def get_parm(parm_name):
    """
    parm_value = cva.view.get_parm(parm_name)
    """
    return _parms[parm_name]

def list_parms():
    """
    keys = cva.view.list_parms()
    """
    keys = _parms.keys()
    return keys

def _init(title="CVA Solution", **kwargs):
    # To display an n-dimensional surface using 3-dimensional views,
    # we need to show combinations of n taken n-3 at a time.  For
    # example a 3-d object is represented in one 3-d view, a 4-d
    # object in four 3-d views, a 5-d object in 10 3-d views, etc.
    #
    global G, P, ndim, nviews, surface_index, parm_index, surface_axes, parm_axes
    global fig, ax

    G = cva.solve.get_parm('G')
    P = cva.solve.get_parm('steps')
    ndim = cva.solve.get_parm('ndim')

#    plt.ion()
    plt.rc('text', usetex=True)
    mpl.rcParams['legend.fontsize'] = 20

    # Calculate the number of views needed
    surface_axes = [x for x in range(ndim)]
    surface_index = list(itertools.combinations(surface_axes, ndim-3))
    parm_axes = [x for x in range(ndim-1)]
    if ndim == 3:
        nsurfaceviews = 1
        nparmviews = 1
        parm_index = [(1)]
    else:

        parm_index = list(itertools.combinations(parm_axes, ndim-4))
        nsurfaceviews = len(surface_index)
        nparmviews = len(parm_index)

    nviews = nsurfaceviews + nparmviews

    fig = plt.figure(figsize=(12, int((6*nviews+1)/2)), dpi=72)
    fig.suptitle(title)
    ax = [x for x in range(nviews)]
    if ndim == 3:
        ax[0] = fig.add_subplot(1, 2, 1, projection='3d')
        ax[1] = fig.add_subplot(1, 2, 2)
        ax[1].set_xlim(0.0, 1.0)
        ax[1].set_ylim(0.0, 1.0)
        ax[1].grid(True)
    else:
        for i in range(len(ax)):
            ax[i] = fig.add_subplot(int((len(ax)+1)/2), 2, i+1, projection='3d')
            if i >= nsurfaceviews:
                ax[i].set_xlim(0, 1)
                ax[i].set_ylim(0, 1)
                ax[i].set_zlim(0, 1)
    return


def _draw_manifold(title='Surface', **kwargs):
    # view a hypersurface in n-dimensions
    #
    N = 33
    decimation = 8
    s = np.zeros((N, ndim-1))
    grid = np.linspace(0.0, 1.0, N)
    colors = ["b", "g", "r", "m"]

    for view in range(len(surface_index)):
        axis = [axis for axis in surface_axes if axis not in surface_index[view]]
        if ndim == 3:
            decimation = 2
            if title == False:
                title = "Surface"
            ax[view].set_title(title)
            ax[view].set_xlabel(r"$x$")
            ax[view].set_ylabel(r"$y$")
            ax[view].set_zlabel(r"$z$")
        else:
            if title == False:
                title = "Hypersurface"
            strng = "x_%d" % (surface_index[view][0])
            for i in range(1, len(surface_index[view])):
                str += ", x_%d" % (surface_index[view][i])
            ax[view].set_title(r"%s (slice at $%s=0$)" % (title, strng))
            ax[view].set_xlabel(r"$x_%d$" % (axis[0]))
            ax[view].set_ylabel(r"$x_%d$" % (axis[1]))
            ax[view].set_zlabel(r"$x_%d$" % (axis[2]))

        # for this view we draw each axis that is not set to zero
        for i in parm_axes:
            # for each parameter axis, i, we fix the remaining axes on a grid
            # and then plot the primary axis
            span = [span for span in parm_axes if span != i]
            # get a list of all grid intersections for the fixed parameters
            points = list(itertools.product(grid[::decimation], repeat=len(span)))
            # for each grid point, we span the primary parameter and plot the resulting line
            for point in points:
                for j in range(N):
                    s[j, i] = grid[j]
                    for k in range(len(span)):
                        s[j, span[k]] = point[k]
                # we have a line in s ready to plot
                x = G(s)
                ax[view].plot(x[:, axis[0]], x[:, axis[1]], x[:, axis[2]], "-", color=colors[i%len(colors)], linewidth=1, linestyle="-")
            try:
                ax[view].set_xlim(cva.view.get_parm('xyzlim'))
                ax[view].set_ylim(cva.view.get_parm('xyzlim'))
                ax[view].set_zlim(cva.view.get_parm('xyzlim'))
            except:
                pass
            try:
                ax[view].set_xlim(cva.view.get_parm('xlim'))
            except:
                pass
            try:
                ax[view].set_ylim(cva.view.get_parm('ylim'))
            except:
                pass
            try:
                ax[view].set_zlim(cva.view.get_parm('zlim'))
            except:
                pass

    for parm_view in range(len(parm_index)):
        view = parm_view+len(surface_index)
        if ndim == 3:
            ax[1].set_title("uv plane")
            ax[1].set_xlabel("u")
            ax[1].set_ylabel("v")
        if ndim == 4:
            ax[view].set_title("uvw view")
            ax[view].set_xlabel("u")
            ax[view].set_ylabel("v")
            ax[view].set_zlabel("w")
        elif ndim > 4:
            axis = [axis for axis in parm_axes if axis not in parm_index[parm_view]]
            str = "u_%d" % (parm_index[parm_view][0])
            for i in range(1, len(parm_index[parm_view])):
                str += ", u_%d" % (parm_index[parm_view][i])
            title = "Phase Space View"
            ax[view].set_title(r"%s (slice at $%s=0$)" % (title, str))
            ax[view].set_xlabel(r"$u_%d$" % (axis[0]))
            ax[view].set_ylabel(r"$u_%d$" % (axis[1]))
            ax[view].set_zlabel(r"$u_%d$" % (axis[2]))
            ax[view].set_zlim(0, 1)
    global initialized
    initialized = True
    return

def _draw_path(s, **kwargs):
    for view in range(len(surface_index)):
        axis = [axis for axis in surface_axes if axis not in surface_index[view]]

        # for this view we draw the axes that are not set to zero
        x = G(s)
        if 'color' not in kwargs.keys():
            kwargs['color'] = 'k'
#                if P <= 4:
#                    kwargs['c'] = '-ko'
#                else:
#                    kwargs['mkr'] = '-k'
        if 'linewidth' not in kwargs.keys():
            kwargs['linewidth'] = 2
        ax[view].plot(x[:, axis[0]], x[:, axis[1]], x[:, axis[2]], **kwargs)
        ax[view].scatter3D(x[:, axis[0]][0], x[:, axis[1]][0], x[:, axis[2]][0], 'o', c='g', s=50, edgecolor='g')    # starting point
        ax[view].scatter3D(x[:, axis[0]][-1], x[:, axis[1]][-1], x[:, axis[2]][-1], 'o', c='r', s=50, edgecolor='r')  # ending point
    for parm_view in range(len(parm_index)):
        view = parm_view+len(surface_index)
        if ndim == 3:
            border = 0.01
            umax = np.max(s[:, 0])
            umax = umax + border if umax > 1.0 + border else 1.0 + border
            umin = np.min(s[:, 0])
            umin = umin - border if umin < 0.0 - border else 0.0 - border
            vmax = np.max(s[:, 1])
            vmax = vmax + border if vmax > 1.0 + border else 1.0 + border
            vmin = np.min(s[:, 1])
            vmin = vmin - border if vmin < 0.0 - border else 0.0 - border
            ax[view].set_xlim(umin, umax)
            ax[view].set_ylim(vmin, vmax)
            ax[view].plot(s[:, 0], s[:, 1], **kwargs)
            ax[view].plot(s[0, 0], s[0, 1], c='g', marker='o')    # starting point
            ax[view].plot(s[-1, 0], s[-1, 1], c='r', marker='o')  # ending point
            ax[view].grid(True)
        else:

            axis = [axis for axis in parm_axes if axis not in parm_index[parm_view]]
            ax[view].plot(s[:, axis[0]], s[:, axis[1]], s[:, axis[2]], **kwargs)
            ax[view].scatter3D(s[0][axis[0]], s[0][axis[1]], s[0][axis[2]], 'o', c='g', s=50, edgecolor='g')    # starting point
            ax[view].scatter3D(s[-1][axis[0]], s[-1][axis[1]], s[-1][axis[2]], 'o', c='r', s=50, edgecolor='r')  # ending point
    return

def draw_hold(s, title='CVA Solution', **kwargs):
    """
    cva.view.draw_hold(s, title='CVA Solution', **kwargs)

    The primary entry point cva.view.draw() is split into two parts,
    cva.view.draw_hold() and cva.view.draw_show().  This split makes
    it possible to construct graphics with multiple paths by placing
    one or more calls to cva.view.draw_hold() followed by a single call
    to cva.view.draw_show().

    Parameters
    ----------
    s : array_like
        This parameter contains a parameter space sequence that defines
        a path to be drawn.
    title : string, optional
        Specify the graphic's top title
    **kwargs : dictionary, optional
        This passthrough parameter allows some matplotlib options to be
        overridden.  See the matplotlib documentation for usage information.

    Returns
    -------
    nothing

    Notes
    -----

    Examples
    --------
    import cva
    sa = (0.4,0.2)
    sb = (0.5,0.5)
    cva.solve.select(cva.model.sphere,cva.metric.distance)
    path = cva.solve.run(sa,sb)
    cva.view.draw_hold(path)
    sa = (0.6,0.2)
    sb = (0.5,0.5)
    path = cva.solve.run(sa,sb)
    cva.view.draw_hold(path)
    cva.view.draw_show()

    In this example, two minimal paths are plotted on a single graphic.
    """
    if not initialized:
        _init(title)
        _draw_manifold()
    _draw_path(s, **kwargs)

def draw_show(image_file=False, **kwargs):
    """
    cva.view.draw_show(image_file=False, **kwargs)

    The primary entry point cva.view.draw() is split into two parts,
    cva.view.draw_hold() and cva.view.draw_show().  This split makes
    it possible to construct graphics with multiple paths by placing
    one or more calls to cva.view.draw_hold() followed by a single call
    to cva.view.draw_show().

    Parameters
    ----------
    image_file : string (optional)
        This parameter contains the file name where an image is to be
        saved.  The extension field of this name is checked to determine the
        format of the saved image.
    **kwargs : dictionary, optional
        This passthrough parameter allows some matplotlib options to be
        overridden.  See the matplotlib documentation for usage information.

    Returns
    -------
    nothing

    Notes
    -----
    See cva.view.draw_hold for example usage.
    """
    initialized = False
    plt.grid(True)
    if image_file:
        fig.tight_layout()
        plt.savefig(image_file)
    else:
        plt.show()
    return

def draw(s, title='CVA Solution', image_file=False, **kwargs):
    """
    cva.view.draw(s, title='CVA Solution', image_file=False, **kwargs)

    This function is a matplotlib wrapper that can be used to display
    and save graphical representations of cva solutions.

    Parameters
    ----------
    s : array_like
        This parameter contains a parameter space sequence that defines
        a path to be drawn.
    title : string, optional
        Specify the graphic's top title
    image_file : string, optional
        In the default, a graphic is displayed.  An image can also be
        directed to a file by giving its name.
        Example: image_file="mygraphic.pdf"
    **kwargs : dictionary, optional
        This passthrough parameter allows some matplotlib options to be
        overridden.  See the matplotlib documentation for usage information.

    Returns
    -------
    nothing

    Notes
    -----
    This is the primary entry point for the cva.view module.

    Examples
    --------
    import cva
    sa = (0.4,0.2)
    sb = (0.6,0.6)
    cva.solve.select(cva.model.sphere,cva.metric.distance)
    path = cva.solve.run(sa,sb)
    cva.view.draw(path)

    In this example, the parameterization points sa and sb are mapped into
    their corresponding points on the surface of a unit sphere, and the
    resulting minimal curve is displayed.
    """
    draw_hold(s, title, **kwargs)
    draw_show(image_file)
    return

if __name__ == "__main__":

    print "running cva/view.py"


