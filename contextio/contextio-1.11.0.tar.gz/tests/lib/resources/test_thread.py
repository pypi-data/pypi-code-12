import unittest
from mock import Mock

from contextio.lib.resources.message import Message
from contextio.lib.resources.thread import Thread
from contextio.lib.resources.source import Source


class TestThread(unittest.TestCase):
    def setUp(self):
        self.thread = Thread(Mock(spec=["foo"]), {"gmail_thread_id": "foobar"})

    def test_constructor_creates_thread_object_with_all_attributes_in_keys_list(self):
        self.assertTrue(hasattr(self.thread, "gmail_thread_id"))
        self.assertTrue(hasattr(self.thread, "email_message_ids"))
        self.assertTrue(hasattr(self.thread, "person_info"))
        self.assertTrue(hasattr(self.thread, "messages"))
        self.assertTrue(hasattr(self.thread, "subject"))
        self.assertTrue(hasattr(self.thread, "folders"))
        self.assertTrue(hasattr(self.thread, "sources"))

    def test_constructor_adds_messages_to_thread_object_if_messages_in_definition(self):
        thread = Thread(Mock(spec=["foo"]), {
            "gmail_thread_id": "foobar",
            "messages": [
                {"message_id": "foo"},
                {"message_id": "bar"}
            ]
        })

        self.assertIsInstance(thread.messages[0], Message)
        self.assertIsInstance(thread.messages[1], Message)

    def test_constructor_adds_sources_to_thread_object_if_sources_in_definition(self):
        thread = Thread(Mock(), {
            "gmail_thread_id": "foobar",
            "sources": [
                {"label": "foo"},
                {"label": "bar"}
            ]
        })

        self.assertIsInstance(thread.sources[0], Source)
        self.assertIsInstance(thread.sources[1], Source)
