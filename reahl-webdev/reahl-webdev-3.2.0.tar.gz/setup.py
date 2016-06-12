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
    name='reahl-webdev',
    version='3.2.0',
    description='Web-specific development tools for Reahl.',
    long_description='Reahl is a web application framework that allows a Python programmer to work in terms of useful abstractions - using a single programming language.\n\nReahl development tools for testing and working with web based programs.\n\nSee http://www.reahl.org/docs/3.2/tutorial/gettingstarted.d.html for installation instructions. ',
    url='http://www.reahl.org',
    maintainer='Iwan Vosloo',
    maintainer_email='iwan@reahl.org',
    packages=['reahl', 'reahl.webdev_dev', 'reahl.webdev'],
    py_modules=['setup'],
    include_package_data=True,
    package_data={'': ['*/LC_MESSAGES/*.mo']},
    namespace_packages=['reahl'],
    install_requires=['reahl-web>=3.2,<3.3', 'reahl-dev>=3.2,<3.3', 'reahl-component>=3.2,<3.3', 'reahl-tofu>=3.2,<3.3', 'reahl-domain>=3.2,<3.3', 'lxml>=3.3,<3.3.999', 'WebTest>=2.0,<2.0.999', 'selenium>=2.42,<2.9999', 'watchdog>=0.8.3,<0.8.999.3'],
    setup_requires=['reahl-bzrsupport>=3.2,<3.3'],
    tests_require=['nose', 'reahl-postgresqlsupport>=3.2,<3.3', 'reahl-stubble>=3.2,<3.3'],
    test_suite='reahl.webdev_dev',
    entry_points={
        'reahl.dev.commands': [
            'ServeCurrentProject = reahl.webdev.commands:ServeCurrentProject'    ],
        'reahl.eggs': [
            'Egg = reahl.component.eggs:ReahlEgg'    ],
                 },
    extras_require={'pillow': ['pillow>=2.5,<2.5.999']},
    cmdclass={'install_test_dependencies': InstallTestDependencies}
)
