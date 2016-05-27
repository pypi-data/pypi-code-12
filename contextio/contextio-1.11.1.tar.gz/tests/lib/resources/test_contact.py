import unittest
from mock import Mock, patch

from contextio.lib.errors import MissingResourceId
from contextio.lib.resources.contact import Contact
from contextio.lib.resources.file import File
from contextio.lib.resources.message import Message
from contextio.lib.resources.thread import Thread

class TestContact(unittest.TestCase):
    def setUp(self):
        self.contact = Contact(Mock(spec=[]), {"email": "fake@email.com"})

    def test_constructor_creates_contact_object_with_all_attributes_in_keys_list(self):
        self.assertTrue(hasattr(self.contact, 'emails'))
        self.assertTrue(hasattr(self.contact, 'name'))
        self.assertTrue(hasattr(self.contact, 'thumbnail'))
        self.assertTrue(hasattr(self.contact, 'last_received'))
        self.assertTrue(hasattr(self.contact, 'last_sent'))
        self.assertTrue(hasattr(self.contact, 'count'))
        self.assertTrue(hasattr(self.contact, 'sent_count'))
        self.assertTrue(hasattr(self.contact, 'received_count'))
        self.assertTrue(hasattr(self.contact, 'sent_from_account_count'))
        self.assertTrue(hasattr(self.contact, 'email'))

    def test_constructor_sets_emails_if_undefined_in_definition(self):
        self.assertEqual(["fake@email.com"], self.contact.emails)

    def test_constructor_creates_emails_list_if_doesnt_exist(self):
        self.assertEqual(["fake@email.com"], self.contact.emails)

    @patch("contextio.lib.resources.base_resource.BaseResource._request_uri")
    def test_get_updates_attributes_and_returns_True(self, mock_request):
        mock_request.return_value = {
            "email": "new@email.com",
            "count": 5,
            "sent_count": 200,
            "received_count": 101,
            "sent_from_account_count": 600,
            "thumbnail": "https://some.url",
            "last_sent": 2000000000,
            "last_received": 2000000000
        }

        response = self.contact.get()

        self.assertTrue(response)
        self.assertEqual("new@email.com", self.contact.email)
        self.assertEqual(5, self.contact.count)
        self.assertEqual(200, self.contact.sent_count)
        self.assertEqual(101, self.contact.received_count)
        self.assertEqual(600, self.contact.sent_from_account_count)
        self.assertEqual("https://some.url", self.contact.thumbnail)
        self.assertEqual(2000000000, self.contact.last_sent)
        self.assertEqual(2000000000, self.contact.last_received)

    @patch("contextio.lib.resources.base_resource.BaseResource._request_uri")
    def test_get_when_email_is_None_it_is_set_from_the_list_of_emails_from_response(self, mock_request):
        mock_request.return_value = {"emails": ["new@email.com"]}

        self.contact.get()

        self.assertEqual("new@email.com", self.contact.email)

    @patch("contextio.lib.resources.base_resource.BaseResource._request_uri")
    def test_get_raises_error_when_email_and_emails_is_empty_in_response(self, mock_request):
        mock_request.return_value = {}

        with self.assertRaises(MissingResourceId):
            self.contact.get()

    @patch("contextio.lib.resources.base_resource.BaseResource._request_uri")
    def test_get_files_returns_list_of_files(self, mock_request):
        mock_request.return_value =[{"file_id": "foobar"}]

        contact_files = self.contact.get_files()

        self.assertEqual(1, len(contact_files))
        self.assertIsInstance(contact_files[0], File)

    @patch("contextio.lib.resources.base_resource.BaseResource._request_uri")
    def test_get_files_returns_list_of_messages(self, mock_request):
        mock_request.return_value = [{"message_id": "foobar"}]

        contact_messages = self.contact.get_messages()

        self.assertEqual(1, len(contact_messages))
        self.assertIsInstance(contact_messages[0], Message)

    @patch("contextio.lib.resources.base_resource.BaseResource._request_uri")
    def test_get_files_returns_list_of_threads(self, mock_request):
        mock_request.return_value =["https://thread.urls/thread"]

        contact_threads = self.contact.get_threads()

        self.assertEqual(1, len(contact_threads))
        self.assertIsInstance(contact_threads[0], Thread)

