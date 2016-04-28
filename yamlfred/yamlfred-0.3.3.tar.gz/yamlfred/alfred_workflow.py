# -*- coding: utf-8 -*-

import os.path
import uuid

import six
import yaml

from yamlfred.utils import (
    text_representer, text_constructor,
    Include, include_representer, include_constructor,
)

yaml.add_representer(six.text_type, text_representer)
yaml.add_constructor("tag:yaml.org,2002:str", text_constructor)
yaml.add_representer(Include, include_representer)
yaml.add_constructor('!include', include_constructor)

import plistlib
from yamlfred.utils import translate_plist, cd

from yamlfred.alfred_connections import AlfredConnections
from yamlfred.alfred_object import AlfredObject


class AlfredWorkflow(object):

    def __init__(self):
        self.readme = ""
        self.prop = {
            "name": str(uuid.uuid4()),
            "description": "",
            "bundleid": "",
            "createdby": "",
            "webaddress": ""
        }
        self.connections = None
        self.objects = []
        return

    def load_plist(self, path='info.plist'):
        plist = plistlib.readPlist(path)
        info = translate_plist(plist)
        self.readme = info.get("readme")
        for key in info.keys():
            self.prop[key] = info[key]
        for obj in info["objects"]:
            self.objects.append(AlfredObject(obj))
        self.connections = AlfredConnections(self.objects, info["connections"])
        return

    def load_yaml(self, path='workflow.yml'):
        dirname = os.path.dirname(path) if os.path.dirname(path) else '.'
        with cd(dirname), open(path, 'r') as f:
            wf_yaml = yaml.load(f.read())
        for key in wf_yaml.keys():
            self.prop[key] = wf_yaml[key]
        for obj in wf_yaml["objects"]:
            new_obj = {'uid': str(uuid.uuid4())}
            new_obj.update(obj)
            uid = new_obj['uid']
            if 'uidata' not in self.prop:
                self.prop['uidata'] = {}
            if uid not in self.prop['uidata']:
                cat = new_obj['type'].split('.')[3]
                uids = [o.prop['uid'] for o in self.objects if cat in o.type]
                if uids:
                    max_ypos = max(
                        self.prop['uidata'][u]['ypos'] for u in uids
                    )
                    self.prop['uidata'][uid] = {'ypos': max_ypos + 120}
                else:
                    self.prop['uidata'][uid] = {'ypos': 30}
            self.objects.append(AlfredObject(new_obj))
        self.connections = AlfredConnections(
            self.objects, wf_yaml["connections"]
        )
        return

    def dump_plist(self, path='info.plist'):
        dic = dict(self.prop.items())
        dic["objects"] = [obj.prop for obj in self.objects]
        if self.connections:
            dic["connections"] = self.connections.items
        plistlib.writePlist(dic, path)
        return

    def dump_workflow(self, path='workflow.yml', readme_path='README', script_dir='.'):
        dic = dict(self.prop.items())
        dic["objects"] = [obj.dump(script_dir) for obj in self.objects]
        if self.connections:
            dic["connections"] = self.connections.dump()
        if self.readme:
            with open(readme_path, 'w') as f:
                f.write(self.readme)
            dic['readme'] = Include(readme_path)
        with open(path, 'w') as f:
            yaml.dump(dic, f, default_flow_style=False)
        return
