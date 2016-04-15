import os

# Make sure the user points to a MuJoCo binary installation.
try:
    bundle_path = os.environ['MUJOCO_PY_BUNDLE_PATH']
except KeyError:
    raise RuntimeError("Please set a MUJOCO_PY_BUNDLE_PATH variable to point to your MuJoCo binary bundle. (It should have a mjkey.txt at the top-level, and linux/osx/win directories containing the relevant unpacked binaries.)")

with open(os.path.join(bundle_path, 'version.txt')) as f:
    version = f.read().strip()
    if version != '1.30':
        raise RuntimeError('Your bundle is for MuJoCo version %s, but mujoco-py is tied to MuJoCo version 1.30. Please delete your bundle directory: %s and redownload. (HINT: once deleted, try importing mujoco-py again, and we will print an error with more instructions.)' % (version, bundle_path))

from .mjviewer import MjViewer
from .mjcore import MjModel
from .mjcore import register_license
import os
import sys
from mjconstants import *
from platname_targdir import targdir

register_license(os.path.join(bundle_path, "mjkey.txt"))
