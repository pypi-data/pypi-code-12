from setuptools import setup, find_packages

setup(
    name='phuntic',
    description='Python Object Serializer (JSON wrapper)',
    version='0.1.0',
    author='Dmitrii Gerasimenko',
    author_email='kiddima@gmail.com',
    url='https://github.com/kidig/phuntic',
    packages=find_packages(exclude=['phuntic']),
)