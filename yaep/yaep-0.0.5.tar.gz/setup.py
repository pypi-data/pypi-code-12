import os
from distutils.core import setup
from setuptools import find_packages


try:
    import pypandoc
except ImportError:
    class pypandoc(object):
        @classmethod
        def convert(self, data, type, format):
            return data


__version__ = 'Unset'
with open('src/yaep/version.py') as vfp:
    vd = vfp.read().strip()
    __version__ = vd.split('=')[1].strip().strip('\'').strip('"')

requirements = []
if os.path.exists('requirements.txt'):
    requirements = [r.strip() for r in open('requirements.txt')]


readme = open('README.md').read()
changelog = open('CHANGELOG.md').read()
long_description = readme + '\n\n' + changelog


config = {
    'description': 'YAEP - Yet Another Environment Package',
    'long_description': pypandoc.convert(long_description, 'rst', format='md'),
    'author': 'James Kelly',
    'author_email': 'pthread1981@gmail.com',
    'license': 'ISC',
    'url': 'https://github.com/jimjkelly/yaep',
    'version': __version__,
    'install_requires': requirements,
    'tests_require': ['nose'],
    'test_suite': 'nose.collector',
    'setup_requires': ['pypandoc'],
    'packages': find_packages('src'),
    'package_dir': {'': 'src'},
    'scripts': [],
    'name': 'yaep',
    'zip_safe': False,
}

setup(**config)
