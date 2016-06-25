import unittest
import sys
from cStringIO import StringIO
from spanner import countdown


include = True


class CountdownTestCase(unittest.TestCase):
    def setUp(self):
        # redirect stdout
        self.old_stdout = sys.stdout
        self.trapped_stdout = sys.stdout = StringIO()

    def tearDown(self):
        # reset stdout
        sys.stdout = self.old_stdout

    def test_normal_function(self):
        iterable = range(100)
        timer = countdown.timer_for_iterable(iterable)
        self.assertTrue(timer.total_iterations == len(iterable))
        for i in iterable:
            timer.tick()

        output = self.trapped_stdout.getvalue()
        self.assertTrue('%d loops completed' % len(iterable) in output)
        self.assertTrue(timer.iterations_elapsed == len(iterable))

    def test_overrun(self):
        iterable = range(100)
        timer = countdown.timer_for_iterable(iterable)
        self.assertTrue(timer.total_iterations == len(iterable))
        for i in iterable:
            timer.tick()

        timer.tick()
        output = self.trapped_stdout.getvalue()
        sys.stdout = self.old_stdout
        self.assertTrue('Timer overrun!' in output)
