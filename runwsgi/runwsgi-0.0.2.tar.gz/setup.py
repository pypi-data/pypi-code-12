
# -*- coding: utf-8 -*-
import os, io
from setuptools import setup

from runwsgi.runwsgi import __version__
here = os.path.abspath(os.path.dirname(__file__))
README = io.open(os.path.join(here, 'README.rst'), encoding='UTF-8').read()
CHANGES = io.open(os.path.join(here, 'CHANGES.rst'), encoding='UTF-8').read()
setup(name='runwsgi',
      version=__version__,
      description="A simple runner for Python wsgi application. Like Gunicorn but can run on Windows. It's to simple, so do not use at production environment.",
      long_description=README + '\n\n\n' + CHANGES,
      url='https://github.com/sintrb/runwsgi',
      classifiers=[
          'Intended Audience :: Developers',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 2.7',
      ],
      keywords='runwsgi wsgirunner wsgi',
      author='sintrb',
      author_email='sintrb@gmail.com',
      license='Apache',
      packages=['runwsgi'],
      scripts = ['runwsgi/runwsgi', 'runwsgi/runwsgi.bat'],
      include_package_data=True,
      zip_safe=False)