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
"""
INDIEGOGO 改版 2016-05-27 改寫
從 source_html 的 HTML 檔案解析資料
結果放置於 parsed_result 下
"""
class ParserV2ForINDIEGOGO:
    #建構子
    def __init__(self):
        self.utility = Utility()
        self.dicSubCommandHandler = {"explore":[self.parseExplorePage],
                                     "category":[self.parseCategoryPage],
                                     "project":[self.beforeParseProjectPage,
                                                self.parseProjectDetailsPage,
                                                self.parseProjectStoryPage,
                                                self.parseProjectUpdatesPage,
                                                self.parseProjectCommentsPage,
                                                self.parseProjectBackersPage,
                                                self.parseProjectRewardPage,
                                                self.parseProjectGalleryPage,
                                                self.afterParseProjectPage],
                                     "individuals":[self.beforeParseIndividualsPage,
                                                    self.parseIndividualsProfilePage,
                                                    self.parseIndividualsCampaignsPage,
                                                    self.afterParseIndividualsPage],}
        self.SOURCE_HTML_BASE_FOLDER_PATH = u"cameo_res\\source_html"
        self.PARSED_RESULT_BASE_FOLDER_PATH = u"cameo_res\\parsed_result"
        self.CATEGORY_URL_LIST_FILENAME = u"category_url_list.txt"
        self.PROJ_URL_LIST_FILENAME = u"_proj_url_list.txt"
        self.dicParsedResultOfProject = {} #project.json 資料
        self.dicParsedResultOfUpdate = {} #update.json 資料
        self.dicParsedResultOfComment = {} #comment.json 資料
        self.dicParsedResultOfReward = {} #reward.json 資料
        self.dicParsedResultOfProfile = {} #profile.json 資料
        
    #取得 parser 使用資訊
    def getUseageMessage(self):
        return ("- INDIEGOGO -\n"
                "useage:\n"
                "explore - parse explore.html then create category_url_list.txt\n"
                "category - parse category.html then create project_url_list.txt\n"
                "project category - parse project's html of given category then create .json\n"
                "individuals category - parse individuals's html of given category then create .json\n")

    #執行 parser
    def runParser(self, lstSubcommand=None):
        strSubcommand = lstSubcommand[0]
        strArg1 = None
        if len(lstSubcommand) == 2:
            strArg1 = lstSubcommand[1]
        for handler in self.dicSubCommandHandler[strSubcommand]:
            handler(strArg1)
#explore #####################################################################################
    #解析 explore.html
    def parseExplorePage(self, uselessArg1=None):
        strExploreHtmlPath = self.SOURCE_HTML_BASE_FOLDER_PATH + u"\\INDIEGOGO\\explore.html"
        strExploreResultFolderPath = self.PARSED_RESULT_BASE_FOLDER_PATH + u"\\INDIEGOGO"
        if not os.path.exists(strExploreResultFolderPath):
            os.mkdir(strExploreResultFolderPath) #mkdir parsed_result/INDIEGOGO/
        with open(strExploreHtmlPath, "r") as expHtmlFile:
            strPageSource = expHtmlFile.read()
        root = Selector(text=strPageSource)
        lstStrCategoryUrls = root.css("explore-category-link-www a.i-uncolored-link::attr(href)").extract()
        if len(lstStrCategoryUrls) == 0:
            lstStrCategoryUrls = root.css("ul.exploreCategories-list li.ng-scope a.ng-binding::attr(href)").extract()
        strCategoryUrlListFilePath = strExploreResultFolderPath + u"\\" + self.CATEGORY_URL_LIST_FILENAME
        with open(strCategoryUrlListFilePath, "w+") as catUrlListFile:
            for strCategoryUrl in lstStrCategoryUrls:
                strCategoryUrl = re.sub("#/browse", "", strCategoryUrl)
                strCategoryUrl = re.search("^(https://www.indiegogo.com/explore/[a-z_]*)\??.*$" ,strCategoryUrl).group(1)
                if strCategoryUrl == "https://www.indiegogo.com/explore/all":
                    continue
                else:
                    catUrlListFile.write(strCategoryUrl + u"\n")
#category #####################################################################################
    #解析 category.html
    def parseCategoryPage(self, uselessArg1=None):
        strCategoryUrlListFilePath = self.PARSED_RESULT_BASE_FOLDER_PATH + u"\\INDIEGOGO\\category_url_list.txt"
        catUrlListFile = open(strCategoryUrlListFilePath)
        for strCategoryUrl in catUrlListFile:#category loop
            strCategoryName = re.search("^https://www.indiegogo.com/explore/(.*)$" ,strCategoryUrl).group(1)
            strCategoryHtmlPath = self.SOURCE_HTML_BASE_FOLDER_PATH + u"\\INDIEGOGO\\%s\\category.html"%(strCategoryName)
            if os.path.exists(strCategoryHtmlPath):#check category.html exists
                strCategoryResultFolderPath = self.PARSED_RESULT_BASE_FOLDER_PATH + u"\\INDIEGOGO\\" + strCategoryName
                if not os.path.exists(strCategoryResultFolderPath):
                    os.mkdir(strCategoryResultFolderPath) #mkdir parsed_result/INDIEGOGO/category/
                with open(strCategoryHtmlPath, "r") as catHtmlFile: #open category.html
                    strPageSource = catHtmlFile.read()
                    root = Selector(text=strPageSource)
                    #project url
                    lstStrProjUrls = root.css("a.discoveryCard::attr(href)").extract() #parse proj urls
                    #記錄抓取時間
                    fCTimeStamp = os.path.getctime(strCategoryHtmlPath)
                    dtCrawlTime = datetime.datetime.fromtimestamp(fCTimeStamp)
                    strCrawlTime = dtCrawlTime.strftime("%Y-%m-%d")
                    #寫入檔案
                    strProjectUrlListFilePath = strCategoryResultFolderPath + u"\\project_url_list.txt"
                    strProjectTimeleftListFilePath = strCategoryResultFolderPath + u"\\project_timeleft_list.txt"
                    with open(strProjectUrlListFilePath, "w+") as projUrlListFile, open(strProjectTimeleftListFilePath, "w+") as projTimeleftListFile:
                        projTimeleftListFile.write(u"Crawl-Time:%s\n"%strCrawlTime)
                        for strProjUrl in lstStrProjUrls:
                            #write to project_url_list.txt
                            projUrlListFile.write(strProjUrl + u"\n")
                            #記錄剩餘時間
                            strProjTimeleft = root.css("a.discoveryCard[href='%s'] div.discoveryCard-timeleft::text"%strProjUrl).extract_first() #parse proj time left
                            #轉換剩餘時間 (Indemaned 及 No time left 均轉為 0)
                            intRemainDays = self.utility.translateTimeleftTextToPureNum(strTimeleftText=strProjTimeleft, strVer="INDIEGOGO")
                            #專案結束日期
                            strEndDate = None
                            if strProjTimeleft == None: #InDemaned
                                strEndDate = "indemand"
                            elif intRemainDays == 0: #No time left
                                strEndDate = "closed"
                            elif intRemainDays > 0:
                                dtEndDate = dtCrawlTime + datetime.timedelta(days=intRemainDays)
                                strEndDate = dtEndDate.strftime("%Y-%m-%d")
                            #write to project_timeleft_list.txt
                            projTimeleftListFile.write(strProjUrl + u"," + unicode(intRemainDays) + u"," + unicode(strEndDate) + u"\n")
