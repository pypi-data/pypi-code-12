from mock import Mock, patch
import unittest

from contextio.lib.resources.email_account import EmailAccount
from contextio.lib.resources.connect_token import ConnectToken
from contextio.lib.resources.folder import Folder

class TestEmailAccount(unittest.TestCase):
    def setUp(self):
        self.email_account = EmailAccount(Mock(spec=[]), {"label": "fake_label"})

    def test_constructor_sets_attributes_on_object(self):
        self.assertTrue(hasattr(self.email_account, "status"))
        self.assertTrue(hasattr(self.email_account, "resource_url"))
        self.assertTrue(hasattr(self.email_account, "type"))
        self.assertTrue(hasattr(self.email_account, "authentication_type"))
        self.assertTrue(hasattr(self.email_account, "use_ssl"))
        self.assertTrue(hasattr(self.email_account, "server"))
        self.assertTrue(hasattr(self.email_account, "label"))
        self.assertTrue(hasattr(self.email_account, "username"))
        self.assertTrue(hasattr(self.email_account, "port"))

    @patch("contextio.lib.resources.base_resource.BaseResource.post")
    def test_post_updates_delimiter(self, mock_post):
        mock_post.return_value = True

        response = self.email_account.post(delimiter="/t")

        self.assertEqual(self.email_account.delimiter, "/t")
        mock_post.assert_called_with(
            all_args=["delimiter"], params={"delimiter": "/t"})
        self.assertTrue(response)

    @patch("contextio.lib.resources.base_resource.BaseResource._request_uri")
    def test_get_folders_returns_list_of_Folders(self, mock_request):
        mock_request.return_value = [{"name": "some_folder"}]

        folders = self.email_account.get_folders()

        self.assertEqual(1, len(folders))
        self.assertIsInstance(folders[0], Folder)

    @patch("contextio.lib.resources.base_resource.BaseResource._request_uri")
    def test_get_connect_tokens_returns_list_of_ConnectTokens(self, mock_request):
        mock_request.return_value = [{"token": "some_token"}]

        connect_tokens = self.email_account.get_connect_tokens()

        self.assertEqual(1, len(connect_tokens))
        self.assertIsInstance(connect_tokens[0], ConnectToken)


