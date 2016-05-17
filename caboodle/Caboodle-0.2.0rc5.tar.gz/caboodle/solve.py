from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support.ui import Select
from skimage.morphology import opening, closing, erosion, dilation
from scipy.ndimage.interpolation import zoom
from skimage import io
from io import BytesIO
from PIL import Image, ImageOps
import subprocess
import warnings
import requests
import tempfile
import base64
import random
import shutil
import glob
import json
import time
import re

warnings.simplefilter('ignore', UserWarning)

class _tesseract(object):
	"""
	The tesseract class solves a CAPTCHA locally
	"""

	def __init__(self):
		self.invalid_words = ['', 'b', 'c', 'd', 'e', 'f', 'g', 'h',
			'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q',
			'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']

	def process(self, image, upper = 3, lower = 0.015):
		"""
		Processes a CAPTCHA by removing noise

		Args:
			image (str): The file path of the image to process
			upper (int): The upper bound of most used colors to remove (default = 3)
			lower (double): The lower bound of most used colors to remove (default = 0.015)

		Raises:
			IndexError if upper < 0 or lower > 1
			ValueError if the resulting threshold is below the upper limit
		"""

		if upper < 0:
			raise IndexError('Upper bound cannot be less than zero')

		if lower > 1:
			raise IndexError('Lower bound cannot be greater than 100%')

		input = io.imread(image)[:, :, :3]
		histogram = {}

		for x in range(input.shape[0]):
			for y in range(input.shape[1]):
				pixel = input[x, y]
				hex = '%02x%02x%02x' % (pixel[0], pixel[1], pixel[2])

				if hex in histogram:
					histogram[hex] += 1
				else:
					histogram[hex] = 1

		histogram = sorted(histogram, key = histogram.get, reverse=True)
		threshold = len(histogram) * lower

		if threshold < upper:
			raise ValueError('Threshold cannot be less than the upper limit')

		for x in range(input.shape[0]):
			for y in range(input.shape[1]):
				pixel = input[x, y]
				hex = '%02x%02x%02x' % (pixel[0], pixel[1], pixel[2])
				index = histogram.index(hex)

				if index < upper or index > threshold:
					input[x, y] = [0, 0, 0]
				else:
					r, g, b = input[x, y]
					q = int(r * 0.299 + g * 0.587 + b * 0.144)

					if q < 200:
						input[x, y] = [255, 255, 255]
					else:
						input[x ,y] = [0, 0, 0]

		input = erosion(closing(input))

		# Remove single pixels
		for x in range(1, input.shape[0] - 1):
			for y in range(1, input.shape[1] - 1):
				left = input[x - 1, y, 0]
				right = input[x + 1, y, 0]

				if left == 0 and right == 0:
					input[x, y] = [0, 0, 0]

		input = opening(dilation(input))[:, :, 0]
		io.imsave(image, input)

	def zoom(self, image, factor = 1.3):
		"""
		Zooms a CAPTCHA for easier OCR

		Args:
			image (str): The file path of the image to zoom
			factor (float): The factor to zoom by (default = 1.3)
		"""

		input = io.imread(image)
		input = zoom(input, factor)
		io.imsave(image, input)

	def valid_word(self, word):
		"""
		Checks if a word is valid

		Args:
			word (str): The word to check

		Returns:
			True if the word is valid
		"""

		r = requests.get('https://api.pearson.com:443/v2/dictionaries/lasde/entries', params = {'headword': word})

		if r.json()['total'] > 0:
			return True
		else:
			return False

	def solve(self, image):
		"""
		Solves a CAPTCHA locally
		"""

		temp = tempfile.NamedTemporaryFile(suffix = '.jpg')
		temp.write(base64.b64decode(image))
		image = temp.name

		shutil.copyfile(image, image + '.bak')
		for i in range(1, 1000):
			for j in range(1, 200):
				shutil.copyfile(image + '.bak', image)

				try:
					self.process(image, i, j * 0.005)
				except ValueError as e:
					continue

				result = subprocess.check_output('tesseract %s stdout '\
					'-c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyz' % (image),
					stderr=subprocess.DEVNULL,
					shell = True,
					universal_newlines = True
				).replace('\n', ' ')[:-2]

				if result:
					for k in range(11, 20):
						self.zoom(image, 1.1)
						result = subprocess.check_output('tesseract %s stdout '\
							'-c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyz' % (image),
							stderr=subprocess.DEVNULL,
							shell = True,
							universal_newlines = True
						).replace('\n', ' ')[:-2].lower()
						valid = True
						words = result.split(' ')

						if len(words) > 1 and words[0] == words[1]:
							continue

						for word in words:
							if word == 'i' or word == 'a' or word == ' ':
								continue

							char = list(word)

							if word in self.invalid_words:
								valid = False
								break
							elif (len(char) > 1 and char[0] == char[1]) or len(char) < 2:
								valid = False
								self.invalid_words.append(word)
								break
							elif not self.valid_word(word):
								valid = False
								self.invalid_words.append(word)
								break

						if valid:
							return result

	def invalid(self):
		"""
		Flags a CAPTCHA as invalid
		"""

		return

