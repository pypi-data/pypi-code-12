"""
This script updates the vendor package (that contains all pure python
dependencies).

Those package must be installed in the development environment. You can install
them all by running ``sudo pip3 -r requirements.txt``.
"""
import os
import shutil

# packages to embed
import pyqode.qt
import pyqode.core
import pyqode.python
import pyqode.cobol
import pyqode.rst
import pyqode.json
import future
import pygments
import jedi
import pep8
import pyflakes
import restructuredtext_lint
import qdarkstyle
import qcrash
import keyring
import binaryornot
import chardet
import coloredlogs
import humanfriendly
import colorama


BUILD = os.path.abspath('hackedit/vendor')

README = '''"""
This directory contains the pure python dependencies of HackEdit.

You can update the dependencies by running ``update_vendor.py`` (located in
the ``scripts`` folder)
"""
'''


def copy_tree(src, dest):
    try:
        shutil.copytree(src, dest)
    except OSError as e:
        print(e)


def embed_packages(packages):
    for package in packages:
        if package.__file__.endswith('__init__.py'):
            # package
            src = os.path.dirname(package.__file__)
            _, dirname = os.path.split(os.path.dirname(package.__file__))
            dest = os.path.join(BUILD, dirname)
            if 'pyqode' in package.__file__:
                dest = os.path.join(BUILD, 'pyqode', dirname)
            print('copying %s to %s' % (src, dest))
            copy_tree(src, dest)
            if 'pyqode' in package.__file__:
                with open(os.path.join(
                        BUILD, 'pyqode', '__init__.py'), 'w'):
                    pass
        else:
            # single module package, copy it directly
            src = package.__file__
            dest = BUILD
            print('copying %s to %s' % (src, dest))
            shutil.copy(src, dest)

    with open(os.path.join(BUILD, '__init__.py'), 'w') as f:
        f.write(README)


try:
    os.mkdir(BUILD)
except FileExistsError:
    for path in os.listdir(BUILD):
        p = os.path.join(BUILD, path)
        if not p.endswith('.dll'):
            if os.path.isdir(p):
                shutil.rmtree(p)
            else:
                os.remove(p)
finally:
    embed_packages([
        future, pygments, qdarkstyle, jedi, pep8, pyflakes, pyqode.qt, pyqode.core, pyqode.python, pyqode.cobol,
        pyqode.rst, pyqode.json, restructuredtext_lint, qcrash, keyring, binaryornot, chardet, coloredlogs, colorama,
        humanfriendly
    ])
