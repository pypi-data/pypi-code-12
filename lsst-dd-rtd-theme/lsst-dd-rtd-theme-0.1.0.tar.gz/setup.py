# -*- coding: utf-8 -*-
"""Fork of sphinx_rtd_theme for LSST design documents.

Original repo is at:

.. _github: https://www.github.com/snide/sphinx_rtd_theme

Fork lives at:

    https://github.com/lsst-sqre/lsst_dd_rtd_theme

"""
from setuptools import setup
from lsst_dd_rtd_theme import __version__


setup(
    name='lsst-dd-rtd-theme',
    version=__version__,
    url='https://github.com/lsst-sqre/lsst_dd_rtd/theme/',
    license='MIT',
    author='Jonathan Sick, originally Dave Snider',
    author_email='jsick@lsst.org',
    description='ReadTheDocs.org theme for Sphinx, 2013 version,'
                'forked by LSST/AURA.',
    long_description=open('README.rst').read(),
    zip_safe=False,
    packages=['lsst_dd_rtd_theme'],
    package_data={'lsst_dd_rtd_theme': [
        'theme.conf',
        '*.html',
        'static/css/*.css',
        'static/js/*.js',
        'static/font/*.*'
    ]},
    include_package_data=True,
    install_requires=open('requirements.txt').read().splitlines(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: BSD License',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'Topic :: Documentation',
        'Topic :: Software Development :: Documentation',
    ],
)
