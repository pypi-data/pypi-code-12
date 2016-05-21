#!/usr/bin/env python
from caboodle import web, solve
import time

# Create the browser and solver
browser = web.Browser('Firefox')
solver = solve.captcha(browser, user = True)
browser.get('http://solvemedia.com/advertisers/captcha-type-in')

# Solve the CAPTCHA
while True:
    solver.solve()
    browser.find_element_by_id('verify_engaging').click()

    try:
        browser.find_element_by_id('engaging-incorrect')
    except:
        break

    solver.invalid()

# Wait and quit
time.sleep(5)
browser.quit()
