from hatcher.testing import unittest
from hatcher.tests.common import (
    MainTestingMixin,
    patch_repository,
    patch_team,
    patch_user,
)
from hatcher.cli import main


class TestMainTeamActions(MainTestingMixin, unittest.TestCase):

    @patch_team
    def test_team_metadata(self, Team):
        # Given
        metadata = {'name': 'team'}
        expected = '{0}\n'.format(metadata)
        team = self._mock_team_class(Team)
        get_metadata = team.metadata
        get_metadata.return_value = metadata

        args = ['--url', 'brood-dev.invalid', 'teams', 'metadata',
                self.organization, self.team]

        # When
        result = self.runner.invoke(main.hatcher, args=args)

        # Then
        self.assertEqual(result.exit_code, 0)
        get_metadata.assert_called_once_with()
        self.assertEqual(result.output, expected)

    @patch_team
    def test_list_repositories(self, Team):
        # Given
        repositories = ["repository1", "repository2"]
        expected = '{0}\n'.format('\n'.join(sorted(repositories)))
        team = self._mock_team_class(Team)
        list_repositories = team.list_repositories
        list_repositories.return_value = repositories

        args = ['--url', 'brood-dev.invalid', 'teams', 'repositories', 'list',
                self.organization, self.team]

        # When
        result = self.runner.invoke(main.hatcher, args=args)

        # Then
        self.assertEqual(result.exit_code, 0)
        list_repositories.assert_called_once_with()
        self.assertEqual(result.output, expected)

    @patch_repository
    @patch_team
    def test_add_repository_to_team(self, Team, Repository):
        # Given
        team = self._mock_team_class(Team)
        repository, _ = self._mock_repository_class(Repository)
        add_repository = team.add_repository

        args = ['--url', 'brood-dev.invalid', 'teams', 'repositories', 'add',
                self.organization, self.team, self.repository]

        # When
        result = self.runner.invoke(main.hatcher, args=args)

        # Then
        self.assertEqual(result.exit_code, 0)
        add_repository.assert_called_once_with(repository)

    @patch_repository
    @patch_team
    def test_remove_repository_from_team(self, Team, Repository):
        # Given
        team = self._mock_team_class(Team)
        repository, _ = self._mock_repository_class(Repository)
        remove_repository = team.remove_repository

        args = ['--url', 'brood-dev.invalid', 'teams', 'repositories',
                'remove', self.organization, self.team, self.repository]

        # When
        result = self.runner.invoke(main.hatcher, args=args)

        # Then
        self.assertEqual(result.exit_code, 0)
        remove_repository.assert_called_once_with(repository)

    @patch_repository
    @patch_team
    def test_query_team_repository_true(self, Team, Repository):
        # Given
        team = self._mock_team_class(Team)
        repository, _ = self._mock_repository_class(Repository)
        query_repository_access = team.query_repository_access
        query_repository_access.return_value = True

        args = ['--url', 'brood-dev.invalid', 'teams', 'repositories', 'query',
                self.organization, self.team, self.repository]

        # When
        result = self.runner.invoke(main.hatcher, args=args)

        # Then
        self.assertEqual(result.exit_code, 0)
        query_repository_access.assert_called_once_with(repository)
        self.assertRegexpMatches(
            result.output, r'has access to')

    @patch_repository
    @patch_team
    def test_query_team_repository_false(self, Team, Repository):
        # Given
        team = self._mock_team_class(Team)
        repository, _ = self._mock_repository_class(Repository)
        query_repository_access = team.query_repository_access
        query_repository_access.return_value = False

        args = ['--url', 'brood-dev.invalid', 'teams', 'repositories', 'query',
                self.organization, self.team, self.repository]

        # When
        result = self.runner.invoke(main.hatcher, args=args)

        # Then
        self.assertEqual(result.exit_code, 1)
        query_repository_access.assert_called_once_with(repository)
        self.assertRegexpMatches(
            result.output, r'does not have access to')

    @patch_team
    def test_list_users(self, Team):
        # Given
        users = ["user1", "user2"]
        expected = '{0}\n'.format('\n'.join(sorted(users)))
        team = self._mock_team_class(Team)
        list_users = team.list_users
        list_users.return_value = users

        args = ['--url', 'brood-dev.invalid', 'teams', 'members', 'list',
                self.organization, self.team]

        # When
        result = self.runner.invoke(main.hatcher, args=args)

        # Then
        self.assertEqual(result.exit_code, 0)
        list_users.assert_called_once_with()
        self.assertEqual(result.output, expected)

    @patch_user
    @patch_team
    def test_add_user_to_team(self, Team, User):
        # Given
        team = self._mock_team_class(Team)
        user = self._mock_user_class(User)
        add_user = team.add_user

        args = ['--url', 'brood-dev.invalid', 'teams', 'members', 'add',
                self.organization, self.team, self.user]

        # When
        result = self.runner.invoke(main.hatcher, args=args)

        # Then
        self.assertEqual(result.exit_code, 0)
        add_user.assert_called_once_with(user)

    @patch_user
    @patch_team
    def test_remove_user_from_team(self, Team, User):
        # Given
        team = self._mock_team_class(Team)
        user = self._mock_user_class(User)
        remove_user = team.remove_user

        args = ['--url', 'brood-dev.invalid', 'teams', 'members', 'remove',
                self.organization, self.team, self.user]

        # When
        result = self.runner.invoke(main.hatcher, args=args)

        # Then
        self.assertEqual(result.exit_code, 0)
        remove_user.assert_called_once_with(user)

    @patch_user
    @patch_team
    def test_query_team_member_true(self, Team, User):
        # Given
        team = self._mock_team_class(Team)
        user = self._mock_user_class(User)
        query_user_access = team.query_user_access
        query_user_access.return_value = True

        args = ['--url', 'brood-dev.invalid', 'teams', 'members', 'query',
                self.organization, self.team, self.user]

        # When
        result = self.runner.invoke(main.hatcher, args=args)

        # Then
        self.assertEqual(result.exit_code, 0)
        query_user_access.assert_called_once_with(user)
        self.assertRegexpMatches(
            result.output, r'has access to')

    @patch_user
    @patch_team
    def test_query_team_member_false(self, Team, User):
        # Given
        team = self._mock_team_class(Team)
        user = self._mock_user_class(User)
        query_user_access = team.query_user_access
        query_user_access.return_value = False

        args = ['--url', 'brood-dev.invalid', 'teams', 'members', 'query',
                self.organization, self.team, self.user]

        # When
        result = self.runner.invoke(main.hatcher, args=args)

        # Then
        self.assertEqual(result.exit_code, 1)
        query_user_access.assert_called_once_with(user)
        self.assertRegexpMatches(
            result.output, r'does not have access to')
