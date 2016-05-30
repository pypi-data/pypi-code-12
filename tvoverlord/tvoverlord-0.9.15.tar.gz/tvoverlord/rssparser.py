
import urllib.request, urllib.parse, urllib.error
import re
from pprint import pprint as pp

from bs4 import BeautifulSoup
import requests


class RssParser:

    def __init__(self):
        pass

    def parse(self, url):

        print(url)
        print()

        CONNECTION_TIMEOUT = 3.05
        READ_TIMEOUT = 20

        try:
            r = requests.get(url)#, timeout=(CONNECTION_TIMEOUT, READ_TIMEOUT))
        except requests.exceptions.ConnectTimeout:
            print('timed out')
            exit()
        except requests.exceptions.ReadTimeout:
            print('read timeout')
            exit()
        except requests.exceptions.ConnectionError:
            print('connection error')
            exit()

        print('souping', '\n')

        soup = BeautifulSoup(r.content, 'lxml')
        #print(soup, '\n')

        items = soup.find_all('item')
        print('items count', len(items))
        for item in items:
            #print(item)
            #print('item len', len(item))

            print(item.pubdate.text)

            for field in item:
                if not field.name: continue

                print(field)
            #exit()
            print()

        #pp(items)



if __name__ == '__main__':


    rss = RssParser()
    #rss.parse('https://thepiratebay.gd/search/doctor%20who/0/99/0')
    #rss.parse('https://extratorrent.unblocked.pe/rss.xml?type=search&cid=0&search=Haven%20S05E22')
    #rss.parse('https://extratorrent.unblocked.pe/rss.xml?type=search&cid=0&search=Haven%20S05E22')
    rss.parse('https://kat.cr/usearch/doctor%20who/?rss=1')
    #rss.parse('')

