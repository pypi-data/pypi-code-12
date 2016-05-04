"""smskit b2mcn test case."""

from unittest import TestCase


class B2mcnTestCase(TestCase):
    """B2mcn test."""

    def test_failure(self):
        """Test failure."""
        self.assertEqual(1, 1)

    def test_success(self):
        """test success."""
        self.assertEqual(1, 1)
