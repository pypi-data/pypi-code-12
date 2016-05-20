#-*- coding:utf-8 -*-

import json
import urllib
import requests
import datetime

from .anti_config import db, Visits
from .utils import get_or_create, transaction
from .webmaster import Wrapper

class Metrika(Wrapper):

    def __init__(self, *args, **kwargs):
        super(Metrika, self).__init__(*args, **kwargs)
        self.site_id = self.get_site_number()

    def get_site_number(self):
        """ Получаем данные с счетчиков """
        url = 'http://api-metrika.yandex.ru/counters.json?oauth_token=%s&per_page=1000' %  self.access_token
        resp = requests.get(url, timeout=120)
        data = json.loads(resp.text)
        for item in data['counters']:
            if self.site.strip().lower() in item['site'].strip().lower():
                return item['id']
        return None

    def get_history_yandex_stat(self, days = 7):
        for item in range(1, days + 1):
            self.get_yandex_stat(days1 = item + 1, days2 = item)

    def get_yandex_stat(self, days1 = 2, days2 = 1):
        """ Получаем данные посещаемости """
        if self.site_id:
            arr = {'av':0,
                   'sv':0,
                   'rv':0,
                   'url': self.site,
                   'date1': datetime.date.today() - datetime.timedelta(days = days1),
                   'date2': datetime.date.today() - datetime.timedelta(days = days2),
                    } #  sv - визиты с поисковых систем, rv - переходы с рекламы, av - остальные переходы
            dt = {'id': self.site_id, 'oauth_token': self.access_token}
            dt['date1'] = arr['date1'].strftime('%Y%m%d')
            dt['date2'] = arr['date2'].strftime('%Y%m%d')
            link = 'http://api-metrika.yandex.ru/stat/sources/summary.json?' + urllib.urlencode(dt)
            resp = requests.get(link, timeout=120)
            data = json.loads(resp.text)
            if data['data']:
                arr['sv'] = data['data'][0]['visits']
                if len(data['data']) > 3:
                    arr['rv'] = data['data'][3]['visits']
                for item in data['data']:
                    arr['av'] += item['visits']
                arr['av'] = arr['av'] - arr['rv'] - arr['sv']

            if days1 - days2 == 1:
                with transaction():
                    date = datetime.date.today() - datetime.timedelta(days = days2)
                    res = get_or_create(db.session, Visits, host_id = self.host.id, date = date)
                    res.av = arr['av']
                    res.sv = arr['sv']
                    res.rv = arr['rv']
                    db.session.commit()
            return arr
        return None
