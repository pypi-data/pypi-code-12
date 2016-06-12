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
    name='reahl-domainui',
    version='3.2.0',
    description='A user interface for reahl-domain.',
    long_description='Reahl is a web application framework that allows a Python programmer to work in terms of useful abstractions - using a single programming language.\n\nThis Reahl component contains a user interface for some of the domain functionality in reahl-domainui.\n\nSee http://www.reahl.org/docs/3.2/tutorial/gettingstarted.d.html for installation instructions. ',
    url='http://www.reahl.org',
    maintainer='Iwan Vosloo',
    maintainer_email='iwan@reahl.org',
    packages=['reahl', 'reahl.messages', 'reahl.domainui', 'reahl.domainui_dev', 'reahl.domainui.bootstrap', 'reahl.domainui_dev.bootstrap'],
    py_modules=['setup'],
    include_package_data=True,
    package_data={'': ['*/LC_MESSAGES/*.mo']},
    namespace_packages=['reahl', 'reahl.messages'],
    install_requires=['reahl-component>=3.2,<3.3', 'reahl-sqlalchemysupport>=3.2,<3.3', 'reahl-web>=3.2,<3.3', 'reahl-web-declarative>=3.2,<3.3', 'reahl-domain>=3.2,<3.3'],
    setup_requires=['reahl-bzrsupport>=3.2,<3.3'],
    tests_require=['nose', 'reahl-tofu>=3.2,<3.3', 'reahl-stubble>=3.2,<3.3', 'reahl-dev>=3.2,<3.3', 'reahl-webdev>=3.2,<3.3', 'reahl-postgresqlsupport>=3.2,<3.3'],
    test_suite='reahl.domainui_dev',
    entry_points={
        'reahl.eggs': [
            'Egg = reahl.component.eggs:ReahlEgg'    ],
        'reahl.workflowui.task_widgets': [
            'TaskWidget = reahl.domainui.workflow:TaskWidget',
            'bootstrap.TaskWidget = reahl.domainui.bootstrap.workflow:TaskWidget'    ],
        'reahl.configspec': [
            'config = reahl.domainuiegg:DomainUiConfig'    ],
        'reahl.translations': [
            'reahl-domainui = reahl.messages'    ],
                 },
    extras_require={},
    cmdclass={'install_test_dependencies': InstallTestDependencies}
)
