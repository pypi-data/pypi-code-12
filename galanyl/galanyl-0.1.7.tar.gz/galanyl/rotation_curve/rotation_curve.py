from __future__ import division

from galanyl.static_data import NBINS, UNIT_CONVERSIONS

from galanyl.utility_functions import \
    _get_profile_data, \
    _get_plot_limits, \
    _get_bins

from collections import OrderedDict

import numpy as np
import h5py
import os
from scipy import interpolate

EXCLUDED_NAMES = [
    'x_slice',
    'y_slice',
    'r_slice',
    'cost',
    'sint',
    'gpot_slice',
    'rotation_frequency_derivative',
]


class RotationCurveAnalyzer(object):
    """A class for calculating rotation curves for simulated galaxies

    Parameters:
      gpot_filename: string
        the filename of an hdf5 file containing the gravitational
        potential covering grid
      cg_filename: string
        the filename of th an hdf5 file containing the covering grids.

    Keyword Arguments:
      n_bins: integer
        The number of bins to use in the 1D approximation for the radial
        derivative of the rotation frequency

    """
    # Looking at this two months later, this is silly, but if it ain't broke...
    _xmin = np.float64(-6.31946875e+22)
    _xmax = -1*_xmin
    _ymin = _xmin
    _ymax = _xmax
    ngrid = 2048

    def __init__(self, gpot_filename=None, nbins=500):
        self.gpot_filename = gpot_filename
        self.nbins = nbins
        linrange = (np.arange(self.ngrid)/(self.ngrid-1) *
                    (self._xmax - self._xmin) + self._xmin)
        linrange = np.atleast_2d(linrange)
        self.profiles = OrderedDict()
        self.x_slice = np.zeros((self.ngrid, self.ngrid)) + linrange
        self.y_slice = np.zeros((self.ngrid, self.ngrid)) + linrange.T
        self.r_slice = np.sqrt(self.x_slice**2 + self.y_slice**2)
        self.cost = self.x_slice/self.r_slice
        self.sint = self.y_slice/self.r_slice
        self.omega_interpolator = None
        self.rotation_frequency = None
        self.kappa = None
        self.circular_velocity = None

        # Annular bin edges and centers
        self.bins = np.linspace(0, 1, self.nbins)*self.r_slice.max()
        self.bin_centers = self.bins[:-1] + (self.bins[1:] - self.bins[:-1])/2.

    def _cache_metadata(self):
        # Read and cache useful metadata right now
        with h5py.File(self.gpot_filename) as f_gpot:
            self.gpot_slice = f_gpot['gravitational_potential'][:, :, 127]

    def calculate_rotation_frequency(self):
        """Find the rotation frequency from the gravitational potential

        Returns the rotation frequency as a 2D array.

        """
        if not hasattr(self, 'gpot_slice'):
            self._cache_metadata()
        dx = self.x_slice[0, 1] - self.x_slice[0, 0]

        # x and y are flipped for mysterious reasons
        dphi_dy, dphi_dx = np.gradient(self.gpot_slice)/dx

        cost = self.x_slice/self.r_slice
        sint = self.y_slice/self.r_slice

        dphi_dr = dphi_dx*cost + dphi_dy*sint

        # Sometimes this happens but it should only be in a few cells
        neg_inds = np.where(dphi_dr.flat < 0)[0]

        dphi_dr.flat[neg_inds] = 0

        omega_measured = np.sqrt(dphi_dr/self.r_slice)

        # Count how many pixels fall into each radial bin
        hist, _ = np.histogram(self.r_slice, self.bins)

        # Get flat 1D indices into r_slice for each bin.
        inds = np.digitize(self.r_slice.flat, self.bins) - 1

        # Calculate mean omega at each radius.
        # Need to append [:-1] to get rid of counts outside bin range.
        omega_of_r = np.bincount(inds, weights=omega_measured.flat)[:-1]/hist

        # Calculate standard deviation of the mean omega for each bin.
        omega2_of_r = np.bincount(
            inds, weights=omega_measured.flat[:]**2)[:-1]/hist
        omega_of_r_std = np.sqrt(omega2_of_r - omega_of_r**2)

        # Calculate radial derivative of the rotation frequency using a spline
        # interpolator
        omega = np.zeros(self.r_slice.shape)
        omega_deriv = np.zeros(self.r_slice.shape)

        self.omega_interpolator = interpolate.splrep(
            self.bin_centers, omega_of_r, k=5, w=1/omega_of_r_std)

        omega.flat[:] = interpolate.splev(
            self.r_slice.flat, self.omega_interpolator)
        self.rotation_frequency = omega

        omega_deriv.flat[:] = interpolate.splev(
            self.r_slice.flat, self.omega_interpolator, der=1)
        self.rotation_frequency_derivative = omega_deriv

        return self.rotation_frequency

    def calculate_circular_velocity(self):
        """Calculate the circular velocity"""
        self.circular_velocity = self.r_slice*self.rotation_frequency
        return self.circular_velocity

    def calculate_epicyclic_frequency(self):
        """Calcualte the epicyclic frequency from the rotation rate

        Returns the epicyclic frequency as a 2D array.
        """
        if self.rotation_frequency is None:
            self.calculate_rotation_frequency()

        domega_dr = np.zeros(self.r_slice.shape)

        domega_dr.flat[:] = interpolate.splev(
            self.r_slice.flat, self.omega_interpolator, der=1)

        # Finally, calculate epicyclic frequency.
        self.kappa = np.sqrt(2*self.rotation_frequency/self.r_slice*(
            2*self.r_slice*self.rotation_frequency + self.r_slice**2*domega_dr))

        return self.kappa

    def write_rotation_curve(self, filename, omega, v_c, kappa):
        """Write output data to an hdf5 file

        This will overwrite the file if it already exists
        """
        if os.path.isfile(filename):
            os.remove(filename)

        with h5py.File(filename) as f:
            f.create_dataset('omega', data=omega, compression='lzf')
            f.create_dataset('v_c', data=v_c, compression='lzf')
            f.create_dataset('kappa', data=kappa, compression='lzf')
            f.create_dataset('x_slice', data=self.x_slice, compression='lzf')
            f.create_dataset('y_slice', data=self.y_slice, compression='lzf')
            f.create_dataset('r_slice', data=self.r_slice, compression='lzf')

    def __setattr__(self, name, value):
        if isinstance(value, np.ndarray):
            if len(value.shape) == 2 and name not in EXCLUDED_NAMES:
                item = ('rot', name)
                if name in self.profiles:
                    if len(self.profiles[name]) != NBINS:
                        del self.profiles[name]
                if name not in self.profiles:
                    xlim, ylim = _get_plot_limits(item, value)
                    plot_bins, bins = _get_bins(xlim, ylim)
                    r_slice = self.r_slice/UNIT_CONVERSIONS['rot', 'radius']
                    kappa = self.kappa
                    prof, _ = _get_profile_data(
                        item, self, value, kappa, r_slice, bins)
                    self.profiles[name] = prof
        super(RotationCurveAnalyzer, self).__setattr__(name, value)
