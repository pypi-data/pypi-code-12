from setuptools import setup, find_packages

setup(
    name='komodo-google-auth',
    version='1.0.0',
    packages=find_packages(),
    install_requires=[
        'flask-login<=1.0.0',
        'python-social-auth<0.3.0',
        'sqlalchemy>=1.0.0,<2.0.0',
        'komodo>=1.0.0,<2.0.0',
    ],

    # metadata for upload to PyPI
    url = "https://github.com/mic159/komodo-google-auth",
    author = "Michael Cooper",
    author_email = "mic159@gmail.com",
    description = "Plugin for Komodo dashboard that enables authentication behind a google login",
    license = "MIT",
    keywords = "dashboard",
)
