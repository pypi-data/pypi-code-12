from __future__ import print_function, unicode_literals
from setuptools import setup, find_packages


__author__ = "danishabdullah"

with open("requirements.txt", 'r') as fyle:
    requirements = fyle.readlines()

setup(
    name="bigschema",
    description="bigschema provide primitives for writing more maintainable/readable schemas for bigquery in yaml"
                "and getting bigquery target output from the specification.",
    author="Danish Abdullah",
    author_email="dev@danishabdullah.com",
    version="1.0.2",
    url="https://github.com/danishabdullah/bigschema",
    license="BSD 3 Clause",
    long_description=open("README.md").read(),
    packages=find_packages(),
    entry_points="""
    [console_scripts]
    bigschema=bigschema.scripts.cli:cli
    """,
    install_requires=requirements,
    zip_safe=False,
    keywords="bigschema bigquery json java schema transformation",
    classifiers=[
        "Development Status :: 6 - Mature",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5"
    ]
)
