"""
Tests for core module.
"""

# The following lines are for Py2/Py3 support with the future module.
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from future.builtins import (  # analysis:ignore
    bytes, dict, int, list, object, range, str,
    ascii, chr, hex, input, next, oct, open,
    pow, round, super,
    filter, map, zip)

import os
from pkg_resources import load_entry_point
import unittest

import numpy as np
from codamag.core import init_data, run, run_cmdline
from codamag.tests.util import tempdir, quiet


travis = os.environ.get('TRAVIS') == 'true'

class TestCase(unittest.TestCase):

    def test_entry_point(self):
        script = load_entry_point('rf', 'console_scripts', 'rf')
        with quiet():
            try:
                script(['-h'])
            except SystemExit:
                pass

    @unittest.skipIf(not travis, 'save time')
    def test_cmdline(self):
        script = run_cmdline
        with tempdir():
            script(['--create-config', '--tutorial'])
            script()

    def test_results_of_tutorial(self):
        with tempdir():
            run(create_config='conf.json', tutorial=True)
            kwargs = {
                'plot_energies': False, 'plot_optimization': False,
                'plot_optresult': False, 'plot_eventresult': False,
                'plot_eventsites': False, 'plot_results': False,
                'plot_sites': False, 'plot_sds': False, 'plot_mags': False
                }
            result = run(conf='conf.json', **kwargs)
        # desired values
        freq = [0.5, 1, 2, 4]
        g0 = [2.89e-6, 3.21e-6, 1.24e-6, 1.04e-6]
        b = [0.016, 0.027, 0.029, 0.037]
        error = [0.39, 0.27, 0.45, 0.52]
        R_FUR = [4.2, 3.4, 3.9, 4.3]
        R_BUG = [0.24, 0.29, 0.26, 0.23]
        M0_1 = 4.5e17  # 2003_02_22
        Mw_1 = 5.8
        M0_2 = 1.6e17  # 2004_12_05
        Mw_2 = 5.5
        rtol = 0.05
        err_msg = 'Frequencies have to be %s for this test' % freq
        np.testing.assert_equal(result['freq'], freq, err_msg)
        np.testing.assert_allclose(result['g0'], g0, rtol=rtol)
        np.testing.assert_allclose(result['b'], b, rtol=rtol)
        np.testing.assert_allclose(result['error'], error, rtol=rtol)
        np.testing.assert_allclose(result['R']['GR.FUR'], R_FUR, rtol=rtol)
        np.testing.assert_allclose(result['R']['GR.BUG'], R_BUG, rtol=rtol)
        ev1 = result['events']['20030222_0000013']
        ev2 = result['events']['20041205_0000033']
        np.testing.assert_allclose(ev1['M0'], M0_1, rtol=rtol)
        np.testing.assert_allclose(ev1['Mw'], Mw_1, rtol=rtol)
        np.testing.assert_allclose(ev2['M0'], M0_2, rtol=rtol)
        np.testing.assert_allclose(ev2['Mw'], Mw_2, rtol=rtol)


    def test_plugin_option(self):
        f = init_data('plugin', plugin='codamag.tests.test_core : gw_test')
        self.assertEqual(f(nework=4, station=2), 42)

def gw_test(**kwargs):
    return 42

if __name__ == '__main__':
    unittest.main()
