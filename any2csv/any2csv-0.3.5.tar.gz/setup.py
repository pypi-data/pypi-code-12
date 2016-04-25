# -*- encoding: utf-8 -*-
from setuptools import setup, find_packages

version = '0.3.5'

setup(
    name='any2csv',
    version=version,
    description="A tool to generate csv file from a list of python instances",
    long_description="""\
""",
    # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: General",
    ],
    keywords='csv python',
    author='Jerome Collette, Florent Aide',
    author_email='collette.jerome@gmail.com, florent.aide@gmail.com',
    url='https://bitbucket.org/faide/any2csv',
    license='BSD License',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "pyjon.utils",
        "six",
        "any2 >= 0.3.1",
    ],
    entry_points="""
    # -*- Entry points: -*-
    """,
    test_suite='nose.collector',
)
