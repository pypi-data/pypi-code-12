#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module: eri.html.utils.py
Author: zlamberty
Created: 2016-05-23

Description:
    utility functions for scraping

Usage:
    <usage>

"""

import os as _os
import re as _re

import lxml.html as _lh
import requests as _requests

import eri.logging as _logging


# ----------------------------- #
#   Module Constants            #
# ----------------------------- #

_TMP = _os.path.join(_os.sep, 'var', 'data', 'eri_cache')

_logging.getLogger('requests').setLevel(_logging.WARNING)
_logger = _logging.getLogger(__name__)
_logging.configure()


# ----------------------------- #
#   utils                       #
# ----------------------------- #

class ScrapeError(Exception):
    def __init__(self, msg):
        _logger.error(msg)
        super().__init__(msg)


def root2bodytext(root):
    """take a root lxml.html element and return cleaned-up text items"""
    avoidNodeTypes = [
        'script',
        'noscript',
        'style',
        'title',
        'header',
        'comments',
        'nav',
        'aside',  # blogspot
    ]
    avoidIds = [
        "header",
        "footer",
        "footer-wrp",
        "nav",
        "subnav",
        "sidebar",
        "slidedown",
        "usermenu",
        "notes",  # tumblr
        "comments",  # blogspot
        "transporter",  # blogspot
    ]
    avoidIds = ["*[@id='{}']".format(_) for _ in avoidIds]
    avoidClasses = [
        "comments",
        "banner",
        "skiplinkcontainer",  # wikia
        "hidden",  # wikia
        "references",  # wikia
        "navbox",  # wikia
        "printheader",  # wikia
        "printfooter",  # wikia
        "slideout-menu",  # collider.com
    ]
    avoidClasses = [
        "*[contains(concat(' ', @class, ' '), ' {} ')]".format(_)
        for _ in avoidClasses
    ]
    avoidElems = avoidNodeTypes + avoidIds + avoidClasses
    avoidString = "|".join([
        'ancestor-or-self::{}'.format(ae) for ae in avoidElems
    ])
    textelems = root.xpath("//body//*[not({})]/text()".format(avoidString))
    textelems = [te.strip() for te in textelems]
    return ' '.join(_ for _ in textelems if _)


def url2root(url, params={'timeout': 5.0}, cachedir=_TMP, forcerefresh=False):
    """fetch urls from source or cache and return converted lxml objects

    args:
        url: url to fetch
        params: dict of params to be passed to requests.get
        cacheDir: directory to/from which cache files will be written/read
        forcerefresh: if True, ignore any cached versions and go straight to
            source (will overwrite cached versions with result)

    returns:
        lxml.html root element of the parsed html text

    throws:
        scrapers.utils.ScrapeError:
            + page is a known 404
            + page is a known timeout

    """
    if not _os.path.isdir(cachedir):
        raise ScrapeError(
            'local cache directory {} does not exist'.format(cachedir)
        )

    # make the local name friendlier
    l = _re.sub(r'^https?://', '', url).replace('/', '_s_')
    localfile = _os.path.join(cachedir, 'local.{}.html'.format(l))

    if forcerefresh:
        # try the web now; if that works, save it and return it
        _logger.debug("fetching html for url {}".format(url))
        try:
            resp = _requests.get(url, params)
            assert resp.ok
            htext = resp.text
            with open(localfile, 'w') as f:
                f.write(htext)
            return _lh.fromstring(htext)
        except AssertionError:
            # retain 404 information for parsed urls
            with open(localfile, 'w') as f:
                f.write('404')
            raise ScrapeError('url returned 404')
        except _requests.exceptions.ConnectionError:
            # retain timeout information for parsed urls
            with open(localfile, 'w') as f:
                f.write('TIMEOUT')
            raise ScrapeError('url timed out')
        except:
            raise ScrapeError("Couldn't scrape the url {}".format(url))
    else:
        _logger.debug("attempting to load cached html for url {}".format(url))
        try:
            with open(localfile, 'r') as f:
                s = f.read()
            _logger.debug("cached version found")

            if s == '404':
                raise ScrapeError('Previously scraped 404')
            elif s == 'TIMEOUT':
                raise ScrapeError('Previously scraped timeout')
            else:
                return _lh.fromstring(s)
        except FileNotFoundError:
            _logger.debug("no local cache, forcing web request")
            return url2root(
                url=url, params=params, cachedir=cachedir, forcerefresh=True
            )
