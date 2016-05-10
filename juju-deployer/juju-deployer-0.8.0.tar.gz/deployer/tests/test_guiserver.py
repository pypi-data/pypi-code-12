"""Tests for the GUI server bundles deployment support."""

from __future__ import absolute_import
from contextlib import contextmanager
import os
import shutil
import tempfile
import unittest

import mock
import yaml

from deployer import guiserver
from deployer.feedback import Feedback
from deployer.tests.base import (
    patch_env_status,
    skip_if_offline,
)


class TestGetDefaultGuiserverOptions(unittest.TestCase):

    def setUp(self):
        self.options = guiserver.get_default_guiserver_options()

    def test_option_keys(self):
        # All the required options are returned.
        # When adding/modifying options, ensure the defaults are sane for us.
        expected_keys = set([
            'bootstrap', 'branch_only', 'configs', 'debug', 'deploy_delay',
            'deployment', 'description', 'destroy_services', 'diff',
            'find_service', 'ignore_errors', 'juju_env', 'list_deploys',
            'no_local_mods', 'no_relations', 'overrides', 'rel_wait',
            'retry_count', 'series', 'skip_unit_wait', 'terminate_machines',
            'timeout', 'update_charms', 'verbose', 'watch'
        ])
        self.assertEqual(expected_keys, set(self.options.__dict__.keys()))

    def test_option_values(self):
        # The options values are suitable to be used by the GUI server.
        # When adding/modifying options, ensure the defaults are sane for us.
        options = self.options
        self.assertFalse(options.bootstrap)
        self.assertFalse(options.branch_only)
        self.assertIsNone(options.configs)
        self.assertFalse(options.debug)
        self.assertEqual(0, options.deploy_delay)
        self.assertIsNone(options.deployment)
        self.assertFalse(options.destroy_services)
        self.assertFalse(options.diff)
        self.assertIsNone(options.find_service)
        self.assertTrue(options.ignore_errors)
        self.assertEqual(os.getenv("JUJU_ENV"), options.juju_env)
        self.assertFalse(options.list_deploys)
        self.assertTrue(options.no_local_mods)
        self.assertIsNone(options.overrides)
        self.assertEqual(60, options.rel_wait)
        self.assertEqual(0, options.retry_count)
        self.assertIsNone(options.series)
        self.assertFalse(options.terminate_machines)
        self.assertEqual(2700, options.timeout)
        self.assertFalse(options.update_charms)
        self.assertFalse(options.verbose)
        self.assertFalse(options.watch)


class TestDeploymentError(unittest.TestCase):

    def test_error(self):
        # A single error is properly stored and represented.
        exception = guiserver.DeploymentError(['bad wolf'])
        self.assertEqual(['bad wolf'], exception.errors)
        self.assertEqual('bad wolf', str(exception))

    def test_multiple_errors(self):
        # Multiple deployment errors are properly stored and represented.
        errors = ['error 1', 'error 2']
        exception = guiserver.DeploymentError(errors)
        self.assertEqual(errors, exception.errors)
        self.assertEqual('error 1\nerror 2', str(exception))


class TestGUIDeployment(unittest.TestCase):

    def setUp(self):
        # Set up a GUIDeployment instance and a Feedback object.
        self.deployment = guiserver.GUIDeployment('mybundle', 'mydata', 4)
        self.feedback = Feedback()

    def test_valid_deployment(self):
        # If the bundle is well formed, the deployment proceeds normally.
        self.assertIsNone(self.deployment._handle_feedback(self.feedback))

    def test_warnings(self):
        # Warning messages are properly logged.
        self.feedback.warn('we are the Borg')
        with mock.patch.object(self.deployment, 'log') as mock_log:
            self.deployment._handle_feedback(self.feedback)
        mock_log.warning.assert_called_once_with('we are the Borg')

    def test_errors(self):
        # A DeploymentError is raised if errors are found in the bundle.
        self.feedback.error('error 1')
        self.feedback.error('error 2')
        with self.assertRaises(guiserver.DeploymentError) as cm:
            self.deployment._handle_feedback(self.feedback)
        self.assertEqual(['error 1', 'error 2'], cm.exception.errors)


