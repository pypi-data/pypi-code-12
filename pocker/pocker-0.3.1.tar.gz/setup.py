from setuptools import find_packages, setup
from codecs import open
from os import path
import os

#hack to fix hard link error
#http://stackoverflow.com/a/22147112
if os.environ.get('USER','') == 'vagrant':
    del os.link


here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

package_dir = path.dirname(path.abspath(__file__))
with open(path.join(package_dir, 'pocker', 'VERSION')) as version_file:
    __version__ = version_file.read().strip()

setup(
    name='pocker',
    version=__version__,
    description='Python wrapper for docker console client',
    long_description=long_description,
    author='Sergey Anuchin',
    author_email='sergunich@gmail.com',
    url="https://bitbucket.org/levelupdev/pocker",
    license='MIT',
    packages = find_packages(),
    include_package_data=True,

    keywords='docker client',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 2 :: Only ', #FIXME
        #'Programming Language :: Python :: 3.4', #TODO
        #'Programming Language :: Python :: 3.5', #TODO
        'Topic :: System :: Systems Administration',
        'Topic :: Utilities',
    ],
)
