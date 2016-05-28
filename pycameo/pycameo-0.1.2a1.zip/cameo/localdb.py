# -*- coding: utf-8 -*-
"""
Copyright (C) 2015, MuChu Hsu
Contributed by Muchu Hsu (muchu1983@gmail.com)
This file is part of BSD license

<https://opensource.org/licenses/BSD-3-Clause>
"""
from bennu.localdb import SQLite3Db
from bennu.localdb import MongoDb
"""
本地端資料庫存取
"""
#匯率API
class LocalDbForCurrencyApi:
    
    #建構子
    def __init__(self):
        self.mongodb = MongoDb().getClient().localdb
        
#投資界
class LocalDbForPEDAILY:
    
    #建構子
    def __init__(self):
        self.db = SQLite3Db(strResFolderPath="cameo_res")
        self.initialDb()
        
    #初取化資料庫
    def initialDb(self):
        strSQLCreateTable = ("CREATE TABLE IF NOT EXISTS pedaily_news("
                             "id INTEGER PRIMARY KEY,"
                             "strNewsUrl TEXT NOT NULL,"
                             "intCategoryId INTEGER NOT NULL,"
                             "isGot BOOLEAN NOT NULL)")
        self.db.commitSQL(strSQL=strSQLCreateTable)
        strSQLCreateTable = ("CREATE TABLE IF NOT EXISTS pedaily_category("
                             "id INTEGER PRIMARY KEY,"
                             "strCategoryName TEXT NOT NULL,"
                             "isGot BOOLEAN NOT NULL)")
        self.db.commitSQL(strSQL=strSQLCreateTable)
        
    #若無重覆，儲存 category
    def insertCategoryIfNotExists(self, strCategoryName=None):
        strSQL = "SELECT * FROM pedaily_category WHERE strCategoryName='%s'"%strCategoryName
        lstRowData = self.db.fetchallSQL(strSQL=strSQL)
        if len(lstRowData) == 0:
            strSQL = "INSERT INTO pedaily_category VALUES(NULL, '%s', 0)"%strCategoryName
            self.db.commitSQL(strSQL=strSQL)
        
    #取得所有 category 名稱
    def fetchallCategoryName(self, isGot=False):
        dicIsGotCode = {True:"1", False:"0"}
        strSQL = "SELECT strCategoryName FROM pedaily_category WHERE isGot=%s"%dicIsGotCode[isGot]
        lstRowData = self.db.fetchallSQL(strSQL=strSQL)
        lstStrCategoryName = []
        for rowData in lstRowData:
            lstStrCategoryName.append(rowData["strCategoryName"])
        return lstStrCategoryName
        
    #取得所有未完成下載的 category 名稱
    def fetchallNotObtainedCategoryName(self):
        return self.fetchallCategoryName(isGot=False)
        
    #取得所有已完成下載的 category 名稱
    def fetchallCompletedObtainedCategoryName(self):
        return self.fetchallCategoryName(isGot=True)
        
    #更新 category 為已完成下載狀態
    def updateCategoryStatusIsGot(self, strCategoryName=None):
        strSQL = "UPDATE pedaily_category SET isGot=1 WHERE strCategoryName='%s'"%strCategoryName
        self.db.commitSQL(strSQL=strSQL)
        
    #取得 category id
    def fetchCategoryIdByName(self, strCategoryName=None):
        strSQL = "SELECT * FROM pedaily_category WHERE strCategoryName='%s'"%strCategoryName
        lstRowData = self.db.fetchallSQL(strSQL=strSQL)
        return lstRowData[0]["id"]
        
    #若無重覆 儲存 news URL
    def insertNewsUrlIfNotExists(self, strNewsUrl=None, strCategoryName=None):
        intCategoryId = self.fetchCategoryIdByName(strCategoryName=strCategoryName)
        #insert news url if not exists
        strSQL = "SELECT * FROM pedaily_news WHERE strNewsUrl='%s'"%strNewsUrl
        lstRowData = self.db.fetchallSQL(strSQL=strSQL)
        if len(lstRowData) == 0:
            strSQL = "INSERT INTO pedaily_news VALUES(NULL, '%s', %d,0)"%(strNewsUrl, intCategoryId)
            self.db.commitSQL(strSQL=strSQL)
        
    #取得指定 category 的 news url
    def fetchallNewsUrlByCategoryName(self, strCategoryName=None):
        intCategoryId = self.fetchCategoryIdByName(strCategoryName=strCategoryName)
        strSQL = "SELECT * FROM pedaily_news WHERE intCategoryId=%d"%intCategoryId
        lstRowData = self.db.fetchallSQL(strSQL=strSQL)
        lstStrNewsUrl = []
        for rowData in lstRowData:
            lstStrNewsUrl.append(rowData["strNewsUrl"])
        return lstStrNewsUrl
        
    #檢查 news 是否已下載
    def checkNewsIsGot(self, strNewsUrl=None):
        isGot = True
        strSQL = "SELECT * FROM pedaily_news WHERE strNewsUrl='%s'"%strNewsUrl
        lstRowData = self.db.fetchallSQL(strSQL=strSQL)
        for rowData in lstRowData:
            if rowData["isGot"] == 0:
                isGot = False
        return isGot
        
    #更新 news 為已完成下載狀態
    def updateNewsStatusIsGot(self, strNewsUrl=None):
        strSQL = "UPDATE pedaily_news SET isGot=1 WHERE strNewsUrl='%s'"%strNewsUrl
        self.db.commitSQL(strSQL=strSQL)
        
    #取得所有已完成下載的 news url
    def fetchallCompletedObtainedNewsUrl(self):
        strSQL = "SELECT strNewsUrl FROM pedaily_news WHERE isGot=1"
        lstRowData = self.db.fetchallSQL(strSQL=strSQL)
        lstStrNewsUrl = []
        for rowData in lstRowData:
            lstStrNewsUrl.append(rowData["strNewsUrl"])
        return lstStrNewsUrl
        
    #更新 news 尚未開始下載狀態
    def updateNewsStatusIsNotGot(self, strNewsUrl=None):
        strSQL = "UPDATE pedaily_news SET isGot=0 WHERE strNewsUrl='%s'"%strNewsUrl
        self.db.commitSQL(strSQL=strSQL)
        
    #清除測試資料 (clear table)
    def clearTestData(self):
        strSQL = "DELETE FROM pedaily_news"
        self.db.commitSQL(strSQL=strSQL)
        strSQL = "DELETE FROM pedaily_category"
        self.db.commitSQL(strSQL=strSQL)
        
