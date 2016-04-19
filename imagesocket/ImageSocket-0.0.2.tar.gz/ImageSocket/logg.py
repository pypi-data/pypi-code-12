needShowLog = False				# log control flag
SHOW = 1						# constant to show log
HIDE = 0						# constant to hide log

"""
	------	Python Plugin ( ImageSocket)	------
	This plugin is written by SunnerLi in 2016 - 04
	This class define the log about this plugin
	The project is follow MIT License
"""

def showLog(status):
	"""
		Control the flag to show the log
	"""
	needShowLog = SHOW

def hideLog(status):
	"""
		Control the flag to hide the log
	"""
	needShowLog = HIDE

def LOG(string):
	if needShowLog:
		print "--< ImageSocket >--   :", string

def LOGI(string, intt):
	if needShowLog:
		print "--< ImageSocket >--   :", string, intt
