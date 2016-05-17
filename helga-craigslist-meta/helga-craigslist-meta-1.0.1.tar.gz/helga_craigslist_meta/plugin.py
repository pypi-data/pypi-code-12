""" Plugin entry point for helga """
import math
from craigslist_scraper.scraper import scrape_url
from helga.plugins import match

TEMPLATE = 'Listing title: {}, price: {}'

@match(r'[A-Za-z]+\.craigslist\.org/.../\S+')
def craigslist_meta(client, channel, nick, message, match):
    """ Return meta information about a listing """
    data = scrape_url('http://' + match[0])
    result = TEMPLATE.format(data.title, data.price)
    for key, value in data.attrs.items():
        result += ', {}: {}'.format(key, value)
    return result
