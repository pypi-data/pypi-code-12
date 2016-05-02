import os
import sys
import subprocess
import setuptools
from setuptools.command.build_ext import build_ext
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
        self._call('python3 -m pytest --cov=sets test')
        self._call('python3 -m pylint sets')
        self._call('python3 -m pylint test')
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


class BuildExtCommand(build_ext):
    """
    Fix Numpy build error when bundled as a dependency.
    From http://stackoverflow.com/a/21621689/1079110
    """

    def finalize_options(self):
        super().finalize_options()
        __builtins__.__NUMPY_SETUP__ = False
        import numpy
        self.include_dirs.append(numpy.get_include())


DESCRIPTION = 'Read datasets in a standard way.'

SETUP_REQUIRES = [
    'numpy',
]

INSTALL_REQUIRES = [
    'numpy',
    'requests',
    'nltk',
]

TESTS_REQUIRE = [
    'pytest',
    'pytest-cov',
    'pylint',
]


if __name__ == '__main__':
    setuptools.setup(
        name='sets',
        version='0.3.0',
        description=DESCRIPTION,
        url='http://github.com/danijar/sets',
        author='Danijar Hafner',
        author_email='mail@danijar.com',
        license='MIT',
        packages=['sets', 'sets.core', 'sets.dataset', 'sets.process'],
        setup_requires=SETUP_REQUIRES,
        install_requires=INSTALL_REQUIRES,
        tests_require=TESTS_REQUIRE + INSTALL_REQUIRES,
        cmdclass={'test': TestCommand, 'build_ext': BuildExtCommand},
    )
