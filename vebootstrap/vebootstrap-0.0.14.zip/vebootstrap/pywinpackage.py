# -*- coding: utf-8 -*-
import os
import sys
import ast
import codecs
import re
import platform
try:
    from urllib.parse import urlparse, urlencode
    from urllib.request import urlopen, Request
    from urllib.error import HTTPError
except ImportError:
    from urlparse import urlparse
    from urllib import urlencode
    from urllib2 import urlopen, Request, HTTPError
try:
    from html.parser import HTMLParser
except ImportError:
    from HTMLParser import HTMLParser
try:
    chr = unichr
except:
    pass


BASE_URL = "http://www.lfd.uci.edu/~gohlke/pythonlibs/"


class Locator(object):
    @staticmethod
    def dl1(ml, mi):
        ot = ""
        for j in range(len(mi)):
            ot += chr(ml[ord(mi[j])-48])
        return ot

    @staticmethod
    def dl(ml, mi):
        """
        >>> Locator.dl([52,105,55,116,45,104,50,112,57,99,109,97,46,101,100,122,121,120,54,110,119,115,95,108,51,47,49,111], 'A:E5?132I7@D1CH646J8497624CKC=4D1CF;:>B0<D5G')
        xmshzit7/pywin32-219-cp27-none-win_amd64.whl
        """
        return Locator.dl1(ml, mi.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&'))


def http_get(url, stream=False):
    req = Request(url)
    req.add_header("User-Agent",
            "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:41.0) Gecko/20100101 Firefox/41.0")
    req.add_header("Accept",
            "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8")
    req.add_header("Accept-Language",
            "ja,en-US;q=0.7,en;q=0.3")
    req.add_header("Referer", BASE_URL)
    return urlopen(req)


def http_save(url, filename=None):
    if not filename:
        filename = os.path.basename(url)
    tmp_filename = filename + ".tmp"
    try:
        with open(tmp_filename, 'wb') as handle:
            response = http_get(url, stream=True)
            while True:
                block = response.read(8192)
                if not block:
                    break
                handle.write(block)
        os.rename(tmp_filename, filename)
    except BaseException as e:
        if os.access(tmp_filename, os.F_OK):
            os.unlink(tmp_filename)
        raise e
    return filename


def parse_requirements(filename="requirements.txt"):
    regex = re.compile(u'^#\\s*windows\\s*:\\s*(?P<package_name>.+)')
    pywin_packages = []
    with codecs.open(filename, "rb", encoding="utf8") as handle:
        for i, line in enumerate(handle):
            line = line.strip()
            match = regex.search(line)
            if match:
                pywin_packages.append((i + 1, match.group('package_name')))
    return pywin_packages



class PackageNotFoundException(Exception):
    def __init__(self, candidates):
        self.candidates = candidates


class PyWinPackages(object):

    def __init__(self, cache_dir=""):
        self.cache_dir = cache_dir

    def list(self):
        regex = re.compile(u'(?P<data>\\(.+\\))')
        parser = PyWinPackagesHTMLParser()
        parser.feed(http_get(BASE_URL).read().decode('utf-8'))
        packages = []
        for filename, onclick in parser.packages:
            package_name = filename.replace(u'\u2011', u'-')
            match = regex.search(onclick)
            ml, mi = ast.literal_eval(match.group('data'))
            download_url = Locator.dl(ml, mi)
            packages.append((package_name, BASE_URL + download_url))
        return packages

    def specify(self, install_name):
        install_name = install_name.lower()
        bit = self.platform_bit()
        package_found = []
        for filename, url in self.list():
            package_name, version, pyver = filename.split(u"-", 2)
            package_name = package_name.lower()
            if install_name in (package_name, package_name.replace(u"_", u"-")):
                package_found.append(filename)
                if pyver.startswith(u"cp{0}{1}".format(sys.version_info[0], sys.version_info[1])):
                    if bit in filename:
                        return (filename, url)

        raise PackageNotFoundException(package_found)

    def download(self, install_name):
        filename, url = self.specify(install_name)
        download_path = os.path.join(self.cache_dir, filename)
        if os.access(download_path, os.F_OK):
            return download_path
        return http_save(url, download_path)

    def platform_bit(self):
        bit, platform_name = platform.architecture()
        if bit == '64bit':
            return "amd64"
        else:
            return "win32"


class PyWinPackagesHTMLParser(HTMLParser):
    def __init__(self, *args, **kwargs):
        HTMLParser.__init__(self, *args, **kwargs)
        self.tmp_onclick = u""
        self.tmp_data = []
        self.packages = []
        self.inner_a = False

    def handle_starttag(self, tag, attrs):
        if tag != u'a':
            self.inner_a = False
            return

        self.tmp_onclick = ([val for key, val in attrs if key==u'onclick'] or [u""])[0]
        if self.tmp_onclick:
            self.inner_a = True

    def handle_data(self, data):
        if self.inner_a:
            self.tmp_data.append(data)

    def handle_charref(self, ref):
        if self.inner_a:
            self.tmp_data.append(chr(int(ref)))

    def handle_entityref(self, name):
        if self.inner_a:
            self.tmp_data.append(name)

    def handle_endtag(self, tag):
        if self.inner_a:
            self.packages.append((u"".join(self.tmp_data), self.tmp_onclick))
            self.tmp_data = []
            self.tmp_onclick = u""

        self.inner_a = False

