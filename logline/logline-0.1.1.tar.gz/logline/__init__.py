import urllib, urllib2, json

class LogLine(object):

	def __init__(self, key):
		""" provide me with your key for LogLine! """
		self.key = key
		self.endpoint = "http://localhost:3000/api/v1"

	def log(self, flag, message):
		data = urllib.urlencode({
			"flag": flag,
			"message": message,
			"key": self.key
		}).replace("+","%20")

		response = json.loads(urllib2.urlopen(self.endpoint + "/msg", data).read())
		return response['success']

	def info(self, message):
		return self.log("info", message)
	def success(self, message):
		return self.log("success", message)
	def warning(self, message):
		return self.log("warning", message)
	def fatal(self, message):
		return self.log("fatal", message)