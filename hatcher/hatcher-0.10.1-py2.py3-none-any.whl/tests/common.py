from click.testing import CliRunner
from mock import Mock, patch

from ..cli import utils
from ..core.brood_client import BroodClient as RealBroodClient
from ..core.model_registry import ModelRegistry
from ..core.v0.team import Team as RealTeam
from ..core.v0.user import User as RealUser
from ..core.v0.organization import Organization as RealOrganization
from ..core.v0.repository import (
    Repository as RealRepository,
    SinglePlatformRepository,
)


patch_brood_client = patch.object(utils, 'BroodClient')
patch_organization = patch.object(ModelRegistry, 'Organization')
patch_repository = patch.object(ModelRegistry, 'Repository')
patch_team = patch.object(ModelRegistry, 'Team')
patch_user = patch.object(ModelRegistry, 'User')


class MainTestingMixin(object):

    def setUp(self):
        self.runner = CliRunner()
        self.organization = 'acme'
        self.repository = 'dev'
        self.team = 'dev-team'
        self.platform = 'rh5-64'
        self.user = 'user@acme.org'

    def tearDown(self):
        pass

    def _mock_brood_client_class(self, BroodClient):
        BroodClient.return_value = brood_client = Mock(
            spec=RealBroodClient)
        BroodClient.from_url.return_value = brood_client
        brood_client.organization.return_value = Mock(
            spec=RealOrganization)
        return brood_client

    def _mock_organization_class(self, Organization):
        Organization.return_value = organization = Mock(spec=RealOrganization)
        organization.repository.return_value = Mock(
            spec=RealRepository)
        organization.team.return_value = Mock(spec=RealTeam)
        return organization

    def _mock_repository_class(self, Repository):
        Repository.return_value = repo = Mock(spec=RealRepository)
        repo.organization_name = self.organization
        repo.name = self.repository
        repo.platform.return_value = platform_repo = Mock(
            spec=SinglePlatformRepository)
        return repo, platform_repo

    def _mock_team_class(self, Team):
        Team.return_value = team = Mock(spec=RealTeam)
        team.name = self.team
        return team

    def _mock_user_class(self, User):
        User.return_value = user = Mock(spec=RealUser)
        user.email = self.user
        return user

    def assertOrganizationConstructedCorrectly(self, Organization):
        self.assertEqual(Organization.call_count, 1)
        self.assertEqual(
            Organization.call_args[0],
            (self.organization,),
        )
        self.assertIn('url_handler', Organization.call_args[1])

    def assertRepositoryConstructedCorrectly(self, Repository):
        self.assertEqual(Repository.call_count, 1)
        self.assertEqual(
            Repository.call_args[0],
            (self.organization, self.repository),
        )
        self.assertIn('url_handler', Repository.call_args[1])

    def assertTeamConstructedCorrectly(self, Team):
        self.assertEqual(Team.call_count, 1)
        self.assertEqual(
            Team.call_args[0],
            (self.organization, self.team),
        )
        self.assertIn('url_handler', Team.call_args[1])

    def assertUserConstructedCorrectly(self, User):
        self.assertEqual(User.call_count, 1)
        self.assertEqual(
            User.call_args[0],
            (self.organization, self.user),
        )
        self.assertIn('url_handler', User.call_args[1])
