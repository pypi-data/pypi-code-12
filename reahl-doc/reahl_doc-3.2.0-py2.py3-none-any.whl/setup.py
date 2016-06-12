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
    name='reahl-doc',
    version='3.2.0',
    description='Documentation and examples for Reahl.',
    long_description='Reahl is a web application framework that allows a Python programmer to work in terms of useful abstractions - using a single programming language.\n\nReahl-doc contains documentation and examples of Reahl.\n\nSee http://www.reahl.org/docs/3.2/tutorial/gettingstarted.d.html for installation instructions. ',
    url='http://www.reahl.org',
    maintainer='Iwan Vosloo',
    maintainer_email='iwan@reahl.org',
    packages=['reahl', 'reahl.doc_dev', 'reahl.doc', 'reahl.doc.examples', 'reahl.doc.examples.tutorial', 'reahl.doc.examples.features', 'reahl.doc.examples.tutorial.login2', 'reahl.doc.examples.tutorial.access2bootstrap', 'reahl.doc.examples.tutorial.sessionscopebootstrap', 'reahl.doc.examples.tutorial.datatable', 'reahl.doc.examples.tutorial.parameterised2', 'reahl.doc.examples.tutorial.pagerbootstrap', 'reahl.doc.examples.tutorial.ajax', 'reahl.doc.examples.tutorial.hello', 'reahl.doc.examples.tutorial.tablebootstrap', 'reahl.doc.examples.tutorial.migrationexample', 'reahl.doc.examples.tutorial.i18nexamplebootstrap', 'reahl.doc.examples.tutorial.access1', 'reahl.doc.examples.tutorial.sessionscope', 'reahl.doc.examples.tutorial.ajaxbootstrap', 'reahl.doc.examples.tutorial.login1', 'reahl.doc.examples.tutorial.migrationexamplebootstrap', 'reahl.doc.examples.tutorial.addressbook2', 'reahl.doc.examples.tutorial.pager', 'reahl.doc.examples.tutorial.hellonginx', 'reahl.doc.examples.tutorial.componentconfig', 'reahl.doc.examples.tutorial.table', 'reahl.doc.examples.tutorial.accessbootstrap', 'reahl.doc.examples.tutorial.slotsbootstrap', 'reahl.doc.examples.tutorial.slots', 'reahl.doc.examples.tutorial.helloapache', 'reahl.doc.examples.tutorial.addressbook1', 'reahl.doc.examples.tutorial.bootstrapgrids', 'reahl.doc.examples.tutorial.pageflow1', 'reahl.doc.examples.tutorial.login2bootstrap', 'reahl.doc.examples.tutorial.access2', 'reahl.doc.examples.tutorial.jobsbootstrap', 'reahl.doc.examples.tutorial.access1bootstrap', 'reahl.doc.examples.tutorial.datatablebootstrap', 'reahl.doc.examples.tutorial.addressbook2bootstrap', 'reahl.doc.examples.tutorial.pageflow1bootstrap', 'reahl.doc.examples.tutorial.jobs', 'reahl.doc.examples.tutorial.login1bootstrap', 'reahl.doc.examples.tutorial.parameterised1', 'reahl.doc.examples.tutorial.access', 'reahl.doc.examples.tutorial.pageflow2', 'reahl.doc.examples.tutorial.pageflow2bootstrap', 'reahl.doc.examples.tutorial.parameterised2bootstrap', 'reahl.doc.examples.tutorial.componentconfigbootstrap', 'reahl.doc.examples.tutorial.parameterised1bootstrap', 'reahl.doc.examples.tutorial.i18nexample', 'reahl.doc.examples.tutorial.login2.login2_dev', 'reahl.doc.examples.tutorial.access2bootstrap.access2bootstrap_dev', 'reahl.doc.examples.tutorial.sessionscopebootstrap.sessionscopebootstrap_dev', 'reahl.doc.examples.tutorial.datatable.datatable_dev', 'reahl.doc.examples.tutorial.parameterised2.parameterised2_dev', 'reahl.doc.examples.tutorial.pagerbootstrap.pagerbootstrap_dev', 'reahl.doc.examples.tutorial.ajax.ajax_dev', 'reahl.doc.examples.tutorial.tablebootstrap.etc', 'reahl.doc.examples.tutorial.tablebootstrap.tablebootstrap_dev', 'reahl.doc.examples.tutorial.migrationexample.migrationexample_dev', 'reahl.doc.examples.tutorial.i18nexamplebootstrap.i18nexamplebootstrap_dev', 'reahl.doc.examples.tutorial.i18nexamplebootstrap.i18nexamplebootstrapmessages', 'reahl.doc.examples.tutorial.access1.access1_dev', 'reahl.doc.examples.tutorial.sessionscope.sessionscope_dev', 'reahl.doc.examples.tutorial.ajaxbootstrap.ajaxbootstrap_dev', 'reahl.doc.examples.tutorial.login1.login1_dev', 'reahl.doc.examples.tutorial.migrationexamplebootstrap.migrationexamplebootstrap_dev', 'reahl.doc.examples.tutorial.addressbook2.addressbook2_dev', 'reahl.doc.examples.tutorial.pager.pager_dev', 'reahl.doc.examples.tutorial.componentconfig.componentconfig_dev', 'reahl.doc.examples.tutorial.table.table_dev', 'reahl.doc.examples.tutorial.accessbootstrap.accessbootstrap_dev', 'reahl.doc.examples.tutorial.addressbook1.addressbook1_dev', 'reahl.doc.examples.tutorial.login2bootstrap.login2bootstrap_dev', 'reahl.doc.examples.tutorial.access2.access2_dev', 'reahl.doc.examples.tutorial.jobsbootstrap.jobsbootstrap_dev', 'reahl.doc.examples.tutorial.access1bootstrap.access1bootstrap_dev', 'reahl.doc.examples.tutorial.datatablebootstrap.datatablebootstrap_dev', 'reahl.doc.examples.tutorial.addressbook2bootstrap.addressbook2bootstrap_dev', 'reahl.doc.examples.tutorial.jobs.jobs_dev', 'reahl.doc.examples.tutorial.login1bootstrap.login1bootstrap_dev', 'reahl.doc.examples.tutorial.access.access_dev', 'reahl.doc.examples.tutorial.parameterised2bootstrap.parameterised2bootstrap_dev', 'reahl.doc.examples.tutorial.componentconfigbootstrap.componentconfigbootstrap_dev', 'reahl.doc.examples.tutorial.i18nexample.i18nexample_dev', 'reahl.doc.examples.tutorial.i18nexample.i18nexamplemessages', 'reahl.doc.examples.features.pageflow', 'reahl.doc.examples.features.tabbedpanelbootstrap', 'reahl.doc.examples.features.persistence', 'reahl.doc.examples.features.validation', 'reahl.doc.examples.features.layout', 'reahl.doc.examples.features.slidingpanel', 'reahl.doc.examples.features.carousel', 'reahl.doc.examples.features.tabbedpanel', 'reahl.doc.examples.features.access', 'reahl.doc.examples.features.i18nexample'],
    py_modules=['setup'],
    include_package_data=True,
    package_data={'': ['*/LC_MESSAGES/*.mo']},
    namespace_packages=['reahl'],
    install_requires=['reahl-web>=3.2,<3.3', 'reahl-component>=3.2,<3.3', 'reahl-sqlalchemysupport>=3.2,<3.3', 'reahl-web-declarative>=3.2,<3.3', 'reahl-domain>=3.2,<3.3', 'reahl-domainui>=3.2,<3.3', 'nose'],
    setup_requires=['reahl-bzrsupport>=3.2,<3.3'],
    tests_require=['nose', 'reahl-tofu>=3.2,<3.3', 'Sphinx', 'reahl-stubble>=3.2,<3.3', 'reahl-dev>=3.2,<3.3', 'reahl-webdev>=3.2,<3.3', 'reahl-postgresqlsupport>=3.2,<3.3', 'reahl-sqlitesupport>=3.2,<3.3'],
    test_suite='reahl.doc_dev',
    entry_points={
        'reahl.persistlist': [
            '0 = reahl.doc.examples.features.persistence.persistence:Comment',
            '1 = reahl.doc.fileupload:Comment',
            '2 = reahl.doc.fileupload:AttachedFile',
            '3 = reahl.doc.examples.tutorial.addressbook2.addressbook2:Address',
            '4 = reahl.doc.examples.tutorial.addressbook2bootstrap.addressbook2bootstrap:Address',
            '5 = reahl.doc.examples.tutorial.addressbook1.addressbook1:Address',
            '6 = reahl.doc.examples.tutorial.pageflow2.pageflow2:Address',
            '7 = reahl.doc.examples.tutorial.pageflow2bootstrap.pageflow2bootstrap:Address',
            '8 = reahl.doc.examples.tutorial.pageflow1.pageflow1:Address',
            '9 = reahl.doc.examples.tutorial.pageflow1bootstrap.pageflow1bootstrap:Address',
            '10 = reahl.doc.examples.tutorial.parameterised1.parameterised1:Address',
            '11 = reahl.doc.examples.tutorial.parameterised1bootstrap.parameterised1bootstrap:Address',
            '12 = reahl.doc.examples.tutorial.parameterised2.parameterised2:Address',
            '13 = reahl.doc.examples.tutorial.parameterised2bootstrap.parameterised2bootstrap:Address',
            '14 = reahl.doc.examples.tutorial.sessionscope.sessionscope:User',
            '15 = reahl.doc.examples.tutorial.sessionscopebootstrap.sessionscopebootstrap:User',
            '16 = reahl.doc.examples.tutorial.sessionscope.sessionscope:LoginSession',
            '17 = reahl.doc.examples.tutorial.sessionscopebootstrap.sessionscopebootstrap:LoginSession',
            '18 = reahl.doc.examples.tutorial.access1.access1:AddressBook',
            '19 = reahl.doc.examples.tutorial.access1.access1:Collaborator',
            '20 = reahl.doc.examples.tutorial.access1.access1:Address',
            '21 = reahl.doc.examples.tutorial.access1bootstrap.access1bootstrap:AddressBook',
            '22 = reahl.doc.examples.tutorial.access1bootstrap.access1bootstrap:Collaborator',
            '23 = reahl.doc.examples.tutorial.access1bootstrap.access1bootstrap:Address',
            '24 = reahl.doc.examples.tutorial.access2.access2:AddressBook',
            '25 = reahl.doc.examples.tutorial.access2.access2:Collaborator',
            '26 = reahl.doc.examples.tutorial.access2.access2:Address',
            '27 = reahl.doc.examples.tutorial.access2bootstrap.access2bootstrap:AddressBook',
            '28 = reahl.doc.examples.tutorial.access2bootstrap.access2bootstrap:Collaborator',
            '29 = reahl.doc.examples.tutorial.access2bootstrap.access2bootstrap:Address',
            '30 = reahl.doc.examples.tutorial.access.access:AddressBook',
            '31 = reahl.doc.examples.tutorial.accessbootstrap.accessbootstrap:AddressBook',
            '32 = reahl.doc.examples.tutorial.access.access:Collaborator',
            '33 = reahl.doc.examples.tutorial.accessbootstrap.accessbootstrap:Collaborator',
            '34 = reahl.doc.examples.tutorial.access.access:Address',
            '35 = reahl.doc.examples.tutorial.accessbootstrap.accessbootstrap:Address',
            '36 = reahl.doc.examples.tutorial.i18nexample.i18nexample:Address',
            '37 = reahl.doc.examples.tutorial.i18nexamplebootstrap.i18nexamplebootstrap:Address',
            '38 = reahl.doc.examples.tutorial.componentconfig.componentconfig:Address',
            '39 = reahl.doc.examples.tutorial.componentconfigbootstrap.componentconfigbootstrap:Address',
            '40 = reahl.doc.examples.tutorial.migrationexample.migrationexample:Address',
            '41 = reahl.doc.examples.tutorial.migrationexamplebootstrap.migrationexamplebootstrap:Address',
            '42 = reahl.doc.examples.tutorial.jobs.jobs:Address',
            '43 = reahl.doc.examples.tutorial.jobsbootstrap.jobsbootstrap:Address',
            '44 = reahl.doc.examples.tutorial.table.table:Address',
            '45 = reahl.doc.examples.tutorial.tablebootstrap.tablebootstrap:Address',
            '46 = reahl.doc.examples.tutorial.datatable.datatable:Address',
            '47 = reahl.doc.examples.tutorial.datatablebootstrap.datatablebootstrap:Address'    ],
        'reahl.scheduled_jobs': [
            'reahl.doc.examples.tutorial.jobs.jobs:Address.clear_added_flags = reahl.doc.examples.tutorial.jobs.jobs:Address.clear_added_flags',
            'reahl.doc.examples.tutorial.jobsbootstrap.jobsbootstrap:Address.clear_added_flags = reahl.doc.examples.tutorial.jobsbootstrap.jobsbootstrap:Address.clear_added_flags'    ],
        'reahl.dev.commands': [
            'GetExample = reahl.doc.commands:GetExample',
            'ListExamples = reahl.doc.commands:ListExamples'    ],
        'reahl.translations': [
            'reahl-doc = reahl.doc.examples.tutorial.i18nexamplebootstrap.i18nexamplebootstrapmessages'    ],
        'reahl.eggs': [
            'Egg = reahl.component.eggs:ReahlEgg'    ],
        'reahl.configspec': [
            'config = reahl.doc.examples.tutorial.componentconfig.componentconfig:AddressConfig'    ],
                 },
    extras_require={'pillow': ['pillow']},
    cmdclass={'install_test_dependencies': InstallTestDependencies}
)
