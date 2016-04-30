from __future__ import division

import numpy as np
import six

from collections import OrderedDict

from galanyl.colormap import my_cm

KPC = 3.08567758e21
PC = KPC/1000
KMPERSEC = 1e5
MSUNPERPC2 = .000208908219
MSUNPERYRPERPC2 = 6.62004339e-12
MSUNPERYRPERKPC2 = MSUNPERYRPERPC2/1e6
MSUNPERYR = 6.30321217e25
MSUN = 1.9891e33
G = 6.67384e-8
KBOLTZ = 1.3806488e-16
GYR = 3.15569e16
PI = np.pi
HYDROGEN_MASS_FRACTION = 0.73

BBOX = np.array([[1.9590353125e+24, 2.08542469e+24],
                 [1.9590353125e+24, 2.08542469e+24],
                 [2.0182803421424e+24, 2.02617967e+24]])

DDS = np.array([2048, 2048, 128])

DX = (BBOX[2, 1] - BBOX[2, 0])/DDS[-1]

MAJOR_TICKMARK_PROPERTIES = {}

MINOR_TICKMARK_PROPERTIES = {}

FBBOX = BBOX.flat

PLOT_FRACTION = 1/6

PLOT_SLICE = np.array([PLOT_FRACTION, (1-PLOT_FRACTION)])*2048

EXTENT = FBBOX[:4]/KPC - (FBBOX[1] - (FBBOX[1] - FBBOX[0])/2)/KPC

EXTENT *= (1-2*PLOT_FRACTION)

NBINS = 1000

# Keys are field names, values are tuples of latex label, plot limits,
# colorbar limit, unit conversion, and color table

