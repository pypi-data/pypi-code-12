from __future__ import absolute_import, division, print_function

from .requirements import scan_directory
from glob import glob
from os import path
from os import environ
from pandora import Version
from pandora.compat import ConfigParser
from setuptools import find_packages
from setuptools import setup
from subprocess import PIPE
from subprocess import Popen

import re
import sys

try:
    import click
except ImportError:
    click = None

_version_re = re.compile(
    '^'
    '(\d+)\.(\d+)\.(\d+)'  # minor, major, patch
    '(-[0-9A-Za-z-\.]+)?'  # pre-release
    '(\+[0-9A-Za-z-\.]+)?'  # build
    '$')


class Package(object):
    """Package information and helpers.

    :param package_name: Name of your package.
    :param setup_path: Base directory containing `setup.py`.
    :param package_path: Directory containing your package.
    :param meta: Meta data from your package `__init__.py`.

    :type package_name: str
    :type setup_path: str
    :type package_path: str
    :type meta: assemble.assemble.Meta

    """

    def __init__(self, package_name, setup_path, package_path):
        self.package_name = package_name
        self.setup_path = setup_path
        self.package_path = package_path
        self.meta = Meta(self.read_from_package('__init__.py'))

    def read_from_setup(self, filename):
        """Read contents from a file in the setup directory.

        :param filename: Filename to read.

        :type filename: str

        :rtype: str
        """
        with open(self.get_filename_setup(filename)) as stream:
            return stream.read()

    def read_from_package(self, filename):
        """Read contents from a file in the package directory.

        :param filename: Filename to read.

        :type filename: str

        :rtype: str
        """
        with open(self.get_filename_package(filename)) as stream:
            return stream.read()

    def get_filename_setup(self, filename):
        """Get the full filename of a file in the setup path.

        :param filename: Filename to locate.

        :type filename: str

        :rtype: str
        """
        return path.join(self.setup_path, filename)

    def get_filename_package(self, filename):
        """Get the full filename of a file in the package path.

        :param filename: Filename to locate.

        :type filename: str

        :rtype: str
        """
        return path.join(self.package_path, filename)

    def setup(self, keywords, classifiers, install_requires=None, **kwargs):
        """Run `setuptools.setup` using the meta-data and `README.rst`

        :param keywords: A list of keywords about your package.
        :param classifiers: A list of classifiers about your package.
        :param install_requires: All requirements to install, when `None`
            it reads them from `requirements.txt`.
        :param \*\*kwargs: Any other arguments you want to pass.

        :type keywords: list
        :type classifiers: list
        :type install_requires: list

        :rtype: distutils.dist.Distribution

        """
        if install_requires is None:
            install_requires = [
                line.strip() for line
                in self.read_from_setup('requirements.txt').split('\n')]

        return setup(name=self.meta.title,
                     description=self.meta.description,
                     license=self.meta.license,
                     url=self.meta.uri,
                     version=self.meta.version,
                     author=self.meta.author,
                     author_email=self.meta.email,
                     maintainer=self.meta.author,
                     maintainer_email=self.meta.email,
                     keywords=keywords,
                     long_description=self.read_from_setup('README.rst'),
                     packages=[self.package_name],
                     package_dir={"": "src"},
                     zip_safe=False,
                     classifiers=classifiers,
                     install_requires=install_requires,
                     **kwargs)

    def get_tox_environments(self):
        """Retrieve a list of tox-environments.

        :rtype: list

        """
        config = ConfigParser()
        config.read(self.get_filename_setup('tox.ini'))
        return filter(lambda e: not e.startswith('coverage-'),
                      config.get('tox', 'envlist').split(','))

    def recreate_tox(self, environments):
        """Recreate tox-environments.

        :param environments: Which environments to recreate.

        :type environments: list

        :rtype: list

        """
        req_txt = self.get_filename_setup('requirements.txt')
        req_dev_txt = self.get_filename_setup('requirements-dev.txt')

        req_mtimes = list()
        env_mtimes = list()

        if path.exists(req_txt):
            req_mtimes.append(path.getmtime(req_txt))
        if path.exists(req_dev_txt):
            req_mtimes.append(path.getmtime(req_dev_txt))

        for environment in environments:
            env_path = self.get_filename_setup('.tox/' + environment)
            if path.exists(env_path):
                env_mtimes.append(path.getmtime(env_path))

        if len(env_mtimes) and max(req_mtimes) > min(env_mtimes):
            run('tox', '--recreate', '--notest')

    def run_tests(self, environments=None, coverage=True):
        """Run tox-tests.

        :param environments: Which environments to test, defaults to all
            environments.
        :param coverage: Capture coverage from all tests, [default `True`].

        :type environments: list
        :type coverage: bool

        """
        if environments is None:
            environments = self.get_tox_environments()

        self.recreate_tox(environments)

        if coverage:
            run('coverage', 'erase')

        run('detox', '-e', ','.join(environments))

        if coverage:
            print('')
            run('coverage', 'combine')
            run('coverage', 'report')

            if path.exists(self.get_filename_setup('.coveralls.yml')):
                run('coveralls')

            print('')

    def assert_git_is_clean(self):
        """Assert that there are no GIT changes pending."""
        run('git', 'fetch', silent=True)

        if len(run('git', 'diff', '--exit-code',
                   capture=True, silent=True)):
            raise RuntimeError('There are modified files in your repository.')

        if len(run('git', 'diff', '--cached', '--exit-code',
                   capture=True, silent=True)):
            raise RuntimeError('There are staged files in your repository.')

        if int(run('git', 'rev-list', 'HEAD...origin/master', '--count',
                   capture=True, silent=True)):
            raise RuntimeError('Your repository is ahead/behind the origin.')

        return True

    def get_git_tags(self):
        """Retrieve all tags from GIT.

        :rtype: list

        """
        return run('git', 'tag', capture=True, silent=True).split('\n')

    def patch_version(self, version):
        """Patch package version in `__init__.py`.

        This will also set the `meta.version` to the new version.

        :param version: The new version.

        :type version: str

        """
        if not Version.check(version):
            click.secho('Invalid version value `{:s}`.'.format(version),
                        fg='red')
            click.Abort()

        assert version not in self.get_git_tags()

        message = 'Bumping {:s} -- {:s} to {:s}, are you sure?'.format(
            self.meta.title, self.meta.version, version)

        click.confirm(message, abort=True, default=True)

        contents = self.read_from_package('__init__.py')
        contents = re.sub(
            r'__version__ = ([\'"]){:s}\1'.format(
                re.escape(self.meta.version)),
            r'__version__ = \g<1>{:s}\g<1>'.format(version),
            contents)

        with open(self.get_filename_package('__init__.py'), 'w') as stream:
            stream.write(contents)

        self.meta.version = version

    def build_distribution(self, verify=True):
        """Build distribution that can be uploaded to PyPI.

        :param verify: Verify the build (checks version) [default `True].

        :type verify: bool

        """
        # -- Build
        click.secho('Building sdist & bdist_wheel', fg='yellow')
        run('python', 'setup.py', 'sdist', 'bdist_wheel', silent=True)

        # -- Verify sdist
        if verify:
            packages = [
                'dist/{:s}-{:s}.tar.gz'.format(
                    self.meta.title, self.meta.version),
                'dist/{:s}-{:s}-py2.py3-none-any.whl'.format(
                    self.meta.title, self.meta.version),
            ]

            for package in packages:
                package_name = package.lower().split('/')[-1].strip('-')
                name = 'venv-' + re.sub('[^a-z0-9_]+', '-', package_name)

                click.secho('Starting virtualenv {:s}'.format(name),
                            fg='yellow')
                try:
                    run('virtualenv', name, silent=True)
                    run(name + '/bin/pip', 'install', '-r',
                        self.get_filename_setup('requirements-dev.txt'),
                        silent=True)
                    run(name + '/bin/pip', 'install', package, silent=True)

                    command = 'import {0:s}; print {0:s}.__version__'.format(
                        self.meta.package)

                    outcome = run(name + '/bin/python', '-c', command,
                                  capture=True)

                    assert outcome.strip() == self.meta.version

                    msg = 'Version of {:s} matches!\n'.format(
                        self.meta.title)
                    print(msg)
                finally:
                    run('rm', '-rf', name)

    def register_pypi(self, environment=None):
        """Register package to PyPI

        :param environment: Which environment to run on.

        :type environment: str

        """
        environment = self.get_environment(environment)
        run('python', 'setup.py', 'register', '-r', environment)

    def git_tag(self):
        """Tag GIT version (add to __init__, commit, push, tag, push)."""
        run('git', 'add', self.get_filename_package('__init__.py'))
        run('git', 'commit', '-m', 'Bump version to {:s}.'.format(
            self.meta.version))
        run('git', 'push')
        run('git', 'tag', 'v' + self.meta.version)
        run('git', 'push', 'origin', '--tags')

    def upload_to_pypi(self, environment=None):
        """Upload builds to PyPI, use `build_distribution` for new builds.

        :param environment: Which environment to run on.

        :type environment: str

        """
        environment = self.get_environment(environment)
        search = 'dist/{:s}-{:s}*'.format(self.meta.title, self.meta.version)

        for filename in glob(search):
            run('twine', 'upload', '-r', environment, filename)

    def upload_documentation(self, environment=None):
        """Upload documentation to PyPI.

        :param environment: Which environment to run on.

        :type environment: str

        """
        environment = self.get_environment(environment)
        run('python', 'setup.py', 'upload_docs', '-r', environment)

    def get_requirements(self, named=False, equal=False):
        """Retrieve requirements of the package (scan using AST).

        :param named: Add name of the module found [default `False`].
        :param equal: Set requirment to `'=='` for equal, otherwise it
            will be `'>='` [default `False`].

        :type named: str
        :type equal: bool

        """
        not_found = list()
        found = list()

        for module_name, distribution in scan_directory(self.package_path):
            if not distribution:
                not_found.append(module_name)
            else:
                if named:
                    found.append('# - {}'.format(module_name))

                if equal:
                    found.append(distribution)
                else:
                    found.append(distribution.replace('==', '>='))

        return found, not_found

    def get_environment(self, environment):
        """When `environment` is `None` use the version to determine.

        When the version is *in development*, it will return the `'test'`
        environment, otherwise it will return `'pypi'`.

        :param environment: Name of the PyPI environment, `None` for
            automatic discovery.

        :type environment: str

        :rtype: str

        """
        if environment is None:
            version = Version(self.meta.version)
            if version.dev:
                return 'test'
            else:
                return 'pypi'
        else:
            return environment


