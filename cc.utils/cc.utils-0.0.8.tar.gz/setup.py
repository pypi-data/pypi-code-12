from setuptools import setup, find_packages

setup(
    name = 'cc.utils',
    version = '0.0.8',
    keywords = ('cchen224'),
    description = 'cc personal use',
    license = 'MIT License',
    install_requires = ['google-api-python-client'],
    include_package_data=True,
    zip_safe=True,

    author = 'cchen224',
    author_email = 'phantomkidding@gmail.com',

    packages = find_packages(),
    platforms = 'any',
)