PLOT_DATA = {
    ('gas', 'surface_density'):
        (r'\Sigma_{\rm{gas}}\ \ (M_\odot\ \rm{pc}^{-2})', (3e-2, 3000),
         (8e-6, .15), MSUNPERPC2, my_cm),
    ('gas', 'sound_speed'):
        (r'c_s\ \ (\rm{km}\ \rm{s}^{-1})', (0.08, 200), (8e-5, .3), KMPERSEC,
         my_cm),
    ('gas', 'velocity_dispersion'):
        (r'\sigma_v\ \ (\rm{km}\ \rm{s}^{-1})', (0.08, 200), (8e-5, .08),
         KMPERSEC, my_cm),
    ('gas', 'velocity_dispersion_disk'):
        (r'\sigma_{v,d}\ \ (\rm{km}\ \rm{s}^{-1})', (0.08, 200), (8e-5, .08),
         KMPERSEC, my_cm),
    ('gas', 'velocity_dispersion_vertical'):
        (r'\sigma_{v,z}\ \ (\rm{km}\ \rm{s}^{-1})', (0.08, 200), (8e-5, .15),
         KMPERSEC, my_cm),
    ('gas', 'velocity_dispersion_ratio'):
        (r'\sqrt{2}\sigma_z/\sigma_d', (0.03, 30), (8e-5, .55), 1.0,
         'RdBu'),
    ('gas', 'c_eff'):
        (r'c_{\rm{eff}}\ \ (\rm{km}\ \rm{s}^{-1})',
         (0.08, 200), (8e-5, .08), KMPERSEC, my_cm),
    ('gas', 'toomre_q'):
        (r'Q_{\rm{gas}}', (0.067, 15), (8e-5, .55), 1.0, 'RdBu'),
    ('gas', 'total_toomre_q'):
        (r'Q_{\rm{total}}', (0.067, 15), (8e-5, .55), 1.0, 'RdBu'),
    ('gas', 'scale_height'):
        (r'H\ \ (\rm{pc})', (1, 500), (8e-5, .55), KPC/1000, my_cm),
    ('gas', 'mass_flux'):
        (r'\dot{M}_{\rm{gas}}\ \ (M_\odot\ \rm{yr}^{-1})', (-30, 30, 1), None,
         MSUNPERYR, 'RdBu'),
    ('gas', 'mass_flux_density'):
        (r'\left<\rho v_r\right>_z\ \ (M_\odot\ \rm{yr}^{-1}\ \rm{pc}^{-2})',
         (-1e-3, 1e-3, 1e-7), (1e1, 1e4), MSUNPERYRPERPC2, 'RdBu'),
    ('gas', 'h2_fraction'):
        (r'\rm{f}_{\rm{H}_2}', (0, 1), (5e-2, 3e1), 1.0, my_cm),
    ('h2', 'surface_density'):
        (r'\Sigma_{\rm{H}_2}\ \ (M_\odot\ \rm{pc}^{-2})', (8e-3, 4000),
         (8e-6, .15), MSUNPERPC2, my_cm),
    ('stars', 'surface_density'):
        (r'\Sigma_{*}\ \ (M_\odot\ \rm{pc}^{-2})', (3e-2, 3000), (8e-6, .015),
         MSUNPERPC2, my_cm),
    ('stars', 'velocity_dispersion'):
        (r'\sigma_{v,*}\ \ (\rm{km}\ \rm{s}^{-1})', (.08, 200), (8e-5, .55),
         KMPERSEC, my_cm),
    ('stars', 'velocity_dispersion_disk'):
        (r'\sigma_{v,d}\ \ (\rm{km}\ \rm{s}^{-1})', (0.08, 200), (8e-5, .08),
         KMPERSEC, my_cm),
    ('stars', 'velocity_dispersion_vertical'):
        (r'\sigma_{v,z}\ \ (\rm{km}\ \rm{s}^{-1})', (0.08, 200), (8e-5, .15),
         KMPERSEC, my_cm),
    ('stars', 'velocity_dispersion_ratio'):
        (r'\sqrt{2}\sigma_{z,*}/\sigma_{d,*}', (0.03, 30), (8e-5, .55), 1.0,
         'RdBu'),
    ('stars', 'scale_height'):
        (r'H_*\ \ (\rm{pc})', (8, 2000), (1e-4, 1e-2), KPC/1000, my_cm),
    ('stars', 'mass_flux'):
        (r'\dot{M}_{*}\ \ (M_\odot\ \rm{yr}^{-1})', (-100, 100, 1), None,
         MSUNPERYR, 'RdBu'),
    ('stars', 'mass_flux_density'):
        (r'\left<\rho_* v_{r,*}\right>_z\ \ ' +
         r'(M_\odot\ \rm{yr}^{-1}\ \rm{pc}^{-2})', (-1e-4, 1e-4, 1e-7),
         (1e0, 3e4), MSUNPERYRPERPC2, 'RdBu'),
    ('stars', 'toomre_q'):
        (r'Q_{\rm{*}}', (0.067, 15), (8e-5, .55), 1.0, 'RdBu'),
    ('formed_stars', 'surface_density'):
        (r'\Sigma_{\rm{formed}}\ \ (M_\odot\ \rm{pc}^{-2})', (8e-3, 300),
         (8e-6, .15), MSUNPERPC2, my_cm),
    ('formed_stars', 'scale_height'):
        (r'H_*\ \ (\rm{pc})', (8, 2000), (1e-4, 1e-2), KPC/1000, my_cm),
    ('formed_stars', 'mass_flux'):
        (r'\dot{M}_{*}\ \ (M_\odot\ \rm{yr}^{-1})', (-100, 100, 1), None,
         MSUNPERYR, my_cm),
    ('formed_stars', 'mass_flux_density'):
        (r'\left<\rho_* v_{r,*}\right>_z\ \ ' +
         r'(M_\odot\ \rm{yr}^{-1}\ \rm{pc}^{-2})', (-1e-4, 1e-4, 1e-7),
         (1e0, 3e4), MSUNPERYRPERPC2, 'RdBu'),
    ('young_stars', 'surface_density'):
        (r'\Sigma_{\rm{young}}\ \ (M_\odot\ \rm{pc}^{-2})', (8e-3, 300),
         (8e-6, .15), MSUNPERPC2, my_cm),
    ('star_formation', 'surface_density'):
        (r'\Sigma_{\rm{SFR}}\ \ (M_\odot\ \rm{pc}^{-2}\ \rm{yr}^{-1})',
         (4e-10, 1.5e-5), (5e-5, 2e8), MSUNPERYRPERPC2, my_cm),
    ('star_formation', 'fake_surface_density'):
        (r'\Sigma_{\rm{SFR, pred}}\ \ (M_\odot\ \rm{pc}^{-2}\ \rm{yr}^{-1})',
         (4e-10, 1.5e-5), (5e-5, 2e8), MSUNPERYRPERPC2, my_cm),
    ('star_formation', 'total'):
        (r'\rm{SFR}\ \ (M_\odot\ \rm{yr}^{-1})', (1.6e-8, .006), (None, None),
         MSUNPERYR, my_cm),
    ('star_formation', 'fake_total'):
        (r'\rm{SFR}_{\rm{pred}}\ \ (M_\odot\ \rm{yr}^{-1})',
         (1.6e-8, .006), (None, None), MSUNPERYR, my_cm),
    ('star_formation', 'depletion_time'):
        (r't_{\rm{dep}}\ \ (\rm{Gyr})', (0.1, 10), (1e-1, 10), GYR, my_cm),
    ('rot', 'rotation_frequency'):
        (r'\Omega\ \ (\rm{s}^{-1})', (7e-17, 2e-13), (8e9, 1.5e15), 1.0,
         'binary_r'),
    ('rot', 'kappa'):
        (r'\kappa\ \ (\rm{km}\ \rm{s}^{-1}\ \rm{kpc}^{-1})', (6e-16, 6e-14),
         (8e11, 1.5e15), 1.0, 'binary_r'),
    ('rot', 'circular_velocity'):
        (r'v_c\ \ (\rm{km}\ \rm{s}^{-1})', (30, 400), (8e-8, 1.5e-2), KMPERSEC,
         my_cm),
    ('rot', 'radius'):
        (r'R\ \ (\rm{kpc})', (None, None), (None, None), KPC, None),
}

