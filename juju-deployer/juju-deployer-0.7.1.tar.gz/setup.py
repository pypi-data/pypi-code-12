from setuptools import setup, find_packages


setup(
    name="juju-deployer",
    version="0.7.1",
    description="A tool for deploying complex stacks with juju.",
    long_description=open("README").read(),
    author="Kapil Thangavelu",
    author_email="kapil.foss@gmail.com",
    url="http://launchpad.net/juju-deployer",
    install_requires=["jujuclient>=0.18", "PyYAML>=3.10", "bzr"],
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python",
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Intended Audience :: System Administrators",
        "Intended Audience :: Developers"],
    test_suite="deployer.tests",
    entry_points={
        "console_scripts": [
            'juju-deployer = deployer.cli:main']})
