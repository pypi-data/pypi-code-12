from setuptools import (setup, find_packages)

PACKAGE = "LightMagic"
NAME = "LightMagic"
DESCRIPTION = __import__(PACKAGE).__doc__
AUTHOR = "Maxim Radyukov"
AUTHOR_EMAIL = "maxim.radyukov@gmail.com"
URL = "https://github.com/MaxRV/LightMagic"
VERSION = __import__(PACKAGE).__version__

with open("README.rst") as f:
    long_description = f.read()

with open("requirements.txt") as f:
    install_requires = f.read()

setup(
        name=NAME,
        version=VERSION,
        description=DESCRIPTION,
        long_description=long_description,
        author=AUTHOR,
        author_email=AUTHOR_EMAIL,
        license="MIT",
        url=URL,
        packages=find_packages(exclude=["tests.*", "tests"]),
        classifiers=[
            "Development Status :: 5 - Production/Stable",
            "Intended Audience :: Developers",
            "License :: OSI Approved :: MIT License",
            "Programming Language :: Python",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: Implementation :: CPython",
            "Topic :: Database :: Front-Ends",
            "Operating System :: OS Independent",
        ],
        install_requires=install_requires
)
