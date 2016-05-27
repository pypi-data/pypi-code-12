from mock import Mock, patch
import unittest

from contextio.lib.resources.folder import Folder
from contextio.lib.resources.message import Message


class TestFolder(unittest.TestCase):
    def setUp(self):
        self.folder = Folder(Mock(spec=[]), {"name": "fake_folder_name"})

    def test_constructor_creates_folder_object_with_all_attributes_in_keys_list(self):
        self.assertTrue(hasattr(self.folder, "name"))
        self.assertTrue(hasattr(self.folder, "attributes"))
        self.assertTrue(hasattr(self.folder, "delim"))
        self.assertTrue(hasattr(self.folder, "nb_messages"))
        self.assertTrue(hasattr(self.folder, "nb_unseen_messages"))

    @patch("contextio.lib.resources.base_resource.BaseResource._request_uri")
    def test_put_sends_params_and_returns_True(self, mock_request):
        mock_request.return_value = {"success": True}

        created_folder = self.folder.put(delim="foobar")

        mock_request.assert_called_with(method="PUT", params={"delim": "foobar"})
        self.assertTrue(created_folder)

    @patch("contextio.lib.resources.base_resource.BaseResource._request_uri")
    @patch("contextio.lib.helpers.sanitize_params")
    def test_get_messages_sanitizes_params(self, mock_sanitize, mock_request):
        self.folder.get_messages(include_body=True)

        mock_sanitize.assert_called_with({'include_body': True}, [
            "include_thread_size", "include_body", "body_type", "include_headers",
            "include_flags", "flag_seen", "limit", "offset" ])

    @patch("contextio.lib.resources.base_resource.BaseResource._request_uri")
    def test_get_messages_returns_list_of_Messages(self, mock_request):
        mock_request.return_value = [{"message_id": "fake_id"}]

        messages = self.folder.get_messages()

        self.assertEqual(1, len(messages))
        self.assertIsInstance(messages[0], Message)
