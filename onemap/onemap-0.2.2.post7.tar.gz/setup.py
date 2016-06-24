from setuptools import setup

try:
  readme = open("README.rst").read()
except (IOError, ImportError):
  readme = open("README.md").read()

setup(
    name='onemap',
    version='0.2.2.post7',
    author='Ruiwen Chua',
    author_email='ruiwen@thoughtmonkeys.com',
    packages=['onemap'],
    url='https://github.com/ruiwen/onemap',
    license='LICENSE.txt',
    description='Wrapper for the OneMapSG API',
    long_description=readme,
    keywords=['onemap', 'onemapsg'],
    install_requires=[
        "requests >= 1.2.3"
    ]
)
