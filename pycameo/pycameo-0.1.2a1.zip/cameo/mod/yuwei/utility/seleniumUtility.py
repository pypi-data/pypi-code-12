#coding: utf-8

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC # available since 2.26.0
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep
from operator import itemgetter
import datetime
import os.path
import io
import json
import sys
from fileUtility import *
from operator import itemgetter
from random import randint

class seleniumUtility:

	'''
	功能：用於需要滑動頁面新增物件的狀況，每次滑動一個螢幕高
	參數：
		driver: selenium的driver
		strCss: 數量會變多的物件的css selector
		intScrollTimeOut: 每次增加物件時會開始計算timeout，若持續滑動都沒有新增物件(時間累計超過timeout)則結束
		fSleepTime: 每次載入更多物件時的等待時間
		bShowMessage: 是否顯示log
	'''
	@staticmethod
	def generatItemByScroll(driver, strItemCss, intScrollTimeOut = 5, fSleepTime = 0.5, bShowMessage = False):
		fCurTime = 0
		intLastItemCount = 0
		intScrollDelta = driver.get_window_size()["height"]
		intScrollTo = intScrollDelta
		while True:
			if bShowMessage == True:
				print("[seleniumUtility.generatItemByScroll] wait displaying items...")
			intCurItemCount = len(driver.find_elements_by_css_selector(strItemCss))
			if fCurTime > intScrollTimeOut:
				break
			elif intCurItemCount > intLastItemCount:
				intLastItemCount = intCurItemCount
				driver.execute_script("window.scrollTo(0, "+ str(intScrollTo).encode("utf8") + ");")
				intScrollTo = intScrollTo + intScrollDelta
				fCurTime = 0
			else:
				fCurTime = fCurTime + fSleepTime
				sleep(fSleepTime)
	'''
	功能：用於需要滑動頁面新增物件的狀況，每次滑到底
	參數：
		driver: selenium的driver
		strCss: 數量會變多的物件的css selector
		intScrollTimeOut: 每次增加物件時會開始計算timeout，若持續滑動都沒有新增物件(時間累計超過timeout)則結束
		fSleepTime: 每次載入更多物件時的等待時間
		bShowMessage: 是否顯示log
	'''
	@staticmethod
	def generatItemByScrollToBottom(driver, strItemCss, intScrollTimeOut = 5, fSleepTime = 0.5, bShowMessage = False):
		fCurTime = 0
		intLastItemCount = 0
		while True:
			if bShowMessage == True:
				print("[seleniumUtility.generatItemByScrollToBottom] wait displaying items...")
			intCurItemCount = len(driver.find_elements_by_css_selector(strItemCss))
			if fCurTime > intScrollTimeOut:
				break
			elif intCurItemCount > intLastItemCount:
				intLastItemCount = intCurItemCount
				driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
				fCurTime = 0
			else:
				fCurTime = fCurTime + fSleepTime
				sleep(fSleepTime)
	'''
	功能：用於需要按下載入更多按鈕來新增物件的狀況
	參數：
		driver: selenium的driver
		strBtnCss: "載入更多"的按鈕
		strItemCss: "載入物件"的css
		bShowMessage: 是否顯示log
		elementContainer: 包含"產生物件"的web element
	'''
	@staticmethod
	def generatItemByClickBtn(driver, strBtnCss, strItemCss, bShowMessage = False, elementContainer = None):
		isScrollToBottom = False
		intLastItemCount = 0
		while isScrollToBottom == False:			
			if bShowMessage == True:
				print("[seleniumUtility.generatItemByClickBtn] Wait displaying items...")
			
			intCurItemCount = 0
			if(elementContainer == None):
				elementContainer = driver
			else:
				print("click more in container")

			intCurItemCount = len(elementContainer.find_elements_by_css_selector(strItemCss))
			if(intCurItemCount == intLastItemCount):
				print("[seleniumUtility.generatItemByClickBtn] Item not increased")
				isScrollToBottom = True
			elif(seleniumUtility.isItemClickable(elementContainer, strBtnCss) == False):
				print("[seleniumUtility.generatItemByClickBtn] Cannot find 'More' button")
				isScrollToBottom = True
			else:
				intLastItemCount = intCurItemCount
				driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
				elementContainer.find_element_by_css_selector(strBtnCss).click()
				print("[seleniumUtility.generatItemByClickBtn] 'More' button clicked...")
				seleniumUtility.waitAjaxComplete(driver)
	'''
	功能：等待ajax執行完畢
	'''
	@staticmethod
	def waitAjaxComplete(driver):
		wait = WebDriverWait(driver, 10)
		print("Wait ajax complete...")
		wait.until(seleniumUtility.isAjaxComplete, "Timeout waiting for page to load")
	'''
	功能：檢查是否正在執行ajax
	'''
	@staticmethod
	def isAjaxComplete(driver):
		sleep(0.1)
		return 0 == driver.execute_script("return jQuery.active")
	'''
	功能：儲存現在的頁面
	參數：
		driver: selenium的driver
		strFilePath: 檔案儲存路徑
	'''
	@staticmethod
	def saveCurrentPage(driver, strFilePath):
		strData = driver.page_source.encode('utf8')
		fileUtility.overwriteTextFile(strData, strFilePath)
	'''
	功能：檢查物件是否存在
	參數：
		driver: selenium的driver
		strCss: 查詢物件的css selector
	'''
	@staticmethod
	def isItemExist(driver, strCss):
		return (len(driver.find_elements_by_css_selector(strCss)) > 0)
	'''
	功能：檢查物件是否可按，當有此物件且可視時(在畫面內且未被擋住)
	參數：
		driver: selenium的driver
		strCss: 查詢物件的css selector
	'''
	@staticmethod
	def isItemClickable(driver, strCss):
		return (len(driver.find_elements_by_css_selector(strCss)) > 0 and driver.find_element_by_css_selector(strCss).is_displayed())
	'''
	功能：產生chrome的selenium driver
	參數：
		chrome路徑，ex: "/Users/yuwei/Documents/Webdriver/chromedriver"
	'''
	@staticmethod
	def createChromeDriver(strProxy = None, intPort = None):
		config = seleniumUtility.getSpiderConfig()
		chromePath = config["strChromePath"][os.name]
		option = webdriver.ChromeOptions()
		option.add_argument('test-type')
		if(strProxy != None and intPort != None):
			option.add_argument('--proxy-server=http://%s' % (strProxy + ":" + str(intPort).encode("utf8")))
		driver = webdriver.Chrome(chromePath, chrome_options = option)
		return driver
	'''
	功能：等待某物件產生
	參數：
		strCss: 該物件的css selector
		strName: 也可以使用Name屬性
		(strCss/strName 則一即可)
	回傳：
		等待產生的物件
	'''
	@staticmethod
	def waitElementCreating(driver, strCss = None, strName = None):
		if(strCss == None and strName == None):
			return None
		while(True):
			if(strCss != None and len(driver.find_elements_by_css_selector(strCss)) > 0):
				return driver.find_element_by_css_selector(strCss)
			if(strName != None and len(driver.find_elements_by_name(strName)) > 0):
				return driver.find_element_by_name(strName)
			sleep(0.1)

	'''
	功能：取得一個https的可用proxy
	回傳：
		{
			"strProxy":proxy
			"strPort":port
		}
	'''
	@staticmethod
	def getEliteProxy():
		driver = webdriver.Firefox()
		driver.get("http://proxy-list.org/")
		
		inputMail = driver.find_element_by_css_selector("#uemail")
		inputPaswd = driver.find_element_by_css_selector("#upassword")
		inputMail.send_keys("eva@cameo.tw")
		inputPaswd.send_keys("netlab2000")
		inputLogin = driver.find_element_by_css_selector("#login")
		inputLogin.click()
		sleep(2)
		driver.find_element_by_css_selector(".close-button").click()
		sleep(2)
		driver.find_element_by_css_selector("a[href*='./index.php']").click()
		sleep(2)
		elementTypeSelect = driver.find_element_by_name("type").click()
		driver.find_element_by_css_selector("option[value='elite']").click()
		elementSslSelect = driver.find_element_by_name("ssl").click()
		driver.find_element_by_css_selector("option[value='yes']").click()
		driver.find_element_by_css_selector(".button[value='Search proxy servers']").click()

		lstStrProxy = driver.find_elements_by_css_selector("#proxy-table ul > li.proxy")
		lstStrSpeed = driver.find_elements_by_css_selector("#proxy-table ul > li.speed")	
		lstProxyObj = []
		dicProxy = None

		for i in range(1, len(lstStrProxy), 1):
			fSpeed = 0
			if("kbit" in lstStrSpeed[i].text):
				fSpeed = float(lstStrSpeed[i].text.replace("kbit", ""))
			lstStrSplitProxy = lstStrProxy[i].text.split(":")
			lstProxyObj.append({"strProxy":lstStrSplitProxy[0], "intPort":int(lstStrSplitProxy[1]), "fSpeed":fSpeed})

		if(len(lstProxyObj) > 1):
			lstProxyObj = sorted(lstProxyObj, key=itemgetter('fSpeed'), reverse=True)  
			dicProxy = lstProxyObj[randint(0, len(lstProxyObj)-1)]
			print("proxy: " + dicProxy["strProxy"] + " " + str(dicProxy["fSpeed"]).encode("utf8"))
		driver.close()
		return dicProxy

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
	seleniumUtility.getEliteProxy()