# -*- coding: utf-8 -*-

import tempfile
import unittest

from courtana.annotations import Annotations, Track, Event


class TestAnnotations(unittest.TestCase):

    def setUp(self):
        # Generate test annotations
        self.annotations = Annotations()
        t = Track(0, 'track_name', '#000000')
        t.add_event(Event(0, 100, 'comment'))
        t.add_event(Event(200, 50))
        self.annotations.tracks = [t]

    def test_save_csv_lineterminator(self):
        expected_output = (
        "0,2,,,#000000,track_name\n"
        "True,0,100,comment,#000000\n"
        "True,200,250,,#000000\n"
        ",,,,,\n"
        )

        output_file = tempfile.NamedTemporaryFile(mode='x+', encoding='utf-8')
        self.annotations.save_to_csv(output_file.name)

        self.assertMultiLineEqual(expected_output, output_file.read())


if __name__ == '__main__':
    unittest.main()
