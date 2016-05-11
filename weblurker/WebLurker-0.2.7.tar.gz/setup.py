from setuptools import setup
from setuptools.command.test import test as TestCommand
import os
import sys

import WebLurker

here = os.path.abspath(os.path.dirname(__file__))


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errcode = pytest.main(self.test_args)
        sys.exit(errcode)

setup(
    name='WebLurker',
    version=WebLurker.__version__,
    url=WebLurker.__github_url__,
    license='http://www.binpress.com/license/view/l/72ebdc04171cf6ec2b1b03c668004b87',
    author='Javier Luna Molina',
    tests_require=['pytest'],
    install_requires=['requests>=2.9.1', 'selenium>=-2.53.1'],
    cmdclass={'test': PyTest},
    author_email='javierlunamolina@gmail.com',
    description='Simple and easy to use web crawler',
    long_description='In progress',
    packages=['WebLurker'],
    include_package_data=True,
    platforms='any',
    test_suite='WebLurker.test.test_weblurker',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Development Status :: 1 - Planning',
        'Natural Language :: English',
        'Intended Audience :: Developers',
        'License :: Other/Proprietary License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Internet :: WWW/HTTP',
        ],
    extras_require={
        'testing': ['pytest'],
    }
)