class _rucaptcha(object):
	"""
	The rucaptcha class interacts with RuCaptcha's web API

	https://rucaptcha.com/api-rucaptcha

	Args:
		key (str): Your API key
	"""

	def __init__(self, key):
		self.key = key
		self.last = None

	def post(self, image, regsense = 0, is_question = 0, is_numeric = 2,
		is_math = 0, min_length = 0, max_length = 0, language = 2):
		"""
		Posts a CAPTCHA to be solved

		Args:
			image (str): The base64 encoded CAPTCHA to be solved
			regsense (int): Register the response as important
				> 0 = False (default)
				> 1 = True
			is_question (int): Is the CAPTCHA a question
				> 0 = False (default)
				> 1 = True
			is_numeric (int): Are there only numbers in the CAPTCHA
				> 0 = Disable
				> 1 = True
				> 2 = False, only characters (default)
				> 3 = Either
			is_math (int): Does the CAPTCHA contain math to be solved
				> 0 = False (default)
				> 1 = True
			min_length (int): The minimum length of the response (0 <= X <= 20) (default = 0, disabled)
			max_length (int): The maximum length of the response (1 <= X <= 20) (default = 0, disabled)
			langauge (int): The language of the CAPTCHA
				> 0 = Disable
				> 1 = Russian
				> 2 = English (default)

		Raises:
			Exception if status code != 200 or the CAPTCHA was not accepted

		Returns:
			True if response == OK
		"""

		data = {
			'method': 'base64',
			'key': self.key,
			'body': image
		}

		r = requests.post('http://rucaptcha.com/in.php', data = data)

		if r.status_code == 200:
			if '|' in r.text:
				response, self.last = r.text.split('|', 1)
				return response == 'OK'
			else:
				raise Exception(r.text)
		else:
			raise Exception(r.text)

	def get(self, id = None):
		"""
		Gets the result of a CAPTCHA

		Args:
			id (int): The ID of the CAPTCHA to get (default = last CAPTCHA)
		"""

		if not id:
			id = self.last

		while True:
			r = requests.get('http://rucaptcha.com/res.php',
				params = {'key': self.key, 'action': 'get', 'id': self.last})

			if r.status_code == 200:
				if '|' in r.text:
					return r.text.split('|', 1)[1]
				elif r.text == 'ERROR_CAPTCHA_UNSOLVABLE':
					return ''
				else:
					time.sleep(5)

	def solve(self, image):
		"""
		Solves a CAPTCHA

		Args:
			image (str): The base64 encoded CAPTCHA to be solved
		"""

		self.post(image)
		time.sleep(5)
		return self.get()

	def invalid(self, id = None):
		"""
		Reports a CAPTCHA as invalid

		Args:
			id (int): The ID of the CAPTCHA to flag (default = last CAPTCHA)
		"""

		if not id:
			id = self.last

		while True:
			r = requests.get('http://rucaptcha.com/res.php',
				params = {'key': self.key, 'action': 'reportbad', 'id': self.last})

			if r.status_code == 200:
				break
			else:
				time.sleep(1)

