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
from scrapy import Selector
from cameo.utility import Utility
from cameo.mod.yuwei.utility.scrapyUtility import scrapyUtility
"""
從 source_html 的 HTML 檔案解析資料
結果放置於 parsed_result 下
"""
class ParserForWEBACKERS:
    #建構子
    def __init__(self):
        self.utility = Utility()
        self.dicSubCommandHandler = {"category":[self.parseCategoryPage],
                            "project":[self.beforeParseProjectPage,
                                   self.parseIntroPage,
                                   self.parseSponsorPage,
                                   self.parseProgressPage,
                                   self.parseFaqPage,
                                   self.afterParseProjectPage],
                            "profile":[self.beforeParseProfilePage,
                                   self.parseProjPage,
                                   self.parseOrderPage,
                                   self.afterParseProfilePage],
                            "automode":[self.parseProjectAndProfilePageAutoMode]}
        self.strWebsiteDomain = u"https://www.webackers.com"
        self.lstStrCategoryName = ["acg", "art", "charity", "design", "music",
                        "publication", "sport", "surprise", "technology", "video"]
        self.SOURCE_HTML_BASE_FOLDER_PATH = u"cameo_res\\source_html"
        self.PARSED_RESULT_BASE_FOLDER_PATH = u"cameo_res\\parsed_result"
        self.dicParsedResultOfCategory = {} #category.json 資料
        self.dicParsedResultOfProject = {} #project.json 資料
        self.dicParsedResultOfUpdate = {} #update.json 資料
        self.dicParsedResultOfQanda = {} #qanda.json 資料
        self.dicParsedResultOfReward = {} #reward.json 資料
        self.dicParsedResultOfProfile = {} #profile.json 資料
        
    #取得 parser 使用資訊
    def getUseageMessage(self):
        return ("- WEBACKERS -\n"
                "useage:\n"
                "category - parse #_category.html then create project_url_list.txt\n"
                "project category - parse project's html of given category, then create .json\n"
                "profile category - parse profile's html of given category, then create .json\n"
                "automode - parse project's and profile's html of all categories, then create .json\n")

    #執行 parser
    def runParser(self, lstSubcommand=None):
        strSubcommand = lstSubcommand[0]
        strArg1 = None
        if len(lstSubcommand) == 2:
            strArg1 = lstSubcommand[1]
        for handler in self.dicSubCommandHandler[strSubcommand]:
            handler(strArg1)
#tool method #####################################################################################
    #將字串陣列合併之後再 strip
    def stripTextArray(self, lstStrText=None):
        strTextLine = u""
        for strText in lstStrText:
            if strText is not None:
                strText = re.sub("\s", "", strText)
                strTextLine = strTextLine + strText
        return strTextLine.strip()
        
    #解析 回饋組合的贊助狀態 字串 ex."1人待繳5人剩餘94人" return (1,5,94)
    def parseStrRewardBacker(self, strRewardBacker=None):
        (intPayed, intNotPayYet, intRemainQuta) = (0,0,0)
        #pattern X人
        m1 = re.match(u"^([0-9]*)人$", strRewardBacker)
        if m1 is not None:
            intPayed = int(m1.group(1))
            return (intPayed, None, None)
        #pattern X人待繳Y人剩餘Z人
        m2 = re.match(u"^([0-9]*)人待繳([0-9]*)人剩餘([0-9]*)人$", strRewardBacker)
        if m2 is not None:
            intPayed = int(m2.group(1))
            intNotPayYet = int(m2.group(2))
            intRemainQuta = int(m2.group(3))
            return (intPayed, intNotPayYet, intRemainQuta)
        #pattern X人待繳Y人
        m3 = re.match(u"^([0-9]*)人待繳([0-9]*)人$", strRewardBacker)
        if m3 is not None:
            intPayed = int(m3.group(1))
            intNotPayYet = int(m3.group(2))
            return (intPayed, intNotPayYet, None)
        #pattern error
        return None
        
    #轉換預計出貨日期格式
    def formatOriginStrRewardDeliveryDate(self, strOrigin=None):
        strRet = None
        if strOrigin is not None:
            matchObj = re.search(u"^([0-9]*)年([0-9]*)月$", strOrigin)
            if matchObj is not None:
                strRet = "-".join([matchObj.group(1), matchObj.group(2), "01"])
        return strRet

