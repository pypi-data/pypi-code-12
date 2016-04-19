"""setup.py file."""

import uuid

from setuptools import setup, find_packages
from pip.req import parse_requirements

__author__ = 'David Barroso <dbarrosop@dravetech.com>'

install_reqs = parse_requirements('requirements.txt', session=uuid.uuid1())
reqs = [str(ir.req) for ir in install_reqs]

setup(
    name="napalm-base",
    version="0.12.0",
    packages=find_packages(),
    author="David Barroso",
    author_email="dbarrosop@dravetech.com",
    description="Network Automation and Programmability Abstraction Layer with Multivendor support",
    classifiers=[
        'Topic :: Utilities',
        'Programming Language :: Python',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS',
    ],
    url="https://github.com/napalm-automation/napalm-base",
    include_package_data=True,
    install_requires=reqs,
    entry_points={
        'console_scripts': [
            'cl_napalm_configure=napalm.clitools.cl_napalm_configure:main',
        ],
    }
)
