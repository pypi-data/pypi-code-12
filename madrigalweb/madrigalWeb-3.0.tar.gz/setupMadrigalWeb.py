"""set up file for the Python Madrigal Remote API

$Id: setupMadrigalWeb.py 5573 2015-10-29 15:01:30Z brideout $
"""
import os, os.path, sys

from distutils.core import setup

if sys.argv[1] == 'sdist':
    # update the documentation
    cmd = 'cp MANIFEST.in.madrigalWeb MANIFEST.in'
    os.system(cmd)
    
setup(name="madrigalWeb",
      version="3.0",
      description="Remote Madrigal Python API",
      author="Bill Rideout",
      author_email="brideout@haystack.mit.edu",
      url="http://www.haystack.mit.edu/~brideout/",
      packages=["madrigalWeb"],
      scripts=['madrigalWeb/globalIsprint.py', 'madrigalWeb/globalDownload.py',
               'madrigalWeb/examples/exampleMadrigalWebServices.py']
      )

if sys.argv[1] == 'sdist':
    cmd = 'rm MANIFEST.in'
    os.system(cmd)
    