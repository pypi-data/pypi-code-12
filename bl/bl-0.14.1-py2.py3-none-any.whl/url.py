# -*- coding: utf-8 -*-

import re, urllib.parse
from bl.dict import Dict

# pattern from https://gist.github.com/gruber/249502#gistcomment-1328838
PATTERN = r"""\b((?:[a-z][\w\-]+:(?:\/{1,3}|[a-z0-9%])|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}\/)(?:[^\s()<>]|\((?:[^\s()<>]|(?:\([^\s()<>]+\)))*\))+(?:\((?:[^\s()<>]|(?:\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))"""
REGEXP = re.compile(PATTERN, re.I+re.U)

class URL(Dict):
    """URL object class. Makes handling URLs very easy. Holds the URL in parsed, unquoted form internally.
    Sample usage:
    >>> u = URL('http://blackearth.us:8888/this/is;really?not=something#important')
    >>> u.scheme, u.host, u.path, u.params, u.qargs, u.fragment
    ('http', 'blackearth.us:8888', '/this/is', 'really', {'not': 'something'}, 'important')
    >>> str(u)
    'http://blackearth.us:8888/this/is;really?not=something#important'
    >>> u
    URL('http://blackearth.us:8888/this/is;really?not=something#important')
    >>> u.qstring()
    'not=something'
    >>> u.drop_qarg('not')
    URL('http://blackearth.us:8888/this/is;really#important')
    >>> u                                                 # no change to u 
    URL('http://blackearth.us:8888/this/is;really?not=something#important')
"""

    def __init__(self, url='', scheme=None, host=None, path=None, params=None, 
                fragment=None, query=None, qargs={}):
        """create a URL object from the given url string."""

        # 1. parse the url string with urlparse
        if type(url) == URL:
            pr = urllib.parse.urlparse(str(url))
        else:
            pr = urllib.parse.urlparse(url)

        # 2. deal with parameters
        self.scheme     = scheme or pr.scheme
        self.host       = host or pr.netloc
        self.path       = urllib.parse.unquote(path or pr.path)
        self.params     = params or pr.params
        self.fragment   = fragment or pr.fragment

        # 3. deal with query arguments
        d = Dict(**urllib.parse.parse_qs(query or pr.query))
        for k in d:
            d[k] = d[k][-1]     # only keep the last instance of an argument
            if d[k] in [None, '']: _=d.pop('k')
        self.qargs = d
        for k in qargs.keys():
            if qargs[k] in ['', None]: 
                if k in self.qargs.keys():
                    _=self.qargs.pop(k)
            else:
                self.qargs[k] = qargs[k]

    def __call__(self, **args):
        """return a new url with the given modifications (immutable design)."""
        u = URL(str(self))
        u.update(**args)
        return u

    def qstring(self):
        return urllib.parse.urlencode(self.qargs)

    def no_qargs(self):
        u = URL(**self)
        u.qargs = Dict()
        return u

    def drop_qarg(self, key):
        u = URL(self)
        for k in u.qargs.keys():
            if k == key:
                del(u.qargs[k])
        return u

    def __str__(self):
        pr = (self.scheme, self.host, self.path,
            self.params, self.qstring(), self.fragment)
        s = urllib.parse.urlunparse(pr)
        if s[:2]=='//': s = s[2:]       # strip an empty protocol separator from beginning
        return s

    def quoted(self):
        pr = (self.scheme, self.host, urllib.parse.quote(self.path),
            self.params, self.qstring(), self.fragment)
        return urllib.parse.urlunparse(pr)        

    def unquoted(self):
        pr = (self.scheme, self.host, urllib.parse.unquote(self.path),
            self.params, self.qstring(), self.fragment)
        return urllib.parse.urlunparse(pr)                

    def __repr__(self):
        return """URL('%s')""" % str(self)

    def basename(self):
        """return the basename of the URL's path"""
        return self.path.split('/')[-1]

    def parent(self):
        """return the parent URL, with params, query, and fragment in place"""
        path = '/'.join(self.path.split('/')[:-1])
        s = path.strip('/').split(':')
        if len(s)==2 and s[1]=='':
            return None
        else:
            return self.__class__(self, path=path)

    @classmethod
    def finditer(C, text):
        """search the given text for URLs and return an iterator of matches."""
        return REGEXP.finditer(text)

    @classmethod
    def join(C, *args, **kwargs):
        """join a list of url elements, and include any keyword arguments, as a new URL"""
        u = C('/'.join([str(arg).strip('/') for arg in args]), **kwargs)
        if u.scheme in [None, '']:
            u.path = '/' + u.path
        return u


if __name__=='__main__':
    import doctest
    doctest.testmod()
