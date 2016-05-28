#coding: utf-8

import geonames
import os
from utility import *
from time import sleep

class geonameHelper:

	__instance = None

	def __init__(self):
		self.__geonamesCache = {}
		self.loadGeonamesCacheData()

	def __parseLocation(self, strLocation):
		if(strLocation.strip() == ''):
			dicEmptyGeoname = {}
			dicEmptyGeoname['strCity'] = ''
			dicEmptyGeoname['strCountry'] = ''
			dicEmptyGeoname['strContinent'] = ''
			return dicEmptyGeoname

		strLocationKey = strLocation
		if(isinstance(strLocationKey, str)): 
			strLocationKey = strLocationKey.decode("utf8")
		else:
			strLocationKey = strLocationKey.encode("utf8")

		if(self.__geonamesCache.get(strLocationKey) == None):
			#print(strLocationKey)
			dicGeonameCache = {} 
			dicSearchResult = geonames.search(q=strLocationKey, maxRows=10, featureClass='P') #countryBias='US'
			#print(dicSearchResult)
			lstStrLocation = strLocationKey.split(', ')
			while (dicSearchResult == None or len(dicSearchResult) == 0) and lstStrLocation != None and len(lstStrLocation) > 0:
				dicSearchResult = geonames.search(q=lstStrLocation[0], maxRows=10, featureClass='P') #countryBias='US'
				del lstStrLocation[0]

			if(len(dicSearchResult) == 0):
				dicNotFoundGeoname = {}
				dicNotFoundGeoname['strCity'] = ''
				dicNotFoundGeoname['strCountry'] = ''
				dicNotFoundGeoname['strContinent'] = ''
				return dicNotFoundGeoname

			strGeonameId = dicSearchResult[0]['geonameId']
			dicGeoname = geonames.get(strGeonameId)
			strFclName = dicGeoname['fclName']
			strCountry = dicGeoname['countryCode']
			strContinent = dicGeoname['continentCode']

			strCity = ''
			if 'city' in strFclName:
				strCity = dicGeoname['asciiName']
			elif dicGeoname.get('bbox') != None:
				bbox = dicGeoname['bbox']
				dicCity = geonames.findCity(north=bbox['north'], south=bbox['south'], east=bbox['east'], west=bbox['west'])[0]
				strCity = dicCity['name']
			else:
				strCity = strLocation[0:strLocation.rfind(",")]
				#import pdb; pdb.set_trace()
			
			if(isinstance(strCity, str)): 
				strCity = strCity.decode("utf8")
			else:
				strCity = strCity.encode("utf8")
			if(isinstance(strCountry, str)): 
				strCountry = strCountry.decode("utf8")
			else:
				strCountry = strCountry.encode("utf8")
			if(isinstance(strContinent, str)): 
				strContinent = strContinent.decode("utf8")
			else:
				strContinent = strContinent.encode("utf8")

			dicGeonameCache['strCity'] = strCity
			dicGeonameCache['strCountry'] = strCountry
			dicGeonameCache['strContinent'] = strContinent
			
			self.__geonamesCache[strLocationKey] = dicGeonameCache
			strLocationData = strLocationKey + ":" + strCity + ":" + strCountry + ":" + strContinent
			#strLocationData.encode(sys.stdin.encoding, "replace").decode(sys.stdin.encoding)
			appendTextFile(strLocationData, geonameHelper.getGeonamesCacheTextFilePath())

		return self.__geonamesCache[strLocationKey]

	def loadGeonamesCacheData(self):
		self.__geonamesCache = {}
		lstStrData = loadStrListInfo(geonameHelper.getGeonamesCacheTextFilePath())
		for strData in lstStrData:
			lstStrLocation = strData.split(":")
			self.__geonamesCache[lstStrLocation[0]] = {"strCity":lstStrLocation[1], "strCountry":lstStrLocation[2], "strContinent":lstStrLocation[3]}

	@staticmethod	
	def getGeonamesCacheTextFilePath():
		return os.path.dirname(os.path.abspath(__file__)) + "/geonamescache.text"

	@staticmethod
	def parseLocation(strLocation):
		if(geonameHelper.__instance == None):
			geonameHelper.__instance = geonameHelper()
		return geonameHelper.__instance.__parseLocation(strLocation.encode("utf8"))


def main():
	print(geonameHelper.parseLocation("Sweden"))
	
if __name__ == '__main__':
	main()
