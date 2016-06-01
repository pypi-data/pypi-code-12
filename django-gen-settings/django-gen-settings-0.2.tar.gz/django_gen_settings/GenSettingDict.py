import copy
import collections
from json import JSONEncoder, JSONDecoder

import pdb


def flatten(d, parent_key='', sep='.'):
    """
    flattens a dict, the single key words are seperated by sep
    :param d: input dict
    :param parent_key:
    :param sep: seperator for the flattend keys
    :return:
    """
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def overlaysettings(settingsdict1, settingsdict2):
    """
    values in settingsdict1 will be overlayed by the settings of settingsdict2
    """
    c = copy.deepcopy(settingsdict1)
    for k, i in settingsdict2.items():
        if isinstance(i, GenSettingDict):       # its a node
            if k not in c.keys():
                c.update({k: i})
            else:
                subsetting = overlaysettings(c[k], i)
                c[k].update(subsetting)
        elif isinstance(i, GenSettingBase):     # its a leaf
            j = copy.deepcopy(i)
            if k not in c.keys():
                c.update({k: j})
            else:  # override but keep description /choices if not overwritten
                if c[k]._overrideable:
                    if j._description == '':
                        j._description = c[k]._description
                    if j._allowed_values == '':
                        j._allowed_values = c[k]._allowed_values
                    j._overwritten = True
                    c.update({k: j})
                    #TODO maybe raise an error if not overrideable
        else:
            raise TypeError("Unsupported type " + str(type(i)))
    return c


def getvaluedict(settingsdict):
    """
    returns a dict with only the values of the settings
    """
    ret = {}
    if isinstance(settingsdict, GenSettingBase):
        return {"value": settingsdict.value}

    for k, i in settingsdict.items():
        if isinstance(i, GenSettingDict):
            ret.update({k: getvaluedict(i)})
        elif isinstance(i, GenSettingBase):
            ret.update({k: i.value})
        else:
            raise TypeError("Unsupported type " + str(type(i)))
    return ret


class GenSettingDict(dict):
    """
    represents a setting dict
    """
    def __init__(self, init={}):
        dict.__init__(self, init)

    def _getfromdict(self, mapList):
        return reduce(lambda d, k: d.get(k), mapList, self)

    def settingexists(self, name):
        """
        checks if a given setting ( key ) exists
        :param name: name of the setting
        :return: true if the setting exist
        """
        nametoken = name.split(".")
        return reduce(lambda d, k: d.get(k), nametoken, self)

    def getsettinginstance(self, name):
        nametoken = name.split(".")
        return self._getfromdict(nametoken)

    def _getsettingdict(self, name):
        nametoken = name.split(".")
        return self._getfromdict(nametoken)

    def getsetting(self, name):
        return self._getsettingdict(name).value

    def setsetting(self, name, value):
        pdb.set_trace()
        if not isinstance(name, str):
            raise TypeError("settings name must be a string")
        sd = self._getsettingdict(name)
        if not sd:
            # self.addsetting(name, value)
            raise KeyError("Setting {} not found!".format(name))
        else:
            sd.value = value

    def addsetting(self, name, value, description='', overrideable=True, allowed_values=[]):
        if not isinstance(name, str):
            raise TypeError("settings name must be a string")
        nametoken = name.split(".")
        if not nametoken:
            raise AssertionError("No valid setting name")

        t1 = GenSetting(value=value, description=description, overrideable=overrideable, allowed_values=allowed_values)
        nametoken = list(reversed(nametoken))
        for idx, t in enumerate(nametoken):
            if idx == len(nametoken)-1:
                if t in self:  # if this key already exists, overlay the settings
                    self[t] = overlaysettings(self[t], t1)
                else:
                    self.update({t: t1})
            s = GenSettingDict({t: t1})
            t1 = s

    def delsetting(self, name):
        nametoken = name.split(".")
        if not nametoken or len(nametoken) == 0:
            raise AssertionError("No valid setting name")
        dct = self
        dct_parents = []

        for token in nametoken:
            if isinstance(dct, dict):
                dct_parents.append(dct)
                dct = dct.get(token, {})
            else:  #we have reached a leaf
                pass

        # Note: we have to delete until a dict comes with more than one value
        rev_list = reversed(zip(dct_parents, nametoken))

        for parent, token in rev_list:
            del parent[token]
            if len(parent) > 0:
                break

    def __setitem__(self, key, value):
        if key == 'value' or key[0] == '_':
            raise KeyError("keys starting with _ are not allowed")
        return super(GenSettingDict, self).__setitem__(key, value)

    def flatten(self):
        """
        returns a dict where the keys are in dot form
        example:
        input  = {'zaatio': {'login': 'test2'}, 'login': 'test'}
        output = {'login': 'test', 'zaatio.login': 'test2'}
        """
        #TODO check if this works with our custom dict!
        return flatten(self)

    def serialize(self):
        enc = GenSettingEncoder()
        return enc.encode(self)

    @staticmethod
    def deserialize(jsonstring):
        return JSONDecoder(object_hook=from_json).decode(jsonstring)

    def valuedict(self):
        return getvaluedict(self)


def from_json(json_object):
    """
    deserialize  a GenSettingDict
    f = JSONDecoder(object_hook = from_json).decode(jsonstring)
    """
    if 'value' in json_object:

        description = ""
        allowed_values = []
        overrideable = True
        value = json_object['value']
        if '_description' in json_object:
            description = json_object['_description']
        if '_allowed_values' in json_object:
            allowed_values = json_object['_allowed_values']
        if '_overrideable' in json_object:
            overrideable = json_object['_overrideable']

        return GenSetting(value=value, description=description, allowed_values=allowed_values, overrideable=overrideable)
    return GenSettingDict(init=json_object)


class GenSettingEncoder(JSONEncoder):
    """
    a = GenSettingDict()
    a["user"] = { "msg": GenSetting(value="hello") }
    enc=GenSettingEncoder()
    jsonstring = enc.encode(a)
    """
    def default(self, o):
        try:
           stype = o.__dict__
        except TypeError:
           pass
        else:
            return stype
        # Let the base class default method raise the TypeError
        return JSONEncoder.default(self, o)


class GenSettingBase(object):
    """
    represents a basic setting class
    """
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return self.__str__()

    def __getitem__(self, item):
        return self.value


class GenSetting(GenSettingBase):

    def __init__(self, value=None, allowed_values=(), description="", overrideable=True):
        super(GenSetting, self).__init__(value=value)
        self._description = description
        self._allowed_values = allowed_values
        self._overrideable = overrideable
        self._overwritten = False

    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return self.__str__()


