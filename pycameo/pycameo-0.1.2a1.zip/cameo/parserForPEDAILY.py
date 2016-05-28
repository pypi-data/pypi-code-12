# -*- coding: utf-8 -*-
"""
Copyright (C) 2015, MuChu Hsu
Contributed by Muchu Hsu (muchu1983@gmail.com)
This file is part of BSD license

<https://opensource.org/licenses/BSD-3-Clause>
"""
import os
import datetime
import re
import json
import logging
import urllib
from scrapy import Selector
from cameo.utility import Utility
from cameo.localdb import LocalDbForPEDAILY
"""
從 source_html 的 HTML 檔案解析資料
結果放置於 parsed_result 下
"""
class ParserForPEDAILY:
    #建構子
    def __init__(self):
        self.utility = Utility()
        self.db = LocalDbForPEDAILY()
        self.dicSubCommandHandler = {"index":[self.parseIndexPage],
                                     "category":[self.parseCategoryPage],
                                     "json":[self.parseNewsPageThenCreateNewsJson]}
        self.strWebsiteDomain = u"http://www.pedaily.cn"
        self.SOURCE_HTML_BASE_FOLDER_PATH = u"cameo_res\\source_html"
        self.PARSED_RESULT_BASE_FOLDER_PATH = u"cameo_res\\parsed_result"
        self.intNewsJsonNum = 0 #news.json 檔案編號
        self.intMaxNewsPerNewsJsonFile = 1000 #每個 news.json 儲存的 news 之最大數量
        self.dicParsedResultOfCategory = {} #category.json 資料
        self.dicParsedResultOfNews = [] #news.json 資料
        
    #取得 parser 使用資訊
    def getUseageMessage(self):
        return ("- PEDAILY -\n"
                "useage:\n"
                "index - parse index.html then insert tag into DB \n"
                "category - parse category.html then insert news into DB \n"
                "json - parse news.html then create json \n")
                
    #執行 parser
    def runParser(self, lstSubcommand=None):
        strSubcommand = lstSubcommand[0]
        strArg1 = None
        if len(lstSubcommand) == 2:
            strArg1 = lstSubcommand[1]
        for handler in self.dicSubCommandHandler[strSubcommand]:
            handler(strArg1)
    
    #解析 index.html
    def parseIndexPage(self, uselessArg1=None):
        strIndexResultFolderPath = self.PARSED_RESULT_BASE_FOLDER_PATH + u"\\PEDAILY"
        if not os.path.exists(strIndexResultFolderPath):
            os.mkdir(strIndexResultFolderPath) #mkdir parsed_result/PEDAILY/
        strIndexHtmlFolderPath = self.SOURCE_HTML_BASE_FOLDER_PATH + u"\\PEDAILY"
        strIndexHtmlFilePath = strIndexHtmlFolderPath + u"\\index.html"
        with open(strIndexHtmlFilePath, "r") as indexHtmlFile:
            strPageSource = indexHtmlFile.read()
            root = Selector(text=strPageSource)
            lstStrCategoryUrl = root.css("div.footer ul.main li.box-fix-d dl dt:nth-of-type(3) ul li a::attr(href)").extract()
            for strCategoryUrl in lstStrCategoryUrl:
                strCategoryName = re.match("^http://www.pedaily.cn/(.*)/$", strCategoryUrl).group(1)
                strCategoryName = urllib.quote(strCategoryName.encode("utf-8")) #url encode
                self.db.insertCategoryIfNotExists(strCategoryName=strCategoryName)
                
    #解析 category.html
    def parseCategoryPage(self, uselessArg1=None):
        strCategoryResultFolderPath = self.PARSED_RESULT_BASE_FOLDER_PATH + u"\\PEDAILY\\category"
        if not os.path.exists(strCategoryResultFolderPath):
            os.mkdir(strCategoryResultFolderPath) #mkdir parsed_result/PEDAILY/category/
        strCategoryHtmlFolderPath = self.SOURCE_HTML_BASE_FOLDER_PATH + u"\\PEDAILY\\category"
        self.dicParsedResultOfCategory = {} #清空 dicParsedResultOfCategory 資料 (暫無用處)
        #取得已下載完成的 strCategoryName list
        lstStrObtainedCategoryName = self.db.fetchallCompletedObtainedCategoryName()
        for strObtainedCategoryName in lstStrObtainedCategoryName: #category loop
            strCategoryHtmlFilePath = strCategoryHtmlFolderPath + u"\\%s_category.html"%strObtainedCategoryName
            logging.info("parse %s"%strCategoryHtmlFilePath)
            with open(strCategoryHtmlFilePath, "r") as categoryHtmlFile:
                strPageSource = categoryHtmlFile.read()
                root = Selector(text=strPageSource)
                #解析 news URL
                lstStrNewsUrl = root.css("div.news-list ul#newslist-all li h3 a::attr(href)").extract()
                for strNewsUrl in lstStrNewsUrl: #news loop
                    #儲存 news url 至 DB
                    if strNewsUrl.endswith(".shtml"):
                        self.db.insertNewsUrlIfNotExists(strNewsUrl=strNewsUrl, strCategoryName=strObtainedCategoryName)
    
    #解析 news.html 產生 news.json (pedaily.cn 將 news 儲放在不同台的 server)
    def parseNewsPageThenCreateNewsJson(self, uselessArg1=None):
        strNewsResultFolderPath = self.PARSED_RESULT_BASE_FOLDER_PATH + u"\\PEDAILY\\news"
        if not os.path.exists(strNewsResultFolderPath):
            os.mkdir(strNewsResultFolderPath) #mkdir parsed_result/PEDAILY/news/
        strNewsHtmlFolderPath = self.SOURCE_HTML_BASE_FOLDER_PATH + u"\\PEDAILY\\news"
        self.dicParsedResultOfNews = [] #清空 news.json 暫存資料
        self.intNewsJsonNum = 0 #計數器歸零
        #pedaily 網頁錯誤率較高，改用 news 資料表作為 parse 的主要 loop
        #若發現 html 檔案不存在或有錯誤，直接將 news 資料 isGot 設為 0 (未抓取)
        lstStrNewsUrl = self.db.fetchallCompletedObtainedNewsUrl()
        for strNewsUrl in lstStrNewsUrl: #url loop
            logging.info("parse %s"%strNewsUrl)
            dicNewsData = {} #新聞資料物件
            strNewsServerName = re.match("^http://([a-z]*).pedaily.cn/.*/([0-9]*).shtml$", strNewsUrl).group(1)
            strNewsName = re.match("^http://([a-z]*).pedaily.cn/.*/([0-9]*).shtml$", strNewsUrl).group(2)
            strNewsHtmlFilePath = strNewsHtmlFolderPath + u"\\%s_%s_news.html"%(strNewsName, strNewsServerName)
            if not os.path.exists(strNewsHtmlFilePath):
                logging.warning("%s news html file not exists, set news isGot=0"%strNewsUrl)
                self.db.updateNewsStatusIsNotGot(strNewsUrl=strNewsUrl)
                continue #skip it
            with open(strNewsHtmlFilePath, "r") as newsHtmlFile:
                strPageSource = newsHtmlFile.read()
                root = Selector(text=strPageSource)
            #解析 news.html
            try:
                # 檢查網頁是否有 newseed 圖片
                lstStrNewseedLogoImgSrc = root.css("a.site-logo img::attr(src)").extract()
                #newseed.pedaily.cn 格式與其他 server 不同
                if len(lstStrNewseedLogoImgSrc) == 1 and "http://pic.pedaily.cn/newseed/logo.png" in lstStrNewseedLogoImgSrc[0]:
                    #strSiteName
                    dicNewsData["strSiteName"] = u"PEDAILY"
                    #strUrl
                    dicNewsData["strUrl"] = strNewsUrl
                    #strTitle
                    strTitle = root.css("div div h1::text").extract_first()
                    dicNewsData["strTitle"] = strTitle
                    #strContent
                    lstStrContent = root.css("div.news-content *:not(script)::text").extract()
                    strContent = re.sub("\s", "", u"".join(lstStrContent)) #接合 新聞內容 並去除空白字元
                    dicNewsData["strContent"] = strContent.strip()
                    #lstStrKeyword
                    lstStrKeyword = root.css("div.news-keyword span a::text").extract()
                    dicNewsData["lstStrKeyword"] = lstStrKeyword
                    #strPublishDate
                    strOriginPublishDate = root.css("div.info div span.date::text").extract_first()
                    strPublishDate = datetime.datetime.strptime(strOriginPublishDate, "%Y-%m-%d %H:%M").strftime("%Y-%m-%d") #date format 2016-04-24
                    dicNewsData["strPublishDate"] = strPublishDate
                    #strCrawlDate
                    dicNewsData["strCrawlDate"] = self.utility.getCtimeOfFile(strFilePath=strNewsHtmlFilePath)
                else:# (news|if|pe|people).pedaily.cn 
                    #strSiteName
                    dicNewsData["strSiteName"] = u"PEDAILY"
                    #strUrl
                    dicNewsData["strUrl"] = strNewsUrl
                    #strTitle
                    strTitle = root.css("div.news-show h1:nth-of-type(1)::text").extract_first()
                    dicNewsData["strTitle"] = strTitle
                    #strContent
                    lstStrContent = root.css("div.news-content *:not(script)::text").extract()
                    strContent = re.sub("\s", "", u"".join(lstStrContent)) #接合 新聞內容 並去除空白字元
                    dicNewsData["strContent"] = strContent.strip()
                    #lstStrKeyword
                    lstStrKeyword = root.css("div.news-tag div.tag a::text").extract()
                    dicNewsData["lstStrKeyword"] = lstStrKeyword
                    #strPublishDate
                    strOriginPublishDate = root.css("div.box-l span.date::text").extract_first()
                    strPublishDate = datetime.datetime.strptime(strOriginPublishDate, "%Y-%m-%d %H:%M").strftime("%Y-%m-%d") #date format 2016-04-24
                    dicNewsData["strPublishDate"] = strPublishDate
                    #strCrawlDate
                    dicNewsData["strCrawlDate"] = self.utility.getCtimeOfFile(strFilePath=strNewsHtmlFilePath)
                #將 新聞資料物件 加入 json
                self.dicParsedResultOfNews.append(dicNewsData)
            except Exception as ex:
                logging.warning("parse %s fail, set news isGot=0"%strNewsUrl)
                logging.warning(ex)
                self.db.updateNewsStatusIsNotGot(strNewsUrl=strNewsUrl)
                continue #skip it
            #每一千筆資料另存一個 json
            if len(self.dicParsedResultOfNews) == self.intMaxNewsPerNewsJsonFile:
                self.intNewsJsonNum = self.intNewsJsonNum + self.intMaxNewsPerNewsJsonFile
                #儲存 json
                strNewsJsonFilePath = strNewsResultFolderPath + u"\\%d_news.json"%self.intNewsJsonNum
                self.utility.writeObjectToJsonFile(dicData=self.dicParsedResultOfNews, strJsonFilePath=strNewsJsonFilePath)
                logging.info("%d news saved on %s"%(self.intMaxNewsPerNewsJsonFile, strNewsJsonFilePath))
                self.dicParsedResultOfNews = [] #清空 news.json 資料
        else:#news loop 順利結束，儲存剩餘的 news 至 json
            self.intNewsJsonNum = self.intNewsJsonNum + self.intMaxNewsPerNewsJsonFile
            #儲存 json
            strNewsJsonFilePath = strNewsResultFolderPath + u"\\%d_news.json"%self.intNewsJsonNum
            self.utility.writeObjectToJsonFile(dicData=self.dicParsedResultOfNews, strJsonFilePath=strNewsJsonFilePath)
            logging.info("%d news saved on %s"%(len(self.dicParsedResultOfNews), strNewsJsonFilePath))
            self.dicParsedResultOfNews = [] #清空 news.json 資料