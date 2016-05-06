from setuptools import setup, find_packages

setup(
    name = 'cchen224-ec2',
    version = '0.0.60',
    keywords = ('ec2', 'cchen224'),
    description = 'cc personal use for AWS',
    license = 'MIT License',
    install_requires = ['google-api-python-client','tweepy','python-instagram','bs4', 'geopy'],
    include_package_data=True,
    zip_safe=True,

    author = 'cchen224',
    author_email = 'phantomkidding@gmail.com',

    packages = find_packages(),
    platforms = 'any',
)