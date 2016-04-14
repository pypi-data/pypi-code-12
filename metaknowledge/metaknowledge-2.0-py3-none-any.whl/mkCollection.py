import copy
import pickle
import os
import os.path
import math
try:
    import collections.abc
except ImportError:
    import collections
    collections.abc = collections

import networkx as nx

from .progressBar import _ProgressBar

from .constants import __version__

from .mkExceptions import CollectionTypeError, cacheError

import metaknowledge

class Collection(collections.abc.MutableSet, collections.abc.Hashable):
    """A named hashable set with some error reporting.

    `Collections` have all the methods of builtin `sets` as well as error reporting with _bad_ and _error_, and control over the contained items with _allowedTypes_ and _collectedTypes_.

    # Customizations

    When created _name_ should be a string that allows users to easily determine the source of the `Collection`

    When created the you must provided a set of types, _allowedTypes_, when new items are added they will be checked and if they are not instances of any of the types an `CollectionTypeError` exception will be raised. The _collectedTypes_ set that is provided should be a set of only the types in the `Collection`.

    If any of the elements in the `Collection` are bad then _bad_ should be set to `True` and the `dict` _errors_ should map the item to it's exception.

    All of these customizations are managed when operations occur on the `Collection` and if 2 `Collections` are modified with one of the binary operators (`|`, `-`, etc) the `_collectedTypes` and `errors` attributes will be modified the same way. `name` will be updated to explain the operation(s) that occurred.

    \_\_Init\_\_

    As `Collection` is mostly meant to be base for other classes all but one of the arguments in the \_\_Init\_\_ are not optional and the optional one is not used.

    # Parameters
    
    _inSet_ : `set`

    > The objects to be contained

    _allowedTypes_ : `set[type]`

    > A set of types, `{object}` will allow virtually everything

    _collectedTypes_ : `set[type]`

    > The types (or supertypes) of the objects in _inSet_

    _name_ : `str`

    > The name of the `Collection`

    _bad_ : `bool`

    > If any of the elements are bad

    _errors_ : `dict[:Exception]`

    > A mapping from items to their errors

    _quietStart_ : `optional [bool]`

    > Default `False`, does nothing. This is here for use as a interface by subclasses
    """
    def __init__(self, inSet, allowedTypes, collectedTypes, name, bad, errors, quietStart = False):
        """Basically a collections.abc.MutableSet wrapper for a set with a bunch of extra record keeping attached."""
        self._collection = inSet
        self._allowedTypes = allowedTypes
        self._collectedTypes = collectedTypes

        self.name = name
        self.bad = bad
        self.errors = errors

    #Hashable method

    def __hash__(self):
        return hash(sum((hash(i) for i in self)))

    #Set methods

    def __le__(self, other):
        if type(self) != type(other):
            return NotImplemented
        else:
            return len(self) <= len(other)

    def __ge__(self, other):
        if type(self) != type(other):
            return NotImplemented
        else:
            return len(self) >= len(other)

    def __eq__(self, other):
        if type(self) != type(other):
            return NotImplemented
        else:
            return self._collection == other._collection

    def __len__(self):
        return len(self._collection)

    def __iter__(self):
        for i in self._collection:
            yield i

    def __contains__(self, item):
        return item in self._collection

    #Mutable Set methods

    def add(self, elem):
        if isinstance(elem, self._allowedTypes):
            self._collection.add(elem)
            self._collectedTypes.add(type(elem).__name__)
        else:
            raise CollectionTypeError("{} can only contain '{}', '{}' is not allowed.".format(type(self).__name__, self._allowedTypes, elem))

    def discard(self, elem):
        return self._collection.discard(elem)

    def remove(self, elem):
        try:
            return self._collection.remove(elem)
        except KeyError:
            raise KeyError("'{}' was not found in the {}: '{}'.".format(elem, type(self).__name__, self)) from None

    def clear(self):
        self.bad = False
        self.errors = {}
        self._collection.clear()

    def pop(self):
        try:
            return self._collection.pop()
        except KeyError:
            raise KeyError("Nothing left in the {}: '{}'.".format(type(self).__name__, self)) from None

    def __ior__(self, other):
        if type(self) != type(other):
            return NotImplemented
        else:
            self._collection |= other._collection
            self._collectedTypes |= other._collectedTypes
            self.name = '{} |= {}'.format(self.name, other.name)
            if other.bad or self.bad:
                self.bad = True
                self.errors.update(other.errors)
            return self

    def __iand__(self, other):
        if type(self) != type(other):
            return NotImplemented
        else:
            self._collection &= other._collection
            self._collectedTypes |= other._collectedTypes
            self.name = '{} &= {}'.format(self.name, other.name)
            if other.bad or self.bad:
                self.bad = True
                self.errors.update(other.errors)
            return self

    def __ixor__(self, other):
        if type(self) != type(other):
            return NotImplemented
        else:
            self._collection ^= other._collection
            self._collectedTypes |= other._collectedTypes
            self.name = '{} ^= {}'.format(self.name, other.name)
            if other.bad or self.bad:
                self.bad = True
                self.errors.update(other.errors)
            return self

    def __isub__(self, other):
        if type(self) != type(other):
            return NotImplemented
        else:
            self._collection -= other._collection
            self._collectedTypes |= other._collectedTypes
            self.name = '{} -= {}'.format(self.name, other.name)
            if other.bad or self.bad:
                self.bad = True
                self.errors.update(other.errors)
            return self

    #These are provided by the above
    #but don't work right unless they are custom written

    def __or__(self, other):
        if type(self) != type(other):
            return NotImplemented
        else:
            retCollection = type(self)(self._collection | other._collection, name = '{} | {}'.format(self.name, other.name), quietStart = True)
            if other.bad or self.bad:
                retCollection.bad = True
                retCollection.errors.update(other.errors)
            return retCollection

    def __and__(self, other):
        if type(self) != type(other):
            return NotImplemented
        else:
            retCollection = type(self)(self._collection & other._collection, name = '{} & {}'.format(self.name, other.name), quietStart = True)
            if other.bad or self.bad:
                retCollection.bad = True
                retCollection.errors.update(other.errors)
            return retCollection

    def __sub__(self, other):
        if type(self) != type(other):
            return NotImplemented
        else:
            retCollection = type(self)(self._collection - other._collection, name = '{} - {}'.format(self.name, other.name), quietStart = True)
            if other.bad or self.bad:
                retCollection.bad = True
                retCollection.errors.update(other.errors)
            return retCollection

    def __xor__(self, other):
        if type(self) != type(other):
            return NotImplemented
        else:
            retCollection = type(self)(self._collection ^ other._collection, name = '{} ^ {}'.format(self.name, other.name), quietStart = True)
            if other.bad or self.bad:
                retCollection.bad = True
                retCollection.errors.update(other.errors)
            return retCollection

    def __repr__(self):
        return "<metaknowledge.{} object {}>".format(type(self).__name__, self.name)

    def __str__(self):
        return "{}({})".format(type(self).__name__, self.name)

    def copy(self):
        collectedCopy = copy.copy(self)
        collectedCopy._collection = copy.copy(collectedCopy._collection)
        self._collectedTypes = copy.copy(self._collectedTypes)
        self._allowedTypes = copy.copy(self._allowedTypes)
        collectedCopy.errors = copy.copy(collectedCopy.errors)
        return collectedCopy

    def peak(self):
        if len(self._collection) > 0:
            return self._collection.__iter__().__next__()
        else:
            return None

    def chunk(self, maxSize):
        chunks = []
        currentSize = maxSize + 1
        for i in self:
            if currentSize >= maxSize:
                currentSize = 0
                chunks.append(type(self)({i}, name = 'Chunk-{}-of-{}'.format(len(chunks), self.name), quietStart = True))
            else:
                chunks[-1].add(i)
            currentSize += 1
        return chunks

    def split(self, maxSize):
        """destructive"""
        chunks = []
        currentSize = maxSize + 1
        try:
            while True:
                if currentSize >= maxSize:
                    currentSize = 0
                    chunks.append(type(self)({self.pop()}, name = 'Chunk-{}-of-{}'.format(len(chunks), self.name), quietStart = True))
                else:
                    chunks[-1].add(self.pop())
                currentSize += 1
        except KeyError:
            self.name = 'Emptied-{}'.format(self.name)
        return chunks

    def _loadFromCache(self, cacheName, flist, name, extension):
        def loadCache(cacheFile, flist, rcName, fileExtensions):
            with open(cacheFile, 'rb') as f:
                try:
                    dat, RC = pickle.load(f)
                except pickle.PickleError as e:
                    raise cacheError("pickle Error: {}".format(e))
            if dat["metaknowledge Version"] != __version__:
                raise cacheError("mk version mismatch")
            if dat["Collection Name"] != rcName:
                raise cacheError("Name mismatch")
            if dat["File Extension"] != fileExtensions:
                raise cacheError("Extension mismatch")
            if len(flist) != len(dat["File dict"]):
                raise cacheError("File number mismatch")
            while len(flist) > 0:
                workingFile = flist.pop()
                if os.stat(workingFile).st_mtime != dat["File dict"][workingFile]:
                    raise cacheError("File modification mismatch")
            return RC.__dict__

        if os.path.isfile(cacheName):
            try:
                self.__dict__ = loadCache(cacheName, flist, name, extension)
            except (cacheError, KeyError, FileNotFoundError):
                os.remove(cacheName)
                return False
            else:
                return True

    def _createCache(self, cacheFile, flist, name, extension):
        dat = {
            "metaknowledge Version" : __version__,
            "File dict" : {},
            "Collection Name" : name,
            "File Extension" : extension,
        }
        for fileName in flist:
            dat["File dict"][fileName] =  os.stat(fileName).st_mtime
        with open(cacheFile, 'wb') as f:
            pickle.dump((dat, self), f)

