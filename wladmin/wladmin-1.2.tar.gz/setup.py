
from setuptools import setup, find_packages


setup(
    name="wladmin",
    version="1.2",
    description="wladmin skin for the WenlinCMS.",
    long_description=open("README.rst").read(),
    author="Feichi LONG",
    author_email="feichi@longfeichi.com",
    maintainer="Feichi LONG",
    maintainer_email="feichi@longfeichi.com",
    url="http://wenlincms.com",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
)
