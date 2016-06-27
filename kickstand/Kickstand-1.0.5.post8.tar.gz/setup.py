#!/usr/bin/env python

__license__ = 'Copyright (c) 2015, Purdue University'
__version__ = '1.0.5.post8'

import os

try:
  from setuptools import setup
  from setuptools.command.install import install
except ImportError:
  from disutils.core import setup
  from disutils.command import install

class post_install(install):
  def run(self):
    install.run(self)

    for inspection_dir in os.listdir('/opt/kickstand/inspections'):
      i_dir = os.path.join('/opt/kickstand/inspections', inspection_dir)
      if( os.path.isdir(i_dir) ):
        for f in os.listdir(i_dir):
          if( f == 'inspect' ):
            os.chmod(os.path.join(i_dir, f), 0555)

setup(
    name             = 'Kickstand',
    version          = __version__,
    description      = 'Machine inventory management system client API',
    long_description = 'An API for interacting with the Kickstand server, which hosts a machine '\
        'inventory database. This API is used to develop CLI tools that talk to the REST API '\
        'hosted by the Kickstand server.',
    author           = 'Seth Cook',
    author_email     = 'sethcook@purdue.edu',
    url              = 'http://www.rcac.purdue.edu',
    packages         = [ 'kickstand', 'kickstand.inventory' ],
    license          = __license__,
    classifiers      = [ 'Programming Language :: Python :: 2.6',
                         'Programming Language :: Python :: 2.7',
                         'Operating System :: Unix',
                         'Development Status :: 4 - Beta', ],
    cmdclass         = { 'install': post_install },
    scripts          = [ 'scripts/kickstand' ],
    data_files       = [ ('/opt/kickstand/inspections/os', ['inspections/os/structure.yaml',
                                                            'inspections/os/inspect']),
                         ('/opt/kickstand/inspections/memory', ['inspections/memory/structure.yaml',
                                                                'inspections/memory/inspect']),
                         ('/usr/local/kickstand/inspections', []),
                       ],
)