class DeployerFunctionsTestMixin(object):
    """Base set up for the functions that make use of the juju-deployer."""

    apiurl = 'wss://api.example.com:17070'
    username = 'who'
    password = 'Secret!'
    name = 'mybundle'
    bundle = yaml.safe_load("""
      services:
        wordpress:
          charm: "cs:precise/wordpress-20"
          num_units: 1
          options:
            debug: "no"
            engine: nginx
            tuning: single
          annotations:
            "gui-x": "425.347"
            "gui-y": "414.547"
        mysql:
          charm: "cs:precise/mysql-28"
          num_units: 2
          constraints:
            arch: i386
            mem: 4G
            cpu-cores: 4
          annotations:
            "gui-x": "494.347"
            "gui-y": "164.547"
      relations:
        - - "mysql:db"
          - "wordpress:db"
      series: precise
    """)

    def check_environment_life(self, mock_environment):
        """Check the calls executed on the given mock environment.

        Ensure that, in order to retrieve the list of currently deployed
        services, the environment is instantiated, connected, env.status is
        called and then the connection is closed.
        """
        mock_environment.assert_called_once_with(
            self.apiurl, self.username, self.password)
        mock_env_instance = mock_environment()
        mock_env_instance.connect.assert_called_once_with()
        mock_env_instance.status.assert_called_once_with()
        mock_env_instance.close.assert_called_once_with()

    @contextmanager
    def assert_overlapping_services(self, mock_environment):
        """Ensure a ValueError is raised in the context manager block.

        The given mock environment object is set up so that its status
        simulates an existing service. The name of this service overlaps with
        the name of one of the services in the bundle.
        """
        mock_env_instance = mock_environment()
        mock_env_instance.status.return_value = {'services': {'mysql': {}}}
        # Ensure a ValueError is raised by the code in the context block.
        with self.assertRaises(ValueError) as context_manager:
            yield
        # The error reflects the overlapping service name.
        error = str(context_manager.exception)
        self.assertEqual('service(s) already in the environment: mysql', error)
        # Even if an error occurs, the environment connection is closed.
        mock_env_instance.close.assert_called_once_with()


@skip_if_offline
@mock.patch('deployer.guiserver.GUIEnvironment')
class TestValidate(DeployerFunctionsTestMixin, unittest.TestCase):

    def test_validation(self, mock_environment):
        # The validation is correctly run.
        guiserver.validate(
            self.apiurl, self.username, self.password, self.bundle)
        # The environment is correctly instantiated and used.
        self.check_environment_life(mock_environment)

    def test_overlapping_services(self, mock_environment):
        # The validation fails if the bundle includes a service name already
        # present in the Juju environment.
        with self.assert_overlapping_services(mock_environment):
            guiserver.validate(
                self.apiurl, self.username, self.password, self.bundle)


