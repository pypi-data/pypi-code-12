# -*- coding: utf-8 -*-
"""
Copyright (C) 2015, MuChu Hsu
Contributed by Muchu Hsu (muchu1983@gmail.com)
This file is part of BSD license

<https://opensource.org/licenses/BSD-3-Clause>
"""
from bennu.localdb import SQLite3Db
"""
本地端資料庫存取
"""
class LocalDbForStoryChain:
    
    #建構子
    def __init__(self):
        self.db = SQLite3Db(strResFolderPath="story_chain_res")
        self.initialDb()
        
    #初取化資料庫
    def initialDb(self):
        strSQLCreateTable = ("CREATE TABLE IF NOT EXISTS story_chain_story("
                             "intId INTEGER PRIMARY KEY,"
                             "strContent TEXT NOT NULL,"
                             "intLike INTEGER NOT NULL,"
                             "intDislike INTEGER NOT NULL)")
        self.db.commitSQL(strSQL=strSQLCreateTable)
        strSQLCreateTable = ("CREATE TABLE IF NOT EXISTS story_chain_chain("
                             "intId INTEGER PRIMARY KEY,"
                             "intStoryId INTEGER NOT NULL,"
                             "intPrevId INTEGER NOT NULL)")
        self.db.commitSQL(strSQL=strSQLCreateTable)
        strSQLCreateTable = ("CREATE TABLE IF NOT EXISTS story_chain_tag("
                             "id INTEGER PRIMARY KEY,"
                             "strTagName TEXT NOT NULL,"
                             "intStoryId INTEGER NOT NULL,"
                             "numTimeLimit DATE NOT NULL)")
        self.db.commitSQL(strSQL=strSQLCreateTable)
        
    #新增故事段落
    def insertNewStory(self, strContent=None, intPrevId=0):
        strSQL = "INSERT INTO story_chain_story VALUES(NULL, '%s', 0, 0)"%strContent
        intLastRowId = self.db.commitSQL(strSQL=strSQL)
        strSQL = "INSERT INTO story_chain_chain VALUES(NULL, %d, %d)"%(intLastRowId, intPrevId)
        self.db.commitSQL(strSQL=strSQL)
        return intLastRowId
        
    #取得指定段落資料 (內容,贊數,噓數)
    def fetchStoryById(self, intStoryId=0):
        strSQL = "SELECT * FROM story_chain_story WHERE intId=%d"%intStoryId
        lstRowData = self.db.fetchallSQL(strSQL=strSQL)
        tupleStoryData = ()
        if lstRowData:
            rowData = lstRowData[0]
            tupleStoryData = (rowData["strContent"], rowData["intLike"], rowData["intDislike"])
        return tupleStoryData
        
    #更新指定段落之贊數與噓數
    def updateStoryLikeOrDislike(self, intStoryId=0, isLike=True):
        tupleStoryData = self.fetchStoryById(intStoryId=intStoryId)
        intLike = tupleStoryData[1]
        intDislike = tupleStoryData[2]
        if isLike:
            intLike = intLike + 1
        else:
            intDislike = intDislike + 1
        strSQL = "UPDATE story_chain_story SET intLike=%d, intDislike=%d WHERE intId=%d"%(intLike, intDislike, intStoryId)
        self.db.commitSQL(strSQL=strSQL)
        
    #取得指定段落的 前段 或 後段
    def fetchNextOrPrevStoryId(self, intStoryId=0, strFetchType=None):
        lstIntStoryId = []
        if strFetchType == "next": #後段 = 以目前 id 為 intPrevId 的 intStoryId
            strSQL = "SELECT * FROM story_chain_chain WHERE intPrevId=%d"%intStoryId
            lstRowData = self.db.fetchallSQL(strSQL=strSQL)
            for rowData in lstRowData:
                lstIntStoryId.append(rowData["intStoryId"])
        elif strFetchType == "prev":#前段 = 以目前 id 為 intStoryId 的 intPrevId
            strSQL = "SELECT * FROM story_chain_chain WHERE intStoryId=%d"%intStoryId
            lstRowData = self.db.fetchallSQL(strSQL=strSQL)
            for rowData in lstRowData:
                lstIntStoryId.append(rowData["intPrevId"])
        return lstIntStoryId