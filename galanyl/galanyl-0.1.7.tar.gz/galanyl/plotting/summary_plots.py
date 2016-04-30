from __future__ import division

from galanyl.static_data import \
    SIM_NAMES, KPC, UNIT_CONVERSIONS, LABELS, \
    IMAGE_COLORBAR_LIMITS, COLORMAPS, NBINS
from galanyl.galaxy_analyzer import decade_counter

import galanyl

import glob
import h5py
import os
import matplotlib
import numpy as np
import palettable

from matplotlib import pyplot as plt
from matplotlib.ticker import MultipleLocator
from mpl_toolkits.axes_grid1 import ImageGrid, AxesGrid
from mpl_toolkits.axes_grid1.anchored_artists import AnchoredText

from collections import OrderedDict

ylims = [[100, 600],
         [50, 600],
         [50, 550]]

xlims = [[0, 8],
         [0, 10],
         [0, 15]]

paths = {
    ('gas', 'mass_flux'): ['flux', 'gas.h5'],
    ('stars', 'mass_flux'): ['flux', 'stars.h5'],
    ('gas', 'surface_density'): ['gas', 'surface_density', 'profile.h5'],
    ('stars', 'surface_density'): ['stars', 'surface_density', 'profile.h5'],
    ('star_formation', 'surface_density'): [
        'star_formation', 'surface_density', 'profile.h5'],
    ('star_formation', 'fake_surface_density'): ['star_formation',
                                                 'fake_surface_density',
                                                 'profile.h5'],
    ('star_formation', 'depletion_time'): ['star_formation', 'depletion_time',
                                           'profile.h5'],
    ('star_formation', 'total'): ['star_formation', 'total', 'profile.h5'],
    ('star_formation', 'fake_total'): ['star_formation', 'fake_total',
                                       'profile.h5'],
    ('gas', 'toomre_q'): ['gas', 'toomre_q', 'profile.h5'],
    ('stars', 'toomre_q'): ['stars', 'toomre_q', 'profile.h5'],
    ('gas', 'total_toomre_q'): ['gas', 'total_toomre_q', 'profile.h5'],
    ('gas', 'c_eff'): ['gas', 'c_eff', 'profile.h5'],
    ('stars', 'velocity_dispersion'): ['stars', 'velocity_dispersion',
                                       'profile.h5'],
    ('gas', 'sound_speed'): ['gas', 'sound_speed', 'profile.h5'],
    ('gas', 'velocity_dispersion'): [
        'gas', 'velocity_dispersion', 'profile.h5'],
    ('gas', 'velocity_dispersion_ratio'): ['gas', 'velocity_dispersion_ratio',
                                           'profile.h5'],
    ('rot', 'kappa'): ['rot', 'kappa', 'profile.h5'],
}

PC = KPC/1000
GALANYL_PATH = os.path.join(os.path.dirname(galanyl.__file__), os.pardir)


def fill_data_dict(sim_folders, toomre_q_lists):
    data = OrderedDict()
    for sim_path in sim_folders:
        sim_name = os.path.basename(sim_path)
        data[sim_name] = {}
        for data_type in toomre_q_lists[sim_path]:
            data[sim_name][data_type] = np.zeros((601, NBINS))
            for i, path in enumerate(toomre_q_lists[sim_path][data_type]):
                with h5py.File(path) as f:
                    dset_name = f.keys()[0]
                    data[sim_name][data_type][i, :] = f[dset_name][:]
            data[sim_name][data_type] /= UNIT_CONVERSIONS[data_type]
    return data


