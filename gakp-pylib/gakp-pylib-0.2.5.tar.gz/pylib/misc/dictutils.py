def remove_nones(obj):
    """Create a new dict without keys that have None values."""
    return {k: v for k, v in obj.items() if v is not None}


def merge_dict(obj1, obj2):
    """Create new dict that is a combination of the two dicts passed.

    Note that the new dict my not be in the order expected
    """
    tmp = obj1.copy()
    tmp.update(obj2)
    return tmp


def dict_items(obj):
    """Create a list of tuples(key, value) of the dict"""
    return list(zip(obj.keys(), obj.values()))
