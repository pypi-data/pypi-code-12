# -*- coding: utf-8 -*-
import unittest

from eatme.cli import EatMe, run_for_all_repos


class TestEatMe(unittest.TestCase):
    def test_run(self):
        self.assertTrue(callable(EatMe.run))

    def test_run_for_all_repos(self):
        def func(path):
            self.assertIsInstance(path, str)

        self.assertTrue(callable(run_for_all_repos))
        self.assertIsNone(run_for_all_repos(func))


if __name__ == '__main__':
    unittest.main()