FIELD_TYPES = {k: k[0] for k, v in six.iteritems(PLOT_DATA)}
LABELS = {k: v[0] for k, v in six.iteritems(PLOT_DATA)}
IMAGE_COLORBAR_LIMITS = {k: v[1] for k, v in six.iteritems(PLOT_DATA)}
PROFILE_AXIS_LIMITS = {k: v[1] for k, v in six.iteritems(PLOT_DATA)}
PROFILE_COLORBAR_LIMITS = {k: v[2] for k, v in six.iteritems(PLOT_DATA)}
UNIT_CONVERSIONS = {k: v[3] for k, v in six.iteritems(PLOT_DATA)}
COLORMAPS = {k: v[4] for k, v in six.iteritems(PLOT_DATA)}

PROFILE_AXIS_LIMITS[('gas', 'toomre_q')] = (0.03, 1e5)

for ll in LABELS:
    LABELS[ll] = '$'+LABELS[ll]+'$'

SIM_NAMES = OrderedDict([
    ('nofeedback_20pc_lgf', r'$\rm{LGF}$'),
    ('feedback_20pc_lgf', r'$\rm{LGF\ FB}$'),
    ('nofeedback_20pc', r'$\rm{Fiducial}$'),
    ('feedback_20pc', r'$\rm{Fiducial\ FB}$'),
    ('nofeedback_20pc_hgf', r'$\rm{HGF}$'),
    ('feedback_20pc_hgf', r'$\rm{HGF\ FB}$'),
])

EXCLUDED_FIELDS = [('stars', 'c_eff'), ('stars', 'sound_speed')]


CONTAINER_NAMES = [
    'gas',
    'stars',
    'formed_stars',
    'young_stars',
    'star_formation',
    'dark_matter',
    'gpot',
    'h2',
]
