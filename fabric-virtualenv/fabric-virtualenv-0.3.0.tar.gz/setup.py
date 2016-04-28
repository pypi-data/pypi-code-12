from setuptools import setup, find_packages


setup(
    name="fabric-virtualenv",
    version="0.3.0",
    author='Daniel Pope',
    author_email='lord.mauve@gmail.com',
    url='http://pypi.python.org/pypi/fabric-virtualenv/',
    description=(
        "Some additional functions for working with remote virtualenvs "
        "in Fabric."
    ),
    long_description=open('README').read(),
    packages=find_packages(),
    install_requires=[
        'Fabric'
    ]
)
