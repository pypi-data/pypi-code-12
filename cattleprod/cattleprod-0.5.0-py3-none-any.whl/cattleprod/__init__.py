#!/usr/bin/env python

import requests
from dotmap import DotMap


class Rod(DotMap):

    def __init__(self, datadict):
        super(Rod, self).__init__(datadict)
        for item_name in self.links:
            # take care of the links. convert them to get_() methods
            # and bind them to the rancher object
            def _local_get(url):
                def new_member():
                    return poke(url)
                return new_member
            use_url = self.links[item_name]
            #print("get_%-30s() -> %s" % (item_name, use_url))
            object.__setattr__(self,
                               "get_{}".format(item_name),
                               _local_get(use_url))
        for item_name in self.actions:
            # now take care of the actions. convert them to do_() objects
            # and bind them too.
            def _local_do(url):
                def execute(data=None):
                    rsp = requests.post(url, data=data)
                    rsp.raise_for_status()
                    return _convert_to_rod(rsp.json())
                return execute
            use_url = self.actions[item_name]
            #print("do_%-30s -> %s" % (item_name, use_url))
            object.__setattr__(self,
                               "do_{}".format(item_name),
                               _local_do(use_url))

    def __str__(self):
        name = self.name if self.name else 'Unknown'
        return "<Rancher {} {} ({})>".format(self.type, name, self.id)

    def __repr__(self):
        return self.__str__()


def _convert_to_rod(thing):
    if type(thing) is dict and ('type' in thing or 'resourceType' in thing):
        # we *should* have a rancher object
        if thing.get('type') == 'collection':
            # multiple elements returned
            rv = [Rod(thing) for thing in thing['data']]
        else:
            # single element
            rv = Rod(thing)
    else:
        # actually no rancher object
        rv = thing
    return rv


def poke(url):
    """
    Poke the Rancher API. Returns a Rod object instance. Central starting
    point for the cattleprod package.
    :param url: The full Rancher URL to the API endpoint.
    :return: A Rod instance, or anything that the URL returns on a GET request
    """
    # print("poke_rancher.url = " + url)
    tmp = requests.get(url)
    tmp.raise_for_status()
    if tmp.headers.get('Content-Type').find("json") != -1:
        rv = _convert_to_rod(tmp.json())
    else:
        rv = tmp.content
    return rv
