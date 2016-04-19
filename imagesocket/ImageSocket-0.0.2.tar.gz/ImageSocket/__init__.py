import sys
import os

"""
	------	Python Plugin ( ImageSocket)	------
	This plugin is written by SunnerLi in 2016 - 04
	This file define module of the plugin
	The project is follow MIT License
"""

def add_path(path):
	"""
		Add the module path
	"""
	if path not in sys.path:
		sys.path.insert(0, path)

this = os.path.dirname(__file__)
__all__ = ["logg", "rtp", "work", "ImageSocket"];
print "?"
# Add log module to the PYTHONPATH
#log_path = os.path.join(this, '..', 'LOG')
#add_path(log_path)

# Add RTP module path to PYTHONPATH
#rtp_path = os.path.join(this, '..', 'RTP')
#add_path(rtp_path)