class Meta(object):
    """Meta data about the package read from `__init__.py` file.

    It scans for `__variable__ = ''` defined variables and adds it to the
    Meta class. It requires all the keywords it scans for.

    :param author: Name of the author `__author__`.
    :param description: Description of the package `__description__`.
    :param email: Email address of author `__email__`.
    :param license: License definition `__license__`.
    :param package: Name of the package `__package__`.
    :param title: Title of the package `__title__`.
    :param uri: URI of package source `__uri__`.
    :param version: Current version `__version__`.

    :type author: str
    :type description: str
    :type email: str
    :type license: str
    :type package: str
    :type title: str
    :type uri: str
    :type version: str

    """

    def __init__(self, content):
        keywords = [
            'author', 'description', 'email', 'license',
            'package', 'title', 'uri', 'version',
        ]

        self.author = None
        self.description = None
        self.email = None
        self.license = None
        self.package = None
        self.title = None
        self.uri = None
        self.version = None

        def find(name):
            match = re.search(
                r'^__{:s}__ = ([\'"])(.+?)\1'.format(name),
                content, re.M)
            if not match:
                message = 'Unable to find __{:s}__ string.'.format(name)
                raise ValueError(message)
            return match.group(2)

        for keyword in keywords:
            setattr(self, keyword, find(keyword))


