import ConfigParser
from os import path
from os.path import expanduser

class Configurations:
	def __init__(self):
		print "Configurations initialised"
		self.config = ConfigParser.RawConfigParser()
		


	def readConfigurations(self):
		home = expanduser('~')
		with open(home+"/settings.cfg", 'a'):
			self.config.read(path.join(home,"settings.cfg"))
		#print "--------------------------"
		print (path.join(home,"settings.cfg"))
		preferences = {}

		if not self.config.has_section("preferences_user"):
			self.writeConfigurations()

		preferences['live_matches'] = self.config.getboolean("preferences_user",'live_matches')
		preferences['all_matches'] = self.config.getboolean("preferences_user","all_matches")
		preferences['hide_leauges'] = self.config.getboolean("preferences_user","hide_leauges")


		return preferences

	def writeConfigurations(self,preferences = None):

		home = expanduser('~')
		self.config.read(path.join(home,"settings.cfg"))

		if not self.config.has_section("preferences_user"):

			self.config.add_section("preferences_user")
			self.config.set("preferences_user",'live_matches','false')
			self.config.set('preferences_user','all_matches','true')
			self.config.set('preferences_user','hide_leauges','false')

		else:
			self.config.set("preferences_user",'live_matches',preferences['live_matches'])
			self.config.set('preferences_user','all_matches',preferences['all_matches'])
			self.config.set('preferences_user','hide_leauges',preferences['hide_leauges'])


		with open(path.join(home,"settings.cfg"),'wb+') as configfile:
			self.config.write(configfile)
