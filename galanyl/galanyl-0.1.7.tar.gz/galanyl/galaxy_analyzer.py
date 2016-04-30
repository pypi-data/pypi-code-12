# pylint: disable=W0612, W0613
from __future__ import division

import glob
import h5py
import inspect
import matplotlib
import time
import weakref

# this is a hack, figure out how to do this using MPL OO interface.
from matplotlib import rc
rc('font', family='serif', serif='cm10', size=14)
rc('text', usetex=True)
rc('axes', labelsize=14)
rc('axes', titlesize=14)
rc('xtick', labelsize=14)
rc('ytick', labelsize=14)
import numexpr as ne
import numpy as np
import os

from collections import OrderedDict
from functools import wraps

from matplotlib import \
    pyplot as plt

from galanyl.radial_flux_analyzer import \
    RadialFluxAnalyzer
from galanyl.rotation_curve import \
    RotationCurveAnalyzer

from galanyl.cython_extensions import \
    particle_dispersion, \
    windowed_sum, \
    cic_particle_density, \
    scale_height

from galanyl.static_data import \
    G, \
    PI, \
    DDS, \
    BBOX, \
    DX, \
    PC, \
    MAJOR_TICKMARK_PROPERTIES, \
    MINOR_TICKMARK_PROPERTIES, \
    EXTENT, \
    NBINS, \
    LABELS, \
    IMAGE_COLORBAR_LIMITS, \
    PROFILE_AXIS_LIMITS, \
    PROFILE_COLORBAR_LIMITS, \
    UNIT_CONVERSIONS, \
    COLORMAPS, \
    EXCLUDED_FIELDS, \
    CONTAINER_NAMES, \
    MSUNPERPC2, \
    HYDROGEN_MASS_FRACTION, \
    GYR, \
    PLOT_SLICE

from galanyl.utility_functions import \
    _get_profile_data, \
    _get_plot_limits, \
    _get_bins


def decade_counter(vmin, vmax, step=2):
    ret = np.array([])
    min_decade = np.floor(np.log10(vmin))
    max_decade = np.ceil(np.log10(vmax))
    for decade in np.arange(min_decade, max_decade):
        start = 10**decade
        end = 10**(decade+1)
        if start < vmin:
            start = vmin + (10**decade - vmin % 10**decade)
        if end > vmax:
            end = vmax
        ret = np.append(ret, np.arange(start, end, step*10**decade))
    return ret


def ensure_directory(base_path, dirname):
    path = os.path.sep.join([base_path, dirname])
    if os.path.exists(path):
        return path
    try:
        os.mkdir(path)
    except OSError:
        split_base = base_path.split(os.path.sep)
        if len(split_base) == 1:
            new_base = './'
            new_dirname = split_base[0]
        elif len(split_base) == 2:
            new_base = split_base[0]
            new_dirname = split_base[1]
        else:
            new_base = os.path.sep.join(split_base[:-1])
            new_dirname = split_base[-1]
        ensure_directory(new_base, new_dirname)
        try:
            os.mkdir(path)
        except OSError:
            if not os.path.exists(path):
                raise
    return path


def create_h5_file(directory, data, dataset_name):
    output_name = os.path.sep.join([directory, dataset_name+'.h5'])
    if os.path.exists(output_name):
        return output_name
    with h5py.File(output_name) as f:
        f.create_dataset(dataset_name, data=data, compression='lzf')
    return output_name


def find_components(path):
    component_directories = sorted(glob.glob(os.path.sep.join([path, '*'])))
    component_list = [os.path.split(comp)[1] for comp in component_directories]
    return component_directories, component_list


def move_component_to_top(component_list, component_directories, search_string):
    index = component_list.index(search_string)

    component = component_list.pop(index)
    component_directory = component_directories.pop(index)

    component_list.insert(0, component)
    component_directories.insert(0, component_directory)


def log_call(func):
    @wraps(func)
    def with_logging(*args, **kwargs):
        if args[0].log_calls is True:
            t0 = time.time()
            nargs = len(args)
            msg = args[0].name + ": " + func.__name__
            if nargs > 1:
                msg = msg + " for " + args[1]
            if nargs > 2:
                msg = msg + " " + args[2]
            # ugly no-good hack
            depth = len(inspect.stack()) - 2
            print ("  "*depth + "going into " + msg)
        ret = func(*args, **kwargs)
        if args[0].log_calls is False:
            return ret
        print ("  "*depth + "leaving " + msg +
               " after %.3f seconds" % (time.time() - t0))
        return ret
    return with_logging


