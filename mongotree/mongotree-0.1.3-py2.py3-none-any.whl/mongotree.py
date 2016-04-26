#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
MongoTree
---------

This is something.
"""

__author__ = 'Joel Bender'
__email__ = 'joel@carrickbender.com'
__version__ = '0.1.3'

import bson


class NodeNotFound(Exception):
    """Node not found."""
    pass


class NodeNotBound(Exception):
    """Node not bound."""
    pass


class MismatchedNodeIdentifier(Exception):
    """Node identifier mismatch from an update."""
    pass


class MongoTreeNode(object):
    """
    A node in a tree.
    """

    def __init__(self, *contents, **attrs):
        """Initialize a new node.

        :param contents: optional children
        :param attrs: optional additional attributes
        """
        super(MongoTreeNode, self).__init__()

        # identity and content containers
        object.__setattr__(self, '_id', None)
        object.__setattr__(self, '_attrs', {})
        object.__setattr__(self, '_contents', [])

        # structure properties
        object.__setattr__(self, '_tree', None)
        object.__setattr__(self, '_parent', None)

        # database backend properties
        object.__setattr__(self, '_proxy', False)
        object.__setattr__(self, '_modified', False)

        # pull the identifier out
        if '_id' in attrs:
            self._id = attrs['_id']
            del attrs['_id']

            # this is a proxy node
            self._proxy = True

        # set the attributes
        for k, v in attrs.items():
            self.__setattr__(k, v)

        # add the content
        for v in contents:
            self.append(v)

    #
    #   database notifications
    #

    def _load(self):
        """This function is called after the node has been loaded."""
        pass

    def _merge(self, node):
        """This function is called by the tree to incorporate database
        content into a proxy."""
        # accept the attributes and content
        self._attrs = node._attrs
        self._contents = node._contents

    def _save(self):
        """This function is called by the tree before the node is
        about to be saved."""
        pass

    #
    #   tree notifications
    #

    def _bind(self, tree):
        pass

    def _unbind(self):
        pass

    #
    #   dict-like functions
    #

    def __getattr__(self, k):
        if not isinstance(k, str):
            raise TypeError("attribute must be a string")
        if k.startswith('_'):
            raise AttributeError

        # load this if it hasn't been loaded yet
        if self._tree and self._proxy:
            self._tree.load_node(self)

        # pass request to the attributes dictionary
        return self._attrs[k]

    def __setattr__(self, k, v):
        if not isinstance(k, str):
            raise TypeError("attribute must be a string")
        if k.startswith('_'):
            return object.__setattr__(self, k, v)

        # load this if it hasn't been loaded yet
        if self._tree and self._proxy:
            self._tree.load_node(self)

        # pass request to the attributes dictionary
        self._attrs[k] = v

        # modified
        self._modified = True

    def __delattr__(self, k):
        if not isinstance(k, str):
            raise TypeError("attribute must be a string")
        if k.startswith('_'):
            raise AttributeError

        # load this if it hasn't been loaded yet
        if self._tree and self._proxy:
            self._tree.load_node(self)

        # pass request to the attributes dictionary
        del self._attrs[k]

        # modified
        self._modified = True

    def __hasattr__(self, k):
        if not isinstance(k, str):
            raise TypeError("attribute must be a string")
        if k.startswith('_'):
            raise AttributeError

        # load this if it hasn't been loaded yet
        if self._tree and self._proxy:
            self._tree.load_node(self)

        # pass request to the attributes dictionary
        return hasattr(self._attrs, k)

    def keys(self):
        # load this if it hasn't been loaded yet
        if self._tree and self._proxy:
            self._tree.load_node(self)

        # pass request to the attributes dictionary
        return self._attrs.keys()

    def items(self):
        # load this if it hasn't been loaded yet
        if self._tree and self._proxy:
            self._tree.load_node(self)

        # pass request to the attributes dictionary
        return self._attrs.items()

    #
    #   list-like functions
    #

    def __getitem__(self, i):
        # load this if it hasn't been loaded yet
        if self._tree and self._proxy:
            self._tree.load_node(self)

        # check for single item or slice
        if isinstance(i, int) or isinstance(i, slice):
            pass
        elif self._tree and isinstance(i, self._tree.marshal.node_id_class):
            i = self.index(i)
        else:
            raise TypeError("unknown kind of item to get")

        # pass request to the contents list
        return self._contents[i]

    def __setitem__(self, i, node):
        # check to see if it is the right type of node
        if self._tree and not isinstance(node, self._tree.marshal.node_class):
            raise TypeError("node must be an instance of " +
                            self._tree.marshal.node_class.__name__)

        # if the node is bound, make sure it is bound to the same tree
        # or both are unbound
        if node._tree and (node._tree != self._tree):
            raise RuntimeError("node bound to the wrong tree")

        # load this if it hasn't been loaded yet
        if self._tree and self._proxy:
            self._tree.load_node(self)

        # pass request to the contents list
        self._contents[i] = node

        # if the node isn't bound, bind it to this tree
        if (not node._tree) and self._tree:
            self._tree.bind(node)

        # modified
        self._modified = True

    def __delitem__(self, i):
        # load this if it hasn't been loaded yet
        if self._tree and self._proxy:
            self._tree.load_node(self)

        # check for single item or slice
        if isinstance(i, int):
            node = self._contents[i]
            if node._tree:
                node._tree.unbind(node)
        elif isinstance(i, slice):
            for node in self._contents[i]:
                if node._tree:
                    node._tree.unbind(node)
        elif self._tree and isinstance(i, self._tree.marshal.node_id_class):
            i = self.index(i)
            node = self._contents[i]
            if node._tree:
                node._tree.unbind(node)
        elif self._tree and isinstance(i, self._tree.marshal.node_class):
            i = self._contents.index(i)
            node = self._contents[i]
            if node._tree:
                node._tree.unbind(node)
        else:
            raise TypeError("unknown kind of thing to delete")

        # pass request to the contents list
        del self._contents[i]

        # modified
        self._modified = True

    def __contains__(self, kv):
        # load this if it hasn't been loaded yet
        if self._tree and self._proxy:
            self._tree.load_node(self)

        # if you are looking for a string, check for an attribute
        if isinstance(kv, str):
            # if it is an attribute, we have a match
            if kv in self._attrs:
                return True
            # if node identifiers are also strings, keep checking
            if (not self._tree) or \
                    (not issubclass(self._tree.marshal.node_id_class, str)):
                return False

        # check for a node based on its instance
        if self._tree and isinstance(kv, self._tree.marshal.node_class):
            try:
                self._contents.index(kv)    # throw away returned value
                return True
            except ValueError:
                return False

        # check for a node by its identifier
        if self._tree and isinstance(kv, self._tree.marshal.node_id_class):
            try:
                self.index(kv)              # throw away returned value
                return True
            except ValueError:
                return False

        # bad news
        raise TypeError("cannot check for something of type " + str(type(kv)))

    def __len__(self):
        # load this if it hasn't been loaded yet
        if self._tree and self._proxy:
            self._tree.load_node(self)

        return len(self._contents)

    def __iter__(self):
        # load this if it hasn't been loaded yet
        if self._tree and self._proxy:
            self._tree.load_node(self)

        # iterate through the contents rather than the attributes
        return iter(self._contents)

    def append(self, node):
        # if this node is bound check to make sure the child is the rigth class
        if self._tree and not isinstance(node, self._tree.marshal.node_class):
            raise TypeError("child must be a node")

        # load this if it hasn't been loaded yet
        if self._tree and self._proxy:
            self._tree.load_node(self)

        # pass along to the contents list
        self._contents.append(node)

        # modified
        self._modified = True

    def extend(self, node_list):
        # load this if it hasn't been loaded yet
        if self._tree and self._proxy:
            self._tree.load_node(self)

        # append each node one at a time
        for node in node_list:
            self.append(node)

    def index(self, node_id):
        # look through the contents
        for i, node in enumerate(self._contents):
            if node_id == node._id:
                return i
        raise ValueError(str(node_id) + " not in contents")


class MongoTreeNodeMarshal(object):
    """
    Base class for marshaling nodes to/from the database.
    """

    def __init__(self, node_class=MongoTreeNode,
                 node_id_class=bson.objectid.ObjectId,
                 dict_class=dict
                 ):
        self.node_class = node_class
        self.node_id_class = node_id_class
        self.dict_class = dict_class

    def dict_to_node(self, some_dict, some_node=None):
        # if a node hasn't been provided, make a new one
        if some_node is None:
            some_node = self.node_class(_id=some_dict['_id'])

        # accept the attributes
        if '_attrs' not in some_dict:
            raise RuntimeError("attrs expected")
        some_node._attrs = some_dict['_attrs']

        # transform the contents into a list of proxy nodes
        if '_contents' not in some_dict:
            raise RuntimeError("contents expected")
        contents = []
        for node_id in some_dict['_contents']:
            contents.append(self.node_class(_id=node_id))

        # save it in the node
        some_node._contents = contents

        # done
        return some_node

    def node_to_dict(self, some_node, some_dict=None):
        # if a dictionary hasn't been provided , make a new one
        if some_dict is None:
            some_dict = self.dict_class()

        # copy the node identifier
        some_dict['_id'] = some_node._id

        # accept the attributes
        some_dict['_attrs'] = some_node._attrs

        # transform the contents to a list of identifiers
        contents = []
        for node in some_node._contents:
            contents.append(node._id)

        # save it in the dict
        some_dict['_contents'] = contents

        # done
        return some_dict


class MongoTree(object):

    def __init__(self, collection, marshal=None):
        self.collection = collection
        self.marshal = marshal or MongoTreeNodeMarshal()
        self.node_cache = {}

    #
    #   basic database functions
    #

    def insert_node(self, node):
        if not isinstance(node, self.marshal.node_class):
            raise TypeError("must be an instance of " +
                            self.marshal.node_class.__name__)

        # turn it into a dict
        some_dict = self.marshal.node_to_dict(node)

        # see if an identifier needs to be assigned
        if (node._id is None):
            if self.marshal.node_id_class is bson.objectid.ObjectId:
                # remove so database assigns an identifier
                if ('_id' in some_dict):
                    del some_dict['_id']
            else:
                # ask the class for an identifier
                try:
                    some_dict['_id'] = self.marshal.node_id_class()
                except Exception as err:
                    raise RuntimeError("node identifier instance error: " +
                                       str(err))
        else:
            if not isinstance(node._id, self.marshal.node_id_class):
                raise TypeError("node identifier must be an instance of " +
                                self.marshal.node_id_class__name__)

        # pass along to the database
        node._id = self.collection.insert(some_dict)

        # no longer modified, nor is it a proxy
        node._modified = False
        node._proxy = False

    def load_node(self, node):
        if not isinstance(node, self.marshal.node_class):
            raise TypeError("must be an instance of " +
                            self.marshal.node_class.__name__)
        if not node._id:
            raise RuntimeError("node has no identity")
        if node._tree and node._tree is not self:
            raise RuntimeError("node not bound to wrong tree " +
                               repr(node._tree))

        # find the object
        some_dict = self.collection.find_one({"_id": node._id})
        if not some_dict:
            raise NodeNotFound(str(node._id))

        # turn it into a (detached) node
        some_node = self.marshal.dict_to_node(some_dict)

        # ask the node to accept the contents
        node._merge(some_node)

        # tell the node is has been loaded
        node._load()

        # node is not longer a proxy
        node._proxy = False

        # bind it to this tree if it is not bound
        if not node._tree:
            self._tree.bind(node)

    def save_node(self, node):
        if node._tree != self:
            raise NodeNotBound("node not bound")
        if not isinstance(node, self.marshal.node_class):
            raise TypeError("must be an instance of " +
                            self.marshal.node_class.__name__)

        # tell the node it is about to be saved
        node._save()

        # turn it into a dict
        some_dict = self.marshal.node_to_dict(node)

        # pass along to the database
        stats = self.collection.find_and_modify(
            query={"_id": node._id},
            update=some_dict,
            fields={"_id": 1},
            )
        if not stats:
            raise NodeNotFound(str(node._id))
        if stats['_id'] != node._id:
            raise MismatchedNodeIdentifier(str(node._id))

        # no longer modified
        node._modified = False

    #
    #   cache functions
    #

    def bind(self, node):
        # make sure it is not bound and the correct type
        if node._tree:
            raise RuntimeError("already bound")
        if not isinstance(node, self.marshal.node_class):
            raise TypeError("must be an instance of " +
                            self.marshal.node_class.__name__)
        if node._id in self.node_cache:
            raise RuntimeError("node already in cache " +
                               repr(node))

        # from tree to node, and node to tree
        self.node_cache[node._id] = node
        node._tree = self

        # tell the node it is bound
        node._bind(self)

    def unbind(self, node):
        # make sure it is bound to this tree and in the cache
        if node._tree is not self:
            raise RuntimeError("node not bound, or not bound to this tree")
        if node._id not in self.node_cache:
            raise RuntimeError("node not in cache " + repr(node))

        # from tree to node, and node from tree
        del self.node_cache[node._id]
        node._tree = None

        # tell the node it is unbound
        node._unbind()

    def save_all_nodes(self):
        # save all the modified nodes in the cache
        for node in self.node_cache.values():
            if node._modified:
                self.save_node(node)

    def flush_cache(self):
        # save all the modified nodes and remove them from the cache
        node_list = list(self.node_cache.values())
        for node in node_list:
            if node._modified:
                self.save_node(node)
            self.unbind(node)

    #
    #   create, retrieve, delete nodes
    #

    def new_node(self, node_id=None):
        # explicit identifier requested
        if (node_id is not None):
            # check the type of node identifier
            if (node_id is not None) and \
                    (not isinstance(node_id, self.marshal.node_id_class)):
                raise TypeError("node identifier must be a " +
                                str(self.marshal.node_id_class))

            # look in the cache
            if node_id in self.node_cache:
                raise RuntimeError("duplicate node identifier " +
                                   repr(node_id))

            # find the object
            some_dict = self.collection.find_one({"_id": node_id}, {"_id": 1})
            if some_dict:
                raise RuntimeError("duplicate node identifier " +
                                   repr(node_id))

        # make a new node
        node = self.marshal.node_class(_id=node_id)

        # save it, giving it an identifier if it doesn't already have one
        self.insert_node(node)

        # associate it with this tree
        self.bind(node)

        # done
        return node

    def get_node(self, node_id):
        # look in the cache
        if node_id in self.node_cache:
            return self.node_cache[node_id]

        # find the object
        some_dict = self.collection.find_one({"_id": node_id})
        if not some_dict:
            raise NodeNotFound(str(node_id))

        # turn it into a (detached) node
        some_node = self.marshal.dict_to_node(some_dict)

        # associate it with this tree
        self.bind(some_node)

        # done
        return some_node

    def del_node(self, node_id):
        # unbind if the node is in the cache
        for node in self.node_cache:
            if node._id == node_id:
                break
        else:
            node = None
        if node:
            self.unbind(node)

        # remove the document
        stats = self.collection.remove(node_id)
        if not stats or stats['n'] != 1:
            raise NodeNotFound(str(node_id))
