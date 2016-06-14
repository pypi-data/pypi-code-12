# -*- coding: utf-8 -*-
from sys import modules


def import_once(name):
    if name not in modules:
        __import__(name)

fast_type = {}

def cached_type(project, name):
    global fast_type
    if project not in fast_type:
        fast_type[project] = dict([(x._name, x) for x in project.types])
    entry = fast_type[project]
    if name in entry:
        return entry[name]
    k = project.types
    for s in k:
        if s._name == name:
            entry[name] = s
            return s
    return None


def isclass(cls, *args):
    """same extension of isinstance to lists"""
    for k in args:
        if cls is k:  # or k in cls.__bases__:
            return True
    return False


def store_access(store, element):
    """Get the access for the element"""
    for k in store:
        if element in store[k]:
            return k
    return None


def access_dict(elements):
    """
    This method constructs a dictionnary with keys 'public', 'protected' and 'private'
    with the set of elements of that access property as value.
    """
    store = {}
    for k in elements:
        if k._access in store:
            store[k._access].add(k)
        else:
            store[k._access] = set([k])
    for k in ['public', 'protected', 'private']:
        if k not in store:
            store[k] = set()
    return store


def join_access(store, candidates, access='public'):
    """
    This method joins the candidate to store with maximum access.
    The store is a dictionnary of three sets:
        store['public'], store['protected'] and store['private']
    The candidates must have the same structure.
    When access is public, all the candidates use their dictionnary
    key as access. If access is protected, both candidates['public'] and
    candidates['protected'] are considered protected. If access is private,
    all candidates are considered private.
    Any candidate already existent in store will be discarded if the
    candidate acces is less powerful than the store acces. For example, any
    element t from cadidate['private'] will be discarded if it exists in
    store['public'] or store['protected']. The reverse situation also
    happens: if any candidate element already exists in some store set
    with less access, then the element is removed from this store set and
    inserted in the store set corresponding to the candidate access"""
    # ensure keys hold
    for k in ['public', 'protected', 'private']:
        if k not in candidates:
            candidates[k] = set()
        if k not in store:
            store[k] = set()
    if access is 'public':
        s = candidates.copy()
    elif access is 'protected':
        s = {
            'public': set(),
            'protected': candidates['public'].union(candidates['protected']),
            'private': candidates['private']
            }
    elif access is 'private':
        s = {
            'public': set(),
            'protected': set(),
            'private': candidates['public'].union(candidates['protected']).union(candidates['private'])
            }
    for t in s['public']:
        store['protected'].discard(t)
        store['private'].discard(t)
        store['public'].add(t)
    for t in s['protected']:
        if t in store['public']:
            continue
        store['private'].discard(t)
        store['protected'].add(t)
    for t in s['private']:
        if t in store['public']:
            continue
        if t in store['protected']:
            continue
        store['private'].add(t)
    return store