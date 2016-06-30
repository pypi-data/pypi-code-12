# Author: Tom Richter
"""
Radiative Transfer: Approximative interpolation solution of Paasschens (1997)

r ... Distance to source in m
t ... Time after source in s
c ... Velocity in m/s
l ... transport mean free path in m
la ... absorption length in m
"""

# The following lines are for Py2/Py3 support with the future module.
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from future.builtins import (  # analysis:ignore
    bytes, dict, int, list, object, range, str,
    ascii, chr, hex, input, next, oct, open,
    pow, round, super,
    filter, map, zip)

import argparse
import numpy as np
import scipy

def rt_3D_b(t, c, l, var='t'):
    """Bulk term of RT solution"""
    if var == 'r':
        fac = 1  # * delta(r - c * t)
    else:
        fac = 1 / c  # * delta(t - r / c)
    return fac * np.exp(-c * t / l) / (4 * np.pi * c ** 2 * t ** 2)


def G2(x):
    return np.sqrt(1 + 2.026 / x)


def rt_3D_approx(r, t, c, l, check=True):
    """Approximative solution of RT without bulk term"""
    if check and np.any(c * t - r <= 0):
        raise ValueError
    arg0 = r ** 2 / c ** 2 / t ** 2
    arg1 = c * t / l
    # Heaviside(c * t - r) *
    return ((1 - arg0) ** (1 / 8) / (4 * np.pi * l * c * t / 3) ** (3 / 2) *
            np.exp(arg1 * ((1 - arg0) ** (3 / 4) - 1)) *
            G2(arg1 * (1 - arg0) ** (3 / 4)))


def integrate_t_rt_3D_approx(r, t, c, l, N=1):
    """Time intergal of approximative solution from r/c to t"""
    if t <= r / c:
        return 0
    res = [np.array((rt_3D_b(r / c, c, l, var='t'), 0))]
    f = lambda t1: rt_3D_approx(r, t1, c, l)
    t = r / c + np.logspace(-3, np.log10(t - r / c), N)
    for i in range(N - 1):
        res0 = scipy.integrate.quad(f, t[i], t[i + 1], limit=300)
        res.append(np.array(res0))
    res = np.sum(res, axis=0)
    return res[0], res[1]

def plot_t(c, l, r, t=None, N=100, log=False):
    """Plot solution as a function of time"""
    # correction factor for G at position 0 -> minimal influence
    # print((1+np.log(2*r/c/0.01))/l/4/np.pi/r**2 + rt_3D_b(t, c, l)/0.01)
    import matplotlib.pyplot as plt
    if t is None:
        t = 10 * r / c
    ts = r / c + np.logspace(-3, np.log10(t - r / c), N)
    G = rt_3D_approx(r, ts, c, l)
    fig = plt.figure()
    ax = fig.add_subplot(111)
    if log:
        ax.semilogy(ts, G)
    else:
        ax.plot(ts, G)
    ax.set_xlim((0, t))
    ax.set_ylabel('G')
    ax.set_xlabel('t (s)')
    plt.show()


def plot_r(c, l, t, r=None, N=100, log=False):
    """Plot solution as a function of distance"""
    import matplotlib.pyplot as plt
    if r is None:
        r = 10 * c * t
    rs = np.linspace(0, c * t - 0.1, N)
    G = rt_3D_approx(rs, t, c, l)
    fig = plt.figure()
    ax = fig.add_subplot(111)
    if log:
        ax.semilogy(rs, G)
    else:
        ax.plot(rs, G)
    ax.set_xlim((0, r))
    ax.set_ylabel('G')
    ax.set_xlabel('r (m)')
    plt.show()


def main(args=None):
    p = argparse.ArgumentParser(description=__doc__.split('\n')[1])
    choices = ('calc', 'plot-t', 'plot-r', 'integrate-t')
    p.add_argument('command', help='command', choices=choices)
    p.add_argument('c', help='velocity', type=float)
    p.add_argument('l', help='transport mean free path', type=float)
    p.add_argument('-r', help='distance from source', type=float)
    p.add_argument('-t', help='time after source', type=float)
    p.add_argument('--log', help='log plot', action='store_true')
    msg = 'absorption length'
    p.add_argument('-a', '--absorption', help=msg, type=float)
    msg = 'calculate ballistic term, ignore argument -r and -a'
    p.add_argument('-b', '--ballistic', help=msg, action='store_true')
    args = p.parse_args(args)
    r, t, c, l, la = args.r, args.t, args.c, args.l, args.absorption
    com = args.command
    if com == 'calc':
        if args.ballistic:
            print(rt_3D_b(t, c, l))
        else:
            res = rt_3D_approx(r, t, c, l)
            if la:
                res = res * np.exp(-c * t / la)
            print(res)
    elif com == 'plot-t':
        plot_t(c, l, r, t=t, log=args.log)
    elif com == 'plot-r':
        plot_r(c, l, t, r=r, log=args.log)
    elif com == 'integrate-t':
        print(integrate_t_rt_3D_approx(r, t, c, l))


if __name__ == '__main__':
    main()
