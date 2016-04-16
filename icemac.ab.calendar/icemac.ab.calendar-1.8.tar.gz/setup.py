# -*- coding: utf-8 -*-
import os.path
import setuptools


def read(*path_elements):
    """Read file."""
    return file(os.path.join(*path_elements)).read()


version = '1.8'
long_description = '\n\n'.join([
    read('README.rst'),
    read('CHANGES.rst'),
])

setuptools.setup(
    name='icemac.ab.calendar',
    version=version,
    description="Calendar feature for icemac.addressbook",
    long_description=long_description,
    keywords='icemac addressbook calendar event recurring',
    author='Michael Howitz',
    author_email='icemac@gmx.net',
    download_url='http://pypi.python.org/pypi/icemac.ab.calendar',
    url='https://bitbucket.org/icemac/icemac.ab.calendar',
    license='ZPL 2.1',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Paste',
        'Framework :: Zope3',
        'License :: OSI Approved',
        'License :: OSI Approved :: Zope Public License',
        'Natural Language :: English',
        'Natural Language :: German',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 2 :: Only',
        'Programming Language :: Python :: Implementation',
        'Programming Language :: Python :: Implementation :: CPython',
    ],
    packages=setuptools.find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['icemac', 'icemac.ab'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'Pyphen',
        'decorator',
        'gocept.month >= 1.2',
        'grokcore.annotation',
        'grokcore.component >= 2.5.1.dev1',
        'icemac.addressbook >= 2.6.dev0',
        'icemac.recurrence >= 1.2.dev0',
        'js.classy',
        'setuptools',
        'zope.cachedescriptors',
    ],
    extras_require=dict(
        test=[
            'gocept.testing',
            'icemac.addressbook [test]',
            'zope.testing >= 3.8.0',
        ]),
    entry_points="""
      [fanstatic.libraries]
      calendar = icemac.ab.calendar.browser.resource:lib
      """,
)