def _plot_image(data, item, fig, ax, cax=None, use_axes_labels=True):
    """Return a matplotlib figure containing an imshow plot

    This should only be called internally.
    """

    cmap = COLORMAPS[item]
    try:
        vmin, vmax, linthresh = IMAGE_COLORBAR_LIMITS[item]
    except ValueError:
        vmin, vmax = IMAGE_COLORBAR_LIMITS[item]

    use_default_formatter = False

    if vmin > 0 and vmin is not None:
        nn = matplotlib.colors.LogNorm()
        tick_locations = None
    elif vmin == 0:
        nn = matplotlib.colors.Normalize()
        tick_locations = None
        use_default_formatter = True
    else:
        nn = matplotlib.colors.SymLogNorm(linthresh)
        maxlog = int(np.ceil(np.log10(vmax)))
        minlog = int(np.ceil(np.log10(-vmin)))
        linthresh = int(np.log10(linthresh))
        takespread = lambda m, n: [i*n//m + n//(2*m) for i in range(m)]
        brange = xrange(minlog, linthresh-1, -1)
        if len(brange) > 4:
            brange = [brange[i] for i in takespread(2, len(brange))]
        trange = xrange(linthresh, maxlog+1)
        if len(trange) > 4:
            trange = [trange[i] for i in takespread(2, len(trange))]
        tick_locations = ([-(10**x) for x in brange] +
                          [0.0, ] +
                          [(10**x) for x in trange])
    sl = slice(PLOT_SLICE[0], PLOT_SLICE[1])
    im = ax.imshow(data[sl, sl], origin='lower', cmap=cmap, norm=nn,
                   extent=EXTENT, vmin=vmin, vmax=vmax, interpolation='nearest')

    def image_exponentiate(x, pos):
        if x == 0:
            return '$0$'
        else:
            ret = '$10^{{{:n}}}$'.format(np.log10(np.abs(x)))
            if x < 0:
                return '-'+ret
            else:
                return ret

    if use_default_formatter is False:
        formatter = matplotlib.ticker.FuncFormatter(image_exponentiate)
    else:
        formatter = None
    cb = fig.colorbar(im, ticks=tick_locations, cax=cax, format=formatter)
    cb.set_label(LABELS[item])
    if vmin > 0:
        cb.ax.tick_params(**MAJOR_TICKMARK_PROPERTIES)
        cb.ax.tick_params(**MINOR_TICKMARK_PROPERTIES)
        cb.ax.minorticks_on()
        minorticks = im.norm(decade_counter(vmin, vmax))
        cb.ax.yaxis.set_ticks(minorticks, minor=True)

    if use_axes_labels is True:
        ax.set_xlabel(r'$\rm{x}\ \ (\rm{kpc})$')
        ax.set_ylabel(r'$\rm{y}\ \ (\rm{kpc})$')
        ax.tick_params(**MAJOR_TICKMARK_PROPERTIES)
        ax.tick_params(**MINOR_TICKMARK_PROPERTIES)
    else:
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_xticklabels([])
        ax.set_yticklabels([])

    ax.minorticks_on()


def _plot_radial_profile(data, item, container, r_slice, kappa, fig, ax):
    """Return a matplotlib figure containing a radial profile plot

    This should only be called internally.
    """
    xlim, ylim = _get_plot_limits(item, data)
    plot_bins, bins = _get_bins(xlim, ylim)
    r_slice = r_slice/UNIT_CONVERSIONS['rot', 'radius']
    prof, weight = _get_profile_data(item, container, data, kappa, r_slice, bins)

    whfinite = np.isfinite(data)

    if not np.any(whfinite):
        hist = np.zeros((NBINS-1, NBINS-1))
    else:
        hist, _, _ = np.histogram2d(r_slice[whfinite], data[whfinite], bins,
                                    normed=True, weights=weight[whfinite])

    x_bin_center = bins[0][:-1] + (bins[0][:-1] - bins[0][1:])/2

    zlim = PROFILE_COLORBAR_LIMITS[item]

    if item[0] != 'rot':
        formatter = matplotlib.ticker.LogFormatterMathtext(labelOnlyBase=False)
        im = ax.pcolormesh(plot_bins[0], plot_bins[1], hist.T, vmin=zlim[0],
                           vmax=zlim[1], norm=matplotlib.colors.LogNorm(),
                           cmap='GnBu')
        cb = fig.colorbar(im, pad=0, format=formatter)
        cb.set_label("Probability Density")
        cb.ax.tick_params(**MAJOR_TICKMARK_PROPERTIES)
        cb.ax.tick_params(**MINOR_TICKMARK_PROPERTIES)
        cb.ax.minorticks_on()

    prof[prof == 0] = np.nan
    if np.any(np.isfinite(prof)):
        if ylim[0] > 0:
            ax.plot(x_bin_center, np.log10(prof), 'k--')
        else:
            ax.plot(x_bin_center, prof, 'k--')

    def exponentiate_integer(x, pos):
        return '$10^{{{:n}}}$'.format(x)

    if ylim[0] > 0:
        ax.set_aspect(abs((bins[0][1] - bins[0][0]) /
                          (np.log10(bins[1][1]) - np.log10(bins[1][0]))))
        ax.axis([xlim[0], xlim[1], np.log10(ylim[0]), np.log10(ylim[1])])
        ax.yaxis.set_major_locator(matplotlib.ticker.MultipleLocator(1.0))
        ax.yaxis.set_minor_locator(matplotlib.ticker.MultipleLocator(0.25))
        formatter = matplotlib.ticker.FuncFormatter(exponentiate_integer)
    else:
        formatter = matplotlib.ticker.ScalarFormatter(useMathText=True)
        formatter.set_powerlimits((-2, 3))
        ax.set_aspect(
            abs((bins[0][1] - bins[0][0]) / (bins[1][1] - bins[1][0])))
        ax.axis([xlim[0], xlim[1], ylim[0], ylim[1]])

    ax.yaxis.set_major_formatter(formatter)
    ax.set_xlabel(LABELS['rot', 'radius'])
    ax.set_ylabel(LABELS[item])
    ax.minorticks_on()
    ax.tick_params(**MAJOR_TICKMARK_PROPERTIES)
    ax.tick_params(**MINOR_TICKMARK_PROPERTIES)


def _plot_radial_mass_flux(radii, fluxes, item, container, fig, ax):
    xlim = (0, 20)
    ylim = PROFILE_AXIS_LIMITS[item]
    ax.plot(radii, fluxes, 'k')
    ax.set_aspect(abs((radii[-1] - radii[0])/(ylim[1] - ylim[0])))
    ax.set_xlabel(LABELS['rot', 'radius'])
    ax.set_ylabel(LABELS[item])
    ax.minorticks_on()
    ax.axis([xlim[0], xlim[1], ylim[0], ylim[1]])
    ax.tick_params(**MAJOR_TICKMARK_PROPERTIES)
    ax.tick_params(**MINOR_TICKMARK_PROPERTIES)

    return fig


def _calculate_projected_field(field):
    return np.sum(field, axis=-1, dtype='float64')*DX


def _calculate_weighted_projection(field, density, surface_density):
    proj = ne.evaluate('density*field')
    return np.sum(proj, axis=-1, dtype='float64')*DX / surface_density


def _sanitize_item(field_type, item):
    if item is None:
        if isinstance(field_type, tuple):
            return field_type
        else:
            raise RuntimeError("Field tuple %s unrecognized" % field_type)
    else:
        return (field_type, item)


def _get_velocity_dispersion_components(density, v):
    ret = []
    rhoconvolve = windowed_sum(density, 5)  # NOQA
    for direction in 'xyz':
        vd = v[direction]  # NOQA
        velconvolve = windowed_sum(ne.evaluate('density*vd'), 5)  # NOQA
        vel2convolve = windowed_sum(ne.evaluate('density*vd**2'), 5)  # NOQA
        ret += [ne.evaluate(
            'where(rhoconvolve != 0,'
            'sqrt(rhoconvolve*vel2convolve - velconvolve**2)/rhoconvolve,0)')]
        del velconvolve
        del vel2convolve
    return ret


def _get_projected_velocity_dispersion(density, sigma_x, sigma_y, sigma_z,
                                       surface_density):
    ret = []
    kinetic_energy = {
        'total': ne.evaluate(
            'density*(sigma_x**2 + sigma_y**2 + sigma_z**2)'),
        'vertical': ne.evaluate('density*sigma_z**2'),
        'disk': ne.evaluate('density*(sigma_x**2 + sigma_y**2)'),
    }

    for field_type in ['total', 'vertical', 'disk']:
        # Return the mean velocity dispersion along the line of sight
        Sigma_turb = np.sum(kinetic_energy[field_type]*DX, axis=-1,
                            dtype='float64')
        whnzero = np.where(surface_density != 0)
        ret += [np.zeros(Sigma_turb.shape)]
        ret[-1][whnzero] = np.sqrt(Sigma_turb[whnzero]/surface_density[whnzero])

    return ret


class PlotManager(object):
    """A class that conveniently displays plots in a notebook"""
    def __init__(self, output_directory, basename, plotting_function, args,
                 item, plot_type):
        self.plot_output_directory = \
            os.path.sep.join([output_directory, "plots"])+os.path.sep
        if not os.path.exists(self.plot_output_directory):
            try:
                os.makedirs(self.plot_output_directory)
            except OSError:
                if not os.path.exists(self.plot_output_directory):
                    raise

        flnm = self.plot_output_directory + "{}_{}_{}_{}.png".format(
            basename, plot_type, item[0], item[1].replace('_', '-'))
        self.plot_filename = flnm
        if os.path.exists(flnm):
            os.remove(flnm)
        fig, ax = plt.subplots()
        args += (fig, ax)
        plotting_function(*args)
        try:
            fig.savefig(flnm, bbox_inches='tight', dpi=175)
            plt.close(fig)
        except RuntimeError:
            # sometimes LaTeX dies myseriously, so we ignore it
            pass

        return

    def display(self):
        from IPython.display import display
        display(self)

    def _ipython_display_(self):
        from IPython.display import display, Image
        display(Image(self.plot_filename, embed=True))


class FieldContainer(object):
    def __init__(self, cg_filenames, component_name, rot):
        if component_name == 'star_formation':
            cg_name = 'sfr'
        else:
            cg_name = component_name
        self.field_type = cg_name
        try:
            self.cg_filename = cg_filenames[self.field_type]
        except KeyError:
            self.cg_filename = None
        self.component_name = component_name
        self.rot = weakref.proxy(rot)
        self.profiles = OrderedDict()
        self.surface_density = None
        if self.field_type in ('stars', 'gas'):
            self.toomre_q = None
        if self.field_type == 'gas':
            self.sound_speed = None
            self.h2_fraction = None
            self.alpha = None
            self.total_toomre_q = None
        if self.field_type == 'gas' or 'stars' in self.field_type:
            self.velocity_dispersion = None
            self.velocity_dispersion_disk = None
            self.velocity_dispersion_vertical = None
            self.velocity_dispersion_ratio = None
            self.c_eff = None
            self.scale_height = None
            self.mass_flux_density = None
        if self.field_type == 'sfr':
            self.total = None
            self.fake_total = None
            self.fake_surface_density = None
            self.depletion_time = None
        if 'stars' in self.field_type:
            self.vx = None
            self.vy = None
            self.vz = None
            self.xind = None
            self.yind = None

    def __setattr__(self, name, value):
        if isinstance(value, np.ndarray):
            if len(value.shape) == 2:
                item = (self.component_name, name)
                if name in self.profiles:
                    if len(self.profiles[name]) != NBINS:
                        del self.profiles[name]
                if name not in self.profiles and item not in EXCLUDED_FIELDS:
                    xlim, ylim = _get_plot_limits(item, value)
                    plot_bins, bins = _get_bins(xlim, ylim)
                    r_slice = self.rot.r_slice/UNIT_CONVERSIONS['rot', 'radius']
                    kappa = self.rot.kappa
                    prof, _ = _get_profile_data(
                        item, self, value, kappa, r_slice, bins)
                    self.profiles[name] = prof
        super(FieldContainer, self).__setattr__(name, value)


class GalaxyAnalyzer(object):
    """Analyzes various quantities for galaxy simulations.

    Parameters:

      cg_filenames: dict
        Dictionary mapping component names to covering grid file paths.

    >>> from pprint import pprint
    >>> pprint(dset_cgs['DD0000'])
    {'formed_stars': 'DD0000_formed-stars_covering_grid.h5',
     'gas': 'DD0000_gas_covering_grid.h5',
     'gpot': 'DD0000_gpot_covering_grid.h5',
     'sfr': 'DD0000_sfr_covering_grid.h5',
     'stars': 'DD0000_stars_covering_grid.h5',
     'young_stars': 'DD0000_young-stars_covering_grid.h5',
     'dark_matter': 'DD0000_dark-matter_covering_grid.h5'}

    """
    fields = sorted(LABELS.keys())
    fields.remove(('rot', 'radius'))

    def __init__(self, cg_filenames, log_calls=True):
        qfilename = None
        if cg_filenames is not None:
            gas_path, gas_name = os.path.split(cg_filenames['gas'])
            self.output_directory = os.path.split(gas_path)[0]
            qfilename = os.path.sep.join(
                [self.output_directory, 'toomre_q',
                 gas_name[:6] + '_toomre'])
            self.dset_name = gas_name[:6]
        else:
            base_path = self.qfilename.rsplit('toomre_q')[0].rstrip(os.path.sep)
            cg_filenames = {}
            for container_name in CONTAINER_NAMES:
                if container_name == 'star_formation':
                    container_name = 'sfr'
                fixed_name = container_name.replace('_', '-')
                cg_name = '%s_%s_covering_grid.h5' % (self.name, fixed_name)
                path = os.path.sep.join([base_path, container_name, cg_name])
                if os.path.exists(path):
                    cg_filenames[container_name] = path
                else:
                    cg_filenames[container_name] = None
            qfilename = self.qfilename
        self.cg_filenames = cg_filenames
        self.rot = RotationCurveAnalyzer(cg_filenames['gpot'])
        for container_name in CONTAINER_NAMES:
            container = FieldContainer(
                cg_filenames, container_name, self.rot)
            setattr(self, container_name, container)
        self.qfilename = qfilename
        self.flux = RadialFluxAnalyzer()
        self.log_calls = log_calls

    @property
    def name(self):
        return self.qfilename[-13:-7]

    @classmethod
    def from_hdf5_file(cls, h5_path, log_calls=True):
        """Create a GalaxyAnalyzer object from cached hdf5 data

        Parameters:
          h5_path: string
             Path to an directory containing cached hdf5 Toomre Q data. Must have
             the same format as directory created by the save_to_hdf5 function.
        """
        obj = super(GalaxyAnalyzer, cls).__new__(cls)
        obj.qfilename = h5_path.rstrip(os.path.sep)
        obj.__init__(None, log_calls=log_calls)
        obj.output_directory = h5_path[:-23]
        obj.dset_name = h5_path[-13:-7]
        if not os.path.isdir(h5_path):
            raise RuntimeError
        component_directories, component_list = find_components(h5_path)
        if 'rot' in component_list:
            move_component_to_top(component_list, component_directories, 'rot')
        for component, directory in zip(component_list, component_directories):
            field_directories, field_list = find_components(directory)
            # Rather than sorting by which fields depend on each other, simply
            # always deal with surface density and velocity dispersion first
            for field in ['surface_density', 'velocity_dispersion']:
                if field in field_list:
                    move_component_to_top(field_list, field_directories, field)

            for field, field_directory in zip(field_list, field_directories):
                if component != 'flux':
                    component_obj = getattr(obj, component)
                    out_directories, out_list = find_components(field_directory)
                    if 'profile.h5' in out_list:
                        index = out_list.index('profile.h5')
                        profile_file = out_directories[index]
                        with h5py.File(profile_file) as f:
                            profile = f['profile'][:]
                        component_obj.profiles[field] = profile
                    if 'image.h5' in out_list:
                        index = out_list.index('image.h5')
                        with h5py.File(out_directories[index]) as f:
                            image = f['image'][:]
                        setattr(component_obj, field, image)
                else:
                    with h5py.File(field_directory) as f:
                        obj.flux.fluxes[field.rstrip('.h5')] = \
                            f[field.rstrip('.h5')][:]
        return obj

    @log_call
    def calculate_rotation_frequency(self):
        """Calculate the rotation frequency (omega)"""
        self.rot.calculate_rotation_frequency()
        return self.rot.rotation_frequency

    @log_call
    def calculate_circular_velocity(self):
        """Calculate the circular velocity"""
        self.rot.calculate_circular_velocity()
        return self.rot.circular_velocity

    @log_call
    def calculate_epicyclic_frequency(self):
        """Calculate the epicyclic frequency"""
        self.rot.calculate_epicyclic_frequency()
        return self.rot.kappa

    @log_call
    def calculate_scale_height(self, field_type):
        """Calculate the scale height for a field type"""
        density = self.get_covering_grid(field_type, 'density')
        z = np.linspace(BBOX[2, 0], BBOX[2, 1], DDS[2])
        h = scale_height(z, density)
        setattr(getattr(self, field_type), 'scale_height', h)
        return getattr(self, field_type).scale_height

    @log_call
    def calculate_surface_density(self, field_type):
        """Calculate the surface density of a field type"""
        if field_type == 'h2':
            self.calculate_h2_surface_density()
            return
        container = getattr(self, field_type)
        try:
            density = self.get_covering_grid(field_type, 'density')
        except KeyError:
            if field_type != 'star_formation':
                raise
            # this is stupid but it's easier to fix on this end
            density = self.get_covering_grid(field_type, 'sfr_density')
        surfden = _calculate_projected_field(density)
        setattr(container, 'surface_density', surfden)
        return getattr(self, field_type).surface_density

    @log_call
    def calculate_radial_mass_flux(self, field_type):
        """Calculate the radial mass flux profile for a given field type"""
        density = self.get_covering_grid(field_type, 'density')
        xvel = self.get_covering_grid(field_type, 'velocity_x')  # NOQA
        yvel = self.get_covering_grid(field_type, 'velocity_y')  # NOQA
        # Figure out why these need to be switched for some reason
        xpos = np.atleast_3d(self.rot.y_slice)  # NOQA
        ypos = np.atleast_3d(self.rot.x_slice)  # NOQA
        vrad = ne.evaluate('(xvel*xpos + yvel*ypos)/sqrt(xpos**2 + ypos**2)')
        del xvel, yvel
        (radii, fluxes) = self.flux.get_fluxes(
            field_type, vrad.flat, density.flat)
        container = getattr(self, field_type)
        if container.surface_density is None:
            self.calculate_surface_density(field_type)
        surface_density = container.surface_density  # NOQA
        mfd = _calculate_projected_field(ne.evaluate('density*density*vrad'))
        del density, vrad
        whnzero = surface_density != 0
        whzero = surface_density == 0
        mfd[whnzero] = mfd[whnzero]/surface_density[whnzero]
        mfd[whzero] = 0
        container.mass_flux_density = mfd
        return radii, fluxes

    @log_call
    def get_covering_grid(self, group, key):
        """Retrieve covering grid data from the covering grid hdf5 file"""
        generate_star_keys = ('velocity_x', 'velocity_y', 'velocity_z',
                              'density')
        star_groups = ('stars', 'young_stars', 'formed_stars')
        container = getattr(self, group)
        if group in star_groups and key in generate_star_keys:
            # Special case for stellar densities, which must be deposited
            if not hasattr(container, 'pmass'):
                include_vels = True
                self.screen_particles(group, include_velocities=include_vels)
            if container.pmass is None:
                # Should only happen if there are no particles in the domain
                ret = np.zeros(DDS)
            else:
                density = cic_particle_density(
                    container.px, container.py, container.pz,
                    container.xind, container.yind, container.zind,
                    None, container.pmass, np.array(DDS), np.array(BBOX))
                if key == 'density':
                    ret = density
                else:
                    pvel = getattr(container, 'v'+key[-1])
                    deposited_velocity = cic_particle_density(  # NOQA
                        container.px, container.py, container.pz,
                        container.xind, container.yind, container.zind,
                        pvel, container.pmass, np.array(DDS), np.array(BBOX))
                    ret = ne.evaluate(
                        'where(density != 0, deposited_velocity/density, 0)')
        else:
            if group == 'dark_matter' and key == 'density':
                key = 'dark_matter_density'
            with h5py.File(container.cg_filename) as f_cg:
                ret = f_cg[key][:]
        return ret

    @log_call
    def get_streaming_velocity(self, field_type, get_z=True):
        """Calculate streaming velocity vector.

        This is the gas velocity with the local circular velocity vector
        subtracted off.

        """
        if self.rot.rotation_frequency is None:
            self.rot.calculate_rotation_frequency()
        if self.rot.circular_velocity is None:
            self.rot.calculate_circular_velocity()

        if field_type == 'gas':
            v_cx = -np.atleast_3d(self.rot.circular_velocity*self.rot.cost)
            v_cy = np.atleast_3d(self.rot.circular_velocity*self.rot.sint)
            vx = self.get_covering_grid('gas', 'velocity_x')
            vy = self.get_covering_grid('gas', 'velocity_y')
            if get_z is True:
                vz = self.get_covering_grid('gas', 'velocity_z')
        elif field_type == 'stars':
            if self.stars.vx is None:
                self.screen_particles('stars')
            vx = self.stars.vx  # NOQA
            vy = self.stars.vy  # NOQA
            if get_z is True:
                vz = self.stars.vz
            v_cx = -(self.rot.circular_velocity*self.rot.cost)[  # NOQA
                self.stars.xind, self.stars.yind]
            v_cy = (self.rot.circular_velocity*self.rot.sint)[  # NOQA
                self.stars.xind, self.stars.yind]
        else:
            raise RuntimeError

        v = {}
        v['x'] = ne.evaluate('vx - v_cx')
        v['y'] = ne.evaluate('vy - v_cy')
        if get_z is True:
            v['z'] = vz

        return v

    @log_call
    def calculate_effective_sound_speed(self, field_type='gas'):
        """Calculate the effective sound speed"""
        container = getattr(self, field_type)

        if field_type == 'gas':
            if container.sound_speed is None:
                self.calculate_sound_speed()

        if container.velocity_dispersion is None:
            self.calculate_velocity_dispersion()

        sound_speed = getattr(container, 'sound_speed', None)

        if sound_speed is None:
            container.c_eff = container.velocity_dispersion.copy()
        else:
            container.c_eff = np.sqrt(
                container.velocity_dispersion**2 + container.sound_speed**2)

        return container.c_eff

    @log_call
    def calculate_velocity_dispersion(self, field_type):
        container = getattr(self, field_type)

        if container.surface_density is None:
            self.calculate_surface_density(field_type)
        surface_density = container.surface_density

        v = self.get_streaming_velocity(field_type)

        density = self.get_covering_grid(field_type, 'density')

        if field_type == 'gas':
            sigma_x, sigma_y, sigma_z = \
                _get_velocity_dispersion_components(density, v)
        elif field_type == 'stars':
            sigma_x, sigma_y, sigma_z = particle_dispersion(
                v['x'], v['y'], v['z'], container.pmass, container.flat_ind,
                np.array(DDS), 5)
        else:
            raise RuntimeError

        v.clear()

        sigma, sigma_vertical, sigma_d = _get_projected_velocity_dispersion(
            density, sigma_x, sigma_y, sigma_z, surface_density)

        del density, sigma_x, sigma_y, sigma_z

        container.velocity_dispersion = sigma
        container.velocity_dispersion_vertical = sigma_vertical
        container.velocity_dispersion_disk = sigma_d

        return container.velocity_dispersion

    @log_call
    def calculate_velocity_dispersion_ratio(self, field_type):
        container = getattr(self, field_type)

        sigma_d = container.velocity_dispersion_disk  # NOQA
        sigma_vertical = container.velocity_dispersion_vertical  # NOQA

        container.velocity_dispersion_ratio = ne.evaluate(
            'where(sigma_d != 0, sigma_vertical/sigma_d, 0)')
        container.velocity_dispersion_ratio *= np.sqrt(2)

        return container.velocity_dispersion_ratio

    @log_call
    def calculate_sound_speed(self):

        if self.gas.surface_density is None:
            self.calculate_surface_density('gas')
        surface_density = self.gas.surface_density

        density = self.get_covering_grid('gas', 'density')
        thermal_energy = self.get_covering_grid('gas', 'thermal_energy')
        thermal_energy = ne.evaluate('density*thermal_energy')
        del density

        Sigma_thermal = np.sum(thermal_energy*DX, axis=-1, dtype='float64')
        del thermal_energy

        gamma = 5./3.
        self.gas.sound_speed = np.sqrt(gamma*(gamma-1) * Sigma_thermal /
                                       surface_density)

        return self.gas.sound_speed

    @log_call
    def calculate_toomre_q(self, field_type):
        """Calculate the 2D Toomre Q parameter for gas or stars"""
        if field_type == 'gas':
            q_constant = PI
        elif field_type == 'stars':
            q_constant = 3.36
        else:
            raise RuntimeError
        container = getattr(self, field_type)
        if self.rot.rotation_frequency is None:
            self.calculate_rotation_frequency()
        if self.rot.circular_velocity is None:
            self.calculate_circular_velocity()
        if self.rot.kappa is None:
            self.calculate_epicyclic_frequency()
        if container.surface_density is None:
            self.calculate_surface_density(field_type)
        if container.velocity_dispersion is None:
            self.calculate_velocity_dispersion(field_type)
        if container.c_eff is None:
            self.calculate_effective_sound_speed(field_type)
        whnzero = np.where(container.surface_density != 0)
        container.toomre_q = np.zeros(container.surface_density.shape)
        container.toomre_q[whnzero] = \
            (container.c_eff[whnzero]*self.rot.kappa[whnzero] /
             (q_constant*G*container.surface_density[whnzero]))
        return container.toomre_q

    @log_call
    def calculate_total_toomre_q(self):
        """Calculates the combined Toomre Q parameter

        Uses a formula that takes into account the finite thickness of the disk
        and that the gas and stars independently contribute to the gravitational
        potential.

        See Romeo & Wiegert (2011) [2011MNRAS.416.1191R] for details
        """
        stars = self.stars
        gas = self.gas

        for container in [stars, gas]:
            # This will implicitly find the velocity dispersions
            if container.toomre_q is None:
                self.calculate_toomre_q(container.field_type)

        T_s = 0.8 + 0.7*(stars.velocity_dispersion_vertical /
                         stars.velocity_dispersion_disk)
        T_g = 0.8 + 0.7*(gas.velocity_dispersion_vertical /
                         gas.velocity_dispersion_disk)

        sigma_g = gas.velocity_dispersion
        sigma_s = stars.velocity_dispersion

        W = 2*sigma_s*sigma_g / (sigma_s**2 + sigma_g**2)

        Q_s = stars.toomre_q
        Q_g = gas.toomre_q

        res1 = W / (Q_s*T_s) + 1 / (Q_g * T_g)
        res2 = 1 / (Q_s*T_s) + W / (Q_g * T_g)

        res = np.where(T_s*Q_s >= T_g*Q_g, res1, res2)

        # Putting this on the gas component, totally ugly hack
        self.gas.total_toomre_q = 1/res

        return res

    @log_call
    def calculate_total_star_formation(self):
        if self.star_formation.surface_density is None:
            self.calculate_surface_density('star_formation')
        surfden = self.star_formation.surface_density
        total_sfr = surfden*(20*PC)**2
        self.star_formation.total = total_sfr
        return self.star_formation.total

    @log_call
    def calculate_depletion_time(self):
        if self.star_formation.total is None:
            self.calculate_total_star_formation()
        if self.gas.surface_density is None:
            self.calculate_surface_density('gas')
        total_sf = self.star_formation.total
        total_gas = self.gas.surface_density*(20*PC)**2
        depletion_time = total_gas / total_sf
        depletion_time[np.isinf(depletion_time)] = np.nan
        self.star_formation.depletion_time = depletion_time
        return self.star_formation.depletion_time

    @log_call
    def calculate_h2_fraction(self):
        if self.gas.surface_density is None:
            self.calculate_surface_density('gas')
        surfden = self.gas.surface_density/MSUNPERPC2

        # See McKee & Krumholz (ApJ 2010; 709; 308M) equation 93
        # (Assumes solar metallicity)

        chi = 0.77*(1+3.1)
        tau = 0.066*surfden
        s = np.log(1 + 0.6*chi + 0.01*chi**2)/(0.6*tau)

        frac = 1.0 - 0.75*s/(1+0.25*s)
        frac[frac < 0] = 0

        self.gas.h2_fraction = frac
        return self.gas.h2_fraction

    @log_call
    def calculate_h2_surface_density(self):
        if self.gas.surface_density is None:
            self.calculate_surface_density('gas')
        if self.gas.h2_fraction is None:
            self.calculate_h2_fraction()

        gas_surface_density = self.gas.surface_density
        h2_fraction = self.gas.h2_fraction
        h2_surface_density = \
            HYDROGEN_MASS_FRACTION * gas_surface_density * h2_fraction

        self.h2.surface_density = h2_surface_density
        return self.h2.surface_density

    @log_call
    def calculate_fake_star_formation_surface_density(self):
        if self.h2.surface_density is None:
            self.calculate_h2_surface_density()

        h2_surface_density = self.h2.surface_density

        self.star_formation.fake_surface_density = \
            h2_surface_density / (2 * GYR)

        return self.star_formation.fake_surface_density

    @log_call
    def calculate_total_fake_star_formation(self):
        if self.star_formation.fake_surface_density is None:
            self.calculate_fake_star_formation_surface_density()
        surfden = self.star_formation.fake_surface_density
        total_sfr = surfden*(20*PC)**2
        self.star_formation.fake_total = total_sfr
        return self.star_formation.fake_total

    @log_call
    def calculate_everything(self):
        if self.rot.rotation_frequency is None:
            self.calculate_rotation_frequency()
        if self.rot.circular_velocity is None:
            self.calculate_circular_velocity()
        if self.rot.kappa is None:
            self.calculate_epicyclic_frequency()
        for field_type in ('gas', 'stars', 'young_stars', 'star_formation',
                           'formed_stars'):
            self.calculate_surface_density(field_type)
        self.calculate_total_star_formation()
        self.calculate_depletion_time()
        self.calculate_fake_star_formation_surface_density()
        self.calculate_total_fake_star_formation()
        for field_type in ('formed_stars', 'gas', 'stars'):
            self.calculate_scale_height(field_type)
            self.calculate_radial_mass_flux(field_type)
        for field_type in ('gas', 'stars'):
            self.calculate_toomre_q(field_type)
            self.calculate_velocity_dispersion_ratio(field_type)
        self.calculate_total_toomre_q()
        return self

    @log_call
    def plot_everything(self):
        for field in ('rotation_frequency', 'kappa', 'circular_velocity'):
            self._plot_both('rot', field)
        for field_type in ('gas', 'stars', 'young_stars', 'star_formation',
                           'formed_stars'):
            self._plot_both(field_type, 'surface_density')
        for field_type in ('gas', 'stars', 'formed_stars'):
            self._plot_both(field_type, 'scale_height')
            self._plot_both(field_type, 'mass_flux_density')
            self.plot_radial_profile(field_type, 'mass_flux')
        for field_type in ('gas', 'stars'):
            for field in \
                ('toomre_q', 'velocity_dispersion', 'velocity_dispersion_disk',
                 'velocity_dispersion_vertical', 'velocity_dispersion_ratio'):
                self._plot_both(field_type, field)
        self._plot_both('gas', 'sound_speed')
        self._plot_both('gas', 'c_eff')

    def _plot_both(self, field_type, component):
        self.plot_image(field_type, component)
        self.plot_radial_profile(field_type, component)

    @log_call
    def save_to_hdf5(self):
        qpath = ensure_directory(self.qfilename, '')
        for item in self.fields:
            if item[1] == 'mass_flux':
                continue
            container_directory = ensure_directory(qpath, item[0])
            container = getattr(self, item[0])
            image = getattr(container, item[1], None)
            if image is None:
                print ("item '%s' not found" % (item,))
                continue
            component_directory = ensure_directory(container_directory, item[1])
            create_h5_file(component_directory, image, 'image')
            profile = container.profiles[item[1]]
            create_h5_file(component_directory, profile, 'profile')
        # save RadialFluxAnalyzer's results
        flux_directory = ensure_directory(qpath, 'flux')
        for item in self.flux.fluxes.keys():
            create_h5_file(flux_directory, self.flux.fluxes[item], item)

    @log_call
    def screen_particles(self, field_type, include_velocities=True):
        px = self.get_covering_grid(field_type, 'particle_position_x')
        py = self.get_covering_grid(field_type, 'particle_position_y')
        pz = self.get_covering_grid(field_type, 'particle_position_z')
        if include_velocities is True:
            vx = self.get_covering_grid(field_type, 'particle_velocity_x')
            vy = self.get_covering_grid(field_type, 'particle_velocity_y')
            vz = self.get_covering_grid(field_type, 'particle_velocity_z')
        pmass = self.get_covering_grid(field_type, 'particle_mass')

        container = getattr(self, field_type)
        if len(px) > 0:
            xbins, ybins, zbins = [np.linspace(BBOX[i, 0], BBOX[i, 1], DDS[i]+1)
                                   for i in range(3)]

            xind, yind, zind = [np.searchsorted(bins, pos) for pos, bins in
                                zip((px, py, pz), (xbins, ybins, zbins))]

            container.px = px
            container.py = py
            container.pz = pz
            if include_velocities is True:
                container.vx = vx
                container.vy = vy
                container.vz = vz
            container.pmass = pmass
            container.xind = xind-1
            container.yind = yind-1
            container.zind = zind-1
            container.flat_ind = \
                (container.xind*DDS[1] + container.yind)*DDS[2] + container.zind
        else:
            container.pmass = None

    @log_call
    def plot_radial_profile(self, field_type, item=None):
        """Returns a radial profile plot

        Parameters:
          field_type: string
            The field type
          item: string
            The field name
        """
        item = _sanitize_item(field_type, item)
        container = getattr(self, item[0])
        if item[1] != 'mass_flux':
            data = (getattr(getattr(self, item[0]), item[1]) /
                    UNIT_CONVERSIONS[item]).copy()
            plot_args = (data, item, container, self.rot.r_slice,
                         self.rot.kappa)
            function = _plot_radial_profile
        else:
            radii = self.flux.radii / UNIT_CONVERSIONS['rot', 'radius']
            data = self.flux.fluxes[item[0]] / UNIT_CONVERSIONS[item]
            plot_args = (radii, data, item, container)
            function = _plot_radial_mass_flux
        plot = PlotManager(self.output_directory, self.dset_name, function,
                           plot_args, item, 'radial-profile')
        return plot

    @log_call
    def plot_image(self, field_type, item=None):
        """Returns an imshow plot

        Parameters:
          field_type: string
            The field type
          item: string
            The field name
        """
        item = _sanitize_item(field_type, item)

        if item[1] != 'mass_flux':
            data = (getattr(getattr(self, item[0]), item[1]) /
                    UNIT_CONVERSIONS[item])
            plot_args = (data, item)
            plot = PlotManager(self.output_directory, self.dset_name,
                               _plot_image, plot_args, item, 'image')
        else:
            raise RuntimeError

        return plot
