#coding=utf8
import urllib2
from bs4 import BeautifulSoup
class NbaApi:
    def __init__(self):
        self.base_url = "http://g.hupu.com"
        self.home_url = 'http://g.hupu.com/nba'
        self.live_url = 'http://g.hupu.com/nba/daily/playbyplay_151581.html'

    def getGames(self):
        req = urllib2.Request(self.home_url)
        req.add_header('User-Agent', 'Mozilla/6.0 (iPhone; CPU iPhone OS 8_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/8.0 Mobile/10A5376e Safari/8536.25')
        text = urllib2.urlopen(req).read()
        soup = BeautifulSoup(text, 'html.parser')

        matches = soup.findAll('div', {"class":"team_vs"})
        playbacks = soup.findAll('div',{"class":"table_choose"})
        pb = []
        mat = []

        for playback in playbacks:
            if playback.find("a",{"class":"b"}):
                pb.append(self.base_url + playback.find("a",{"class":"b"})['href'])
            else:
                pb.append(None)

        for i,match in enumerate(matches):
            team1 = match.find('div', {"class":"team_vs_" + chr(97+i) + "_1"})
            team2 = match.find('div', {"class":"team_vs_" + chr(97+i) + "_2"})
            n1 = team1.find('span',{"class":"num"}).get_text()
            n2 = team2.find('span',{"class":"num"}).get_text()
            team1_name = team1.findAll('a')[1].get_text().encode('utf8', 'ignore')
            team2_name = team2.findAll('a')[1].get_text().encode('utf8', 'ignore')
            mat.append({"t_name1":team1_name,"t_name2":team2_name,
                        "n1":n1,"n2":n2,"pb_url":pb[i]
                        })
        return mat

    def getMessage(self, url):
        if url == None:
            return
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/6.0 (iPhone; CPU iPhone OS 8_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/8.0 Mobile/10A5376e Safari/8536.25')
        text = urllib2.urlopen(req).read()
        soup = BeautifulSoup(text, 'html.parser')

        msgs = []

        messages = soup.findAll("div",{"class":"table_list_live"})[1].findAll("tr")[:10]
        for m in messages:
            me = m.findAll('td')

            time = me[0].get_text().encode('utf8', 'ignore')
            if len(me) == 1:
                msgs.append({"time":time,"team":"*","info":"*","score":"*"})
            else:
                team = me[1].get_text().encode('utf8', 'ignore')
                info = me[2].get_text().encode('utf8', 'ignore').strip()
                score = me[3].get_text()
                msgs.append({"time":time,"team":team,"info":info,"score":score})
        return msgs
