from setuptools import setup, find_packages

version = '1.0.1'

setup(
    name='collective.ogtags',
    version=version,
    description='OpenGraph for plone4',
    long_description=(open('README.rst').read() + '\n' +
                      open('CONTRIBUTORS.rst').read() + '\n' +
                      open('CHANGES.rst').read()),
    # Get more strings from
    # https://pypi.python.org/pypi?:action=list_classifiers
    classifiers=[
        'Framework :: Plone',
        'Programming Language :: Python',
        'Framework :: Plone :: 4.3',
        'Programming Language :: Python :: 2.7',
    ],
    keywords='OpenGraph tags facebook twitter linkedin',
    author='Diederik Veeze',
    author_email='d.veeze@zestsoftware.nl',
    url='https://zestsoftware.nl/',
    license='GPL',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['collective'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
    ],
    entry_points="""
    # -*- Entry points: -*-

    [z3c.autoinclude.plugin]
    target = plone
    """,
)
