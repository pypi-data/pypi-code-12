#! python
'''
Physical constants
'''
from __future__ import print_function, division
import webbrowser
from scipy.constants import m_e, e, c, h, hbar, alpha, Rydberg

class MeasuredValue(float):
    ''' subclass of built-in type float'''
    def __new__(cls, value, uncertainty, unit):
        measured = float.__new__(cls, value)
        measured.value = value
        measured.uncertainty = uncertainty
        measured.unit = unit
        measured.source = None
        measured.url = None
        return measured

    def article(self):
        ''' open url to constant reference'''
        if self.url is not None:
            webbrowser.open(self.url)
        else:
            raise LookupError('The source url has not been specified.')

# Planck constant uncertainty CODATA [J s]
h_uncertainty = 8.1e-42
# mass [kg]
m_Ps = 2.0 * m_e
# reduced mass [kg]
reduced_mass_Ps = m_e/ 2.0
# Rydberg
Ryd_Ps = Rydberg / 2.0
Rydberg_Ps = Rydberg / 2.0
# Bohr radius [m]
a_0 = hbar / (m_e * c * alpha)
# Ps Bohr raidus [m]
a_Ps = 2.0 * a_0

# ground-state decay rate / lifetime
## para-positronium
decay_pPs = MeasuredValue(7990.9e6, 1.7e6, 'Hz')
tau_pPs = MeasuredValue(1.0 / decay_pPs, decay_pPs.uncertainty/ decay_pPs**2.0, 's')
for con in [decay_pPs, tau_pPs]:
    setattr(con, 'source', 'Al-Ramadhan, A. H. and Gidley, D. W. (1994) ' + \
                           'Phys. Rev. Lett. 72, 1632 ')
    setattr(con, 'url', 'http://dx.doi.org/10.1103/PhysRevLett.72.1632')

## ortho-positronium
decay_oPs = MeasuredValue(7.0404e6, 0.0018e6, 'Hz')
tau_oPs = MeasuredValue(1.0 / decay_oPs, decay_oPs.uncertainty/ decay_oPs**2.0, 's')
for con in [decay_oPs, tau_oPs]:
    setattr(con, 'source', 'R. S. Vallery, P. W. Zitzewitz, and D. W. Gidley (2003) ' + \
                           'Phys. Rev. Lett. 90, 203402')
    setattr(con, 'url', 'http://dx.doi.org/10.1103/PhysRevLett.90.203402')

# ground-state hyperfine splitting
nu_hfs = MeasuredValue(203.38910e9, 000.00074e9, 'Hz')
energy_hfs = MeasuredValue(h * nu_hfs,
                           ((h * nu_hfs.uncertainty)**2.0 + (h_uncertainty * nu_hfs)**2.0)**0.5,
                           'J')
for con in [nu_hfs, energy_hfs]:
    setattr(con, 'source', 'M. W. Ritter, P. O. Egan, V. W. Hughes, and ' +
                           'K. A. Woodle (1984) Phys. Rev. A 30, 1331')
    setattr(con, 'url', 'http://dx.doi.org/10.1103/PhysRevA.30.1331')

# 1^3S-2^3S interval
nu_1s2s = MeasuredValue(1233607216.4e6, 3.2e6, 'Hz')
energy_1s2s = MeasuredValue(h * nu_1s2s,
                            ((h * nu_1s2s.uncertainty)**2.0 + (h_uncertainty * nu_1s2s)**2.0)**0.5,
                            'J')
for con in [nu_1s2s, energy_1s2s]:
    setattr(con, 'source', 'Fee, M.S. et al. (1993) Phys. Rev. Lett. 70, 1397')
    setattr(con, 'url', 'http://dx.doi.org/10.1103/PhysRevLett.70.1397')

# rescale atomic units
## energy / energy interval / wavelength/ wavenumbers
au_energy = dict({'J': (lambda x: x * 2.0 * Rydberg * h * c),
                  'eV': (lambda x: x * 2.0 * Rydberg * h * c / e),
                  'meV': (lambda x: 1e3 * x * 2.0 * Rydberg * h * c / e),
                  'ueV': (lambda x: 1e6 * x * 2.0 * Rydberg * h * c / e),
                  'Hz': (lambda x: x * 2.0 * Rydberg * c),
                  'kHz': (lambda x: 1e-3 * x * 2.0 * Rydberg * c),
                  'MHz': (lambda x: 1e-6 * x * 2.0 * Rydberg * c),
                  'GHz': (lambda x: 1e-9 * x * 2.0 * Rydberg * c),
                  'THz': (lambda x: 1e-12 * x * 2.0 * Rydberg * c),
                  'm': (lambda x: 1.0 / (x * 2.0 * Rydberg)),
                  'cm': (lambda x: 1e2 / (x * 2.0 * Rydberg)),
                  'mm': (lambda x: 1e3 / (x * 2.0 * Rydberg)),
                  'um': (lambda x: 1e6 / (x * 2.0 * Rydberg)),
                  'nm': (lambda x: 1e9 / (x * 2.0 * Rydberg)),
                  'A': (lambda x: 1e10 / (x * 2.0 * Rydberg)),
                  'pm': (lambda x: 1e12 / (x * 2.0 * Rydberg)),
                  'fm': (lambda x: 1e15 / (x * 2.0 * Rydberg)),
                  'm^-1': (lambda x: x * 2.0 * Rydberg),
                  'cm^-1': (lambda x: 1e-2 * x * 2.0 * Rydberg)})
## distance
au_distance = dict({'m': (lambda x: x * a_0),
                    'cm': (lambda x: x * a_0 * 1e2),
                    'mm': (lambda x: x * a_0 * 1e3),
                    'um': (lambda x: x * a_0 * 1e6),
                    'nm': (lambda x: x * a_0 * 1e9),
                    'A': (lambda x: x * a_0 * 1e10),
                    'pm': (lambda x: x * a_0 * 1e12),
                    'fm': (lambda x: x * a_0 * 1e15)})
