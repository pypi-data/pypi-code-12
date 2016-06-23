# -*- coding: utf-8 -*-

"""
    tickets.movies
    ~~~~~~~~~~~~~~

    Movies model.
"""

import requests
from prettytable import PrettyTable


QUERY_URL = 'http://58921.com/'


class HotAndComingMovies(object):

    """Docstring for HotAndComingMovies. """

    header = '电影名称 累计票房 即将上映 日期'

    def __init__(self):
        """TODO: to be defined1. """
