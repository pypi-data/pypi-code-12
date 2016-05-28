#coding: utf-8
import os
import os.path
import io
import json
import sys
import math

class fileUtility: 
	'''
	功能：讀取json檔案
	參數：
		strFilePath: 檔案路徑
	回傳：
		dictionary
	'''
	@staticmethod
	def loadObjFromJsonFile(strFilePath):
		if os.path.isfile(strFilePath) == True:
			with open(strFilePath, 'r') as jsonfile:
				jsonData = json.loads(jsonfile.read(), encoding='utf-8')
			return jsonData
		else:
			return None
	'''
	功能：確認字串是否是空
	參數：
		str: 檔案路徑
	回傳：
		bool
	'''
	@staticmethod
	def checkStringValid(str):
		if(str == None or str == "" or str == 0):
			return False
		else:
			return True

	'''
	功能：讀取字串列表類型檔案
	參數：
		strFilePath: 檔案路徑
	回傳：
		string list
	'''
	@staticmethod
	def loadStrListInfo(strFilePath): 									
		lstStr = []
		if(os.path.isfile(strFilePath) == True):
			with io.open(strFilePath, encoding="utf8") as f:
				for line in f:
					lstStr.append(fileUtility.purifyString(line))
		return lstStr

	'''
	功能：把dictionary物件儲存成json檔案
	參數：
		dicData: 資料dictionary物件
		strOutputPath: 檔案輸出路徑
	'''
	@staticmethod
	def saveObjToJson(dicData, strOutputPath):
		fileUtility.overwriteTextFile(json.dumps(dicData, ensure_ascii = False).encode('utf8'), strOutputPath)
		return

	'''
	功能：把字串輸出成檔案
	參數：
		strData: 資料字串
		strOutputPath: 檔案輸出路徑
	'''
	@staticmethod
	def overwriteTextFile(strData, strOutputPath):
		directory = strOutputPath[0:strOutputPath.rfind('/')]
		if not os.path.exists(directory):
			os.makedirs(directory)
		with io.open(strOutputPath, "wb") as file:
			file.write(strData)

	'''
	功能：在目標文字檔案最下方新增一行文字
	參數：
		strData: 資料字串
		strOutputPath: 檔案輸出路徑
	'''
	@staticmethod
	def appendTextFile(strData, strOutputPath):
		directory = strOutputPath[0:strOutputPath.rfind('/')]
		if not os.path.exists(directory):
			os.makedirs(directory)
		with io.open(strOutputPath, "a") as file:
			file.write(strData + u"\n")

	'''
	功能：把string list組合後print
	參數：
		lstStr: string list
	'''
	@staticmethod
	def printStringList(lstStr):
		print(', '.join(lstStr))

	'''
	功能：把字串前後的換行和空白消除	
	參數：
		strOri: 原字串
	'''
	@staticmethod
	def purifyString(strOri):
		str = strOri.replace("\n", "")
		str = str.strip()
		return str

	'''
	功能：把字串list整個清乾淨
	參數：
		strOri: 原字串
	'''
	@staticmethod
	def purifyStringList(lstStrOri):
		lstStr = []
		for strOri in lstStrOri:
			lstStr.append(fileUtility.purifyString(strOri))
		return lstStr

	'''
	功能：得到url中最後那串文字，ex: return "filename" from "XXXX/XXXX/XXXX/filename.XXXX"
	參數：
		strUrl: 原字串
	回傳：
		string
	'''
	@staticmethod
	def getFileNameInUrl(strUrl):
		idIndex = strUrl.rfind('/')+1
		dotIndex = strUrl.rfind('.')
		if dotIndex == -1 or dotIndex < idIndex:
			dotIndex = len(strUrl)
		return strUrl[idIndex:dotIndex]

	'''
	功能：得到儲存抓取頁面的根目錄，並組成完整目錄回傳
	參數：
		strCustumPath: 子目錄
	回傳：
		string
	'''
	@staticmethod
	def getLocalFilePath(strCustumPath):
		spiderConfig = fileUtility.getSpiderConfig()
		return spiderConfig["strLocalFilePath"][os.name] + strCustumPath
	'''
	功能：得到儲存分析結果的根目錄，並組成完整目錄回傳
	參數：
		strCustumPath: 子目錄
	回傳：
		string
	'''
	@staticmethod
	def getParsedFilePath(strCustumPath):
		spiderConfig = fileUtility.getSpiderConfig()
		return spiderConfig["strParsedFilePath"][os.name] + strCustumPath
	'''
	功能：取得config檔案內容
	'''
	dicConfig = None
	strConfigPath = "spiderConfig.json"
	@staticmethod 
	def getSpiderConfig():
		if(fileUtility.dicConfig == None):
			dicConfig = fileUtility.loadObjFromJsonFile(os.path.split(os.path.realpath(__file__))[0] + "/" + fileUtility.strConfigPath)
		return dicConfig

if __name__ == '__main__':
	print(fileUtility.getParsedFilePath("Test"))