def create_radius_time_summary(data, field_name, paper_dir,
                               overplot_lines=False, tick_locations=None,
                               colorbar_limits=None):
    linthresh = None
    if colorbar_limits is not None:
        vmin, vmax = colorbar_limits
        norm = None
    else:
        try:
            vmin, vmax, linthresh = IMAGE_COLORBAR_LIMITS[field_name]
            norm = matplotlib.colors.SymLogNorm(linthresh)
        except:
            vmin, vmax = IMAGE_COLORBAR_LIMITS[field_name]
            norm = matplotlib.colors.LogNorm()


    if paper_dir == 'paper2':
        nrows_ncols = (3, 1)
        figsize = (4.2, 4.8)
    else:
        nrows_ncols = (3, 1)
        figsize = (4.0, 4.8)

    fig = plt.figure(1, figsize)

    grid = ImageGrid(fig, 111, nrows_ncols=nrows_ncols, axes_pad=0.2,
                     cbar_size='2%', cbar_mode='single', label_mode='L',
                     cbar_pad=0.08)

    extent = [0., 15., 0., 600.]

    aspect = 0.5*(extent[1] - extent[0])/(extent[3] - extent[2])

    for i, name in enumerate(data):
        display_data = data[name][field_name][:, :750].copy()
        if norm is None:
            display_data[display_data == 0] = np.nan
        imax = grid[i].imshow(display_data, origin='lower',
                              norm=norm, vmin=vmin, vmax=vmax, extent=extent,
                              aspect=aspect)
        if overplot_lines is True and i < 2:
            grid[i].plot(xlims[i], ylims[i])
        grid[i].set_xlabel(r'$\rm{R}\ \ (\rm{kpc})$')
        if i == 2:
            grid[i].set_ylabel(r'$\rm{Time}\  \ (\rm{Myr})$')
            grid[i].set_aspect(10./600.)
            grid[i].set_ylim(0, 300)
            grid[i].set_yticks([0, 150, 300])
            grid[i].yaxis.set_minor_locator(MultipleLocator(50))
        else:
            grid[i].set_ylim(0, 600)
            grid[i].set_yticks([0, 200, 400, 600])
            grid[i].yaxis.set_minor_locator(MultipleLocator(100))
        grid[i].set_xticks([0, 5, 10, 15])
        grid[i].xaxis.set_minor_locator(MultipleLocator(1))
        grid[i].add_artist(AnchoredText(SIM_NAMES[name], loc=1,
                                        prop={'size': 'x-small'}))
        imax.set_cmap(COLORMAPS[field_name])

    cax = grid.cbar_axes[0]

    cb = fig.colorbar(imax, cax=cax, ticks=tick_locations)

    cb.solids.set_edgecolor("face")

    cb.ax.minorticks_on()

    if norm is not None:
        minorticks = imax.norm(decade_counter(vmin, vmax))
        cb.ax.yaxis.set_ticks(minorticks, minor=True)

    cb.set_label(LABELS[field_name])

    plt.tight_layout()

    figure_path = '%s/%s/figures' % (GALANYL_PATH, paper_dir)
    if not os.path.exists(figure_path):
        os.makedirs(figure_path)
    plt.savefig('%s/radius_time_%s_%s.eps' %
                (figure_path, field_name[0], field_name[1]), dpi=400)

    plt.show(fig)

    plt.close(fig)


def fill_filename_dictionary(sim_folders):
    maxlen = 0
    minlen = 1000

    toomre_q_lists = {}

    for path in sim_folders:
        base_path = [path, 'covering_grids', 'toomre_q', '*']
        toomre_q_lists[path] = {}
        for field_name, field_path in paths.items():
            toomre_q_lists[path][field_name] = \
                sorted(glob.glob(os.path.sep.join(base_path + field_path)))
            nsims = len(toomre_q_lists[path][field_name])
            if nsims > maxlen:
                maxlen = nsims
            if nsims < minlen:
                minlen = nsims

    return toomre_q_lists, minlen, maxlen


def _get_mean_data(data, name, field, yarr, xarr, sim_index):
    datacopy = data[name][field].copy()

    datacopy[np.isnan(datacopy)] = 0

    whbad = np.where(yarr - ((ylims[sim_index][1] - ylims[sim_index][0]) /
                             (xlims[sim_index][1] - xlims[sim_index][0]))*xarr
                     < ylims[sim_index][0])
    datacopy[whbad] = 0

    ycopy = yarr.copy()
    ycopy[whbad] = 0
    ycopy[ycopy == 0] = np.nan

    ptp = (np.nanmax(ycopy, axis=0) - np.nanmin(ycopy, axis=0))

    mean_data = np.trapz(datacopy, axis=0, dx=1e6)/(ptp*1e6)

    mean_data_error = np.empty_like(mean_data)
    mean_data_error[:] = np.nan
    mean_data_lower_variance = mean_data_error.copy()
    mean_data_upper_variance = mean_data_error.copy()

    datacopy[np.isnan(ycopy)] = np.nan

    for col in range(datacopy.shape[1]):
        column = datacopy[:, col]
        n_measurements = np.isfinite(column).astype('int64').sum()
        if n_measurements < 0:
            continue
        std = np.nanstd(column)
        # divide by 10 to account for the fact that measurements are correlated
        # over a period of about 10 million years. This was estimated by
        # visually inspecting the autocorrelation of the mass flux at a given
        # radius
        mean_data_error[col] = std/np.sqrt(n_measurements/10)
        mean_data_lower_variance[col] = np.nanpercentile(column, 17)
        mean_data_upper_variance[col] = np.nanpercentile(column, 83)

    return (mean_data, mean_data_error, mean_data_lower_variance,
            mean_data_upper_variance)


