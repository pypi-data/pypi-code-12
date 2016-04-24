import unittest
import mock

from prboard import utils, filters, settings


class TestUtils(unittest.TestCase):
    @mock.patch("prboard.utils.constants")
    def test_parse_pr_filters(self, mock_constants):
        """ Test parse_pr_filters """
        mock_num_filter = mock.Mock(spec=filters.PRNumberFilter)
        mock_title_filter = mock.Mock(spec=filters.PRFilter)
        mock_etitle_filter = mock.Mock(spec=filters.PRFilter, wildcard=True)
        mock_labels_filter = mock.Mock(spec=filters.LabelFilter)

        mock_constants.FILTER_COMMAND_MAPPING = {
            'num': mock_num_filter,
            'title': mock_title_filter,
            'etitle': mock_etitle_filter,
            'labels': mock_labels_filter
        }

        filter_str = "num:123"
        objects = utils.parse_pr_filters(filter_str)
        mock_num_filter.assert_called_once_with("123")

        filter_str = "labels:label1;label2;label3"
        objects = utils.parse_pr_filters(filter_str)
        mock_labels_filter.assert_called_with(["label1", "label2", "label3"])

        filter_str = "title:pr_title"
        objects = utils.parse_pr_filters(filter_str)
        mock_title_filter.assert_called_with("pr_title")

        filter_str = "etitle:pr_title"
        objects = utils.parse_pr_filters(filter_str)
        mock_etitle_filter.assert_called_with("pr_title")

        filter_str = "num:1234,labels:label11;label12;label13,title:pr_title_1"
        objects = utils.parse_pr_filters(filter_str)
        mock_num_filter.assert_called_with("1234")
        mock_labels_filter.assert_called_with(["label11", "label12", "label13"])
        mock_title_filter.assert_called_with("pr_title_1")

    def test_overload_settings_from_file(self):
        """ Test overload_settings_from_file """
        PRBOARD_SETTINGS_FILE = settings.PRBOARD_SETTINGS_FILE
        read_data = "PRBOARD_BASE_URL=https://api.test.com\n" \
                    "PRBOARD_REPO_FILTER=test-repo\n" \
                    "PRBOARD_GITHUB_USERNAME=test_user\n" \
                    "PRBOARD_SETTINGS_FILE=test_settings_file.cfg\n" \
                    "PRBOARD_GITHUB_PASSWORD=test_password"""

        with mock.patch("prboard.utils.open", mock.mock_open(read_data=read_data)) as m:
            utils.overload_settings_from_file()

        m.assert_called_once_with(PRBOARD_SETTINGS_FILE, "r")
        self.assertEqual(settings.PRBOARD_BASE_URL, "https://api.test.com")
        self.assertEqual(settings.PRBOARD_REPO_FILTER, "test-repo")
        self.assertEqual(settings.PRBOARD_GITHUB_USERNAME, "test_user")
        self.assertEqual(settings.PRBOARD_GITHUB_PASSWORD, "test_password")
        # settings.PRBOARD_SETTINGS_FILE should not change as we ignore it.
        self.assertEqual(settings.PRBOARD_SETTINGS_FILE, PRBOARD_SETTINGS_FILE)

    def test_print_header(self):
        """ Test print_header """
        pass
