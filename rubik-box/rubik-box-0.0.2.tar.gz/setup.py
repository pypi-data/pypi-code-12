import os
import re

from setuptools import setup, Command


def read_version(version_file_name):
    """
    Reads the package version from the supplied file
    """
    version_file = open(os.path.join(version_file_name)).read()
    return re.search("__version__ = ['\"]([^'\"]+)['\"]", version_file).group(1)


setup(
    name='rubik-box',
    version=read_version(os.path.join('rubik_box','__init__.py')),
    description='Rubik\'s cube solver',
    url='https://github.com/colonelmo/rubik-box',
    author='Mohammad Nasirifar',
    author_email='far.nasiri.m@gmail.com',
    license='Beerware',
    keywords='rubik rubik\'s cube solver',
    packages=['rubik_box'],
    include_package_data=True,
    zip_safe=True,
    install_requires= ['markdown'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: Other/Proprietary License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Topic :: Games/Entertainment :: Puzzle Games'
    ],
)
