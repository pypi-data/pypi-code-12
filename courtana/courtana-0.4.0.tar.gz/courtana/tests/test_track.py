# -*- coding: utf-8 -*-

import unittest

import numpy as np

from courtana.annotations import Track
from courtana.annotations import Event


class TestTrack(unittest.TestCase):

    def setUp(self):
        pass

    def test_track_init_parameters(self):
        track = Track(0, 'track', '#000000')
        self.assertEqual(track.id, 0)
        self.assertEqual(track.name, 'track')
        self.assertEqual(track.color, '#000000')

    def test_add_event(self):
        track = Track(0, 'track', '#000000')
        event = Event(0)
        self.assertEqual(track.nevents, 0)
        track.add_event(event)
        self.assertEqual(track.nevents, 1)
        self.assertEqual(track.events[0], event)

    def test_added_events_are_sorted_by_time(self):
        track = Track(0, 'track', '#000000')
        event_1 = Event(1)
        event_2 = Event(2)
        track.add_event(event_2)
        track.add_event(event_1)
        self.assertEqual(track.events[0], event_1)
        self.assertEqual(track.events[1], event_2)

    def test_track_bool_mask(self):
        track = Track(0, 'track', '#000000')
        event_1 = Event(t=1)
        event_3 = Event(t=3, duration=2)
        track.add_event(event_1)
        track.add_event(event_3)
        mask = track.get_mask(min=0, max=5)
        np.testing.assert_equal(
            mask, np.array([False, True, False, True, True, False]))


if __name__ == '__main__':
    unittest.main()
