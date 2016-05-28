#coding: utf-8
import os
import sys
import time
import datetime
import math
import re
from scrapy import Selector
from fileUtility import *

class scrapyUtility:

	'''
	功能：若確定字串內只有一個整數，可得之
	參數：
		str: 含一個正整數的字串
	回傳：
		int
	'''
	@staticmethod 
	def getIntegerInString(str):
		str.replace(",", "") #ex: 19,000 to 19000
		lstIntNum = re.findall('\d+', str)
		return int(lstIntNum[0])

	'''
	功能：開始分析某個本地html檔案
	參數：
		strFilePath: 本地html檔案路徑
	回傳：
		scrapy的root
	'''
	@staticmethod
	def startParseLocalPage(strFilePath):
		with open(strFilePath, "rb") as file: #讀取本地端文件檔案內容到字串
			strPageSource = file.read()
		root = Selector(text=strPageSource) #開始使用Scrapy解析字串
		return root

	'''
	功能：取出文字內的原價或市價，若無此資訊則回傳0(台經院特殊需求)
	參數：
		strRewardContent: 回饋方案說明文字
		lstStrKeyword: 出現什麼關鍵字代表說明文字內可能含有原價資訊
		intRewardMoney: 回饋方案價格
	回傳：
		int
	'''
	@staticmethod
	def getRetailPrice(strRewardContent, lstStrKeyword, intRewardMoney):
		intRewardRetailPrice = 0
		bHasRetailPrice = False
		for strKeyword in lstStrKeyword:
			if(strKeyword in strRewardContent):
				bHasRetailPrice = True
				break

		if(bHasRetailPrice):
			strRewardContentWithoutComma = strRewardContent.replace(",", "")
			lstIntNum = re.findall('\d+', strRewardContentWithoutComma)		
			intRetailPrice = sys.maxint
			for intNum in lstIntNum:
				intNum = int(intNum)
				if ((intNum >= intRewardMoney) and (intNum <= intRetailPrice)):
					intRetailPrice = intNum
			if(intRetailPrice < sys.maxint):
				intRewardRetailPrice = intRetailPrice

		return intRewardRetailPrice	