import galanyl
import glob
import h5py
import numpy as np
import os
import yt

from skimage.measure import block_reduce

from galanyl import GalaxyAnalyzer
from galanyl.static_data import \
    MSUNPERPC2, MSUNPERYRPERKPC2, \
    PC, SIM_NAMES, my_cm

from matplotlib import pyplot as plt
from mpl_toolkits.axes_grid1.anchored_artists import AnchoredText
from yt.units import pc, msun, yr

GALANYL_PATH = os.path.join(os.path.dirname(galanyl.__file__), os.pardir)

yt.enable_parallelism()

xlim = 3e-2, 3e2
ylim = 1e-7, 1

xlabel_pos = 10**(np.log10(xlim[0]) +
                  0.15*(np.log10(xlim[1]) - np.log10(xlim[0])))
ylabel_pos = 2.5e-5

rotation = 42


def create_bigiel_plot(ax, sf_reduced_image, surfden_reduced_image,
                       draw_tdep_labels=False, xlabel='', ylabel=''):
    whsf = np.nonzero(sf_reduced_image)

    surfden = surfden_reduced_image[whsf]/MSUNPERPC2
    sf_surfden = sf_reduced_image[whsf]/(MSUNPERYRPERKPC2)

    ax.scatter(surfden, sf_surfden)

    surfden = np.logspace(np.log10(xlim[0]), np.log10(xlim[1]))*msun/pc**2
    surfden.convert_to_units('Msun/pc**2')

    for tdep in [1e8, 1e9, 1e10]*yr:
        pred_sf_surfden = (surfden/tdep).in_units('Msun/kpc**2/yr')
        ax.plot(surfden, pred_sf_surfden, linestyle=':', color='k')

    if draw_tdep_labels is True:
        ax.text(xlabel_pos, ylabel_pos, '$10^{%i}$ yr' % np.log10(1e10),
                rotation=rotation, ha='center', va='center',
                fontdict={'size': 'x-small'})
        ax.text(xlabel_pos, 10*ylabel_pos, '$10^{%i}$ yr' % np.log10(1e9),
                rotation=rotation, ha='center', va='center',
                fontdict={'size': 'x-small'})
        ax.text(xlabel_pos, 100*ylabel_pos, '$10^{%i}$ yr' % np.log10(1e8),
                rotation=rotation, ha='center', va='center',
                fontdict={'size': 'x-small'})

    if ylabel == '':
        for ticklabel in ax.get_yticklabels():
            ticklabel.set_visible(False)

    ax.set_xscale('log')
    ax.set_yscale('log')

    ax.set_xlim(xlim[0], xlim[1])
    ax.set_ylim(ylim[0], ylim[1])

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)


