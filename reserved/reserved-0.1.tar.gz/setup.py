
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name = 'reserved',
    packages = ['reserved'],
    version = '0.1',
    description = 'Check usernames for reserved email addresses, subdomains, or Unix usernames.',
    license = 'BSD',
    classifiers = [
        'Programming Language :: Python',
        'License :: OSI Approved :: BSD License',
        'Topic :: Communications :: Email',
        'Operating System :: OS Independent',
    ],
    author = 'Ayke van Laethem',
    author_email = 'aykevanlaethem@gmail.com',
    url = 'https://github.com/aykevl/reserved',
    download_url = 'https://github.com/aykevl/reserved/tarball/0.1',
    keywords = ['username', 'unix', 'email', 'authentication', 'signup'],
    install_requires = [
        'pyyaml',
    ],
    include_package_data = True,
)
