import unittest

from ConcordanceCrawler.core.concordance_crawler import *
from ConcordanceCrawler.core.bazwords import IncreasingNumbers

class TestApp(unittest.TestCase):

	def test_setting_handler_fails(self):
		crawler = ConcordanceCrawler("scrape")
		# test that you cannot set handler on ignored exception
		crawler.ignore_exception(A)
		self.assertRaises(Exception, crawler.set_exception_handler, A, None)


