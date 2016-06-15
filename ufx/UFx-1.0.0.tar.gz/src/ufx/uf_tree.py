# Copyright (c) 2013-2016, Philippe Bordron <philippe.bordron+ufx@gmail.com>
# -*- encoding: utf-8 -*-
# This file is part of UFx.
#
# UFx is free software: you can redistribute it and/or modify
# it under the terms of the GNU LESSER GENERAL PUBLIC LICENSE as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# UFx is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU LESSER GENERAL PUBLIC LICENSE for more details.
#
# You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
# along with UFx. If not, see <http://www.gnu.org/licenses/>

import sys

class UFNode:
    """
    The class UFNode is a node of the union-find tree.
    """

    def __init__(self, elem):
        """Create an UFNode containing the element elem"""
        self.elem = elem
        self.parent = None
        self.__rank = 0
        self.size = 1
        self.__repr__ = str(self.elem)
        #self.__repr__ = self.__str__

    def __str__(self):
        """To string function"""
        return str(self.elem)

    def find(self):
        """Return the root in the Union-Find structure that contains yourself"""
        if self.parent == None:
            return self
        self.parent = self.parent.find()
        return self.parent

    def union(self, other):
        """Merge the set containing yourself with the set containing other"""
        n1 = self.find()
        n2 = other.find()
        if n1 != n2: #self and other are not in the same set, we merge them
            if n1.__rank > n2.__rank:
                tmp = n1
                n1 = n2
                n2 = tmp
            # n1 has the smaller rank here
            n1.parent = n2
            n2.size += n1.size
            if n1.__rank == n2.__rank:
                n2.__rank += 1
        return n2

    def get_size(self):
        """Return the size of the set containing yourself"""
        return self.find().size

    def get_elem(self):
        """Return the elem stored in yourself."""
        return self.elem

    def cut(self):
        """For cleanning purpose:
        Remove your parent relationship"""
        self.parent=None
#end class


class UnionFind:
    """
    The class UnionFind from "uf_tree.py" implements the independant set data
    structure with a tree structure. This structure allows to realize in an
    efficient way (the computation time follows an Ackerman function):
        - to make the union of sets
        - to test if some elements are in a same set
    """

    def __init__(self):
        """Create an empty union-find data structure."""
        self.elements = {}
        self.__repr__ = self.__str__

    def contains(self, elem):
        """Return True if elem is in one of the sets stored in the data
        structure"""
        return elem in self.elements

    def make_set(self, elem):
        """Add an element elem as a singleton"""
        n = UFNode(elem)
        self.elements[elem] = n
        return n.get_elem()

    def find(self, elem):
        """Return the root of the set containing elem"""
        return self.elements[elem].find().get_elem()

    def union(self, elem1, elem2):
        """Merge the sets that contain resp. elem1 and elem2 and return the
        root"""
        return self.elements[elem1].union(self.elements[elem2]).get_elem()

    def get_size(self, elem):
        """Get the size of the set that contains elem."""
        return self.elements[elem].get_size()

    def clear(self):
        """Clear the data structure"""
        for n in self.elements.values():
            n.cut()
        self.elements.clear()


    # Included for testing purposes only.
    def get_set_map(self):
        """For testing purpose only.
        Return a map that associates to each set identified by its root the set
        of its elements"""
        result = {}
        for k,e in self.elements.items():
            root = e.find().get_elem()
            if not root in result:
                result[root] = set()
            result[root].add(k)
        return result

    def __str__(self):
        """For testing purpose only.
        To string function"""
        return str(self.get_set_map())
#end class


if __name__ == '__main__':
    sys.stdout.write("Testing...\n")
    u = UnionFind()
    az = "abcdefghijklmnopqrstuvwxyz"
    az += az.upper()
    for e in az:
        u.make_set(e)
    cnt = 0
    while cnt < 26:
        cnt += 1
        one=random.choice(az)
        two=random.choice(az)
        u.union(one, two)
        sys.stdout.write("fuse {} and {}\n".format(one, two))
    sys.stdout.write("{}\n".format(str(uf)))
    target = 'a'
    sys.stdout.write("size of subset {}: {}\n".format(target, u.get_size(target)))
    u.clear()
    sys.stdout.write("Testing complete\n")
