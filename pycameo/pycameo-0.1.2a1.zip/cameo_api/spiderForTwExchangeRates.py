# -*- coding: utf-8 -*-
"""
Copyright (C) 2015, MuChu Hsu
Contributed by Muchu Hsu (muchu1983@gmail.com)
This file is part of BSD license

<https://opensource.org/licenses/BSD-3-Clause>
"""
from selenium import webdriver
import os
import logging
import time
import datetime
import re
import random
import pkg_resources
from cameo.externaldb import ExternalDbForCurrencyApi
#from cameo.localdb import LocalDbForCurrencyApi #測試用本地端 db

"""
抓取 http://tw.exchange-rates.org/ 即時匯率
"""
class SpiderForTwExchangeRates:
    
    #建構子
    def __init__(self):
        self.driver = None
        self.db = ExternalDbForCurrencyApi().mongodb
        #self.db = LocalDbForCurrencyApi().mongodb #測試用本地端 db
        
    #取得 selenium driver 物件
    def getDriver(self):
        chromeDriverExeFilePath = pkg_resources.resource_filename("cameo_res", "chromedriver.exe")
        driver = webdriver.Chrome(chromeDriverExeFilePath)
        #phantomjsDriverExeFilePath = pkg_resources.resource_filename("cameo_res", "phantomjs.exe")
        #driver = webdriver.PhantomJS(phantomjsDriverExeFilePath)
        return driver
        
    #初始化 selenium driver 物件
    def initDriver(self):
        if self.driver is None:
            self.driver = self.getDriver()
        
    #終止 selenium driver 物件
    def quitDriver(self):
        self.driver.quit()
        self.driver = None
        
    #執行 spider
    def runSpider(self):
        self.initDriver() #init selenium driver
        self.updateExRateData()
        self.quitDriver() #quit selenium driver
        
    #更新 匯率 資料
    def updateExRateData(self):
        self.driver.get("http://tw.exchange-rates.org/")
        #北美和南美、亞太地區、歐洲、中東和中亞、非洲
        elesAreaLink = self.driver.find_elements_by_css_selector("div#currencies-region div a.link")
        intCurrentAreaLink = 0
        while len(elesAreaLink) == 5:
            time.sleep(random.randint(20,30))
            strAreaLink = elesAreaLink[intCurrentAreaLink].get_attribute("href")
            self.driver.get(strAreaLink)
            logging.info("search ex-rate on %s"%strAreaLink)
            time.sleep(random.randint(20,30))
            #解析 匯率資料
            elesExRateTr = self.driver.find_elements_by_css_selector("table.table-exchangeX.large-only tbody tr")
            for eleExRateTr in elesExRateTr:
                strExRateHref = eleExRateTr.find_element_by_css_selector("td.text-nowrapX a:nth-of-type(1)").get_attribute("href")
                strCurrencyName = re.match("http://tw.exchange-rates.org/currentRates/./(...)", strExRateHref).group(1)
                strXXXToUSD = eleExRateTr.find_element_by_css_selector("td:nth-of-type(5)").text
                fUSDToXXX = 1.0/float(strXXXToUSD.strip())
                logging.info("find ex-rate: 1 USD to %s is %f"%(strCurrencyName, fUSDToXXX))
                # update DB
                logging.info("start update ex-rate data...")
                strTimeNow = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.db.ModelExRate.update_one({"strCurrencyName":"USD"+strCurrencyName},
                                   {"$set": {"strDate":strTimeNow,
                                          "strCurrencyName":"USD"+strCurrencyName,
                                          "fUSDollar":fUSDToXXX
                                          }
                                   }, 
                                   upsert=True) #upsert = update or insert if data not exists (有則更新，無則新增)
                logging.info("ex-rate data updated. [%s]"%strTimeNow)
            #準備切換至下一個 area tab
            elesAreaLink = self.driver.find_elements_by_css_selector("div#currencies-region div a.link")
            intCurrentAreaLink = (intCurrentAreaLink+1)%5