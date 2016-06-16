# -*- coding:utf-8 -*-

import datetime
import requests

from bs4 import BeautifulSoup

from .utils import get_normal_url_decode, get_or_create, transaction
from .anti_config import db, Host, SeoData, Token


class Wrapper(object):
    def __init__(self, site, user, passwd, client_secret, client_id):
        self.site = get_normal_url_decode(site)
        self.user = user
        self.passwd = passwd
        self.client_secret = client_secret
        self.client_id = client_id
        with transaction():
            self.host = get_or_create(db.session, Host, host=self.site)
        self.tkn = Token.query.first()
        if self.tkn:
            self.access_token = self.tkn.token
        self.url = self.get_url()

    def auth(self):
        """ Авторизация """
        self.user = self.user
        self.passwd = self.passwd
        self.client_secret = self.client_secret
        self.client_id = self.client_id

        url = 'https://oauth.yandex.ru/authorize?response_type=token&client_id=%s' % self.client_id
        resp = requests.get(url, timeout=120)
        soup = BeautifulSoup(resp.text)
        data = {'login': self.user, 'passwd': self.passwd}
        for item in soup.findAll('input', {'type': 'hidden'}):
            data[item['name']] = item['value']
        url = soup.find('form')['action'] if 'action' in soup.find('form') else resp.url

        resp = requests.post(url, data, timeout=120)
        soup = BeautifulSoup(resp.text)
        if soup.find('button', {'class': ' nb-button _nb-action-button _init'}):
            url = 'https://oauth.yandex.ru' + soup.find('form')['action']
            for item in soup.findAll('input', {'type': 'hidden'}):
                data[item['name']] = item['value']
            resp = requests.post(url, data, timeout=120)
        self.access_token = resp.url[resp.url.find('#'):].replace('#', '').split('&')[0].split('=')[1]
        if not self.tkn:
            self.tkn = Token(token=self.access_token)
            db.session.add(self.tkn)
        else:
            self.tkn.token = self.access_token

        with transaction():
            db.session.commit()

    def get_url(self):
        """ Получение адреса для api"""
        if not hasattr(self, 'access_token'):
            self.auth()
        self.headers = {'Authorization': 'OAuth %s' % self.access_token}
        resp = requests.get('https://webmaster.yandex.ru/api/v2/hosts', headers=self.headers, timeout=120)
        soup = BeautifulSoup(resp.text)
        hosts = soup.findAll('host')
        for host in hosts:
            name = host.find('name').text.lower()
            if name in self.site or self.site in name:
                url = host['href']
                return url
        return None


class Webmaster(Wrapper):

    def commit(self):
        with transaction():
            if hasattr(self, 'history_tic'):
                for value in self.history_tic:
                    date = datetime.datetime.strptime(value['date'], '%Y-%m-%d')
                    res = get_or_create(db.session, SeoData, date=date, host_id=self.host.id)
                    res.wm_tic = int(value['value'])

            if hasattr(self, 'indexed'):
                res = get_or_create(db.session, SeoData, date=datetime.date.today(), host_id=self.host.id)
                res.wm_indexed = self.indexed

            if hasattr(self, 'history_indexed'):
                for value in self.history_indexed:
                    date = datetime.datetime.strptime(value['date'], '%Y-%m-%d')
                    res = get_or_create(db.session, SeoData, date=date, host_id=self.host.id)
                    res.wm_indexed = value['value']
            db.session.commit()

    def get_tic(self):
        if self.url:
            url = self.url + '/history/tic'
            rsst = requests.get(url, headers=self.headers, timeout=120)
            soup = BeautifulSoup(rsst.text)
            self.history_tic = [{'date': item['date'], 'value': item.text} for item in soup.findAll('value')]
            return self.history_tic
        return None

    def get_indexed(self):
        if self.url:
            url = self.url + '/indexed/'
            rsst = requests.get(url, headers=self.headers, timeout=120)
            soup = BeautifulSoup(rsst.text)
            self.indexed = 0
            if soup.find('index-count'):
                self.indexed = soup.find('index-count').text
            return self.indexed
        return None

    def get_history_indexed(self):
        if self.url:
            url = self.url + '/history/indexed-urls'
            rsst = requests.get(url, headers=self.headers, timeout=120)
            soup = BeautifulSoup(rsst.text)
            self.history_indexed = [{'date': item['date'], 'value': item.text} for item in soup.findAll('value')]
            return self.history_indexed
        return None

    def get_original_texts(self):
        # WTF к яндексу
        if self.url:
            url = self.url + '/original-texts/'
            rsst = requests.get(url, headers=self.headers, timeout=120)
            soup = BeautifulSoup(rsst.text)
            texts = soup.findAll('original-text')
            return texts
        return None
