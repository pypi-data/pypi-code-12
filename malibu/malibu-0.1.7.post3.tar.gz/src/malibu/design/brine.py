# -*- coding: utf-8 -*-
import json
import time
import types
import uuid
from difflib import SequenceMatcher

__doc__ = """
malibu.design.brine
-------------------

Brine is a play on Python's pickle module, which is used for
serializing data. Brine is used for serialization as well, but
into JSON, not a binary structure.
"""

# Declare a set of method types that should be filtered for.
METHOD_TYPES = [types.MethodType, types.FunctionType, types.LambdaType]


def fuzzy_ratio(a, b):
    """ Compares two values using the SequenceMatcher from difflib.
        Used for ~approximated~ fuzzy search.

        :param str a: lhs string
        :param str b: rhs string
        :rtype: int
        :returns: Integer ration of a <=> b
    """

    return SequenceMatcher(None, a, b).ratio()


class BrineObject(object):
    """ This object is for use as a base class for other data.
        Essentially, it will expose a set of members that can be set
        and then squashed down to a JSON object through a call to to_json.

        It can also be used as a meta-class for the base of a caching object
        model or other neat things.
    """

    @classmethod
    def by_json(cls, data, read_only=False, **kw):
        """ Creates a new instance and calls from_json on the instance.

            Will take kwargs and pass to the underlying instance
            initializer.

            :param class cls: Class method is running on
            :param str data: JSON string to create object from
            :param bool read_only: Set object read-only
            :param dict **kw: Object initializer options
            :rtype: cls
            :returns: new BrineObject subclass instance
        """

        inst = cls(**kw)
        inst.from_json(data)
        if read_only:
            inst.read_only()

        return inst

    @classmethod
    def by_dict(cls, data, read_only=False, **kw):
        """ Creates a new instance with fields from the data parameter
            as long as they match what is in _fields.

            Also does recursion on nested Brine objects.

            :param class cls: BrineObject subclass
            :param dict data: Dictionary to use for fields
            :param bool read_only: Set object read-only
            :param dict **kw: BrineObject initializer options
            :rtype: BrineObject
            :returns: BrineObject subclass instance
            :raises TypeError: If data is not dict type
        """

        if not isinstance(data, dict):
            raise TypeError("Data parameter must be a dict.")

        o = cls(**kw)
        o.from_dict(data)
        if read_only:
            o.read_only()

        return o

    def __init__(self, *args, **kw):

        # Do this because MRO.
        super(BrineObject, self).__init__()

        # Disable custom __setattr__ for the meantime.
        self._initialized = False
        self._read_only = False

        # For now, lets make this simple and treat fields with no special
        # syntax (underlines, mainly) as our schema.
        self._special_fields = ["timestamp", "uuid"]
        self._fields = []
        for field in dir(self):
            if field.startswith("_"):
                continue
            # Also, make sure this isn't a function.
            if type(getattr(self, field)) in METHOD_TYPES:
                continue
            self._fields.append(field)

        if kw.get("timestamp", False):
            self.timestamp = int(time.time())
        else:
            self._special_fields.remove("timestamp")

        if kw.get("uuid", False):
            self.uuid = str(uuid.uuid4())
        else:
            self._special_fields.remove("uuid")

        self._initialized = True

    def __setattr__(self, attr, value):
        """ Allows setting local values, obviously. Mainly ensures that
            nested BrineObjects do *not* get clobbered, only modified.

            :param str attr: Local instance attribute to set
            :param object value: Value of instance attribute
            :rtype: None
            :returns: None
            :raises AttributeError: Immutable or non-existent field
            :raises TypeError: Overwriting function type with object
        """

        # I wish this didn't have to be a special case.
        if attr == "_initialized":
            self.__dict__[attr] = value
            return

        # Check that init has finished.
        if not getattr(self, "_initialized", False):
            self.__dict__[attr] = value
            return

        if attr in self._special_fields:
            raise AttributeError("Field {} is immutable.".format(attr))
        elif attr not in self._fields:
            if attr.startswith("_"):  # Untracked instance variable
                if attr in ["_fields", "_special_fields"]:
                    # These fields can NOT be overwritten
                    raise AttributeError("Field {} is immutable.".format(attr))
            else:
                raise AttributeError("Field {} does not exist.".format(attr))
        elif attr in self._fields and self._read_only:
            raise AttributeError("Tracked fields are read-only.")

        # Verify that the set *will not* overwrite a method or Brine object.
        _attr_cur = getattr(self, attr, None)
        if type(_attr_cur) in METHOD_TYPES:
            raise TypeError("Function {} can not be overwritten.".format(attr))
        elif isinstance(_attr_cur, BrineObject):
            raise AttributeError("Brine object {} can't be clobbered.".format(
                attr))

        # Set the variable in the dictionary.
        self.__dict__[attr] = value

    def as_dict(self):
        """ Returns the dictionary representation of the fields
            in this object.

            :rtype: dict
            :returns: Current object in dictionary form
        """

        obj = {}

        for val in self._fields + self._special_fields:
            if not hasattr(self, val):
                continue
            # Also, make sure this isn't a function.
            if type(getattr(self, val)) in METHOD_TYPES:
                continue
            attr = getattr(self, val)
            if isinstance(attr, BrineObject):
                obj.update({val: attr.as_dict()})
            else:
                obj.update({val: getattr(self, val)})

        return obj

    def to_json(self):
        """ Converts the object into JSON form.
            Simple, right?

            :rtype: str
            :returns: Current object in JSON string form.
        """

        return json.dumps(self.as_dict())

    def from_json(self, data):
        """ Converts the JSON data back into an object, then loads
            the data into the model instance.

            NOTE: This changes the current model *in-place*!

            :param str data: JSON string to import
            :rtype: None
            :returns: None
        """

        obj = json.loads(data)

        if not isinstance(obj, dict):
            raise TypeError("Expected JSON serialized dictionary, not %s" % (
                type(obj)))

        for k, v in obj.items():
            # We need to make sure the data is sanitized a little bit.
            if k.startswith("_") and k not in self._special_fields:
                continue
            if k in self._fields:
                fval = getattr(self, k, None)
                if isinstance(fval, BrineObject):
                    fval.from_json(json.dumps(v))
                else:
                    setattr(self, k, v)

    def from_dict(self, data):
        """ Creates a new instance with fields from the data parameter
            as long as they match what is in _fields.

            Also does recursion on nested Brine objects.

            NOTE: Modifies the BrineObject *in-place*!
                  If there are recursive objects also provided
                  in the dictionary that are defined on the original
                  object, they will also be modified *in-place*!

                  Keys prefixed by an underscore will be
                  inserted into the object, but will not be tracked
                  in _fields or _special_fields.

            WARNING: This silently ignores "bad" fields.

            :param dict data: Dictionary to use for fields
            :rtype: None
            :returns: None
            :raises TypeError: If data is not dict type
        """

        if not isinstance(data, dict):
            raise TypeError("Data parameter must be a dict.")

        for k, v in data.items():
            if k.startswith("_"):  # Untracked instance variable
                if k in ["_fields", "_special_fields"]:
                    # These vars can NOT be overwritten
                    continue
                else:
                    setattr(self, k, v)
                    continue

            if k not in self._fields + self._special_fields:
                continue

            if isinstance(getattr(self, k, None), BrineObject):
                cl = getattr(self, k)
                cl.from_dict(v)
                continue

            if type(getattr(self, k)) in METHOD_TYPES:
                continue

            setattr(self, k, v)

    def read_only(self):
        """ Set object as read-only. After an object is set
            read-only, it can not be unset as read-only.

            :rtype: None
            :returns: None

        """

        self._read_only = True


