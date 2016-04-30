import numpy as np

from galanyl.static_data import \
    NBINS, \
    PROFILE_AXIS_LIMITS, \
    PI, \
    G, \
    UNIT_CONVERSIONS


def _get_profile_data(item, container, data, kappa, r_slice, bins):
    if item[1] == 'toomre_q':
        if kappa is None:
            raise RuntimeError
        if item[0] == 'gas':
            c_eff = container.c_eff
        else:
            c_eff = container.velocity_dispersion
        surface_density = container.surface_density
        _, sigma_profile = _get_profile(c_eff, surface_density, r_slice, bins[0])
        ones = np.ones(surface_density.shape)
        _, surfden_profile = _get_profile(surface_density, ones, r_slice,
                                          bins[0])
        _, kappa_profile = _get_profile(kappa, ones, r_slice, bins[0])
        if item[0] == 'stars':
            prof = sigma_profile * kappa_profile / (3.36 * G * surfden_profile)
        elif item[0] == 'gas':
            prof = sigma_profile * kappa_profile / (PI * G * surfden_profile)
        weight = surface_density / UNIT_CONVERSIONS[item]
    else:
        unweight_fields = ('surface_density', 'total', 'fake_total',
                           'depletion_time')
        if item[1] in unweight_fields or item[0] == 'rot':
            weight = np.ones(data.shape)
        else:
            weight = (container.surface_density /
                      UNIT_CONVERSIONS[item[0], 'surface_density'])
        if 'total' in item[1]:
            normalize_bins = False
        else:
            normalize_bins = True
        profile, weight_profile = _get_profile(data, weight, r_slice, bins[0],
                                               normalize_bins)
        if item[1] in unweight_fields:
            prof = profile
        else:
            prof = weight_profile
    return prof, weight


def _get_plot_limits(item, data):
    xlim = (0, 20)
    ylim = PROFILE_AXIS_LIMITS[item]
    if ylim[0] is None:
        ylim = (np.nanmin(data), ylim[1])
    if ylim[1] is None:
        ylim = (ylim[0], np.nanmax(data))

    return xlim, ylim


def _get_bins(xlim, ylim):

    xbins = np.linspace(xlim[0], xlim[1], NBINS+1)
    if ylim[0] > 0:
        ybins = np.logspace(np.log10(ylim[0]), np.log10(ylim[1]), NBINS+1)
        plot_bins = (xbins, np.log10(ybins))
    else:
        ybins = np.linspace(ylim[0], ylim[1], NBINS+1)
        plot_bins = (xbins, ybins)
    bins = xbins, ybins
    return plot_bins, bins


def _get_profile(data, weight, r_slice, x_bin_edges, normalize_bins=True):
    whfinite = np.isfinite(data)

    if not np.any(whfinite):
        x_hist = np.zeros(NBINS)
        inds = np.array((), dtype='int64')
    else:
        if normalize_bins is True:
            x_hist, _ = np.histogram(r_slice[whfinite], x_bin_edges)
        else:
            x_hist = np.ones(NBINS)
        inds = np.digitize(r_slice[whfinite], x_bin_edges) - 1

    minlength = len(x_hist)

    def unpad_binsum(binsum, minlength):
        if len(binsum) == minlength+1:
            return binsum[:-1]
        elif len(binsum) == minlength:
            return binsum
        else:
            raise RuntimeError

    data_binsum = unpad_binsum(
        np.bincount(inds, weights=data[whfinite], minlength=minlength),
        minlength)

    weight_binsum = unpad_binsum(
        np.bincount(inds, weights=weight[whfinite], minlength=minlength),
        minlength)

    data_weight_binsum = unpad_binsum(
        np.bincount(inds, weights=(data*weight)[whfinite], minlength=minlength),
        minlength)

    nonzero = x_hist > 0

    radial_profile = np.zeros(NBINS)
    radial_weight_profile = np.zeros(NBINS)
    weight_radial_profile = np.zeros(NBINS)

    radial_profile[nonzero] = data_binsum[nonzero] / x_hist[nonzero]
    radial_weight_profile[nonzero] = weight_binsum[nonzero] / x_hist[nonzero]
    if np.any(radial_weight_profile):
        weight_radial_profile[nonzero] = (
            data_weight_binsum[nonzero] /
            (x_hist[nonzero]*radial_weight_profile[nonzero]))

    return radial_profile, weight_radial_profile
