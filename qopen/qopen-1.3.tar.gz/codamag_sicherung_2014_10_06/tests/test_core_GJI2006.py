"""
Test if core module reproduces results of Sens-Schoenfelder and Wegler (2006)
"""

# The following lines are for Py2/Py3 support with the future module.
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from future.builtins import (  # analysis:ignore
    bytes, dict, int, list, object, range, str,
    ascii, chr, hex, input, next, oct, open,
    pow, round, super,
    filter, map, zip)

import json
import os.path
from pkg_resources import resource_filename
import unittest

import numpy as np
from codamag.core import run
from codamag.tests.util import tempdir

PLOT = False

LOG = 'test_core_GJI2006.log'
OUT = 'test_core_GJI2006_results.json'

class TestCase(unittest.TestCase):
    @unittest.skipIf(__name__ != '__main__', 'start only explicitly')
    def test_reproduce_results_of_GJI2006(self):
        calc_results()
        results = load_results()
        freq = [0.1875, 0.375, 0.75, 1.5, 3.0, 6.0, 12.0, 24.0]  # page 1365
        g0 = [2e-6, 2e-6, 1e-6, 1e-6, 1e-6, 1e-6, 1.5e-6, 2e-6]  # fig 4
        Qi = [2e-3, 2e-3, 1.8e-3, 2e-3, 1.5e-3, 1e-3, 5e-4, 2e-4]  # fig 5
        b = np.array(Qi) * (2 * np.pi * np.array(freq))
        M0 = {
            '19920413': 9.3e16, '19950620': 9.0e14, '19971021': 1.7e14,
            '19971129': 4.5e14, '20010623': 5.4e14, '20020722': 4.1e15,
            '20030222': 1.5e16, '20030322': 8.8e14, '20040522': 1.8e14,
            '20041020': 2.4e15, '20041205': 6.8e15
            }  # table 1
        M0_res = {evid.split('_')[0]: r['M0']
                  for evid, r in results['events'].items()}
        temp = [(evid, M0_res[evid], M0[evid])
                for evid in sorted(M0) if evid in M0_res]
        evids, M0_res, M0 = zip(*temp)
        M0 = np.array(M0) * 2 # wrong surface correction in paper
        if PLOT:
            plot_comparison(freq, results['g0'], g0, results['b'], b)
            plot_results(results)
        np.testing.assert_equal(results['freq'], freq)
        np.testing.assert_allclose(results['g0'], g0, rtol=2.0)
        # ignore value for low frequency
        np.testing.assert_allclose(results['b'][1:], b[1:], rtol=1.8)

        # M0s are not determined well
        np.testing.assert_allclose(M0_res, M0, rtol=20,
                                   err_msg='eventids: ' + ' '.join(evids))
        # test that results do not change
        g02 = [1.8e-6, 3.0e-6, 2.2e-6, 9.7e-7, 1.2e-6, 2.1e-6, 2.8e-6, 5.7e-6]
        b2 = [0.012, 0.010, 0.017, 0.020, 0.031, 0.044, 0.055, 0.073]
        error = [0.3, 0.6, 0.7, 0.6, 0.5, 0.5, 0.3, 0.2]
        np.testing.assert_allclose(results['g0'], g02, rtol = 0.1)
        np.testing.assert_allclose(results['b'], b2, rtol = 0.1)
        np.testing.assert_allclose(results['error'], error, rtol = 0.2)


def calc_results():
    conf = resource_filename('codamag', 'tests/data/conf_de.json')
    events = resource_filename('codamag', 'tests/data/events_de.xml')
    inv = resource_filename('codamag', 'tests/data/stations_de.xml')
    with tempdir(delete=False, change_dir=False) as tempd:
        logfile = os.path.join(tempd, LOG)
        outfile = os.path.join(tempd, OUT)
        run(conf=conf, events=events, inventory=inv, cache_waveforms=tempd,
            logfile=logfile, output=outfile)

def load_results():
    with tempdir(delete=False, change_dir=False) as tempd:
        outfile = os.path.join(tempd, OUT)
        with open(outfile) as f:
            results = json.load(f)
    return results

def plot_comparison(freq, g1, g2, b1, b2):
    from pylab import loglog, savefig, legend
    loglog(freq, g1, label='g0')
    loglog(freq, g2, label='g0 GJI')
    loglog(freq, b1, label='b')
    loglog(freq, b2, label='b GJI')
    legend()
    savefig('comparison.pdf')

def plot_results(results):
    from codamag.imaging import plot_results, plot_sites, plot_all_sds
    from codamag.imaging import plot_mags
    plot_results(results, fname='results.pdf')
    plot_sites(results, fname='sites.pdf')
    plot_all_sds(results, fname='sds.pdf')
    plot_mags(results, fname='mags.pdf')

if __name__ == '__main__':
    unittest.main()

