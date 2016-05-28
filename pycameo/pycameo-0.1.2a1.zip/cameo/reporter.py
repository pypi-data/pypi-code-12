# -*- coding: utf-8 -*-
"""
Copyright (C) 2015, MuChu Hsu
Contributed by Muchu Hsu (muchu1983@gmail.com)
This file is part of BSD license

<https://opensource.org/licenses/BSD-3-Clause>
"""
import os
from cameo.utility import Utility
"""
INDIEGOGO 分析報告
"""
class ReporterForINDIEGOGO:
    
    #建構子
    def __init__(self):
        self.strSourceBasedir = u"cameo_res\\source_html\\INDIEGOGO"
        self.strResultBasedir = u"cameo_res\\parsed_result\\INDIEGOGO"
        self.utility = Utility()
        
    #取得報表結果
    def getReportMessage(self):
        intDownloadedProject = self.CountDownloadedProject()
        intParsedProject = self.CountParsedProject()
        strReportMsg = (u"- INDIEGOGO -\n" +
                        u"downloaded:\n" +
                        str(intDownloadedProject) + u"\n"
                        u"parsed:\n" + 
                        str(intParsedProject) + u"\n")
        return strReportMsg
    
    #計算已下載的專案數量
    def CountDownloadedProject(self):
        #find _story.html file path
        lstStrStoryHtmlFilePath = self.utility.recursiveGetFilePathListWithSuffixes(strBasedir=self.strSourceBasedir, strSuffixes="_story.html")
        return len(lstStrStoryHtmlFilePath)
        
    #計算已解析的專案數量
    def CountParsedProject(self):
        #find project.json file path
        lstStrProjectJsonFilePath = self.utility.recursiveGetFilePathListWithSuffixes(strBasedir=self.strResultBasedir, strSuffixes="project.json")
        #read project.json file and count keys
        intParsedProject = 0
        for strProjectJsonFilePath in lstStrProjectJsonFilePath:
            dicProject =  self.utility.readObjectFromJsonFile(strJsonFilePath=strProjectJsonFilePath)
            intParsedProject = intParsedProject + len(dicProject)
        return intParsedProject

"""
WEBACKERS 分析報告
"""
class ReporterForWEBACKERS:
    
    #建構子
    def __init__(self):
        self.strSourceBasedir = "cameo_res\\source_html\\WEBACKERS"
        self.strResultBasedir = "cameo_res\\parsed_result\\WEBACKERS"
        self.utility = Utility()
        
    #取得報表結果
    def getReportMessage(self):
        intDownloadedProject = self.CountDownloadedProject()
        intParsedProject = self.CountParsedProject()
        strReportMsg = (u"- WEBACKERS -\n" +
                        u"downloaded:\n" +
                        str(intDownloadedProject) + u"\n"
                        u"parsed:\n" + 
                        str(intParsedProject) + u"\n")
        return strReportMsg
    
    #計算已下載的專案數量
    def CountDownloadedProject(self):
        #find _intro.html file path
        lstStrIntroHtmlFilePath = self.utility.recursiveGetFilePathListWithSuffixes(strBasedir=self.strSourceBasedir, strSuffixes="_intro.html")
        return len(lstStrIntroHtmlFilePath)
        
    #計算已解析的專案數量
    def CountParsedProject(self):
        #find project.json file path
        lstStrProjectJsonFilePath = self.utility.recursiveGetFilePathListWithSuffixes(strBasedir=self.strResultBasedir, strSuffixes="project.json")
        #read project.json file and count keys
        intParsedProject = 0
        for strProjectJsonFilePath in lstStrProjectJsonFilePath:
            dicProject =  self.utility.readObjectFromJsonFile(strJsonFilePath=strProjectJsonFilePath)
            intParsedProject = intParsedProject + len(dicProject)
        return intParsedProject
    