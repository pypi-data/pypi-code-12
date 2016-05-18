#!/usr/bin/env python3

import codecs
import os
from setuptools import setup
import subprocess
import urllib.request
import sys

if sys.version_info < (3, 4):
    raise Exception('Python 3.4 or higher is required to use PyLinkbot3.')

class ExternalResource():
    URL = '' # something like http://hostename.com/proj_name.tar.gz
    FILENAME = '' # proj_name.tar.gz
    UNPACKED_DIR_NAME = '' # proj_name

    def __init__(self):
        self._cwd = os.getcwd()
        self._deps_dir = os.path.join(self._cwd, 'deps')
        self._filename = os.path.join(self._deps_dir, self.FILENAME)

    def exists(self):
        return os.path.exists( 
            os.path.join(self._deps_dir, self.UNPACKED_DIR_NAME) )
        
    def fetch(self):
        if not os.path.exists(self._deps_dir):
            os.mkdir(self._deps_dir)
        urllib.request.urlretrieve(self.URL, self._filename)

    def unpack(self):
        subprocess.check_call(['tar', '-C', self._deps_dir, '-xf', self._filename])

    def getdir(self):
        return os.path.join(self._deps_dir, self.UNPACKED_DIR_NAME)

class NanoPbResource(ExternalResource):
    URL = 'http://koti.kapsi.fi/~jpa/nanopb/download/nanopb-0.3.1-linux-x86.tar.gz'
    FILENAME = 'nanopb-0.3.1-linux-x86.tar.gz'
    UNPACKED_DIR_NAME = 'nanopb-0.3.1-linux-x86'

    def __init__(self):
        super().__init__()

    def build(self):
        # ./deps/nanopb-0.3.1-linux-x86/generator-bin/protoc --proto_path=deps/nanopb-0.3.1-linux-x86/generator/proto --proto_path=LinkbotLabs-SDK/baromesh/interfaces/ --python_out=pbout LinkbotLabs-SDK/baromesh/int
        pb_files = [
            'LinkbotLabs-SDK/baromesh/interfaces/robot.proto',
            'LinkbotLabs-SDK/baromesh/interfaces/daemon.proto',
        ]
        for f in pb_files:
            subprocess.check_call([
                #os.path.join(self.getdir(), 'generator-bin', 'protoc'),
                'protoc',
                '--proto_path='+os.path.join(self.getdir(), 'generator', 'proto'),
                '--proto_path='+os.path.join('LinkbotLabs-SDK', 'baromesh', 'interfaces'),
                '--proto_path='+os.path.join('LinkbotLabs-SDK', 'ribbon-bridge', 'proto'),
                '--python_out='+os.path.join('src', 'linkbot3', 'async'),
                f ])

nanopb = NanoPbResource()
if not nanopb.exists():
    nanopb.fetch()
nanopb.unpack()
nanopb.build()

here = os.path.abspath(os.path.dirname(__file__))
README = codecs.open(os.path.join(here, 'README.txt'), encoding='utf8').read()
setup (name = 'PyLinkbot3',
       author = 'David Ko',
       author_email = 'david@barobo.com',
       version = '3.0.0a2',
       description = "This is a pure Python implementation of PyLinkbot. See http://github.com/BaroboRobotics/PyLinkbot",
       long_description = README,
       package_dir = {'':'src'},
       packages = ['linkbot3', 'linkbot3.async'],
       url = 'http://github.com/BaroboRobotics/PyLinkbot3',
       install_requires=[
           'PyRibbonBridge>=0.0.6', 
           'PySfp>=0.1.1', 
           'websockets>=3.0',],
       classifiers=[
           'Development Status :: 3 - Alpha',
           'Intended Audience :: Education',
           'Operating System :: OS Independent',
           'Programming Language :: Python :: 3.5',
       ],
)
