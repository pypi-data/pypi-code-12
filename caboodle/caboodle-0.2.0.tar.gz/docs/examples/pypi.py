#!/usr/bin/env python
from caboodle import web
import time

# Create the browser
browser = web.Browser('Firefox')
browser.get('https://pypi.python.org')

# Search for caboodle
browser.find_element_by_id('term').send_keys('caboodle')
browser.find_element_by_id('submit').click()

# Wait and quit
time.sleep(5)
browser.quit()
