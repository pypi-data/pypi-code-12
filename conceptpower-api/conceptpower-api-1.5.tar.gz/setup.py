from distutils.core import setup

DISTNAME = 'conceptpower-api'
AUTHOR = 'E. Peirson, Digital Innovation Group @ ASU'
MAINTAINER = 'Erick Peirson'
MAINTAINER_EMAIL = 'erick [dot] peirson [at] asu [dot] edu'
DESCRIPTION = ('A very simple library for querying a Conceptpower REST API.')
LICENSE = 'GNU GPL 3'
URL = 'https://github.com/erickpeirson/Conceptpower-API'
VERSION = '1.5'

PACKAGES = [ 'conceptpower',]

setup(
    name=DISTNAME,
    author=AUTHOR,
    author_email=MAINTAINER_EMAIL,
    maintainer=MAINTAINER,
    maintainer_email=MAINTAINER_EMAIL,
    description=DESCRIPTION,
    license=LICENSE,
    url=URL,
    version=VERSION,
    packages = PACKAGES,
    install_requires=[
        "requests",
    ],
)