#category #####################################################################################
    #解析 category.html
    def parseCategoryPage(self, uselessArg1=None):
        strBrowseResultFolderPath = self.PARSED_RESULT_BASE_FOLDER_PATH + u"\\WEBACKERS"
        strBrowseHtmlFolderPath = self.SOURCE_HTML_BASE_FOLDER_PATH + u"\\WEBACKERS"
        lstStrCategoryHtmlFolderPath = self.utility.getSubFolderPathList(strBasedir=strBrowseHtmlFolderPath)
        for strCategoryHtmlFolderPath in lstStrCategoryHtmlFolderPath: #各分類子資料夾
            strCategoryResultFolderPath = strBrowseResultFolderPath + u"\\%s"%re.match("^.*WEBACKERS\\\\([a-z]*)$", strCategoryHtmlFolderPath).group(1)
            if not os.path.exists(strCategoryResultFolderPath):
                os.mkdir(strCategoryResultFolderPath) #mkdir parsed_result/WEBACKERS/category/
            strCategoryJsonFilePath = strCategoryResultFolderPath + u"\\category.json"
            #清空 dicParsedResultOfCategory 資料
            self.dicParsedResultOfCategory = {}
            self.dicParsedResultOfCategory["project_url_list"] = []
            self.dicParsedResultOfCategory["profile_url_list"] = []
            #解析各頁的 category.html 並將 url 集合於 json 檔案裡
            lstStrCategoryHtmlFilePath = self.utility.getFilePathListWithSuffixes(strBasedir=strCategoryHtmlFolderPath, strSuffixes=u"category.html")
            for strCategoryHtmlFilePath in lstStrCategoryHtmlFilePath: #category.html 各分頁
                #記錄抓取時間
                strCrawlTime = self.utility.getCtimeOfFile(strFilePath=strCategoryHtmlFilePath)
                self.dicParsedResultOfCategory["strCrawlTime"] = strCrawlTime
                with open(strCategoryHtmlFilePath, "r") as categoryHtmlFile:
                    strPageSource = categoryHtmlFile.read()
                    root = Selector(text=strPageSource)
                    #開始解析
                    lstStrProjectUrl = root.css("li.cbp-item div.thumbnail > a:first-of-type::attr(href)").extract()
                    lstStrProfileUrl = root.css("li.cbp-item div.thumbnail a.pull-left::attr(href)").extract()
                    #寫入 url
                    for strProjectUrl in lstStrProjectUrl:
                        #儲存在 category.html 頁面下的 project 資料
                        dicProjectData = {}
                        #strUrl
                        strFullProjectUrl = self.strWebsiteDomain + strProjectUrl
                        dicProjectData["strUrl"] = strFullProjectUrl
                        #strDescription and #strStatus
                        strDescription = None
                        strStatus = None
                        elesDivItemWrapper = root.css("div.cbp-item-wrapper")
                        for eleDivItemWrapper in elesDivItemWrapper:
                            if len(eleDivItemWrapper.css("div.thumbnail a[href='%s']"%strProjectUrl)) != 0:
                                strDescription = eleDivItemWrapper.css("div.thumbnail div.caption_view p::text").extract_first()
                                lstStrStatus = eleDivItemWrapper.css("div.case_msg_i li.timeitem::text").extract()
                                strStatus = self.stripTextArray(lstStrText=lstStrStatus)
                        dicProjectData["strDescription"] = strDescription
                        dicProjectData["strStatus"] = strStatus
                        #append project 資料
                        self.dicParsedResultOfCategory["project_url_list"].append(dicProjectData)
                    for strProfileUrl in lstStrProfileUrl:
                        strFullProfileUrl = self.strWebsiteDomain + strProfileUrl
                        self.dicParsedResultOfCategory["profile_url_list"].append(strFullProfileUrl)
            self.utility.writeObjectToJsonFile(self.dicParsedResultOfCategory, strCategoryJsonFilePath)
