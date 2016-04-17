import os

# Make sure the user points to a MuJoCo binary installation.
try:
    bundle_path = os.environ['MUJOCO_PY_BUNDLE_PATH']
except KeyError:
    raise RuntimeError("Please set a MUJOCO_PY_BUNDLE_PATH variable to point to your MuJoCo binary bundle. (It should have a mjkey.txt at the top-level, and linux/osx/win directories containing the relevant unpacked binaries.)")

# Check that they are using the right MuJoCo binary versions
with open(os.path.join(bundle_path, 'version.txt')) as f:
    version = f.read().strip()
    if version != '1.30':
        raise RuntimeError('Your bundle is for MuJoCo version %s, but mujoco-py is tied to MuJoCo version 1.30. Please delete your bundle directory: %s and redownload. (HINT: once deleted, try importing mujoco-py again, and we will print an error with more instructions.)' % (version, bundle_path))

# Check that they are using the right numpy version
import distutils.version, numpy
if distutils.version.StrictVersion(numpy.__version__) < distutils.version.StrictVersion('1.10.4'):
    raise RuntimeError('You are running with numpy {}, but you must use >= 1.10.4. (In particular, earlier versions of numpy have been seen to cause mujoco-py to return different results from later ones.)'.format(numpy.__version__, '1.10.4'))
del numpy, distutils

# Ok, everything's great! Do the actual work now.
from .mjviewer import MjViewer
from .mjcore import MjModel
from .mjcore import register_license
import os
import sys
from mjconstants import *
from platname_targdir import targdir

register_license(os.path.join(bundle_path, "mjkey.txt"))
