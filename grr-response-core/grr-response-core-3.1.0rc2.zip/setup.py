#!/usr/bin/env python
"""Setup configuration for the python grr modules."""

# pylint: disable=unused-variable
# pylint: disable=g-multiple-import
# pylint: disable=g-import-not-at-top
import os
import subprocess

from setuptools import find_packages, setup, Extension
from setuptools.command.install import install
from setuptools.command.sdist import sdist


def find_data_files(source):
  result = []
  for directory, _, files in os.walk(source):
    files = [os.path.join(directory, x) for x in files]
    result.append((directory, files))

  return result


class Sdist(sdist):

  def run(self):
    # Compile the protobufs.
    base_dir = os.getcwd()
    subprocess.check_call(["python", "makefile.py"])

    # Sync the artifact repo with upstream for distribution.
    subprocess.check_call(["python", "makefile.py"], cwd="grr/artifacts")

    sdist.run(self)


class Install(install):
  """Allow some installation options."""
  DEFAULT_TEMPLATE = """
# Autogenerated file. Do not edit. Written by setup.py.
CONFIG_FILE = "%(CONFIG_FILE)s"
"""

  user_options = install.user_options + [
      ("config-file=", None,
       "Specify the default location of the GRR config file."),
  ]

  def initialize_options(self):
    self.config_file = None
    install.initialize_options(self)

  def finalize_options(self):
    if (self.config_file is not None and
        not os.access(self.config_file, os.R_OK)):
      raise RuntimeError("Default config file %s is not readable." %
                         self.config_file)

    install.finalize_options(self)

  def run(self):
    # Update the defaults if needed.
    if self.config_file:
      with open("grr/defaults.py", "wb") as fd:
        fd.write(self.DEFAULT_TEMPLATE % dict(
            CONFIG_FILE=self.config_file))

    install.run(self)


data_files = (find_data_files("docs") +
              find_data_files("executables") +
              find_data_files("scripts") +
              find_data_files("test_data") +
              find_data_files("grr/artifacts") +
              find_data_files("grr/checks") +
              find_data_files("grr/gui/static") +
              find_data_files("grr/gui/local/static"))


setup_args = dict(
    name="grr-response-core",
    version="3.1.0rc2",
    description="GRR Rapid Response",
    license="Apache License, Version 2.0",
    url="https://github.com/google/grr",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    ext_modules=[
        Extension(
            "grr._semantic",
            ["accelerated/accelerated.c"],
        )
    ],
    cmdclass={
        "sdist": Sdist,
        "install": Install,
    },
    install_requires=[
        "GRR-M2Crypto==0.22.6.post2",
        "PyYAML==3.11",
        "binplist==0.1.4",
        "ipaddr==2.1.11",
        "ipython==4.1.1",
        "pexpect==4.0.1",
        "pip>=8.1.1,<9",
        "portpicker==1.1.1",
        "psutil==4.0.0",
        "pyaml==15.8.2",
        "pycrypto==2.6.1",
        "pyinstaller==3.1.1",
        "python-crontab==2.0.1",
        "python-dateutil==2.4.2",
        "pytsk3==20160226",
        "pytz==2015.7",
        "urllib3==1.14",
        "protobuf==2.6.1",
    ],
    extras_require={
        # This is an optional component. Install to get MySQL data
        # store support:
        # pip install grr-response[MySQLDataStore]
        "MySQLDataStore": [
            "MySQL-python==1.2.5"
        ],

        "test": [
            "mock==1.3.0",
            "mox==0.5.3",
            "selenium==2.50.1",
        ],

        "Server": [
            "wsgiref==0.1.2",
            "Werkzeug==0.11.3",
            "Django==1.8.3",
            "oauth2client==1.5.2",
            "rekall-core>=1.5.0.post4",
            "google-api-python-client==1.4.2",
        ],

        # The following requirements are needed in Windows.
        ':sys_platform=="win32"': [
            "WMI==1.4.9",
            "pypiwin32==219",
        ],
    },

    # Data files used by GRR. Access these via the config_lib "resource" filter.
    data_files=data_files
)

setup(**setup_args)
