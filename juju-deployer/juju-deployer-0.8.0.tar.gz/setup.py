from __future__ import absolute_import
from setuptools import setup, find_packages


setup(
    name="juju-deployer",
    version="0.8.0",
    description="A tool for deploying complex stacks with juju.",
    long_description=open("README").read(),
    author="Kapil Thangavelu",
    author_email="kapil.foss@gmail.com",
    url="http://launchpad.net/juju-deployer",
    install_requires=["jujuclient>=0.18", "PyYAML>=3.10", "six"],
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Developers"],
    test_suite="deployer.tests",
    entry_points={
        "console_scripts": [
            'juju-deployer = deployer.cli:main']})
