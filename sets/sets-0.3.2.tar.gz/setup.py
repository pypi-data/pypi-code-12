import sys
import os
import subprocess
import setuptools
from setuptools.command.build_ext import build_ext


SETUP_REQUIRES = [
    'numpy',
]

INSTALL_REQUIRES = [
    'numpy',
    'requests',
    'nltk',
    'lxml',
    'definitions',
]


class Command(setuptools.Command):

    requires = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._returncode = 0

    def finalize_options(self):
        pass

    def run(self):
        if type(self).requires:
            self.distribution.fetch_build_eggs(type(self).requires)
            self.run_command('egg_info')
            self.reinitialize_command('build_ext', inplace=1)
            self.run_command('build_ext')
        self.__call__()
        if self._returncode:
            sys.exit(self._returncode)

    def call(self, command):
        env = os.environ.copy()
        env['PYTHONPATH'] = ''.join(':' + x for x in sys.path)
        self.announce('Run command: {}'.format(command), level=2)
        try:
            subprocess.check_call(command.split(), env=env)
        except subprocess.CalledProcessError as error:
            self._returncode = 1
            message = 'Command failed with exit code {}'
            message = message.format(error.returncode)
            self.announce(message, level=2)


class TestCommand(Command):

    requires = ['pytest', 'pytest-cov'] + INSTALL_REQUIRES
    description = 'run tests and create a coverage report'
    user_options = [('args=', None, 'args to forward to pytest')]

    def initialize_options(self):
        self.args = ''

    def __call__(self):
        self.call('python3 -m pytest --cov=sets test ' + self.args)


class LintCommand(Command):

    requires = ['pep8', 'pylint'] + INSTALL_REQUIRES
    description = 'run linters'
    user_options = [('args=', None, 'args to forward to pylint')]

    def initialize_options(self):
        self.args = ''

    def finalize_options(self):
        self.args += ' --rcfile=setup.cfg'

    def __call__(self):
        self.call('python3 -m pep8 sets test setup.py')
        self.call('python3 -m pylint sets ' + self.args)
        self.call('python3 -m pylint test ' + self.args)
        self.call('python3 -m pylint setup.py ' + self.args)


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


if __name__ == '__main__':
    setuptools.setup(
        name='sets',
        version='0.3.2',
        description='Read datasets in a standard way.',
        url='http://github.com/danijar/sets',
        author='Danijar Hafner',
        author_email='mail@danijar.com',
        license='MIT',
        packages=['sets', 'sets.core', 'sets.dataset', 'sets.process'],
        package_data={'sets': ['data/schema.yaml']},
        setup_requires=SETUP_REQUIRES,
        install_requires=INSTALL_REQUIRES,
        cmdclass={
            'test': TestCommand,
            'lint': LintCommand,
            'build_ext': BuildExtCommand,
        },
    )