def create_mass_flux_summary_plot(data, paper_dir, plot_ylims, sim_names,
                                  yticks):

    nrows = 2
    figsize = (3, 4)

    fig = plt.figure(1, figsize)

    grid = AxesGrid(fig, 111, nrows_ncols=(nrows, 1), axes_pad=0.2,
                    cbar_mode='None', label_mode='L')

    xd = np.linspace(0, 20, 1000)
    yd = np.linspace(0, 600, 601)

    xarr, yarr = np.meshgrid(xd, yd)

    for j in range(nrows):
        sim_name = sim_names[j]
        ax = grid[j]
        ax.set_color_cycle(palettable.tableau.ColorBlind_10.mpl_colors)

        label = SIM_NAMES[sim_name]
        color = palettable.tableau.ColorBlind_10.mpl_colors[j]

        for field in [('gas', 'mass_flux'), ('star_formation', 'total')]:
            (mean_data, mean_data_error, mean_data_lower_variance,
             mean_data_upper_variance) = _get_mean_data(
                 data, sim_name, field, yarr, xarr, j)

            if field[0] == 'star_formation':
                ax.plot(
                    xd[:500],
                    -1*np.cumsum(mean_data[:500]),
                    linewidth=2.0,
                    linestyle='--',
                    label=label,
                    color=color)
            else:
                ax.fill_between(
                    x=xd[:500],
                    y1=mean_data_upper_variance[:500],
                    y2=mean_data_lower_variance[:500],
                    alpha=0.5,
                    facecolor=color,
                    linewidth=0)
                ax.fill_between(
                    x=xd[:500],
                    y1=mean_data[:500] - mean_data_error[:500],
                    y2=mean_data[:500] + mean_data_error[:500],
                    alpha=0.7,
                    facecolor=color,
                    linewidth=0)
                ax.plot(
                    xd[:500],
                    mean_data[:500],
                    alpha=1.0,
                    color=color,
                    linewidth=1.0)

        ylabel = (r'$\langle \dot{M}_{\rm{gas}}\rangle_t\ \ '
                  r'(M_\odot\ \rm{yr}^{-1})$')

        ax.set_ylabel(ylabel, fontsize=11)

        ax.plot([0, 10], [0, 0], color='black', linestyle='--', alpha=0.8)

        ax.set_ylim(plot_ylims[j][0], plot_ylims[j][1])
        ax.yaxis.set_ticks(yticks[j])
        aspect = 0.8*(10 - 0)/(plot_ylims[j][1] - plot_ylims[j][0])
        ax.set_aspect(aspect)
        ax.set_xlabel(r'$\rm{R}\ \ (\rm{kpc})$')
        ax.add_artist(
            AnchoredText(
                label, loc=1, prop={'size': 'x-small'}, borderpad=0.7))

    plt.tight_layout()

    figure_path = '%s/%s/figures' % (GALANYL_PATH, paper_dir)
    if not os.path.exists(figure_path):
        os.makedirs(figure_path)
    plt.savefig('%s/mass_flux_summary.pdf' % (figure_path, ))

    plt.show(fig)

    plt.close(fig)


