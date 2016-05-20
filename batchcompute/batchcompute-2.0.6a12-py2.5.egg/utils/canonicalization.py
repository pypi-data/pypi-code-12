'''
Functions and classes to make interfaces or keys canonicalization.
'''
import re
from datetime import timedelta


from .functions import (
    partial, timestamp_datetime, import_json, timediff, str2datetime,
    utc2local
)
from .constants import STATE_MAP, PY2, PY3, STRING
# from batchcompute.core.exceptions import JsonError

json = import_json()

class CamelCasedClass(type):
    '''
    MetaClass for all classes which expected supply lower-camel-case methods
    instead of methods with `_` joined lower cases.

    Mainly add descriptor for each property descripted in description dict.

    e.g.:
        You can get JobId of a job status 'j' through both j.jobId and
        j.getJobId(), and the like.

    '''
    def __new__(cls, nm, parents, attrs):
        super_new = super(CamelCasedClass, cls).__new__

        tmp_dct = dict()
        for name, value in attrs.items():
            if not name.startswith('__') and not name.endswith('__'):
                tmp_dct[name] = value
        attrs.update(tmp_dct)

        # Create property for each key in `description_map` dict.
        # Besides, if `descriptor_type` is data descriptor, a `getxxx` and
        # a `setxxx` method also will be added to `cls`, if `descriptor_type`
        # is non data descriptor, only a `getxxx` method added.
        if 'descriptor_map' in attrs:
            for attr in attrs['descriptor_map']:
                # Definition of getter and setter method for properties.
                def get_attr(attr, self):
                    return self.getproperty(attr)
                def set_attr(attr, self, value):
                    self.setproperty(attr, value)

                property_name = attr
                getter = partial(get_attr, attr)
                setter = partial(set_attr, attr)
                # Add property to class.
                if attrs['descriptor_type'] == 'data descriptor':
                    # data descriptor.
                    attrs[property_name] = property(getter, setter, None, attr)
                else:
                    # non data descriptor.
                    attrs[property_name] = property(getter, None, None, attr)
        return super_new(cls, nm, parents, attrs)


def remap(container, human_readable=False):
    '''
    Canonicalize keys in container to standard names.

    `container` must be a list, dict or string.
    '''

    if not container:
        if isinstance(container, STRING):
            return dict()
        else:
            return container

    from batchcompute.core.exceptions import JsonError
    s = ""
    try:
        if PY2:
            if isinstance(container, str):
                s = container.strip()
                container = json.loads(s) if s else dict()
        else:
            # For Python 3 compatibility.
            if isinstance(container, bytes):
                s = str(container, encoding='ascii').strip()
                container = json.loads(s) if s else dict()
    except Exception:
        raise JsonError(s)

    new_container = type(container)()
    if isinstance(container, dict):
        new_container.update(container)
    else:
        new_container = container

    get_iter = lambda c: c.items() if isinstance(c, dict) else enumerate(c)
    # Make all keys canonical recursively.
    for key, value in get_iter(new_container):
        # XXX maybe unicode
        if isinstance(key, STRING) and key.endswith('Time'):
            # Convert epoch time to human readable time format.
            new_value = utc2local(str2datetime(value))
        elif isinstance(value, (list, dict)):
            # Only for ListResponse.
            new_value = remap(value, human_readable) 
        else:
            new_value = value
        new_container[key] = new_value
    return new_container
