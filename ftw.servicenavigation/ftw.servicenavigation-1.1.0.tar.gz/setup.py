from setuptools import setup, find_packages
import os

version = '1.1.0'

tests_require = [
    'ftw.builder',
    'ftw.testing',
    'ftw.testbrowser',
    'plone.app.testing',
    'ftw.mobile'
]


setup(
    name='ftw.servicenavigation',
    version=version,
    description="",
    long_description="{0}\n{1}".format(
        open("README.rst").read(),
        open(os.path.join("docs", "HISTORY.txt")).read()
    ),

    classifiers=[
        "Environment :: Web Environment",
        'Framework :: Plone',
        'Framework :: Plone :: 4.3',
        "Intended Audience :: Developers",
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],

    keywords='ftw.servicenavigation',
    author='4teamwork AG',
    author_email='mailto:info@4teamwork.ch',
    url='https://github.com/4teamwork/ftw.servicenavigation',
    license='GPL2',

    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['ftw'],
    include_package_data=True,
    zip_safe=False,

    install_requires=[
        'Plone',
        'PyYAML',
        'collective.z3cform.datagridfield',
        'ftw.upgrade',
        'plone.api',
        'plone.formwidget.contenttree',
        'plone.app.relationfield',
        'setuptools',
        'z3c.relationfield',
    ],
    tests_require=tests_require,
    extras_require=dict(tests=tests_require),

    entry_points="""
    # -*- Entry points: -*-
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