class CollectionWithIDs(Collection):
    """A Collection with a few extra methods that assume all the contained items have an id attribute and a bad attribute, e.g. Records or Grants"""
    def __init__(self, inSet, allowedTypes, collectedTypes, name, bad, errors, quietStart = False):

        Collection.__init__(self, inSet, allowedTypes, collectedTypes, name, bad, errors, quietStart = quietStart)

    def containsID(self, idVal):
        for i in self:
            if i.id == idVal:
                return True
        return False

    def discardID(self, idVal):
        for i in self:
            if i.id == idVal:
                self._collection.discard(i)
                return

    def removeID(self, idVal):
        for i in self:
            if i.id == idVal:
                self._collection.remove(i)
                return
        raise KeyError("A Record with the ID '{}' was not found in the RecordCollection: '{}'.".format(idVal, self))

    def getID(self, idVal):
        for i in self:
            if i.id == idVal:
                return i
        return None

    def badEntries(self):
        badEntries = set()
        for i in self:
            if i.bad:
                badEntries.add(i)
        return type(self)(badEntries, quietStart = True)

    def dropBadEntries(self):
        self._collection = set((i for i in self if not i.bad))

    def tags(self):
        tags = set()
        for i in self:
            tags |= set(i.keys())
        return tags

    def oneModeNetwork(self, mode, nodeCount = True, edgeWeight = True, stemmer = None, edgeAttribute = None, nodeAttribute = None):
        """Creates a network of the objects found by one WOS tag _mode_.

        A **oneModeNetwork**() looks are each Record in the RecordCollection and extracts its values for the tag given by _mode_, e.g. the `'AF'` tag. Then if multiple are returned an edge is created between them. So in the case of the author tag `'AF'` a co-authorship network is created.

        The number of times each object occurs is count if _nodeCount_ is `True` and the edges count the number of co-occurrences if _edgeWeight_ is `True`. Both are`True` by default.

        **Note** Do not use this for the construction of co-citation networks use [Recordcollection.coCiteNetwork()](#RecordCollection.coCiteNetwork) it is more accurate and has more options.

        # Parameters

        _mode_ : `str`

        > A two character WOS tag or one of the full names for a tag

        _nodeCount_ : `optional [bool]`

        > Default `True`, if `True` each node will have an attribute called "count" that contains an int giving the number of time the object occurred.

        _edgeWeight_ : `optional [bool]`

        > Default `True`, if `True` each edge will have an attribute called "weight" that contains an int giving the number of time the two objects co-occurrenced.

        _stemmer_ : `optional [func]`

        > Default `None`, If _stemmer_ is a callable object, basically a function or possibly a class, it will be called for the ID of every node in the graph, all IDs are strings. For example:

        > The function ` f = lambda x: x[0]` if given as the stemmer will cause all IDs to be the first character of their unstemmed IDs. e.g. the title `'Goos-Hanchen and Imbert-Fedorov shifts for leaky guided modes'` will create the node `'G'`.

        # Returns

        `networkx Graph`

        > A networkx Graph with the objects of the tag _mode_ as nodes and their co-occurrences as edges
        """
        stemCheck = False
        if stemmer is not None:
            if isinstance(stemmer, collections.abc.Callable):
                stemCheck = True
            else:
                raise TypeError("stemmer must be callable, e.g. a function or class with a __call__ method.")
        count = 0
        progArgs = (0, "Starting to make a one mode network with {}".format(mode))
        if metaknowledge.VERBOSE_MODE:
            progKwargs = {'dummy' : False}
        else:
            progKwargs = {'dummy' : True}
        with _ProgressBar(*progArgs, **progKwargs) as PBar:
            if edgeAttribute is not None:
                grph = nx.MultiGraph()
            else:
                grph = nx.Graph()
            for R in self:
                if PBar:
                    count += 1
                    PBar.updateVal(count / len(self), "Analyzing: " + str(R))
                if edgeAttribute:
                    edgeVals = [str(v) for v in R.get(edgeAttribute, [])]
                if nodeAttribute:
                    nodeVals = [str(v) for v in R.get(nodeAttribute, [])]
                if isinstance(mode, list):
                    contents = []
                    for attr in mode:
                        tmpContents = R.get(attr, [])
                        if isinstance(tmpContents, list):
                            contents += tmpContents
                        else:
                            contents.append(tmpContents)
                else:
                    contents = R.get(mode)
                if contents is not None:
                    if not isinstance(contents, str) and isinstance(contents, collections.abc.Iterable):
                        if stemCheck:
                            tmplst = [stemmer(str(n)) for n in contents]
                        else:
                            tmplst = [str(n) for n in contents]
                        if len(tmplst) > 1:
                            for i, node1 in enumerate(tmplst):
                                for node2 in tmplst[i + 1:]:
                                    if edgeAttribute:
                                        for edgeVal in edgeVals:
                                            if grph.has_edge(node1, node2, key = edgeVal):
                                                if edgeWeight:
                                                    for i, a in grph[node1][node2].items():
                                                        if a['key'] == edgeVal:
                                                            grph[node1][node2][i]['weight'] += 1
                                                            break
                                            else:
                                                if edgeWeight:
                                                    attrDict = {'key' : edgeVal, 'weight' : 1}
                                                else:
                                                    attrDict = {'key' : edgeVal}
                                                grph.add_edge(node1, node2, attr_dict = attrDict)
                                    elif edgeWeight:
                                        try:
                                            grph.edge[node1][node2]['weight'] += 1
                                        except KeyError:
                                            grph.add_edge(node1, node2, weight = 1)
                                    else:
                                        if not grph.has_edge(node1, node2):
                                            grph.add_edge(node1, node2)
                                if not grph.has_node(node1):
                                    grph.add_node(node1)
                                if nodeCount:
                                    try:
                                        grph.node[node1]['count'] += 1
                                    except KeyError:
                                        grph.node[node1]['count'] = 1
                                if nodeAttribute:
                                    try:
                                        currentAttrib = grph.node[node1][nodeAttribute]
                                    except KeyError:
                                        grph.node[node1][nodeAttribute] = nodeVals
                                    else:
                                        for nodeValue in (n for n in nodeVals if n not in currentAttrib):
                                            grph.node[node1][nodeAttribute].append(nodeValue)
                        elif len(tmplst) == 1:
                            if nodeCount:
                                try:
                                    grph.node[tmplst[0]]['count'] += 1
                                except KeyError:
                                    grph.add_node(tmplst[0], count = 1)
                            else:
                                if not grph.has_node(tmplst[0]):
                                    grph.add_node(tmplst[0])
                            if nodeAttribute:
                                try:
                                    currentAttrib = grph.node[tmplst[0]][nodeAttribute]
                                except KeyError:
                                    grph.node[tmplst[0]][nodeAttribute] = nodeVals
                                else:
                                    for nodeValue in (n for n in nodeVals if n not in currentAttrib):
                                        grph.node[tmplst[0]][nodeAttribute].append(nodeValue)
                        else:
                            pass
                    else:
                        if stemCheck:
                            nodeVal = stemmer(str(contents))
                        else:
                            nodeVal = str(contents)
                        if nodeCount:
                            try:
                                grph.node[nodeVal]['count'] += 1
                            except KeyError:
                                grph.add_node(nodeVal, count = 1)
                        else:
                            if not grph.has_node(nodeVal):
                                grph.add_node(nodeVal)
                        if nodeAttribute:
                            try:
                                currentAttrib = grph.node[nodeVal][nodeAttribute]
                            except KeyError:
                                grph.node[nodeVal][nodeAttribute] = nodeVals
                            else:
                                for nodeValue in (n for n in nodeVals if n not in currentAttrib):
                                    grph.node[nodeVal][nodeAttribute].append(nodeValue)
            if PBar:
                PBar.finish("Done making a one mode network with {}".format(mode))
        return grph

    def twoModeNetwork(self, tag1, tag2, directed = False, recordType = True, nodeCount = True, edgeWeight = True, stemmerTag1 = None, stemmerTag2 = None, edgeAttribute = None):
        """Creates a network of the objects found by two WOS tags _tag1_ and _tag2_, each node marked by which tag spawned it making the resultant graph bipartite.

        A **twoModeNetwork()** looks at each Record in the `RecordCollection` and extracts its values for the tags given by _tag1_ and _tag2_, e.g. the `'WC'` and `'LA'` tags. Then for each object returned by each tag and edge is created between it and every other object of the other tag. So the WOS defined subject tag `'WC'` and language tag `'LA'`, will give a two-mode network showing the connections between subjects and languages. Each node will have an attribute call `'type'` that gives the tag that created it or both if both created it, e.g. the node `'English'` would have the type attribute be `'LA'`.

        The number of times each object occurs is count if _nodeCount_ is `True` and the edges count the number of co-occurrences if _edgeWeight_ is `True`. Both are`True` by default.

        The _directed_ parameter if `True` will cause the network to be directed with the first tag as the source and the second as the destination.

        # Parameters

        _tag1_ : `str`

        > A two character WOS tag or one of the full names for a tag, the source of edges on the graph

        _tag1_ : `str`

        > A two character WOS tag or one of the full names for a tag, the target of edges on the graph

        _directed_ : `optional [bool]`

        > Default `False`, if `True` the returned network is directed

        _nodeCount_ : `optional [bool]`

        > Default `True`, if `True` each node will have an attribute called "count" that contains an int giving the number of time the object occurred.

        _edgeWeight_ : `optional [bool]`

        > Default `True`, if `True` each edge will have an attribute called "weight" that contains an int giving the number of time the two objects co-occurrenced.

        _stemmerTag1_ : `optional [func]`

        > Default `None`, If _stemmerTag1_ is a callable object, basically a function or possibly a class, it will be called for the ID of every node given by _tag1_ in the graph, all IDs are strings.

        > For example: the function `f = lambda x: x[0]` if given as the stemmer will cause all IDs to be the first character of their unstemmed IDs. e.g. the title `'Goos-Hanchen and Imbert-Fedorov shifts for leaky guided modes'` will create the node `'G'`.

        _stemmerTag2_ : `optional [func]`

        > Default `None`, see _stemmerTag1_ as it is the same but for _tag2_

        # Returns

        `networkx Graph or networkx DiGraph`

        > A networkx Graph with the objects of the tags _tag1_ and _tag2_ as nodes and their co-occurrences as edges.
        """
        if not isinstance(tag1, str):
            raise TypeError("{} is not a string it cannot be a tag.".format(tag1))
        if not isinstance(tag2, str):
            raise TypeError("{} is not a string it cannot be a tag.".format(tag2))
        if stemmerTag1 is not None:
            if isinstance(stemmerTag1, collections.abc.Callable):
                stemCheck = True
            else:
                raise TypeError("stemmerTag1 must be callable, e.g. a function or class with a __call__ method.")
        else:
            stemmerTag1 = lambda x: x
        if stemmerTag2 is not None:
            if isinstance(stemmerTag2, collections.abc.Callable):
                stemCheck = True
            else:
                raise TypeError("stemmerTag2 must be callable, e.g. a function or class with a __call__ method.")
        else:
            stemmerTag2 = lambda x: x
        count = 0
        progArgs = (0, "Starting to make a two mode network of " + tag1 + " and " + tag2)
        if metaknowledge.VERBOSE_MODE:
            progKwargs = {'dummy' : False}
        else:
            progKwargs = {'dummy' : True}
        with _ProgressBar(*progArgs, **progKwargs) as PBar:
            if edgeAttribute is not None:
                if directed:
                    grph = nx.MultiDiGraph()
                else:
                    grph = nx.MultiGraph()
            else:
                if directed:
                    grph = nx.DiGraph()
                else:
                    grph = nx.Graph()
            for R in self:
                if PBar:
                    count += 1
                    PBar.updateVal(count / len(self), "Analyzing: {}".format(R))
                if edgeAttribute:
                    edgeVals = [str(v) for v in getattr(R, edgeAttribute, [])]
                contents1 = R.get(tag1)
                contents2 = R.get(tag2)
                if isinstance(contents1, list):
                    contents1 = [stemmerTag1(str(v)) for v in contents1]
                elif contents1 == None:
                    contents1 = []
                else:
                    contents1 = [stemmerTag1(str(contents1))]
                if isinstance(contents2, list):
                    contents2 = [stemmerTag2(str(v)) for v in contents2]
                elif contents2 == None:
                    contents2 = []
                else:
                    contents2 = [stemmerTag2(str(contents2))]
                for node1 in contents1:
                    for node2 in contents2:
                        if edgeAttribute:
                            for edgeVal in edgeVals:
                                if grph.has_edge(node1, node2, key = edgeVal):
                                    if edgeWeight:
                                        for i, a in grph[node1][node2].items():
                                            if a['key'] == edgeVal:
                                                grph[node1][node2][i]['weight'] += 1
                                                break
                                else:
                                    if edgeWeight:
                                        attrDict = {'key' : edgeVal, 'weight' : 1}
                                    else:
                                        attrDict = {'key' : edgeVal}
                                    grph.add_edge(node1, node2, attr_dict = attrDict)
                        elif edgeWeight:
                            try:
                                grph.edge[node1][node2]['weight'] += 1
                            except KeyError:
                                grph.add_edge(node1, node2, weight = 1)
                        else:
                            if not grph.has_edge(node1, node2):
                                grph.add_edge(node1, node2)
                    if nodeCount:
                        try:
                            grph.node[node1]['count'] += 1
                        except KeyError:
                            try:
                                grph.node[node1]['count'] = 1
                                if recordType:
                                    grph.node[node1]['type'] = tag1
                            except KeyError:
                                if recordType:
                                    grph.add_node(node1, type = tag1)
                                else:
                                    grph.add_node(node1)
                    else:
                        if not grph.has_node(node1):
                            if recordType:
                                grph.add_node(node1, type = tag1)
                            else:
                                grph.add_node(node1)
                        elif recordType:
                            if 'type' not in grph.node[node1]:
                                grph.node[node1]['type'] = tag1

                for node2 in contents2:
                    if nodeCount:
                        try:
                            grph.node[node2]['count'] += 1
                        except KeyError:
                            try:
                                grph.node[node2]['count'] = 1
                                if recordType:
                                    grph.node[node2]['type'] = tag2
                            except KeyError:
                                grph.add_node(node2, count = 1)
                                if recordType:
                                    grph.node[node2]['type'] = tag2
                    else:
                        if not grph.has_node(node2):
                            if recordType:
                                grph.add_node(node2, type = tag2)
                            else:
                                grph.add_node(node2)
                        elif recordType:
                            if 'type' not in grph.node[node2]:
                                grph.node[node2]['type'] = tag2
            if PBar:
                PBar.finish("Done making a two mode network of " + tag1 + " and " + tag2)
        return grph

    def nModeNetwork(self, tags, recordType = True, nodeCount = True, edgeWeight = True, stemmer = None, edgeAttribute = None):
        """Creates a network of the objects found by all WOS tags in _tags_, each node is marked by which tag spawned it making the resultant graph n-partite.

        A **nModeNetwork()** looks are each Record in the RecordCollection and extracts its values for the tags given by _tags_. Then for all objects returned an edge is created between them, regardless of their type. Each node will have an attribute call `'type'` that gives the tag that created it or both if both created it, e.g. if `'LA'` were in _tags_ node `'English'` would have the type attribute be `'LA'`.

        For example if _tags_ was set to `['CR', 'UT', 'LA']`, a three mode network would be created, composed of a co-citation network from the `'CR'` tag. Then each citation would also have edges to all the languages of Records that cited it and to the WOS number of the those Records.

        The number of times each object occurs is count if _nodeCount_ is `True` and the edges count the number of co-occurrences if _edgeWeight_ is `True`. Both are`True` by default.

        # Parameters

        _mode_ : `str`

        > A two character WOS tag or one of the full names for a tag

        _nodeCount_ : `optional [bool]`

        > Default `True`, if `True` each node will have an attribute called `'count'` that contains an int giving the number of time the object occurred.

        _edgeWeight_ : `optional [bool]`

        > Default `True`, if `True` each edge will have an attribute called `'weight'` that contains an int giving the number of time the two objects co-occurrenced.

        _stemmer_ : `optional [func]`

        > Default `None`, If _stemmer_ is a callable object, basically a function or possibly a class, it will be called for the ID of every node in the graph, note that all IDs are strings.

        > For example: the function `f = lambda x: x[0]` if given as the stemmer will cause all IDs to be the first character of their unstemmed IDs. e.g. the title `'Goos-Hanchen and Imbert-Fedorov shifts for leaky guided modes'` will create the node `'G'`.

        # Returns

        `networkx Graph`

        > A networkx Graph with the objects of the tags _tags_ as nodes and their co-occurrences as edges
        """
        for t in (i for i in tags if not isinstance(i, str)):
            raise TypeError("{} is not a string it cannot be a tag.".format(t))
        stemCheck = False
        if stemmer is not None:
            if isinstance(stemmer, collections.abc.Callable):
                stemCheck = True
            else:
                raise TypeError("stemmer must be Callable, e.g. a function or class with a __call__ method.")
        count = 0
        progArgs = (0, "Starting to make a " + str(len(tags)) + "-mode network of: " + ', '.join(tags))
        if metaknowledge.VERBOSE_MODE:
            progKwargs = {'dummy' : False}
        else:
            progKwargs = {'dummy' : True}
        with _ProgressBar(*progArgs, **progKwargs) as PBar:
            if edgeAttribute is not None:
                grph = nx.MultiGraph()
            else:
                grph = nx.Graph()
            for R in self:
                if PBar:
                    count += 1
                    PBar.updateVal(count / len(self), "Analyzing: " + str(R))
                contents = []
                for t in tags:
                    tmpVal = R.get(t)
                    if stemCheck:
                        if tmpVal:
                            if isinstance(tmpVal, list):
                                contents.append((t, [stemmer(str(v)) for v in tmpVal]))
                            else:
                                contents.append((t, [stemmer(str(tmpVal))]))
                    else:
                        if tmpVal:
                            if isinstance(tmpVal, list):
                                contents.append((t, [str(v) for v in tmpVal]))
                            else:
                                contents.append((t, [str(tmpVal)]))
                for i, vlst1 in enumerate(contents):
                    for node1 in vlst1[1]:
                        for vlst2 in contents[i + 1:]:
                            for node2 in vlst2[1]:
                                if edgeAttribute:
                                    for edgeVal in edgeVals:
                                        if grph.has_edge(node1, node2, key = edgeVal):
                                            if edgeWeight:
                                                for i, a in grph[node1][node2].items():
                                                    if a['key'] == edgeVal:
                                                        grph[node1][node2][i]['weight'] += 1
                                                        break
                                        else:
                                            if edgeWeight:
                                                attrDict = {'key' : edgeVal, 'weight' : 1}
                                            else:
                                                attrDict = {'key' : edgeVal}
                                            grph.add_edge(node1, node2, attr_dict = attrDict)
                                elif edgeWeight:
                                    try:
                                        grph.edge[node1][node2]['weight'] += 1
                                    except KeyError:
                                        grph.add_edge(node1, node2, weight = 1)
                                else:
                                    if not grph.has_edge(node1, node2):
                                        grph.add_edge(node1, node2)
                        if nodeCount:
                            try:
                                grph.node[node1]['count'] += 1
                            except KeyError:
                                try:
                                    grph.node[node1]['count'] = 1
                                    if recordType:
                                        grph.node[node1]['type'] = vlst1[0]
                                except KeyError:
                                    if recordType:
                                        grph.add_node(node1, type = vlst1[0])
                                    else:
                                        grph.add_node(node1)
                        else:
                            if not grph.has_node(node1):
                                if recordType:
                                    grph.add_node(node1, type = vlst1[0])
                                else:
                                    grph.add_node(node1)
                            elif recordType:
                                try:
                                    grph.node[node1]['type'] += vlst1[0]
                                except KeyError:
                                    grph.node[node1]['type'] = vlst1[0]
            if PBar:
                PBar.finish("Done making a {}-mode network of: {}".format(len(tags), ', '.join(tags)))
        return grph
