from __future__ import unicode_literals

from optparse import make_option
import os
from shutil import rmtree
from subprocess import Popen, PIPE

import django
from django.conf import settings as django_settings
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.test.utils import get_runner

from sbo_selenium.conf import settings
from sbo_selenium.testcase import sauce_sessions
from sbo_selenium.utils import DockerSelenium, OutputMonitor

if 'django_nose' in django_settings.INSTALLED_APPS:
    from django_nose.management.commands.test import Command as TestCommand
else:
    from django.core.management.commands.test import Command as TestCommand

OPTIONS = (
    (('-b', '--browser'), {'dest': 'browser_name', 'default': settings.SELENIUM_DEFAULT_BROWSER, 'help': 'Name of the browser to run the tests in (default is SELENIUM_DEFAULT_BROWSER)'}),
    (('-n',), {'dest': 'count', 'type': int, 'default': 1, 'help': 'Number of times to run each test'}),
    (('--command-executor',), {'dest': 'command_executor', 'help': 'URL of the Selenium server to use if not using Sauce Labs or directly launching a browser'}),
    (('--docker',), {'dest': 'docker', 'action': 'store_true', 'help': 'Start and use a standalone Selenium server in a Docker container (chrome or firefox only)'}),
    (('--platform',), {'dest': 'platform', 'help': 'OS and version thereof for the Sauce OnDemand VM to use'}),
    (('--browser-version',), {'dest': 'browser_version', 'help': 'Browser version for the Sauce OnDemand VM to use'}),
    (('--tunnel-identifier',), {'dest': 'tunnel_id', 'help': 'Sauce Connect tunnel identifier'}),
)


