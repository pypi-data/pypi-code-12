from distutils.core import setup

setup(
    name='koalacompanies',
    packages=['koalacompanies'],  # this must be the same as the name above
    version='0.1.1-alpha',
    description='Addon module for koalacore which provides company profiles.',
    author='Matt Badger',
    author_email='foss@lighthouseuk.net',
    url='https://github.com/LighthouseUK/koalacompanies',  # use the URL to the github repo
    download_url='https://github.com/LighthouseUK/koalacompanies/tarball/0.1.1-alpha',  # I'll explain this in a second
    keywords=['gae', 'lighthouse', 'koala'],  # arbitrary keywords
    classifiers=[],
    requires=['koalacore']
)
