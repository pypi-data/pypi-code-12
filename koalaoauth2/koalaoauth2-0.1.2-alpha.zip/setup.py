from distutils.core import setup

setup(
    name='koalaoauth2',
    packages=['koalaoauth2'],  # this must be the same as the name above
    version='0.1.2-alpha',
    description='',
    author='Matt Badger',
    author_email='foss@lighthouseuk.net',
    url='https://github.com/LighthouseUK/koalaoauth2',  # use the URL to the github repo
    download_url='https://github.com/LighthouseUK/koalaoauth2/tarball/0.1.1-alpha',  # I'll explain this in a second
    keywords=['gae', 'lighthouse', 'koala'],  # arbitrary keywords
    classifiers=[],
    requires=['koalacore', 'blinker', 'oauthlib']
)
