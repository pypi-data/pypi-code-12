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
    name='reahl-domain',
    version='3.2.0',
    description='End-user domain functionality for use with Reahl.',
    long_description='Reahl is a web application framework that allows a Python programmer to work in terms of useful abstractions - using a single programming language.\n\nThis Reahl component includes functionality modelling user accounts, some simple workflow concepts and more.\n\nSee http://www.reahl.org/docs/3.2/tutorial/gettingstarted.d.html for installation instructions. ',
    url='http://www.reahl.org',
    maintainer='Iwan Vosloo',
    maintainer_email='iwan@reahl.org',
    packages=['reahl', 'reahl.domain_dev', 'reahl.messages', 'reahl.domain'],
    py_modules=['setup'],
    include_package_data=True,
    package_data={'': ['*/LC_MESSAGES/*.mo']},
    namespace_packages=['reahl', 'reahl.messages'],
    install_requires=['reahl-component>=3.2,<3.3', 'reahl-mailutil>=3.2,<3.3', 'reahl-sqlalchemysupport>=3.2,<3.3', 'reahl-web-declarative>=3.2,<3.3'],
    setup_requires=['reahl-bzrsupport>=3.2,<3.3'],
    tests_require=['nose', 'reahl-tofu>=3.2,<3.3', 'reahl-stubble>=3.2,<3.3', 'reahl-dev>=3.2,<3.3', 'reahl-postgresqlsupport>=3.2,<3.3', 'reahl-webdev>=3.2,<3.3'],
    test_suite='reahl.domain_dev',
    entry_points={
        'reahl.migratelist': [
            '0 = reahl.domain.migrations:ElixirToDeclarativeDomainChanges',
            '1 = reahl.domain.migrations:AddLoginSession'    ],
        'reahl.persistlist': [
            '0 = reahl.partymodel:Party',
            '1 = reahl.systemaccountmodel:SystemAccount',
            '2 = reahl.systemaccountmodel:LoginSession',
            '3 = reahl.systemaccountmodel:EmailAndPasswordSystemAccount',
            '4 = reahl.systemaccountmodel:AccountManagementInterface',
            '5 = reahl.systemaccountmodel:VerificationRequest',
            '6 = reahl.systemaccountmodel:VerifyEmailRequest',
            '7 = reahl.systemaccountmodel:NewPasswordRequest',
            '8 = reahl.systemaccountmodel:ActivateAccount',
            '9 = reahl.systemaccountmodel:ChangeAccountEmail',
            '10 = reahl.workflowmodel:DeferredAction',
            '11 = reahl.workflowmodel:Requirement',
            '12 = reahl.workflowmodel:Queue',
            '13 = reahl.workflowmodel:Task'    ],
        'reahl.scheduled_jobs': [
            'reahl.workflowmodel:DeferredAction.check_deadline = reahl.workflowmodel:DeferredAction.check_deadline'    ],
        'reahl.eggs': [
            'Egg = reahl.component.eggs:ReahlEgg'    ],
        'reahl.translations': [
            'reahl-domain = reahl.messages'    ],
        'reahl.configspec': [
            'config = reahl.systemaccountmodel:SystemAccountConfig'    ],
                 },
    extras_require={},
    cmdclass={'install_test_dependencies': InstallTestDependencies}
)
