# pylint: disable=W0612, W0613
import numpy as np
import numexpr as ne
from .line_circle_intercepts import get_line_circle_intercepts

from galanyl.static_data import BBOX, DDS, KPC

NRADII = 1000


class RadialFluxAnalyzer(object):
    """An object that does a radial flux analyis on a list of radii.

    Currently samples happen at regular intervals in linear space.

    """
    def __init__(self):
        self.bbox = BBOX
        self.shape = DDS
        self.nx, self.ny, self.nz = DDS
        self.radii = (np.arange(NRADII, dtype='float64')+1)/NRADII*20*KPC
        self.fluxes = {}
        dx = (self.bbox[0][1] - self.bbox[0][0])/self.nx
        dy = (self.bbox[1][1] - self.bbox[1][0])/self.ny
        dz = (self.bbox[2][1] - self.bbox[2][0])/self.nz

        self.dx, self.dy, self.dz = dx, dy, dz

        self.xedges = (np.arange(self.nx+1) - self.nx/2)*dx
        self.yedges = (np.arange(self.ny+1) - self.ny/2)*dy

        self.xcenters = (np.arange(self.nx) - self.nx/2)*dx + dx/2
        self.ycenters = (np.arange(self.ny) - self.ny/2)*dy + dy/2

        xim, yim = np.meshgrid(self.xcenters, self.ycenters)

        # need to do some juggling to get it to the proper branch choice.
        # theta = 0 along positive x-axis and theta is defined on [0, 2*pi)
        self.pixel_angle = np.arctan2(yim, xim)
        self.pixel_angle = np.flipud(np.fliplr(self.pixel_angle)) + np.pi
        self.xim, self.yim = xim/dx + self.nx/2, yim/dy + self.ny/2
        self.rim = np.sqrt(xim**2 + yim**2)

    def get_flux(self, fluxing_field, radial_flow_field, r):
        """Find the flux across the outer surface of a cylinder of radius r

        Input parameters:
            fluxing_field - ndarray
                Flattened array containing the field we want to find the flux
                of
             radial_flow_field - ndarray
                Flattened array containing the radial component of a vector
                field.
             r - float
                Radius of the cylinder

        """
        xint, yint = self.get_xy_intercepts(r)

        inds = self.get_intersection_inds(xint, yint)

        dtheta1d = np.tile(self.get_dtheta(inds, xint, yint), self.nz)  # NOQA

        flat_inds3d = self.get_flat_3d_inds(inds)

        ff = np.take(fluxing_field, flat_inds3d)  # NOQA
        rf = np.take(radial_flow_field, flat_inds3d)  # NOQA
        dz = self.dz  # NOQA

        return ne.evaluate('ff * rf * r * dtheta1d * dz').sum()

    def get_fluxes(self, field_type, fluxing_field, radial_flow_field):
        """Finds the flux of a field for all radii"""
        self.fluxes[field_type] = np.zeros_like(self.radii)

        for i, r in enumerate(self.radii):
            self.fluxes[field_type][i] = \
                self.get_flux(fluxing_field, radial_flow_field, r)

        return self.radii, self.fluxes[field_type]

    def get_intersection_inds(self, xint, yint):
        """Get 2D indices of cells that touch coordinates

        Input parameters:
            xint - ndarray
                x coordinates of points.
            yint - ndarray
                y coordinates of points.

        """
        # The indices for which the intersection happens along an axis
        xpix = xint/self.dx + self.nx/2
        ypix = yint/self.dy + self.ny/2

        lookx = np.nonzero(np.in1d(xint, self.xedges))[0]
        looky = np.nonzero(np.in1d(yint, self.yedges))[0]

        xindsx = xpix[lookx]-1
        yindsx = np.floor(ypix[lookx])

        xindsy = np.floor(xpix[looky])
        yindsy = ypix[looky]-1

        yinds = np.rint(
            np.concatenate([yindsx, yindsx, yindsy, yindsy+1])).astype('int64')
        xinds = np.rint(
            np.concatenate([xindsx+1, xindsx, xindsy, xindsy])).astype('int64')

        ret = np.unique(
            np.ravel_multi_index((yinds, xinds), (self.nx, self.ny)))

        assert xint.shape == ret.shape

        return ret

    def get_flat_3d_inds(self, inds):
        """Generate flat indices into a 3D array based on 2D indices

        Assumes cylindrical symmetry.

        Since the radial flux problem has cylindrical symmetry, we need only
        calculate the indices for pixels the circle intersects with in 2D.  This
        generates 1D indices into a 3D array for the voxels the cylinder
        intersects.

        Input parameters:
            inds - flat index array
                2D pixel indices

        """
        inds2d = np.unravel_index(inds, (self.nx, self.ny))
        rep = np.tile(inds2d, (1, self.nz))
        inds3d = tuple(
            ind for ind in rep) + (np.tile(np.arange(self.nz), len(inds)),)

        return np.ravel_multi_index(inds3d, self.shape)

    def get_xy_intercepts(self, r):
        """Get the coordinates of all collisions between a circle and mesh

        Input parameters:
            r - float
                Radius of the circle
        """
        intercepts = []

        for x in self.xedges:
            x1 = x
            x2 = x
            y1 = self.yedges[0]
            y2 = self.yedges[-1]

            ints = get_line_circle_intercepts(x1, x2, y1, y2, r)
            if ints is not None:
                intercepts.extend(ints)

        for y in self.yedges:
            x1 = self.xedges[0]
            x2 = self.xedges[-1]
            y1 = y
            y2 = y

            ints = get_line_circle_intercepts(x1, x2, y1, y2, r)
            if ints is not None:
                intercepts.extend(ints)

        xint, yint = zip(*intercepts)

        return np.array(xint), np.array(yint)

    def get_dtheta(self, inds, xint, yint):
        """Obtain a list of angle increments given a list of points

        This calculates the increment in angle between a set of points whose
        coordinates are stored in xint and yint.

        Input parameters:
            inds - index array
                2D Indices into an image
            xint - float array
                x coordinates of points
            yint - float array
                y coordinates of points

        """

        theta_int = ne.evaluate('arctan2(yint, xint)')

        theta_int[theta_int < 0] += 2*np.pi

        theta_int = np.sort(theta_int)

        sort_args = np.argsort(self.pixel_angle.flat[inds])
        inv_sort_args = np.argsort(sort_args)

        dtheta = np.zeros_like(inds, dtype='float64')

        ti1 = theta_int
        ti2 = np.roll(theta_int, -1)

        dtheta = np.mod(ti2 - ti1, 2*np.pi)[inv_sort_args]

        return dtheta