def get_package(origin='.', search='src'):
    """Get package from current directory.

    This method tries to locate your package in the current directory. Use
    this in your `setup.py`.

    :param origin: Where to start looking, this should be the directory
        containing your `setup.py`.
    :param search: Directory containing the source of your package.

    :type origin: str
    :type search: str

    :rtype: assemble.Package
    """
    origin = path.abspath(origin)
    directory = path.join(origin, search)

    if not path.exists(directory):
        raise ValueError('Package could not be loaded.')

    packages = find_packages(where=directory)

    if len(packages) > 1:
        packages = find_packages(where=origin)

        if search in packages:
            package_name = search
            package_path = path.join(origin, search)
        else:
            raise ValueError('Package not found in %s' % packages)
    elif len(packages) == 1:
        package_name = packages[0]
        package_path = path.join(origin, search, package_name)
    else:
        raise ValueError('No packages were found.')

    return Package(package_name, origin, package_path)


def run(*cmd, **kwargs):
    """Simply run a process, tweaked for internal use.

    Passes current environment!

    :param silent: Optional *keyword* to suppress any stdout.
    :param capture: Optional *keyword* to capture stdout.

    """
    silent = kwargs.get('silent') is True
    capture = kwargs.get('capture') is True
    env = environ.copy()
    env.update(kwargs.get('env', dict()))

    if silent or capture:
        proc = Popen(cmd, stdout=PIPE, env=env)

        lines = list()
        for line in iter(proc.stdout.readline, ''):
            if not silent:
                print(line.replace('\n', '').replace('\r', ''))
                sys.stdout.flush()
            lines.append(line)

        return ''.join(lines)
    else:
        proc = Popen(cmd, env=env)
        proc.wait()
