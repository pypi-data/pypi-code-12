import unittest
import mock

import github
from github import Requester


from prboard import utils, filters, settings, hub


class TestGithub(unittest.TestCase):
    def setUp(self):
        pass

    def test_github_init(self):
        """ Test if Github gets instantiated with addditional methods """
        g = hub.Github()
        self.assertTrue(hasattr(g, 'get_user_repos'))
        self.assertTrue(hasattr(g, 'get_org_repos'))

    @mock.patch.object(github.PaginatedList, "PaginatedList")
    def test_github_get_user_repos_raises_assert_error(self, mock_paginated_list):
        """ Test if Github.get_user_repos raises assertion error if since is not a valid value """
        g = hub.Github()
        with self.assertRaises(AssertionError):
            g.get_user_repos("kumar", "a")

    @mock.patch.object(github.PaginatedList, "PaginatedList")
    def test_github_get_user_repos_pass(self, mock_paginated_list):
        """ Test if Github.get_user_repos raises assertion error if since is not a valid value """
        args = [mock.MagicMock(), "", "", ""]
        data = [github.Repository.Repository(*args), github.Repository.Repository(*args), github.Repository.Repository(*args)]
        mock_paginated_list.return_value = data
        g = hub.Github()
        repos = g.get_user_repos("kumar")
        # Cannot use assert_called_once_with as the requester object gets an instance
        self.assertEqual(mock_paginated_list.call_args[0][0], github.Repository.Repository)
        self.assertEqual(mock_paginated_list.call_args[0][2], "/users/{}/repos".format("kumar"))
        self.assertEqual(repos, data)

    @mock.patch.object(github.PaginatedList, "PaginatedList")
    def test_github_get_org_repos_pass(self, mock_paginated_list):
        """ Test if Github.get_org_repos raises assertion error if since is not a valid value """
        args = [mock.MagicMock(), "", "", ""]
        data = [github.Repository.Repository(*args), github.Repository.Repository(*args), github.Repository.Repository(*args)]
        mock_paginated_list.return_value = data
        g = hub.Github()
        repos = g.get_org_repos("kumar")
        # Cannot use assert_called_once_with as the requester object gets an instance
        self.assertEqual(mock_paginated_list.call_args[0][0], github.Repository.Repository)
        self.assertEqual(mock_paginated_list.call_args[0][2], "orgs/{}/repositories".format("kumar"))
        self.assertEqual(repos, data)
