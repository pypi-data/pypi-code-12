import unittest
try:
    import mock
except ImportError: #pragma: no cover
    from unittest import mock

from . import timing


class TimeTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    @mock.patch('time.clock')
    @mock.patch('time.time')
    def test_set(self, mock_time, mock_clock):
        r0 = timing.timing('set')
        r0.stop()
        self.assertEqual(mock_time.call_count, 2)
        self.assertEqual(mock_clock.call_count, 2)

    @mock.patch('time.clock')
    @mock.patch('time.time')
    def test_get(self, mock_time, mock_clock):
        mock_time.side_effect = [0, 0.15]
        mock_clock.side_effect = [0, 0.25]
        r0 = timing.timing('dummy')
        info = str(r0)
        self.assertEqual(info, """\
Time used in dummy               :      0.25 (cpu)       0.15 (wall)"""
            )

    
        

if __name__ == "__main__": #pragma: no cover
    unittest.main()
