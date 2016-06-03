# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import os
import unittest

from samitizer import Smi


class TestSamitizer(unittest.TestCase):

    def setUp(self):
        self.smi_file_name = 'sample.smi'
        self.vtt_text = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sample.vtt')).read()
        self.plain_text = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sample.txt')).read()

    def test_parsed(self):
        smi = Smi(os.path.join(os.path.dirname(os.path.abspath(__file__)), self.smi_file_name))
        self.assertEqual(len(smi.subtitles), 3)

    def test_convert_vtt(self):
        smi = Smi(os.path.join(os.path.dirname(os.path.abspath(__file__)), self.smi_file_name))
        vtt_text = smi.convert('vtt', 'KRCC')
        self.assertEqual(vtt_text, self.vtt_text)

    def test_convert_plain(self):
        smi = Smi(os.path.join(os.path.dirname(os.path.abspath(__file__)), self.smi_file_name))
        plain_text = smi.convert('plain', 'KRCC')
        self.assertEqual(plain_text, self.plain_text)


if __name__ == '__main__':
    unittest.main()
