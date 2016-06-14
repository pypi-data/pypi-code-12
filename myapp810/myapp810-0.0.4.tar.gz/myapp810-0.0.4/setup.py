from setuptools import setup

with open('README.rst') as f:
     readme = f.read()

setup(
    name="myapp810",
    version="0.0.4",
    packages=['myapp810'],
    description='114 514',
    long_description=readme,
    url='https://github.com/me/hhh',
    author='me',
    author_email='me@etwings.com',
    license='MIT',
    install_requires=[
        'FuelSDK',
    ],
)
