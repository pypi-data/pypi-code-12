"""
Tests

SunPower Corp. (c) 2016
"""

from nose.tools import ok_
import numpy as np
from uncertainty_wrapper import unc_wrapper, unc_wrapper_args
import logging
from scipy.constants import Boltzmann as KB, elementary_charge as QE
from datetime import datetime, timedelta
from solar_utils import *
import pytz

PST = pytz.timezone('US/Pacific')
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)


def test_unc_wrapper():
    """
    Test uncertainty wrapper
    """
    x, cov = np.array([[1.0]]), np.array([[0.1]])
    
    @unc_wrapper
    def f(y):
        return np.exp(y)
    
    avg, var, jac = f(x, __covariance__=cov)
    LOGGER.debug("average = %g", avg)
    LOGGER.debug("variance = %g", var)
    ok_(np.isclose(avg, np.exp(x)))
    ok_(np.isclose(var, cov * np.exp(x) ** 2))
    ok_(np.isclose(jac, np.exp(x)))
    return avg, var, jac


def IV(x, Vd, E0=1000, T0=298.15, kB=KB, qe=QE):
    Ee, Tc, Rs, Rsh, Isat1_0, Isat2, Isc0, alpha_Isc, Eg = x
    Vt = Tc * kB / qe
    Isc = Ee * Isc0 * (1.0 + (Tc - T0) * alpha_Isc)
    Isat1 = (
        Isat1_0 * (Tc ** 3.0 / T0 ** 3.0) *
        np.exp(Eg * qe / kB * (1.0 / T0 - 1.0 / Tc))
    )
    Vd_sc = Isc * Rs  # at short circuit Vc = 0 
    Id1_sc = Isat1 * (np.exp(Vd_sc / Vt) - 1.0)
    Id2_sc = Isat2 * (np.exp(Vd_sc / 2.0 / Vt) - 1.0)
    Ish_sc = Vd_sc / Rsh
    Iph = Isc + Id1_sc + Id2_sc + Ish_sc
    Id1 = Isat1 * (np.exp(Vd / Vt) - 1.0)
    Id2 = Isat2 * (np.exp(Vd / 2.0 / Vt) - 1.0)
    Ish = Vd / Rsh
    Ic = Iph - Id1 - Id2 - Ish
    Vc = Vd - Ic * Rs
    return np.array([Ic, Vc, Ic * Vc])


def Voc(x, E0=1000, T0=298.15, kB=KB, qe=QE):
    Ee, Tc, Rs, Rsh, Isat1_0, Isat2, Isc0, alpha_Isc, Eg = x
    msg = ['Ee=%g[suns]','Tc=%g[K]','Rs=%g[ohms]','Rsh=%g[ohms]',
           'Isat1_0=%g[A]','Isat2=%g[A]','Isc0=%g[A]','alpha_Isc=%g[]',
           'Eg=%g[eV]']
    LOGGER.debug('\n' + '\n'.join(msg) + '\n', *x)
    Vt = Tc * kB / qe
    LOGGER.debug('Vt=%g[V]', Vt)
    Isc = Ee * Isc0 * (1.0 + (Tc - T0) * alpha_Isc)
    LOGGER.debug('Isc=%g[A]', Isc)
    Isat1 = (
        Isat1_0 * (Tc ** 3.0 / T0 ** 3.0) *
        np.exp(Eg * qe / kB * (1.0 / T0 - 1.0 / Tc))
    )
    LOGGER.debug('Isat1=%g[A]', Isat1)
    Vd_sc = Isc * Rs  # at short circuit Vc = 0 
    Id1_sc = Isat1 * (np.exp(Vd_sc / Vt) - 1.0)
    Id2_sc = Isat2 * (np.exp(Vd_sc / 2.0 / Vt) - 1.0)
    Ish_sc = Vd_sc / Rsh
    Iph = Isc + Id1_sc + Id2_sc + Ish_sc
    # estimate Voc
    delta = Isat2 ** 2.0 + 4.0 * Isat1 * (Iph + Isat1 + Isat2)
    return Vt * np.log(((-Isat2 + np.sqrt(delta)) / 2.0 / Isat1) ** 2.0)


RS = 0.004267236774264931  # [ohm] series resistance
RSH = 10.01226369025448  # [ohm] shunt resistance
ISAT1_0 = 2.286188161253440E-11  # [A] diode one saturation current
ISAT2 = 1.117455042372326E-6  # [A] diode two saturation current
ISC0 = 6.3056  # [A] reference short circuit current
EE = 0.8
TC = 323.15
EG = 1.1
ALPHA_ISC = 0.0003551
VOC = Voc((EE, TC, RS, RSH, ISAT1_0, ISAT2, ISC0, ALPHA_ISC, EG))
assert np.isclose(VOC, 0.62816490891656673)
LOGGER.debug('Voc = %g[V]', VOC)
VD = np.arange(0, VOC, 0.005)
X = np.array([EE, TC, RS, RSH, ISAT1_0, ISAT2, ISC0, ALPHA_ISC, EG])
COV = np.diag([1e-4] * X.size)
X = X.reshape(-1, 1).repeat(VD.size, axis=1)
COV = np.tile(COV, (VD.size, 1, 1))


def test_IV():
    """
    Test calculation of photovoltaic cell IV curve using 2-diode model.
    """
    f = unc_wrapper(IV)
    return f(X, VD, __covariance__=COV)


@unc_wrapper_args('lat', 'lon', 'press', 'tamb', 'seconds')
def solar_position(lat, lon, press, tamb, timestamps, seconds=0):
    """
    calculate solar position
    """
    seconds = np.sign(seconds) * np.ceil(np.abs(seconds))
    # seconds = np.where(x > 0, np.ceil(seconds), np.floor(seconds))
    try:
        ntimestamps = len(timestamps)
    except TypeError:
        ntimestamps = 1
        timestamps = [timestamps]
    an, am = np.zeros((ntimestamps, 2)), np.zeros((ntimestamps, 2))
    for n, ts in enumerate(timestamps):
        utcoffset = ts.utcoffset() or 0.0
        dst = ts.dst() or 0.0
        tz = (utcoffset.total_seconds() - dst.total_seconds()) / 3600.0
        loc = [lat, lon, tz]
        dt = ts + timedelta(seconds=seconds.item())
        dt = dt.timetuple()[:6]
        LOGGER.debug('datetime: %r', datetime(*dt).strftime('%Y/%m/%d-%H:%M:%S'))
        LOGGER.debug('lat: %f, lon: %f, tz: %d', *loc)
        LOGGER.debug('p = %f[mbar], T = %f[C]', press, tamb)
        an[n], am[n] = solposAM(loc, dt, [press, tamb])
    return an[:, 0], an[:, 1], am[:, 0], am[:, 1]


def test_solpos():
    """
    Test solar position calculation using NREL's SOLPOS.
    """
    dt = PST.localize(datetime(2016, 4, 13, 12, 30, 0))
    return solar_position(37.405, -121.95, 1013.25, 20.0, dt,
                          __covariance__=np.diag([0.0001] * 5))

if __name__ == '__main__':
    test_unc_wrapper()
    test_IV()
    test_solpos()
