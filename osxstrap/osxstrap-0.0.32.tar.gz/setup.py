# -*- coding: utf-8 -*-


"""setup.py: setuptools control."""


import re
from setuptools import setup


version = re.search(
    '^__version__\s*=\s*"(.*)"',
    open('osxstrap/osxstrap.py').read(),
    re.M
    ).group(1)


with open("README.md", "rb") as f:
    long_descr = f.read().decode("utf-8")

files = ['ansible/*']

setup(
    name = "osxstrap",
    packages = ["osxstrap"],
    install_requires=[
        'pyyaml',
        'Click',
        'colorama',
        'ansible==1.9.4',
        'simplegist',
        'python-dotenv',
        'github3.py'
    ],
    package_data = {'osxstrap' : files },
    entry_points = {
        "console_scripts": ['osxstrap = osxstrap.osxstrap:cli']
        },
    version = version,
    description = "Better OSX provisioning using Ansible.",
    long_description = long_descr,
    author = "Jeremy Litten",
    author_email = "jeremy.litten@gmail.com",
    url = "https://github.com/osxstrap/osxstrap",
    license='MIT License',
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        'Environment :: Console',
        'Intended Audience :: System Administrators',
        'Topic :: System :: Systems Administration',

        # Pick your license as you wish (should match "license" above)
         'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ]
)