#數位時代
class LocalDbForBNEXT:
    
    #建構子
    def __init__(self):
        self.db = SQLite3Db(strResFolderPath="cameo_res")
        self.initialDb()
        
    #初取化資料庫
    def initialDb(self):
        strSQLCreateTable = ("CREATE TABLE IF NOT EXISTS bnext_news("
                             "id INTEGER PRIMARY KEY,"
                             "strNewsUrl TEXT NOT NULL,"
                             "isGot BOOLEAN NOT NULL)")
        self.db.commitSQL(strSQL=strSQLCreateTable)
        strSQLCreateTable = ("CREATE TABLE IF NOT EXISTS bnext_tag("
                             "id INTEGER PRIMARY KEY,"
                             "strTagName TEXT NOT NULL,"
                             "isGot BOOLEAN NOT NULL)")
        self.db.commitSQL(strSQL=strSQLCreateTable)
        strSQLCreateTable = ("CREATE TABLE IF NOT EXISTS bnext_newstag("
                             "id INTEGER PRIMARY KEY,"
                             "strNewsUrl TEXT NOT NULL,"
                             "strTagName TEXT NOT NULL)")
        self.db.commitSQL(strSQL=strSQLCreateTable)
        
    #若無重覆，儲存Tag
    def insertTagIfNotExists(self, strTagName=None):
        strSQL = "SELECT * FROM bnext_tag WHERE strTagName='%s'"%strTagName
        lstRowData = self.db.fetchallSQL(strSQL=strSQL)
        if len(lstRowData) == 0:
            strSQL = "INSERT INTO bnext_tag VALUES(NULL, '%s', 0)"%strTagName
            self.db.commitSQL(strSQL=strSQL)
            
    #取得所有未完成下載的 Tag 名稱
    def fetchallNotObtainedTagName(self):
        strSQL = "SELECT strTagName FROM bnext_tag WHERE isGot=0"
        lstRowData = self.db.fetchallSQL(strSQL=strSQL)
        lstStrTagName = []
        for rowData in lstRowData:
            lstStrTagName.append(rowData["strTagName"])
        return lstStrTagName
        
    #取得所有已完成下載的 Tag 名稱
    def fetchallCompletedObtainedTagName(self):
        strSQL = "SELECT strTagName FROM bnext_tag WHERE isGot=1"
        lstRowData = self.db.fetchallSQL(strSQL=strSQL)
        lstStrTagName = []
        for rowData in lstRowData:
            lstStrTagName.append(rowData["strTagName"])
        return lstStrTagName
        
    #更新 Tag 為已完成下載狀態
    def updateTagStatusIsGot(self, strTagName=None):
        strSQL = "UPDATE bnext_tag SET isGot=1 WHERE strTagName='%s'"%strTagName
        self.db.commitSQL(strSQL=strSQL)
        
    #儲存 news URL 以及 URL 所對應的 tag 
    def insertNewsUrlAndNewsTagMappingIfNotExists(self, strNewsUrl=None, strTagName=None):
        #insert news url if not exists
        strSQL = "SELECT * FROM bnext_news WHERE strNewsUrl='%s'"%strNewsUrl
        lstRowData = self.db.fetchallSQL(strSQL=strSQL)
        if len(lstRowData) == 0:
            strSQL = "INSERT INTO bnext_news VALUES(NULL, '%s', 0)"%strNewsUrl
            self.db.commitSQL(strSQL=strSQL)
        #insert news tag mapping if not exists
        strSQL = "SELECT * FROM bnext_newstag WHERE strNewsUrl='%s' AND strTagName='%s'"%(strNewsUrl, strTagName)
        lstRowData = self.db.fetchallSQL(strSQL=strSQL)
        if len(lstRowData) == 0:
            strSQL = "INSERT INTO bnext_newstag VALUES(NULL, '%s', '%s')"%(strNewsUrl, strTagName)
            self.db.commitSQL(strSQL=strSQL)
        
    #取得指定 tag 的 news url
    def fetchallNewsUrlByTagName(self, strTagName=None):
        strSQL = "SELECT * FROM bnext_newstag WHERE strTagName='%s'"%strTagName
        lstRowData = self.db.fetchallSQL(strSQL=strSQL)
        lstStrNewsUrl = []
        for rowData in lstRowData:
            lstStrNewsUrl.append(rowData["strNewsUrl"])
        return lstStrNewsUrl
        
    #檢查 news 是否已下載
    def checkNewsIsGot(self, strNewsUrl=None):
        isGot = True
        strSQL = "SELECT * FROM bnext_news WHERE strNewsUrl='%s'"%strNewsUrl
        lstRowData = self.db.fetchallSQL(strSQL=strSQL)
        for rowData in lstRowData:
            if rowData["isGot"] == 0:
                isGot = False
        return isGot
        
    #更新 news 為已完成下載狀態
    def updateNewsStatusIsGot(self, strNewsUrl=None):
        strSQL = "UPDATE bnext_news SET isGot=1 WHERE strNewsUrl='%s'"%strNewsUrl
        self.db.commitSQL(strSQL=strSQL)
        
    #清除測試資料 (clear table)
    def clearTestData(self):
        strSQL = "DELETE FROM bnext_news"
        self.db.commitSQL(strSQL=strSQL)
        strSQL = "DELETE FROM bnext_tag"
        self.db.commitSQL(strSQL=strSQL)
        strSQL = "DELETE FROM bnext_newstag"
        self.db.commitSQL(strSQL=strSQL)

