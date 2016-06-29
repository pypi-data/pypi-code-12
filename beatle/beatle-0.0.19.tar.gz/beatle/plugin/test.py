# -*- coding: utf-8 -*-

import os
import xml.etree.ElementTree as et

class Test:

    def __init__(self):
        self._name = 'Ozores'

v = Test()
dictionary={}
dictionary['toRel']=v

z=eval('toRel',dictionary)
print(z)
print(v)
exit()

tree = et.parse(
    '/home/mel/pythonProjects/proCxx/plugin/models/relation/standard/toMethods.xml')
root = tree.getroot()
definitions = root.find('definitions')
if definitions is not None:
    for definition in definitions:
        text = definition.findtext('.')
        print tuple(tuple(text.split('=')))
        for x, y in [text.split('=')]:
            v = y.format(**dictionary)
            dictionary[x] = v
        print dictionary
