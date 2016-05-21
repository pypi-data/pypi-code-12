#!/usr/bin/env python
from caboodle import web, solve
import time

# Create the browser
browser = web.Browser('Firefox')
solver = solve.captcha(browser, online = ['rucaptcha', 'YOUR API KEY'])
browser.get('https://www.google.com/recaptcha/api2/demo')

# Solve the CAPTCHA
while True:
    solver.solve()
    browser.find_element_by_tag_name('form').submit()

    try:
        browser.find_element_by_class_name('recaptcha-error-message')
    except:
        break

    solver.invalid()

# Wait and quit
time.sleep(5)
browser.quit()
