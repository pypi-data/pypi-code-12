# -*- coding:utf-8 -*-

import re
import datetime
import urllib
import json

from .anti_config import db, Key, Pos, Host, Url

from .utils import get_normal_url, get_normal_quote, parse_google_url


TODAY = datetime.date.today()
YANDEX_URL = 'http://yandex.ru/yandsearch?p=%d&text=%s&site=&rstr=&within=0&numdoc=50&lr=%d'
YANDEX_RANGE = range(2)
GOOGLE_URL = 'https://www.google.ru/search?num=100&q=%s'


class openYandexMixin():
    def get_yandex_cache_pos(self, phrase, lr=213, storage=True):
        """ data = obj.get_yandex_cache_pos(phrase, lr?). Получим позиции по ключевой фразе(первые 100)"""
        phrase_quote = get_normal_quote(phrase)
        res = []
        for i in YANDEX_RANGE:
            url = YANDEX_URL % (i, phrase_quote, lr)
            data = self.rds.get('page:' + url)
            if data:
                res += json.loads(data)
            elif storage:
                res += self.get_soup(url, normalize=True)
        return res

    def get_yandex_date_pos(self, phrase, date, lr=213):
        res = db.session.query(Pos.pos,
                               Key.key,
                               Host.host,
                               Url.url,
                               Pos.search,
                               Pos.lr)\
                        .join(Key).join(Host).join(Url)\
                        .filter(Key.key == phrase, Pos.date == date, Pos.lr == lr).all()
        return res

    def get_google_cache_pos(self, phrase, storage=True):
        phrase_quote = get_normal_quote(phrase)
        url = GOOGLE_URL % phrase_quote
        data = self.rds.get('page:' + url)
        res = []
        if data:
            res = json.loads(data)
        elif storage:
            res = self.get_soup(url, normalize=True)
        return res

    def clear_yandex_cache_pos(self, phrase, lr=213):
        phrase_quote = get_normal_quote(phrase)
        for i in YANDEX_RANGE:
            url = YANDEX_URL % (i, phrase_quote, lr)
            self.rds.delete('page:' + url)

    def clear_google_cache_pos(self, phrase):
        phrase_quote = get_normal_quote(phrase)
        url = GOOGLE_URL % phrase_quote
        self.rds.delete('page:' + url)

    def pages_of_site_in_index_yandex(self, site, pages=None, link=None):
        """ Получение данных по страницам сайта в индексе yandex """
        if pages is None:
            pages = []
        if isinstance(site, unicode):
            site = site.encode('utf8')

        if not link:
            link = u'http://yandex.ru/yandsearch?text=host:%s | host:www.%s&site=&rstr=&within=0&numdoc=50&lr=213'\
                % (urllib.quote_plus(site), urllib.quote_plus(site))
        soup = self.get_soup(link, save=False)
        blocks = soup.find_all(class_='serp-item')
        if blocks:
            for item in blocks:
                tlink = item.find('a', class_='serp-url__link')
                if tlink and not item.find('div', text='Реклама'):
                    host = get_normal_url(tlink['href'])
                    if 'yandex.ru' not in host and 'infected?' not in host:
                        url = item.find('a', class_='serp-item__title-link').get('href')
                        title = item.find('a', class_='serp-item__title-link').text
                        desc = item.find('div', class_='serp-item__text')
                        desc = desc.text if desc else None
                        if url not in [i['url'] for i in pages]:
                            pages.append({'url': url, 'title': title, 'desc': desc})

        link = soup.find('a', class_='pager__item_kind_next')
        if link:
            link = 'http://yandex.ru' + link['href']
            self.pages_of_site_in_index_yandex(site, pages, link)
        return pages

    def pages_of_site_in_index_google(self, site, pages=None, start=0):
        """ Получение данных по страницам сайта в индексе google """
        if pages is None:
            pages = []

        if isinstance(site, unicode):
            site = site.encode('utf8')
        link = 'https://www.google.ru/search?num=100&start=%d&q=site:%s' % (start, urllib.quote_plus(site))
        soup = self.get_soup(link, save=False)

        # Добавляем данные со страницы
        for item in soup.find_all(class_='g'):
            url = item.find('h3', {'class': 'r'}).find('a')['href']
            title = item.find('h3', {'class': 'r'}).find('a').text
            desc = item.find('span', {'class': 'st'}).text
            pages.append({'url': url, 'title': title, 'desc': desc})

        # Проверяем следующую страницу из пагинатора
        test = re.search('Следующая', str(soup))
        if test:
            start += 100
            self.pages_of_site_in_index_google(site, pages, start)
        return pages

    def clear_redis(self):
        """ Очистить базу redis """
        for key in self.rds.keys():
            self.rds.delete(key)

    def load_core(self, phrase, lr=213):
        phrase_quote = get_normal_quote(phrase)
        for i in YANDEX_RANGE:
            url = YANDEX_URL % (i, phrase_quote, lr)
            self.get_soup(url)
        url = GOOGLE_URL % phrase_quote
        self.get_soup(url)
