from bs4 import BeautifulSoup
from yahoo_finance import Share
import urllib2
import time
from argparse import ArgumentParser 
from colorama import init, Fore, Back, Style


averagevolumeflag = 100 # the percentage volume to flag in output with 
#init()
init(autoreset=True) #For colorama it autoresets color everytime it's called

baseurl = 'http://finance.yahoo.com/q?s='
endurl = '&ql=1'

def startup(self):
	print "Runing against..." + url

def getStock(self):
    return Share(self)

def getPrice(self):
	return self.get_price()

def getOpen(self): 
	go = self.get_open()
	if go is not None:
		return float(self.get_open())
	else:
		return 1

def getYearHigh(self):
	return self.get_year_high()

def getYearLow(self):
    return self.get_year_low()

def getVolume(self):
	return float(self.get_volume())

def getAvgDailyVolume(self):
	return float(self.get_avg_daily_volume())

def scraper(self):
	page = urllib2.urlopen(self)
	soup = BeautifulSoup(page.read(), "lxml")
	target = soup.find("span", {"class": "time_rtq_ticker"}).span.contents
	return target[0]

def getDayChange(self):
	#Checks to see if the gdc is None (e.g. between ~9am-9:45am Yhaoo Finance returns N/A for change).  If Yahoo-Finance returns N/A (none), then return 0 to prevent error.  Returning 0 causes winLoss() to return invalid data.
	gdc = mystock.get_change()
	if gdc is not None:
		#print ticker, gdc
		return float(self.get_change())
	else:
		return 1

def percentChange(self):
	if (myDayChange is not None) and (myOpen is not None):
		tickerPercentChange = (myDayChange/myOpen)*100
		tickerPercentChange = round(tickerPercentChange, 2)
		return tickerPercentChange
	else:
		return 0

def offHigh(self):
	oh1 = float(myYearHigh) - (float(realtime))
	percentOffHigh = str(round((oh1 / float(realtime))*100, 2))+ "%"
	return percentOffHigh

def offlow(self):
	olrealtime = float(realtime)
	olmyyearlow = float(myyearlow)
	ol1 = olrealtime- olmyyearlow
	ol2 = (ol1 / olmyyearlow)*100
	ol2 = str(round(ol2,2)) + "%"
	return ol2


def getYearLow(self):
    return self.get_year_low()


def ofAverageVolume(self):
	myAverageVolume = getAvgDailyVolume(self)
	myCurrentVolume = getVolume(self)
	if myAverageVolume > myCurrentVolume:
		ofAverageVolume = round((myCurrentVolume / myAverageVolume)*100,2)
		return ofAverageVolume
	else:
		ofAverageVolume = round((1-(myAverageVolume - myCurrentVolume)/(myAverageVolume))*100, 2)
		return ofAverageVolume

def realtimePrice(a, b, c, d, e, f, g, h, i, j, k, l):

	print "Timestamp: %s" % (time.strftime('%Y-%m-%d %H:%M:%S'))
	print "ticker: %s" % ticker
	if realtime >= myPrice:												#Visualize in color the direction of realtime price relative delayed price - right now, is it going up or down?
		print "Realtime: %s" % (Style.BRIGHT + Fore.GREEN + realtime)
	else:
		print "Realtime: %s" % (Style.BRIGHT + Fore.RED + realtime)

 	print "Delayed Price: %s" % myPrice

	print "Day Change: %s" % myDayChange

	if myPercentChange >0:												#Visualize in color the overall direction
		strmypercentchange= str(myPercentChange) 						#convert it to a string; fixes float to string concatenation
		print "Percent Change: %s" % (Style.BRIGHT + Fore.GREEN + strmypercentchange + "%")
	else:
		strmypercentchange= str(myPercentChange)
		print "Percent Change: %s" % (Style.BRIGHT + Fore.RED + strmypercentchange + "%")
	
	print "Volume: %s" % myVolume
	print "Average Volume: %s" % myAverageDailyVolume
	
	if myOfAverageVolume > averagevolumeflag:							#Flag 
		strmyofaveragevolume = str(myOfAverageVolume) 					#convert it to a string; fixes float to string concatenation
		print "Percent of Average: %s" % (Style.BRIGHT + Fore.YELLOW + strmyofaveragevolume + "%") 
	else:
		print "Percent of Average: %s" % myOfAverageVolume + "%"

	print "52-week High: %s" %myYearHigh
	print "Percent off high: %s" %myOffHigh
	print "52-week low: %s" %myyearlow
	print "Percent off low: %s" %myofflow

	print (Style.RESET_ALL)



	#		print ticker.strip('\n') + ", " + str(round(mypercentchange, 2))+'%' + ", " + str(round(myofAverageVolume, 2))+'%'

parser = ArgumentParser(description = 'Get Realtime ticker from Yahoo-Finance')
parser.add_argument("-t", "--ticker", dest="ticker", help="ticker for lookup", metavar="FILE")
args = parser.parse_args()

if args.ticker:
	ticker = args.ticker
	url = baseurl + ticker + endurl
	startup(url)
	mystock = getStock(ticker)
	myPrice = getPrice(mystock)
	myOpen = getOpen(mystock)
	myVolume = getVolume(mystock)
	myAverageDailyVolume = getAvgDailyVolume(mystock)
	myOfAverageVolume = ofAverageVolume(mystock)
	myDayChange = getDayChange(mystock)
	myYearHigh = getYearHigh(mystock)
	myPercentChange = percentChange(mystock)
	realtime = scraper(url)
	myyearlow = getYearLow(mystock)
	myOffHigh = offHigh(mystock)
	myofflow = offlow(mystock)

	realtimePrice(ticker, realtime, myPrice, myDayChange, myPercentChange, myVolume, myAverageDailyVolume, myOfAverageVolume, myYearHigh, myOffHigh, myyearlow, myofflow)
	
	#print myPrice, myOpen


