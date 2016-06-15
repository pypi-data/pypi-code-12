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
# along with UFx.  If not, see <http://www.gnu.org/licenses/>

import sys

class UnionFind:
    """
    The class UnionFind from "uf_hash.py" implements the independant set data
    structure with a hashmap structure. This structure allows to realize in an
    efficient way (the computation time follows an Ackerman function):
        - to make the union of sets
        - to test if some elements are in a same set
    """

    def __init__(self):
        """Create an empty union-find data structure."""
        self.parent = {}
        self.rank = {}
        self.size = {}
        self.__repr__ = self.__str__

    def contains(self, elem):
        """Return True if elem is in one of the sets stored in the data
        structure"""
        return elem in self.parent

    def make_set(self, elem):
        """Add an element elem as a singleton"""
        self.parent[elem] = elem
        self.rank[elem] = 0
        self.size[elem] = 1
        return elem

    # recursive version
    def find(self, elem):
        """Return the root of the set containing elem"""
        if self.parent[elem] != elem:
            self.parent[elem] = self.find(self.parent[elem])
        return self.parent[elem]

    ## iterative version
    #def find(self, elem):
    #    """Return the root of the set containing elem"""
    #    update_list = list()
    #    while not elem == self.parent[elem]:
    #        update_list.append(elem)
    #        elem = self.parent[elem]
    #    while len(update_list)>0:
    #        self.parent[update_list.pop(0)] = elem
    #    return elem

    def union(self, elem1, elem2):
        """Merge the sets that contain resp. elem1 and elem2 and return the
        root"""
        n1 = self.find(elem1)
        n2 = self.find(elem2)
        if n1 != n2: #elem1 and elem2 are not in the same set, we merge them
            if self.rank[n1] > self.rank[n2]:
                tmp = n1
                n1 = n2
                n2 = tmp
            # n1 has the smaller rank here
            self.parent[n1] = n2
            self.size[n2] += self.size[n1]
            if self.rank[n1] == self.rank[n2]:
                self.rank[n2] += 1
            del self.size[n1]
            del self.rank[n1]
        return n2 #optional
    #end

    def get_size(self, elem):
        """Get the size of the set that contains elem."""
        return self.size[self.find(elem)]

    def clear(self):
        """Clear the data structure"""
        self.parent.clear()
        self.rank.clear()
        self.size.clear()


    # Function specific to the hashmap version of union-find data structure

    def add_to_set(self, dest_elem, elem):
        """Add an element elem to the set containing dest_elem"""
        root = self.find(dest_elem)
        if not elem in parent:
            self.parent[elem] = root
            self.size[root] += 1
            if self.rank[root] == 0:
                self.rank[root] = 1
        return root

    def union_from(self, list_of_elem):
        """Merge the sets that contains at least one element of list_of_elem"""
        set_id = set()
        if not list_of_elem:
            return None
        rank_max = -1
        for e in list_of_elem:
            p = self.find(e)
            set_id.add(p)
            if self.rank[p] > rank_max:
                root = p
                rank_max = self.rank[p]
        update_rank = False
        add_size = 0
        for e in set_id:
            if e != root:
                self.parent[e] = root
                add_size += self.size[e]
                del self.size[e]
                update_rank = update_rank or self.rank[e] == rank_max
                del self.rank[e]
        self.size[root] += add_size
        if update_rank:
            self.rank[root] = rank_max + 1
        return root
    #end


    # Included for testing purposes only.
    def get_set_map(self):
        """For testing purpose only.
        Return a map that associates to each set identified by its root the set
        of its elements"""
        result = {}
        for e in self.parent.keys():
            root = self.find(e)
            if not root in result:
                result[root] = set()
            result[root].add(e)
        return result

    # To string function
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
    sys.stdout.write("{}\n".format(str(u)))
    target = 'a'
    sys.stdout.write("size of subset {}: {}\n".format(target, u.get_size(target)))
    u.clear()
    sys.stdout.write("Testing complete\n")
