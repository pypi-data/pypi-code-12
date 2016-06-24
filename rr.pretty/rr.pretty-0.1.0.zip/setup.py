from setuptools import setup, find_packages
import pkgutil


with open("README.rst", "r") as readme_file:
    readme = readme_file.read()

setup(
    name="rr.pretty",
    version=pkgutil.get_data("rr.pretty", "VERSION").strip(),
    description="Helpers for creation of nicer repr() and str().",
    long_description=readme,
    url="https://github.com/2xR/rr.pretty",
    author="Rui Jorge Rei",
    author_email="rui.jorge.rei@googlemail.com",
    license="MIT",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
    ],
    packages=find_packages(),
    package_data={"": ["LICENSE", "VERSION"]},
)
