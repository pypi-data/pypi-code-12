
VERSION = '0.6.1'

#pylint:disable=missing-docstring,unused-import,import-error

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

LONG_DESCRIPTION = open("README.txt").read()
INSTALL_REQUIRES = [
    "mercurial_extension_utils>=1.3.0",
]

setup(
    name="mercurial_update_version",
    version=VERSION,
    author='Marcin Kasperski',
    author_email='Marcin.Kasperski@mekk.waw.pl',
    url='http://bitbucket.org/Mekk/mercurial-update_version',
    description='Mercurial Update Version Extension',
    long_description=LONG_DESCRIPTION,
    license='BSD',
    py_modules=[
        'mercurial_update_version',
    ],
    install_requires=INSTALL_REQUIRES,
    keywords="mercurial hg version auto-update tag",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: DFSG approved',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Version Control'
    ],
    zip_safe=True)
