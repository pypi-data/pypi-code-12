#
# growler_ext/JadeRenderer.py
#
"""
Loader script for the JadeRenderer class.

This script overloads the expected module object with the class JadeRenderer.
"""

import sys
from growler_jade.jade_renderer import JadeRenderer

sys.modules[__name__] = JadeRenderer
