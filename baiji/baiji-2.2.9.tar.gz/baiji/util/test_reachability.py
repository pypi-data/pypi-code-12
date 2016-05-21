import unittest

class TestReachability(unittest.TestCase):
    def test_internet_reachable(self):
        # These tests are implemented as integration tests against S3. In
        # theory they could be rewritten so that they mock key boto
        # functionality.
        #
        # This test is not so much about testing that the internet is
        # reachable, but that the code runs and the required dependency is
        # present.
        from baiji.util.reachability import internet_reachable
        self.assertTrue(internet_reachable())