#project #####################################################################################
    #解析 project page(s) 之前
    def beforeParseProjectPage(self, strCategoryName=None):
        self.dicParsedResultOfProject = {} #project.json 資料
        self.dicParsedResultOfUpdate = {} #update.json 資料
        self.dicParsedResultOfComment = {} #comment.json 資料
        self.dicParsedResultOfReward = {} #reward.json 資料
        strProjectsResultFolderPath = self.PARSED_RESULT_BASE_FOLDER_PATH + (u"\\INDIEGOGO\\%s\\projects"%strCategoryName)
        if not os.path.exists(strProjectsResultFolderPath):
            #mkdir parsed_result/INDIEGOGO/category/projects/
            os.mkdir(strProjectsResultFolderPath)
            
    #解析 project page(s) 之後
    def afterParseProjectPage(self, strCategoryName=None):
        strProjectsResultFolderPath = self.PARSED_RESULT_BASE_FOLDER_PATH + (u"\\INDIEGOGO\\%s\\projects"%strCategoryName)
        #將 parse 結果寫入 json 檔案
        self.utility.writeObjectToJsonFile(self.dicParsedResultOfProject, strProjectsResultFolderPath + u"\\project.json")
        self.utility.writeObjectToJsonFile(self.dicParsedResultOfUpdate, strProjectsResultFolderPath + u"\\update.json")
        self.utility.writeObjectToJsonFile(self.dicParsedResultOfComment, strProjectsResultFolderPath + u"\\comment.json")
        self.utility.writeObjectToJsonFile(self.dicParsedResultOfReward, strProjectsResultFolderPath + u"\\reward.json")
            
    #檢查 project url 是否在 project_url_list.txt 列表內
    def checkIsProjUrlInProjUrlListFile(self, strCategoryName=None, strProjUrl=None):
        isExists = False
        strProjectUrlListFilePath = self.PARSED_RESULT_BASE_FOLDER_PATH + u"\\INDIEGOGO\\%s\\project_url_list.txt"%strCategoryName
        with open(strProjectUrlListFilePath, "r") as projUrlListFile:
            for strProjUrlLine in projUrlListFile:
                if strProjUrl in strProjUrlLine:
                    isExists = True
        return isExists
    
    #解析 _details.html
    def parseProjectDetailsPage(self, strCategoryName=None):
        strProjectsHtmlFolderPath = self.SOURCE_HTML_BASE_FOLDER_PATH + (u"\\INDIEGOGO\\%s\\projects"%strCategoryName)
        lstStrDetailsHtmlFilePath = self.utility.getFilePathListWithSuffixes(strBasedir=strProjectsHtmlFolderPath, strSuffixes="_details.html")
        for strProjectDetailsHtmlPath in lstStrDetailsHtmlFilePath:
            logging.info("parsing %s"%strProjectDetailsHtmlPath)
            with open(strProjectDetailsHtmlPath, "r") as projDetailsHtmlFile: #open *_details.html
                strProjHtmlFileName = os.path.basename(projDetailsHtmlFile.name)
                strProjUrl = "https://www.indiegogo.com/projects/" + re.search("^(.*)_details.html$", strProjHtmlFileName).group(1)
                if not self.checkIsProjUrlInProjUrlListFile(strCategoryName=strCategoryName, strProjUrl=strProjUrl):
                    logging.warning("%s not in project_url_list.txt, skip parse it"%strProjUrl)
                    continue #skip
                if strProjUrl not in self.dicParsedResultOfProject:
                    self.dicParsedResultOfProject[strProjUrl] = {}
                strPageSource = projDetailsHtmlFile.read()
                root = Selector(text=strPageSource)
                #parse *_details.html
                #strCreatorUrl
                strIndividualsUrl = root.css("div.campaignTrustPassportDesktop-ownerInfo a.ng-binding[href*='individuals']::attr(href)").extract_first() #parse individuals url
                self.dicParsedResultOfProject[strProjUrl]["strCreatorUrl"] = strIndividualsUrl
                # append url to parsed_result/*/category/individuals_url_list.txt
                strIndividualsUrlListFilePath = self.PARSED_RESULT_BASE_FOLDER_PATH + (u"\\INDIEGOGO\\%s\\individuals_url_list.txt"%(strCategoryName))
                lstStrExistsIndividualsUrl = []
                if os.path.exists(strIndividualsUrlListFilePath):
                    with open(strIndividualsUrlListFilePath, "r") as individualsUrlListFile:
                        lstStrExistsIndividualsUrl = individualsUrlListFile.readlines()
                if strIndividualsUrl+u"\n" not in lstStrExistsIndividualsUrl:#檢查有無重覆的 individuals url
                    with open(strIndividualsUrlListFilePath, "a") as individualsUrlListFile:
                        individualsUrlListFile.write(strIndividualsUrl + u"\n") #append url to individuals_url_list.txt
                    
    #解析 _story.html
    def parseProjectStoryPage(self, strCategoryName=None):
        strProjectsHtmlFolderPath = self.SOURCE_HTML_BASE_FOLDER_PATH + (u"\\INDIEGOGO\\%s\\projects"%strCategoryName)
        lstStrStoryHtmlFilePath = self.utility.getFilePathListWithSuffixes(strBasedir=strProjectsHtmlFolderPath, strSuffixes="_story.html")
        for strProjStoryFilePath in lstStrStoryHtmlFilePath:
            try:
                logging.info("parsing %s"%strProjStoryFilePath)
                with open(strProjStoryFilePath, "r") as projStoryHtmlFile:
                    strProjHtmlFileName = os.path.basename(projStoryHtmlFile.name)
                    strProjUrl = "https://www.indiegogo.com/projects/" + re.search("^(.*)_story.html$", strProjHtmlFileName).group(1)
                    if not self.checkIsProjUrlInProjUrlListFile(strCategoryName=strCategoryName, strProjUrl=strProjUrl):
                        logging.warning("%s not in project_url_list.txt, skip parse it"%strProjUrl)
                        continue #skip
                    if strProjUrl not in self.dicParsedResultOfProject:
                        self.dicParsedResultOfProject[strProjUrl] = {}
                    strPageSource = projStoryHtmlFile.read()
                    root = Selector(text=strPageSource)
                    #parse *_story.html
                    #strSource
                    self.dicParsedResultOfProject[strProjUrl]["strSource"] = \
                        u"INDIEGOGO"
                    #strUrl
                    self.dicParsedResultOfProject[strProjUrl]["strUrl"] = \
                        strProjUrl
                    #strProjectName
                    self.dicParsedResultOfProject[strProjUrl]["strProjectName"] = \
                        root.css("h1.campaignHeader-title::text").extract_first().strip()
                    #strLocation
                    self.dicParsedResultOfProject[strProjUrl]["strLocation"] = \
                        root.css("div.campaignHeader-location a.ng-binding::text").extract_first().strip()
                    #strCity
                    strCity = root.css("div.campaignHeader-city a.ng-binding::text").extract_first()
                    strCity = (strCity.strip() if strCity is not None else None)
                    self.dicParsedResultOfProject[strProjUrl]["strCity"] = strCity
                    #strCountry
                    strCountry = root.css("div.campaignTrustTeaser-item:nth-of-type(2) div.campaignTrustTeaser-text div.ng-binding:nth-of-type(3)::text").extract_first().strip()
                    self.dicParsedResultOfProject[strProjUrl]["strCountry"] = \
                        self.utility.getCountryCode(strCountry)
                    #strContinent
                    self.dicParsedResultOfProject[strProjUrl]["strContinent"] = \
                        self.utility.getContinentByCountryNameWikiVersion(strCountry)
                    #strDescription
                    self.dicParsedResultOfProject[strProjUrl]["strDescription"] = \
                        root.css("div.i-musty-background div:nth-of-type(1)::text").extract_first().strip()
                    #strIntroduction
                    strIntroduction = u""
                    lstStrIntroductionParagraph = root.css("div.i-description  campaign-description *::text").extract()
                    for strIntroductionParagraph in lstStrIntroductionParagraph:
                        strIntroduction = strIntroduction + strIntroductionParagraph.strip()
                    self.dicParsedResultOfProject[strProjUrl]["strIntroduction"] = \
                        strIntroduction
                    #strCreator
                    self.dicParsedResultOfProject[strProjUrl]["strCreator"] = \
                        root.css("div.campaignTrustTeaser-item:nth-of-type(1) div.campaignTrustTeaser-text div.campaignTrustTeaser-text-title::text").extract_first().strip()
                    #intImageCount
                    strGalleryCountText = root.css("span.i-tab:nth-of-type(5) span span::text").extract_first()
                    intImageCount = 0
                    if strGalleryCountText != None:
                        intImageCount = int(strGalleryCountText.strip())
                    self.dicParsedResultOfProject[strProjUrl]["intImageCount"] = intImageCount
                    #intStatus
                    isIndemand = False
                    isClosed = False
                    if len(root.css("div.indemandSidebar-banner").extract()) > 0:
                        isIndemand = True
                    if len(root.css("div.i-campaign-closed").extract()) > 0:
                        isClosed = True
                    intIndemandFundedPersentage = 0
                    intFundingPersentage = 0
                    if isIndemand: #InDemaned
                        strIndemandBlurbText = root.css("div.preOrder-fundingBlurb::text").extract_first().strip()
                        intIndemandFundedPersentage = int(re.search("^Original campaign was ([0-9\.]*)% funded on .*$", strIndemandBlurbText).group(1))
                        if intIndemandFundedPersentage >= 100:
                            self.dicParsedResultOfProject[strProjUrl]["intStatus"] = 3
                        else:
                            self.dicParsedResultOfProject[strProjUrl]["intStatus"] = 4
                    elif isClosed:
                        strClosedText = root.css("div.indemandSidebar-closed-textSection::text").extract_first()
                        if (strClosedText is not None) and (u"100%" in strClosedText):
                            self.dicParsedResultOfProject[strProjUrl]["intStatus"] = 1
                        else:
                            self.dicParsedResultOfProject[strProjUrl]["intStatus"] = 2
                    else:#not InDemaned and not Closed
                        strMetaFundingText = root.css("div.campaignGoal-barMetaFunding em::text").extract_first().strip()
                        intFundingPersentage = int(re.search("([0-9\.]*)%", strMetaFundingText).group(1))
                        if intFundingPersentage >= 100: #已超過 100%
                            self.dicParsedResultOfProject[strProjUrl]["intStatus"] = 1
                        else:#未超過 100%
                            strMetaRemainingText = root.css("div.campaignGoal-barMetaRemaining em::text").extract_first()
                            if strMetaRemainingText != None and strMetaRemainingText.strip() == u"No":
                                #已結束 (No time left)
                                self.dicParsedResultOfProject[strProjUrl]["intStatus"] = 2
                            else:
                                #未結束
                                self.dicParsedResultOfProject[strProjUrl]["intStatus"] = 0
                    #strCategory
                    strCategory = root.css("div.campaignTrustTeaser-item:nth-of-type(2) div.campaignTrustTeaser-text-title::text").extract_first().strip()
                    self.dicParsedResultOfProject[strProjUrl]["strCategory"] = \
                        strCategory
                    #strSubCategory 與 strCategory 相同
                    self.dicParsedResultOfProject[strProjUrl]["strSubCategory"] = \
                        strCategory
                    #intRaisedMoney
                    intRaisedMoney = 0
                    if isIndemand:
                        strFundsAmountText = root.css("div.preOrder-combinedBalance div.ng-binding span.currency span::text").extract_first().strip()
                    elif isClosed:
                        strFundsAmountText = root.css("div.preOrder-combinedBalance div.ng-binding span.currency span::text").extract_first()
                        if strFundsAmountText is not None:
                            strFundsAmountText = strFundsAmountText.strip()
                        else:
                            strFundsAmountText = u"0"
                    else:
                        strFundsAmountText = root.css("div.campaignGoal-funds span.campaignGoal-fundsAmount span.currency span::text").extract_first().strip()
                    intRaisedMoney = int(re.sub("[^0-9]", "", strFundsAmountText))
                    self.dicParsedResultOfProject[strProjUrl]["intRaisedMoney"] = \
                        intRaisedMoney
                    #intFundTarget
                    if isIndemand:
                        intFundTarget = int(float(intRaisedMoney) / (float(intIndemandFundedPersentage) / 100 ))
                    elif isClosed:
                        intFundTarget = None
                    else:
                        strRaisedGoalText = root.css("span.campaignGoal-fundsRaisedGoal span.numeral::text").extract_first().strip()
                        intFundTarget = int(re.sub("[^0-9]", "", strRaisedGoalText))
                    self.dicParsedResultOfProject[strProjUrl]["intFundTarget"] = intFundTarget
                    #fFundProgress
                    if isIndemand:
                        self.dicParsedResultOfProject[strProjUrl]["fFundProgress"] = float(intIndemandFundedPersentage)
                    elif isClosed:
                        self.dicParsedResultOfProject[strProjUrl]["fFundProgress"] = None
                    else:
                        self.dicParsedResultOfProject[strProjUrl]["fFundProgress"] = float(intFundingPersentage)
                    #strCurrency
                    if isIndemand:
                        strCurrencyText = root.css("div.preOrder-combinedBalance div.ng-binding span.currency em::text").extract_first().strip()
                    elif isClosed:
                        strCurrencyText = root.css("div.preOrder-combinedBalance div.ng-binding span.currency em::text").extract_first()
                        if strCurrencyText is not None:
                            strCurrencyText = strCurrencyText.strip()
                        else:
                            strCurrencyText = None
                    else:
                        strCurrencyText = root.css("div.campaignGoal-funds span.campaignGoal-fundsAmount span.currency em::text").extract_first().strip()
                    self.dicParsedResultOfProject[strProjUrl]["strCurrency"] = strCurrencyText
                    #intBacker
                    self.dicParsedResultOfProject[strProjUrl]["intBacker"] = \
                        int(root.css("span.i-tab:nth-of-type(4) span span::text").extract_first().strip())
                    #intUpdate
                    self.dicParsedResultOfProject[strProjUrl]["intUpdate"] = \
                        int(root.css("span.i-tab:nth-of-type(2) span span::text").extract_first().strip())
                    #intComment
                    self.dicParsedResultOfProject[strProjUrl]["intComment"] = \
                        int(root.css("span.i-tab:nth-of-type(3) span span::text").extract_first().strip())
                    #intFbLike
                    strShareBannerText = root.css("div.shareBanner div.shareBanner-label div.shareBanner-labelText::text").extract_first().strip()
                    intFbLike = self.utility.translateNumTextToPureNum(strShareBannerText)
                    self.dicParsedResultOfProject[strProjUrl]["intFbLike"] = intFbLike
                    #isDemand
                    if isIndemand:
                        self.dicParsedResultOfProject[strProjUrl]["isDemand"] = True
                    else:
                        self.dicParsedResultOfProject[strProjUrl]["isDemand"] = False
                    #isAON
                    strIStatusText = root.css("div.campaignGoal-goalFundingType span.i-status::text").extract_first()
                    if strIStatusText != None and strIStatusText.strip() == "Flexible Funding":
                        self.dicParsedResultOfProject[strProjUrl]["isAON"] = True
                    else:
                        self.dicParsedResultOfProject[strProjUrl]["isAON"] = False
                    strProjectTimeleftListFilePath = self.PARSED_RESULT_BASE_FOLDER_PATH + (u"\\INDIEGOGO\\%s\\project_timeleft_list.txt"%strCategoryName)
                    with open(strProjectTimeleftListFilePath, "r") as projectTimeleftListFile:
                        #strCrawlTime local category.html的建立時間
                        strCrawlTime = projectTimeleftListFile.readline().split(u":")[1].strip()
                        #intRemainDays and strEndDate
                        intRemainDays = 0
                        strEndDate = None
                        isProjInProjTimeleftList = False
                        for strProjTimeleftLine in projectTimeleftListFile:
                            if strProjUrl in strProjTimeleftLine:
                                isProjInProjTimeleftList = True
                                intRemainDays = int(strProjTimeleftLine.split(",")[1].strip())
                                strEndDate = strProjTimeleftLine.split(",")[2].strip()
                        if not isProjInProjTimeleftList:
                            strCrawlTime = None
                        self.dicParsedResultOfProject[strProjUrl]["strCrawlTime"] = \
                            strCrawlTime
                        self.dicParsedResultOfProject[strProjUrl]["intRemainDays"] = \
                            intRemainDays
                        self.dicParsedResultOfProject[strProjUrl]["strEndDate"] = \
                            strEndDate
                    #intVideoCount
                    lstVideoElements = root.css("campaign-video.campaignVideo, iframe.embedly-embed[src*='media']").extract()
                    self.dicParsedResultOfProject[strProjUrl]["intVideoCount"] = \
                        len(lstVideoElements)
                    #strStartDate = "" 無法取得
                    self.dicParsedResultOfProject[strProjUrl]["strStartDate"] = None
                    #isPMSelect = "" 無法取得
                    self.dicParsedResultOfProject[strProjUrl]["isPMSelect"] = None
                    #strCreatorUrl = "" 已由 parseProjectDetailsPage 取得
                    #lstStrBacker = "" 已由 parseProjectBackersPage 取得
            except:
                strErrorLogFilePath = self.PARSED_RESULT_BASE_FOLDER_PATH + (u"\\INDIEGOGO\\error.log")
                with open(strErrorLogFilePath, "a") as errFile:
                    errFile.write(strProjUrl + "\n")
                continue
                
    #解析 _updates.html
    def parseProjectUpdatesPage(self, strCategoryName=None):
        strProjectsHtmlFolderPath = self.SOURCE_HTML_BASE_FOLDER_PATH + (u"\\INDIEGOGO\\%s\\projects"%strCategoryName)
        lstStrUpdatesHtmlFilePath = self.utility.getFilePathListWithSuffixes(strBasedir=strProjectsHtmlFolderPath, strSuffixes="_updates.html")
        for strProjUpdatesFilePath in lstStrUpdatesHtmlFilePath:
            logging.info("parsing %s"%strProjUpdatesFilePath)
            with open(strProjUpdatesFilePath, "r") as projUpdatesHtmlFile:
                strProjHtmlFileName = os.path.basename(projUpdatesHtmlFile.name)
                strProjUrl = "https://www.indiegogo.com/projects/" + re.search("^(.*)_updates.html$", strProjHtmlFileName).group(1)
                if not self.checkIsProjUrlInProjUrlListFile(strCategoryName=strCategoryName, strProjUrl=strProjUrl):
                    logging.warning("%s not in project_url_list.txt, skip parse it"%strProjUrl)
                    continue #skip
                strPageSource = projUpdatesHtmlFile.read()
                root = Selector(text=strPageSource)
                #parse *_updates.html
                lstDicUpdateData = []
                #loop of append update data to lstDicUpdateData
                for elementUpdate in root.css("desktop-updates div.activityUpdate"):
                    dicUpdateData = {}
                    #strUrl
                    dicUpdateData["strUrl"] = strProjUrl
                    #strUpdateContent
                    strUpdateContent = u""
                    lstStrUpdateContentParagraph = elementUpdate.css("div.ugcContent *::text").extract()
                    for strUpdateContentParagraph in lstStrUpdateContentParagraph:
                        strUpdateContent = strUpdateContent + strUpdateContentParagraph.strip()
                    dicUpdateData["strUpdateContent"] = strUpdateContent
                    #strUpdateDate
                    strUpdateDate = None
                    strOriginUpdateDate = elementUpdate.css("h2.activityUpdate-timestamp::text").extract_first().strip()
                    strParsedUpdateDate = self.utility.parseStrDateByDateparser(strOriginDate=strOriginUpdateDate,
                                                               strBaseDate=self.utility.getCtimeOfFile(strFilePath=strProjUpdatesFilePath))
                    #如果原文字含有 months ago 將轉換後的日期強制設定為 01 號
                    if "month" in strOriginUpdateDate.lower():
                        lstStrParsedUpdateDate = list(strParsedUpdateDate)
                        lstStrParsedUpdateDate[-1] = "1"
                        lstStrParsedUpdateDate[-2] = "0"
                        strUpdateDate = "".join(lstStrParsedUpdateDate)
                    else:
                        strUpdateDate = strParsedUpdateDate
                    dicUpdateData["strUpdateDate"] = strUpdateDate
                    #intComment 無法取得
                    dicUpdateData["intComment"] = None
                    #intLike 無法取得
                    dicUpdateData["intLike"] = None
                    #strUpdateTitle 無法取得
                    dicUpdateData["strUpdateTitle"] = None
                    lstDicUpdateData.append(dicUpdateData)
                self.dicParsedResultOfUpdate[strProjUrl] = lstDicUpdateData
        
    #解析 _comments.html
    def parseProjectCommentsPage(self, strCategoryName=None):
        strProjectsHtmlFolderPath = self.SOURCE_HTML_BASE_FOLDER_PATH + (u"\\INDIEGOGO\\%s\\projects"%strCategoryName)
        lstStrCommentsHtmlFilePath = self.utility.getFilePathListWithSuffixes(strBasedir=strProjectsHtmlFolderPath, strSuffixes="_comments.html")
        for strProjCommentsFilePath in lstStrCommentsHtmlFilePath:
            logging.info("parsing %s"%strProjCommentsFilePath)
            with open(strProjCommentsFilePath, "r") as projCommentsHtmlFile:
                strProjHtmlFileName = os.path.basename(projCommentsHtmlFile.name)
                strProjUrl = "https://www.indiegogo.com/projects/" + re.search("^(.*)_comments.html$", strProjHtmlFileName).group(1)
                if not self.checkIsProjUrlInProjUrlListFile(strCategoryName=strCategoryName, strProjUrl=strProjUrl):
                    logging.warning("%s not in project_url_list.txt, skip parse it"%strProjUrl)
                    continue #skip
                strPageSource = projCommentsHtmlFile.read()
                root = Selector(text=strPageSource)
                #parse *_comments.html
                lstDicCommentData = []
                #loop of append comment data to lstDicCommentData
                for elementComment in root.css("div.i-comments desktop-comment"):
                    dicCommentData = {}
                    #strUrl
                    dicCommentData["strUrl"] = strProjUrl
                    #strCommentName
                    dicCommentData["strCommentName"] = \
                        elementComment.css("div.commentLayout-header:nth-of-type(1) a.commentLayout-account::text").extract_first()
                    #isCreator
                    strPillText = elementComment.css("div.commentLayout-header:nth-of-type(1) span.i-annotation-pill::text").extract_first()
                    isCreator = False
                    if strPillText != None and strPillText.strip() == "Campaigner":
                        isCreator = True
                    dicCommentData["isCreator"] = isCreator
                    #strCommentContent
                    strCommentContent = u""
                    lstStrCommentContentParagraph = elementComment.css("div.commentLayout-text:nth-of-type(2) *::text").extract()
                    for strCommentContentParagraph in lstStrCommentContentParagraph:
                        strCommentContent = strCommentContent + strCommentContentParagraph.strip()
                    dicCommentData["strCommentContent"] = strCommentContent
                    #strCommentDate
                    strCommentDate = None
                    strOriginCommentDate = elementComment.css("div.commentLayout-header:nth-of-type(1) span.commentNote::text").extract_first().strip()
                    strParsedCommentDate = self.utility.parseStrDateByDateparser(strOriginDate=strOriginCommentDate,
                                                                strBaseDate=self.utility.getCtimeOfFile(strFilePath=strProjCommentsFilePath))
                    #如果原文字含有 months ago 將轉換後的日期強制設定為 01 號
                    if "month" in strOriginCommentDate.lower():
                        lstStrParsedCommentDate = list(strParsedCommentDate)
                        lstStrParsedCommentDate[-1] = "1"
                        lstStrParsedCommentDate[-2] = "0"
                        strCommentDate = "".join(lstStrParsedCommentDate)
                    else:
                        strCommentDate = strParsedCommentDate
                    dicCommentData["strCommentDate"] = strCommentDate
                    #加入 Comment 資料
                    lstDicCommentData.append(dicCommentData)
                self.dicParsedResultOfComment[strProjUrl] = lstDicCommentData
                
    #解析 _backers.html
    def parseProjectBackersPage(self, strCategoryName=None):
        strProjectsHtmlFolderPath = self.SOURCE_HTML_BASE_FOLDER_PATH + (u"\\INDIEGOGO\\%s\\projects"%strCategoryName)
        lstStrBackersHtmlFilePath = self.utility.getFilePathListWithSuffixes(strBasedir=strProjectsHtmlFolderPath, strSuffixes="_backers.html")
        for strProjBackersFilePath in lstStrBackersHtmlFilePath:
            logging.info("parsing %s"%strProjBackersFilePath)
            with open(strProjBackersFilePath, "r") as projBackersHtmlFile:
                strProjHtmlFileName = os.path.basename(projBackersHtmlFile.name)
                strProjUrl = "https://www.indiegogo.com/projects/" + re.search("^(.*)_backers.html$", strProjHtmlFileName).group(1)
                if not self.checkIsProjUrlInProjUrlListFile(strCategoryName=strCategoryName, strProjUrl=strProjUrl):
                    logging.warning("%s not in project_url_list.txt, skip parse it"%strProjUrl)
                    continue #skip
                if strProjUrl not in self.dicParsedResultOfProject:
                    self.dicParsedResultOfProject[strProjUrl] = {}
                strPageSource = projBackersHtmlFile.read()
                root = Selector(text=strPageSource)
                #parse *_backers.html
                #lstStrBacker
                lstStrBacker = root.css("div.i-funder-row div.i-name-col div.i-name div.i-details-name::text,a.i-details-name::text").extract()
                self.dicParsedResultOfProject[strProjUrl]["lstStrBacker"] = lstStrBacker
                
    #解析 _story.html (INDIEGOGO 的 reward 資料置於 _story.html)
    def parseProjectRewardPage(self, strCategoryName=None):
        strProjectsHtmlFolderPath = self.SOURCE_HTML_BASE_FOLDER_PATH + (u"\\INDIEGOGO\\%s\\projects"%strCategoryName)
        lstStrStoryHtmlFilePath = self.utility.getFilePathListWithSuffixes(strBasedir=strProjectsHtmlFolderPath, strSuffixes="_story.html")
        for strProjStoryFilePath in lstStrStoryHtmlFilePath:
            logging.info("parsing %s"%strProjStoryFilePath)
            with open(strProjStoryFilePath, "r") as projStoryHtmlFile:
                strProjHtmlFileName = os.path.basename(projStoryHtmlFile.name)
                strProjUrl = "https://www.indiegogo.com/projects/" + re.search("^(.*)_story.html$", strProjHtmlFileName).group(1)
                if not self.checkIsProjUrlInProjUrlListFile(strCategoryName=strCategoryName, strProjUrl=strProjUrl):
                    logging.warning("%s not in project_url_list.txt, skip parse it"%strProjUrl)
                    continue #skip
                strPageSource = projStoryHtmlFile.read()
                root = Selector(text=strPageSource)
                #parse *_story.html (for reward data)
                lstDicRewardData = []
                #loop of append reward data to lstDicRewardData
                for elementReward in root.css("div.perkItem-campaignPerkContainer"):
                    dicRewardData = {}
                    #strUrl
                    dicRewardData["strUrl"] = strProjUrl
                    #strRewardContent
                    strPerkTitleText = elementReward.css("perk-title div.perkItem-title::text").extract_first().strip()
                    strPerkDescriptionText = elementReward.css("perk-description div.perkItem-description::text").extract_first().strip()
                    strRewardContent = strPerkTitleText + "\n" + strPerkDescriptionText
                    dicRewardData["strRewardContent"] = strRewardContent
                    #intRewardMoney
                    strPerkAmountText = elementReward.css("amount-with-currency span.perkItem-perkAmount::text").extract_first().strip()
                    dicRewardData["intRewardMoney"] = \
                        int(re.sub("[^0-9]", "", strPerkAmountText))
                    #intRewardBacker and intRewardLimit
                    elementAvailability = elementReward.css("span.availability")
                    #intRewardBacker
                    dicRewardData["intRewardBacker"] = \
                        int(elementAvailability.css("b:nth-of-type(1)::text").extract_first().strip())
                    #intRewardLimit
                    intRewardLimit = 0
                    if len(elementAvailability.css("b").extract()) == 2:
                        intRewardLimit = int(elementAvailability.css("b:nth-of-type(2)::text").extract_first().strip())
                    dicRewardData["intRewardLimit"] = intRewardLimit
                    #strRewardShipTo
                    strShipsToLabelText = elementReward.css("ships-to-countries span.shipsTo-label::text").extract_first()
                    lstStrShipsToValueText = elementReward.css("ships-to-countries span.shipsTo-value::text").extract()
                    strRewardShipTo = None
                    if lstStrShipsToValueText: #is not None
                        strRewardShipTo = u""
                        for strShipsToValueText in lstStrShipsToValueText:
                            strRewardShipTo = strRewardShipTo + strShipsToValueText.strip()
                    elif strShipsToLabelText: #is not None
                        strRewardShipTo = re.search("^Ships (.*)$", strShipsToLabelText.strip()).group(1)
                    else:
                        strRewardShipTo = None
                    dicRewardData["strRewardShipTo"] = strRewardShipTo
                    #strRewardDeliveryDate
                    strRewardDeliveryDate = None
                    lstStrEstimateDeliveryText = elementReward.css("perk-description div[ng-if*=estimated_delivery_date] span::text").extract()
                    if len(lstStrEstimateDeliveryText) == 2 and lstStrEstimateDeliveryText[0].strip() == "Estimated delivery:":
                        strRewardDeliveryDate = lstStrEstimateDeliveryText[1].strip()
                        strRewardDeliveryDate = self.utility.parseStrDateByDateparser(strOriginDate=strRewardDeliveryDate)
                        if strRewardDeliveryDate: # is not None
                            #強制設定為 每月 1 號 ex 2016-05-20 -> 2016-05-01
                            lstStrRewardDeliveryDate = list(strRewardDeliveryDate)
                            lstStrRewardDeliveryDate[-1] = "1"
                            lstStrRewardDeliveryDate[-2] = "0"
                            strRewardDeliveryDate = "".join(lstStrRewardDeliveryDate)
                    dicRewardData["strRewardDeliveryDate"] = strRewardDeliveryDate
                    #intRewardRetailPrice 零售價出現格式不統一難以取得
                    dicRewardData["intRewardRetailPrice"] = None
                    lstDicRewardData.append(dicRewardData)
                self.dicParsedResultOfReward[strProjUrl] = lstDicRewardData
                
    #解析 _gallery.html (暫無用處，備用)
    def parseProjectGalleryPage(self, strCategoryName=None):
        pass
