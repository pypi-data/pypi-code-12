#!/usr/bin/env python
#
# Script to build and install Python-bindings.
# Version: 20160316

from __future__ import print_function
import glob
import platform
import os
import shlex
import shutil
import subprocess
import sys

from distutils import sysconfig
from distutils.ccompiler import new_compiler
from distutils.command.build_ext import build_ext
from distutils.command.bdist import bdist
from distutils.command.sdist import sdist
from distutils.core import Extension, setup


class custom_bdist_rpm(bdist):
  """Custom handler for the bdist_rpm command."""

  def run(self):
    print("'setup.py bdist_rpm' command not supported use 'rpmbuild' instead.")
    sys.exit(1)


class custom_build_ext(build_ext):
  """Custom handler for the build_ext command."""

  def _RunCommand(self, command):
    """Runs the command."""
    arguments = shlex.split(command)
    process = subprocess.Popen(
        arguments, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    if not process:
      raise RuntimeError("Running: {0:s} failed.".format(command))

    output, error = process.communicate()
    if process.returncode != 0:
      error = "\n".join(error.split(b"\n")[-5:])
      if sys.version_info[0] >= 3:
        error = error.decode("ascii", errors="replace")
      raise RuntimeError(
          "Running: {0:s} failed with error:\n{1:s}.".format(
              command, error))

    return output

  def build_extensions(self):
    # TODO: move build customization here?
    build_ext.build_extensions(self)

  def run(self):
    compiler = new_compiler(compiler=self.compiler)
    if compiler.compiler_type == "msvc":
      self.define = [
          ("UNICODE", ""),
      ]

    else:
      # We need to run "configure" to make sure config.h is generated
      # properly. We invoke "configure" with "sh" here to make sure
      # that it works on mingw32 with the standard python.org binaries.
      command = "sh configure --help"
      output = self._RunCommand(command)

      # We want to build as much as possible self contained Python binding.
      configure_arguments = []
      for line in output.split(b"\n"):
        line = line.strip()
        line, _, _ = line.rpartition(b"[=DIR]")
        if line.startswith(b"--with-lib") and not line.endswith(b"-prefix"):
          if sys.version_info[0] >= 3:
            line = line.decode("ascii")
          configure_arguments.append("{0:s}=no".format(line))
        elif line == b"--with-openssl":
          configure_arguments.append("--with-openssl=no")
        elif line == b"--with-zlib":
          configure_arguments.append("--with-zlib=no")

      command = "sh configure {0:s}".format(" ".join(configure_arguments))
      output = self._RunCommand(command)

      print_line = False
      for line in output.split(b"\n"):
        line = line.rstrip()
        if line == b"configure:":
          print_line = True

        if print_line:
          if sys.version_info[0] >= 3:
            line = line.decode("ascii")
          print(line)

      self.define = [
          ("HAVE_CONFIG_H", ""),
          ("LOCALEDIR", "\"/usr/share/locale\""),
      ]

    build_ext.run(self)


class custom_sdist(sdist):
  """Custom handler for the sdist command."""

  def run(self):
    if self.formats != ["gztar"]:
      print("'setup.py sdist' unsupported format.")
      sys.exit(1)

    if glob.glob("*.tar.gz"):
      print("'setup.py sdist' remove existing *.tar.gz files from "
            "source directory.")
      sys.exit(1)

    command = "make dist"
    exit_code = subprocess.call(command, shell=True)
    if exit_code != 0:
      raise RuntimeError("Running: {0:s} failed.".format(command))

    if not os.path.exists("dist"):
      os.mkdir("dist")

    source_package_file = glob.glob("*.tar.gz")[0]
    source_package_prefix, _, source_package_suffix = (
        source_package_file.partition("-"))
    sdist_package_file = "{0:s}-python-{1:s}".format(
        source_package_prefix, source_package_suffix)
    sdist_package_file = os.path.join("dist", sdist_package_file)
    os.rename(source_package_file, sdist_package_file)

    # Inform distutils what files were created.
    dist_files = getattr(self.distribution, "dist_files", [])
    dist_files.append(("sdist", "", sdist_package_file))


class ProjectInformation(object):
  """Class to define the project information."""

  def __init__(self):
    """Initializes a project information object."""
    super(ProjectInformation, self).__init__()
    self.include_directories = []
    self.library_name = None
    self.library_names = []
    self.library_version = None

    self._ReadConfigureAc()
    self._ReadMakefileAm()

  @property
  def module_name(self):
    """The Python module name."""
    return "py{0:s}".format(self.library_name[3:])

  @property
  def package_name(self):
    """The package name."""
    return "{0:s}-python".format(self.library_name)

  @property
  def package_description(self):
    """The package description."""
    return "Python bindings module for {0:s}".format(self.library_name)

  @property
  def project_url(self):
    """The project URL."""
    return "https://github.com/libyal/{0:s}/".format(self.library_name)

  def _ReadConfigureAc(self):
    """Reads configure.ac to initialize the project information."""
    file_object = open("configure.ac", "rb")
    if not file_object:
      raise IOError("Unable to open: configure.ac")

    found_ac_init = False
    found_library_name = False
    for line in file_object.readlines():
      line = line.strip()
      if found_library_name:
        library_version = line[1:-2]
        if sys.version_info[0] >= 3:
          library_version = library_version.decode("ascii")
        self.library_version = library_version
        break

      elif found_ac_init:
        library_name = line[1:-2]
        if sys.version_info[0] >= 3:
          library_name = library_name.decode("ascii")
        self.library_name = library_name
        found_library_name = True

      elif line.startswith(b"AC_INIT"):
        found_ac_init = True

    file_object.close()

    if not self.library_name or not self.library_version:
      raise RuntimeError(
          "Unable to find library name and version in: configure.ac")

  def _ReadMakefileAm(self):
    """Reads Makefile.am to initialize the project information."""
    if not self.library_name:
      raise RuntimeError("Missing library name")

    file_object = open("Makefile.am", "rb")
    if not file_object:
      raise IOError("Unable to open: Makefile.am")

    found_subdirs = False
    for line in file_object.readlines():
      line = line.strip()
      if found_subdirs:
        library_name, _, _ = line.partition(b" ")
        if sys.version_info[0] >= 3:
          library_name = library_name.decode("ascii")

        self.include_directories.append(library_name)

        if library_name.startswith("lib"):
          self.library_names.append(library_name)

        if library_name == self.library_name:
          break

      elif line.startswith(b"SUBDIRS"):
        found_subdirs = True

    file_object.close()

    if not self.include_directories or not self.library_names:
      raise RuntimeError(
          "Unable to find include directories and library names in: "
          "Makefile.am")


def GetPythonLibraryDirectoryPath():
  """Retrieves the Python library directory path."""
  path = sysconfig.get_python_lib(True)
  _, _, path = path.rpartition(sysconfig.PREFIX)

  if path.startswith(os.sep):
    path = path[1:]

  return path


project_information = ProjectInformation()

MODULE_VERSION = project_information.library_version
if "bdist_msi" in sys.argv:
  # bdist_msi does not support the library version so we add ".1"
  # as a work around.
  MODULE_VERSION = "{0:s}.1".format(MODULE_VERSION)

PYTHON_LIBRARY_DIRECTORY = GetPythonLibraryDirectoryPath()

SOURCES = []

# TODO: replace by detection of MSC
DEFINE_MACROS = []
if platform.system() == "Windows":
  DEFINE_MACROS.append(("WINVER", "0x0501"))
  # TODO: determine how to handle third party DLLs.
  for library_name in project_information.library_names:
    if library_name != project_information.library_name:
      definition = "HAVE_LOCAL_{0:s}".format(library_name.upper())

    DEFINE_MACROS.append((definition, ""))

# Put everything inside the Python module to prevent issues with finding
# shared libaries since pip does not integrate well with the system package
# management.
for library_name in project_information.library_names:
  source_files = glob.glob(os.path.join(library_name, "*.c"))
  SOURCES.extend(source_files)

source_files = glob.glob(os.path.join(project_information.module_name, "*.c"))
SOURCES.extend(source_files)

# Add the LICENSE file to the distribution.
copying_file = os.path.join("COPYING")
license_file = "LICENSE.{0:s}".format(project_information.module_name)
shutil.copyfile(copying_file, license_file)

LIBRARY_DATA_FILES = [license_file]

# TODO: find a way to detect missing python.h
# e.g. on Ubuntu python-dev is not installed by python-pip

# TODO: what about description and platform in egg file

setup(
    name=project_information.package_name,
    url=project_information.project_url,
    version=MODULE_VERSION,
    description=project_information.package_description,
    long_description=project_information.package_description,
    author="Joachim Metz",
    author_email="joachim.metz@gmail.com",
    license="GNU Lesser General Public License v3 or later (LGPLv3+)",
    cmdclass={
        "build_ext": custom_build_ext,
        "bdist_rpm": custom_bdist_rpm,
        "sdist": custom_sdist,
    },
    ext_modules=[
        Extension(
            project_information.module_name,
            define_macros=DEFINE_MACROS,
            include_dirs=project_information.include_directories,
            libraries=[],
            library_dirs=[],
            sources=SOURCES,
        ),
    ],
    data_files=[(PYTHON_LIBRARY_DIRECTORY, LIBRARY_DATA_FILES)],
)

os.remove(license_file)

