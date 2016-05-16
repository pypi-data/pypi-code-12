# -*- coding: utf-8 -*-
"""
Copyright (C) 2015, MuChu Hsu
Contributed by Muchu Hsu (muchu1983@gmail.com)
This file is part of BSD license

<https://opensource.org/licenses/BSD-3-Clause>
"""
import json
from flask import Flask
from flask import request
from flask import render_template
from flask import jsonify
from story_chain.localdb import LocalDbForStoryChain

app = Flask(__name__.split(".")[0])

#啟動 server
def start_flask_server():
    app.run(host="0.0.0.0", port=5000, debug=True)
    
#建立 jsonp response
def make_jsonp_response(dicJsonObj=None):
    strCallback = request.args.get("strJsonpCallback", 0, type=str)
    return strCallback + "(" + json.dumps(dicJsonObj) + ")"
    
#在指定的段落之後 加入新的故事段落 (return 新段落 id)
@app.route("/story_chain/api_post/story", methods=["GET"])
def apiPostNewStory():
    db = LocalDbForStoryChain()
    strStoryContent = request.args.get("str_story_content", type=str)
    intPrevStoryId = request.args.get("int_prev_story_id", type=int)
    intNewStoryId = db.insertNewStory(strContent=strStoryContent, intPrevId=intPrevStoryId)
    return make_jsonp_response(dicJsonObj={"new_story_id":intNewStoryId})
    
#取得指定段落內容
@app.route("/story_chain/api_get/story/<int:intStoryId>", methods=["GET"])
def apiGetStoryById(intStoryId=0):
    db = LocalDbForStoryChain()
    (strContent, intLike, intDislike) = db.fetchStoryById(intStoryId=intStoryId)
    dicJsonObj = {"str_content":strContent,
                  "int_like":intLike,
                  "int_dislike":intDislike}
    return make_jsonp_response(dicJsonObj=dicJsonObj)
    
#修改指定段落內容 (按贊/按噓)
@app.route("/story_chain/api_put/story/<int:intStoryId>", methods=["GET"])
def apiPutStoryById(intStoryId=0):
    pass
    
#取得 前 or 後 故事段 列表 (return 段落 id list)
@app.route("/story_chain/api_get/story", methods=["GET"])
def apiGetStoryList():
    db = LocalDbForStoryChain()
    strType = request.args.get("str_type", type=str) #"next" or "prev"
    intStoryId = request.args.get("int_story_id", type=int)
    lstIntStoryId = db.fetchNextOrPrevStoryId(intStoryId=intStoryId, strFetchType=strType)
    dicJsonObj = None
    if strType == "prev":
        #前一段必定是唯一的
        dicJsonObj = {"int_prev_story_id":(lstIntStoryId[0] if lstIntStoryId else 0)}
    elif strType == "next":
        #下一段可能有多個選擇
        dicJsonObj = {"lst_int_next_story_id":lstIntStoryId}
    else:
        dicJsonObj = {}
    return make_jsonp_response(dicJsonObj)
#讀取書籤
@app.route("/story_chain/api_get/tag/<strTagName>", methods=["GET"])
def apiGetTagByName(strTagName=None):
    pass
    

#新增書籤 (書籤有時限)
@app.route("/story_chain/api_post/tag", methods=["GET"])
def apiPostTag(strTagName=None):
    request.args.get("strTagName")
    request.args.get("intStoryId")
    pass

#= Flask 範例 =
#GET POST參數範例
@app.route("/hello/<username>/<int:num>", methods=["GET", "POST"])
def hello(username, num):
    #http://192.168.1.101:5000/hello/muchu/7?love=lunna
    request.form #get form data when POST
    return "Hello World! %s %d method: %s args: %s"%(username, num, 
                                                     request.method, request.args.get("love"))
    
#template範例
@app.route("/template/")
@app.route("/template/<name>")
def template(name=None):
    return render_template("temp.html", name=name)
    
#post json範例
@app.route("/jsonpapi", methods=["GET"])
def jsonpapi():
    x = request.args.get("x", 0, type=int)
    y = request.args.get("y", 0, type=int)
    dicResultJson = {"result":x+y}
    return make_jsonp_response(dicJsonObj=dicResultJson)
    
if __name__ == "__main__":
    start_flask_server()