class CachingBrineObject(BrineObject):
    """ This is a magical class that performs the same function as the
        BrineObject, but it also adds object caching, searching, and fuzzy
        searching on the cache. Also provided is cached field invalidation /
        "dirtying".
    """

    # Ratio for fuzzy search. Closer to 1.0 means stricter results.
    _FUZZ_RATIO = 0.535

    @classmethod
    def _initialize_cache(cls):
        """ Initialize a class-level cache to store Json models for cache and
            searching purposes.
        """

        if not hasattr(cls, "_CachingBrineObject__cache"):
            cls.__cache = []

    @classmethod
    def fuzzy_search(cls, ignore_case=False, **kw):
        """ Performs a fuzzy search on the cache to find objects that have at
            least a diff ratio of FUZZ_RATIO.

            Note that this can return more than one object and it may not be
            accurate. Time will tell.

            Returns a list of matches ordered by likelihood of match.

            :param class cls: Class to fuzzy search on
            :param bool ignore_case: Whether searching should ignore case
            :param dict **kw: Fields to search
            :rtype: list
            :returns: List of matching CachingBrineObjects
        """

        ratios = {}

        cls._initialize_cache()

        for k, v in kw.items():
            for obj in cls.__cache:
                ob_value = getattr(obj, k, None)
                if ignore_case:
                    if isinstance(v, str) and isinstance(ob_value, str):
                        r = fuzzy_ratio(ob_value.lower(), v.lower())
                else:
                    r = fuzzy_ratio(ob_value, v)
                if r >= cls._FUZZ_RATIO:
                    ratios.update({obj: r})

        # TODO - sort by fuzzy search ratio.
        # We need to ensure the results get properly sorted by match ratio
        # before returning.

        return ratios.keys()

    @classmethod
    def search(cls, ignore_case=False, **kw):
        """ Searches through the cache to find objects with field that match
            those given by the **kw.

            Note that this can return more than one object.

            :param bool ignore_case: Should search ignore case?
            :param dict **kw: Fields to search
            :rtype: list
            :returns: List of matching CachingBrineObjects
        """

        result = []

        cls._initialize_cache()

        for k, v in kw.items():
            for obj in cls.__cache:
                ob_value = getattr(obj, k, None)
                if ignore_case:
                    if isinstance(v, str) and isinstance(ob_value, str):
                        r = (v.lower() == ob_value.lower())
                else:
                    r = (v == ob_value)
                if r:
                    if obj in result:
                        continue
                    else:
                        result.append(obj)
                else:
                    continue

        return result

    def __init__(self, *args, **kw):

        # Call the parent initializer.
        super(CachingBrineObject, self).__init__(self, *args, **kw)
        self._initialized = False

        # Make sure the cache is initialized.
        self._initialize_cache()

        # The "dirty" cache list is just a list of fields that have been
        # updated.
        self.__dirty = []

        # Throw this object into the cache.
        self.__cache.append(self)

        # Let the attribute handler know we're done loading.
        self._initialized = True

    def __setattr__(self, attr, value):
        """ Sets local fields and determines if the cache needs to be
            marked dirty for that set and ensures that the value can
            actually be set.

            :param str attr: Local instance attribute to set
            :param object value: Value of instance attribute
            :rtype: None
            :returns: None
            :raises AttributeError: Immutable of non-existent field
            :raises TypeError: Overwriting function type with object
        """

        # I wish this didn't have to be a special case.
        if attr == "_initialized":
            self.__dict__[attr] = value
            return

        # Check that init has finished.
        if not getattr(self, "_initialized", False):
            self.__dict__[attr] = value
            return

        # Check various conditions used to determine if a variable has been
        # dirtied or can be set.
        if attr in self._fields:
            if self._read_only:
                raise AttributeError("Tracked fields are read-only.")

            if attr not in self.__dirty:
                self.__dirty.append(attr)
        elif attr in self._special_fields:
            raise AttributeError("Special field {} is immutable.".format(attr))
        elif attr in ["_fields", "_special_fields"]:
            raise AttributeError("Field {} is immutable.".format(attr))
        elif attr not in self.__dict__:
            if not attr.startswith("_"):  # Untracked instance variable
                raise AttributeError("Field {} does not exist.".format(attr))

        # Verify that the set *will not* overwrite a method.
        _attr_cur = getattr(self, attr, None)
        if type(_attr_cur) in METHOD_TYPES:
            raise TypeError("Function {} can not be overwritten.".format(attr))
        elif isinstance(_attr_cur, BrineObject):
            raise AttributeError("Brine object {} can't be clobbered.".format(
                attr))

        # Set the variable in the dictionary.
        self.__dict__[attr] = value

    def uncache(self):
        """ Removes the object from the state cache forcibly.

            :rtype: None
            :returns: None
        """

        self.__cache.remove(self)

    def unmark(self, *fields):
        """ Unmarks some field as dirty. Should only be called after
            the upstream is updated or only if you know what you're doing!

            :param list *fields: Fields to unmark
            :rtype: None
            :returns: None
        """

        for field in fields:
            if field not in self.__dirty:
                continue

            self.__dirty.remove(field)

    def dirty_dict(self):
        """ Dumps a dictionary of dirty fields.

            :rtype: dict
            :returns: Dictionary of all *dirty* values
        """

        obj = {}
        for val in self.__dirty:
            if not hasattr(self, val):
                continue
            # Also, make sure this isn't a function.
            if type(getattr(self, val)) in METHOD_TYPES:
                continue
            obj.update({val: getattr(self, val)})

        return obj

    def dirty_json(self):
        """ Dumps the dirty dictionary as JSON.

            :rtype: str
            :returns: JSON dictionary of dirty values
        """

        return json.dumps(self.dirty_dict())
