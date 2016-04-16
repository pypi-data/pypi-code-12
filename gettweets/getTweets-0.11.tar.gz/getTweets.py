#!/usr/bin/env python

import requests, re, time
import bs4
import sys
import datetime
import codecs

class Tweet:
    def __init__(self, text, links=None):
        self.text = text
        self.time = time.strptime('', '')
        self.link = self.src = ''
        self.num  = 0
    def add_time(self, data):
        self.time = time.strptime(data, "%I:%M %p - %d %b %Y")
    def add_link(self, data):
        self.link = data
        self.num = data.split('/')[-1]
        self.src = data.split('/')[1]
    def __lt__(self, othr):
        return self.time < othr.time
    def __hash__(self):
        return self.text.__hash__() * 31 + self.time.__hash__()
    def __eq__(self, othr):
        return self.text == othr.text and self.time == othr.time
    def pnt(self):
        sys.stdout.write(datetime.time(self.time.tm_hour,self.time.tm_min).strftime("%I:%M %p") + " on " + str(self.time.tm_mon) + "/" + str(self.time.tm_mday) + "/" + str(self.time.tm_year) + ",\"")
        sys.stdout.write(self.text.encode('utf-8').replace("\"", "\"\""))
        print "\",https://twitter.com" + self.link

def visit(pos = 0, url="https://twitter.com/realDonaldTrump/"):
    h = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:44.0) Gecko/20100101 Firefox/44.0',
            'content-type': 'application/octet-stream',
            'DNT': '1', }
    p = {'include_available_features' : '1',
            'include_entities': '1',
            'reset_error_state' : 'false' }
    if pos:
        p['max_position'] = str(pos)
    r = requests.get(url, headers = h, params = p)
    return r

def extract(html):
    soup = bs4.BeautifulSoup(html, "html.parser")
    tweets = [Tweet(p.get_text()) for p in soup.find_all(attrs={'class': 'TweetTextSize'})]
    details = [t.contents[1].attrs for t in soup.find_all('small', {'class': 'time'})]
    if len(tweets) != len(details):
        print "Tweets: " + str(len(tweets)) 
        print "Details: " + str(len(details))
    for i in range(len(details)):
        if i < len(tweets):
            tweets[i].add_time(details[i]['title'])
            tweets[i].add_link(details[i]['href'])
    return tweets

def collect(n, addr):
    #collects tweets by 'scrolling down' from main page
    #de jure 3200 limit (twitter)
    tweets = []
    last = 0
    PastLen = -1
    for i in range(n):
        r = visit(last, addr)
        tmp = extract(r.text)
        duplix = set(tweets).intersection(set(tmp))
        tweets += tmp
        if len(tweets) == PastLen:
            break
        PastLen = len(tweets)
        print str(i) + ":\t" + str(len(duplix)) + " old (of "  + str(len(tmp))+"; " + str(PastLen) + " total)"
        last = tweets[-1].num
    
    print str(len(set(tweets))) + " original of " + str(len(tweets))
    return tweets

def getTweets(addr, n=4000):
    AllTweets = collect(n, addr)
    sys.stdout = open('TweetsOut.csv', 'w')
    print "When,What,Where"
    for i in range(len(AllTweets)):
        AllTweets[i].pnt()
    sys.stdout.flush()
    sys.stdout.close()

#What actually runs.
if len(sys.argv) != 2:
    print "Error, wrong number of arguments.\nUsage, python This_Script Twitter_Address"
else:
    getTweets(sys.argv[1])
