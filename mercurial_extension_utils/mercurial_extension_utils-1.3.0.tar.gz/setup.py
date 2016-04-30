# pylint:disable=missing-docstring

from setuptools import setup, find_packages

VERSION = '1.3.0'
LONG_DESCRIPTION = open("README.txt").read()
INSTALL_REQUIRES = []

setup(
    name="mercurial_extension_utils",
    version=VERSION,
    author='Marcin Kasperski',
    author_email='Marcin.Kasperski@mekk.waw.pl',
    url='http://bitbucket.org/Mekk/mercurial-extension_utils',
    description='Mercurial Extension Utils',
    long_description=LONG_DESCRIPTION,
    license='BSD',
    py_modules=['mercurial_extension_utils'],
    keywords="mercurial hg extension",
    install_requires=INSTALL_REQUIRES,
    # Giving up on python setup.py test, discovery too problematic
    # tests_require=TEST_REQUIRES,
    # test_suite='tests',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: DFSG approved',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Version Control',
        # 'Topic :: Software Development :: Version Control :: Mercurial',
    ],
    zip_safe=True)
