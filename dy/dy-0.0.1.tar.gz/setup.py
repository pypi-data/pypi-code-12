# References on Packaging & Distributing Python Packages
# ______________________________________________________
# https://packaging.python.org/en/latest/distributing.html
# http://peterdowns.com/posts/first-time-with-pypi.html
# http://stackoverflow.com/questions/6344076/differences-between-distribute-distutils-setuptools-and-distutils2

from setuptools import setup


setup(
    name='dy',
    version='0.0.1',
    packages=['dy'],
    url='https://github.com/MBALearnsToCode/PyDy',
    author='MBA Learns to Code',
    author_email='MBALearnsToCode@UChicago.edu',
    description='Dynamic Optimization / Dynamic Programming',
    long_description='Dynamic Optimization / Dynamic Programming',
    license='MIT License',
    install_requires=[],
    classifiers=[],   # https://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords='dynamic optimization programming')
