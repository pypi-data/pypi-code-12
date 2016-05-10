import os
import sys
import subprocess
import setuptools
from setuptools.command.test import test


class TestCommand(test):

    description = 'run tests, linters and create a coverage report'
    user_options = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.returncode = 0

    def finalize_options(self):
        super().finalize_options()
        # New setuptools don't need this anymore, thus the try block.
        try:
            # pylint: disable=attribute-defined-outside-init
            self.test_args = []
            self.test_suite = 'True'
        except AttributeError:
            pass

    def run_tests(self):
        self._call('python3 -m pytest --cov=easycrf/tests')
        self._call('python3 -m pylint easycrf/feature_training')
        self._call('python3 -m pylint tests')
        self._call('python3 -m pylint setup.py')
        self._check()

    def _call(self, command):
        env = os.environ.copy()
        env['PYTHONPATH'] = ''.join(':' + x for x in sys.path)
        print('Run command', command)
        try:
            subprocess.check_call(command.split(), env=env)
        except subprocess.CalledProcessError as error:
            print('Command failed with exit code', error.returncode)
            self.returncode = 1

    def _check(self):
        if self.returncode:
            sys.exit(self.returncode)


DESCRIPTION = 'Make it easy to define features for crf models.'

INSTALL_REQUIRES = [
    'nltk',
]

TESTS_REQUIRE = [
    'pytest',
    'pytest-cov',
    'pylint',
]

if __name__ == '__main__':
    setuptools.setup(
        name='easycrf',
        version='0.1.0',
        description=DESCRIPTION,
        url='https://github.com/bitbender/NLPTools',
        author='Patrick Kuhn',
        author_email='patrick.kuhn@student.hpi.de',
        license='Apache Software License',
        packages=['easycrf'],
        # setup_requires=SETUP_REQUIRES,
        install_requires=INSTALL_REQUIRES,
        tests_require=TESTS_REQUIRE + INSTALL_REQUIRES,
        cmdclass={'test': TestCommand},
    )
