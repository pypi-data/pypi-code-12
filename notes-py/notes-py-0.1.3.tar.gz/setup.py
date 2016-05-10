from distutils.core import setup

from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name = 'notes-py',
    packages = ['notes_py'],
    version = '0.1.3',
    description = 'A dumb static site generator.',
    long_description = long_description,
    author = 'Maximilian Friedersdorff',
    author_email = 'max@friedersdorff.com',
    license='GPL',
    url = 'https://github.com/maxf130/notes-py',
    download_url = 'https://github.com/maxf130/notes-py/tarball/0.1.3',
    keywords = ['site generator'],
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3.4',
    ],
    install_requires = ['CommonMark>=0.6,<0.7'],
    entry_points={
        'console_scripts': [
            'compile_notes=notes_py.notes:main',
        ],
    },
)
