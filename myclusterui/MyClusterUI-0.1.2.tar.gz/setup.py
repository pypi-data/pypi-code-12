from setuptools import setup, find_packages
import os
import re
from myclusterui.version import get_git_version


classes = """
    Development Status :: 4 - Beta
    Intended Audience :: Developers
    License :: OSI Approved :: BSD License
    Topic :: System :: Logging
    Programming Language :: Python
    Programming Language :: Python :: 2
    Programming Language :: Python :: 2.7
    Operating System :: POSIX :: Linux
"""
classifiers = [s.strip() for s in classes.split('\n') if s]


setup(
    name='MyClusterUI',
    version=get_git_version(),
    packages=find_packages(exclude=['tests', 'tests.*']),
    license='BSD',
    author='Zenotech',
    author_email='admin@zenotech.com',
    url='https://github.com/zenotech/MyClusterUI',
    classifiers=classifiers,
    description='UI for MyCluster Application',
    long_description=open('README.md').read(),
    install_requires=['MyCluster','PySide','qdarkstyle'],
    scripts=['scripts/myclusterui'],
    include_package_data=True,
    package_data = {
        '': ['*.md','RELEASE-VERSION'],
        'myclusterui':['images/*.png','images/*.jpg'],
    },
    data_files = [('share/MyClusterUI', ['RELEASE-VERSION']),],
)