def create_q_summary_plot(data, maxlen, sim, paper_dir):

    params = matplotlib.figure.SubplotParams(
        left=.06, right=0.98, bottom=0.09, top=0.95)

    fig = plt.figure(1, (7.5, 7), subplotpars=params)

    xd = np.linspace(0, 20, 1000)
    yd = np.linspace(0, 600, 601)

    xarr, yarr = np.meshgrid(xd, yd)

    fields = [[('gas', 'toomre_q'), ('stars', 'toomre_q'),
               ('gas', 'total_toomre_q')],
              [('gas', 'surface_density'), ('stars', 'surface_density')],
              [('gas', 'c_eff'), ('stars', 'velocity_dispersion')],
              [('rot', 'kappa')]]

    ncols = 3
    nrows = len(fields)

    grid = AxesGrid(fig, 111, nrows_ncols=(nrows, ncols), axes_pad=0.1,
                    cbar_mode='None', label_mode='L')

    y_limits = [(.3, 300), (.7, 3000), (3, 300), (5e-16, 1.5e-14)]
    linestyles = ['-', '-.', '--']

    labels = [r'$\rm{Q}$', r'$\Sigma\ \ (M_\odot\ \rm{pc}^{-2})$',
              r'$c_{\rm{eff}}\ \ (\rm{km}\ \rm{s}^{-1})$',
              r'$\kappa\ \ (\rm{km}\ \rm{s}^{-1}\ \rm{kpc}^{-1})$']

    time_ranges = [[0, 200], [200, 400], [400, 600]]

    for colnum, time_range in enumerate(time_ranges):
        for rownum in range(nrows):
            axes_num = colnum + ncols*rownum
            grid[axes_num].set_color_cycle(
                palettable.tableau.ColorBlind_10.mpl_colors)
            for j, field in enumerate(fields[rownum]):

                whbad = np.where(
                    np.logical_or(yarr < time_range[0], yarr > time_range[1]))

                qdatacopy = np.log10(data[sim][field].copy())

                qdatacopy[whbad] = 0
                qdatacopy[np.isnan(qdatacopy)] = 0

                ycopy = yarr.copy()
                ycopy[whbad] = 0
                ycopy[ycopy == 0] = np.nan

                ptp = time_range[1] - time_range[0]

                mean_q = np.trapz(qdatacopy, axis=0, dx=1e6)/(ptp*1e6)

                label = field[0].title()
                color = None

                if field[1] == 'total_toomre_q':
                    label = 'Total'
                elif field[0] == 'rot':
                    label = None
                    color = 'black'

                if np.any(data[sim][field]):
                    plot_data = 10**(mean_q[:550])
                else:
                    plot_data = np.zeros(550) + np.nan
                    plot_data[0] = y_limits[rownum][1] + y_limits[rownum][0]
                    plot_data[0] /= 2

                grid[axes_num].semilogy(xd[:550], plot_data, label=label,
                                        linestyle=linestyles[j], linewidth=2,
                                        color=color)

                aspect = 0.8*(10 - 0)/(y_limits[rownum][1] - y_limits[rownum][0])

                grid[axes_num].set_aspect(aspect)

                grid[axes_num].set_ylim(*y_limits[rownum])

                grid[axes_num].set_xlim(0, 11)

                grid[axes_num].set_ylabel(labels[rownum])

                grid[axes_num].set_xlabel(r'$\rm{R}\ \ (\rm{kpc})$')

                if rownum == 0:
                    grid[axes_num].set_title(r'$%d\mbox{--}%d\ \ \rm{Myr}$'
                                             % tuple(time_range))

                if rownum == 0 and colnum == 0:
                    grid[axes_num].legend(prop={'size': 'x-small'}, loc=2)

    figure_path = '%s/%s/figures' % (GALANYL_PATH, paper_dir)
    if not os.path.exists(figure_path):
        os.makedirs(figure_path)
    plt.savefig('%s/q_summary_plot.eps' % (figure_path, ))

    plt.show(fig)

    plt.close(fig)