#科技報橘
class LocalDbForTECHORANGE:
    
    #建構子
    def __init__(self):
        self.db = SQLite3Db(strResFolderPath="cameo_res")
        self.initialDb()
        
    #初取化資料庫
    def initialDb(self):
        strSQLCreateTable = ("CREATE TABLE IF NOT EXISTS techorange_news("
                             "id INTEGER PRIMARY KEY,"
                             "strNewsUrl TEXT NOT NULL,"
                             "isGot BOOLEAN NOT NULL)")
        self.db.commitSQL(strSQL=strSQLCreateTable)
        strSQLCreateTable = ("CREATE TABLE IF NOT EXISTS techorange_tag("
                             "id INTEGER PRIMARY KEY,"
                             "strTagName TEXT NOT NULL,"
                             "isGot BOOLEAN NOT NULL)")
        self.db.commitSQL(strSQL=strSQLCreateTable)
        strSQLCreateTable = ("CREATE TABLE IF NOT EXISTS techorange_newstag("
                             "id INTEGER PRIMARY KEY,"
                             "strNewsUrl TEXT NOT NULL,"
                             "strTagName TEXT NOT NULL)")
        self.db.commitSQL(strSQL=strSQLCreateTable)
        
    #若無重覆，儲存Tag
    def insertTagIfNotExists(self, strTagName=None):
        strSQL = "SELECT * FROM techorange_tag WHERE strTagName='%s'"%strTagName
        lstRowData = self.db.fetchallSQL(strSQL=strSQL)
        if len(lstRowData) == 0:
            strSQL = "INSERT INTO techorange_tag VALUES(NULL, '%s', 0)"%strTagName
            self.db.commitSQL(strSQL=strSQL)
            
    #取得所有未完成下載的 Tag 名稱
    def fetchallNotObtainedTagName(self):
        strSQL = "SELECT strTagName FROM techorange_tag WHERE isGot=0"
        lstRowData = self.db.fetchallSQL(strSQL=strSQL)
        lstStrTagName = []
        for rowData in lstRowData:
            lstStrTagName.append(rowData["strTagName"])
        return lstStrTagName
        
    #取得所有已完成下載的 Tag 名稱
    def fetchallCompletedObtainedTagName(self):
        strSQL = "SELECT strTagName FROM techorange_tag WHERE isGot=1"
        lstRowData = self.db.fetchallSQL(strSQL=strSQL)
        lstStrTagName = []
        for rowData in lstRowData:
            lstStrTagName.append(rowData["strTagName"])
        return lstStrTagName
        
    #更新 Tag 為已完成下載狀態
    def updateTagStatusIsGot(self, strTagName=None):
        strSQL = "UPDATE techorange_tag SET isGot=1 WHERE strTagName='%s'"%strTagName
        self.db.commitSQL(strSQL=strSQL)
        
    #儲存 news URL 以及 URL 所對應的 tag 
    def insertNewsUrlAndNewsTagMappingIfNotExists(self, strNewsUrl=None, strTagName=None):
        #insert news url if not exists
        strSQL = "SELECT * FROM techorange_news WHERE strNewsUrl='%s'"%strNewsUrl
        lstRowData = self.db.fetchallSQL(strSQL=strSQL)
        if len(lstRowData) == 0:
            strSQL = "INSERT INTO techorange_news VALUES(NULL, '%s', 0)"%strNewsUrl
            self.db.commitSQL(strSQL=strSQL)
        #insert news tag mapping if not exists
        strSQL = "SELECT * FROM techorange_newstag WHERE strNewsUrl='%s' AND strTagName='%s'"%(strNewsUrl, strTagName)
        lstRowData = self.db.fetchallSQL(strSQL=strSQL)
        if len(lstRowData) == 0:
            strSQL = "INSERT INTO techorange_newstag VALUES(NULL, '%s', '%s')"%(strNewsUrl, strTagName)
            self.db.commitSQL(strSQL=strSQL)
        
    #取得指定 tag 的 news url
    def fetchallNewsUrlByTagName(self, strTagName=None):
        strSQL = "SELECT * FROM techorange_newstag WHERE strTagName='%s'"%strTagName
        lstRowData = self.db.fetchallSQL(strSQL=strSQL)
        lstStrNewsUrl = []
        for rowData in lstRowData:
            lstStrNewsUrl.append(rowData["strNewsUrl"])
        return lstStrNewsUrl
        
    #檢查 news 是否已下載
    def checkNewsIsGot(self, strNewsUrl=None):
        isGot = True
        strSQL = "SELECT * FROM techorange_news WHERE strNewsUrl='%s'"%strNewsUrl
        lstRowData = self.db.fetchallSQL(strSQL=strSQL)
        for rowData in lstRowData:
            if rowData["isGot"] == 0:
                isGot = False
        return isGot
        
    #更新 news 為已完成下載狀態
    def updateNewsStatusIsGot(self, strNewsUrl=None):
        strSQL = "UPDATE techorange_news SET isGot=1 WHERE strNewsUrl='%s'"%strNewsUrl
        self.db.commitSQL(strSQL=strSQL)
        
    #更新 news 為未完成下載狀態 (指定 部分 url )
    def updateNewsStatusIsNotGot(self, strNewsUrlPart=None):
        strSQL = "UPDATE techorange_news SET isGot=0 WHERE strNewsUrl LIKE'%" + strNewsUrlPart + "%'"
        self.db.commitSQL(strSQL=strSQL)
        
    #清除測試資料 (clear table)
    def clearTestData(self):
        strSQL = "DELETE FROM techorange_news"
        self.db.commitSQL(strSQL=strSQL)
        strSQL = "DELETE FROM techorange_tag"
        self.db.commitSQL(strSQL=strSQL)
        strSQL = "DELETE FROM techorange_newstag"
        self.db.commitSQL(strSQL=strSQL)