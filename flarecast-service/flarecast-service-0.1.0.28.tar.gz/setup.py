import pip
from setuptools import setup
import os

try:
    # fixes dependecy problem on buildserver
    pip.main(['install', '--user', 'pypandoc'])
    import pypandoc

    description = pypandoc.convert('README.md', 'rst')
except:
    description = ''

build_version = os.environ[
    "BUILD_VERSION"] if 'BUILD_VERSION' in os.environ else '0'

setup(
    name='flarecast-service',
    version='0.1.0.' + build_version,
    packages=['flarecast', 'flarecast.service'],
    url='https://dev.flarecast.eu/stash/projects'
        '/INFRA/repos/flarecastservice/',
    license='',
    author='i4Ds',
    author_email='florian.bruggisser@fhnw.ch',
    description='Flarecast Service is the base '
                'package of all flarecast connexion services.',
    long_description=description,
    download_url='https://dev.flarecast.eu/stash/'
                 'scm/infra/flarecastservice.git',
    keywords=['flarecast', 'service', 'web', 'connexion', 'base', 'i4Ds'],
    install_requires=[
        "connexion",
        "Flask-Compress",
        "Flask-Cors"
    ],
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
    ]
)
