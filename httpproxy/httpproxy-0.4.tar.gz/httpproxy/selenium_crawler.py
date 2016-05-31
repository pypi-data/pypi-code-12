# -*- coding: utf-8 -*-
# Created by lvjiyong on 16/5/31

"""
须先安装selenium
"""
from configreset import logger


def get(url):

    try:

        from selenium import webdriver
        from selenium.common.exceptions import NoSuchElementException

        # browser = webdriver.Firefox() # Get local session of firefox
        browser = webdriver.Remote("http://localhost:4444/wd/hub",
                                desired_capabilities=webdriver.DesiredCapabilities.HTMLUNIT)
        browser.get(url)
        print(help(browser))

        browser.close()


    except Exception as e:
        logger.error(e)



get('http://proxy.goubanjia.com/free/index.shtml')