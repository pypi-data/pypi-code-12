from pygaze._display.pygamedisplay import PyGameDisplay
from pygaze._display.psychopydisplay import PsychoPyDisplay
from inspect import ismethod

def copy_docstr(src, target):
	
	"""
	Copies docstrings from the methods of a source class to the methods of a
	target class.
	
	Arguments:
	src		--	The source class.
	target	--	The target class.
	"""

	for attr_name in dir(target):
		if not hasattr(src, attr_name) or not ismethod(getattr(src, attr_name)):
			print 'Skipping %s' % attr_name
			continue
		print 'Copying %s' % attr_name
		getattr(target, attr_name).__func__.__doc__ = getattr(src, \
			attr_name).__func__.__doc__
		
copy_docstr(PyGameDisplay, PsychoPyDisplay)
