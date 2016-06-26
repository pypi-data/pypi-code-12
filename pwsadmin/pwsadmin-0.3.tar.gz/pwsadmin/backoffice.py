from bs4 import BeautifulSoup
import os
from requests import Session

clean_els = lambda els: [str(el.get_text().strip()) for el in els]

def clean_money(money):
    sign = 1
    if money[0] == '(':
        sign = -1
        money = money[1:-1]
    return sign * float(money.replace(',', '').replace('$', ''))

def expand_date(date, prefix):
    keys = ['year', 'month', 'day']
    if prefix:
        keys = map(lambda x: prefix + x, keys)

    return dict(zip(keys, map(int, date.split('-'))))

def txn_transform(txn):
    return {
        'winnings': clean_money(txn['Winnings']),
        'amount': clean_money(txn['Amount']),
        'bonus': clean_money(txn['Bonus']),
        'deposits': clean_money(txn['Deposits']),
        'winnings': clean_money(txn['Winnings']),
        'game': txn['Game'],
        'game_id': int(txn['Game #']),
        'hall_id': int(txn['Hall #']),
        'txn_id': int(txn['ID']),
        'type': txn['Type'],
    }

def room_transform(room):
    return {
        'id': int(room['ID']),
        'name': room['Name'],
        'filter': room['filter'],
        'games_played': int(room['gamesplayed']),
        'players': int(room['players']),
        'port': int(room['port']),
        'skin_name': room['skinname'],
        'state': room['start/stop']
    }

def dbinfo_transform(room):
    return {
        'records': int(room['Records']),
        'speed': int(room['Speed (ms)']),
        'name': room['Table Name']
    }

class PWSAdmin(object):
    def __init__(self, endpoint, username, password):
        self.endpoint = endpoint
        self.credentials = {'ID': username, 'password': password}
        self.session = None

    def _page(self, page):
        return self.endpoint + page

    def dbinfo(self):
        soup = self.fetch_soup('dbmaint.asp')
        tables = self.table(soup, 'table', simple=True)
        return map(dbinfo_transform, tables)

    def fetch_soup(self, page):
        r = self.session.get(self._page(page))
        if r.status_code == 302:
            raise Exception('Redirected while fetching ' + page)
        return BeautifulSoup(r.content, 'lxml')

    def post_soup(self, page, data=None):
        r = self.session.post(self._page(page), data=data)
        if r.status_code == 302:
            raise Exception('Redirected while fetching ' + page)
        return BeautifulSoup(r.content, 'lxml')

    def login(self):
        self.session = Session()
        self.session.post(self._page('layout_menu.asp'), data=self.credentials)

    def rooms(self):
        table = self.table(self.fetch_soup('mproom.asp'), 'table.tablesorter')
        return map(room_transform, table)

    def table(self, soup, selector, simple=False):
        tables = soup.select(selector)[0]

        if simple:
            rows = tables.select('tr')
            headers = clean_els(rows[0].select('td'))
            rows = rows[1:]
        else:
            rows = tables.select('tbody tr')
            headers = clean_els(tables.select('thead tr th'))

        return map(lambda r: dict(zip(headers, clean_els(r.select('td')))), rows)

    def user_transactions(self, userid, start, end):
        params = dict(expand_date(start, 'start').items() + expand_date(end, 'end').items())
        params = (params.items() + {
            'id': userid,
            'action': 'SEARCH',
            'Submit': 'Submit',
            'username': ''
        }.items())

        soup = self.post_soup('listtransactions.asp', params)
        return map(txn_transform, self.table(soup, 'table.tablesorter'))
