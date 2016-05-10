from __future__ import absolute_import
import os

import mock

from deployer.config import ConfigStack
from deployer.action.importer import Importer

from .base import (
    Base,
    patch_env_status,
    skip_if_offline,
)


class Options(dict):

    def __getattr__(self, key):
        return self[key]


class ImporterTest(Base):

    def setUp(self):
        self.juju_home = self.mkdir()
        self.change_environment(JUJU_HOME=self.juju_home)
        self.options = Options({
            'bootstrap': False,
            'branch_only': False,
            'configs': [os.path.join(self.test_data_dir, 'wiki.yaml')],
            'debug': True,
            'deploy_delay': 0,
            'destroy_services': None,
            'diff': False,
            'find_service': None,
            'ignore_errors': False,
            'list_deploys': False,
            'no_local_mods': True,
            'no_relations': False,
            'overrides': None,
            'rel_wait': 60,
            'retry_count': 0,
            'series': None,
            'skip_unit_wait': False,
            'terminate_machines': False,
            'timeout': 2700,
            'update_charms': False,
            'verbose': True,
            'watch': False})

    @skip_if_offline
    @mock.patch('deployer.action.importer.time')
    def test_importer(self, mock_time):
        mock_time.time.return_value = 0
        # Trying to track down where this comes from http://pad.lv/1243827
        stack = ConfigStack(self.options.configs)
        deploy = stack.get('wiki')
        env = mock.MagicMock()
        patch_env_status(env, {'wiki': 1, 'db': 1})
        importer = Importer(env, deploy, self.options)
        importer.run()

        config = {'name': '$hi_world _are_you_there? {guess_who}'}
        self.assertEqual(
            env.method_calls[3], mock.call.deploy(
                'wiki', 'cs:precise/mediawiki',
                os.environ.get("JUJU_REPOSITORY", ""),
                config, None, 1, None, 'precise'))
        env.add_relation.assert_called_once_with('wiki', 'db')

    @skip_if_offline
    @mock.patch('deployer.action.importer.time')
    def test_importer_no_relations(self, mock_time):
        mock_time.time.return_value = 0
        self.options.no_relations = True
        stack = ConfigStack(self.options.configs)
        deploy = stack.get('wiki')
        env = mock.MagicMock()
        patch_env_status(env, {'wiki': 1, 'db': 1})
        importer = Importer(env, deploy, self.options)
        importer.run()
        self.assertFalse(env.add_relation.called)

    @skip_if_offline
    @mock.patch('deployer.action.importer.time')
    def test_importer_add_machine_series(self, mock_time):
        mock_time.time.return_value = 0
        self.options.configs = [
            os.path.join(self.test_data_dir, 'v4', 'series.yaml')]
        stack = ConfigStack(self.options.configs)
        deploy = stack.get(self.options.configs[0])
        env = mock.MagicMock()
        patch_env_status(env, {'mediawiki': 1, 'mysql': 1})
        importer = Importer(env, deploy, self.options)
        importer.run()

        self.assertEqual(env.add_machine.call_count, 2)
        env.add_machine.assert_has_calls([
            mock.call(series='precise', constraints='mem=512M'),
            mock.call(series='trusty', constraints='mem=512M'),
        ], any_order=True)

    @skip_if_offline
    @mock.patch('deployer.action.importer.time')
    def test_importer_existing_machine(self, mock_time):
        mock_time.time.return_value = 0
        self.options.configs = [
            os.path.join(self.test_data_dir, 'v4',
                         'container-existing-machine.yaml')]
        stack = ConfigStack(self.options.configs)
        deploy = stack.get(self.options.configs[0])
        env = mock.MagicMock()
        patch_env_status(env, {'mediawiki': 1, 'mysql': 1}, machines=[1])

        importer = Importer(env, deploy, self.options)
        importer.run()
        self.assertFalse(env.add_machine.called)
