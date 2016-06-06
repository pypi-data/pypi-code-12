from setuptools import setup, find_packages
from codecs import open
from os import path
import mcheck

here = path.abspath(path.dirname(__file__))

entry_points = {
    "console_scripts": [
        "mcheck = mcheck.cli:main",
    ]
}

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# get the dependencies and installs
with open(path.join(here, 'requirements.txt'), encoding='utf-8') as f:
    all_reqs = f.read().split('\n')

install_requires = [x.strip() for x in all_reqs if 'git+' not in x]
dependency_links = [x.strip().replace('git+', '') for x in all_reqs if 'git+' not in x]

setup(
    name='mcheck',
    version=mcheck.__version__,
    description='A python package that can be installed with pip.',
    long_description=long_description,
    url='https://github.com/coder-james/mcheck',
    #download_url='https://github.com/coder-james/mcheck/tarball/' + __version__,
    license='GPL',
    entry_points = entry_points,
    classifiers=[
      'Development Status :: 3 - Alpha',
      'Intended Audience :: Developers',
      'Programming Language :: Python :: 2.6',
      'Programming Language :: Python :: 2.7',
      'Programming Language :: Python :: 3',
    ],
    keywords='',
    packages=find_packages(exclude=['docs', 'tests*']),
    include_package_data=True,
    author='Yidong Ma',
    install_requires=install_requires,
    dependency_links=dependency_links,
    author_email='1120598207@qq.com'
)
