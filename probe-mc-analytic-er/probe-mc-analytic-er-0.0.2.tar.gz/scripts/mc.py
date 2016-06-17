#!/usr/bin/env python
from probe.mc import run_integrator_in_parallel
import scipy.constants as C
import sys

if __name__ == '__main__':

    particle = sys.argv[1]
    assert particle in ['el', 'ari']
    proc_no = sys.argv[2]
    npar = sys.argv[3]
    cycle = sys.argv[4]
    out_file = sys.argv[5]

    kwargs = {
        'particle': particle,
        'T': 300.0,
        'er_C':1.44398701e-08,
        'p': 15.0,
        'Tg': 300.0,
        'mg': 4.002602*C.m_u,
        'rd':0.05,
        'rdd': 0.005,
        'npar': int(npar),
        'show_progress_every_par': 10,
        'output_file': out_file,
    }

    run_integrator_in_parallel(int(proc_no), int(cycle), **kwargs)


