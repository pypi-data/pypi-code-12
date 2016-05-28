# -*- coding: utf-8 -*-
"""
Copyright (C) 2015, MuChu Hsu
Contributed by Muchu Hsu (muchu1983@gmail.com)
This file is part of BSD license

<https://opensource.org/licenses/BSD-3-Clause>
"""
from subprocess import call
"""
以 shell script 執行 sikuli
從 parsed_resul 取得資訊
透過 sikuli 將 HTML 抓取到 source_html 下
"""
class SpiderForINDIEGOGO:
    
    #建構子
    def __init__(self):
        self.dicSubCommandHandler = {"explore":self.handleExplorePage,
                                     "category":self.handleCategoryPage,
                                     "project":self.handleProjectPage,
                                     "individuals":self.handleIndividualsPage,}
    
    #下載及解析 explore 頁面
    def handleExplorePage(self, arg1=None):
        #download html
        call([r"cameo_sikuli\runsikulix.cmd", "-c",
              r"-r", r"cameo_sikuli\spiderForINDIEGOGO.sikuli",
              r"--args", r"explore"])
    
    #下載及解析 category 頁面
    def handleCategoryPage(self, arg1=None):
        call([r"cameo_sikuli\runsikulix.cmd", "-c",
              r"-r", r"cameo_sikuli\spiderForINDIEGOGO.sikuli",
              r"--args", r"category"])

    #下載及解析 project 頁面
    def handleProjectPage(self, arg1=None):
        call([r"cameo_sikuli\runsikulix.cmd", "-c",
              r"-r", r"cameo_sikuli\spiderForINDIEGOGO.sikuli",
              r"--args", r"project", arg1])

    #下載及解析 individuals 頁面
    def handleIndividualsPage(self, arg1=None):
        call([r"cameo_sikuli\runsikulix.cmd", "-c",
              r"-r", r"cameo_sikuli\spiderForINDIEGOGO.sikuli",
              r"--args", r"individuals", arg1])
              
    #取得 spider 使用資訊
    def getUseageMessage(self):
        return ("- INDIEGOGO -\n"
                "useage:\n"
                "explore - download explore.html\n"
                "category - download category.html\n"
                "project category - download project's pages of given category, if category==automode means all category\n"
                "individuals category - download individuals's pages of given category, if category==automode means all category\n")
                
    #執行 spider
    def runSpider(self, lstSubcommand=None):
        strSubcommand = lstSubcommand[0]
        strArg1 = None
        if len(lstSubcommand) == 2:
            strArg1 = lstSubcommand[1]
        self.dicSubCommandHandler[strSubcommand](strArg1)