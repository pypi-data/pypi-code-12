from setuptools import setup, find_packages


setup(
    name='gocept.month',
    version='2.0',
    author='gocept gmbh & co. kg',
    author_email='mail@gocept.com',
    url='https://bitbucket.org/gocept/gocept.month',
    description="A datatype which stores a year and a month.",
    long_description=(
        open('COPYRIGHT.txt').read() +
        '\n\n' +
        open('README.rst').read() +
        '\n\n' +
        open('CHANGES.rst').read()),
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    license='ZPL 2.1',
    classifiers="""\
License :: OSI Approved
License :: OSI Approved :: Zope Public License
Programming Language :: Python
Programming Language :: Python :: 2
Programming Language :: Python :: 2.7
Programming Language :: Python :: 3
Programming Language :: Python :: 3.4
Programming Language :: Python :: 3.5
Programming Language :: Python :: Implementation :: CPython
Programming Language :: Python :: Implementation :: PyPy
Development Status :: 5 - Production/Stable
Framework :: Zope2
Framework :: Zope3
Framework :: Pyramid
Framework :: Plone
Intended Audience :: Developers
Natural Language :: English
Operating System :: OS Independent
Topic :: Software Development
Topic :: Software Development :: Libraries
Topic :: Software Development :: Libraries :: Python Modules
Topic :: Utilities
""".splitlines(),
    namespace_packages=['gocept'],
    install_requires=[
        'setuptools',
        'zope.component',
        'zope.i18nmessageid',
        'zope.interface >= 4.0',
        'zope.schema',
    ],
    extras_require=dict(
        form=[
            'z3c.form >= 3.0',
            'zope.formlib >= 4.0',
        ],
        test=[
            'zope.testing',
        ]),
)
