# py2deb: Python to Debian package converter.
#
# Authors:
#  - Arjan Verwer
#  - Peter Odding <peter.odding@paylogic.com>
# Last Change: September 24, 2015
# URL: https://py2deb.readthedocs.org

"""
The :py:mod:`py2deb.converter` module contains the high level conversion logic.

This module defines the :py:class:`PackageConverter` class which provides the
intended way for external Python code to interface with `py2deb`. The separation
between the :py:class:`PackageConverter` and :py:class:`.PackageToConvert`
classes is somewhat crude (because neither class can work without the other)
but the idea is to separate the high level conversion logic from the low level
conversion logic.
"""

# Standard library modules.
import importlib
import logging
import os
import re
import shutil
import tempfile

# External dependencies.
from cached_property import cached_property
from deb_pkg_tools.cache import get_default_cache
from deb_pkg_tools.checks import check_duplicate_files
from deb_pkg_tools.utils import find_debian_architecture
from humanfriendly import coerce_boolean, compact
from pip_accel import PipAccelerator
from pip_accel.config import Config as PipAccelConfig
from six.moves import configparser

# Modules included in our package.
from py2deb.utils import (compact_repeating_words, normalize_package_name, normalize_package_version,
                          package_names_match, PackageRepository, tokenize_version)
from py2deb.package import PackageToConvert

# Initialize a logger.
logger = logging.getLogger(__name__)

MACHINE_ARCHITECTURE_MAPPING = dict(i686='i386', x86_64='amd64', armv6l='armhf')
"""
Mapping of supported machine architectures (a dictionary).

The keys are the names reported by :func:`os.uname()` and the values are
machine architecture labels used in the Debian packaging system.
"""


