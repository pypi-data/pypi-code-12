# -*- coding: utf-8 -*-
"""
Created on Tue Apr 19 12:34:35 2016

@author: deelden
"""
from lxml import html
import requests
import re
import numpy as np
from tabulate import tabulate

#No Google Finance API so we need to scrape content from web page
page_finance = requests.get('https://www.google.com/finance')
page_contents = html.fromstring(page_finance.content)

#Create lists from Global Markets data
symbol = page_contents.xpath('//*[@id="markets"]/div/table/tbody/tr/td[@class="symbol"]/a/text()')
price = page_contents.xpath('//*[@id="markets"]/div/table/tbody/tr/td[@class="price"]/span/text()')
change = page_contents.xpath('//*[@id="markets"]/div/table/tbody/tr/td[@class="change"]/span[1]/text()')
change_percent = page_contents.xpath('//*[@id="markets"]/div/table/tbody/tr/td[@class="change"]/span[2]/text()')

#Combine lists into a list of lists
def globalMktData(list1, list2, list3, list4):
    combList = []
    for i in range(len(symbol)):
        combList.append([list1[i].rstrip(), list2[i].rstrip(), list3[i].rstrip(), list4[i].rstrip()])
    return combList

globalMkt = globalMktData(symbol, price, change, change_percent)

#Tabulate data set
globalMkt = tabulate(globalMkt, headers=['Symbol', 'Price', 'Change', 'Percent Change'], tablefmt='orgtbl')

#Convert percent change strings to float numbers
def makeFloat(theList):
    newList= []
    for i in theList:
        scrubbed = re.sub('[()%]', '', i) #Remove ()% from string
        newList.append(float(scrubbed))
    return newList

floats = makeFloat(change_percent)

#Calculate standard deviation of percent change data set and round to two decimal places
stdDev = round(np.std(floats), 2)

def displayGlobals():
    print globalMkt + '\n'
    print 'Standard Deviation: ' + str(stdDev) + '%' + '\n'

displayGlobals()