def create_velocity_summary(data, sim, maxlen, paper_dir, plot_ylims):
    fig = plt.figure(1, (4, 5))

    grid = AxesGrid(fig, 111, nrows_ncols=(3, 1), axes_pad=0.15,
                    cbar_mode='None', label_mode='L')

    xd = np.linspace(0, 20, 1000)
    yd = np.linspace(0, 600, 601)

    xarr, yarr = np.meshgrid(xd, yd)

    sigmadatacopy = data[sim][('gas', 'velocity_dispersion')].copy()
    csdatacopy = data[sim][('gas', 'sound_speed')].copy()
    ceffdatacopy = data[sim][('gas', 'c_eff')].copy()
    ratiodatacopy = data[sim][('gas', 'velocity_dispersion_ratio')].copy()

    sigmadatacopy[np.isnan(sigmadatacopy)] = 0
    csdatacopy[np.isnan(csdatacopy)] = 0
    ceffdatacopy[np.isnan(ceffdatacopy)] = 0
    ratiodatacopy[np.isnan(ratiodatacopy)] = 0

    velocity_plot_labels = [
        r'$-\langle\rm{c_{\rm eff}}\rangle_t\ \ (\rm{km}\ \rm{s}^{-1})$',
        r'$\langle \sqrt{2}\sigma_{v,z}/\sigma_{v,d} \rangle_t$',
        r'$v\ \ (\rm{km}\ \rm{s}^{-1})$'
    ]

    # these are hard-coded to refer to nofeedback_20pc ylims
    slope = (ylims[1][1] - ylims[1][0])/(xlims[1][1] - xlims[1][0])
    whbad = np.where(np.logical_and(yarr - slope*xarr < ylims[1][0],
                                    yarr > maxlen))

    sigmadatacopy[whbad] = 0
    csdatacopy[whbad] = 0
    ceffdatacopy[whbad] = 0
    ratiodatacopy[whbad] = 0

    ycopy = yarr.copy()
    ycopy[whbad] = 0
    ycopy[ycopy == 0] = np.nan

    ptp = (np.nanmax(ycopy, axis=0) - np.nanmin(ycopy, axis=0))

    mean_ceff = np.trapz(ceffdatacopy, axis=0, dx=1e6)/(ptp*1e6)

    ceffdatacopy[ceffdatacopy == 0] = np.nan

    std_ceff = np.nanstd(ceffdatacopy, axis=0)

    grid[0].plot(xd[:700], mean_ceff[:700], zorder=2, color='k')
    grid[0].fill_between(xd[:700], mean_ceff[:700]-std_ceff[:700],
                         mean_ceff[:700]+std_ceff[:700], alpha=0.5, zorder=1)

    ratiodatacopy = np.log10(ratiodatacopy)
    ratiodatacopy[np.isinf(ratiodatacopy)] = 0

    mean_ratio = (np.trapz(ratiodatacopy, axis=0, dx=1e6)/(ptp*1e6))

    ratiodatacopy[ratiodatacopy == 0] = np.nan

    std_ratio = np.nanstd(ratiodatacopy, axis=0)

    mean_ratio[mean_ratio == 0] = np.nan
    mean_ratio[np.isinf(mean_ratio)] = np.nan

    grid[1].semilogy(xd[:700], 10**mean_ratio[:700], zorder=2, color='k')
    grid[1].fill_between(xd[:700], 10**(mean_ratio[:700]-std_ratio[:700]),
                         10**(mean_ratio[:700]+std_ratio[:700]), alpha=0.5,
                         zorder=1)

    mean_sigma = np.trapz(sigmadatacopy, axis=0, dx=1e6)/(ptp*1e6)
    mean_cs = np.trapz(csdatacopy, axis=0, dx=1e6)/(ptp*1e6)

    grid[2].set_color_cycle(palettable.tableau.ColorBlind_10.mpl_colors)
    grid[2].plot(xd[:700], mean_sigma[:700],
                 label=r'$\langle \sigma_v \rangle_t$')
    grid[2].plot(xd[:700], mean_cs[:700],
                 label=r'$\langle c_s \rangle_t$')
    grid[2].plot(xd[:700], mean_ceff[:700],
                 label=r'$\langle c_{\rm eff} \rangle_t$')
    grid[2].legend(prop={'size': 'x-small'})

    for i in range(3):
        aspect = 0.35*(20 - 0)/(plot_ylims[i][1] - plot_ylims[i][0])
        grid[i].set_aspect(aspect)
        grid[i].set_ylim(plot_ylims[i][0], plot_ylims[i][1])
        grid[i].set_xlabel(r'$\rm{R}\ \ (\rm{kpc})$')
        grid[i].set_ylabel(velocity_plot_labels[i])
        grid[i].minorticks_on()
        if i in (0, 2):
            grid[i].set_yticks(range(0, plot_ylims[i][1], 10))

    plt.tight_layout()

    figure_path = '%s/%s/figures' % (GALANYL_PATH, paper_dir)
    if not os.path.exists(figure_path):
        os.makesirs(figure_path)
    plt.savefig('%s/velocity_summary_plot.pdf' % (figure_path, ))

    plt.show(fig)

    plt.close(fig)
