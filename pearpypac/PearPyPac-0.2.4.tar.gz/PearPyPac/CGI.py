# -*- coding: utf-8 -*-

import os
import cgi


class PearCGI(object):

	def __init__(self):
		return

	def isPost(self):
		if(os.environ["REQUEST_METHOD"] == "POST"):
			return True
		else:
			return False

	def isGet(self):
		if(os.environ["REQUEST_METHOD"] == "GET"):
			return True
		else:
			return False

	def isPut(self):
		if(os.environ["REQUEST_METHOD"] == "PUT"):
			return True
		else:
			return False

	def isDelete(self):
		if(os.environ["REQUEST_METHOD"] == "DELETE"):
			return True
		else:
			return False

	def getParam(self):
		param = cgi.FieldStorage()
		return param

