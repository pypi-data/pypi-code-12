#! python
'''
Binding energy of positronium according to calculations by
Richard A. Ferrell (1951) Phys. Rev. 84, 858
http://dx.doi.org/10.1103/PhysRev.84.858

Nb. This does not include the Lamb shift/ radiative corrections.
'''
from __future__ import print_function, division
import numpy as np
from positronium.constants import alpha, au_energy

def epsilon(l, S, J):
    """ scaling of the fine structure shift accoring to l, S and J."""
    epsilon = -0.5 * np.divide(1.0, 2.0*l + 1.0)
    if S == 0:
        # singlet
        pass
    elif S == 1:
        # triplet
        delta = int(l == 0)
        if J == l + 1:
            omega = np.divide(3.0 * l + 4.0,
                              (l + 1.0) * (2.0 * l + 3.0))
        elif J == l:
            omega = -np.divide(1.0, l * (l + 1.0))
        elif J == l - 1:
            omega = -np.divide(3.0 * l - 1.0, l * (2.0 * l - 1.0))
        else:
            raise ValueError("The total angular momentum quantum number 'J' must " + \
                             "be in the range l - 1 < J < l + 1")
        epsilon = epsilon + 7.0 * delta/ 12.0 + np.divide(1 - delta, 8.0*(l + 0.5)) * omega
    else:
        raise ValueError("The total spin quantum number 'S' must be 0 or 1.")
    return epsilon


def fine_structure(n, l, S, J, unit='au'):
    """ fine structure shift (default: atomic units) for quantum numbers n, l, S and J"""
    delta_E = np.power(n, -4.0) * 11.0 * alpha**2 / 64.0 + \
              np.power(n, -3.0) * alpha**2 * epsilon(l, S, J)
    if (unit == 'au') or (unit == 'Hartree'):
            return delta_E
    elif unit in au_energy:
        return au_energy[unit](delta_E)
    else:
        raise KeyError(unit + ' is not recognised as a suitable unit.')

def energy_level(n, l, S, J, unit='au'):
    """ energy level (default: atomic units) of Ps with quantum numbers n, l, S and J"""
    energy = -np.power(n, -2.0) / 4.0 + fine_structure(n, l, S, J, unit='au')
    if (unit == 'au') or (unit == 'Hartree'):
        return energy
    elif unit in au_energy:
        return au_energy[unit](energy)
    else:
        raise KeyError(unit + ' is not recognised as a suitable unit.')