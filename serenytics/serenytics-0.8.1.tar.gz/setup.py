import sys
import os.path as osp
from setuptools import setup, find_packages


__version__ = None
path_version = osp.join(osp.dirname(__file__), 'serenytics/version.py')
if sys.version_info[0] == 3:
    exec(open(path_version).read())
else:
    execfile(path_version)


setup(
    name='serenytics',
    version=__version__,
    description='Serenytics API client for python',
    install_requires=['requests[security] >= 2.8.1', 'pandas >= 0.16', 'paramiko >= 1.16'],
    packages=find_packages(),
    include_package_data=True,
    author='Serenytics Team',
    author_email='support@serenytics.com',
    url='https://github.com/Serenytics/serenytics-python-client',
    keywords=['serenytics', 'backend', 'hosted', 'cloud',
              'bi', 'dashboard', 'scripts', 'etl'],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ]
)
