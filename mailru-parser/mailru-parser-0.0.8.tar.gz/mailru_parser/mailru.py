# -*- coding:utf-8 -*-
import json
import re
import unicodedata
from urllib import quote, unquote
from urlparse import urlparse, urlunsplit, urlsplit

from mailru_parser.exceptions import EmptySerp, MatchCaptchaError


class MailRuParser(object):
    json_data_re = re.compile('.*?go.dataJson\s*=\s*(.*?);\s*</script>', re.DOTALL)

    params_regexr = re.U | re.M | re.DOTALL | re.I
    captcha_re = {
        'captcha': re.compile('<img src="(/ar_captcha\?id=.*?)"', params_regexr),
        'sqid': re.compile('<input.*?name=\"sqid\".*?value=\"([^\"]+)\".*?>', params_regexr),
        'sf': re.compile('<input.*?name=\"back\".*?value=\"([^\"]+)\".*?>', params_regexr),
        'errback': re.compile('<input.*?name=\"errback\".*?value=\"([^\"]+)\".*?>', params_regexr),
        'q': re.compile('<input.*?name=\"q\".*?value=\"([^\"]+)\".*?>', params_regexr)
    }

    captcha_image_url = "http://go.mail.ru{image_url}"


    def __init__(self, content, snippet_fileds=('d', 'p', 'u', 't', 's', 'm')):
        self.content = to_unicode(content)
        self.snippet_fileds = snippet_fileds

        self._json_data = None

    def get_serp(self):
        if self.is_not_found():
            return {'pc': 0, 'sn': []}

        pagecount = self.get_pagecount()
        snippets = self.get_snippets()

        if not snippets:
            raise EmptySerp()

        return {'pc': pagecount, 'sn': snippets}

    def is_not_found(self):
        return self.json_data['serp']['count_show'] == 0 and not self.is_blocked()

    def is_blocked(self):
        return self.json_data['antirobot']['blocked']

    def get_pagecount(self):
        return self.json_data['serp']['count_show']

    def get_captcha_data(self):
        if not self.json_data['antirobot']['blocked']:
            return

        qid =self.json_data['antirobot']['qid']
        url_image = 'http://go.mail.ru/ar_captcha?id={0}'.format(
            self.json_data['antirobot']['qid']
        )

        return {
            'url': url_image,
            'sqid': qid,
            'ajax': '1',
        }

    def get_snippets(self):
        serp = self.json_data['serp']['results']
        serp.sort(key=lambda x: x['number'])

        snippets = []
        position = 0
        for snippet in serp:
            parsed_snippet = self._parse_snippet(snippet)
            if not parsed_snippet:
                continue
            position += 1
            parsed_snippet['p'] = position
            snippets.append(parsed_snippet)
        return snippets

    def _parse_snippet(self, raw_snippet):
        if 'smack_type' in raw_snippet:
            return {}

        title = raw_snippet['title']
        url = raw_snippet['url']
        if not url:
            return {}

        try:
            domain = get_full_domain_without_scheme(url)
        except UnicodeError as e:
            raise e

        snippet = {
            'd': domain,  # domain
            'u': url,  # url
            'm': self._is_map_snippet(raw_snippet),  # map
            't': None,  # title snippet
            's': None,  # body snippet
        }
        if 't' in self.snippet_fileds:
            snippet['t'] = title
        if 's' in self.snippet_fileds:
            snippet['s'] = raw_snippet['passage']

        return snippet

    def _is_map_snippet(self, raw_snippet):
        return False

    @property
    def json_data(self):
        if self._json_data:
            return self._json_data

        match = self.json_data_re.match(self.content)
        if not match:
            raise Exception('no json data in response')

        self._json_data = json.loads(match.group(1))
        return self._json_data


def to_unicode(content, from_charset=None):
    u"""Безопасное приведение к юникоду

    :type  content: str
    :param content: текст
    :type  from_charset: str
    :param from_charset: Кодировка исходного текста

    :rtype: unicode
    :returns: текст, преобразованный в юникод
    """
    if type(content) == unicode:
        return content

    charsets = {
        'utf-8' : 'utf8',
        'utf8' : 'utf8',
        'cp1251' : 'cp1251',
        'cp-1251' : 'cp1251',
        'windows-1251' : 'cp1251',
        'win-1251' : 'cp1251',
        '1251' : 'cp1251',
        'русdows-1251': 'cp1251',
        'koi8-r' : 'koi8-r'
    }
    if type(from_charset) in (str, unicode):
        from_charset = str(from_charset.lower())

    try:
        from_charset = charsets[from_charset]
        return unicode(content, encoding=from_charset)

    except KeyError:
        for from_charset in ('utf8', 'cp1251', 'koi8-r', None):
            try:
                if from_charset is not None:
                    return unicode(content, encoding=from_charset)
                else:
                    return unicode(content)
            except UnicodeError:
                continue

        raise UnicodeError('Can not be converted to Unicode')

    except UnicodeError:
        return unicode(content, encoding=from_charset, errors='ignore')

def normalize(url, charset='utf-8'):
    def _clean(string):
        string = unicode(unquote(string), 'utf-8', 'replace')
        return unicodedata.normalize('NFC', string).encode('utf-8')

    default_port = {
        'ftp': 21,
        'telnet': 23,
        'http': 80,
        'gopher': 70,
        'news': 119,
        'nntp': 119,
        'prospero': 191,
        'https': 443,
        'snews': 563,
        'snntp': 563,
    }

    if isinstance(url, unicode):
        url = url.encode(charset, 'ignore')

    if url[0] not in ['/', '-'] and ':' not in url[:7]:
        url = 'http://' + url

    url = url.replace('#!', '?_escaped_fragment_=')

    scheme, auth, path, query, fragment = urlsplit(url.strip())
    (userinfo, host, port) = re.search('([^@]*@)?([^:]*):?(.*)', auth).groups()

    scheme = scheme.lower()

    host = host.lower()
    if host and host[-1] == '.':
        host = host[:-1]
        # take care about IDN domains
    try:
        host = host.decode(charset).encode('idna')  # IDN -> ACE
    except Exception:
        host = host.decode(charset)

    path = quote(_clean(path), "~:/?#[]@!$&'()*+,;=")
    fragment = quote(_clean(fragment), "~")

    query = "&".join(["=".join([quote(_clean(t), "~:/?#[]@!$'()*+,;=") for t in q.split("=", 1)]) for q in query.split("&")])

    if scheme in ["", "http", "https", "ftp", "file"]:
        output = []
        for part in path.split('/'):
            if part == "":
                if not output:
                    output.append(part)
            elif part == ".":
                pass
            elif part == "..":
                if len(output) > 1:
                    output.pop()
            else:
                output.append(part)
        if part in ["", ".", ".."]:
            output.append("")
        path = '/'.join(output)

    if userinfo in ["@", ":@"]:
        userinfo = ""

    if path == "" and scheme in ["http", "https", "ftp", "file"]:
        path = "/"

    if port and scheme in default_port.keys():
        if port.isdigit():
            port = str(int(port))
            if int(port) == default_port[scheme]:
                port = ''

    auth = (userinfo or "") + host
    if port:
        auth += ":" + port
    if url.endswith("#") and query == "" and fragment == "":
        path += "#"
    return urlunsplit((scheme, auth, path, query, fragment))


def get_full_domain_without_scheme(url):
    absolute_url = normalize(url).replace('//www.', '//')
    parsed = urlparse(absolute_url)
    return urlunsplit(('', parsed.netloc, '', '', '')).replace('//', '')
