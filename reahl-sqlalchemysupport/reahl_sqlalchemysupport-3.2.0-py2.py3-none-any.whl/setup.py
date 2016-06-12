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
    name='reahl-sqlalchemysupport',
    version='3.2.0',
    description='Support for using SqlAlchemy with Reahl.',
    long_description='Reahl is a web application framework that allows a Python programmer to work in terms of useful abstractions - using a single programming language.\n\nThis package contains infrastructure necessary to use Reahl with SqlAlchemy or Elixir.\n\nSee http://www.reahl.org/docs/3.2/tutorial/gettingstarted.d.html for installation instructions. ',
    url='http://www.reahl.org',
    maintainer='Iwan Vosloo',
    maintainer_email='iwan@reahl.org',
    packages=['reahl', 'reahl.sqlalchemysupport_dev', 'reahl.sqlalchemysupport'],
    py_modules=['setup'],
    include_package_data=False,
    package_data={'': ['*/LC_MESSAGES/*.mo']},
    namespace_packages=['reahl'],
    install_requires=['reahl-component>=3.2,<3.3', 'sqlalchemy>=0.9.2,<0.9.999', 'alembic>=0.6,<0.6.999'],
    setup_requires=['reahl-bzrsupport>=3.2,<3.3'],
    tests_require=['nose', 'reahl-sqlitesupport>=3.2,<3.3', 'reahl-domain>=3.2,<3.3', 'reahl-dev>=3.2,<3.3', 'reahl-tofu>=3.2,<3.3', 'reahl-stubble>=3.2,<3.3'],
    test_suite='reahl.sqlalchemysupport_dev',
    entry_points={
        'reahl.persistlist': [
            '0 = reahl.sqlalchemysupport:SchemaVersion'    ],
        'reahl.eggs': [
            'Egg = reahl.component.eggs:ReahlEgg'    ],
        'reahl.configspec': [
            'config = reahl.sqlalchemysupport:SqlAlchemyConfig'    ],
        'reahl.migratelist': [
            '0 = reahl.sqlalchemysupport.elixirmigration:ElixirToDeclarativeSqlAlchemySupportChanges'    ],
                 },
    extras_require={},
    cmdclass={'install_test_dependencies': InstallTestDependencies}
)
