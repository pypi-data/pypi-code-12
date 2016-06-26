from bs4 import BeautifulSoup
import os
from requests import Session

clean_els = lambda els: [str(el.get_text().strip()) for el in els]

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

class PWSAdmin(object):
    def __init__(self, endpoint, username, password):
        self.endpoint = endpoint
        self.credentials = {'ID': username, 'password': password}
        self.session = None

    def _page(self, page):
        return self.endpoint + page

    def fetch_soup(self, page):
        r = self.session.get(self._page(page))
        if r.status_code == 302:
            raise Exception('Redirected while fetching ' + page)
        return BeautifulSoup(r.content, 'lxml')

    def login(self):
        self.session = Session()
        self.session.post(self._page('layout_menu.asp'), data=self.credentials)

    def rooms(self):
        table = self.table(self.fetch_soup('mproom.asp'), 'table.tablesorter')
        return map(room_transform, table)

    def table(self, soup, selector):
        tables = soup.select(selector)[0]

        rows = tables.select('tbody tr')
        headers = clean_els(tables.select('thead tr th'))
        if not headers:
            headers = clean_els(rows[0])
            rows = rows[1:]

        return map(lambda r: dict(zip(headers, clean_els(r.select('td')))), rows)
