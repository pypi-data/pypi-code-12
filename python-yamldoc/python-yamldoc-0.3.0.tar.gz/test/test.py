#!/usr/bin/env python
#-*- coding:utf-8 -*-

from yamldoc import validate

class test(object):

	"""
	desc:
		A test object, with [func1] and [test.func2].
	"""

	@staticmethod
	def func1(a):

		"""
		desc:
			Refers to [func2].

		arguments:
			a:
				desc:	test
				type:	[NoneType, int]
		"""

		pass

	def func2(self, a):

		"""
		desc:
			Refers to [func2].

		arguments:
			a:
				desc:	test
				type:	[NoneType, int]
		"""

		pass

	# def func2(self, e, d, c, b, a, f=0, g=0, h=0):
	#
	# 	"""
	# 	desc:
	# 		Refers to [func1].
	#
	# 	arguments:
	# 		e: test
	# 		c: test
	# 		a:
	# 			desc:	Yes!
	# 			type:	int
	#
	# 	keywords:
	# 		g: tests
	# 		z: Test
	# 	"""
	#
	# 	pass

from yamldoc import _basedoc
_basedoc.docTemplate = u"""%(headerText)s

%(desc)s

%(sections)s
%(misc)s
"""
import yamldoc

df = yamldoc.DocFactory(test)
print(df.qSciApi())
# test
