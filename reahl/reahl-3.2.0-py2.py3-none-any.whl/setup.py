from setuptools import setup, Command
from pkg_resources import require
class InstallTestDependencies(Command):
    user_options = []
    def run(self):
        from setuptools.command import easy_install
        if self.distribution.tests_require: easy_install.main(self.distribution.tests_require)

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

setup(
    name='reahl',
    version='3.2.0',
    description='The Reahl web framework.',
    long_description='Reahl is a web application framework for Python programmers.\n\nWith Reahl, programming is done purely in Python, using concepts familiar from GUI programming---like reusable Widgets and Events. There\'s no need for a programmer to know several different languages (HTML, JavaScript, template languages, etc) or to keep up with the tricks of these trades. The abstractions presented by Reahl relieve the programmer from the burden of dealing with the annoying problems of the web: security, accessibility, progressive enhancement (or graceful degradation) and browser quirks.\n\nReahl consists of many different eggs that are not all needed all of the time. This package does not contain much itself, but is an entry point for installing a set of Reahl eggs:\n\nInstall Reahl by installing with extras, eg: pip install "reahl[declarative,sqlite,dev,doc]" to install everything needed to run Reahl on sqlite, the dev tools and documentation. (On Windows platforms, use easy_install instead of pip.)\n\nSee http://www.reahl.org/docs/3.2/tutorial/gettingstarted.d.html for complete installation instructions. ',
    url='http://www.reahl.org',
    maintainer='Iwan Vosloo',
    maintainer_email='iwan@reahl.org',
    packages=[],
    py_modules=['setup'],
    include_package_data=False,
    package_data={'': ['*/LC_MESSAGES/*.mo']},
    namespace_packages=[],
    install_requires=[],
    setup_requires=['reahl-bzrsupport>=3.2,<3.3'],
    tests_require=[],
    test_suite='tests',
    entry_points={
        'reahl.eggs': [
            'Egg = reahl.component.eggs:ReahlEgg'    ],
                 },
    extras_require={'web': ['reahl-component>=3.2,<3.3', 'reahl-web>=3.2,<3.3', 'reahl-mailutil>=3.2,<3.3'], 'doc': ['reahl-doc>=3.2,<3.3'], 'dev': ['reahl-dev>=3.2,<3.3', 'reahl-webdev>=3.2,<3.3', 'reahl-stubble>=3.2,<3.3', 'reahl-tofu>=3.2,<3.3'], 'all': ['reahl-component>=3.2,<3.3', 'reahl-web>=3.2,<3.3', 'reahl-mailutil>=3.2,<3.3', 'reahl-sqlalchemysupport>=3.2,<3.3', 'reahl-web-declarative>=3.2,<3.3', 'reahl-domain>=3.2,<3.3', 'reahl-domainui>=3.2,<3.3', 'reahl-postgresqlsupport>=3.2,<3.3', 'reahl-sqlitesupport>=3.2,<3.3', 'reahl-dev>=3.2,<3.3', 'reahl-webdev>=3.2,<3.3', 'reahl-stubble>=3.2,<3.3', 'reahl-tofu>=3.2,<3.3', 'reahl-doc>=3.2,<3.3'], 'sqlite': ['reahl-sqlitesupport>=3.2,<3.3'], 'postgresql': ['reahl-postgresqlsupport>=3.2,<3.3'], 'declarative': ['reahl-sqlalchemysupport>=3.2,<3.3', 'reahl-web-declarative>=3.2,<3.3', 'reahl-domain>=3.2,<3.3', 'reahl-domainui>=3.2,<3.3']},
    cmdclass={'install_test_dependencies': InstallTestDependencies}
)
