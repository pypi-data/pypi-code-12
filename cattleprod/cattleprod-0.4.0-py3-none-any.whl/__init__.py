#!/usr/bin/env python

import requests


class RancherObject(object):

    @staticmethod
    def _getranch(rancher_url, path, classname=None):
        tmp = requests.get(rancher_url + "/v1/" + path)
        if tmp.headers.get('Content-Type').find("json") != -1:
            tmp = tmp.json()
            if tmp.get('data') and tmp.get('type') == 'collection':
                # multiple elements returned
                rv = []
                for tmp2 in tmp['data']:
                    rv.append(RancherObject(raw=tmp2, rancher_url=rancher_url, classname=classname))
            elif tmp.get('id') and tmp.get('type'):
                # single element
                rv = RancherObject(raw=tmp, rancher_url=rancher_url, classname=classname)
            else:
                rv = tmp
        else:
            rv = tmp.content
        return rv

    def __init__(self, rancher_url, raw, classname):
        self.raw = raw
        self.name = raw.get("name", None)
        self.id = raw['id']
        self.type = raw['type']
        self.classname = classname if classname else self.type
        self.rancher_url = rancher_url
        for link in raw['links']:
            def get_member(url, path):
                def new_member():
                    return RancherObject._getranch(url, path)
                return new_member
            link_path = raw['links'][link]
            link_path = link_path[link_path.find("v1/")+3:]
            setattr(self, "get_{}".format(link), get_member(rancher_url, link_path))

    def __str__(self):
        name = '{}'.format(self.name) if self.name else 'None'
        return "<Rancher {} {} ({})>".format(self.classname, name, self.id)

    def __repr__(self):
        return self.__str__()

    def links(self):
        return self.raw.get('links', None)

    def get(self, link_target):
        link_path = self.raw['links'][link_target]
        link_path = link_path[link_path.find("v1/")+3:]
        return RancherObject._getranch(self.rancher_url, link_path)


def connect(rancher_url):
    return RancherObject._getranch(rancher_url=rancher_url, path="")
