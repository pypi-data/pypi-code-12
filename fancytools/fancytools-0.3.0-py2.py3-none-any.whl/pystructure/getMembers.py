# -*- coding: utf-8 -*-

'''
Different functions to return members within a given module or package.
'''

import inspect


def getAvailableClassesInModule(prooveModule):
	'''
	return a list of all classes in the given module
	that dont begin with '_'
	'''
	l=tuple(x[1] for x in inspect.getmembers(prooveModule,inspect.isclass))
	l = [x for x in l if x.__name__[0] != "_" ]
	return l


def getAvailableClassesInPackage(package):
	'''
	return a list of all classes in the given package
	whose modules dont begin with '_'
	'''
	l=list(x[1] for x in inspect.getmembers(package,inspect.isclass))

	modules = list(x[1] for x in inspect.getmembers(package,inspect.ismodule))
	for m in modules:
		l.extend(list(x[1] for x in inspect.getmembers(m,inspect.isclass)))
	l = [x for x in l if x.__name__[0] != "_" ]
	n=0
	while n < len(l):
		cls =l[n]
		if not  cls.__module__.startswith(package.__name__):
			l.pop(n)
			n-=1
		n+=1
	return l


def getAvClassNamesInPackage(package):
	'''get the class names within a package'''
	l = getAvailableClassesInPackage(package)
	return [x.__name__ for x in l]


def getAvClassNamesInModule(prooveModule):
	'''get the class names within a module'''
	l = getAvailableClassesInModule(prooveModule)
	return [x.__name__ for x in l]


def getClassInPackageFromName(className, pkg):
	'''
	get a class from name within a package
	'''
	#TODO: more efficiency!
	n = getAvClassNamesInPackage(pkg)
	i = n.index(className)
	c = getAvailableClassesInPackage(pkg)
	return c[i]


def getClassInModuleFromName(className, module):
	'''
	get a class from name within a module
	'''
	n = getAvClassNamesInModule(module)
	i = n.index(className)
	c = getAvailableClassesInModule(module)
	return c[i]



if __name__ == '__main__':
	import numpy
	c_names = getAvClassNamesInPackage(numpy)
	print('classes within numpy are: %s' %c_names )
	print('get class from the first name [%s]: [%s]' %(
					c_names[0], getClassInPackageFromName(c_names[0], numpy) ) )