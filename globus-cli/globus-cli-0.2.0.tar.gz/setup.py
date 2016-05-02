import os
from setuptools import setup, find_packages

# single source of truth for package version
version_ns = {}
with open(os.path.join("globus_cli", "version.py")) as f:
    exec(f.read(), version_ns)
version = version_ns['__version__']

setup(
    name="globus-cli",
    version=version,
    packages=find_packages(),
    install_requires=['click', 'globus-sdk>=0.2.0'],

    entry_points={
        'console_scripts': ['globus = globus_cli:main']
    },

    # descriptive info, non-critical
    description="Globus CLI",
    long_description=open("README.rst").read(),
    author="Stephen Rosen",
    author_email="sirosen@globus.org",
    url="https://github.com/globusonline/globus-cli",
    keywords=["globus", "cli", "command line"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: POSIX",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5"
    ],
)
