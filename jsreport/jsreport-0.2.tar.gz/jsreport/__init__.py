#!/usr/bin/env python
"""
Helper script to pull data from https://www.justserve.org.
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.select import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException



def get_project_count(zipcode, radius="5", driver="firefox"):
    """
    Returns the number of projects on JustServe.org at the given zipcode,
    within the given radius.
    """
    num_projects = "0"
    if driver=='chrome':
        driver = webdriver.Chrome()
    elif driver=='phantomjs':
        driver = webdriver.PhantomJS()
    else:
        driver = webdriver.Firefox()

    try:
        # Load the page
        driver.get('https://www.justserve.org')
        # search by zipcode
        zip_box = driver.find_element_by_css_selector("input.form__search__input")
        zip_box.send_keys(zipcode)
        # expose the advanced search
        adv_search = driver.find_element_by_css_selector("a.js-toggle-form-filters")
        adv_search.click()
        # wait for the search radius to be visible. To humans, this looks 
        # instantaneous. To the browser it is slow enough to cause problems.
        wait_element = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, "select.js-miles")
            )
        )
        # select the proper search radius
        radius_element = driver.find_element_by_css_selector("select.js-miles")
        radius_select = Select(radius_element)
        radius_select.select_by_value(radius)
        # click Search
        # We have the find the visible button, as there are a few versions
        # on the page, depending on whether 'advanced search' is enabled
        search_btns = driver.find_elements_by_css_selector("input.js-loadable")
        for btn in search_btns:
            if btn.is_displayed():
                btn.click()
                break
        # wait up to 10 seconds for the results
        # the ul appears to hold the search results, 
        # that is how we know the search is complete.
        wait_element = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, "ul.js-flagstones")
            )
        )
        # Get the project count
        # Note, the html has several <small> tags with almost every option
        # of result (i.e. none found, etc). We want the one that is visible.
        smalls = driver.find_elements_by_css_selector("small.project-count")
        for e in smalls:
            if e.is_displayed():
                try:
                    num_element = e.find_element_by_css_selector("span.project-count__num.ng-binding")
                    num_projects = num_element.text
                    break
                except NoSuchElementException:
                    # this is one of the cases where there are no search results
                    num_projects = 0
    finally:
        driver.quit()
    return str(num_projects)




if __name__=='__main__':
    # Main entry point, when run as a script
    from datetime import datetime
    import argparse
    # Collect the command-line arguments
    parser = argparse.ArgumentParser(
            description="Retrieve the number of JustServe projects at a zipcode.")
    parser.add_argument("zipcode", 
            help="The five digit zipcode at the center of the search radius.")
    parser.add_argument("-r", "--radius", default="5",
            choices=["5", "10", "15", "25", "50", "75"],
            help="The search radius, in miles. Defaults to 5.")
    parser.add_argument("-d", "--driver", default="firefox",
            choices=["firefox", "chrome", "phantomjs"],
            help="The WebDriver to use. Defaults to firefox.")
    parser.add_argument("-o", "--output", default="human",
            choices=["human", "csv", "json"],
            help="The output format. Defaults to human-readable.")
    args = parser.parse_args()
    # Go get the project count
    project_count = get_project_count(args.zipcode, args.radius, args.driver)
    # get today's date
    now = datetime.now().strftime('%Y-%m-%d')
    # Handle the output
    if args.output=='csv':
        print "%s,%s,%s,%s" % (now, args.zipcode, args.radius, project_count)
    elif args.output=='json':
        import json
        o = {'date': now, 'zipcode': args.zipcode, 'radius': args.radius,
                'project_count': project_count}
        print json.dumps(o)
    else:
        print "%s projects within a %s mile radius of %s" % (project_count, 
                args.radius, args.zipcode)
