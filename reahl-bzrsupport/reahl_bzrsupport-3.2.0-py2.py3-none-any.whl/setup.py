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
    name='reahl-bzrsupport',
    version='3.2.0',
    description='Distutils support for Bazaar when using Reahl development tools.',
    long_description='Reahl is a web application framework that allows a Python programmer to work in terms of useful abstractions - using a single programming language.\n\nReahl-bzrsupport contains a finder for distutils for the Bazaar version control system.\n\nSee http://www.reahl.org/docs/3.2/tutorial/gettingstarted.d.html for installation instructions. ',
    url='http://www.reahl.org',
    maintainer='Iwan Vosloo',
    maintainer_email='iwan@reahl.org',
    packages=['reahl', 'reahl.bzrsupport_dev'],
    py_modules=['setup'],
    include_package_data=False,
    package_data={'': ['*/LC_MESSAGES/*.mo']},
    namespace_packages=['reahl'],
    install_requires=[],
    setup_requires=['reahl-bzrsupport>=3.2,<3.3'],
    tests_require=['nose'],
    test_suite='reahl.bzrsupport_dev',
    entry_points={
        'setuptools.file_finders': [
            'reahl_finder = reahl.bzrsupport:find_files'    ],
        'reahl.eggs': [
            'Egg = reahl.component.eggs:ReahlEgg'    ],
                 },
    extras_require={},
    cmdclass={'install_test_dependencies': InstallTestDependencies}
)
