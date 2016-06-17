try:
    import ujson as json
except:
    import json
from collections import namedtuple
import urllib.request
#from cnamedtuple import namedtuple

import urllib.request

Node = namedtuple('Node', 'path parent key value')


#all:
#    root=None

#get/find:
#    expand=False
#    context=False


    
#######################################################################################
#   GET
#######################################################################################

def find(obj, path="", root=None, expand=False, context=False, filt=None):
    if not root:
        root = obj
    parts = splitPath(path)
    for node in _walk(Node('', None, None, obj), parts, DEFAULT_EXPANDER(root), None):
        if filt and not filt(node):
            continue
        if expand:
            value=_expand(node.value, root, expand)
            node = Node(node.path, node.parent, node.key, value)
        if context:
            yield node
        else:
            yield node.value

def get(obj, path="", root=None, expand=False, context=False):
    parts = splitPath(path)
    if '*' in parts:
        raise Exception('No wildcards allowed in getter path!')
        
    return next(find(obj, path, root, expand, context))
 
def splitPath(path):
    parts = path.strip('/').split('/')
    parts = [p for p in parts if p != '']
    # we don't know yet if number keys are strings for dicts or ints for lists
    return parts



def _walk_old(node, parts, expander=None, builder=None):
    """Walks down the tree according to the path.
    parts -- the path split in a list of strings
    expander -- when a reference node is encountered, the expander will be called like expander(ref) and expects the node's value in return. If None, nodes will not be expanded.
    builder -- when a key is missing, the builder will be called like builder(parent, key, remaining_parts) and expects the child's value in return. If None, no nodes will be built.
    """
    if not parts:
        yield node
        return
    
    key = parts[0]
    tail = parts[1:]
    current = node.value
    
    if expander and isinstance(current, dict) and '$ref' in current:
        current = expander( current['$ref'] )
    
    if key != '*':
        path = node.path + '/' + key
        if isinstance(current, list):
            if not key.isdigit():
                raise Exception("Digits expected in path instead of " + key + " at: " + path)
            key = int(key)
            if key < len(current):
                child = Node(path, current, key, current[key])
                for hit in _walk(child, tail, root, follow):
                    yield hit
            else:
                raise Exception("No such path: " + path)
        elif isinstance(current, dict):
            if key in current:
                child = Node(path, current, key, current[key])
                for hit in _walk(child, tail, root, follow):
                    yield hit
            else:
                raise Exception("No such path: " + path)
        else:
            raise Exception("Unexpected primitive value at " + node.path)
    
    else: # wildcard
        
        if isinstance(current, list):
            # we need to iterate in reverse in case these get deleted on the fly
            for key in range(len(current)-1,-1,-1):
                path = node.path + '/' + str(key)
                child = Node(path, current, key, current[key])
                for hit in _walk(child, tail, root, follow):
                    yield hit
        elif isinstance(current, dict):
            for (key, value) in current.items():
                path = node.path + '/' + key
                child = Node(path, current, key, value)
                for hit in _walk(child, tail, root, follow):
                    yield hit
        else:
            raise Exception("Unexpected primitive value at " + node.path)




def _walk(node, parts, expander, builder):
    """Walks down the tree according to the path.
    parts -- the path split in a list of strings
    expander -- when a reference node is encountered, the expander will be called like expander(ref) and expects the node's value in return. If None, nodes will not be expanded.
    builder -- when a key is missing, the builder will be called like builder(parent, key, remaining_parts) and expects the child's value in return. If None, no nodes will be built.
    """
    print(node)
    if not parts:
        yield node
        return
    
    key = parts[0]
    tail = parts[1:]
    current = node.value
    
    if expander and isinstance(current, dict) and '$ref' in current:
        current = expander( current['$ref'] )
    
    if isinstance(current, list):
        if key == '*':
            keys = range(len(current)-1,-1,-1) # we need to iterate in reverse in case these get deleted on the fly
        else:
            if not key.isdigit():
                raise Exception("Digits expected in path instead of " + key + " at: " + node.path)
            n = int(key)
            if n >= len(current):
                raise Exception("No such index at path: %s/%d" % (node.path, n))
            keys = [ n ]
    elif isinstance(current, dict):
        if key == '*':
            keys = current.keys()
        else:
            if builder and key not in current:
                builder(current, key, tail)
            if key not in current:
                raise Exception("No such path: " + node.path + "/" + key)
            keys = [ key ]
    
    for key in keys:
        path = node.path + '/' + str(key)
        child = Node(path, current, key, current[key])
        print(child)
        for hit in _walk(child, tail, expander, builder):
            yield hit
                

def _expand(obj, root, depth=1):
    if depth == True:
        depth = 1
    elif depth <= 0:
        return obj
        
    if isinstance(obj,dict):
        if '$ref' in obj:
            trg = _getRef(obj['$ref'], root, external=True)
            return _expand(trg, root, depth-1)
        else:
            trg = {}
            for (k,v) in obj.items():
                trg[k] = _expand(v, root, depth)
            return trg
    elif isinstance(obj,list):
        trg = []
        for val in obj:
            trg.append( _expand(val, root, depth) )
        return trg
    else:
        return obj


def apply(fun, obj, path, root, filt, builder=None):
    if not root:
        root = obj
    parts = splitPath(path)
    modified = []
    for node in _walk(Node('', None, None, obj), parts, LOCAL_EXPANDER(root), builder):
        if filt and not filt(node):
            continue
        fun(node)
        modified.append(node.path)
    return modified


def set(obj, path, value, root=None, filt=None):
    def _set(node):
        node.parent[node.key] = value
    return apply(_set, obj, path, root, filt, builder=LAST_KEY_APPENDER)

 
def update(obj, path, value, root=None, filt=None):
    def _update(node):
        node.parent[node.key].update(value)
    return apply(_update, obj, path, root, filt)
    

def add(obj, path, value, root=None, filt=None):
    def _add(node):
        node.parent[node.key].append(value)
    return apply(_add, obj, path, root, filt)


def delete(obj, path, root=None, filt=None):
    def _delete(node):
        del node.parent[node.key]
    return apply(_delete, obj, path, root, filt)


def DEFAULT_EXPANDER(root):
    return lambda ref: _getRef(ref, root, True)

def LOCAL_EXPANDER(root):
    return lambda ref: _getRef(ref, root, False)

def LAST_KEY_APPENDER(dic, key, tail):
    if not tail:
        dic[key] = {}
    else:
        raise Exception('')
    
def _getRef(ref, root, external=True):
    if ref.startswith('/'):
        return get(root, ref)
    elif ref.startswith('#'):
        return get(root, ref[1:])
    elif not external:
        raise Exception('External or invalid reference: ' + ref)
    elif ref.startswith('file:///'):
        return _loadFile(ref.lstrip('file:///'))
    elif ref.startswith('file://'):
        return _loadFile(ref.lstrip('file://'))
    elif ref.startswith('http://') or ref.startswith('https://'):
        return _loadHTTP(ref.lstrip('file:///'))
    else:
        raise Exception('Invalid reference: ' + ref)


#TODO: encoding?
def _loadFile(path):
    with open(path) as f:
        raw = f.read()
        obj = json.loads(raw)
        return obj


#TODO: encoding?
def _loadHTTP(url):
    raw = urllib.request.urlopen(url).read().decode('utf-8')
    obj = json.loads(raw)
    return obj

