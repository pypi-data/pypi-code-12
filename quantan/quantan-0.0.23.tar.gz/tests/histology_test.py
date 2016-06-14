#! /usr/bin/python # -*- coding: utf-8 -*-
# import funkcí z jiného adresáře
import os.path

path_to_script = os.path.dirname(os.path.abspath(__file__))
import unittest
from nose.plugins.attrib import attr
import numpy as np

import logging
logger = logging.getLogger(__name__)

from quantan.quantan import HistologyAnalyser
from quantan.histology_report import HistologyReport


class HistologyTest(unittest.TestCase):
    interactiveTests = False


    def test_synthetic_data_vessel_tree_evaluation(self):
        """
        Generovani umeleho stromu do 3D a jeho evaluace.
        V testu dochazi ke kontrole predpokladaneho objemu a deky cev


        """
        from skelet3d.tree_processing import TreeGenerator
        print "zacatek podezreleho testu"
        # import segmentation
        # import misc

        # generate 3d data from yaml for testing
        tvg = TreeGenerator()
        yaml_path = os.path.join(path_to_script, "./hist_stats_test.yaml")
        tvg.importFromYaml(yaml_path)
        tvg.voxelsize_mm = [1, 1, 1]
        tvg.shape = [100, 100, 100]
        data3d = tvg.generateTree()

        # init histology Analyser
        metadata = {'voxelsize_mm': tvg.voxelsize_mm}
        data3d = data3d * 10
        threshold = 2.5
        ha = HistologyAnalyser(data3d, metadata, threshold)

        print "prostreded 0 "
        # segmented data
        ha.data_to_binar()
        print "prostreded 1 "
        ha.data_to_skeleton()
        print "prostreded 2 "

        # get statistics
        ha.data_to_statistics()
        yaml_new = os.path.join(path_to_script, "hist_stats_new.yaml")
        ha.writeStatsToYAML(filename=yaml_new)

        print "prostreded 3 "
        # get histology reports
        hr = HistologyReport()
        hr.importFromYaml(yaml_path)
        hr.generateStats()
        stats_orig = hr.stats['Report']

        print "prostreded 4 "
        hr = HistologyReport()
        hr.importFromYaml(yaml_new)
        hr.generateStats()
        stats_new = hr.stats['Report']

        csv_new = os.path.join(path_to_script, "vt_new.csv")
        ha.writeStatsToCSV(filename=csv_new)
        # compare
        self.assertGreater(stats_orig['Other']['Total length mm'],stats_new['Other']['Total length mm']*0.9)  # noqa
        self.assertLess(stats_orig['Other']['Total length mm'],stats_new['Other']['Total length mm']*1.1)  # noqa

        self.assertGreater(stats_orig['Other']['Avg length mm'],stats_new['Other']['Avg length mm']*0.9)  # noqa
        self.assertLess(stats_orig['Other']['Avg length mm'],stats_new['Other']['Avg length mm']*1.1)  # noqa

        self.assertGreater(stats_orig['Other']['Avg radius mm'],stats_new['Other']['Avg radius mm']*0.9)  # noqa
        self.assertLess(stats_orig['Other']['Avg radius mm'],stats_new['Other']['Avg radius mm']*1.1)  # noqa

        print "konec podezreleho testu"




    def test_generate_sample_data(self):
        """
        Test has no strong part
        """

        import quantan.quantan
        quantan.quantan.generate_sample_data()


if __name__ == "__main__":
    unittest.main()