class captcha(object):
	"""
	The captcha class solves CAPTCHAs with various methods such as:

		- Local
			> User input (most basic)
			> OCR
				* tesseract
		- Online
			> 2captcha
			> rucaptcha

	Args:
		browser (browser): The browser to interact with
		user (boolean): Should the user be prompted (default = False)
		online (tuple): The online provider to use (default = False)
			ex: ('rucaptcha', '123pass')
		ocr (boolean): Use optical character recognition (default = False)
	"""

	def __init__(self, browser = None, user = False, online = False, ocr = False):
		if not browser:
			raise Exception('No browser declared')

		if not user and not online and not ocr:
			raise Exception('No solving method declared')

		self.browser = browser
		self.user = user
		self.online = online
		self.ocr = ocr
		self.solver = None

		if online and online[0] == 'rucaptcha':
			self.solver = _rucaptcha(online[1])

		if ocr:
			self.solver = _tesseract()

	def _solve(self, form):
		"""
		The private function that does the solving

		Args:
			form (dict): The form elements to solve
		"""

		if self.online or self.ocr:
			if 'captcha' in form:
				temp = tempfile.NamedTemporaryFile(suffix = '.jpg')
				captcha = Image.open(BytesIO(requests.get(form['captcha'].get_attribute('src')).content))
				captcha = captcha.resize((captcha.width * 2, captcha.height * 2))
				captcha = captcha.convert('RGB')
				captcha.save(temp.name)

				result = subprocess.check_output('tesseract %s stdout '\
							'-c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyz' % (temp.name),
							stderr=subprocess.DEVNULL,
							shell = True,
							universal_newlines = True
						).replace('\n', ' ')[:-2].lower()
				result = result.split()[2:]

				return form['box'].send_keys(' '.join(result))

			if 'iframe' in form:
				temp = tempfile.NamedTemporaryFile(suffix = '.jpg')
				img = BytesIO(base64.b64decode(form['image'].value_of_css_property('background-image')[27:-2]))
				Image.open(img).save(temp.name)

				result = subprocess.check_output('tesseract %s stdout '\
							'-c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyz' % (temp.name),
							stderr=subprocess.DEVNULL,
							shell = True,
							universal_newlines = True
						).replace('\n', ' ')[:-2].lower()
				result = result.split()[2:]

				self.browser.switch_to_default_content()
				return form['box'].send_keys(' '.join(result))

			x, y, w, h = form['image'].location['x'], form['image'].location['y'], form['image'].size['width'], form['image'].size['height']
			screen = BytesIO(base64.b64decode(self.browser.get_screenshot_as_base64()))
			captcha = BytesIO()

			Image.open(screen).crop((x, y + 18, x + w, y + h)).save(captcha, format = 'JPEG')

			self.browser.switch_to_default_content()
			return form['box'].send_keys(self.solver.solve(base64.b64encode(captcha.getvalue())))

		if self.user:
			return form['box'].send_keys(input('Please solve the CAPTCHA: '))

	def solve(self):
		"""
		Solves the CAPTCHA on the page and returns the text

		Raises:
			Exception if unrecognized CAPTCHA provider
		"""

		# Solve Media Reveal
		try:
			form = {}
			form['iframe'] = self.browser.find_element_by_xpath('//iframe[starts-with(@id, "adcopy-unique-")]')
			self.browser.switch_to_frame(form['iframe'])
			form['reveal'] = self.browser.find_element_by_id('playBtn')
			form['reveal'].click()

			form['image'] = self.browser.find_element_by_id('overlay')
			while form['image'].size['width'] == 0:
				time.sleep(2)

			self.browser.switch_to_default_content()
			form['box'] = self.browser.find_element_by_id('adcopy-expanded-response')
			self.browser.switch_to_frame(form['iframe'])

			self._solve(form)
			self.browser.find_element_by_id('adcopy-page-return').click()
			return
		except StaleElementReferenceException:
			return self.solve()
		except:
			pass

		# Solve Media Video
		try:
			form = {}
			container = self.browser.find_element_by_id('adcopy-puzzle-image')
			container.find_element_by_tag_name('video')
			container.click()

			while True:
				time.sleep(2)

				try:
					form['captcha'] = self.browser.find_element_by_id('adcopy-ti-overlay')
					break
				except:
					pass

			form['box'] = self.browser.find_element_by_id('adcopy_response')
			form['reload'] = self.browser.find_element_by_id('adcopy-link-refresh')

			return self._solve(form)
		except StaleElementReferenceException:
			return self.solve()
		except:
			pass

		# Solve Media Text
		try:
			form = {}
			form['image'] = self.browser.find_element_by_id('adcopy-puzzle-image-image')
			form['box'] = self.browser.find_element_by_id('adcopy_response')
			form['elements'] = form['box'].find_elements_by_css_selector('*')
			form['reload'] = self.browser.find_element_by_id('adcopy-link-refresh')

			if len(form['elements']) > 0:
				return Select(form['elements']).select_by_visible_text('No')
			else:
				return self._solve(form)
		except StaleElementReferenceException:
			return self.solve()
		except AttributeError:
			form['reload'].click()
			return self.solve()
		except:
			pass

		# reCAPTCHA
		# Give me a job Google
		try:
			widget = self.browser.find_element_by_xpath('//iframe[@title="recaptcha widget"]')
			self.browser.switch_to_frame(widget)

			check = self.browser.find_element_by_id('recaptcha-anchor')
			check.click()

			time.sleep(1)

			while check.get_attribute('aria-checked') == 'false':
				self.browser.switch_to_default_content()

				# Find challenge and switch to it
				challenge = self.browser.find_element_by_xpath('//iframe[@title="recaptcha challenge"]')
				self.browser.switch_to_frame(challenge)

				# Start audio challenge
				try:
					self.browser.find_element_by_id('recaptcha-audio-button').click()
				except:
					pass

				time.sleep(1)

				# Download audio, process it and get response
				audio = requests.get(self.browser.find_element_by_class_name('rc-audiochallenge-download-link').get_attribute('href'))
				sox = shutil.which('sox') or glob.glob('C:\Program Files*\sox*\sox.exe')[0]
				p = subprocess.Popen(sox + ' -t mp3 - -t flac - silence -l 1 0.2 0.1% -1 0.2 0.1% norm -5 rate 16k', stdin = subprocess.PIPE, stdout = subprocess.PIPE, shell = True)
				stdout, stderr = p.communicate(audio.content)
				url = 'http://www.google.com/speech-api/v2/recognize?client=chromium&lang=en-US&key=AIzaSyBOti4mM-6x9WDnZIjIeyEU21OpBXqWBgw'
				headers = {'Content-Type': 'audio/x-flac; rate=16000'}
				response = requests.post(url, data = stdout, headers = headers).text

				# Get result
				result = None
				for line in response.split('\n'):
					try:
						result = json.loads(line)['result'][0]['alternative'][0]['transcript']
						break
					except:
						pass

				# Reload if no result or letters in result
				# Letters would indicate imperfect recognition
				if not result or re.search('[a-zA-Z]', result):
					self.browser.find_element_by_id('recaptcha-reload-button').click()
					time.sleep(1)
					self.browser.switch_to_default_content()
					self.browser.switch_to_frame(widget)
					continue
				else:
					result = re.sub('[^0-9]','', result)

				# Solve CAPTCHA
				time.sleep(len(result) * 2)
				self.browser.find_element_by_id('audio-response').send_keys(result)
				self.browser.find_element_by_id('recaptcha-verify-button').click()
				self.browser.switch_to_default_content()
				self.browser.switch_to_frame(widget)
				time.sleep(1)

			self.browser.switch_to_default_content()
			return
		except:
			pass

		raise Exception('Unrecognized CAPTCHA provider')

	def invalid(self):
		"""
		Flags the last CAPTCHA as invalid
		"""

		self.solver.invalid()
