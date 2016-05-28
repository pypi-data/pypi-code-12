"""Low level layer, parsing http://rosalind.info in order to get
information about users

"""

import os
from bs4 import BeautifulSoup
import requests
from urllib.request import urlopen
import pickle


USERNAME_URL = 'http://rosalind.info/users/{}'
FILE_CACHE = 'cache.pkl'
FILE_CACHE = None  # comment to enable dumb cache feature


def problems(username:str) -> iter:
    """Yield problems solved by user with given username in ROSALIND"""
    if FILE_CACHE and os.path.exists(FILE_CACHE):
        with open(FILE_CACHE, 'rb') as fd:
            html = pickle.load(fd)
    else:
        html = _get_page(USERNAME_URL.format(username))
        if FILE_CACHE:
            with open(FILE_CACHE, 'wb') as fd:
                pickle.dump(html, fd)

    problems = _parse_problems(html)
    yield from (problem for problem, is_solved in problems if is_solved)


def _parse_problems(html:str) -> iter:
    """Yield pairs (problem, is_solved) from given rosalind html user page"""
    page = BeautifulSoup(html, 'html.parser')
    for elem in page.find_all(**{'class':'badge'}):
        yield elem.string, elem['class'] == ['badge', 'badge-success']


def _get_page(url:str) -> str:
    """Return raw html of given page"""
    return requests.get(url).text
