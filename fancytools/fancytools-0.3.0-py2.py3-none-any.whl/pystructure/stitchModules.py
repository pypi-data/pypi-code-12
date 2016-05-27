# -*- coding: utf-8 -*-

def stitchModules(module, fallbackModule):
		'''
		complete missing attributes with those in fallbackModule
		
		imagine you have 2 modules: a and b
		a is some kind of an individualised module of b - but will maybe
		not contain all attributes of b.
		in this case a should use the attributes from b
		
		>>> import types
		>>> a = types.ModuleType('a', 'The a.py module') # you will have of course a file for those
		>>> b = types.ModuleType('b', 'The b.py module')

		>>> b.var1 = 'standard 1'
		>>> b.var2 = 'standard 2'

		>>> a.var1 = 'individual 1'
		
		what we now want is to all all missing attributes from b to a:
		
		>>> stitchModules(a,b)
		
		>>> print a.var1
		individual 1
		>>> print a.var2
		standard 2
		'''
		for name, attr in fallbackModule.__dict__.iteritems():
			if name not in module.__dict__:
				module.__dict__[name] = attr



if __name__ == "__main__":
	import doctest
	doctest.testmod()