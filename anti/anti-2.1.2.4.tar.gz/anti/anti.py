# -*- coding:utf-8 -*-

import redis
import datetime
import urlparse
import socket
import json
import time
import logging
from contextlib import contextmanager

try:
    from django.conf import settings
except ImportError:
    import config as settings

from bs4 import BeautifulSoup

from .utils import parse_yandex, parse_google
from .mixin import openYandexMixin
from .decorators import fail_counter

MAX_OPEN_LINKS = 50
TIMEOUT = settings.TIMEOUT if hasattr(settings, 'TIMEOUT') else 120


def sendData(string, server, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(TIMEOUT)
    print server + ':' + str(port)
    s.connect((server, port))
    s.send(string)


def getData(string, server, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(TIMEOUT)
    print server + ':' + str(port)
    s.connect((server, port))
    s.send(string)
    data = ''
    text = ''
    now = datetime.datetime.now()

    while True:
        data += s.recv(1024)
        if (datetime.datetime.now() - datetime.timedelta(seconds=TIMEOUT)) > now:
            raise socket.timeout('Fail when get soup')

        if '###end###' in data:
            text = data.replace('###end###', '')
            break
    return BeautifulSoup(text)


def getServer():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(TIMEOUT)
    s.connect(settings.ANTI_BALANCER)
    string = "###GET_SERVER###"
    s.send(string)
    data = ''
    text = ''
    now = datetime.datetime.now()

    while True:
        data += s.recv(1024)
        if (datetime.datetime.now() - datetime.timedelta(seconds=TIMEOUT)) > now:
            raise socket.timeout('All servers is binding')

        if '###end###' in data:
            text = data.replace('###end###', '')
            break
    server, port = text.split(':')
    return text, server, int(port)


class openYandex(openYandexMixin):
    def __init__(self, key):
        self.key = key
        self.rds = redis.Redis(**settings.ANTI_REDIS_CONF)

    @contextmanager
    def ip_port(self):
        self.redis_key, self.server, self.port = getServer()

        try:
            self.state = json.loads(self.rds.get(self.redis_key))
        except:
            self.state = {'counter': 0, 'state': True}

        try:
            yield
        except:
            raise
        finally:
            self.update_state()

    def update_state(self):
        """ Обновление состояния браузера и рестарт в случае надобности """
        if hasattr(self, 'redis_key'):
            self.state['counter'] += 1
            if self.state['counter'] >= MAX_OPEN_LINKS:
                string = '###restart###'
                sendData(string, self.server, self.port)
                time.sleep(7)
                self.state['counter'] = 0
            self.state['state'] = False
            self.rds.set(self.redis_key, json.dumps(self.state))

    @fail_counter
    def get_soup(self, url, save=True, counter=0, normalize=False):
        """ Получение супа в ответе сервера """
        self.url = url
        self.save = save
        self.counter = counter
        self.normalize = normalize
        with self.ip_port():
            parse_url = urlparse.urlparse(url)
            self.hostname = parse_url.hostname
            self.query = parse_url.query
            if isinstance(self.query, unicode):
                self.query = self.query.encode('utf8')

            string = '###split###'.join((url, self.key))
            soup = getData(string, self.server, self.port)

        if save:
            data = self.saveData(soup)
            if normalize:
                return data
        return soup

    def formatData(self, soup):
        """ Формирование данных """
        data = None
        if 'yandex.ru' == self.hostname:
            data = parse_yandex(soup, self.query)
            if data is False:
                logging.warning('ParseYandexError: query is empty or yandex changed layout or yandex response is empty.')
                data = self.get_soup(self.url, self.save, self.counter, self.normalize)
        if 'www.google.ru' == self.hostname:
            data = parse_google(soup, self.query)
        return data

    def saveData(self, soup):
        """ Сохранение в базу """
        data = self.formatData(soup)
        self.rds.set('page:' + self.url, json.dumps(data))
        return data

openGoogle = openYandex