def save_images(sim_paths):

    ylabel = r'$\Sigma_{\rm{SFR}}\ \ (M_\odot\ \rm{yr}^{-1}\ \rm{kpc}^{-2})$'

    for sim_path in sim_paths:
        toomre_files = sorted(glob.glob(
            '%s/covering_grids/toomre_q/DD????_toomre/' % sim_path))

        of = os.path.sep.join([sim_path, 'reduced_images', ''])

        if not os.path.exists(of):
            try:
                os.mkdir(of)
            except OSError:
                pass

        for toomre_file in yt.parallel_objects(toomre_files):

            output_file = of + toomre_file[-14:-8] + '_reduced_image.h5'

            if os.path.exists(output_file):
                continue

            ganyl = GalaxyAnalyzer.from_hdf5_file(toomre_file)

            print ganyl.name

            surfden_image = ganyl.gas.surface_density
            h2_surfden_image = \
                ganyl.gas.h2_fraction * ganyl.gas.surface_density
            h1_surfden_image = \
                (1.0 - ganyl.gas.h2_fraction) * ganyl.gas.surface_density
            sf_total_image = ganyl.star_formation.total

            surfden_reduced_image = block_reduce(surfden_image, (37, 37),
                                                 np.nanmean)
            sf_reduced_image = block_reduce(sf_total_image, (37, 37),
                                            np.nansum)
            h2_reduced_image = block_reduce(h2_surfden_image, (37, 37),
                                            np.nanmean)
            h1_reduced_image = block_reduce(h1_surfden_image, (37, 37),
                                            np.nanmean)

            sf_reduced_image /= (740*PC)**2

            with h5py.File(output_file) as f:
                f.create_dataset('sf_reduced_image', data=sf_reduced_image,
                                 compression='lzf')
                f.create_dataset('h2_reduced_image', data=h2_reduced_image,
                                 compression='lzf')
                f.create_dataset('h1_reduced_image', data=h1_reduced_image,
                                 compression='lzf')
                f.create_dataset('surfden_reduced_image',
                                 data=surfden_reduced_image,
                                 compression='lzf')

            fig = plt.figure(figsize=(9, 4))

            gs = plt.GridSpec(1, 3, wspace=0.1, hspace=0.1, bottom=0.15,
                              top=0.95)

            axes = []

            axes.append(fig.add_subplot(gs[0, 0]))
            axes.append(fig.add_subplot(gs[0, 1]))
            axes.append(fig.add_subplot(gs[0, 2]))

            xlabel = r'$\Sigma_{\rm{gas}}\ \ (M_\odot\ \rm{pc}^{-2})$'
            create_bigiel_plot(axes[0], sf_reduced_image,
                               surfden_reduced_image,
                               draw_tdep_labels=True, xlabel=xlabel,
                               ylabel=ylabel)

            xlabel = r'$\Sigma_{\rm{H}_2}\ \ (M_\odot\ \rm{pc}^{-2})$'
            create_bigiel_plot(axes[1], sf_reduced_image, h2_reduced_image,
                               xlabel=xlabel)

            xlabel = r'$\Sigma_{\rm{H\,I}}\ \ (M_\odot\ \rm{pc}^{-2})$'
            create_bigiel_plot(axes[2], sf_reduced_image, h1_reduced_image,
                               xlabel=xlabel)

            plt.savefig(of+ganyl.name+'_ks_image.png')


def get_reduced_image_data(sim_paths):
    sf_surfden = {}
    surfden = {}

    surfden['gas'] = {}
    surfden['h1'] = {}
    surfden['h2'] = {}

    for fn_path in sim_paths:
        sf_surfden[fn_path] = np.array([])

        surfden['gas'][fn_path] = np.array([])
        surfden['h1'][fn_path] = np.array([])
        surfden['h2'][fn_path] = np.array([])
        h5_files = sorted(glob.glob(os.sep.join(
            [fn_path, 'reduced_images', '*.h5'])))
        for h5_file in h5_files:
            with h5py.File(h5_file) as f:
                sf = f['sf_reduced_image'][:]/MSUNPERYRPERKPC2

                whsf = np.nonzero(sf)
                if len(whsf[0]) == 0:
                    continue

                h1 = f['h1_reduced_image'][:]/MSUNPERPC2
                h2 = f['h2_reduced_image'][:]/MSUNPERPC2
                surfden_image = f['surfden_reduced_image'][:]/MSUNPERPC2

                sf_surfden[fn_path] = np.append(sf_surfden[fn_path], sf[whsf])

                surfden['gas'][fn_path] = np.append(surfden['gas'][fn_path],
                                                    surfden_image[whsf])
                surfden['h1'][fn_path] = np.append(surfden['h1'][fn_path],
                                                   h1[whsf])
                surfden['h2'][fn_path] = np.append(surfden['h2'][fn_path],
                                                   h2[whsf])
    return sf_surfden, surfden