#project #####################################################################################

    #解析 project page(s) 之前
    def beforeParseProjectPage(self, strCategoryName=None):
        self.dicParsedResultOfProject = {} #project.json 資料
        self.dicParsedResultOfUpdate = {} #update.json 資料
        self.dicParsedResultOfQanda = {} #qanda.json 資料
        self.dicParsedResultOfReward = {} #reward.json 資料
        strProjectsResultFolderPath = self.PARSED_RESULT_BASE_FOLDER_PATH + (u"\\WEBACKERS\\%s\\projects"%strCategoryName)
        if not os.path.exists(strProjectsResultFolderPath):
            #mkdir parsed_result/WEBACKERS/category/projects/
            os.mkdir(strProjectsResultFolderPath)
            
    #解析 project page(s) 之後
    def afterParseProjectPage(self, strCategoryName=None):
        strProjectsResultFolderPath = self.PARSED_RESULT_BASE_FOLDER_PATH + (u"\\WEBACKERS\\%s\\projects"%strCategoryName)
        #將 parse 結果寫入 json 檔案
        self.utility.writeObjectToJsonFile(self.dicParsedResultOfProject, strProjectsResultFolderPath + u"\\project.json")
        self.utility.writeObjectToJsonFile(self.dicParsedResultOfReward, strProjectsResultFolderPath + u"\\reward.json")
        self.utility.writeObjectToJsonFile(self.dicParsedResultOfUpdate, strProjectsResultFolderPath + u"\\update.json")
        self.utility.writeObjectToJsonFile(self.dicParsedResultOfQanda, strProjectsResultFolderPath + u"\\qanda.json")
        
    #解析 intro.html
    def parseIntroPage(self, strCategoryName=None):
        strProjectsHtmlFolderPath = self.SOURCE_HTML_BASE_FOLDER_PATH + (u"\\WEBACKERS\\%s\\projects"%strCategoryName)
        lstStrIntroHtmlFilePath = self.utility.getFilePathListWithSuffixes(strBasedir=strProjectsHtmlFolderPath, strSuffixes="_intro.html")
        for strProjectIntroHtmlFilePath in lstStrIntroHtmlFilePath:
            logging.info("parsing %s"%strProjectIntroHtmlFilePath)
            with open(strProjectIntroHtmlFilePath, "r") as projectIntroHtmlFile:
                strProjHtmlFileName = os.path.basename(projectIntroHtmlFile.name)
                #取得 url
                strProjId = re.search("^(.*)_intro.html$", strProjHtmlFileName).group(1)
                strProjUrl = u"https://www.webackers.com/Proposal/Display/" + strProjId
                if strProjUrl not in self.dicParsedResultOfProject:
                    self.dicParsedResultOfProject[strProjUrl] = {}
                #取得 category 頁面的 project 資料
                strCategoryJsonFilePath = self.PARSED_RESULT_BASE_FOLDER_PATH + (u"\\WEBACKERS\\%s\\category.json"%strCategoryName)
                dicCategoryData = self.utility.readObjectFromJsonFile(strJsonFilePath=strCategoryJsonFilePath)
                dicCurrentProjectData = None
                for dicProjectData in dicCategoryData["project_url_list"]:
                    if dicProjectData["strUrl"] == strProjUrl:
                        dicCurrentProjectData = dicProjectData
                #開始解析
                strPageSource = projectIntroHtmlFile.read()
                root = Selector(text=strPageSource)
                # - 解析 project.json -
                #strSource
                self.dicParsedResultOfProject[strProjUrl]["strSource"] = \
                    u"WEBACKERS"
                #strUrl
                self.dicParsedResultOfProject[strProjUrl]["strUrl"] = \
                    strProjUrl
                #strCrawlTime
                strCrawlTime = dicCategoryData["strCrawlTime"]
                self.dicParsedResultOfProject[strProjUrl]["strCrawlTime"] = strCrawlTime
                #strProjectName
                self.dicParsedResultOfProject[strProjUrl]["strProjectName"] = \
                    root.css("a[href*='%s'] span.case_title::text"%strProjId).extract_first().strip()
                #strLocation
                self.dicParsedResultOfProject[strProjUrl]["strLocation"] = u"Taiwan"
                #strCity
                self.dicParsedResultOfProject[strProjUrl]["strCity"] = u"Taiwan"
                #strCountry
                self.dicParsedResultOfProject[strProjUrl]["strCountry"] = u"TW"
                #strContinent
                self.dicParsedResultOfProject[strProjUrl]["strContinent"] = u"AS"
                #strDescription
                strDescription = dicCurrentProjectData["strDescription"]
                self.dicParsedResultOfProject[strProjUrl]["strDescription"] = strDescription
                #strIntroduction
                strIntroduction = u""
                for strIntroductionText in root.css("div.description *::text").extract():
                    strIntroduction = strIntroduction + strIntroductionText
                self.dicParsedResultOfProject[strProjUrl]["strIntroduction"] = strIntroduction
                #intStatus
                dicMappingStatus = {u"已完成":1,
                               u"已結束":2,}
                intStatus = 0
                strStatus = dicCurrentProjectData["strStatus"]
                if strStatus in dicMappingStatus:
                    intStatus = dicMappingStatus[strStatus]
                else:
                    intStatus = 0
                self.dicParsedResultOfProject[strProjUrl]["intStatus"] = intStatus
                #strCreator
                strCreator = root.css("aside.col-md-3 article:nth-of-type(5) h3 a::text").extract_first().strip()
                self.dicParsedResultOfProject[strProjUrl]["strCreator"] = strCreator
                #strCreatorUrl
                strCreatorUrl = root.css("aside.col-md-3 article:nth-of-type(5) h3 a::attr('href')").extract_first().strip()
                self.dicParsedResultOfProject[strProjUrl]["strCreatorUrl"] = self.strWebsiteDomain + strCreatorUrl
                #strCategory and strSubCategory
                strCategory = root.css("a[href*='category='] span.case_title::text").extract_first().strip()
                self.dicParsedResultOfProject[strProjUrl]["strCategory"] = strCategory
                self.dicParsedResultOfProject[strProjUrl]["strSubCategory"] = strCategory
                #intFundTarget
                strFundTarget = root.css("span.money_target::text").extract_first().strip()
                intFundTarget = int(re.sub("[^0-9]", "", strFundTarget))
                self.dicParsedResultOfProject[strProjUrl]["intFundTarget"] = intFundTarget
                #intRaisedMoney
                strRaisedMoney = root.css("span.money_now::text").extract_first().strip()
                intRaisedMoney = int(re.sub("[^0-9]", "", strRaisedMoney))
                self.dicParsedResultOfProject[strProjUrl]["intRaisedMoney"] = intRaisedMoney
                #fFundProgress
                fFundProgress = (float(intRaisedMoney) / float(intFundTarget)) * 100
                self.dicParsedResultOfProject[strProjUrl]["fFundProgress"] = int(fFundProgress)
                #strCurrency
                self.dicParsedResultOfProject[strProjUrl]["strCurrency"] = u"NTD"
                #intRemainDays
                intRemainDays = self.utility.translateTimeleftTextToPureNum(strTimeleftText=strStatus, strVer="WEBACKERS")
                self.dicParsedResultOfProject[strProjUrl]["intRemainDays"] = intRemainDays
                #strEndDate
                strEndDate = None
                if intRemainDays > 0: #進行中
                    strCrawlTime = dicCategoryData["strCrawlTime"]
                    dtCrawlTime = datetime.datetime.strptime(strCrawlTime, "%Y-%m-%d")
                    dtEndDate = dtCrawlTime + datetime.timedelta(days=intRemainDays)
                    strEndDate = dtEndDate.strftime("%Y-%m-%d")
                else:#已完成 或 已結束
                    strEndDate = root.css("aside.col-md-3 article:nth-of-type(4) div.panel-body span:nth-of-type(2)::text").extract_first().strip()
                    dtEndDate = datetime.datetime.strptime(strEndDate, "%Y/%m/%d %H:%M")
                    strEndDate = dtEndDate.strftime("%Y-%m-%d")
                self.dicParsedResultOfProject[strProjUrl]["strEndDate"] = strEndDate
                #strStartDate 無法取得
                self.dicParsedResultOfProject[strProjUrl]["strStartDate"] = None
                #intUpdate
                intUpdate = int(root.css("ul.nav-tabs li a[href*='tab=progress'] div.badge::text").extract_first().strip())
                self.dicParsedResultOfProject[strProjUrl]["intUpdate"] = intUpdate
                #intBacker
                intBacker = int(root.css("ul.nav-tabs li a[href*='tab=sponsor'] div.badge::text").extract_first().strip())
                self.dicParsedResultOfProject[strProjUrl]["intBacker"] = intBacker
                #intComment
                intComment = int(root.css("ul.nav-tabs li a[href*='tab=faq'] div.badge::text").extract_first().strip())
                self.dicParsedResultOfProject[strProjUrl]["intComment"] = intComment
                #intFbLike
                intFbLike = int(root.css("span.fbBtn span.fb_share_count::text").extract_first().strip())
                self.dicParsedResultOfProject[strProjUrl]["intFbLike"] = intFbLike
                #intVideoCount
                intVideoCount = len(root.css("div.description iframe[src*='youtube'], div.flex-video"))
                self.dicParsedResultOfProject[strProjUrl]["intVideoCount"] = intVideoCount
                #intImageCount
                intImageCount = len(root.css("div.description img[src*='image']"))
                self.dicParsedResultOfProject[strProjUrl]["intImageCount"] = intImageCount
                #isPMSelect 無法取得
                self.dicParsedResultOfProject[strProjUrl]["isPMSelect"] = None
                #
                # - 解析 reward.json -
                lstDicRewardData = []
                elesReward = root.css("aside article div.panel")
                for eleReward in elesReward:
                    if len(eleReward.css("div.panel-case")) != 0:
                        dicRewardData = {}
                        #strUrl
                        dicRewardData["strUrl"] = strProjUrl
                        #strRewardContent
                        lstStrRewardContent = eleReward.css("div.panel-body div.fa-black_h.padding_space.txt_line_fix::text").extract()
                        strRewardContent = self.stripTextArray(lstStrText=lstStrRewardContent)
                        dicRewardData["strRewardContent"] = strRewardContent
                        #intRewardMoney
                        strRewardMoney = eleReward.css("div.panel-case div.pull-left span.font_m1::text").extract_first().strip()
                        intRewardMoney = int(re.sub("[^0-9]", "", strRewardMoney))
                        dicRewardData["intRewardMoney"] = intRewardMoney
                        #intRewardBacker
                        lstStrRewardBacker = eleReward.css("div.panel-case div.pull-right::text").extract()
                        strRewardBacker = self.stripTextArray(lstStrText=lstStrRewardBacker) #ex. "1人待繳5人剩餘94人"
                        (intPayed, intNotPayYet, intRemainQuta) = self.parseStrRewardBacker(strRewardBacker=strRewardBacker)
                        intRewardBacker = intPayed
                        dicRewardData["intRewardBacker"] = intRewardBacker
                        #intRewardLimit
                        intRewardLimit = 0
                        if intRemainQuta is not None:
                            intRewardLimit = sum((intPayed, intNotPayYet, intRemainQuta))
                        dicRewardData["intRewardLimit"] = intRewardLimit
                        #strRewardShipTo and strRewardDeliveryDate
                        lstStrDeliveryDateAndShipTo = eleReward.css("div.panel-body div.fa-black_h.bg_gray_h::text").extract()
                        strDeliveryDateAndShipTo = self.stripTextArray(lstStrText=lstStrDeliveryDateAndShipTo) #"寄送條件：.*預計送達：.*"
                        mDeliveryDateAndShipTo = re.match(u"^寄送條件：(.*)預計送達：(.*)$", strDeliveryDateAndShipTo)
                        (strRewardDeliveryDate, strRewardShipTo) = (None, None)
                        if mDeliveryDateAndShipTo is not None:
                            strRewardShipTo = mDeliveryDateAndShipTo.group(1)
                            strRewardDeliveryDate = mDeliveryDateAndShipTo.group(2)
                        dicRewardData["strRewardShipTo"] = strRewardShipTo
                        strRewardDeliveryDate = self.formatOriginStrRewardDeliveryDate(strOrigin=strRewardDeliveryDate) #轉換格式 2016年04月 -> 2016-04-01
                        dicRewardData["strRewardDeliveryDate"] = strRewardDeliveryDate
                        #intRewardRetailPrice
                        dicRewardData["intRewardRetailPrice"] = scrapyUtility.getRetailPrice(strRewardContent,  [u"原價", u"市價", u"價", u"零售"], intRewardMoney=intRewardMoney)
                        #append reward 資料
                        lstDicRewardData.append(dicRewardData)
                self.dicParsedResultOfReward[strProjUrl] = lstDicRewardData
                
    #解析 sponsor.html
    def parseSponsorPage(self, strCategoryName=None):
        strProjectsHtmlFolderPath = self.SOURCE_HTML_BASE_FOLDER_PATH + (u"\\WEBACKERS\\%s\\projects"%strCategoryName)
        lstStrSponsorHtmlFilePath = self.utility.getFilePathListWithSuffixes(strBasedir=strProjectsHtmlFolderPath, strSuffixes="_sponsor.html")
        for strProjectSponsorHtmlFilePath in lstStrSponsorHtmlFilePath:
            logging.info("parsing %s"%strProjectSponsorHtmlFilePath)
            with open(strProjectSponsorHtmlFilePath, "r") as projectSponsorHtmlFile:
                strProjHtmlFileName = os.path.basename(projectSponsorHtmlFile.name)
                #取得 url
                strProjId = re.search("^(.*)_sponsor.html$", strProjHtmlFileName).group(1)
                strProjUrl = u"https://www.webackers.com/Proposal/Display/" + strProjId
                if strProjUrl not in self.dicParsedResultOfProject:
                    self.dicParsedResultOfProject[strProjUrl] = {}
                #開始解析
                strPageSource = projectSponsorHtmlFile.read()
                root = Selector(text=strPageSource)
                #lstStrBacker
                lstStrBacker = root.css("div#sponsor_panel p a.fa-black_h::text").extract()
                self.dicParsedResultOfProject[strProjUrl]["lstStrBacker"] = lstStrBacker
    
    #解析 progress.html
    def parseProgressPage(self, strCategoryName=None):
        strProjectsHtmlFolderPath = self.SOURCE_HTML_BASE_FOLDER_PATH + (u"\\WEBACKERS\\%s\\projects"%strCategoryName)
        lstStrProgressHtmlFilePath = self.utility.getFilePathListWithSuffixes(strBasedir=strProjectsHtmlFolderPath, strSuffixes="_progress.html")
        for strProjectProgressHtmlFilePath in lstStrProgressHtmlFilePath:
            logging.info("parsing %s"%strProjectProgressHtmlFilePath)
            with open(strProjectProgressHtmlFilePath, "r") as projectProgressHtmlFile:
                strProjHtmlFileName = os.path.basename(projectProgressHtmlFile.name)
                #取得 url
                strProjId = re.search("^(.*)_progress.html$", strProjHtmlFileName).group(1)
                strProjUrl = u"https://www.webackers.com/Proposal/Display/" + strProjId
                #開始解析
                strPageSource = projectProgressHtmlFile.read()
                root = Selector(text=strPageSource)
                lstDicUpdateData = []
                elesUpdate = root.css("div.active div.panel-group")
                for eleUpdate in elesUpdate:
                    dicUpdateData = {}
                    #strUrl
                    dicUpdateData["strUrl"] = strProjUrl
                    #strUpdateTitle
                    strUpdateTitle = eleUpdate.css("div.panel-heading div.pull-left h4::text").extract_first().strip()
                    dicUpdateData["strUpdateTitle"] = strUpdateTitle
                    #strUpdateContent
                    lstStrUpdateContentText = eleUpdate.css("div.panel-body div.content_area *::text").extract()
                    strUpdateContent = self.stripTextArray(lstStrText=lstStrUpdateContentText)
                    dicUpdateData["strUpdateContent"] = strUpdateContent
                    #strUpdateDate
                    strUpdateDate = eleUpdate.css("div.panel-heading div.pull-right span:nth-of-type(2)::text").extract_first().strip()
                    strUpdateDate = re.sub("/", "-", strUpdateDate)
                    dicUpdateData["strUpdateDate"] = strUpdateDate
                    #append update 資料
                    lstDicUpdateData.append(dicUpdateData)
                self.dicParsedResultOfUpdate[strProjUrl] = lstDicUpdateData

    #解析 faq.html
    def parseFaqPage(self, strCategoryName=None):
        strProjectsHtmlFolderPath = self.SOURCE_HTML_BASE_FOLDER_PATH + (u"\\WEBACKERS\\%s\\projects"%strCategoryName)
        lstStrFaqHtmlFilePath = self.utility.getFilePathListWithSuffixes(strBasedir=strProjectsHtmlFolderPath, strSuffixes="_faq.html")
        for strProjectFaqHtmlFilePath in lstStrFaqHtmlFilePath:
            logging.info("parsing %s"%strProjectFaqHtmlFilePath)
            with open(strProjectFaqHtmlFilePath, "r") as projectFaqHtmlFile:
                strProjHtmlFileName = os.path.basename(projectFaqHtmlFile.name)
                #取得 url
                strProjId = re.search("^(.*)_faq.html$", strProjHtmlFileName).group(1)
                strProjUrl = u"https://www.webackers.com/Proposal/Display/" + strProjId
                #開始解析
                strPageSource = projectFaqHtmlFile.read()
                root = Selector(text=strPageSource)
                lstDicQandaData = []
                elesQanda = root.css("div.panel-group div.panel")
                for eleQanda in elesQanda:
                    dicQandaData = {}
                    #strUrl
                    dicQandaData["strUrl"] = strProjUrl
                    #strQnaQuestion
                    lstStrQnaQuestionText = eleQanda.css("div.panel-heading a::text").extract()
                    strQnaQuestion = self.stripTextArray(lstStrText=lstStrQnaQuestionText)
                    dicQandaData["strQnaQuestion"] = strQnaQuestion
                    #strQnaAnswer
                    lstStrQnaAnswerText = eleQanda.css("div.panel-collapse div.panel-body div.reply::text").extract()
                    strQnaAnswer = self.stripTextArray(lstStrText=lstStrQnaAnswerText)
                    dicQandaData["strQnaAnswer"] = strQnaAnswer
                    #strQnaDate 無法取得
                    dicQandaData["strQnaDate"] = None
                    #append qanda 資料
                    lstDicQandaData.append(dicQandaData)
                self.dicParsedResultOfQanda[strProjUrl] = lstDicQandaData

