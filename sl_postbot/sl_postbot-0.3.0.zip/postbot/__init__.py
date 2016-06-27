from selenium import webdriver
from Queue import Queue
from time import sleep
from errors import *

# base class for bots
class Bot(webdriver.Firefox):
	# initialization
	def __init__(self,username,password,away=604800):
		super().__init__()
		# default values
		self.posts=Queue()
		self.away=604800
		self.waitTime=0

		self.username=username
		self.password=password

		# set self.away to user spec, if included
		if away!=604800:
			# check if int
			if type(away) is int:
				# check for time length
				if away<604800:
					raise TimerError('Timer must be at least 604800 (one week)')
					exit()
				else:
					# reset variable
					self.away=away
			else:
				# raise error if it's not int
				raise TypeError('parameter "away" is not int')

	# add post to queue
	def newPost(self,post):
		# check if post is dict
		if not type(post) is dict:
			raise TypeError('supplied post is not a dict')

		# check that parameters are present
		for p in ['title','forum','body']:
			if not p in post:
				raise DataError('parameter %s is required'%p)

		self.posts.put(post)							# add to queue
		self.waitTime=int(self.away/self.posts.qsize())	# update waitTime

	# begin the process
	def begin(self):
		# while the post queue isn't empty...
		while not self.posts.empty():
			# pause the program for half the time specified in waitTime
			sleep(int(self.waitTime/2))

			# log in
			self.get('https://sinister.ly/index.php')
			sleep(7)
			self.find_element_by_xpath('/html/body/div[1]/div/a[1]').click()

			self.find_element_by_id('quick_login_username').send_keys(self.username)
			self.find_element_by_id('quick_login_password').send_keys(self.password)
			self.find_element_by_xpath('//*[@id="login_modal"]/form/input[6]').click()
			
			# get the next post
			post=self.posts.get()

			# go to new thread page
			self.get('https://sinister.ly/Forum-'+post['forum'].replace(' ','-'))
			self.find_element_by_xpath('//*[@id="content"]/div[2]/a').click()

			# set prefix (if available)
			if 'prefix' in post:
				pfMenu=self.find_element_by_xpath('//*[@id="content"]/form/table[1]/tbody/tr[3]/td[2]/select')
				for i in pfMenu.find_elements_by_css_selector('*'):
					if i.get_attribute('innerHTML')==post['prefix']:
						i.click()
						break

			# set title
			self.find_element_by_xpath('//*[@id="content"]/form/table[1]/tbody/tr[3]/td[2]/input').send_keys(post['title'])

			# set body
			body=self.find_element_by_xpath('//*[@id="content"]/form/table[1]/tbody/tr[5]/td[2]/div/textarea')
			body.send_keys(post['body']+'\n\n[align=right][size=xx-small]Generated using SL PostBot\nhttps://github.com/LiaSL/SLPostBot\n(C) Shinoa[/size][/align]')

			# click post button
			self.find_element_by_xpath('//*[@id="content"]/form/div/input[1]').click()

			# tear down the browser
			self.stop()

			# pause for the other half
			sleep(int(self.waitTime/2))