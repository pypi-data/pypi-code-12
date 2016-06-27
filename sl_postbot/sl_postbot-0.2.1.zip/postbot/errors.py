class TimerError(Exception):
	def __init__(self,value):
		self.value=value
	def __str__(self):
		return repr(self.value)

class PostError(Exception):
	def __init__(self,value):
		self.value=value
	def __str__(self):
		return repr(self.value)

class ForumError(Exception):
	def __init__(self,value):
		self.value=value
	def __str__(self):
		return repr(self.value)

class DataError(Exception):
	def __init__(self,value):
		self.value=value
	def __str__(self):
		return repr(self.value)