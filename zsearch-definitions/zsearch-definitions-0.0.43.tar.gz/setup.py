from setuptools import setup, find_packages

setup(
    name = "zsearch-definitions",
    description = "Egg version of files that can be used for interacting with zdb through python",
    version = "0.0.43",
    license = "Apache License, Version 2.0",
    author = "Zakir Durumeric",
    author_email = "zakird@gmail.com",
    maintainer = "Zakir Durumeric",
    maintainer_email = "zakird@gmail.com",
    keywords = "python json zsearch",
    zip_safe = False,
    install_requires = [
        "zschema"
    ],
    packages = [
        "zsearch_definitions",
    ]
)

