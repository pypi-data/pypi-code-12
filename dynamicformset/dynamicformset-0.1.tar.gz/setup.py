import os
from setuptools import setup, find_packages, Command

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

README = open('README.md').read()
try:
    version = open('version.txt').read()
except IOError:
    version = '0'


class TestCommand(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        if self.distribution.install_requires:
            self.distribution.fetch_build_eggs(
                self.distribution.install_requires)
        if self.distribution.tests_require:
            self.distribution.fetch_build_eggs(self.distribution.tests_require)

        from django.conf import settings
        settings.configure(
            DATABASES={'default': {'NAME': ':memory:', 'ENGINE': 'django.db.backends.sqlite3'}},
            INSTALLED_APPS=('dynamicformset',),
            MIDDLEWARE_CLASSES=(),
            TEMPLATE_LOADERS=('django.template.loaders.app_directories.Loader',),
        )
        from django.core.management import call_command
        import django

        if django.VERSION[:2] >= (1, 7):
            django.setup()
        call_command('test', 'dynamicformset')


setup(
    name='dynamicformset',
    version=version,
    packages=find_packages(),
    include_package_data=True,
    license='BSD',  # example license
    description='',
    long_description=README,
    author='Stan Misiurev',
    author_email='misiurev@ncbi.nlm.nih.gov',
    install_requires=['Django'],
    tests_require=[],
    test_suite='dynamicformset.tests',
    cmdclass={'test': TestCommand},
)