#profile #####################################################################################
    #解析 profile page(s) 之前
    def beforeParseProfilePage(self, strCategoryName=None):
        self.dicParsedResultOfProfile = {} #profile.json 資料
        strProfilesResultFolderPath = self.PARSED_RESULT_BASE_FOLDER_PATH + (u"\\WEBACKERS\\%s\\profiles"%strCategoryName)
        if not os.path.exists(strProfilesResultFolderPath):
            #mkdir parsed_result/WEBACKERS/category/profiles
            os.mkdir(strProfilesResultFolderPath)
            
    #解析 profile page(s) 之後
    def afterParseProfilePage(self, strCategoryName=None):
        strProfilesResultFolderPath = self.PARSED_RESULT_BASE_FOLDER_PATH + (u"\\WEBACKERS\\%s\\profiles"%strCategoryName)
        #將 parse 結果寫入 json 檔案
        self.utility.writeObjectToJsonFile(self.dicParsedResultOfProfile, strProfilesResultFolderPath + u"\\profile.json")
        
    #解析 proj.html
    def parseProjPage(self, strCategoryName=None):
        strProfilesHtmlFolderPath = self.SOURCE_HTML_BASE_FOLDER_PATH + (u"\\WEBACKERS\\%s\\profiles"%strCategoryName)
        lstStrProjHtmlFilePath = self.utility.getFilePathListWithSuffixes(strBasedir=strProfilesHtmlFolderPath, strSuffixes="_proj.html")
        for strProfileProjHtmlFilePath in lstStrProjHtmlFilePath:
            logging.info("parsing %s"%strProfileProjHtmlFilePath)
            with open(strProfileProjHtmlFilePath, "r") as profileProjHtmlFile:
                strProfHtmlFileName = os.path.basename(profileProjHtmlFile.name)
                #取得 url
                strProfId = re.search("^(.*)_proj.html$", strProfHtmlFileName).group(1)
                strProfUrl = u"https://www.webackers.com/Proposal/CreatorProfile?proposalId=" + strProfId
                if strProfUrl not in self.dicParsedResultOfProfile:
                    self.dicParsedResultOfProfile[strProfUrl] = {}
                #開始解析
                strPageSource = profileProjHtmlFile.read()
                root = Selector(text=strPageSource)
                #strUrl
                self.dicParsedResultOfProfile[strProfUrl]["strUrl"] = strProfUrl
                #strName
                lstStrNameText = root.css("h4.fa-black::text").extract()
                strName = self.stripTextArray(lstStrText=lstStrNameText)
                self.dicParsedResultOfProfile[strProfUrl]["strName"] = strName
                #strIdentityName 同 strName
                self.dicParsedResultOfProfile[strProfUrl]["strIdentityName"] = strName
                #strDescription
                lstStrDescription = root.css("p small.fa-gray::text").extract()
                strDescription = self.stripTextArray(lstStrText=lstStrDescription)
                self.dicParsedResultOfProfile[strProfUrl]["strDescription"] = strDescription
                #strLocation
                self.dicParsedResultOfProfile[strProfUrl]["strLocation"] = u"Taiwan"
                #strCity
                self.dicParsedResultOfProfile[strProfUrl]["strCity"] = u"Taiwan"
                #strCountry
                self.dicParsedResultOfProfile[strProfUrl]["strCountry"] = u"TW"
                #strContinent
                self.dicParsedResultOfProfile[strProfUrl]["strContinent"] = u"AS"
                #intCreatedCount
                intCreatedCount = int(root.css("ul.nav-tabs li a[href*='tab=project'] div.badge::text").extract_first())
                self.dicParsedResultOfProfile[strProfUrl]["intCreatedCount"] = intCreatedCount
                #intBackedCount
                intBackedCount = int(root.css("ul.nav-tabs li a[href*='tab=order'] div.badge::text").extract_first())
                self.dicParsedResultOfProfile[strProfUrl]["intBackedCount"] = intBackedCount
                #isCreator
                isCreator = (True if intCreatedCount > 0 else False)
                self.dicParsedResultOfProfile[strProfUrl]["isCreator"] = isCreator
                #isBacker
                isBacker = (True if intBackedCount > 0 else False)
                self.dicParsedResultOfProfile[strProfUrl]["isBacker"] = isBacker
                #lstStrCreatedProject and lstStrCreatedProjectUrl
                elesCreatedProject = root.css("div.panel-body div.col-sm-6.col-md-4.col-lg-4.col-xs-12")
                lstStrCreatedProject = []
                lstStrCreatedProjectUrl = []
                lstStrCreatedProjectStatus = []
                for eleCreatedProject in elesCreatedProject:
                    lstStrCreatedProjectText = eleCreatedProject.css("div.thumbnail div.caption h4::text").extract()
                    strCreatedProject = self.stripTextArray(lstStrText=lstStrCreatedProjectText)
                    lstStrCreatedProject.append(strCreatedProject)
                    strCreatedProjectUrl = (self.strWebsiteDomain + 
                                    eleCreatedProject.css("div.thumbnail a::attr('href')").extract_first().strip())
                    lstStrCreatedProjectUrl.append(strCreatedProjectUrl)
                    #記錄 status 以用來計算 intLiveProject, intSuccessProject, intFailedProject
                    lstStrCreatedProjectStatusText = eleCreatedProject.css("div.about_i li.timeitem::text").extract()
                    strCreatedProjectStatus = self.stripTextArray(lstStrText=lstStrCreatedProjectStatusText)
                    lstStrCreatedProjectStatus.append(strCreatedProjectStatus)
                self.dicParsedResultOfProfile[strProfUrl]["lstStrCreatedProject"] = lstStrCreatedProject
                self.dicParsedResultOfProfile[strProfUrl]["lstStrCreatedProjectUrl"] = lstStrCreatedProjectUrl
                #intSuccessProject
                intSuccessProject = lstStrCreatedProjectStatus.count(u"已完成")
                self.dicParsedResultOfProfile[strProfUrl]["intSuccessProject"] = intSuccessProject
                #intFailedProject
                intFailedProject = lstStrCreatedProjectStatus.count(u"已結束")
                self.dicParsedResultOfProfile[strProfUrl]["intFailedProject"] = intFailedProject
                #intLiveProject
                intLiveProject = len(lstStrCreatedProjectStatus) - intSuccessProject - intFailedProject
                self.dicParsedResultOfProfile[strProfUrl]["intLiveProject"] = intLiveProject
                #lstStrSocialNetwork 無法取得
                self.dicParsedResultOfProfile[strProfUrl]["lstStrSocialNetwork"] = None
                #intFbFriend 無法取得
                self.dicParsedResultOfProfile[strProfUrl]["intFbFriend"] = None
                #strLastLoginDate 無法取得
                self.dicParsedResultOfProfile[strProfUrl]["strLastLoginDate"] = None
                
    #解析 order.html
    def parseOrderPage(self, strCategoryName=None):
        strProfilesHtmlFolderPath = self.SOURCE_HTML_BASE_FOLDER_PATH + (u"\\WEBACKERS\\%s\\profiles"%strCategoryName)
        lstStrOrderHtmlFilePath = self.utility.getFilePathListWithSuffixes(strBasedir=strProfilesHtmlFolderPath, strSuffixes="_order.html")
        for strProfileOrderHtmlFilePath in lstStrOrderHtmlFilePath:
            logging.info("parsing %s"%strProfileOrderHtmlFilePath)
            with open(strProfileOrderHtmlFilePath, "r") as profileOrderHtmlFile:
                strProfHtmlFileName = os.path.basename(profileOrderHtmlFile.name)
                #取得 url
                strProfId = re.search("^(.*)_order.html$", strProfHtmlFileName).group(1)
                strProfUrl = u"https://www.webackers.com/Proposal/CreatorProfile?proposalId=" + strProfId
                if strProfUrl not in self.dicParsedResultOfProfile:
                    self.dicParsedResultOfProfile[strProfUrl] = {}
                #開始解析
                strPageSource = profileOrderHtmlFile.read()
                root = Selector(text=strPageSource)
                #lstStrBackedProject and lstStrBackedProjectUrl
                elesBackedProject = root.css("div#history-panel div.col-sm-6.col-md-4.col-lg-4.col-xs-12")
                lstStrBackedProject = []
                lstStrBackedProjectUrl = []
                for eleBackedProject in elesBackedProject:
                    strBackedProject = eleBackedProject.css("div.thumbnail div.caption h4::text").extract_first().strip()
                    lstStrBackedProject.append(strBackedProject)
                    strBackedProjectUrl = (self.strWebsiteDomain + 
                                           eleBackedProject.css("div.thumbnail > a::attr('href')").extract_first().strip())
                    lstStrBackedProjectUrl.append(strBackedProjectUrl)
                self.dicParsedResultOfProfile[strProfUrl]["lstStrBackedProject"] = lstStrBackedProject
                self.dicParsedResultOfProfile[strProfUrl]["lstStrBackedProjectUrl"] = lstStrBackedProjectUrl
                
    #解析 sub.html 目前無用處暫不處理
    def parseSubPage(self, strCategoryName=None):
        pass
#automode #####################################################################################
    #全自動 解析 所有類別 的 案件頁面 及 個人資料頁面
    def parseProjectAndProfilePageAutoMode(self, uselessArg1=None):
        for strCategoryName in self.lstStrCategoryName:
            #parse project page
            self.beforeParseProjectPage(strCategoryName)
            self.parseIntroPage(strCategoryName)
            self.parseSponsorPage(strCategoryName)
            self.parseProgressPage(strCategoryName)
            self.parseFaqPage(strCategoryName)
            self.afterParseProjectPage(strCategoryName)
            #parse profile page
            self.beforeParseProfilePage(strCategoryName)
            self.parseProjPage(strCategoryName)
            self.parseOrderPage(strCategoryName)
            self.afterParseProfilePage(strCategoryName)