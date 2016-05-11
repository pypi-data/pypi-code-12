"""
Tools for handling the relations.
"""
from collections import defaultdict
from functools import lru_cache
from . import models

# pylint: disable=no-member, redefined-variable-type

@lru_cache()
def lookups():
    "Return lookups"
    tmp = dict()
    _ = models.Organisation.objects.all().values_list('id', 'label')
    tmp['name'] = dict(_)
    tmp['name'][0] = '∞'
    tmp['id'] = {tmp['name'][key]: key for key in tmp['name']}
    tmp['stem_leafs'] = defaultdict(set)
    tmp['leaf_stems'] = defaultdict(set)
    tmp['stems'] = set()
    tmp['leafs'] = set()
    _ =  models.Association.objects.all().values_list('organisation__id',
                                                      'associations__id')
    for stem, leaf in _:
        tmp['stems'].add(stem)
        tmp['leafs'].add(leaf)
        tmp['stem_leafs'][stem].add(leaf)
        tmp['leaf_stems'][leaf].add(stem)

    tmp['head'] = tmp['stems'].difference(tmp['leafs'])
    tmp['tail'] = tmp['leafs'].difference(tmp['stems'])
    tmp['node'] = tmp['stems'].intersection(tmp['leafs'])

    return tmp


def _id_to_name_recursive(container):
    "converts a list of ids to a list of names"
    names = lookups()['name']
    if isinstance(container, (int,)):
        return names[container]

    if isinstance(container, dict):
        _ = dict()
        for key, value in container.items():
            key = names[key]
            _[key] = _id_to_name_recursive(value)
        return _

    if isinstance(container, (set, tuple, list)):
        _ = list()
        for entry in container:
            _.append(_id_to_name_recursive(entry))
        if len(_) == 1:
            return _[0]
        else:
            return _

    text = 'Unexpected container type %s with value %s'
    text = text % (str(type(container)), str(container))
    raise ValueError(text)


def get_heads_as_ids():
    "Return all organisations that have no parent association."
    tmp = lookups()
    return tmp['head']

def get_heads():
    "Same as get_heads_ids but lookup names."
    return _id_to_name_recursive(get_heads_as_ids())

def get_tails_as_ids():
    "Return all organisations that have no parent association."
    tmp = lookups()
    return tmp['tail']

def get_tails():
    "Same as get_tails_ids but lookup names."
    return _id_to_name_recursive(get_tails_as_ids())

def get_nodes_as_ids():
    "Return organisations that are neither head nor tail."
    tmp = lookups()
    return tmp['node']

def get_nodes():
    "Same as get_roots_ids but lookup name."
    return _id_to_name_recursive(get_nodes_as_ids())

def get_name(identifier):
    "Return the name by the id."
    tmp = lookups()
    return tmp['name'][identifier]

def get_id(name):
    "Return the id by the name."
    tmp = lookups()
    return tmp['id'][name]

def _get_relations_by_id(key, idx, recursive=False, root=None):
    """Get relations, key is either 'tail' or 'head'.
    This means that if tail is specified the idx is followed to all its tails.
    Alternatively if head is specified the idx is followed to all its heads.
    """
    tmp = lookups()
    if key == 'tail':
        related = tmp['stem_leafs'][idx]
    elif key == 'head':
        related = tmp['leaf_stems'][idx]
    else:
        raise ValueError("Key must be either 'tail' or 'head', not %s" % key)

    related = list(related)
    related.sort()

    if not recursive:
        return related

    returns = {idx:list()}

    if root is None:
        root = [idx]

    for entry in related:
        if entry in tmp[key]:
            append = entry
        else:
            if entry in root:
                append = {entry: 0}
            else:
                root.append(entry)
                append = _get_relations_by_id(key, entry, recursive, root)

        returns[idx].append(append)

    return returns

def get_leafs_by_id(organisation_id, recursive=False):
    "Actual implementation on get_leafs."
    return _get_relations_by_id('tail', organisation_id, recursive)

def get_stems_by_id(organisation_id, recursive=False):
    "Actual implementation on get_leafs."
    return _get_relations_by_id('head', organisation_id, recursive)

def get_stems(organisation, recursive=False):
    "Return instances that have organisation as (one of their) leafs."
    tmp = lookups()
    array = get_stems_by_id(tmp['id'][organisation], recursive)
    return _id_to_name_recursive(array)

def get_leafs(organisation, recursive=False):
    "Return instances that have organisation as (one of their) stems."
    tmp = lookups()
    array = get_leafs_by_id(tmp['id'][organisation], recursive)
    return _id_to_name_recursive(array)

def flatten(container, returns=None, prefix=None):
    "Flattens the container."
    if prefix is None:
        prefix = list()
    else:
        prefix = prefix[::]

    if returns is None:
        returns = list()

    if isinstance(container, dict):
        for key, value in container.items():
            returns.append(prefix+[key])
            prefix.append(key)
            flatten(value, returns, prefix)

    elif isinstance(container, (list, tuple, set)):
        for item in container:
            flatten(item, returns, prefix)
    else:
        returns.append(prefix + [container])

    return returns
