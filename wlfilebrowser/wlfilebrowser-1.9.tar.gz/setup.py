
from setuptools import setup, find_packages


setup(
    name="wlfilebrowser",
    version="1.9",
    description="a dependency for the WenlinCMS.",
    long_description=open("README.rst").read(),
    author="Feichi Long",
    author_email="feichi@longfeichi.com",
    maintainer="Feichi Long",
    maintainer_email="feichi@longfeichi.com",
    url="http://wenlincms.com",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
)
