from unittest import TestCase

from hms_base.client import Client


class TestClient(TestCase):

    def test_init_with_ping(self):
        c = Client('test', 'haum', ['irc'])
        self.assertTrue(c._handle_ping in c.listeners)
        self.assertTrue('ping' in c.topics)

    def test_init_without_ping(self):
        c = Client('test', 'haum', ['irc'], enable_ping=False)
        self.assertTrue(c._handle_ping not in c.listeners)
        self.assertTrue('ping' not in c.topics)