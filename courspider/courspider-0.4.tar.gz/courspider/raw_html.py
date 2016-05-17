import re

from html import unescape
from urllib import request


# regex used to remove comments from the raw html
# _comments = re.compile('\\s*<!--\[if.*?\]>.*?<!\[endif\]-->\\s*', re.DOTALL)
_comments = re.compile('\\s*<!--.*?-*>.*?<-*.*?-->\\s*', re.DOTALL)

_empty_tags = re.compile('<(.*?)>\\s*<\/\\1>', re.DOTALL)

def get_html(url):
    """
    Retrive the unescaped html string at the give url

    :param url: The url where the html resides
    :type url: str
    :return: The raw html string
    :rtype: str
    """
    with request.urlopen(url) as response:
        print("reading raw html from {}".format(url))
        html = response.read()

    print("decoding and refactoring raw html")
    # decode and unescape the raw html
    html = unescape(html.decode('utf8'))

    # the unescape function turns &nbsp; to some different
    # white space characters, so replace with usual ones
    html = html.replace(' ', ' ')

    # remove comments
    html = _comments.sub("", html)

    # remove empty tags that contain no data
    html = _empty_tags.sub("", html)

    return html
