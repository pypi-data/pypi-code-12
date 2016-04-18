
from setuptools import setup, find_packages


setup(
    name="syfilebrowser",
    version="1.0",
    description="a dependency for the ShuyuCMS.",
    long_description=open("README.rst").read(),
    author="Feichi Long",
    author_email="feichi@longfeichi.com",
    maintainer="Feichi Long",
    maintainer_email="feichi@longfeichi.com",
    url="http://zhidaoii.com",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
)
