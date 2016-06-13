# -*- coding: utf-8 -*-

import unittest
import os
from datetime import datetime, timedelta
from waybackscraper import wayback


class TestWayback(unittest.TestCase):
    def test_list_snapshots(self):
        """
        Extract a list of memento from the resources/memento_list.txt file
        """
        # Mock the memento URL
        wayback.MEMENTO_TEMPLATE = 'file://{memento_list}'.format(
            memento_list=os.path.abspath('resources/memento_list.txt'))

        # List the snapshot found in the test memento
        snapshots = wayback.list_archives('')

        self.assertEquals(len(snapshots), 771)

    def test_next_date_with_offset(self):
        """
        Test the function that filters a list of archive to keep the one matching the given criteria
        """
        archives = [
            wayback.Archive(datetime(2015, 1, 1, 0, 0), ''),
            wayback.Archive(datetime(2016, 1, 1, 0, 0), ''),
            wayback.Archive(datetime(2016, 1, 5, 0, 0), ''),
            wayback.Archive(datetime(2016, 1, 7, 0, 0), ''),
            wayback.Archive(datetime(2016, 1, 10, 0, 0), ''),
            wayback.Archive(datetime(2016, 2, 10, 0, 0), '')
        ]

        filtered_archives = [archive for archive in wayback.archive_period_filter(archives,
                                                                                  datetime(2016, 1, 1, 0, 0),
                                                                                  datetime(2016, 2, 1, 0, 0),
                                                                                  timedelta(days=2))]

        self.assertEqual([archive.date for archive in filtered_archives],
                         [datetime(2016, 1, 1, 0, 0), datetime(2016, 1, 5, 0, 0), datetime(2016, 1, 10, 0, 0)])
