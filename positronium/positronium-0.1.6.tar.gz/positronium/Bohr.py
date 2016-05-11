#! python
'''
The Bohr model of positronium
'''
from __future__ import print_function, division
import numpy as np
from . import constants

def energy(n1=1, n2=float('inf'), **kwargs):
    '''
    Calculate the interval between energy levels n1 and n2
    according to the Bohr model, i.e., the Rydberg formula.

    kwargs:
        unit:
            J, eV, meV, ueV, au (Hartree),          [energy]
            Hz, kHz, MHz, GHz, THz,                 [frequency]
            m, cm, mm, um, nm, A, pm, fm,           [vacuum wavelength]
            m^-1, cm^-1.                            [wavenumber]

    defaults:
        n1 = 1
        n2 = infinity
        unit='eV'

    '''
    unit = kwargs.get('unit', 'eV')
    interval = 0.25 * (np.subtract(np.power(n1, -2.0),
                                   np.power(n2, -2.0)))
    if (unit == 'au') or (unit == 'Hartree'):
        return interval
    elif unit in constants.au_energy:
        return constants.au_energy[unit](interval)
    else:
        raise KeyError(unit + ' is not recognised as a suitable unit. See' + \
                              ' docstring for unit list.')

def radius(n=1, **kwargs):
    '''
    Return the Bohr radius for positronium (2 * a_0).

    kwargs:
        unit:
            m, cm, mm, um, nm, A, pm, fm, (SI)
            au (Bohr).

    defaults:
        n = 1
        unit = 'm'

    '''
    unit = kwargs.get('unit', 'm')
    rad = (2.0 * np.power(n, 2.0))
    if (unit == 'au') or (unit == 'Bohr'):
        return rad
    elif unit in constants.au_distance:
        return constants.au_distance[unit](rad)
    else:
        raise KeyError(unit + ' is not recognised as a suitable unit. See' + \
                              ' docstring for unit list.')
