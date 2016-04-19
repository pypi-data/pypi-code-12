"""
Tests for :func:`~uncertainty_wrapper.unc_wrapper` and
:func:`~uncertainty_wrapper.unc_wrapper_args`
"""

from uncertainty_wrapper.tests import *
from uncertainty_wrapper.tests.test_algopy import IV_algopy_jac, solpos_nd_jac


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
    Test calculation of photovoltaic cell IV curve using 2-diode model and
    and compare Jacobian estimated by finite central difference to AlgoPy
    automatic differentiation.
    """
    f = unc_wrapper(IV)
    pv, pv_cov, pv_jac = f(X, VD, __covariance__=COV)
    pv_jac_algopy = IV_algopy_jac(*X, Vd=VD)
    nVd = pv_jac_algopy.shape[1]
    for n in xrange(nVd // 2, nVd):
        irow, icol = 3 * n, 9 * n
        jrow, jcol = 3 + irow, 9 +icol
        pv_jac_n = pv_jac[irow:jrow, icol:jcol]
        pv_jac_algopy_n = pv_jac_algopy[:, n, n::VD.size]
        LOGGER.debug('pv jac at Vd = %g[V]:\n%r', VD[n], pv_jac_n)
        LOGGER.debug('pv jac AlgoPy at Vd = %g[V]:\n%r', VD[n], pv_jac_algopy_n)
        reldiff = pv_jac_n / pv_jac_algopy_n - 1.0
        LOGGER.debug('reldiff at Vd = %g[V]:\n%r', VD[n], reldiff)
        resnorm = np.linalg.norm(reldiff)
        LOGGER.debug('resnorm at Vd = %g[V]: %r', VD[n], resnorm)
        rms = np.sqrt(np.sum(reldiff ** 2.0) / 9.0/ 3.0)
        LOGGER.debug('rms at Vd = %g[V]: %r', VD[n], rms)
        ok_(np.allclose(pv_jac_n, pv_jac_algopy_n, rtol=1e-3, atol=1e-3))
    return pv, pv_cov, pv_jac, pv_jac_algopy


def plot_pv(pv, pv_cov):
    """
    IV and PV 2-axis plot with errorbars 
    """
    i_pv, v_pv, p_pv = pv
    i_stdev = np.sqrt(pv_cov.diagonal()[::3])
    v_stdev = np.sqrt(pv_cov.diagonal()[1::3])
    p_stdev = np.sqrt(pv_cov.diagonal()[2::3]) 
    fig, ax1 = plt.subplots()
    ax1.errorbar(v_pv, i_pv, i_stdev, v_stdev)
    ax1.grid()
    ax1.set_xlabel('voltage [V]')
    ax1.set_ylabel('current [A]', color='b')
    ax1.set_ylim([0, 6.0])
    ax2 = ax1.twinx()
    ax2.errorbar(v_pv, p_pv, p_stdev, v_stdev, fmt='r')
    ax2.grid()
    ax2.set_ylabel('power [W]', color='r')
    ax2.set_ylim([0, 3.0])
    ax1.set_title('IV and PV curves')
    return fig


def plot_pv_jac(pv_jac, pv_jac_algopy, Vd=VD):
    """
    Log plot of relative difference between AlgoPy and central finite difference
    approximations

    :param pv_jac: central finite approximations
    :param pv_jac_algopy: automatic differentiation
    :param Vd: voltages
    :return: fig
    """
    fn = ['Cell Current, Ic [A]', 'Cell Voltage, Vc [V]', 'Cell Power, Pc [W]']
    fig, ax = plt.subplots(3, 1, **{'figsize': (8.0, 18.0)})
    colorcycle = [
        'firebrick', 'goldenrod', 'sage', 'lime', 'seagreen', 'turquoise',
        'royalblue', 'indigo', 'fuchsia'
    ]
    for m in xrange(3):
        for n in xrange(9):
            pv_jac_n = pv_jac[m::3, n::9].diagonal()
            pv_jac_algopy_n = pv_jac_algopy[m, :, n * 126:(n + 1) * 126].diagonal()
            reldiff = np.abs(pv_jac_n / pv_jac_algopy_n - 1.0)
            ax[m].semilogy(Vd, reldiff, colorcycle[n])
        ax[m].grid()
        ax[m].legend(
            ['Ee', 'Tc', 'Rs', 'Rsh', 'Isat1_0', 'Isat2', 'Isc0', 'alpha_Isc',
             'Eg'], fancybox=True, framealpha=0.5
        )
        ax[m].set_xlabel('Diode Voltage, Vd [V]')
        ax[m].set_ylabel('Relative Difference')
        ax[m].set_title(fn[m])
    plt.tight_layout()
    return fig

@UREG.wraps(('deg', 'deg', 'dimensionless', 'dimensionless', None, None),
            ('deg', 'deg', 'millibar', 'degC', None, 'second', None), strict=False)
@unc_wrapper_args(0, 1, 2, 3, 5)
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
        utcoffset = ts.utcoffset()
        dst = ts.dst()
        if None in (utcoffset, dst):
            tz = 0.0  # assume UTC if naive
        else:
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
    lat = 37.405 * UREG.deg
    lon = -121.95 * UREG.deg
    press = 101325 * UREG.Pa
    tamb = 293.15 * UREG.degK
    seconds = 1 * UREG.s
    cov = np.diag([0.0001] * 5)
    ze, az, am, ampress, cov, jac = solar_position(lat, lon, press, tamb, dt,
                                                   seconds, __covariance__=cov)
    jac_nd = solpos_nd_jac(lat, lon, press.to('millibar'), tamb.to('degC'), dt,
                           seconds)
    ok_(np.allclose(jac[:, :4], jac_nd[:, :4], rtol=0.1, atol=0.1, equal_nan=True))
    return ze, az, am, ampress, cov, jac, jac_nd


if __name__ == '__main__':
    test_unc_wrapper()
    pv, pv_cov, pv_jac, pv_jac_algopy = test_IV()
    test_solpos()
    fig1 = plot_pv(pv, pv_cov)
    fig1.show()
    fig2 = plot_pv_jac(pv_jac, pv_jac_algopy)
    fig2.savefig('IV-PV-jac-errors.png')
    fig2.show()
