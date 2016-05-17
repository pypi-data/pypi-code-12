from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.proxy import *
from selenium.webdriver.common.action_chains import ActionChains

class Browser(object):
	"""
	The browser class is the core of the web module and is what creates
	the window to interact with.

	Args:
		type (str): The type of browser
		proxy (str): The proxy to use (ex: 127.0.0.1:3128)
	"""

	def __init__(self, type, proxy = None):
		if proxy:
			proxy = Proxy({
				'proxyType': ProxyType.MANUAL,
				'httpProxy': proxy,
				'ftpProxy': proxy,
				'sslProxy': proxy
			})

			self.driver = getattr(webdriver, type)(proxy = proxy)
		else:
			self.driver = getattr(webdriver, type)()

	def __getattr__(self, attr):
		return self.driver.__getattribute__(attr)

	def get(self, url):
		"""
		Performs a get request
		"""

		try:
			self.driver.get(url)
		except TimeoutException:
			self.driver.execute_script('window.stop()')

	def action(self):
		"""
		Creates an action chain to string together interactions

		Returns:
			An ActionChains object
		"""

		return ActionChains(self.driver)