@skip_if_offline
@mock.patch('deployer.guiserver.GUIEnvironment')
class TestImportBundle(DeployerFunctionsTestMixin, unittest.TestCase):

    # The options attribute simulates the options passed to the Importer.
    options = guiserver.get_default_guiserver_options()

    @contextmanager
    def patch_juju_home(self):
        """Patch the value used by the bundle importer as Juju home."""
        base_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, base_dir)
        juju_home = os.path.join(base_dir, 'juju-home')
        with mock.patch('deployer.guiserver.JUJU_HOME', juju_home):
            try:
                yield juju_home
            finally:
                del os.environ['JUJU_HOME']

    def import_bundle(self, version=4):
        """Call the import_bundle function."""
        guiserver.import_bundle(
            self.apiurl, self.username, self.password, self.name, self.bundle,
            version, self.options)

    def cleanup_series_path(self):
        """Remove the series path created by the Deployment object."""
        if os.path.isdir('precise'):
            os.rmdir('precise')

    @mock.patch('deployer.guiserver.Importer')
    def test_importing_bundle(self, mock_importer, mock_environment):
        # The juju-deployer importer is correctly set up and run.
        with self.patch_juju_home():
            self.import_bundle()
        # The environment is correctly instantiated and used.
        self.check_environment_life(mock_environment)
        # The importer is correctly instantiated.
        self.assertEqual(1, mock_importer.call_count)
        importer_args = mock_importer.call_args[0]
        self.assertEqual(3, len(importer_args))
        env, deployment, options = importer_args
        # The first argument passed to the importer is the environment.
        self.assertIs(mock_environment(), env)
        # The second argument is the deployment object.
        self.assertIsInstance(deployment, guiserver.GUIDeployment)
        self.assertEqual(self.name, deployment.name)
        self.assertEqual(self.bundle, deployment.data)
        # The third and last argument is the options object.
        self.assertIs(self.options, options)
        # The importer is started.
        mock_importer().run.assert_called_once_with()

    def test_overlapping_services(self, mock_environment):
        # The import fails if the bundle includes a service name already
        # present in the Juju environment.
        with self.assert_overlapping_services(mock_environment):
            with self.patch_juju_home():
                self.import_bundle()

    @mock.patch('deployer.guiserver.Importer')
    def test_juju_home(self, mock_importer, mock_environment):
        # A customized Juju home is created and used during the import process.
        with self.patch_juju_home() as juju_home:
            assert not os.path.isdir(juju_home), 'directory should not exist'

            def run():
                # Ensure JUJU_HOME is included in the context when the Importer
                # instance is run.
                self.assertEqual(juju_home, os.getenv('JUJU_HOME'))
            mock_importer().run = run
            self.import_bundle()
        # The JUJU_HOME directory has been created.
        self.assertTrue(os.path.isdir(juju_home))

    @mock.patch('time.sleep')
    def test_importer_behavior(self, mock_sleep, mock_environment):
        # The importer executes the expected environment calls.
        self.addCleanup(self.cleanup_series_path)
        patch_env_status(mock_environment(), {'mysql': 1, 'wordpress': 1})
        mock_environment.reset_mock()
        with self.patch_juju_home():
            self.import_bundle(version=3)
        mock_sleep.assert_has_calls([mock.call(5.1), mock.call(60)])
        # If any of the calls below fails, then we have to change the
        # signatures of deployer.guiserver.GUIEnvironment methods.
        mock_environment.assert_called_once_with(
            self.apiurl, self.username, self.password)
        mock_environment().assert_has_calls([
            mock.call.connect(),
            mock.call.status(),
            mock.call.deploy(
                'mysql', 'cs:precise/mysql-28', '', None,
                {'arch': 'i386', 'cpu-cores': 4, 'mem': '4G'}, 2, None,
                'precise'),
            mock.call.set_annotation(
                'mysql', {'gui-y': '164.547', 'gui-x': '494.347'}),
            mock.call.deploy(
                'wordpress', 'cs:precise/wordpress-20', '',
                {'debug': 'no', 'engine': 'nginx', 'tuning': 'single'},
                None, 1, None, 'precise'),
            mock.call.set_annotation(
                'wordpress', {'gui-y': '414.547', 'gui-x': '425.347'}),
            mock.call.add_units('mysql', 1),
            mock.call.add_relation('mysql:db', 'wordpress:db'),
            mock.call.close(),
        ], any_order=True)

    def test_deployment_errors(self, mock_environment):
        # A DeploymentError is raised if the deployment fails.
        bundle = {
            'services': {
                'wordpress': {
                    'charm': 'cs:precise/wordpress-20',
                    'options': {'no-such-option': 42},  # Invalid options.
                },
                'mysql': {
                    'charm': 'cs:precise/mysql-28',
                    'options': {'bad': 'wolf'},  # Invalid options.
                },
            },
        }
        version = 4
        self.addCleanup(self.cleanup_series_path)
        with self.patch_juju_home():
            with self.assertRaises(guiserver.DeploymentError) as cm:
                guiserver.import_bundle(
                    self.apiurl, self.username, self.password, self.name,
                    bundle, version, self.options)
        expected_errors = set([
            'Invalid config charm cs:precise/wordpress-20 no-such-option=42',
            'Invalid config charm cs:precise/mysql-28 bad=wolf',
        ])
        self.assertEqual(expected_errors, set(cm.exception.errors))