#individuals #####################################################################################
    #解析 individuals page(s) 之前
    def beforeParseIndividualsPage(self, strCategoryName=None):
        self.dicParsedResultOfProfile = {} #profile.json 資料
        strIndividualsResultFolderPath = self.PARSED_RESULT_BASE_FOLDER_PATH + (u"\\INDIEGOGO\\%s\\profiles"%strCategoryName)
        if not os.path.exists(strIndividualsResultFolderPath):
            #mkdir parsed_result/INDIEGOGO/category/profiles/
            os.mkdir(strIndividualsResultFolderPath) 
            
    #解析 individuals page(s) 之後
    def afterParseIndividualsPage(self, strCategoryName=None):
        strIndividualsResultFolderPath = self.PARSED_RESULT_BASE_FOLDER_PATH + (u"\\INDIEGOGO\\%s\\profiles"%strCategoryName)
        #將 parse 結果寫入 json 檔案
        self.utility.writeObjectToJsonFile(self.dicParsedResultOfProfile, strIndividualsResultFolderPath + u"\\profile.json")
        
    #解析 _profile.html
    def parseIndividualsProfilePage(self, strCategoryName=None):
        strIndividualsHtmlFolderPath = self.SOURCE_HTML_BASE_FOLDER_PATH + (u"\\INDIEGOGO\\%s\\profiles"%strCategoryName)
        lstStrProfileHtmlFilePath = self.utility.getFilePathListWithSuffixes(strBasedir=strIndividualsHtmlFolderPath, strSuffixes="_profile.html")
        for strIndividualsProfileFilePath in lstStrProfileHtmlFilePath:
            logging.info("parsing %s"%strIndividualsProfileFilePath)
            with open(strIndividualsProfileFilePath, "r") as individualsProfileHtmlFile:
                strIndividualsHtmlFileName = os.path.basename(individualsProfileHtmlFile.name)
                strIndividualsUrl = "https://www.indiegogo.com/individuals/" + re.search("^(.*)_profile.html$", strIndividualsHtmlFileName).group(1)
                if strIndividualsUrl not in self.dicParsedResultOfProfile:
                    self.dicParsedResultOfProfile[strIndividualsUrl] = {}
                strPageSource = individualsProfileHtmlFile.read()
                root = Selector(text=strPageSource)
                #parse *_profile.html
                #strUrl
                self.dicParsedResultOfProfile[strIndividualsUrl]["strUrl"] = \
                    strIndividualsUrl
                #strName
                strName = root.css("h1.i-profileHeader-accountName::text").extract_first().strip()
                self.dicParsedResultOfProfile[strIndividualsUrl]["strName"] = \
                    strName
                #strDescription
                self.dicParsedResultOfProfile[strIndividualsUrl]["strDescription"] = \
                    root.css("div.i-profile-show-content p.i-description::text").extract_first().strip()
                #strLocation
                strLocationSpanText = root.css("div.i-profileHeader-location span::text").extract_first()
                strLocation = strLocationSpanText
                self.dicParsedResultOfProfile[strIndividualsUrl]["strLocation"] = \
                    strLocation
                #strCountry and strCity
                strCountry = None
                strCity = None
                if strLocationSpanText != None:
                    lstStrLocationPart = strLocationSpanText.split(",")
                    if len(lstStrLocationPart) > 1 :
                        strCountry = lstStrLocationPart[-1].strip()
                        strCity = lstStrLocationPart[0].strip()
                    elif len(lstStrLocationPart) == 1:
                        strCountry = lstStrLocationPart[0].strip()
                self.dicParsedResultOfProfile[strIndividualsUrl]["strCountry"] = \
                    self.utility.getCountryCode(strCountry)
                self.dicParsedResultOfProfile[strIndividualsUrl]["strCity"] = \
                    strCity
                #strContinent
                self.dicParsedResultOfProfile[strIndividualsUrl]["strContinent"] = \
                    self.utility.getContinentByCountryNameWikiVersion(strCountry)
                #intBackedCount and intCreatedCount
                lstStrStatsEmText = root.css("ul.i-stats li em::text").extract()
                intCreatedCount = 0
                intBackedCount = 0
                if len(lstStrStatsEmText) == 3:
                    intCreatedCount = int(lstStrStatsEmText[0].strip())
                    intBackedCount = int(lstStrStatsEmText[2].strip())
                self.dicParsedResultOfProfile[strIndividualsUrl]["intCreatedCount"] = \
                    intCreatedCount
                self.dicParsedResultOfProfile[strIndividualsUrl]["intBackedCount"] = \
                    intBackedCount
                #isCreator
                isCreator = False
                if intCreatedCount > 0:
                    isCreator = True
                self.dicParsedResultOfProfile[strIndividualsUrl]["isCreator"] = isCreator
                #isBacker
                isBacker = False
                if intBackedCount > 0:
                    isBacker = True
                self.dicParsedResultOfProfile[strIndividualsUrl]["isBacker"] = isBacker
                #strIdentityName (同 strName)
                self.dicParsedResultOfProfile[strIndividualsUrl]["strIdentityName"] = \
                    strName
                #intFbFriend
                intFbFriend = 0
                lstStrVerificationSpanText = root.css("div.i-verifications div.profileVerification span::text").extract()
                for strVerificationSpanText in lstStrVerificationSpanText:
                    if "friends" in strVerificationSpanText:
                        strVerificationSpanText = re.sub("[^0-9]", "", strVerificationSpanText)
                        intFbFriend = int(strVerificationSpanText)
                self.dicParsedResultOfProfile[strIndividualsUrl]["intFbFriend"] = intFbFriend
                #intLiveProject 無法取得
                self.dicParsedResultOfProfile[strIndividualsUrl]["intLiveProject"] = None
                #intSuccessProject 無法取得
                self.dicParsedResultOfProfile[strIndividualsUrl]["intSuccessProject"] = None
                #intFailedProject 無法取得
                self.dicParsedResultOfProfile[strIndividualsUrl]["intFailedProject"] = None
        
    #解析 _campaigns.html
    def parseIndividualsCampaignsPage(self, strCategoryName=None):
        strIndividualsHtmlFolderPath = self.SOURCE_HTML_BASE_FOLDER_PATH + (u"\\INDIEGOGO\\%s\\profiles"%strCategoryName)
        lstStrCampaignsHtmlFilePath = self.utility.getFilePathListWithSuffixes(strBasedir=strIndividualsHtmlFolderPath, strSuffixes="_campaigns.html")
        for strIndividualsCampaignFilePath in lstStrCampaignsHtmlFilePath:
            logging.info("parsing %s"%strIndividualsCampaignFilePath)
            with open(strIndividualsCampaignFilePath, "r") as individualsCampaignHtmlFile:
                strIndividualsHtmlFileName = os.path.basename(individualsCampaignHtmlFile.name)
                strIndividualsUrl = "https://www.indiegogo.com/individuals/" + re.search("^(.*)_campaigns.html$", strIndividualsHtmlFileName).group(1)
                if strIndividualsUrl not in self.dicParsedResultOfProfile:
                    self.dicParsedResultOfProfile[strIndividualsUrl] = {}
                strPageSource = individualsCampaignHtmlFile.read()
                root = Selector(text=strPageSource)
                #parse *_campaigns.html
                #lstStrCreatedProject and lstStrCreatedProjectUrl
                elementCreatedProj = root.css("div.i-profile-container div.i-profile-campaigns-section:nth-of-type(1)")
                lstStrCreatedProject = elementCreatedProj.css("ul li.i-profile-list-item-campaigns_on div.i-campaign a::text").extract()
                lstStrCreatedProjectUrl = elementCreatedProj.css("ul li.i-profile-list-item-campaigns_on div.i-campaign a::attr(href)").extract()
                self.dicParsedResultOfProfile[strIndividualsUrl]["lstStrCreatedProject"] = \
                    lstStrCreatedProject
                self.dicParsedResultOfProfile[strIndividualsUrl]["lstStrCreatedProjectUrl"] = \
                    lstStrCreatedProjectUrl
                #lstStrBackedProject and lstStrBackedProjectUrl
                elementBackedProj = root.css("div.i-profile-container div.i-profile-campaigns-section:nth-of-type(2)")
                lstStrBackedProject = elementBackedProj.css("ul li.i-profile-list-item-campaigns_funded div.i-campaign a::text").extract()
                lstStrBackedProjectUrl = elementBackedProj.css("ul li.i-profile-list-item-campaigns_funded div.i-campaign a::attr(href)").extract()
                self.dicParsedResultOfProfile[strIndividualsUrl]["lstStrBackedProject"] = \
                    lstStrBackedProject
                self.dicParsedResultOfProfile[strIndividualsUrl]["lstStrBackedProjectUrl"] = \
                    lstStrBackedProjectUrl
                    