class Command(BaseCommand):
    """
    Django management command for running Selenium tests.
    """
    help = 'Run Selenium tests for this application'
    requires_model_validation = True
    # Command line arguments for Django 1.7 and below
    custom_options = tuple([make_option(*option[0], **option[1]) for option in OPTIONS])

    @property
    def use_argparse(self):
        return not (django.VERSION[0] == 1 and django.VERSION[1] < 8)

    def add_arguments(self, parser):
        """Command line arguments for Django 1.8+"""
        # Add the underlying test command arguments first
        test_command = TestCommand()
        test_command.add_arguments(parser)

        for option in OPTIONS:
            parser.add_argument(*option[0], **option[1])

    def create_parser(self, prog_name, subcommand):
        """
        Override the base create_parser() method to add this command's custom
        options in Django 1.7 and below.
        """
        if not self.use_argparse:
            self.__class__.option_list = TestCommand.option_list + self.custom_options
        parser = super(Command, self).create_parser(prog_name, subcommand)
        return parser

    @staticmethod
    def clean():
        """Clear out any old screenshots"""
        screenshot_dir = settings.SELENIUM_SCREENSHOT_DIR
        if screenshot_dir and os.path.isdir(screenshot_dir):
            rmtree(screenshot_dir, ignore_errors=True)

    def handle(self, *args, **options):
        """
        Run the specified Selenium test(s) the indicated number of times in
        the specified browser.
        """
        browser_name = options['browser_name']
        count = options['count']
        if len(args) > 0:
            tests = list(args)
        else:
            tests = settings.SELENIUM_DEFAULT_TESTS

        # Kill any orphaned chromedriver processes
        process = Popen(['killall', 'chromedriver'],
                        stderr=open(os.devnull, 'w'))
        process.wait()

        # Clear any old log and screenshots
        self.clean()

        docker = None
        sc_process = None
        selenium_process = None
        if options['docker']:
            if browser_name not in ['chrome', 'firefox']:
                self.stdout.write('Only chrome and firefox can currently be run in a Docker container')
                return
            docker = DockerSelenium(browser=browser_name,
                                    port=settings.SELENIUM_DOCKER_PORT,
                                    tag=settings.SELENIUM_DOCKER_TAG,
                                    debug=settings.SELENIUM_DOCKER_DEBUG)
        elif 'platform' in options and settings.SELENIUM_SAUCE_CONNECT_PATH:
            running, sc_process = self.verify_sauce_connect_is_running(options)
            if not running:
                return
        elif browser_name in ['opera', 'safari']:
            running, selenium_process = self.verify_selenium_server_is_running()
            if not running:
                return
        elif browser_name in ['ipad', 'iphone']:
            if not self.verify_appium_is_running():
                return

        # Make it so django-nose won't have nosetests choke on our parameters
        TestRunner = get_runner(django_settings)
        if hasattr(TestRunner, 'django_opts'):
            for option in OPTIONS:
                TestRunner.django_opts.extend(option[0])

        # Configure and run the tests
        try:
            if docker:
                docker.start()
                options['command_executor'] = docker.command_executor()
            self.update_environment(options)
            self.run_tests(tests, browser_name, count)
        finally:
            # Stop the Selenium Docker container, if running
            if docker and docker.container_id:
                docker.stop()

        # Kill Sauce Connect, if running
        if sc_process:
            sc_process.kill()

        # Kill the Selenium standalone server, if running
        if selenium_process:
            selenium_process.kill()

    def run_tests(self, tests, browser_name, count):
        """Configure and run the tests"""
        test_args = ['test'] + tests
        test_options = settings.SELENIUM_TEST_COMMAND_OPTIONS
        for i in range(count):
            msg = 'Test run %d using %s' % (i + 1, browser_name)
            self.stdout.write(msg)
            call_command(*test_args, **test_options)
            for session in sauce_sessions:
                self.stdout.write(session)
            self.stdout.flush()
            del sauce_sessions[:]

    @staticmethod
    def update_environment(options):
        """
        Populate the environment variables that need to be added for test
        execution to work correctly.  Most (but not all) of these are to match
        what the Jenkins Sauce OnDemand plugin would use for the test
        configuration that was specified on the command line.
        """
        env = os.environ
        # https://docs.djangoproject.com/en/1.6/topics/testing/tools/#liveservertestcase
        env['DJANGO_LIVE_TEST_SERVER_ADDRESS'] = settings.DJANGO_LIVE_TEST_SERVER_ADDRESS
        tunnel_id = options['tunnel_id']
        if tunnel_id:
            env['SAUCE_TUNNEL_ID'] = tunnel_id
        if 'SAUCE_API_KEY' in env:
            # Jenkins plugin has already configured the environment for us
            return
        env['SELENIUM_BROWSER'] = options['browser_name']
        if options['command_executor']:
            env['SELENIUM_COMMAND_EXECUTOR'] = options['command_executor']
        platform = options['platform']
        browser_version = options['browser_version']
        if not platform or not browser_version:
            # None of the following Sauce OnDemand stuff applies
            return
        if settings.SELENIUM_SAUCE_CONNECT_PATH:
            host = 'localhost'
            port = '4445'
        else:
            host = 'ondemand.saucelabs.com'
            port = '80'
        env.update({
            'SAUCE_API_KEY': settings.SELENIUM_SAUCE_API_KEY,
            'SAUCE_USER_NAME': settings.SELENIUM_SAUCE_USERNAME,
            'SELENIUM_BROWSER': options['browser_name'],
            'SELENIUM_HOST': host,
            'SELENIUM_PLATFORM': platform,
            'SELENIUM_PORT': port,
            'SELENIUM_VERSION': browser_version,
        })

    def verify_sauce_connect_is_running(self, options):
        """
        Start Sauce Connect, if it isn't already running.  Returns a tuple of
        two elements:

        * A boolean which is True if Sauce Connect is now running
        * The Popen object representing the process so it can be terminated
          later; if it was already running, this value is "None"
        """
        sc_path = settings.SELENIUM_SAUCE_CONNECT_PATH
        if len(sc_path) < 2:
            self.stdout.write('You need to configure SELENIUM_SAUCE_CONNECT_PATH')
            return False, None
        username = settings.SELENIUM_SAUCE_USERNAME
        if not username:
            self.stdout.write('You need to configure SELENIUM_SAUCE_USERNAME')
            return False, None
        key = settings.SELENIUM_SAUCE_API_KEY
        if not key:
            self.stdout.write('You need to configure SELENIUM_SAUCE_API_KEY')
            return False, None
        # Is it already running?
        process = Popen(['ps -e | grep "%s"' % key],
                        shell=True, stdout=PIPE)
        (grep_output, _grep_error) = process.communicate()
        grep_command = 'grep {}'.format(key)
        lines = grep_output.split('\n')
        for line in lines:
            if 'sc' in line and username in line and grep_command not in line:
                self.stdout.write('Sauce Connect is already running')
                return True, None
        self.stdout.write('Starting Sauce Connect')
        output = OutputMonitor()
        command = [sc_path, '-u', username, '-k', key]
        tunnel_id = options['tunnel_id']
        if tunnel_id:
            command.extend(['-i', tunnel_id])
        sc_process = Popen(command,
                           stdout=output.stream.input,
                           stderr=open(os.devnull, 'w'),
                           universal_newlines=True)
        ready_log_line = 'Connection established.'
        if not output.wait_for(ready_log_line, 60):
            self.stdout.write('Timeout starting Sauce Connect:\n')
            self.stdout.write('\n'.join(output.lines))
            return False, None
        return True, sc_process

    def verify_selenium_server_is_running(self):
        """
        Start the Selenium standalone server, if it isn't already running.
        Returns a tuple of two elements:

        * A boolean which is True if the server is now running
        * The Popen object representing the process so it can be terminated
          later; if the server was already running, this value is "None"
        """
        selenium_jar = settings.SELENIUM_JAR_PATH
        if len(selenium_jar) < 5:
            self.stdout.write('You need to configure SELENIUM_JAR_PATH')
            return False, None
        _jar_dir, jar_name = os.path.split(selenium_jar)
        # Is it already running?
        process = Popen(['ps -e | grep "%s"' % jar_name[:-4]],
                        shell=True, stdout=PIPE)
        (grep_output, _grep_error) = process.communicate()
        lines = grep_output.split('\n')
        for line in lines:
            if jar_name in line:
                self.stdout.write('Selenium standalone server is already running')
                return True, None
        self.stdout.write('Starting the Selenium standalone server')
        output = OutputMonitor()
        selenium_process = Popen(['java', '-jar', selenium_jar],
                                 stdout=open(os.devnull, 'w'),
                                 stderr=output.stream.input)
        ready_log_line = 'Selenium Server is up and running'
        if not output.wait_for(ready_log_line, 10):
            self.stdout.write('Timeout starting the Selenium server:\n')
            self.stdout.write('\n'.join(output.lines))
            return False, None
        return True, selenium_process

    def verify_appium_is_running(self):
        """Verify that Appium is running so it can be used for local iOS tests."""
        process = Popen(['ps -e | grep "Appium"'], shell=True, stdout=PIPE)
        (grep_output, _grep_error) = process.communicate()
        lines = grep_output.split('\n')
        for line in lines:
            if 'Appium.app' in line:
                self.stdout.write('Appium is already running')
                return True
        self.stdout.write('Please launch and configure Appium first')
        return False
