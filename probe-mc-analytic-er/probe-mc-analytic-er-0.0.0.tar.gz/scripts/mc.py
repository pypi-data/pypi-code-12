#!/usr/bin/env python
from probe.mc import run_integrator_in_parallel
import scipy.constants as C
import sys

if __name__ == '__main__':

    proc_no = sys.argv[1]
    npar = sys.argv[2]
    cycle = sys.argv[3]

    kwargs = {
        'particle': 'el',
        'T': 300.0,
        'er_C':1.44398701e-08,
        'p': 15.0,
        'Tg': 300.0,
        'mg': 4.002602*C.m_u,
        'rd':0.05,
        'rdd': 0.005,
        'npar': int(npar),
        'show_progress_every_par': 10,
    }

    run_integrator_in_parallel(int(proc_no), int(cycle), **kwargs)


