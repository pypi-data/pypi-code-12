# -*- coding: utf-8 -*-
"""
Copyright (C) 2015, MuChu Hsu
Contributed by Muchu Hsu (muchu1983@gmail.com)
This file is part of BSD license

<https://opensource.org/licenses/BSD-3-Clause>
"""
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import os
import time
import logging
import re
import random
from cameo.utility import Utility
"""
抓取 貝果 html 存放到 source_html 
"""
class SpiderForWEBACKERS:
    
    #建構子
    def __init__(self):
        self.SOURCE_HTML_BASE_FOLDER_PATH = u"cameo_res\\source_html"
        self.PARSED_RESULT_BASE_FOLDER_PATH = u"cameo_res\\parsed_result"
        self.dicSubCommandHandler = {"browse":self.downloadBrowsePageAndParseBrowsePage,
                                     "category":self.downloadCategoryPage,
                                     "project":self.downloadProjectPage,
                                     "profile":self.downloadProfilePage,
                                     "automode":self.downloadProjectAndProfilePageAutoMode}
        self.lstStrCategoryName = ["acg", "art", "charity", "design", "music",
                                   "publication", "sport", "surprise", "technology", "video"]
        self.CATEGORY_URL_LIST_FILENAME = u"category_url_list.txt"
        self.PROJ_URL_LIST_FILENAME = u"_proj_url_list.txt"
        self.utility = Utility()
        self.driver = None
        
    #取得 spider 使用資訊
    def getUseageMessage(self):
        return ("- WEBACKERS -\n"
                "useage:\n"
                "browse - download browse.html with parse it\n"
                "category - download #_category.html (# is page number.)\n"
                "project category - download project pages of given category\n"
                "profile category - download profile pages of given category\n"
                "automode - download project and profile pages of all categories\n")
    
    #取得 selenium driver 物件
    def getDriver(self):
        chromeDriverExeFilePath = ".\cameo_res\chromedriver.exe"
        driver = webdriver.Chrome(chromeDriverExeFilePath)
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
    def runSpider(self, lstSubcommand=None):
        strSubcommand = lstSubcommand[0]
        strArg1 = None
        if len(lstSubcommand) == 2:
            strArg1 = lstSubcommand[1]
        self.initDriver() #init selenium driver
        self.dicSubCommandHandler[strSubcommand](strArg1)
        self.quitDriver() #quit selenium driver
        
    #下載 Browse 頁面 並解析
    def downloadBrowsePageAndParseBrowsePage(self, uselessArg1=None):
        logging.info("download browse page, and parse it.")
        strBrowseHtmlFolderPath = self.SOURCE_HTML_BASE_FOLDER_PATH + u"\\WEBACKERS"
        if not os.path.exists(strBrowseHtmlFolderPath):
            os.mkdir(strBrowseHtmlFolderPath) #mkdir source_html/WEBACKERS/
        #貝果首頁
        self.driver.get("https://www.webackers.com/")
        #瀏覽提案
        strBrowseUrl = self.driver.find_element_by_css_selector("ul.nav li.font_m1 a[href*='/Proposal/Browse']").get_attribute("href")
        self.driver.get(strBrowseUrl)
        #所有案件
        strAllStatusUrl = self.driver.find_element_by_css_selector("aside.col-md-2 article:nth-of-type(1) a[href*='fundedStatus=ALL']").get_attribute("href")
        self.driver.get(strAllStatusUrl)
        #儲存 browse.html
        strBrowseHtmlFilePath = strBrowseHtmlFolderPath + u"\\browse.html"
        self.utility.overwriteSaveAs(strFilePath=strBrowseHtmlFilePath, unicodeData=self.driver.page_source)
        #解析 category url
        strBrowseResultFolderPath = self.PARSED_RESULT_BASE_FOLDER_PATH + u"\\WEBACKERS"
        if not os.path.exists(strBrowseResultFolderPath):
            os.mkdir(strBrowseResultFolderPath) #mkdir parsed_result/WEBACKERS/
        strCategoryUrlListFilePath = strBrowseResultFolderPath + u"\\category_url_list.txt"
        elesCategoryUrl = self.driver.find_elements_by_css_selector("aside.col-md-2 article:nth-of-type(2) a")
        with open(strCategoryUrlListFilePath, "w+") as categoryUrlListFile:
            for eleCategoryUrl in elesCategoryUrl:
                categoryUrlListFile.write(eleCategoryUrl.get_attribute("href") + u"\n")
            
    #下載類別頁面
    def downloadCategoryPage(self, uselessArg1=None):
        logging.info("download category page")
        strCategoryUrlListFilePath = self.PARSED_RESULT_BASE_FOLDER_PATH + "\\WEBACKERS\\category_url_list.txt"
        with open(strCategoryUrlListFilePath, "r") as categoryUrlListFile:
            for strCategoryUrl in categoryUrlListFile:
                if "category=ALL" in strCategoryUrl:
                    continue #略過所有類別
                strCategoryName = re.match("^https://www.webackers.com/Proposal/Browse?.*category=([A-Z]*)$", strCategoryUrl).group(1).lower()
                strCategoryHtmlFolderPath = self.SOURCE_HTML_BASE_FOLDER_PATH + u"\\WEBACKERS\\%s"%strCategoryName
                if not os.path.exists(strCategoryHtmlFolderPath):
                    os.mkdir(strCategoryHtmlFolderPath) #mkdir source_html/WEBACKERS/category/
                intPageNum = 0
                strCategoryHtmlFilePath = strCategoryHtmlFolderPath + "\\%d_category.html"%intPageNum
                #第0頁
                self.driver.get(strCategoryUrl)
                self.utility.overwriteSaveAs(strFilePath=strCategoryHtmlFilePath, unicodeData=self.driver.page_source)
                #下一頁
                elesNextPageA = self.driver.find_elements_by_css_selector("ul.pagination li:last-of-type a")
                while len(elesNextPageA) != 0:
                    time.sleep(random.randint(2,5))
                    intPageNum = intPageNum+1
                    strNextPageUrl = elesNextPageA[0].get_attribute("href")
                    strCategoryHtmlFilePath = strCategoryHtmlFolderPath + "\\%d_category.html"%intPageNum
                    self.driver.get(strNextPageUrl)
                    self.utility.overwriteSaveAs(strFilePath=strCategoryHtmlFilePath, unicodeData=self.driver.page_source)
                    #再下一頁
                    elesNextPageA = self.driver.find_elements_by_css_selector("ul.pagination li:last-of-type a")
           
    #點擊 more button
    def clickMoreBtn(self):
        try:
            eleBtnMore = self.driver.find_element_by_css_selector("#more")
            strBtnMoreStyle = eleBtnMore.get_attribute("style")
            while u"none" not in strBtnMoreStyle:
                eleBtnMore.click()
                time.sleep(random.randint(3,7))
                eleBtnMore = self.driver.find_element_by_css_selector("#more")
                strBtnMoreStyle = eleBtnMore.get_attribute("style")
        except NoSuchElementException:
            logging.info("selenium driver can't find the more button.")
            return
            
    #全自動下載 所有類別 的 案件頁面 及 個人資料頁面
    def downloadProjectAndProfilePageAutoMode(self, uselessArg1=None):
        for strCategoryName in self.lstStrCategoryName:
            self.downloadProjectPage(strCategoryName=strCategoryName)
            self.downloadProfilePage(strCategoryName=strCategoryName)
            
    #下載案件頁面
    def downloadProjectPage(self, strCategoryName=None):
        logging.info("download project page.(%s)"%strCategoryName)
        strProjectsHtmlFolderPath = self.SOURCE_HTML_BASE_FOLDER_PATH + u"\\WEBACKERS\\%s\\projects"%strCategoryName
        if not os.path.exists(strProjectsHtmlFolderPath):
            os.mkdir(strProjectsHtmlFolderPath) #mkdir source_html/WEBACKERS/category/projects/
        #讀取 category.json
        strCategoryJsonFilePath = self.PARSED_RESULT_BASE_FOLDER_PATH + (u"\\WEBACKERS\\%s\\category.json"%strCategoryName)
        dicCategoryData = self.utility.readObjectFromJsonFile(strJsonFilePath=strCategoryJsonFilePath)
        for dicProjectData in dicCategoryData["project_url_list"]:
            strProjectIntroUrl = dicProjectData["strUrl"]
            strProjId = re.match("^https://www.webackers.com/Proposal/Display/([0-9]*)$", strProjectIntroUrl).group(1)
            #專案介紹 TAB
            strProjectIntroHtmlFileName = strProjId + u"_intro.html"
            strProjectIntroHtmlFilePath = strProjectsHtmlFolderPath + (u"\\%s"%strProjectIntroHtmlFileName)
            time.sleep(random.randint(2,5))
            self.driver.get(strProjectIntroUrl.strip())
            self.utility.overwriteSaveAs(strFilePath=strProjectIntroHtmlFilePath, unicodeData=self.driver.page_source)
            #進度報告 TAB
            strProjectProgressHtmlFileName = strProjId + u"_progress.html"
            strProjectProgressHtmlFilePath = strProjectsHtmlFolderPath + (u"\\%s"%strProjectProgressHtmlFileName)
            time.sleep(random.randint(2,5))
            strProjectProgressUrl = self.driver.find_element_by_css_selector("ul.nav-tabs li a[href*='tab=progress']").get_attribute("href")
            self.driver.get(strProjectProgressUrl.strip())
            self.utility.overwriteSaveAs(strFilePath=strProjectProgressHtmlFilePath, unicodeData=self.driver.page_source)
            #獲得贊助 TAB (點開 more)
            strProjectSponsorHtmlFileName = strProjId + u"_sponsor.html"
            strProjectSponsorHtmlFilePath = strProjectsHtmlFolderPath + (u"\\%s"%strProjectSponsorHtmlFileName)
            time.sleep(random.randint(2,5))
            strProjectSponsorUrl = self.driver.find_element_by_css_selector("ul.nav-tabs li a[href*='tab=sponsor']").get_attribute("href")
            self.driver.get(strProjectSponsorUrl.strip())
            self.clickMoreBtn() #點開 more
            self.utility.overwriteSaveAs(strFilePath=strProjectSponsorHtmlFilePath, unicodeData=self.driver.page_source)
            #問與答 TAB (點開 more)
            strProjectFaqHtmlFileName = strProjId + u"_faq.html"
            strProjectFaqHtmlFilePath = strProjectsHtmlFolderPath + (u"\\%s"%strProjectFaqHtmlFileName)
            time.sleep(random.randint(2,5))
            strProjectFaqUrl = self.driver.find_element_by_css_selector("ul.nav-tabs li a[href*='tab=faq']").get_attribute("href")
            self.driver.get(strProjectFaqUrl.strip())
            self.clickMoreBtn() #點開 more
            self.utility.overwriteSaveAs(strFilePath=strProjectFaqHtmlFilePath, unicodeData=self.driver.page_source)
                
    #下載個人資料頁面
    def downloadProfilePage(self, strCategoryName=None):
        logging.info("download profile page.(%s)"%strCategoryName)
        strProfilesHtmlFolderPath = self.SOURCE_HTML_BASE_FOLDER_PATH + u"\\WEBACKERS\\%s\\profiles"%strCategoryName
        if not os.path.exists(strProfilesHtmlFolderPath):
            os.mkdir(strProfilesHtmlFolderPath) #mkdir source_html/WEBACKERS/category/profiles/
        #讀取 category.json
        strCategoryJsonFilePath = self.PARSED_RESULT_BASE_FOLDER_PATH + (u"\\WEBACKERS\\%s\\category.json"%strCategoryName)
        dicCategoryData = self.utility.readObjectFromJsonFile(strJsonFilePath=strCategoryJsonFilePath)
        for strProfileProjectUrl in dicCategoryData["profile_url_list"]:
            strProfileId = re.match("^.*proposalId=([0-9]*)$", strProfileProjectUrl).group(1)
            #啟動專案 TAB
            strProfileProjHtmlFileName = strProfileId + u"_proj.html"
            strProfileProjHtmlFilePath = strProfilesHtmlFolderPath + (u"\\%s"%strProfileProjHtmlFileName)
            time.sleep(random.randint(2,5))
            self.driver.get(strProfileProjectUrl.strip())
            self.utility.overwriteSaveAs(strFilePath=strProfileProjHtmlFilePath, unicodeData=self.driver.page_source)
            #贊助過的專案 TAB
            strProfileOrderHtmlFileName = strProfileId + u"_order.html"
            strProfileOrderHtmlFilePath = strProfilesHtmlFolderPath + (u"\\%s"%strProfileOrderHtmlFileName)
            time.sleep(random.randint(2,5))
            strProfileOrderUrl = self.driver.find_element_by_css_selector("ul.nav-tabs li a[href*='tab=order']").get_attribute("href")
            self.driver.get(strProfileOrderUrl)
            self.utility.overwriteSaveAs(strFilePath=strProfileOrderHtmlFilePath, unicodeData=self.driver.page_source)
            #喜歡的專案 TAB
            strProfileSubHtmlFileName = strProfileId + u"_sub.html"
            strProfileSubHtmlFilePath = strProfilesHtmlFolderPath + (u"\\%s"%strProfileSubHtmlFileName)
            time.sleep(random.randint(2,5))
            strProfileSubUrl = self.driver.find_element_by_css_selector("ul.nav-tabs li a[href*='tab=subscribe']").get_attribute("href")
            self.driver.get(strProfileSubUrl)
            self.utility.overwriteSaveAs(strFilePath=strProfileSubHtmlFilePath, unicodeData=self.driver.page_source)
                