from setuptools import setup
from setuptools.command.test import test as TestCommand
import os
import sys


if sys.version_info < (3, 5):
    raise RuntimeError("libskaro requires Python 3.5+")


# Find __version__ without import that requires dependencies to be installed:
exec(open(os.path.join(
    os.path.dirname(__file__), 'libskaro/version.py'
)).read())


class Pep8Command(TestCommand):

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pep8
        style_guide = pep8.StyleGuide(config_file='setup.cfg')
        report = style_guide.check_files(['libskaro'])
        if report.total_errors:
            sys.exit(1)


with open('README.rst') as f:
    readme = f.read()


install_requires = [
    'websockets',
    'cbor',
]


setup(
    name='libskaro',
    version=__version__,
    description='a library that simplifies working with skaro protocol.',
    long_description=readme,
    url='https://gitlab.com/exarh-team/libskaro',
    author='Alexandr Danilov',
    author_email='modos189@ya.ru',
    license='MIT',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Topic :: Communications :: Chat',
    ],
    packages=['libskaro'],
    install_requires=install_requires,
    tests_require=[
        'pep8==1.7.0',
    ],
    cmdclass={
        'style': Pep8Command,
    },
)
