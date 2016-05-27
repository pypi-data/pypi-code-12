# -*- coding: utf-8 -*-
from collections import OrderedDict



class NestedOrderedDict(OrderedDict):
    '''
    an OrderedDict allowing the access of nested items
    through a .path attribute
    
    every item of the NestedOrderedDict that is also a NestedOrderedDict
    inherits the path information to the uppermost NestedOrderedDict
    
    lets' build a nested structure:

    >>> parent = NestedOrderedDict()
    >>> ch1 = 'foo'
    >>> ch2 = NestedOrderedDict()
    >>> ch2_1 = NestedOrderedDict()
    >>> ch2_1_1 = NestedOrderedDict([['hello','world']])

    set items:
    
    >>> parent['2'] = ch1
    >>> parent['3'] = ch2
    >>> ch2['4'] = ch2_1
    >>> ch2_1['5'] = ch2_1_1

    get the path from the most nested item:
    
    >>> p = ch2_1_1.path
    >>> print p
    3, 4, 5
    
    access this item from the parent dict:
    
    >>> print parent[p]
    NestedOrderedDict({hello: world})
    '''


    def __init__(self, *args, **kwargs):
        super(NestedOrderedDict, self).__init__(*args, **kwargs)
        self.path = ''


    def __getitem__(self, key):
        try:
            return OrderedDict.__getitem__(self,key)
        except KeyError:
            key = key.split(', ')
            key2 = ', '.join(key[1:])
            return self[key[0]].__getitem__(key2)


    def __setitem__(self, key, value):
        super(NestedOrderedDict, self).__setitem__(key, value)
        if isinstance(value,self.__class__):
            if self.path:
                value.path = self.path + ', ' + key
            else:
                value.path = key


    def __repr__(self):
        '''limit the number of shown items to 5 and give it a more dict-like view'''
        contents = ''
        n = 0
        for n, (key, item) in enumerate(self.iteritems()):
            contents += '%s: %s, ' %(key,item)
            if n == 5:
                break
        if contents:
            contents = contents[:-2]
        if n == 5:
            contents += ', ...'
        return '%s({%s})' %(self.__class__.__name__, contents)




if __name__ == '__main__':
    import doctest
    doctest.testmod()