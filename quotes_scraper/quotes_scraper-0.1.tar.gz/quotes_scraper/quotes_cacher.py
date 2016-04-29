"""
Quotes Cacher.

Cache quotes, stored as dictionaries in a .py file.

Joshua Litven 2016.
"""

import imp
import os
import pprint
from quotes_scraper import scrape_quotes


def load_cached_quotes():
    """Return quotes in cache."""
    print 'Loading cached quotes...'
    module = imp.load_source('my_quotes',
                             get_quotes_file())
    quotes = module.quotes
    return quotes


def update_cached_quotes():
    """Scrape Goodreads quotes and stores in cache."""
    print 'Updating cached quotes...'
    user_id = my_user_id()
    quotes = scrape_quotes(user_id)
    with open(get_quotes_file(), 'w') as f:
        f.write('quotes = ' + pprint.pformat(quotes))


def my_user_id():
    return '27405185'


def get_data_dir():
    dir_name = 'quotes'
    path = os.getenv("HOME")
    dir_path = os.path.join(path, dir_name)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    return dir_path


def get_quotes_file():
    dir_name = get_data_dir()
    return os.path.join(dir_name, 'my_quotes.py')
