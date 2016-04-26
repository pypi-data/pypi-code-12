from setuptools import setup, find_packages

setup(
    name = 'cchen224-ec2',
    version = '0.0.1',
    keywords = ('ec2', 'cchen224'),
    description = 'cc personal use for AWS',
    license = 'MIT License',
    install_requires = ['simplejson>=1.1'],

    author = 'cchen224',
    author_email = 'phantomkidding@gmail.com',

    packages = find_packages(),
    platforms = 'any',
)