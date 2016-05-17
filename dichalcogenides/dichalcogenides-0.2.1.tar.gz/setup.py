import os
import re
from setuptools import find_packages, setup

from dichalcogenides import __version__

with open('README.rst', 'r') as f:
    long_description = f.read()

if os.environ.get('READTHEDOCS') == 'True':
    mocked = ['numpy', 'scipy']
    mock_filter = lambda x: re.sub(r'>.+', '', x) not in mocked
else:
    mock_filter = lambda p: True

setup(
    name='dichalcogenides',
    version=__version__,
    author='Evan Sosenko',
    author_email='razorx@evansosenko.com',
    packages=find_packages(exclude=['docs']),
    url='https://github.com/razor-x/dichalcogenides',
    license='MIT',
    description='Python analysis code for dichalcogenide systems.',
    long_description=long_description,
    install_requires=list(filter(mock_filter, [
        'numpy>=1.11.0,<2.0.0',
        'scipy>=0.17.0,<1.0.0',
        'pyyaml>=3.11,<4.0'
    ]))
)
