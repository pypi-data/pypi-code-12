from setuptools import setup, find_packages
from codecs import open
from os import path


here = path.abspath(path.dirname(__file__))
# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:

    long_description = f.read()

    setup(
    name='fileidentify',
    version='1.8',
    description='File type identification',
    long_description=long_description,
    url='https://github.com/rida914-4/fileidentify',
    author='Tridah',
    author_email='ridah.naseem@ebryx.com',
    license='MIT',
    classifiers=[

    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    ],

    keywords='',
    py_modules=["fileidentify"],
    install_requires=['python-magic'],
    extras_require={
    'dev': [''],
    'test': [''],
    },
    package_data={
    'sample': [''],
    },
    # Although 'package_data' is the preferred approach, in some case you may
    # need to place data files outside of your packages. See:
    # http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files # noqa
    # In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
    data_files=[('', [''])],
    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={
    'console_scripts': [
    'fileidentify=fileidentify.main:main',
    ],
    },
    )