def integrated_bigiel_plots(sim_paths, sf_surfden, surfden):
    fig = plt.figure(figsize=(7, 7))
    gs = plt.GridSpec(3, 4, wspace=0.075, hspace=0.075,
                      width_ratios=[1, 1, 1, .1], bottom=0.1, top=0.95)

    xlim = [3e-2, 1.5e3]
    ylim = [1.5e-5, 30]

    vmin = 0
    vmax = 150

    xlabel_pos = 10**(np.log10(xlim[0]) +
                      0.22*(np.log10(xlim[1]) - np.log10(xlim[0])))
    ylabel_pos = 7e-5

    rotation = 45

    n_bins = 50
    log_bin_edges = np.linspace(-1, 3, num=n_bins+1)
    log_bin_centers = (log_bin_edges + (2./n_bins))[:n_bins]

    bin_edges = 10**log_bin_edges
    bin_centers = 10**log_bin_centers

    for rownum, sim_path in enumerate(sim_paths):
        for colnum, component in enumerate(['gas', 'h2', 'h1']):
            median_y = np.empty(n_bins)
            median_y[:] = np.nan
            bin_indices = np.digitize(surfden[component][sim_path], bin_edges)
            for i in range(n_bins+1):
                if len(bin_indices[bin_indices == i]) > 0:
                    values = sf_surfden[sim_path][bin_indices == i+1]
                    median_y[i] = np.median((values))

            ax = fig.add_subplot(gs[rownum, colnum])
            hb = ax.hexbin(surfden[component][sim_path], sf_surfden[sim_path],
                           xscale='log', yscale='log', cmap=my_cm, mincnt=3,
                           vmin=vmin, vmax=vmax)
            ax.plot(bin_centers, median_y, linestyle='--', color='k')
            ax.set_xlim(xlim[0], xlim[1])
            ax.set_ylim(ylim[0], ylim[1])

            xlim_surfden = np.logspace(np.log10(xlim[0]),
                                       np.log10(xlim[1]))*msun/pc**2
            xlim_surfden.convert_to_units('Msun/pc**2')

            for tdep in [1e8, 1e9, 1e10]*yr:
                pred_sf_surfden = (xlim_surfden/tdep).in_units('Msun/kpc**2/yr')
                ax.plot(xlim_surfden, pred_sf_surfden, linestyle=':', color='k')

            if colnum != 0:
                for ticklabel in ax.get_yticklabels():
                    ticklabel.set_visible(False)
            else:
                ax.set_ylabel(
                    r"$\Sigma_{\rm{SFR}}\ \ "
                    r"(M_\odot\ \rm{yr}^{-1}\ \rm{kpc}^{-2})$")

            if colnum == 0:
                ax.add_artist(
                    AnchoredText(SIM_NAMES['no'+sim_path], loc=2,
                                 prop={'size': 'small'}))

            if rownum != 2:
                for ticklabel in ax.get_xticklabels():
                    ticklabel.set_visible(False)
            else:
                if colnum == 0:
                    ax.set_xlabel(
                        r'$\Sigma_{\rm{gas}}\ \ (M_\odot\ \rm{pc}^{-2})$')
                elif colnum == 1:
                    ax.set_xlabel(
                        r'$\Sigma_{\rm{H}_2}\ \ (M_\odot\ \rm{pc}^{-2})$')
                elif colnum == 2:
                    ax.set_xlabel(
                        r'$\Sigma_{\rm{H\,I}}\ \ (M_\odot\ \rm{pc}^{-2})$')

            if rownum == 0 and colnum == 0:
                ax.text(xlabel_pos, ylabel_pos, '$10^{%i}$ yr' % np.log10(1e10),
                        rotation=rotation, ha='center', va='center',
                        fontdict={'size': 'x-small'})
                ax.text(xlabel_pos, 10*ylabel_pos,
                        '$10^{%i}$ yr' % np.log10(1e9), rotation=rotation,
                        ha='center', va='center', fontdict={'size': 'x-small'})
                ax.text(xlabel_pos, 100*ylabel_pos,
                        '$10^{%i}$ yr' % np.log10(1e8), rotation=rotation,
                        ha='center', va='center', fontdict={'size': 'x-small'})

    cax = fig.add_subplot(gs[:, 3])
    cb = plt.colorbar(hb, cax=cax, label='Number of Measurements')
    cb.solids.set_edgecolor("face")
    cb.ax.minorticks_on()

    plt.savefig('%s/paper2/figures/ks_plot.eps' % GALANYL_PATH)

    plt.show()
