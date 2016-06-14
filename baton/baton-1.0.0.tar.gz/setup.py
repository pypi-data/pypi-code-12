from setuptools import setup, find_packages

try:
    from pypandoc import convert
    def read_markdown(file: str) -> str:
        return convert(file, "rst")
except ImportError:
    def read_markdown(file: str) -> str:
        return open(file, "r").read()

setup(
    name="baton",
    version="1.0.0",
    author="Colin Nolan",
    author_email="colin.nolan@sanger.ac.uk",
    packages=find_packages(exclude=["tests"]),
    install_requires=[x for x in open("requirements.txt", "r").read().splitlines()],
    url="https://github.com/wtsi-hgi/python-baton-wrapper",
    license="LGPL",
    description="Python wrapper for baton.",
    long_description=read_markdown("README.md"),
    test_suite="baton.tests",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.5",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)"
    ]
)
