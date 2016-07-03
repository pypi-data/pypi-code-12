import codecs
import os.path
import re

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


def fpath(name):
    return os.path.join(os.path.dirname(__file__), name)


def read(fname):
    return codecs.open(fpath(fname), encoding='utf-8').read()


def grep(attrname):
    pattern = r"{0}\W*=\W*'([^']+)'".format(attrname)
    strval, = re.findall(pattern, file_text)
    return strval

file_text = read(fpath('whydtogo/__init__.py'))

setup(
    name='WhydToGo',
    version=grep('__version__'),
    description='Whyd To Go - Take your Whyd playlists away',
    long_description=read(fpath('README.rst')),
    url='https://github.com/Djiit/whydtogo',
    author='Julien Tanay',
    author_email='julien.tanay@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    keywords='whyd scraping youtube-dl',
    packages=['whydtogo'],
    install_requires=read(fpath('requirements.txt')).splitlines(),
    test_suite="tests",
    entry_points={
        'console_scripts': [
            'whydtogo=whydtogo:main',
        ],
    },
)
