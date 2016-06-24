from setuptools import setup, find_packages
from pyfoobot import __version__

DOWNLOAD_URL = ('https://github.com/philipbl/pyfoobot/archive/'
                '{}.zip'.format(__version__))
PACKAGES = find_packages(exclude=['tests', 'tests.*'])
REQUIRES = [
    'requests>=2.7',
]

setup(
    name='pyfoobot',
    version=__version__,
    license='MIT License',
    url='https://github.com/philipbl/pyfoobot',
    download_url=DOWNLOAD_URL,
    author='Philip Lundrigan',
    author_email='philiplundrigan@gmail.com',
    description='A Python wrapper around the Foobot air quality API.',
    long_description=open('README.rst').read(),
    packages=PACKAGES,
    platforms='any',
    install_requires=REQUIRES,
    keywords=['air quality', 'sensor', 'IoT'],
    classifiers=[
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.4',
    ],
)
