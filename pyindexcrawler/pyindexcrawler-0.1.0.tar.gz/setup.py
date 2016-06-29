from setuptools import setup

setup(
    # Application name:
    name="pyindexcrawler",

    # Version number (initial):
    version="0.1.0",

    # Application author details:
    author="Anthony",
    author_email="ACTrevis@rockwellautomation.com",

    # Packages
    packages=["pyindexcrawler"],

    # Include additional files into the package
    include_package_data=True,

    # Details
    url="https://testpypi.python.org/pypi",

    #
    # license="LICENSE.txt",
    description="Artifactory file structure crawler",

    long_description=open("README.txt").read(),

    # Dependent packages (distributions)
    install_requires=[
        "requests >= 2.10.0",
        "HTMLParser >= 0.0.1",
        "BS4 >= 0.0.1",
        "xlsxwriter >= 0.9.2",
    ],
	
)