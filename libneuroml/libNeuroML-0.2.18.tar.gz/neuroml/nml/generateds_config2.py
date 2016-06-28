#Maps from NeuroML element space (Key) to python object space (value)
#The class names are essentially correct, the instance names need converting
#also attributes need fixing

import lxml
from lxml import objectify
import re
from config import variables
import csv
import sys

sys.setrecursionlimit(1500)

def remove_curlies(string):
    return re.sub("{.*}","",string)

def to_lowercase_with_underscores(string):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', string)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

def to_camelback(string):
    string_list = list(string)
    i = 0
    for m in re.finditer('_', string):
        underscore_index = m.end()
        string_list[underscore_index - i] = string_list[underscore_index - i].capitalize()
        string_list.pop(underscore_index - (1 + i))
        i += 1
    string = ''.join(string_list)

    return str(string)

def traverse_doc(queue,rename):
    """Recursive function to traverse the nodes of a tree in
    breadth-first order.

    The first argument should be the tree root; children
    should be a function taking as argument a tree node and
    returning an iterator of the node's children.
    """
    if len(queue) > 0:
        node = queue.pop()
        children = node.getchildren()
        rename(node)
        queue = queue + children
        traverse_doc(queue,rename)
    else:
        return None

def pluralize(noun):                            
    if re.search('[sxz]$', noun):             
        return re.sub('$', 'es', noun)        
    elif re.search('[^aeioudgkprt]h$', noun):
        return re.sub('$', 'es', noun)       
    elif re.search('[^aeiou]y$', noun):      
        return re.sub('y$', 'ies', noun)     
    else:                                    
        return noun + 's'

def _node_to_python(node):

    pluralize_flag = 'maxOccurs' in node.attrib

    for attribute in node.attrib:
        nml_attribute = node.attrib.pop(attribute)
        if nml_attribute[0].islower():
            renamed_attribute = to_lowercase_with_underscores(nml_attribute)
            if pluralize_flag:
                renamed_attribute = pluralize(renamed_attribute)
            NameTable[nml_attribute] = renamed_attribute



if __name__ == '__main__':
    print("Testing")
    
    tt = ['fgsdfSSDF','WWee','123Er4','tauDecay2','gbase2','gbase1']
    for t in tt:
        print('%s -> %s'%(t,to_lowercase_with_underscores(t)))