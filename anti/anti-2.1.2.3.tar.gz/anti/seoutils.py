# -*- coding:utf-8 -*-

import datetime
import re
import httplib
import requests
import whois
import urlparse

from bs4 import BeautifulSoup

from .anti import openYandex, openGoogle
from .anti_config import db, Host, SeoData
from .utils import get_or_create, GetHash, check_page, check_absolute_page, get_normal_url, transaction, get_normal_quote

prhost = 'toolbarqueries.google.com'
prpath = '/tbr?client=navclient-auto&ch=%s&features=Rank&q=info:%s'


class SeoParser():

    def __init__(self, site, KEY_ANTIGATE):
        self.site = get_normal_url(site)
        self.quote = get_normal_quote(self.site)
        self.KEY_ANTIGATE = KEY_ANTIGATE
        with transaction():
            self.host = get_or_create(db.session, Host, host=self.site)


    def commit(self):
        with transaction():
            db.session.commit()
            res = get_or_create(db.session, SeoData, date=datetime.date.today(), host_id=self.host.id)
            if hasattr(self, 'tic'):
                res.tic = self.tic
            if hasattr(self, 'pr'):
                res.pr = self.pr
            if hasattr(self, 'yaca'):
                res.yaca = self.yaca
            if hasattr(self, 'indexed_yandex'):
                res.indexed_yandex = self.indexed_yandex
            if hasattr(self, 'indexed_google'):
                res.indexed_google = self.indexed_google
            if hasattr(self, 'indexed_google_clear'):
                res.indexed_google_clear = self.indexed_google_clear
            if hasattr(self, 'donors'):
                res.donors = self.donors
            if hasattr(self, 'backlinks'):
                res.backlinks = self.backlinks
            db.session.commit()

    def GetPageTic(self):
        yurl = 'http://bar-navig.yandex.ru/u?ver=2&show=32&url=http://%s' % self.site
        f = requests.get(yurl, timeout=120)
        st = f.text
        m = re.search(r'value="([0-9]{1,5})"', st)
        try:
            self.tic = m.group(1)
        except:
            self.tic = 0
        return self.tic

    def GetPageRank(self):
        conn = httplib.HTTPConnection(prhost)
        hash = GetHash(self.site)
        path = prpath % (hash, self.quote)
        conn.request("GET", path)
        response = conn.getresponse()
        data = response.read()
        conn.close()
        try:
            self.pr = int(data.split(":")[-1])
            return self.pr
        except ValueError:
            return 0

    def GetYaca(self):
        yurl = 'http://bar-navig.yandex.ru/u?ver=2&show=32&url=http://%s' % self.site
        resp = requests.get(yurl, timeout=120)
        m = re.search(r'<textinfo>(?P<author>[\W\w]+)</textinfo>', resp.text)
        try:
            self.yaca = m.group(1)
        except:
            self.yaca = ''
        if len(self.yaca) > 2:
            self.yaca = True
        else:
            self.yaca = False
        return self.yaca

    def check_robots(self):
        if check_page(self.site + '/robots.txt'):
            return True
        return False

    def check_sitemap(self):
        content = check_page(self.site + '/robots.txt')
        if content:
            res = re.search(ur'sitemap(\ )*:(\ *)(.*)', content.lower())
            if res:
                url = res.groups()[2]
                check_absolute_page(url)
                return True, res.groups()[2]

        url = self.site + '/sitemap.xml'
        if check_page(url):
            return True, 'http://' + url
        return False

    def check_sitemap_len(self):
        check, url = self.check_sitemap()
        if self.check_sitemap():
            response = requests.get(url, timeout=120)
            soup = BeautifulSoup(response.text)
            return len(soup.find_all('url'))
        return 0

    def check_404(self):
        link = 'http://%s/klfsdfhlj/fdsf/sdflkasflk' % self.site
        resp = requests.get(link, timeout=120)
        if resp.status_code == 404:
            return True
        return False

    def check_www(self):
        url = 'http://' + self.site
        www_url = 'http://www.' + self.site

        try:
            reqst = requests.get(url, timeout=120, verify=False)
            if len(reqst.history) > 0:
                if urlparse.urlparse(reqst.url).netloc == urlparse.urlparse(www_url).netloc:
                    if 302 not in [item.status_code for item in reqst.history]:
                        return 'www.'

        except requests.ConnectionError:
            pass

        except requests.TooManyRedirects:
            pass

        try:
            reqst = requests.get(www_url, timeout=120, verify=False)
            if len(reqst.history) > 0:

                if urlparse.urlparse(reqst.url).netloc == urlparse.urlparse(url).netloc:
                    if 302 not in [item.status_code for item in reqst.history]:
                        return True
        except:
            pass

        return False

    def check_yandex_www(self):
        obj = openYandex(self.KEY_ANTIGATE)
        data = obj.get_yandex_cache_pos('host:%s' % self.quote)
        if len(data) > 0:
            return True
        data = obj.get_yandex_cache_pos('host:www.%s' % self.quote)
        if len(data) > 0:
            return 'www.'
        return False

    def check_yandex_pages(self):
        link = u'http://yandex.ru/yandsearch?text=host:%s | host:www.%s&site=&rstr=&within=0&numdoc=50&lr=213&p=18'
        link = link % (self.quote, self.quote)
        obj = openYandex(self.KEY_ANTIGATE)
        soup = obj.get_soup(link, save=False)
        self.indexed_yandex = 0

        if not soup:
            return self.check_yandex_pages(self.site)

        text = soup.find('div', class_='input__found')
        if text:
            res = re.search(ur'(\d+)', text.text)
            if res:
                self.indexed_yandex = int(res.group())
                if re.search(ur'млн', text.text):
                    self.indexed_yandex = self.indexed_yandex * 1000000

                if re.search(ur'тыс', text.text):
                    self.indexed_yandex = self.indexed_yandex * 1000

                return self.indexed_yandex
        return 0

    def check_last_update(self):
        link = u'http://yandex.ru/yandsearch?text=host:%s | host:www.%s&site=&rstr=&within=0&numdoc=50&lr=213&how=tm' % (self.quote, self.quote)
        obj = openYandex(self.KEY_ANTIGATE)
        soup = obj.get_soup(link)

        if not soup:
            return self.check_last_update()

        try:
            return soup.find('span', {'class': 'serp-item__date'}).text
        except AttributeError, exc:
            return None

    def check_google_pages(self):
        link = 'https://www.google.ru/search?num=100&q=site:%s/' % self.quote
        print link
        obj = openGoogle(self.KEY_ANTIGATE)
        soup = obj.get_soup(link)

        data = soup.findAll('div', {'id': 'resultStats'})
        if len(data) > 0:
            data = str(data[0])
            comp = re.search(r'[\d]+', data.replace('\xc2\xa0', ''))
            if comp:
                self.indexed_google = int(comp.group().replace('&#160;', ''))
                return self.indexed_google
        return 0

    def check_google_pages_clear(self):
        link = 'https://www.google.ru/search?num=100&q=site:%s/&' % self.quote
        obj = openGoogle(self.KEY_ANTIGATE)
        soup = obj.get_soup(link)

        data = soup.findAll('div', {'id': 'resultStats'})
        if len(data) > 0:
            data = str(data[0])
            comp = re.search(r'[\d]+', data.replace('\xc2\xa0', ''))
            if comp:
                self.indexed_google_clear = comp.group().replace('&#160;', '')
                return int(self.indexed_google_clear)
        return 0

    def get_backlinks_donors(self):
        link = 'http://xml.linkpad.ru/?url=http://' + self.site
        resp = requests.get(link, timeout=120)
        soup = BeautifulSoup(resp.text)
        self.backlinks = soup.find('hin').text
        self.donors = soup.find('din').text
        return self.backlinks, self.donors

    def get_aod(self):
        try:
            instance = whois.whois(self.site)
            return (datetime.datetime.now() - instance.creation_date).days
        except:
            return None

    def get_counter(self):
        rsst = requests.get('http://counter.yadro.ru/values?site=%s' % (self.site), timeout=120, verify=False)
        res = re.search('(LI_month_vis = )(\d+);', rsst.text)
        if res:
            return int(res.group(2))
        else:
            rsst = requests.get('http://counter.yadro.ru/values?site=www.%s' % (self.site), timeout=120, verify=False)
            res = re.search('(LI_month_vis = )(\d+);', rsst.text)
            if res:
                return int(res.group(2))
        return 0
