import ldap.dn


# Copied from http://code.activestate.com/recipes/194371-case-insensitive-strings/
class istr(str):
    """Case insensitive strings class.
    Performs like str except comparisons are case insensitive."""

    def __init__(self, strMe):
        str.__init__(self, strMe)
        self.__lowerCaseMe = strMe.lower()

    def __repr__(self):
        return "iStr(%s)" % str.__repr__(self)

    def __eq__(self, other):
        if not hasattr(other, 'lower'):
            return False
        return self.__lowerCaseMe == other.lower()

    def __lt__(self, other):
        return self.__lowerCaseMe < other.lower()

    def __le__(self, other):
        return self.__lowerCaseMe <= other.lower()

    def __gt__(self, other):
        return self.__lowerCaseMe > other.lower()

    def __ne__(self, other):
        if not hasattr(other, 'lower'):
            return True
        return self.__lowerCaseMe != other.lower()

    def __ge__(self, other):
        return self.__lowerCaseMe >= other.lower()

    def __cmp__(self, other):
        return cmp(self.__lowerCaseMe, other.lower())

    def __hash__(self):
        return hash(self.__lowerCaseMe)

    def __contains__(self, other):
        return other.lower() in self.__lowerCaseMe

    def count(self, other, *args):
        return str.count(self.__lowerCaseMe, other.lower(), *args)

    def endswith(self, other, *args):
        return str.endswith(self.__lowerCaseMe, other.lower(), *args)

    def find(self, other, *args):
        return str.find(self.__lowerCaseMe, other.lower(), *args)

    def index(self, other, *args):
        return str.index(self.__lowerCaseMe, other.lower(), *args)

    def lower(self):   # Courtesy Duncan Booth
        return self.__lowerCaseMe

    def rfind(self, other, *args):
        return str.rfind(self.__lowerCaseMe, other.lower(), *args)

    def rindex(self, other, *args):
        return str.rindex(self.__lowerCaseMe, other.lower(), *args)

    def startswith(self, other, *args):
        return str.startswith(self.__lowerCaseMe, other.lower(), *args)


class idict(dict):
    """A case insensitive dictionary that only permits strings as keys."""
    def __init__(self, indict={}):
        dict.__init__(self)
        self._keydict = {}  # not self.__keydict because I want it to be easily accessible by subclasses
        for entry in indict:
            self[entry] = indict[entry]  # not dict.__setitem__(self, entry, indict[entry]) becasue this causes errors (phantom entries) where indict has overlapping keys

    def findkey(self, item):
        """A caseless way of checking if a key exists or not.
        It returns None or the correct key."""
        if not isinstance(item, str):
            raise TypeError('Keywords for this object must be strings. You supplied %s' % type(item))
        key = item.lower()
        try:
            return self._keydict[key]
        except:
            return None

    def changekey(self, item):
        """For changing the casing of a key.
        If a key exists that is a caseless match for 'item' it will be changed to 'item'.
        This is useful when initially setting up default keys - but later might want to preserve an alternative casing.
        (e.g. if later read from a config file - and you might want to write back out with the user's casing preserved).
        """
        key = self.findkey(item)           # does the key exist
        if key is None:
            raise KeyError(item)
        temp = self[key]
        del self[key]
        self[item] = temp
        self._keydict[item.lower()] = item

    def lowerkeys(self):
        """Returns a lowercase list of all member keywords."""
        return self._keydict.keys()

    def __setitem__(self, item, value):             # setting a keyword
        """To implement lowercase keys."""
        key = self.findkey(item)           # if the key already exists
        if key is not None:
            dict.__delitem__(self, key)
        self._keydict[item.lower()] = item
        dict.__setitem__(self, item, value)

    def __getitem__(self, item):
        """To implement lowercase keys."""
        key = self.findkey(item)           # does the key exist
        if key is None:
            raise KeyError(item)
        return dict.__getitem__(self, key)

    def __delitem__(self, item):                # deleting a keyword
        key = self.findkey(item)           # does the key exist
        if key is None:
            raise KeyError(item)
        dict.__delitem__(self, key)
        del self._keydict[item.lower()]

    def pop(self, item, default=None):
        """Correctly emulates the pop method."""
        key = self.findkey(item)           # does the key exist
        if key is None:
            if default is None:
                raise KeyError(item)
            else:
                return default
        del self._keydict[item.lower()]
        return dict.pop(self, key)

    def popitem(self):
        """Correctly emulates the popitem method."""
        popped = dict.popitem(self)
        del self._keydict[popped[0].lower()]
        return popped

    def has_key(self, item):
        """A case insensitive test for keys."""
        if not isinstance(item, str):
            return False               # should never have a non-string key
        return item.lower() in self._keydict           # does the key exist

    def __contains__(self, item):
        """A case insensitive __contains__."""
        if not isinstance(item, str):
            return False               # should never have a non-string key
        return item.lower() in self._keydict           # does the key exist

    def setdefault(self, item, default=None):
        """A case insensitive setdefault.
        If no default is supplied it sets the item to None"""
        key = self.findkey(item)           # does the key exist
        if key is not None:
            return self[key]
        self.__setitem__(item, default)
        self._keydict[item.lower()] = item
        return default

    def get(self, item, default=None):
        """A case insensitive get."""
        key = self.findkey(item)           # does the key exist
        if key is not None:
            return self[key]
        return default

    def update(self, indict):
        """A case insensitive update.
        If your dictionary has overlapping keys (e.g. 'FISH' and 'fish') then one will overwrite the other.
        The one that is kept is arbitrary."""
        for entry in indict:
            self[entry] = indict[entry]         # this uses the new __setitem__ method

    def copy(self):
        """Create a new caselessDict object that is a copy of this one."""
        return idict(self)

    def dict(self):
        """Create a dictionary version of this caselessDict."""
        return dict.copy(self)

    def clear(self):
        """Clear this caselessDict."""
        self._keydict = {}
        dict.clear(self)

    def __repr__(self):
        """A caselessDict version of __repr__ """
        return 'caselessDict(' + dict.__repr__(self) + ')'

    def __eq__(self, other):
        for k in self:
            if k not in other:
                 return False
            if self[k] != other[k]:
                 return False
        for k in other:
            if k not in self:
                 return False
            if self[k] != other[k]:
                 return False
        return True

    def __ne__(self, other):
	return not (self == other)


def batch_generator(gen, *batch_size):
    batch = []
    for result in gen:
        batch.append(result)
        if len(batch) == batch_size[0]:
            yield batch
            batch = []
            if len(batch_size) > 1:
                batch_size = batch_size[1:]
    if len(batch):
        yield batch


def to_dict_of_set(d):
    r = idict({k: set(v) for k, v in d.iteritems()})
    if 'objectclass' in r:
        r['objectclass'] = set(istr(v) for v in r['objectclass'])
    return r


def str2dn(s):
    return tuple(map(tuple, ldap.dn.str2dn(s)))
