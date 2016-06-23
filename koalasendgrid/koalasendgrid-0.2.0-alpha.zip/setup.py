from distutils.core import setup

setup(
    name='koalasendgrid',
    packages=['koalasendgrid'],  # this must be the same as the name above
    version='0.2.0-alpha',
    description='',
    author='Matt Badger',
    author_email='foss@lighthouseuk.net',
    url='https://github.com/LighthouseUK/koalasendgrid',  # use the URL to the github repo
    download_url='https://github.com/LighthouseUK/koalasendgrid/tarball/0.2.0-alpha',  # I'll explain this in a second
    keywords=['gae', 'lighthouse', 'koala'],  # arbitrary keywords
    classifiers=[],
    requires=['sendgrid']
)