class PackageConverter(object):

    """
    The external interface of `py2deb`, the Python to Debian package converter.

    .. attribute:: alternatives

       A :py:class:`set` of tuples with two strings each (the strings passed to
       :py:func:`install_alternative()`). Used by
       :py:func:`~py2deb.hooks.create_alternatives()` and
       :py:func:`~py2deb.hooks.cleanup_alternatives()` during installation and
       removal of the generated package.
    """

    def __init__(self, load_configuration_files=True, load_environment_variables=True):
        """
        Initialize a Python to Debian package converter.

        :param load_configuration_files: When ``True`` (the default)
                                         :py:func:`load_default_configuration_files()`
                                         is called automatically.
        :param load_environment_variables: When ``True`` (the default)
                                         :py:func:`load_environment_variables()`
                                         is called automatically.
        """
        self.alternatives = set()
        self.install_prefix = '/usr'
        self.lintian_enabled = True
        self.name_mapping = {}
        self.name_prefix = 'python'
        self.pip_accel = PipAccelerator(PipAccelConfig())
        self.python_callback = None
        self.repository = PackageRepository(tempfile.gettempdir())
        self.scripts = {}
        if load_configuration_files:
            self.load_default_configuration_files()
        if load_environment_variables:
            self.load_environment_variables()

    def set_repository(self, directory):
        """
        Set pathname of directory where `py2deb` stores converted packages.

        :param directory: The pathname of a directory (a string).
        :raises: :py:exc:`~exceptions.ValueError` when the directory doesn't
                 exist.
        """
        directory = os.path.abspath(directory)
        if not os.path.isdir(directory):
            msg = "Repository directory doesn't exist! (%s)"
            raise ValueError(msg % directory)
        self.repository = PackageRepository(directory)

    def set_name_prefix(self, prefix):
        """
        Set package name prefix to use during package conversion.

        :param prefix: The name prefix to use (a string).
        :raises: :py:exc:`~exceptions.ValueError` when no name prefix is
                 provided (e.g. an empty string).
        """
        if not prefix:
            raise ValueError("Please provide a nonempty name prefix!")
        self.name_prefix = prefix

    def rename_package(self, python_package_name, debian_package_name):
        """
        Override package name conversion algorithm for given pair of names.

        :param python_package_name: The name of a Python package
                                    as found on PyPI (a string).
        :param debian_package_name: The name of the converted
                                    Debian package (a string).
        :raises: :py:exc:`~exceptions.ValueError` when a package name is not
                 provided (e.g. an empty string).
        """
        if not python_package_name:
            raise ValueError("Please provide a nonempty Python package name!")
        if not debian_package_name:
            raise ValueError("Please provide a nonempty Debian package name!")
        self.name_mapping[python_package_name.lower()] = debian_package_name.lower()

    def set_install_prefix(self, directory):
        """
        Set installation prefix to use during package conversion.

        The installation directory doesn't have to exist on the system where
        the package is converted.

        :param directory: The pathname of the directory where the converted
                          packages should be installed (a string).
        :raises: :py:exc:`~exceptions.ValueError` when no installation prefix is
                 provided (e.g. an empty string).
        """
        if not directory:
            raise ValueError("Please provide a nonempty installation prefix!")
        self.install_prefix = directory

    def set_auto_install(self, enabled):
        """
        Enable or disable automatic installation of build time dependencies.

        :param enabled: Any value, evaluated using
                        :py:func:`~humanfriendly.coerce_boolean()`.
        """
        self.pip_accel.config.auto_install = coerce_boolean(enabled)

    def set_lintian_enabled(self, enabled):
        """
        Enable or disable automatic Lintian_ checks after package building.

        :param enabled: Any value, evaluated using
                        :py:func:`~humanfriendly.coerce_boolean()`.

        .. _Lintian: http://lintian.debian.org/
        """
        self.lintian_enabled = coerce_boolean(enabled)

    def install_alternative(self, link, path):
        r"""
        Install system wide link for program installed in custom installation prefix.

        Use Debian's update-alternatives_ system to add an executable that's
        installed in a custom installation prefix to the system wide executable
        search path using a symbolic link.

        :param link: The generic name for the master link (a string). This is
                     the first argument passed to ``update-alternatives
                     --install``.
        :param path: The alternative being introduced for the master link (a
                     string). This is the third argument passed to
                     ``update-alternatives --install``.
        :raises: :py:exc:`~exceptions.ValueError` when one of the paths is not
                 provided (e.g. an empty string).

        If this is a bit vague, consider the following example:

        .. code-block:: sh

           $ py2deb --name-prefix=py2deb \
                    --no-name-prefix=py2deb \
                    --install-prefix=/usr/lib/py2deb \
                    --install-alternative=/usr/bin/py2deb,/usr/lib/py2deb/bin/py2deb \
                    py2deb==0.1

        This example will convert `py2deb` and its dependencies using a custom
        name prefix and a custom installation prefix which means the ``py2deb``
        program is not available on the default executable search path. This is
        why ``update-alternatives`` is used to create a symbolic link
        ``/usr/bin/py2deb`` which points to the program inside the custom
        installation prefix.

        .. _update-alternatives: http://manpages.debian.org/cgi-bin/man.cgi?query=update-alternatives
        """
        if not link:
            raise ValueError("Please provide a nonempty name for the master link!")
        if not path:
            raise ValueError("Please provide a nonempty name for the alternative being introduced!")
        self.alternatives.add((link, path))

    def set_conversion_command(self, python_package_name, command):
        """
        Set shell command to be executed during conversion process.

        :param python_package_name: The name of a Python package
                                    as found on PyPI (a string).
        :param command: The shell command to execute (a string).
        :raises: :py:exc:`~exceptions.ValueError` when the package name or
                 command is not provided (e.g. an empty string).

        The shell command is executed in the directory containing the Python
        module(s) that are to be installed by the converted package.

        .. warning:: This functionality allows arbitrary manipulation of the
                     Python modules to be installed by the converted package.
                     It should clearly be considered a last resort, only for
                     for fixing things like packaging issues with Python
                     packages that you can't otherwise change.

        For example old versions of Fabric_ bundle a copy of Paramiko_. Most
        people will never notice this because Python package managers don't
        complain about this, they just blindly overwrite the files... Debian's
        packaging system is much more strict and will consider the converted
        Fabric and Paramiko packages as conflicting and thus broken. In this
        case you have two options:

        1. Switch to a newer version of Fabric that no longer bundles Paramiko;
        2. Use the conversion command ``rm -rf paramiko`` to convert Fabric
           (yes this is somewhat brute force :-).

        .. _Fabric: https://pypi.python.org/pypi/Fabric
        .. _Paramiko: https://pypi.python.org/pypi/paramiko
        """
        if not python_package_name:
            raise ValueError("Please provide a nonempty Python package name!")
        if not command:
            raise ValueError("Please provide a nonempty shell command!")
        self.scripts[python_package_name.lower()] = command

    def set_python_callback(self, expression):
        """
        Set a Python callback to be called during the conversion process.

        :param expression: One of the following:

                           1. A callable object (to be provided by Python API callers).
                           2. A string containing the pathname of a Python
                              script and the name of a callable, separated by a
                              colon. The Python script will be loaded using
                              :keyword:`exec`.
                           3. A string containing the "dotted path" of a Python
                              module and the name of a callable, separated by a
                              colon. The Python module will be loaded using
                              :func:`importlib.import_module()`.
                           4. Any value that evaluates to :data:`False` will
                              clear an existing callback (if any).
        :raises: :exc:`~exceptions.ValueError` when the given expression does
                 not result in a valid callable. :exc:`~exceptions.ImportError`
                 when the expression contains a dotted path that cannot be
                 imported.

        The callback will be called at the very last step before the binary
        package's metadata and contents are packaged as a ``*.deb`` archive.

        This allows arbitrary manipulation of resulting binary packages, e.g.
        changing package metadata or files to be packaged.

        An example use case:

        - Consider a dependency set (group of related packages) that has
          previously been converted and deployed.

        - A new version of the dependency set switches from Python package A to
          Python package B, where the two Python packages contain conflicting
          files (installed in the same location). This could happen when
          switching to a project's fork.

        - A deployment of the new dependency set will conflict with existing
          installations due to "unrelated" packages (in the eyes of ``apt`` and
          ``dpkg``) installing the same files.

        - By injecting a custom Python callback the user can mark package B as
          "replacing" and "breaking" package A. Refer to `section 7.6`_ of the
          Debian policy manual for details about the required binary control
          fields (hint: ``Replaces:`` and ``Breaks:``).

        .. warning:: The callback is responsible for not making changes that
                     would break the installation of the converted dependency
                     set!

        .. _section 7.6: https://www.debian.org/doc/debian-policy/ch-relationships.html#s-replaces
        """
        if expression:
            if callable(expression):
                # Python callers get to pass a callable directly.
                self.python_callback = expression
            else:
                # Otherwise we expect a string to parse (from a command line
                # argument, environment variable or configuration file).
                callback_path, _, callback_name = expression.partition(':')
                if os.path.isfile(callback_path):
                    # Callback specified as Python script.
                    script_name = os.path.basename(callback_path)
                    if script_name.endswith('.py'):
                        script_name, _ = os.path.splitext(script_name)
                    environment = dict(__file__=callback_path, __name__=script_name)
                    logger.debug("Loading Python callback from pathname: %s", callback_path)
                    with open(callback_path) as handle:
                        exec(handle.read(), environment)
                    self.python_callback = environment.get(callback_name)
                else:
                    # Callback specified as `dotted path'.
                    logger.debug("Loading Python callback from dotted path: %s", callback_path)
                    module = importlib.import_module(callback_path)
                    self.python_callback = getattr(module, callback_name, None)
                if not callable(self.python_callback):
                    raise ValueError(compact("""
                        The Python callback expression {expr} didn't result in
                        a valid callable! (result: {value})
                    """, expr=expression, value=self.python_callback))
        else:
            # Clear an existing callback (if any).
            self.python_callback = None

    def load_environment_variables(self):
        """
        Load configuration defaults from environment variables.

        The following environment variables are currently supported:

        - ``$PY2DEB_CONFIG``
        - ``$PY2DEB_REPOSITORY``
        - ``$PY2DEB_NAME_PREFIX``
        - ``$PY2DEB_INSTALL_PREFIX``
        - ``$PY2DEB_AUTO_INSTALL``
        - ``$PY2DEB_LINTIAN``
        """
        for variable, setter in (('PY2DEB_CONFIG', self.load_configuration_file),
                                 ('PY2DEB_REPOSITORY', self.set_repository),
                                 ('PY2DEB_NAME_PREFIX', self.set_name_prefix),
                                 ('PY2DEB_INSTALL_PREFIX', self.set_install_prefix),
                                 ('PY2DEB_AUTO_INSTALL', self.set_auto_install),
                                 ('PY2DEB_LINTIAN', self.set_lintian_enabled),
                                 ('PY2DEB_CALLBACK', self.set_python_callback)):
            value = os.environ.get(variable)
            if value is not None:
                setter(value)

    def load_configuration_file(self, configuration_file):
        """
        Load configuration defaults from a configuration file.

        :param configuration_file: The pathname of a configuration file (a
                                   string).
        :raises: :py:exc:`~exceptions.Exception` when the configuration file
                 cannot be loaded.

        Below is an example of the available options, I assume that the mapping
        between the configuration options and the setters of
        :py:class:`PackageConverter` is fairly obvious (it should be :-).

        .. code-block:: ini

           # The `py2deb' section contains global options.
           [py2deb]
           repository = /tmp
           name-prefix = py2deb
           install-prefix = /usr/lib/py2deb
           auto-install = on
           lintian = on

           # The `alternatives' section contains instructions
           # for Debian's `update-alternatives' system.
           [alternatives]
           /usr/bin/py2deb = /usr/lib/py2deb/bin/py2deb

           # Sections starting with `package:' contain conversion options
           # specific to a package.
           [package:py2deb]
           no-name-prefix = true

        Note that the configuration options shown here are just examples, they
        are not the configuration defaults (they are what I use to convert
        `py2deb` itself). Package specific sections support the following
        options:

        **no-name-prefix**:
          A boolean indicating whether the configured name prefix should be
          applied or not. Understands ``true`` and ``false`` (``false`` is the
          default and you only need this option to change the default).

        **rename**:
          Gives an override for the package name conversion algorithm (refer to
          :py:func:`rename_package()` for details).

        **script**:
          Set a shell command to be executed during the conversion process
          (refer to :py:func:`set_conversion_command()` for details).
        """
        # Load the configuration file.
        parser = configparser.RawConfigParser()
        configuration_file = os.path.expanduser(configuration_file)
        logger.debug("Loading configuration file: %s", configuration_file)
        files_loaded = parser.read(configuration_file)
        try:
            assert len(files_loaded) == 1
            assert os.path.samefile(configuration_file, files_loaded[0])
        except Exception:
            msg = "Failed to load configuration file! (%s)"
            raise Exception(msg % configuration_file)
        # Apply the global settings in the configuration file.
        if parser.has_option('py2deb', 'repository'):
            self.set_repository(parser.get('py2deb', 'repository'))
        if parser.has_option('py2deb', 'name-prefix'):
            self.set_name_prefix(parser.get('py2deb', 'name-prefix'))
        if parser.has_option('py2deb', 'install-prefix'):
            self.set_install_prefix(parser.get('py2deb', 'install-prefix'))
        if parser.has_option('py2deb', 'auto-install'):
            self.set_auto_install(parser.get('py2deb', 'auto-install'))
        if parser.has_option('py2deb', 'lintian'):
            self.set_lintian_enabled(parser.get('py2deb', 'lintian'))
        if parser.has_option('py2deb', 'python-callback'):
            self.set_python_callback(parser.get('py2deb', 'python-callback'))
        # Apply the defined alternatives.
        if parser.has_section('alternatives'):
            for link, path in parser.items('alternatives'):
                self.install_alternative(link, path)
        # Apply any package specific settings.
        for section in parser.sections():
            tag, _, package = section.partition(':')
            if tag == 'package':
                if parser.has_option(section, 'no-name-prefix'):
                    if parser.getboolean(section, 'no-name-prefix'):
                        self.rename_package(package, package)
                if parser.has_option(section, 'rename'):
                    rename_to = parser.get(section, 'rename')
                    self.rename_package(package, rename_to)
                if parser.has_option(section, 'script'):
                    script = parser.get(section, 'script')
                    self.set_conversion_command(package, script)

    def load_default_configuration_files(self):
        """
        Load configuration options from default configuration files.

        The following default configuration file locations are checked:

        - ``/etc/py2deb.ini``
        - ``~/.py2deb.ini``

        :raises: :py:exc:`~exceptions.Exception` when a configuration file
                 exists but cannot be loaded.
        """
        for location in ('/etc/py2deb.ini', os.path.expanduser('~/.py2deb.ini')):
            if os.path.isfile(location):
                self.load_configuration_file(location)

    def convert(self, pip_install_arguments):
        """
        Convert one or more Python packages to Debian packages.

        :param pip_install_arguments: The command line arguments to the ``pip
                                      install`` command.
        :returns: A tuple with two lists:

                  1. A list of strings containing the pathname(s) of the
                     generated Debian package package archive(s).

                  2. A list of strings containing the Debian package
                     relationship(s) required to depend on the converted
                     package(s).
        :raises: :py:exc:`~deb_pkg_tools.checks.DuplicateFilesFound` if two
                 converted package archives contain the same files (certainly
                 not what you want within a set of dependencies).

        Here's an example of what's returned:

        >>> from py2deb import PackageConverter
        >>> converter = PackageConverter()
        >>> archives, relationships = converter.convert(['py2deb'])
        >>> print(archives)
        ['/tmp/python-py2deb_0.18_all.deb']
        >>> print(relationships)
        ['python-py2deb (=0.18)']

        """
        try:
            generated_archives = []
            dependencies_to_report = []
            # Download and unpack the requirement set and store the complete
            # set as an instance variable because transform_version() will need
            # it later on.
            self.packages_to_convert = list(self.get_source_distributions(pip_install_arguments))
            # Convert packages that haven't been converted already.
            for package in self.packages_to_convert:
                # If the requirement is a 'direct' (non-transitive) requirement
                # it means the caller explicitly asked for this package to be
                # converted, so we add it to the list of converted dependencies
                # that we report to the caller once we've finished converting.
                if package.requirement.is_direct:
                    dependencies_to_report.append('%s (= %s)' % (package.debian_name, package.debian_version))
                if package.existing_archive:
                    # If the same version of this package was converted in a
                    # previous run we can save a lot of time by skipping it.
                    logger.info("Package %s (%s) already converted: %s",
                                package.python_name, package.python_version,
                                package.existing_archive.filename)
                    generated_archives.append(package.existing_archive)
                else:
                    archive = package.convert()
                    if not os.path.samefile(os.path.dirname(archive), self.repository.directory):
                        shutil.move(archive, self.repository.directory)
                        archive = os.path.join(self.repository.directory, os.path.basename(archive))
                    generated_archives.append(archive)
            # Use deb-pkg-tools to sanity check the generated package archives
            # for duplicate files. This should never occur but unfortunately
            # can happen because Python's packaging infrastructure is a lot
            # more `forgiving' in the sense of blindly overwriting files
            # installed by other packages ;-).
            if len(generated_archives) > 1:
                check_duplicate_files(generated_archives, cache=get_default_cache())
            # Let the caller know which archives were generated (whether
            # previously or now) and how to depend on the converted packages.
            return generated_archives, sorted(dependencies_to_report)
        finally:
            # Always clean up temporary directories created by pip and pip-accel.
            self.pip_accel.cleanup_temporary_directories()

    def get_source_distributions(self, pip_install_arguments):
        """
        Use :py:mod:`pip_accel` to download and unpack Python source distributions.

        Retries several times if a download fails (so it doesn't fail
        immediately when a package index server returns a transient error).

        :param pip_install_arguments: The command line arguments to the ``pip
                                      install`` command.
        :returns: A generator of :py:class:`.PackageToConvert` objects.
        :raises: When downloading fails even after several retries this
                 function raises :py:exc:`pip.exceptions.DistributionNotFound`.
                 This function can also raise other exceptions raised by pip
                 because it uses :py:mod:`pip_accel` to call pip (as a Python
                 API).
        """
        # We depend on `pip install --ignore-installed ...' so we can guarantee
        # that all of the packages specified by the caller are converted,
        # instead of only those not currently installed somewhere where pip can
        # see them (a poorly defined concept to begin with).
        arguments = ['--ignore-installed'] + list(pip_install_arguments)
        for requirement in self.pip_accel.get_requirements(arguments):
            yield PackageToConvert(self, requirement)

    def transform_name(self, python_package_name, *extras):
        """
        Transform Python package name to Debian package name.

        :param python_package_name: The name of a Python package
                                    as found on PyPI (a string).
        :param extras: Any extras requested to be included (a tuple of strings).
        :returns: The transformed name (a string).

        Examples:

        >>> from py2deb import PackageConverter
        >>> converter = PackageConverter()
        >>> converter.transform_name('example')
        'python-example'
        >>> converter.set_name_prefix('my-custom-prefix')
        >>> converter.transform_name('example')
        'my-custom-prefix-example'
        >>> converter.set_name_prefix('some-web-app')
        >>> converter.transform_name('raven', 'flask')
        'some-web-app-raven-flask'

        """
        # Check for an override by the caller.
        debian_package_name = self.name_mapping.get(python_package_name.lower())
        if not debian_package_name:
            # No override. Make something up :-).
            with_name_prefix = '%s-%s' % (self.name_prefix, python_package_name)
            normalized_words = normalize_package_name(with_name_prefix).split('-')
            debian_package_name = '-'.join(compact_repeating_words(normalized_words))
        # If a requirement includes extras this changes the dependencies of the
        # package. Because Debian doesn't have this concept we encode the names
        # of the extras in the name of the package.
        if extras:
            sorted_extras = sorted(extra.lower() for extra in extras)
            debian_package_name = '%s-%s' % (debian_package_name, '-'.join(sorted_extras))
        # Always normalize the package name (even if it was given to us by the caller).
        return normalize_package_name(debian_package_name)

    def transform_version(self, package_to_convert, python_requirement_name, python_requirement_version):
        """
        Transform a Python requirement version to a Debian version number.

        :param package_to_convert: The :class:`.PackageToConvert` whose
                                   requirement is being transformed.
        :param python_requirement_name: The name of a Python package
                                        as found on PyPI (a string).
        :param python_requirement_version: The required version of the
                                           Python package (a string).
        :returns: The transformed version (a string).

        This method is a wrapper for :func:`.normalize_package_version()` that
        takes care of one additional quirk to ensure compatibility with pip.
        Explaining this quirk requires a bit of context:

        - When package A requires package B (via ``install_requires``) and
          package A absolutely pins the required version of package B using one
          or more trailing zeros (e.g. ``B==1.0.0``) but the actual version
          number of package B (embedded in the metadata of package B) contains
          less trailing zeros (e.g. ``1.0``) then pip will not complain but
          silently fetch version ``1.0`` of package B to satisfy the
          requirement.

        - However this doesn't change the absolutely pinned version in the
          ``install_requires`` metadata of package A.

        - When py2deb converts the resulting requirement set, the dependency of
          package A is converted as ``B (= 1.0.0)``. The resulting packages
          will not be installable because ``apt`` considers ``1.0`` to be
          different from ``1.0.0``.

        This method analyzes the requirement set to identify occurrences of
        this quirk and strip trailing zeros in ``install_requires`` metadata
        that would otherwise result in converted packages that cannot be
        installed.
        """
        matching_packages = [p for p in self.packages_to_convert
                             if package_names_match(p.python_name, python_requirement_name)]
        if len(matching_packages) != 1:
            # My assumption while writing this code is that this should never
            # happen. This check is to make sure that if it does happen it will
            # be noticed because the last thing I want is for this `hack' to
            # result in packages that are silently wrongly converted.
            normalized_name = normalize_package_name(python_requirement_name)
            num_matches = len(matching_packages)
            raise Exception(compact("""
                Expected requirement set to contain exactly one Python package
                whose name can be normalized to {name} but encountered {count}
                packages instead! (matching packages: {matches})
            """, name=normalized_name, count=num_matches, matches=matching_packages))
        # Check whether the version number included in the requirement set
        # matches the version number in a package's requirements.
        requirement_to_convert = matching_packages[0]
        if python_requirement_version != requirement_to_convert.python_version:
            logger.debug("Checking whether to strip trailing zeros from required version ..")
            # Check whether the version numbers share the same prefix.
            required_version = tokenize_version(python_requirement_version)
            included_version = tokenize_version(requirement_to_convert.python_version)
            common_length = min(len(required_version), len(included_version))
            required_prefix = required_version[:common_length]
            included_prefix = included_version[:common_length]
            prefixes_match = (required_prefix == included_prefix)
            logger.debug("Prefix of required version: %s", required_prefix)
            logger.debug("Prefix of included version: %s", included_prefix)
            logger.debug("Prefixes match? %s", prefixes_match)
            # Check if 1) only the required version has a suffix and 2) this
            # suffix consists only of trailing zeros.
            required_suffix = required_version[common_length:]
            included_suffix = included_version[common_length:]
            logger.debug("Suffix of required version: %s", required_suffix)
            logger.debug("Suffix of included version: %s", included_suffix)
            if prefixes_match and required_suffix and not included_suffix:
                # Check whether the suffix of the required version contains
                # only zeros, i.e. pip considers the version numbers the same
                # although apt would not agree.
                if all(re.match('^0+$', t) for t in required_suffix if t.isdigit()):
                    modified_version = ''.join(required_prefix)
                    logger.warning("Stripping superfluous trailing zeros from required"
                                   " version of %s required by %s! (%s -> %s)",
                                   python_requirement_name, package_to_convert.python_name,
                                   python_requirement_version, modified_version)
                    python_requirement_version = modified_version
        return normalize_package_version(python_requirement_version)

    @cached_property
    def debian_architecture(self):
        """
        Find the Debian architecture of the current environment.

        This logic was originally implemented in py2deb but has since been
        moved to :py:func:`deb_pkg_tools.utils.find_debian_architecture()`.
        This property remains as a convenient shortcut.
        """
        return find_debian_architecture()
