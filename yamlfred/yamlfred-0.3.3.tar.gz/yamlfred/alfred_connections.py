# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from yamlfred.utils import remove_default, merge_dicts

link_default = {
    "modifiers": "",
    "modifiersubtext": "",
}


class AlfredConnections(object):

    def __init__(self, objects, dic):
        self.items = {}
        for obj in objects:
            uid = obj.prop['uid']
            if uid not in self.items:
                self.items[uid] = []
        for uid, links in dic.items():
            if links:
                self.items[uid] = [
                    merge_dicts(link, link_default) for link in links
                ]
            else:
                self.items[uid] = []
        return

    def dump(self):
        prop = {}
        for key, links in self.items.items():
            if not links:
                prop[key] = []
                continue
            prop[key] = [remove_default(link, link_default) for link in links]
        return prop
