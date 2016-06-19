# -*- coding: utf-8 -*-
import requests
import settings as local_settings


class Pynger:

    def __init__(self, sitemap_url, PING_URLS=None):
        if PING_URLS is None:
            self.PING_URLS = local_settings.PING_URLS
        else:
            self.PING_URLS = PING_URLS
        self.sitemap_url = sitemap_url

    def ping(self, name):
        ping_url = self.PING_URLS[name] % self.sitemap_url
        r = requests.get(url=ping_url)
        return r.status_code

    def ping_all(self):
        results = {}
        for key in self.PING_URLS.keys():
            r = self.ping(name=key)
            results[key] = r

        return results



