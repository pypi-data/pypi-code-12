from os import path

from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))

setup(
        name='baconql',
        version='0.0.1',
        description='Python SQL without ORM & easy migrations',
        long_description=open('README.md').read(),

        url='https://github.com/lsenta/baconql',
        author='lsenta',
        # author_email='',
        # maintainer='',
        # maintainer_email='',

        # license='',

        packages=find_packages(),
        entry_points={
            'console_scripts': ['baconql = baconql.cli:execute']
        },
        classifiers=[
            'Development Status :: 3 - Alpha',

            'Intended Audience :: Developers',

            # TODO: Add Topic :: etc
            # TODO: Add License :: etc

            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.7',
            # TODO: Add more compat if possible (3, 2.6)
        ],
        install_requires=[
            'SQLAlchemy>=1.0.13',
            'click>=6.6',
            'Jinja2>=2.8',
        ]
)
