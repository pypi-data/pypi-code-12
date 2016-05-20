from setuptools import setup, find_packages
import os

version = '1.0.0'
maintainer = 'Martin Baechtold'

tests_require = [
    'ftw.builder',
    'ftw.testing',
    'ftw.testbrowser',
    'plone.app.testing',
    'plone.testing',
]

extras_require = {
    'tests': tests_require,
    'test': tests_require,
}

setup(
    name='ftw.htmlblock',
    version=version,
    description='A block rendering unescaped HTML to be used on a content '
                'page powered by ftw.simplelayout',
    long_description=open('README.rst').read() + '\n' + open(
        os.path.join('docs', 'HISTORY.txt')).read(),

    # Get more strings from
    # http://www.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Framework :: Plone',
        'Framework :: Plone :: 4.3',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],

    keywords='ftw plone html block',
    author='4teamwork AG',
    author_email='mailto:info@4teamwork.ch',
    maintainer=maintainer,
    url='https://github.com/4teamwork/ftw.htmlblock',
    license='GPL2',

    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['ftw', ],
    include_package_data=True,
    zip_safe=False,

    install_requires=[
        'ftw.simplelayout [contenttypes]',
        'setuptools',
        'plone.api>=1.3.0',
        'plone.dexterity',
        'plone.app.dexterity',
        'Plone',
    ],

    tests_require=tests_require,
    extras_require=extras_require,

    entry_points="""
    # -*- Entry points: -*-
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
