# -*- encoding: utf-8 -*-

import os

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))
from setuptools import setup, Command


class PyTest(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import subprocess
        import sys

        errno = subprocess.call([sys.executable, 'runtests.py'])
        raise SystemExit(errno)


setup(
    name='django-remdow',
    version='0.0.6',
    author='Alexander Sapronov',
    author_email='a@sapronov.me',
    keywords=['django', 'static', 'templatetags', 'downloader', ],
    packages=['django_remdow'],
    include_package_data=True,
    url='https://github.com/WarmongeR1/django-remdow',
    license='MIT',
    description='Simple Django app for manipulating static files (img files)',
    long_description=README,
    install_requires=['django>=1.6', 'beautifulsoup4'],
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
