# import Libraries of other lib packages
import bob.io.base

# import our own Library
import bob.extension
bob.extension.load_bob_library('bob.io.image', __file__)

from . import _library
from . import version
from .version import module as __version__

import os

def get_config():
  """Returns a string containing the configuration information.
  """
  import bob.extension
  return bob.extension.get_config(__name__, version.externals)


def get_include_directories():
  """get_include_directories() -> includes

  Returns a list of include directories for dependent libraries, such as libjpeg, libtiff, ...
  This function is automatically used by :py:func:`bob.extension.get_bob_libraries` to retrieve the non-standard include directories that are required to use the C bindings of this library in dependent classes.
  You shouldn't normally need to call this function by hand.

  **Returns:**

  ``includes`` : [str]
    The list of non-standard include directories required to use the C bindings of this class.
    For now, only the directory for the HDF5 headers are returned.
  """
  # try to use pkg_config first
  from bob.extension.utils import find_header, uniq_paths
  from bob.extension import pkgconfig
  import logging
  logger = logging.getLogger("bob.io.image")
  directories = []
  for name, header in (('libjpeg', 'jpeglib.h'), ('libtiff', 'tiff.h'), ('giflib', 'gif_lib.h')):
    # locate pkg-config on our own
    candidates = find_header(header)
    if not candidates:
      logger.warn("could not find %s's `%s' - have you installed %s on this machine?" % (name, header, name))

    directories.append(os.path.dirname(candidates[0]))
  for name in ("libpng",):
    try:
      pkg = pkgconfig(name)
      directories.extend(pkg.include_directories())
    except:
      pass
  return uniq_paths(directories)


def get_macros():
  """get_macros() -> macros

  Returns a list of preprocessor macros, such as ``(HAVE_LIBJPEG, 1)``.
  This function is automatically used by :py:func:`bob.extension.get_bob_libraries` to retrieve the prerpocessor definitions that are required to use the C bindings of this library in dependent classes.
  You shouldn't normally need to call this function by hand.

  **Returns:**

  ``macros`` : [str]
    The list of preprocessor macros required to use the C bindings of this class.
  """
  # try to use pkg_config first
  from bob.extension.utils import find_header, uniq_paths
  from bob.extension import pkgconfig
  macros = []
  for define, header in (('HAVE_LIBJPEG', 'jpeglib.h'), ('HAVE_LIBTIFF', 'tiff.h'), ('HAVE_GIFLIB', 'gif_lib.h')):
    # locate pkg-config on our own
    candidates = find_header(header)
    if candidates:
      macros.append((define, '1'))
  for define, name in (("HAVE_LIBPNG", "libpng"),):
    try:
      pkg = pkgconfig(name)
      macros.append((define, '1'))
    except:
      pass
  return macros


# gets sphinx autodoc done right - don't remove it
__all__ = [_ for _ in dir() if not _.startswith('_')]
