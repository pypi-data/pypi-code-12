from setuptools import setup
from codecs import open
from os import path
from ffmpymedia import __version__

here = path.abspath(path.dirname(__file__))

# Get the long description from the relevant file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='ffmpymedia',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # http://packaging.python.org/en/latest/tutorial.html#version
    version=__version__,

    description='Wrapper around the FFMPEG utility',
    long_description=long_description,

    packages=['ffmpymedia'],

    # The project's main homepage.
    url='https://github.com/flaviocpontes/ffmpymedia',
    download_url='https://github.com/flaviocpontes/ffmpymedia/tarball/0.3.2.2',

    # Choose your license
    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],

    author='Flávio Cardoso Pontes',
    author_email='flaviopontes@acerp.org.br',

    keywords=['media', 'ffmpeg']
)
