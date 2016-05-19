import os
import sys
import warnings
from distutils import log
from importlib import import_module
from unittest import TestSuite

import django
from django.apps import apps
from django.conf import settings
from django_jenkins.runner import CITestSuiteRunner, EXMLTestResult

__author__ = "Dariusz Rzepka <dariusz.rzepka@deployed.pl>"


class SetupTestSuite(TestSuite):
    """
    Test Suite configuring Django settings and using
    DiscoverRunner or DjangoTestSuiteRunner as the test runner.
    Also runs PEP8 and Coverage checks.
    """

    DEFAULT_OPTIONS = {
        'args': [],
        'coverage': False,
        'coverage_excludes': [],
        'coverage_format': 'xml',
        'coverage_rcfile': '',
        'csslint_exclude': '.min.css',
        'csslint_ignore': '',
        'failfast': False,
        'flake8-max-complexity': None,
        'interactive': True,
        'output_dir': 'reports',
        'pep8-exclude': None,
        'pep8-ignore': None,
        'pep8-max-line-length': None,
        'pep8-rcfile': None,
        'pep8-select': None,
        'project_apps_tests': True,
        'pyflakes_exclude_dirs': ['south_migrations'],
        'pylint_errors_only': False,
        'pylint_load_plugins': None,
        'pylint_rcfile': None,
        'verbosity': True,
    }

    def __init__(self, *args, **kwargs):
        self.configure()
        self.get_jenkins_tasks()
        self.options = self.DEFAULT_OPTIONS
        self.options.update(getattr(settings, 'SETUPTEST_JENKINS', {}))

        super(SetupTestSuite, self).__init__()

    def configure(self):
        """
        Configures Django settings.
        """
        try:
            test_settings = import_module('test_settings')
        except ImportError as e:
            log.info('ImportError: Unable to import test settings: %s' % e)
            sys.exit(1)

        setting_attrs = {}
        for attr in dir(test_settings):
            if '__' not in attr:
                setting_attrs[attr] = getattr(test_settings, attr)

        if not settings.configured:
            settings.configure(**setting_attrs)

        if hasattr(django, 'setup'):
            django.setup()

    def get_jenkins_tasks(self):
        tasks_list = getattr(settings, 'JENKINS_TASKS', ())
        tasks_cls = [import_module(module_name).Reporter
            for module_name in tasks_list]
        self.tasks = [task_cls() for task_cls in tasks_cls]

    def get_tested_locations(self):
        # TODO: add option to test specific labels
        locations = []

        if hasattr(settings, 'PROJECT_APPS'):
            test_labels = settings.PROJECT_APPS
        else:
            warnings.warn('No PROJECT_APPS settings, coverage gathered over all apps')
            test_labels = settings.INSTALLED_APPS

        for test_label in test_labels:
            app_config = apps.get_containing_app_config(test_label)
            if app_config is not None:
                locations.append(os.path.dirname(app_config.module.__file__))
            else:
                warnings.warn('No app found for test: {0}'.format(test_label))

        return locations

    def run_jenkins_tasks(self):
        if self.options['verbosity']:
            print("\nRunning jenkins tasks...")

        tested_locations = self.get_tested_locations()

        if self.options['coverage']:
            from django_jenkins.tasks.with_coverage import CoverageReporter
            coverage = CoverageReporter()

            if self.options['verbosity']:
                print('Storing coverage info...')

            coverage.save(tested_locations, self.options)

        # run reporters
        for task in self.tasks:
            if self.options['verbosity']:
                print('Executing {0}...'.format(task.__module__))
            task.run(tested_locations, **self.options)

        if self.options['verbosity']:
            print('Done')
        pass

    def run(self, result, *args, **kwargs):
        """
        Run the test, teardown the environment and generate reports.
        """

        self.test_runner = CITestSuiteRunner(
            resultclass=EXMLTestResult,
            **self.options)
        suite = self.test_runner.build_suite()

        # Create reports output dir
        output_dir = self.options['output_dir']
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        self.test_runner.setup_test_environment()
        old_config = self.test_runner.setup_databases()
        result = self.test_runner.run_suite(suite)
        self.test_runner.teardown_databases(old_config)
        self.test_runner.teardown_test_environment()

        if result.failures:
            sys.exit(bool(result.failures))

        self.run_jenkins_tasks()
        return result
