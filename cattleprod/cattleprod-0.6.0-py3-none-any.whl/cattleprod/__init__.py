#!/usr/bin/env python

import requests
from dotmap import DotMap

from functools import partial


class Rod(DotMap):

    def __init__(self, datadict, **req_args):
        super(Rod, self).__init__(datadict)
        for item_name in self.links:
            # take care of the links. convert them to get_() methods
            # and bind them to the rancher object
            use_url = self.links[item_name]
            object.__setattr__(self,
                               "get_{}".format(item_name),
                               partial(poke, use_url,
                                       **req_args))
        for item_name in self.actions:
            # now take care of the actions. convert them to do_() objects
            # and bind them too.
            use_url = self.actions[item_name]
            object.__setattr__(self,
                               "do_{}".format(item_name),
                               partial(poke, use_url,
                                       __method__='POST',
                                       **req_args))

    def __str__(self):
        name = self.name if self.name else 'Unknown'
        return "<Rancher {} {} ({})>".format(self.type, name, self.id)

    def __repr__(self):
        return self.__str__()


def _convert_to_rod(thing, **req_args):
    # make sure we can also process
    if type(thing) is dict and ('type' in thing or 'resourceType' in thing):
        # we *should* have a rancher object
        if thing.get('type') == 'collection':
            # multiple elements returned
            rv = [Rod(thing, **req_args) for thing in thing['data']]
        else:
            # single element
            rv = Rod(thing, **req_args)
    else:
        # actually no rancher object
        rv = thing
    return rv


def poke(url, accesskey=None, secretkey=None, __method__='GET', **req_args):
    """
    Poke the Rancher API. Returns a Rod object instance. Central starting
    point for the cattleprod package.
    :param url: The full Rancher URL to the API endpoint.
    :param accesskey: The rancher access key, optional.
    :param secretkey: The rancher secret key, optional.
    :param __method__: Internal method, don't use!
    :param req_args: Arguments which are passed directly to the requests API.
    The accesskey / secretkey values have precedence before simple auth
    objects defined in here.
    :return: A Rod instance, or anything that the URL returns on a GET request
    """
    if accesskey and secretkey:
        req_args['auth'] = (accesskey, secretkey)
    tmp = requests.request(__method__.lower(), url, **req_args)
    tmp.raise_for_status()
    if tmp.headers.get('Content-Type').find("json") != -1:
        rv = _convert_to_rod(tmp.json(), **req_args)
    else:
        rv = tmp.content
    return rv
