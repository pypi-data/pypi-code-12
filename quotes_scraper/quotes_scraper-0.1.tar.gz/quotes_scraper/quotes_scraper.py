"""
Goodreads Quotes Scraper.

Creates quotes from a Goodreads user id.

Joshua Litven 2016.
"""

import re
import sys
from bs4 import BeautifulSoup
import requests

# TODO: Break up scraping


class Quote(dict):
    """Stores the quote data."""

    def __init__(self, text, url, author, author_url, image_url):
        self['text'] = text
        self['url'] = url
        self['author'] = author
        self['author_url'] = author_url
        self['image_url'] = image_url

    def __str__(self):
        s = u'{}\n- {}'.format(self['text'], self['author'])
        return s.encode('utf-8')


def format_text(quote_text):

    text = ''
    for e in quote_text.contents:
        if isinstance(e, basestring):
            text += e.strip() + '\n'
        else:
            break
    text = re.sub(u"  +", u"", text)
    text = text.replace(u'\n\u2015\n', u'')
    return text


def get_image_url(quote_text):

    try:
        image_url = quote_text.parent.find('a').find('img').get('src')
        image_url = image_url.replace('p2', 'p4')  # grab larger image
    except:
        image_url = ''
    return image_url


# TODO: Fix Shaupernhaer quote
def create_quotes(url):

    res = requests.get(url=url)
    res.raise_for_status()
    content = res.content
    soup = BeautifulSoup(content, "lxml")

    # Get rid of html breaks
    for e in soup.findAll('br'):
        e.extract()

    quote_texts = soup.findAll('div', attrs={'class': 'quoteText'})
    quote_footers = soup.findAll('div', attrs={'class': 'right'})

    quotes = []
    for (quote_text, quote_footer) in zip(quote_texts, quote_footers):

        text = format_text(quote_text)
        quote_link = quote_text.find('a')
        author_url = quote_link.get('href')
        author = quote_link.getText()
        footer_link = quote_footer.find('a')
        quote_url = footer_link.get('href')
        image_url = get_image_url(quote_text)
        quote = Quote(text, quote_url, author, author_url, image_url)
        quotes.append(quote)

    return quotes


def gen_goodreads_quote_pages(user_id):

    url = "https://www.goodreads.com/quotes/list/{}".format(str(user_id))
    yield url
    page = 2
    while True:
        yield url + '?page=' + str(page)
        page += 1


def scrape_quotes(user_id, num_quotes=100):
    print 'Scraping Goodread for quotes...'
    quotes = []
    for page in gen_goodreads_quote_pages(user_id):
        page_quotes = create_quotes(page)
        if page_quotes:
            quotes.extend(page_quotes)
        else:
            break
        if len(quotes) >= num_quotes:
            quotes = quotes[:num_quotes]
            break
    return quotes


def main():
    if len(sys.argv) > 1:
        quotes = scrape_quotes(user_id=sys.argv[1])
    else:
        print 'Usage: {} user_id'.format(sys.argv[0])
        sys.exit()

    for quote in quotes:
        print quote

if __name__ == '__main__':

    main()
