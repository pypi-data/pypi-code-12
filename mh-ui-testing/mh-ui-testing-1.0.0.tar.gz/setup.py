
import os
import re
import codecs
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))


def read(path):
    return codecs.open(os.path.join(here, path), 'r', 'utf-8').read()

version_file = read('mh_cli/__init__.py')
version = re.search(
    r"^__version__ = ['\"]([^'\"]*)['\"]",
    version_file,
    re.M).group(1)

install_requires = [
    "selenium==2.48.0",
    "click==5.1",
    "Fabric==1.11.1",
    "pytimeparse==1.1.5",
    "unipath==1.1",
    "pytest>=2.8.1",
    "pytest-ghostinspector==0.4.0",
    "pytest-xdist==1.14",
    "splinter==0.7.3"
]

setup(
    name='mh-ui-testing',
    version=version,
    packages=find_packages(),
    url='https://github.com/harvard-dce/mh-ui-testing',
    license='Apache 2.0',
    author='Jay Luker',
    author_email='jay_luker@harvard.edu',
    description='Automated admin tasks and tests DCE Matterhorn',
    install_requires=install_requires,
    py_modules=["mh", "mh_pages"],
    entry_points='''
        [console_scripts]
        mh=mh:cli
    '''
)
